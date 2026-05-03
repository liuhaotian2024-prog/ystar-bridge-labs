from __future__ import annotations

from typing import Any, Dict, List, Mapping


E15_ROUTES = ["E15A", "E15B", "E15C", "E15D", "E15E"]


def build_c3_e15_next_action_packet(
    *,
    batch: Mapping[str, Any],
    replay_report: Mapping[str, Any],
    handoff_batch: Mapping[str, Any],
    feedback_fixture: Mapping[str, Any],
) -> Dict[str, Any]:
    all_consistent = replay_report.get("all_consistent") is True
    handoff_ready = len(handoff_batch.get("handoff_items", [])) >= 5
    primary_ready = sum(1 for item in batch.get("actions", []) if item.get("role") == "primary") == 3
    recommended = "E15A" if all_consistent and handoff_ready and primary_ready else "E15E"
    return {
        "packet_id": "c3_e15_next_action_decision_packet",
        "recommended_route": recommended,
        "routes": {
            "E15A": {
                "name": "owner manually sends 3 validation messages and records result",
                "trigger_condition": "C3 owner-handoff batch is ready and owner activates narrow envelope.",
                "required_evidence": ["C3 batch", "owner activation", "valid action ledger after manual send"],
                "allowed_actions": ["owner manual send", "action ledger entry", "feedback event entry"],
                "blocked_actions": ["Aiden autonomous send", "payment", "login", "form submit", "publication"],
                "owner_involvement_level": "constitutional activation plus optional manual send while gov-mcp live adapter is inactive",
                "expected_next_repository_milestone": "E15A_owner_handoff_validation_execution",
            },
            "E15B": {
                "name": "revise offer before sending because target/message fit is weak",
                "trigger_condition": "feedback fixture or owner review flags weak fit.",
                "required_evidence": ["target/message fit issue", "offer objection"],
                "allowed_actions": ["revise draft", "rerun batch selection"],
                "blocked_actions": ["send unrevised weak-fit message"],
                "owner_involvement_level": "review revised positioning only",
                "expected_next_repository_milestone": "E15B_offer_revision_before_action",
            },
            "E15C": {
                "name": "expand target discovery before outreach",
                "trigger_condition": "insufficient primary/fallback target quality.",
                "required_evidence": ["missing_fields", "weak evidence basis"],
                "allowed_actions": ["public read-only target discovery"],
                "blocked_actions": ["scrape personal contacts", "contact targets"],
                "owner_involvement_level": "approve target-class boundary if changed",
                "expected_next_repository_milestone": "E15C_target_expansion",
            },
            "E15D": {
                "name": "activate narrower gov-mcp controlled execution pilot after owner approval",
                "trigger_condition": "owner approves gov-mcp controlled execution envelope and adapter is available.",
                "required_evidence": ["owner activation", "gov-mcp adapter preflight", "suppression policy"],
                "allowed_actions": ["gov-mcp controlled low-volume execution"],
                "blocked_actions": ["out-of-envelope execution", "bulk outreach", "payment"],
                "owner_involvement_level": "constitutional envelope only, not micro-operator",
                "expected_next_repository_milestone": "E15D_gov_mcp_controlled_action_pilot",
            },
            "E15E": {
                "name": "suppress risky/incomplete targets and replace batch",
                "trigger_condition": "risk, missing fields, opt-out, complaint, or decision replay inconsistency.",
                "required_evidence": ["suppression reason", "replacement criteria"],
                "allowed_actions": ["suppress target", "replace target"],
                "blocked_actions": ["continue suppressed target"],
                "owner_involvement_level": "review only if target class changes",
                "expected_next_repository_milestone": "E15E_batch_replacement",
            },
        },
        "why_recommended": "C3 replay is consistent and owner-handoff batch is ready; real execution still requires owner activation and later ledger/feedback.",
        "external_action_executed": False,
        "feedback_fixture_count": len(feedback_fixture.get("examples", [])),
    }


def validate_c3_e15_next_action_packet(packet: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if packet.get("recommended_route") not in E15_ROUTES:
        errors.append("invalid_recommended_route")
    for route in E15_ROUTES:
        if route not in packet.get("routes", {}):
            errors.append(f"missing_route_{route}")
    if packet.get("external_action_executed") is not False:
        errors.append("e15_packet_must_not_execute_external_action")
    route = packet.get("routes", {}).get(packet.get("recommended_route"), {})
    for key in ["trigger_condition", "required_evidence", "allowed_actions", "blocked_actions", "owner_involvement_level", "expected_next_repository_milestone"]:
        if not route.get(key):
            errors.append(f"recommended_route_missing_{key}")
    return errors
