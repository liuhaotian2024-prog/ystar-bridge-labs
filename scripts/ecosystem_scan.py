#!/usr/bin/env python3
"""
Y* Bridge Labs Ecosystem Scanner — CEO 瞬间洞悉生态全貌

Scans team, products, infrastructure in one shot.
Outputs structured snapshot + imports into Aiden Neural Network.

Usage:
    ecosystem_scan.py              — full scan + neural network import
    ecosystem_scan.py --team       — team only
    ecosystem_scan.py --infra      — infrastructure only
    ecosystem_scan.py --summary    — one-page summary
"""

import os
import sys
import json
import subprocess
import time
import glob
from pathlib import Path

COMPANY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YGOV_ROOT = os.path.join(os.path.dirname(COMPANY_ROOT), "Y-star-gov")

sys.path.insert(0, os.path.dirname(__file__))


# ── Team Scanner ────────────────────────────────────────────────────

def scan_team() -> dict:
    """Scan all team members: charter existence, recent CZL activity, known gaps."""
    agents_dir = os.path.join(COMPANY_ROOT, ".claude", "agents")
    team = {}

    for f in sorted(os.listdir(agents_dir)):
        if not f.endswith(".md"):
            continue
        role = f.replace(".md", "")
        charter_path = os.path.join(agents_dir, f)
        with open(charter_path, "r", encoding="utf-8") as fh:
            content = fh.read()

        charter_lines = len(content.split("\n"))
        has_principles = "principle" in content.lower() or "原理" in content
        has_scope = "scope" in content.lower() or "管辖" in content

        # Check recent dispatch activity from sync log
        czl_count = 0
        sync_log = os.path.join(COMPANY_ROOT, "scripts", ".logs", "dispatch_sync.log")
        if os.path.exists(sync_log):
            with open(sync_log, "r", encoding="utf-8") as sl:
                for line in sl:
                    if role.lower() in line.lower():
                        czl_count += 1

        # Determine activation status
        active_roles = ["ceo", "cto", "eng-kernel", "eng-governance", "eng-platform"]
        is_active = role in active_roles
        dormant_roles = ["cso", "cfo"]
        is_dormant = role in dormant_roles

        team[role] = {
            "charter_lines": charter_lines,
            "has_principles": has_principles,
            "has_scope": has_scope,
            "czl_dispatches": czl_count,
            "status": "ACTIVE" if is_active else ("DORMANT" if is_dormant else "AVAILABLE"),
            "capability_evidence": "needs_assessment",
        }

    return team


# ── Infrastructure Scanner ──────────────────────────────────────────

def scan_infrastructure() -> dict:
    """Scan hooks, daemons, CIEU, ForgetGuard, session state."""
    infra = {}

    # Hook daemon
    hook_sock = "/tmp/ystar_hook.sock"
    infra["hook_daemon"] = {
        "socket_exists": os.path.exists(hook_sock),
        "status": "RUNNING" if os.path.exists(hook_sock) else "DOWN",
    }

    # CIEU database
    cieu_db = os.path.join(COMPANY_ROOT, ".ystar_cieu.db")
    if os.path.exists(cieu_db):
        size_kb = os.path.getsize(cieu_db) // 1024
        infra["cieu_db"] = {"exists": True, "size_kb": size_kb, "status": "LIVE"}
    else:
        infra["cieu_db"] = {"exists": False, "status": "MISSING"}

    # Aiden Brain
    brain_db = os.path.join(COMPANY_ROOT, "aiden_brain.db")
    if os.path.exists(brain_db):
        import sqlite3
        conn = sqlite3.connect(brain_db)
        nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        hebbian = conn.execute(
            "SELECT COUNT(*) FROM edges WHERE edge_type='hebbian'").fetchone()[0]
        conn.close()
        infra["aiden_brain"] = {
            "nodes": nodes, "edges": edges, "hebbian_learned": hebbian,
            "status": "LIVE"
        }
    else:
        infra["aiden_brain"] = {"status": "NOT_INITIALIZED"}

    # Session state
    session_json = os.path.join(COMPANY_ROOT, ".ystar_session.json")
    if os.path.exists(session_json):
        with open(session_json, "r", encoding="utf-8") as f:
            try:
                session = json.load(f)
                infra["session"] = {
                    "constraints": len(session.get("constraints", {})),
                    "status": "LOADED"
                }
            except json.JSONDecodeError:
                infra["session"] = {"status": "CORRUPT"}
    else:
        infra["session"] = {"status": "MISSING"}

    # ForgetGuard rules
    fg_rules = os.path.join(YGOV_ROOT, "ystar", "governance", "forget_guard_rules.yaml")
    if os.path.exists(fg_rules):
        with open(fg_rules, "r", encoding="utf-8") as f:
            content = f.read()
        rule_count = content.count("- name:")
        infra["forget_guard"] = {"rules": rule_count, "status": "LOADED"}
    else:
        infra["forget_guard"] = {"status": "NOT_FOUND"}

    # Key hook scripts
    hook_scripts = [
        "hook_client_labs.sh", "hook_wrapper.py", "hook_ceo_pre_output.py",
        "hook_pretool_agent_dispatch.py"
    ]
    for hs in hook_scripts:
        path = os.path.join(COMPANY_ROOT, "scripts", hs)
        infra[f"hook_{hs.split('.')[0]}"] = {
            "exists": os.path.exists(path),
            "lines": len(open(path).readlines()) if os.path.exists(path) else 0,
        }

    # CEO enforcement hook status
    infra["ceo_enforcement"] = {
        "pre_output_hook": "LIVE (CZL-159/160, format fixed 2026-04-17)",
        "code_write_block": "LIVE (constitutional, format fixed CZL-161)",
    }

    return infra


# ── Product Scanner (high-level, CTO does deep scan) ────────────────

def scan_products() -> dict:
    """High-level product status. CTO provides deep module scan."""
    products = {}

    # Y*gov
    if os.path.exists(YGOV_ROOT):
        py_files = list(Path(YGOV_ROOT, "ystar").rglob("*.py"))
        test_files = list(Path(YGOV_ROOT, "tests").rglob("test_*.py"))
        products["ygov"] = {
            "path": YGOV_ROOT,
            "source_files": len(py_files),
            "test_files": len(test_files),
            "status": "ACTIVE",
            "pypi_published": False,
            "local_install": True,
        }
    else:
        products["ygov"] = {"status": "NOT_FOUND"}

    # K9 Audit
    k9_path = "/tmp/K9Audit"
    products["k9_audit"] = {
        "path": k9_path,
        "exists": os.path.exists(k9_path),
        "status": "READ_ONLY",
        "license": "AGPL-3.0",
    }

    # Y*-Defuse
    products["ystar_defuse"] = {
        "status": "ABANDONED",
        "note": "Formally abandoned task #6, 2026-04-16",
    }

    # Gov-MCP
    mcp_test = os.path.join(YGOV_ROOT, "tests", "test_gov_mcp_delegation.py")
    mcp_doc = os.path.join(YGOV_ROOT, "docs", "gov_mcp_setup.md")
    products["gov_mcp"] = {
        "test_exists": os.path.exists(mcp_test),
        "doc_exists": os.path.exists(mcp_doc),
        "status": "UNCLEAR — needs CTO assessment",
    }

    return products


# ── Entanglement Map ───────────────────────────────────────────────

def build_entanglement_map() -> list:
    """Known team↔product entanglements from empirical evidence."""
    return [
        {
            "team_gap": "CTO lacks cross-layer system thinking",
            "product_gap": "No unified hook output spec/adapter",
            "evidence": "CZL-160 fixed one layer but missed daemon path + output format",
            "fix_yields": "CTO capability + hook architecture improvement",
        },
        {
            "team_gap": "Sub-agents hallucinate receipts (tool_uses=0)",
            "product_gap": "CIEU Gate 2 receipt validation partial",
            "evidence": "CZL-114 (Ethan), CZL-134 (Ryan) hallucinated",
            "fix_yields": "Trust system + automated verification",
        },
        {
            "team_gap": "CEO skips U-workflow for writing",
            "product_gap": "CEO enforcement hook was not LIVE",
            "evidence": "Case study + TS3L paper written without research",
            "fix_yields": "CEO discipline + hook enforcement pattern",
        },
        {
            "team_gap": "Ryan scope overflow (53-file commit)",
            "product_gap": "No pre-commit scope guard in product",
            "evidence": "d2852174 swept unrelated files",
            "fix_yields": "Scope discipline + scope enforcement feature",
        },
        {
            "team_gap": "Maya claim/reality mismatch",
            "product_gap": "Claim mismatch detector needs refinement",
            "evidence": "CZL-83 non-actionable classification questioned",
            "fix_yields": "Honest reporting culture + better detector",
        },
    ]


# ── Full Ecosystem Snapshot ─────────────────────────────────────────

def full_scan() -> dict:
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "team": scan_team(),
        "infrastructure": scan_infrastructure(),
        "products": scan_products(),
        "entanglement_map": build_entanglement_map(),
    }


def print_summary(snapshot: dict):
    """One-page ecosystem summary for CEO instant perception."""
    print("=" * 60)
    print("  Y* BRIDGE LABS — ECOSYSTEM SNAPSHOT")
    print(f"  {snapshot['timestamp']}")
    print("=" * 60)

    # Team
    print("\n── TEAM ──")
    for role, info in snapshot["team"].items():
        status = info["status"]
        czl = info["czl_dispatches"]
        marker = {"ACTIVE": "●", "DORMANT": "○", "AVAILABLE": "◌"}.get(status, "?")
        print(f"  {marker} {role:20s} [{status:9s}] CZL dispatches: {czl}")

    # Infrastructure
    print("\n── INFRASTRUCTURE ──")
    infra = snapshot["infrastructure"]
    for key in ["hook_daemon", "cieu_db", "aiden_brain", "session",
                "forget_guard", "ceo_enforcement"]:
        if key in infra:
            status = infra[key].get("status", "UNKNOWN")
            extra = ""
            if key == "aiden_brain" and status == "LIVE":
                extra = f" ({infra[key]['nodes']}n/{infra[key]['edges']}e/{infra[key]['hebbian_learned']}h)"
            if key == "forget_guard" and "rules" in infra[key]:
                extra = f" ({infra[key]['rules']} rules)"
            print(f"  {key:25s}: {status}{extra}")

    # Products
    print("\n── PRODUCTS ──")
    for name, info in snapshot["products"].items():
        status = info.get("status", "UNKNOWN")
        extra = ""
        if "source_files" in info:
            extra = f" ({info['source_files']} src, {info['test_files']} tests)"
        print(f"  {name:20s}: {status}{extra}")

    # Entanglement
    print(f"\n── ENTANGLEMENT MAP ({len(snapshot['entanglement_map'])} known pairs) ──")
    for ent in snapshot["entanglement_map"]:
        print(f"  Team: {ent['team_gap'][:45]}")
        print(f"  Prod: {ent['product_gap'][:45]}")
        print(f"  Fix→: {ent['fix_yields'][:45]}")
        print()

    print("=" * 60)


def import_to_brain(snapshot: dict):
    """Import ecosystem snapshot as nodes into Aiden Neural Network."""
    try:
        from aiden_brain import init_db, add_node, add_edge, DB_PATH
        init_db()

        # Add team member nodes
        for role, info in snapshot["team"].items():
            node_id = f"team/{role}"
            add_node(node_id, f"Team: {role}",
                     node_type="ecosystem_team",
                     dims={"y": 0.3, "x": 0.6, "z": 0.4, "t": 0.5,
                           "phi": 0.3, "c": 0.4},
                     summary=f"{info['status']}, {info['czl_dispatches']} CZLs",
                     db_path=DB_PATH)

        # Add product nodes
        for name, info in snapshot["products"].items():
            node_id = f"product/{name}"
            status = info.get("status", "UNKNOWN")
            add_node(node_id, f"Product: {name}",
                     node_type="ecosystem_product",
                     dims={"y": 0.5, "x": 0.7, "z": 0.6, "t": 0.5,
                           "phi": 0.4, "c": 0.3},
                     summary=status,
                     db_path=DB_PATH)

        # Add entanglement edges
        for i, ent in enumerate(snapshot["entanglement_map"]):
            ent_id = f"entanglement/{i}"
            add_node(ent_id, f"Entanglement: {ent['team_gap'][:30]}",
                     node_type="ecosystem_entanglement",
                     dims={"y": 0.6, "x": 0.5, "z": 0.5, "t": 0.7,
                           "phi": 0.8, "c": 0.6},
                     summary=ent["fix_yields"],
                     db_path=DB_PATH)

        # Connect entanglements to WHO_I_AM (CEO needs to see them)
        for i in range(len(snapshot["entanglement_map"])):
            add_edge("WHO_I_AM", f"entanglement/{i}", weight=0.6,
                     edge_type="ecosystem", db_path=DB_PATH)

        # Connect CTO to all product nodes
        add_edge("team/cto", "product/ygov", weight=0.9,
                 edge_type="ecosystem", db_path=DB_PATH)
        add_edge("team/cto", "product/gov_mcp", weight=0.5,
                 edge_type="ecosystem", db_path=DB_PATH)

        # Connect CEO to all team nodes
        for role in snapshot["team"]:
            add_edge("WHO_I_AM", f"team/{role}", weight=0.7,
                     edge_type="ecosystem", db_path=DB_PATH)

        print(f"\nImported {len(snapshot['team'])} team + "
              f"{len(snapshot['products'])} product + "
              f"{len(snapshot['entanglement_map'])} entanglement nodes into brain")

    except Exception as e:
        print(f"Brain import failed: {e}")


# ── Main ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--team" in sys.argv:
        team = scan_team()
        print(json.dumps(team, indent=2))
    elif "--infra" in sys.argv:
        infra = scan_infrastructure()
        print(json.dumps(infra, indent=2))
    elif "--summary" in sys.argv:
        snapshot = full_scan()
        print_summary(snapshot)
    else:
        snapshot = full_scan()
        print_summary(snapshot)
        import_to_brain(snapshot)

        # Save snapshot for future reference
        out_path = os.path.join(COMPANY_ROOT, "reports", "ceo",
                                "ecosystem_snapshot_latest.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        print(f"\nSnapshot saved to {out_path}")
