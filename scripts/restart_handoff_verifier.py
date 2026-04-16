#!/usr/bin/env python3
"""Restart Handoff Verifier — Post-restart state persistence verification

Ultimate tier: Verify ALL state persistence artifacts exist + content readable after restart.

Authority: Jordan Lee CZL-145 P0 HEAVY (2026-04-16)
Upstream: Ethan CZL-137 standard 7-step restart + session_close_yml.py + governance_boot.sh
Downstream: CIEU replay recovery + auto-trigger integration

Usage:
    python3 scripts/restart_handoff_verifier.py [--json]

Output:
    Human-readable report (default) or JSON (--json flag)
    Exit code: 0 if gaps=0, 1 if gaps>0

Emits CIEU event:
    - RESTART_HANDOFF_GAP if gaps > 0
    - RESTART_HANDOFF_VERIFIED if all checks pass
"""

import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add Y-star-gov to path for CIEU recording
YSTAR_GOV_PATH = Path(__file__).parent.parent.parent / "Y-star-gov"
if YSTAR_GOV_PATH.exists():
    sys.path.insert(0, str(YSTAR_GOV_PATH))

sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import _get_current_agent

# Import after path setup
try:
    from ystar.governance.cieu import emit_cieu
except ImportError:
    def emit_cieu(*args, **kwargs):
        pass  # Fallback if ystar not available


COMPANY_ROOT = Path(__file__).parent.parent


def check_continuation_json() -> Dict:
    """Verify memory/continuation.json exists + has focus field"""
    path = COMPANY_ROOT / "memory/continuation.json"
    if not path.exists():
        return {"verified": False, "gap": "continuation.json missing"}

    try:
        data = json.loads(path.read_text())
        if "focus" not in data and "action_queue" not in data:
            return {"verified": False, "gap": "continuation.json missing focus/action_queue"}
        return {"verified": True, "hash": hash(path.read_text()) % 100000}
    except Exception as e:
        return {"verified": False, "gap": f"continuation.json unreadable: {e}"}


def check_session_summary() -> Dict:
    """Verify latest memory/session_summary_*.md exists + ≥500 words"""
    pattern = COMPANY_ROOT / "memory/session_summary_*.md"
    summaries = list(COMPANY_ROOT.glob("memory/session_summary_*.md"))

    if not summaries:
        return {"verified": False, "gap": "session_summary_*.md missing"}

    latest = max(summaries, key=lambda p: p.stat().st_mtime)
    try:
        content = latest.read_text()
        word_count = len(content.split())
        if word_count < 500:
            return {"verified": False, "gap": f"session_summary only {word_count} words (< 500)"}
        return {"verified": True, "hash": hash(content) % 100000, "words": word_count}
    except Exception as e:
        return {"verified": False, "gap": f"session_summary unreadable: {e}"}


def check_czl_subgoals() -> Dict:
    """Verify .czl_subgoals.json exists + campaign_status readable + remaining list populated"""
    path = COMPANY_ROOT / ".czl_subgoals.json"
    if not path.exists():
        return {"verified": False, "gap": ".czl_subgoals.json missing"}

    try:
        data = json.loads(path.read_text())
        if "campaign_status" not in data:
            return {"verified": False, "gap": ".czl_subgoals.json missing campaign_status"}
        if "remaining" not in data or not isinstance(data["remaining"], list):
            return {"verified": False, "gap": ".czl_subgoals.json missing/invalid remaining list"}
        return {"verified": True, "hash": hash(path.read_text()) % 100000, "remaining_count": len(data["remaining"])}
    except Exception as e:
        return {"verified": False, "gap": f".czl_subgoals.json unreadable: {e}"}


def check_priority_brief() -> Dict:
    """Verify reports/priority_brief.md exists + ≥300 words"""
    path = COMPANY_ROOT / "reports/priority_brief.md"
    if not path.exists():
        return {"verified": False, "gap": "priority_brief.md missing"}

    try:
        content = path.read_text()
        word_count = len(content.split())
        if word_count < 300:
            return {"verified": False, "gap": f"priority_brief only {word_count} words (< 300)"}
        return {"verified": True, "hash": hash(content) % 100000, "words": word_count}
    except Exception as e:
        return {"verified": False, "gap": f"priority_brief unreadable: {e}"}


def check_memory_md() -> Dict:
    """Verify memory/MEMORY.md exists + ≥10 entries"""
    path = COMPANY_ROOT / "memory/MEMORY.md"
    if not path.exists():
        return {"verified": False, "gap": "MEMORY.md missing"}

    try:
        content = path.read_text()
        # Count lines starting with "- [" (markdown list entries)
        entry_lines = [line for line in content.split('\n') if line.strip().startswith('- [')]
        if len(entry_lines) < 10:
            return {"verified": False, "gap": f"MEMORY.md only {len(entry_lines)} entries (< 10)"}
        return {"verified": True, "hash": hash(content) % 100000, "entries": len(entry_lines)}
    except Exception as e:
        return {"verified": False, "gap": f"MEMORY.md unreadable: {e}"}


def check_engineer_trust_scores() -> Dict:
    """Verify knowledge/engineer_trust_scores.json exists + 9 entries"""
    path = COMPANY_ROOT / "knowledge/engineer_trust_scores.json"
    if not path.exists():
        return {"verified": False, "gap": "engineer_trust_scores.json missing"}

    try:
        data = json.loads(path.read_text())
        if len(data) < 9:
            return {"verified": False, "gap": f"engineer_trust_scores.json only {len(data)} entries (< 9)"}
        return {"verified": True, "hash": hash(path.read_text()) % 100000, "count": len(data)}
    except Exception as e:
        return {"verified": False, "gap": f"engineer_trust_scores.json unreadable: {e}"}


def check_agent_files() -> Dict:
    """Verify .claude/agents/*.md — 14 files exist + model field present"""
    agent_dir = COMPANY_ROOT / ".claude/agents"
    if not agent_dir.exists():
        return {"verified": False, "gap": ".claude/agents/ directory missing"}

    agent_files = list(agent_dir.glob("*.md"))
    if len(agent_files) < 14:
        return {"verified": False, "gap": f"Only {len(agent_files)}/14 agent files exist"}

    # Spot-check 3 files for model field
    sample = agent_files[:3]
    for f in sample:
        content = f.read_text()
        if "model:" not in content.lower():
            return {"verified": False, "gap": f"{f.name} missing model field"}

    return {"verified": True, "count": len(agent_files)}


def check_daemons() -> Dict:
    """Verify 4 daemons alive (pgrep)"""
    daemons = [
        "k9_routing_subscriber",
        "k9_alarm_consumer",
        "cto_dispatch_broker",
        "engineer_task_subscriber"
    ]

    alive = []
    dead = []

    for daemon in daemons:
        result = subprocess.run(["pgrep", "-f", daemon], capture_output=True)
        if result.returncode == 0:
            alive.append(daemon)
        else:
            dead.append(daemon)

    if dead:
        return {"verified": False, "gap": f"Daemons dead: {', '.join(dead)}"}

    return {"verified": True, "alive": alive}


def verify_post_restart() -> Dict:
    """Run all verification checks and aggregate results"""
    checks = {
        "continuation_json": check_continuation_json(),
        "session_summary": check_session_summary(),
        "czl_subgoals": check_czl_subgoals(),
        "priority_brief": check_priority_brief(),
        "memory_md": check_memory_md(),
        "engineer_trust_scores": check_engineer_trust_scores(),
        "agent_files": check_agent_files(),
        "daemons": check_daemons(),
    }

    verified = sum(1 for c in checks.values() if c["verified"])
    total = len(checks)
    gaps = [f"{name}: {c['gap']}" for name, c in checks.items() if not c["verified"]]

    hash_map = {name: c.get("hash", 0) for name, c in checks.items() if c["verified"]}

    return {
        "verified": verified,
        "total": total,
        "gaps": gaps,
        "hash_map": hash_map,
        "checks": checks
    }


def main():
    """CLI entry point"""
    json_output = "--json" in sys.argv

    result = verify_post_restart()

    # Emit CIEU event
    agent_id = _get_current_agent()
    if result["gaps"]:
        emit_cieu(
            "RESTART_HANDOFF_GAP",
            agent_id=agent_id,
            metadata={
                "verified": result["verified"],
                "total": result["total"],
                "gaps": result["gaps"]
            }
        )
    else:
        emit_cieu(
            "RESTART_HANDOFF_VERIFIED",
            agent_id=agent_id,
            metadata={
                "verified": result["verified"],
                "total": result["total"]
            }
        )

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print("=== Restart Handoff Verification Report ===")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Verified: {result['verified']}/{result['total']}")
        print()

        if result["gaps"]:
            print("❌ GAPS DETECTED:")
            for gap in result["gaps"]:
                print(f"  - {gap}")
            print()
        else:
            print("✅ All state persistence checks PASSED")
            print()

        print("Artifact Hashes:")
        for name, h in result["hash_map"].items():
            print(f"  {name}: {h}")

    sys.exit(1 if result["gaps"] else 0)


if __name__ == "__main__":
    main()
