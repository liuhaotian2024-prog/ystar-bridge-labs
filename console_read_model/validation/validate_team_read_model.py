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

    print_report(report)
    return 0 if not report.failed else 1


def print_report(report: Report) -> None:
    status = "PASS" if not report.failed else "FAIL"
    print(f"Static Team Read Model Validator: {status}")
    print(f"Checks passed: {len(report.passed)}")
    print(f"Checks failed: {len(report.failed)}")
    print(f"Warnings: {len(report.warnings)}")
    print(f"Files inspected: {len(report.files_inspected)}")

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
