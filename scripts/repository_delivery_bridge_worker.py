#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import glob
import json
import os
import shutil
import subprocess
import tarfile
import time
from pathlib import Path
from typing import Any

from repository_delivery_bridge_schema import (
    BRIDGE_ROOT,
    COMPLETED_DIR,
    DEFAULT_FORBIDDEN_PATTERNS,
    FAILED_DIR,
    PENDING_DIR,
    RUNNING_DIR,
    ensure_bridge_dirs,
    is_forbidden_path,
    redact_text,
    utc_now,
    validate_job,
    write_json,
)


def run(repo: Path, args: list[str], timeout: int = 180, env: dict[str, str] | None = None) -> dict[str, Any]:
    completed = subprocess.run(
        args,
        cwd=repo,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        env=env,
    )
    return {
        "command": args,
        "returncode": completed.returncode,
        "stdout": redact_text((completed.stdout or "").strip()),
        "stderr": redact_text((completed.stderr or "").strip()),
    }


def parse_status_porcelain(output: str) -> list[str]:
    paths: list[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 and line[2] == " " else line[2:].lstrip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.strip())
    return paths


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch("/" + path, pattern) for pattern in patterns)


def cleanup_generated_files(repo_root: Path) -> list[str]:
    return cleanup_transient_generated_files(repo_root)


def is_transient_generated_path(path: str) -> bool:
    path = strip_dirty_prefix(path)
    normalized = Path(path)
    parts = normalized.parts
    basename = normalized.name
    return (
        "__pycache__" in parts
        or basename.endswith(".pyc")
        or basename.endswith(".pyo")
        or ".pytest_cache" in parts
        or ".mypy_cache" in parts
        or ".ruff_cache" in parts
        or basename == ".DS_Store"
        or basename.startswith("._")
        or "__MACOSX" in parts
    )


def strip_dirty_prefix(path: str) -> str:
    for prefix in ("forbidden_dirty:", "unexpected_dirty_file:", "transient_dirty:"):
        if path.startswith(prefix):
            return path[len(prefix) :]
    return path


def safe_dirty_relative_path(path: str) -> Path | None:
    stripped = strip_dirty_prefix(path).strip()
    candidate = Path(stripped)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    if ".git" in candidate.parts:
        return None
    return candidate


def nearest_transient_target(repo_root: Path, path: Path) -> Path | None:
    parts = path.parts
    for cache_name in ("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__MACOSX"):
        if cache_name in parts:
            index = parts.index(cache_name)
            return repo_root.joinpath(*parts[: index + 1])
    basename = path.name
    if basename == ".DS_Store" or basename.startswith("._") or basename.endswith((".pyc", ".pyo")):
        return repo_root / path
    return None


def cleanup_transient_dirty_paths(repo_root: Path, dirty_entries: list[str]) -> list[str]:
    removed: list[str] = []
    repo_root = Path(repo_root).resolve()
    for entry in dirty_entries:
        rel = safe_dirty_relative_path(entry)
        if rel is None or not is_transient_generated_path(str(rel)):
            continue
        target = nearest_transient_target(repo_root, rel)
        if target is None or ".git" in target.parts:
            continue
        if target.exists() and target.is_dir():
            removed.append(str(target.relative_to(repo_root)))
            shutil.rmtree(target)
        elif target.exists() and (target.is_file() or target.is_symlink()):
            removed.append(str(target.relative_to(repo_root)))
            target.unlink()
    return sorted(set(removed))


def cleanup_transient_generated_files(repo_root: Path) -> list[str]:
    removed: list[str] = []
    repo_root = Path(repo_root).resolve()

    def in_git(path: Path) -> bool:
        return ".git" in path.parts

    for path in sorted(repo_root.rglob("__pycache__"), key=lambda item: len(item.parts), reverse=True):
        if not in_git(path) and path.is_dir():
            removed.append(str(path.relative_to(repo_root)))
            shutil.rmtree(path)

    for pattern in ("*.pyc", "*.pyo"):
        for path in repo_root.rglob(pattern):
            if not in_git(path) and path.is_file():
                removed.append(str(path.relative_to(repo_root)))
                path.unlink()

    for cache_name in (".pytest_cache", ".mypy_cache", ".ruff_cache"):
        for path in sorted(repo_root.rglob(cache_name), key=lambda item: len(item.parts), reverse=True):
            if not in_git(path) and path.is_dir():
                removed.append(str(path.relative_to(repo_root)))
                shutil.rmtree(path)

    for path in repo_root.rglob(".DS_Store"):
        if not in_git(path) and path.is_file():
            removed.append(str(path.relative_to(repo_root)))
            path.unlink()

    for path in repo_root.rglob("._*"):
        if not in_git(path) and path.is_file():
            removed.append(str(path.relative_to(repo_root)))
            path.unlink()

    for path in sorted(repo_root.rglob("__MACOSX"), key=lambda item: len(item.parts), reverse=True):
        if not in_git(path) and path.is_dir():
            removed.append(str(path.relative_to(repo_root)))
            shutil.rmtree(path)

    return sorted(set(removed))


def safe_cleanup_metadata(repo_root: Path) -> list[str]:
    return cleanup_generated_files(repo_root)


def safe_tar_members(tar: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members: list[tarfile.TarInfo] = []
    for member in tar.getmembers():
        name = member.name
        parts = Path(name).parts
        basename = Path(name).name
        if Path(name).is_absolute() or ".." in parts:
            continue
        if "__MACOSX" in parts or basename == ".DS_Store" or basename.startswith("._"):
            continue
        members.append(member)
    return members


def unpack_payload(job: dict[str, Any], repo_root: Path) -> list[str]:
    payload = Path(job["payload_path"]).expanduser()
    extracted: list[str] = []
    with tarfile.open(payload, "r:gz") as tar:
        members = safe_tar_members(tar)
        for member in members:
            if member.isfile():
                extracted.append(member.name)
        tar.extractall(repo_root, members=members)
    return extracted


def expand_command(repo_root: Path, command: str) -> list[str]:
    parts = command.split()
    expanded: list[str] = []
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


def dirty_paths(repo_root: Path) -> list[str]:
    result = run(repo_root, ["git", "status", "--porcelain=v1", "-uall"], timeout=60)
    if result["returncode"] != 0:
        return [f"<git-status-failed:{result['stderr']}>"]
    return parse_status_porcelain(result["stdout"])


def validate_dirty_set(repo_root: Path, job: dict[str, Any]) -> tuple[bool, list[str]]:
    allowed = set(job["allowed_files"])
    force_allowed = set(job.get("force_add_allowlisted_files", []))
    forbidden = job.get("forbidden_patterns") or DEFAULT_FORBIDDEN_PATTERNS
    unexpected: list[str] = []
    for path in dirty_paths(repo_root):
        if path in allowed or path in force_allowed:
            continue
        if is_forbidden_path(path, forbidden):
            unexpected.append(f"forbidden_dirty:{path}")
        else:
            unexpected.append(path)
    return (not unexpected, unexpected)


def classify_dirty_set(repo_root: Path, job: dict[str, Any]) -> dict[str, list[str]]:
    allowed = set(job["allowed_files"])
    force_allowed = set(job.get("force_add_allowlisted_files", []))
    forbidden = job.get("forbidden_patterns") or DEFAULT_FORBIDDEN_PATTERNS
    classified = {
        "all_dirty_files": [],
        "allowed_dirty_files": [],
        "transient_dirty_files": [],
        "persistent_unsafe_dirty_files": [],
        "unexpected_non_allowed_dirty_files": [],
    }
    for path in dirty_paths(repo_root):
        classified["all_dirty_files"].append(path)
        if path in allowed or path in force_allowed:
            classified["allowed_dirty_files"].append(path)
        elif is_transient_generated_path(path):
            classified["transient_dirty_files"].append(f"forbidden_dirty:{path}")
        elif is_forbidden_path(path, forbidden):
            classified["persistent_unsafe_dirty_files"].append(f"forbidden_dirty:{path}")
        else:
            classified["unexpected_non_allowed_dirty_files"].append(path)
    return classified


def dirty_entry_facts(repo_root: Path, dirty_entries: list[str]) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for entry in dirty_entries:
        rel = safe_dirty_relative_path(entry)
        if rel is None:
            facts.append({"entry": entry, "safe_relative_path": False})
            continue
        target = repo_root / rel
        nearest = nearest_transient_target(repo_root, rel)
        facts.append(
            {
                "entry": entry,
                "safe_relative_path": True,
                "target": str(target),
                "target_exists": target.exists(),
                "nearest_transient_target": str(nearest) if nearest else "",
                "nearest_transient_target_exists": nearest.exists() if nearest else False,
            }
        )
    return facts


def clean_and_validate_dirty_set(repo_root: Path, job: dict[str, Any], report: dict[str, Any], label: str) -> tuple[bool, str, list[str]]:
    classified = classify_dirty_set(repo_root, job)
    report[f"{label}_dirty_files"] = classified["all_dirty_files"]
    if classified["transient_dirty_files"]:
        report[f"{label}_transient_dirty_files"] = classified["transient_dirty_files"]
        dirty_cleanup = cleanup_transient_dirty_paths(repo_root, classified["transient_dirty_files"])
        broad_cleanup = cleanup_transient_generated_files(repo_root)
        removed = sorted(set(dirty_cleanup + broad_cleanup))
        report[f"{label}_transient_cleanup"] = removed
        report[f"{label}_dirty_after_transient_cleanup"] = dirty_paths(repo_root)
        if not removed:
            report[f"{label}_transient_cleanup_path_facts"] = dirty_entry_facts(repo_root, classified["transient_dirty_files"])
            return False, "TRANSIENT_CLEANUP_FAILED", classified["transient_dirty_files"]
        classified = classify_dirty_set(repo_root, job)
    report[f"{label}_persistent_unsafe_dirty_files"] = classified["persistent_unsafe_dirty_files"]
    report[f"{label}_unexpected_non_allowed_dirty_files"] = classified["unexpected_non_allowed_dirty_files"]
    if classified["transient_dirty_files"]:
        report[f"{label}_remaining_transient_dirty_files"] = classified["transient_dirty_files"]
        return False, "TRANSIENT_CLEANUP_FAILED", classified["transient_dirty_files"]
    if classified["persistent_unsafe_dirty_files"] or classified["unexpected_non_allowed_dirty_files"]:
        return (
            False,
            "WORKTREE_DIRTY_UNEXPECTED",
            classified["persistent_unsafe_dirty_files"] + classified["unexpected_non_allowed_dirty_files"],
        )
    return True, "", []


def clean_stale_job(job_id: str, bridge_root: Path = BRIDGE_ROOT) -> list[str]:
    removed: list[str] = []
    for queue in ["pending", "running"]:
        for suffix in [".json", ".report.json", ".report.md"]:
            path = bridge_root / queue / f"{job_id}{suffix}"
            if path.exists():
                path.unlink()
                removed.append(str(path))
    return removed


def git_check_ignored(repo_root: Path, paths: list[str]) -> dict[str, dict[str, Any]]:
    ignored: dict[str, dict[str, Any]] = {}
    for path in paths:
        result = run(repo_root, ["git", "check-ignore", "-v", path], timeout=30)
        if result["returncode"] == 0:
            ignored[path] = result
    return ignored


def safe_git_add(repo_root: Path, job: dict[str, Any]) -> dict[str, Any]:
    allowed = list(job["allowed_files"])
    force_allowed = list(job.get("force_add_allowlisted_files", []))
    forbidden = job.get("forbidden_patterns") or DEFAULT_FORBIDDEN_PATTERNS
    for path in force_allowed:
        if path not in allowed:
            return {"ok": False, "failure_code": "FORCE_ADD_NOT_ALLOWLISTED", "path": path}
        if is_forbidden_path(path, forbidden):
            return {"ok": False, "failure_code": "FORCE_ADD_FORBIDDEN_FILE", "path": path}

    ignored = git_check_ignored(repo_root, allowed)
    ignored_not_force = sorted(path for path in ignored if path not in force_allowed)
    if ignored_not_force:
        return {
            "ok": False,
            "failure_code": "IGNORED_ALLOWED_FILE_NOT_FORCE_ALLOWLISTED",
            "ignored_files": ignored_not_force,
            "git_check_ignore_source": ignored,
        }

    normal = [path for path in allowed if path not in force_allowed]
    commands: list[dict[str, Any]] = []
    if normal:
        result = run(repo_root, ["git", "add", "--", *normal], timeout=60)
        commands.append(result)
        if result["returncode"] != 0:
            return {"ok": False, "failure_code": "GIT_ADD_FAILED", "commands": commands}
    if force_allowed:
        result = run(repo_root, ["git", "add", "-f", "--", *force_allowed], timeout=60)
        commands.append(result)
        if result["returncode"] != 0:
            return {"ok": False, "failure_code": "GIT_FORCE_ADD_FAILED", "commands": commands}
    return {
        "ok": True,
        "commands": commands,
        "ignored_by_gitignore": bool(ignored),
        "forced_add_allowlisted_files": force_allowed,
        "git_check_ignore_source": ignored,
    }


def classify_push_failure(text: str) -> str:
    lower = text.lower()
    if "could not resolve host" in lower or "nodename nor servname" in lower:
        return "PUSH_DNS_FAILED"
    if "authentication failed" in lower or "could not read username" in lower:
        return "PUSH_AUTH_FAILED"
    if "permission denied" in lower or "403" in lower or "write access" in lower:
        return "PUSH_PERMISSION_FAILED"
    if "protected branch" in lower or "pre-receive hook declined" in lower:
        return "PUSH_BRANCH_POLICY_FAILED"
    return "PUSH_FAILED"


def process_job(job: dict[str, Any], *, push: bool = True) -> dict[str, Any]:
    repo_root = Path(job["repo_path"]).expanduser()
    report: dict[str, Any] = {
        "job_id": job.get("job_id"),
        "status": "blocked",
        "started_at": utc_now(),
        "repo_path": str(repo_root),
        "repository_delivery_rt1": 1,
        "committed": False,
        "pushed": False,
        "remote_confirmed": False,
        "forced_add_allowlisted_files": [],
        "external_business_side_effects": False,
        "commands": [],
        "errors": [],
    }

    validation = validate_job(job)
    if not validation.ok:
        report["failure_code"] = "JOB_INVALID"
        report["errors"] = validation.errors
        return report

    branch = run(repo_root, ["git", "branch", "--show-current"], timeout=30)
    head = run(repo_root, ["git", "rev-parse", "HEAD"], timeout=30)
    report["commands"].extend([branch, head])
    report["branch"] = branch["stdout"]
    report["base_head"] = head["stdout"]
    if branch["returncode"] != 0 or branch["stdout"] != job["expected_branch"]:
        report["failure_code"] = "WRONG_BRANCH"
        return report
    if head["returncode"] != 0 or not head["stdout"].startswith(job["expected_base_head"]):
        report["failure_code"] = "BASE_HEAD_MISMATCH"
        return report

    report["cleanup_before"] = cleanup_generated_files(repo_root)
    report["extracted_files"] = unpack_payload(job, repo_root)
    report["cleanup_after_extract"] = cleanup_generated_files(repo_root)
    report["cleanup_before_initial_dirty_validation"] = cleanup_generated_files(repo_root)

    ok, failure_code, unexpected = clean_and_validate_dirty_set(repo_root, job, report, "initial_dirty_validation")
    if not ok:
        report["failure_code"] = failure_code
        report["unexpected_dirty_files"] = unexpected
        return report

    validation_env = dict(os.environ)
    validation_env["PYTHONDONTWRITEBYTECODE"] = "1"
    for command in job["validation_commands"]:
        result = run(repo_root, expand_command(repo_root, command), timeout=600, env=validation_env)
        report["commands"].append(result)
        if result["returncode"] != 0:
            report["cleanup_after_failed_validation"] = cleanup_generated_files(repo_root)
            report["failure_code"] = "VALIDATION_FAILED"
            report["failed_validation_command"] = command
            return report

    report["cleanup_after_validation"] = cleanup_generated_files(repo_root)
    report["cleanup_before_dirty_validation"] = cleanup_generated_files(repo_root)

    ok, failure_code, unexpected = clean_and_validate_dirty_set(repo_root, job, report, "final_dirty_validation")
    if not ok:
        report["failure_code"] = failure_code
        report["unexpected_dirty_files"] = unexpected
        return report

    add_result = safe_git_add(repo_root, job)
    report["git_add"] = add_result
    report["forced_add_allowlisted_files"] = add_result.get("forced_add_allowlisted_files", [])
    if not add_result.get("ok"):
        report["failure_code"] = add_result.get("failure_code", "GIT_ADD_FAILED")
        return report

    diff_cached = run(repo_root, ["git", "diff", "--cached", "--name-only"], timeout=60)
    report["commands"].append(diff_cached)
    if not diff_cached["stdout"].strip():
        report["committed"] = False
        result_head = run(repo_root, ["git", "rev-parse", "HEAD"], timeout=30)
    else:
        commit = run(repo_root, ["git", "commit", "-m", job["commit_message"]], timeout=120)
        report["commands"].append(commit)
        if commit["returncode"] != 0:
            report["failure_code"] = "COMMIT_FAILED"
            return report
        report["committed"] = True
        result_head = run(repo_root, ["git", "rev-parse", "HEAD"], timeout=30)
    report["commands"].append(result_head)
    report["result_head"] = result_head["stdout"]

    if not push:
        report["status"] = "DRY_RUN_COMPLETED"
        report["failure_code"] = "PUSH_SKIPPED_SMOKE_MODE"
        report["repository_delivery_rt1"] = 1
        return report

    push_result = run(repo_root, ["git", "push", job["push_remote"], f"HEAD:{job['push_branch']}"], timeout=300)
    report["commands"].append(push_result)
    if push_result["returncode"] != 0:
        report["failure_code"] = classify_push_failure(push_result["stderr"] + "\n" + push_result["stdout"])
        return report
    report["pushed"] = True

    confirm = run(repo_root, ["git", "ls-remote", job["push_remote"], job["push_branch"]], timeout=120)
    report["commands"].append(confirm)
    if confirm["returncode"] != 0:
        report["failure_code"] = "REMOTE_CONFIRMATION_FAILED"
        return report
    remote_head = confirm["stdout"].split()[0] if confirm["stdout"].split() else ""
    report["remote_head"] = remote_head
    if remote_head != report["result_head"]:
        report["failure_code"] = "REMOTE_HEAD_MISMATCH"
        return report

    report["status"] = "DELIVERY_SUCCEEDED"
    report["failure_code"] = "DELIVERY_SUCCEEDED"
    report["remote_confirmed"] = True
    report["repository_delivery_rt1"] = 0
    return report


def report_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Host-Local Repository Delivery Bridge Report",
            "",
            f"- job_id: {report.get('job_id')}",
            f"- status: {report.get('status')}",
            f"- failure_code: {report.get('failure_code')}",
            f"- repo_path: {report.get('repo_path')}",
            f"- branch: {report.get('branch')}",
            f"- base_head: {report.get('base_head')}",
            f"- result_head: {report.get('result_head', '')}",
            f"- remote_head: {report.get('remote_head', '')}",
            f"- committed: {str(report.get('committed')).lower()}",
            f"- pushed: {str(report.get('pushed')).lower()}",
            f"- remote_confirmed: {str(report.get('remote_confirmed')).lower()}",
            f"- repository_delivery_rt1: {report.get('repository_delivery_rt1')}",
            f"- forced_add_allowlisted_files: {', '.join(report.get('forced_add_allowlisted_files') or []) or 'none'}",
            "- no_external_business_side_effects: true",
            "",
        ]
    )


def handle_job_file(job_file: Path, *, bridge_root: Path = BRIDGE_ROOT, push: bool = True) -> dict[str, Any]:
    ensure_bridge_dirs(bridge_root)
    running = bridge_root / "running" / job_file.name
    job_file.rename(running)
    job = json.loads(running.read_text(encoding="utf-8"))
    report = process_job(job, push=push)
    target_dir = bridge_root / ("completed" if report.get("repository_delivery_rt1") == 0 else "failed")
    target_json = target_dir / f"{job['job_id']}.report.json"
    target_md = target_dir / f"{job['job_id']}.report.md"
    write_json(target_json, report)
    target_md.write_text(report_markdown(report), encoding="utf-8")
    running.rename(target_dir / running.name)
    return report


def run_once(*, bridge_root: Path = BRIDGE_ROOT, push: bool = True) -> int:
    ensure_bridge_dirs(bridge_root)
    pending = sorted((bridge_root / "pending").glob("*.json"))
    if not pending:
        return 0
    exit_code = 0
    for job_file in pending:
        report = handle_job_file(job_file, bridge_root=bridge_root, push=push)
        if report.get("repository_delivery_rt1") != 0:
            exit_code = 2
    return exit_code


def daemon_loop(*, bridge_root: Path = BRIDGE_ROOT, poll_interval: float = 5.0) -> int:
    ensure_bridge_dirs(bridge_root)
    while True:
        run_once(bridge_root=bridge_root, push=True)
        time.sleep(poll_interval)


def main() -> int:
    parser = argparse.ArgumentParser(description="Host-local repository delivery bridge worker.")
    parser.add_argument("--bridge-root", default=str(BRIDGE_ROOT))
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--daemon", action="store_true")
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--smoke-no-push", action="store_true", help="Process jobs without pushing; for fake repo smoke tests only.")
    args = parser.parse_args()
    bridge_root = Path(args.bridge_root)
    if args.daemon:
        return daemon_loop(bridge_root=bridge_root, poll_interval=args.poll_interval)
    return run_once(bridge_root=bridge_root, push=not args.smoke_no_push)



# D0_MANUAL_TRACKED_TRANSIENT_CLEANUP_PATCH_START
from pathlib import Path as _D0Path
import shutil as _d0_shutil
import subprocess as _d0_subprocess

def _d0_git(repo_root, args):
    return _d0_subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
        check=False,
    )

def _d0_strip_dirty_prefix(entry):
    s = str(entry).strip()
    for prefix in ("forbidden_dirty:", "unexpected_dirty_file:", "transient_dirty:"):
        if s.startswith(prefix):
            s = s[len(prefix):]
    if " -> " in s:
        s = s.split(" -> ", 1)[1]
    return s.strip().strip('"').strip("'")

def _d0_safe_rel(rel):
    p = _D0Path(rel)
    if p.is_absolute():
        return None
    if any(part in ("..", "") for part in p.parts):
        return None
    if ".git" in p.parts:
        return None
    return str(p)

def _d0_is_transient_rel(rel):
    p = _D0Path(rel)
    parts = p.parts
    name = p.name
    return (
        "__pycache__" in parts
        or ".pytest_cache" in parts
        or ".mypy_cache" in parts
        or ".ruff_cache" in parts
        or "__MACOSX" in parts
        or name.endswith(".pyc")
        or name.endswith(".pyo")
        or name == ".DS_Store"
        or name.startswith("._")
    )

def _d0_is_tracked(repo_root, rel):
    r = _d0_git(repo_root, ["ls-files", "--error-unmatch", "--", rel])
    return r.returncode == 0

def _d0_has_tracked_under(repo_root, rel_dir):
    rel_dir = str(rel_dir).rstrip("/") + "/"
    r = _d0_git(repo_root, ["ls-files", "--", rel_dir])
    return bool(r.stdout.strip())

def _d0_nearest_transient_target(repo_root, rel):
    p = _D0Path(rel)
    parts = list(p.parts)
    for marker in ("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__MACOSX"):
        if marker in parts:
            idx = parts.index(marker)
            return repo_root.joinpath(*parts[: idx + 1]), "/".join(parts[: idx + 1])
    return repo_root / p, str(p)

def cleanup_transient_dirty_paths(repo_root, dirty_entries):
    repo_root = _D0Path(repo_root).resolve()
    changed = []
    for entry in dirty_entries or []:
        rel = _d0_safe_rel(_d0_strip_dirty_prefix(entry))
        if not rel or not _d0_is_transient_rel(rel):
            continue

        # If Git tracks it, do NOT delete it. Restore tracked deletions instead.
        if _d0_is_tracked(repo_root, rel):
            target = repo_root / rel
            if not target.exists():
                r = _d0_git(repo_root, ["restore", "--", rel])
                if r.returncode == 0:
                    changed.append("restored_tracked:" + rel)
            continue

        target, target_rel = _d0_nearest_transient_target(repo_root, rel)

        if target.is_dir():
            if not _d0_has_tracked_under(repo_root, target_rel):
                _d0_shutil.rmtree(target, ignore_errors=True)
                changed.append(target_rel)
        elif target.is_file() or target.is_symlink():
            if not _d0_is_tracked(repo_root, target_rel):
                try:
                    target.unlink()
                    changed.append(target_rel)
                except FileNotFoundError:
                    pass
    return sorted(set(changed))

def cleanup_transient_generated_files(repo_root):
    repo_root = _D0Path(repo_root).resolve()
    changed = []

    # First handle tracked deletions already visible to Git.
    status = _d0_git(repo_root, ["status", "--porcelain=v1", "-uall"]).stdout.splitlines()
    dirty_paths = []
    for line in status:
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 and line[2] == " " else line[2:].lstrip()
        dirty_paths.append(path)
    changed.extend(cleanup_transient_dirty_paths(repo_root, dirty_paths))

    # Then remove untracked transient directories/files only.
    transient_dirs = []
    for marker in ("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__MACOSX"):
        transient_dirs.extend([p for p in repo_root.rglob(marker) if p.is_dir() and ".git" not in p.parts])

    for p in sorted(transient_dirs, key=lambda x: len(x.parts), reverse=True):
        rel = str(p.relative_to(repo_root))
        if not _d0_has_tracked_under(repo_root, rel):
            _d0_shutil.rmtree(p, ignore_errors=True)
            changed.append(rel)

    for pattern in ("*.pyc", "*.pyo", ".DS_Store", "._*"):
        for p in repo_root.rglob(pattern):
            if ".git" in p.parts:
                continue
            if p.is_file() or p.is_symlink():
                rel = str(p.relative_to(repo_root))
                if not _d0_is_tracked(repo_root, rel):
                    try:
                        p.unlink()
                        changed.append(rel)
                    except FileNotFoundError:
                        pass

    return sorted(set(changed))
# D0_MANUAL_TRACKED_TRANSIENT_CLEANUP_PATCH_END



# D0_MANUAL_COMPAT_CLEANUP_WRAPPER_START
try:
    _d0_cleanup_transient_generated_files_impl = cleanup_transient_generated_files
    def cleanup_transient_generated_files(repo_root=None):
        if repo_root is None:
            repo_root = REPO_ROOT if "REPO_ROOT" in globals() else Path("/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs")
        return _d0_cleanup_transient_generated_files_impl(repo_root)

    _d0_cleanup_transient_dirty_paths_impl = cleanup_transient_dirty_paths
    def cleanup_transient_dirty_paths(*args):
        if len(args) == 1:
            repo_root = REPO_ROOT if "REPO_ROOT" in globals() else Path("/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs")
            dirty_entries = args[0]
        else:
            repo_root, dirty_entries = args
        return _d0_cleanup_transient_dirty_paths_impl(repo_root, dirty_entries)
except NameError:
    pass
# D0_MANUAL_COMPAT_CLEANUP_WRAPPER_END


if __name__ == "__main__":
    raise SystemExit(main())
