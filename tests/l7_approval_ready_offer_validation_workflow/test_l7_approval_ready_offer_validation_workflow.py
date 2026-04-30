import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "l7_approval_ready_offer_validation_workflow"


def load_json(relative_path: str):
    path = OUT / relative_path
    assert path.exists(), f"missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_l7_3_summary_and_selected_cash_path_exist():
    summary = load_json("l7_3_summary.json")
    selected = load_json("selected_cash_path/selected_cash_path.json")

    assert summary["selected_offer"] == "Founder AI Workflow Audit & CEO Command Brief Sprint"
    assert summary["selected_cash_path"] == "path_001"
    assert selected["path_id"] == "path_001"
    assert selected["first_possible_paid_offer"]


def test_service_offer_and_target_customer_exist():
    offer = load_json("service_offer_definition/service_offer_definition.json")
    profile = load_json("target_customer_selection/target_customer_profile.json")
    criteria = load_json("target_customer_selection/customer_discovery_criteria.json")

    assert offer["offer_name"] == "Founder AI Workflow Audit & CEO Command Brief Sprint"
    assert "AI startup founder" in profile["buyer_persona"]
    assert criteria["contact_status"] == "blocked_until_human_approved"
    assert offer["approval_required_before_external_claims"] is True


def test_outreach_generator_and_drafts_are_approval_gated():
    spec = load_json("approval_ready_outreach_generator/outreach_generator_spec.json")
    draft_paths = sorted((OUT / "outreach_draft_packets").glob("*.json"))
    drafts = [json.loads(path.read_text(encoding="utf-8")) for path in draft_paths]

    assert spec["no_auto_send"] is True
    assert len(drafts) >= 3
    assert all(draft["forbidden_auto_send"] is True for draft in drafts)
    assert all(draft["human_approval_required"] is True for draft in drafts)
    assert all(draft["external_action_status"] == "blocked_until_human_approved" for draft in drafts)


def test_human_approval_request_and_execution_preflight_block_execution():
    approval = load_json("human_approval_request/l7_3_outreach_approval_request.json")
    preflight = load_json("execution_preflight/outreach_execution_preflight.json")

    assert approval["default_decision"] == "blocked_until_human_approved"
    assert approval["approval_granted"] is False
    assert "approve_one_draft_for_manual_send" in approval["approval_options"]
    assert preflight["execution_allowed"] is False
    assert preflight["reason"] == "human_approval_not_yet_granted"


def test_service_delivery_workflow_and_templates_exist():
    workflow = load_json("service_delivery_workflow/service_delivery_workflow.json")
    intake = load_json("customer_intake_template/customer_intake_form_template.json")
    observation = load_json("governed_observation_delivery_template/governed_observation_delivery_template.json")
    brief = load_json("ceo_command_brief_delivery_template/ceo_command_brief_delivery_template.json")
    audit = load_json("workflow_audit_template/workflow_audit_template.json")

    assert len(workflow["steps"]) == 11
    assert intake["template_only"] is True
    assert observation["customer_observation_executed"] is False
    assert len(brief["sections"]) >= 8
    assert len(audit["audit_dimensions"]) >= 9


def test_pricing_quality_feedback_and_risk_boundaries_exist():
    pricing = load_json("pricing_and_payment_hypothesis/pricing_hypothesis.json")
    quality = load_json("service_quality_checklist/service_quality_checklist.json")
    feedback_questions = load_json("customer_feedback_loop/feedback_questions.json")
    feedback_rubric = load_json("customer_feedback_loop/feedback_scoring_rubric.json")
    risk = load_json("risk_and_claim_boundary/risk_register.json")
    claim = load_json("risk_and_claim_boundary/claim_boundary.json")

    assert pricing["payment_execution_status"] == "not_allowed_in_this_sprint"
    assert pricing["human_approval_required_before_quoting_externally"] is True
    assert len(quality["checks"]) >= 8
    assert feedback_questions["customer_contact_status"] == "not_contacted"
    assert "willingness_to_pay" in feedback_rubric["score_dimensions"]
    assert risk["risks"]
    assert "Guaranteed revenue" in claim["must_not_be_claimed"]


def test_memory_writeback_candidates_are_dry_run_only():
    candidates = load_json("memory_writeback_dry_run/l7_3_memory_writeback_candidates.json")
    receipt = load_json("memory_writeback_dry_run/l7_3_writeback_no_action_receipt.json")

    assert candidates["candidates"]
    assert all(candidate["dry_run_only"] is True for candidate in candidates["candidates"])
    assert all(candidate["default_decision"] == "blocked_until_human_approved" for candidate in candidates["candidates"])
    assert receipt["actual_writeback_occurred"] is False


def test_owner_review_packet_exists_and_is_plain():
    packet = load_json("owner_review_packet/l7_3_owner_review_packet.json")
    markdown = (OUT / "owner_review_packet/l7_3_owner_review_packet.md").read_text(encoding="utf-8")

    assert packet["first_offer"] == "Founder AI Workflow Audit & CEO Command Brief Sprint"
    assert packet["recommended_outreach_draft"] == "outreach_draft_001"
    assert "What is the first offer?" in markdown
    assert "What do I need to approve?" in markdown
    assert "What remains blocked?" in markdown


def test_no_action_receipt_blocks_external_side_effects_and_core_writeback():
    summary = load_json("l7_3_summary.json")
    receipt = load_json("l7_3_no_action_receipt/l7_3_no_action_receipt.json")

    assert summary["ask_user_url_occurred"] is False
    assert summary["external_side_effects_occurred"] is False
    assert summary["customer_contacted"] is False
    assert summary["email_sent"] is False
    assert summary["form_submitted"] is False
    assert summary["payment_occurred"] is False
    assert summary["publication_occurred"] is False
    assert summary["core_writeback_occurred"] is False

    assert receipt["outreach_occurred"] is False
    assert receipt["email_sent_occurred"] is False
    assert receipt["form_submission_occurred"] is False
    assert receipt["publication_occurred"] is False
    assert receipt["payment_occurred"] is False
    assert receipt["customer_contact_occurred"] is False
    assert receipt["actual_memory_brain_canonical_cieu_db_writeback_occurred"] is False
    assert receipt["ask_user_url_occurred"] is False


def test_no_secret_serialization_in_l7_3_outputs():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in OUT.rglob("*") if path.is_file())
    forbidden_patterns = [
        r"tvly-[A-Za-z0-9_\-]{12,}",
        r"(?i)bearer\s+[A-Za-z0-9_\-.]{20,}",
        r"(?i)(TAVILY_API_KEY|BRAVE_SEARCH_API_KEY|SERPAPI_API_KEY)\s*=\s*[^<\s][^\n]{8,}",
    ]
    for pattern in forbidden_patterns:
        assert re.search(pattern, combined) is None


def test_runner_exists_and_next_command_is_deterministic():
    runner = ROOT / "scripts/run_l7_3_offer_validation_workflow.sh"
    summary = load_json("l7_3_summary.json")

    assert runner.exists()
    assert summary["next_one_command_action"] == "bash scripts/run_l7_3_offer_validation_workflow.sh --mode build"
    assert summary["execution_allowed"] is False
