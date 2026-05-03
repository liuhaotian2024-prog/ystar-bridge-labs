#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import glob
import json
import os
import shlex
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


FAILURE_CODES = {
    "REQUEST_INVALID",
    "WRONG_REPO",
    "WRONG_BRANCH",
    "BASE_HEAD_MISMATCH",
    "WORKTREE_DIRTY_UNEXPECTED",
    "FORBIDDEN_FILE_PRESENT",
    "VALIDATION_FAILED",
    "COMMIT_FAILED",
    "PUSH_DNS_FAILED",
    "PUSH_AUTH_FAILED",
    "PUSH_PERMISSION_FAILED",
    "PUSH_REMOTE_OBJECT_FAILURE",
    "REMOTE_CONFIRMATION_FAILED",
    "DELIVERY_SUCCEEDED",
}

DEFAULT_FORBIDDEN_PATTERNS = [
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

ALLOWED_VALIDATION_PREFIXES = [
    ["python3.11", "-m", "py_compile"],
    ["python3", "-m", "py_compile"],
    ["pytest"],
    ["python3.11", "scripts/check_repository_delivery.py"],
    ["python3", "scripts/check_repository_delivery.py"],
]


@dataclass(frozen=True)
class CommandResult:
    command: List[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HostDeliveryResult:
    request_id: str
    milestone_id: str
    status: str
    failure_code: str
    repo_root: str
    expected_branch: str
    branch: str = ""
    expected_base_head: str = ""
    base_head: str = ""
    result_head: str = ""
    remote_head: str = ""
    repository_delivery_rt1: int = 1
    validation_results: List[CommandResult] = field(default_factory=list)
    committed: bool = False
    pushed: bool = False
    remote_confirmed: bool = False
    report_path: str = ""
    errors: List[str] = field(default_factory=list)
    no_external_side_effects_statement: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["validation_results"] = [item.to_dict() for item in self.validation_results]
        return data


def run(repo_root: Path, args: Sequence[str], timeout: int = 120, env: Dict[str, str] | None = None) -> CommandResult:
    completed = subprocess.run(
        list(args),
        cwd=repo_root,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        env=env,
    )
    return CommandResult(list(args), completed.returncode, completed.stdout.strip(), completed.stderr.strip())


def load_request(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def combined_output(result: CommandResult) -> str:
    return "\n".join(part for part in [result.stdout, result.stderr] if part)


def classify_git_failure(text: str) -> str:
    lowered = text.lower()
    if "could not resolve host" in lowered or "nodename nor servname" in lowered:
        return "PUSH_DNS_FAILED"
    if "authentication failed" in lowered or "could not read username" in lowered:
        return "PUSH_AUTH_FAILED"
    if "permission denied" in lowered or "403" in lowered or "write access" in lowered:
        return "PUSH_PERMISSION_FAILED"
    if "unable to create temporary object directory" in lowered or "remote unpack failed" in lowered:
        return "PUSH_REMOTE_OBJECT_FAILURE"
    return "REMOTE_CONFIRMATION_FAILED"


def parse_status_porcelain(output: str) -> List[str]:
    paths: List[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 and line[2] == " " else line[2:].lstrip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.strip())
    return paths


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch("/" + path, pattern) for pattern in patterns)


def validate_command(command: str) -> List[str]:
    errors: List[str] = []
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        return [f"invalid_command_syntax: {exc}"]
    if not parts:
        return ["empty_validation_command"]
    if any(token in command for token in [";", "&&", "||", "`", "$(", ">", "<", "|"]):
        errors.append("shell_injection_operator_blocked")
    if not any(parts[: len(prefix)] == prefix for prefix in ALLOWED_VALIDATION_PREFIXES):
        errors.append("validation_command_not_allowlisted")
    return errors


def expand_validation_args(repo_root: Path, parts: List[str]) -> List[str]:
    expanded: List[str] = []
    for part in parts:
        if any(mark in part for mark in ["*", "?", "["]):
            matches = sorted(glob.glob(str(repo_root / part)))
            if matches:
                expanded.extend(str(Path(match).relative_to(repo_root)) for match in matches)
            else:
                expanded.append(part)
        else:
            expanded.append(part)
    return expanded


def validate_request(request: Dict[str, Any]) -> List[str]:
    required = [
        "request_id",
        "milestone_id",
        "repo_root",
        "expected_branch",
        "expected_base_head",
        "commit_message",
        "allowed_files",
        "forbidden_patterns",
        "validation_commands",
        "push_remote",
        "push_branch",
        "remote_confirmation_required",
        "created_by",
        "created_at",
        "safety_boundary",
        "no_external_side_effects_statement",
    ]
    errors = [f"missing_{key}" for key in required if key not in request]
    if not isinstance(request.get("allowed_files"), list) or not request.get("allowed_files"):
        errors.append("allowed_files_required")
    if not isinstance(request.get("validation_commands"), list) or not request.get("validation_commands"):
        errors.append("validation_commands_required")
    for command in request.get("validation_commands", []):
        errors.extend(validate_command(str(command)))
    if request.get("push_remote") != "origin":
        errors.append("push_remote_must_be_origin")
    if request.get("remote_confirmation_required") is not True:
        errors.append("remote_confirmation_required_must_be_true")
    return list(dict.fromkeys(errors))


def safe_cleanup_bytecode(repo_root: Path) -> None:
    for pycache in repo_root.rglob("__pycache__"):
        if ".git" in pycache.parts:
            continue
        if pycache.is_dir():
            for child in pycache.rglob("*"):
                if child.is_file():
                    child.unlink()
            for directory in sorted([p for p in pycache.rglob("*") if p.is_dir()], reverse=True):
                directory.rmdir()
            pycache.rmdir()
    tracked = run(repo_root, ["git", "ls-files", "*.pyc", "*.pyo"], timeout=30)
    tracked_paths = [line.strip() for line in tracked.stdout.splitlines() if line.strip()]
    if tracked_paths:
        run(repo_root, ["git", "restore", "--", *tracked_paths], timeout=60)


def changed_paths(repo_root: Path) -> List[str]:
    status = run(repo_root, ["git", "status", "--porcelain"], timeout=30)
    return parse_status_porcelain(status.stdout)


def reject_unexpected_dirty(
    paths: List[str],
    allowed_files: List[str],
    forbidden_patterns: List[str],
    ignored_dirty_patterns: List[str] | None = None,
) -> List[str]:
    allowed = set(allowed_files)
    ignored = ignored_dirty_patterns or []
    errors: List[str] = []
    for path in paths:
        if matches_any(path, ignored):
            continue
        if matches_any(path, forbidden_patterns):
            errors.append(f"forbidden_file_present: {path}")
        elif path not in allowed:
            errors.append(f"unexpected_dirty_file: {path}")
    return errors


def stage_allowed_files(repo_root: Path, allowed_files: List[str]) -> CommandResult:
    return run(repo_root, ["git", "add", "--", *allowed_files], timeout=60)


def staged_paths(repo_root: Path) -> List[str]:
    result = run(repo_root, ["git", "diff", "--cached", "--name-only"], timeout=30)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def parse_ls_remote(output: str) -> str:
    for line in output.splitlines():
        parts = line.split()
        if parts:
            return parts[0]
    return ""


def report_text(result: HostDeliveryResult) -> str:
    lines = [
        "# Host-Side Repository Delivery Report",
        "",
        f"- request_id: {result.request_id}",
        f"- milestone_id: {result.milestone_id}",
        f"- status: {result.status}",
        f"- failure_code: {result.failure_code}",
        f"- repository_delivery_rt1: {result.repository_delivery_rt1}",
        f"- repo_root: {result.repo_root}",
        f"- expected_branch: {result.expected_branch}",
        f"- branch: {result.branch}",
        f"- expected_base_head: {result.expected_base_head}",
        f"- base_head: {result.base_head}",
        f"- result_head: {result.result_head or 'none'}",
        f"- remote_head: {result.remote_head or 'none'}",
        f"- committed: {str(result.committed).lower()}",
        f"- pushed: {str(result.pushed).lower()}",
        f"- remote_confirmed: {str(result.remote_confirmed).lower()}",
        "",
        "## Validation Results",
    ]
    for item in result.validation_results:
        lines.append(f"- `{shlex.join(item.command)}` -> {item.returncode}")
    lines.extend(["", "## Errors"])
    lines.extend(f"- {error}" for error in result.errors or ["none"])
    lines.extend(
        [
            "",
            "## CZL",
            "- Y*: host-side runner validates request/repo/branch/base/dirty-set, runs allowlisted tests, commits only allowed files, pushes, and confirms remote SHA.",
            f"- Xt: branch={result.branch}, base_head={result.base_head}, remote_head={result.remote_head or 'none'}",
            "- U: request validation, repo validation, validation commands, git add/commit/push/ls-remote confirmation.",
            f"- Yt+1: status={result.status}, committed={result.committed}, pushed={result.pushed}, remote_confirmed={result.remote_confirmed}",
            f"- Rt+1: {result.repository_delivery_rt1}",
            "",
            "## Safety Boundary",
            f"- {result.no_external_side_effects_statement}",
            "- force_push: false",
            "- history_rewrite: false",
            "- remote_url_mutation: false",
            "- arbitrary_shell_commands: false",
            "- commits_outside_allowed_files: false",
        ]
    )
    return "\n".join(lines)


def write_report(repo_root: Path, request: Dict[str, Any], result: HostDeliveryResult) -> Path:
    reports_dir = repo_root / "operations" / "repository_delivery" / "delivery_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"{request['request_id']}.md"
    result.report_path = str(path.relative_to(repo_root))
    path.write_text(report_text(result) + "\n", encoding="utf-8")
    return path


def execute_delivery(request_path: Path) -> HostDeliveryResult:
    request = load_request(request_path)
    repo_root = Path(request.get("repo_root", "")).expanduser().resolve()
    result = HostDeliveryResult(
        request_id=str(request.get("request_id", "")),
        milestone_id=str(request.get("milestone_id", "")),
        status="blocked",
        failure_code="REQUEST_INVALID",
        repo_root=str(repo_root),
        expected_branch=str(request.get("expected_branch", "")),
        expected_base_head=str(request.get("expected_base_head", "")),
        no_external_side_effects_statement=str(request.get("no_external_side_effects_statement", "")),
    )
    request_errors = validate_request(request)
    if request_errors:
        result.errors = request_errors
        return result
    if not (repo_root / ".git").exists():
        result.failure_code = "WRONG_REPO"
        result.errors = ["repo_root_is_not_git_repo"]
        return result

    if request.get("cleanup_generated_bytecode") is True:
        safe_cleanup_bytecode(repo_root)

    branch = run(repo_root, ["git", "branch", "--show-current"], timeout=30)
    head = run(repo_root, ["git", "rev-parse", "HEAD"], timeout=30)
    result.branch = branch.stdout.strip()
    result.base_head = head.stdout.strip()
    if result.branch != request["expected_branch"]:
        result.failure_code = "WRONG_BRANCH"
        result.errors = [f"expected {request['expected_branch']}, got {result.branch}"]
        write_report(repo_root, request, result)
        return result
    if not result.base_head.startswith(str(request["expected_base_head"])):
        result.failure_code = "BASE_HEAD_MISMATCH"
        result.errors = [f"expected {request['expected_base_head']}, got {result.base_head}"]
        write_report(repo_root, request, result)
        return result

    forbidden_patterns = list(request.get("forbidden_patterns") or DEFAULT_FORBIDDEN_PATTERNS)
    allowed_files = list(request["allowed_files"])
    ignored_dirty_patterns = list(request.get("ignored_dirty_patterns") or [])
    dirty_errors = reject_unexpected_dirty(changed_paths(repo_root), allowed_files, forbidden_patterns, ignored_dirty_patterns)
    if dirty_errors:
        result.failure_code = "FORBIDDEN_FILE_PRESENT" if any(error.startswith("forbidden_file") for error in dirty_errors) else "WORKTREE_DIRTY_UNEXPECTED"
        result.errors = dirty_errors
        write_report(repo_root, request, result)
        return result

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for command in request["validation_commands"]:
        parts = expand_validation_args(repo_root, shlex.split(command))
        command_result = run(repo_root, parts, timeout=600, env=env)
        result.validation_results.append(command_result)
        if command_result.returncode != 0:
            result.failure_code = "VALIDATION_FAILED"
            result.errors = [f"validation_failed: {command}"]
            write_report(repo_root, request, result)
            return result

    if request.get("cleanup_generated_bytecode") is True:
        safe_cleanup_bytecode(repo_root)
    dirty_errors = reject_unexpected_dirty(changed_paths(repo_root), allowed_files, forbidden_patterns, ignored_dirty_patterns)
    if dirty_errors:
        result.failure_code = "FORBIDDEN_FILE_PRESENT" if any(error.startswith("forbidden_file") for error in dirty_errors) else "WORKTREE_DIRTY_UNEXPECTED"
        result.errors = dirty_errors
        write_report(repo_root, request, result)
        return result

    add_result = stage_allowed_files(repo_root, allowed_files)
    if add_result.returncode != 0:
        result.failure_code = "COMMIT_FAILED"
        result.errors = [combined_output(add_result)]
        write_report(repo_root, request, result)
        return result
    staged = staged_paths(repo_root)
    if set(staged) != set(allowed_files):
        result.failure_code = "WORKTREE_DIRTY_UNEXPECTED"
        result.errors = [f"staged_paths_do_not_match_allowed_files: {staged}"]
        write_report(repo_root, request, result)
        return result

    commit = run(repo_root, ["git", "commit", "-m", request["commit_message"]], timeout=120)
    if commit.returncode != 0:
        result.failure_code = "COMMIT_FAILED"
        result.errors = [combined_output(commit)]
        write_report(repo_root, request, result)
        return result
    result.committed = True
    result.result_head = run(repo_root, ["git", "rev-parse", "HEAD"], timeout=30).stdout.strip()

    push = run(repo_root, ["git", "push", request["push_remote"], request["push_branch"]], timeout=300)
    if push.returncode != 0:
        result.failure_code = classify_git_failure(combined_output(push))
        result.errors = [combined_output(push), "Run this from owner normal Terminal, not Codex sandbox."]
        write_report(repo_root, request, result)
        return result
    result.pushed = True

    remote = run(repo_root, ["git", "ls-remote", request["push_remote"], request["push_branch"]], timeout=120)
    if remote.returncode != 0:
        result.failure_code = classify_git_failure(combined_output(remote))
        result.errors = [combined_output(remote)]
        write_report(repo_root, request, result)
        return result
    result.remote_head = parse_ls_remote(remote.stdout)
    if result.remote_head != result.result_head:
        result.failure_code = "REMOTE_CONFIRMATION_FAILED"
        result.errors = [f"remote_head {result.remote_head} != local_head {result.result_head}"]
        write_report(repo_root, request, result)
        return result

    result.status = "DELIVERY_SUCCEEDED"
    result.failure_code = "DELIVERY_SUCCEEDED"
    result.remote_confirmed = True
    result.repository_delivery_rt1 = 0
    write_report(repo_root, request, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Host-side safe repository delivery runner.")
    parser.add_argument("request", help="Path to a delivery request JSON file.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()
    result = execute_delivery(Path(args.request))
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(report_text(result))
        if result.report_path:
            print(f"\nreport_path: {result.report_path}")
    return 0 if result.repository_delivery_rt1 == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
