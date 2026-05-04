#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path("/tmp/ystar_delivery_bridge")
PENDING_DIR = BRIDGE_ROOT / "pending"
RUNNING_DIR = BRIDGE_ROOT / "running"
COMPLETED_DIR = BRIDGE_ROOT / "completed"
FAILED_DIR = BRIDGE_ROOT / "failed"
LOG_DIR = BRIDGE_ROOT / "logs"

ALLOWLISTED_REPOS = {
    "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
    "/Users/haotianliu/.openclaw/workspace/gov-mcp",
    "/Users/haotianliu/.openclaw/workspace/Y-star-gov",
    "/Users/haotianliu/.openclaw/workspace/ystar-company",
}

DEFAULT_FORBIDDEN_PATTERNS = [
    "._*",
    "**/._*",
    ".DS_Store",
    "**/.DS_Store",
    "__MACOSX/**",
    "**/__MACOSX/**",
    "**/__pycache__/**",
    "**/*.pyc",
    "*.pyc",
    "**/*.pyo",
    "*.pyo",
    "**/*.db",
    "*.db",
    "**/*.sqlite",
    "*.sqlite",
    "**/*.sqlite3",
    "*.sqlite3",
    "**/*.wal",
    "*.wal",
    "**/*.shm",
    "*.shm",
    "**/*.log",
    "*.log",
    "**/active-agent*",
    "**/active_agent*",
]

SECRET_FILE_BASENAMES = {
    ".env",
    "credentials.json",
    "credential.json",
    "secrets.json",
    "secret.json",
    "id_rsa",
    "id_ed25519",
}

SAFE_CREDENTIAL_TEST_BASENAMES = {
    "test_repository_delivery_bridge_sanitizes_credentials.py",
    "test_repository_delivery_bridge_redacts_credentials.py",
    "test_repository_delivery_bridge_credential_redaction.py",
    "test_repository_delivery_bridge_credential_safety.py",
}

ALLOWED_VALIDATION_PREFIXES = [
    ["python3.11", "-m", "py_compile"],
    ["python3", "-m", "py_compile"],
    ["pytest"],
    ["python3.11", "scripts/check_repository_delivery.py"],
    ["python3", "scripts/check_repository_delivery.py"],
    ["python3.11", "scripts/repository_delivery_bridge_smoke_test.py"],
    ["python3", "scripts/repository_delivery_bridge_smoke_test.py"],
]

REQUIRED_JOB_FIELDS = [
    "job_id",
    "created_at",
    "created_by",
    "repo_path",
    "expected_branch",
    "expected_base_head",
    "payload_path",
    "payload_sha256",
    "allowed_files",
    "force_add_allowlisted_files",
    "forbidden_patterns",
    "validation_commands",
    "commit_message",
    "push_remote",
    "push_branch",
    "remote_confirmation_required",
    "no_force_push",
    "no_history_rewrite",
    "no_remote_url_mutation",
    "no_external_side_effects_statement",
]


@dataclass(frozen=True)
class BridgeValidation:
    ok: bool
    errors: list[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_bridge_dirs(root: Path = BRIDGE_ROOT) -> None:
    for directory in ["pending", "running", "completed", "failed", "logs"]:
        (root / directory).mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def redact_text(value: str) -> str:
    value = re.sub(r"gh[pousr]_[A-Za-z0-9_]+", "[REDACTED_GH_TOKEN]", value)
    value = re.sub(r"github_pat_[A-Za-z0-9_]+", "[REDACTED_GITHUB_PAT]", value)
    value = re.sub(r"sk-[A-Za-z0-9_-]{12,}", "[REDACTED_SECRET]", value)
    value = re.sub(r"https://[^/@\\s]+@github.com/", "https://[REDACTED]@github.com/", value)
    return value


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch("/" + path, pattern) for pattern in patterns)


def is_forbidden_path(path: str, patterns: list[str] | None = None) -> bool:
    patterns = patterns or DEFAULT_FORBIDDEN_PATTERNS
    if matches_any(path, patterns):
        return True
    normalized = Path(path)
    parts = normalized.parts
    basename = normalized.name
    lower_basename = basename.lower()
    lower_parts = [part.lower() for part in parts]

    if len(parts) >= 3 and parts[0] == "tests" and parts[1] == "office" and basename in SAFE_CREDENTIAL_TEST_BASENAMES:
        return False

    if lower_basename in SECRET_FILE_BASENAMES:
        return True
    if lower_basename.startswith(".env."):
        return True
    if lower_basename.endswith((".pem", ".key")):
        return True
    if any(part in {".ssh", "credential", "credentials", "secret", "secrets"} for part in lower_parts[:-1]):
        return True
    if "_token" in lower_basename or "token_" in lower_basename or lower_basename.endswith("_token.json"):
        return True
    if "_secret" in lower_basename or "secret_" in lower_basename or lower_basename.endswith("_secret.json"):
        return True
    return False


def is_transient_payload_metadata(path: str) -> bool:
    normalized = Path(path)
    parts = normalized.parts
    basename = normalized.name
    if "__MACOSX" in parts or basename == ".DS_Store" or basename.startswith("._"):
        return True
    if "__pycache__" in parts or ".pytest_cache" in parts or ".mypy_cache" in parts or ".ruff_cache" in parts:
        return True
    return normalized.suffix in {".pyc", ".pyo"}


def payload_manifest_allowed_files(payload_path: str | Path) -> list[str]:
    payload = Path(payload_path).expanduser()
    allowed: list[str] = []
    with tarfile.open(payload, "r:gz") as tar:
        for member in tar.getmembers():
            name = member.name
            path = Path(name)
            if not member.isfile():
                continue
            if path.is_absolute() or ".." in path.parts:
                continue
            normalized = str(path)
            if is_transient_payload_metadata(normalized):
                continue
            allowed.append(normalized)
    return sorted(dict.fromkeys(allowed))


def validate_validation_command(command: str) -> list[str]:
    errors: list[str] = []
    if any(token in command for token in [";", "&&", "||", "`", "$(", ">", "<", "|"]):
        errors.append("arbitrary_shell_operator_blocked")
    parts = command.split()
    if not parts:
        errors.append("empty_validation_command")
        return errors
    if not any(parts[: len(prefix)] == prefix for prefix in ALLOWED_VALIDATION_PREFIXES):
        errors.append("validation_command_not_allowlisted")
    return errors


def validate_job(job: dict[str, Any], *, allowlisted_repos: set[str] | None = None) -> BridgeValidation:
    errors: list[str] = []
    allowlisted_repos = allowlisted_repos or ALLOWLISTED_REPOS

    for field in REQUIRED_JOB_FIELDS:
        if field not in job:
            errors.append(f"missing_{field}")

    if errors:
        return BridgeValidation(False, errors)

    repo_path = str(Path(job["repo_path"]).expanduser())
    if repo_path not in allowlisted_repos and not job.get("allow_temp_repo_for_smoke_test"):
        errors.append("repo_path_not_allowlisted")

    if job["push_remote"] != "origin":
        errors.append("push_remote_must_be_origin")
    if job["remote_confirmation_required"] is not True:
        errors.append("remote_confirmation_required_must_be_true")
    if job["no_force_push"] is not True:
        errors.append("force_push_not_allowed")
    if job["no_history_rewrite"] is not True:
        errors.append("history_rewrite_not_allowed")
    if job["no_remote_url_mutation"] is not True:
        errors.append("remote_url_mutation_not_allowed")

    allowed_files = job.get("allowed_files", [])
    force_add = job.get("force_add_allowlisted_files", [])
    forbidden_patterns = job.get("forbidden_patterns") or DEFAULT_FORBIDDEN_PATTERNS
    if not isinstance(allowed_files, list) or not allowed_files:
        errors.append("allowed_files_required")
    if not isinstance(force_add, list):
        errors.append("force_add_allowlisted_files_must_be_list")
    for path in allowed_files + force_add:
        if Path(path).is_absolute() or ".." in Path(path).parts:
            errors.append(f"unsafe_relative_path:{path}")
        if is_forbidden_path(path, forbidden_patterns):
            errors.append(f"forbidden_allowed_file:{path}")
    for path in force_add:
        if path not in allowed_files:
            errors.append(f"force_add_not_allowlisted:{path}")

    payload = Path(job["payload_path"]).expanduser()
    if not payload.exists():
        errors.append("payload_missing")
    elif sha256_file(payload) != job["payload_sha256"]:
        errors.append("payload_sha256_mismatch")

    for command in job.get("validation_commands", []):
        errors.extend(validate_validation_command(str(command)))

    return BridgeValidation(not errors, list(dict.fromkeys(errors)))


def build_job(
    *,
    job_id: str,
    repo_path: str,
    expected_branch: str,
    expected_base_head: str,
    payload_path: str,
    allowed_files: list[str],
    validation_commands: list[str],
    commit_message: str,
    push_branch: str,
    force_add_allowlisted_files: list[str] | None = None,
    created_by: str = "Codex",
) -> dict[str, Any]:
    payload = Path(payload_path).expanduser()
    return {
        "job_id": job_id,
        "created_at": utc_now(),
        "created_by": created_by,
        "repo_path": repo_path,
        "expected_branch": expected_branch,
        "expected_base_head": expected_base_head,
        "payload_path": str(payload),
        "payload_sha256": sha256_file(payload),
        "allowed_files": allowed_files,
        "force_add_allowlisted_files": force_add_allowlisted_files or [],
        "forbidden_patterns": DEFAULT_FORBIDDEN_PATTERNS,
        "validation_commands": validation_commands,
        "commit_message": commit_message,
        "push_remote": "origin",
        "push_branch": push_branch,
        "remote_confirmation_required": True,
        "no_force_push": True,
        "no_history_rewrite": True,
        "no_remote_url_mutation": True,
        "no_external_side_effects_statement": (
            "Repository delivery only. No customer contact, email/message, publication, payment, "
            "account creation, form submission, login, external validation submission, provider API call, "
            "or core brain/CIEU/memory canonical writeback is authorized."
        ),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
