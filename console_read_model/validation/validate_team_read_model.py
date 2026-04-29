#!/usr/bin/env python3
"""Static validator for curated team console/capsule read-model files.

This script intentionally reads only curated JSON/Markdown files listed in the
expected structure. It does not open DBs, logs, daemon state, active-agent
markers, or runtime stores.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = ROOT / "console_read_model" / "validation" / "expected_structure.json"


class Report:
    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: list[str] = []
        self.warnings: list[str] = []
        self.files_inspected: set[str] = set()
        self.schema_alignment = {
            "agent_brain_capsules_checked": 0,
            "brain_profiles_checked": 0,
            "ref_files_checked": 0,
            "execution_channel_files_checked": 0,
            "pre_u_packet_schemas_checked": 0,
        }

    def pass_(self, message: str) -> None:
        self.passed.append(message)

    def fail(self, message: str) -> None:
        self.failed.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def inspect(self, path: Path) -> None:
        try:
            self.files_inspected.add(str(path.relative_to(ROOT)))
        except ValueError:
            self.files_inspected.add(str(path))


def load_json(path: Path, report: Report) -> Any:
    report.inspect(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # pragma: no cover - surfaced in CLI report
        report.fail(f"JSON load failed: {path.relative_to(ROOT)} ({exc})")
        return None


def check_exists(path: Path, report: Report, label: str) -> None:
    if path.exists():
        report.pass_(f"{label} exists: {path.relative_to(ROOT)}")
    else:
        report.fail(f"{label} missing: {path.relative_to(ROOT)}")


def check_json_file(path: Path, report: Report, label: str) -> Any:
    check_exists(path, report, label)
    if not path.exists():
        return None
    data = load_json(path, report)
    if data is not None:
        report.pass_(f"{label} JSON valid: {path.relative_to(ROOT)}")
    return data


def is_non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def fail_field(report: Report, rel: str, field: str, message: str) -> None:
    report.fail(f"{rel}: {field}: {message}")


def warn_field(report: Report, rel: str, field: str, message: str) -> None:
    report.warn(f"{rel}: {field}: {message}")


def check_brain_profile_alignment(agent_id: str, path: Path, data: Any, report: Report) -> None:
    rel = str(path.relative_to(ROOT))
    report.schema_alignment["brain_profiles_checked"] += 1

    if not isinstance(data, dict):
        report.fail(f"{rel}: brain_profile top-level must be object")
        return

    required_fields = [
        "agent_id",
        "canonical_name",
        "aliases",
        "role_type",
        "capsule_version",
        "capsule_status",
        "source_registry_refs",
        "primary_layers",
        "db_content_opened",
        "scripts_run",
        "evidence_paths",
        "open_gaps",
    ]
    for field in required_fields:
        if field not in data:
            fail_field(report, rel, field, "missing required profile field")
        elif not is_non_empty(data[field]) and field not in {"db_content_opened", "scripts_run"}:
            fail_field(report, rel, field, "critical profile field is empty")

    if data.get("agent_id") != agent_id:
        fail_field(report, rel, "agent_id", f"expected {agent_id}, got {data.get('agent_id')}")

    if data.get("capsule_status") != "reference_only":
        fail_field(report, rel, "capsule_status", "reference capsules should remain reference_only")

    if data.get("db_content_opened") is not False:
        fail_field(report, rel, "db_content_opened", "must be false for reference capsules")

    if data.get("scripts_run") is not False:
        fail_field(report, rel, "scripts_run", "must be false for reference capsules")

    if not isinstance(data.get("aliases"), list):
        fail_field(report, rel, "aliases", "must be an array")

    if not isinstance(data.get("primary_layers"), list):
        fail_field(report, rel, "primary_layers", "must be an array")

    if "role_specific_focus" not in data:
        warn_field(
            report,
            rel,
            "role_specific_focus",
            "missing recommended shared-schema field; allowed for older Aiden v0 profile until migration",
        )
    elif not is_non_empty(data.get("role_specific_focus")):
        fail_field(report, rel, "role_specific_focus", "present but empty")

    report.pass_(f"brain profile schema-aligned: {rel}")


def check_ref_file_alignment(agent_id: str, path: Path, data: Any, report: Report) -> None:
    rel = str(path.relative_to(ROOT))
    report.schema_alignment["ref_files_checked"] += 1

    if not isinstance(data, (dict, list)):
        report.fail(f"{rel}: ref file top-level must be object or array")
        return

    if isinstance(data, list):
        if not data:
            report.fail(f"{rel}: ref file array must not be empty")
        report.pass_(f"ref file schema-aligned: {rel}")
        return

    if not data:
        report.fail(f"{rel}: ref file object must not be empty")
        return

    if data.get("agent_id") != agent_id:
        fail_field(report, rel, "agent_id", f"expected {agent_id}, got {data.get('agent_id')}")

    reference_arrays = [key for key in ("refs", "references", "stages") if key in data]
    if not reference_arrays:
        report.fail(f"{rel}: expected one of refs, references, or stages")
        return

    for key in reference_arrays:
        value = data.get(key)
        if not isinstance(value, list) or not value:
            fail_field(report, rel, key, "must be a non-empty array")
            continue
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                fail_field(report, rel, f"{key}[{index}]", "must be an object")
                continue
            if key in {"refs", "references"} and not is_non_empty(item.get("path")):
                fail_field(report, rel, f"{key}[{index}].path", "reference entry must include a path")
            if key == "stages" and not is_non_empty(item.get("references")):
                fail_field(report, rel, f"{key}[{index}].references", "stage entry must include references")

    report.pass_(f"ref file schema-aligned: {rel}")


def check_execution_channels_alignment(agent_id: str, path: Path, data: Any, report: Report) -> None:
    rel = str(path.relative_to(ROOT))
    report.schema_alignment["execution_channel_files_checked"] += 1

    if not isinstance(data, dict):
        report.fail(f"{rel}: execution channels top-level must be object")
        return

    for field in [
        "agent_id",
        "identity_boundary",
        "canonical_identity_location",
        "execution_channels",
        "delegation_requirements",
        "evidence_return_policy",
        "prohibited_interpretations",
        "open_gaps",
    ]:
        if not is_non_empty(data.get(field)):
            fail_field(report, rel, field, "missing or empty execution-channel field")

    if data.get("agent_id") != agent_id:
        fail_field(report, rel, "agent_id", f"expected {agent_id}, got {data.get('agent_id')}")

    for index, channel in enumerate(data.get("execution_channels", [])):
        if not isinstance(channel, dict):
            fail_field(report, rel, f"execution_channels[{index}]", "must be object")
            continue
        if channel.get("owns_identity") is not False:
            fail_field(report, rel, f"execution_channels[{index}].owns_identity", "execution substrates must not own identity")

    report.pass_(f"execution channels schema-aligned: {rel}")


def check_pre_u_packet_schema_alignment(path: Path, data: Any, report: Report) -> None:
    rel = str(path.relative_to(ROOT))
    report.schema_alignment["pre_u_packet_schemas_checked"] += 1

    if not isinstance(data, dict):
        report.fail(f"{rel}: Pre-U packet schema top-level must be object")
        return

    required = set(data.get("required", []))
    properties = data.get("properties", {})
    concepts = {
        "Y*": "y_star",
        "Xt": "x_t_summary",
        "m_functor": "m_functor",
        "candidate_U": "candidate_actions",
        "selected_U": "selected_action",
        "why_min_residual": "residual_minimization_rationale",
        "CIEU link policy": "cieu_link_policy",
    }
    for concept, field in concepts.items():
        if field not in required or field not in properties:
            fail_field(report, rel, concept, f"expected schema field {field}")

    candidate = properties.get("candidate_actions", {}).get("items", {})
    candidate_required = set(candidate.get("required", []))
    for concept, field in {
        "predicted_Yt+1": "predicted_y_t1",
        "predicted_Rt+1": "predicted_r_t1",
        "candidate_U_summary": "u_summary",
    }.items():
        if field not in candidate_required:
            fail_field(report, rel, concept, f"expected candidate action field {field}")

    selected = properties.get("selected_action", {})
    selected_required = set(selected.get("required", []))
    if "why_selected" not in selected_required:
        fail_field(report, rel, "selected_action.why_selected", "selected action should explain residual-minimizing choice")

    report.pass_(f"Pre-U packet schema-aligned: {rel}")


def check_capsule_schema_alignment(expected: dict[str, Any], report: Report) -> None:
    required_agents = expected["required_agents"]
    base_files = expected["required_base_capsule_files"]

    for agent_id in required_agents:
        capsule_dir = ROOT / "agent_brains" / agent_id
        report.schema_alignment["agent_brain_capsules_checked"] += 1
        check_exists(capsule_dir, report, "schema alignment capsule directory")

        profile_path = capsule_dir / "brain_profile.json"
        profile = check_json_file(profile_path, report, f"{agent_id} schema profile")
        if profile is not None:
            check_brain_profile_alignment(agent_id, profile_path, profile, report)

        for filename in base_files:
            if filename.endswith("_refs.json"):
                ref_path = capsule_dir / filename
                ref_data = check_json_file(ref_path, report, f"{agent_id} schema ref")
                if ref_data is not None:
                    check_ref_file_alignment(agent_id, ref_path, ref_data, report)

    execution_path = ROOT / "agent_brains" / "Ethan-CTO" / "execution_channels.json"
    execution = check_json_file(execution_path, report, "Ethan execution channels schema")
    if execution is not None:
        check_execution_channels_alignment("Ethan-CTO", execution_path, execution, report)

    pre_u_path = ROOT / "agent_brains" / "Aiden-CEO" / "pre_u_counterfactual" / "packet_schema.json"
    pre_u = check_json_file(pre_u_path, report, "Aiden Pre-U packet schema")
    if pre_u is not None:
        check_pre_u_packet_schema_alignment(pre_u_path, pre_u, report)


def contains_unsafe_pattern(value: str, unsafe_patterns: list[str]) -> str | None:
    lowered = value.lower()
    for pattern in unsafe_patterns:
        p = pattern.lower()
        if p in {".db", ".db-wal", ".db-shm"}:
            if lowered.endswith(p):
                return pattern
        elif p in lowered:
            return pattern
    return None


def main() -> int:
    report = Report()
    expected = check_json_file(EXPECTED, report, "expected structure")
    if expected is None:
        print_report(report)
        return 1

    required_console_files = expected["required_console_files"]
    required_loader_files = expected.get("required_loader_files", [])
    required_cli_files = expected.get("required_cli_files", [])
    required_check_files = expected.get("required_check_files", [])
    required_generated_files = expected.get("required_generated_files", [])
    required_safe_mining_files = expected.get("required_safe_mining_files", [])
    required_backlog_disposition_files = expected.get("required_backlog_disposition_files", [])
    required_evidence_review_files = expected.get("required_evidence_review_files", [])
    required_labs_governance_bridge_files = expected.get("required_labs_governance_bridge_files", [])
    required_labs_runtime_acceptance_files = expected.get("required_labs_runtime_acceptance_files", [])
    required_cross_repo_alignment_files = expected.get("required_cross_repo_alignment_files", [])
    required_labs_live_readiness_files = expected.get("required_labs_live_readiness_files", [])
    required_labs_live_boundary_files = expected.get("required_labs_live_boundary_files", [])
    required_labs_cieu_runtime_boundary_files = expected.get("required_labs_cieu_runtime_boundary_files", [])
    required_company_autonomy_inventory_files = expected.get("required_company_autonomy_inventory_files", [])
    required_company_autonomous_work_cycle_files = expected.get("required_company_autonomous_work_cycle_files", [])
    required_legacy_asset_triage_files = expected.get("required_legacy_asset_triage_files", [])
    required_governed_observation_loop_files = expected.get("required_governed_observation_loop_files", [])
    required_governed_readonly_observation_tool_files = expected.get(
        "required_governed_readonly_observation_tool_files", []
    )
    required_governed_tool_invocation_bridge_files = expected.get(
        "required_governed_tool_invocation_bridge_files", []
    )
    required_agent_team_work_proposal_files = expected.get("required_agent_team_work_proposal_files", [])
    required_mission_dashboard_refresh_loop_files = expected.get(
        "required_mission_dashboard_refresh_loop_files", []
    )
    required_recurring_observation_loop_contract_files = expected.get(
        "required_recurring_observation_loop_contract_files", []
    )
    required_manual_recurring_observation_tick_runner_files = expected.get(
        "required_manual_recurring_observation_tick_runner_files", []
    )
    required_field_functional_archaeology_files = expected.get(
        "required_field_functional_archaeology_files", []
    )
    required_mission_field_projection_files = expected.get(
        "required_mission_field_projection_files", []
    )
    required_field_functional_auto_projection_core_files = expected.get(
        "required_field_functional_auto_projection_core_files", []
    )
    required_projection_checked_autonomous_work_cycle_files = expected.get(
        "required_projection_checked_autonomous_work_cycle_files", []
    )
    required_review_gated_shadow_projection_cycle_files = expected.get(
        "required_review_gated_shadow_projection_cycle_files", []
    )
    required_cross_repo_governance_contract_proof_files = expected.get(
        "required_cross_repo_governance_contract_proof_files", []
    )
    required_governed_mcp_dry_run_adapter_files = expected.get(
        "required_governed_mcp_dry_run_adapter_files", []
    )
    required_controlled_canonical_learning_design_files = expected.get(
        "required_controlled_canonical_learning_design_files", []
    )
    required_approved_canonical_update_sandbox_files = expected.get(
        "required_approved_canonical_update_sandbox_files", []
    )
    required_real_approval_workflow_boundary_files = expected.get(
        "required_real_approval_workflow_boundary_files", []
    )
    required_controlled_approval_record_sandbox_files = expected.get(
        "required_controlled_approval_record_sandbox_files", []
    )
    required_controlled_real_release_preflight_files = expected.get(
        "required_controlled_real_release_preflight_files", []
    )
    required_real_release_simulation_sandbox_files = expected.get(
        "required_real_release_simulation_sandbox_files", []
    )
    required_live_boundary_no_go_framework_files = expected.get(
        "required_live_boundary_no_go_framework_files", []
    )
    required_l6_meta_development_generative_selection_engine_files = expected.get(
        "required_l6_meta_development_generative_selection_engine_files", []
    )
    required_l6_meta_development_mvp_artifact_sandbox_files = expected.get(
        "required_l6_meta_development_mvp_artifact_sandbox_files", []
    )
    required_l6_governed_external_observation_boundary_files = expected.get(
        "required_l6_governed_external_observation_boundary_files", []
    )
    required_l6_controlled_external_observation_sandbox_files = expected.get(
        "required_l6_controlled_external_observation_sandbox_files", []
    )
    required_l6_real_read_only_external_observation_preflight_files = expected.get(
        "required_l6_real_read_only_external_observation_preflight_files", []
    )
    required_l6_controlled_real_read_only_observation_pilot_design_files = expected.get(
        "required_l6_controlled_real_read_only_observation_pilot_design_files", []
    )
    required_l6_controlled_observation_pilot_approval_packet_files = expected.get(
        "required_l6_controlled_observation_pilot_approval_packet_files", []
    )
    required_l6_integrated_approval_record_and_pilot_readiness_sandbox_files = (
        expected.get(
            "required_l6_integrated_approval_record_and_pilot_readiness_sandbox_files",
            [],
        )
    )
    required_l6_agentic_evidence_discovery_trust_engine_files = expected.get(
        "required_l6_agentic_evidence_discovery_trust_engine_files", []
    )
    required_l6_controlled_agentic_evidence_pilot_approval_dry_run_files = expected.get(
        "required_l6_controlled_agentic_evidence_pilot_approval_dry_run_files", []
    )
    required_l6_tiny_real_read_only_agentic_evidence_observation_pilot_files = expected.get(
        "required_l6_tiny_real_read_only_agentic_evidence_observation_pilot_files", []
    )
    required_l6_controlled_source_locator_resolution_tiny_observation_retry_files = expected.get(
        "required_l6_controlled_source_locator_resolution_tiny_observation_retry_files", []
    )
    required_l6_governed_capability_gap_toolmaking_locator_resolver_files = expected.get(
        "required_l6_governed_capability_gap_toolmaking_locator_resolver_files", []
    )
    required_l6_controlled_locator_resolver_enablement_files = expected.get(
        "required_l6_controlled_locator_resolver_enablement_files", []
    )
    required_schema_files = expected["required_shared_schema_files"]
    required_agents = expected["required_agents"]
    base_files = expected["required_base_capsule_files"]
    unsafe_patterns = expected["unsafe_direct_source_patterns"]

    for rel in required_console_files:
        path = ROOT / rel
        check_exists(path, report, "console file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "console JSON")

    for rel in required_loader_files:
        path = ROOT / rel
        check_exists(path, report, "loader file")

    for rel in required_cli_files:
        path = ROOT / rel
        check_exists(path, report, "CLI file")

    for rel in required_check_files:
        path = ROOT / rel
        check_exists(path, report, "local check file")

    for rel in required_safe_mining_files:
        path = ROOT / rel
        check_exists(path, report, "safe mining file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "safe mining JSON")

    for rel in required_backlog_disposition_files:
        path = ROOT / rel
        check_exists(path, report, "backlog disposition file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "backlog disposition JSON")

    for rel in required_evidence_review_files:
        path = ROOT / rel
        check_exists(path, report, "evidence review file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "evidence review JSON")

    for rel in required_labs_governance_bridge_files:
        path = ROOT / rel
        check_exists(path, report, "labs-governance bridge file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "labs-governance bridge JSON")

    for rel in required_labs_runtime_acceptance_files:
        path = ROOT / rel
        check_exists(path, report, "labs runtime acceptance file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "labs runtime acceptance JSON")

    for rel in required_cross_repo_alignment_files:
        path = ROOT / rel
        check_exists(path, report, "cross-repo alignment file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "cross-repo alignment JSON")

    for rel in required_labs_live_readiness_files:
        path = ROOT / rel
        check_exists(path, report, "labs live readiness file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "labs live readiness JSON")

    for rel in required_labs_live_boundary_files:
        path = ROOT / rel
        check_exists(path, report, "labs live boundary file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "labs live boundary JSON")

    for rel in required_labs_cieu_runtime_boundary_files:
        path = ROOT / rel
        check_exists(path, report, "labs CIEU runtime boundary file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "labs CIEU runtime boundary JSON")

    for rel in required_company_autonomy_inventory_files:
        path = ROOT / rel
        check_exists(path, report, "company autonomy inventory file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "company autonomy inventory JSON")

    for rel in required_company_autonomous_work_cycle_files:
        path = ROOT / rel
        check_exists(path, report, "company autonomous work cycle file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "company autonomous work cycle JSON")

    for rel in required_legacy_asset_triage_files:
        path = ROOT / rel
        check_exists(path, report, "legacy asset triage file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "legacy asset triage JSON")

    for rel in required_governed_observation_loop_files:
        path = ROOT / rel
        check_exists(path, report, "governed observation loop file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "governed observation loop JSON")

    for rel in required_governed_readonly_observation_tool_files:
        path = ROOT / rel
        check_exists(path, report, "governed read-only observation tool file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "governed read-only observation tool JSON")

    for rel in required_governed_tool_invocation_bridge_files:
        path = ROOT / rel
        check_exists(path, report, "governed tool invocation bridge file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "governed tool invocation bridge JSON")

    for rel in required_agent_team_work_proposal_files:
        path = ROOT / rel
        check_exists(path, report, "agent team work proposal file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "agent team work proposal JSON")

    for rel in required_mission_dashboard_refresh_loop_files:
        path = ROOT / rel
        check_exists(path, report, "mission dashboard refresh loop file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "mission dashboard refresh loop JSON")

    for rel in required_recurring_observation_loop_contract_files:
        path = ROOT / rel
        check_exists(path, report, "recurring observation loop contract file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "recurring observation loop contract JSON")

    for rel in required_manual_recurring_observation_tick_runner_files:
        path = ROOT / rel
        check_exists(path, report, "manual recurring observation tick runner file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "manual recurring observation tick runner JSON")

    for rel in required_field_functional_archaeology_files:
        path = ROOT / rel
        check_exists(path, report, "field functional archaeology file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "field functional archaeology JSON")

    for rel in required_mission_field_projection_files:
        path = ROOT / rel
        check_exists(path, report, "mission field projection file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "mission field projection JSON")

    for rel in required_field_functional_auto_projection_core_files:
        path = ROOT / rel
        check_exists(path, report, "field functional auto-projection file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "field functional auto-projection JSON")

    for rel in required_projection_checked_autonomous_work_cycle_files:
        path = ROOT / rel
        check_exists(path, report, "projection-checked autonomous cycle file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "projection-checked autonomous cycle JSON")

    for rel in required_review_gated_shadow_projection_cycle_files:
        path = ROOT / rel
        check_exists(path, report, "review-gated shadow projection cycle file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "review-gated shadow projection cycle JSON")

    for rel in required_cross_repo_governance_contract_proof_files:
        path = ROOT / rel
        check_exists(path, report, "cross-repo governance contract proof file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "cross-repo governance contract proof JSON")

    for rel in required_governed_mcp_dry_run_adapter_files:
        path = ROOT / rel
        check_exists(path, report, "governed MCP dry-run adapter file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "governed MCP dry-run adapter JSON")

    for rel in required_controlled_canonical_learning_design_files:
        path = ROOT / rel
        check_exists(path, report, "controlled canonical learning design file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "controlled canonical learning design JSON")

    for rel in required_approved_canonical_update_sandbox_files:
        path = ROOT / rel
        check_exists(path, report, "approved canonical update sandbox file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "approved canonical update sandbox JSON")

    for rel in required_real_approval_workflow_boundary_files:
        path = ROOT / rel
        check_exists(path, report, "real approval workflow boundary file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "real approval workflow boundary JSON")

    for rel in required_controlled_approval_record_sandbox_files:
        path = ROOT / rel
        check_exists(path, report, "controlled approval record sandbox file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "controlled approval record sandbox JSON")

    for rel in required_controlled_real_release_preflight_files:
        path = ROOT / rel
        check_exists(path, report, "controlled real release preflight file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "controlled real release preflight JSON")

    for rel in required_real_release_simulation_sandbox_files:
        path = ROOT / rel
        check_exists(path, report, "real release simulation sandbox file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "real release simulation sandbox JSON")

    for rel in required_live_boundary_no_go_framework_files:
        path = ROOT / rel
        check_exists(path, report, "live boundary no-go framework file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "live boundary no-go framework JSON")

    for rel in required_l6_meta_development_generative_selection_engine_files:
        path = ROOT / rel
        check_exists(path, report, "L6 meta-development file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6 meta-development JSON")

    for rel in required_l6_meta_development_mvp_artifact_sandbox_files:
        path = ROOT / rel
        check_exists(path, report, "L6.1 MVP artifact sandbox file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6.1 MVP artifact sandbox JSON")

    for rel in required_l6_governed_external_observation_boundary_files:
        path = ROOT / rel
        check_exists(path, report, "L6.2 governed external observation boundary file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6.2 governed external observation boundary JSON")

    for rel in required_l6_controlled_external_observation_sandbox_files:
        path = ROOT / rel
        check_exists(path, report, "L6.3 controlled external observation sandbox file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6.3 controlled external observation sandbox JSON")

    for rel in required_l6_real_read_only_external_observation_preflight_files:
        path = ROOT / rel
        check_exists(path, report, "L6.4 real read-only external observation preflight file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6.4 real read-only external observation preflight JSON")

    for rel in required_l6_controlled_real_read_only_observation_pilot_design_files:
        path = ROOT / rel
        check_exists(path, report, "L6.5 controlled real read-only observation pilot design file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6.5 controlled real read-only observation pilot design JSON")

    for rel in required_l6_controlled_observation_pilot_approval_packet_files:
        path = ROOT / rel
        check_exists(path, report, "L6.6 controlled observation pilot approval packet file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6.6 controlled observation pilot approval packet JSON")

    for rel in required_l6_integrated_approval_record_and_pilot_readiness_sandbox_files:
        path = ROOT / rel
        check_exists(
            path,
            report,
            "L6.7 integrated approval record and pilot readiness sandbox file",
        )
        if path.suffix == ".json" and path.exists():
            check_json_file(
                path,
                report,
                "L6.7 integrated approval record and pilot readiness sandbox JSON",
            )

    for rel in required_l6_agentic_evidence_discovery_trust_engine_files:
        path = ROOT / rel
        check_exists(path, report, "L6.8 agentic evidence discovery trust engine file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6.8 agentic evidence discovery trust engine JSON")

    for rel in required_l6_controlled_agentic_evidence_pilot_approval_dry_run_files:
        path = ROOT / rel
        check_exists(path, report, "L6.9 controlled agentic evidence pilot approval dry-run file")
        if path.suffix == ".json" and path.exists():
            check_json_file(
                path,
                report,
                "L6.9 controlled agentic evidence pilot approval dry-run JSON",
            )

    for rel in required_l6_tiny_real_read_only_agentic_evidence_observation_pilot_files:
        path = ROOT / rel
        check_exists(path, report, "L6.10 tiny real read-only observation pilot file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6.10 tiny real read-only observation pilot JSON")

    for rel in required_l6_controlled_source_locator_resolution_tiny_observation_retry_files:
        path = ROOT / rel
        check_exists(path, report, "L6.10R controlled source locator retry file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6.10R controlled source locator retry JSON")

    for rel in required_l6_governed_capability_gap_toolmaking_locator_resolver_files:
        path = ROOT / rel
        check_exists(path, report, "L6.10T governed toolmaking locator resolver file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6.10T governed toolmaking locator resolver JSON")

    for rel in required_l6_controlled_locator_resolver_enablement_files:
        path = ROOT / rel
        check_exists(path, report, "L6.10U controlled locator resolver enablement file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "L6.10U controlled locator resolver enablement JSON")

    generated_json: dict[str, Any] = {}
    for rel in required_generated_files:
        path = ROOT / rel
        check_exists(path, report, "generated file")
        if path.suffix == ".json" and path.exists():
            generated_json[rel] = check_json_file(path, report, "generated JSON")

    for rel in required_schema_files:
        path = ROOT / rel
        check_exists(path, report, "shared schema file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "shared schema JSON")

    read_model = check_json_file(
        ROOT / "console_read_model" / "team_brain_read_model.json",
        report,
        "team brain read model",
    )
    agent_cards = check_json_file(
        ROOT / "console_read_model" / "agent_cards.json",
        report,
        "agent cards",
    )
    capability_matrix = check_json_file(
        ROOT / "console_read_model" / "capability_matrix.json",
        report,
        "capability matrix",
    )
    team_capsule_map = check_json_file(
        ROOT / "agent_brains" / "team_capsule_map.json",
        report,
        "team capsule map",
    )

    if read_model:
        agents = {a.get("agent_id") for a in read_model.get("agents", [])}
        for agent_id in required_agents:
            if agent_id in agents:
                report.pass_(f"required agent in read model: {agent_id}")
            else:
                report.fail(f"required agent missing from read model: {agent_id}")

        safe_to_read = read_model.get("data_safety", {}).get("safe_to_read", [])
        unsafe_to_read = read_model.get("data_safety", {}).get("unsafe_to_read_directly", [])

        for item in safe_to_read:
            match = contains_unsafe_pattern(str(item), unsafe_patterns)
            if match:
                report.fail(f"unsafe pattern '{match}' appears in safe_to_read: {item}")
        report.pass_("safe_to_read checked for unsafe direct-source patterns")

        required_unsafe_terms = [".db", ".db-wal", ".db-shm", "logs", "active-agent", "daemon", "__pycache__"]
        unsafe_joined = " | ".join(str(x).lower() for x in unsafe_to_read)
        for term in required_unsafe_terms:
            if term in unsafe_joined:
                report.pass_(f"unsafe_to_read_directly lists category: {term}")
            else:
                report.fail(f"unsafe_to_read_directly missing category: {term}")

    if agent_cards:
        cards = {c.get("card_id") for c in agent_cards.get("cards", [])}
        for agent_id in required_agents:
            if agent_id in cards:
                report.pass_(f"agent card present: {agent_id}")
            else:
                report.fail(f"agent card missing: {agent_id}")

    if capability_matrix:
        agents = set(capability_matrix.get("agents", []))
        for agent_id in required_agents:
            if agent_id in agents:
                report.pass_(f"capability matrix agent present: {agent_id}")
            else:
                report.fail(f"capability matrix agent missing: {agent_id}")

    if team_capsule_map:
        agents = {a.get("agent_id"): a for a in team_capsule_map.get("agents", [])}
        for agent_id in required_agents:
            if agent_id in agents:
                report.pass_(f"team capsule map agent present: {agent_id}")
            else:
                report.fail(f"team capsule map agent missing: {agent_id}")

    snapshot = generated_json.get("console_read_model/generated/team_console_snapshot.json")
    if snapshot:
        agents = {a.get("agent_id") for a in snapshot.get("agents", [])}
        for agent_id in required_agents:
            if agent_id in agents:
                report.pass_(f"generated snapshot agent present: {agent_id}")
            else:
                report.fail(f"generated snapshot agent missing: {agent_id}")
        quarantine_summary = snapshot.get("quarantine_summary")
        if quarantine_summary:
            report.pass_("generated snapshot contains quarantine_summary")
            for field in [
                "framework_status",
                "current_mining_level",
                "artifacts_classified",
                "unsafe_artifacts_count",
                "classes_seen",
                "generated_manifest_ref",
                "forbidden_direct_reads",
                "future_adapter_candidates",
                "safety_warning",
            ]:
                if field in quarantine_summary:
                    report.pass_(f"snapshot quarantine_summary field present: {field}")
                else:
                    report.fail(f"snapshot quarantine_summary missing field: {field}")
        else:
            report.fail("generated snapshot missing quarantine_summary")

        safe_mining_summary = snapshot.get("safe_mining_summary")
        if safe_mining_summary:
            report.pass_("generated snapshot contains safe_mining_summary")
            for field in [
                "candidate_count",
                "classes_seen",
                "generated_candidate_index",
                "safety_level",
                "ingestion_status",
                "allowed_next_step",
                "forbidden_next_step",
                "warning",
            ]:
                if field in safe_mining_summary:
                    report.pass_(f"snapshot safe_mining_summary field present: {field}")
                else:
                    report.fail(f"snapshot safe_mining_summary missing field: {field}")
            if safe_mining_summary.get("ingestion_status") != "candidate_only":
                report.fail("snapshot safe_mining_summary must remain candidate_only")
            if safe_mining_summary.get("forbidden_next_step") != "direct_brain_writeback":
                report.fail("snapshot safe_mining_summary must forbid direct brain writeback")
        else:
            report.fail("generated snapshot missing safe_mining_summary")

        review_queue_summary = snapshot.get("review_queue_summary")
        if review_queue_summary:
            report.pass_("generated snapshot contains review_queue_summary")
            for field in [
                "review_count",
                "statuses",
                "intended_use_summary",
                "generated_queue_path",
                "default_review_status",
                "default_ingestion_status",
                "forbidden_actions",
                "warning",
            ]:
                if field in review_queue_summary:
                    report.pass_(f"snapshot review_queue_summary field present: {field}")
                else:
                    report.fail(f"snapshot review_queue_summary missing field: {field}")
            if review_queue_summary.get("default_review_status") != "pending_review":
                report.fail("snapshot review_queue_summary must remain pending_review")
            if review_queue_summary.get("default_ingestion_status") != "not_ingested":
                report.fail("snapshot review_queue_summary must remain not_ingested")
        else:
            report.fail("generated snapshot missing review_queue_summary")

        disposition_summary = snapshot.get("artifact_disposition_summary")
        if disposition_summary:
            report.pass_("generated snapshot contains artifact_disposition_summary")
            for field in [
                "total_artifacts",
                "artifacts_with_disposition",
                "dispositions",
                "safe_mined_to_review_queue",
                "deferred_adapter_counts",
                "forbidden_direct_read_count",
                "evidence_scoring_status",
                "generated_disposition_index",
                "warning",
            ]:
                if field in disposition_summary:
                    report.pass_(f"snapshot artifact_disposition_summary field present: {field}")
                else:
                    report.fail(f"snapshot artifact_disposition_summary missing field: {field}")
            if disposition_summary.get("total_artifacts") != disposition_summary.get("artifacts_with_disposition"):
                report.fail("snapshot artifact_disposition_summary must cover every manifest artifact")
            evidence = set(disposition_summary.get("evidence_scoring_status", {}))
            if evidence and evidence != {"not_started"}:
                report.fail("snapshot artifact_disposition_summary evidence scoring must remain not_started")
        else:
            report.fail("generated snapshot missing artifact_disposition_summary")

        evidence_review_summary = snapshot.get("evidence_review_summary")
        if evidence_review_summary:
            report.pass_("generated snapshot contains evidence_review_summary")
            for field in [
                "candidates_scored",
                "decision_stubs_created",
                "routes_created",
                "reuse_readiness",
                "route_counts",
                "semantic_truth_status",
                "automatic_approvals",
                "brain_writeback_allowed",
                "memory_ingestion_allowed",
                "cieu_write_allowed",
                "warning",
            ]:
                if field in evidence_review_summary:
                    report.pass_(f"snapshot evidence_review_summary field present: {field}")
                else:
                    report.fail(f"snapshot evidence_review_summary missing field: {field}")
            if evidence_review_summary.get("automatic_approvals") != 0:
                report.fail("snapshot evidence_review_summary must not contain automatic approvals")
            for field in ["brain_writeback_allowed", "memory_ingestion_allowed", "cieu_write_allowed"]:
                if evidence_review_summary.get(field) != 0:
                    report.fail(f"snapshot evidence_review_summary must not allow {field}")
            semantic = set(evidence_review_summary.get("semantic_truth_status", {}))
            if semantic and semantic != {"not_evaluated"}:
                report.fail("snapshot evidence_review_summary semantic truth status must remain not_evaluated")
        else:
            report.fail("generated snapshot missing evidence_review_summary")

        governance_bridge_summary = snapshot.get("governance_bridge_summary")
        if governance_bridge_summary:
            report.pass_("generated snapshot contains governance_bridge_summary")
            for field in [
                "latest_bridge_run_id",
                "source_task_id",
                "agent_id",
                "ystar_gov_cli_path",
                "ystar_gov_exit_code",
                "ystar_gov_decision",
                "allow_execution",
                "require_revision",
                "deny",
                "escalate",
                "dry_run_only",
                "non_execution_confirmation",
                "action_executed",
                "cieu_written",
                "brain_writeback_performed",
                "memory_ingestion_performed",
                "warning",
            ]:
                if field in governance_bridge_summary:
                    report.pass_(f"snapshot governance_bridge_summary field present: {field}")
                else:
                    report.fail(f"snapshot governance_bridge_summary missing field: {field}")
            if governance_bridge_summary.get("dry_run_only") is not True:
                report.fail("snapshot governance_bridge_summary must remain dry_run_only")
            if governance_bridge_summary.get("non_execution_confirmation") is not True:
                report.fail("snapshot governance_bridge_summary must confirm non-execution")
            for field in [
                "action_executed",
                "cieu_written",
                "brain_writeback_performed",
                "memory_ingestion_performed",
            ]:
                if governance_bridge_summary.get(field) is not False:
                    report.fail(f"snapshot governance_bridge_summary must keep {field}=false")
        else:
            report.fail("generated snapshot missing governance_bridge_summary")

        pre_u_governance_summary = snapshot.get("pre_u_governance_summary")
        if pre_u_governance_summary:
            report.pass_("generated snapshot contains pre_u_governance_summary")
            for field in [
                "packets_generated",
                "roles_covered",
                "decision_counts",
                "decisions_by_role",
                "dry_run_only",
                "action_executed",
                "cieu_written",
                "brain_writeback_performed",
                "memory_ingestion_performed",
                "warning",
            ]:
                if field in pre_u_governance_summary:
                    report.pass_(f"snapshot pre_u_governance_summary field present: {field}")
                else:
                    report.fail(f"snapshot pre_u_governance_summary missing field: {field}")
            if set(pre_u_governance_summary.get("roles_covered", [])) != set(required_agents):
                report.fail("snapshot pre_u_governance_summary must cover required agents")
            if pre_u_governance_summary.get("packets_generated") != len(required_agents):
                report.fail("snapshot pre_u_governance_summary must include three generated packets")
            if pre_u_governance_summary.get("dry_run_only") is not True:
                report.fail("snapshot pre_u_governance_summary must remain dry_run_only")
            for field in ["action_executed", "cieu_written", "brain_writeback_performed", "memory_ingestion_performed"]:
                if pre_u_governance_summary.get(field) is not False:
                    report.fail(f"snapshot pre_u_governance_summary must keep {field}=false")
        else:
            report.fail("generated snapshot missing pre_u_governance_summary")

        labs_acceptance_summary = snapshot.get("labs_acceptance_summary")
        if labs_acceptance_summary:
            report.pass_("generated snapshot contains labs_acceptance_summary")
            for field in [
                "accepted",
                "checks_passed",
                "checks_total",
                "roles_covered",
                "decision_counts",
                "action_executed",
                "cieu_written",
                "brain_writeback_performed",
                "memory_ingestion_performed",
                "raw_runtime_artifacts_ingested",
                "warning",
            ]:
                if field in labs_acceptance_summary:
                    report.pass_(f"snapshot labs_acceptance_summary field present: {field}")
                else:
                    report.fail(f"snapshot labs_acceptance_summary missing field: {field}")
            roles = set(labs_acceptance_summary.get("roles_covered", []))
            if roles and roles != set(required_agents):
                report.fail("snapshot labs_acceptance_summary must cover required agents when roles are present")
            for field in [
                "action_executed",
                "cieu_written",
                "brain_writeback_performed",
                "memory_ingestion_performed",
                "raw_runtime_artifacts_ingested",
            ]:
                if labs_acceptance_summary.get(field) is not False:
                    report.fail(f"snapshot labs_acceptance_summary must keep {field}=false")
        else:
            report.fail("generated snapshot missing labs_acceptance_summary")

        cross_repo_alignment_summary = snapshot.get("cross_repo_alignment_summary")
        if cross_repo_alignment_summary:
            report.pass_("generated snapshot contains cross_repo_alignment_summary")
            for field in [
                "alignment_accepted",
                "ystar_company_head",
                "ystar_company_head_summary",
                "ystar_gov_head",
                "ystar_gov_head_summary",
                "ystar_gov_endpoint_accepted",
                "labs_runtime_accepted",
                "roles_covered",
                "decision_counts",
                "safety_assertions",
                "warning",
            ]:
                if field in cross_repo_alignment_summary:
                    report.pass_(f"snapshot cross_repo_alignment_summary field present: {field}")
                else:
                    report.fail(f"snapshot cross_repo_alignment_summary missing field: {field}")
            roles = set(cross_repo_alignment_summary.get("roles_covered", []))
            if roles and roles != set(required_agents):
                report.fail("snapshot cross_repo_alignment_summary must cover required agents when roles are present")
            for name, value in cross_repo_alignment_summary.get("safety_assertions", {}).items():
                if value is not True:
                    report.fail(f"snapshot cross_repo_alignment_summary safety assertion must be true: {name}")
        else:
            report.fail("generated snapshot missing cross_repo_alignment_summary")

        live_readiness_summary = snapshot.get("live_readiness_summary")
        if live_readiness_summary:
            report.pass_("generated snapshot contains live_readiness_summary")
            for field in [
                "dry_run_governance_ready",
                "minimal_live_loop_ready",
                "minimal_live_loop_status",
                "recommended_next_phase",
                "live_action_execution_allowed",
                "live_cieu_write_allowed",
                "live_brain_writeback_allowed",
                "live_memory_ingestion_allowed",
                "candidate_auto_approval_allowed",
                "raw_artifact_ingestion_allowed",
                "blockers",
                "transition_backlog_items",
                "generated_report",
                "generated_transition_backlog",
                "warning",
            ]:
                if field in live_readiness_summary:
                    report.pass_(f"snapshot live_readiness_summary field present: {field}")
                else:
                    report.fail(f"snapshot live_readiness_summary missing field: {field}")
            if live_readiness_summary.get("minimal_live_loop_ready") is not False:
                report.fail("snapshot live_readiness_summary must keep minimal_live_loop_ready=false")
            if live_readiness_summary.get("minimal_live_loop_status") != "blocked_until_required_gates_exist":
                report.fail("snapshot live_readiness_summary must keep minimal live loop blocked")
            for field in [
                "live_action_execution_allowed",
                "live_cieu_write_allowed",
                "live_brain_writeback_allowed",
                "live_memory_ingestion_allowed",
                "candidate_auto_approval_allowed",
                "raw_artifact_ingestion_allowed",
            ]:
                if live_readiness_summary.get(field) is not False:
                    report.fail(f"snapshot live_readiness_summary must keep {field}=false")
        else:
            report.fail("generated snapshot missing live_readiness_summary")

        live_boundary_summary = snapshot.get("live_boundary_summary")
        if live_boundary_summary:
            report.pass_("generated snapshot contains live_boundary_summary")
            for field in [
                "live_boundary_defined",
                "operator_approval_gate_defined",
                "action_sandbox_contract_defined",
                "rollback_policy_defined",
                "cieu_writer_boundary_defined",
                "live_action_execution_enabled",
                "cieu_write_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "candidate_auto_approval_enabled",
                "raw_artifact_ingestion_enabled",
                "requires_manual_enablement",
                "minimal_live_loop_ready",
                "blocked_reason",
                "checklist_status_counts",
                "ready_or_enabled_checklist_items",
                "generated_manifest",
                "generated_checklist",
                "warning",
            ]:
                if field in live_boundary_summary:
                    report.pass_(f"snapshot live_boundary_summary field present: {field}")
                else:
                    report.fail(f"snapshot live_boundary_summary missing field: {field}")
            for field in [
                "live_boundary_defined",
                "operator_approval_gate_defined",
                "action_sandbox_contract_defined",
                "rollback_policy_defined",
                "cieu_writer_boundary_defined",
                "requires_manual_enablement",
            ]:
                if live_boundary_summary.get(field) is not True:
                    report.fail(f"snapshot live_boundary_summary must keep {field}=true")
            for field in [
                "live_action_execution_enabled",
                "cieu_write_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "candidate_auto_approval_enabled",
                "raw_artifact_ingestion_enabled",
                "minimal_live_loop_ready",
            ]:
                if live_boundary_summary.get(field) is not False:
                    report.fail(f"snapshot live_boundary_summary must keep {field}=false")
            if live_boundary_summary.get("blocked_reason") != "required_live_gates_defined_but_disabled":
                report.fail("snapshot live_boundary_summary must keep live boundary blocked")
            if live_boundary_summary.get("ready_or_enabled_checklist_items") != 0:
                report.fail("snapshot live_boundary_summary must not include ready/enabled checklist items")
        else:
            report.fail("generated snapshot missing live_boundary_summary")

        cieu_boundary_summary = snapshot.get("cieu_boundary_summary")
        if cieu_boundary_summary:
            report.pass_("generated snapshot contains cieu_boundary_summary")
            for field in [
                "cieu_runtime_boundary_defined",
                "cieu_runtime_event_schema_defined",
                "prediction_delta_fixture_defined",
                "cieu_writer_policy_defined",
                "dry_run_only",
                "persistence_enabled",
                "live_action_execution_enabled",
                "cieu_write_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "candidate_auto_approval_enabled",
                "raw_artifact_ingestion_enabled",
                "requires_manual_enablement",
                "minimal_live_loop_ready",
                "blocked_reason",
                "generated_manifest",
                "generated_sample_event",
                "generated_prediction_delta_fixture",
                "warning",
            ]:
                if field in cieu_boundary_summary:
                    report.pass_(f"snapshot cieu_boundary_summary field present: {field}")
                else:
                    report.fail(f"snapshot cieu_boundary_summary missing field: {field}")
            for field in [
                "cieu_runtime_boundary_defined",
                "cieu_runtime_event_schema_defined",
                "prediction_delta_fixture_defined",
                "cieu_writer_policy_defined",
                "dry_run_only",
                "requires_manual_enablement",
            ]:
                if cieu_boundary_summary.get(field) is not True:
                    report.fail(f"snapshot cieu_boundary_summary must keep {field}=true")
            for field in [
                "persistence_enabled",
                "live_action_execution_enabled",
                "cieu_write_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "candidate_auto_approval_enabled",
                "raw_artifact_ingestion_enabled",
                "minimal_live_loop_ready",
            ]:
                if cieu_boundary_summary.get(field) is not False:
                    report.fail(f"snapshot cieu_boundary_summary must keep {field}=false")
            if cieu_boundary_summary.get("blocked_reason") != "cieu_runtime_boundary_defined_but_persistence_disabled":
                report.fail("snapshot cieu_boundary_summary must keep persistence disabled")
        else:
            report.fail("generated snapshot missing cieu_boundary_summary")

        autonomy_inventory_summary = snapshot.get("autonomy_inventory_summary")
        if autonomy_inventory_summary:
            report.pass_("generated snapshot contains autonomy_inventory_summary")
            for field in [
                "company_autonomy_inventory_defined",
                "repo_archaeology_completed",
                "observation_capability_map_defined",
                "resource_sensing_map_defined",
                "action_capability_map_defined",
                "governed_tool_registry_candidates_defined",
                "agent_role_capability_matrix_defined",
                "commercial_agent_company_goal_aligned",
                "governance_only_runtime",
                "live_actions_enabled",
                "external_actions_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "cieu_persistence_enabled",
                "git_push_enabled",
                "daemon_control_enabled",
                "email_or_external_communication_enabled",
                "requires_manual_enablement",
                "next_required_milestone",
                "generated_summary",
                "generated_report",
                "warning",
            ]:
                if field in autonomy_inventory_summary:
                    report.pass_(f"snapshot autonomy_inventory_summary field present: {field}")
                else:
                    report.fail(f"snapshot autonomy_inventory_summary missing field: {field}")
            for field in [
                "company_autonomy_inventory_defined",
                "repo_archaeology_completed",
                "observation_capability_map_defined",
                "resource_sensing_map_defined",
                "action_capability_map_defined",
                "governed_tool_registry_candidates_defined",
                "agent_role_capability_matrix_defined",
                "commercial_agent_company_goal_aligned",
                "requires_manual_enablement",
            ]:
                if autonomy_inventory_summary.get(field) is not True:
                    report.fail(f"snapshot autonomy_inventory_summary must keep {field}=true")
            for field in [
                "governance_only_runtime",
                "live_actions_enabled",
                "external_actions_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "cieu_persistence_enabled",
                "git_push_enabled",
                "daemon_control_enabled",
                "email_or_external_communication_enabled",
            ]:
                if autonomy_inventory_summary.get(field) is not False:
                    report.fail(f"snapshot autonomy_inventory_summary must keep {field}=false")
            if (
                autonomy_inventory_summary.get("next_required_milestone")
                != "L4.2 Company Autonomous Work Cycle Simulator v0"
            ):
                report.fail("snapshot autonomy_inventory_summary must point to L4.2 simulator milestone")
        else:
            report.fail("generated snapshot missing autonomy_inventory_summary")

        autonomous_cycle_summary = snapshot.get("autonomous_cycle_summary")
        if autonomous_cycle_summary:
            report.pass_("generated snapshot contains autonomous_cycle_summary")
            for field in [
                "autonomous_work_cycle_defined",
                "mission_bounded_autonomy_defined",
                "founder_sets_mission_agent_team_drives",
                "step_by_step_human_prompting_required",
                "observation_snapshot_defined",
                "autonomous_work_backlog_defined",
                "selected_work_item_defined",
                "role_delegation_defined",
                "governed_tool_selection_defined",
                "pre_u_packet_simulated",
                "governance_decision_simulated",
                "action_plan_simulated",
                "cieu_event_simulated",
                "residual_delta_simulated",
                "next_task_recommendations_defined",
                "real_action_executed",
                "external_action_executed",
                "live_action_enabled",
                "git_push_enabled",
                "daemon_control_enabled",
                "cieu_persistence_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "email_or_external_communication_enabled",
                "requires_manual_enablement_for_live",
                "next_required_milestone",
                "generated_summary",
                "generated_report",
                "warning",
            ]:
                if field in autonomous_cycle_summary:
                    report.pass_(f"snapshot autonomous_cycle_summary field present: {field}")
                else:
                    report.fail(f"snapshot autonomous_cycle_summary missing field: {field}")
            for field in [
                "autonomous_work_cycle_defined",
                "mission_bounded_autonomy_defined",
                "founder_sets_mission_agent_team_drives",
                "observation_snapshot_defined",
                "autonomous_work_backlog_defined",
                "selected_work_item_defined",
                "role_delegation_defined",
                "governed_tool_selection_defined",
                "pre_u_packet_simulated",
                "governance_decision_simulated",
                "action_plan_simulated",
                "cieu_event_simulated",
                "residual_delta_simulated",
                "next_task_recommendations_defined",
                "requires_manual_enablement_for_live",
            ]:
                if autonomous_cycle_summary.get(field) is not True:
                    report.fail(f"snapshot autonomous_cycle_summary must keep {field}=true")
            for field in [
                "step_by_step_human_prompting_required",
                "real_action_executed",
                "external_action_executed",
                "live_action_enabled",
                "git_push_enabled",
                "daemon_control_enabled",
                "cieu_persistence_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "email_or_external_communication_enabled",
            ]:
                if autonomous_cycle_summary.get(field) is not False:
                    report.fail(f"snapshot autonomous_cycle_summary must keep {field}=false")
            if autonomous_cycle_summary.get("next_required_milestone") != "L4.3 Governed Read-Only Observation Loop v0":
                report.fail("snapshot autonomous_cycle_summary must point to L4.3 observation-loop milestone")
        else:
            report.fail("generated snapshot missing autonomous_cycle_summary")

        legacy_triage_summary = snapshot.get("legacy_triage_summary")
        if legacy_triage_summary:
            report.pass_("generated snapshot contains legacy_triage_summary")
            for field in [
                "legacy_asset_triage_defined",
                "assets_scored",
                "absorption_buckets_defined",
                "bucket_counts",
                "top_absorption_candidates_defined",
                "governed_absorption_backlog_defined",
                "blind_absorption_allowed",
                "blanket_rewrite_allowed",
                "live_actions_enabled",
                "next_required_milestone",
                "generated_summary",
                "generated_report",
                "warning",
            ]:
                if field in legacy_triage_summary:
                    report.pass_(f"snapshot legacy_triage_summary field present: {field}")
                else:
                    report.fail(f"snapshot legacy_triage_summary missing field: {field}")
            for field in [
                "legacy_asset_triage_defined",
                "absorption_buckets_defined",
                "top_absorption_candidates_defined",
                "governed_absorption_backlog_defined",
            ]:
                if legacy_triage_summary.get(field) is not True:
                    report.fail(f"snapshot legacy_triage_summary must keep {field}=true")
            for field in ["blind_absorption_allowed", "blanket_rewrite_allowed", "live_actions_enabled"]:
                if legacy_triage_summary.get(field) is not False:
                    report.fail(f"snapshot legacy_triage_summary must keep {field}=false")
            if not legacy_triage_summary.get("assets_scored", 0) > 0:
                report.fail("snapshot legacy_triage_summary must score assets")
            if legacy_triage_summary.get("next_required_milestone") != "L4.4 First Governed Read-Only Observation Tool Wrapper v0":
                report.fail("snapshot legacy_triage_summary must point to L4.4 wrapper milestone")
        else:
            report.fail("generated snapshot missing legacy_triage_summary")

        observation_loop_summary = snapshot.get("observation_loop_summary")
        if observation_loop_summary:
            report.pass_("generated snapshot contains observation_loop_summary")
            for field in [
                "governed_observation_loop_defined",
                "read_only_observation_loop_defined",
                "observation_source_registry_defined",
                "observation_tick_generated",
                "mission_dashboard_snapshot_defined",
                "company_state_digest_defined",
                "observation_to_work_item_candidates_defined",
                "mission_bounded_autonomy_supported",
                "step_by_step_human_prompting_reduced",
                "real_action_executed",
                "external_action_executed",
                "live_action_enabled",
                "cieu_persistence_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "next_required_milestone",
                "generated_summary",
                "generated_report",
                "warning",
            ]:
                if field in observation_loop_summary:
                    report.pass_(f"snapshot observation_loop_summary field present: {field}")
                else:
                    report.fail(f"snapshot observation_loop_summary missing field: {field}")
            for field in [
                "governed_observation_loop_defined",
                "read_only_observation_loop_defined",
                "observation_source_registry_defined",
                "observation_tick_generated",
                "mission_dashboard_snapshot_defined",
                "company_state_digest_defined",
                "observation_to_work_item_candidates_defined",
                "mission_bounded_autonomy_supported",
                "step_by_step_human_prompting_reduced",
            ]:
                if observation_loop_summary.get(field) is not True:
                    report.fail(f"snapshot observation_loop_summary must keep {field}=true")
            for field in [
                "real_action_executed",
                "external_action_executed",
                "live_action_enabled",
                "cieu_persistence_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
            ]:
                if observation_loop_summary.get(field) is not False:
                    report.fail(f"snapshot observation_loop_summary must keep {field}=false")
            if observation_loop_summary.get("next_required_milestone") != "L4.4 First Governed Read-Only Observation Tool Wrapper v0":
                report.fail("snapshot observation_loop_summary must point to L4.4 wrapper milestone")
        else:
            report.fail("generated snapshot missing observation_loop_summary")

        readonly_tool_summary = snapshot.get("readonly_tool_summary")
        if readonly_tool_summary:
            report.pass_("generated snapshot contains readonly_tool_summary")
            for field in [
                "governed_readonly_observation_tool_defined",
                "tool_contract_defined",
                "allowed_source_registry_defined",
                "sample_invocation_defined",
                "sample_result_defined",
                "unsafe_invocation_rejected",
                "tool_cieu_event_defined",
                "local_readonly_dry_run_callable",
                "first_governed_tool_wrapper_created",
                "real_action_executed",
                "external_action_executed",
                "live_action_enabled",
                "cieu_persistence_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "next_required_milestone",
                "generated_summary",
                "generated_contract",
                "generated_registry",
                "warning",
            ]:
                if field in readonly_tool_summary:
                    report.pass_(f"snapshot readonly_tool_summary field present: {field}")
                else:
                    report.fail(f"snapshot readonly_tool_summary missing field: {field}")
            for field in [
                "governed_readonly_observation_tool_defined",
                "tool_contract_defined",
                "allowed_source_registry_defined",
                "sample_invocation_defined",
                "sample_result_defined",
                "unsafe_invocation_rejected",
                "tool_cieu_event_defined",
                "local_readonly_dry_run_callable",
                "first_governed_tool_wrapper_created",
            ]:
                if readonly_tool_summary.get(field) is not True:
                    report.fail(f"snapshot readonly_tool_summary must keep {field}=true")
            for field in [
                "real_action_executed",
                "external_action_executed",
                "live_action_enabled",
                "cieu_persistence_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
            ]:
                if readonly_tool_summary.get(field) is not False:
                    report.fail(f"snapshot readonly_tool_summary must keep {field}=false")
            if readonly_tool_summary.get("next_required_milestone") != "L4.5 Governed Tool Invocation Through Pre-U Bridge v0":
                report.fail("snapshot readonly_tool_summary must point to L4.5 Pre-U bridge milestone")
        else:
            report.fail("generated snapshot missing readonly_tool_summary")

        tool_bridge_summary = snapshot.get("tool_bridge_summary")
        if tool_bridge_summary:
            report.pass_("generated snapshot contains tool_bridge_summary")
            for field in [
                "governed_tool_invocation_bridge_defined",
                "bridge_contract_defined",
                "agent_tool_request_defined",
                "pre_u_tool_packet_defined",
                "governance_decision_defined",
                "bridge_authorization_defined",
                "tool_invoked_through_bridge",
                "direct_tool_invocation_rejected",
                "unsafe_bridge_request_rejected",
                "bridge_cieu_event_defined",
                "bridge_residual_delta_defined",
                "mission_bounded_autonomy_supported",
                "step_by_step_human_prompting_reduced",
                "first_governed_tool_invocation_chain_created",
                "real_action_executed",
                "external_action_executed",
                "live_action_enabled",
                "network_enabled",
                "git_push_enabled",
                "daemon_control_enabled",
                "cieu_persistence_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "email_or_external_communication_enabled",
                "next_required_milestone",
                "generated_summary",
                "generated_contract",
                "generated_pre_u_packet",
                "generated_bridged_result",
                "generated_cieu_event",
                "warning",
            ]:
                if field in tool_bridge_summary:
                    report.pass_(f"snapshot tool_bridge_summary field present: {field}")
                else:
                    report.fail(f"snapshot tool_bridge_summary missing field: {field}")
            for field in [
                "governed_tool_invocation_bridge_defined",
                "bridge_contract_defined",
                "agent_tool_request_defined",
                "pre_u_tool_packet_defined",
                "governance_decision_defined",
                "bridge_authorization_defined",
                "tool_invoked_through_bridge",
                "direct_tool_invocation_rejected",
                "unsafe_bridge_request_rejected",
                "bridge_cieu_event_defined",
                "bridge_residual_delta_defined",
                "mission_bounded_autonomy_supported",
                "step_by_step_human_prompting_reduced",
                "first_governed_tool_invocation_chain_created",
            ]:
                if tool_bridge_summary.get(field) is not True:
                    report.fail(f"snapshot tool_bridge_summary must keep {field}=true")
            for field in [
                "real_action_executed",
                "external_action_executed",
                "live_action_enabled",
                "network_enabled",
                "git_push_enabled",
                "daemon_control_enabled",
                "cieu_persistence_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "email_or_external_communication_enabled",
            ]:
                if tool_bridge_summary.get(field) is not False:
                    report.fail(f"snapshot tool_bridge_summary must keep {field}=false")
            if tool_bridge_summary.get("next_required_milestone") != "L4.6 Agent Team Work Proposal to Governed Tool Invocation v0":
                report.fail("snapshot tool_bridge_summary must point to L4.6 agent proposal bridge milestone")
        else:
            report.fail("generated snapshot missing tool_bridge_summary")

        work_proposal_summary = snapshot.get("work_proposal_summary")
        if work_proposal_summary:
            report.pass_("generated snapshot contains work_proposal_summary")
            for field in [
                "agent_team_work_proposal_defined",
                "mission_context_snapshot_defined",
                "agent_team_observation_input_defined",
                "autonomous_work_proposals_defined",
                "selected_work_proposal_defined",
                "role_review_board_defined",
                "tool_need_analysis_defined",
                "generated_tool_request_defined",
                "work_proposal_routed_to_bridge",
                "bridge_runner_used",
                "direct_tool_invocation_used",
                "bridged_tool_result_ref_defined",
                "work_proposal_cieu_event_defined",
                "work_proposal_residual_delta_defined",
                "next_agent_work_recommendations_defined",
                "agent_team_generated_the_work",
                "agent_team_selected_governed_tool",
                "pre_u_bridge_required",
                "pre_u_bridge_satisfied",
                "real_action_executed",
                "external_action_executed",
                "live_action_enabled",
                "network_enabled",
                "git_push_enabled",
                "daemon_control_enabled",
                "cieu_persistence_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "email_or_external_communication_enabled",
                "next_required_milestone",
                "generated_summary",
                "generated_tool_request",
                "generated_bridge_trace",
                "generated_bridged_result_ref",
                "generated_cieu_event",
                "warning",
            ]:
                if field in work_proposal_summary:
                    report.pass_(f"snapshot work_proposal_summary field present: {field}")
                else:
                    report.fail(f"snapshot work_proposal_summary missing field: {field}")
            for field in [
                "agent_team_work_proposal_defined",
                "mission_context_snapshot_defined",
                "agent_team_observation_input_defined",
                "autonomous_work_proposals_defined",
                "selected_work_proposal_defined",
                "role_review_board_defined",
                "tool_need_analysis_defined",
                "generated_tool_request_defined",
                "work_proposal_routed_to_bridge",
                "bridge_runner_used",
                "bridged_tool_result_ref_defined",
                "work_proposal_cieu_event_defined",
                "work_proposal_residual_delta_defined",
                "next_agent_work_recommendations_defined",
                "agent_team_generated_the_work",
                "agent_team_selected_governed_tool",
                "pre_u_bridge_required",
                "pre_u_bridge_satisfied",
            ]:
                if work_proposal_summary.get(field) is not True:
                    report.fail(f"snapshot work_proposal_summary must keep {field}=true")
            for field in [
                "direct_tool_invocation_used",
                "real_action_executed",
                "external_action_executed",
                "live_action_enabled",
                "network_enabled",
                "git_push_enabled",
                "daemon_control_enabled",
                "cieu_persistence_enabled",
                "brain_writeback_enabled",
                "memory_ingestion_enabled",
                "email_or_external_communication_enabled",
            ]:
                if work_proposal_summary.get(field) is not False:
                    report.fail(f"snapshot work_proposal_summary must keep {field}=false")
            if work_proposal_summary.get("next_required_milestone") != "L4.7 First Mission Dashboard Refresh Loop v0":
                report.fail("snapshot work_proposal_summary must point to L4.7 mission dashboard milestone")
        else:
            report.fail("generated snapshot missing work_proposal_summary")

    quarantine = generated_json.get("console_read_model/generated/quarantine_summary.json")
    if quarantine:
        for field in [
            "framework_status",
            "current_mining_level",
            "artifacts_classified",
            "unsafe_artifacts_count",
            "classes_seen",
            "generated_manifest_ref",
            "forbidden_direct_reads",
            "future_adapter_candidates",
            "safety_warning",
        ]:
            if field in quarantine:
                report.pass_(f"generated quarantine summary field present: {field}")
            else:
                report.fail(f"generated quarantine summary missing field: {field}")

    safe_mining = generated_json.get("console_read_model/generated/safe_mining_summary.json")
    if safe_mining:
        for field in [
            "candidate_count",
            "classes_seen",
            "generated_candidate_index",
            "safety_level",
            "ingestion_status",
            "allowed_next_step",
            "forbidden_next_step",
            "warning",
        ]:
            if field in safe_mining:
                report.pass_(f"generated safe mining summary field present: {field}")
            else:
                report.fail(f"generated safe mining summary missing field: {field}")
        if safe_mining.get("ingestion_status") != "candidate_only":
            report.fail("generated safe mining summary must remain candidate_only")
        if safe_mining.get("forbidden_next_step") != "direct_brain_writeback":
            report.fail("generated safe mining summary must forbid direct brain writeback")

    review_queue = generated_json.get("console_read_model/generated/review_queue_summary.json")
    if review_queue:
        for field in [
            "review_count",
            "statuses",
            "intended_use_summary",
            "generated_queue_path",
            "default_review_status",
            "default_ingestion_status",
            "forbidden_actions",
            "warning",
        ]:
            if field in review_queue:
                report.pass_(f"generated review queue summary field present: {field}")
            else:
                report.fail(f"generated review queue summary missing field: {field}")
        if review_queue.get("default_review_status") != "pending_review":
            report.fail("generated review queue summary must remain pending_review")
        if review_queue.get("default_ingestion_status") != "not_ingested":
            report.fail("generated review queue summary must remain not_ingested")
        forbidden_actions = set(review_queue.get("forbidden_actions", []))
        for action in ["direct_brain_writeback", "direct_memory_ingestion", "direct_cieu_write"]:
            if action in forbidden_actions:
                report.pass_(f"generated review queue forbids action: {action}")
            else:
                report.fail(f"generated review queue missing forbidden action: {action}")

    disposition = generated_json.get("console_read_model/generated/artifact_disposition_summary.json")
    if disposition:
        for field in [
            "total_artifacts",
            "artifacts_with_disposition",
            "dispositions",
            "safe_mined_to_review_queue",
            "deferred_adapter_counts",
            "forbidden_direct_read_count",
            "evidence_scoring_status",
            "generated_disposition_index",
            "warning",
        ]:
            if field in disposition:
                report.pass_(f"generated artifact disposition summary field present: {field}")
            else:
                report.fail(f"generated artifact disposition summary missing field: {field}")
        if disposition.get("total_artifacts") != disposition.get("artifacts_with_disposition"):
            report.fail("generated artifact disposition summary must cover every manifest artifact")
        evidence = set(disposition.get("evidence_scoring_status", {}))
        if evidence and evidence != {"not_started"}:
            report.fail("generated artifact disposition evidence scoring must remain not_started")

    evidence_review = generated_json.get("console_read_model/generated/evidence_review_summary.json")
    if evidence_review:
        for field in [
            "candidates_scored",
            "decision_stubs_created",
            "routes_created",
            "reuse_readiness",
            "route_counts",
            "semantic_truth_status",
            "automatic_approvals",
            "brain_writeback_allowed",
            "memory_ingestion_allowed",
            "cieu_write_allowed",
            "warning",
        ]:
            if field in evidence_review:
                report.pass_(f"generated evidence review summary field present: {field}")
            else:
                report.fail(f"generated evidence review summary missing field: {field}")
        if evidence_review.get("automatic_approvals") != 0:
            report.fail("generated evidence review summary must not contain automatic approvals")
        for field in ["brain_writeback_allowed", "memory_ingestion_allowed", "cieu_write_allowed"]:
            if evidence_review.get(field) != 0:
                report.fail(f"generated evidence review summary must not allow {field}")
        semantic = set(evidence_review.get("semantic_truth_status", {}))
        if semantic and semantic != {"not_evaluated"}:
            report.fail("generated evidence review semantic truth status must remain not_evaluated")

    governance_bridge = generated_json.get("console_read_model/generated/governance_bridge_summary.json")
    if governance_bridge:
        for field in [
            "latest_bridge_run_id",
            "source_task_id",
            "agent_id",
            "ystar_gov_cli_path",
            "ystar_gov_exit_code",
            "ystar_gov_decision",
            "allow_execution",
            "require_revision",
            "deny",
            "escalate",
            "dry_run_only",
            "non_execution_confirmation",
            "action_executed",
            "cieu_written",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "warning",
        ]:
            if field in governance_bridge:
                report.pass_(f"generated governance bridge summary field present: {field}")
            else:
                report.fail(f"generated governance bridge summary missing field: {field}")
        if governance_bridge.get("dry_run_only") is not True:
            report.fail("generated governance bridge summary must remain dry_run_only")
        if governance_bridge.get("non_execution_confirmation") is not True:
            report.fail("generated governance bridge summary must confirm non-execution")
        for field in [
            "action_executed",
            "cieu_written",
            "brain_writeback_performed",
            "memory_ingestion_performed",
        ]:
            if governance_bridge.get(field) is not False:
                report.fail(f"generated governance bridge summary must keep {field}=false")

    pre_u_governance = generated_json.get("console_read_model/generated/pre_u_governance_summary.json")
    if pre_u_governance:
        for field in [
            "packets_generated",
            "roles_covered",
            "decision_counts",
            "decisions_by_role",
            "dry_run_only",
            "action_executed",
            "cieu_written",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "warning",
        ]:
            if field in pre_u_governance:
                report.pass_(f"generated Pre-U governance summary field present: {field}")
            else:
                report.fail(f"generated Pre-U governance summary missing field: {field}")
        if set(pre_u_governance.get("roles_covered", [])) != set(required_agents):
            report.fail("generated Pre-U governance summary must cover required agents")
        if pre_u_governance.get("packets_generated") != len(required_agents):
            report.fail("generated Pre-U governance summary must include three generated packets")
        if pre_u_governance.get("dry_run_only") is not True:
            report.fail("generated Pre-U governance summary must remain dry_run_only")
        for field in ["action_executed", "cieu_written", "brain_writeback_performed", "memory_ingestion_performed"]:
            if pre_u_governance.get(field) is not False:
                report.fail(f"generated Pre-U governance summary must keep {field}=false")

    labs_acceptance = generated_json.get("console_read_model/generated/labs_acceptance_summary.json")
    if labs_acceptance:
        for field in [
            "accepted",
            "checks_passed",
            "checks_total",
            "roles_covered",
            "decision_counts",
            "action_executed",
            "cieu_written",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "raw_runtime_artifacts_ingested",
            "warning",
        ]:
            if field in labs_acceptance:
                report.pass_(f"generated labs acceptance summary field present: {field}")
            else:
                report.fail(f"generated labs acceptance summary missing field: {field}")
        roles = set(labs_acceptance.get("roles_covered", []))
        if roles and roles != set(required_agents):
            report.fail("generated labs acceptance summary must cover required agents when roles are present")
        for field in [
            "action_executed",
            "cieu_written",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "raw_runtime_artifacts_ingested",
        ]:
            if labs_acceptance.get(field) is not False:
                report.fail(f"generated labs acceptance summary must keep {field}=false")

    cross_repo_alignment = generated_json.get("console_read_model/generated/cross_repo_alignment_summary.json")
    if cross_repo_alignment:
        for field in [
            "alignment_accepted",
            "ystar_company_head",
            "ystar_company_head_summary",
            "ystar_gov_head",
            "ystar_gov_head_summary",
            "ystar_gov_endpoint_accepted",
            "labs_runtime_accepted",
            "roles_covered",
            "decision_counts",
            "safety_assertions",
            "warning",
        ]:
            if field in cross_repo_alignment:
                report.pass_(f"generated cross-repo alignment summary field present: {field}")
            else:
                report.fail(f"generated cross-repo alignment summary missing field: {field}")
        roles = set(cross_repo_alignment.get("roles_covered", []))
        if roles and roles != set(required_agents):
            report.fail("generated cross-repo alignment summary must cover required agents when roles are present")
        for name, value in cross_repo_alignment.get("safety_assertions", {}).items():
            if value is not True:
                report.fail(f"generated cross-repo alignment safety assertion must be true: {name}")

    live_readiness = generated_json.get("console_read_model/generated/live_readiness_summary.json")
    if live_readiness:
        for field in [
            "dry_run_governance_ready",
            "minimal_live_loop_ready",
            "minimal_live_loop_status",
            "recommended_next_phase",
            "live_action_execution_allowed",
            "live_cieu_write_allowed",
            "live_brain_writeback_allowed",
            "live_memory_ingestion_allowed",
            "candidate_auto_approval_allowed",
            "raw_artifact_ingestion_allowed",
            "blockers",
            "transition_backlog_items",
            "generated_report",
            "generated_transition_backlog",
            "warning",
        ]:
            if field in live_readiness:
                report.pass_(f"generated live readiness summary field present: {field}")
            else:
                report.fail(f"generated live readiness summary missing field: {field}")
        if live_readiness.get("minimal_live_loop_ready") is not False:
            report.fail("generated live readiness summary must keep minimal_live_loop_ready=false")
        if live_readiness.get("minimal_live_loop_status") != "blocked_until_required_gates_exist":
            report.fail("generated live readiness summary must keep minimal live loop blocked")
        for field in [
            "live_action_execution_allowed",
            "live_cieu_write_allowed",
            "live_brain_writeback_allowed",
            "live_memory_ingestion_allowed",
            "candidate_auto_approval_allowed",
            "raw_artifact_ingestion_allowed",
        ]:
            if live_readiness.get(field) is not False:
                report.fail(f"generated live readiness summary must keep {field}=false")

    live_boundary = generated_json.get("console_read_model/generated/live_boundary_summary.json")
    if live_boundary:
        for field in [
            "live_boundary_defined",
            "operator_approval_gate_defined",
            "action_sandbox_contract_defined",
            "rollback_policy_defined",
            "cieu_writer_boundary_defined",
            "live_action_execution_enabled",
            "cieu_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "raw_artifact_ingestion_enabled",
            "requires_manual_enablement",
            "minimal_live_loop_ready",
            "blocked_reason",
            "checklist_status_counts",
            "ready_or_enabled_checklist_items",
            "generated_manifest",
            "generated_checklist",
            "warning",
        ]:
            if field in live_boundary:
                report.pass_(f"generated live boundary summary field present: {field}")
            else:
                report.fail(f"generated live boundary summary missing field: {field}")
        for field in [
            "live_boundary_defined",
            "operator_approval_gate_defined",
            "action_sandbox_contract_defined",
            "rollback_policy_defined",
            "cieu_writer_boundary_defined",
            "requires_manual_enablement",
        ]:
            if live_boundary.get(field) is not True:
                report.fail(f"generated live boundary summary must keep {field}=true")
        for field in [
            "live_action_execution_enabled",
            "cieu_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "raw_artifact_ingestion_enabled",
            "minimal_live_loop_ready",
        ]:
            if live_boundary.get(field) is not False:
                report.fail(f"generated live boundary summary must keep {field}=false")
        if live_boundary.get("blocked_reason") != "required_live_gates_defined_but_disabled":
            report.fail("generated live boundary summary must keep live boundary blocked")
        if live_boundary.get("ready_or_enabled_checklist_items") != 0:
            report.fail("generated live boundary summary must not include ready/enabled checklist items")

    cieu_boundary = generated_json.get("console_read_model/generated/cieu_boundary_summary.json")
    if cieu_boundary:
        for field in [
            "cieu_runtime_boundary_defined",
            "cieu_runtime_event_schema_defined",
            "prediction_delta_fixture_defined",
            "cieu_writer_policy_defined",
            "dry_run_only",
            "persistence_enabled",
            "live_action_execution_enabled",
            "cieu_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "raw_artifact_ingestion_enabled",
            "requires_manual_enablement",
            "minimal_live_loop_ready",
            "blocked_reason",
            "generated_manifest",
            "generated_sample_event",
            "generated_prediction_delta_fixture",
            "warning",
        ]:
            if field in cieu_boundary:
                report.pass_(f"generated CIEU boundary summary field present: {field}")
            else:
                report.fail(f"generated CIEU boundary summary missing field: {field}")
        for field in [
            "cieu_runtime_boundary_defined",
            "cieu_runtime_event_schema_defined",
            "prediction_delta_fixture_defined",
            "cieu_writer_policy_defined",
            "dry_run_only",
            "requires_manual_enablement",
        ]:
            if cieu_boundary.get(field) is not True:
                report.fail(f"generated CIEU boundary summary must keep {field}=true")
        for field in [
            "persistence_enabled",
            "live_action_execution_enabled",
            "cieu_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "raw_artifact_ingestion_enabled",
            "minimal_live_loop_ready",
        ]:
            if cieu_boundary.get(field) is not False:
                report.fail(f"generated CIEU boundary summary must keep {field}=false")
        if cieu_boundary.get("blocked_reason") != "cieu_runtime_boundary_defined_but_persistence_disabled":
            report.fail("generated CIEU boundary summary must keep persistence disabled")

    autonomy_inventory = generated_json.get("console_read_model/generated/autonomy_inventory_summary.json")
    if autonomy_inventory:
        for field in [
            "company_autonomy_inventory_defined",
            "repo_archaeology_completed",
            "observation_capability_map_defined",
            "resource_sensing_map_defined",
            "action_capability_map_defined",
            "governed_tool_registry_candidates_defined",
            "agent_role_capability_matrix_defined",
            "commercial_agent_company_goal_aligned",
            "governance_only_runtime",
            "live_actions_enabled",
            "external_actions_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "cieu_persistence_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "email_or_external_communication_enabled",
            "requires_manual_enablement",
            "next_required_milestone",
            "generated_summary",
            "generated_report",
            "warning",
        ]:
            if field in autonomy_inventory:
                report.pass_(f"generated autonomy inventory summary field present: {field}")
            else:
                report.fail(f"generated autonomy inventory summary missing field: {field}")
        for field in [
            "company_autonomy_inventory_defined",
            "repo_archaeology_completed",
            "observation_capability_map_defined",
            "resource_sensing_map_defined",
            "action_capability_map_defined",
            "governed_tool_registry_candidates_defined",
            "agent_role_capability_matrix_defined",
            "commercial_agent_company_goal_aligned",
            "requires_manual_enablement",
        ]:
            if autonomy_inventory.get(field) is not True:
                report.fail(f"generated autonomy inventory summary must keep {field}=true")
        for field in [
            "governance_only_runtime",
            "live_actions_enabled",
            "external_actions_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "cieu_persistence_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "email_or_external_communication_enabled",
        ]:
            if autonomy_inventory.get(field) is not False:
                report.fail(f"generated autonomy inventory summary must keep {field}=false")
        if autonomy_inventory.get("next_required_milestone") != "L4.2 Company Autonomous Work Cycle Simulator v0":
            report.fail("generated autonomy inventory summary must point to L4.2 simulator milestone")

    autonomous_cycle = generated_json.get("console_read_model/generated/autonomous_cycle_summary.json")
    if autonomous_cycle:
        for field in [
            "autonomous_work_cycle_defined",
            "mission_bounded_autonomy_defined",
            "founder_sets_mission_agent_team_drives",
            "step_by_step_human_prompting_required",
            "observation_snapshot_defined",
            "autonomous_work_backlog_defined",
            "selected_work_item_defined",
            "role_delegation_defined",
            "governed_tool_selection_defined",
            "pre_u_packet_simulated",
            "governance_decision_simulated",
            "action_plan_simulated",
            "cieu_event_simulated",
            "residual_delta_simulated",
            "next_task_recommendations_defined",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
            "requires_manual_enablement_for_live",
            "next_required_milestone",
            "generated_summary",
            "generated_report",
            "warning",
        ]:
            if field in autonomous_cycle:
                report.pass_(f"generated autonomous cycle summary field present: {field}")
            else:
                report.fail(f"generated autonomous cycle summary missing field: {field}")
        for field in [
            "autonomous_work_cycle_defined",
            "mission_bounded_autonomy_defined",
            "founder_sets_mission_agent_team_drives",
            "observation_snapshot_defined",
            "autonomous_work_backlog_defined",
            "selected_work_item_defined",
            "role_delegation_defined",
            "governed_tool_selection_defined",
            "pre_u_packet_simulated",
            "governance_decision_simulated",
            "action_plan_simulated",
            "cieu_event_simulated",
            "residual_delta_simulated",
            "next_task_recommendations_defined",
            "requires_manual_enablement_for_live",
        ]:
            if autonomous_cycle.get(field) is not True:
                report.fail(f"generated autonomous cycle summary must keep {field}=true")
        for field in [
            "step_by_step_human_prompting_required",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
        ]:
            if autonomous_cycle.get(field) is not False:
                report.fail(f"generated autonomous cycle summary must keep {field}=false")
        if autonomous_cycle.get("next_required_milestone") != "L4.3 Governed Read-Only Observation Loop v0":
            report.fail("generated autonomous cycle summary must point to L4.3 observation-loop milestone")

    legacy_triage = generated_json.get("console_read_model/generated/legacy_triage_summary.json")
    if legacy_triage:
        for field in [
            "legacy_asset_triage_defined",
            "assets_scored",
            "absorption_buckets_defined",
            "bucket_counts",
            "top_absorption_candidates_defined",
            "governed_absorption_backlog_defined",
            "blind_absorption_allowed",
            "blanket_rewrite_allowed",
            "live_actions_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_report",
            "warning",
        ]:
            if field in legacy_triage:
                report.pass_(f"generated legacy triage summary field present: {field}")
            else:
                report.fail(f"generated legacy triage summary missing field: {field}")
        for field in [
            "legacy_asset_triage_defined",
            "absorption_buckets_defined",
            "top_absorption_candidates_defined",
            "governed_absorption_backlog_defined",
        ]:
            if legacy_triage.get(field) is not True:
                report.fail(f"generated legacy triage summary must keep {field}=true")
        for field in ["blind_absorption_allowed", "blanket_rewrite_allowed", "live_actions_enabled"]:
            if legacy_triage.get(field) is not False:
                report.fail(f"generated legacy triage summary must keep {field}=false")
        if not legacy_triage.get("assets_scored", 0) > 0:
            report.fail("generated legacy triage summary must score assets")
        if legacy_triage.get("next_required_milestone") != "L4.4 First Governed Read-Only Observation Tool Wrapper v0":
            report.fail("generated legacy triage summary must point to L4.4 wrapper milestone")

    observation_loop = generated_json.get("console_read_model/generated/observation_loop_summary.json")
    if observation_loop:
        for field in [
            "governed_observation_loop_defined",
            "read_only_observation_loop_defined",
            "observation_source_registry_defined",
            "observation_tick_generated",
            "mission_dashboard_snapshot_defined",
            "company_state_digest_defined",
            "observation_to_work_item_candidates_defined",
            "mission_bounded_autonomy_supported",
            "step_by_step_human_prompting_reduced",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_report",
            "warning",
        ]:
            if field in observation_loop:
                report.pass_(f"generated observation loop summary field present: {field}")
            else:
                report.fail(f"generated observation loop summary missing field: {field}")
        for field in [
            "governed_observation_loop_defined",
            "read_only_observation_loop_defined",
            "observation_source_registry_defined",
            "observation_tick_generated",
            "mission_dashboard_snapshot_defined",
            "company_state_digest_defined",
            "observation_to_work_item_candidates_defined",
            "mission_bounded_autonomy_supported",
            "step_by_step_human_prompting_reduced",
        ]:
            if observation_loop.get(field) is not True:
                report.fail(f"generated observation loop summary must keep {field}=true")
        for field in [
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ]:
            if observation_loop.get(field) is not False:
                report.fail(f"generated observation loop summary must keep {field}=false")
        if observation_loop.get("next_required_milestone") != "L4.4 First Governed Read-Only Observation Tool Wrapper v0":
            report.fail("generated observation loop summary must point to L4.4 wrapper milestone")

    readonly_tool = generated_json.get("console_read_model/generated/readonly_tool_summary.json")
    if readonly_tool:
        for field in [
            "governed_readonly_observation_tool_defined",
            "tool_contract_defined",
            "allowed_source_registry_defined",
            "sample_invocation_defined",
            "sample_result_defined",
            "unsafe_invocation_rejected",
            "tool_cieu_event_defined",
            "local_readonly_dry_run_callable",
            "first_governed_tool_wrapper_created",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_contract",
            "generated_registry",
            "warning",
        ]:
            if field in readonly_tool:
                report.pass_(f"generated readonly tool summary field present: {field}")
            else:
                report.fail(f"generated readonly tool summary missing field: {field}")
        for field in [
            "governed_readonly_observation_tool_defined",
            "tool_contract_defined",
            "allowed_source_registry_defined",
            "sample_invocation_defined",
            "sample_result_defined",
            "unsafe_invocation_rejected",
            "tool_cieu_event_defined",
            "local_readonly_dry_run_callable",
            "first_governed_tool_wrapper_created",
        ]:
            if readonly_tool.get(field) is not True:
                report.fail(f"generated readonly tool summary must keep {field}=true")
        for field in [
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ]:
            if readonly_tool.get(field) is not False:
                report.fail(f"generated readonly tool summary must keep {field}=false")
        if readonly_tool.get("next_required_milestone") != "L4.5 Governed Tool Invocation Through Pre-U Bridge v0":
            report.fail("generated readonly tool summary must point to L4.5 Pre-U bridge milestone")

    tool_bridge = generated_json.get("console_read_model/generated/tool_bridge_summary.json")
    if tool_bridge:
        for field in [
            "governed_tool_invocation_bridge_defined",
            "bridge_contract_defined",
            "agent_tool_request_defined",
            "pre_u_tool_packet_defined",
            "governance_decision_defined",
            "bridge_authorization_defined",
            "tool_invoked_through_bridge",
            "direct_tool_invocation_rejected",
            "unsafe_bridge_request_rejected",
            "bridge_cieu_event_defined",
            "bridge_residual_delta_defined",
            "mission_bounded_autonomy_supported",
            "step_by_step_human_prompting_reduced",
            "first_governed_tool_invocation_chain_created",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "network_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_contract",
            "generated_pre_u_packet",
            "generated_bridged_result",
            "generated_cieu_event",
            "warning",
        ]:
            if field in tool_bridge:
                report.pass_(f"generated tool bridge summary field present: {field}")
            else:
                report.fail(f"generated tool bridge summary missing field: {field}")
        for field in [
            "governed_tool_invocation_bridge_defined",
            "bridge_contract_defined",
            "agent_tool_request_defined",
            "pre_u_tool_packet_defined",
            "governance_decision_defined",
            "bridge_authorization_defined",
            "tool_invoked_through_bridge",
            "direct_tool_invocation_rejected",
            "unsafe_bridge_request_rejected",
            "bridge_cieu_event_defined",
            "bridge_residual_delta_defined",
            "mission_bounded_autonomy_supported",
            "step_by_step_human_prompting_reduced",
            "first_governed_tool_invocation_chain_created",
        ]:
            if tool_bridge.get(field) is not True:
                report.fail(f"generated tool bridge summary must keep {field}=true")
        for field in [
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "network_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
        ]:
            if tool_bridge.get(field) is not False:
                report.fail(f"generated tool bridge summary must keep {field}=false")
        if tool_bridge.get("next_required_milestone") != "L4.6 Agent Team Work Proposal to Governed Tool Invocation v0":
            report.fail("generated tool bridge summary must point to L4.6 agent proposal bridge milestone")

    work_proposal = generated_json.get("console_read_model/generated/work_proposal_summary.json")
    if work_proposal:
        for field in [
            "agent_team_work_proposal_defined",
            "mission_context_snapshot_defined",
            "agent_team_observation_input_defined",
            "autonomous_work_proposals_defined",
            "selected_work_proposal_defined",
            "role_review_board_defined",
            "tool_need_analysis_defined",
            "generated_tool_request_defined",
            "work_proposal_routed_to_bridge",
            "bridge_runner_used",
            "direct_tool_invocation_used",
            "bridged_tool_result_ref_defined",
            "work_proposal_cieu_event_defined",
            "work_proposal_residual_delta_defined",
            "next_agent_work_recommendations_defined",
            "agent_team_generated_the_work",
            "agent_team_selected_governed_tool",
            "pre_u_bridge_required",
            "pre_u_bridge_satisfied",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "network_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_tool_request",
            "generated_bridge_trace",
            "generated_bridged_result_ref",
            "generated_cieu_event",
            "warning",
        ]:
            if field in work_proposal:
                report.pass_(f"generated work proposal summary field present: {field}")
            else:
                report.fail(f"generated work proposal summary missing field: {field}")
        for field in [
            "agent_team_work_proposal_defined",
            "mission_context_snapshot_defined",
            "agent_team_observation_input_defined",
            "autonomous_work_proposals_defined",
            "selected_work_proposal_defined",
            "role_review_board_defined",
            "tool_need_analysis_defined",
            "generated_tool_request_defined",
            "work_proposal_routed_to_bridge",
            "bridge_runner_used",
            "bridged_tool_result_ref_defined",
            "work_proposal_cieu_event_defined",
            "work_proposal_residual_delta_defined",
            "next_agent_work_recommendations_defined",
            "agent_team_generated_the_work",
            "agent_team_selected_governed_tool",
            "pre_u_bridge_required",
            "pre_u_bridge_satisfied",
        ]:
            if work_proposal.get(field) is not True:
                report.fail(f"generated work proposal summary must keep {field}=true")
        for field in [
            "direct_tool_invocation_used",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "network_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
        ]:
            if work_proposal.get(field) is not False:
                report.fail(f"generated work proposal summary must keep {field}=false")
        if work_proposal.get("next_required_milestone") != "L4.7 First Mission Dashboard Refresh Loop v0":
            report.fail("generated work proposal summary must point to L4.7 mission dashboard milestone")

    dashboard_refresh = generated_json.get("console_read_model/generated/dashboard_refresh_summary.json")
    if dashboard_refresh:
        for field in [
            "mission_dashboard_refresh_loop_defined",
            "refresh_loop_contract_defined",
            "previous_dashboard_snapshot_defined",
            "current_observation_input_defined",
            "refreshed_mission_dashboard_defined",
            "company_state_delta_defined",
            "refreshed_autonomous_backlog_defined",
            "refresh_loop_trace_defined",
            "refresh_cieu_event_defined",
            "refresh_residual_delta_defined",
            "next_loop_recommendations_defined",
            "mission_bounded_autonomy_supported",
            "founder_sets_mission_agent_team_drives",
            "step_by_step_human_prompting_required",
            "dashboard_refresh_loop_ran",
            "scheduler_used",
            "daemon_used",
            "manual_local_run_only",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "network_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_contract",
            "generated_refreshed_dashboard",
            "generated_company_state_delta",
            "generated_cieu_event",
            "warning",
        ]:
            if field in dashboard_refresh:
                report.pass_(f"generated dashboard refresh summary field present: {field}")
            else:
                report.fail(f"generated dashboard refresh summary missing field: {field}")
        for field in [
            "mission_dashboard_refresh_loop_defined",
            "refresh_loop_contract_defined",
            "previous_dashboard_snapshot_defined",
            "current_observation_input_defined",
            "refreshed_mission_dashboard_defined",
            "company_state_delta_defined",
            "refreshed_autonomous_backlog_defined",
            "refresh_loop_trace_defined",
            "refresh_cieu_event_defined",
            "refresh_residual_delta_defined",
            "next_loop_recommendations_defined",
            "mission_bounded_autonomy_supported",
            "founder_sets_mission_agent_team_drives",
            "dashboard_refresh_loop_ran",
            "manual_local_run_only",
        ]:
            if dashboard_refresh.get(field) is not True:
                report.fail(f"generated dashboard refresh summary must keep {field}=true")
        for field in [
            "step_by_step_human_prompting_required",
            "scheduler_used",
            "daemon_used",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "network_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
        ]:
            if dashboard_refresh.get(field) is not False:
                report.fail(f"generated dashboard refresh summary must keep {field}=false")
        if dashboard_refresh.get("next_required_milestone") != (
            "L4.8 Governed Recurring Observation Loop Contract v0"
        ):
            report.fail("generated dashboard refresh summary must point to L4.8 recurring loop milestone")

    recurring_loop = generated_json.get("console_read_model/generated/recurring_loop_summary.json")
    if recurring_loop:
        for field in [
            "recurring_observation_loop_contract_defined",
            "recurrence_policy_defined",
            "recurrence_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "auto_run_enabled",
            "manual_local_simulation_only",
            "allowed_observation_sources_defined",
            "tick_governance_gate_defined",
            "simulated_observation_tick_defined",
            "simulated_tick_dashboard_delta_defined",
            "simulated_tick_work_candidates_defined",
            "simulated_tick_cieu_event_defined",
            "simulated_tick_residual_delta_defined",
            "stop_abort_conditions_defined",
            "escalation_conditions_defined",
            "manual_enablement_checklist_defined",
            "mission_bounded_autonomy_supported",
            "founder_sets_mission_agent_team_drives",
            "step_by_step_human_prompting_required",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "network_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_contract",
            "generated_allowed_sources",
            "generated_tick",
            "generated_cieu_event",
            "generated_residual_delta",
            "warning",
        ]:
            if field in recurring_loop:
                report.pass_(f"generated recurring loop summary field present: {field}")
            else:
                report.fail(f"generated recurring loop summary missing field: {field}")
        for field in [
            "recurring_observation_loop_contract_defined",
            "recurrence_policy_defined",
            "manual_local_simulation_only",
            "allowed_observation_sources_defined",
            "tick_governance_gate_defined",
            "simulated_observation_tick_defined",
            "simulated_tick_dashboard_delta_defined",
            "simulated_tick_work_candidates_defined",
            "simulated_tick_cieu_event_defined",
            "simulated_tick_residual_delta_defined",
            "stop_abort_conditions_defined",
            "escalation_conditions_defined",
            "manual_enablement_checklist_defined",
            "mission_bounded_autonomy_supported",
            "founder_sets_mission_agent_team_drives",
        ]:
            if recurring_loop.get(field) is not True:
                report.fail(f"generated recurring loop summary must keep {field}=true")
        for field in [
            "recurrence_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "auto_run_enabled",
            "step_by_step_human_prompting_required",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "network_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
        ]:
            if recurring_loop.get(field) is not False:
                report.fail(f"generated recurring loop summary must keep {field}=false")
        if recurring_loop.get("next_required_milestone") != (
            "L4.9 Manual Recurring Observation Tick Runner v0"
        ):
            report.fail("generated recurring loop summary must point to L4.9 manual tick runner milestone")

    manual_tick = generated_json.get("console_read_model/generated/manual_tick_summary.json")
    if manual_tick:
        for field in [
            "manual_recurring_observation_tick_runner_defined",
            "manual_tick_runner_contract_defined",
            "manual_tick_request_defined",
            "manual_tick_preflight_defined",
            "manual_tick_source_validation_defined",
            "manual_tick_governance_decision_defined",
            "manual_tick_result_defined",
            "manual_tick_dashboard_delta_defined",
            "manual_tick_work_candidates_defined",
            "manual_tick_cieu_event_defined",
            "manual_tick_residual_delta_defined",
            "manual_tick_run_receipt_defined",
            "manual_tick_history_index_defined",
            "manual_tick_next_recommendations_defined",
            "manual_trigger_required",
            "one_tick_per_invocation",
            "total_recorded_ticks",
            "mission_bounded_autonomy_supported",
            "founder_sets_mission_agent_team_drives",
            "step_by_step_human_prompting_required",
            "recurrence_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "auto_run_enabled",
            "manual_local_run_only",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "network_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_contract",
            "generated_request",
            "generated_result",
            "generated_receipt",
            "generated_history",
            "generated_cieu_event",
            "generated_residual_delta",
            "warning",
        ]:
            if field in manual_tick:
                report.pass_(f"generated manual tick summary field present: {field}")
            else:
                report.fail(f"generated manual tick summary missing field: {field}")
        for field in [
            "manual_recurring_observation_tick_runner_defined",
            "manual_tick_runner_contract_defined",
            "manual_tick_request_defined",
            "manual_tick_preflight_defined",
            "manual_tick_source_validation_defined",
            "manual_tick_governance_decision_defined",
            "manual_tick_result_defined",
            "manual_tick_dashboard_delta_defined",
            "manual_tick_work_candidates_defined",
            "manual_tick_cieu_event_defined",
            "manual_tick_residual_delta_defined",
            "manual_tick_run_receipt_defined",
            "manual_tick_history_index_defined",
            "manual_tick_next_recommendations_defined",
            "manual_trigger_required",
            "one_tick_per_invocation",
            "mission_bounded_autonomy_supported",
            "founder_sets_mission_agent_team_drives",
            "manual_local_run_only",
        ]:
            if manual_tick.get(field) is not True:
                report.fail(f"generated manual tick summary must keep {field}=true")
        for field in [
            "step_by_step_human_prompting_required",
            "recurrence_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "auto_run_enabled",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "network_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
        ]:
            if manual_tick.get(field) is not False:
                report.fail(f"generated manual tick summary must keep {field}=false")
        if manual_tick.get("total_recorded_ticks") != 1:
            report.fail("generated manual tick summary must record exactly one tick")
        if manual_tick.get("next_required_milestone") != (
            "L5.0 Review-Gated Learning Candidate Queue v0"
        ):
            report.fail("generated manual tick summary must point to L5.0 review-gated learning milestone")

    field_functional = generated_json.get("console_read_model/generated/field_functional_summary.json")
    if field_functional:
        for field in [
            "field_functional_archaeology_defined",
            "repos_scanned",
            "assets_scanned",
            "field_functional_assets_found",
            "reuse_candidates_count",
            "wrap_candidates_count",
            "rewrite_candidates_count",
            "concept_reference_count",
            "do_not_absorb_count",
            "old_field_functional_work_found",
            "mission_projection_merge_plan_defined",
            "ready_for_L5_projection_harness",
            "live_action_enabled",
            "external_action_enabled",
            "network_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_inventory",
            "generated_merge_plan",
            "warning",
        ]:
            if field in field_functional:
                report.pass_(f"generated field functional summary field present: {field}")
            else:
                report.fail(f"generated field functional summary missing field: {field}")
        for field in [
            "field_functional_archaeology_defined",
            "old_field_functional_work_found",
            "mission_projection_merge_plan_defined",
            "ready_for_L5_projection_harness",
        ]:
            if field_functional.get(field) is not True:
                report.fail(f"generated field functional summary must keep {field}=true")
        for field in [
            "live_action_enabled",
            "external_action_enabled",
            "network_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ]:
            if field_functional.get(field) is not False:
                report.fail(f"generated field functional summary must keep {field}=false")
        if field_functional.get("field_functional_assets_found", 0) <= 0:
            report.fail("generated field functional summary must find at least one asset")
        if field_functional.get("next_required_milestone") != (
            "L5.1 Mission Field Functional Projection Harness v0"
        ):
            report.fail("generated field functional summary must point to L5.1 projection harness milestone")

    mission_projection = generated_json.get("console_read_model/generated/mission_projection_summary.json")
    if mission_projection:
        for field in [
            "mission_field_projection_harness_defined",
            "l5_1_projection_contract_defined",
            "layered_projection_trace_generated",
            "pre_u_adapter_candidate_generated",
            "residual_delta_fixture_generated",
            "action_layer_projection_only",
            "action_field_execution_implemented",
            "ready_for_L5_2_field_functional_auto_projection_core",
            "deep_xt_model_is_not_l5_2_main_milestone",
            "live_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_contract",
            "generated_trace",
            "generated_pre_u_candidate",
            "generated_residual_delta",
            "warning",
        ]:
            if field in mission_projection:
                report.pass_(f"generated mission projection summary field present: {field}")
            else:
                report.fail(f"generated mission projection summary missing field: {field}")
        for field in [
            "mission_field_projection_harness_defined",
            "l5_1_projection_contract_defined",
            "layered_projection_trace_generated",
            "pre_u_adapter_candidate_generated",
            "residual_delta_fixture_generated",
            "action_layer_projection_only",
            "ready_for_L5_2_field_functional_auto_projection_core",
            "deep_xt_model_is_not_l5_2_main_milestone",
        ]:
            if mission_projection.get(field) is not True:
                report.fail(f"generated mission projection summary must keep {field}=true")
        for field in [
            "action_field_execution_implemented",
            "live_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
        ]:
            if mission_projection.get(field) is not False:
                report.fail(f"generated mission projection summary must keep {field}=false")
        if mission_projection.get("next_required_milestone") != (
            "L5.2 Field Functional Auto-Projection Core v0"
        ):
            report.fail("generated mission projection summary must point to L5.2 auto-projection core milestone")

    field_projection = generated_json.get("console_read_model/generated/field_projection_summary.json")
    if field_projection:
        for field in [
            "field_functional_auto_projection_core_defined",
            "projection_operator_defined",
            "mission_level_y_star_input_defined",
            "mission_to_behavior_projection_generated",
            "projection_layers",
            "behavior_level_y_star_candidate_generated",
            "pre_u_packet_candidate_from_behavior_y_star_generated",
            "residual_delta_loop_fixture_generated",
            "learning_candidate_stub_generated_but_not_approved",
            "live_execution_still_blocked",
            "writeback_still_blocked",
            "external_action_still_blocked",
            "ready_for_l5_3_projection_checked_autonomous_cycle",
            "l6_revenue_opportunity_discovery_enabled",
            "dry_run_only",
            "pre_u_production_ready",
            "live_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "behavior_execution_enabled",
            "next_required_milestone",
            "generated_operator_summary",
            "generated_projection_summary",
            "generated_behavior_candidate",
            "generated_pre_u_candidate",
            "generated_residual_loop_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in field_projection:
                report.pass_(f"generated field projection summary field present: {field}")
            else:
                report.fail(f"generated field projection summary missing field: {field}")
        for field in [
            "field_functional_auto_projection_core_defined",
            "projection_operator_defined",
            "mission_level_y_star_input_defined",
            "mission_to_behavior_projection_generated",
            "behavior_level_y_star_candidate_generated",
            "pre_u_packet_candidate_from_behavior_y_star_generated",
            "residual_delta_loop_fixture_generated",
            "learning_candidate_stub_generated_but_not_approved",
            "live_execution_still_blocked",
            "writeback_still_blocked",
            "external_action_still_blocked",
            "ready_for_l5_3_projection_checked_autonomous_cycle",
            "dry_run_only",
        ]:
            if field_projection.get(field) is not True:
                report.fail(f"generated field projection summary must keep {field}=true")
        if field_projection.get("projection_layers") != [
            "mission",
            "company",
            "milestone",
            "session",
            "task",
            "behavior",
        ]:
            report.fail("generated field projection summary must use mission/company/milestone/session/task/behavior layers")
        for field in [
            "l6_revenue_opportunity_discovery_enabled",
            "pre_u_production_ready",
            "live_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "behavior_execution_enabled",
        ]:
            if field_projection.get(field) is not False:
                report.fail(f"generated field projection summary must keep {field}=false")
        if field_projection.get("next_required_milestone") != (
            "L5.3 Projection-Checked Autonomous Work Cycle v0"
        ):
            report.fail("generated field projection summary must point to L5.3 projection-checked cycle milestone")

    projection_cycle = generated_json.get("console_read_model/generated/projection_cycle_summary.json")
    if projection_cycle:
        for field in [
            "projection_checked_autonomous_work_cycle_defined",
            "behavior_y_star_consumed_by_cycle",
            "work_proposal_checked_against_behavior_y_star",
            "pre_u_packet_candidate_generated",
            "dry_run_gate_decision_generated",
            "dry_run_result_generated",
            "cieu_like_event_fixture_generated",
            "residual_delta_generated",
            "learning_review_candidate_generated_but_not_approved",
            "projection_gate_decision",
            "cycle_pre_u_gate_decision",
            "dry_run_only",
            "pre_u_production_ready",
            "real_execution_performed",
            "event_mode",
            "db_write_performed",
            "live_execution_still_blocked",
            "writeback_still_blocked",
            "external_action_still_blocked",
            "ready_for_l5_4_review_gated_learning_loop",
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
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "next_required_milestone",
            "generated_cycle_summary",
            "generated_work_summary",
            "generated_pre_u_summary",
            "generated_result_summary",
            "generated_residual_summary",
            "generated_learning_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in projection_cycle:
                report.pass_(f"generated projection cycle summary field present: {field}")
            else:
                report.fail(f"generated projection cycle summary missing field: {field}")
        for field in [
            "projection_checked_autonomous_work_cycle_defined",
            "behavior_y_star_consumed_by_cycle",
            "work_proposal_checked_against_behavior_y_star",
            "pre_u_packet_candidate_generated",
            "dry_run_gate_decision_generated",
            "dry_run_result_generated",
            "cieu_like_event_fixture_generated",
            "residual_delta_generated",
            "learning_review_candidate_generated_but_not_approved",
            "live_execution_still_blocked",
            "writeback_still_blocked",
            "external_action_still_blocked",
            "ready_for_l5_4_review_gated_learning_loop",
            "dry_run_only",
        ]:
            if projection_cycle.get(field) is not True:
                report.fail(f"generated projection cycle summary must keep {field}=true")
        for field in [
            "pre_u_production_ready",
            "real_execution_performed",
            "db_write_performed",
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
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
        ]:
            if projection_cycle.get(field) is not False:
                report.fail(f"generated projection cycle summary must keep {field}=false")
        if projection_cycle.get("next_required_milestone") != "L5.4 Review-Gated Learning Loop v0":
            report.fail("generated projection cycle summary must point to L5.4 review-gated learning loop")

    shadow_learning_cycle = generated_json.get(
        "console_read_model/generated/shadow_learning_cycle_summary.json"
    )
    if shadow_learning_cycle:
        for field in [
            "integrated_review_gated_shadow_learning_cycle_defined",
            "l5_3_residual_consumed",
            "deterministic_review_gate_decision_generated",
            "review_gate_decision",
            "learning_target_classification_generated",
            "projection_policy_update_candidate_generated",
            "shadow_projection_policy_patch_generated",
            "shadow_behavior_y_star_preview_generated",
            "shadow_updated_projection_cycle_generated",
            "shadow_cycle_cieu_fixture_generated",
            "original_vs_shadow_cycle_comparison_generated",
            "integrated_cieu_like_fixture_generated",
            "candidate_approved",
            "candidate_applied",
            "canonical_policy_mutation_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "previous_residual_influenced_shadow_projection",
            "ready_for_controlled_canonical_learning_design",
            "ready_for_l6_revenue_opportunity_discovery",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "candidate_auto_approval_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "shadow_patch_live_application_enabled",
            "shadow_patch_preview_only",
            "shadow_cycle_real_execution_performed",
            "shadow_cycle_db_write_performed",
            "integrated_cieu_db_write_performed",
            "next_required_milestone",
            "generated_loop_summary",
            "generated_review_summary",
            "generated_target_summary",
            "generated_update_summary",
            "generated_shadow_patch_summary",
            "generated_reprojection_summary",
            "generated_shadow_cycle_summary",
            "generated_shadow_residual_summary",
            "generated_integrated_cieu_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in shadow_learning_cycle:
                report.pass_(f"generated shadow learning cycle summary field present: {field}")
            else:
                report.fail(f"generated shadow learning cycle summary missing field: {field}")
        for field in [
            "integrated_review_gated_shadow_learning_cycle_defined",
            "l5_3_residual_consumed",
            "deterministic_review_gate_decision_generated",
            "learning_target_classification_generated",
            "projection_policy_update_candidate_generated",
            "shadow_projection_policy_patch_generated",
            "shadow_behavior_y_star_preview_generated",
            "shadow_updated_projection_cycle_generated",
            "shadow_cycle_cieu_fixture_generated",
            "original_vs_shadow_cycle_comparison_generated",
            "integrated_cieu_like_fixture_generated",
            "previous_residual_influenced_shadow_projection",
            "ready_for_controlled_canonical_learning_design",
            "shadow_patch_preview_only",
        ]:
            if shadow_learning_cycle.get(field) is not True:
                report.fail(f"generated shadow learning cycle summary must keep {field}=true")
        for field in [
            "candidate_approved",
            "candidate_applied",
            "canonical_policy_mutation_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "ready_for_l6_revenue_opportunity_discovery",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "candidate_auto_approval_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "shadow_patch_live_application_enabled",
            "shadow_cycle_real_execution_performed",
            "shadow_cycle_db_write_performed",
            "integrated_cieu_db_write_performed",
        ]:
            if shadow_learning_cycle.get(field) is not False:
                report.fail(f"generated shadow learning cycle summary must keep {field}=false")
        if shadow_learning_cycle.get("review_gate_decision") != "eligible_for_shadow_update_candidate":
            report.fail("generated shadow learning cycle review gate must allow shadow update only")
        if shadow_learning_cycle.get("next_required_milestone") != (
            "Controlled Canonical Learning Architecture v0"
        ):
            report.fail("generated shadow learning cycle summary must point to controlled canonical learning")

    cross_repo_governance = generated_json.get(
        "console_read_model/generated/cross_repo_governance_summary.json"
    )
    if cross_repo_governance:
        for field in [
            "cross_repo_governance_contract_proof_defined",
            "y_star_gov_surfaces_inventoried_read_only",
            "gov_mcp_surfaces_inventoried_read_only",
            "behavior_y_star_mapped_to_governance_contract",
            "pre_u_candidates_mapped_to_validator_expectations",
            "cieu_fixtures_mapped_to_prediction_delta_expectations",
            "gov_mcp_boundary_mapped",
            "non_bypass_invariants_defined",
            "bypass_risks_identified",
            "no_non_ystar_company_repo_modified",
            "no_mcp_server_or_tool_executed",
            "ready_for_l5_6_governed_mcp_dry_run_adapter",
            "ready_for_l6_revenue_opportunity_discovery",
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
            "next_required_milestone",
            "generated_contract_summary",
            "generated_y_star_gov_surface_summary",
            "generated_alignment_summary",
            "generated_gov_mcp_surface_summary",
            "generated_governed_mcp_interface_summary",
            "generated_non_bypass_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in cross_repo_governance:
                report.pass_(f"generated cross-repo governance summary field present: {field}")
            else:
                report.fail(f"generated cross-repo governance summary missing field: {field}")
        for field in [
            "cross_repo_governance_contract_proof_defined",
            "y_star_gov_surfaces_inventoried_read_only",
            "gov_mcp_surfaces_inventoried_read_only",
            "behavior_y_star_mapped_to_governance_contract",
            "pre_u_candidates_mapped_to_validator_expectations",
            "cieu_fixtures_mapped_to_prediction_delta_expectations",
            "gov_mcp_boundary_mapped",
            "non_bypass_invariants_defined",
            "bypass_risks_identified",
            "no_non_ystar_company_repo_modified",
            "no_mcp_server_or_tool_executed",
            "ready_for_l5_6_governed_mcp_dry_run_adapter",
        ]:
            if cross_repo_governance.get(field) is not True:
                report.fail(f"generated cross-repo governance summary must keep {field}=true")
        for field in [
            "ready_for_l6_revenue_opportunity_discovery",
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
        ]:
            if cross_repo_governance.get(field) is not False:
                report.fail(f"generated cross-repo governance summary must keep {field}=false")
        if cross_repo_governance.get("next_required_milestone") != (
            "L5.6 Governed MCP Dry-Run Adapter v0"
        ):
            report.fail("generated cross-repo governance summary must point to L5.6")

    governed_mcp_adapter = generated_json.get(
        "console_read_model/generated/governed_mcp_adapter_summary.json"
    )
    if governed_mcp_adapter:
        for field in [
            "l5_6_governed_mcp_dry_run_adapter_defined",
            "behavior_y_star_loaded",
            "mcp_request_intent_generated",
            "mcp_pre_u_packet_candidate_generated",
            "dry_run_governance_decision_envelope_generated",
            "bridge_authorization_receipt_generated",
            "governed_mcp_call_candidate_generated",
            "real_mcp_execution_blocked",
            "mcp_dry_run_receipt_generated",
            "mcp_cieu_like_event_generated",
            "mcp_residual_delta_generated",
            "review_only_mcp_learning_candidate_generated",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "mcp_server_not_started",
            "mcp_tool_not_executed",
            "mcp_resource_not_mutated",
            "ready_for_l5_7_controlled_canonical_learning_design",
            "ready_for_l6_revenue_opportunity_discovery",
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
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "mcp_resource_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "next_required_milestone",
            "generated_adapter_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in governed_mcp_adapter:
                report.pass_(f"generated governed MCP adapter summary field present: {field}")
            else:
                report.fail(f"generated governed MCP adapter summary missing field: {field}")
        for field in [
            "l5_6_governed_mcp_dry_run_adapter_defined",
            "behavior_y_star_loaded",
            "mcp_request_intent_generated",
            "mcp_pre_u_packet_candidate_generated",
            "dry_run_governance_decision_envelope_generated",
            "bridge_authorization_receipt_generated",
            "governed_mcp_call_candidate_generated",
            "real_mcp_execution_blocked",
            "mcp_dry_run_receipt_generated",
            "mcp_cieu_like_event_generated",
            "mcp_residual_delta_generated",
            "review_only_mcp_learning_candidate_generated",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "mcp_server_not_started",
            "mcp_tool_not_executed",
            "mcp_resource_not_mutated",
            "ready_for_l5_7_controlled_canonical_learning_design",
        ]:
            if governed_mcp_adapter.get(field) is not True:
                report.fail(f"generated governed MCP adapter summary must keep {field}=true")
        for field in [
            "ready_for_l6_revenue_opportunity_discovery",
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
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "mcp_resource_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
        ]:
            if governed_mcp_adapter.get(field) is not False:
                report.fail(f"generated governed MCP adapter summary must keep {field}=false")
        if governed_mcp_adapter.get("next_required_milestone") != (
            "L5.7 Controlled Canonical Learning Design v0"
        ):
            report.fail("generated governed MCP adapter summary must point to L5.7")

    controlled_canonical_learning = generated_json.get(
        "console_read_model/generated/controlled_canonical_learning_summary.json"
    )
    if controlled_canonical_learning:
        for field in [
            "l5_7_controlled_canonical_learning_design_defined",
            "y_star_non_mutation_invariant_defined",
            "canonical_learning_target_registry_generated",
            "promotion_evidence_bundle_generated",
            "promotion_eligibility_gate_generated",
            "canonical_update_package_candidate_generated",
            "versioned_patch_plan_generated",
            "rollback_audit_plan_generated",
            "post_promotion_validation_plan_generated",
            "dry_run_promotion_fixture_generated",
            "candidate_approved",
            "candidate_applied",
            "canonical_policy_mutation_performed",
            "canonical_update_application_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "strategy_mutation_performed",
            "y_star_direct_mutation_performed",
            "actual_canonical_application_blocked",
            "candidate_approval_blocked",
            "brain_writeback_blocked",
            "memory_ingestion_blocked",
            "y_star_direct_mutation_blocked",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "ready_for_l5_8_approved_canonical_update_sandbox",
            "ready_for_l6_revenue_opportunity_discovery",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "canonical_policy_mutation_enabled",
            "canonical_update_application_enabled",
            "y_star_direct_mutation_enabled",
            "y_star_gov_modification_enabled",
            "gov_mcp_modification_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "next_required_milestone",
            "generated_design_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in controlled_canonical_learning:
                report.pass_(f"generated controlled canonical learning summary field present: {field}")
            else:
                report.fail(f"generated controlled canonical learning summary missing field: {field}")
        for field in [
            "l5_7_controlled_canonical_learning_design_defined",
            "y_star_non_mutation_invariant_defined",
            "canonical_learning_target_registry_generated",
            "promotion_evidence_bundle_generated",
            "promotion_eligibility_gate_generated",
            "canonical_update_package_candidate_generated",
            "versioned_patch_plan_generated",
            "rollback_audit_plan_generated",
            "post_promotion_validation_plan_generated",
            "dry_run_promotion_fixture_generated",
            "actual_canonical_application_blocked",
            "candidate_approval_blocked",
            "brain_writeback_blocked",
            "memory_ingestion_blocked",
            "y_star_direct_mutation_blocked",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "ready_for_l5_8_approved_canonical_update_sandbox",
        ]:
            if controlled_canonical_learning.get(field) is not True:
                report.fail(f"generated controlled canonical learning summary must keep {field}=true")
        for field in [
            "candidate_approved",
            "candidate_applied",
            "canonical_policy_mutation_performed",
            "canonical_update_application_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "strategy_mutation_performed",
            "y_star_direct_mutation_performed",
            "ready_for_l6_revenue_opportunity_discovery",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "canonical_policy_mutation_enabled",
            "canonical_update_application_enabled",
            "y_star_direct_mutation_enabled",
            "y_star_gov_modification_enabled",
            "gov_mcp_modification_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
        ]:
            if controlled_canonical_learning.get(field) is not False:
                report.fail(f"generated controlled canonical learning summary must keep {field}=false")
        if controlled_canonical_learning.get("next_required_milestone") != (
            "L5.8 Approved Canonical Update Sandbox v0"
        ):
            report.fail("generated controlled canonical learning summary must point to L5.8")

    approved_sandbox_update = generated_json.get(
        "console_read_model/generated/approved_sandbox_update_summary.json"
    )
    if approved_sandbox_update:
        for field in [
            "l5_8_approved_canonical_update_sandbox_defined",
            "sandbox_approval_fixture_generated",
            "sandbox_application_approved",
            "real_application_approved",
            "candidate_real_approved",
            "sandbox_baseline_generated",
            "sandbox_patch_applied",
            "real_canonical_state_unchanged",
            "y_star_non_mutation_invariant_preserved",
            "sandbox_post_update_validation_generated",
            "sandbox_post_update_validation_passed",
            "sandbox_behavior_y_star_reprojection_generated",
            "sandbox_governed_mcp_preview_generated",
            "sandbox_update_cieu_like_fixture_generated",
            "sandbox_update_residual_delta_generated",
            "sandbox_rollback_validation_generated",
            "rollback_restored_baseline",
            "original_vs_sandbox_vs_rollback_comparison_generated",
            "sandbox_update_effect_class",
            "previous_residual_influenced_sandbox_projection",
            "real_candidate_approved",
            "real_candidate_applied",
            "real_canonical_policy_mutation_performed",
            "real_canonical_update_application_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "strategy_mutation_performed",
            "direct_y_star_mutation_performed",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "ready_for_l5_9_real_approval_workflow_boundary",
            "ready_for_l6_revenue_opportunity_discovery",
            "next_required_milestone",
            "generated_sandbox_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in approved_sandbox_update:
                report.pass_(f"generated approved sandbox update summary field present: {field}")
            else:
                report.fail(f"generated approved sandbox update summary missing field: {field}")
        for field in [
            "l5_8_approved_canonical_update_sandbox_defined",
            "sandbox_approval_fixture_generated",
            "sandbox_application_approved",
            "sandbox_baseline_generated",
            "sandbox_patch_applied",
            "real_canonical_state_unchanged",
            "y_star_non_mutation_invariant_preserved",
            "sandbox_post_update_validation_generated",
            "sandbox_post_update_validation_passed",
            "sandbox_behavior_y_star_reprojection_generated",
            "sandbox_governed_mcp_preview_generated",
            "sandbox_update_cieu_like_fixture_generated",
            "sandbox_update_residual_delta_generated",
            "sandbox_rollback_validation_generated",
            "rollback_restored_baseline",
            "original_vs_sandbox_vs_rollback_comparison_generated",
            "previous_residual_influenced_sandbox_projection",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "ready_for_l5_9_real_approval_workflow_boundary",
        ]:
            if approved_sandbox_update.get(field) is not True:
                report.fail(f"generated approved sandbox update summary must keep {field}=true")
        for field in [
            "real_application_approved",
            "candidate_real_approved",
            "real_candidate_approved",
            "real_candidate_applied",
            "real_canonical_policy_mutation_performed",
            "real_canonical_update_application_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "strategy_mutation_performed",
            "direct_y_star_mutation_performed",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "ready_for_l6_revenue_opportunity_discovery",
        ]:
            if approved_sandbox_update.get(field) is not False:
                report.fail(f"generated approved sandbox update summary must keep {field}=false")
        if approved_sandbox_update.get("next_required_milestone") != (
            "L5.9 Real Approval Workflow Boundary v0"
        ):
            report.fail("generated approved sandbox update summary must point to L5.9")

    real_approval_workflow = generated_json.get(
        "console_read_model/generated/real_approval_workflow_summary.json"
    )
    if real_approval_workflow:
        for field in [
            "l5_9_real_approval_workflow_boundary_defined",
            "approval_authority_model_generated",
            "approval_evidence_dossier_generated",
            "durable_approval_record_contract_generated",
            "approval_decision_packet_fixture_generated",
            "validity_revocation_policy_generated",
            "pre_application_snapshot_policy_generated",
            "real_application_boundary_gate_generated",
            "post_approval_preflight_validation_plan_generated",
            "manual_approval_runbook_generated",
            "approval_workflow_cieu_like_fixture_generated",
            "real_approval_granted",
            "real_application_authorized",
            "approval_record_created_as_durable_record",
            "durable_approval_record_written",
            "durable_db_write_performed",
            "real_canonical_policy_mutation_performed",
            "real_canonical_update_application_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "strategy_mutation_performed",
            "direct_y_star_mutation_performed",
            "real_approval_still_blocked",
            "real_application_still_blocked",
            "durable_approval_persistence_still_blocked",
            "brain_writeback_still_blocked",
            "memory_ingestion_still_blocked",
            "y_star_direct_mutation_still_blocked",
            "mcp_execution_still_blocked",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "ready_for_l5_10_controlled_approval_record_sandbox",
            "ready_for_l6_revenue_opportunity_discovery",
            "next_required_milestone",
            "generated_workflow_summary",
            "generated_authority_summary",
            "generated_evidence_summary",
            "generated_record_summary",
            "generated_decision_summary",
            "generated_validity_summary",
            "generated_snapshot_summary",
            "generated_boundary_summary",
            "generated_preflight_summary",
            "generated_runbook_summary",
            "generated_audit_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in real_approval_workflow:
                report.pass_(f"generated real approval workflow summary field present: {field}")
            else:
                report.fail(f"generated real approval workflow summary missing field: {field}")
        for field in [
            "l5_9_real_approval_workflow_boundary_defined",
            "approval_authority_model_generated",
            "approval_evidence_dossier_generated",
            "durable_approval_record_contract_generated",
            "approval_decision_packet_fixture_generated",
            "validity_revocation_policy_generated",
            "pre_application_snapshot_policy_generated",
            "real_application_boundary_gate_generated",
            "post_approval_preflight_validation_plan_generated",
            "manual_approval_runbook_generated",
            "approval_workflow_cieu_like_fixture_generated",
            "real_approval_still_blocked",
            "real_application_still_blocked",
            "durable_approval_persistence_still_blocked",
            "brain_writeback_still_blocked",
            "memory_ingestion_still_blocked",
            "y_star_direct_mutation_still_blocked",
            "mcp_execution_still_blocked",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "ready_for_l5_10_controlled_approval_record_sandbox",
        ]:
            if real_approval_workflow.get(field) is not True:
                report.fail(f"generated real approval workflow summary must keep {field}=true")
        for field in [
            "real_approval_granted",
            "real_application_authorized",
            "approval_record_created_as_durable_record",
            "durable_approval_record_written",
            "durable_db_write_performed",
            "real_canonical_policy_mutation_performed",
            "real_canonical_update_application_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "strategy_mutation_performed",
            "direct_y_star_mutation_performed",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "ready_for_l6_revenue_opportunity_discovery",
        ]:
            if real_approval_workflow.get(field) is not False:
                report.fail(f"generated real approval workflow summary must keep {field}=false")
        if real_approval_workflow.get("next_required_milestone") != (
            "L5.10 Controlled Approval Record Sandbox v0"
        ):
            report.fail("generated real approval workflow summary must point to L5.10")

    controlled_approval_record = generated_json.get(
        "console_read_model/generated/approval_record_sandbox_summary.json"
    )
    if controlled_approval_record:
        for field in [
            "l5_10_controlled_approval_record_sandbox_defined",
            "sandbox_approval_record_instance_generated",
            "integrity_validation_generated",
            "integrity_validation_status",
            "validity_state_machine_replay_generated",
            "current_sandbox_state",
            "expired_revoked_tampered_wrong_scope_missing_evidence_blocked",
            "valid_sandbox_record_gate_replay_generated",
            "valid_record_gate_result",
            "invalid_record_gate_blocking_generated",
            "audit_lineage_generated",
            "approval_record_cieu_like_fixture_generated",
            "approval_record_residual_delta_generated",
            "real_approval_granted",
            "durable_approval_record_written",
            "real_application_authorized",
            "canonical_policy_mutation_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "direct_y_star_mutation_performed",
            "durable_persistence_still_blocked",
            "real_approval_still_blocked",
            "real_application_still_blocked",
            "brain_writeback_still_blocked",
            "memory_ingestion_still_blocked",
            "y_star_direct_mutation_still_blocked",
            "mcp_execution_still_blocked",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "real_approval_record_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "ready_for_l5_11_controlled_real_release_preflight",
            "ready_for_l6_revenue_opportunity_discovery",
            "next_required_milestone",
            "generated_sandbox_summary",
            "generated_record_summary",
            "generated_integrity_summary",
            "generated_state_machine_summary",
            "generated_revocation_summary",
            "generated_gate_summary",
            "generated_audit_summary",
            "generated_cieu_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in controlled_approval_record:
                report.pass_(f"generated controlled approval record summary field present: {field}")
            else:
                report.fail(f"generated controlled approval record summary missing field: {field}")
        for field in [
            "l5_10_controlled_approval_record_sandbox_defined",
            "sandbox_approval_record_instance_generated",
            "integrity_validation_generated",
            "validity_state_machine_replay_generated",
            "expired_revoked_tampered_wrong_scope_missing_evidence_blocked",
            "valid_sandbox_record_gate_replay_generated",
            "invalid_record_gate_blocking_generated",
            "audit_lineage_generated",
            "approval_record_cieu_like_fixture_generated",
            "approval_record_residual_delta_generated",
            "durable_persistence_still_blocked",
            "real_approval_still_blocked",
            "real_application_still_blocked",
            "brain_writeback_still_blocked",
            "memory_ingestion_still_blocked",
            "y_star_direct_mutation_still_blocked",
            "mcp_execution_still_blocked",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "ready_for_l5_11_controlled_real_release_preflight",
        ]:
            if controlled_approval_record.get(field) is not True:
                report.fail(f"generated controlled approval record summary must keep {field}=true")
        for field in [
            "real_approval_granted",
            "durable_approval_record_written",
            "real_application_authorized",
            "canonical_policy_mutation_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "direct_y_star_mutation_performed",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "real_approval_record_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "ready_for_l6_revenue_opportunity_discovery",
        ]:
            if controlled_approval_record.get(field) is not False:
                report.fail(f"generated controlled approval record summary must keep {field}=false")
        if controlled_approval_record.get("next_required_milestone") != (
            "L5.11 Controlled Real Release Preflight v0"
        ):
            report.fail("generated controlled approval record summary must point to L5.11")

    controlled_real_release = generated_json.get(
        "console_read_model/generated/real_release_preflight_summary.json"
    )
    if controlled_real_release:
        for field in [
            "l5_11_controlled_real_release_preflight_defined",
            "release_candidate_assembled",
            "release_scope_validation_generated",
            "release_scope_validation_status",
            "approval_record_preflight_generated",
            "approval_record_validation_status",
            "snapshot_rollback_preflight_generated",
            "snapshot_preflight_generated",
            "rollback_preflight_generated",
            "y_star_non_mutation_preflight_generated",
            "mcp_non_bypass_preflight_generated",
            "no_direct_writeback_preflight_generated",
            "post_release_validation_matrix_generated",
            "release_operator_handoff_packet_generated",
            "release_blocker_decision_generated",
            "release_blocker_decision",
            "release_preflight_cieu_like_fixture_generated",
            "release_preflight_residual_delta_generated",
            "real_approval_granted",
            "real_release_authorized",
            "real_application_authorized",
            "durable_approval_record_written",
            "canonical_policy_mutation_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "direct_y_star_mutation_performed",
            "real_release_still_blocked",
            "real_approval_still_blocked",
            "durable_persistence_still_blocked",
            "real_canonical_application_still_blocked",
            "brain_writeback_still_blocked",
            "memory_ingestion_still_blocked",
            "y_star_direct_mutation_still_blocked",
            "mcp_execution_still_blocked",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "real_approval_record_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_release_execution_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "ready_for_l5_12_real_release_simulation_sandbox",
            "ready_for_l6_revenue_opportunity_discovery",
            "next_required_milestone",
            "generated_preflight_summary",
            "generated_release_candidate_summary",
            "generated_scope_summary",
            "generated_approval_record_preflight_summary",
            "generated_snapshot_rollback_summary",
            "generated_invariant_summary",
            "generated_post_release_summary",
            "generated_handoff_summary",
            "generated_blocker_summary",
            "generated_cieu_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in controlled_real_release:
                report.pass_(f"generated controlled real release preflight summary field present: {field}")
            else:
                report.fail(f"generated controlled real release preflight summary missing field: {field}")
        for field in [
            "l5_11_controlled_real_release_preflight_defined",
            "release_candidate_assembled",
            "release_scope_validation_generated",
            "approval_record_preflight_generated",
            "snapshot_rollback_preflight_generated",
            "snapshot_preflight_generated",
            "rollback_preflight_generated",
            "y_star_non_mutation_preflight_generated",
            "mcp_non_bypass_preflight_generated",
            "no_direct_writeback_preflight_generated",
            "post_release_validation_matrix_generated",
            "release_operator_handoff_packet_generated",
            "release_blocker_decision_generated",
            "release_preflight_cieu_like_fixture_generated",
            "release_preflight_residual_delta_generated",
            "real_release_still_blocked",
            "real_approval_still_blocked",
            "durable_persistence_still_blocked",
            "real_canonical_application_still_blocked",
            "brain_writeback_still_blocked",
            "memory_ingestion_still_blocked",
            "y_star_direct_mutation_still_blocked",
            "mcp_execution_still_blocked",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "ready_for_l5_12_real_release_simulation_sandbox",
        ]:
            if controlled_real_release.get(field) is not True:
                report.fail(f"generated controlled real release preflight summary must keep {field}=true")
        for field in [
            "real_approval_granted",
            "real_release_authorized",
            "real_application_authorized",
            "durable_approval_record_written",
            "canonical_policy_mutation_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "direct_y_star_mutation_performed",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "real_approval_record_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_release_execution_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "ready_for_l6_revenue_opportunity_discovery",
        ]:
            if controlled_real_release.get(field) is not False:
                report.fail(f"generated controlled real release preflight summary must keep {field}=false")
        if controlled_real_release.get("next_required_milestone") != (
            "L5.12 Real Release Simulation Sandbox v0"
        ):
            report.fail("generated controlled real release preflight summary must point to L5.12")

    real_release_simulation = generated_json.get(
        "console_read_model/generated/real_release_simulation_summary.json"
    )
    if real_release_simulation:
        for field in [
            "l5_12_real_release_simulation_sandbox_defined",
            "sandbox_release_authority_fixture_generated",
            "simulated_durable_approval_record_generated",
            "sandbox_snapshot_generated",
            "simulated_release_operator_confirmed",
            "simulated_rollback_operator_confirmed",
            "sandbox_release_execution_plan_generated",
            "sandbox_release_execution_generated",
            "sandbox_release_executed",
            "real_canonical_state_unchanged",
            "sandbox_post_release_validation_generated",
            "sandbox_post_release_validation_status",
            "sandbox_post_release_projection_generated",
            "sandbox_mcp_preview_generated",
            "sandbox_rollback_drill_generated",
            "rollback_restored_baseline",
            "original_release_rollback_comparison_generated",
            "release_simulation_cieu_like_fixture_generated",
            "release_simulation_residual_delta_generated",
            "real_approval_granted",
            "real_release_authorized",
            "real_release_performed",
            "durable_approval_record_written",
            "canonical_policy_mutation_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "direct_y_star_mutation_performed",
            "real_release_still_blocked",
            "real_approval_still_blocked",
            "durable_persistence_still_blocked",
            "real_canonical_application_still_blocked",
            "brain_writeback_still_blocked",
            "memory_ingestion_still_blocked",
            "y_star_direct_mutation_still_blocked",
            "mcp_execution_still_blocked",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "real_approval_record_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_release_execution_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "ready_for_l5_13_live_boundary_no_go_decision_framework",
            "ready_for_l6_revenue_opportunity_discovery",
            "next_required_milestone",
            "generated_simulation_summary",
            "generated_authority_summary",
            "generated_simulated_record_summary",
            "generated_snapshot_summary",
            "generated_plan_summary",
            "generated_result_summary",
            "generated_validation_summary",
            "generated_projection_mcp_summary",
            "generated_rollback_summary",
            "generated_comparison_summary",
            "generated_cieu_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in real_release_simulation:
                report.pass_(f"generated real release simulation summary field present: {field}")
            else:
                report.fail(f"generated real release simulation summary missing field: {field}")
        for field in [
            "l5_12_real_release_simulation_sandbox_defined",
            "sandbox_release_authority_fixture_generated",
            "simulated_durable_approval_record_generated",
            "sandbox_snapshot_generated",
            "simulated_release_operator_confirmed",
            "simulated_rollback_operator_confirmed",
            "sandbox_release_execution_plan_generated",
            "sandbox_release_execution_generated",
            "sandbox_release_executed",
            "real_canonical_state_unchanged",
            "sandbox_post_release_validation_generated",
            "sandbox_post_release_projection_generated",
            "sandbox_mcp_preview_generated",
            "sandbox_rollback_drill_generated",
            "rollback_restored_baseline",
            "original_release_rollback_comparison_generated",
            "release_simulation_cieu_like_fixture_generated",
            "release_simulation_residual_delta_generated",
            "real_release_still_blocked",
            "real_approval_still_blocked",
            "durable_persistence_still_blocked",
            "real_canonical_application_still_blocked",
            "brain_writeback_still_blocked",
            "memory_ingestion_still_blocked",
            "y_star_direct_mutation_still_blocked",
            "mcp_execution_still_blocked",
            "y_star_gov_unmodified",
            "gov_mcp_unmodified",
            "ready_for_l5_13_live_boundary_no_go_decision_framework",
        ]:
            if real_release_simulation.get(field) is not True:
                report.fail(f"generated real release simulation summary must keep {field}=true")
        for field in [
            "real_approval_granted",
            "real_release_authorized",
            "real_release_performed",
            "durable_approval_record_written",
            "canonical_policy_mutation_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "direct_y_star_mutation_performed",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "real_approval_record_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_release_execution_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "ready_for_l6_revenue_opportunity_discovery",
        ]:
            if real_release_simulation.get(field) is not False:
                report.fail(f"generated real release simulation summary must keep {field}=false")
        if real_release_simulation.get("next_required_milestone") != (
            "L5.13 Live Boundary / No-Go Decision Framework v0"
        ):
            report.fail("generated real release simulation summary must point to L5.13")

    live_boundary_no_go = generated_json.get(
        "console_read_model/generated/live_boundary_no_go_summary.json"
    )
    if live_boundary_no_go:
        for field in [
            "l5_13_live_boundary_no_go_framework_defined",
            "live_capability_domains_classified",
            "no_go_invariants_defined",
            "l5_0_to_l5_12_evidence_indexed",
            "l5_evidence_index_generated",
            "live_blockers_identified",
            "l6_design_entry_gate_generated",
            "l6_non_execution_boundary_defined",
            "l6_forbidden_hardcoding_policy_defined",
            "system_no_go_decision_packet_generated",
            "live_boundary_cieu_like_fixture_generated",
            "live_execution_decision",
            "real_mcp_execution_decision",
            "real_canonical_update_decision",
            "brain_memory_writeback_decision",
            "durable_persistence_decision",
            "real_release_decision",
            "l6_design_entry_decision",
            "l6_execution_decision",
            "revenue_execution_decision",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "real_approval_record_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_release_execution_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "revenue_execution_enabled",
            "l6_design_entry_allowed",
            "l6_revenue_execution_allowed",
            "l6_external_observation_allowed",
            "l6_external_action_allowed",
            "l6_network_enabled",
            "l6_publication_enabled",
            "l6_payment_enabled",
            "live_execution_still_blocked",
            "real_mcp_execution_still_blocked",
            "real_canonical_update_still_blocked",
            "brain_writeback_still_blocked",
            "memory_ingestion_still_blocked",
            "durable_persistence_still_blocked",
            "real_release_still_blocked",
            "revenue_execution_still_blocked",
            "external_action_still_blocked",
            "network_still_blocked",
            "ready_for_l6_meta_development_generative_engine_design",
            "ready_for_l6_revenue_opportunity_execution",
            "next_required_milestone",
            "generated_framework_summary",
            "generated_capability_summary",
            "generated_invariant_summary",
            "generated_evidence_summary",
            "generated_blocker_summary",
            "generated_l6_entry_summary",
            "generated_decision_summary",
            "generated_cieu_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in live_boundary_no_go:
                report.pass_(f"generated live boundary no-go summary field present: {field}")
            else:
                report.fail(f"generated live boundary no-go summary missing field: {field}")
        for field in [
            "l5_13_live_boundary_no_go_framework_defined",
            "live_capability_domains_classified",
            "no_go_invariants_defined",
            "l5_0_to_l5_12_evidence_indexed",
            "l5_evidence_index_generated",
            "live_blockers_identified",
            "l6_design_entry_gate_generated",
            "l6_non_execution_boundary_defined",
            "l6_forbidden_hardcoding_policy_defined",
            "system_no_go_decision_packet_generated",
            "live_boundary_cieu_like_fixture_generated",
            "l6_design_entry_allowed",
            "live_execution_still_blocked",
            "real_mcp_execution_still_blocked",
            "real_canonical_update_still_blocked",
            "brain_writeback_still_blocked",
            "memory_ingestion_still_blocked",
            "durable_persistence_still_blocked",
            "real_release_still_blocked",
            "revenue_execution_still_blocked",
            "external_action_still_blocked",
            "network_still_blocked",
            "ready_for_l6_meta_development_generative_engine_design",
        ]:
            if live_boundary_no_go.get(field) is not True:
                report.fail(f"generated live boundary no-go summary must keep {field}=true")
        for field in [
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "real_approval_record_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_release_execution_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "revenue_execution_enabled",
            "l6_revenue_execution_allowed",
            "l6_external_observation_allowed",
            "l6_external_action_allowed",
            "l6_network_enabled",
            "l6_publication_enabled",
            "l6_payment_enabled",
            "ready_for_l6_revenue_opportunity_execution",
        ]:
            if live_boundary_no_go.get(field) is not False:
                report.fail(f"generated live boundary no-go summary must keep {field}=false")
        expected_decisions = {
            "live_execution_decision": "no_go",
            "real_mcp_execution_decision": "no_go",
            "real_canonical_update_decision": "no_go",
            "brain_memory_writeback_decision": "no_go",
            "durable_persistence_decision": "no_go",
            "real_release_decision": "no_go",
            "l6_design_entry_decision": "design_only_go",
            "l6_execution_decision": "no_go",
            "revenue_execution_decision": "no_go",
        }
        for field, expected_value in expected_decisions.items():
            if live_boundary_no_go.get(field) != expected_value:
                report.fail(
                    f"generated live boundary no-go summary expected {field}={expected_value}"
                )
        if live_boundary_no_go.get("next_required_milestone") != (
            "L6 Meta-Development Generative Engine Design v0"
        ):
            report.fail("generated live boundary no-go summary must point to L6 design")

    l6_meta_development = generated_json.get(
        "console_read_model/generated/l6_meta_development_summary.json"
    )
    if l6_meta_development:
        for field in [
            "l6_0_meta_development_generative_selection_engine_defined",
            "self_model_generated",
            "unique_asset_field_generated",
            "world_value_field_generated",
            "conversion_operator_library_generated",
            "value_hypotheses_generated",
            "non_hardcoding_check_generated",
            "conversion_physics_defined",
            "redeemability_selection_generated",
            "minimum_viable_proof_plans_generated",
            "governed_experiment_portfolio_generated",
            "strategic_residual_loop_generated",
            "l6_design_only",
            "hardcoded_opportunity_categories_forbidden",
            "seed_examples_non_exhaustive",
            "seed_examples_not_authorized_for_execution",
            "hypothesis_count",
            "selected_for_sandbox_design_count",
            "mvp_plan_count",
            "experiment_count",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "real_approval_record_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_release_execution_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "revenue_execution_enabled",
            "external_market_scan_enabled",
            "public_content_publication_enabled",
            "payment_enabled",
            "l6_design_only_enabled",
            "l6_hypothesis_generation_enabled",
            "l6_selection_design_enabled",
            "l6_sandbox_experiment_design_enabled",
            "l6_external_execution_enabled",
            "l6_network_enabled",
            "l6_publication_enabled",
            "l6_payment_enabled",
            "l6_revenue_execution_enabled",
            "l6_execution_still_blocked",
            "external_action_still_blocked",
            "network_still_blocked",
            "publication_still_blocked",
            "payment_still_blocked",
            "revenue_execution_still_blocked",
            "ready_for_l6_1_meta_development_mvp_artifact_sandbox",
            "ready_for_l6_revenue_opportunity_execution",
            "next_required_milestone",
            "generated_engine_summary",
            "generated_self_asset_summary",
            "generated_world_value_summary",
            "generated_operator_summary",
            "generated_hypothesis_summary",
            "generated_physics_summary",
            "generated_selection_summary",
            "generated_mvp_summary",
            "generated_portfolio_summary",
            "generated_residual_summary",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_meta_development:
                report.pass_(f"generated L6 meta-development summary field present: {field}")
            else:
                report.fail(f"generated L6 meta-development summary missing field: {field}")
        for field in [
            "l6_0_meta_development_generative_selection_engine_defined",
            "self_model_generated",
            "unique_asset_field_generated",
            "world_value_field_generated",
            "conversion_operator_library_generated",
            "value_hypotheses_generated",
            "non_hardcoding_check_generated",
            "conversion_physics_defined",
            "redeemability_selection_generated",
            "minimum_viable_proof_plans_generated",
            "governed_experiment_portfolio_generated",
            "strategic_residual_loop_generated",
            "l6_design_only",
            "hardcoded_opportunity_categories_forbidden",
            "seed_examples_non_exhaustive",
            "seed_examples_not_authorized_for_execution",
            "l6_design_only_enabled",
            "l6_hypothesis_generation_enabled",
            "l6_selection_design_enabled",
            "l6_sandbox_experiment_design_enabled",
            "l6_execution_still_blocked",
            "external_action_still_blocked",
            "network_still_blocked",
            "publication_still_blocked",
            "payment_still_blocked",
            "revenue_execution_still_blocked",
            "ready_for_l6_1_meta_development_mvp_artifact_sandbox",
        ]:
            if l6_meta_development.get(field) is not True:
                report.fail(f"generated L6 meta-development summary must keep {field}=true")
        for field in [
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "mcp_server_execution_enabled",
            "mcp_tool_execution_enabled",
            "cieu_persistence_enabled",
            "durable_approval_persistence_enabled",
            "real_approval_record_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "strategy_mutation_enabled",
            "candidate_auto_approval_enabled",
            "real_candidate_approval_enabled",
            "real_canonical_policy_mutation_enabled",
            "real_canonical_update_application_enabled",
            "real_release_execution_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "revenue_execution_enabled",
            "external_market_scan_enabled",
            "public_content_publication_enabled",
            "payment_enabled",
            "l6_external_execution_enabled",
            "l6_network_enabled",
            "l6_publication_enabled",
            "l6_payment_enabled",
            "l6_revenue_execution_enabled",
            "ready_for_l6_revenue_opportunity_execution",
        ]:
            if l6_meta_development.get(field) is not False:
                report.fail(f"generated L6 meta-development summary must keep {field}=false")
        if l6_meta_development.get("hypothesis_count", 0) < 12:
            report.fail("generated L6 meta-development summary must include at least 12 hypotheses")
        if l6_meta_development.get("next_required_milestone") != (
            "L6.1 Meta-Development MVP Artifact Sandbox v0"
        ):
            report.fail("generated L6 meta-development summary must point to L6.1")

    l6_mvp_artifact_sandbox = generated_json.get(
        "console_read_model/generated/l6_mvp_artifact_sandbox_summary.json"
    )
    if l6_mvp_artifact_sandbox:
        for field in [
            "l6_1_mvp_artifact_sandbox_defined",
            "selected_hypotheses_count",
            "generated_case_count",
            "internal_artifacts_generated",
            "artifact_generation_authorized",
            "review_gate_generated",
            "externalization_boundary_generated",
            "strategic_residual_loop_generated",
            "structural_validation_only",
            "semantic_truth_scoring_enabled",
            "network_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_1_sandbox_only",
            "l6_1_internal_artifact_generation_enabled",
            "l6_1_artifact_review_gate_required",
            "l6_1_external_execution_enabled",
            "l6_1_network_enabled",
            "l6_1_publication_enabled",
            "l6_1_outreach_enabled",
            "l6_1_payment_enabled",
            "l6_1_revenue_execution_enabled",
            "ready_for_l6_2_external_observation_boundary_design",
            "ready_for_external_execution",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
            "next_recommended_milestone",
            "generated_milestone_summary",
            "generated_selected_hypotheses",
            "generated_case_index",
            "generated_validation_matrix",
            "generated_review_gate",
            "generated_externalization_blocker",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_mvp_artifact_sandbox:
                report.pass_(f"generated L6.1 MVP artifact sandbox summary field present: {field}")
            else:
                report.fail(f"generated L6.1 MVP artifact sandbox summary missing field: {field}")
        for field in [
            "l6_1_mvp_artifact_sandbox_defined",
            "internal_artifacts_generated",
            "artifact_generation_authorized",
            "review_gate_generated",
            "externalization_boundary_generated",
            "strategic_residual_loop_generated",
            "structural_validation_only",
            "l6_1_sandbox_only",
            "l6_1_internal_artifact_generation_enabled",
            "l6_1_artifact_review_gate_required",
            "ready_for_l6_2_external_observation_boundary_design",
        ]:
            if l6_mvp_artifact_sandbox.get(field) is not True:
                report.fail(f"generated L6.1 MVP artifact sandbox summary must keep {field}=true")
        for field in [
            "semantic_truth_scoring_enabled",
            "network_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_1_external_execution_enabled",
            "l6_1_network_enabled",
            "l6_1_publication_enabled",
            "l6_1_outreach_enabled",
            "l6_1_payment_enabled",
            "l6_1_revenue_execution_enabled",
            "ready_for_external_execution",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
        ]:
            if l6_mvp_artifact_sandbox.get(field) is not False:
                report.fail(f"generated L6.1 MVP artifact sandbox summary must keep {field}=false")
        if not 1 <= l6_mvp_artifact_sandbox.get("selected_hypotheses_count", 0) <= 3:
            report.fail("generated L6.1 summary must select between 1 and 3 hypotheses")
        if l6_mvp_artifact_sandbox.get("generated_case_count") != (
            l6_mvp_artifact_sandbox.get("selected_hypotheses_count")
        ):
            report.fail("generated L6.1 summary case count must match selected count")
        if l6_mvp_artifact_sandbox.get("next_recommended_milestone") != (
            "L6.2 Governed External Observation Boundary v0"
        ):
            report.fail("generated L6.1 summary must point to L6.2 boundary design")

    l6_external_observation_boundary = generated_json.get(
        "console_read_model/generated/l6_external_observation_boundary_summary.json"
    )
    if l6_external_observation_boundary:
        for field in [
            "l6_2_external_observation_boundary_defined",
            "boundary_only",
            "sandbox_only",
            "pre_observation_packet_schema_defined",
            "pre_observation_required_fields_count",
            "source_registry_defined",
            "source_type_count",
            "permission_gate_defined",
            "manual_import_sandbox_defined",
            "observation_to_artifact_linker_defined",
            "claim_boundary_policy_defined",
            "no_action_receipts_generated",
            "strategic_residual_loop_generated",
            "static_fixture_generation_authorized",
            "manual_evidence_import_contract_authorized",
            "real_external_observation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_2_boundary_only",
            "l6_2_sandbox_only",
            "l6_2_real_external_observation_enabled",
            "l6_2_network_enabled",
            "l6_2_api_enabled",
            "l6_2_scraping_enabled",
            "l6_2_browser_fetch_enabled",
            "ready_for_l6_3_controlled_external_observation_sandbox",
            "ready_for_real_network_observation",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
            "next_recommended_milestone",
            "generated_milestone_summary",
            "generated_packet_schema",
            "generated_source_registry",
            "generated_permission_gate",
            "generated_manual_import_contract",
            "generated_no_action_receipt",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_external_observation_boundary:
                report.pass_(f"generated L6.2 external observation boundary summary field present: {field}")
            else:
                report.fail(f"generated L6.2 external observation boundary summary missing field: {field}")
        for field in [
            "l6_2_external_observation_boundary_defined",
            "boundary_only",
            "sandbox_only",
            "pre_observation_packet_schema_defined",
            "source_registry_defined",
            "permission_gate_defined",
            "manual_import_sandbox_defined",
            "observation_to_artifact_linker_defined",
            "claim_boundary_policy_defined",
            "no_action_receipts_generated",
            "strategic_residual_loop_generated",
            "static_fixture_generation_authorized",
            "manual_evidence_import_contract_authorized",
            "l6_2_boundary_only",
            "l6_2_sandbox_only",
            "ready_for_l6_3_controlled_external_observation_sandbox",
        ]:
            if l6_external_observation_boundary.get(field) is not True:
                report.fail(f"generated L6.2 summary must keep {field}=true")
        for field in [
            "real_external_observation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_2_real_external_observation_enabled",
            "l6_2_network_enabled",
            "l6_2_api_enabled",
            "l6_2_scraping_enabled",
            "l6_2_browser_fetch_enabled",
            "ready_for_real_network_observation",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
        ]:
            if l6_external_observation_boundary.get(field) is not False:
                report.fail(f"generated L6.2 summary must keep {field}=false")
        if l6_external_observation_boundary.get("pre_observation_required_fields_count", 0) < 30:
            report.fail("generated L6.2 summary must include complete Pre-Observation packet fields")
        if l6_external_observation_boundary.get("source_type_count", 0) < 10:
            report.fail("generated L6.2 summary must include source type registry entries")
        if l6_external_observation_boundary.get("next_recommended_milestone") != (
            "L6.3 Controlled External Observation Sandbox v0"
        ):
            report.fail("generated L6.2 summary must point to L6.3")

    l6_controlled_observation_sandbox = generated_json.get(
        "console_read_model/generated/l6_controlled_observation_sandbox_summary.json"
    )
    if l6_controlled_observation_sandbox:
        for field in [
            "l6_3_controlled_observation_sandbox_defined",
            "sandbox_only",
            "fixture_only",
            "static_fixture_observation_authorized",
            "manual_import_fixture_authorized",
            "real_external_observation_authorized",
            "selected_observation_case_count",
            "pre_observation_packet_count",
            "static_manual_fixture_count",
            "permission_replay_generated",
            "evidence_validation_generated",
            "claim_freshness_assessment_generated",
            "refinement_candidates_generated",
            "refinement_candidate_count",
            "review_packets_generated",
            "review_packet_count",
            "no_action_receipts_generated",
            "strategic_residual_loop_generated",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_3_sandbox_only",
            "l6_3_fixture_only",
            "l6_3_static_fixture_observation_enabled",
            "l6_3_manual_import_fixture_enabled",
            "l6_3_real_external_observation_enabled",
            "l6_3_network_enabled",
            "l6_3_api_enabled",
            "l6_3_scraping_enabled",
            "l6_3_browser_fetch_enabled",
            "l6_3_artifact_refinement_application_enabled",
            "ready_for_l6_4_real_read_only_external_observation_preflight",
            "ready_for_real_network_observation",
            "ready_for_scraping",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
            "next_recommended_milestone",
            "generated_milestone_summary",
            "generated_selected_cases",
            "generated_packet_index",
            "generated_permission_replay",
            "generated_fixture_index",
            "generated_refinement_candidates",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_controlled_observation_sandbox:
                report.pass_(f"generated L6.3 controlled observation summary field present: {field}")
            else:
                report.fail(f"generated L6.3 controlled observation summary missing field: {field}")
        for field in [
            "l6_3_controlled_observation_sandbox_defined",
            "sandbox_only",
            "fixture_only",
            "static_fixture_observation_authorized",
            "manual_import_fixture_authorized",
            "permission_replay_generated",
            "evidence_validation_generated",
            "claim_freshness_assessment_generated",
            "refinement_candidates_generated",
            "review_packets_generated",
            "no_action_receipts_generated",
            "strategic_residual_loop_generated",
            "l6_3_sandbox_only",
            "l6_3_fixture_only",
            "l6_3_static_fixture_observation_enabled",
            "l6_3_manual_import_fixture_enabled",
            "ready_for_l6_4_real_read_only_external_observation_preflight",
        ]:
            if l6_controlled_observation_sandbox.get(field) is not True:
                report.fail(f"generated L6.3 summary must keep {field}=true")
        for field in [
            "real_external_observation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_3_real_external_observation_enabled",
            "l6_3_network_enabled",
            "l6_3_api_enabled",
            "l6_3_scraping_enabled",
            "l6_3_browser_fetch_enabled",
            "l6_3_artifact_refinement_application_enabled",
            "ready_for_real_network_observation",
            "ready_for_scraping",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
        ]:
            if l6_controlled_observation_sandbox.get(field) is not False:
                report.fail(f"generated L6.3 summary must keep {field}=false")
        if not 1 <= l6_controlled_observation_sandbox.get("selected_observation_case_count", 0) <= 3:
            report.fail("generated L6.3 summary must select between 1 and 3 observation cases")
        if l6_controlled_observation_sandbox.get("pre_observation_packet_count") != (
            l6_controlled_observation_sandbox.get("selected_observation_case_count")
        ):
            report.fail("generated L6.3 packet count must match selected observation case count")
        if l6_controlled_observation_sandbox.get("static_manual_fixture_count") != (
            l6_controlled_observation_sandbox.get("selected_observation_case_count")
        ):
            report.fail("generated L6.3 fixture count must match selected observation case count")
        if l6_controlled_observation_sandbox.get("next_recommended_milestone") != (
            "L6.4 Real Read-Only External Observation Preflight v0"
        ):
            report.fail("generated L6.3 summary must point to L6.4")

    l6_real_observation_preflight = generated_json.get(
        "console_read_model/generated/l6_real_observation_preflight_summary.json"
    )
    if l6_real_observation_preflight:
        for field in [
            "l6_4_real_read_only_observation_preflight_defined",
            "preflight_only",
            "sandbox_only",
            "future_real_read_only_observation_candidate_allowed",
            "candidate_count",
            "approval_packet_count",
            "preflight_requirement_count",
            "source_allowlist_defined",
            "source_denylist_defined",
            "operator_handoff_plan_generated",
            "network_isolation_preflight_defined",
            "evidence_capture_preflight_defined",
            "abort_rollback_quarantine_policy_defined",
            "no_action_guarantees_generated",
            "preflight_decision_gate_generated",
            "strategic_residual_loop_generated",
            "real_external_observation_authorized",
            "real_observation_execution_authorized",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_4_preflight_only",
            "l6_4_sandbox_only",
            "l6_4_future_real_read_only_observation_candidate_allowed",
            "l6_4_approval_packet_generation_enabled",
            "l6_4_operator_handoff_plan_enabled",
            "l6_4_evidence_capture_plan_enabled",
            "l6_4_real_observation_execution_enabled",
            "l6_4_network_enabled",
            "l6_4_api_enabled",
            "l6_4_scraping_enabled",
            "l6_4_browser_fetch_enabled",
            "ready_for_l6_5_controlled_real_read_only_observation_pilot_design",
            "ready_for_actual_network_observation_now",
            "ready_for_scraping",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
            "next_recommended_milestone",
            "generated_milestone_summary",
            "generated_selected_candidates",
            "generated_preflight_contract",
            "generated_source_allowlist",
            "generated_approval_packets",
            "generated_operator_handoff",
            "generated_network_isolation",
            "generated_evidence_capture",
            "generated_decision_gate",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_real_observation_preflight:
                report.pass_(f"generated L6.4 real observation preflight summary field present: {field}")
            else:
                report.fail(f"generated L6.4 real observation preflight summary missing field: {field}")
        for field in [
            "l6_4_real_read_only_observation_preflight_defined",
            "preflight_only",
            "sandbox_only",
            "future_real_read_only_observation_candidate_allowed",
            "source_allowlist_defined",
            "source_denylist_defined",
            "operator_handoff_plan_generated",
            "network_isolation_preflight_defined",
            "evidence_capture_preflight_defined",
            "abort_rollback_quarantine_policy_defined",
            "no_action_guarantees_generated",
            "preflight_decision_gate_generated",
            "strategic_residual_loop_generated",
            "l6_4_preflight_only",
            "l6_4_sandbox_only",
            "l6_4_future_real_read_only_observation_candidate_allowed",
            "l6_4_approval_packet_generation_enabled",
            "l6_4_operator_handoff_plan_enabled",
            "l6_4_evidence_capture_plan_enabled",
            "ready_for_l6_5_controlled_real_read_only_observation_pilot_design",
        ]:
            if l6_real_observation_preflight.get(field) is not True:
                report.fail(f"generated L6.4 summary must keep {field}=true")
        for field in [
            "real_external_observation_authorized",
            "real_observation_execution_authorized",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_4_real_observation_execution_enabled",
            "l6_4_network_enabled",
            "l6_4_api_enabled",
            "l6_4_scraping_enabled",
            "l6_4_browser_fetch_enabled",
            "ready_for_actual_network_observation_now",
            "ready_for_scraping",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
        ]:
            if l6_real_observation_preflight.get(field) is not False:
                report.fail(f"generated L6.4 summary must keep {field}=false")
        if not 1 <= l6_real_observation_preflight.get("candidate_count", 0) <= 3:
            report.fail("generated L6.4 summary must select between 1 and 3 candidates")
        if l6_real_observation_preflight.get("approval_packet_count") != (
            l6_real_observation_preflight.get("candidate_count")
        ):
            report.fail("generated L6.4 approval packet count must match candidate count")
        if l6_real_observation_preflight.get("next_recommended_milestone") != (
            "L6.5 Controlled Real Read-Only Observation Pilot Design v0"
        ):
            report.fail("generated L6.4 summary must point to L6.5")

    l6_pilot_design = generated_json.get(
        "console_read_model/generated/l6_pilot_design_summary.json"
    )
    if l6_pilot_design:
        for field in [
            "l6_5_controlled_real_read_only_observation_pilot_design_defined",
            "pilot_design_only",
            "preflight_only",
            "future_real_read_only_observation_pilot_candidate_allowed",
            "candidate_count",
            "approval_packet_count",
            "pilot_scope_defined",
            "pilot_source_constraints_defined",
            "pilot_approval_packet_candidates_generated",
            "pilot_operator_runbook_generated",
            "pilot_evidence_packet_templates_generated",
            "post_observation_review_workflow_defined",
            "abort_quarantine_policy_defined",
            "success_failure_criteria_defined",
            "no_action_guarantees_generated",
            "pilot_design_decision_gate_generated",
            "strategic_residual_loop_generated",
            "real_external_observation_authorized",
            "real_pilot_execution_authorized",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "search_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "search_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_5_pilot_design_only",
            "l6_5_preflight_only",
            "l6_5_pilot_approval_packet_generation_enabled",
            "l6_5_pilot_operator_runbook_enabled",
            "l6_5_pilot_evidence_template_enabled",
            "l6_5_real_pilot_execution_enabled",
            "l6_5_network_enabled",
            "l6_5_search_enabled",
            "ready_for_l6_6_controlled_real_read_only_observation_pilot_approval_packet",
            "ready_for_actual_network_observation_now",
            "ready_for_scraping",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
            "next_recommended_milestone",
            "generated_milestone_summary",
            "generated_selected_candidates",
            "generated_pilot_scope",
            "generated_source_allowlist",
            "generated_approval_packets",
            "generated_operator_runbook",
            "generated_evidence_template",
            "generated_decision_gate",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_pilot_design:
                report.pass_(f"generated L6.5 pilot design summary field present: {field}")
            else:
                report.fail(f"generated L6.5 pilot design summary missing field: {field}")
        for field in [
            "l6_5_controlled_real_read_only_observation_pilot_design_defined",
            "pilot_design_only",
            "preflight_only",
            "future_real_read_only_observation_pilot_candidate_allowed",
            "pilot_scope_defined",
            "pilot_source_constraints_defined",
            "pilot_approval_packet_candidates_generated",
            "pilot_operator_runbook_generated",
            "pilot_evidence_packet_templates_generated",
            "post_observation_review_workflow_defined",
            "abort_quarantine_policy_defined",
            "success_failure_criteria_defined",
            "no_action_guarantees_generated",
            "pilot_design_decision_gate_generated",
            "strategic_residual_loop_generated",
            "l6_5_pilot_design_only",
            "l6_5_preflight_only",
            "l6_5_pilot_approval_packet_generation_enabled",
            "l6_5_pilot_operator_runbook_enabled",
            "l6_5_pilot_evidence_template_enabled",
            "ready_for_l6_6_controlled_real_read_only_observation_pilot_approval_packet",
        ]:
            if l6_pilot_design.get(field) is not True:
                report.fail(f"generated L6.5 summary must keep {field}=true")
        for field in [
            "real_external_observation_authorized",
            "real_pilot_execution_authorized",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "search_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "search_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_5_real_pilot_execution_enabled",
            "l6_5_network_enabled",
            "l6_5_search_enabled",
            "ready_for_actual_network_observation_now",
            "ready_for_scraping",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
        ]:
            if l6_pilot_design.get(field) is not False:
                report.fail(f"generated L6.5 summary must keep {field}=false")
        if not 1 <= l6_pilot_design.get("candidate_count", 0) <= 3:
            report.fail("generated L6.5 summary must select between 1 and 3 candidates")
        if l6_pilot_design.get("approval_packet_count") != (
            l6_pilot_design.get("candidate_count")
        ):
            report.fail("generated L6.5 approval packet count must match candidate count")
        if l6_pilot_design.get("next_recommended_milestone") != (
            "L6.6 Controlled Real Read-Only Observation Pilot Approval Packet v0"
        ):
            report.fail("generated L6.5 summary must point to L6.6")

    l6_pilot_approval = generated_json.get(
        "console_read_model/generated/l6_pilot_approval_summary.json"
    )
    if l6_pilot_approval:
        for field in [
            "l6_6_controlled_observation_pilot_approval_packet_defined",
            "approval_packet_only",
            "approval_sandbox_only",
            "future_real_read_only_observation_pilot_candidate_allowed",
            "approval_candidate_count",
            "approval_packet_count",
            "evidence_dossier_count",
            "risk_review_count",
            "approval_authority_model_generated",
            "approval_packet_instances_generated",
            "evidence_dossiers_generated",
            "risk_reviews_generated",
            "operator_authorization_prerequisites_generated",
            "runtime_isolation_attestation_templates_generated",
            "evidence_capture_authorization_templates_generated",
            "no_action_constraints_generated",
            "approval_decision_sandbox_generated",
            "non_persistence_receipts_generated",
            "strategic_residual_loop_generated",
            "real_external_observation_authorized",
            "real_pilot_execution_authorized",
            "real_approval_granted",
            "durable_real_approval_record_created",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "search_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "search_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_6_approval_packet_only",
            "l6_6_approval_sandbox_only",
            "l6_6_approval_packet_generation_enabled",
            "l6_6_approval_decision_sandbox_enabled",
            "l6_6_real_approval_granted",
            "l6_6_durable_real_approval_record_created",
            "ready_for_l6_7_controlled_real_read_only_observation_approval_record_sandbox",
            "ready_for_actual_network_observation_now",
            "ready_for_real_approval_now",
            "ready_for_durable_approval_persistence_now",
            "ready_for_scraping",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
            "next_recommended_milestone",
            "generated_milestone_summary",
            "generated_selected_candidates",
            "generated_authority_model",
            "generated_approval_packets",
            "generated_evidence_dossiers",
            "generated_risk_reviews",
            "generated_decision_sandbox",
            "generated_non_persistence_receipt",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_pilot_approval:
                report.pass_(f"generated L6.6 pilot approval summary field present: {field}")
            else:
                report.fail(f"generated L6.6 pilot approval summary missing field: {field}")
        for field in [
            "l6_6_controlled_observation_pilot_approval_packet_defined",
            "approval_packet_only",
            "approval_sandbox_only",
            "future_real_read_only_observation_pilot_candidate_allowed",
            "approval_authority_model_generated",
            "approval_packet_instances_generated",
            "evidence_dossiers_generated",
            "risk_reviews_generated",
            "operator_authorization_prerequisites_generated",
            "runtime_isolation_attestation_templates_generated",
            "evidence_capture_authorization_templates_generated",
            "no_action_constraints_generated",
            "approval_decision_sandbox_generated",
            "non_persistence_receipts_generated",
            "strategic_residual_loop_generated",
            "l6_6_approval_packet_only",
            "l6_6_approval_sandbox_only",
            "l6_6_approval_packet_generation_enabled",
            "l6_6_approval_decision_sandbox_enabled",
            "ready_for_l6_7_controlled_real_read_only_observation_approval_record_sandbox",
        ]:
            if l6_pilot_approval.get(field) is not True:
                report.fail(f"generated L6.6 summary must keep {field}=true")
        for field in [
            "real_external_observation_authorized",
            "real_pilot_execution_authorized",
            "real_approval_granted",
            "durable_real_approval_record_created",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "search_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "search_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_6_real_approval_granted",
            "l6_6_durable_real_approval_record_created",
            "ready_for_actual_network_observation_now",
            "ready_for_real_approval_now",
            "ready_for_durable_approval_persistence_now",
            "ready_for_scraping",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
        ]:
            if l6_pilot_approval.get(field) is not False:
                report.fail(f"generated L6.6 summary must keep {field}=false")
        if not 1 <= l6_pilot_approval.get("approval_candidate_count", 0) <= 3:
            report.fail("generated L6.6 summary must select between 1 and 3 candidates")
        if l6_pilot_approval.get("approval_packet_count") != (
            l6_pilot_approval.get("approval_candidate_count")
        ):
            report.fail("generated L6.6 approval packet count must match candidate count")
        if l6_pilot_approval.get("evidence_dossier_count") != (
            l6_pilot_approval.get("approval_candidate_count")
        ):
            report.fail("generated L6.6 evidence dossier count must match candidate count")
        if l6_pilot_approval.get("next_recommended_milestone") != (
            "L6.7 Controlled Real Read-Only Observation Approval Record Sandbox v0"
        ):
            report.fail("generated L6.6 summary must point to L6.7")

    l6_integrated_pilot_readiness = generated_json.get(
        "console_read_model/generated/l6_integrated_pilot_readiness_summary.json"
    )
    if l6_integrated_pilot_readiness:
        for field in [
            "l6_7_integrated_approval_record_and_pilot_readiness_sandbox_defined",
            "integrated_sandbox_only",
            "approval_record_sandbox_only",
            "pilot_run_readiness_only",
            "sandbox_approval_record_created",
            "sandbox_approval_record_count",
            "pilot_run_package_count",
            "operator_readiness_package_created",
            "runtime_isolation_readiness_created",
            "evidence_capture_readiness_created",
            "post_observation_review_readiness_created",
            "manual_evidence_import_readiness_created",
            "integrated_decision_gate_created",
            "no_action_receipts_created",
            "strategic_residual_loop_created",
            "manual_evidence_import_future_candidate_allowed",
            "durable_real_approval_record_created",
            "real_approval_granted",
            "real_external_observation_authorized",
            "real_pilot_execution_authorized",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "search_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "search_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "durable_approval_persistence_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_7_integrated_sandbox_only",
            "l6_7_approval_record_sandbox_only",
            "l6_7_pilot_run_readiness_only",
            "l6_7_sandbox_approval_record_created",
            "l6_7_real_approval_granted",
            "l6_7_durable_real_approval_record_created",
            "ready_for_l6_8_user_mediated_manual_evidence_import_pilot",
            "ready_for_actual_network_observation_now",
            "ready_for_real_approval_now",
            "ready_for_durable_real_approval_persistence_now",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
            "next_recommended_milestone",
            "generated_milestone_summary",
            "generated_sandbox_records",
            "generated_pilot_run_packages",
            "generated_operator_readiness",
            "generated_runtime_readiness",
            "generated_evidence_capture",
            "generated_manual_import_readiness",
            "generated_decision_gate",
            "generated_no_action_receipt",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_integrated_pilot_readiness:
                report.pass_(f"generated L6.7 integrated pilot readiness field present: {field}")
            else:
                report.fail(f"generated L6.7 integrated pilot readiness missing field: {field}")
        for field in [
            "l6_7_integrated_approval_record_and_pilot_readiness_sandbox_defined",
            "integrated_sandbox_only",
            "approval_record_sandbox_only",
            "pilot_run_readiness_only",
            "sandbox_approval_record_created",
            "operator_readiness_package_created",
            "runtime_isolation_readiness_created",
            "evidence_capture_readiness_created",
            "post_observation_review_readiness_created",
            "manual_evidence_import_readiness_created",
            "integrated_decision_gate_created",
            "no_action_receipts_created",
            "strategic_residual_loop_created",
            "manual_evidence_import_future_candidate_allowed",
            "l6_7_integrated_sandbox_only",
            "l6_7_approval_record_sandbox_only",
            "l6_7_pilot_run_readiness_only",
            "l6_7_sandbox_approval_record_created",
            "ready_for_l6_8_user_mediated_manual_evidence_import_pilot",
        ]:
            if l6_integrated_pilot_readiness.get(field) is not True:
                report.fail(f"generated L6.7 summary must keep {field}=true")
        for field in [
            "durable_real_approval_record_created",
            "real_approval_granted",
            "real_external_observation_authorized",
            "real_pilot_execution_authorized",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "search_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "search_enabled",
            "external_action_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "durable_approval_persistence_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_7_real_approval_granted",
            "l6_7_durable_real_approval_record_created",
            "ready_for_actual_network_observation_now",
            "ready_for_real_approval_now",
            "ready_for_durable_real_approval_persistence_now",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
        ]:
            if l6_integrated_pilot_readiness.get(field) is not False:
                report.fail(f"generated L6.7 summary must keep {field}=false")
        if not 1 <= l6_integrated_pilot_readiness.get("sandbox_approval_record_count", 0) <= 3:
            report.fail("generated L6.7 summary must include between 1 and 3 sandbox approval records")
        if l6_integrated_pilot_readiness.get("pilot_run_package_count") != (
            l6_integrated_pilot_readiness.get("sandbox_approval_record_count")
        ):
            report.fail("generated L6.7 pilot run package count must match sandbox approval record count")
        if l6_integrated_pilot_readiness.get("next_recommended_milestone") != (
            "L6.8 User-Mediated Manual Evidence Import Pilot v0"
        ):
            report.fail("generated L6.7 summary must point to L6.8")

    l6_agentic_evidence = generated_json.get(
        "console_read_model/generated/l6_agentic_evidence_summary.json"
    )
    if l6_agentic_evidence:
        for field in [
            "l6_8_agentic_evidence_discovery_trust_engine_defined",
            "mode",
            "agentic_evidence_discovery_design_and_sandbox_only",
            "evidence_need_count",
            "source_hypothesis_count",
            "ranked_source_hypothesis_count",
            "observation_work_order_count",
            "rejected_source_hypothesis_count",
            "autonomous_evidence_need_inference_authorized",
            "autonomous_source_hypothesis_generation_authorized",
            "autonomous_evidence_value_judgment_authorized",
            "autonomous_trust_assessment_authorized",
            "observation_work_order_generation_authorized",
            "source_type_value_model_generated",
            "structural_trust_judgment_generated",
            "value_of_information_model_generated",
            "conflict_corroboration_model_generated",
            "pre_observation_rejection_filter_generated",
            "agentic_evidence_decision_gate_generated",
            "no_action_receipts_generated",
            "strategic_residual_loop_generated",
            "real_external_observation_authorized",
            "agent_external_fetch_authorized",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "search_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "real_approval_granted",
            "durable_real_approval_record_created",
            "future_controlled_read_only_observation_pilot_candidate_allowed",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "search_enabled",
            "external_action_enabled",
            "agent_external_fetch_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "durable_approval_persistence_enabled",
            "semantic_truth_scoring_enabled",
            "llm_confidence_as_authority_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_8_agentic_evidence_discovery_design_and_sandbox_only",
            "l6_8_autonomous_evidence_need_inference_enabled",
            "l6_8_autonomous_source_hypothesis_generation_enabled",
            "l6_8_autonomous_evidence_value_judgment_enabled",
            "l6_8_autonomous_trust_assessment_enabled",
            "l6_8_observation_work_order_generation_enabled",
            "l6_8_real_external_observation_enabled",
            "l6_8_agent_external_fetch_enabled",
            "ready_for_l6_9_controlled_read_only_agentic_evidence_discovery_pilot_approval",
            "ready_for_actual_network_observation_now",
            "ready_for_autonomous_web_search_now",
            "ready_for_scraping",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
            "next_recommended_milestone",
            "generated_milestone_summary",
            "generated_evidence_needs",
            "generated_source_hypotheses",
            "generated_source_value_model",
            "generated_trust_judgment",
            "generated_value_of_information",
            "generated_source_ranking",
            "generated_work_orders",
            "generated_rejection_filter",
            "generated_decision_gate",
            "generated_no_action_receipt",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_agentic_evidence:
                report.pass_(f"generated L6.8 agentic evidence field present: {field}")
            else:
                report.fail(f"generated L6.8 agentic evidence missing field: {field}")
        for field in [
            "l6_8_agentic_evidence_discovery_trust_engine_defined",
            "agentic_evidence_discovery_design_and_sandbox_only",
            "autonomous_evidence_need_inference_authorized",
            "autonomous_source_hypothesis_generation_authorized",
            "autonomous_evidence_value_judgment_authorized",
            "autonomous_trust_assessment_authorized",
            "observation_work_order_generation_authorized",
            "source_type_value_model_generated",
            "structural_trust_judgment_generated",
            "value_of_information_model_generated",
            "conflict_corroboration_model_generated",
            "pre_observation_rejection_filter_generated",
            "agentic_evidence_decision_gate_generated",
            "no_action_receipts_generated",
            "strategic_residual_loop_generated",
            "future_controlled_read_only_observation_pilot_candidate_allowed",
            "l6_8_agentic_evidence_discovery_design_and_sandbox_only",
            "l6_8_autonomous_evidence_need_inference_enabled",
            "l6_8_autonomous_source_hypothesis_generation_enabled",
            "l6_8_autonomous_evidence_value_judgment_enabled",
            "l6_8_autonomous_trust_assessment_enabled",
            "l6_8_observation_work_order_generation_enabled",
            "ready_for_l6_9_controlled_read_only_agentic_evidence_discovery_pilot_approval",
        ]:
            if l6_agentic_evidence.get(field) is not True:
                report.fail(f"generated L6.8 summary must keep {field}=true")
        for field in [
            "real_external_observation_authorized",
            "agent_external_fetch_authorized",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "search_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "real_approval_granted",
            "durable_real_approval_record_created",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "search_enabled",
            "external_action_enabled",
            "agent_external_fetch_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "durable_approval_persistence_enabled",
            "semantic_truth_scoring_enabled",
            "llm_confidence_as_authority_enabled",
            "raw_runtime_artifact_reading_enabled",
            "l6_8_real_external_observation_enabled",
            "l6_8_agent_external_fetch_enabled",
            "ready_for_actual_network_observation_now",
            "ready_for_autonomous_web_search_now",
            "ready_for_scraping",
            "ready_for_publication",
            "ready_for_outreach",
            "ready_for_payment",
            "ready_for_revenue_execution",
            "ready_for_mcp_execution",
            "ready_for_canonical_update",
            "ready_for_brain_memory_writeback",
        ]:
            if l6_agentic_evidence.get(field) is not False:
                report.fail(f"generated L6.8 summary must keep {field}=false")
        if l6_agentic_evidence.get("mode") != "agentic_evidence_discovery_design_and_sandbox":
            report.fail("generated L6.8 summary must be design/sandbox mode")
        if l6_agentic_evidence.get("evidence_need_count", 0) < 8:
            report.fail("generated L6.8 summary must include at least 8 evidence needs")
        if l6_agentic_evidence.get("source_hypothesis_count", 0) < 4:
            report.fail("generated L6.8 summary must include at least 4 source hypotheses")
        if not 1 <= l6_agentic_evidence.get("observation_work_order_count", 0) <= (
            l6_agentic_evidence.get("ranked_source_hypothesis_count", 0)
        ):
            report.fail("generated L6.8 work order count must be bounded by ranked sources")
        if l6_agentic_evidence.get("rejected_source_hypothesis_count", 0) < 1:
            report.fail("generated L6.8 summary must include rejected source hypotheses")
        if l6_agentic_evidence.get("next_recommended_milestone") != (
            "L6.9 Controlled Read-Only Agentic Evidence Discovery Pilot Approval v0"
        ):
            report.fail("generated L6.8 summary must point to L6.9")

    l6_agentic_pilot_dry_run = generated_json.get(
        "console_read_model/generated/l6_agentic_pilot_dry_run_summary.json"
    )
    if l6_agentic_pilot_dry_run:
        for field in [
            "l6_9_controlled_agentic_evidence_pilot_approval_dry_run_defined",
            "mode",
            "pilot_approval_and_dry_run_only",
            "sandbox_approval_record_only",
            "selected_work_order_count",
            "eligible_work_order_count",
            "approval_packet_count",
            "sandbox_approval_record_count",
            "runtime_readiness_packet_count",
            "dry_run_trace_count",
            "empty_evidence_packet_count",
            "post_run_review_packet_count",
            "refinement_candidate_count",
            "agentic_work_order_selection_authorized",
            "pilot_approval_packet_generation_authorized",
            "sandbox_approval_record_generation_authorized",
            "dry_run_lifecycle_simulation_authorized",
            "empty_evidence_capture_simulation_authorized",
            "approval_eligibility_gate_generated",
            "approval_packets_generated",
            "sandbox_approval_records_generated",
            "runtime_readiness_generated",
            "dry_run_traces_generated",
            "empty_evidence_capture_generated",
            "post_run_review_generated",
            "residual_refinement_candidates_generated",
            "real_execution_blockers_generated",
            "no_action_receipts_generated",
            "strategic_residual_loop_generated",
            "real_external_observation_authorized",
            "real_pilot_execution_authorized",
            "real_approval_granted",
            "durable_real_approval_record_created",
            "agent_external_fetch_authorized",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "search_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "future_tiny_real_read_only_pilot_candidate_allowed",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "search_enabled",
            "external_action_enabled",
            "agent_external_fetch_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "durable_approval_persistence_enabled",
            "semantic_truth_scoring_enabled",
            "llm_confidence_as_authority_enabled",
            "raw_runtime_artifact_reading_enabled",
            "ready_for_l6_10_tiny_real_read_only_agentic_evidence_observation_pilot",
            "ready_for_actual_network_observation_now",
            "ready_for_autonomous_web_search_now",
            "next_recommended_milestone",
            "generated_selected_work_orders",
            "generated_approval_packets",
            "generated_sandbox_records",
            "generated_dry_run_traces",
            "generated_empty_evidence",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_agentic_pilot_dry_run:
                report.pass_(f"generated L6.9 agentic pilot dry-run field present: {field}")
            else:
                report.fail(f"generated L6.9 agentic pilot dry-run missing field: {field}")
        for field in [
            "l6_9_controlled_agentic_evidence_pilot_approval_dry_run_defined",
            "pilot_approval_and_dry_run_only",
            "sandbox_approval_record_only",
            "agentic_work_order_selection_authorized",
            "pilot_approval_packet_generation_authorized",
            "sandbox_approval_record_generation_authorized",
            "dry_run_lifecycle_simulation_authorized",
            "empty_evidence_capture_simulation_authorized",
            "approval_eligibility_gate_generated",
            "approval_packets_generated",
            "sandbox_approval_records_generated",
            "runtime_readiness_generated",
            "dry_run_traces_generated",
            "empty_evidence_capture_generated",
            "post_run_review_generated",
            "residual_refinement_candidates_generated",
            "real_execution_blockers_generated",
            "no_action_receipts_generated",
            "strategic_residual_loop_generated",
            "future_tiny_real_read_only_pilot_candidate_allowed",
            "ready_for_l6_10_tiny_real_read_only_agentic_evidence_observation_pilot",
        ]:
            if l6_agentic_pilot_dry_run.get(field) is not True:
                report.fail(f"generated L6.9 summary must keep {field}=true")
        for field in [
            "real_external_observation_authorized",
            "real_pilot_execution_authorized",
            "real_approval_granted",
            "durable_real_approval_record_created",
            "agent_external_fetch_authorized",
            "network_authorized",
            "api_authorized",
            "scraping_authorized",
            "browser_fetch_authorized",
            "search_authorized",
            "publication_authorized",
            "outreach_authorized",
            "payment_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "network_enabled",
            "api_enabled",
            "scraping_enabled",
            "browser_fetch_enabled",
            "search_enabled",
            "external_action_enabled",
            "agent_external_fetch_enabled",
            "publication_enabled",
            "outreach_enabled",
            "payment_enabled",
            "revenue_execution_enabled",
            "mcp_tool_execution_enabled",
            "live_execution_enabled",
            "cieu_db_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "real_canonical_update_application_enabled",
            "real_y_star_direct_mutation_enabled",
            "durable_approval_persistence_enabled",
            "semantic_truth_scoring_enabled",
            "llm_confidence_as_authority_enabled",
            "raw_runtime_artifact_reading_enabled",
            "ready_for_actual_network_observation_now",
            "ready_for_autonomous_web_search_now",
        ]:
            if l6_agentic_pilot_dry_run.get(field) is not False:
                report.fail(f"generated L6.9 summary must keep {field}=false")
        if l6_agentic_pilot_dry_run.get("mode") != "pilot_approval_and_dry_run_only":
            report.fail("generated L6.9 summary must be pilot approval and dry-run mode")
        selected_count = l6_agentic_pilot_dry_run.get("selected_work_order_count", 0)
        if not 1 <= selected_count <= 3:
            report.fail("generated L6.9 summary must select 1-3 work orders")
        for field in [
            "approval_packet_count",
            "sandbox_approval_record_count",
            "dry_run_trace_count",
            "empty_evidence_packet_count",
            "post_run_review_packet_count",
        ]:
            if l6_agentic_pilot_dry_run.get(field) != selected_count:
                report.fail(f"generated L6.9 summary must align {field} with selected count")
        if l6_agentic_pilot_dry_run.get("next_recommended_milestone") != (
            "L6.10 Tiny Real Read-Only Agentic Evidence Observation Pilot v0"
        ):
            report.fail("generated L6.9 summary must point to L6.10")

    l6_tiny_observation_pilot = generated_json.get(
        "console_read_model/generated/l6_tiny_observation_pilot_summary.json"
    )
    if l6_tiny_observation_pilot:
        for field in [
            "l6_10_tiny_real_read_only_observation_pilot_defined",
            "mode",
            "selected_work_order_count",
            "source_locator_resolved",
            "observation_executed",
            "blocked_pilot",
            "external_requests_count",
            "pages_read_count",
            "search_queries_count",
            "evidence_packet_generated",
            "post_observation_review_packet_generated",
            "artifact_refinement_candidate_generated",
            "artifact_refinement_applied",
            "ready_for_retry_after_condition_resolved",
            "next_recommended_milestone",
            "generated_selected_work_order",
            "generated_observation_trace",
            "generated_evidence_packet",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_tiny_observation_pilot:
                report.pass_(f"generated L6.10 tiny observation field present: {field}")
            else:
                report.fail(f"generated L6.10 tiny observation missing field: {field}")
        if l6_tiny_observation_pilot.get("mode") != "tiny_real_read_only_observation_pilot":
            report.fail("generated L6.10 summary must be tiny real read-only observation mode")
        if l6_tiny_observation_pilot.get("selected_work_order_count") != 1:
            report.fail("generated L6.10 summary must select exactly one work order")
        for field in [
            "l6_10_tiny_real_read_only_observation_pilot_defined",
            "real_read_only_observation_pilot_authorized",
            "evidence_packet_generated",
            "post_observation_review_packet_generated",
            "artifact_refinement_candidate_generated",
            "ready_for_retry_after_condition_resolved",
        ]:
            if l6_tiny_observation_pilot.get(field) is not True:
                report.fail(f"generated L6.10 summary must keep {field}=true")
        for field in [
            "broad_web_search_authorized",
            "crawling_authorized",
            "scraping_authorized",
            "browser_automation_authorized",
            "login_authorized",
            "account_creation_authorized",
            "payment_authorized",
            "form_submission_authorized",
            "posting_commenting_messaging_authorized",
            "publication_authorized",
            "outreach_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "semantic_truth_scoring_enabled",
            "llm_confidence_as_authority_enabled",
            "artifact_refinement_applied",
        ]:
            if l6_tiny_observation_pilot.get(field) is not False:
                report.fail(f"generated L6.10 summary must keep {field}=false")
        limits = {
            "external_requests_count": l6_tiny_observation_pilot.get("max_external_requests"),
            "pages_read_count": l6_tiny_observation_pilot.get("max_pages_read"),
            "search_queries_count": l6_tiny_observation_pilot.get(
                "max_search_queries_if_locator_missing"
            ),
        }
        for count_field, limit in limits.items():
            if limit is not None and l6_tiny_observation_pilot.get(count_field, 0) > limit:
                report.fail(f"generated L6.10 summary exceeds runtime limit for {count_field}")

    l6_10r_locator_retry = generated_json.get(
        "console_read_model/generated/l6_10r_locator_retry_summary.json"
    )
    if l6_10r_locator_retry:
        for field in [
            "l6_10r_controlled_source_locator_resolution_retry_defined",
            "mode",
            "selected_work_order_count",
            "controlled_locator_discovery_authorized",
            "tiny_real_read_only_observation_retry_authorized",
            "locator_discovery_executed",
            "locator_discovery_queries_count",
            "concrete_locator_resolved",
            "locator_eligible_for_observation",
            "retry_observation_authorized",
            "tiny_read_only_observation_executed",
            "external_reads_total",
            "pages_read_count",
            "evidence_packet_generated",
            "post_observation_review_packet_generated",
            "artifact_refinement_candidate_generated",
            "artifact_refinement_applied",
            "remaining_blocker",
            "generated_selected_work_order",
            "generated_locator_resolution",
            "generated_observation_trace",
            "generated_evidence_packet",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_10r_locator_retry:
                report.pass_(f"generated L6.10R locator retry field present: {field}")
            else:
                report.fail(f"generated L6.10R locator retry missing field: {field}")
        if l6_10r_locator_retry.get("mode") != "controlled_locator_resolution_and_tiny_observation_retry":
            report.fail("generated L6.10R summary must be locator retry mode")
        if l6_10r_locator_retry.get("selected_work_order_count") != 1:
            report.fail("generated L6.10R summary must select exactly one work order")
        for field in [
            "l6_10r_controlled_source_locator_resolution_retry_defined",
            "controlled_locator_discovery_authorized",
            "tiny_real_read_only_observation_retry_authorized",
            "evidence_packet_generated",
            "post_observation_review_packet_generated",
            "artifact_refinement_candidate_generated",
        ]:
            if l6_10r_locator_retry.get(field) is not True:
                report.fail(f"generated L6.10R summary must keep {field}=true")
        for field in [
            "broad_web_search_authorized",
            "repeated_search_loop_authorized",
            "crawling_authorized",
            "scraping_authorized",
            "browser_automation_authorized",
            "login_authorized",
            "account_creation_authorized",
            "contact_authorized",
            "payment_authorized",
            "form_submission_authorized",
            "contact_authorized",
            "posting_commenting_messaging_authorized",
            "publication_authorized",
            "outreach_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "semantic_truth_scoring_enabled",
            "llm_confidence_as_authority_enabled",
            "artifact_refinement_applied",
        ]:
            if l6_10r_locator_retry.get(field) is not False:
                report.fail(f"generated L6.10R summary must keep {field}=false")
        limits = {
            "locator_discovery_queries_count": l6_10r_locator_retry.get("max_locator_discovery_queries"),
            "external_reads_total": l6_10r_locator_retry.get("max_external_reads_total"),
            "pages_read_count": l6_10r_locator_retry.get("max_pages_read"),
        }
        for count_field, limit in limits.items():
            if limit is not None and l6_10r_locator_retry.get(count_field, 0) > limit:
                report.fail(f"generated L6.10R summary exceeds runtime limit for {count_field}")

    l6_10t_toolmaking_locator_resolver = generated_json.get(
        "console_read_model/generated/l6_10t_toolmaking_locator_resolver_summary.json"
    )
    if l6_10t_toolmaking_locator_resolver:
        for field in [
            "l6_10t_governed_capability_gap_toolmaking_defined",
            "mode",
            "os_neutral_design_required",
            "mac_only_solution_allowed",
            "capability_gap_diagnosis_completed",
            "governed_toolmaking_methodology_created",
            "controlled_tool_contract_model_created",
            "tool_authority_use_gate_created",
            "tool_validation_harness_created",
            "primary_gap_type",
            "secondary_gap_type",
            "resolver_capability_probe_executed",
            "capability_probe_local_only",
            "probe_used_network",
            "controlled_resolver_adapter_available",
            "selected_resolver_adapter_id",
            "resolver_mode",
            "capability_gap_code",
            "locator_discovery_executed",
            "locator_discovery_queries_count",
            "concrete_locator_resolved",
            "tiny_read_only_observation_executed",
            "external_reads_total",
            "pages_read_count",
            "evidence_packet_generated",
            "artifact_refinement_candidate_generated",
            "artifact_refinement_applied",
            "generated_tools_granted_live_authority",
            "general_governed_toolmaking_methodology_ready_for_reuse",
            "remaining_blocker",
            "next_recommended_milestone",
            "generated_probe_result",
            "generated_adapter_trace",
            "generated_evidence_packet",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_10t_toolmaking_locator_resolver:
                report.pass_(f"generated L6.10T toolmaking locator resolver field present: {field}")
            else:
                report.fail(f"generated L6.10T toolmaking locator resolver missing field: {field}")
        if (
            l6_10t_toolmaking_locator_resolver.get("mode")
            != "governed_capability_gap_toolmaking_and_locator_resolver_adapter"
        ):
            report.fail("generated L6.10T summary must be governed toolmaking locator resolver mode")
        if l6_10t_toolmaking_locator_resolver.get("primary_gap_type") != "tool_capability_gap":
            report.fail("generated L6.10T summary must classify primary gap as tool capability gap")
        if l6_10t_toolmaking_locator_resolver.get("secondary_gap_type") != "runtime_environment_gap":
            report.fail("generated L6.10T summary must classify secondary gap as runtime environment gap")
        if l6_10t_toolmaking_locator_resolver.get("selected_resolver_adapter_id") != "disabled_no_network_resolver":
            report.fail("generated L6.10T summary must select disabled no-network resolver by default")
        if l6_10t_toolmaking_locator_resolver.get("capability_gap_code") != "no_controlled_locator_resolver_available":
            report.fail("generated L6.10T summary must name exact missing resolver capability gap")
        for field in [
            "l6_10t_governed_capability_gap_toolmaking_defined",
            "os_neutral_design_required",
            "capability_gap_diagnosis_completed",
            "governed_toolmaking_methodology_created",
            "controlled_tool_contract_model_created",
            "tool_authority_use_gate_created",
            "tool_validation_harness_created",
            "resolver_capability_probe_executed",
            "capability_probe_local_only",
            "evidence_packet_generated",
            "artifact_refinement_candidate_generated",
            "general_governed_toolmaking_methodology_ready_for_reuse",
        ]:
            if l6_10t_toolmaking_locator_resolver.get(field) is not True:
                report.fail(f"generated L6.10T summary must keep {field}=true")
        for field in [
            "mac_only_solution_allowed",
            "probe_used_network",
            "controlled_resolver_adapter_available",
            "locator_discovery_executed",
            "concrete_locator_resolved",
            "tiny_read_only_observation_executed",
            "artifact_refinement_applied",
            "generated_tools_granted_live_authority",
            "broad_web_search_authorized",
            "repeated_search_loop_authorized",
            "crawling_authorized",
            "scraping_authorized",
            "browser_automation_authorized",
            "login_authorized",
            "account_creation_authorized",
            "contact_authorized",
            "payment_authorized",
            "form_submission_authorized",
            "posting_commenting_messaging_authorized",
            "publication_authorized",
            "outreach_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "tool_external_authority_auto_grant_authorized",
            "semantic_truth_scoring_authorized",
            "llm_confidence_as_authority_authorized",
        ]:
            if l6_10t_toolmaking_locator_resolver.get(field) is not False:
                report.fail(f"generated L6.10T summary must keep {field}=false")
        limits = {
            "locator_discovery_queries_count": l6_10t_toolmaking_locator_resolver.get(
                "max_locator_discovery_queries"
            ),
            "external_reads_total": l6_10t_toolmaking_locator_resolver.get("max_external_reads_total"),
            "pages_read_count": l6_10t_toolmaking_locator_resolver.get("max_pages_read"),
        }
        for count_field, limit in limits.items():
            if limit is not None and l6_10t_toolmaking_locator_resolver.get(count_field, 0) > limit:
                report.fail(f"generated L6.10T summary exceeds runtime limit for {count_field}")

    l6_10u_locator_resolver_enablement = generated_json.get(
        "console_read_model/generated/l6_10u_locator_resolver_enablement_summary.json"
    )
    if l6_10u_locator_resolver_enablement:
        for field in [
            "l6_10u_controlled_locator_resolver_enablement_complete",
            "mode",
            "resolver_runtime_created",
            "seed_registry_resolver_created",
            "environment_gated_search_resolver_created",
            "disabled_resolver_created",
            "selected_work_order_id",
            "source_selected_work_order_id",
            "resolver_mode_used",
            "resolver_id",
            "seed_registry_lookup_executed",
            "seed_registry_lookup_count",
            "controlled_search_executed",
            "search_query_count",
            "external_reads_count",
            "concrete_locator_resolved",
            "resolved_locator",
            "facts_inferred_from_resolution",
            "locator_eligible_for_observation",
            "tiny_read_only_observation_executed",
            "evidence_packet_generated",
            "live_source_evidence_captured",
            "artifact_refinement_candidate_generated",
            "artifact_refinement_applied",
            "remaining_blocker",
            "next_recommended_milestone",
            "generated_resolution_result",
            "generated_observation_trace",
            "generated_evidence_packet",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_10u_locator_resolver_enablement:
                report.pass_(f"generated L6.10U locator resolver field present: {field}")
            else:
                report.fail(f"generated L6.10U locator resolver missing field: {field}")
        if (
            l6_10u_locator_resolver_enablement.get("mode")
            != "controlled_locator_resolver_enablement_first_attempt"
        ):
            report.fail("generated L6.10U summary must be controlled locator resolver enablement mode")
        for field in [
            "l6_10u_controlled_locator_resolver_enablement_complete",
            "resolver_runtime_created",
            "seed_registry_resolver_created",
            "environment_gated_search_resolver_created",
            "disabled_resolver_created",
            "seed_registry_resolver_authorized",
            "environment_gated_controlled_search_resolver_authorized",
            "disabled_resolver_authorized",
            "evidence_packet_generated",
            "artifact_refinement_candidate_generated",
        ]:
            if l6_10u_locator_resolver_enablement.get(field) is not True:
                report.fail(f"generated L6.10U summary must keep {field}=true")
        for field in [
            "controlled_search_executed",
            "concrete_locator_resolved",
            "facts_inferred_from_resolution",
            "locator_eligible_for_observation",
            "tiny_read_only_observation_executed",
            "live_source_evidence_captured",
            "artifact_refinement_applied",
            "broad_search_authorized",
            "repeated_search_loop_authorized",
            "crawling_authorized",
            "scraping_authorized",
            "browser_automation_authorized",
            "login_authorized",
            "account_creation_authorized",
            "contact_authorized",
            "payment_authorized",
            "form_submission_authorized",
            "posting_commenting_messaging_authorized",
            "publication_authorized",
            "outreach_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
        ]:
            if l6_10u_locator_resolver_enablement.get(field) is not False:
                report.fail(f"generated L6.10U summary must keep {field}=false")
        if l6_10u_locator_resolver_enablement.get("resolver_mode_used") != "disabled":
            report.fail("generated L6.10U default run must use disabled resolver after seed/search miss")
        if l6_10u_locator_resolver_enablement.get("remaining_blocker") != "no_enabled_locator_resolution_path":
            report.fail("generated L6.10U summary must name no_enabled_locator_resolution_path blocker")
        limits = {
            "selected_work_order_count": l6_10u_locator_resolver_enablement.get(
                "max_selected_work_orders"
            ),
            "seed_registry_lookup_count": l6_10u_locator_resolver_enablement.get(
                "max_seed_registry_lookups"
            ),
            "search_query_count": l6_10u_locator_resolver_enablement.get("max_search_queries"),
            "external_reads_count": l6_10u_locator_resolver_enablement.get(
                "max_total_external_reads"
            ),
            "pages_read_count": l6_10u_locator_resolver_enablement.get("max_pages_read"),
        }
        for count_field, limit in limits.items():
            if limit is not None and l6_10u_locator_resolver_enablement.get(count_field, 0) > limit:
                report.fail(f"generated L6.10U summary exceeds runtime limit for {count_field}")

    l6_10v_seed_or_search_resolver_enablement = generated_json.get(
        "console_read_model/generated/l6_10v_seed_or_search_resolver_enablement_summary.json"
    )
    if l6_10v_seed_or_search_resolver_enablement:
        for field in [
            "l6_10v_controlled_seed_locator_or_search_resolver_enablement_complete",
            "mode",
            "reviewed_seed_locator_registry_created",
            "explicit_controlled_search_resolver_created",
            "selected_work_order_id",
            "source_selected_work_order_id",
            "resolution_path_used",
            "seed_registry_lookup_executed",
            "seed_registry_lookup_count",
            "reviewed_seed_locator_count",
            "seed_locator_resolved",
            "controlled_search_enabled",
            "controlled_search_executed",
            "controlled_search_query_count",
            "external_reads_count",
            "concrete_locator_resolved",
            "resolved_locator",
            "facts_inferred_from_resolution",
            "search_snippets_used_as_evidence",
            "locator_eligible_for_observation",
            "tiny_read_only_observation_executed",
            "evidence_packet_generated",
            "live_source_evidence_captured",
            "artifact_refinement_candidate_generated",
            "artifact_refinement_applied",
            "remaining_blocker",
            "next_recommended_milestone",
            "generated_registry",
            "generated_resolution_result",
            "generated_observation_trace",
            "generated_evidence_packet",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_10v_seed_or_search_resolver_enablement:
                report.pass_(f"generated L6.10V seed/search resolver field present: {field}")
            else:
                report.fail(f"generated L6.10V seed/search resolver missing field: {field}")
        if (
            l6_10v_seed_or_search_resolver_enablement.get("mode")
            != "controlled_seed_locator_or_explicit_search_resolver_enablement"
        ):
            report.fail("generated L6.10V summary must be seed/search resolver enablement mode")
        for field in [
            "l6_10v_controlled_seed_locator_or_search_resolver_enablement_complete",
            "reviewed_seed_locator_registry_created",
            "explicit_controlled_search_resolver_created",
            "seed_registry_lookup_executed",
            "reviewed_seed_locator_registry_authorized",
            "explicit_controlled_search_resolver_authorized",
            "controlled_search_requires_explicit_enable_flag",
            "evidence_packet_generated",
            "artifact_refinement_candidate_generated",
        ]:
            if l6_10v_seed_or_search_resolver_enablement.get(field) is not True:
                report.fail(f"generated L6.10V summary must keep {field}=true")
        for field in [
            "seed_locator_resolved",
            "controlled_search_enabled",
            "controlled_search_executed",
            "concrete_locator_resolved",
            "facts_inferred_from_resolution",
            "search_snippets_used_as_evidence",
            "locator_eligible_for_observation",
            "tiny_read_only_observation_executed",
            "live_source_evidence_captured",
            "artifact_refinement_applied",
            "broad_search_authorized",
            "repeated_search_loop_authorized",
            "crawling_authorized",
            "scraping_authorized",
            "browser_automation_authorized",
            "login_authorized",
            "account_creation_authorized",
            "contact_authorized",
            "payment_authorized",
            "form_submission_authorized",
            "posting_commenting_messaging_authorized",
            "publication_authorized",
            "outreach_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
        ]:
            if l6_10v_seed_or_search_resolver_enablement.get(field) is not False:
                report.fail(f"generated L6.10V summary must keep {field}=false")
        if (
            l6_10v_seed_or_search_resolver_enablement.get("resolution_path_used")
            != "disabled_no_path"
        ):
            report.fail("generated L6.10V default run must use disabled_no_path")
        if (
            l6_10v_seed_or_search_resolver_enablement.get("remaining_blocker")
            != "no_enabled_locator_resolution_path"
        ):
            report.fail("generated L6.10V summary must name no_enabled_locator_resolution_path blocker")
        limits = {
            "selected_work_order_count": l6_10v_seed_or_search_resolver_enablement.get(
                "max_selected_work_orders"
            ),
            "seed_registry_lookup_count": l6_10v_seed_or_search_resolver_enablement.get(
                "max_seed_registry_lookups"
            ),
            "controlled_search_query_count": l6_10v_seed_or_search_resolver_enablement.get(
                "max_controlled_search_queries"
            ),
            "external_reads_count": l6_10v_seed_or_search_resolver_enablement.get(
                "max_total_external_reads"
            ),
            "pages_read_count": l6_10v_seed_or_search_resolver_enablement.get(
                "max_pages_read"
            ),
        }
        for count_field, limit in limits.items():
            if (
                limit is not None
                and l6_10v_seed_or_search_resolver_enablement.get(count_field, 0) > limit
            ):
                report.fail(f"generated L6.10V summary exceeds runtime limit for {count_field}")

    l6_10w_reviewed_seed_locator_injection = generated_json.get(
        "console_read_model/generated/l6_10w_reviewed_seed_locator_injection_summary.json"
    )
    if l6_10w_reviewed_seed_locator_injection:
        for field in [
            "l6_10w_reviewed_seed_locator_injection_tiny_retry_complete",
            "mode",
            "selected_work_order_id",
            "reviewed_seed_locator_found",
            "concrete_locator",
            "seed_candidate_status",
            "user_action_required_generated",
            "user_action_request_count",
            "requested_item",
            "retry_attempted",
            "tiny_read_only_observation_executed",
            "external_reads_count",
            "pages_read_count",
            "evidence_packet_generated",
            "live_source_evidence_captured",
            "artifact_refinement_candidate_generated",
            "artifact_refinement_applied",
            "remaining_blocker",
            "next_recommended_milestone",
            "generated_user_action_required",
            "generated_seed_candidate",
            "generated_observation_trace",
            "generated_evidence_packet",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_10w_reviewed_seed_locator_injection:
                report.pass_(f"generated L6.10W reviewed seed locator field present: {field}")
            else:
                report.fail(f"generated L6.10W reviewed seed locator missing field: {field}")
        if (
            l6_10w_reviewed_seed_locator_injection.get("mode")
            != "reviewed_seed_locator_injection_and_tiny_retry"
        ):
            report.fail("generated L6.10W summary must be reviewed seed locator injection mode")
        for field in [
            "l6_10w_reviewed_seed_locator_injection_tiny_retry_complete",
            "user_action_required_generated",
            "user_action_request_authorized",
            "reviewed_seed_locator_injection_authorized",
            "seed_locator_from_existing_repo_artifacts_authorized",
            "evidence_packet_generated",
            "artifact_refinement_candidate_generated",
        ]:
            if l6_10w_reviewed_seed_locator_injection.get(field) is not True:
                report.fail(f"generated L6.10W summary must keep {field}=true")
        for field in [
            "reviewed_seed_locator_found",
            "retry_attempted",
            "tiny_read_only_observation_executed",
            "live_source_evidence_captured",
            "artifact_refinement_applied",
            "url_invention_authorized",
            "fake_locator_authorized",
            "broad_search_authorized",
            "repeated_search_loop_authorized",
            "crawling_authorized",
            "scraping_authorized",
            "browser_automation_authorized",
            "login_authorized",
            "account_creation_authorized",
            "contact_authorized",
            "payment_authorized",
            "form_submission_authorized",
            "posting_commenting_messaging_authorized",
            "publication_authorized",
            "outreach_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
        ]:
            if l6_10w_reviewed_seed_locator_injection.get(field) is not False:
                report.fail(f"generated L6.10W summary must keep {field}=false")
        if l6_10w_reviewed_seed_locator_injection.get("user_action_request_count") != 1:
            report.fail("generated L6.10W summary must request exactly one URL")
        if l6_10w_reviewed_seed_locator_injection.get("requested_item") != "one_concrete_public_url":
            report.fail("generated L6.10W summary must request one concrete public URL")
        if (
            l6_10w_reviewed_seed_locator_injection.get("remaining_blocker")
            != "user_must_provide_one_reviewed_seed_locator_url"
        ):
            report.fail("generated L6.10W summary must name one-URL user action blocker")
        limits = {
            "selected_work_order_count": l6_10w_reviewed_seed_locator_injection.get(
                "max_selected_work_orders"
            ),
            "external_reads_count": l6_10w_reviewed_seed_locator_injection.get(
                "max_total_external_reads"
            ),
            "pages_read_count": l6_10w_reviewed_seed_locator_injection.get(
                "max_pages_read"
            ),
        }
        for count_field, limit in limits.items():
            if (
                limit is not None
                and l6_10w_reviewed_seed_locator_injection.get(count_field, 0) > limit
            ):
                report.fail(f"generated L6.10W summary exceeds runtime limit for {count_field}")

    l6_10x_budgeted_controlled_search_evidence = generated_json.get(
        "console_read_model/generated/l6_10x_budgeted_controlled_search_evidence_summary.json"
    )
    if l6_10x_budgeted_controlled_search_evidence:
        for field in [
            "l6_10x_budgeted_controlled_external_search_evidence_pilot_complete",
            "mode",
            "selected_work_order_id",
            "query_count",
            "search_backend_mode",
            "backend_missing",
            "search_executed",
            "search_results_considered",
            "pages_opened",
            "domains_touched",
            "crawl_depth_used",
            "evidence_packets_generated",
            "conflicts_found",
            "page_read_backend_missing",
            "manual_url_request_avoided",
            "ask_user_for_url_authorized",
            "user_manual_url_provision_required",
            "controlled_external_search_authorized",
            "bounded_public_page_read_authorized",
            "bounded_crawl_authorized",
            "evidence_corroboration_authorized",
            "search_snippets_as_evidence_authorized",
            "llm_confidence_as_truth_authority_authorized",
            "semantic_truth_scoring_authorized",
            "remaining_blocker",
            "next_step",
            "generated_milestone_summary",
            "generated_query_plan",
            "generated_search_trace",
            "generated_crawl_trace",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_10x_budgeted_controlled_search_evidence:
                report.pass_(f"generated L6.10X budgeted search field present: {field}")
            else:
                report.fail(f"generated L6.10X budgeted search missing field: {field}")
        if (
            l6_10x_budgeted_controlled_search_evidence.get("mode")
            != "budgeted_controlled_external_search_evidence_pilot"
        ):
            report.fail("generated L6.10X summary must be budgeted controlled external search mode")
        for field in [
            "l6_10x_budgeted_controlled_external_search_evidence_pilot_complete",
            "controlled_external_search_authorized",
            "bounded_public_page_read_authorized",
            "bounded_crawl_authorized",
            "evidence_corroboration_authorized",
            "manual_url_request_avoided",
            "artifact_refinement_candidate_generation_authorized",
            "rate_limit_required",
            "stop_on_login_or_payment_or_form",
            "stop_on_private_or_sensitive_data",
            "stop_on_scope_drift",
        ]:
            if l6_10x_budgeted_controlled_search_evidence.get(field) is not True:
                report.fail(f"generated L6.10X summary must keep {field}=true")
        for field in [
            "ask_user_for_url_authorized",
            "user_manual_url_provision_required",
            "login_authorized",
            "account_creation_authorized",
            "contact_authorized",
            "payment_authorized",
            "form_submission_authorized",
            "posting_commenting_messaging_authorized",
            "publication_authorized",
            "outreach_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "artifact_refinement_application_authorized",
            "search_snippets_as_evidence_authorized",
            "llm_confidence_as_truth_authority_authorized",
            "semantic_truth_scoring_authorized",
            "private_sensitive_data_collection_authorized",
            "high_volume_crawling_authorized",
            "unbounded_scraping_authorized",
        ]:
            if l6_10x_budgeted_controlled_search_evidence.get(field) is not False:
                report.fail(f"generated L6.10X summary must keep {field}=false")
        exact_limits = {
            "max_selected_work_orders": 1,
            "max_queries": 5,
            "max_search_results_considered": 20,
            "max_pages_opened": 8,
            "max_domains": 5,
            "max_pages_per_domain": 3,
            "max_crawl_depth": 1,
            "max_total_external_reads": 12,
            "max_evidence_packets": 8,
        }
        for field, expected_value in exact_limits.items():
            if l6_10x_budgeted_controlled_search_evidence.get(field) != expected_value:
                report.fail(f"generated L6.10X summary must keep {field}={expected_value}")
        count_limits = {
            "selected_work_order_count": l6_10x_budgeted_controlled_search_evidence.get(
                "max_selected_work_orders"
            ),
            "query_count": l6_10x_budgeted_controlled_search_evidence.get("max_queries"),
            "search_results_considered": l6_10x_budgeted_controlled_search_evidence.get(
                "max_search_results_considered"
            ),
            "pages_opened": l6_10x_budgeted_controlled_search_evidence.get(
                "max_pages_opened"
            ),
            "domains_touched": l6_10x_budgeted_controlled_search_evidence.get(
                "max_domains"
            ),
            "crawl_depth_used": l6_10x_budgeted_controlled_search_evidence.get(
                "max_crawl_depth"
            ),
            "evidence_packets_generated": l6_10x_budgeted_controlled_search_evidence.get(
                "max_evidence_packets"
            ),
        }
        for count_field, limit in count_limits.items():
            if (
                limit is not None
                and l6_10x_budgeted_controlled_search_evidence.get(count_field, 0) > limit
            ):
                report.fail(f"generated L6.10X summary exceeds runtime limit for {count_field}")
        query_count = l6_10x_budgeted_controlled_search_evidence.get("query_count", 0)
        if query_count < 1:
            report.fail("generated L6.10X summary must plan at least one query")
        if l6_10x_budgeted_controlled_search_evidence.get("search_backend_mode") == "disabled":
            if l6_10x_budgeted_controlled_search_evidence.get("search_executed") is not False:
                report.fail("generated L6.10X disabled backend must not execute search")
            if (
                l6_10x_budgeted_controlled_search_evidence.get("remaining_blocker")
                != "controlled_search_backend_required"
            ):
                report.fail("generated L6.10X disabled backend must name controlled_search_backend_required")

    l6_11_controlled_backend_page_read = generated_json.get(
        "console_read_model/generated/l6_11_controlled_backend_page_read_enablement_summary.json"
    )
    if l6_11_controlled_backend_page_read:
        for field in [
            "l6_11_controlled_search_backend_page_read_enablement_complete",
            "mode",
            "selected_work_order_id",
            "backend_mode_tested",
            "page_read_mode_tested",
            "default_backend_mode",
            "network_allowed",
            "fixture_full_pipeline_generated_non_empty_evidence_packet",
            "query_count",
            "search_results_considered",
            "pages_opened",
            "domains_touched",
            "crawl_depth_used",
            "evidence_packets_generated",
            "conflicts_found",
            "blockers",
            "disabled_blockers",
            "configuration_receipt_generated",
            "safety_preflight_decision",
            "ask_user_for_url_occurred",
            "manual_url_request_receipt_executed",
            "search_snippets_used_as_evidence",
            "page_read_extracted_content_used_as_evidence_candidate",
            "contact_authorized",
            "generated_milestone_summary",
            "generated_configuration_receipt",
            "generated_safety_preflight",
            "generated_fixture_pipeline_trace",
            "generated_evidence_index",
            "generated_readiness",
            "warning",
        ]:
            if field in l6_11_controlled_backend_page_read:
                report.pass_(f"generated L6.11 backend/page-read field present: {field}")
            else:
                report.fail(f"generated L6.11 backend/page-read missing field: {field}")
        if (
            l6_11_controlled_backend_page_read.get("mode")
            != "controlled_search_backend_page_read_adapter_enablement"
        ):
            report.fail("generated L6.11 summary must be controlled backend/page-read enablement mode")
        for field in [
            "l6_11_controlled_search_backend_page_read_enablement_complete",
            "fixture_full_pipeline_generated_non_empty_evidence_packet",
            "page_read_extracted_content_used_as_evidence_candidate",
            "artifact_refinement_candidate_generation_authorized",
        ]:
            if l6_11_controlled_backend_page_read.get(field) is not True:
                report.fail(f"generated L6.11 summary must keep {field}=true")
        for field in [
            "network_allowed",
            "ask_user_for_url_occurred",
            "manual_url_request_receipt_executed",
            "search_snippets_used_as_evidence",
            "ask_user_for_url_authorized",
            "user_manual_url_provision_required",
            "search_snippets_as_evidence_authorized",
            "login_authorized",
            "account_creation_authorized",
            "payment_authorized",
            "form_submission_authorized",
            "posting_commenting_messaging_authorized",
            "publication_authorized",
            "outreach_authorized",
            "revenue_execution_authorized",
            "mcp_execution_authorized",
            "live_behavior_authorized",
            "cieu_db_write_authorized",
            "canonical_update_authorized",
            "brain_writeback_authorized",
            "memory_ingestion_authorized",
            "direct_y_star_mutation_authorized",
            "artifact_refinement_application_authorized",
        ]:
            if l6_11_controlled_backend_page_read.get(field) is not False:
                report.fail(f"generated L6.11 summary must keep {field}=false")
        exact_values = {
            "backend_mode_tested": "fixture",
            "page_read_mode_tested": "fixture",
            "default_backend_mode": "disabled",
            "safety_preflight_decision": "pass",
            "max_selected_work_orders": 1,
            "max_queries": 5,
            "max_search_results_considered": 20,
            "max_pages_opened": 8,
            "max_domains": 5,
            "max_pages_per_domain": 3,
            "max_crawl_depth": 1,
            "max_total_external_reads": 12,
            "max_evidence_packets": 8,
        }
        for field, expected_value in exact_values.items():
            if l6_11_controlled_backend_page_read.get(field) != expected_value:
                report.fail(f"generated L6.11 summary must keep {field}={expected_value}")
        count_limits = {
            "query_count": l6_11_controlled_backend_page_read.get("max_queries"),
            "search_results_considered": l6_11_controlled_backend_page_read.get(
                "max_search_results_considered"
            ),
            "pages_opened": l6_11_controlled_backend_page_read.get("max_pages_opened"),
            "domains_touched": l6_11_controlled_backend_page_read.get("max_domains"),
            "crawl_depth_used": l6_11_controlled_backend_page_read.get("max_crawl_depth"),
            "evidence_packets_generated": l6_11_controlled_backend_page_read.get(
                "max_evidence_packets"
            ),
        }
        for count_field, limit in count_limits.items():
            if limit is not None and l6_11_controlled_backend_page_read.get(count_field, 0) > limit:
                report.fail(f"generated L6.11 summary exceeds runtime limit for {count_field}")
        for field in [
            "search_results_considered",
            "pages_opened",
            "evidence_packets_generated",
        ]:
            if l6_11_controlled_backend_page_read.get(field, 0) < 1:
                report.fail(f"generated L6.11 fixture summary must produce positive {field}")
        disabled_blockers = set(l6_11_controlled_backend_page_read.get("disabled_blockers", []))
        for blocker in [
            "controlled_search_backend_not_configured",
            "controlled_public_page_read_adapter_not_configured",
        ]:
            if blocker not in disabled_blockers:
                report.fail(f"generated L6.11 disabled path must preserve blocker: {blocker}")

    manifest = generated_json.get("console_read_model/generated/generation_manifest.json")
    if manifest:
        for source in manifest.get("source_files", []):
            match = contains_unsafe_pattern(str(source), unsafe_patterns)
            if match:
                report.fail(f"generated manifest lists unsafe source '{match}': {source}")
        report.pass_("generated manifest source files checked for unsafe patterns")

    for agent_id in required_agents:
        capsule_dir = ROOT / "agent_brains" / agent_id
        check_exists(capsule_dir, report, "agent capsule directory")
        for filename in base_files:
            check_exists(capsule_dir / filename, report, f"{agent_id} base capsule file")
            if filename.endswith(".json") and (capsule_dir / filename).exists():
                check_json_file(capsule_dir / filename, report, f"{agent_id} JSON")

    for rel in expected["required_aiden_extended_files"]:
        path = ROOT / "agent_brains" / "Aiden-CEO" / rel
        check_exists(path, report, "Aiden extended file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "Aiden extended JSON")

    for rel in expected["required_ethan_extended_files"]:
        path = ROOT / "agent_brains" / "Ethan-CTO" / rel
        check_exists(path, report, "Ethan extended file")
        if path.suffix == ".json" and path.exists():
            check_json_file(path, report, "Ethan extended JSON")

    check_capsule_schema_alignment(expected, report)

    print_report(report)
    return 0 if not report.failed else 1


def print_report(report: Report) -> None:
    status = "PASS" if not report.failed else "FAIL"
    print(f"Static Team Read Model Validator: {status}")
    print(f"Checks passed: {len(report.passed)}")
    print(f"Checks failed: {len(report.failed)}")
    print(f"Warnings: {len(report.warnings)}")
    print(f"Files inspected: {len(report.files_inspected)}")
    print("Schema alignment:")
    print(f"- agent brain capsules checked: {report.schema_alignment['agent_brain_capsules_checked']}")
    print(f"- brain profiles checked: {report.schema_alignment['brain_profiles_checked']}")
    print(f"- ref files checked: {report.schema_alignment['ref_files_checked']}")
    print(f"- execution channel files checked: {report.schema_alignment['execution_channel_files_checked']}")
    print(f"- pre-U packet schemas checked: {report.schema_alignment['pre_u_packet_schemas_checked']}")

    if report.failed:
        print("\nFailures:")
        for item in report.failed:
            print(f"- {item}")

    if report.warnings:
        print("\nWarnings:")
        for item in report.warnings:
            print(f"- {item}")

    print("\nFiles inspected:")
    for item in sorted(report.files_inspected):
        print(f"- {item}")


if __name__ == "__main__":
    sys.exit(main())
