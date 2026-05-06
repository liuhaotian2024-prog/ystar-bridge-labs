from __future__ import annotations

from pathlib import Path
from typing import Any

from .e58_case_study_boundary import BRIDGE_ROOT, NEXT_MILESTONE, write_md


def write_e58_handoffs(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    chinese_lines = [
        "E57 把赚钱路线从单一 proof packet 升级为 AI Agent Company Runtime Harness Case Study，因为 E54/E55/E56 之后，系统证明的不再只是一个工具层包，而是一个内部 L5 公司运行时。",
        "E58 包装了 case study、证据链、架构说明、no-overclaim 边界、老板审阅包、外部智能缺口声明，以及 E59 requirements packet。",
        "它证明的是内部 L5 runtime harness：CEO brain、行为中枢、内部 operating loop、证据闭环、anti-drift 和 capability binding 都能协同工作。",
        "它没有证明客户验证、付费需求、real MCP transport、外部专家评价、生产可用、市场最新情报或 external intelligence L5。",
        "现在仍不能真实联系用户，因为 owner_decision_status 还是 pending_owner_decision，而且 E59 外部世界智能 L5 尚未完成。",
        "必须做 E59，因为 E57 的 public-read-only evidence refresh 被 external_page_read_adapter_unavailable 阻断；E59 要先审计并复用现有外部观察能力，不能重新造轮子。",
        "E59 完成后，再做 E60 市场进入 readiness retest，届时再判断是否准备 owner-approved controlled external review。",
    ]
    operator_lines = [
        "E58 packages the E57-selected `AI_agent_company_runtime_harness_case_study` route as owner-reviewable material only.",
        "The case study inherits E52 proof-packet evidence and E54/E55/E56 L5 runtime evidence, then records the E57 route shift.",
        "External World Intelligence / Technology Capture / Market Learning L5 remains incomplete and is explicitly assigned to E59.",
        "External action remains blocked; pending owner decision is not approval.",
        f"Recommended next milestone: `{NEXT_MILESTONE}`.",
    ]
    write_md(root, "reports/integration/e58_owner_handoff_chinese.md", "E58 老板交接", chinese_lines)
    write_md(root, "reports/integration/e58_operator_handoff.md", "E58 Operator Handoff", operator_lines)
    return {
        "artifact_id": "e58_handoff_result",
        "owner_handoff": "reports/integration/e58_owner_handoff_chinese.md",
        "operator_handoff": "reports/integration/e58_operator_handoff.md",
        "recommended_next_milestone": NEXT_MILESTONE,
        "external_action_allowed": False,
    }

