from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "cross_repo_governance_contract_proof"
    / "tools"
    / "build_cross_repo_governance_contract_proof.py"
)

REQUIRED_DIRECTORIES = [
    "cross_repo_governance_contract_proof",
    "y_star_gov_contract_surface_inventory",
    "ystar_company_to_y_star_gov_alignment",
    "gov_mcp_boundary_inventory",
    "governed_mcp_interface_contract",
    "cross_repo_non_bypass_proof",
    "cross_repo_gap_and_readiness",
]

REQUIRED_FILES = [
    "cross_repo_governance_contract_proof/README.md",
    "cross_repo_governance_contract_proof/tools/build_cross_repo_governance_contract_proof.py",
    "cross_repo_governance_contract_proof/cross_repo_contract_proof_contract.json",
    "cross_repo_governance_contract_proof/cross_repo_contract_proof_input_fixture.json",
    "cross_repo_governance_contract_proof/cross_repo_contract_proof_run.json",
    "cross_repo_governance_contract_proof/cross_repo_contract_proof_summary.json",
    "cross_repo_governance_contract_proof/cross_repo_contract_proof_report.md",
    "y_star_gov_contract_surface_inventory/y_star_gov_readonly_scan_manifest.json",
    "y_star_gov_contract_surface_inventory/y_star_gov_contract_surface_inventory.json",
    "y_star_gov_contract_surface_inventory/y_star_gov_validator_expectation_map.json",
    "y_star_gov_contract_surface_inventory/y_star_gov_adapter_expectation_map.json",
    "y_star_gov_contract_surface_inventory/y_star_gov_prediction_delta_expectation_map.json",
    "y_star_gov_contract_surface_inventory/y_star_gov_surface_gap_report.md",
    "y_star_gov_contract_surface_inventory/y_star_gov_surface_summary.json",
    "ystar_company_to_y_star_gov_alignment/behavior_y_star_to_governance_contract_map.json",
    "ystar_company_to_y_star_gov_alignment/pre_u_candidate_to_validator_expectation_map.json",
    "ystar_company_to_y_star_gov_alignment/cycle_gate_to_decision_envelope_map.json",
    "ystar_company_to_y_star_gov_alignment/cieu_fixture_to_prediction_delta_map.json",
    "ystar_company_to_y_star_gov_alignment/residual_delta_to_learning_eligibility_map.json",
    "ystar_company_to_y_star_gov_alignment/labs_vs_kernel_responsibility_boundary.json",
    "ystar_company_to_y_star_gov_alignment/ystar_company_to_y_star_gov_alignment_summary.json",
    "ystar_company_to_y_star_gov_alignment/ystar_company_to_y_star_gov_alignment_report.md",
    "gov_mcp_boundary_inventory/gov_mcp_readonly_scan_manifest.json",
    "gov_mcp_boundary_inventory/gov_mcp_boundary_surface_inventory.json",
    "gov_mcp_boundary_inventory/gov_mcp_tool_resource_boundary_map.json",
    "gov_mcp_boundary_inventory/gov_mcp_bypass_risk_inventory.json",
    "gov_mcp_boundary_inventory/gov_mcp_surface_gap_report.md",
    "gov_mcp_boundary_inventory/gov_mcp_surface_summary.json",
    "governed_mcp_interface_contract/governed_mcp_interface_contract.json",
    "governed_mcp_interface_contract/governed_mcp_call_lifecycle.md",
    "governed_mcp_interface_contract/mcp_call_pre_u_boundary_contract.json",
    "governed_mcp_interface_contract/mcp_call_cieu_receipt_contract.json",
    "governed_mcp_interface_contract/mcp_non_bypass_invariant_map.json",
    "governed_mcp_interface_contract/governed_mcp_interface_summary.json",
    "governed_mcp_interface_contract/governed_mcp_interface_report.md",
    "cross_repo_non_bypass_proof/cross_repo_non_bypass_invariant_map.json",
    "cross_repo_non_bypass_proof/cross_repo_action_path_lifecycle.json",
    "cross_repo_non_bypass_proof/forbidden_bypass_path_matrix.json",
    "cross_repo_non_bypass_proof/required_gate_sequence.json",
    "cross_repo_non_bypass_proof/cross_repo_non_bypass_gap_report.md",
    "cross_repo_non_bypass_proof/cross_repo_non_bypass_summary.json",
    "cross_repo_gap_and_readiness/cross_repo_alignment_gap_report.json",
    "cross_repo_gap_and_readiness/cross_repo_alignment_gap_report.md",
    "cross_repo_gap_and_readiness/cross_repo_governance_readiness.json",
    "cross_repo_gap_and_readiness/cross_repo_governance_readiness.md",
    "cross_repo_gap_and_readiness/l5_6_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_PROOF_STAGES = [
    "load_ystar_company_l5_artifacts",
    "inspect_y_star_gov_contract_surfaces_read_only",
    "inspect_gov_mcp_boundary_surfaces_read_only",
    "map_behavior_y_star_to_y_star_gov_contract_expectations",
    "map_pre_u_candidates_to_y_star_gov_validator_expectations",
    "map_residual_deltas_to_y_star_gov_prediction_delta_expectations",
    "map_bridge_gate_receipts_to_governance_decision_envelope_expectations",
    "map_gov_mcp_resources_to_governed_interface_boundary",
    "identify_bypass_risks",
    "produce_cross_repo_contract_alignment_matrix",
    "produce_non_bypass_invariant_map",
    "produce_cross_repo_gap_report",
    "produce_l5_6_recommendation",
]

REQUIRED_MCP_INVARIANTS = {
    "no_mcp_call_without_behavior_y_star",
    "no_mcp_call_without_pre_u_candidate",
    "no_mcp_call_without_governance_decision",
    "no_mcp_call_without_bridge_receipt",
    "no_mcp_call_without_cieu_receipt",
    "no_mcp_call_without_residual_delta",
    "no_mcp_call_with_direct_brain_writeback",
    "no_mcp_call_with_direct_memory_ingestion",
    "no_mcp_call_with_unapproved_external_action",
}

FALSE_FLAG_FIELDS = {
    "live_execution_enabled",
    "behavior_execution_enabled",
    "external_action_enabled",
    "network_enabled",
    "scheduler_enabled",
    "daemon_enabled",
    "cieu_persistence_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "candidate_auto_approval_enabled",
    "canonical_policy_mutation_enabled",
    "y_star_gov_modification_enabled",
    "gov_mcp_modification_enabled",
    "mcp_tool_execution_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "revenue_opportunity_discovery_enabled",
    "production_ready",
    "persistence_enabled",
    "db_write_performed",
    "modification_performed",
    "server_executed",
    "tool_executed",
    "mcp_server_or_tool_executed",
    "y_star_gov_modified",
    "gov_mcp_modified",
    "mcp_server_executed",
    "mcp_tool_executed",
    "candidate_approved",
    "candidate_applied",
    "ready_for_l6_revenue_opportunity_discovery",
}


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


@pytest.fixture(scope="module", autouse=True)
def generated_cross_repo_governance_contract_proof() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert result.returncode == 0, result.stdout + result.stderr


def load_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    assert path.exists(), f"missing file: {relative_path}"
    return json.loads(path.read_text(encoding="utf-8"))


def walk_json(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def assert_false_flags(document: Any) -> None:
    for node in walk_json(document):
        for field in FALSE_FLAG_FIELDS:
            if field in node:
                assert node[field] is False, f"{field} must remain false"


def test_required_l5_5_directories_and_files_exist() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir(), f"missing directory: {directory}"
    for relative_path in REQUIRED_FILES:
        assert (ROOT / relative_path).exists(), f"missing file: {relative_path}"


def test_all_required_json_artifacts_parse() -> None:
    for relative_path in JSON_FILES:
        load_json(relative_path)


def test_cross_repo_contract_contains_required_stages_and_disabled_flags() -> None:
    contract = load_json("cross_repo_governance_contract_proof/cross_repo_contract_proof_contract.json")
    assert contract["proof_stages"] == REQUIRED_PROOF_STAGES
    assert set(contract["involved_repos"]) == {"ystar-company", "Y-star-gov", "gov-mcp"}
    assert contract["repo_roles"]["Y-star-gov"] == "canonical deterministic governance kernel"
    assert contract["repo_roles"]["gov-mcp"] == "governed interface/resource/tool boundary"
    assert_false_flags(contract)


def test_readonly_manifests_record_present_or_missing_without_modification() -> None:
    y_manifest = load_json("y_star_gov_contract_surface_inventory/y_star_gov_readonly_scan_manifest.json")
    mcp_manifest = load_json("gov_mcp_boundary_inventory/gov_mcp_readonly_scan_manifest.json")
    for manifest in [y_manifest, mcp_manifest]:
        assert manifest["repo_status"] in {"present_read_only_scanned", "missing_repo"}
        assert "repo_present" in manifest
        assert manifest["modification_performed"] is False
        assert manifest["server_executed"] is False
        assert manifest["tool_executed"] is False


def test_no_artifact_claims_reference_repo_modification_or_mcp_execution() -> None:
    for relative_path in JSON_FILES:
        document = load_json(relative_path)
        assert_false_flags(document)


def test_company_to_y_star_gov_alignment_artifacts_exist_and_keep_kernel_boundary() -> None:
    behavior_map = load_json(
        "ystar_company_to_y_star_gov_alignment/behavior_y_star_to_governance_contract_map.json"
    )
    pre_u_map = load_json(
        "ystar_company_to_y_star_gov_alignment/pre_u_candidate_to_validator_expectation_map.json"
    )
    decision_map = load_json(
        "ystar_company_to_y_star_gov_alignment/cycle_gate_to_decision_envelope_map.json"
    )
    cieu_map = load_json("ystar_company_to_y_star_gov_alignment/cieu_fixture_to_prediction_delta_map.json")
    residual_map = load_json(
        "ystar_company_to_y_star_gov_alignment/residual_delta_to_learning_eligibility_map.json"
    )
    boundary = load_json("ystar_company_to_y_star_gov_alignment/labs_vs_kernel_responsibility_boundary.json")

    assert behavior_map["expected_governance_contract_concept"] == "declared_Y_star"
    assert pre_u_map["validator_status"] == "requires_future_Y_star_gov_or_versioned_adapter_validation"
    assert decision_map["labs_decision_authority"] == "dry_run_candidate_only"
    assert cieu_map["persistence_enabled"] is False
    assert residual_map["writeback_blocked"] is True
    assert boundary["ystar_company_must_not_be_treated_as_canonical_governance_kernel"] is True
    assert boundary["Y_star_gov_remains_intended_canonical_validator_decision_kernel"] is True


def test_gov_mcp_boundary_and_governed_interface_contracts_are_non_bypass() -> None:
    bypass = load_json("gov_mcp_boundary_inventory/gov_mcp_bypass_risk_inventory.json")
    contract = load_json("governed_mcp_interface_contract/governed_mcp_interface_contract.json")
    invariants = load_json("governed_mcp_interface_contract/mcp_non_bypass_invariant_map.json")

    assert bypass["risks_identified"] is True
    assert {item["risk_name"] for item in bypass["risks"]} >= {
        "direct tool bypass",
        "direct resource bypass",
        "ungoverned MCP call path",
    }
    rules = contract["contract_rules"]
    assert rules["future_mcp_call_downstream_of_behavior_y_star"] is True
    assert rules["future_mcp_call_requires_pre_u_candidate"] is True
    assert rules["future_mcp_call_requires_y_star_gov_or_versioned_adapter_validation"] is True
    assert rules["future_mcp_call_requires_bridge_or_gate_authorization"] is True
    assert rules["future_mcp_call_requires_receipt"] is True
    assert rules["future_mcp_call_requires_cieu_like_or_real_cieu_event"] is True
    assert rules["future_mcp_call_requires_residual_delta"] is True
    assert {item["invariant_id"] for item in invariants["invariants"]} == REQUIRED_MCP_INVARIANTS


def test_required_gate_sequence_and_forbidden_bypass_matrix() -> None:
    sequence = load_json("cross_repo_non_bypass_proof/required_gate_sequence.json")
    matrix = load_json("cross_repo_non_bypass_proof/forbidden_bypass_path_matrix.json")
    gate_names = [item["gate"] for item in sequence["sequence"]]
    assert gate_names[0] == "mission-level Y*"
    assert gate_names[-1] == "approved controlled update only if separately authorized"
    assert "behavior-level Y*" in gate_names
    assert "Pre-U packet" in gate_names
    assert "CIEU event" in gate_names
    forbidden = {item["path_name"]: item["status"] for item in matrix["paths"]}
    assert forbidden["candidate_U directly to MCP call"] == "forbidden"
    assert forbidden["MCP call directly to brain writeback"] == "forbidden"
    assert forbidden["MCP call directly to memory ingestion"] == "forbidden"


def test_readiness_keeps_l6_blocked_and_l5_6_ready() -> None:
    readiness = load_json("cross_repo_gap_and_readiness/cross_repo_governance_readiness.json")
    assert readiness["behavior_y_star_mapped_to_governance_contract"] is True
    assert readiness["pre_u_candidates_mapped_to_validator_expectations"] is True
    assert readiness["cieu_fixtures_mapped_to_prediction_delta_expectations"] is True
    assert readiness["gov_mcp_boundary_mapped"] is True
    assert readiness["non_bypass_invariants_defined"] is True
    assert readiness["bypass_risks_identified"] is True
    assert readiness["labs_kernel_responsibility_boundary_defined"] is True
    assert readiness["ready_for_l5_6_governed_mcp_dry_run_adapter"] is True
    assert readiness["ready_for_controlled_canonical_learning_design"] is True
    assert readiness["ready_for_l6_revenue_opportunity_discovery"] is False


def test_builder_static_safety_constraints() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "subprocess.run" not in source
    assert "requests." not in source
    assert "urllib.request" not in source
    assert ".open(" not in source


def test_console_read_model_integration_passes() -> None:
    loader = run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    assert loader.returncode == 0, loader.stdout + loader.stderr
    validator = run_command(["python3", "console_read_model/validation/validate_team_read_model.py"])
    assert validator.returncode == 0, validator.stdout + validator.stderr
    console = run_command(["python3", "console_read_model/cli/team_console.py", "cross-repo-governance"])
    assert console.returncode == 0, console.stdout + console.stderr
    assert "L5.5 cross-repo governance contract proof defined: True" in console.stdout
    assert "no MCP server/tool executed: True" in console.stdout
    assert "ready for L5.6 governed MCP dry-run adapter: True" in console.stdout
    assert "ready for L6 revenue opportunity discovery: False" in console.stdout
