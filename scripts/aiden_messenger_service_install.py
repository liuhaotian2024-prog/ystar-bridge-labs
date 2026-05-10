#!/usr/bin/env python3
from __future__ import annotations

import argparse
import plistlib
import subprocess
from pathlib import Path
from typing import Any


LABEL = "com.ystar.aiden-messenger-runtime"
LEGACY_LABELS = ("com.ystar.aiden-agent-native-messenger",)
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
    legacy_cleanup = cleanup_legacy_launch_agents(target.parent)
    with target.open("wb") as handle:
        plistlib.dump(plist, handle)

    domain = f"gui/{_uid()}"
    service = f"{domain}/{LABEL}"
    bootout = _run(["launchctl", "bootout", service])
    # macOS can leave a label enabled but absent after a broken bootstrap. Booting
    # out by plist path and then falling back to legacy load makes reinstalling
    # idempotent for owner-facing repair commands.
    bootout_by_path = _run(["launchctl", "bootout", domain, str(target)])
    bootstrap = subprocess.run(["launchctl", "bootstrap", domain, str(target)], text=True, capture_output=True, check=False)
    legacy_load = {"returncode": None, "stderr": "", "stdout": ""}
    if bootstrap.returncode != 0:
        legacy_load = _run(["launchctl", "load", "-w", str(target)])
    enable = subprocess.run(["launchctl", "enable", service], text=True, capture_output=True, check=False)
    kick = subprocess.run(["launchctl", "kickstart", "-k", service], text=True, capture_output=True, check=False)
    health = _run(["/usr/bin/curl", "-sS", "--max-time", "5", f"http://127.0.0.1:{port}/api/health"])
    return {
        "installed": True,
        "target": str(target),
        "service": service,
        "port": port,
        "url": f"http://127.0.0.1:{port}",
        "bootout_returncode": bootout.returncode,
        "bootout_stderr": bootout.stderr,
        "bootout_by_path_returncode": bootout_by_path["returncode"],
        "bootout_by_path_stderr": bootout_by_path["stderr"],
        "bootstrap_returncode": bootstrap.returncode,
        "bootstrap_stderr": bootstrap.stderr,
        "legacy_load_returncode": legacy_load["returncode"],
        "legacy_load_stderr": legacy_load["stderr"],
        "enable_returncode": enable.returncode,
        "kickstart_returncode": kick.returncode,
        "kickstart_stderr": kick.stderr,
        "health_returncode": health["returncode"],
        "health_stdout": health["stdout"],
        "health_stderr": health["stderr"],
        "legacy_cleanup": legacy_cleanup,
        "log_root": str(log_root),
    }


def cleanup_legacy_launch_agents(launch_agents_dir: Path) -> list[dict[str, Any]]:
    domain = f"gui/{_uid()}"
    cleaned: list[dict[str, Any]] = []
    for label in LEGACY_LABELS:
        service = f"{domain}/{label}"
        plist = launch_agents_dir / f"{label}.plist"
        by_service = _run(["launchctl", "bootout", service])
        by_path = _run(["launchctl", "bootout", domain, str(plist)]) if plist.exists() else {"returncode": None, "stderr": "", "stdout": ""}
        removed = False
        try:
            plist.unlink(missing_ok=True)
            removed = True
        except Exception:
            removed = False
        cleaned.append(
            {
                "label": label,
                "plist": str(plist),
                "bootout_returncode": by_service["returncode"],
                "bootout_by_path_returncode": by_path["returncode"],
                "removed_plist": removed,
            }
        )
    return cleaned


def _run(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(args, text=True, capture_output=True, check=False)
    return {
        "command": args,
        "returncode": completed.returncode,
        "stdout": (completed.stdout or "").strip(),
        "stderr": (completed.stderr or "").strip(),
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
