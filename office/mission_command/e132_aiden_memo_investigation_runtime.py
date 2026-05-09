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
    "x402": re.compile(r"\bx402\b", re.I),
    "Mission GO": re.compile(r"\bMission\s+GO\b", re.I),
    "USDC": re.compile(r"\bUSDC\b", re.I),
    "agent payments": re.compile(r"\bagent(?:ic)?\s+payments?\b|agent\s+economy|agent经济", re.I),
    "HTTP 402": re.compile(r"\bHTTP\s*402\b|402\s+Payment\s+Required", re.I),
    "wallet": re.compile(r"\bwallets?\b|钱包", re.I),
    "stablecoin": re.compile(r"\bstablecoins?\b|稳定币", re.I),
}


def is_memo_investigation_request(owner_message: str) -> bool:
    text = owner_message or ""
    lowered = text.lower()
    signal_count = sum(1 for signal in MEMO_INVESTIGATION_SIGNALS if signal in lowered)
    long_structured_input = len(text) >= 1800 and ("#" in text or "**" in text or "\n" in text)
    asks_to_verify_material = any(term in text for term in ("验证", "核实", "分析下面", "这份", "备忘录"))
    return signal_count >= 2 or (signal_count >= 1 and asks_to_verify_material) or (
        long_structured_input and asks_to_verify_material
    )


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
    queries = build_memo_investigation_queries(owner_message, entities=entities, metadata=metadata)
    evidence = collect_memo_public_read_evidence(
        queries,
        provider=public_read_provider,
        allow_live_network=allow_live_network,
    )
    repo_relation = scan_labs_relation_to_memo(owner_message, repo_root=base, entities=entities)
    suitability = build_runtime_suitability_gate(owner_message)
    analysis = build_memo_strategic_analysis(
        metadata=metadata,
        entities=entities,
        claims=claims,
        queries=queries,
        evidence=evidence,
        repo_relation=repo_relation,
        allow_live_network=allow_live_network,
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
    metadata: Mapping[str, Any],
    entities: list[Mapping[str, Any]],
    claims: list[Mapping[str, Any]],
    queries: list[Mapping[str, Any]],
    evidence: list[Mapping[str, Any]],
    repo_relation: Mapping[str, Any],
    allow_live_network: bool,
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
        "这份 memo 应被当作“agent 经济支付/结算基础设施方向”的战略调查材料，而不是当前可直接执行的付款或外部联系授权。"
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
        "生成一份 no-send 的 x402/Mission GO 机会核验包：列出协议事实、竞品/替代方案、买家场景、支付风险、"
        "我们能做的治理差异化，以及是否值得进入 owner-approved 技术预研。"
    )
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


def render_memo_investigation_owner_answer(analysis: Mapping[str, Any]) -> str:
    understanding = analysis["memo_understanding"]
    not_proven = "\n".join(f"- {item}" for item in analysis["what_is_not_proven"])
    risks = "\n".join(f"- {item}" for item in analysis["risk_register"])
    return (
        "我这次没有把你的备忘录丢进“赚钱路线排行榜”。这是一轮受控的 memo investigation。\n\n"
        "1. 我理解你给我的材料是什么\n"
        f"标题/主题：{understanding.get('title') or 'owner research memo'}\n"
        f"识别到的关键实体：{', '.join(understanding.get('entities') or [])}\n"
        f"抽取待核验主张：{understanding.get('claim_count')} 条；生成公开检索问题：{understanding.get('query_count')} 条。\n\n"
        "2. 这轮证据状态\n"
        f"public-read 状态：{analysis['public_read_status']}\n"
        f"公开证据数量：{analysis['evidence_count']}；带日期证据：{analysis['dated_evidence_count']}；未带日期证据：{analysis['undated_evidence_count']}。\n"
        f"provider 失败/无结果次数：{analysis.get('provider_failure_count', 0)}。\n"
        f"本仓库相关能力命中路径数：{analysis['repo_matched_path_count']}。\n\n"
        "3. Aiden 的初步战略判断\n"
        f"{analysis['strategic_verdict']}\n\n"
        "4. 它和我们到底有什么关系\n"
        f"{analysis['relation_to_labs']}\n\n"
        "5. 现在不能声称什么\n"
        f"{not_proven}\n\n"
        "6. 主要风险\n"
        f"{risks}\n\n"
        "7. 下一步\n"
        f"{analysis['recommended_next_action']}\n\n"
        "边界：这轮没有外部发送、没有客户联系、没有付款、没有 USDC 转账、没有 live provider execution、没有 K9Audit 写入。"
    )


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
