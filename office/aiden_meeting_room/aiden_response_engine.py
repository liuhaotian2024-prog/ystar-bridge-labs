from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from .aiden_intent_classifier import IntentProfile, classify_intent, classify_intent_profile
from .company_context_loader import CompanyContext, load_company_context
from .directive_retriage_analyzer import grouped_directive_summary
from .evidence_extractor import EvidenceItem, format_evidence
from .governance_burden_analyzer import burden_findings, permission_tier_replacement_findings
from .meeting_memory import MeetingMemory, default_memory_path
from office.mission_command.e101_adaptive_governance_discovery_and_correct_path_navigator import (
    build_adaptive_governance_result,
)


_STRATEGIC_INTENTS = {
    "fastest_cash",
    "rationale_meta",
    "next_ceo_action",
    "current_money_blocker",
    "permission_tier_replacement",
}

_EXTERNAL_OR_EXECUTION_INTENTS = {
    "approval",
    "next_ceo_action",
    "fastest_cash",
}


def _boundary() -> str:
    return "边界：我不会自动发邮件、联系客户、发布、付款、提交表单、创建账号或写回核心 DB/brain/memory/CIEU。"


def _repeat_prefix(memory: MeetingMemory, message: str) -> str:
    if memory.repeated(message):
        return "你刚才已经问过这个方向，我这次补更深一层。\n\n"
    return ""


def build_aiden_answer_owner_action_context(owner_message: str, intent: str) -> dict:
    """Build the adaptive-governance action context for the CEO meeting entrypoint."""

    lowered = (owner_message or "").lower()
    is_strategy = intent in _STRATEGIC_INTENTS
    is_external_candidate = intent in _EXTERNAL_OR_EXECUTION_INTENTS or any(
        token in lowered
        for token in ("l4", "external", "客户", "customer", "revenue", "payment", "pricing", "价格", "赚钱", "收入")
    )
    is_codex = any(token in lowered for token in ("codex", "prompt", "执行", "implementation"))
    return {
        "action_id": f"aiden_answer_owner::{intent}",
        "action_type": "market_strategy" if is_strategy else "owner_readback",
        "mission_type": "ceo_meeting_room_answer",
        "route_type": "external_feedback_candidate" if is_external_candidate else "status_only_readback",
        "L_level": "L4" if is_external_candidate else "L2",
        "major_action": is_strategy or is_external_candidate or is_codex,
        "market_strategy_required": is_strategy,
        "external_observation_required": is_strategy,
        "provider_tool_boundary": False,
        "owner_decision_required": is_external_candidate,
        "revenue_or_payment_related": any(token in lowered for token in ("revenue", "payment", "pricing", "价格", "收入", "付")),
        "codex_executor_boundary": is_codex,
        "codex_prompt_generation": is_codex,
        "new_capability_discovered": False,
        "residual_learning": False,
        "generation_mode": "aiden_meeting_room_structured_response",
    }


def build_aiden_adaptive_governance_result(owner_message: str, intent: str, body: str) -> dict:
    action_context = build_aiden_answer_owner_action_context(owner_message, intent)
    invocation_proof = _aiden_invocation_proof(intent, body)
    return build_adaptive_governance_result(
        action_context=action_context,
        runtime_artifact={
            "source_entrypoint": "office.aiden_meeting_room.aiden_response_engine.answer_owner",
            "intent": intent,
            "body_preview": body[:800],
        },
        invocation_proof=invocation_proof,
    )


def render_adaptive_governance_notice(result: dict) -> str:
    proof = result.get("obligation_invocation_proof", {})
    missing = proof.get("missing_obligations") or []
    if not missing:
        return "Adaptive Governance Gate: ALLOW\n"
    steps = result.get("correct_path_navigator", {}).get("steps", [])
    rendered_steps = "\n".join(
        f"- {step.get('missing_obligation')}: {step.get('correct_path')}" for step in steps[:8]
    )
    return (
        "Adaptive Governance Gate: REQUIRE_REVISION\n"
        "Correct path before treating this answer as a governed CEO strategy/action packet:\n"
        f"{rendered_steps}\n"
    )


def _aiden_invocation_proof(intent: str, body: str) -> dict:
    satisfied = []
    if "Evidence:" in body or "依据" in body or "repo 证据" in body:
        satisfied.append("external_observation_or_staleness_boundary")
    if "owner" in body.lower() or "审批" in body or "批准" in body:
        satisfied.append("post_action_residual")
    return {
        "proof_id": f"aiden_answer_owner::{intent}::adaptive_proof",
        "satisfied_obligations": satisfied,
        "evidence_refs": ["office/aiden_meeting_room/aiden_response_engine.py"],
        "customer_validation_claim": False,
        "pricing_validation_claim": False,
        "revenue_claim": False,
        "payment_claim": False,
        "external_action_executed": False,
    }


def answer_owner(
    owner_message: str,
    repo_root: Path | None = None,
    memory_path: Path | None = None,
    record_memory: bool = True,
) -> str:
    ctx = load_company_context(repo_root)
    mem_path = memory_path or default_memory_path(ctx.repo_root)
    memory = MeetingMemory.load(mem_path)
    profile = classify_intent_profile(owner_message)
    body = build_dynamic_owner_answer(ctx, owner_message, profile)
    adaptive_result = build_aiden_adaptive_governance_result(owner_message, profile.intent, body)
    governance_notice = render_adaptive_governance_notice(adaptive_result)
    response = (
        _repeat_prefix(memory, owner_message)
        + body
        + "\n\n"
        + _boundary()
        + "\n\n治理导航：\n"
        + governance_notice
    )
    if record_memory:
        memory.record(owner_message, response, profile.intent)
    return response


def build_dynamic_owner_answer(ctx: CompanyContext, owner_message: str, profile: IntentProfile) -> str:
    owner_terms = _extract_owner_terms(owner_message)
    answer_mode = _infer_answer_mode(owner_message, profile)
    evidence = _select_context_evidence(ctx, owner_terms, profile)
    sections = [
        _render_lead_judgment(answer_mode, profile),
        _render_focus(owner_message, owner_terms, profile),
        _render_mode_specific_analysis(ctx, profile, evidence),
        _render_action_packet(ctx, owner_message, profile),
        "repo 证据：\n" + format_evidence(evidence, limit=6),
    ]
    if profile.intent in _STRATEGIC_INTENTS:
        sections.append(
            "strategy/memo runtime 导航：这个 meeting-room 回答只能做 CEO 会议层判断；如果要把它当成真实战略结论，"
            "必须进入 E108/E110/E115/E132 等 strategy/memo runtime，完成外部证据、竞品、right-to-win、CZL residual 和 owner decision packet。"
        )
    return "\n\n".join(section for section in sections if section)


def _render_lead_judgment(answer_mode: str, profile: IntentProfile) -> str:
    if answer_mode == "action":
        return (
            "我的判断：你要的不是再听一段固定解释，而是把问题推进成可执行的行动包。"
            "所以我会先给目标、交付物、证据、风险边界和下一步执行线。"
        )
    if answer_mode == "diagnosis":
        return (
            "我的判断：这个问题要先定位系统性原因，而不是按某个旧模板给结论。"
            "我会把它拆成 owner 真正要决定的问题、repo 证据、当前缺口和正确推进路径。"
        )
    return (
        "我的判断：这不是一个固定 intent handler 能回答的问题；Aiden 应该根据 owner 意图和 repo 证据动态组织回答。"
        "下面是这轮的 repo-grounded 结论。"
    )


def _render_focus(owner_message: str, owner_terms: list[str], profile: IntentProfile) -> str:
    terms = "、".join(owner_terms[:8]) if owner_terms else "未抽取到稳定关键词"
    matched = "、".join(profile.matched_features[:8]) if profile.matched_features else "无固定命中特征"
    return (
        "owner 真正要决定的问题：这条请求应该如何靠近 M-3，而不是继续制造报告或模板回答。\n"
        f"意图画像：{profile.intent}，置信度 {profile.confidence}，分类方式 {profile.classification_mode}。\n"
        f"owner 语义线索：{terms}。\n"
        f"命中特征：{matched}。"
    )


def _render_mode_specific_analysis(ctx: CompanyContext, profile: IntentProfile, evidence: list[EvidenceItem]) -> str:
    if profile.intent == "agents_burden":
        findings = burden_findings(ctx.evidence_index) if ctx.evidence_index else []
        rendered = _render_governance_findings(findings)
        return (
            "系统判断：M-2 不能被削弱，但 M-2 不能吞掉 M-3。12-layer、5-tuple、Nightly/daily/weekly 报告、"
            "Idle 学习循环这类机制只有绑定真实任务和停机条件时才有价值。\n"
            f"{rendered}"
        )
    if profile.intent == "directive_retriage":
        return _render_directive_retriage(ctx)
    if profile.intent == "operations_calendar":
        return (
            "运营判断：OPERATIONS 里的 HN/LinkedIn/日程类内容不应该默认继续约束当前公司。"
            "它们是历史运营资产，只有绑定当前赚钱路径、证据和 owner approval 时才重新激活。\n"
            + _render_operations_findings(ctx)
        )
    if profile.intent == "current_money_blocker":
        return (
            "赚钱阻塞判断：当前最大问题不是“治理不够”，而是产品化交付和分发仍没有被压成真客户可购买的最小包。"
            "治理应该保护行动，不能替代行动；分发必须服务于具体 offer，而不是泛泛发布。"
        )
    if profile.intent == "permission_tier_replacement":
        findings = permission_tier_replacement_findings(ctx.evidence_index) if ctx.evidence_index else []
        return (
            "权限判断：旧的全局审批墙应该被 permission tier 替代。内部分析和本地草稿是 Tier 0；只读公开研究是 Tier 1；"
            "外联/发布/报价/表单是 Tier 2/3 owner-approved；付款、法律承诺、核心写回、secret/private DB/log 是 Tier 4。\n"
            + _render_governance_findings(findings)
        )
    if profile.intent == "self_state":
        return (
            "状态判断：我是 repo-grounded CEO meeting layer，不是完全自治 CEO。"
            "我能读取安全上下文、组织判断、生成行动包和指出治理边界；我不会自动发邮件、付款、联系客户或写核心 DB。"
        )
    if profile.intent == "repo_repair":
        return (
            "仓库判断：问题不是没有能力，而是能力没有被检索、编排、调用和治理闭环。"
            "修法不是继续造新轮子，而是 Search before build、现有能力召回、重复能力归并、runtime 入口绑定、CIEU/CZL 记录。"
        )
    if profile.intent == "fastest_cash":
        return (
            "战略判断：最快赚钱路径不能再由 meeting-room 里某个固定候选决定。它必须通过 strategy/memo runtime 生成："
            "先做外部证据和竞品，再做 buyer/problem/offer/right-to-win，再形成 no-send owner decision packet。"
            "M-3 的底线仍是真产品、真客户、真收入、真业界影响。"
        )
    if profile.intent == "approval":
        return "审批判断：需要 owner 批准的不是内部思考，而是任何外部副作用、报价、付款、合同、公开发布和核心写回。"
    if profile.intent == "owner_coordination_help":
        return (
            "协作判断：你不需要替 Aiden 做内部分析、检索、整理、生成 no-send packet 或 dry-run 草案；"
            "这些都应该由 Aiden 在本地受控边界里自主完成。你只需要在真正会产生外部副作用或核心写回的关口做选择："
            "approve / reject / hold / revise。"
        )
    if profile.intent == "next_ceo_action":
        return "推进判断：下一步应该输出行动包，而不是只说“建议下一步”。Aiden 要给出目标、交付物、验证问题、风险边界和执行 backlog。"
    return "综合判断：这条请求需要按 M Triangle、证据、能力召回和行动边界组织，不应该落回近期记忆或单点模板。"


def _render_action_packet(ctx: CompanyContext, owner_message: str, profile: IntentProfile) -> str:
    target = _infer_target(owner_message, profile)
    deliverable = _infer_deliverable(profile)
    validation = _infer_validation_questions(profile)
    backlog = _infer_internal_backlog(profile)
    return (
        "行动包：\n"
        f"- 目标：{target}\n"
        f"- 交付物：{deliverable}\n"
        f"- 验证问题：{validation}\n"
        f"- 内部执行：{backlog}\n"
        "- 风险边界：不执行外部发送、不报价、不付款、不触达客户；需要外部动作时转 owner decision packet。"
    )


def _select_context_evidence(ctx: CompanyContext, owner_terms: list[str], profile: IntentProfile) -> list[EvidenceItem]:
    if not ctx.evidence_index:
        return []
    evidence: list[EvidenceItem] = []
    if profile.intent == "agents_burden":
        evidence.extend(ctx.evidence_index.by_classification("administrative_burden"))
        evidence.extend(ctx.evidence_index.by_label("Idle learning loop", "Reporting obligation", "Unified work protocol"))
    elif profile.intent == "directive_retriage":
        evidence.extend(ctx.evidence_index.search("Directive tracker", "HN article task", "Enterprise sales task", "Testing baseline task"))
    elif profile.intent == "operations_calendar":
        evidence.extend(ctx.evidence_index.search("HN cadence", "LinkedIn cadence", "Daily schedule", "Weekly cycle"))
    elif profile.intent == "permission_tier_replacement":
        evidence.extend(ctx.evidence_index.by_classification("replace_with_permission_tier"))
    elif profile.intent in {"fastest_cash", "current_money_blocker", "next_ceo_action"}:
        evidence.extend(ctx.evidence_index.search("M-3 Value Production", "真客户", "真收入", "Value production criteria"))
        evidence.extend(ctx.evidence_index.search("Search before build", "Real tests over hand-wave", "Plan is not done"))
    elif profile.intent == "self_state":
        evidence.extend(ctx.evidence_index.search("BOARD_NL", "INTENT_RECORDED", "Mission Command", "M-3 Value Production"))
    elif profile.intent == "repo_repair":
        evidence.extend(ctx.evidence_index.search("Search before build", "三仓库", "gov_order", "Obligation registered"))
    if owner_terms:
        evidence.extend(ctx.evidence_index.search(*owner_terms[:8]))
    if not evidence:
        evidence.extend(ctx.evidence_index.by_label("M-3 Value Production", "Plan is not done", "Board NL pipeline"))
    return _dedupe_evidence(evidence)[:8]


def _render_governance_findings(findings: Iterable[object]) -> str:
    rendered = []
    for item in list(findings)[:5]:
        refs = ", ".join(getattr(item, "evidence_refs", [])[:3])
        rendered.append(f"- {getattr(item, 'title', 'finding')}: {getattr(item, 'reason', '')} Evidence: {refs}")
    return "\n".join(rendered) if rendered else "- Evidence: no direct governance burden finding found."


def _render_directive_retriage(ctx: CompanyContext) -> str:
    grouped = grouped_directive_summary(ctx.directive_findings)
    parts = []
    for status in ("ARCHIVE_LEGACY", "REVENUE_RELEVANT_NOW", "OWNER_DECISION_REQUIRED", "SUPERSEDED_BY_RUNTIME", "ACTIVE_NOW"):
        items = grouped.get(status, [])[:3]
        if not items:
            continue
        examples = "; ".join(f"{item.task_id} {item.task} ({item.evidence_ref})" for item in items)
        parts.append(f"- {status}: {examples}")
    parts.append("runtime artifact: directive_retriage.json")
    return "Directive triage：\n" + "\n".join(parts)


def _render_operations_findings(ctx: CompanyContext) -> str:
    rows = []
    for item in ctx.operations_findings[:5]:
        rows.append(f"- {item.classification}: {item.reason} Evidence: {item.evidence_ref}")
    return "\n".join(rows) if rows else "- Evidence: no operations calendar finding found."


def _extract_owner_terms(message: str) -> list[str]:
    text = (message or "").replace("，", " ").replace("。", " ").replace("？", " ").replace("！", " ")
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_\-]{2,}|[\u4e00-\u9fff]{2,}", text)
    stopwords = {"Aiden", "请你", "我们", "现在", "这个", "那个", "为什么", "什么", "是不是", "如何", "可以"}
    terms = []
    for token in tokens:
        if token in stopwords:
            continue
        if token not in terms:
            terms.append(token)
    return terms[:12]


def _infer_answer_mode(owner_message: str, profile: IntentProfile) -> str:
    lowered = (owner_message or "").lower()
    if any(term in lowered for term in ("推进", "行动", "落地", "赚钱", "变现", "下一步", "做")):
        return "action"
    if any(term in lowered for term in ("为什么", "根本原因", "问题", "缺口", "修")):
        return "diagnosis"
    if profile.intent in _STRATEGIC_INTENTS:
        return "action"
    return "readback"


def _infer_target(owner_message: str, profile: IntentProfile) -> str:
    if profile.intent in {"fastest_cash", "current_money_blocker"}:
        return "形成一个可被真客户理解和验证的 M-3 first-cash owner decision packet。"
    if profile.intent == "repo_repair":
        return "把散落能力变成可检索、可调用、可治理的主线 runtime。"
    if profile.intent == "agents_burden":
        return "保留安全内核，移除拖慢 M-3 的行政仪式。"
    if profile.intent == "owner_coordination_help":
        return "把 owner 从内部执行负担里解放出来：Aiden 自主推进本地 no-send 工作，只在高风险边界请求 owner 决策。"
    return "把 owner 的问题变成可验证、可执行、可回收 residual 的 CEO action thread。"


def _infer_deliverable(profile: IntentProfile) -> str:
    if profile.intent == "directive_retriage":
        return "directive 分类表：archive / continue / owner decision / superseded。"
    if profile.intent == "permission_tier_replacement":
        return "permission tier map：Tier 0-4、对应动作、审批条件、拒绝边界。"
    if profile.intent in {"fastest_cash", "next_ceo_action", "current_money_blocker"}:
        return "no-send action packet：买方/问题/交付物/验证问题/内部 backlog/风险边界。"
    if profile.intent == "owner_coordination_help":
        return "owner coordination map：Aiden 自主做什么、owner 只在哪些边界做 approve/reject/hold/revise。"
    return "CEO-readable action thread：判断、证据、取舍、下一步、边界。"


def _infer_validation_questions(profile: IntentProfile) -> str:
    if profile.intent in {"fastest_cash", "current_money_blocker"}:
        return "谁有预算、为什么现在痛、替代方案是什么、我们凭什么赢、最小验证动作是什么。"
    if profile.intent == "repo_repair":
        return "是否已有能力、是否 runtime-active、是否可被检索调用、是否有治理/CIEU 记录。"
    if profile.intent == "owner_coordination_help":
        return "这一步是否能由 Aiden 本地自主完成；是否涉及外发、付款、报价、发布、客户触达或核心写回。"
    return "这一步是否推进 M-3、是否需要 owner approval、是否有真实证据、是否会产生外部副作用。"


def _infer_internal_backlog(profile: IntentProfile) -> str:
    if profile.intent == "repo_repair":
        return "先检索现有模块，再归并重复能力，最后接入 runtime/gov/CIEU，不重新造轮子。"
    if profile.intent in {"fastest_cash", "next_ceo_action", "current_money_blocker"}:
        return "调用 strategy/memo runtime，生成候选、竞品、right-to-win、no-send packet 和 CZL residual。"
    if profile.intent == "owner_coordination_help":
        return (
            "Aiden 继续跑 memo/strategy/runtime、整理证据和 no-send owner packet；"
            "owner 只需要对外部发送、支付、报价、发布、客户触达、production brain/core DB 写回做 approve/reject/hold/revise。"
        )
    return "读取 repo 证据，形成 owner-facing 判断，再进入对应 runtime。"


def _dedupe_evidence(items: Iterable[EvidenceItem]) -> list[EvidenceItem]:
    seen = set()
    result = []
    for item in items:
        key = item.ref
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


__all__ = [
    "answer_owner",
    "build_aiden_adaptive_governance_result",
    "build_aiden_answer_owner_action_context",
    "build_dynamic_owner_answer",
    "render_adaptive_governance_notice",
]
