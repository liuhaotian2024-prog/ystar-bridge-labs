#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(DEFAULT_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(DEFAULT_REPO_ROOT))

from office.mission_command.c1_action_intent_packet import build_c1_action_intent_examples
from office.mission_command.c1_action_ledger import build_c1_action_ledger_template
from office.mission_command.c1_constitutional_envelope import build_c1_constitutional_envelope_request
from office.mission_command.c1_czl_closure import build_c1_czl_closure
from office.mission_command.c1_feedback_events import build_c1_feedback_event_template
from office.mission_command.c1_gov_mcp_execution_bridge import build_c1_gov_mcp_execution_contract
from office.mission_command.c1_readiness_report import build_c1_readiness_report
from office.mission_command.c1_signal_evaluator import evaluate_c1_signal
from office.mission_command.c1_y_gov_decision_bridge import evaluate_y_gov_decision


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_entry_report(readiness: dict[str, Any]) -> str:
    return f"""# C1 First Y*gov-Governed Real Action Readiness Package

## 人话摘要

C1 准备的是第一轮真实低风险动作的受治理执行包，不是执行动作本身。Owner 不再是操作员；owner 批准的是 7 天、最多 3 个低风险动作的 constitutional envelope。批准后，Aiden 产生 intent，Y*gov 判断，gov-mcp 执行或拒绝，action ledger / CIEU / feedback 回流。

## Most Ready Action

`{readiness['most_ready_low_risk_action']}`

## Required Owner Approval

{readiness['required_owner_approval']}

## Still Not Allowed

{chr(10).join('- ' + item for item in readiness['still_not_allowed'])}

## Live Execution

No live external action is executed in this milestone.
"""


def render_flow_report() -> str:
    return """# C1 Y*gov / gov-mcp Action Flow

```text
Aiden intent packet
-> Y*gov Pre-U/action packet validation
-> gov-mcp allow / deny / escalate
-> execution receipt if executed in a later approved cycle
-> action ledger
-> feedback event
-> CIEU residual candidate
-> learning candidate only after validation
```

The current milestone creates readiness artifacts only. It does not log in, send, submit, publish, create accounts, or write core memory/CIEU/brain state.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    ops = root / "operations" / "external_validation"
    reports = root / "reports" / "integration"

    envelope = build_c1_constitutional_envelope_request()
    packets = build_c1_action_intent_examples()
    contract = build_c1_gov_mcp_execution_contract()
    readiness = build_c1_readiness_report()
    signal_fixture = {
        "classifications": [
            "blocked_no_envelope",
            "denied_by_Y_gov",
            "denied_by_gov_mcp",
            "approved_not_executed",
            "executed_no_feedback_yet",
            "no_response_after_valid_action",
            "weak_positive",
            "strong_positive",
            "negative",
            "paid_signal_candidate",
            "invalid_feedback",
        ],
        "examples": {
            "blocked_no_envelope": evaluate_c1_signal(envelope_present=False),
            "approved_not_executed": evaluate_c1_signal(envelope_present=True, y_gov_decision="allow", gov_mcp_decision="allow"),
            "paid_signal_candidate": evaluate_c1_signal(
                envelope_present=True,
                y_gov_decision="allow",
                gov_mcp_decision="allow",
                action_executed=True,
                feedback_event={"feedback_source": "reply", "feedback_type": "asks_price", "paid_signal_candidate": True},
            ),
        },
    }

    write_json(ops / "c1_owner_constitutional_envelope.request.json", envelope.to_dict())
    write_json(ops / "c1_action_intent_examples.json", {"examples": [packet.to_dict() for packet in packets]})
    write_json(ops / "c1_gov_mcp_execution_contract.json", contract.to_dict())
    write_json(ops / "c1_action_ledger.template.json", build_c1_action_ledger_template())
    write_json(ops / "c1_feedback_events.template.json", build_c1_feedback_event_template())
    write_json(ops / "c1_signal_evaluator_fixture.json", signal_fixture)
    write_json(ops / "c1_governed_action_readiness_report.json", readiness)
    write_text(reports / "c1_governed_real_action_entry.md", render_entry_report(readiness))
    write_text(reports / "c1_y_gov_gov_mcp_action_flow.md", render_flow_report())
    write_text(
        reports / "c1_czl_closure.md",
        "# C1 CZL Closure\n\n```json\n" + json.dumps(build_c1_czl_closure(1), indent=2, ensure_ascii=False) + "\n```\n",
    )
    # Exercise the bridge once so generation fails if packet/envelope no longer align.
    decision = evaluate_y_gov_decision(packets[0].to_dict(), envelope.to_dict())
    if not decision.allowed:
        raise SystemExit(f"unexpected C1 readiness decision: {decision.to_dict()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
