from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class IntentProfile:
    intent: str
    confidence: float
    matched_features: tuple[str, ...]
    classification_mode: str


INTENT_FEATURES: dict[str, tuple[str, ...]] = {
    "agents_burden": (
        "agents.md",
        "治理规则",
        "拖慢",
        "旧规则",
        "m-3 value production",
        "m-3",
        "行政负担",
    ),
    "directive_retriage": (
        "directive_tracker",
        "directive tracker",
        "归档",
        "继续推进",
        "re-triage",
    ),
    "operations_calendar": (
        "operations.md",
        "hn/linkedin",
        "linkedin 日程",
        "hn 日程",
        "旧 hn",
        "旧hn",
        "发布节奏",
    ),
    "current_money_blocker": (
        "最阻碍",
        "阻碍 labs 赚钱",
        "赚钱的是治理问题",
        "产品问题",
        "分发问题",
        "为什么赚不到钱",
    ),
    "permission_tier_replacement": (
        "permission tier",
        "permission-tier",
        "权限层",
        "替代",
        "审批层",
    ),
    "fastest_cash": (
        "最快拿到第一笔钱",
        "第一笔钱",
        "现金",
        "revenue",
        "first cash",
        "赚钱路径",
        "变现路径",
    ),
    "rationale_meta": (
        "依据",
        "为什么",
        "元发展",
        "meta",
        "怎么认识",
    ),
    "self_state": (
        "什么状态",
        "形容自己",
        "你现在自己",
        "你是谁",
    ),
    "repo_repair": (
        "之前仓库的问题",
        "新架构",
        "怎么修",
        "这几天",
        "孤岛模块",
        "散乱",
        "重复造轮子",
    ),
    "approval": (
        "批准",
        "审批",
        "approval",
        "授权",
        "外部动作",
    ),
    "next_ceo_action": (
        "下一步",
        "带团队",
        "ceo 应该",
        "ceo应该",
        "马上做",
        "推进",
        "落地",
    ),
    "owner_coordination_help": (
        "怎么配合",
        "如何配合",
        "我需要做什么",
        "要求我怎么",
        "我完全不明白",
        "我不明白",
        "你需要我",
    ),
}


def classify_intent_profile(message: str) -> IntentProfile:
    text = (message or "").lower()
    scores: list[tuple[float, str, tuple[str, ...]]] = []
    for intent, features in INTENT_FEATURES.items():
        matched = tuple(feature for feature in features if feature.lower() in text)
        if not matched:
            continue
        coverage = len(matched) / max(1, len(features))
        strength = min(1.0, 0.42 + coverage + (0.08 * min(3, len(matched))))
        scores.append((strength, intent, matched))
    if not scores:
        return IntentProfile(
            intent="general",
            confidence=0.35,
            matched_features=(),
            classification_mode="feature_fallback",
        )
    scores.sort(reverse=True)
    confidence, intent, matched = scores[0]
    return IntentProfile(
        intent=intent,
        confidence=round(confidence, 3),
        matched_features=matched,
        classification_mode="feature_scored",
    )


def classify_intent(message: str) -> str:
    return classify_intent_profile(message).intent


def flatten_intent_features() -> Iterable[str]:
    for features in INTENT_FEATURES.values():
        yield from features


__all__ = [
    "INTENT_FEATURES",
    "IntentProfile",
    "classify_intent",
    "classify_intent_profile",
    "flatten_intent_features",
]
