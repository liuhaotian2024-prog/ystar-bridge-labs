from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, NEXT_MILESTONE, write_md


def write_e59_handoffs(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    chinese = [
        "E59 首先审计了 E50B/E57/E58 以及历史外部观察相关资产，确认可复用 source receipt、evidence atom、public-read-only policy 和治理 gate，不重新造轮子。",
        "E57 的 `external_page_read_adapter_unavailable` 被处理为：旧系统有证据/receipt 资产，但没有活跃可控 page-read runtime；E59 增加了薄适配器，并在无网络时明确返回 `live_public_read_unavailable_nonfatal`。",
        "外部世界智能 L5 已完成到 fixture/adapter/pipeline/readback 证明层；没有伪造 live fresh market read。",
        "外部知识观察和外部人类联系不同：读公开论文、公开文档、GitHub、技术博客是学习，不是联系专家或客户。",
        "这不等于客户验证、付费信号、专家反馈或市场验证。",
        "对 E58 case study 路线的影响：路线更适合用 runtime/governance/operations 语言包装，但 E60 仍需重新评估市场进入 readiness。",
        f"下一步应做 `{NEXT_MILESTONE}`：结合内部 L5 + 外部智能 L5 重新评估 money route 和 market entry readiness。",
        "真实外部联系仍然需要 owner approval；pending_owner_decision 不是 approval。",
    ]
    operator = [
        "E59 creates a reuse-first external intelligence L5 capability.",
        "The controlled adapter supports fixture reads and classifies live public reads as unavailable/nonfatal unless host/network is explicitly available.",
        "Source discovery is methodology-driven and open-ended; seed domains are not exhaustive.",
        "Public knowledge observation is permitted; human contact and contact scraping are forbidden.",
        f"Recommended next milestone: `{NEXT_MILESTONE}`.",
    ]
    write_md(root, "reports/integration/e59_owner_handoff_chinese.md", "E59 老板交接", chinese)
    write_md(root, "reports/integration/e59_operator_handoff.md", "E59 Operator Handoff", operator)
    return {"artifact_id": "e59_handoff_result", "recommended_next_milestone": NEXT_MILESTONE, "external_action_allowed": False}

