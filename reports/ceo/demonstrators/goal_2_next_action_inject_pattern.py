"""
Goal 2 Demonstrator — 每 agent 明确路径 + 边界 (不错做也不空转)

Audience: Board (Goal 2 pattern evidence — not production wire).
Research basis: OmissionEngine is a detector. Dispatch_board is a
queue. Neither actively surfaces "next action" to the agent — agent
must ask. This script demonstrates the inject pattern that Y*gov
should implement so the agent receives NEXT_ACTION without asking.
Synthesis: 不空转 = "next action always surfaced by system". This
demonstrator proves the pattern is achievable with current data.

Run: python3 reports/ceo/demonstrators/goal_2_next_action_inject_pattern.py <agent_id>
Output: prints formatted NEXT hint to stdout; writes to file.
"""
import json
import sys
import time
from pathlib import Path

BOARD = "/Users/haotianliu/.openclaw/workspace/ystar-company/governance/dispatch_board.json"
OBLIG_LOG = "/Users/haotianliu/.openclaw/workspace/ystar-company/governance/active_dispatch_log.md"
OUT = "/Users/haotianliu/.openclaw/workspace/ystar-company/reports/ceo/demonstrators/goal_2_output.txt"


def _read_board():
    if not Path(BOARD).exists():
        return {"tasks": []}
    try:
        with open(BOARD, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"tasks": []}


def next_for_agent(agent_id: str) -> str:
    board = _read_board()
    # Rule 1: claimed task not yet completed → continue it
    for t in board.get("tasks", []):
        if t.get("status") == "claimed" and t.get("claimed_by") == agent_id:
            return (
                f"NEXT: resume claimed task {t['atomic_id']}\n"
                f"  scope: {t.get('scope','')}\n"
                f"  desc:  {(t.get('description') or '')[:140]}"
            )
    # Rule 2: open task → claim the highest-priority open
    open_tasks = [t for t in board.get("tasks", []) if t.get("status") == "open"]
    priority_rank = {"P0": 0, "P1": 1, "P2": 2}
    open_tasks.sort(key=lambda t: (priority_rank.get(t.get("urgency", "P2"), 9)))
    if open_tasks:
        t = open_tasks[0]
        return (
            f"NEXT: python3 scripts/dispatch_board.py claim "
            f"--atomic_id {t['atomic_id']} --claimed_by {agent_id}\n"
            f"  urgency: {t.get('urgency','?')}\n"
            f"  scope:   {t.get('scope','')}"
        )
    # Rule 3: no tasks → suggest introspection
    return (
        "NEXT: no open or claimed tasks for this agent.\n"
        f"  Suggested: python3 scripts/learning_report.py --agent {agent_id}\n"
        "  Rationale: idle window is ideal for meta-learning."
    )


if __name__ == "__main__":
    agent_id = sys.argv[1] if len(sys.argv) > 1 else "eng-kernel"
    hint = next_for_agent(agent_id)
    Path(OUT).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%S')}\n")
        f.write(f"Agent: {agent_id}\n\n{hint}\n")
    print(hint)
