from __future__ import annotations

from typing import Any

from .e42_reuse_first_no_rebuild_gate import evaluate_reuse_first_gate
from .e42_task_capability_matcher import match_task_to_capabilities
from .e44a_ceo_capability_activation_registry import build_ceo_capability_activation_registry
from .e44a_ceo_cognition_cascade_runtime import run_ceo_cognition_cascade
from .e44a_router_cognition_overlay import route_task_with_cognition_overlay

STRATEGIC_TERMS = ["strategy", "strategic", "commercial", "business", "customer", "buyer", "first user", "opportunity", "innovation", "imagination", "route"]

def run_ceo_task_preflight_v2(task: dict[str, Any]) -> dict[str, Any]:
    task_text = f"{task.get('task_title', '')}\n{task.get('task_description', '')}"
    router_matches = match_task_to_capabilities(task_text, top_n=12)
    overlay = route_task_with_cognition_overlay(task_text)
    cascade = run_ceo_cognition_cascade(task)
    gate = evaluate_reuse_first_gate(task_text, router_matches)
    serious = any(term in task_text.lower() for term in STRATEGIC_TERMS)
    return {
        "artifact_id": "e44a_ceo_task_preflight_v2_result",
        "task": task,
        "required_flow": [
            "E42 resource router",
            "E44A cognition activation registry",
            "E44A CEO cognition cascade",
            "E42/E44A no-rebuild gate",
            "route selection",
            "execution plan",
            "validation",
            "owner packet",
        ],
        "router_matches": router_matches,
        "cognition_overlay": overlay,
        "cognition_registry": build_ceo_capability_activation_registry(),
        "cognition_cascade": cascade,
        "no_rebuild_gate": gate,
        "route_selection": cascade["route_selection"],
        "serious_ceo_task": serious,
        "valid": validate_preflight_v2_result({"serious_ceo_task": serious, "cognition_cascade": cascade, "cognition_registry": build_ceo_capability_activation_registry(), "output_mode": "runtime_plus_packet", "external_action_requested": False})["valid"],
        "external_action_occurred": False,
    }

def validate_preflight_v2_result(result: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if result.get("serious_ceo_task") and not result.get("cognition_cascade"):
        errors.append("strategic_or_commercial_task_requires_cognition_cascade")
    registry = result.get("cognition_registry") or {}
    classes = {cap.get("capability_class") for cap in registry.get("capabilities", [])}
    required = {"cognition_lens", "opportunity_generator", "customer_lens", "commercial_screen", "evidence_lens", "execution_screen", "route_selector"}
    missing = sorted(required - classes)
    if missing:
        errors.append("missing_required_capability_classes:" + ",".join(missing))
    if result.get("output_mode") == "report_pile_only":
        errors.append("report_pile_only_blocked_for_execution_or_commercial_task")
    if result.get("external_action_requested") and not result.get("owner_approval_present"):
        errors.append("external_action_blocked_without_owner_approval")
    return {"valid": not errors, "errors": errors}
