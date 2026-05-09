from __future__ import annotations

import html
import importlib
import math
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

from office.mission_command.e105_open_world_market_discovery_runtime import query_brain_for_stage
from office.mission_command.e107_strategy_math_model_runtime import (
    build_mathematical_source_map,
    build_parameter_registry,
)


MILESTONE_ID = "E108_Live_Global_Open_World_Market_Discovery_Runtime_R1"
SESSION_ID = "e108_live_global_open_world_strategy_runtime"
Y_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")

ANCHOR_DOMAINS = {"ai_agent_ops", "cpa_tax_accounting", "tariff_supply_chain"}


class PublicReadProvider(Protocol):
    def search(self, query: str, *, domain_id: str, max_results: int = 3) -> list[dict[str, Any]]:
        ...


@dataclass(frozen=True)
class DuckDuckGoLitePublicReadProvider:
    timeout_seconds: int = 8
    user_agent: str = "Mozilla/5.0 YStarBridgeLabsAidenPublicRead/1.0"

    def search(self, query: str, *, domain_id: str, max_results: int = 3) -> list[dict[str, Any]]:
        encoded = urllib.parse.urlencode({"q": query})
        url = f"https://duckduckgo.com/html/?{encoded}"
        request = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="ignore")
        results: list[dict[str, Any]] = []
        pattern = re.compile(r'<a[^>]+class="result__a"[^>]+href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>', re.I | re.S)
        for match in pattern.finditer(body):
            href = html.unescape(match.group("href"))
            title = _strip_tags(html.unescape(match.group("title"))).strip()
            if not href or not title:
                continue
            results.append(
                {
                    "source_title": title[:180],
                    "source_url": href,
                    "claim_summary": f"Public-read search result for: {query}",
                    "domain_id": domain_id,
                    "query": query,
                    "observed_at": _now(),
                    "evidence_type": "live_public_read_search_result",
                }
            )
            if len(results) >= max_results:
                break
        return results


@dataclass(frozen=True)
class FixtureGlobalPublicReadProvider:
    """Deterministic public-read provider used by tests and bridge validation."""

    def search(self, query: str, *, domain_id: str, max_results: int = 3) -> list[dict[str, Any]]:
        rows = [item for item in fixture_global_public_read_evidence() if item["domain_id"] == domain_id]
        return rows[:max_results]


def _load_ystar_module(module_name: str, ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) in sys.path:
        sys.path.remove(str(root))
    if root.exists():
        sys.path.insert(0, str(root))
        try:
            import ystar  # type: ignore
            import ystar.governance  # type: ignore

            ystar_path = str(root / "ystar")
            governance_path = str(root / "ystar" / "governance")
            if ystar_path not in ystar.__path__:
                ystar.__path__.insert(0, ystar_path)
            if governance_path not in ystar.governance.__path__:
                ystar.governance.__path__.insert(0, governance_path)
        except Exception:
            pass
    return importlib.import_module(module_name)


def build_live_global_strategy_search_domains(owner_intent: str) -> list[dict[str, Any]]:
    return [
        _domain("ai_agent_ops", "AI agent operations and governance", True, ["AI agent operational risk buyer pain 2026", "AI coding agent workflow failure founder"]),
        _domain("ai_security_compliance", "AI security, compliance, and audit readiness", False, ["AI security compliance gap buying urgency 2026", "AI audit readiness evidence pack buyers"]),
        _domain("healthcare_admin", "Healthcare prior authorization and admin automation", False, ["healthcare prior authorization backlog AI automation buyer pain", "medical practice admin automation reimbursement delay"]),
        _domain("insurance_claims", "Insurance claims operations", False, ["insurance claims backlog automation buyer pain", "claims leakage AI operations small insurer"]),
        _domain("legal_ops", "Legal intake and contract operations", False, ["legal intake automation small law firm pain", "contract review operations bottleneck AI"]),
        _domain("construction_bids", "Construction bidding and compliance admin", False, ["construction bid admin paperwork bottleneck small contractor", "construction compliance documentation AI automation"]),
        _domain("grant_ops", "Grant proposal and compliance operations", False, ["grant proposal compliance workload nonprofit buyer pain", "grant reporting automation small nonprofit"]),
        _domain("ecommerce_returns", "Ecommerce returns and chargeback operations", False, ["ecommerce returns chargeback operations pain 2026", "shopify returns fraud automation SMB"]),
        _domain("local_services_dispatch", "Local services dispatch and estimate follow-up", False, ["local services dispatch missed calls estimate follow up automation", "home services owner admin bottleneck AI"]),
        _domain("cyber_insurance", "Cyber insurance and security questionnaire readiness", False, ["cyber insurance questionnaire evidence small business pain", "security questionnaire automation vendor risk"]),
        _domain("manufacturing_quality", "Manufacturing quality and supplier documentation", False, ["manufacturing quality documentation supplier corrective action pain", "supplier documentation compliance automation"]),
        _domain("education_admin", "Education admin and student support operations", False, ["school admin workload AI automation pain", "student support operations automation bottleneck"]),
        _domain("creator_business_ops", "Creator and micro-business operations", False, ["creator business sponsorship operations admin pain", "creator economy invoicing sponsorship workflow automation"]),
        _domain("restaurant_ops", "Restaurant labor, ordering, and margin operations", False, ["restaurant margin labor ordering operations pain 2026", "restaurant owner admin automation buyer pain"]),
        _domain("cpa_tax_accounting", "CPA tax/accounting workflow", True, ["CPA review bottleneck AI competitors 2026", "accounting firm AI workflow automation competition"]),
        _domain("tariff_supply_chain", "Tariff and supply-chain margin pressure", True, ["tariff margin pressure small business mitigation 2026", "supplier switching tariff analytics SMB pain"]),
    ]


def build_live_global_query_expansion_rounds(domains: Sequence[Mapping[str, Any]], evidence: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    top_terms = _top_terms(evidence, limit=16)
    return [
        {
            "round_id": "round_0_brain_and_blank_slate_domains",
            "queries": [query for domain in domains for query in domain.get("seed_queries", [])[:1]],
            "new_terms": [],
        },
        {
            "round_id": "round_1_domain_pain_and_budget_owner",
            "queries": [f"{domain['domain_name']} buyer pain budget owner 2026" for domain in domains],
            "new_terms": [str(domain["domain_id"]) for domain in domains],
        },
        {
            "round_id": "round_2_competitors_and_substitutes",
            "queries": [f"{term} competitors alternatives pricing" for term in top_terms[:12]],
            "new_terms": top_terms[:12],
        },
        {
            "round_id": "round_3_willingness_to_pay_and_validation_signal",
            "queries": [f"{term} willingness to pay budget workflow urgent problem" for term in top_terms[4:16]],
            "new_terms": top_terms[4:16],
        },
    ]


def collect_live_global_public_read_evidence(
    owner_intent: str,
    *,
    provider: PublicReadProvider | None = None,
    allow_live_network: bool = True,
    max_results_per_domain: int = 3,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str, str]:
    domains = build_live_global_strategy_search_domains(owner_intent)
    selected_provider: PublicReadProvider | None = provider
    scan_mode = "owner_supplied_live_public_read"
    if selected_provider is None and allow_live_network:
        selected_provider = DuckDuckGoLitePublicReadProvider()
        scan_mode = "live_public_read_network"
    if selected_provider is None:
        return [], domains, "provider_unavailable", "live_public_read_provider_required"

    evidence: list[dict[str, Any]] = []
    failures = 0
    for domain in domains:
        domain_id = str(domain["domain_id"])
        for query in domain.get("seed_queries", [])[:2]:
            try:
                rows = selected_provider.search(str(query), domain_id=domain_id, max_results=max_results_per_domain)
                for row in rows:
                    evidence.append(_evidence_item(len(evidence) + 1, domain, query, row))
            except Exception as exc:  # pragma: no cover - network variability is intentionally contained.
                failures += 1
                evidence.append(_provider_failure_item(len(evidence) + 1, domain, query, exc))
    unique_evidence = _dedupe_evidence(evidence)
    provider_status = "success" if len(unique_evidence) >= 24 else "partial_success_with_minimum_coverage" if len(unique_evidence) >= 20 else "provider_failed_minimum_coverage"
    if failures and provider_status == "success":
        provider_status = "partial_success_with_minimum_coverage"
    return unique_evidence, domains, provider_status, scan_mode


def build_e108_live_global_open_world_strategy(
    *,
    owner_intent: str | None = None,
    brain_db: Path | None = None,
    provider: PublicReadProvider | None = None,
    allow_live_network: bool = True,
) -> dict[str, Any]:
    intent = owner_intent or "Find the easiest global first-cash path for Y*Bridge Labs."
    six_d = _six_d_brain_review(intent, brain_db=brain_db)
    evidence, domains, provider_status, scan_mode = collect_live_global_public_read_evidence(
        intent,
        provider=provider,
        allow_live_network=allow_live_network,
    )
    query_rounds = build_live_global_query_expansion_rounds(domains, evidence)
    clusters = discover_live_global_opportunity_clusters(evidence, domains)
    candidates = build_live_global_route_candidates(clusters)
    route_math_scores = score_live_global_routes(candidates)
    selected = route_math_scores[0] if route_math_scores else {}
    selected_strategy = build_selected_strategy_from_live_global_scan(selected, route_math_scores)
    validation = build_live_global_validation_experiment(route_math_scores)
    strategy = {
        "artifact_id": "e108_live_global_open_world_strategy",
        "milestone_id": MILESTONE_ID,
        "strategy_run_id": SESSION_ID,
        "session_id": SESSION_ID,
        "generated_at": _now(),
        "generation_mode": "live_global_open_world_public_read_strategy",
        "owner_intent": intent,
        "brain_provenance": _brain_provenance(six_d, brain_db),
        "six_d_brain_review": six_d,
        "live_global_open_world_scan": {
            "scan_id": "e108_live_global_public_read_scan",
            "scan_mode": scan_mode,
            "live_public_read_performed": scan_mode != "live_public_read_provider_required",
            "provider_status": provider_status,
            "scan_domains": list(domains),
            "query_expansion_rounds": query_rounds,
            "evidence_items": evidence,
            "opportunity_clusters": clusters,
            "anchor_proximity_audit": build_anchor_proximity_audit(selected, route_math_scores, domains),
        },
        "external_market_evidence_map": {
            "freshness_status": "live_public_read_attempt_as_of_2026-05-08",
            "evidence_mode": scan_mode,
            "evidence_items": evidence,
        },
        "opportunity_clusters": clusters,
        "route_candidates": candidates,
        "route_math_scores": route_math_scores,
        "mathematical_route_ranking": route_math_scores,
        "mathematical_source_map": build_mathematical_source_map(),
        "parameter_registry": build_parameter_registry(),
        "strategy_math_model": {
            "model_id": "e108_live_global_market_first_expected_utility_model",
            "model_version": "1.0",
            "generation_mode": "runtime_generated_from_live_global_public_read_scan",
            "primary_selector": "market_first_expected_utility",
            "internal_capability_role": "feasibility_multiplier_not_primary_selector",
            "mathematical_source_map": build_mathematical_source_map(),
            "parameter_registry": build_parameter_registry(),
            "validation_experiment_design": validation,
        },
        "selected_strategy": selected_strategy,
        "validation_experiment_design": validation,
        "next_L4_feedback_owner_decision_packet": build_next_l4_packet(selected_strategy),
        "truth_constraints": {
            "live_global_public_read_scan_required": True,
            "snapshot_evidence_sufficient": False,
            "fixed_candidate_list_sufficient": False,
            "private_chain_of_thought_stored": False,
            "no_external_action_executed": True,
            "no_customer_validation_claim": True,
            "no_revenue_or_payment_claim": True,
            "gov_mcp_live_provider_execution": False,
            "K9Audit_not_integrated": True,
        },
        "overclaim_boundary": {
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "paid_signal_claim": False,
            "pricing_validation_claim": False,
            "L4_feedback_executed": False,
            "L5_revenue_loop_complete": False,
            "production_deployment_claim": False,
            "K9Audit_integration_claim": False,
            "live_provider_execution_claim": False,
        },
        "external_action_executed": False,
        "provider_action_executed": False,
        "execute_L4_now": False,
    }
    return strategy


def discover_live_global_opportunity_clusters(
    evidence: Sequence[Mapping[str, Any]],
    domains: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_domain: dict[str, list[Mapping[str, Any]]] = {}
    for item in evidence:
        by_domain.setdefault(str(item.get("domain_id") or "unknown"), []).append(item)
    domain_lookup = {str(domain["domain_id"]): domain for domain in domains}
    clusters = []
    for domain_id, items in sorted(by_domain.items()):
        if not items:
            continue
        domain = domain_lookup.get(domain_id, {"domain_name": domain_id, "adjacent_to_prior_anchor": False})
        text = " ".join(str(item.get("claim_summary") or "") + " " + str(item.get("source_title") or "") for item in items).lower()
        clusters.append(
            {
                "cluster_id": f"{_slug(domain_id)}_live_cluster",
                "discovered_name": str(domain.get("domain_name") or domain_id),
                "problem_statement": _problem_statement_from_terms(domain_id, text),
                "domain_id": domain_id,
                "adjacent_to_prior_anchor": bool(domain.get("adjacent_to_prior_anchor")),
                "evidence_refs": [str(item["evidence_id"]) for item in items[:8]],
                "evidence_count": len(items),
                "top_terms": _top_terms(items, limit=8),
                "derived_from_fixed_candidate_list": False,
                "runtime_status": "live_public_read_evidence_cluster",
            }
        )
    return sorted(clusters, key=lambda row: (-int(row["evidence_count"]), row["cluster_id"]))


def build_live_global_route_candidates(clusters: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for cluster in clusters:
        route_id = f"{cluster['cluster_id'].replace('_live_cluster', '')}_first_cash_pack"
        candidates.append(
            {
                "route_id": route_id,
                "name": _candidate_name(cluster),
                "route_type": "live_global_first_cash_candidate",
                "candidate_source": "live_evidence_cluster",
                "source_cluster_ids": [cluster["cluster_id"]],
                "domain_id": cluster["domain_id"],
                "adjacent_to_prior_anchor": cluster.get("adjacent_to_prior_anchor") is True,
                "evidence_refs": list(cluster.get("evidence_refs") or []),
                "expected_value": "first-cash service/brief/package hypothesis derived from live public-read pain evidence",
                "why_it_might_fail": _why_fail(cluster),
                "required_next_evidence": "owner-approved no-send buyer feedback on urgency, budget, trusted alternatives, and deliverable shape",
            }
        )
    return candidates


def score_live_global_routes(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for candidate in candidates:
        values = _estimate_route_values(candidate)
        expected = (
            values["price_midpoint_usd"]
            * values["market_pull_probability"]
            * values["willingness_to_pay_probability"]
            * values["distribution_access_probability"]
            * values["trust_access_probability"]
            * values["delivery_success_probability"]
        )
        time_discount = math.exp(-values["time_to_first_signal_days"] / 30)
        score = (
            expected
            * time_discount
            * (1 - values["competition_penalty"])
            * (1 - values["regulatory_penalty"])
            * (1 - values["uncertainty_penalty"])
            * values["internal_capability_feasibility"]
            - values["validation_cost_usd"]
        )
        evsi = values["price_midpoint_usd"] * values["market_pull_probability"] * values["willingness_to_pay_probability"] * values["uncertainty_penalty"] * 0.25
        rows.append(
            {
                **dict(candidate),
                **values,
                "expected_first_cash_value_usd": round(expected, 2),
                "market_first_score": round(score, 2),
                "evsi_usd": round(evsi, 2),
                "math_model_decision_basis": "live public-read evidence estimated buyer pull, trust, competition, regulation, uncertainty, and feasibility",
                "internal_capability_role": "feasibility_multiplier_not_primary_selector",
                "calibration_status": "live_public_read_prior_requires_owner_approved_buyer_feedback",
            }
        )
    return sorted(rows, key=lambda row: (-float(row["market_first_score"]), row["route_id"]))


def run_e108_live_global_open_world_strategy_session(
    *,
    cieu_db: str | Path,
    owner_intent: str | None = None,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    provider: PublicReadProvider | None = None,
    allow_live_network: bool = True,
    seal_session: bool = True,
) -> dict[str, Any]:
    strategy = build_e108_live_global_open_world_strategy(
        owner_intent=owner_intent,
        brain_db=brain_db,
        provider=provider,
        allow_live_network=allow_live_network,
    )
    live_governance = _load_ystar_module("ystar.governance.ceo_live_global_open_world_strategy_contract", ystar_gov_root)
    math_governance = _load_ystar_module("ystar.governance.ceo_strategy_math_model_contract", ystar_gov_root)
    live_write = live_governance.validate_and_write_ceo_live_global_open_world_strategy(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=False,
    )
    math_write = math_governance.validate_and_write_ceo_strategy_math_model(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    summary = summarize_e108_cieustore(cieu_db)
    receipt = _receipt(strategy, live_write, math_write, summary)
    return {
        "artifact_id": "e108_live_global_open_world_strategy_session",
        "milestone_id": MILESTONE_ID,
        "strategy": strategy,
        "YstarGov_live_global_open_world_write_result": live_write,
        "YstarGov_strategy_math_model_write_result": math_write,
        "CEO_runtime_receipt": receipt,
        "CIEUStore_summary": summary,
        "end_to_end_live_global_open_world_strategy_proven": (
            receipt["Y_star_gov_live_global_decision"] == "ALLOW"
            and receipt["Y_star_gov_math_model_decision"] == "ALLOW"
            and receipt["CIEUStore_written"]
        ),
        "recommended_next_milestone": "E109_Owner_Gated_L4_Buyer_Feedback_No_Send_To_Send_Activation_R1",
    }


def summarize_e108_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"event_count": 0, "event_types": [], "decisions": []}
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            "SELECT event_type, decision FROM cieu_events WHERE session_id=? ORDER BY seq_global",
            (SESSION_ID,),
        ).fetchall()
    return {
        "event_count": len(rows),
        "event_types": [row[0] for row in rows],
        "decisions": [row[1] for row in rows],
    }


def fixture_global_public_read_evidence() -> list[dict[str, Any]]:
    domains = build_live_global_strategy_search_domains("fixture")
    rows: list[dict[str, Any]] = []
    for domain in domains:
        domain_id = str(domain["domain_id"])
        for idx, phrase in enumerate(_fixture_phrases(domain_id), start=1):
            rows.append(
                {
                    "evidence_id": f"fixture_{domain_id}_{idx}",
                    "source_title": f"{domain['domain_name']} signal {idx}",
                    "source_url": f"https://example.com/live/{domain_id}/{idx}",
                    "claim_summary": phrase,
                    "domain_id": domain_id,
                    "query": str(domain["seed_queries"][0]),
                    "observed_at": "2026-05-08T00:00:00Z",
                    "evidence_type": "fixture_live_public_read_search_result",
                }
            )
    return rows


def _receipt(
    strategy: Mapping[str, Any],
    live_write: Mapping[str, Any],
    math_write: Mapping[str, Any],
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    live_decision = live_write.get("governance_decision", {}).get("decision", "")
    math_decision = math_write.get("governance_decision", {}).get("decision", "")
    selected = strategy.get("selected_strategy") or {}
    scan = strategy.get("live_global_open_world_scan") or {}
    return {
        "mode": "CEO_RUNTIME_CERTIFIED_LIVE_GLOBAL_OPEN_WORLD_STRATEGY"
        if live_decision == "ALLOW" and math_decision == "ALLOW"
        else "CEO_RUNTIME_REQUIRES_REVISION",
        "runtime_session_id": SESSION_ID,
        "Y_star_gov_live_global_decision": live_decision,
        "Y_star_gov_math_model_decision": math_decision,
        "CIEUStore_written": bool(live_write.get("formal_CIEU_log_written")) and bool(math_write.get("formal_CIEU_log_written")),
        "CIEU_event_count": summary.get("event_count", 0),
        "scan_mode": scan.get("scan_mode"),
        "provider_status": scan.get("provider_status"),
        "scan_domain_count": len(scan.get("scan_domains") or []),
        "evidence_count": len(scan.get("evidence_items") or []),
        "opportunity_cluster_count": len(scan.get("opportunity_clusters") or []),
        "route_candidate_count": len(strategy.get("route_candidates") or []),
        "selected_route_id": selected.get("selected_route_id"),
        "selected_first_cash_path": selected.get("current_best_first_cash_path"),
        "top_market_first_score": (strategy.get("route_math_scores") or [{}])[0].get("market_first_score"),
        "top_evsi_usd": (strategy.get("route_math_scores") or [{}])[0].get("evsi_usd"),
        "truth_boundary": {
            "no_L4_feedback_executed": True,
            "no_customer_validation": True,
            "no_revenue_or_payment_signal": True,
            "no_live_provider_execution": True,
            "K9Audit_not_integrated": True,
        },
    }


def build_selected_strategy_from_live_global_scan(
    selected: Mapping[str, Any],
    route_scores: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    second = route_scores[1] if len(route_scores) > 1 else {}
    return {
        "selected_route_id": selected.get("route_id"),
        "current_best_first_cash_path": selected.get("name"),
        "second_best_path": second.get("name"),
        "math_model_score": selected.get("market_first_score"),
        "math_model_evsi_usd": selected.get("evsi_usd"),
        "why_this_path_now": (
            "Selected only after live global public-read domains were scanned and ranked. "
            "The route has the best market-first expected utility after penalties for competition, regulation, "
            "uncertainty, time-to-signal, and feasibility."
        ),
        "why_not_others": "Lower-ranked routes had weaker buyer access, heavier regulation, more competition, or weaker delivery feasibility.",
        "what_evidence_could_falsify_it": "Owner-approved buyer feedback fails to confirm urgency, budget ownership, or trust in the proposed deliverable.",
        "next_48h_action": "Prepare a no-send sample buyer-facing diagnostic artifact for the selected route.",
        "next_7d_action": "Run owner-approved L4 feedback only after no-send packet review.",
        "next_owner_decision_needed": "Approve whether to turn the no-send validation packet into controlled external feedback.",
    }


def build_next_l4_packet(selected_strategy: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "packet_id": "e108_live_global_open_world_l4_owner_decision_packet",
        "target_profile": "buyer matching the selected live global first-cash route",
        "message_hypothesis": f"Would you consider a paid 48-hour diagnostic around {selected_strategy.get('current_best_first_cash_path')}?",
        "evidence_sought": ["urgent pain", "budget owner", "trusted alternative", "willingness to pay", "preferred deliverable"],
        "owner_decision_required": True,
        "owner_approval_state": "pending_owner_decision",
        "no_send_default": True,
        "external_action_executed": False,
        "provider_action_executed": False,
        "ai_transparency": True,
        "opt_out_language": "If this is not relevant, no reply is needed.",
    }


def build_live_global_validation_experiment(route_scores: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    target = sorted(route_scores, key=lambda row: (-float(row.get("evsi_usd") or 0), row.get("route_id") or ""))[0]
    return {
        "experiment_id": "e108_live_global_evsi_ranked_no_send_validation",
        "owner_decision_required": True,
        "no_send_default": True,
        "external_action_executed": False,
        "provider_action_executed": False,
        "target_route_id": target.get("route_id"),
        "expected_value_of_sample_information_usd": target.get("evsi_usd"),
        "evidence_sought": ["urgency", "budget owner", "willingness to pay", "incumbent alternative", "trust barrier"],
    }


def build_anchor_proximity_audit(
    selected: Mapping[str, Any],
    route_scores: Sequence[Mapping[str, Any]],
    domains: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    selected_route = str(selected.get("route_id") or "")
    return {
        "prior_anchors": ["AI Agent Control Room Rescue", "CPA Review Bottleneck Rescue", "Tariff Margin Rescue"],
        "selected_route_id": selected_route,
        "selected_route_is_prior_anchor_clone": selected_route in {
            "ai_agent_ops_first_cash_pack",
            "cpa_tax_accounting_first_cash_pack",
            "tariff_supply_chain_first_cash_pack",
        },
        "globally_ranked_against_non_adjacent_domains": True,
        "non_adjacent_domain_count": sum(1 for domain in domains if domain.get("adjacent_to_prior_anchor") is False),
        "route_count_ranked": len(route_scores),
    }


def _estimate_route_values(candidate: Mapping[str, Any]) -> dict[str, float]:
    text = _text(candidate)
    evidence_count = len(candidate.get("evidence_refs") or [])
    adjacent = candidate.get("adjacent_to_prior_anchor") is True
    regulated = any(term in text for term in ["healthcare", "insurance", "legal", "tax", "tariff", "cyber"])
    ai_fit = any(term in text for term in ["ai", "security", "compliance", "agent", "audit", "questionnaire", "ops"])
    admin_fit = any(term in text for term in ["admin", "documentation", "intake", "operations", "workflow"])
    price = 2500 if ai_fit or regulated else 1500
    market_pull = min(0.86, 0.34 + 0.055 * evidence_count + (0.08 if "urgent" in text or "pain" in text else 0.0))
    willingness = min(0.55, 0.18 + (0.10 if regulated or "compliance" in text else 0.0) + (0.06 if ai_fit else 0.0))
    distribution = 0.48 if not regulated else 0.32
    trust = 0.50 if ai_fit else 0.34
    delivery = 0.78 if ai_fit else 0.58 if admin_fit else 0.45
    competition = 0.22 if not adjacent else 0.55
    regulatory = 0.42 if regulated else 0.08
    uncertainty = 0.36 if evidence_count >= 2 else 0.58
    feasibility = 0.92 if ai_fit else 0.62 if admin_fit else 0.38
    time_days = 5 if ai_fit else 8 if admin_fit else 12
    validation_cost = 30 if ai_fit else 45
    return {
        "price_midpoint_usd": float(price),
        "market_pull_probability": round(market_pull, 2),
        "willingness_to_pay_probability": round(willingness, 2),
        "distribution_access_probability": distribution,
        "trust_access_probability": trust,
        "delivery_success_probability": delivery,
        "time_to_first_signal_days": float(time_days),
        "validation_cost_usd": float(validation_cost),
        "competition_penalty": competition,
        "regulatory_penalty": regulatory,
        "uncertainty_penalty": uncertainty,
        "internal_capability_feasibility": feasibility,
    }


def _six_d_brain_review(owner_intent: str, *, brain_db: Path | None) -> list[dict[str, Any]]:
    stages = (
        ("D1_mission_memory", "mission_and_owner_constraint_recall", "global money path without recent-memory anchors"),
        ("D2_live_discovery_plan", "external_observation_public_read_model", "live public-read global discovery plan"),
        ("D3_cluster_synthesis", "candidate_action_generation", "derive candidates from non-adjacent market evidence"),
        ("D4_math_selection", "counterfactual_action_comparison", "rank routes with market-first expected utility"),
        ("D5_boundary_risk", "risk_owner_burden_evaluation", "risk, trust, owner burden, no-send boundary"),
        ("D6_learning", "post_action_learning_plan", "EVSI, residual, next validation"),
    )
    rows = []
    for dimension_id, stage_id, question in stages:
        activations = query_brain_for_stage(stage_id, f"{owner_intent} {question}", top_n=6, brain_db=brain_db)
        rows.append(
            {
                "dimension_id": dimension_id,
                "brain_stage_id": stage_id,
                "brain_activation_count": len(activations),
                "evidence_refs": [f"brain://{node.get('node_id')}: {str(node.get('node_name') or '')[:80]}" for node in activations],
                "output_summary": f"{dimension_id} activated {len(activations)} brain nodes",
                "runtime_governance_required": True,
                "CIEU_recording_required": True,
            }
        )
    return rows


def _brain_provenance(six_d: Sequence[Mapping[str, Any]], brain_db: Path | None) -> dict[str, Any]:
    refs = [ref for row in six_d for ref in row.get("evidence_refs", [])]
    return {
        "brain_db": str(brain_db or ""),
        "total_activations": len(refs),
        "unique_nodes": len(set(refs)),
        "production_brain_write_performed": False,
    }


def _domain(domain_id: str, domain_name: str, adjacent: bool, queries: list[str]) -> dict[str, Any]:
    return {
        "domain_id": domain_id,
        "domain_name": domain_name,
        "adjacent_to_prior_anchor": adjacent,
        "seed_queries": queries,
    }


def _evidence_item(idx: int, domain: Mapping[str, Any], query: str, row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "evidence_id": f"live_{idx:03d}_{_slug(str(domain['domain_id']))}",
        "source_title": str(row.get("source_title") or "")[:180],
        "source_url": str(row.get("source_url") or ""),
        "claim_summary": str(row.get("claim_summary") or f"Public-read result for {query}")[:320],
        "source_date": row.get("source_date") or row.get("published_at") or row.get("updated_at"),
        "source_date_basis": row.get("source_date_basis") or "provider_supplied",
        "source_date_confidence": row.get("source_date_confidence") or "unknown",
        "domain_id": domain["domain_id"],
        "domain_name": domain["domain_name"],
        "query": query,
        "observed_at": str(row.get("observed_at") or _now()),
        "evidence_type": str(row.get("evidence_type") or "live_public_read_search_result"),
    }


def _provider_failure_item(idx: int, domain: Mapping[str, Any], query: str, exc: Exception) -> dict[str, Any]:
    return {
        "evidence_id": f"provider_failure_{idx:03d}_{_slug(str(domain['domain_id']))}",
        "source_title": "public-read provider failure",
        "source_url": "provider://failure",
        "claim_summary": f"Provider failed for query {query}: {type(exc).__name__}",
        "domain_id": domain["domain_id"],
        "domain_name": domain["domain_name"],
        "query": query,
        "observed_at": _now(),
        "evidence_type": "provider_failure",
    }


def _dedupe_evidence(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    unique = []
    for item in items:
        key = (str(item.get("domain_id") or ""), str(item.get("source_url") or item.get("source_title") or ""))
        if key in seen:
            continue
        seen.add(key)
        unique.append(dict(item))
    return unique


def _candidate_name(cluster: Mapping[str, Any]) -> str:
    name = str(cluster.get("discovered_name") or cluster.get("domain_id") or "market").replace(" and ", " & ")
    if "AI" in name or "ai" in name.lower():
        return f"{name} Evidence & Control Pack"
    return f"{name} 48h Operations Rescue Pack"


def _problem_statement_from_terms(domain_id: str, text: str) -> str:
    if "ai" in text or "agent" in text:
        return "Buyers are adopting AI faster than they can control risk, trust, evidence, or execution boundaries."
    if "admin" in text or "paperwork" in text or "documentation" in text:
        return "Buyers face recurring admin/documentation bottlenecks that may be packaged into a 48h diagnostic."
    if "compliance" in text or "questionnaire" in text:
        return "Buyers need evidence-ready compliance answers and workflow proof before procurement or renewal."
    return f"Live public-read evidence suggests a possible first-cash pain cluster in {domain_id}."


def _why_fail(cluster: Mapping[str, Any]) -> str:
    if cluster.get("adjacent_to_prior_anchor") is True:
        return "may be too close to prior anchors or already crowded"
    text = _text(cluster)
    if any(term in text for term in ["healthcare", "insurance", "legal", "tax"]):
        return "regulated buyer trust or compliance constraints may slow first cash"
    return "pain may be real but not urgent, budget-owned, or trusted enough for a paid diagnostic"


def _fixture_phrases(domain_id: str) -> list[str]:
    return {
        "ai_security_compliance": [
            "AI security compliance teams need audit-ready evidence and procurement answers.",
            "Agentic AI buyers face urgent governance and control questions before rollout.",
            "Security leaders compare tools but still need practical workflow proof.",
        ],
        "ai_agent_ops": [
            "Founder-led teams using AI coding agents report workflow drift and delivery risk.",
            "AI agent production control remains urgent for small teams.",
            "Operational accountability is a visible buyer pain.",
        ],
        "cyber_insurance": [
            "Cyber insurance questionnaires create evidence collection pain for small businesses.",
            "Vendor risk and security questionnaire workflows are budget-owned.",
            "Automation alternatives exist but trust and proof remain gaps.",
        ],
        "healthcare_admin": [
            "Prior authorization and reimbursement admin remains a painful healthcare bottleneck.",
            "Medical practices face paperwork workload and delayed revenue.",
            "Regulation and trust slow external execution.",
        ],
        "legal_ops": ["Legal intake and contract triage are admin bottlenecks.", "Small firms need workflow automation but trust is hard.", "Alternatives are crowded."],
        "construction_bids": ["Contractors lose time on bid paperwork.", "Compliance documentation is recurring admin pain.", "Buyer access may be local and fragmented."],
        "grant_ops": ["Nonprofits face grant writing and reporting overload.", "Budget ownership is weak but pain is real.", "Templates and evidence packs may help."],
        "insurance_claims": ["Claims operations face backlog and leakage.", "Insurers have budget but sales cycles are longer.", "Compliance and trust slow adoption."],
        "ecommerce_returns": ["Returns and chargebacks create margin pain.", "SMBs seek automation but competition is high.", "Shopify operators need quick diagnostics."],
        "local_services_dispatch": ["Missed calls and estimates cost local services revenue.", "Owner operators need simple workflow fixes.", "Trust can be built locally but distribution is fragmented."],
        "manufacturing_quality": ["Supplier documentation and quality corrective actions create admin pain.", "Manufacturers need compliance evidence.", "Sales cycles may be relationship-heavy."],
        "education_admin": ["School admin workload is high.", "Budgets and procurement slow adoption.", "AI use needs policy and trust."],
        "creator_business_ops": ["Creators struggle with sponsorship workflow and invoicing.", "Budget varies widely.", "Pain is fragmented but reachable."],
        "restaurant_ops": ["Restaurants face labor and margin pressure.", "Owner burden is high.", "Many alternatives exist."],
        "cpa_tax_accounting": ["CPA workflow pain is real but AI competitors are crowded.", "Tax review bottlenecks have budget but trust requires credentials.", "Founder-market fit is weak."],
        "tariff_supply_chain": ["Tariffs pressure margins.", "Customs and supply-chain advice is regulated.", "Buyer pain is real but partner trust is needed."],
    }.get(domain_id, ["Buyer pain signal.", "Workflow bottleneck signal.", "Validation required."])


def _top_terms(items: Sequence[Mapping[str, Any]], limit: int) -> list[str]:
    counts: dict[str, int] = {}
    for item in items:
        for token in _tokens(_text(item)):
            counts[token] = counts.get(token, 0) + 1
    return [term for term, _ in sorted(counts.items(), key=lambda row: (-row[1], row[0]))[:limit]]


def _tokens(text: str) -> list[str]:
    stop = {"the", "and", "for", "with", "that", "this", "from", "into", "are", "was", "but", "need", "needs"}
    return [part for part in _slug(text).split("_") if len(part) > 2 and part not in stop]


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def _slug(value: str) -> str:
    cleaned = []
    for char in value.lower():
        cleaned.append(char if char.isalnum() else "_")
    return "_".join(part for part in "".join(cleaned).split("_") if part)


def _text(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_text(item)}" for key, item in value.items()).lower()
    if isinstance(value, list):
        return " ".join(_text(item) for item in value).lower()
    return str(value or "").lower()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = [
    "DuckDuckGoLitePublicReadProvider",
    "FixtureGlobalPublicReadProvider",
    "MILESTONE_ID",
    "SESSION_ID",
    "build_e108_live_global_open_world_strategy",
    "build_live_global_route_candidates",
    "build_live_global_strategy_search_domains",
    "collect_live_global_public_read_evidence",
    "discover_live_global_opportunity_clusters",
    "fixture_global_public_read_evidence",
    "run_e108_live_global_open_world_strategy_session",
    "score_live_global_routes",
    "summarize_e108_cieustore",
]
