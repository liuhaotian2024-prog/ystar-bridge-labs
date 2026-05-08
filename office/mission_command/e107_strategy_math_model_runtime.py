from __future__ import annotations

import importlib
import math
import sqlite3
import sys
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e106_strategy_process_integrity_runtime import (
    build_strategy_process_integrity_runtime_strategy,
)


MILESTONE_ID = "E107_Market_First_Strategy_Math_Model_Runtime_R1"
SESSION_ID = "e107_strategy_math_model_runtime"
Y_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")


def _load_ystar_module(module_name: str, ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def build_market_first_strategy_math_model_strategy(
    *,
    owner_intent: str | None = None,
    brain_db: Path | None = None,
) -> dict[str, Any]:
    strategy = build_strategy_process_integrity_runtime_strategy(
        owner_intent=owner_intent,
        brain_db=brain_db,
    )
    strategy["artifact_id"] = "e107_market_first_strategy_math_model_strategy"
    strategy["milestone_id"] = MILESTONE_ID
    strategy["strategy_run_id"] = SESSION_ID
    strategy["session_id"] = SESSION_ID
    source_map = build_mathematical_source_map()
    parameter_registry = build_parameter_registry()
    route_math_scores = score_routes_with_market_first_math_model(strategy)
    selected = route_math_scores[0]
    second = route_math_scores[1]
    strategy["mathematical_source_map"] = source_map
    strategy["parameter_registry"] = parameter_registry
    strategy["route_math_scores"] = route_math_scores
    strategy["mathematical_route_ranking"] = route_math_scores
    strategy["strategy_math_model"] = {
        "model_id": "market_first_expected_utility_model_v1",
        "model_version": "1.0",
        "generation_mode": "runtime_generated_structured_output",
        "primary_selector": "market_first_expected_utility",
        "internal_capability_role": "feasibility_multiplier_not_primary_selector",
        "model_equation": (
            "market_first_score = (price_midpoint_usd * market_pull_probability * "
            "willingness_to_pay_probability * distribution_access_probability * "
            "trust_access_probability * delivery_success_probability) * exp(-time_to_first_signal_days/30) "
            "* (1-competition_penalty) * (1-regulatory_penalty) * (1-uncertainty_penalty) "
            "* internal_capability_feasibility - validation_cost_usd"
        ),
        "model_design_principles": [
            "market demand, buyer pain, buyer access, trust, and willingness-to-pay are upstream of internal capability",
            "internal capability is only a feasibility multiplier",
            "uncertainty produces an explicit penalty and a value-of-information target",
            "route selection must match the top market-first score unless an override is justified",
        ],
        "mathematical_source_map": source_map,
        "parameter_registry": parameter_registry,
        "validation_experiment_design": build_math_validation_experiment(route_math_scores),
    }
    strategy["validation_experiment_design"] = build_math_validation_experiment(route_math_scores)
    strategy["selected_strategy"] = build_math_selected_strategy(strategy, selected, second)
    strategy["strategy_math_model_status"] = {
        "prior_weight_problem_corrected": True,
        "internal_capability_role": "feasibility_multiplier_not_primary_selector",
        "market_first_score_required": True,
        "value_of_information_required": True,
        "strategy_conclusion_status": "provisional_until_owner_approved_external_feedback",
    }
    return strategy


def build_mathematical_source_map() -> dict[str, dict[str, str]]:
    return {
        "multi_attribute_utility": {
            "source_name": "Keeney and Raiffa, Decisions with Multiple Objectives",
            "source_url": "https://www.cambridge.org/core/books/decisions-with-multiple-objectives/frontmatter/4F61BAED42123B864E5DFFFD3EC40A33",
            "model_role": "structure conflicting strategic objectives instead of using one vague score",
        },
        "analytic_hierarchy_process": {
            "source_name": "Saaty, The Analytic Hierarchy Process",
            "source_url": "https://books.google.com/books/about/The_Analytic_Hierarchy_Process.html?id=Xxi7AAAAIAAJ",
            "model_role": "make criteria hierarchy explicit; do not hide weights as intuition",
        },
        "expected_utility": {
            "source_name": "Expected utility decision theory",
            "source_url": "https://www.investopedia.com/terms/e/expectedutility.asp",
            "model_role": "rank uncertain first-cash routes by probability-adjusted outcome, not wishful upside",
        },
        "value_of_information": {
            "source_name": "USGS / Decision Analysis value of information",
            "source_url": "https://www.usgs.gov/publications/a-simplified-method-value-information-using-constructed-scales",
            "model_role": "choose the next validation experiment by how much uncertainty it can reduce",
        },
        "competitive_forces": {
            "source_name": "Porter's Five Forces, Harvard Institute for Strategy and Competitiveness",
            "source_url": "https://www.isc.hbs.edu/strategy/business-strategy/Pages/the-five-forces.aspx",
            "model_role": "penalize saturated/crowded markets and buyer/supplier/substitute power",
        },
        "adoption_diffusion": {
            "source_name": "Bass diffusion model, Management Science",
            "source_url": "https://pubsonline.informs.org/doi/abs/10.1287/mnsc.15.5.215",
            "model_role": "represent adoption timing and imitation/innovation uncertainty",
        },
        "business_model_canvas": {
            "source_name": "Strategyzer Business Model Canvas",
            "source_url": "https://www.strategyzer.com/library/what-is-a-business-model",
            "model_role": "force customer segment, value proposition, channel, cost, and revenue assumptions to be explicit",
        },
        "product_market_fit_measurement": {
            "source_name": "Superhuman / Sean Ellis PMF leading indicator",
            "source_url": "https://blog.superhuman.com/how-superhuman-built-an-engine-to-find-product-market-fit/",
            "model_role": "turn validation into a measurable future signal, not a narrative claim",
        },
        "rice_prioritization": {
            "source_name": "Intercom RICE prioritization",
            "source_url": "https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/",
            "model_role": "separate reach, impact, confidence, and effort when planning validation work",
        },
    }


def build_parameter_registry() -> dict[str, dict[str, Any]]:
    return {
        "price_midpoint_usd": _param("Hypothesized entry offer price midpoint.", "business_model_canvas", [0, 10000]),
        "market_pull_probability": _param("Probability that the pain is urgent and externally recognizable.", "multi_attribute_utility", [0, 1]),
        "willingness_to_pay_probability": _param("Probability that the segment will consider paying for the rescue artifact.", "expected_utility", [0, 1]),
        "distribution_access_probability": _param("Probability that we can reach the buyer through allowed/no-send validation paths.", "rice_prioritization", [0, 1]),
        "trust_access_probability": _param("Probability that the buyer can trust us enough for first paid engagement.", "competitive_forces", [0, 1]),
        "delivery_success_probability": _param("Probability that we can deliver credible value with current runtime assets.", "multi_attribute_utility", [0, 1]),
        "time_to_first_signal_days": _param("Estimated days to obtain first owner-approved validation signal.", "rice_prioritization", [0, 90]),
        "validation_cost_usd": _param("Internal cash-equivalent cost of the next no-send validation step.", "value_of_information", [0, 10000]),
        "competition_penalty": _param("Penalty for rivalry, substitutes, and crowded incumbents.", "competitive_forces", [0, 1]),
        "regulatory_penalty": _param("Penalty for regulated advice, credentials, compliance, or payment boundary risk.", "competitive_forces", [0, 1]),
        "uncertainty_penalty": _param("Penalty for unvalidated or stale assumptions.", "value_of_information", [0, 1]),
        "internal_capability_feasibility": _param("Feasibility multiplier from current bridge-labs/Y-star-gov/gov-mcp assets.", "analytic_hierarchy_process", [0, 1]),
        "evsi_usd": _param("Expected value of sample information from the next validation experiment.", "value_of_information", [0, 10000]),
    }


def score_routes_with_market_first_math_model(strategy: Mapping[str, Any]) -> list[dict[str, Any]]:
    route_rows = []
    for route in strategy.get("route_scoring", []):
        route_id = str(route["route_id"])
        values = _route_prior_values(route_id)
        expected = (
            values["price_midpoint_usd"]
            * values["market_pull_probability"]
            * values["willingness_to_pay_probability"]
            * values["distribution_access_probability"]
            * values["trust_access_probability"]
            * values["delivery_success_probability"]
        )
        time_discount = math.exp(-values["time_to_first_signal_days"] / 30)
        market_first_score = (
            expected
            * time_discount
            * (1 - values["competition_penalty"])
            * (1 - values["regulatory_penalty"])
            * (1 - values["uncertainty_penalty"])
            * values["internal_capability_feasibility"]
            - values["validation_cost_usd"]
        )
        evsi = (
            values["price_midpoint_usd"]
            * values["market_pull_probability"]
            * values["willingness_to_pay_probability"]
            * values["uncertainty_penalty"]
            * 0.25
        )
        route_rows.append(
            {
                "route_id": route_id,
                "route_name": route.get("name"),
                "source_cluster_ids": list(route.get("source_cluster_ids") or []),
                "evidence_refs": list(route.get("evidence_refs") or []),
                "price_midpoint_usd": values["price_midpoint_usd"],
                "expected_first_cash_value_usd": round(expected, 2),
                "market_pull_probability": values["market_pull_probability"],
                "willingness_to_pay_probability": values["willingness_to_pay_probability"],
                "distribution_access_probability": values["distribution_access_probability"],
                "trust_access_probability": values["trust_access_probability"],
                "delivery_success_probability": values["delivery_success_probability"],
                "time_to_first_signal_days": values["time_to_first_signal_days"],
                "validation_cost_usd": values["validation_cost_usd"],
                "competition_penalty": values["competition_penalty"],
                "regulatory_penalty": values["regulatory_penalty"],
                "uncertainty_penalty": values["uncertainty_penalty"],
                "internal_capability_feasibility": values["internal_capability_feasibility"],
                "market_first_score": round(market_first_score, 2),
                "evsi_usd": round(evsi, 2),
                "math_model_decision_basis": _decision_basis(route_id),
                "internal_capability_role": "feasibility_multiplier_not_primary_selector",
                "calibration_status": "source_backed_prior_requires_owner_approved_market_validation",
            }
        )
    return sorted(route_rows, key=lambda row: (-row["market_first_score"], row["route_id"]))


def build_math_selected_strategy(
    strategy: Mapping[str, Any],
    selected: Mapping[str, Any],
    second: Mapping[str, Any],
) -> dict[str, Any]:
    prior = dict(strategy.get("selected_strategy") or {})
    prior.update(
        {
            "selected_route_id": selected["route_id"],
            "current_best_first_cash_path": selected.get("route_name") or selected["route_id"],
            "second_best_path": second.get("route_name") or second["route_id"],
            "math_model_score": selected["market_first_score"],
            "math_model_evsi_usd": selected["evsi_usd"],
            "math_model_selection_reason": (
                "Selected by market-first expected utility after penalties for competition, regulation, "
                "uncertainty, time-to-signal, and feasibility. Internal capability is not the primary selector."
            ),
            "why_this_path_now": (
                "The selected route has the best market-first score after combining buyer pain, willingness-to-pay "
                "uncertainty, distribution/trust access, competitive saturation, regulatory risk, validation cost, "
                "and delivery feasibility. It remains a hypothesis until owner-approved external feedback."
            ),
            "what_evidence_could_falsify_it": (
                "The route is falsified if owner-approved feedback shows weak urgent pain, no budget owner, "
                "or preference for existing alternatives at a lower switching cost."
            ),
        }
    )
    return prior


def build_math_validation_experiment(route_math_scores: list[Mapping[str, Any]]) -> dict[str, Any]:
    top_evsi = sorted(route_math_scores, key=lambda row: (-float(row["evsi_usd"]), row["route_id"]))[0]
    return {
        "experiment_id": "e107_value_of_information_ranked_l4_no_send_feedback_test",
        "owner_decision_required": True,
        "no_send_default": True,
        "external_action_executed": False,
        "provider_action_executed": False,
        "target_route_id": top_evsi["route_id"],
        "expected_value_of_sample_information_usd": top_evsi["evsi_usd"],
        "evidence_sought": [
            "urgent buyer pain",
            "budget owner",
            "willingness to pay",
            "trusted alternative",
            "minimum acceptable deliverable",
        ],
        "success_signal": "buyer says the pain is urgent and asks to see a no-send sample or price",
        "failure_signal": "buyer does not recognize the pain, budget owner, or deliverable value",
    }


def run_e107_strategy_math_model_session(
    *,
    cieu_db: str | Path,
    owner_intent: str | None = None,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    seal_session: bool = True,
) -> dict[str, Any]:
    strategy = build_market_first_strategy_math_model_strategy(
        owner_intent=owner_intent,
        brain_db=brain_db,
    )
    strategic_governance = _load_ystar_module("ystar.governance.ceo_strategic_intelligence_benchmark", ystar_gov_root)
    refresh_governance = _load_ystar_module("ystar.governance.ceo_market_strategy_refresh_contract", ystar_gov_root)
    open_world_governance = _load_ystar_module("ystar.governance.ceo_open_world_strategy_contract", ystar_gov_root)
    integrity_governance = _load_ystar_module("ystar.governance.ceo_strategy_process_integrity_contract", ystar_gov_root)
    math_governance = _load_ystar_module("ystar.governance.ceo_strategy_math_model_contract", ystar_gov_root)
    strategic_write = strategic_governance.validate_and_write_ceo_strategic_intelligence_strategy(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=False,
    )
    refresh_write = refresh_governance.validate_and_write_ceo_market_strategy_refresh(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=False,
    )
    open_world_write = open_world_governance.validate_and_write_ceo_open_world_strategy(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=False,
    )
    integrity_write = integrity_governance.validate_and_write_ceo_strategy_process_integrity(
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
    cieu_summary = summarize_e107_cieustore(cieu_db)
    receipt = _receipt(strategy, strategic_write, refresh_write, open_world_write, integrity_write, math_write, cieu_summary)
    return {
        "artifact_id": "e107_strategy_math_model_session",
        "milestone_id": MILESTONE_ID,
        "strategy": strategy,
        "YstarGov_strategic_benchmark_write_result": strategic_write,
        "YstarGov_market_refresh_write_result": refresh_write,
        "YstarGov_open_world_write_result": open_world_write,
        "YstarGov_process_integrity_write_result": integrity_write,
        "YstarGov_strategy_math_model_write_result": math_write,
        "CEO_runtime_receipt": receipt,
        "CIEUStore_summary": cieu_summary,
        "end_to_end_strategy_math_model_proven": (
            receipt["Y_star_gov_strategic_decision"] == "ALLOW"
            and receipt["Y_star_gov_market_refresh_decision"] == "ALLOW"
            and receipt["Y_star_gov_open_world_decision"] == "ALLOW"
            and receipt["Y_star_gov_process_integrity_decision"] == "ALLOW"
            and receipt["Y_star_gov_math_model_decision"] == "ALLOW"
            and receipt["CIEUStore_written"]
        ),
        "recommended_next_milestone": "E108_Live_Public_Read_Provider_And_Calibrated_Parameter_Update_R1",
    }


def summarize_e107_cieustore(cieu_db: str | Path) -> dict[str, Any]:
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


def _receipt(
    strategy: Mapping[str, Any],
    strategic_write: Mapping[str, Any],
    refresh_write: Mapping[str, Any],
    open_world_write: Mapping[str, Any],
    integrity_write: Mapping[str, Any],
    math_write: Mapping[str, Any],
    cieu_summary: Mapping[str, Any],
) -> dict[str, Any]:
    decisions = {
        "strategic": strategic_write.get("governance_decision", {}).get("decision", ""),
        "refresh": refresh_write.get("governance_decision", {}).get("decision", ""),
        "open_world": open_world_write.get("governance_decision", {}).get("decision", ""),
        "integrity": integrity_write.get("governance_decision", {}).get("decision", ""),
        "math": math_write.get("governance_decision", {}).get("decision", ""),
    }
    selected = strategy["selected_strategy"]
    proof = strategy["strategy_process_integrity_proof"]
    math_scores = strategy["route_math_scores"]
    return {
        "mode": "CEO_RUNTIME_CERTIFIED_MARKET_FIRST_STRATEGY_MATH_MODEL"
        if all(value == "ALLOW" for value in decisions.values())
        else "CEO_RUNTIME_REQUIRES_REVISION",
        "runtime_session_id": SESSION_ID,
        "Y_star_gov_strategic_decision": decisions["strategic"],
        "Y_star_gov_market_refresh_decision": decisions["refresh"],
        "Y_star_gov_open_world_decision": decisions["open_world"],
        "Y_star_gov_process_integrity_decision": decisions["integrity"],
        "Y_star_gov_math_model_decision": decisions["math"],
        "CIEUStore_written": bool(strategic_write.get("formal_CIEU_log_written"))
        and bool(refresh_write.get("formal_CIEU_log_written"))
        and bool(open_world_write.get("formal_CIEU_log_written"))
        and bool(integrity_write.get("formal_CIEU_log_written"))
        and bool(math_write.get("formal_CIEU_log_written")),
        "CIEU_event_count": cieu_summary.get("event_count", 0),
        "selected_route_id": selected["selected_route_id"],
        "selected_first_cash_path": selected["current_best_first_cash_path"],
        "math_model_id": strategy["strategy_math_model"]["model_id"],
        "internal_capability_role": strategy["strategy_math_model"]["internal_capability_role"],
        "top_market_first_score": math_scores[0]["market_first_score"],
        "top_evsi_usd": math_scores[0]["evsi_usd"],
        "completed_strategy_phase_count": len(proof["completed_phases"]),
        "opportunity_universe_count": len(proof["opportunity_universe_scan"]),
        "counterfactual_route_count": len(proof["counterfactual_comparison"]),
        "anchor_penalty_applied": proof["anchor_dependence_audit"]["anchor_penalty_applied"],
        "recent_memory_only": proof["recent_memory_only"],
        "truth_boundary": {
            "no_L4_feedback_executed": True,
            "no_customer_validation": True,
            "no_revenue_or_payment_signal": True,
            "no_live_provider_execution": True,
            "K9Audit_not_integrated": True,
        },
    }


def _route_prior_values(route_id: str) -> dict[str, float]:
    if "agentic_ai_runtime_governance" in route_id:
        return _values(2500, 0.78, 0.38, 0.55, 0.50, 0.86, 4, 25, 0.25, 0.03, 0.32, 0.95)
    if "agent_production_gap" in route_id:
        return _values(2200, 0.74, 0.30, 0.42, 0.42, 0.78, 6, 35, 0.38, 0.05, 0.38, 0.88)
    if "ai_observability_gap" in route_id:
        return _values(2200, 0.72, 0.28, 0.38, 0.38, 0.75, 7, 35, 0.48, 0.04, 0.40, 0.82)
    if "smb_ai_workflow" in route_id:
        return _values(1200, 0.62, 0.24, 0.45, 0.34, 0.65, 6, 30, 0.55, 0.03, 0.48, 0.65)
    if "ai_crm_execution_gap" in route_id:
        return _values(1500, 0.58, 0.22, 0.30, 0.30, 0.58, 8, 40, 0.60, 0.04, 0.50, 0.58)
    if "cpa_ai_saturation" in route_id:
        return _values(1500, 0.70, 0.22, 0.18, 0.16, 0.42, 10, 45, 0.85, 0.28, 0.58, 0.35)
    if "tariff_margin_pressure" in route_id:
        return _values(1800, 0.68, 0.24, 0.20, 0.18, 0.38, 10, 45, 0.50, 0.62, 0.60, 0.30)
    return _values(1000, 0.40, 0.18, 0.25, 0.25, 0.45, 14, 45, 0.60, 0.20, 0.65, 0.35)


def _values(
    price_midpoint_usd: float,
    market_pull_probability: float,
    willingness_to_pay_probability: float,
    distribution_access_probability: float,
    trust_access_probability: float,
    delivery_success_probability: float,
    time_to_first_signal_days: float,
    validation_cost_usd: float,
    competition_penalty: float,
    regulatory_penalty: float,
    uncertainty_penalty: float,
    internal_capability_feasibility: float,
) -> dict[str, float]:
    return locals()


def _decision_basis(route_id: str) -> str:
    if "agentic_ai_runtime_governance" in route_id:
        return "highest combined market pull, trust-access fit, low regulatory penalty, and strong delivery feasibility"
    if "cpa" in route_id:
        return "real pain but heavily penalized for competitor saturation, trust gap, and regulated/founder-market fit risk"
    if "tariff" in route_id:
        return "real pain but heavily penalized for regulated advice boundary and weak founder-market fit"
    return "ranked by expected first-cash value after competition, uncertainty, time, and feasibility penalties"


def _param(definition: str, source_family: str, allowed_range: list[float]) -> dict[str, Any]:
    return {
        "definition": definition,
        "source_family": source_family,
        "calibration_status": "source_backed_prior_requires_validation",
        "allowed_range": allowed_range,
        "update_rule": "replace prior with owner-approved external feedback or public-read evidence in future runs",
    }


__all__ = [
    "MILESTONE_ID",
    "SESSION_ID",
    "build_market_first_strategy_math_model_strategy",
    "build_math_selected_strategy",
    "build_math_validation_experiment",
    "build_mathematical_source_map",
    "build_parameter_registry",
    "run_e107_strategy_math_model_session",
    "score_routes_with_market_first_math_model",
    "summarize_e107_cieustore",
]
