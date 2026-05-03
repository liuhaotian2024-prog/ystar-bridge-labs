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

from office.mission_command.b2r_capability_domains import build_capability_domains
from office.mission_command.b2r_c1_entry_gate import build_c1_entry_gate
from office.mission_command.b2r_czl_closure import build_b2r_czl_closure
from office.mission_command.b2r_gov_mcp_execution_contract import build_gov_mcp_execution_contract
from office.mission_command.b2r_owner_constitutional_envelope import build_owner_constitutional_envelope_request
from office.mission_command.b2r_progressive_unlock import build_progressive_unlock_matrix
from office.mission_command.b2r_y_gov_action_packet import build_action_packet


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_runtime_report() -> str:
    return """# B2R Y*gov-Governed External Action Runtime

## 人话摘要

B2R 把 owner 从操作员位置移回宪法级授权者位置。登录、表单、发布、账号创建和低风险验证消息不再被永久 hard-block；它们被建模为 Y*gov-governed capability domains，由 gov-mcp 执行或拒绝。

本 milestone 不执行真实外部动作。它只建立 governed runtime、契约、测试和 C1 readiness gate。

## Architecture

```text
Aiden intent
-> Y*gov Pre-U/action packet validation
-> gov-mcp execute_or_deny contract
-> action ledger / CIEU residual / feedback
-> only hard exceptions escalate owner
```

## Owner Role

Owner approves constitutional envelopes, financial/legal exceptions, customer-system access, and canonical core writeback. Owner should not be the default person clicking buttons, logging in, filling ordinary forms, publishing approved low-risk content, or sending every envelope-compliant validation message.

## Still Hard-Gated

- payment
- contract
- legal obligation
- financial commitment
- customer system access
- regulated/government/tax/immigration/identity forms
- credential disclosure
- core brain/CIEU/memory canonical writeback
"""


def render_unlock_report() -> str:
    matrix = build_progressive_unlock_matrix()
    lines = ["# B2R Progressive Capability Unlock", ""]
    for level in matrix["levels"]:
        lines += [
            f"## Level {level['level']}: {level['name']}",
            f"- domains: {', '.join(level['capability_domains']) or 'internal only'}",
            f"- owner role: {level['owner_role']}",
            f"- stop conditions: {', '.join(level['stop_conditions'])}",
            "",
        ]
    return "\n".join(lines)


def render_cross_repo_plan() -> str:
    return """# B2R Cross-Repo Integration Plan

## Y-star-gov should own

- normative governance kernel
- Pre-U/action packet validation
- CIEU/residual standards
- approval/envelope validity standards
- progressive capability policy
- live boundary / no-go standards

## gov-mcp should own

- tool execution gateway
- MCP/action preflight
- execute/deny contract
- result normalization
- tool evidence envelope
- action execution receipts
- rollback/takedown wrappers where needed

## ystar-bridge-labs should own

- Aiden/CEO runtime
- commercial validation loop
- offer/target/evidence/action intent generation
- owner/board interface
- feedback interpretation

## ystar-company should own

- historical incubator artifacts only
- backflow candidates
- no final source-of-truth status unless promoted

## Integration status

This task creates bridge-labs-side interface contracts and plans only. It does not modify Y-star-gov, gov-mcp, or ystar-company source code.
"""


def render_c1_report() -> str:
    gate = build_c1_entry_gate()
    return f"""# B2R C1 Governed Action Entry Gate

## Status

`{gate['status']}`

C1 can prepare the first real governed action cycle, but this milestone does not execute it.

## Supported readiness paths

{chr(10).join('- ' + item for item in gate['supported_readiness_paths'])}

## Hard blocks

{chr(10).join('- ' + item for item in gate['hard_blocks'])}

## CIEU / Residual

{gate['cieu_residual_semantics']}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    ops = root / "operations" / "external_validation"
    reports = root / "reports" / "integration"

    write_json(ops / "b2r_progressive_capability_unlock_matrix.json", build_progressive_unlock_matrix())
    write_json(ops / "b2r_owner_constitutional_envelope.request.json", build_owner_constitutional_envelope_request())
    write_json(
        ops / "b2r_action_packet_examples.json",
        {
            "examples": [build_action_packet(domain.domain_id).to_dict() for domain in build_capability_domains()],
            "gov_mcp_contract": build_gov_mcp_execution_contract().to_dict(),
        },
    )
    write_json(
        ops / "b2r_escalation_policy.json",
        {
            "hard_owner_gates": build_owner_constitutional_envelope_request()["hard_owner_gates"],
            "escalate_on": ["out_of_envelope", "negative_feedback", "opt_out", "complaint", "budget_exceeded", "credential_missing", "mfa_required"],
            "owner_is_operator": False,
        },
    )
    write_json(ops / "b2r_c1_governed_action_entry_gate.json", build_c1_entry_gate())

    write_text(reports / "b2r_y_gov_governed_external_action_runtime.md", render_runtime_report())
    write_text(reports / "b2r_progressive_capability_unlock.md", render_unlock_report())
    write_text(reports / "b2r_cross_repo_integration_plan.md", render_cross_repo_plan())
    write_text(reports / "b2r_c1_entry_gate.md", render_c1_report())
    write_text(
        reports / "b2r_czl_closure.md",
        "# B2R CZL Closure\n\n```json\n"
        + json.dumps(build_b2r_czl_closure(repository_delivery_rt1=1), indent=2, ensure_ascii=False)
        + "\n```\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
