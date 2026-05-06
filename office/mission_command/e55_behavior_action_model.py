from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))

ACTION_TYPES = {
    "internal_analysis", "internal_packaging", "internal_validation", "internal_dispatch",
    "public_readonly_observation", "external_contact", "publication", "payment",
    "config_mutation", "server_process", "unknown",
}
EXTERNALITY_LEVELS = {"none", "local_repo", "local_process", "public_readonly", "external_human", "external_publication", "payment_or_secret"}

@dataclass(frozen=True)
class ActionProposal:
    action_id: str
    source: str
    action_type: str
    intent: str
    Xt_current_state: str
    Y_star_target: str
    U_intervention: str
    predicted_Yt_plus_1: str
    predicted_Rt_plus_1: str
    required_inputs: list[str]
    expected_outputs: list[str]
    side_effect_profile: dict[str, Any]
    externality_level: str
    owner_approval_required: bool
    governance_required: bool
    evidence_required: bool
    allowed_by_default: bool
    canonical_runtime_required: bool = True
    evidence_path: list[str] | None = None

@dataclass(frozen=True)
class ActionAuthorization:
    action_id: str
    authorization_status: str
    reason: str
    Y_star_gov_gate_result: dict[str, Any]
    gov_mcp_gate_result: dict[str, Any]
    owner_approval_status: str
    no_go_boundary_result: dict[str, Any]
    capability_binding_result: dict[str, Any]
    anti_drift_result: dict[str, Any]
    external_action_allowed: bool
    no_external_action: bool

@dataclass(frozen=True)
class ActionExecutionEnvelope:
    action_id: str
    execution_mode: str
    command_or_operation: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    expected_artifacts: list[str]
    cleanup_required: bool
    evidence_capture_required: bool
    result_status: str

@dataclass(frozen=True)
class ActionEvidence:
    action_id: str
    evidence_id: str
    output_artifacts: list[str]
    tests_run: list[str]
    KG_update: str
    CZL_closure: str
    CIEU_residual: str
    brain_readback_required: bool


def _proposal(**kwargs: Any) -> dict[str, Any]:
    data = asdict(ActionProposal(**kwargs))
    if data["evidence_path"] is None:
        data["evidence_path"] = []
    return data


def build_seed_action_proposals() -> list[dict[str, Any]]:
    common = {
        "source": "canonical_runtime",
        "Xt_current_state": "CEO brain L5 is ready; E53 owner review remains pending; external action is blocked.",
        "Y_star_target": "L5 behavior control center with governed proposal, authorization, dry-run execution, evidence, and readback.",
        "predicted_Rt_plus_1": "internal behavior loop can prove safe dry-run behavior without external action.",
        "required_inputs": ["E54 brain L5 state", "E53 pending owner decision", "E51 anti-drift/capability gates"],
        "side_effect_profile": {"external_action": False, "network": False, "server_started": False, "client_config_mutation": False},
        "owner_approval_required": False,
        "governance_required": True,
        "evidence_required": True,
        "allowed_by_default": True,
        "canonical_runtime_required": True,
    }
    return [
        _proposal(action_id="e55_behavior_control_center_l5_convergence", action_type="internal_validation", intent="Converge the behavior control center to L5 using dry-run internal validation only.", U_intervention="Build action model, queue, authorization gate, dry-run envelope, and evidence loop.", predicted_Yt_plus_1="Behavior center L5 readiness gate passes.", expected_outputs=["e55_behavior_center_l5_readiness_gate_result.json"], externality_level="local_repo", evidence_path=["operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json"], **common),
        _proposal(action_id="e55_validate_behavior_action_model", action_type="internal_validation", intent="Validate behavior action object model.", U_intervention="Check typed action proposal/auth/envelope/evidence records.", predicted_Yt_plus_1="Action objects are valid and deny unsafe defaults.", expected_outputs=["e55_behavior_action_model.json"], externality_level="none", evidence_path=["operations/external_validation/e55_behavior_action_model.json"], **common),
        _proposal(action_id="e55_validate_behavior_queue", action_type="internal_validation", intent="Validate behavior queue prioritization and external blocking.", U_intervention="Queue internal dry-run proposals and block external review track.", predicted_Yt_plus_1="Queue contains only dry-run executable internal items.", expected_outputs=["e55_behavior_queue_snapshot.json"], externality_level="none", evidence_path=["operations/external_validation/e55_behavior_queue_snapshot.json"], **common),
        _proposal(action_id="e55_validate_authorization_gate", action_type="internal_validation", intent="Validate deterministic authorization gate.", U_intervention="ALLOW/dry-run internal actions and DENY unsafe/external fixtures.", predicted_Yt_plus_1="Authorization gate distinguishes reasoning, proposal, authorization, and execution.", expected_outputs=["e55_action_authorization_gate_result.json"], externality_level="none", evidence_path=["operations/external_validation/e55_action_authorization_gate_result.json"], **common),
        _proposal(action_id="e55_validate_no_external_action_allowed", action_type="internal_validation", intent="Validate no external action remains allowed while owner decision is pending.", U_intervention="Check no-go boundaries and pending owner decision status.", predicted_Yt_plus_1="External action remains blocked.", expected_outputs=["e55_dry_run_action_executor_result.json"], externality_level="none", evidence_path=["operations/external_validation/e55_dry_run_action_executor_result.json"], **common),
    ]


def build_broken_action_fixtures() -> list[dict[str, Any]]:
    base = build_seed_action_proposals()[0].copy()
    fixtures = []
    def make(action_id: str, action_type: str, intent: str, externality: str, **updates: Any) -> dict[str, Any]:
        item = base.copy()
        item.update({"action_id": action_id, "action_type": action_type, "intent": intent, "externality_level": externality, "allowed_by_default": False})
        item.update(updates)
        return item
    fixtures.append(make("fixture_external_contact_pending_owner", "external_contact", "Contact a first reviewer while owner decision is pending.", "external_human", owner_approval_required=True))
    fixtures.append(make("fixture_publication_pending_owner", "publication", "Publish proof packet before owner approval.", "external_publication", owner_approval_required=True))
    fixtures.append(make("fixture_payment_secret_action", "payment", "Use payment or secret material.", "payment_or_secret", owner_approval_required=True))
    fixtures.append(make("fixture_real_mcp_transport_claim", "internal_analysis", "Claim real MCP transport closure without proof.", "none", side_effect_profile={"claim_real_mcp_transport_closed": True}, evidence_path=["operations/external_validation/nonexistent_real_mcp_transport.json"]))
    fixtures.append(make("fixture_customer_validation_claim", "internal_analysis", "Claim customer validation without customer validation.", "none", side_effect_profile={"claim_customer_validation": True}))
    fixtures.append(make("fixture_paid_signal_claim", "internal_analysis", "Claim paid signal without paid signal.", "none", side_effect_profile={"claim_paid_signal": True}))
    fixtures.append(make("fixture_unknown_action", "unknown", "Unknown behavior request.", "none"))
    fixtures.append(make("fixture_ceo_brain_direct_execution", "internal_dispatch", "Let CEO brain execute directly.", "local_repo", source="CEO_brain", canonical_runtime_required=False))
    fixtures.append(make("fixture_missing_evidence_path", "internal_validation", "Complete behavior without evidence path.", "none", evidence_path=[]))
    fixtures.append(make("fixture_bypass_canonical_runtime", "internal_validation", "Bypass canonical action runtime.", "none", canonical_runtime_required=False))
    return fixtures


def validate_action_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    for key in ["action_id", "source", "action_type", "intent", "externality_level", "side_effect_profile"]:
        if key not in proposal:
            failures.append(f"missing_{key}")
    if proposal.get("action_type") not in ACTION_TYPES:
        failures.append("invalid_action_type")
    if proposal.get("externality_level") not in EXTERNALITY_LEVELS:
        failures.append("invalid_externality_level")
    if proposal.get("source") == "CEO_brain" and proposal.get("canonical_runtime_required") is False:
        failures.append("ceo_brain_direct_execution_not_allowed")
    return {"valid": not failures, "failures": failures}


def build_action_model_contract() -> dict[str, Any]:
    proposals = build_seed_action_proposals()
    fixtures = build_broken_action_fixtures()
    return {
        "artifact_id": "e55_behavior_action_model",
        "model_status": "valid",
        "rules": [
            "CEO brain may propose actions but may not authorize or execute.",
            "Canonical behavior center authorizes actions.",
            "External contact, publication, payment, config mutation, and server process actions require explicit owner approval/governance.",
            "pending_owner_decision is not approval.",
            "unknown action defaults to deny/quarantine.",
            "no action can be completed without evidence capture.",
        ],
        "seed_proposals": proposals,
        "broken_fixtures": fixtures,
        "validation": {"seed_valid": all(validate_action_proposal(p)["valid"] for p in proposals), "broken_fixture_count": len(fixtures)},
        "external_action_allowed": False,
        "owner_decision_status": "pending_owner_decision",
        "no_external_action": True,
    }


def write_behavior_action_model(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_action_model_contract()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_behavior_action_model.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = "# E55 Behavior Action Model\n\nModel status: `%s`\n\nSeed proposals: `%s`\n\nExternal action allowed: `false`\n" % (data["model_status"], len(data["seed_proposals"]))
    (root / "reports/integration/e55_behavior_action_model.md").write_text(md, encoding="utf-8")
    return data
