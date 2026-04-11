#!/usr/bin/env python3.11
"""Learning progress report - aggregate idle learning status across all agents.

Scans knowledge/{role}/ directories and reports:
- Priority 1 completion (role_definition files)
- Priority 2 theory count
- Priority 3 simulation count
- Last learning activity date

Usage:
    python3.11 scripts/learning_report.py
"""

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"

ROLES = ["ceo", "cto", "cmo", "cso", "cfo", "secretary"]

PRIORITY_1_FILES = [
    "world_class_standard.md",
    "role_heroes.md",
    "task_type_map.md",
]


def check_priority_1(actor: str) -> str:
    """Check role_definition completeness.

    Returns:
        "X/3" where X is number of files present
    """
    role_def_dir = KNOWLEDGE_ROOT / actor / "role_definition"
    if not role_def_dir.exists():
        return "0/3"

    present = sum(1 for f in PRIORITY_1_FILES if (role_def_dir / f).exists())
    return f"{present}/3"


def check_priority_2(actor: str) -> int:
    """Count theory entries.

    Returns:
        Number of .md files in theory/ directory
    """
    theory_dir = KNOWLEDGE_ROOT / actor / "theory"
    if not theory_dir.exists():
        return 0

    return len(list(theory_dir.glob("*.md")))


def check_priority_3(actor: str) -> int:
    """Count counterfactual simulations.

    Returns:
        Number of simulation_*.md files in gaps/ directory
    """
    gaps_dir = KNOWLEDGE_ROOT / actor / "gaps"
    if not gaps_dir.exists():
        return 0

    return len(list(gaps_dir.glob("simulation_*.md")))


def get_last_learning_date(actor: str) -> str:
    """Get date of last idle learning activity.

    Reads gemma_sessions.log and finds most recent idle_learning entry.

    Returns:
        "YYYY-MM-DD" or "Never"
    """
    gaps_dir = KNOWLEDGE_ROOT / actor / "gaps"
    log_path = gaps_dir / "gemma_sessions.log"

    if not log_path.exists():
        return "Never"

    try:
        last_timestamp = None
        with open(log_path, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("mode") == "idle_learning":
                        ts = entry.get("timestamp", 0)
                        if last_timestamp is None or ts > last_timestamp:
                            last_timestamp = ts
                except json.JSONDecodeError:
                    continue

        if last_timestamp:
            return time.strftime("%Y-%m-%d", time.localtime(last_timestamp))
        else:
            return "Never"
    except Exception:
        return "Never"


def main():
    print("=== Y* Bridge Labs Idle Learning Progress ===\n")

    # Table header
    print(f"{'Role':<12} | {'P1 Complete':<12} | {'P2 Theories':<12} | {'P3 Sims':<8} | {'Last Learning':<12}")
    print("-" * 70)

    for actor in ROLES:
        p1 = check_priority_1(actor)
        p2 = check_priority_2(actor)
        p3 = check_priority_3(actor)
        last_date = get_last_learning_date(actor)

        print(f"{actor:<12} | {p1:<12} | {p2:<12} | {p3:<8} | {last_date:<12}")

    print("\n=== Definitions ===")
    print("P1 Complete: world_class_standard.md + role_heroes.md + task_type_map.md")
    print("P2 Theories: Number of theory/*.md entries")
    print("P3 Sims:     Number of counterfactual simulations in gaps/")
    print("\nRun: python3.11 scripts/idle_learning.py --actor <role> --priority all")

    return 0


if __name__ == "__main__":
    sys.exit(main())
