#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path("/tmp/ystar_host_runtime_bridge")
PENDING_DIR = BRIDGE_ROOT / "pending"
RUNNING_DIR = BRIDGE_ROOT / "running"
COMPLETED_DIR = BRIDGE_ROOT / "completed"
FAILED_DIR = BRIDGE_ROOT / "failed"
LOG_DIR = BRIDGE_ROOT / "logs"
SERVICE_DIR = BRIDGE_ROOT / "services"

ALLOWED_SERVICES = {"ollama_server"}
ALLOWED_ACTIONS = {
    "health_check",
    "start",
    "stop",
    "probe_models",
    "pull_allowlisted_model",
    "smoke_test_generate",
}
ALLOWED_MODELS = {"gemma4", "gemma4:e4b", "gemma4:latest", "gemma3", "gemma3:latest", "ystar-gemma"}
ALLOWED_OLLAMA_EXECUTABLES = {"ollama", "/opt/homebrew/bin/ollama"}


@dataclass(frozen=True)
class RuntimeBridgeValidation:
    ok: bool
    errors: list[str]


def ensure_bridge_dirs(root: Path = BRIDGE_ROOT) -> None:
    for name in ("pending", "running", "completed", "failed", "logs", "services"):
        (root / name).mkdir(parents=True, exist_ok=True)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def validate_service_job(job: dict[str, Any]) -> RuntimeBridgeValidation:
    required = [
        "job_id",
        "service_order_id",
        "service_order_hash",
        "service_id",
        "requested_action",
        "command_plan",
        "safety_boundary",
        "no_external_business_side_effects_statement",
    ]
    errors = [f"missing_{field}" for field in required if field not in job]
    if errors:
        return RuntimeBridgeValidation(False, errors)

    if job.get("service_id") not in ALLOWED_SERVICES:
        errors.append("service_not_allowlisted")
    if job.get("requested_action") not in ALLOWED_ACTIONS:
        errors.append("action_not_allowlisted")
    safety = job.get("safety_boundary") if isinstance(job.get("safety_boundary"), dict) else {}
    if safety.get("host_local_only") is not True:
        errors.append("host_local_only_required")
    if safety.get("external_business_side_effects") is not False:
        errors.append("external_business_side_effects_must_be_false")
    if safety.get("arbitrary_shell_allowed") is not False:
        errors.append("arbitrary_shell_must_be_false")
    errors.extend(validate_command_plan(job.get("command_plan"), action=str(job.get("requested_action") or "")))
    return RuntimeBridgeValidation(not errors, sorted(dict.fromkeys(errors)))


def validate_command_plan(command_plan: Any, *, action: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(command_plan, dict):
        return ["command_plan_not_mapping"]
    if command_plan.get("shell") is True:
        errors.append("shell_execution_forbidden")
    argv = command_plan.get("command_argv")
    if not isinstance(argv, list) or not argv:
        return ["command_argv_required"]
    parts = [str(part) for part in argv]
    if any(_has_shell_operator(part) for part in parts):
        errors.append("shell_operator_forbidden")
    if parts[0] not in ALLOWED_OLLAMA_EXECUTABLES:
        errors.append("executable_not_allowlisted")
    subcommand = parts[1] if len(parts) > 1 else ""
    allowed_subcommands = {
        "health_check": {"list", "--version"},
        "start": {"serve"},
        "stop": {"service-stop"},
        "probe_models": {"list"},
        "pull_allowlisted_model": {"pull"},
        "smoke_test_generate": {"run"},
    }
    if subcommand not in allowed_subcommands.get(action, set()):
        errors.append("subcommand_does_not_match_action")
    if action in {"pull_allowlisted_model", "smoke_test_generate"}:
        model = str(command_plan.get("model_name") or (parts[2] if len(parts) > 2 else ""))
        if model not in ALLOWED_MODELS:
            errors.append("model_not_allowlisted")
    return errors


def is_safe_service_job_path(path: Path) -> bool:
    return path.suffix == ".json" and not any(fnmatch.fnmatch(path.name, pattern) for pattern in ("._*", ".DS_Store"))


def _has_shell_operator(value: str) -> bool:
    return any(token in value for token in (";", "&&", "||", "`", "$(", ">", "<", "|"))


__all__ = [
    "BRIDGE_ROOT",
    "PENDING_DIR",
    "RUNNING_DIR",
    "COMPLETED_DIR",
    "FAILED_DIR",
    "LOG_DIR",
    "SERVICE_DIR",
    "ALLOWED_MODELS",
    "ensure_bridge_dirs",
    "sha256_json",
    "validate_service_job",
    "validate_command_plan",
    "is_safe_service_job_path",
]
