from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))

E56_CYCLE_ID = "e56_internal_company_operating_cycle_20260506T000001Z"
SELECTED_ACTION = "run_internal_operating_loop_self_test"
NEAREST_ALTERNATIVE = "prepare_E57_post_L5_money_route_retest"
NEXT_MILESTONE = "E57_post_L5_money_route_retest"
OWNER_STATUS = "pending_owner_decision"


@dataclass(frozen=True)
class InternalCompanyCycle:
    cycle_id: str
    trigger: str
    mission_context: str
    current_state: dict[str, Any]
    interpreted_task: str
    candidate_actions: list[dict[str, Any]]
    counterfactual_comparison: dict[str, Any]
    selected_action: str
    behavior_queue_item: dict[str, Any]
    authorization_result: dict[str, Any]
    execution_envelope: dict[str, Any]
    execution_result: dict[str, Any]
    evidence_packet: dict[str, Any]
    KG_update: str
    CZL_closure: str
    CIEU_residual: str
    brain_readback: dict[str, Any]
    self_evaluation: dict[str, Any]
    next_milestone_proposal: str
    no_external_action: bool


def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(root: Path, rel: str, data: dict[str, Any]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def current_state_summary() -> dict[str, Any]:
    e54 = _json("operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json")
    e55 = _json("operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json")
    e53 = _json("operations/external_validation/e53_first_user_review_risk_gate_result.json")
    return {
        "ceo_brain_l5_status": e54.get("final_status") or "ceo_brain_l5_cognitive_center_ready",
        "behavior_center_l5_status": e55.get("final_status") or "behavior_control_center_l5_ready",
        "owner_decision_status": e53.get("owner_decision_status") or OWNER_STATUS,
        "risk_gate_status": e53.get("gate_status") or "blocked_pending_owner_decision",
        "external_action_allowed": False,
        "proof_packet_status": "owner_reviewable_only",
        "real_mcp_transport_claimed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
    }


def cycle_stages() -> list[dict[str, Any]]:
    return [
        {"stage_id": "load_ceo_brain_state", "required_input": "E54 CEO brain L5 state", "required_output": "current state summary"},
        {"stage_id": "interpret_mission_and_current_state", "required_input": "owner directive plus current state", "required_output": "internal loop task interpretation"},
        {"stage_id": "generate_candidate_next_actions", "required_input": "current blockers and no-go boundaries", "required_output": "candidate internal/external actions"},
        {"stage_id": "run_counterfactual_comparison", "required_input": "candidate actions", "required_output": "selected internal self-test action and nearest alternative"},
        {"stage_id": "enqueue_selected_internal_action", "required_input": "selected action", "required_output": "behavior queue item"},
        {"stage_id": "authorize_action", "required_input": "queue item", "required_output": "dry-run-only authorization"},
        {"stage_id": "dry_run_execute_internal_action", "required_input": "authorization", "required_output": "internal dry-run trace"},
        {"stage_id": "capture_evidence", "required_input": "dry-run trace", "required_output": "evidence packet"},
        {"stage_id": "write_KG_CZL_CIEU", "required_input": "evidence packet", "required_output": "KG/CZL/CIEU artifacts"},
        {"stage_id": "readback_into_CEO_brain", "required_input": "brain update", "required_output": "CEO brain readback smoke"},
        {"stage_id": "self_evaluate", "required_input": "cycle evidence and readback", "required_output": "self-evaluation"},
        {"stage_id": "propose_next_milestone", "required_input": "self-evaluation", "required_output": NEXT_MILESTONE},
    ]


def build_internal_company_cycle_model() -> dict[str, Any]:
    rules = [
        "external actions must be blocked",
        "pending_owner_decision is not approval",
        "CEO brain cannot execute directly",
        "action must pass authorization before dry-run execution",
        "every executed dry-run action must produce evidence",
        "evidence must be read back by CEO brain",
        "cycle must produce next milestone proposal",
    ]
    return {
        "artifact_id": "e56_internal_company_loop_model",
        "model_status": "valid",
        "cycle_id": E56_CYCLE_ID,
        "current_state": current_state_summary(),
        "stages": cycle_stages(),
        "rules": rules,
        "external_action_allowed": False,
        "owner_decision_status": OWNER_STATUS,
        "no_external_action": True,
    }


def build_cycle_shell() -> dict[str, Any]:
    return asdict(InternalCompanyCycle(
        cycle_id=E56_CYCLE_ID,
        trigger="E55 behavior center L5 completed and recommended E56 internal loop proof.",
        mission_context="Prove CEO Brain L5 plus Behavior Center L5 can run a complete internal company operating cycle.",
        current_state=current_state_summary(),
        interpreted_task="Run one internal dry-run company loop without external contact or owner-approval fabrication.",
        candidate_actions=[],
        counterfactual_comparison={},
        selected_action=SELECTED_ACTION,
        behavior_queue_item={},
        authorization_result={},
        execution_envelope={},
        execution_result={},
        evidence_packet={},
        KG_update="operations/knowledge_graph/e56_ceo_kg_read_model_update.json",
        CZL_closure="operations/external_validation/e56_czl_closure.json",
        CIEU_residual="operations/external_validation/e56_cieu_residual_summary.json",
        brain_readback={},
        self_evaluation={},
        next_milestone_proposal=NEXT_MILESTONE,
        no_external_action=True,
    ))


def write_internal_company_loop_model(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_internal_company_cycle_model()
    write_json(root, "operations/external_validation/e56_internal_company_loop_model.json", data)
    write_md(root, "reports/integration/e56_internal_company_loop_model.md", "E56 Internal Company Loop Model", [
        f"Model status: `{data['model_status']}`",
        f"Cycle stages: `{len(data['stages'])}`",
        "External action allowed: `false`",
    ])
    return data

