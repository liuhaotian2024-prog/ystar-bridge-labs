#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from repository_delivery_bridge_schema import BRIDGE_ROOT, ensure_bridge_dirs, write_json


PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "com.ystar.repository-delivery-bridge.plist"


def launchctl_status() -> dict[str, Any]:
    result = subprocess.run(
        ["launchctl", "list"],
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )
    text = (result.stdout or "") + "\n" + (result.stderr or "")
    return {
        "launchctl_available": result.returncode in (0, 1),
        "plist_path": str(PLIST_PATH),
        "plist_exists": PLIST_PATH.exists(),
        "loaded": "com.ystar.repository-delivery-bridge" in text,
        "tokens_printed": False,
        "credential_values_printed": False,
    }


def collect_status(bridge_root: Path = BRIDGE_ROOT) -> dict[str, Any]:
    ensure_bridge_dirs(bridge_root)
    queues = {}
    for name in ["pending", "running", "completed", "failed", "logs"]:
        path = bridge_root / name
        queues[name] = sorted(item.name for item in path.glob("*") if item.name != ".gitkeep")
    last_completed = queues["completed"][-1] if queues["completed"] else ""
    last_failed = queues["failed"][-1] if queues["failed"] else ""
    status = {
        "artifact_id": "repository_delivery_bridge_status",
        "bridge_root": str(bridge_root),
        "queues": queues,
        "last_completed": last_completed,
        "last_failed": last_failed,
        "launch_agent": launchctl_status(),
        "bridge_installed": launchctl_status()["loaded"],
        "transport_mode": "host_local_bridge" if launchctl_status()["loaded"] else "bridge_install_required_once",
        "next_milestone_delivery_mode": "host_local_bridge" if launchctl_status()["loaded"] else "bridge_install_required_once",
        "job_submission_contract": "scripts/repository_delivery_bridge_submit.py",
        "per_milestone_bootstrap_allowed": False,
        "future_owner_delivery_commands_required": False if launchctl_status()["loaded"] else True,
    }
    return status


def render_markdown(status: dict[str, Any]) -> str:
    queues = status["queues"]
    launch_agent = status["launch_agent"]
    return "\n".join(
        [
            "# Repository Delivery Bridge Status",
            "",
            f"- bridge_root: {status['bridge_root']}",
            f"- transport_mode: {status['transport_mode']}",
            f"- bridge_installed: {str(status['bridge_installed']).lower()}",
            f"- launch_agent_plist_exists: {str(launch_agent['plist_exists']).lower()}",
            f"- launch_agent_loaded: {str(launch_agent['loaded']).lower()}",
            f"- pending_jobs: {len(queues['pending'])}",
            f"- running_jobs: {len(queues['running'])}",
            f"- completed_artifacts: {len(queues['completed'])}",
            f"- failed_artifacts: {len(queues['failed'])}",
            f"- future_owner_delivery_commands_required: {str(status['future_owner_delivery_commands_required']).lower()}",
            f"- per_milestone_bootstrap_allowed: {str(status['per_milestone_bootstrap_allowed']).lower()}",
            f"- job_submission_contract: `{status['job_submission_contract']}`",
            "- credentials_printed: false",
            "",
            "Future Codex tasks must submit bridge jobs.",
            "Future Codex tasks must not ask owner to run per-milestone bootstrap.",
            "Owner manual terminal command is only allowed for one-time bridge repair/reinstall.",
            "",
        ]
    )


def write_repo_reports(repo_root: Path, status: dict[str, Any]) -> None:
    reports = repo_root / "operations" / "repository_delivery" / "delivery_reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "repository_delivery_bridge_status.json", status)
    (reports / "repository_delivery_bridge_status.md").write_text(render_markdown(status), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Show host-local repository delivery bridge status.")
    parser.add_argument("--bridge-root", default=str(BRIDGE_ROOT))
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--write-repo-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    status = collect_status(Path(args.bridge_root))
    if args.write_repo_report and args.repo_root:
        write_repo_reports(Path(args.repo_root), status)
    if args.json:
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
