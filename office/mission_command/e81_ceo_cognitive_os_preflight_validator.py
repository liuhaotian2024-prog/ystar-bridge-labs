from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .e81_ceo_cognitive_os_contract import (
    BRIDGE_ROOT,
    FORBIDDEN_CLAIMS,
    JOB_ID,
    base_verified,
    git_state,
    load_json,
    utc_now,
    write_contract_outputs,
    write_json,
    write_md,
)


def _hash_payload(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _cieu_validation_record(packet: dict[str, Any], decision: str, reason: str, failed_stage: str = "") -> dict[str, Any]:
    return {
        "X_t": {
            "contract": "ceo_cognitive_os_loop_contract_v1",
            "packet_id": packet.get("packet_id"),
            "action_class": packet.get("action_class"),
        },
        "U_t": "bridge_labs_pre_sync_cognitive_os_validation",
        "Y_star_t": "CEO work passes mandatory discovery-first cognitive loop before acceptance",
        "Y_t_plus_1": {"decision": decision, "reason": reason, "failed_stage": failed_stage},
        "R_t_plus_1": "no residual" if decision == "ALLOW" else f"blocked residual: {reason}",
    }


def _decision(decision: str, reason: str, packet: dict[str, Any], failed_stage: str = "") -> dict[str, Any]:
    return {
        "decision": decision,
        "reason": reason,
        "failed_stage": failed_stage,
        "CIEU_validation_record": _cieu_validation_record(packet, decision, reason, failed_stage),
    }


def _required_loop_stage_ids(root: Path) -> list[str]:
    contract = load_json("operations/external_validation/e81_ceo_cognitive_os_loop_contract.json", root)
    return [stage["stage_id"] for stage in contract.get("mandatory_stages", [])]


def _inventory_by_id(root: Path) -> dict[str, dict[str, Any]]:
    inv = load_json("operations/external_validation/e80_whole_ecosystem_capability_inventory.json", root)
    return {cap["capability_id"]: cap for cap in inv.get("capabilities", [])}


def validate_pre_action_packet(packet: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    schema = load_json("operations/external_validation/e81_ceo_mandatory_pre_action_packet_schema.json", base)
    required = schema.get("minimum_required_fields", [])
    missing = [field for field in required if field not in packet]
    if missing:
        return _decision("DENY", f"missing required fields: {', '.join(missing)}", packet, "schema")
    if packet.get("bypass_attempt") is not False:
        return _decision("DENY", "bypass attempt is not allowed", packet, "bypass_policy")

    stage_ids = set(_required_loop_stage_ids(base))
    packet_stage_ids = {item.get("stage_id") for item in packet.get("loop_stage_results", [])}
    missing_stages = sorted(stage_ids - packet_stage_ids)
    if missing_stages:
        return _decision("DENY", f"missing loop stages: {', '.join(missing_stages[:6])}", packet, "cognitive_os_loop")

    capabilities = packet.get("discovered_capabilities_consulted", [])
    if not capabilities:
        return _decision("DENY", "no discovered capabilities consulted", packet, "full_capability_inventory_recall")
    inventory = _inventory_by_id(base)
    for cap in capabilities:
        cap_id = cap.get("capability_id")
        if not cap.get("evidence_paths"):
            return _decision("DENY", f"capability lacks evidence paths: {cap_id}", packet, "repository_evidence")
        if cap_id not in inventory and cap.get("claimed_runtime_active"):
            return _decision("DENY", f"unverified runtime-active capability claim: {cap_id}", packet, "repository_evidence")
        if cap.get("claimed_runtime_active") and inventory.get(cap_id, {}).get("activation_state") not in {"active_in_current_CEO_loop", "active_but_shallow", "readback_only", "legacy_promoted"}:
            return _decision("DENY", f"capability is not verified runtime/context active: {cap_id}", packet, "repository_evidence")

    if packet.get("current_mission_context", {}).get("reasoning_scope") == "recent_memory_only":
        return _decision("DENY", "recent-memory-only reasoning is blocked", packet, "full_capability_inventory_recall")
    if len(packet.get("counterfactual_comparison", [])) < 2:
        return _decision("DENY", "counterfactual comparison requires at least two candidate actions", packet, "counterfactual_action_comparison")

    predictions = packet.get("predicted_CIEU_records", [])
    if not predictions:
        return _decision("DENY", "missing pre-action CIEU prediction", packet, "pre_action_CIEU_residual_prediction")
    required_cieu = set(schema.get("predicted_CIEU_record_required_fields", []))
    for prediction in predictions:
        if not required_cieu.issubset(prediction):
            return _decision("DENY", "pre-action CIEU prediction missing required fields", packet, "pre_action_CIEU_residual_prediction")
    if not packet.get("adversarial_critique"):
        return _decision("DENY", "missing adversarial critique", packet, "adversarial_critique")
    if not packet.get("what_not_to_do"):
        return _decision("DENY", "missing what-not-to-do declaration", packet, "what_not_to_do_declaration")
    if packet.get("action_class") in {"construction", "new_module_construction"} and not packet.get("no_new_wheel_decision", {}).get("non_duplication_proof"):
        return _decision("DENY", "construction recommendation missing no-new-wheel proof", packet, "no_new_wheel_gate")
    if packet.get("action_class") in {"L4_external_feedback_execution", "external_action"} and packet.get("owner_approval_state") != "approved":
        return _decision("DENY", "L4/external execution requires explicit owner approval", packet, "owner_approval_gate")
    if packet.get("approval_required") and packet.get("owner_approval_state") not in {"pending_owner_decision", "approved"}:
        return _decision("DENY", "approval-required action has invalid owner approval state", packet, "owner_approval_gate")

    claims = packet.get("overclaim_boundary", {})
    for claim in FORBIDDEN_CLAIMS:
        if claims.get(claim) is True:
            return _decision("DENY", f"forbidden claim present: {claim}", packet, "overclaim_boundary")
    return _decision("ALLOW", "pre-action packet satisfies bridge-labs pre-sync cognitive OS validator", packet)


def validate_post_action_residual(residual: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    schema = load_json("operations/external_validation/e81_ceo_mandatory_post_action_residual_schema.json", base)
    missing = [field for field in schema.get("minimum_required_fields", []) if field not in residual]
    if missing:
        return _decision("DENY", f"missing post-action fields: {', '.join(missing)}", residual, "post_action_schema")
    cieu = residual.get("CIEU_record", {})
    for field in schema.get("CIEU_record_required_fields", []):
        if field not in cieu:
            return _decision("DENY", f"missing CIEU field: {field}", residual, "post_action_CIEU_residual")
    for claim in FORBIDDEN_CLAIMS:
        if residual.get("overclaim_check", {}).get(claim) is True:
            return _decision("DENY", f"forbidden post-action claim present: {claim}", residual, "post_action_overclaim_check")
    if residual.get("no_new_wheel_check", {}).get("passed") is not True:
        return _decision("DENY", "post-action no-new-wheel check failed", residual, "post_action_no_new_wheel_check")
    if residual.get("intelligence_gate_result", {}).get("passed") is not True:
        return _decision("DENY", "post-action intelligence gate failed", residual, "post_action_intelligence_gate")
    return _decision("ALLOW", "post-action residual satisfies mandatory schema", residual)


def build_valid_pre_action_packet(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    contract = load_json("operations/external_validation/e81_ceo_cognitive_os_loop_contract.json", base)
    inv = load_json("operations/external_validation/e80_whole_ecosystem_capability_inventory.json", base)
    caps = [
        {
            "capability_id": cap["capability_id"],
            "evidence_paths": cap.get("file_paths", [])[:4],
            "activation_state": cap.get("activation_state"),
            "claimed_runtime_active": cap.get("activation_state") in {"active_in_current_CEO_loop", "active_but_shallow", "readback_only"},
        }
        for cap in inv.get("capabilities", [])
        if cap.get("file_paths") and cap.get("activation_state") in {"active_in_current_CEO_loop", "active_but_shallow", "readback_only", "legacy_promoted", "dormant"}
    ][:12]
    stage_results = [
        {
            "stage_id": stage["stage_id"],
            "status": "passed",
            "evidence_paths": stage.get("evidence_source_paths", [])[:5],
        }
        for stage in contract.get("mandatory_stages", [])
    ]
    candidate_actions = [
        "E82_Owner_Approved_YStarGov_CEO_Cognitive_OS_Sync_Patch",
        "E82_Record_Owner_Decision_or_Execute_Minimal_L4_Feedback_Through_Cognitive_OS_If_Approved",
        "E82_Fix_CEO_Cognitive_OS_Preflight_Validator_Blockers",
        "E82_Return_to_L2_Strategic_Rebuild_With_Discovery_First_Cognition",
    ]
    return {
        "packet_id": "e81_valid_live_internal_decision_pre_action_packet",
        "job_id": JOB_ID,
        "proposed_action": "recommend owner decision for Y-star-gov cognitive OS sync patch before L4 execution",
        "action_class": "owner_decision_preparation",
        "owner_intent": "make future CEO work enforceably gated by cognitive OS, not soft instruction",
        "current_mission_context": {"reasoning_scope": "discovery_first_full_ecosystem", "external_action_allowed": False},
        "discovered_capabilities_consulted": caps,
        "historical_assets_consulted": ["E80 discovery indexes", "E79 judgment gate", "E73 no-new-wheel policy", "E24/E10-E23 commercial assets"],
        "canonical_owner_map": {"bridge-labs": "pre-sync validator", "Y-star-gov": "canonical governance", "K9Audit": "CIEU ledger/verifier", "gov-mcp": "provider execution envelope"},
        "no_new_wheel_decision": {"decision": "wrap_existing_and_sync_contract", "non_duplication_proof": "bridge-labs validates pre-sync only; Y-star-gov remains canonical enforcement owner"},
        "buyer_or_user_context": "owner / future CEO work reviewer",
        "commercial_path_context": "protect L4 feedback path from generic CEO artifacts",
        "candidate_actions": candidate_actions,
        "counterfactual_comparison": [
            {"candidate": candidate_actions[0], "expected_gain": "canonical enforcement sync", "expected_risk": "requires owner-approved Y-star-gov mutation"},
            {"candidate": candidate_actions[1], "expected_gain": "moves toward L4 feedback", "expected_risk": "canonical sync still pending"},
            {"candidate": candidate_actions[2], "expected_gain": "fixes blockers if validator fails", "expected_risk": "unneeded if validator passes"},
        ],
        "predicted_CIEU_records": [
            {
                "X_t": "E80 discovery-first loop exists; E81 must make it mandatory",
                "U_t": "create owner-decision path for Y-star-gov sync patch",
                "Y_star_t": "future CEO work cannot bypass cognitive OS",
                "expected_Y_t_plus_1": "bridge-labs validator works and Y-star-gov sync packet is ready",
                "predicted_R_t_plus_1": "canonical Y-star-gov patch remains owner-gated",
                "residual_severity": "medium",
            }
        ],
        "adversarial_critique": "This can still become bureaucracy if it blocks real L4 feedback without a clear owner decision.",
        "what_not_to_do": ["do not mutate Y-star-gov without verified base", "do not create parallel governance engine", "do not execute L4 without owner approval"],
        "selected_action": candidate_actions[0],
        "why_this_action": "It closes the gap between advisory bridge-labs preflight and canonical Y-star-gov enforcement.",
        "why_not_other_actions": "L4 feedback is useful but should run through the cognitive OS gate; more validator work is unnecessary if fixtures pass.",
        "safety_boundary": {"external_action_allowed": False, "Y_star_gov_mutation_allowed": False},
        "overclaim_boundary": {claim: False for claim in FORBIDDEN_CLAIMS},
        "Y_star_contract_hash_input": _hash_payload(contract),
        "required_YstarGov_check": "future owner-approved Y-star-gov patch should consume sync packet",
        "approval_required": True,
        "owner_approval_state": "pending_owner_decision",
        "bypass_attempt": False,
        "loop_stage_results": stage_results,
    }


def build_post_action_residual(pre_packet: dict[str, Any], validator_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "packet_id": "e81_live_internal_decision_post_action_residual",
        "linked_pre_action_packet_id": pre_packet["packet_id"],
        "action_taken": pre_packet["selected_action"],
        "expected_outcome": pre_packet["predicted_CIEU_records"][0]["expected_Y_t_plus_1"],
        "actual_output": "live internal decision accepted only after pre-action validator ALLOW decision",
        "CIEU_record": {
            "X_t": "E81 cognitive OS contract and validator exist",
            "U_t": "validated live internal decision",
            "Y_star_t": "future CEO work is enforceably gated in bridge-labs and ready for Y-star-gov sync",
            "Y_t_plus_1": "validator allowed owner-decision path; no external action executed",
            "R_t_plus_1": "Y-star-gov canonical sync remains pending owner-approved patch",
        },
        "residuals": ["Y-star-gov not mutated", "L4 feedback not executed", "customer/paid/pricing validation absent"],
        "unexpected_failures": [],
        "overclaim_check": {claim: False for claim in FORBIDDEN_CLAIMS},
        "no_new_wheel_check": {"passed": True, "proof": "no Y-star-gov/K9/gov-mcp core duplicate created"},
        "owner_usefulness_check": {"passed": True, "reason": "next owner decision is concrete"},
        "intelligence_gate_result": {"passed": validator_result["decision"] == "ALLOW"},
        "capability_state_updates": ["CEO cognitive OS pre-sync enforcement installed in bridge-labs"],
        "learning_candidates": ["patch Y-star-gov only after owner approval and base verification"],
        "YstarGov_sync_status": "pending_owner_approved_patch",
        "next_action_recommendation": "E82_Owner_Approved_YStarGov_CEO_Cognitive_OS_Sync_Patch",
        "what_not_to_do_next": ["do not bypass cognitive OS", "do not mutate Y-star-gov without owner approval", "do not execute L4 without approval"],
    }


def _fixture_variants(valid: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    fixtures: list[tuple[str, dict[str, Any]]] = [("valid_full_packet", valid)]

    recent = json.loads(json.dumps(valid))
    recent["packet_id"] = "invalid_recent_memory_only"
    recent["current_mission_context"]["reasoning_scope"] = "recent_memory_only"
    fixtures.append(("invalid_recent_memory_only", recent))

    no_counter = json.loads(json.dumps(valid))
    no_counter["packet_id"] = "invalid_no_counterfactual"
    no_counter["counterfactual_comparison"] = []
    fixtures.append(("invalid_no_counterfactual", no_counter))

    no_cieu = json.loads(json.dumps(valid))
    no_cieu["packet_id"] = "invalid_no_pre_action_cieu_prediction"
    no_cieu["predicted_CIEU_records"] = []
    fixtures.append(("invalid_no_pre_action_cieu_prediction", no_cieu))

    no_critique = json.loads(json.dumps(valid))
    no_critique["packet_id"] = "invalid_no_adversarial_critique"
    no_critique["adversarial_critique"] = ""
    fixtures.append(("invalid_no_adversarial_critique", no_critique))

    construction = json.loads(json.dumps(valid))
    construction["packet_id"] = "invalid_construction_without_no_new_wheel"
    construction["action_class"] = "construction"
    construction["no_new_wheel_decision"] = {"decision": "create_new"}
    fixtures.append(("invalid_construction_without_no_new_wheel", construction))

    l4 = json.loads(json.dumps(valid))
    l4["packet_id"] = "invalid_L4_without_owner_approval"
    l4["action_class"] = "L4_external_feedback_execution"
    l4["owner_approval_state"] = "pending_owner_decision"
    fixtures.append(("invalid_L4_without_owner_approval", l4))

    unverified = json.loads(json.dumps(valid))
    unverified["packet_id"] = "invalid_unverified_runtime_active_capability"
    unverified["discovered_capabilities_consulted"].append({"capability_id": "cap_fake_runtime_brain", "evidence_paths": ["prompt_only"], "claimed_runtime_active": True})
    fixtures.append(("invalid_unverified_runtime_active_capability", unverified))

    forbidden = json.loads(json.dumps(valid))
    forbidden["packet_id"] = "invalid_forbidden_customer_paid_compliance_claim"
    forbidden["overclaim_boundary"]["customer_validation_claim"] = True
    fixtures.append(("invalid_forbidden_customer_paid_compliance_claim", forbidden))

    return fixtures


def build_fixture_results(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    valid = build_valid_pre_action_packet(base)
    results = []
    for fixture_id, packet in _fixture_variants(valid):
        result = validate_pre_action_packet(packet, base)
        results.append(
            {
                "fixture_id": fixture_id,
                "decision": result["decision"],
                "reason": result["reason"],
                "failed_stage": result["failed_stage"],
                "CIEU_style_validation_record": result["CIEU_validation_record"],
            }
        )
    return {
        "artifact_id": "e81_cognitive_os_enforcement_fixture_results",
        "bridge_job_id": JOB_ID,
        "validator": "bridge_labs_pre_sync_validator",
        "canonical_governance_owner": "Y-star-gov",
        "fixture_count": len(results),
        "results": results,
        "valid_packet_allowed": any(item["fixture_id"] == "valid_full_packet" and item["decision"] == "ALLOW" for item in results),
        "invalid_packets_denied": all(item["decision"] == "DENY" for item in results if item["fixture_id"] != "valid_full_packet"),
    }


def build_validator_state(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    contract = load_json("operations/external_validation/e81_ceo_cognitive_os_loop_contract.json", base)
    return {
        "artifact_id": "e81_ceo_cognitive_os_preflight_validator_state",
        "bridge_job_id": JOB_ID,
        "validator_status": "bridge_labs_pre_sync_validator_ready",
        "canonical_governance_owner": "Y-star-gov",
        "future_sync_required": True,
        "contract_loaded": bool(contract.get("contract_id")),
        "decision_values": ["ALLOW", "DENY", "ESCALATE"],
        "denial_rules": [
            "missing loop stage",
            "missing repository evidence",
            "missing counterfactual",
            "missing CIEU prediction",
            "missing adversarial critique",
            "missing what-not-to-do",
            "missing no-new-wheel proof",
            "missing owner approval for L4/external action",
            "forbidden claim",
            "bypass attempt",
        ],
        "Y_star_gov_mutated": False,
        "external_action_allowed": False,
    }


def build_live_internal_decision(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    pre_packet = build_valid_pre_action_packet(base)
    pre_packet["packet_id"] = "e81_live_internal_decision_pre_action_packet"
    pre_packet["candidate_actions"] = [
        "E82_Owner_Approved_YStarGov_CEO_Cognitive_OS_Sync_Patch",
        "E82_Record_Owner_Decision_or_Execute_Minimal_L4_Feedback_Through_Cognitive_OS_If_Approved",
        "E82_Return_to_L2_Strategy",
        "E82_Another_Capability_Activation",
    ]
    pre_packet["selected_action"] = "E82_Owner_Approved_YStarGov_CEO_Cognitive_OS_Sync_Patch"
    validator_result = validate_pre_action_packet(pre_packet, base)
    post_residual = build_post_action_residual(pre_packet, validator_result)
    post_result = validate_post_action_residual(post_residual, base)
    return {
        "pre_action_packet": pre_packet,
        "validator_result": validator_result,
        "post_action_residual": post_residual,
        "post_action_validator_result": post_result,
    }


def _md_table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    result = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        result.append("| " + " | ".join(str(value).replace("\n", " ")[:180] for value in row) + " |")
    return result


def write_validator_markdowns(root: Path, outputs: dict[str, Any]) -> None:
    state = outputs["validator_state"]
    write_md(
        root,
        "operations/external_validation/e81_ceo_cognitive_os_preflight_validator_state.md",
        "E81 CEO Cognitive OS Preflight Validator State",
        [
            f"- Status: {state['validator_status']}",
            f"- Canonical governance owner: {state['canonical_governance_owner']}",
            f"- Future sync required: {state['future_sync_required']}",
            f"- Y-star-gov mutated: {state['Y_star_gov_mutated']}",
        ],
    )
    fixtures = outputs["fixture_results"]
    write_md(
        root,
        "operations/external_validation/e81_cognitive_os_enforcement_fixture_results.md",
        "E81 Cognitive OS Enforcement Fixture Results",
        [
            f"- Valid packet allowed: {fixtures['valid_packet_allowed']}",
            f"- Invalid packets denied: {fixtures['invalid_packets_denied']}",
            "",
            *_md_table([[item["fixture_id"], item["decision"], item["failed_stage"], item["reason"]] for item in fixtures["results"]], ["fixture", "decision", "failed_stage", "reason"]),
        ],
    )
    live = outputs["live"]
    for key, rel, title in [
        ("pre_action_packet", "operations/external_validation/e81_live_internal_decision_pre_action_packet.md", "E81 Live Internal Decision Pre-Action Packet"),
        ("validator_result", "operations/external_validation/e81_live_internal_decision_validator_result.md", "E81 Live Internal Decision Validator Result"),
        ("post_action_residual", "operations/external_validation/e81_live_internal_decision_post_action_residual.md", "E81 Live Internal Decision Post-Action Residual"),
    ]:
        write_md(root, rel, title, ["```json", json.dumps(live[key], indent=2, sort_keys=True), "```"])


def write_validator_outputs(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    if not (base / "operations/external_validation/e81_ceo_cognitive_os_loop_contract.json").exists():
        write_contract_outputs(base)
    state = build_validator_state(base)
    write_json(base, "operations/external_validation/e81_ceo_cognitive_os_preflight_validator_state.json", state)
    fixtures = build_fixture_results(base)
    write_json(base, "operations/external_validation/e81_cognitive_os_enforcement_fixture_results.json", fixtures)
    live = build_live_internal_decision(base)
    write_json(base, "operations/external_validation/e81_live_internal_decision_pre_action_packet.json", live["pre_action_packet"])
    write_json(base, "operations/external_validation/e81_live_internal_decision_validator_result.json", live["validator_result"])
    write_json(base, "operations/external_validation/e81_live_internal_decision_post_action_residual.json", live["post_action_residual"])
    outputs = {"validator_state": state, "fixture_results": fixtures, "live": live}
    write_validator_markdowns(base, outputs)
    return outputs


if __name__ == "__main__":
    result = write_validator_outputs()
    print(json.dumps({"artifact_id": "e81_validator_outputs", "fixture_count": result["fixture_results"]["fixture_count"]}, indent=2))
