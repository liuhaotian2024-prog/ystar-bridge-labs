from __future__ import annotations


def classify_intent(message: str) -> str:
    text = message.lower()
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
