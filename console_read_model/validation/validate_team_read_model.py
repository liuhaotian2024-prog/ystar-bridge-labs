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
