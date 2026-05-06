from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e58_case_study_boundary import BRIDGE_ROOT, NEXT_MILESTONE, PRODUCT_DIR, write_json, write_md


def build_owner_review_packet() -> dict[str, Any]:
    return {
        "artifact_id": "e58_owner_review_packet_result",
        "packet_status": "owner_reviewable_only",
        "owner_decision_status": "pending_owner_decision",
        "approval_fabricated": False,
        "external_action_allowed": False,
        "what_owner_can_approve_now": ["continue_internal_E59_external_world_intelligence_L5_convergence"],
        "what_owner_cannot_approve_implicitly": ["outreach", "publication", "customer validation claim", "paid signal claim", "real MCP transport claim"],
        "next_recommended_milestone": NEXT_MILESTONE,
        "no_external_action": True,
    }


def write_owner_review_package(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_owner_review_packet()
    write_json(root, "operations/external_validation/e58_owner_review_packet_result.json", data)
    write_json(root, str(PRODUCT_DIR / "owner_review_packet.json"), data)
    lines = [
        "这个 case study 是 AI agent company runtime harness 的内部 L5 证明包。",
        "它证明：CEO brain L5、行为中枢 L5、内部公司 operating loop L5、证据闭环和 E57 路线重选已经完成。",
        "它没有证明：客户验证、付费需求、外部专家评价、real MCP transport closure、生产可用或市场最新情报。",
        "老板应阅读 README、executive_brief、proof_chain、commercial_route_shift、external_intelligence_gap、e59_requirements_packet。",
        "它比 E52 proof packet 高阶，因为 E52 是单一 proof packet，E58 包装的是完整 L5 公司运行时 harness。",
        "现在仍不能外联，因为 owner_decision_status 仍是 pending_owner_decision，pending 不是 approval。",
        "E59 是下一步，因为外部世界智能 / 技术捕捉 / 市场学习 L5 还没有完成。",
        "如果老板批准，当前只能批准继续内部 E59，不是批准外联、发布、识别真人或联系任何人。",
        "如果老板不同意，应要求补：更清晰的证据链、更保守的语言、或先补 real MCP transport / K9 写集成。",
    ]
    write_md(root, str(PRODUCT_DIR / "owner_review_packet.md"), "E58 Owner Review Packet", lines)
    write_md(root, "reports/integration/e58_owner_review_packet_chinese.md", "E58 老板审阅包", lines)
    return data

