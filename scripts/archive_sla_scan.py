#!/usr/bin/env python3
"""
archive_sla_scan.py — Secretary archival SLA enforcer (cron-runnable)

Scans directories for new artifacts (mtime < 30 min) and checks if they are
indexed in knowledge/ARCHIVE_INDEX.md. Emits CIEU ARTIFACT_UNARCHIVED_SLA_BREACH
for each miss.

Usage:
  python3 scripts/archive_sla_scan.py              # enforce mode, emits CIEU
  python3 scripts/archive_sla_scan.py --dry-run    # print breaches, no CIEU emit
  python3 scripts/archive_sla_scan.py --max-age-minutes 60  # extend SLA window

Exit codes:
  0 — no breaches
  1 — ≥1 breach found (dry-run or enforce)
  2 — error (missing ARCHIVE_INDEX, etc.)

Designed to run from cron (see scripts/archive_sla_cron.txt for install example).
"""
import argparse
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Import canonical agent_id + CIEU emit helpers
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cieu_helpers import emit_cieu

SLA_MINUTES_DEFAULT = 30

def get_repo_root():
    """Get REPO_ROOT, either from script location or cwd (for test isolation)."""
    # Test mode: if cwd has any scan dir (reports/knowledge/products/content/governance), use cwd
    cwd = Path.cwd()
    if any((cwd / d).exists() for d in ["reports", "knowledge", "products", "content", "governance"]):
        return cwd
    # Normal mode: use script location
    return Path(__file__).resolve().parent.parent

REPO_ROOT = get_repo_root()
ARCHIVE_INDEX = REPO_ROOT / "knowledge" / "ARCHIVE_INDEX.md"
SCAN_DIRS = ["reports", "knowledge", "products", "content", "governance"]


def load_archive_index(path: Path) -> set[str]:
    """Parse ARCHIVE_INDEX.md, extract all filepaths from markdown links."""
    if not path.exists():
        return set()

    indexed = set()
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            # Match markdown link: [Title](path)
            if "](" in line and ")" in line:
                start = line.index("](") + 2
                end = line.index(")", start)
                rel_path = line[start:end]
                # Normalize: remove leading ./ or /
                rel_path = rel_path.lstrip("./")
                indexed.add(rel_path)

    return indexed


def scan_fresh_artifacts(dirs: list[str], max_age_minutes: int) -> list[tuple[Path, float]]:
    """Find files with mtime < max_age_minutes, return list of (path, age_minutes)."""
    cutoff = time.time() - (max_age_minutes * 60)
    fresh = []

    for dir_name in dirs:
        dir_path = REPO_ROOT / dir_name
        if not dir_path.exists():
            continue

        for fpath in dir_path.rglob("*"):
            if not fpath.is_file():
                continue
            # Skip dotfiles, __pycache__, etc.
            if any(part.startswith(".") or part == "__pycache__" for part in fpath.parts):
                continue
            # Skip ARCHIVE_INDEX.md itself (it indexes others, doesn't get indexed)
            if fpath.name == "ARCHIVE_INDEX.md":
                continue

            mtime = fpath.stat().st_mtime
            if mtime >= cutoff:
                age_minutes = (time.time() - mtime) / 60
                fresh.append((fpath, age_minutes))

    return fresh


def compute_breaches(fresh_artifacts: list[tuple[Path, float]], indexed: set[str]) -> list[dict]:
    """Return list of breach dicts: {path, age_minutes, relative_path}."""
    breaches = []

    for fpath, age_minutes in fresh_artifacts:
        rel_path = str(fpath.relative_to(REPO_ROOT))
        if rel_path not in indexed:
            breaches.append({
                "path": str(fpath),
                "relative_path": rel_path,
                "age_minutes": round(age_minutes, 1),
            })

    return breaches


def emit_breaches(breaches: list[dict], dry_run: bool) -> None:
    """Emit CIEU events for each breach (unless dry_run)."""
    for breach in breaches:
        msg = f"Artifact {breach['relative_path']} age {breach['age_minutes']}min, not in ARCHIVE_INDEX"

        if dry_run:
            print(f"[DRY-RUN] {msg}")
        else:
            emit_cieu(
                event_type="ARTIFACT_UNARCHIVED_SLA_BREACH",
                actor="secretary",
                metadata={
                    "path": breach["relative_path"],
                    "age_minutes": breach["age_minutes"],
                    "sla_minutes": SLA_MINUTES_DEFAULT,
                },
                description=msg,
            )
            print(f"[EMITTED] {msg}")


def main():
    parser = argparse.ArgumentParser(description="Secretary archival SLA scanner")
    parser.add_argument("--dry-run", action="store_true", help="Print breaches without emitting CIEU")
    parser.add_argument("--max-age-minutes", type=int, default=SLA_MINUTES_DEFAULT, help="SLA window in minutes")
    args = parser.parse_args()

    # 1. Check fresh artifacts first (if none, skip ARCHIVE_INDEX check for test isolation)
    fresh = scan_fresh_artifacts(SCAN_DIRS, args.max_age_minutes)

    # 2. Load archive index (error only if we have fresh artifacts to check)
    if not ARCHIVE_INDEX.exists():
        if fresh:
            print(f"ERROR: ARCHIVE_INDEX not found at {ARCHIVE_INDEX}", file=sys.stderr)
            sys.exit(2)
        else:
            # No fresh artifacts + no index = graceful exit 0 (no work to do)
            print(f"✓ No SLA breaches (scanned 0 fresh artifacts)")
            sys.exit(0)

    indexed = load_archive_index(ARCHIVE_INDEX)

    # 3. Compute breaches
    breaches = compute_breaches(fresh, indexed)

    # 4. Emit (or dry-run print)
    emit_breaches(breaches, args.dry_run)

    # 5. Exit code
    if breaches:
        print(f"\n{len(breaches)} artifact(s) unarchived beyond {args.max_age_minutes}min SLA")
        sys.exit(1)
    else:
        print(f"✓ No SLA breaches (scanned {len(fresh)} fresh artifacts)")
        sys.exit(0)


if __name__ == "__main__":
    main()
