#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Iterable


BRIDGE_ROOT = Path("/tmp/ystar_delivery_bridge")
BRIDGE_LABEL = "com.ystar.repository-delivery-bridge"


def run_git(repo: Path, args: list[str], timeout: int = 60) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return {
        "command": ["git", *args],
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
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


def command_text(result: dict[str, Any]) -> str:
    return "\n".join(part for part in [result.get("stdout", ""), result.get("stderr", "")] if part)


def classify_transport(repo: Path, facts: dict[str, Any]) -> str:
    if not facts["exists"] or not facts["is_git_repo"]:
        return "unknown_blocker"
    if facts["dirty_set"]:
        return "direct_push_blocked_by_dirty_state"
    ls_remote = facts.get("ls_remote_current_branch", {})
    dry_run = facts.get("push_dry_run", {})
    text = (command_text(ls_remote) + "\n" + command_text(dry_run)).lower()
    if ls_remote.get("returncode") != 0:
        if "could not resolve host" in text or "temporary failure in name resolution" in text:
            return "direct_push_blocked_by_network"
        if "authentication failed" in text or "could not read username" in text:
            return "direct_push_blocked_by_auth"
        if "permission denied" in text:
            return "direct_push_blocked_by_auth"
        return "host_side_bootstrap_required"
    if dry_run.get("returncode") == 0:
        return "direct_push_available"
    if "protected branch" in text or "pre-receive hook declined" in text:
        return "direct_push_blocked_by_branch_policy"
    if "permission" in text or "403" in text or "write access" in text:
        return "direct_push_blocked_by_repo_permissions"
    if "could not resolve host" in text:
        return "direct_push_blocked_by_network"
    if os.environ.get("CODEX_SANDBOX") or os.environ.get("OPENAI_SANDBOX"):
        return "direct_push_blocked_by_sandbox"
    if facts.get("host_local_bridge", {}).get("available"):
        return "host_local_bridge_available"
    return "unknown_blocker"


def inspect_host_local_bridge(bridge_root: Path = BRIDGE_ROOT) -> dict[str, Any]:
    queues = {}
    for name in ["pending", "running", "completed", "failed", "logs"]:
        path = bridge_root / name
        queues[name] = {
            "exists": path.exists(),
            "count": len(list(path.glob("*"))) if path.exists() else 0,
        }
    launchctl = subprocess.run(
        ["launchctl", "list"],
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )
    combined = (launchctl.stdout or "") + "\n" + (launchctl.stderr or "")
    loaded = BRIDGE_LABEL in combined
    return {
        "bridge_root": str(bridge_root),
        "root_exists": bridge_root.exists(),
        "queues": queues,
        "launch_agent_loaded": loaded,
        "available": bridge_root.exists() and loaded,
        "future_owner_delivery_commands_required": False if loaded else None,
    }


def classify_direct_delivery_mode(repo_facts: dict[str, Any]) -> str:
    classification = repo_facts.get("transport_classification")
    bridge = repo_facts.get("host_local_bridge", {})
    if classification == "direct_push_available":
        return "native_direct_push_available"
    if bridge.get("available"):
        return "host_local_bridge_available"
    if bridge.get("root_exists"):
        return "bridge_install_required_once"
    return "blocked_no_delivery_channel"


def inspect_repo_transport(repo_path: str | Path) -> dict[str, Any]:
    repo = Path(repo_path)
    exists = repo.exists()
    facts: dict[str, Any] = {
        "repo_path": str(repo),
        "exists": exists,
        "is_git_repo": bool((repo / ".git").exists()) if exists else False,
        "worktree_writable": os.access(repo, os.W_OK) if exists else False,
        "git_dir_writable": os.access(repo / ".git", os.W_OK) if exists and (repo / ".git").exists() else False,
        "index_lock_present": (repo / ".git" / "index.lock").exists() if exists else False,
        "git_objects_writable": os.access(repo / ".git" / "objects", os.W_OK) if exists else False,
        "env_presence": {
            "HTTP_PROXY": bool(os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")),
            "HTTPS_PROXY": bool(os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")),
            "ALL_PROXY": bool(os.environ.get("ALL_PROXY") or os.environ.get("all_proxy")),
            "NO_PROXY": bool(os.environ.get("NO_PROXY") or os.environ.get("no_proxy")),
            "GITHUB_TOKEN": bool(os.environ.get("GITHUB_TOKEN")),
            "GH_TOKEN": bool(os.environ.get("GH_TOKEN")),
        },
        "host_local_bridge": inspect_host_local_bridge(),
    }
    if not facts["is_git_repo"]:
        facts["transport_classification"] = classify_transport(repo, {**facts, "dirty_set": []})
        return facts

    branch = run_git(repo, ["branch", "--show-current"])
    head = run_git(repo, ["rev-parse", "HEAD"])
    remote = run_git(repo, ["config", "--get", "remote.origin.url"])
    upstream = run_git(repo, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    status = run_git(repo, ["status", "--porcelain=v1", "-uall"])
    current_branch = branch["stdout"]

    facts.update(
        {
            "current_branch": current_branch,
            "head_sha": head["stdout"],
            "remote_url_protocol": "ssh" if remote["stdout"].startswith("git@") else "https" if remote["stdout"].startswith("https://") else "other",
            "remote_url_present": bool(remote["stdout"]),
            "upstream_branch": upstream["stdout"] if upstream["returncode"] == 0 else "",
            "dirty_set": parse_status_porcelain(status["stdout"]),
            "ls_remote_head": run_git(repo, ["ls-remote", "origin", "HEAD"], timeout=120),
            "ls_remote_current_branch": run_git(repo, ["ls-remote", "origin", current_branch], timeout=120),
            "push_dry_run": run_git(repo, ["push", "--dry-run", "origin", f"HEAD:{current_branch}"], timeout=120),
        }
    )
    facts["transport_classification"] = classify_transport(repo, facts)
    facts["direct_delivery_mode"] = classify_direct_delivery_mode(facts)
    facts["safe_credential_posture"] = {
        "tokens_printed": False,
        "credential_values_printed": False,
        "credential_helper_secret_read": False,
    }
    facts["fix_path"] = fix_path_for_classification(facts["transport_classification"])
    return facts


def fix_path_for_classification(classification: str) -> dict[str, Any]:
    fixes = {
        "direct_push_available": ("No owner action required.", False, True),
        "direct_push_blocked_by_auth": ("Use existing local gh/ssh/git credential helper; do not paste tokens into chat.", True, False),
        "direct_push_blocked_by_network": ("Run host-side bootstrap from normal Terminal or restore network/DNS egress.", True, False),
        "direct_push_blocked_by_repo_permissions": ("Confirm branch write permission or repository installation access.", True, False),
        "direct_push_blocked_by_dirty_state": ("Clean or commit only allowlisted files; delivery runner must fail closed.", False, True),
        "direct_push_blocked_by_branch_policy": ("Use allowed branch or PR flow; do not force push.", True, False),
        "direct_push_blocked_by_sandbox": ("Use host-side bootstrap until sandbox egress/auth is restored.", True, False),
        "host_side_bootstrap_required": ("Use one-command host-side bootstrap.", True, False),
        "unknown_blocker": ("Inspect command evidence in doctor report.", True, False),
        "host_local_bridge_available": ("Submit structured delivery jobs to the host-local bridge; no owner per-milestone bootstrap.", False, True),
    }
    description, owner_action, automation_can_fix = fixes.get(classification, fixes["unknown_blocker"])
    return {
        "description": description,
        "owner_action_required": owner_action,
        "automation_can_fix": automation_can_fix,
    }


def safe_git_add_allowlisted(repo: Path, allowed_files: list[str], force_add_files: list[str] | None = None) -> dict[str, Any]:
    force_add_files = force_add_files or []
    allowed = set(allowed_files)
    forced: list[str] = []
    normal = [path for path in allowed_files if path not in force_add_files]
    if normal:
        result = run_git(repo, ["add", "--", *normal])
        if result["returncode"] != 0:
            return {"status": "blocked", "failure_code": "GIT_ADD_FAILED", "result": result}
    for path in force_add_files:
        if path not in allowed:
            return {"status": "blocked", "failure_code": "FORCE_ADD_NOT_ALLOWLISTED", "path": path}
        if any(token in path for token in ["__pycache__", ".pyc", ".pyo", ".db", ".sqlite", ".wal", ".shm", ".log"]):
            return {"status": "blocked", "failure_code": "FORCE_ADD_UNSAFE_FILE", "path": path}
    if force_add_files:
        result = run_git(repo, ["add", "-f", "--", *force_add_files])
        if result["returncode"] != 0:
            return {"status": "blocked", "failure_code": "GIT_FORCE_ADD_FAILED", "result": result}
        forced = force_add_files
    return {"status": "ok", "forced_add_allowlisted_tests": forced}


def render_transport_report(results: Iterable[dict[str, Any]]) -> str:
    lines = ["# Repository Delivery Transport Doctor", ""]
    for result in results:
        lines.extend(
            [
                f"## {result['repo_path']}",
                f"- exists: {str(result.get('exists')).lower()}",
                f"- is_git_repo: {str(result.get('is_git_repo')).lower()}",
                f"- branch: {result.get('current_branch', 'unknown')}",
                f"- head: {result.get('head_sha', 'unknown')}",
                f"- remote_url_protocol: {result.get('remote_url_protocol', 'unknown')}",
                f"- dirty_count: {len(result.get('dirty_set', []))}",
                f"- transport_classification: {result.get('transport_classification')}",
                f"- direct_delivery_mode: {result.get('direct_delivery_mode', 'unknown')}",
                f"- host_local_bridge_available: {str(result.get('host_local_bridge', {}).get('available', False)).lower()}",
                f"- fix_path: {result.get('fix_path', {}).get('description', 'unknown')}",
                "",
            ]
        )
    lines.extend(
        [
            "## Credential Safety",
            "- token_values_printed: false",
            "- credential_values_printed: false",
            "- credential_helper_secret_read: false",
            "",
        ]
    )
    return "\n".join(lines)
