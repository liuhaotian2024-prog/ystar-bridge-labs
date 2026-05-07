import json
from pathlib import Path

from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e83_autoguidance_semantics_readback import (
    REQUIRED_ARTIFACTS,
    build_correct_semantics,
    build_l4_l5_design,
    generate_e83_artifacts,
    load_e83_autoguidance_state_for_brain,
)


ROOT = Path(__file__).resolve().parents[2]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_e83_required_artifacts_exist_and_are_generated():
    generate_e83_artifacts()

    for rel in REQUIRED_ARTIFACTS:
        assert (ROOT / rel).exists(), rel


def test_topology_and_lineage_identify_repository_discovered_require_revision():
    topology = load("operations/external_validation/e83_ystar_gov_full_topology_audit.json")
    lineage = load("operations/external_validation/e83_auto_guidance_lineage_discovery.json")

    assert topology["selected_patch_target"] == "ystar/governance/ceo_cognitive_os_contract.py"
    assert topology["topology_node_count"] >= 6
    assert lineage["repository_discovered_correct_path_name"] == "REQUIRE_REVISION"
    assert any("pre_u" in item["mechanism_id"] for item in lineage["mechanisms"])
    assert any(item["repo"] == "gov-mcp" for item in lineage["mechanisms"])


def test_correct_semantics_distinguish_revision_deny_and_escalate():
    semantics = build_correct_semantics()["final_decision_semantics"]

    assert "missing counterfactual comparison" in semantics["REQUIRE_REVISION"]["when"]
    assert "hard boundary violation" in semantics["DENY"]["when"]
    assert "L4/external execution has pending owner approval" in semantics["ESCALATE"]["when"]
    assert semantics["STATUS_ONLY"]["runtime_decision"] is False


def test_e82_semantics_audit_records_patch_and_no_parallel_governance_engine():
    audit = load("operations/external_validation/e83_e82_cognitive_os_semantics_audit.json")

    assert audit["E82_semantics_audit_decision"] == "correct_but_needs_auto_guidance_semantics"
    assert audit["validator_patched"] is True
    assert audit["patch_result"] == "implemented_REQUIRE_REVISION_guidance"
    assert audit["no_parallel_governance_engine"] is True


def test_l4_l5_design_uses_autoguidance_without_execution_or_l5_claim():
    design = build_l4_l5_design()

    assert design["L4_flow"]["pre_action_packet_missing_cognitive_requirements"].startswith("REQUIRE_REVISION")
    assert design["L4_flow"]["complete_but_owner_approval_pending"].startswith("ESCALATE")
    assert design["L4_flow"]["mass_outreach_publication_payment_login_scraping"] == "DENY"
    assert design["L4_flow"]["L4_execution_status_in_E83"] == "not_executed"
    assert design["L5_flow"]["L5_readiness_status_in_E83"] == "not_ready"
    assert design["role_split"]["gov_mcp"].startswith("later governed provider")


def test_completion_report_has_no_forbidden_claims_or_read_only_repo_mutation():
    completion = load("operations/external_validation/e83_completion_report.json")
    safety = completion["safety_statement"]

    assert safety["no_external_action"] is True
    assert safety["no_customer_validation_claim"] is True
    assert safety["no_paid_signal_claim"] is True
    assert safety["no_pricing_validation_claim"] is True
    assert safety["no_compliance_legal_claim"] is True
    assert safety["no_production_deployment_claim"] is True
    assert safety["no_L4_execution_claim"] is True
    assert safety["no_L5_readiness_claim"] is True
    assert safety["no_K9Audit_or_gov_mcp_mutation"] is True
    assert safety["no_parallel_Y_star_gov_governance_engine"] is True


def test_ceo_brain_readback_reports_e83_autoguidance_state():
    readback = load_e83_autoguidance_state_for_brain()
    context = load_ceo_brain_context({"task_title": "E83 readback", "task_description": "auto-guidance"})

    assert readback["Y_star_gov_validator_supports_correct_path_guidance"] is True
    assert "REQUIRE_REVISION" in context["current_e83_actual_decision_vocabulary"]
    assert context["current_e83_L4_execution_authorized"] is False
    assert context["current_e83_L5_ready"] is False
