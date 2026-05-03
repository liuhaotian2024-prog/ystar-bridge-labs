#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]

APPROVAL_TEXT = """I approve owner-operated manual validation for the E14 batch only.
I will manually send the approved E14 draft to the selected targets.
This approval does not authorize Aiden or any agent to send messages, publish, collect payment, create accounts, submit forms, log in, or write to core brain/CIEU/memory.
Valid action ledger entries and feedback events are required before E15."""

NOT_APPROVED = [
    "Aiden autonomous sending",
    "Codex/Aiden customer contact",
    "email/message sending by any agent",
    "publication",
    "payment collection",
    "account creation",
    "form submission",
    "login",
    "tracking links or attachments unless separately approved",
    "core brain/CIEU/memory writeback",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_targets(repo_root: Path, target_ids: list[str]) -> list[dict[str, Any]]:
    candidates = read_json(repo_root / "operations/external_validation/e14_target_candidates.json")["candidates"]
    by_id = {item["target_id"]: item for item in candidates}
    return [by_id[target_id] for target_id in target_ids if target_id in by_id]


def build_console(repo_root: Path) -> dict[str, Any]:
    approval = read_json(repo_root / "operations/external_validation/e14_owner_approval_packet.request.json")
    batch = read_json(repo_root / "operations/external_validation/e14_target_batch.proposed.json")
    signal = read_json(repo_root / "operations/external_validation/e14_validation_signal_report.json")
    decision = read_json(repo_root / "operations/external_validation/e14_owner_decision_packet.json")
    draft_md = (repo_root / "operations/external_validation/e14_manual_send_draft.md").read_text(encoding="utf-8")
    targets = selected_targets(repo_root, batch["selected_target_ids"])
    choices = [
        {
            "choice": "approve_owner_operated_manual_validation",
            "meaning": "Owner personally sends the approved draft to the selected targets only.",
            "requires": ["valid owner approval", "owner execution", "action ledger", "feedback event before E15"],
            "aiden_sends": False,
        },
        {
            "choice": "request_revision",
            "meaning": "Revise target batch, channel, or draft; no sending.",
            "requires": ["new owner review packet"],
            "aiden_sends": False,
        },
        {
            "choice": "hold",
            "meaning": "Take no action; E15 remains blocked.",
            "requires": [],
            "aiden_sends": False,
        },
        {
            "choice": "reject_current_path",
            "meaning": "Reject this validation path and return to offer/target revision.",
            "requires": ["return to E13R or alternate offer path"],
            "aiden_sends": False,
        },
    ]
    return {
        "console_id": "b1_e14_owner_decision_console",
        "generated_at": utc_now(),
        "recommended_action": "approve_owner_operated_manual_validation",
        "approval_status": approval["status"],
        "signal_classification": signal["classification"],
        "e15_entry_allowed": False,
        "exact_offer": approval["exact_offer"],
        "target_batch_id": batch["batch_id"],
        "selected_targets": targets,
        "manual_send_draft": draft_md,
        "copyable_approval_text": APPROVAL_TEXT,
        "owner_choices": choices,
        "what_is_approved_if_owner_accepts": approval["what_is_approved_if_owner_accepts"],
        "what_is_not_approved": NOT_APPROVED,
        "risk_boundary": {
            "owner_operated_only": True,
            "aiden_or_codex_sending_authorized": False,
            "max_sends": approval["max_sends"],
            "allowed_channel": approval["allowed_channel"],
            "stop_conditions": approval["stop_conditions"],
            "approval_expiration": approval["expiration"],
            "revocation_rule": approval["revocation_rule"],
        },
        "feedback_recording_instructions": {
            "strong_positive": "明确表达付费意愿、要求价格/下一步，或提出真实工作流并要求继续。",
            "weak_positive": "表示感兴趣、要求示例、要求更多说明，但没有预算或具体下一步。",
            "negative": "明确说不需要、没有紧迫性、已有替代方案、价格/信任/时机不合适。",
            "no_response_after_valid_action": "只有 owner 已记录有效 action ledger，并过了模板中 no_response_allowed_after_date 后才可记录。",
            "invalid_feedback": "没有 action_id、不是 owner-entered、来自 public evidence、凭空推断、或没有真实回复来源。",
            "paid_signal_candidate": "必须有有效 action ledger + 真实反馈事件，并包含预算/付费/下一步信号；public evidence 不算。",
        },
        "valid_feedback_examples": [
            "They ask for price and describe a current AI-agent rollout problem.",
            "They say a readiness review would help and ask for a concrete next step.",
            "They describe unsafe coding-agent changes and ask what the 48h review includes.",
        ],
        "invalid_feedback_examples": [
            "A public pricing page or blog post treated as customer feedback.",
            "No-response recorded before any valid owner action ledger exists.",
            "A guessed buyer reaction inferred from target rationale.",
        ],
        "e15_entry_rules": [
            "valid owner approval exists",
            "valid action ledger exists for the sent draft and selected target",
            "valid owner-entered feedback event exists",
            "E14 signal evaluator classifies weak_positive, strong_positive, negative, or paid_signal_candidate from real feedback",
            "no public evidence is treated as validation feedback",
        ],
        "architecture_note": {
            "owner_operated_is_transitional": True,
            "long_term_direction": "Aiden intent -> Y*gov governance decision -> gov-mcp execute/deny -> action ledger/CIEU/feedback -> only hard exceptions escalate owner",
            "owner_role": "constitutional_boundary_setter_not_operator",
        },
        "source_packets": {
            "approval_request": "operations/external_validation/e14_owner_approval_packet.request.json",
            "target_batch": "operations/external_validation/e14_target_batch.proposed.json",
            "manual_draft": "operations/external_validation/e14_manual_send_draft.md",
            "action_ledger_template": "operations/external_validation/e14_action_ledger.template.json",
            "feedback_event_template": "operations/external_validation/e14_feedback_events.template.json",
            "decision_packet": "operations/external_validation/e14_owner_decision_packet.json",
        },
        "upstream_decision_packet": decision,
    }


def target_table(targets: list[dict[str, Any]]) -> str:
    rows = [
        "| target | segment | why | status |",
        "|---|---|---|---|",
    ]
    for target in targets:
        rows.append(
            "| {name} (`{target_id}`) | {segment} | {why} | no contact until owner approval |".format(
                name=target["organization_or_person_name"],
                target_id=target["target_id"],
                segment=target["segment"],
                why=target["relevance_to_offer"],
            )
        )
    return "\n".join(rows)


def render_markdown(console: dict[str, Any]) -> str:
    draft = console["manual_send_draft"].strip()
    return f"""# E14 Owner Decision Console

## 人话摘要

你现在要批准的不是“让 Aiden 发消息”，也不是“进入 E15”。你要决定的是：是否由 owner 亲自、手动、最多向 3 个已选目标发送这版 E14 草稿，并在发送后按模板记录 action ledger 和真实反馈。

当前状态：`{console['signal_classification']}`。没有 owner approval、没有 action ledger、没有 feedback event，所以 E15 仍然 blocked。

## 长期架构提醒

B1 是过渡层，不是长期架构。长期方向不是 owner-operated，而是：

```text
{console['architecture_note']['long_term_direction']}
```

Owner 的长期角色应该是 `{console['architecture_note']['owner_role']}`，不是人工操作员。

## 推荐选择

`approve_owner_operated_manual_validation`

- owner personally sends to selected targets.
- Aiden/Codex does not send.
- action ledger required.
- feedback event required before E15.

## 可复制批准文本

```text
{console['copyable_approval_text']}
```

## Selected Targets

{target_table(console['selected_targets'])}

## Manual-Send Draft

{draft}

## 风险边界

- approved if accepted: {', '.join(console['what_is_approved_if_owner_accepts'])}
- not approved: {', '.join(console['what_is_not_approved'])}
- max sends: {console['risk_boundary']['max_sends']}
- allowed channel: {console['risk_boundary']['allowed_channel']}
- expiration: {console['risk_boundary']['approval_expiration']}

## Owner Choices

1. `approve_owner_operated_manual_validation`: owner 手动发送；Aiden 不发送；必须记录 action ledger 和 feedback event。
2. `request_revision`: 修改目标批次或草稿；不发送。
3. `hold`: 暂停；E15 blocked。
4. `reject_current_path`: 否定当前路径；回到 E13R 或替代 offer。

## 反馈记录说明

- `strong_positive`: {console['feedback_recording_instructions']['strong_positive']}
- `weak_positive`: {console['feedback_recording_instructions']['weak_positive']}
- `negative`: {console['feedback_recording_instructions']['negative']}
- `no_response_after_valid_action`: {console['feedback_recording_instructions']['no_response_after_valid_action']}
- `invalid_feedback`: {console['feedback_recording_instructions']['invalid_feedback']}
- `paid_signal_candidate`: {console['feedback_recording_instructions']['paid_signal_candidate']}

## 有效反馈例子

- {console['valid_feedback_examples'][0]}
- {console['valid_feedback_examples'][1]}
- {console['valid_feedback_examples'][2]}

## 无效反馈例子

- {console['invalid_feedback_examples'][0]}
- {console['invalid_feedback_examples'][1]}
- {console['invalid_feedback_examples'][2]}

## E15 Entry Rules

E15 只有在以下条件全部满足时才允许进入：

- valid owner approval exists.
- valid action ledger exists.
- valid owner-entered feedback event exists.
- feedback is not public evidence and not guessed.
- E14 signal evaluator sees real validation signal.

## Safety Receipt

- no customer contact by Aiden/Codex
- no email/message sent by Aiden/Codex
- no publication
- no payment
- no account creation
- no form submission
- no login
- no core brain/CIEU/memory writeback
"""


def render_explainer(console: dict[str, Any]) -> str:
    return f"""# E14 Owner Decision Explainer

## 这是什么

B1 把 E14 的 JSON packet 翻译成 owner 可读的决策台。它回答：批准什么、谁发、发给谁、发什么、风险是什么、回复怎么记录、什么情况下才能进入 E15。

## 现在不是什么

这不是客户外联执行；不是 Aiden 自动发送；不是市场验证完成；不是 paid signal；不是进入 E15。B1 也是过渡解释层，不是长期 owner-operated 架构。

## 当前判断

- recommended action: `{console['recommended_action']}`
- approval status: `{console['approval_status']}`
- signal classification: `{console['signal_classification']}`
- E15 entry allowed: `{console['e15_entry_allowed']}`
- selected target count: `{len(console['selected_targets'])}`

## Owner 下一步

如果 owner 认可目标、草稿、通道和边界，可以复制 approval text，并且由 owner 本人手动发送。发送后必须记录 action ledger；收到回复后必须记录 feedback event。没有这两类记录，E15 继续 blocked。

## Long-Term Direction

`{console['architecture_note']['long_term_direction']}`

Owner 应回到宪法级授权者位置；Y*gov 是治理主体，gov-mcp 是执行或拒绝网关。

## CZL

- B1 decision_console_rt1: 0
- B1 approval_execution_rt1: 1 until owner approves and executes manually
- B1 feedback_capture_rt1: 1 until valid feedback event exists
- B1 repository_delivery_rt1: 1 until host-side delivery confirms remote SHA
- B1 full_mission_rt1: 1 because no approval/action/feedback occurred
"""


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    console = build_console(repo_root)
    write_json(repo_root / "operations/external_validation/e14_owner_decision_console.json", console)
    (repo_root / "operations/external_validation/e14_owner_decision_console.md").write_text(
        render_markdown(console), encoding="utf-8"
    )
    explainer = repo_root / "reports/integration/e14_owner_decision_explainer.md"
    explainer.parent.mkdir(parents=True, exist_ok=True)
    explainer.write_text(render_explainer(console), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
