from __future__ import annotations


def classify_intent(message: str) -> str:
    text = message.lower()
    if any(k in text for k in ["旧规则", "不应该再约束", "不再约束", "obsolete rules", "old rules"]):
        return "obsolete_rules"
    if any(k in text for k in ["active 的治理", "active治理", "当前 active", "真正 active", "治理规则是什么"]):
        return "active_rules"
    if any(k in text for k in ["历史包袱", "旧历史", "旧任务", "包袱"]):
        return "legacy_burden"
    if any(k in text for k in ["减少我的手工负担", "减少手工负担", "manual burden", "手工操作"]):
        return "reduce_owner_burden"
    if any(k in text for k in ["优先推进 m triangle", "哪一面", "m triangle 的哪", "m 三角"]):
        return "m_triangle_priority"
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
