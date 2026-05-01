from __future__ import annotations


def classify_intent(message: str) -> str:
    text = message.lower()
    if any(k in text for k in ["agents.md", "治理规则", "拖慢", "m-3 value production", "m-3"]):
        if any(k in text for k in ["拖慢", "旧规则", "治理规则"]):
            return "agents_burden"
    if any(k in text for k in ["directive_tracker", "directive tracker", "归档", "继续推进"]):
        return "directive_retriage"
    if any(k in text for k in ["operations.md", "hn/linkedin", "linkedin 日程", "hn 日程", "旧 hn", "旧hn"]):
        return "operations_calendar"
    if any(k in text for k in ["最阻碍", "阻碍 labs 赚钱", "赚钱的是治理问题", "产品问题", "分发问题"]):
        return "current_money_blocker"
    if any(k in text for k in ["permission tier", "permission-tier", "权限层", "替代"]):
        return "permission_tier_replacement"
    if any(k in text for k in ["最快拿到第一笔钱", "第一笔钱", "现金", "revenue", "first cash"]):
        return "fastest_cash"
    if any(k in text for k in ["依据", "为什么", "元发展", "meta"]):
        return "rationale_meta"
    if any(k in text for k in ["什么状态", "形容自己", "你现在自己"]):
        return "self_state"
    if any(k in text for k in ["之前仓库的问题", "新架构", "怎么修", "这几天"]):
        return "repo_repair"
    if any(k in text for k in ["批准", "审批", "approval"]):
        return "approval"
    if any(k in text for k in ["下一步", "带团队", "ceo 应该", "ceo应该"]):
        return "next_ceo_action"
    return "general"
