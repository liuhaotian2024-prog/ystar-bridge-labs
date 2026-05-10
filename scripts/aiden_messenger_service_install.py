#!/usr/bin/env python3
from __future__ import annotations

import argparse
import plistlib
import subprocess
from pathlib import Path
from typing import Any


LABEL = "com.ystar.aiden-agent-native-messenger"
DEFAULT_LOG_ROOT = "/tmp/ystar_agent_native_messenger"
DEFAULT_YSTAR_GOV_ROOT = "/Users/haotianliu/.openclaw/workspace/Y-star-gov"


def build_plist(
    *,
    repo_root: Path,
    ystar_gov_root: Path = Path(DEFAULT_YSTAR_GOV_ROOT),
    port: int = 8784,
    runtime_timeout_seconds: int = 180,
    allow_live_network_by_default: bool = False,
    log_root: str = DEFAULT_LOG_ROOT,
) -> dict[str, Any]:
    env = {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONPATH": str(repo_root),
        "YSTAR_BRIDGE_LABS_ROOT": str(repo_root),
        "YSTAR_GOV_ROOT": str(ystar_gov_root),
        "AIDEN_MESSENGER_PORT": str(port),
        "AIDEN_MESSENGER_RUNTIME_TIMEOUT_SECONDS": str(runtime_timeout_seconds),
        "AIDEN_MESSENGER_ALLOW_LIVE_NETWORK": "1" if allow_live_network_by_default else "0",
    }
    return {
        "Label": LABEL,
        "ProgramArguments": [
            "/opt/homebrew/bin/python3.11",
            str(repo_root / "office" / "agent_native_messenger" / "server.py"),
        ],
        "WorkingDirectory": str(repo_root),
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": f"{log_root}/logs/aiden_messenger.stdout.log",
        "StandardErrorPath": f"{log_root}/logs/aiden_messenger.stderr.log",
        "EnvironmentVariables": env,
    }


def install_launch_agent(
    *,
    repo_root: Path,
    ystar_gov_root: Path = Path(DEFAULT_YSTAR_GOV_ROOT),
    port: int = 8784,
    runtime_timeout_seconds: int = 180,
    allow_live_network_by_default: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    log_root = Path(DEFAULT_LOG_ROOT)
    plist = build_plist(
        repo_root=repo_root,
        ystar_gov_root=ystar_gov_root,
        port=port,
        runtime_timeout_seconds=runtime_timeout_seconds,
        allow_live_network_by_default=allow_live_network_by_default,
        log_root=str(log_root),
    )
    target = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
    if dry_run:
        return {"installed": False, "dry_run": True, "target": str(target), "plist": plist}

    (log_root / "logs").mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as handle:
        plistlib.dump(plist, handle)

    domain = f"gui/{_uid()}"
    service = f"{domain}/{LABEL}"
    bootout = subprocess.run(["launchctl", "bootout", service], text=True, capture_output=True, check=False)
    bootstrap = subprocess.run(["launchctl", "bootstrap", domain, str(target)], text=True, capture_output=True, check=False)
    enable = subprocess.run(["launchctl", "enable", service], text=True, capture_output=True, check=False)
    kick = subprocess.run(["launchctl", "kickstart", "-k", service], text=True, capture_output=True, check=False)
    return {
        "installed": True,
        "target": str(target),
        "service": service,
        "port": port,
        "url": f"http://127.0.0.1:{port}",
        "bootout_returncode": bootout.returncode,
        "bootstrap_returncode": bootstrap.returncode,
        "bootstrap_stderr": bootstrap.stderr,
        "enable_returncode": enable.returncode,
        "kickstart_returncode": kick.returncode,
        "kickstart_stderr": kick.stderr,
        "log_root": str(log_root),
    }


def _uid() -> str:
    return subprocess.check_output(["id", "-u"], text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Install/restart Aiden Agent-Native Messenger as a local macOS LaunchAgent.")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--ystar-gov-root", default=DEFAULT_YSTAR_GOV_ROOT)
    parser.add_argument("--port", type=int, default=8784)
    parser.add_argument("--runtime-timeout-seconds", type=int, default=180)
    parser.add_argument("--allow-live-network-by-default", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = install_launch_agent(
        repo_root=Path(args.repo_root),
        ystar_gov_root=Path(args.ystar_gov_root),
        port=args.port,
        runtime_timeout_seconds=args.runtime_timeout_seconds,
        allow_live_network_by_default=args.allow_live_network_by_default,
        dry_run=args.dry_run,
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
