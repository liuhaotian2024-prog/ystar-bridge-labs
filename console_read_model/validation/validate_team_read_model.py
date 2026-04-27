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
