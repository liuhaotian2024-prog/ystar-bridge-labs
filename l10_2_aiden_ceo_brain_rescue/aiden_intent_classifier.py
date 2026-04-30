"""Deterministic local intent classification for Aiden CEO chat."""

from __future__ import annotations


def classify_intent(message: str) -> dict[str, object]:
    text = message.strip()
    lowered = text.lower()
    rules: list[tuple[str, list[str], float, str]] = [
        ("critique_or_frustration", ["垃圾", "傻子", "疯", "哭", "折磨", "失望", "心凉", "崩溃"], 0.95, "owner frustration or critique"),
        ("self_state_question", ["你现在自己", "你现在是", "你现在是什么状态", "怎么形容自己", "你是什么状态"], 0.95, "Aiden self-state question"),
        ("rationale_question", ["依据什么", "为什么", "凭什么", "怎么得出", "得出来", "理由", "basis"], 0.92, "asks for reasoning basis"),
        ("meta_development_question", ["元发展", "meta-development", "meta development", "labs 的发展", "labs的发展"], 0.94, "asks about Labs meta-development"),
        ("team_delegation_request", ["带团队", "7 天行动计划", "七天行动计划", "制定 7 天", "制定7天", "行动计划"], 0.9, "asks Aiden to lead team planning"),
        ("approval_question", ["批准", "审批", "需要我", "授权", "approve", "approval"], 0.9, "asks what requires owner approval"),
        ("runtime_status_question", ["runtime", "系统状态", "办公室状态", "现在能做什么", "功能状态"], 0.82, "asks current runtime status"),
        ("fastest_cash_question", ["第一笔钱", "最快拿到钱", "最快赚钱", "cash", "收入", "付费"], 0.95, "asks fastest cash path"),
        ("next_action_question", ["下一步", "现在做什么", "先做什么", "怎么开始"], 0.85, "asks next concrete action"),
        ("general_strategy_question", ["战略", "方向", "路线", "机会", "不要锁死", "不锁死", "founder ai workflow audit"], 0.8, "asks strategy or portfolio direction"),
    ]
    for intent, keywords, confidence, reason in rules:
        if any(keyword in text or keyword in lowered for keyword in keywords):
            return {"intent": intent, "confidence": confidence, "matched_reason": reason, "used_unknown": False}
    return {"intent": "unknown", "confidence": 0.45, "matched_reason": "no exact rule matched", "used_unknown": True}
