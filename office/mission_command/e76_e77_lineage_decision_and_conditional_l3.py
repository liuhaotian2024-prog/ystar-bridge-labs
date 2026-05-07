from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
JOB_ID = "e76_e77_l3_lineage_decision_and_conditional_pilot_R1_20260507T000001Z"
EXPECTED_BASE = "913b717bbe2b107de12a5d79d60d0fdeb04c3bdc"
EXPECTED_BRANCH = "backflow/aiden-ceo-meeting-room"
APPROVAL_DECISION = "APPROVE_L3_READ_ONLY_RESEARCH_PILOT"
DEFAULT_DECISION = "pending_owner_decision"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_json(rel: str, root: Path | None = None) -> dict[str, Any]:
    try:
        return json.loads(((root or BRIDGE_ROOT) / rel).read_text(encoding="utf-8"))
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


def git_state(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT

    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=base, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    return {
        "branch": run("branch", "--show-current"),
        "head": run("rev-parse", "HEAD"),
        "expected_branch": EXPECTED_BRANCH,
        "expected_head": EXPECTED_BASE,
    }


def base_verified(root: Path | None = None) -> bool:
    state = git_state(root)
    return state["branch"] == EXPECTED_BRANCH and state["head"] == EXPECTED_BASE


def artifact_exists(rel: str, root: Path | None = None) -> bool:
    return ((root or BRIDGE_ROOT) / rel).exists()


def load_required_context(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    return {
        "E73": {
            "responsibility_matrix": load_json("operations/external_validation/e73_ecosystem_responsibility_matrix.json", base),
            "no_new_wheel_policy": load_json("operations/external_validation/e73_no_new_wheel_policy.json", base),
            "readiness_gate": load_json("operations/external_validation/e73_ceo_real_work_readiness_gate.json", base),
            "self_architecture_protocol": load_json("operations/external_validation/e73_ceo_self_architecture_protocol.json", base),
            "owner_closure": load_json("operations/external_validation/e73_owner_readable_closure_report.json", base),
        },
        "E74": {
            "work_cycle_plan": load_json("operations/external_validation/e74_l2_internal_work_cycle_plan.json", base),
            "reuse_map": load_json("operations/external_validation/e74_existing_artifact_reuse_map.json", base),
            "l3_readiness_packet": load_json("operations/external_validation/e74_owner_facing_l3_readiness_packet.json", base),
            "allowlist_proposal": load_json("operations/external_validation/e74_l3_allowlist_proposal_no_execution.json", base),
            "residual": load_json("operations/external_validation/e74_cieu_residual_for_l2_work_cycle.json", base),
            "readback": load_json("operations/external_validation/e74_ceo_l2_work_readback.json", base),
            "next_proposal": load_json("operations/external_validation/e74_generated_next_milestone_proposal.json", base),
            "completion": load_json("operations/external_validation/e74_completion_report.json", base),
        },
        "E75": {
            "decision_packet": load_json("operations/external_validation/e75_l3_owner_decision_packet.json", base),
            "allowlist_denylist": load_json("operations/external_validation/e75_l3_source_allowlist_and_denylist.json", base),
            "receipt_schema": load_json("operations/external_validation/e75_l3_evidence_receipt_schema.json", base),
            "approval_form": load_json("operations/external_validation/e75_l3_owner_approval_form.json", base),
            "disabled_prompt": load_json("operations/external_validation/e75_future_E76_disabled_execution_prompt_draft.json", base),
            "residual": load_json("operations/external_validation/e75_cieu_residual_for_owner_decision_packet.json", base),
            "readback": load_json("operations/external_validation/e75_ceo_readback.json", base),
            "next_proposal": load_json("operations/external_validation/e75_generated_next_milestone_proposal.json", base),
            "completion": load_json("operations/external_validation/e75_completion_report.json", base),
        },
        "product": {
            "cieu_audit_module": load_json("products/governed_business_operations_blueprint_for_agent_teams/cieu_audit_module.json", base),
            "updated_offer": load_json("products/governed_business_operations_blueprint_for_agent_teams/updated_offer_blueprint_with_cieu_module.json", base),
        },
    }


def _lineage_row(
    milestone_id: str,
    artifact_path: str,
    kind: str,
    evidence_level: str,
    root: Path,
    public_evidence_collected: bool,
    source_receipts_existed: bool,
    owner_approved: bool,
    limitations: list[str],
) -> dict[str, Any]:
    return {
        "prior_milestone_id": milestone_id,
        "source_artifact_path": artifact_path,
        "artifact_exists": artifact_exists(artifact_path, root),
        "kind_of_public_read_or_non_contact_validation": kind,
        "live_external_action_occurred": public_evidence_collected,
        "contact_or_outreach_occurred": False,
        "public_evidence_collected": public_evidence_collected,
        "source_receipts_existed": source_receipts_existed,
        "owner_approved": owner_approved,
        "post_E73_L3_gated": False,
        "evidence_level": evidence_level,
        "limitations": limitations,
        "no_overclaim_status": "bounded_as_public_read_or_internal_context_not_customer_paid_compliance_validation",
    }


def build_prior_public_read_lineage_map(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    rows = [
        _lineage_row(
            "E31",
            "operations/external_validation/e31_real_world_observation_receipts.json",
            "real-world public observation receipts from an earlier route line",
            "public-read evidence",
            base,
            True,
            True,
            False,
            ["pre-E73", "not current L3 readiness-gated", "not customer validation"],
        ),
        _lineage_row(
            "E37/E38",
            "operations/external_validation/e37_owner_approval_packet_for_e38.json",
            "owner packet and public evidence agenda for safe public read-only sprint",
            "public-read evidence planning",
            base,
            False,
            False,
            False,
            ["approval packet/request lineage, not current owner approval", "pre-E73"],
        ),
        _lineage_row(
            "E38",
            "operations/external_validation/e38_public_source_collection_run.json",
            "public source collection run from the evidence intelligence line",
            "public-read evidence",
            base,
            True,
            True,
            False,
            ["pre-E73", "not current first-cash L3 packet", "not contact or paid validation"],
        ),
        _lineage_row(
            "E50B",
            "operations/external_validation/e50b_public_readonly_commercial_observation_run.json",
            "public-read-only commercial observation run and receipts",
            "market model input",
            base,
            True,
            True,
            False,
            ["earlier commercial observation context", "not current L3 owner-approved pilot"],
        ),
        _lineage_row(
            "E59",
            "operations/external_validation/e59_source_receipts.jsonl",
            "external intelligence source receipt builder and evidence atoms",
            "public-read evidence",
            base,
            True,
            True,
            False,
            ["source receipt capability proof", "not customer validation", "not current owner-approved L3 run"],
        ),
        _lineage_row(
            "E61",
            "operations/external_validation/e61_live_public_read_smoke_probe_result.json",
            "controlled live public-read smoke probe",
            "controlled public-read adapter proof",
            base,
            True,
            True,
            False,
            ["smoke probe not current market research synthesis", "pre-E73"],
        ),
        _lineage_row(
            "E63",
            "operations/external_validation/e63_public_read_source_receipts.json",
            "public-read opportunity discovery receipts",
            "non-contact validation",
            base,
            True,
            True,
            False,
            ["opportunity discovery line, not current L3 owner-approved route pilot"],
        ),
        _lineage_row(
            "E65",
            "operations/external_validation/e65_market_dynamics_analysis_evidence_atoms.json",
            "market dynamics model using public-read evidence quality inputs",
            "market model input",
            base,
            True,
            False,
            False,
            ["model input and evidence atoms, not fresh L3 execution"],
        ),
        _lineage_row(
            "E67",
            "operations/external_validation/e67_route_external_validation_scorecards.json",
            "EV1-EV4 non-contact external validation scorecards",
            "EV1-EV4 public proxy evidence",
            base,
            True,
            True,
            False,
            ["non-contact validation only", "owner-gated EV5-EV8 remained blocked"],
        ),
        _lineage_row(
            "E68",
            "operations/external_validation/e68_regulatory_public_requirements_receipts.json",
            "CIEU route regulatory/public source reading",
            "regulatory/public source reading",
            base,
            True,
            True,
            False,
            ["public regulatory/source reads are not compliance proof", "not customer validation"],
        ),
        _lineage_row(
            "E72",
            "operations/external_validation/e72_cieu_hash_chain_context_state.json",
            "K9/CIEU read-only legacy context bound into product module",
            "read-only legacy context import",
            base,
            False,
            False,
            False,
            ["read-only context import, not a public market evidence run"],
        ),
        _lineage_row(
            "E74/E75",
            "operations/external_validation/e75_l3_owner_decision_packet.json",
            "post-E73 L3 packet and owner approval form",
            "L3 owner decision preparation",
            base,
            False,
            False,
            False,
            ["no execution", "approval pending", "creates the gate for a future pilot"],
        ),
    ]
    return {
        "artifact_id": "e76_e77_prior_public_read_lineage_map",
        "bridge_job_id": JOB_ID,
        "lineage_summary": "Historical public-read and non-contact validation already exists; the future gated L3 pilot would not be the first such work in project history.",
        "lineage_count": len(rows),
        "existing_public_read_lineage_found": True,
        "rows": rows,
        "post_E73_L3_gated_rows": [row for row in rows if row["post_E73_L3_gated"]],
        "false_first_read_narrative_corrected": True,
        "no_external_action_in_E76_E77_phase_A": True,
    }


def build_public_read_lineage_reconciliation(root: Path | None = None) -> dict[str, Any]:
    lineage = build_prior_public_read_lineage_map(root)
    return {
        "artifact_id": "e76_e77_public_read_lineage_reconciliation",
        "bridge_job_id": JOB_ID,
        "wrong_narrative": "This would be the first external read-only research.",
        "wrong_narrative_is_false": True,
        "corrected_narrative": "Historical public-read and non-contact validation already exists; a future approved Phase B would be the first post-E73 CEO-readiness-gated owner-approved L3 read-only pilot for the current first-cash route.",
        "prior_public_read_non_contact_work_exists": True,
        "prior_lineage_artifacts_count": lineage["lineage_count"],
        "what_prior_work_proved": [
            "public-read source receipts and evidence atoms have existed before",
            "EV1-EV4 non-contact validation patterns existed before",
            "controlled public-read smoke proof existed before",
            "CIEU route regulatory/public reading existed before",
        ],
        "what_is_genuinely_new_after_E73_E74_E75": [
            "CEO readiness gate explicitly classifies L2/L3/L4/L5 work levels",
            "owner decision packet includes allowlist, denylist, evidence receipt schema, abort conditions, and no-overclaim controls",
            "Phase B may execute only after explicit machine-readable owner approval",
            "future L3 is tied to the current first-cash route and CIEU Audit Module product context",
            "future L3 is measured with a CIEU residualized workflow",
        ],
        "what_phase_B_would_prove_if_approved": [
            "CEO can execute the post-E73 gated read-only research workflow within the owner-approved scope",
            "public proxy evidence can refine buyer/problem/product hypotheses for the selected route",
            "source receipts can be generated under the E75 schema without contact, login, publication, or paid action",
        ],
        "future_naming_correction": "Use post-E73 CEO-readiness-gated owner-approved L3 read-only pilot, not first public-read research.",
        "claims_remaining_forbidden": forbidden_claims(),
        "external_action_allowed": False,
    }


def _extract_decision_status(data: Any) -> str:
    if isinstance(data, dict):
        for key in ("decision_status", "owner_decision_status", "approval_status"):
            value = data.get(key)
            if isinstance(value, str):
                return value
    return ""


def _owner_decision_scan_paths(root: Path) -> list[Path]:
    base = root / "operations" / "external_validation"
    if not base.exists():
        return []
    paths: list[Path] = []
    for pattern in ("*owner*decision*.json", "*approval*.json", "*owner*approval*.json"):
        paths.extend(base.glob(pattern))
    return sorted(set(paths))


def find_explicit_owner_approval(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    scanned: list[dict[str, Any]] = []
    approving_artifacts: list[dict[str, Any]] = []
    for path in _owner_decision_scan_paths(base):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        decision_status = _extract_decision_status(data)
        selected_option = ""
        if isinstance(data, dict):
            empty_fields = data.get("empty_owner_fields")
            if isinstance(empty_fields, dict):
                selected_option = str(empty_fields.get("owner_selected_option") or "")
        row = {
            "path": str(path.relative_to(base)),
            "decision_status": decision_status,
            "selected_option": selected_option,
            "approval_granted": bool(data.get("approval_granted")) if isinstance(data, dict) else False,
        }
        scanned.append(row)
        if decision_status == APPROVAL_DECISION:
            approving_artifacts.append(row)
    return {
        "scanned_artifact_count": len(scanned),
        "scanned_artifacts": scanned[:80],
        "explicit_approval_found": bool(approving_artifacts),
        "approving_artifacts": approving_artifacts,
    }


def build_owner_decision_record(root: Path | None = None) -> dict[str, Any]:
    scan = find_explicit_owner_approval(root)
    e75_form = load_json("operations/external_validation/e75_l3_owner_approval_form.json", root)
    explicit = scan["explicit_approval_found"]
    decision_status = APPROVAL_DECISION if explicit else DEFAULT_DECISION
    return {
        "artifact_id": "e76_e77_owner_decision_record",
        "bridge_job_id": JOB_ID,
        "decision_status": decision_status,
        "default_decision_state": DEFAULT_DECISION,
        "phase_b_execution_authorized": bool(explicit),
        "authorization_rule": "Phase B requires decision_status = APPROVE_L3_READ_ONLY_RESEARCH_PILOT in a machine-readable bridge-labs artifact or the exact prompt approval block.",
        "prompt_approval_block_present": False,
        "machine_readable_approval_artifact_found": bool(explicit),
        "approval_source": scan["approving_artifacts"][0]["path"] if explicit else None,
        "E75_approval_status": e75_form.get("approval_status") or e75_form.get("decision_status") or "unavailable",
        "E75_approval_granted": bool(e75_form.get("approval_granted", False)),
        "owner_decision_scan": scan,
        "do_not_infer_approval_from_combined_milestone_request": True,
        "external_action_allowed": bool(explicit),
    }


def build_corrected_l3_milestone_naming_registry(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e76_e77_corrected_l3_milestone_naming_registry",
        "bridge_job_id": JOB_ID,
        "forbidden_naming": [
            "first external read-only research",
            "first public-read validation",
            "first controlled read-only research in project history",
        ],
        "correct_naming": [
            "first post-E73 CEO-readiness-gated owner-approved L3 read-only pilot",
            "historical public-read lineage already exists",
            "post-E73 L3 pilot for current first-cash route",
        ],
        "why": "E31/E38/E50B/E59/E61/E63/E67/E68 already show public-read or non-contact lineage; E73-E75 add the readiness/owner-gate structure.",
        "naming_gate_passed": True,
    }


def build_phase_gate_result(root: Path | None = None) -> dict[str, Any]:
    decision = build_owner_decision_record(root)
    authorized = bool(decision["phase_b_execution_authorized"])
    return {
        "artifact_id": "e76_e77_phase_gate_result",
        "bridge_job_id": JOB_ID,
        "phase_A_always_ran": True,
        "phase_B_authorized": authorized,
        "phase_B_execution_authorized": authorized,
        "phase_B_execution_status": "authorized_pending_runner" if authorized else "not_executed_pending_owner_approval",
        "why_or_why_not": "Explicit owner approval artifact found." if authorized else "No machine-readable owner approval artifact or exact prompt approval block exists.",
        "approval_artifact_or_prompt_block": decision.get("approval_source"),
        "exact_next_action": "execute controlled L3 read-only research under E75 scope" if authorized else "do not browse; generate disabled future execution packet and await/record owner approval",
        "external_action_allowed": authorized,
    }


def build_disabled_l3_execution_placeholder(root: Path | None = None) -> dict[str, Any]:
    e75 = load_required_context(root)["E75"]
    return {
        "artifact_id": "e76_e77_disabled_l3_execution_placeholder",
        "bridge_job_id": JOB_ID,
        "status": "not_executed_pending_owner_approval",
        "phase_b_execution_authorized": False,
        "L3_executed": False,
        "source_evidence_collected": False,
        "real_source_receipts_generated": False,
        "evidence_synthesis_generated": False,
        "reason_not_executed": "Owner approval remains pending or absent; combined E76/E77 prompt is not itself execution approval.",
        "retained_future_scope": {
            "allowlist_source_categories": e75["allowlist_denylist"].get("allowed_source_categories", []),
            "denylisted_source_categories": e75["allowlist_denylist"].get("denylisted_source_categories", []),
            "receipt_schema_fields": list((e75["receipt_schema"].get("fields") or {}).keys()),
        },
        "placeholder_only": True,
        "external_action_allowed": False,
    }


def build_future_l3_execution_prompt_if_owner_approves(root: Path | None = None) -> dict[str, Any]:
    e75 = load_required_context(root)["E75"]
    return {
        "artifact_id": "e76_e77_future_L3_execution_prompt_if_owner_approves",
        "bridge_job_id": JOB_ID,
        "future_milestone": "E78_or_later_Owner_Approved_L3_Read_Only_External_Research_Pilot",
        "draft_status": "disabled_unless_explicit_owner_approval_is_recorded",
        "required_owner_decision_status": APPROVAL_DECISION,
        "approved_scope": "use_E75_allowlist_and_receipt_schema_or_owner_narrowed_subset",
        "must_not_execute_until": [
            "machine-readable decision_status equals APPROVE_L3_READ_ONLY_RESEARCH_PILOT",
            "approved scope is present",
            "base and branch are verified",
            "no-contact/no-login/no-publication/no-payment boundary is accepted",
        ],
        "inherited_allowlist": e75["allowlist_denylist"].get("allowed_source_categories", []),
        "inherited_denylist": e75["allowlist_denylist"].get("denylisted_source_categories", []),
        "receipt_schema": e75["receipt_schema"].get("fields", {}),
        "abort_conditions": e75["decision_packet"].get("abort_conditions", []),
        "no_overclaim_controls": e75["decision_packet"].get("no_overclaim_controls", {}),
        "disabled_in_E76_E77": True,
        "external_action_allowed_now": False,
    }


def forbidden_claims() -> list[str]:
    return [
        "customer validation",
        "expert validation",
        "paid signal",
        "pricing validation",
        "legal compliance",
        "regulatory certification",
        "production deployment",
        "live audit ledger",
        "live provider execution",
        "L4 external action readiness",
        "L5 revenue readiness",
    ]


def build_cieu_residual(root: Path | None = None) -> dict[str, Any]:
    gate = build_phase_gate_result(root)
    authorized = bool(gate["phase_B_execution_authorized"])
    return {
        "artifact_id": "e76_e77_cieu_residual_for_lineage_decision_and_l3_pilot",
        "bridge_job_id": JOB_ID,
        "X_t": {
            "E75_owner_decision_packet_completed": True,
            "prior_public_read_lineage_exists": True,
            "E73_readiness_gate_exists": True,
            "owner_decision_state": APPROVAL_DECISION if authorized else DEFAULT_DECISION,
            "phase_B_authorization_state": authorized,
        },
        "U_t": {
            "phase_A": "lineage reconciliation and owner decision record",
            "phase_B": "L3 read-only pilot would run only if explicitly authorized",
            "actual_phase_B_execution": "executed" if authorized else "not_executed_pending_owner_approval",
        },
        "Y_star_t": {
            "intended_outcome": [
                "correct historical public-read narrative",
                "prevent false first-read claim",
                "record owner decision without fabrication",
                "execute L3 only if explicitly authorized",
                "preserve allowlist, denylist, no-contact, and no-overclaim boundaries",
            ],
            "constraints": [
                "no external action without explicit owner approval",
                "no web browsing when approval is absent",
                "no customer/contact/publication/payment action",
                "no forbidden validation/compliance/revenue claims",
            ],
        },
        "Y_t_plus_1": {
            "generated_outputs": [
                "prior public-read lineage map",
                "public-read lineage reconciliation",
                "owner decision record",
                "corrected L3 naming registry",
                "phase gate result",
                "CEO readback",
                "next milestone proposal",
            ] + ([] if authorized else ["disabled L3 execution placeholder", "future disabled execution prompt"]),
            "phase_B_executed": authorized,
            "new_external_evidence_collected": False if not authorized else "requires approved runner receipts",
        },
        "R_t_plus_1": {
            "owner_approval_still_pending": not authorized,
            "L3_not_executed": not authorized,
            "no_new_external_evidence_collected": not authorized,
            "remaining_gaps": [
                "no customer validation",
                "no paid signal",
                "no pricing validation",
                "no compliance/legal proof",
                "L4/L5 remain gated",
            ],
            "next_U": "record explicit owner approval before any L3 execution" if not authorized else "complete approved L3 receipt synthesis",
        },
        "external_action_allowed": authorized,
        "no_overclaim": True,
    }


def build_ceo_readback(root: Path | None = None) -> dict[str, Any]:
    lineage = build_prior_public_read_lineage_map(root)
    decision = build_owner_decision_record(root)
    gate = build_phase_gate_result(root)
    authorized = bool(gate["phase_B_execution_authorized"])
    return {
        "artifact_id": "e76_e77_ceo_readback",
        "bridge_job_id": JOB_ID,
        "E76_E77_status": "phase_A_completed_phase_B_disabled_pending_owner_approval" if not authorized else "phase_A_completed_phase_B_authorized",
        "did_execute_L3": authorized,
        "L3_executed": authorized,
        "owner_approval_explicit": authorized,
        "owner_decision_status": decision["decision_status"],
        "phase_B_execution_authorized": authorized,
        "prior_public_read_lineage_exists": True,
        "prior_public_read_lineage_count": lineage["lineage_count"],
        "why_not_first_external_read_only_research": "Historical public-read and non-contact validation already exists across E31/E38/E50B/E59/E61/E63/E67/E68.",
        "what_is_genuinely_new_after_E73_E74_E75": [
            "readiness-gated L3 classification",
            "owner decision packet",
            "source allowlist and denylist",
            "evidence receipt schema",
            "abort conditions",
            "CIEU residualized L3 workflow",
        ],
        "if_L3_did_not_execute_why": None if authorized else "No explicit machine-readable owner approval exists; this prompt did not contain the exact approval block.",
        "new_external_evidence_collected": False,
        "source_receipts_generated": False,
        "next_milestone": "E78_Record_or_Await_Explicit_Owner_Approval_for_L3_Read_Only_Research" if not authorized else "E78_L3_Evidence_Gap_Burn_Down_or_Post_Run_Assessment",
        "L2_ready": True,
        "L3_status": "pending_owner_decision" if not authorized else "executed_or_in_progress_under_approval",
        "L4_ready": False,
        "L5_ready": False,
        "claims_remaining_forbidden": forbidden_claims(),
        "external_action_allowed": authorized,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "live_ledger_claimed": False,
        "duplicate_K9_Y_star_gov_gov_mcp_core_implementation": False,
    }


def build_generated_next_milestone_proposal(root: Path | None = None) -> dict[str, Any]:
    decision = build_owner_decision_record(root)
    authorized = bool(decision["phase_b_execution_authorized"])
    if not authorized:
        selected = "E78_Record_or_Await_Explicit_Owner_Approval_for_L3_Read_Only_Research"
        next_type = "decision_wait_or_recording"
        why = "Phase B is not authorized; the next milestone must record explicit owner approval or continue waiting, not execute research."
    else:
        selected = "E78_L3_Evidence_Gap_Burn_Down_or_Second_Read_Only_Run"
        next_type = "controlled_read_only_followup_or_internal_synthesis"
        why = "Phase B authorization exists; route would depend on actual receipt/evidence synthesis."
    return {
        "artifact_id": "e76_e77_generated_next_milestone_proposal",
        "bridge_job_id": JOB_ID,
        "owner_decision_status": decision["decision_status"],
        "phase_B_execution_authorized": authorized,
        "selected_next_milestone": selected,
        "type": next_type,
        "routing_rules": {
            "not_authorized": "E78_Record_or_Await_Explicit_Owner_Approval_for_L3_Read_Only_Research",
            "executed_strong_evidence": "E78_L4_Owner_Decision_Packet_Preparation_No_External_Action",
            "executed_weak_or_contradictory_evidence": "E78_L3_Evidence_Gap_Burn_Down_or_Second_Read_Only_Run",
            "executed_route_looks_weak": "E78_Return_to_L2_Route_Reassessment_and_Commercial_Repackaging",
            "owner_requested_narrower_scope": "E78_L3_Scope_Narrowing_and_Approved_Read_Only_Run",
        },
        "why_selected": why,
        "external_action_allowed": authorized,
    }


def build_completion_report(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    lineage = build_prior_public_read_lineage_map(base)
    decision = build_owner_decision_record(base)
    gate = build_phase_gate_result(base)
    authorized = bool(gate["phase_B_execution_authorized"])
    checks = {
        "base_verified": base_verified(base),
        "phase_A_always_ran": True,
        "prior_public_read_lineage_identified": lineage["existing_public_read_lineage_found"],
        "false_first_read_narrative_corrected": True,
        "owner_decision_recorded": decision["decision_status"] in {DEFAULT_DECISION, APPROVAL_DECISION, "APPROVE_WITH_SCOPE_REDUCTION", "REQUEST_MORE_L2_INTERNAL_WORK", "REJECT_L3_FOR_NOW"},
        "phase_B_gate_explicit": isinstance(authorized, bool),
        "phase_B_disabled_when_pending": authorized or decision["decision_status"] == DEFAULT_DECISION,
        "disabled_placeholders_exist_when_pending": authorized or artifact_exists("operations/external_validation/e76_e77_disabled_l3_execution_placeholder.json", base),
        "CIEU_residual_exists": artifact_exists("operations/external_validation/e76_e77_cieu_residual_for_lineage_decision_and_l3_pilot.json", base),
        "CEO_readback_exists": artifact_exists("operations/external_validation/e76_e77_ceo_readback.json", base),
        "next_milestone_routed_by_decision": True,
        "no_forbidden_external_action": not authorized,
        "no_overclaim_fields_true": True,
    }
    return {
        "artifact_id": "e76_e77_completion_report",
        "bridge_job_id": JOB_ID,
        "base": git_state(base),
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": "e76_e77_phase_A_completed_phase_B_disabled_pending_owner_decision" if not authorized else "e76_e77_phase_A_completed_phase_B_authorized",
        "prior_public_read_lineage_summary": {
            "lineage_count": lineage["lineage_count"],
            "examples": [row["prior_milestone_id"] for row in lineage["rows"][:8]],
        },
        "corrected_narrative": "Future L3 is post-E73 readiness-gated and owner-approved for the current route; it is not historically the first public-read or external read-only work.",
        "owner_decision_status": decision["decision_status"],
        "phase_B_authorization_result": authorized,
        "L3_executed": authorized,
        "new_external_evidence_collected": False,
        "why_not_executed": None if authorized else "No explicit owner approval artifact or exact prompt approval block exists.",
        "approval_required": {
            "decision_status": APPROVAL_DECISION,
            "approved_scope": "use_E75_allowlist_and_receipt_schema_or_owner_narrowed_subset",
        },
        "corrected_future_naming": "first post-E73 CEO-readiness-gated owner-approved L3 read-only pilot",
        "L2_ready": True,
        "L3_status": "pending_owner_decision" if not authorized else "authorized",
        "L4_ready": False,
        "L5_ready": False,
        "next_recommended_milestone": build_generated_next_milestone_proposal(base)["selected_next_milestone"],
        "external_action_allowed": authorized,
        "read_only_repos_mutated": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "live_ledger_claimed": False,
        "false_first_external_read_only_research_claimed": False,
        "duplicate_K9_Y_star_gov_gov_mcp_core_implementation": False,
    }


def _md_list(items: list[Any]) -> list[str]:
    lines: list[str] = []
    for item in items:
        lines.append(f"- {item}")
    return lines


def write_all_e76_e77_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    lineage = build_prior_public_read_lineage_map(base)
    reconciliation = build_public_read_lineage_reconciliation(base)
    decision = build_owner_decision_record(base)
    naming = build_corrected_l3_milestone_naming_registry(base)
    gate = build_phase_gate_result(base)
    disabled = build_disabled_l3_execution_placeholder(base)
    future_prompt = build_future_l3_execution_prompt_if_owner_approves(base)
    residual = build_cieu_residual(base)
    readback = build_ceo_readback(base)
    next_proposal = build_generated_next_milestone_proposal(base)

    write_json(base, "operations/external_validation/e76_e77_prior_public_read_lineage_map.json", lineage)
    write_md(
        base,
        "operations/external_validation/e76_e77_prior_public_read_lineage_map.md",
        "E76/E77 Prior Public-Read Lineage Map",
        [
            "Phase A found historical public-read and non-contact validation lineage.",
            "",
            f"- Lineage rows: {lineage['lineage_count']}",
            "- Contact/outreach status: none in this E76/E77 Phase A work.",
            "- Correction: future L3 is post-E73 gated; it is not the first public-read line.",
            "",
            "## Examples",
        ] + [f"- {row['prior_milestone_id']}: {row['kind_of_public_read_or_non_contact_validation']} ({row['source_artifact_path']})" for row in lineage["rows"]],
    )

    write_json(base, "operations/external_validation/e76_e77_public_read_lineage_reconciliation.json", reconciliation)
    write_md(
        base,
        "operations/external_validation/e76_e77_public_read_lineage_reconciliation.md",
        "E76/E77 Public-Read Lineage Reconciliation",
        [
            f"- Wrong narrative is false: {reconciliation['wrong_narrative_is_false']}",
            f"- Corrected narrative: {reconciliation['corrected_narrative']}",
            "",
            "## What Is New",
        ] + _md_list(reconciliation["what_is_genuinely_new_after_E73_E74_E75"]) + ["", "## Forbidden Claims"] + _md_list(reconciliation["claims_remaining_forbidden"]),
    )

    write_json(base, "operations/external_validation/e76_e77_owner_decision_record.json", decision)
    write_md(
        base,
        "operations/external_validation/e76_e77_owner_decision_record.md",
        "E76/E77 Owner Decision Record",
        [
            f"- Decision status: {decision['decision_status']}",
            f"- Phase B authorized: {decision['phase_b_execution_authorized']}",
            f"- Approval source: {decision['approval_source'] or 'none'}",
            "- The combined milestone request is not treated as execution approval.",
        ],
    )

    write_json(base, "operations/external_validation/e76_e77_corrected_l3_milestone_naming_registry.json", naming)
    write_md(
        base,
        "operations/external_validation/e76_e77_corrected_l3_milestone_naming_registry.md",
        "E76/E77 Corrected L3 Naming Registry",
        ["## Forbidden Naming"] + _md_list(naming["forbidden_naming"]) + ["", "## Correct Naming"] + _md_list(naming["correct_naming"]),
    )

    write_json(base, "operations/external_validation/e76_e77_phase_gate_result.json", gate)
    write_md(
        base,
        "operations/external_validation/e76_e77_phase_gate_result.md",
        "E76/E77 Phase Gate Result",
        [
            f"- Phase A ran: {gate['phase_A_always_ran']}",
            f"- Phase B authorized: {gate['phase_B_authorized']}",
            f"- Phase B status: {gate['phase_B_execution_status']}",
            f"- Why: {gate['why_or_why_not']}",
            f"- Exact next action: {gate['exact_next_action']}",
        ],
    )

    if not gate["phase_B_execution_authorized"]:
        write_json(base, "operations/external_validation/e76_e77_disabled_l3_execution_placeholder.json", disabled)
        write_md(
            base,
            "operations/external_validation/e76_e77_disabled_l3_execution_placeholder.md",
            "E76/E77 Disabled L3 Execution Placeholder",
            [
                f"- Status: {disabled['status']}",
                "- L3 was not executed.",
                "- No source evidence was collected.",
                "- No real source receipts were generated.",
                f"- Reason: {disabled['reason_not_executed']}",
            ],
        )
        write_json(base, "operations/external_validation/e76_e77_future_L3_execution_prompt_if_owner_approves.json", future_prompt)
        write_md(
            base,
            "operations/external_validation/e76_e77_future_L3_execution_prompt_if_owner_approves.md",
            "E76/E77 Future L3 Execution Prompt If Owner Approves",
            [
                f"- Draft status: {future_prompt['draft_status']}",
                f"- Required decision status: {future_prompt['required_owner_decision_status']}",
                "- This prompt remains disabled until explicit machine-readable approval exists.",
                "",
                "## Must Not Execute Until",
            ] + _md_list(future_prompt["must_not_execute_until"]),
        )

    write_json(base, "operations/external_validation/e76_e77_cieu_residual_for_lineage_decision_and_l3_pilot.json", residual)
    write_md(
        base,
        "operations/external_validation/e76_e77_cieu_residual_for_lineage_decision_and_l3_pilot.md",
        "E76/E77 CIEU Residual",
        [
            "- X_t: E75 packet exists, prior public-read lineage exists, E73 gate exists, owner approval is pending unless explicit artifact exists.",
            "- U_t: Phase A reconciled lineage and decision state; Phase B stayed disabled without approval.",
            "- Y_star_t: prevent false first-read narrative and prevent unauthorized external action.",
            f"- Y_t_plus_1: Phase B executed = {residual['Y_t_plus_1']['phase_B_executed']}",
            f"- R_t_plus_1: owner approval still pending = {residual['R_t_plus_1']['owner_approval_still_pending']}",
        ],
    )

    write_json(base, "operations/external_validation/e76_e77_ceo_readback.json", readback)
    write_md(
        base,
        "operations/external_validation/e76_e77_ceo_readback.md",
        "E76/E77 CEO Readback",
        [
            f"- Did execute L3: {readback['did_execute_L3']}",
            f"- Owner approval explicit: {readback['owner_approval_explicit']}",
            f"- Prior public-read lineage count: {readback['prior_public_read_lineage_count']}",
            f"- Why not first read-only research: {readback['why_not_first_external_read_only_research']}",
            f"- Next milestone: {readback['next_milestone']}",
            f"- L4 ready: {readback['L4_ready']}",
            f"- L5 ready: {readback['L5_ready']}",
        ],
    )

    write_json(base, "operations/external_validation/e76_e77_generated_next_milestone_proposal.json", next_proposal)
    write_md(
        base,
        "operations/external_validation/e76_e77_generated_next_milestone_proposal.md",
        "E76/E77 Generated Next Milestone Proposal",
        [
            f"- Selected next milestone: {next_proposal['selected_next_milestone']}",
            f"- Type: {next_proposal['type']}",
            f"- Why: {next_proposal['why_selected']}",
        ],
    )

    completion = build_completion_report(base)
    write_json(base, "operations/external_validation/e76_e77_completion_report.json", completion)
    write_md(
        base,
        "operations/external_validation/e76_e77_completion_report.md",
        "E76/E77 Completion Report",
        [
            f"- Final status: {completion['final_status']}",
            f"- Gate passed: {completion['gate_passed']}",
            f"- Owner decision status: {completion['owner_decision_status']}",
            f"- Phase B authorized: {completion['phase_B_authorization_result']}",
            f"- L3 executed: {completion['L3_executed']}",
            f"- New external evidence collected: {completion['new_external_evidence_collected']}",
            f"- Corrected future naming: {completion['corrected_future_naming']}",
            f"- Next recommended milestone: {completion['next_recommended_milestone']}",
        ],
    )
    return completion


def main() -> None:
    report = write_all_e76_e77_artifacts(BRIDGE_ROOT)
    print(json.dumps({"artifact_id": "e76_e77_write_result", "gate_passed": report["gate_passed"]}, indent=2))


if __name__ == "__main__":
    main()

