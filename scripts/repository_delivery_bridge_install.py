#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from repository_delivery_bridge_schema import BRIDGE_ROOT, ensure_bridge_dirs, utc_now, write_json
from repository_delivery_bridge_status import collect_status, render_markdown


LABEL = "com.ystar.repository-delivery-bridge"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def plist_text(repo_root: Path, bridge_root: Path) -> str:
    worker = repo_root / "scripts" / "repository_delivery_bridge_worker.py"
    log_dir = bridge_root / "logs"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/env</string>
    <string>python3.11</string>
    <string>{worker}</string>
    <string>--daemon</string>
    <string>--bridge-root</string>
    <string>{bridge_root}</string>
    <string>--poll-interval</string>
    <string>5</string>
  </array>
  <key>WorkingDirectory</key>
  <string>{repo_root}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>{log_dir / "repository_delivery_bridge.stdout.log"}</string>
  <key>StandardErrorPath</key>
  <string>{log_dir / "repository_delivery_bridge.stderr.log"}</string>
</dict>
</plist>
"""


def run(args: list[str]) -> dict:
    completed = subprocess.run(args, text=True, capture_output=True, timeout=60, check=False)
    return {
        "command": args,
        "returncode": completed.returncode,
        "stdout": (completed.stdout or "").strip(),
        "stderr": (completed.stderr or "").strip(),
    }


def install(repo_root: Path, bridge_root: Path = BRIDGE_ROOT, *, start: bool = True) -> dict:
    ensure_bridge_dirs(bridge_root)
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    result: dict = {
        "artifact_id": "host_local_delivery_bridge_install",
        "installed_at": utc_now(),
        "repo_root": str(repo_root),
        "bridge_root": str(bridge_root),
        "plist_path": str(PLIST_PATH),
        "one_time_setup_required": False,
        "future_owner_delivery_commands_required": False,
        "commands": [],
        "credentials_printed": False,
        "tokens_printed": False,
    }
    PLIST_PATH.write_text(plist_text(repo_root, bridge_root), encoding="utf-8")
    result["plist_written"] = True
    if start:
        load_attempts: list[dict] = []
        unload = run(["launchctl", "unload", str(PLIST_PATH)])
        load_attempts.append(unload)
        load = run(["launchctl", "load", str(PLIST_PATH)])
        load_attempts.append(load)
        if load["returncode"] != 0:
            bootstrap = run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(PLIST_PATH)])
            load_attempts.append(bootstrap)
            if bootstrap["returncode"] == 0:
                kickstart = run(["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/{LABEL}"])
                load_attempts.append(kickstart)
        result["commands"].extend(load_attempts)
        result["launchagent_load_attempts"] = load_attempts
    status = collect_status(bridge_root)
    result["bridge_status"] = status
    if start:
        result["started"] = bool(status.get("launch_agent", {}).get("loaded"))
    return result


def write_reports(repo_root: Path, result: dict) -> None:
    reports = repo_root / "operations" / "repository_delivery" / "delivery_reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "host_local_delivery_bridge_install.json", result)
    lines = [
        "# Host-Local Delivery Bridge Install",
        "",
        f"- installed_at: {result['installed_at']}",
        f"- repo_root: {result['repo_root']}",
        f"- bridge_root: {result['bridge_root']}",
        f"- plist_path: {result['plist_path']}",
        f"- plist_written: {str(result.get('plist_written')).lower()}",
        f"- started: {str(result.get('started', False)).lower()}",
        f"- one_time_setup_required: {str(result['one_time_setup_required']).lower()}",
        f"- future_owner_delivery_commands_required: {str(result['future_owner_delivery_commands_required']).lower()}",
        f"- per_milestone_bootstrap_allowed: {str(result.get('per_milestone_bootstrap_allowed', False)).lower()}",
        "- credentials_printed: false",
        "",
        render_markdown(result["bridge_status"]),
    ]
    (reports / "host_local_delivery_bridge_install.md").write_text("\n".join(lines), encoding="utf-8")


def installer_success_payload(self_delivery: dict, launchagent_loaded: bool) -> dict:
    remote_confirmed = bool(self_delivery.get("remote_confirmed"))
    repository_delivery_rt1 = 0 if remote_confirmed and launchagent_loaded else 1
    return {
        "status": "DELIVERY_SUCCEEDED" if repository_delivery_rt1 == 0 else "BLOCKED",
        "bridge_installed": bool(launchagent_loaded),
        "self_delivery": {
            "committed": bool(self_delivery.get("committed")),
            "pushed": bool(self_delivery.get("pushed")),
            "remote_confirmed": remote_confirmed,
            "repository_delivery_rt1": 0 if remote_confirmed else 1,
        },
        "future_owner_delivery_commands_required": False if repository_delivery_rt1 == 0 else True,
        "per_milestone_bootstrap_allowed": False if repository_delivery_rt1 == 0 else None,
        "next_milestone_delivery_mode": "host_local_bridge" if repository_delivery_rt1 == 0 else "bridge_repair_required",
        "repository_delivery_rt1": repository_delivery_rt1,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the host-local repository delivery bridge as a macOS LaunchAgent.")
    parser.add_argument("--repo-root", default="/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs")
    parser.add_argument("--bridge-root", default=str(BRIDGE_ROOT))
    parser.add_argument("--no-start", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    result = install(repo_root, Path(args.bridge_root), start=not args.no_start)
    write_reports(repo_root, result)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print((repo_root / "operations/repository_delivery/delivery_reports/host_local_delivery_bridge_install.md"))
    return 0 if result.get("started", True) or args.no_start else 2



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
