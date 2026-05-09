#!/usr/bin/env python3
from __future__ import annotations

import argparse
import plistlib
import subprocess
from pathlib import Path


LABEL = "com.ystar.host-runtime-service-bridge"
DEFAULT_BRIDGE_ROOT = "/tmp/ystar_host_runtime_bridge"


def build_plist(*, repo_root: Path, bridge_root: str = DEFAULT_BRIDGE_ROOT, poll_interval: float = 5.0) -> dict:
    return {
        "Label": LABEL,
        "ProgramArguments": [
            "/opt/homebrew/bin/python3.11",
            str(repo_root / "scripts" / "host_runtime_service_bridge_worker.py"),
            "--daemon",
            "--bridge-root",
            bridge_root,
            "--poll-interval",
            str(poll_interval),
        ],
        "WorkingDirectory": str(repo_root),
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": f"{bridge_root}/logs/host_runtime_service_bridge.stdout.log",
        "StandardErrorPath": f"{bridge_root}/logs/host_runtime_service_bridge.stderr.log",
        "EnvironmentVariables": {"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"},
    }


def install_launch_agent(*, repo_root: Path, dry_run: bool = False) -> dict:
    plist = build_plist(repo_root=repo_root)
    target = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
    if dry_run:
        return {"installed": False, "dry_run": True, "target": str(target), "plist": plist}
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as handle:
        plistlib.dump(plist, handle)
    bootstrap = subprocess.run(["launchctl", "bootstrap", f"gui/{_uid()}", str(target)], text=True, capture_output=True, check=False)
    if bootstrap.returncode != 0 and "already bootstrapped" not in (bootstrap.stderr or "").lower():
        # LaunchAgent may already exist; kickstart still refreshes it after code updates.
        pass
    subprocess.run(["launchctl", "enable", f"gui/{_uid()}/{LABEL}"], text=True, capture_output=True, check=False)
    kick = subprocess.run(["launchctl", "kickstart", "-k", f"gui/{_uid()}/{LABEL}"], text=True, capture_output=True, check=False)
    return {"installed": True, "target": str(target), "kickstart_returncode": kick.returncode, "kickstart_stderr": kick.stderr}


def _uid() -> str:
    return subprocess.check_output(["id", "-u"], text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Y* host runtime service bridge LaunchAgent.")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = install_launch_agent(repo_root=Path(args.repo_root), dry_run=args.dry_run)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
