#!/usr/bin/env python3
"""Role-grounded routing for the recovered Y*Bridge Labs team."""

from __future__ import annotations

from typing import Any


AGENT_ROLES: dict[str, dict[str, Any]] = {
    "aiden_ceo": {
        "display_name": "Aiden Liu",
        "role": "CEO",
        "keywords": ["goal", "strategy", "route", "delegate", "team", "整体", "团队", "目标", "战略"],
    },
    "ethan_cto": {
        "display_name": "Ethan Wright",
        "role": "CTO",
        "keywords": ["tool", "code", "test", "architecture", "implementation", "builder", "工具", "代码", "测试", "架构"],
    },
    "sofia_cmo": {
        "display_name": "Sofia Blake",
        "role": "CMO",
        "keywords": ["message", "positioning", "content", "narrative", "marketing", "文案", "定位", "叙事", "增长"],
    },
    "marco_cfo": {
        "display_name": "Marco Rivera",
        "role": "CFO",
        "keywords": ["price", "pricing", "cash", "revenue", "finance", "money", "钱", "收入", "定价", "现金"],
    },
    "zara_cso": {
        "display_name": "Zara Johnson",
        "role": "CSO",
        "keywords": ["sales", "customer", "buyer", "commercial", "offer", "patent", "销售", "客户", "买家", "商业", "报价"],
    },
    "samantha_secretary": {
        "display_name": "Samantha Lin",
        "role": "Secretary",
        "keywords": ["archive", "index", "record", "organize", "dna", "秘书", "归档", "索引", "记录"],
    },
    "leo_engineer": {
        "display_name": "Leo Chen",
        "role": "Kernel Engineer",
        "keywords": ["kernel", "compiler", "runtime", "内核", "编译"],
    },
    "maya_engineer": {
        "display_name": "Maya Patel",
        "role": "Governance Engineer",
        "keywords": ["governance", "policy", "approval", "boundary", "risk", "治理", "审批", "边界", "风险"],
    },
    "ryan_engineer": {
        "display_name": "Ryan Park",
        "role": "Platform Engineer",
        "keywords": ["platform", "server", "ui", "api", "hook", "平台", "网页", "接口"],
    },
    "jordan_engineer": {
        "display_name": "Jordan Lee",
        "role": "Domains Engineer",
        "keywords": ["domain", "template", "workflow", "openclaw", "模板", "工作流"],
    },
    "jinjin_k9_scout": {
        "display_name": "Jinjin / K9 Scout",
        "role": "Research / Cross-model Scout",
        "keywords": ["research", "scan", "observe", "source", "evidence", "market", "调研", "观察", "证据", "市场"],
    },
}

FORBIDDEN_ACTIONS = [
    "external outreach",
    "email sending",
    "customer contact",
    "publication",
    "payment",
    "form submission",
    "account creation",
    "grant/RFP submission",
    "MCP/live behavior",
    "actual memory/brain/canonical/CIEU DB writeback",
]

APPROVAL_REQUIRED_FOR = [
    "outreach",
    "publication",
    "payment",
    "account creation",
    "form submission",
    "grant/RFP submission",
    "customer contact",
    "MCP/live behavior",
    "actual memory/brain/canonical/CIEU DB writeback",
]


def score_agents(text: str) -> dict[str, int]:
    lowered = text.lower()
    scores = {agent_id: 0 for agent_id in AGENT_ROLES}
    for agent_id, profile in AGENT_ROLES.items():
        for keyword in profile["keywords"]:
            if keyword.lower() in lowered:
                scores[agent_id] += 1
    return scores


def route_owner_goal(text: str, target: str = "whole_team") -> dict[str, Any]:
    """Create an Aiden-led routing decision using only legacy team roles."""
    normalized_target = target.strip() or "whole_team"
    lowered = text.lower()
    scores = score_agents(text)
    supporting = [agent_id for agent_id, score in sorted(scores.items(), key=lambda item: (-item[1], item[0])) if score > 0]
    if any(term in lowered for term in ["first cash", "first revenue", "first money", "第一笔钱", "赚钱", "收入", "兑现"]):
        for agent_id in ["zara_cso", "marco_cfo", "sofia_cmo", "jinjin_k9_scout", "ethan_cto", "samantha_secretary"]:
            if agent_id not in supporting:
                supporting.append(agent_id)
    if "aiden_ceo" not in supporting:
        supporting.insert(0, "aiden_ceo")
    if normalized_target not in {"whole_team", "team", "aiden_ceo"} and normalized_target in AGENT_ROLES:
        primary_agent = normalized_target
        if primary_agent not in supporting:
            supporting.insert(0, primary_agent)
    else:
        primary_agent = "aiden_ceo"
    if len(supporting) == 1 and supporting[0] == "aiden_ceo":
        supporting.extend(["zara_cso", "marco_cfo", "sofia_cmo", "ethan_cto", "jinjin_k9_scout", "samantha_secretary"])
    # Keep Aiden as coordinator while giving domain agents visible ownership.
    supporting_agents = [agent_id for agent_id in supporting if agent_id != primary_agent]
    expected_outputs = [
        "shared interpretation",
        "role-specific agent replies",
        "safe internal work item",
        "approval boundary notes",
        "completion report when done",
    ]
    approval_points = [
        item for item in APPROVAL_REQUIRED_FOR if any(word in text.lower() for word in item.replace("/", " ").split())
    ] or ["external action remains blocked until explicit owner approval"]
    return {
        "primary_agent": primary_agent,
        "supporting_agents": supporting_agents[:8],
        "reason": "Aiden coordinates owner goals, then routes domain work to the original legacy team roles.",
        "expected_outputs": expected_outputs,
        "approval_points": approval_points,
        "no_go_boundaries": FORBIDDEN_ACTIONS,
        "coo_invented": False,
    }


def known_agent_ids() -> list[str]:
    return list(AGENT_ROLES)
