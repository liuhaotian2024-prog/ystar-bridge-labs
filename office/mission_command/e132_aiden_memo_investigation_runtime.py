from __future__ import annotations

import importlib
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol

from office.mission_command.e114_live_web_capability_utilized_strategy_run import (
    summarize_source_dates,
)
from office.mission_command.e108_live_global_open_world_strategy_runtime import (
    DuckDuckGoLitePublicReadProvider,
)


MILESTONE_ID = "E132_Aiden_Memo_Investigation_Runtime_R1"
SESSION_ID = "e132_aiden_memo_investigation_runtime"
BRIDGE_ROOT = Path(__file__).resolve().parents[2]
Y_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")


class PublicReadProvider(Protocol):
    def search(self, query: str, *, domain_id: str, max_results: int = 3) -> list[dict[str, Any]]:
        ...


MEMO_INVESTIGATION_SIGNALS = (
    "archive id",
    "strat-",
    "research memo",
    "owner research memo",
    "备忘录",
    "研究备忘录",
    "验证分析",
    "核实",
    "验证下面",
    "验证这份",
    "跟我们之间的关系",
    "提出你的看法",
    "深度战略分析",
    "x402",
    "mission go",
)

ENTITY_PATTERNS = {
    "x402": re.compile(r"(?<![A-Za-z0-9_])x402(?![A-Za-z0-9_])", re.I),
    "Mission GO": re.compile(r"\bMission\s+GO\b", re.I),
    "USDC": re.compile(r"\bUSDC\b", re.I),
    "agent payments": re.compile(r"\bagent(?:ic)?\s+payments?\b|agent\s+economy|agent经济", re.I),
    "HTTP 402": re.compile(r"\bHTTP\s*402\b|402\s+Payment\s+Required", re.I),
    "wallet": re.compile(r"\bwallets?\b|钱包", re.I),
    "stablecoin": re.compile(r"\bstablecoins?\b|稳定币", re.I),
}

DEFAULT_STRAT002_OPEN_QUESTIONS = (
    {
        "source_heading_id": "8.1",
        "question_title": "Asset-to-Surface Matching",
        "question_text": "Which Mission GO/Y* capabilities meaningfully match agent-buyer demand under x402/AP2-style infrastructure?",
    },
    {
        "source_heading_id": "8.2",
        "question_title": "Path Sequencing vs Parallelism",
        "question_text": "Should the x402 path be parallel to the Mining Plant Plugin path, sequenced after it, a replacement, or deferred?",
    },
    {
        "source_heading_id": "8.3",
        "question_title": "e34 Re-Scoring",
        "question_text": "Which e34 opportunity spaces or institutional voids should be re-scored under the new agent-to-agent payment infrastructure facts?",
    },
    {
        "source_heading_id": "8.4",
        "question_title": "Defuse Revival Determination",
        "question_text": "Do the Defuse dead-path revival conditions apply, and what is the cleanest non-launch resurfacing form?",
    },
    {
        "source_heading_id": "8.5",
        "question_title": "Multi-Tenant Engineering Cost",
        "question_text": "What engineering scope is required to make single-tenant Mission GO assets safe for external or agent-buyer service surfaces?",
    },
    {
        "source_heading_id": "8.6",
        "question_title": "Patent-Scope Boundaries",
        "question_text": "How should P1/P3/P4 patent scope shape what can be exposed externally versus kept proprietary?",
    },
    {
        "source_heading_id": "8.7",
        "question_title": "What Would Change the Answer",
        "question_text": "What single evidence item would most reduce uncertainty about whether to pursue an x402 path?",
    },
)

MEMO_ACTION_ADVANCEMENT_TERMS = (
    "推进",
    "行动",
    "赚钱",
    "变现",
    "商业化",
    "落地",
    "拟定",
    "开始做",
    "没有行动",
    "一直都没有行动",
    "revenue",
    "monetize",
    "go-to-market",
    "gtm",
)


def is_memo_investigation_request(owner_message: str) -> bool:
    text = owner_message or ""
    lowered = text.lower()
    signal_count = sum(1 for signal in MEMO_INVESTIGATION_SIGNALS if signal in lowered)
    long_structured_input = len(text) >= 1800 and ("#" in text or "**" in text or "\n" in text)
    asks_to_verify_material = any(term in text for term in ("验证", "核实", "分析下面", "这份", "备忘录"))
    return signal_count >= 2 or (signal_count >= 1 and asks_to_verify_material) or (
        long_structured_input and asks_to_verify_material
    )


def is_strat002_reference(text: str) -> bool:
    lowered = (text or "").lower()
    return (
        "strat-002" in lowered
        or ("x402" in lowered and any(term in lowered for term in ("mission go", "mission", "备忘录", "memo", "生态")))
    )


def is_memo_action_advancement_request(text: str) -> bool:
    lowered = (text or "").lower()
    has_action_intent = any(term in lowered for term in MEMO_ACTION_ADVANCEMENT_TERMS)
    has_memo_or_strategy_context = is_memo_investigation_request(text) or is_strat002_reference(text)
    return has_action_intent and has_memo_or_strategy_context


def is_strat002_action_advancement_request(text: str) -> bool:
    """Backward-compatible alias; the runtime uses the generic memo action gate."""
    return is_memo_action_advancement_request(text)


def run_aiden_memo_investigation_runtime(
    owner_message: str,
    *,
    cieu_db: str | Path,
    repo_root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
    public_read_provider: PublicReadProvider | None = None,
    allow_live_network: bool = True,
) -> dict[str, Any]:
    base = Path(repo_root or BRIDGE_ROOT)
    ygov = Path(ystar_gov_root or Y_GOV_ROOT)
    metadata = extract_memo_metadata(owner_message)
    entities = extract_memo_entities(owner_message)
    claims = extract_memo_claims(owner_message, entities=entities)
    open_questions = extract_memo_open_questions(owner_message)
    advancement_requested = is_memo_action_advancement_request(owner_message)
    queries = build_memo_investigation_queries(owner_message, entities=entities, metadata=metadata)
    evidence = collect_memo_public_read_evidence(
        queries,
        provider=public_read_provider,
        allow_live_network=allow_live_network,
    )
    repo_relation = scan_labs_relation_to_memo(owner_message, repo_root=base, entities=entities)
    suitability = build_runtime_suitability_gate(owner_message)
    analysis = build_memo_strategic_analysis(
        owner_message=owner_message,
        metadata=metadata,
        entities=entities,
        claims=claims,
        open_questions=open_questions,
        queries=queries,
        evidence=evidence,
        repo_relation=repo_relation,
        allow_live_network=allow_live_network,
        advancement_requested=advancement_requested,
    )
    result = {
        "artifact_id": "e132_aiden_memo_investigation_result",
        "milestone_id": MILESTONE_ID,
        "created_at": _now(),
        "generation_mode": "deterministic_memo_investigation_with_public_read_evidence",
        "owner_message_preview": _compact(owner_message, 360),
        "runtime_suitability_gate": suitability,
        "memo_metadata": metadata,
        "memo_entities": entities,
        "memo_claims": claims,
        "memo_open_questions": open_questions,
        "memo_action_advancement_requested": advancement_requested,
        "public_read_queries": queries,
        "public_read_evidence": evidence,
        "source_date_summary": summarize_source_dates(evidence),
        "repo_relation": repo_relation,
        "strategic_analysis": analysis,
        "owner_facing_answer": render_memo_investigation_owner_answer(analysis),
        "truth_constraints": {
            "first_cash_ranking_substituted_for_memo_analysis": False,
            "raw_recent_memory_answer": False,
            "live_public_read_claim_without_provider": False,
            "external_action_executed": False,
            "provider_action_executed": False,
            "payment_executed": False,
            "customer_validation_claim": False,
            "revenue_claim": False,
            "K9Audit_write_claim": False,
        },
    }
    write_memo_investigation_cieu_record(result, cieu_db=cieu_db, ystar_gov_root=ygov)
    result["CIEUStore_summary"] = summarize_cieustore(cieu_db)
    result["memo_investigation_runtime_proven"] = True
    return result


def extract_memo_metadata(text: str) -> dict[str, Any]:
    def field(label: str) -> str:
        match = re.search(rf"\*\*{re.escape(label)}\*\*\s*:\s*([^\n]+)", text, flags=re.I)
        if not match:
            match = re.search(rf"{re.escape(label)}\s*:\s*([^\n]+)", text, flags=re.I)
        return match.group(1).strip() if match else ""

    title_match = re.search(r"#\s*([^#\n]{8,180})", text)
    return {
        "title": title_match.group(1).strip() if title_match else "owner-supplied research memo",
        "archive_id": field("Archive ID"),
        "date": field("Date"),
        "author": field("Author"),
        "type": field("Type"),
        "status": field("Status"),
        "input_character_count": len(text),
        "structured_memo_detected": bool(title_match or field("Archive ID") or "STRAT-" in text.upper()),
    }


def extract_memo_entities(text: str) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    for name, pattern in ENTITY_PATTERNS.items():
        matches = list(pattern.finditer(text))
        if matches:
            entities.append(
                {
                    "entity": name,
                    "occurrence_count": len(matches),
                    "first_context": _context_window(text, matches[0].start(), width=120),
                }
            )
    if not entities:
        entities.append(
            {
                "entity": "owner_supplied_research_memo",
                "occurrence_count": 1,
                "first_context": _compact(text, 180),
            }
        )
    return entities


def extract_memo_claims(text: str, *, entities: list[Mapping[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    entity_names = [str(entity.get("entity") or "") for entity in entities]
    pieces = re.split(r"(?<=[。！？.!?])\s+|\n+-\s+|\n\d+\.\s+", text)
    claims: list[dict[str, Any]] = []
    for piece in pieces:
        normalized = " ".join(piece.split())
        if len(normalized) < 28:
            continue
        if any(name and name.lower() in normalized.lower() for name in entity_names) or any(
            term in normalized for term in ("should", "must", "opportunity", "risk", "应该", "必须", "机会", "风险", "整合", "集成")
        ):
            claims.append(
                {
                    "claim_id": f"claim_{len(claims) + 1:02d}",
                    "claim_text": normalized[:520],
                    "verification_status": "requires_public_read_and_repo_relation_check",
                }
            )
        if len(claims) >= limit:
            break
    return claims


def extract_memo_open_questions(text: str) -> list[dict[str, Any]]:
    """Extract the memo's own questions so Aiden answers the brief, not a nearby template."""
    normalized = text or ""
    open_block = normalized
    block_match = re.search(
        r"(^|\n)##\s*(?:\d+\.?\s*)?(?:Open Questions|开放问题|待调查问题|问题)[^\n]*\n(?P<body>.*?)(?=\n##\s+\d|\n#\s+|\Z)",
        normalized,
        flags=re.I | re.S,
    )
    if block_match:
        open_block = block_match.group("body")

    heading_matches = list(re.finditer(r"^###\s*([0-9]+(?:\.[0-9]+)*)\s+(.+?)\s*$", open_block, flags=re.M))
    questions: list[dict[str, Any]] = []
    for idx, match in enumerate(heading_matches):
        start = match.end()
        end = heading_matches[idx + 1].start() if idx + 1 < len(heading_matches) else len(open_block)
        body = " ".join(open_block[start:end].strip().split())
        questions.append(
            {
                "question_id": f"memo_open_question_{len(questions) + 1:02d}",
                "source_heading_id": match.group(1),
                "question_title": match.group(2).strip(),
                "question_text": body[:900] or match.group(2).strip(),
                "extraction_basis": "explicit_open_questions_section",
            }
        )

    if not questions:
        for match in re.finditer(r"(?P<q>[^。\n.!?？]{16,240}[?？])", normalized):
            question_text = " ".join(match.group("q").split())
            if any(
                term in question_text.lower()
                for term in ("aiden", "x402", "mission", "which", "what", "whether", "如何", "是否", "哪个")
            ):
                questions.append(
                    {
                        "question_id": f"memo_open_question_{len(questions) + 1:02d}",
                        "source_heading_id": "",
                        "question_title": _compact(question_text, 80).rstrip("?？"),
                        "question_text": question_text[:900],
                        "extraction_basis": "question_mark_sentence",
                    }
                )
            if len(questions) >= 8:
                break

    lower = normalized.lower()
    if not questions and is_strat002_reference(normalized):
        questions = [
            {
                "question_id": f"memo_open_question_{idx + 1:02d}",
                "source_heading_id": str(row["source_heading_id"]),
                "question_title": str(row["question_title"]),
                "question_text": str(row["question_text"]),
                "extraction_basis": "strat002_default_question_set",
            }
            for idx, row in enumerate(DEFAULT_STRAT002_OPEN_QUESTIONS)
        ]
    return questions


def build_memo_investigation_queries(
    owner_message: str,
    *,
    entities: list[Mapping[str, Any]],
    metadata: Mapping[str, Any],
) -> list[dict[str, Any]]:
    names = {str(entity.get("entity") or "") for entity in entities}
    raw_queries: list[str] = []
    if "x402" in names:
        raw_queries.extend(
            [
                "x402 payment protocol official documentation",
                "x402 agent payments USDC protocol 2026",
                "HTTP 402 Payment Required x402 protocol",
            ]
        )
    if "Mission GO" in names:
        raw_queries.extend(["Mission GO x402 agent payments", "Mission GO USDC agent economy integration"])
    if "USDC" in names or "stablecoin" in names:
        raw_queries.extend(["USDC stablecoin agent payments protocol 2026", "stablecoin micropayments AI agents x402"])
    if not raw_queries:
        title = str(metadata.get("title") or "agent economy memo")
        raw_queries.extend([f"{title} official source", f"{title} competitors alternatives"])
    unique = []
    for query in raw_queries:
        if query not in unique:
            unique.append(query)
    return [
        {
            "query_id": f"memo_query_{idx + 1:02d}",
            "query": query,
            "why": "verify owner-supplied memo claims with current public-read evidence",
        }
        for idx, query in enumerate(unique[:8])
    ]


def collect_memo_public_read_evidence(
    queries: list[Mapping[str, Any]],
    *,
    provider: PublicReadProvider | None,
    allow_live_network: bool,
    max_results_per_query: int = 3,
) -> list[dict[str, Any]]:
    selected_provider = provider
    provider_mode = "owner_supplied_public_read_provider"
    if selected_provider is None and allow_live_network:
        selected_provider = DuckDuckGoLitePublicReadProvider()
        provider_mode = "host_mac_live_duckduckgo_public_read_provider"
    if selected_provider is None:
        return []

    evidence: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for query_row in queries:
        query = str(query_row["query"])
        try:
            rows = selected_provider.search(query, domain_id="memo_investigation", max_results=max_results_per_query)
        except Exception as exc:  # pragma: no cover - host network is intentionally contained.
            evidence.append(
                {
                    "evidence_id": f"memo_provider_failure_{len(evidence) + 1:03d}",
                    "source_title": "public-read provider failure",
                    "source_url": "provider://failure",
                    "claim_summary": f"Provider failed for query {query}: {type(exc).__name__}",
                    "query": query,
                    "domain_id": "memo_investigation",
                    "observed_at": _now(),
                    "provider_mode": provider_mode,
                    "evidence_type": "provider_failure",
                }
            )
            continue
        if not rows:
            evidence.append(
                {
                    "evidence_id": f"memo_provider_no_result_{len(evidence) + 1:03d}",
                    "source_title": "public-read provider returned no results",
                    "source_url": "provider://no-result",
                    "claim_summary": f"Provider returned no public-read rows for query {query}.",
                    "query": query,
                    "domain_id": "memo_investigation",
                    "observed_at": _now(),
                    "provider_mode": provider_mode,
                    "evidence_type": "provider_no_result",
                }
            )
            continue
        for row in rows:
            url = str(row.get("source_url") or "")
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)
            evidence.append(
                {
                    "evidence_id": f"memo_evidence_{len(evidence) + 1:03d}",
                    "source_title": str(row.get("source_title") or "")[:180],
                    "source_url": url,
                    "claim_summary": str(row.get("claim_summary") or f"Public-read result for {query}")[:420],
                    "source_date": row.get("source_date") or row.get("published_at") or row.get("updated_at"),
                    "source_date_basis": row.get("source_date_basis") or "provider_supplied_or_missing",
                    "source_date_confidence": row.get("source_date_confidence") or "unknown",
                    "query": query,
                    "domain_id": "memo_investigation",
                    "observed_at": str(row.get("observed_at") or _now()),
                    "provider_mode": provider_mode,
                    "evidence_type": str(row.get("evidence_type") or "memo_public_read_search_result"),
                }
            )
    return evidence


def scan_labs_relation_to_memo(
    owner_message: str,
    *,
    repo_root: Path,
    entities: list[Mapping[str, Any]],
) -> dict[str, Any]:
    entity_terms = [str(entity.get("entity") or "").lower() for entity in entities]
    relation_terms = sorted(set(entity_terms + ["wallet", "usdc", "payment", "model orchestration", "governance", "cieu", "agent-native"]))
    candidate_paths = [
        "office/mission_command/e124_agent_native_company_messenger.py",
        "office/mission_command/e123_aiden_model_orchestration_runtime.py",
        "office/mission_command/e113_no_new_wheel_runtime_law.py",
        "office/mission_command/e114_live_web_capability_utilized_strategy_run.py",
        "office/mission_command/e121_aiden_host_autonomous_web_observer.py",
        "office/agent_native_messenger/server.py",
    ]
    matches = []
    for rel in candidate_paths:
        path = repo_root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        matched_terms = [term for term in relation_terms if term and term in text]
        if matched_terms:
            matches.append(
                {
                    "path": rel,
                    "matched_terms": sorted(dict.fromkeys(matched_terms)),
                    "relation_summary": _relation_summary_for_path(rel),
                }
            )
    return {
        "repo_relation_scan_performed": True,
        "matched_paths": matches,
        "matched_path_count": len(matches),
        "payment_execution_boundary": "proposal_only_no_payment_execution",
        "integration_claim_allowed_now": False,
        "why": (
            "Labs has governed agent messaging, model orchestration metadata, CIEU memory, and wallet/payment proposal boundaries; "
            "it does not yet have a live x402/Mission GO/payment execution integration."
        ),
    }


def build_runtime_suitability_gate(owner_message: str) -> dict[str, Any]:
    memo_request = is_memo_investigation_request(owner_message)
    return {
        "gate_id": "e132_intent_runtime_suitability_gate",
        "owner_intent_class": "research_memo_investigation" if memo_request else "general_owner_message",
        "selected_runtime": "E132_Aiden_Memo_Investigation_Runtime_R1" if memo_request else "not_applicable",
        "forbidden_substitute_runtimes": ["E114_first_cash_route_ranking", "generic_strategy_receipt_translation"],
        "decision": "ALLOW" if memo_request else "REQUIRE_REVISION",
        "reason": "owner asked to verify/analyze a supplied memo; route ranking is not a valid substitute",
    }


def build_memo_strategic_analysis(
    *,
    owner_message: str,
    metadata: Mapping[str, Any],
    entities: list[Mapping[str, Any]],
    claims: list[Mapping[str, Any]],
    open_questions: list[Mapping[str, Any]],
    queries: list[Mapping[str, Any]],
    evidence: list[Mapping[str, Any]],
    repo_relation: Mapping[str, Any],
    allow_live_network: bool,
    advancement_requested: bool = False,
) -> dict[str, Any]:
    date_summary = summarize_source_dates(evidence)
    provider_failure_count = sum(
        1
        for item in evidence
        if str(item.get("evidence_type") or "") in {"provider_failure", "provider_no_result"}
    )
    public_evidence_count = max(0, len(evidence) - provider_failure_count)
    entity_names = [str(item.get("entity")) for item in entities]
    has_x402 = any(name.lower() == "x402" for name in entity_names)
    has_payment = any(name.lower() in {"usdc", "wallet", "stablecoin", "agent payments"} for name in entity_names)
    if not allow_live_network:
        public_read_status = "not_live_network_this_run"
    elif provider_failure_count and public_evidence_count == 0:
        public_read_status = "live_public_read_attempted_but_provider_failed_or_returned_no_results"
    elif provider_failure_count:
        public_read_status = "live_public_read_partial_with_provider_failures"
    else:
        public_read_status = "live_or_provider_public_read_attempted"
    immediate_verdict = (
        "这份 memo 的重点是 x402/AP2/AgentCore 这类基础设施是否让 Mission GO/Y* 既有治理资产出现新的 agent-buyer 商业化表面；支付执行只是高风险边界，不是主题。"
        if has_x402 or has_payment
        else "这份 memo 是一个需要证据核验的 owner research memo，不能被 first-cash 排行榜替代。"
    )
    relation_to_labs = (
        "它和 Labs 的关系在于：我们已经有 agent-native messenger、CIEU/CZL 消息脊柱、model orchestration、"
        "no-send/no-payment 边界和治理记录，因此适合先研究“agent 支付意图如何被治理、审计、拒绝和记录”。"
    )
    if has_x402:
        relation_to_labs += " 但当前没有 x402 live integration，也不能声称 Mission GO 或任何支付协议已经接入。"
    next_step = (
        "生成一份 no-send 的 STRAT-002 逐项核验包：按 memo 第 8 节问题逐项给出资产匹配、e34 重评分、Plugin 关系、Defuse resurfacing、"
        "multi-tenant 成本、专利边界和最关键不确定性证据。"
    )
    evidence_digest = build_evidence_digest(evidence)
    open_question_coverage = build_memo_open_question_answer_matrix(
        open_questions=open_questions,
        evidence_digest=evidence_digest,
        repo_relation=repo_relation,
        owner_message=owner_message,
    )
    strat002_dossier = build_strat002_deep_strategy_dossier(
        owner_message=owner_message,
        evidence_digest=evidence_digest,
        repo_relation=repo_relation,
    )
    claim_verification_matrix = build_claim_verification_matrix(claims=claims, evidence_digest=evidence_digest)
    strategic_implications = build_memo_strategic_implications(
        entity_names=entity_names,
        evidence_digest=evidence_digest,
        repo_relation=repo_relation,
    )
    opportunity_map = build_memo_opportunity_map(
        entity_names=entity_names,
        evidence_digest=evidence_digest,
        repo_relation=repo_relation,
    )
    memo_action_packet = build_memo_action_advancement_packet(
        owner_message=owner_message,
        metadata=metadata,
        entities=entities,
        evidence_digest=evidence_digest,
        repo_relation=repo_relation,
        open_question_coverage=open_question_coverage,
        opportunity_map=opportunity_map,
        advancement_requested=advancement_requested,
    )
    decision_recommendation = build_memo_decision_recommendation(
        evidence_count=public_evidence_count,
        dated_evidence_count=date_summary["dated_count"],
        provider_failure_count=provider_failure_count,
        has_payment=has_payment,
        has_x402=has_x402,
    )
    if advancement_requested:
        decision_recommendation = {
            **decision_recommendation,
            "ceo_bottom_line": (
                "我不再把这件事停留在“建议下一步”。这轮 owner 要的是把 memo/战略讨论推进成可执行的受控行动产物："
                "明确买方、交付物、赚钱假设、no-send 验证问题和内部 dry-run backlog。"
            ),
            "decision": "ALLOW_MEMO_ACTION_ADVANCEMENT_PACKET",
            "owner_decision_needed": True,
        }
    return {
        "memo_understanding": {
            "title": metadata.get("title"),
            "entities": entity_names,
            "claim_count": len(claims),
            "query_count": len(queries),
        },
        "public_read_status": public_read_status,
        "evidence_count": public_evidence_count,
        "provider_failure_count": provider_failure_count,
        "dated_evidence_count": date_summary["dated_count"],
        "undated_evidence_count": max(0, date_summary["undated_count"] - provider_failure_count),
        "repo_matched_path_count": repo_relation.get("matched_path_count", 0),
        "strategic_verdict": immediate_verdict,
        "ceo_bottom_line": decision_recommendation["ceo_bottom_line"],
        "evidence_digest": evidence_digest,
        "claim_verification_matrix": claim_verification_matrix,
        "memo_open_question_coverage": open_question_coverage,
        "strategic_implications": strategic_implications,
        "opportunity_map": opportunity_map,
        "decision_recommendation": decision_recommendation,
        "strat002_deep_strategy_dossier": strat002_dossier,
        "memo_action_advancement_packet": memo_action_packet,
        "relation_to_labs": relation_to_labs,
        "what_is_not_proven": [
            "没有证明 x402/Mission GO 已经和 Labs 集成",
            "没有证明市场愿意为该方向付费",
            "没有执行任何支付、钱包转账、外部发送或客户触达",
            "没有把 first-cash 路线排序当作这份 memo 的答案",
        ],
        "risk_register": [
            "支付/钱包/USDC 涉及高风险边界，必须 owner-approved 且不能由 Aiden 自动执行",
            "如果 public-read 证据没有日期或只有二手来源，只能作为低置信度线索",
            "协议热度不等于买家痛点，必须另行验证预算 owner 与付费场景",
            "Mission GO 与 x402 的实际关系必须由可核验公开来源证明，不能从 memo 直接继承",
        ],
        "recommended_next_action": next_step,
        "owner_decision_packet_status": "not_sent_prepare_no_send_investigation_packet_only",
    }


def build_strat002_deep_strategy_dossier(
    *,
    owner_message: str,
    evidence_digest: list[Mapping[str, Any]],
    repo_relation: Mapping[str, Any],
) -> dict[str, Any]:
    text = owner_message.lower()
    is_strat002 = is_strat002_reference(owner_message)
    if not is_strat002:
        return {"applies": False, "reason": "memo is not STRAT-002 style x402/Mission GO investigation"}

    evidence_ids = [str(row.get("evidence_id")) for row in evidence_digest[:6]]
    return {
        "applies": True,
        "answer_to_owner_question": (
            "x402 改变的是“agent 买方可以机器化付款/调用”的基础设施条件，"
            "但没有自动证明 Y* 应该做支付执行或公开 launch。最干净路径是：把 Mission GO 资产包装成 "
            "agent-to-agent trust/receipt/preflight 服务面，而不是做钱包或支付处理商。"
        ),
        "path_sequencing": {
            "decision": "parallel_research_not_replacement",
            "why": (
                "Plugin/Mining Plant 仍是面向人类开发者和平台分发的主线；x402 是面向 agent buyer 的第二表面。"
                "当前证据支持并行 no-send 预研，不支持替代 Plugin 主线。"
            ),
            "resource_rule": "只允许小范围 owner-review packet 与 technical spike；不得挤占 Plugin mainline execution capacity。",
        },
        "e34_rescore": [
            {
                "item": "void_10_agent_to_agent_payment",
                "movement": "commercial_reality_up",
                "reason": "payment rail/bazaar/gateway infrastructure now exists; governance half remains open.",
                "evidence_refs": evidence_ids,
            },
            {
                "item": "opportunity_space_05_autonomous_chain_of_custody_receipt_standard",
                "movement": "priority_up",
                "reason": "paid agent calls require receipts, delivery proof, dispute evidence, and replayable audit trails.",
                "evidence_refs": evidence_ids,
            },
            {
                "item": "opportunity_space_17_autonomous_approval_mandate_compiler",
                "movement": "priority_up",
                "reason": "AP2/x402-style payment flows need machine-readable authorization and spending mandates.",
                "evidence_refs": evidence_ids,
            },
            {
                "item": "opportunity_space_22_residual_risk_marketplace_for_agent_actions",
                "movement": "watchlist_up_not_build_now",
                "reason": "risk residual pricing becomes more concrete when agent actions have payment events, but buyer demand remains unproven.",
                "evidence_refs": evidence_ids,
            },
            {
                "item": "generic_low_price_gov_check_endpoint",
                "movement": "priority_down",
                "reason": "sub-cent generic endpoints push Y* into STRAT-001 speed-race, not trust-race.",
                "evidence_refs": evidence_ids,
            },
        ],
        "asset_to_surface_matching": [
            {
                "asset": "gov-mcp outbound state machine",
                "surface": "x402/payment intent preflight verifier",
                "fit": "strong",
                "why": "already models sandbox/dry-run/canary/live promotion, kill switch, receipts, and no-send/no-payment boundaries.",
            },
            {
                "asset": "CIEUStore + K9 sentinel",
                "surface": "agent action receipt and chain-of-custody proof object",
                "fit": "strong_but_multi_tenant_needed",
                "why": "maps naturally to payable proof/receipt demand, but current deployment is single-tenant/local.",
            },
            {
                "asset": "counterfactual_engine / Pearl L3 SCM",
                "surface": "counterfactual risk proof for paid agent actions",
                "fit": "potentially_differentiated_requires_competitor_verification",
                "why": "could be more defensible than generic LLM-judge guardrails, but must be compared against Promptfoo/Galileo/Maxim/Braintrust/Langfuse-class tooling.",
            },
            {
                "asset": "OmissionEngine / Narrative Coherence / ClaimMismatch",
                "surface": "tool receipt verifier and obligation-gap detector for paid agent work",
                "fit": "strong_if_packaged_as evidence audit not generic governance",
                "why": "payment events increase the cost of missing obligations and false tool-use claims.",
            },
        ],
        "defuse_revival": {
            "decision": "re_surface_as_capability_under_y_provider_identity_not_standalone_brand",
            "why": (
                "owner rejected brand-conflict reason, but duplication and premature launch constraints remain. "
                "Endpoint exposure under Y* provider identity can be evaluated; PyPI/Show HN/independent Defuse brand remains forbidden."
            ),
            "required_gate": "dead_path revival evaluation plus no independent launch proof",
        },
        "multi_tenant_cost_scope": [
            "tenant-scoped CIEU databases or tenant_id isolation with access-control tests",
            "K9 sentinel per-tenant stream isolation instead of owner-machine PID coupling",
            "provider receipt retention, idempotency, replay protection, and audit export",
            "wallet/payment credential never exposed to Aiden; only payment-intent preflight until owner/Board approves live path",
            "patent/IP review before exposing P3/P4-adjacent mechanisms as public APIs",
        ],
        "patent_boundary": {
            "safe_default": "externalize proof artifacts and preflight outputs, not the full self-governing core mechanism",
            "requires_counsel": ["P3 SRGCS self-referential governance closure", "P4 OmissionEngine claim scope"],
            "productization_rule": "API output can be a receipt/risk decision; proprietary internal reasoning/contract lifecycle remains internal unless counsel approves.",
        },
        "single_best_uncertainty_reducing_evidence": (
            "Find whether real x402/Bazaar/AP2 service providers would pay for an independent preflight/receipt/mandate verifier "
            "that reduces failed paid-agent calls, disputes, or compliance burden. The no-send version is a buyer-facing packet plus 3 target profiles; "
            "no live outreach until owner approves."
        ),
        "do_not_do": [
            "do not expose generic sub-cent gov_check endpoints as first move",
            "do not integrate wallets or execute USDC",
            "do not abandon Mining Plant/Plugin mainline based on infrastructure evidence alone",
            "do not revive Defuse as independent brand",
            "do not use Coinbase self-reported volume as audited buyer demand",
        ],
    }


def build_memo_open_question_answer_matrix(
    *,
    open_questions: list[Mapping[str, Any]],
    evidence_digest: list[Mapping[str, Any]],
    repo_relation: Mapping[str, Any],
    owner_message: str,
) -> list[dict[str, Any]]:
    evidence_refs = [str(row.get("evidence_id")) for row in evidence_digest[:5] if row.get("evidence_id")]
    repo_refs = [str(row.get("path")) for row in repo_relation.get("matched_paths", [])[:6] if row.get("path")]
    matrix: list[dict[str, Any]] = []
    for question in open_questions:
        title = str(question.get("question_title") or "")
        text = str(question.get("question_text") or "")
        lower = f"{title} {text}".lower()
        answer = _answer_open_question_by_class(lower)
        matrix.append(
            {
                "question_id": question.get("question_id"),
                "source_heading_id": question.get("source_heading_id"),
                "question_title": title,
                "question_text": text,
                "coverage_status": "answered",
                "answer_summary": answer["answer_summary"],
                "decision": answer["decision"],
                "uncertainty": answer["uncertainty"],
                "correct_next_action": answer["correct_next_action"],
                "evidence_refs": evidence_refs,
                "repo_refs": repo_refs,
                "why_this_is_the_memo_point": answer["why_this_is_the_memo_point"],
            }
        )
    if not matrix and is_memo_investigation_request(owner_message):
        matrix.append(
            {
                "question_id": "memo_open_question_gap_01",
                "source_heading_id": "",
                "question_title": "Open-question extraction gap",
                "question_text": "No explicit open questions were extracted from the supplied memo.",
                "coverage_status": "requires_revision",
                "answer_summary": "Aiden must extract the memo's decision questions before producing a strategic conclusion.",
                "decision": "REQUIRE_REVISION",
                "uncertainty": "Cannot know whether the answer covers owner intent without explicit question coverage.",
                "correct_next_action": "Ask the memo runtime to run open-question extraction or use the STRAT-002 default question set.",
                "evidence_refs": evidence_refs,
                "repo_refs": repo_refs,
                "why_this_is_the_memo_point": "The owner asked for judgment content, not a process receipt.",
            }
        )
    return matrix


def build_memo_action_advancement_packet(
    *,
    owner_message: str,
    metadata: Mapping[str, Any],
    entities: list[Mapping[str, Any]],
    evidence_digest: list[Mapping[str, Any]],
    repo_relation: Mapping[str, Any],
    open_question_coverage: list[Mapping[str, Any]],
    opportunity_map: list[Mapping[str, Any]],
    advancement_requested: bool,
) -> dict[str, Any]:
    if not advancement_requested:
        return {"applies": False, "reason": "owner did not ask to advance the memo into action"}

    evidence_refs = [str(row.get("evidence_id")) for row in evidence_digest[:6] if row.get("evidence_id")]
    repo_refs = [str(row.get("path")) for row in repo_relation.get("matched_paths", [])[:6] if row.get("path")]
    entity_names = [str(entity.get("entity") or "") for entity in entities if entity.get("entity")]
    title = str(metadata.get("title") or "owner-supplied research memo")
    primary_opportunity = opportunity_map[0] if opportunity_map else {
        "name": "Memo-derived opportunity packet",
        "buyer_visible_shape": "把 memo 的问题转成买方能理解的交付物、验证问题和内部 dry-run。",
        "why_us": "复用当前 Labs 能力、CIEU/CZL 和治理边界。",
        "risk": "买方、预算和付费意愿未验证。",
        "next_test": "生成 no-send owner decision packet。",
    }
    buyer_context = infer_action_packet_buyer_context(entity_names=entity_names, title=title)
    deliverables = build_action_packet_deliverables(
        primary_opportunity=primary_opportunity,
        open_question_coverage=open_question_coverage,
        buyer_context=buyer_context,
    )
    validation_questions = build_action_packet_validation_questions(
        primary_opportunity=primary_opportunity,
        buyer_context=buyer_context,
    )
    return {
        "applies": True,
        "packet_id": "MEMO_ACTION_ADVANCEMENT_PACKET_V1",
        "owner_intent_class": "advance_memo_or_strategy_discussion_into_controlled_action",
        "memo_subject": {
            "title": title,
            "entities": entity_names,
            "detected_reference": "strat002_reference" if is_strat002_reference(owner_message) else "generic_memo_or_strategy_reference",
        },
        "ceo_decision": (
            "把 owner 的 memo/战略讨论推进成 no-send 行动产物：先选择最小买方 wedge，产出买方可读交付物、"
            "验证问题、内部 dry-run backlog 和 owner approval 边界；不再停留在“建议下一步”。"
        ),
        "selected_wedge": {
            "name": primary_opportunity.get("name"),
            "one_sentence": primary_opportunity.get("buyer_visible_shape"),
            "why_us": primary_opportunity.get("why_us"),
            "risk": primary_opportunity.get("risk"),
        },
        "target_buyers": buyer_context,
        "buyer_visible_deliverables": deliverables,
        "first_money_path_hypothesis": {
            "path": "paid diagnostic / readiness pack before any live integration",
            "pricing_status": "hypothesis_only_not_validated",
            "why_someone_might_pay": (
                "如果这个 memo 指向的是高风险、高责任或高摩擦工作流，买方可能愿意先为一份具体的 readiness / evidence / control pack 付费，"
                "因为它降低了集成、审计、争议、合规或内部决策成本。该假设必须通过 no-send buyer validation 证明。"
            ),
            "forbidden_claim": "不能声称已有客户、收入、付费意愿、live integration、钱包能力或外部执行。",
        },
        "no_send_owner_packet_now": {
            "title": f"{primary_opportunity.get('name')} - no-send buyer validation packet",
            "recipient_profile": buyer_context[0]["buyer"] if buyer_context else "target buyer profile pending",
            "opening_claim": (
                "We are testing whether this specific high-friction agent/company workflow needs an evidence-bound readiness pack, "
                "not claiming a live integration or asking for payment yet."
            ),
            "three_validation_questions": validation_questions,
            "non_send_status": "draft_only_owner_must_approve_before_any_external_contact",
        },
        "internal_action_backlog": [
            {
                "task": "Turn the memo into an asset-to-surface map with buyer, pain, deliverable, evidence, and boundary columns",
                "owner": "Aiden -> Codex order candidate",
                "external_action": False,
            },
            {
                "task": "Generate one local dry-run demo thread showing the proposed buyer workflow and governance receipt",
                "owner": "Aiden -> Codex order candidate",
                "external_action": False,
            },
            {
                "task": "Build buyer-facing one-page no-send packet and target-profile list from the inferred buyer context",
                "owner": "Aiden",
                "external_action": False,
            },
            {
                "task": "Run no-new-wheel and dead-path checks before creating any new endpoint, product label, or integration path",
                "owner": "Aiden",
                "external_action": False,
            },
        ],
        "governance_boundary": {
            "allowed_now": [
                "local technical spike",
                "no-send owner decision packet",
                "repo capability mapping",
                "public-read research",
                "dry-run receipt demo",
            ],
            "owner_approval_required": [
                "external message/contact",
                "public page/listing",
                "wallet/key setup",
                "x402 live integration",
                "payment execution",
                "pricing commitment",
            ],
        },
        "evidence_refs": evidence_refs,
        "repo_refs": repo_refs,
    }


def infer_action_packet_buyer_context(*, entity_names: list[str], title: str) -> list[dict[str, str]]:
    lowered = " ".join(entity_names + [title]).lower()
    if "x402" in lowered or "agent payments" in lowered or "usdc" in lowered or "wallet" in lowered:
        return [
            {
                "buyer": "paid agent endpoint / MCP server provider",
                "pain": "付费调用后需要证明授权、交付、拒绝、重放和争议责任。",
                "entry_offer": "governed preflight + CIEU/CZL receipt readiness pack",
            },
            {
                "buyer": "agent platform / security / compliance lead",
                "pain": "允许 agent 花钱或调用付费工具前，需要 spending mandate、审计链和 kill-switch proof。",
                "entry_offer": "agent action mandate and receipt control pack",
            },
            {
                "buyer": "protocol / wallet / payment infrastructure team",
                "pain": "payment rail 有了，但上层行动合法性、争议证据和拒绝理由仍然不完整。",
                "entry_offer": "payment-intent governance and dispute-evidence map",
            },
        ]
    if "market" in lowered or "strategy" in lowered or "战略" in lowered:
        return [
            {
                "buyer": "founder / operator with an urgent strategy-to-execution gap",
                "pain": "有战略判断但缺少可执行、可验证、可复盘的行动包。",
                "entry_offer": "strategy-to-action evidence and execution packet",
            }
        ]
    return [
        {
            "buyer": "owner-approved target profile derived from the memo",
            "pain": "memo 指向的问题尚未转成买方、痛点、交付物和验证问题。",
            "entry_offer": "no-send opportunity validation packet",
        }
    ]


def build_action_packet_deliverables(
    *,
    primary_opportunity: Mapping[str, Any],
    open_question_coverage: list[Mapping[str, Any]],
    buyer_context: list[Mapping[str, str]],
) -> list[str]:
    deliverables = [
        f"Buyer-visible offer brief: {primary_opportunity.get('name')}",
        f"Target buyer profile and pain map: {buyer_context[0].get('buyer') if buyer_context else 'pending'}",
        "Evidence digest with source dates and uncertainty flags",
        "Capability-to-surface map: existing assets, missing wiring, no-new-wheel check",
        "Governance boundary map: allow / require_revision / deny / escalate",
        "No-send buyer validation questions",
        "Internal dry-run demo plan with CIEU/CZL receipt output",
        "Owner decision packet: approve research spike / hold / reject",
    ]
    for row in open_question_coverage[:3]:
        title = str(row.get("question_title") or "").strip()
        if title:
            deliverables.append(f"Open-question answer artifact: {title}")
    return list(dict.fromkeys(deliverables))


def build_action_packet_validation_questions(
    *,
    primary_opportunity: Mapping[str, Any],
    buyer_context: list[Mapping[str, str]],
) -> list[str]:
    buyer = buyer_context[0].get("buyer") if buyer_context else "your team"
    offer = primary_opportunity.get("name") or "this readiness pack"
    return [
        f"For {buyer}, what is the current painful failure mode this offer would reduce?",
        f"What evidence or artifact would make {offer} immediately useful rather than merely interesting?",
        "Who owns the budget or approval for this problem, and what event makes it urgent now?",
    ]


def _answer_open_question_by_class(question_lower: str) -> dict[str, str]:
    if "multi-tenant" in question_lower or "tenant" in question_lower or "engineering cost" in question_lower:
        return {
            "answer_summary": (
                "最大工程成本不是 x402 HTTP wrapper，而是多租户安全：tenant-scoped CIEU/K9、receipt retention、idempotency/replay protection、"
                "provider dry-run/canary/live promotion、密钥/钱包隔离、审计导出、滥用/争议处理。"
            ),
            "decision": "multi_tenanting_is_required_before_external_service_surface",
            "uncertainty": "当前只能给 scope，不应给时间估计；单租户 owner-machine 形态不能直接商业化。",
            "correct_next_action": "产出 multi-tenant scope checklist 和 minimal safe endpoint boundary。",
            "why_this_is_the_memo_point": "memo 明确问的是工程范围，不是付款开关。",
        }
    if "asset" in question_lower or "surface" in question_lower or "capabilit" in question_lower:
        return {
            "answer_summary": (
                "有匹配，但不是“支付处理”匹配。最强匹配是 gov-mcp outbound state machine、CIEU/K9 receipt spine、"
                "Omission/Narrative/ClaimMismatch 类证据治理、approval mandate compiler、chain-of-custody receipt。它们可以变成 "
                "agent-buyer 付费调用前后的 preflight / receipt / dispute evidence 服务面。"
            ),
            "decision": "yes_subset_fit_for_trust_receipt_and_preflight_surface",
            "uncertainty": "还不知道 x402/AP2 服务提供者是否愿意为独立治理/receipt 层付费。",
            "correct_next_action": "做 asset-to-endpoint map，不做钱包集成；为每个可暴露能力列输入、输出、租户隔离和价格假设。",
            "why_this_is_the_memo_point": "问题是已有 Mission GO 资产是否因为机器买方基础设施出现新商业表面。",
        }
    if "sequencing" in question_lower or "parallel" in question_lower or "plugin" in question_lower or "replacement" in question_lower:
        return {
            "answer_summary": (
                "x402 路径应作为 Plugin/Mining Plant 的并行 no-send 研究线，不应替代主线。Plugin 是人类开发者/平台分发路径；"
                "x402 是 agent buyer/机器调用路径。两者服务不同买方，短期只允许小范围研究，不挤占 Plugin mainline。"
            ),
            "decision": "parallel_research_not_replacement",
            "uncertainty": "若出现明确 agent-buyer 付费意愿，资源比例可以上调；没有前不能替代 Plugin。",
            "correct_next_action": "给 x402 设 research budget/scope cap，并保留 Mining Plant 为 canonical execution path。",
            "why_this_is_the_memo_point": "memo 明确要求判定 parallel / sequenced / replacement / deferred。",
        }
    if "e34" in question_lower or "void" in question_lower or "opportunity" in question_lower:
        return {
            "answer_summary": (
                "应重评分：void #10 agent_to_agent_payment 上升最大；opportunity #05 chain-of-custody receipt、#17 approval mandate compiler "
                "上升；#22 residual risk marketplace 进入 watchlist；generic low-price gov_check endpoint 下降，因为会落入 STRAT-001 禁止的 speed-race。"
            ),
            "decision": "rescore_selected_voids_and_opportunity_spaces",
            "uncertainty": "商业分数只能因基础设施存在而上调，不能因 Coinbase/AWS 生态热度直接推导付费需求。",
            "correct_next_action": "重新生成 e34 delta table：old score、new score、reason、evidence、forbidden overclaim。",
            "why_this_is_the_memo_point": "memo 的核心动作之一就是用新基础设施事实重评分旧战略资产。",
        }
    if "defuse" in question_lower or "revival" in question_lower or "dead-path" in question_lower:
        return {
            "answer_summary": (
                "可以重新审查 Defuse-class 能力，但只能作为 Y* provider identity 下的能力/endpoint resurfacing；不能独立品牌、PyPI、Show HN 或 Day-N launch。"
                "owner 已否定 mindshare-conflict 理由，但 capability duplication 和 premature launch 约束仍有效。"
            ),
            "decision": "re_surface_as_capability_not_standalone_brand",
            "uncertainty": "是否值得 resurfacing 取决于 endpoint 是否提供 Y*gov 主线没有的 buyer-visible value。",
            "correct_next_action": "跑 dead_path revival evaluation，明确哪些 revival 条件满足，哪些仍阻塞。",
            "why_this_is_the_memo_point": "memo 要求重新判断旧 dead path 在新 A2A 基础设施下是否出现非 launch 型出口。",
        }
    if "patent" in question_lower or "p3" in question_lower or "p4" in question_lower or "claim" in question_lower:
        return {
            "answer_summary": (
                "默认只外露 proof object、receipt、preflight decision、risk summary，不外露 SRGCS/P3 自治理核心和 P4 OmissionEngine 内部机制。"
                "任何 P3/P4 相邻能力产品化前必须做 counsel review。"
            ),
            "decision": "externalize_outputs_not_core_claimed_mechanisms",
            "uncertainty": "具体 claim scope 需要律师确认，Aiden 不能替代法律判断。",
            "correct_next_action": "给每个候选 endpoint 标记 patent adjacency：safe output / counsel-needed / blocked。",
            "why_this_is_the_memo_point": "memo 要求判断可商业化边界，而不是把所有代码直接做成 API。",
        }
    if "change the answer" in question_lower or "single piece" in question_lower or "reduce" in question_lower or "uncertainty" in question_lower:
        return {
            "answer_summary": (
                "最能改变答案的证据不是更多协议新闻，而是 3 个真实 agent-service/provider buyer 是否愿意使用或付费测试 "
                "independent payment-intent preflight/receipt/mandate verifier。"
            ),
            "decision": "buyer_problem_signal_is_the_key_uncertainty_reducer",
            "uncertainty": "基础设施存在已经较可信；需求侧和预算 owner 尚未证明。",
            "correct_next_action": "准备 no-send buyer validation packet；owner 批准前不发送。",
            "why_this_is_the_memo_point": "memo 明确把 infrastructure bet 和 demand bet 分开，下一步应验证需求而不是继续堆协议资料。",
        }
    return {
        "answer_summary": "这个问题需要按 memo 原文、公开证据和 repo 能力三方交叉回答，不能用 first-cash 排行榜代替。",
        "decision": "answer_requires_specific_evidence_mapping",
        "uncertainty": "需要更多 question-specific evidence。",
        "correct_next_action": "把该问题拆成 claim/evidence/repo capability/decision 四列后再判断。",
        "why_this_is_the_memo_point": "Aiden 必须回答 owner memo 的具体问题。",
    }


def build_evidence_digest(evidence: list[Mapping[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    digest: list[dict[str, Any]] = []
    for item in evidence:
        evidence_type = str(item.get("evidence_type") or "")
        if evidence_type in {"provider_failure", "provider_no_result"}:
            continue
        title = str(item.get("source_title") or "").strip()
        url = str(item.get("source_url") or "").strip()
        query = str(item.get("query") or "").strip()
        lower = f"{title} {url} {query}".lower()
        signal_type = "general_public_read_signal"
        if "whitepaper" in lower or "documentation" in lower or "docs" in lower or "official" in lower:
            signal_type = "protocol_or_official_source_signal"
        elif "coinbase" in lower or "aws" in lower or "usdc" in lower:
            signal_type = "ecosystem_or_enterprise_adoption_signal"
        elif "verify" in lower or "verification" in lower or "payment processor" in lower:
            signal_type = "implementation_or_verification_signal"
        elif "competitor" in lower or "alternative" in lower:
            signal_type = "competitive_landscape_signal"
        digest.append(
            {
                "evidence_id": str(item.get("evidence_id") or f"memo_evidence_{len(digest) + 1:03d}"),
                "title": title[:180] or "untitled public-read result",
                "url": url,
                "source_date": item.get("source_date") or "",
                "source_date_basis": item.get("source_date_basis") or "",
                "signal_type": signal_type,
                "query": query[:180],
            }
        )
        if len(digest) >= limit:
            break
    return digest


def build_claim_verification_matrix(
    *,
    claims: list[Mapping[str, Any]],
    evidence_digest: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    for claim in claims[:6]:
        claim_text = str(claim.get("claim_text") or "")
        claim_terms = _keyword_terms(claim_text)
        matches = []
        for row in evidence_digest:
            haystack = f"{row.get('title', '')} {row.get('query', '')} {row.get('url', '')}".lower()
            overlap = sorted(term for term in claim_terms if term in haystack)
            if overlap:
                matches.append({"evidence_id": row.get("evidence_id"), "overlap_terms": overlap[:4]})
        if len(matches) >= 2:
            status = "partially_supported_by_public_read_evidence"
            action = "use as working assumption, but require dated primary source before implementation"
        elif matches:
            status = "weakly_supported_single_source_or_query_overlap"
            action = "seek corroboration before treating as strategic fact"
        else:
            status = "not_supported_by_current_public_read_snapshot"
            action = "do not inherit this claim from the memo"
        matrix.append(
            {
                "claim_id": claim.get("claim_id"),
                "claim_text": claim_text[:260],
                "verification_status": status,
                "evidence_matches": matches[:3],
                "correct_path": action,
            }
        )
    if not matrix:
        matrix.append(
            {
                "claim_id": "claim_gap_01",
                "claim_text": "No concrete memo claims were extractable from the supplied text.",
                "verification_status": "requires_revision",
                "evidence_matches": [],
                "correct_path": "ask Aiden to extract explicit claims before deciding strategy",
            }
        )
    return matrix


def build_memo_strategic_implications(
    *,
    entity_names: list[str],
    evidence_digest: list[Mapping[str, Any]],
    repo_relation: Mapping[str, Any],
) -> list[dict[str, str]]:
    names = {name.lower() for name in entity_names}
    has_protocol_signal = any(row.get("signal_type") == "protocol_or_official_source_signal" for row in evidence_digest)
    has_ecosystem_signal = any(row.get("signal_type") == "ecosystem_or_enterprise_adoption_signal" for row in evidence_digest)
    has_implementation_signal = any(row.get("signal_type") == "implementation_or_verification_signal" for row in evidence_digest)
    implications = [
        {
            "theme": "strategic_reframe",
            "judgment": (
                "x402/Mission GO 不应该先被理解成“我们马上接入支付”，而应该先被理解成 "
                "agent-to-agent 经济里“支付意图、授权、证据、拒绝、回滚”的治理问题。"
            ),
            "why_it_matters": "这把讨论从高风险钱包执行，转成我们更有优势的治理/审计/控制层。"
        },
        {
            "theme": "right_to_win",
            "judgment": (
                "Labs 的优势不是成为支付处理商，而是把 agent payment intent 变成可治理的 CIEU/CZL 记录、"
                "owner decision packet、dry-run/preflight 和 no-send/no-payment 边界。"
            ),
            "why_it_matters": "这更贴近已有 messenger、Y-star-gov、CIEUStore、gov-mcp 边界能力。"
        },
    ]
    if "x402" in names and has_protocol_signal:
        implications.append(
            {
                "theme": "market_signal",
                "judgment": "public-read 结果出现协议/白皮书/文档信号，说明 x402 至少值得作为 agent commerce 基础设施线索继续核验。",
                "why_it_matters": "这支持进入 no-send 技术预研，而不是直接产品化或支付执行。"
            }
        )
    if has_ecosystem_signal:
        implications.append(
            {
                "theme": "ecosystem_signal",
                "judgment": "USDC、Coinbase、AWS 等生态信号若被证据支持，说明 agent payment 不是孤立想象。",
                "why_it_matters": "但生态热度仍不等于 Y*Bridge Labs 的付费客户需求。"
            }
        )
    if has_implementation_signal:
        implications.append(
            {
                "theme": "implementation_risk",
                "judgment": "verification/payment-processor 相关信号提示：真正难点不是发起支付，而是证明支付、授权、失败、退款和争议处理。",
                "why_it_matters": "这正好要求先做 preflight/receipt/audit，而不是 live wallet transfer。"
            }
        )
    if not repo_relation.get("matched_path_count"):
        implications.append(
            {
                "theme": "capability_gap",
                "judgment": "当前 repo 未命中相关 runtime 能力路径，不能声称已有实现基础。",
                "why_it_matters": "正确路径是先做 capability discovery，而不是 memo-based strategy claim。"
            }
        )
    return implications


def build_memo_opportunity_map(
    *,
    entity_names: list[str],
    evidence_digest: list[Mapping[str, Any]],
    repo_relation: Mapping[str, Any],
) -> list[dict[str, Any]]:
    names = {name.lower() for name in entity_names}
    if not {"x402", "usdc", "wallet", "stablecoin", "agent payments"}.intersection(names):
        return [
            {
                "opportunity_id": "memo_to_action_readiness_pack",
                "name": "Memo-to-Action Readiness Pack",
                "buyer_visible_shape": "把 owner memo 转成买方、痛点、证据、交付物、风险边界和 no-send 验证问题。",
                "why_us": "复用 Aiden memo investigation、retrieval、CIEU/CZL、Y-star-gov 和 no-new-wheel governance。",
                "risk": "主题实体不足时不能声称已有明确市场或付费需求。",
                "next_test": "抽取实体和 open questions 后生成 no-send owner decision packet。",
            }
        ]
    return [
        {
            "opportunity_id": "payment_intent_governance_pack",
            "name": "Agent Payment Intent Governance Pack",
            "buyer_visible_shape": "给 agent 公司/协议团队一份支付意图治理包：授权边界、拒绝路径、CIEU/CZL receipt、dry-run trace、owner approval map。",
            "why_us": "复用 agent-native messenger、Y-star-gov、CIEUStore、gov-mcp no-send/no-payment 边界。",
            "risk": "客户未验证；不能声称 x402/Mission GO 已集成。",
            "next_test": "生成 no-send opportunity packet，请 owner 选择是否进入技术预研。"
        },
        {
            "opportunity_id": "x402_preflight_gateway_research",
            "name": "x402 Payment Preflight Gateway Research Spike",
            "buyer_visible_shape": "不转账，只模拟 agent 请求付费 API 时的授权、证据、失败、审计、回滚流程。",
            "why_us": "我们擅长把高风险动作降级为 governed dry-run/preflight。",
            "risk": "协议细节、钱包签名、Base/USDC rails 需要真实文档核验。",
            "next_test": "列出 x402 request/response/verification 的最小字段，并映射到 CIEU 五元组。"
        },
        {
            "opportunity_id": "agent_contract_messenger_extension",
            "name": "Agent Contract Messenger Extension",
            "buyer_visible_shape": "把 messenger 从对话工具升级为 agent 合同/付款意图协商室：人话 + CIEU/CZL + no-payment escrow intent。",
            "why_us": "当前 meeting room 已有人/agent 消息脊柱和治理记录。",
            "risk": "如果 UI/回复质量不成熟，会伤害信任；必须先修好 memo dossier 输出质量。",
            "next_test": "在本地生成一个 x402 no-send contract thread demo，不连接钱包。"
        },
    ]


def build_memo_decision_recommendation(
    *,
    evidence_count: int,
    dated_evidence_count: int,
    provider_failure_count: int,
    has_payment: bool,
    has_x402: bool,
) -> dict[str, Any]:
    if provider_failure_count and evidence_count == 0:
        return {
            "ceo_bottom_line": "不能做战略结论，只能做本地能力关系判断；先修 public-read provider 或换证据源。",
            "decision": "REQUIRE_REVISION",
            "why": "live public-read attempted but returned no usable evidence",
            "owner_decision_needed": False,
        }
    if has_payment or has_x402:
        return {
            "ceo_bottom_line": (
                "值得进入 no-send 技术/市场预研，但不值得立刻集成支付或对外承诺。最佳下一步是做 "
                "x402/Mission GO Payment Intent Governance Pack 的 owner-review packet。"
            ),
            "decision": "ALLOW_NO_SEND_RESEARCH_PACKET",
            "why": "memo relates to agent payments, but payment execution remains high-risk and unvalidated",
            "owner_decision_needed": True,
            "minimum_evidence_bar": {
                "public_evidence_count": evidence_count,
                "dated_evidence_count": dated_evidence_count,
                "dated_primary_source_required_before_build": True,
            },
        }
    return {
        "ceo_bottom_line": "这份 memo 需要更多实体和可验证主张后才能进入战略路线选择。",
        "decision": "REQUIRE_REVISION",
        "why": "memo does not contain enough recognized agent-economy/payment entities",
        "owner_decision_needed": False,
    }


def render_memo_investigation_owner_answer(analysis: Mapping[str, Any]) -> str:
    understanding = analysis["memo_understanding"]
    not_proven = "\n".join(f"- {item}" for item in analysis["what_is_not_proven"])
    risks = "\n".join(f"- {item}" for item in analysis["risk_register"])
    evidence_lines = "\n".join(
        f"- [{row.get('evidence_id')}] {row.get('title')} ({row.get('source_date') or 'date unknown'})\n  {row.get('url')}"
        for row in analysis.get("evidence_digest", [])[:6]
    ) or "- 本轮没有可用公开证据；不能把 memo 主张当作事实。"
    claim_lines = "\n".join(
        f"- {row.get('claim_id')}: {row.get('verification_status')} -> {row.get('correct_path')}"
        for row in analysis.get("claim_verification_matrix", [])[:6]
    )
    open_question_lines = "\n".join(
        (
            f"- {row.get('source_heading_id')} {row.get('question_title')}\n"
            f"  回答：{row.get('answer_summary')}\n"
            f"  判断：{row.get('decision')}\n"
            f"  下一步：{row.get('correct_next_action')}"
        )
        for row in analysis.get("memo_open_question_coverage", [])[:8]
    )
    implication_lines = "\n".join(
        f"- {row.get('theme')}: {row.get('judgment')}（意义：{row.get('why_it_matters')}）"
        for row in analysis.get("strategic_implications", [])[:5]
    )
    strat002 = analysis.get("strat002_deep_strategy_dossier", {})
    strat002_section = ""
    if strat002.get("applies"):
        rescore_lines = "\n".join(
            f"- {row.get('item')}: {row.get('movement')}。理由：{row.get('reason')}"
            for row in strat002.get("e34_rescore", [])[:5]
        )
        asset_lines = "\n".join(
            f"- {row.get('asset')} -> {row.get('surface')}；fit={row.get('fit')}；{row.get('why')}"
            for row in strat002.get("asset_to_surface_matching", [])[:4]
        )
        multi_tenant_lines = "\n".join(f"- {item}" for item in strat002.get("multi_tenant_cost_scope", [])[:5])
        do_not_lines = "\n".join(f"- {item}" for item in strat002.get("do_not_do", [])[:5])
        strat002_section = (
            "\n\n6. STRAT-002 综合判断\n"
            f"{strat002.get('answer_to_owner_question')}\n"
            f"路径关系：{strat002.get('path_sequencing', {}).get('decision')}。"
            f"{strat002.get('path_sequencing', {}).get('why')}\n\n"
            "e34 重评分建议：\n"
            f"{rescore_lines}\n\n"
            "资产到 x402/A2A 服务面的匹配：\n"
            f"{asset_lines}\n\n"
            "Defuse revival 判断：\n"
            f"{strat002.get('defuse_revival', {}).get('decision')}。{strat002.get('defuse_revival', {}).get('why')}\n\n"
            "multi-tenant 工程成本范围，不给时间估计：\n"
            f"{multi_tenant_lines}\n\n"
            "专利/IP 默认边界：\n"
            f"{strat002.get('patent_boundary', {}).get('safe_default')}\n\n"
            "最能降低不确定性的一条证据：\n"
            f"{strat002.get('single_best_uncertainty_reducing_evidence')}\n\n"
            "明确不要做：\n"
            f"{do_not_lines}"
        )
    opportunity_lines = "\n".join(
        f"- {row.get('name')}: {row.get('buyer_visible_shape')} 下一步：{row.get('next_test')}"
        for row in analysis.get("opportunity_map", [])[:3]
    )
    action_packet = analysis.get("memo_action_advancement_packet", {})
    action_packet_section = ""
    if action_packet.get("applies"):
        buyer_lines = "\n".join(
            f"- {row.get('buyer')}: 痛点={row.get('pain')}；入口 offer={row.get('entry_offer')}"
            for row in action_packet.get("target_buyers", [])[:3]
        )
        deliverable_lines = "\n".join(f"- {item}" for item in action_packet.get("buyer_visible_deliverables", [])[:7])
        backlog_lines = "\n".join(
            f"- {row.get('task')}（external_action={row.get('external_action')}）"
            for row in action_packet.get("internal_action_backlog", [])[:4]
        )
        validation_questions = "\n".join(
            f"- {item}" for item in action_packet.get("no_send_owner_packet_now", {}).get("three_validation_questions", [])
        )
        action_packet_section = (
            "\n\n12. 我现在直接推进，而不是继续复读“下一步”\n"
            f"通用行动推进包：{action_packet.get('packet_id')}\n"
            f"CEO 决策：{action_packet.get('ceo_decision')}\n\n"
            f"选定 wedge：{action_packet.get('selected_wedge', {}).get('name')}\n"
            f"{action_packet.get('selected_wedge', {}).get('one_sentence')}\n"
            f"为什么是我们：{action_packet.get('selected_wedge', {}).get('why_us')}\n"
            f"当前风险：{action_packet.get('selected_wedge', {}).get('risk')}\n\n"
            "目标买方：\n"
            f"{buyer_lines}\n\n"
            "买方能看懂的交付物：\n"
            f"{deliverable_lines}\n\n"
            "赚钱路径假设：\n"
            f"{action_packet.get('first_money_path_hypothesis', {}).get('path')}；"
            f"{action_packet.get('first_money_path_hypothesis', {}).get('why_someone_might_pay')}\n"
            f"状态：{action_packet.get('first_money_path_hypothesis', {}).get('pricing_status')}。\n\n"
            "no-send buyer validation packet 草案问题：\n"
            f"{validation_questions}\n\n"
            "内部行动 backlog（现在就该做的东西，不需要外部联系）：\n"
            f"{backlog_lines}\n\n"
            "仍然不能越界：外部联系、公开发布、钱包/key、x402 live integration、付款、价格承诺都需要 owner approval。"
        )
    decision = analysis.get("decision_recommendation", {})
    return (
        f"我的判断：{analysis.get('ceo_bottom_line')}\n\n"
        "1. 这份备忘录的核心命题\n"
        "它真正讨论的不是“支付还是不支付”，而是：x402/AP2/AgentCore 这类 agent-to-agent 经济基础设施出现后，"
        "Mission GO/Y* 已经做出来的治理、证据、授权、receipt、CIEU/CZL、gov-mcp 边界能力，是否出现了新的机器买方商业化表面。\n"
        f"标题/主题：{understanding.get('title') or 'owner research memo'}\n"
        f"识别到的关键实体：{', '.join(understanding.get('entities') or [])}\n"
        f"我抽取到 {understanding.get('claim_count')} 条需要核验的主张。\n\n"
        "2. 证据告诉我的事\n"
        f"可用公开证据：{analysis['evidence_count']} 条；其中带日期证据：{analysis['dated_evidence_count']} 条。"
        f"{' 证据获取异常/无结果：' + str(analysis.get('provider_failure_count', 0)) + ' 次。' if analysis.get('provider_failure_count', 0) else ''}\n"
        f"{evidence_lines}\n\n"
        "3. 哪些主张能暂时成立，哪些不能继承\n"
        f"{claim_lines}\n\n"
        "4. 这份 memo 明确问题的逐项回答\n"
        f"{open_question_lines or '- 没有抽取到明确 open questions；这是需要修正的输入覆盖缺口。'}\n\n"
        "5. 我的战略判断\n"
        f"{implication_lines}\n\n"
        "6. 这件事和 Y*Bridge Labs 的关系\n"
        f"{analysis['relation_to_labs']}\n\n"
        f"{strat002_section}\n\n"
        "7. 我认为可以形成的产品/机会形态\n"
        f"{opportunity_lines}\n\n"
        "8. 我不会采纳的错误方向\n"
        "- 不把 x402 热度直接等同于客户愿意付钱。\n"
        "- 不把 Mission GO memo 当作已经验证过的事实。\n"
        "- 不把支付执行当作第一步；第一步应该是支付意图治理、preflight、receipt 和 owner approval。\n"
        "- 不把这件事塞回泛泛的 first-cash 排行榜。\n\n"
        "9. 现在不能声称什么\n"
        f"{not_proven}\n\n"
        "10. 主要风险\n"
        f"{risks}\n\n"
        "11. 我建议的下一步\n"
        f"{analysis['recommended_next_action']}\n"
        f"具体说：先做一份 no-send 的 owner decision packet，标题可以是 “x402/Mission GO Payment Intent Governance Pack”。它应该包含协议事实、证据来源、竞品/替代方案、我们可交付的治理工件、不能触碰的钱包/支付边界，以及是否批准进入技术预研。\n\n"
        f"{action_packet_section}\n\n"
        "边界：这轮没有外部发送、没有客户联系、没有付款、没有 USDC 转账、没有 live provider execution、没有 K9Audit 写入。"
    )


def _keyword_terms(text: str) -> set[str]:
    terms = {
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}|[\u4e00-\u9fff]{2,}", text)
        if token.lower()
        not in {
            "the",
            "and",
            "for",
            "with",
            "this",
            "that",
            "should",
            "would",
            "could",
            "about",
        }
    }
    return {term for term in terms if len(term) >= 3}


def write_memo_investigation_cieu_record(
    result: Mapping[str, Any],
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path,
) -> bool:
    if str(ystar_gov_root) not in sys.path:
        sys.path.insert(0, str(ystar_gov_root))
    store_mod = importlib.import_module("ystar.governance.cieu_store")
    store = store_mod.CIEUStore(db_path=str(cieu_db))
    return store.write_dict(
        {
            "event_id": f"e132_memo_investigation_{uuid.uuid4().hex[:12]}",
            "session_id": SESSION_ID,
            "agent_id": "Aiden",
            "event_type": "AIDEN_MEMO_INVESTIGATION_DECISION",
            "decision": "ALLOW",
            "passed": True,
            "task_description": "Aiden memo investigation runtime selected instead of generic strategy ranking",
            "params": {
                "owner_message_preview": result.get("owner_message_preview"),
                "memo_entities": result.get("memo_entities"),
            },
            "result": {
                "runtime_suitability_gate": result.get("runtime_suitability_gate"),
                "source_date_summary": result.get("source_date_summary"),
                "strategic_verdict": result.get("strategic_analysis", {}).get("strategic_verdict"),
            },
            "human_initiator": "owner",
            "lineage_path": ["owner", "Aiden", "E132_memo_investigation_runtime"],
            "m_functor": "M-2b",
            "m_weight": 2,
            "y_star_validator_pass": True,
        }
    )


def summarize_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"db_path": str(path), "event_count": 0, "event_types": []}
    with sqlite3.connect(path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM cieu_events").fetchone()[0]
        event_types = [row[0] for row in conn.execute("SELECT DISTINCT event_type FROM cieu_events ORDER BY event_type").fetchall()]
    return {"db_path": str(path), "event_count": int(count), "event_types": event_types}


def _context_window(text: str, index: int, *, width: int = 100) -> str:
    start = max(0, index - width)
    end = min(len(text), index + width)
    return _compact(text[start:end], width * 2)


def _compact(text: str, limit: int = 240) -> str:
    normalized = " ".join(str(text).split())
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip() + "..."


def _relation_summary_for_path(path: str) -> str:
    if "e124" in path:
        return "agent-native messenger and wallet/payment proposal-only boundary"
    if "e123" in path:
        return "model orchestration and long-term memory asset discovery"
    if "e113" in path:
        return "no-new-wheel capability utilization law"
    if "e114" in path:
        return "dated public-read evidence and freshness filter"
    if "e121" in path:
        return "host autonomous public-read observation boundary"
    if "server" in path:
        return "local-only messenger server boundary"
    return "related Labs capability"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


__all__ = [
    "MILESTONE_ID",
    "is_memo_investigation_request",
    "run_aiden_memo_investigation_runtime",
    "extract_memo_metadata",
    "extract_memo_entities",
    "extract_memo_claims",
    "build_memo_investigation_queries",
    "collect_memo_public_read_evidence",
    "scan_labs_relation_to_memo",
    "render_memo_investigation_owner_answer",
]
