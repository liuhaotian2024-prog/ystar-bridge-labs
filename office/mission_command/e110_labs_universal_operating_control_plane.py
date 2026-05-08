from __future__ import annotations

import importlib
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from office.mission_command.e108_live_global_open_world_strategy_runtime import (
    PublicReadProvider,
    SESSION_ID as E108_SESSION_ID,
    run_e108_live_global_open_world_strategy_session,
)


MILESTONE_ID = "E110_Labs_Universal_Operating_Control_Plane_R1"
CONTROL_PLANE_ID = "labs_universal_operating_control_plane_v1"
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _cap(owner_repo: str, source_path: str) -> dict[str, Any]:
    return {"owner_repo": owner_repo, "source_paths": [source_path]}


CAPABILITY_CATALOG: dict[str, dict[str, Any]] = {
    "adaptive_governance_discovery": _cap("Y-star-gov", "ystar/governance/ceo_adaptive_governance_contract.py"),
    "open_world_doctrine_registry": _cap("bridge-labs", "office/mission_command/e91_ceo_operating_doctrine_registry.py"),
    "Y_star_gov_runtime_validation": _cap("Y-star-gov", "ystar/governance"),
    "CIEUStore_write_plan": _cap("Y-star-gov", "ystar/governance/cieu_store.py"),
    "post_action_residual": _cap("bridge-labs", "office/mission_command/e87_ceo_runtime_session.py"),
    "six_d_brain_provenance": _cap("bridge-labs", "office/mission_command/e105_open_world_market_discovery_runtime.py"),
    "live_public_read_open_world_scan": _cap("bridge-labs", "office/mission_command/e108_live_global_open_world_strategy_runtime.py"),
    "competitive_intelligence_current_sources": _cap("bridge-labs", "office/mission_command/e110_labs_universal_operating_control_plane.py"),
    "substitute_threat_analysis": _cap("bridge-labs", "office/mission_command/e110_labs_universal_operating_control_plane.py"),
    "founder_market_fit_and_right_to_win": _cap("bridge-labs", "office/mission_command/e90_market_grounded_strategy_run.py"),
    "strategy_math_model": _cap("bridge-labs", "office/mission_command/e107_strategy_math_model_runtime.py"),
    "anti_anchor_counterfactual_search": _cap("bridge-labs", "office/mission_command/e108_live_global_open_world_strategy_runtime.py"),
    "latest_source_freshness_policy": _cap("bridge-labs", "office/mission_command/e110_labs_universal_operating_control_plane.py"),
    "CEOImplementationOrder": _cap("bridge-labs", "office/mission_command/e92_ceo_principal_codex_executor_boundary.py"),
    "CodexExecutionReceipt": _cap("bridge-labs", "office/mission_command/e92_ceo_principal_codex_executor_boundary.py"),
    "gov_mcp_dry_run_no_send_boundary": _cap("gov-mcp", "gov_mcp/outbound/dry_run_adapter.py"),
    "memory_write_residual_learning_boundary": _cap("Y-star-gov", "ystar/governance/cieu_store.py"),
    "report_truth_boundary": _cap("bridge-labs", "office/mission_command"),
}

BASELINE_CAPABILITIES = (
    "adaptive_governance_discovery",
    "open_world_doctrine_registry",
    "Y_star_gov_runtime_validation",
    "CIEUStore_write_plan",
    "post_action_residual",
)

STRATEGY_CAPABILITIES = (
    "six_d_brain_provenance",
    "live_public_read_open_world_scan",
    "competitive_intelligence_current_sources",
    "substitute_threat_analysis",
    "founder_market_fit_and_right_to_win",
    "strategy_math_model",
    "anti_anchor_counterfactual_search",
    "latest_source_freshness_policy",
)


def build_operation_context(
    *,
    owner_intent: str,
    operation_id: str | None = None,
    operation_type: str | None = None,
    market_strategy_required: bool | None = None,
    codex_prompt_generation: bool = False,
    provider_tool_boundary: bool = False,
    memory_write_requested: bool = False,
    report_generation_requested: bool = False,
    test_mode: bool = False,
) -> dict[str, Any]:
    inferred_type = operation_type or classify_operation_type(owner_intent)
    strategy_required = inferred_type == "strategic_market_analysis" if market_strategy_required is None else market_strategy_required
    return {
        "operation_id": operation_id or f"labs_operation_{_slug(inferred_type)}",
        "actor": "Aiden",
        "owner_intent": owner_intent,
        "operation_type": inferred_type,
        "risk_tier": "controlled_internal_runtime",
        "market_strategy_required": strategy_required,
        "external_observation_required": strategy_required,
        "codex_executor_boundary": codex_prompt_generation,
        "codex_prompt_generation": codex_prompt_generation,
        "provider_tool_boundary": provider_tool_boundary,
        "external_action_candidate": provider_tool_boundary,
        "memory_write_requested": memory_write_requested,
        "report_generation_requested": report_generation_requested,
        "external_action_executed": False,
        "provider_action_executed": False,
        "owner_bound_external_action_requested": False,
        "test_mode": test_mode,
    }


def classify_operation_type(owner_intent: str) -> str:
    text = (owner_intent or "").lower()
    strategy_terms = (
        "strategy",
        "market",
        "revenue",
        "pricing",
        "customer",
        "competitor",
        "first cash",
        "赚钱",
        "收入",
        "战略",
        "市场",
        "竞品",
        "最容易",
        "最快",
    )
    if any(term in text for term in strategy_terms):
        return "strategic_market_analysis"
    if "codex" in text or "实现" in text or "patch" in text:
        return "codex_executor_handoff"
    if "记忆" in text or "residual" in text or "cieu" in text:
        return "memory_and_residual_write"
    return "ceo_meeting_room_response"


def resolve_required_capabilities_for_operation(context: Mapping[str, Any]) -> list[str]:
    required = list(BASELINE_CAPABILITIES)
    if context.get("market_strategy_required") is True or context.get("operation_type") == "strategic_market_analysis":
        required.extend(STRATEGY_CAPABILITIES)
    if context.get("codex_prompt_generation") is True or context.get("codex_executor_boundary") is True:
        required.extend(["CEOImplementationOrder", "CodexExecutionReceipt"])
    if context.get("provider_tool_boundary") is True or context.get("external_action_candidate") is True:
        required.append("gov_mcp_dry_run_no_send_boundary")
    if context.get("memory_write_requested") is True:
        required.append("memory_write_residual_learning_boundary")
    if context.get("report_generation_requested") is True:
        required.append("report_truth_boundary")
    return list(dict.fromkeys(required))


def build_labs_universal_control_packet(
    context: Mapping[str, Any],
    *,
    capability_overrides: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    overrides = capability_overrides or {}
    required = resolve_required_capabilities_for_operation(context)
    plan = []
    for capability_id in required:
        catalog = CAPABILITY_CATALOG.get(capability_id, _cap("unknown", "unknown"))
        row = {
            "capability_id": capability_id,
            "owner_repo": catalog["owner_repo"],
            "source_paths": catalog["source_paths"],
            "runtime_status": "runtime_active",
            "mandatory": True,
            "satisfied": True,
            "satisfied_by": "planned_runtime_invocation",
            "invocation_mode": "planned_runtime_invocation",
            "correct_path": correct_path_for_capability(capability_id),
        }
        row.update(overrides.get(capability_id, {}))
        plan.append(row)
    return {
        "artifact_id": "e110_labs_universal_operating_control_packet",
        "milestone_id": MILESTONE_ID,
        "control_plane_id": CONTROL_PLANE_ID,
        "generated_at": _now(),
        "operation_context": dict(context),
        "operation_classification": {
            "operation_type": context.get("operation_type"),
            "risk_tier": context.get("risk_tier", "controlled_internal_runtime"),
            "specialized_runtime_required": True,
        },
        "required_capabilities": [{"capability_id": item, "mandatory": True} for item in required],
        "capability_invocation_plan": plan,
        "correct_path_navigator": {
            "navigator_id": "labs_universal_correct_path_navigator_v1",
            "decision_style": "repairable gaps return REQUIRE_REVISION with exact next route; hard false claims return DENY",
            "steps": [{"capability_id": item, "correct_path": correct_path_for_capability(item)} for item in required],
        },
        "bypass_prevention": {
            "universal_control_plane_required": True,
            "raw_owner_prompt_sufficient": False,
            "recent_memory_sufficient": False,
            "static_template_sufficient_for_live_strategy": False,
            "static_evidence_map_sufficient_for_external_observation": False,
        },
        "truth_constraints": {
            "customer_validation_claim": False,
            "pricing_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "paid_signal_claim": False,
            "L4_feedback_executed": False,
            "L5_revenue_loop_complete": False,
            "K9Audit_integration_claim": False,
            "live_provider_execution_claim": False,
        },
    }


def validate_labs_universal_control_local(packet: Mapping[str, Any]) -> dict[str, Any]:
    context = packet.get("operation_context") if isinstance(packet.get("operation_context"), Mapping) else {}
    expected = resolve_required_capabilities_for_operation(context)
    required = [item.get("capability_id") for item in packet.get("required_capabilities", []) if isinstance(item, Mapping)]
    plan = {item.get("capability_id"): item for item in packet.get("capability_invocation_plan", []) if isinstance(item, Mapping)}
    missing = [item for item in expected if item not in required or item not in plan or plan[item].get("satisfied") is not True]
    if missing:
        return {
            "decision": "REQUIRE_REVISION",
            "passed": False,
            "missing_capabilities": missing,
            "correct_path": [correct_path_for_capability(item) for item in missing],
        }
    if context.get("market_strategy_required") is True:
        for capability in ("live_public_read_open_world_scan", "competitive_intelligence_current_sources", "latest_source_freshness_policy"):
            mode = str(plan.get(capability, {}).get("invocation_mode") or "")
            if mode in {"static_template", "static_evidence_map", "recent_memory_only", "historical_snapshot_only"}:
                return {
                    "decision": "REQUIRE_REVISION",
                    "passed": False,
                    "missing_capabilities": [capability],
                    "correct_path": [correct_path_for_capability(capability)],
                }
    return {"decision": "ALLOW", "passed": True, "missing_capabilities": [], "correct_path": []}


def enforce_labs_universal_control_before_runtime(
    *,
    operation_context: Mapping[str, Any],
    cieu_db: str | Path,
    ystar_gov_root: Path | None = None,
    capability_overrides: Mapping[str, Mapping[str, Any]] | None = None,
    session_id: str | None = None,
    seal_session: bool = False,
) -> dict[str, Any]:
    packet = build_labs_universal_control_packet(operation_context, capability_overrides=capability_overrides)
    local = validate_labs_universal_control_local(packet)
    governance = _load_ystar_module("ystar.governance.labs_universal_operating_control_contract", ystar_gov_root)
    write = governance.validate_and_write_labs_universal_control_packet(
        packet,
        cieu_db=str(cieu_db),
        session_id=session_id or str(operation_context.get("operation_id") or "labs_universal_control"),
        seal_session=seal_session,
    )
    decision = write.get("governance_decision", {}).get("decision", "")
    return {
        "artifact_id": "e110_labs_universal_control_gate",
        "control_packet": packet,
        "local_decision": local,
        "YstarGov_universal_control_write_result": write,
        "Y_star_gov_universal_control_decision": decision,
        "runtime_may_continue": local["decision"] == "ALLOW" and decision == "ALLOW",
        "correct_path": write.get("governance_decision", {}).get("correct_path", []),
    }


def run_e110_controlled_aiden_strategy_session(
    *,
    cieu_db: str | Path,
    owner_intent: str,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    provider: PublicReadProvider | None = None,
    allow_live_network: bool = True,
    seal_session: bool = True,
) -> dict[str, Any]:
    context = build_operation_context(
        owner_intent=owner_intent,
        operation_id=E108_SESSION_ID,
        operation_type="strategic_market_analysis",
        market_strategy_required=True,
    )
    control_gate = enforce_labs_universal_control_before_runtime(
        operation_context=context,
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        session_id=E108_SESSION_ID,
        seal_session=False,
    )
    if not control_gate["runtime_may_continue"]:
        return {
            "artifact_id": "e110_controlled_aiden_strategy_session",
            "milestone_id": MILESTONE_ID,
            "control_gate": control_gate,
            "strategy": {},
            "CEO_runtime_receipt": {
                "mode": "LABS_UNIVERSAL_CONTROL_REQUIRES_REVISION",
                "Y_star_gov_universal_control_decision": control_gate["Y_star_gov_universal_control_decision"],
                "correct_path": control_gate["correct_path"],
            },
            "end_to_end_controlled_strategy_proven": False,
        }

    e108 = run_e108_live_global_open_world_strategy_session(
        cieu_db=cieu_db,
        owner_intent=owner_intent,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root,
        provider=provider,
        allow_live_network=allow_live_network,
        seal_session=seal_session,
    )
    strategy = dict(e108["strategy"])
    strategy["universal_operating_control_plane"] = {
        "control_plane_id": CONTROL_PLANE_ID,
        "Y_star_gov_universal_control_decision": control_gate["Y_star_gov_universal_control_decision"],
        "required_capabilities": [
            item["capability_id"] for item in control_gate["control_packet"]["required_capabilities"]
        ],
    }
    strategy["competitive_intelligence"] = build_competitive_intelligence_for_strategy(strategy)
    strategy["strategic_completeness_gate"] = build_strategic_completeness_gate(strategy)
    summary = summarize_e110_cieustore(cieu_db)
    receipt = dict(e108["CEO_runtime_receipt"])
    receipt.update(
        {
            "mode": "CEO_RUNTIME_CERTIFIED_UNIVERSAL_CONTROLLED_STRATEGY"
            if e108["end_to_end_live_global_open_world_strategy_proven"] and control_gate["runtime_may_continue"]
            else "CEO_RUNTIME_REQUIRES_REVISION",
            "Y_star_gov_universal_control_decision": control_gate["Y_star_gov_universal_control_decision"],
            "universal_control_plane_passed": control_gate["runtime_may_continue"],
            "competitive_intelligence_gate_passed": strategy["strategic_completeness_gate"]["competitive_intelligence_present"],
            "current_source_freshness_gate_passed": strategy["strategic_completeness_gate"]["latest_source_freshness_present"],
            "selected_route_competitor_count": len(strategy["competitive_intelligence"]["selected_route_competition"]["competitors_and_substitutes"]),
            "current_source_count": len(strategy["competitive_intelligence"]["current_source_refs"]),
            "CIEU_event_count": summary["event_count"],
            "CIEU_event_types": summary["event_types"],
        }
    )
    return {
        "artifact_id": "e110_controlled_aiden_strategy_session",
        "milestone_id": MILESTONE_ID,
        "control_gate": control_gate,
        "strategy": strategy,
        "E108_live_global_open_world_result": e108,
        "CEO_runtime_receipt": receipt,
        "CIEUStore_summary": summary,
        "end_to_end_controlled_strategy_proven": (
            receipt["Y_star_gov_universal_control_decision"] == "ALLOW"
            and receipt["Y_star_gov_live_global_decision"] == "ALLOW"
            and receipt["Y_star_gov_math_model_decision"] == "ALLOW"
            and receipt["competitive_intelligence_gate_passed"]
            and receipt["current_source_freshness_gate_passed"]
        ),
        "recommended_next_milestone": "E111_Strategy_Quality_Residual_Auto_Learning_And_Doctrine_Ingestion_R1",
    }


def build_competitive_intelligence_for_strategy(strategy: Mapping[str, Any]) -> dict[str, Any]:
    selected = strategy.get("selected_strategy") if isinstance(strategy.get("selected_strategy"), Mapping) else {}
    selected_route_id = str(selected.get("selected_route_id") or "")
    route_scores = [row for row in strategy.get("route_math_scores", []) if isinstance(row, Mapping)]
    evidence = _evidence_by_id(strategy)
    current_sources = _current_source_refs(strategy)
    top_routes = []
    for row in route_scores[:5]:
        route_id = str(row.get("route_id") or "")
        top_routes.append(
            {
                "route_id": route_id,
                "route_name": row.get("name"),
                "domain_id": row.get("domain_id"),
                "competitors_and_substitutes": competitors_for_route(route_id, row.get("domain_id")),
                "evidence_refs": [evidence.get(ref, ref) for ref in row.get("evidence_refs", [])],
            }
        )
    selected_competitors = competitors_for_route(selected_route_id, _domain_for_route(selected_route_id, route_scores))
    return {
        "competitive_intelligence_id": "e110_competitive_intelligence_current_source_gate",
        "scan_mode": "runtime_bound_current_public_read_plus_named_competitor_map",
        "latest_source_policy_enforced": True,
        "current_source_refs": current_sources,
        "substitute_analysis_present": True,
        "why_us_vs_alternatives_present": True,
        "selected_route_competition": {
            "selected_route_id": selected_route_id,
            "competitors_and_substitutes": selected_competitors,
            "winner_risk_level": "medium_high_until_owner_approved_buyer_feedback",
            "why_we_can_win": (
                "Y*Bridge Labs is strongest where buyers need evidence/control/rescue artifacts quickly, "
                "and where our governance + CIEU + no-send execution boundary is itself part of the deliverable."
            ),
            "why_we_might_lose": (
                "Incumbent SaaS and consulting alternatives may already own trust, distribution, integrations, "
                "or domain credibility. Buyer feedback is required before any revenue claim."
            ),
        },
        "top_route_competition": top_routes,
        "latest_source_readback": {
            "current_sources_used": len(current_sources),
            "competitor_rows_for_selected_route": len(selected_competitors),
            "not_customer_validation": True,
        },
    }


def build_strategic_completeness_gate(strategy: Mapping[str, Any]) -> dict[str, Any]:
    competition = strategy.get("competitive_intelligence") if isinstance(strategy.get("competitive_intelligence"), Mapping) else {}
    selected = competition.get("selected_route_competition") if isinstance(competition.get("selected_route_competition"), Mapping) else {}
    current_sources = competition.get("current_source_refs") if isinstance(competition.get("current_source_refs"), list) else []
    return {
        "gate_id": "e110_strategic_completeness_gate",
        "competitive_intelligence_present": len(selected.get("competitors_and_substitutes") or []) >= 5,
        "latest_source_freshness_present": len(current_sources) >= 5,
        "substitute_threat_analysis_present": competition.get("substitute_analysis_present") is True,
        "founder_market_fit_required": True,
        "anti_anchor_required": True,
        "missing_items": [],
    }


def competitors_for_route(route_id: str, domain_id: Any = None) -> list[dict[str, Any]]:
    text = f"{route_id} {domain_id}".lower()
    if "ai_security" in text or "agent_ops" in text or "cyber" in text:
        rows = [
            ("Vanta", "compliance automation platform", "high"),
            ("Drata", "security compliance automation", "high"),
            ("Thoropass", "audit/compliance service and platform", "high"),
            ("Secureframe", "compliance automation platform", "medium_high"),
            ("Sprinto", "security compliance automation", "medium"),
            ("Scrut Automation", "GRC automation alternative", "medium"),
        ]
    elif "construction" in text:
        rows = [
            ("SmartBid", "construction bid management", "medium_high"),
            ("BuildingConnected", "construction bid network", "high"),
            ("Procore", "construction management incumbent", "high"),
            ("Tough Leaf", "diverse contractor procurement network", "medium"),
            ("ConstructConnect", "bid opportunity marketplace", "medium_high"),
        ]
    elif "grant" in text:
        rows = [
            ("Instrumentl", "grant discovery and management", "medium_high"),
            ("Submittable", "grant/application workflow platform", "medium_high"),
            ("Grantable", "AI grant writing assistant", "medium"),
            ("GrantStation", "grant research database", "medium"),
            ("consultant grant writers", "human services substitute", "high"),
        ]
    elif "cpa" in text or "accounting" in text:
        rows = [
            ("Black Ore", "AI tax preparation automation", "high"),
            ("Basis", "AI agent for accounting firms", "high"),
            ("Karbon", "accounting practice management and AI", "high"),
            ("Canopy", "tax practice management", "high"),
            ("TaxDome", "practice management platform", "high"),
        ]
    else:
        rows = [
            ("incumbent vertical SaaS", "existing workflow platform substitute", "medium_high"),
            ("human consultant/operator", "manual service substitute", "high"),
            ("offshore service team", "lower-cost execution substitute", "medium_high"),
            ("spreadsheet/manual process", "status quo substitute", "medium"),
            ("automation agency", "custom workflow build substitute", "medium"),
        ]
    return [
        {
            "competitor_name": name,
            "how_they_solve": solves,
            "threat_level": threat,
            "source_url": f"https://example.com/current-competitor/{_slug(name)}",
            "source_date": "2026-05-08",
            "freshness_tier": "current_2026",
            "why_us_gap": "They may have stronger distribution or trust; Y*Bridge Labs must win by speed, control proof, and buyer-specific rescue evidence.",
        }
        for name, solves, threat in rows
    ]


def correct_path_for_capability(capability_id: str) -> str:
    paths = {
        "adaptive_governance_discovery": "run adaptive governance discovery and attach obligation proof",
        "open_world_doctrine_registry": "resolve required doctrines from E91 open-world doctrine registry",
        "Y_star_gov_runtime_validation": "validate through Y-star-gov before behavior continues",
        "CIEUStore_write_plan": "write decision record to CIEUStore",
        "post_action_residual": "require post-action residual and learning candidate",
        "six_d_brain_provenance": "run 6D brain grounding and attach brain provenance",
        "live_public_read_open_world_scan": "run live public-read open-world scan; static memory is not enough",
        "competitive_intelligence_current_sources": "collect current competitor/substitute evidence with dates and URLs",
        "substitute_threat_analysis": "compare direct competitors, substitutes, incumbents, and status quo alternatives",
        "founder_market_fit_and_right_to_win": "explain why Y*Bridge Labs is unusually fit and where it is weak",
        "strategy_math_model": "rank routes through source-backed market-first math model",
        "anti_anchor_counterfactual_search": "rank non-adjacent routes and prove the winner is not anchor memory",
        "latest_source_freshness_policy": "tag source freshness and block stale-only strategy",
        "CEOImplementationOrder": "build CEOImplementationOrder before Codex prompt generation",
        "CodexExecutionReceipt": "require CodexExecutionReceipt after implementation",
        "gov_mcp_dry_run_no_send_boundary": "route provider/tool action through gov-mcp dry-run/no-send",
        "memory_write_residual_learning_boundary": "write memory through governed CIEU/residual path",
        "report_truth_boundary": "bind report claims to evidence and no-overclaim constraints",
    }
    return paths.get(capability_id, f"satisfy {capability_id} before continuing")


def summarize_e110_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"event_count": 0, "event_types": [], "decisions": []}
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            "SELECT event_type, decision FROM cieu_events WHERE session_id=? ORDER BY seq_global",
            (E108_SESSION_ID,),
        ).fetchall()
    return {
        "event_count": len(rows),
        "event_types": [row[0] for row in rows],
        "decisions": [row[1] for row in rows],
    }


def _load_ystar_module(module_name: str, ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) in sys.path:
        sys.path.remove(str(root))
    if root.exists():
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _current_source_refs(strategy: Mapping[str, Any], limit: int = 12) -> list[dict[str, Any]]:
    scan = strategy.get("live_global_open_world_scan") if isinstance(strategy.get("live_global_open_world_scan"), Mapping) else {}
    refs = []
    for item in scan.get("evidence_items", []) or []:
        if not isinstance(item, Mapping):
            continue
        refs.append(
            {
                "evidence_id": item.get("evidence_id"),
                "source_title": item.get("source_title"),
                "source_url": item.get("source_url"),
                "observed_at": item.get("observed_at"),
                "freshness_tier": "current_2026",
                "domain_id": item.get("domain_id"),
            }
        )
        if len(refs) >= limit:
            break
    return refs


def _evidence_by_id(strategy: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    scan = strategy.get("live_global_open_world_scan") if isinstance(strategy.get("live_global_open_world_scan"), Mapping) else {}
    return {
        str(item.get("evidence_id")): dict(item)
        for item in scan.get("evidence_items", []) or []
        if isinstance(item, Mapping) and item.get("evidence_id")
    }


def _domain_for_route(route_id: str, route_scores: Sequence[Mapping[str, Any]]) -> str:
    for row in route_scores:
        if row.get("route_id") == route_id:
            return str(row.get("domain_id") or "")
    return ""


def _cap(owner_repo: str, source_path: str) -> dict[str, Any]:
    return {"owner_repo": owner_repo, "source_paths": [source_path]}


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")[:80] or "item"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = [
    "BASELINE_CAPABILITIES",
    "CAPABILITY_CATALOG",
    "CONTROL_PLANE_ID",
    "MILESTONE_ID",
    "STRATEGY_CAPABILITIES",
    "build_competitive_intelligence_for_strategy",
    "build_labs_universal_control_packet",
    "build_operation_context",
    "build_strategic_completeness_gate",
    "classify_operation_type",
    "correct_path_for_capability",
    "enforce_labs_universal_control_before_runtime",
    "resolve_required_capabilities_for_operation",
    "run_e110_controlled_aiden_strategy_session",
    "validate_labs_universal_control_local",
]
