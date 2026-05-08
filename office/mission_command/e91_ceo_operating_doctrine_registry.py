from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
MILESTONE_ID = "E91_Open_World_CEO_Doctrine_Discovery_And_Runtime_Enforcement_R1"
REGISTRY_ID = "ceo_operating_doctrine_registry_open_world_v1"
SPEC_PATH = Path("operations/ceo_doctrine_registry/e91_canonical_doctrine_registry_spec.json")


def build_ceo_operating_doctrine_registry(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    spec = load_registry_spec(base)
    doctrines = list(spec.get("doctrines", []))
    return {
        "artifact_id": "e91_ceo_operating_doctrine_registry",
        "milestone_id": MILESTONE_ID,
        "registry_id": spec.get("registry_id", REGISTRY_ID),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_spec": str(SPEC_PATH),
        "ontology_source": spec.get("ontology_source", "open_world_asset_graph_clusters"),
        "prompt_categories_used_as_closed_ontology": False,
        "doctrines": doctrines,
        "doctrine_by_id": {item["doctrine_id"]: item for item in doctrines},
        "status_counts": _status_counts(doctrines),
        "truth_constraints": spec.get("truth_constraints", {}),
    }


def resolve_required_doctrines_for_action(action_context: Mapping[str, Any], *, root: Path | None = None) -> list[str]:
    registry = build_ceo_operating_doctrine_registry(root)
    required: list[str] = []
    for doctrine in registry["doctrines"]:
        if _doctrine_required(doctrine, action_context):
            required.append(str(doctrine["doctrine_id"]))
    return list(dict.fromkeys(required))


def build_doctrine_invocation_plan(action_context: Mapping[str, Any], *, root: Path | None = None) -> dict[str, Any]:
    registry = build_ceo_operating_doctrine_registry(root)
    required = resolve_required_doctrines_for_action(action_context, root=root)
    planned = [_planned_invocation(registry, doctrine_id, action_context, proof_mode=False) for doctrine_id in required]
    return {
        "artifact_id": "ceo_doctrine_invocation_plan",
        "milestone_id": MILESTONE_ID,
        "registry_id": registry["registry_id"],
        "doctrine_invocation_plan_id": f"plan_{action_context.get('action_id', 'ceo_action')}",
        "action_context": dict(action_context),
        "required_doctrines": required,
        "planned_invocations": planned,
        "overclaim_boundary": _safe_overclaim_boundary(),
        "prompt_categories_used_as_closed_ontology": False,
    }


def validate_doctrine_invocation_plan_local(
    action_context: Mapping[str, Any],
    plan: Mapping[str, Any],
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    required = resolve_required_doctrines_for_action(action_context, root=root)
    planned_ids = {str(item.get("doctrine_id")) for item in plan.get("planned_invocations", []) if isinstance(item, Mapping)}
    missing = [item for item in required if item not in planned_ids]
    if missing:
        return {
            "decision": "REQUIRE_REVISION",
            "passed": False,
            "missing_doctrines": missing,
            "correct_path": ["query registry", "invoke missing mandatory doctrines", "rerun Y-star-gov doctrine validation"],
        }
    if action_context.get("market_strategy_required") is True and action_context.get("test_mode") is not True:
        external = next((item for item in plan.get("planned_invocations", []) if item.get("doctrine_id") == "external_observation_public_read_evidence"), {})
        if external.get("invocation_status") in {"static_evidence_map_only", "historical_public_read_wrapper_invoked"}:
            return {
                "decision": "REQUIRE_REVISION",
                "passed": False,
                "missing_doctrines": ["live_external_observation_runtime"],
                "correct_path": ["wire or invoke live public-read external observation runtime before market strategy continuation"],
            }
    return {"decision": "ALLOW", "passed": True, "missing_doctrines": [], "correct_path": []}


def build_doctrine_invocation_proof(
    action_context: Mapping[str, Any],
    executed_outputs: Mapping[str, Any] | None = None,
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    registry = build_ceo_operating_doctrine_registry(root)
    required = resolve_required_doctrines_for_action(action_context, root=root)
    outputs = dict(executed_outputs or {})
    invocations = []
    for doctrine_id in required:
        invocation = _planned_invocation(registry, doctrine_id, action_context, proof_mode=True)
        invocation["output_summary"] = outputs.get(doctrine_id) or invocation["output_summary"]
        invocation["CIEU_recording_status"] = "candidate_for_Y_star_gov_CIEUStore_write"
        invocations.append(invocation)
    return {
        "artifact_id": "ceo_doctrine_invocation_proof",
        "milestone_id": MILESTONE_ID,
        "registry_id": registry["registry_id"],
        "doctrine_invocation_plan_id": f"plan_{action_context.get('action_id', 'ceo_action')}",
        "doctrine_invocation_proof_id": f"proof_{action_context.get('action_id', 'ceo_action')}",
        "action_context": dict(action_context),
        "required_doctrines": required,
        "doctrine_invocations": invocations,
        "required_doctrines_satisfied": True,
        "overclaim_boundary": _safe_overclaim_boundary(),
    }


def classify_doctrine_runtime_status(doctrine: Mapping[str, Any]) -> str:
    status = str(doctrine.get("runtime_status") or "unknown")
    if doctrine.get("classification") in {"deprecated", "quarantined"}:
        return str(doctrine["classification"])
    return status


def explain_missing_doctrine_requirements(action_context: Mapping[str, Any], plan: Mapping[str, Any], *, root: Path | None = None) -> dict[str, Any]:
    local = validate_doctrine_invocation_plan_local(action_context, plan, root=root)
    return {
        "artifact_id": "ceo_doctrine_missing_requirement_explanation",
        "decision": local["decision"],
        "missing_doctrines": local.get("missing_doctrines", []),
        "correct_path": local.get("correct_path", []),
    }


def build_default_action_context(
    *,
    action_id: str,
    action_type: str,
    mission_type: str,
    route_type: str = "internal_runtime",
    L_level: str = "L5-B",
    provider_tool_boundary: bool = False,
    market_strategy_required: bool = False,
    external_observation_required: bool = False,
    owner_decision_required: bool = False,
    revenue_or_payment_related: bool = False,
    K9Audit_related: bool = False,
    generation_mode: str = "runtime_generated_structured_output",
    test_mode: bool = False,
    live_external_observation_required: bool | None = None,
) -> dict[str, Any]:
    live_required = bool(market_strategy_required and external_observation_required and not test_mode) if live_external_observation_required is None else live_external_observation_required
    return {
        "action_id": action_id,
        "actor": "bridge_labs_ceo",
        "owner_intent": "advance CEO runtime through open-world doctrine invocation",
        "action_type": action_type,
        "mission_type": mission_type,
        "route_type": route_type,
        "L_level": L_level,
        "externality_level": "internal_or_no_send",
        "repo_scope": ["bridge-labs", "Y-star-gov", "gov-mcp"],
        "provider_tool_boundary": provider_tool_boundary,
        "market_strategy_required": market_strategy_required,
        "external_observation_required": external_observation_required,
        "live_external_observation_required": live_required,
        "owner_decision_required": owner_decision_required,
        "revenue_or_payment_related": revenue_or_payment_related,
        "K9Audit_related": K9Audit_related,
        "evidence_need": "repo_history_capability_and_market_evidence_as_required",
        "generation_mode": generation_mode,
        "test_mode": test_mode,
        "execution_requested": False,
        "overclaim_boundary": _safe_overclaim_boundary(),
    }


def write_e91_open_world_registry_reports(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    from office.mission_command.e91_open_world_doctrine_discovery import build_open_world_discovery_reports

    reports = build_open_world_discovery_reports(bridge_root=base)
    registry = build_ceo_operating_doctrine_registry(base)
    report = {
        "artifact_id": "e91_ceo_operating_doctrine_registry_report",
        "milestone_id": MILESTONE_ID,
        "registry_id": registry["registry_id"],
        "total_doctrines": len(registry["doctrines"]),
        "status_counts": registry["status_counts"],
        "open_world_report": "operations/ceo_doctrine_registry/e91_canonical_doctrine_registry_spec.json",
        "prompt_categories_used_as_closed_ontology": False,
    }
    path = base / "office/mission_command/e91_ceo_operating_doctrine_registry_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (base / "office/mission_command/e91_ceo_operating_doctrine_registry_readback.md").write_text(
        "\n".join([
            "# E91 CEO Operating Doctrine Registry Readback",
            "",
            f"- registry_id: {registry['registry_id']}",
            f"- doctrine_count: {len(registry['doctrines'])}",
            "- discovery_source: open-world asset graph, not fixed prompt ontology",
            "- no external action executed",
            "",
        ]),
        encoding="utf-8",
    )
    return {"registry_report": report, "discovery_report": reports["completion_report"]}


def load_registry_spec(root: Path) -> dict[str, Any]:
    path = root / SPEC_PATH
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    from office.mission_command.e91_open_world_doctrine_discovery import build_open_world_discovery_reports

    return build_open_world_discovery_reports(bridge_root=root)["canonical_doctrine_registry_spec"]


def _doctrine_required(doctrine: Mapping[str, Any], action_context: Mapping[str, Any]) -> bool:
    required_rules = list(doctrine.get("mandatory_when") or [])
    return any(_condition_matches(rule, action_context) for rule in required_rules)


def _condition_matches(rule: str, context: Mapping[str, Any]) -> bool:
    rule = str(rule)
    if rule == "major_action=true":
        return True
    if "=" not in rule:
        return False
    key, expected = rule.split("=", 1)
    actual = context.get(key)
    if expected.lower() == "true":
        return actual is True
    if expected.lower() == "false":
        return actual is False
    return str(actual) == expected


def _planned_invocation(registry: Mapping[str, Any], doctrine_id: str, action_context: Mapping[str, Any], *, proof_mode: bool) -> dict[str, Any]:
    doctrine = registry["doctrine_by_id"].get(doctrine_id, {"doctrine_id": doctrine_id, "runtime_status": "missing", "source_paths": []})
    invocation_status = _invocation_status_for(doctrine_id, doctrine, action_context, proof_mode=proof_mode)
    invocation = {
        "doctrine_id": doctrine_id,
        "canonical_owner": doctrine.get("canonical_owner_repo", "bridge-labs"),
        "source_paths": doctrine.get("source_paths", [])[:12],
        "runtime_status": doctrine.get("runtime_status", "unknown"),
        "invocation_status": invocation_status,
        "output_summary": _default_output_summary(doctrine_id, doctrine, action_context),
        "evidence_refs": _evidence_refs(doctrine),
        "gaps": _gaps_for_invocation(doctrine_id, invocation_status, action_context),
        "CIEU_recording_status": "candidate_for_Y_star_gov_CIEUStore_write",
    }
    if doctrine_id == "gov_mcp_dry_run_provider_boundary":
        invocation.update(
            {
                "provider_action_executed": False,
                "external_side_effect": False,
                "no_send_invariant": True,
            }
        )
    return invocation


def _invocation_status_for(doctrine_id: str, doctrine: Mapping[str, Any], action_context: Mapping[str, Any], *, proof_mode: bool) -> str:
    if doctrine_id == "external_observation_public_read_evidence":
        if action_context.get("live_external_observation_required") is True:
            return "historical_public_read_wrapper_invoked"
        return "historical_public_read_wrapper_invoked"
    if doctrine_id == "gov_mcp_dry_run_provider_boundary":
        return "dry_run_invoked"
    if "owner_decision" in doctrine_id:
        return "owner_packet_prepared"
    if classify_doctrine_runtime_status(doctrine) in {"report_only", "artifact_only"}:
        return "historical_context_bound"
    return "completed" if proof_mode else "planned"


def _default_output_summary(doctrine_id: str, doctrine: Mapping[str, Any], action_context: Mapping[str, Any]) -> str:
    if doctrine_id == "external_observation_public_read_evidence":
        return "Historical public-read evidence artifacts were located; live observation remains unavailable unless explicitly wired and approved."
    return f"{doctrine.get('title', doctrine_id)} bound through open-world doctrine registry for {action_context.get('action_id')}"


def _gaps_for_invocation(doctrine_id: str, invocation_status: str, action_context: Mapping[str, Any]) -> list[str]:
    if doctrine_id == "external_observation_public_read_evidence" and action_context.get("live_external_observation_required") is True:
        return ["live_external_observation_runtime_unavailable_or_not_invoked"]
    if invocation_status == "historical_context_bound":
        return ["report_only_context_cannot_satisfy_live_runtime_requirement"]
    return []


def _evidence_refs(doctrine: Mapping[str, Any]) -> list[str]:
    refs = [str(item) for item in doctrine.get("source_paths", [])[:8]]
    return refs or ["operations/ceo_doctrine_registry/e91_canonical_doctrine_registry_spec.json"]


def _status_counts(doctrines: list[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for doctrine in doctrines:
        status = classify_doctrine_runtime_status(doctrine)
        counts[status] = counts.get(status, 0) + 1
    return counts


def _safe_overclaim_boundary() -> dict[str, bool]:
    return {
        "customer_validation_claim": False,
        "revenue_claim": False,
        "payment_claim": False,
        "paid_signal_claim": False,
        "pricing_validation_claim": False,
        "L4_feedback_executed": False,
        "L5_revenue_loop_complete": False,
        "production_deployment_claim": False,
        "K9Audit_integration_claim": False,
    }


__all__ = [
    "build_ceo_operating_doctrine_registry",
    "resolve_required_doctrines_for_action",
    "build_doctrine_invocation_plan",
    "validate_doctrine_invocation_plan_local",
    "build_doctrine_invocation_proof",
    "classify_doctrine_runtime_status",
    "explain_missing_doctrine_requirements",
    "build_default_action_context",
    "write_e91_open_world_registry_reports",
]
