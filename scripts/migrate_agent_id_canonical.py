#!/usr/bin/env python3
"""
CIEU agent_id canonical migration — F4
Migrates historical CIEU events to canonical agent_id per governance/agent_id_canonical.json
Board P0, 2026-04-16
"""
import json
import sqlite3
import sys
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = REPO_ROOT / "governance" / "agent_id_canonical.json"
DB_PATH = REPO_ROOT / ".ystar_cieu.db"


def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_before(cursor):
    """Before migration: distribution of agent_id"""
    cursor.execute("SELECT agent_id, COUNT(*) FROM cieu_events GROUP BY agent_id ORDER BY COUNT(*) DESC")
    rows = cursor.fetchall()
    print("\n=== BEFORE MIGRATION ===")
    total = sum(c for _, c in rows)
    unknown_family = {"agent", "unknown", "", "orchestrator", "path_a_agent", "intervention_engine", "omission_engine"}
    unknown_count = sum(c for aid, c in rows if aid in unknown_family)
    print(f"Total events: {total:,}")
    print(f"Unknown family count: {unknown_count:,} ({100*unknown_count/total:.1f}%)")
    print("\nTop 20 agent_id:")
    for aid, count in rows[:20]:
        pct = 100 * count / total
        print(f"  {aid!r:30s} {count:8,} ({pct:5.1f}%)")
    return total, unknown_count


def migrate(cursor, registry, dry_run=True):
    """Migrate agent_id to canonical"""
    aliases = registry["aliases"]
    system_components = registry["system_components"]
    system_prefix = registry["system_prefix"]

    updates = []

    # Alias normalization
    for alias, canonical in aliases.items():
        cursor.execute("SELECT COUNT(*) FROM cieu_events WHERE agent_id = ?", (alias,))
        count = cursor.fetchone()[0]
        if count > 0:
            updates.append((alias, canonical, count))

    # System components prefix
    for comp in system_components:
        cursor.execute("SELECT COUNT(*) FROM cieu_events WHERE agent_id = ?", (comp,))
        count = cursor.fetchone()[0]
        if count > 0:
            canonical_sys = f"{system_prefix}{comp}"
            updates.append((comp, canonical_sys, count))

    # Fallback unknowns → 'unidentified'
    for fallback in ["agent", "unknown", ""]:
        cursor.execute("SELECT COUNT(*) FROM cieu_events WHERE agent_id = ?", (fallback,))
        count = cursor.fetchone()[0]
        if count > 0:
            updates.append((fallback, "unidentified", count))

    print("\n=== MIGRATION PLAN ===")
    for old, new, count in updates:
        print(f"  {old!r:30s} → {new!r:30s} ({count:8,} events)")

    if not dry_run:
        print("\nExecuting UPDATE statements...")
        for old, new, count in updates:
            cursor.execute("UPDATE cieu_events SET agent_id = ? WHERE agent_id = ?", (new, old))
        print(f"✓ {len(updates)} UPDATE statements executed")
    else:
        print("\n(DRY RUN — no changes applied)")

    return updates


def analyze_after(cursor):
    """After migration: distribution of agent_id"""
    cursor.execute("SELECT agent_id, COUNT(*) FROM cieu_events GROUP BY agent_id ORDER BY COUNT(*) DESC")
    rows = cursor.fetchall()
    print("\n=== AFTER MIGRATION ===")
    total = sum(c for _, c in rows)
    unknown_count = sum(c for aid, c in rows if aid == "unidentified")
    print(f"Total events: {total:,}")
    print(f"Unidentified count: {unknown_count:,} ({100*unknown_count/total:.1f}%)")
    print("\nTop 20 agent_id:")
    for aid, count in rows[:20]:
        pct = 100 * count / total
        print(f"  {aid!r:30s} {count:8,} ({pct:5.1f}%)")
    return total, unknown_count


def main():
    dry_run = "--apply" not in sys.argv

    print("CIEU agent_id canonical migration")
    print(f"Registry: {REGISTRY_PATH}")
    print(f"Database: {DB_PATH}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'APPLY'}")

    if not REGISTRY_PATH.exists():
        print(f"❌ Registry not found: {REGISTRY_PATH}")
        sys.exit(1)

    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        sys.exit(1)

    registry = load_registry()

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Before
    total_before, unknown_before = analyze_before(cursor)

    # Migrate
    updates = migrate(cursor, registry, dry_run=dry_run)

    if not dry_run:
        # After
        total_after, unknown_after = analyze_after(cursor)

        # Commit + VACUUM
        conn.commit()
        print("\n✓ Changes committed")
        cursor.execute("VACUUM")
        print("✓ VACUUM completed")

        # Summary
        print("\n=== SUMMARY ===")
        print(f"Before unknown_family: {100*unknown_before/total_before:.1f}%")
        print(f"After unidentified: {100*unknown_after/total_after:.1f}%")
        print(f"Δ: {100*(unknown_before - unknown_after)/total_before:+.1f}% reduction")
    else:
        print("\n▶ Run with --apply to execute migration")

    conn.close()


if __name__ == "__main__":
    main()
