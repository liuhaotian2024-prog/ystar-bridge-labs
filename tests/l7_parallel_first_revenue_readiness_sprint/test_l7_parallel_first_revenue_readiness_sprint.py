import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_json(relative_path: str):
    path = ROOT / relative_path
    assert path.exists(), f"missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_l7_4_summary_and_runner_exist():
    summary = load_json("l7_parallel_first_revenue_readiness_sprint/l7_4_summary.json")
    runner = ROOT / "scripts/run_l7_4_parallel_first_revenue_sprint.sh"

    assert runner.exists()
    assert summary["selected_offer"] == "Founder AI Workflow Audit & CEO Command Brief Sprint"
    assert summary["first_revenue_readiness_score"] >= 80
    assert summary["next_strategic_sprint"] == "L7.5 Human-Approved First Outreach Execution Preparation"


def test_all_six_lane_directories_exist():
    for directory in [
        "l7_target_customer_discovery_radar",
        "l7_human_approved_outreach_execution_pipeline",
        "l7_service_delivery_dry_run_fulfillment_kit",
        "l7_trust_proof_case_study_readiness",
        "l7_pricing_payment_contract_readiness",
        "l7_cockpit_v3_and_conservatism_batch",
    ]:
        assert (ROOT / directory).is_dir(), directory


def test_target_customer_discovery_has_no_private_live_contact_list():
    report = load_json("l7_target_customer_discovery_radar/read_only_customer_discovery_report.json")
    archetypes = load_json("l7_target_customer_discovery_radar/candidate_customer_archetypes.json")
    template = load_json("l7_target_customer_discovery_radar/no_contact_target_list_template.json")

    assert report["approval_required_before_contact"] is True
    assert report["real_web_observation_used"] is False
    assert len(archetypes["archetypes"]) >= 6
    assert template["contains_live_customer_contacts"] is False
    assert "private email" in template["forbidden_fields"]


def test_outreach_pipeline_exists_and_blocks_execution():
    gate = load_json("l7_human_approved_outreach_execution_pipeline/outreach_pre_send_gate.json")
    receipt_schema = load_json("l7_human_approved_outreach_execution_pipeline/post_outreach_receipt_schema.json")

    assert gate["execution_allowed"] is False
    assert gate["reason"] == "owner_has_not_approved_send"
    assert gate["actual_send"] == "blocked_until_explicit_approval"
    assert receipt_schema["required_after_any_future_approved_send"] is True


def test_service_delivery_dry_run_uses_fictional_sample_customer():
    dry_run = load_json("l7_service_delivery_dry_run_fulfillment_kit/service_delivery_dry_run.json")
    scenario = load_json("l7_service_delivery_dry_run_fulfillment_kit/sample_customer_scenario.json")
    work_order = load_json("l7_service_delivery_dry_run_fulfillment_kit/sample_governed_observation_work_order.json")

    assert dry_run["can_deliver_1500_pilot_with_current_tools"] is True
    assert scenario["fictional_sample_customer"] is True
    assert work_order["real_customer_observation"] is False
    assert work_order["budget"]["external_reads"] == 0


def test_trust_proof_pack_and_claim_boundaries_exist():
    trust = load_json("l7_trust_proof_case_study_readiness/trust_gap_analysis.json")
    not_allowed = load_json("l7_trust_proof_case_study_readiness/claims_not_allowed_yet.json")
    boundary = load_json("l7_trust_proof_case_study_readiness/credibility_claim_boundary.json")

    assert trust["trust_assets_available_now"]
    assert "guaranteed revenue" in not_allowed["claims_not_allowed_yet"]
    assert boundary["publication_allowed"] is False


def test_payment_contract_preflight_blocks_payment_and_contract_is_internal():
    pricing = load_json("l7_pricing_payment_contract_readiness/pricing_readiness_review.json")
    payment = load_json("l7_pricing_payment_contract_readiness/payment_execution_preflight.json")
    contract = (ROOT / "l7_pricing_payment_contract_readiness/contract_terms_draft_internal_only.md").read_text(encoding="utf-8")

    assert pricing["must_be_approved_before_quoting"] is True
    assert payment["payment_execution_allowed"] is False
    assert payment["reason"] == "no human approval and no customer commitment"
    assert "Internal Only" in contract


def test_owner_cockpit_v3_and_status_cards_exist():
    cockpit = load_json("l7_cockpit_v3_and_conservatism_batch/owner_cockpit_v3.json")
    first_revenue = load_json("l7_cockpit_v3_and_conservatism_batch/first_revenue_status_card.json")
    cash_path = load_json("l7_cockpit_v3_and_conservatism_batch/cash_path_status_card.json")

    assert cockpit["next_one_command_action"] == "bash scripts/run_l7_4_parallel_first_revenue_sprint.sh --mode status"
    assert first_revenue["ready_now"]
    assert cash_path["readiness_score"] == 82


def test_integration_manifest_and_lane_status_exist():
    status = load_json("l7_parallel_first_revenue_readiness_sprint/l7_4_lane_status.json")
    manifest = load_json("l7_parallel_first_revenue_readiness_sprint/l7_4_first_revenue_readiness_manifest.json")

    assert len(status["lanes"]) == 6
    assert all(row["status"] == "complete" for row in status["lanes"])
    assert manifest["target_customer_archetypes_generated"] >= 6
    assert manifest["approval_pipeline_ready"] is True
    assert manifest["delivery_dry_run_ready"] is True
    assert manifest["pricing_payment_contract_preflight_ready"] is True


def test_no_action_receipts_and_summary_block_side_effects():
    summary = load_json("l7_parallel_first_revenue_readiness_sprint/l7_4_summary.json")
    receipt = load_json("l7_parallel_first_revenue_readiness_sprint/l7_4_no_action_receipt.json")

    assert summary["execution_allowed"] is False
    assert summary["payment_execution_allowed"] is False
    assert summary["ask_user_url_occurred"] is False
    assert summary["external_side_effects_occurred"] is False
    assert summary["customer_contacted"] is False
    assert summary["email_sent"] is False
    assert summary["form_submitted"] is False
    assert summary["payment_occurred"] is False
    assert summary["publication_occurred"] is False
    assert summary["account_created"] is False
    assert summary["core_writeback_occurred"] is False

    assert receipt["email_sent_occurred"] is False
    assert receipt["customer_contact_occurred"] is False
    assert receipt["payment_occurred"] is False
    assert receipt["actual_memory_brain_canonical_cieu_db_writeback_occurred"] is False
    assert receipt["ask_user_url_occurred"] is False


def test_no_secret_serialization_in_l7_4_outputs():
    roots = [
        "l7_parallel_first_revenue_readiness_sprint",
        "l7_target_customer_discovery_radar",
        "l7_human_approved_outreach_execution_pipeline",
        "l7_service_delivery_dry_run_fulfillment_kit",
        "l7_trust_proof_case_study_readiness",
        "l7_pricing_payment_contract_readiness",
        "l7_cockpit_v3_and_conservatism_batch",
    ]
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for root in roots
        for path in (ROOT / root).rglob("*")
        if path.is_file()
    )
    forbidden_patterns = [
        r"tvly-[A-Za-z0-9_\-]{12,}",
        r"(?i)bearer\s+[A-Za-z0-9_\-.]{20,}",
        r"(?i)(TAVILY_API_KEY|BRAVE_SEARCH_API_KEY|SERPAPI_API_KEY)\s*=\s*[^<\s][^\n]{8,}",
    ]
    for pattern in forbidden_patterns:
        assert re.search(pattern, combined) is None


def test_outputs_are_deterministic_enough_for_tests():
    summary = load_json("l7_parallel_first_revenue_readiness_sprint/l7_4_summary.json")
    assert summary["generated_at_utc"] == "2026-04-30T00:00:00Z"
    assert summary["next_one_command_action"] == "bash scripts/run_l7_4_parallel_first_revenue_sprint.sh --mode status"
