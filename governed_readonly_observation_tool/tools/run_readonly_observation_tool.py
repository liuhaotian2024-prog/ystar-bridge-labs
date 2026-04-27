#!/usr/bin/env python3
"""Run the governed read-only observation tool wrapper.

The runner reads only registry-approved generated JSON summaries. It rejects
unknown or unsafe sources before reading any requested source and never performs
external actions, live execution, CIEU persistence, or brain/memory writes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "governed_readonly_observation_tool" / "generated"
CONTRACT_PATH = GENERATED / "tool_contract.json"
REGISTRY_PATH = GENERATED / "allowed_source_registry.json"
TRACE_PATH = GENERATED / "tool_invocation_trace.json"
TOOL_ID = "governed_readonly_observation_tool_v0"

UNSAFE_PATH_PARTS = [
    ".git/",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "scripts/.logs",
    "reports/ceo/brain_dream_diffs",
    "reports/escalation",
    "reports/daily",
    "reports/drift_hourly",
    "backups/",
    "active-agent",
    "memory/WORLD_STATE.md",
    "BOARD_PENDING.md",
]
UNSAFE_SUFFIXES = [
    ".db",
    ".db-shm",
    ".db-wal",
    ".sqlite",
    ".sqlite3",
    ".log",
]


class ToolPolicyError(Exception):
    """Raised when a wrapper invocation violates the tool policy."""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json_path(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_repo_path(relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ToolPolicyError(f"absolute paths are not allowed: {relative_path}")
    normalized = str(candidate)
    if normalized.startswith("../") or "/../" in normalized:
        raise ToolPolicyError(f"path traversal is not allowed: {relative_path}")
    lowered = normalized.lower()
    for marker in UNSAFE_PATH_PARTS:
        if marker.lower() in lowered:
            raise ToolPolicyError(f"unsafe source path rejected: {relative_path}")
    for suffix in UNSAFE_SUFFIXES:
        if lowered.endswith(suffix):
            raise ToolPolicyError(f"unsafe source suffix rejected: {relative_path}")
    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ToolPolicyError(f"path escapes repository root: {relative_path}") from exc
    return resolved


def resolve_output_path(relative_path: str) -> Path:
    path = resolve_repo_path(relative_path)
    try:
        path.relative_to(GENERATED)
    except ValueError as exc:
        raise ToolPolicyError("output must be under governed_readonly_observation_tool/generated") from exc
    if path.suffix != ".json":
        raise ToolPolicyError("output must be a JSON file")
    return path


def load_registry() -> dict[str, dict[str, Any]]:
    data = load_json_path(REGISTRY_PATH)
    sources = data.get("sources", [])
    return {source["source_id"]: source for source in sources}


def load_contract() -> dict[str, Any]:
    contract = load_json_path(CONTRACT_PATH)
    if contract.get("tool_id") != TOOL_ID:
        raise ToolPolicyError("tool contract does not match runner tool id")
    return contract


def invocation_requested_live_behavior(invocation: dict[str, Any]) -> list[str]:
    blocked = []
    for field in [
        "live_action_requested",
        "external_action_requested",
        "brain_writeback_requested",
        "memory_ingestion_requested",
        "cieu_persistence_requested",
    ]:
        if invocation.get(field) is True:
            blocked.append(field)
    return blocked


def validate_invocation(invocation: dict[str, Any], registry: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    blocked: list[dict[str, Any]] = []
    if invocation.get("tool_id") != TOOL_ID:
        blocked.append(
            {
                "source_id": invocation.get("tool_id"),
                "reason": "wrong_tool_id",
            }
        )
    for field in invocation_requested_live_behavior(invocation):
        blocked.append({"source_id": field, "reason": "live_or_writeback_request_forbidden"})

    requested_sources = invocation.get("requested_sources", [])
    if not isinstance(requested_sources, list) or not requested_sources:
        blocked.append({"source_id": "requested_sources", "reason": "requested_sources_must_be_non_empty_array"})
        return blocked

    for source_id in requested_sources:
        if source_id not in registry:
            blocked.append({"source_id": source_id, "reason": "source_not_in_allowed_registry"})
            continue
        source = registry[source_id]
        if source.get("safe_to_read_now") is not True:
            blocked.append({"source_id": source_id, "reason": "source_not_safe_to_read_now"})
        if source.get("raw_runtime_artifact") is not False:
            blocked.append({"source_id": source_id, "reason": "raw_runtime_artifact_forbidden"})
        if source.get("requires_network") is not False:
            blocked.append({"source_id": source_id, "reason": "network_required_forbidden"})
        if source.get("requires_credentials") is not False:
            blocked.append({"source_id": source_id, "reason": "credentials_required_forbidden"})
        if source.get("read_mode") != "json_summary":
            blocked.append({"source_id": source_id, "reason": "only_json_summary_read_mode_allowed"})
        try:
            path = resolve_repo_path(str(source.get("source_path", "")))
        except ToolPolicyError as exc:
            blocked.append({"source_id": source_id, "reason": str(exc)})
            continue
        if path.suffix != ".json":
            blocked.append({"source_id": source_id, "reason": "only_json_sources_allowed"})
        if not path.exists():
            blocked.append({"source_id": source_id, "reason": "allowed_source_missing"})
        elif path.stat().st_size > int(source.get("max_bytes", 0)):
            blocked.append({"source_id": source_id, "reason": "allowed_source_exceeds_max_bytes"})
    return blocked


def compact_value(value: Any) -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float, str)):
        text = str(value)
        return text if len(text) <= 180 else text[:177] + "..."
    if isinstance(value, list):
        return {"list_count": len(value)}
    if isinstance(value, dict):
        return {"object_key_count": len(value), "keys": sorted(value.keys())[:10]}
    return str(type(value).__name__)


def summarize_source(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {"top_level_type": type(data).__name__}

    interesting: dict[str, Any] = {}
    for key, value in data.items():
        lowered = key.lower()
        if (
            isinstance(value, bool)
            or lowered in {"schema_name", "schema_version", "next_required_milestone", "warning"}
            or "count" in lowered
            or lowered.endswith("_enabled")
            or lowered.endswith("_defined")
            or lowered.endswith("_executed")
            or lowered.endswith("_supported")
            or lowered.endswith("_ready")
            or lowered.endswith("_allowed")
        ):
            interesting[key] = compact_value(value)
    return {
        "top_level_type": "object",
        "top_level_key_count": len(data),
        "top_level_keys": sorted(data.keys())[:16],
        "selected_fields": interesting,
    }


def build_success_result(
    invocation: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    requested_sources: list[str],
) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    read_sources = []
    for source_id in requested_sources:
        source = registry[source_id]
        path = resolve_repo_path(source["source_path"])
        data = load_json_path(path)
        summaries[source_id] = {
            "source_type": source.get("source_type"),
            "source_path": source.get("source_path"),
            "summary": summarize_source(data),
        }
        read_sources.append(
            {
                "source_id": source_id,
                "source_path": source.get("source_path"),
                "read_mode": source.get("read_mode"),
            }
        )

    return {
        "schema_name": "ystar.governed_readonly_observation_tool.generated.tool_result",
        "schema_version": "v0",
        "result_id": f"result-{invocation['invocation_id']}",
        "invocation_id": invocation["invocation_id"],
        "tool_id": TOOL_ID,
        "status": "success",
        "read_sources": read_sources,
        "normalized_observation": {
            "request_type": invocation.get("request_type"),
            "summary_level": invocation.get("requested_summary_level"),
            "source_summaries": summaries,
            "mission_state": "mission-bounded autonomy can use generated read-model summaries safely",
            "safety_state": "no live, external, persistence, brain, or memory action enabled",
        },
        "blocked_sources": [],
        "policy_decision": {
            "decision": "allow_readonly_dry_run",
            "reason": "all requested sources are in the safe generated/read-model registry",
            "requires_y_star_gov": invocation.get("requires_y_star_gov"),
            "requires_cieu_event": invocation.get("requires_cieu_event"),
        },
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "next_work_candidates": [
            {
                "candidate_id": "next-tool-bridge-001",
                "title": "Route governed read-only tool invocation through Pre-U bridge",
                "next_required_milestone": "L4.5 Governed Tool Invocation Through Pre-U Bridge v0",
                "live_enabled": False,
            },
            {
                "candidate_id": "next-observation-loop-002",
                "title": "Add recurring read-only observation loop fixture without scheduler activation",
                "live_enabled": False,
            },
        ],
        "notes": "Read-only generated summaries were normalized. No unsafe source or action was used.",
    }


def build_rejected_result(invocation: dict[str, Any], blocked: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_readonly_observation_tool.generated.tool_result",
        "schema_version": "v0",
        "result_id": f"result-{invocation.get('invocation_id', 'rejected')}",
        "invocation_id": invocation.get("invocation_id"),
        "tool_id": invocation.get("tool_id", TOOL_ID),
        "status": "rejected",
        "read_sources": [],
        "normalized_observation": {},
        "blocked_sources": blocked,
        "policy_decision": {
            "decision": "reject",
            "reason": "one or more requested sources or requested behaviors violated the read-only tool policy",
        },
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "next_work_candidates": [],
        "notes": "Invocation rejected before reading any requested source.",
    }


def run_invocation(invocation: dict[str, Any]) -> dict[str, Any]:
    load_contract()
    registry = load_registry()
    blocked = validate_invocation(invocation, registry)
    if blocked:
        return build_rejected_result(invocation, blocked)
    return build_success_result(invocation, registry, invocation["requested_sources"])


def build_trace(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_readonly_observation_tool.generated.tool_invocation_trace",
        "schema_version": "v0",
        "trace_id": f"trace-{result.get('invocation_id')}",
        "entries": [
            {
                "invocation_id": result.get("invocation_id"),
                "status": result.get("status"),
                "read_source_count": len(result.get("read_sources", [])),
                "blocked_source_count": len(result.get("blocked_sources", [])),
                "real_action_executed": False,
                "external_action_executed": False,
            }
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the governed read-only observation tool.")
    parser.add_argument("--input", required=True, help="Invocation JSON path")
    parser.add_argument("--output", required=True, help="Result JSON path under generated/")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        input_path = resolve_repo_path(args.input)
        output_path = resolve_output_path(args.output)
        invocation = load_json_path(input_path)
        if not isinstance(invocation, dict):
            raise ToolPolicyError("invocation must be a JSON object")
        result = run_invocation(invocation)
        write_json(output_path, result)
        write_json(TRACE_PATH, build_trace(result))
        print(f"Governed read-only observation tool: {result['status']}")
        print(f"read_sources: {len(result.get('read_sources', []))}")
        print(f"blocked_sources: {len(result.get('blocked_sources', []))}")
        return 0 if result["status"] == "success" else 2
    except Exception as exc:
        print(f"Governed read-only observation tool failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

