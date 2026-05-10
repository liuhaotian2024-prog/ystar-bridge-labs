#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


DEFAULT_LOG_ROOT = Path("/tmp/ystar_agent_native_messenger")
DEFAULT_YSTAR_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")


def start_background(
    *,
    repo_root: Path,
    ystar_gov_root: Path = DEFAULT_YSTAR_GOV_ROOT,
    port: int = 8784,
    runtime_timeout_seconds: int = 180,
    allow_live_network_by_default: bool = False,
) -> dict[str, Any]:
    log_dir = DEFAULT_LOG_ROOT / "logs"
    service_dir = DEFAULT_LOG_ROOT / "services" / "aiden_messenger"
    log_dir.mkdir(parents=True, exist_ok=True)
    service_dir.mkdir(parents=True, exist_ok=True)
    pid_file = service_dir / "aiden_messenger.pid"
    existing = _read_live_pid(pid_file)
    if existing:
        health = health_check(port=port)
        return {"status": "already_running", "pid": existing, "health": health, "url": f"http://127.0.0.1:{port}"}

    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(repo_root),
            "YSTAR_BRIDGE_LABS_ROOT": str(repo_root),
            "YSTAR_GOV_ROOT": str(ystar_gov_root),
            "AIDEN_MESSENGER_PORT": str(port),
            "AIDEN_MESSENGER_RUNTIME_TIMEOUT_SECONDS": str(runtime_timeout_seconds),
            "AIDEN_MESSENGER_ALLOW_LIVE_NETWORK": "1" if allow_live_network_by_default else "0",
        }
    )
    stdout_path = log_dir / "aiden_messenger.background.stdout.log"
    stderr_path = log_dir / "aiden_messenger.background.stderr.log"
    with stdout_path.open("ab") as stdout, stderr_path.open("ab") as stderr:
        process = subprocess.Popen(
            [sys.executable, str(repo_root / "office" / "agent_native_messenger" / "server.py")],
            cwd=str(repo_root),
            env=env,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
    pid_file.write_text(str(process.pid), encoding="utf-8")
    time.sleep(2)
    health = health_check(port=port)
    return {
        "status": "started" if health["ok"] else "started_but_health_failed",
        "pid": process.pid,
        "pid_file": str(pid_file),
        "url": f"http://127.0.0.1:{port}",
        "health": health,
        "stdout_log": str(stdout_path),
        "stderr_log": str(stderr_path),
    }


def stop_background() -> dict[str, Any]:
    pid_file = DEFAULT_LOG_ROOT / "services" / "aiden_messenger" / "aiden_messenger.pid"
    pid = _read_live_pid(pid_file)
    if not pid:
        pid_file.unlink(missing_ok=True)
        return {"status": "not_running"}
    os.kill(pid, signal.SIGTERM)
    pid_file.unlink(missing_ok=True)
    return {"status": "stopped", "pid": pid}


def status_background(*, port: int = 8784) -> dict[str, Any]:
    pid_file = DEFAULT_LOG_ROOT / "services" / "aiden_messenger" / "aiden_messenger.pid"
    return {"pid": _read_live_pid(pid_file), "pid_file": str(pid_file), "health": health_check(port=port)}


def health_check(*, port: int = 8784) -> dict[str, Any]:
    url = f"http://127.0.0.1:{port}/api/health"
    try:
        with urlopen(url, timeout=5) as response:
            body = response.read(4096).decode("utf-8", errors="ignore")
        return {"ok": True, "url": url, "status": response.status, "body": body}
    except URLError as exc:
        return {"ok": False, "url": url, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "url": url, "error": f"{type(exc).__name__}: {exc}"}


def _read_live_pid(pid_file: Path) -> int | None:
    if not pid_file.exists():
        return None
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
        os.kill(pid, 0)
        return pid
    except Exception:
        pid_file.unlink(missing_ok=True)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Start/stop/status Aiden messenger without launchctl.")
    parser.add_argument("action", choices=["start", "stop", "status"])
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--ystar-gov-root", default=str(DEFAULT_YSTAR_GOV_ROOT))
    parser.add_argument("--port", type=int, default=8784)
    parser.add_argument("--runtime-timeout-seconds", type=int, default=180)
    parser.add_argument("--allow-live-network-by-default", action="store_true")
    args = parser.parse_args()
    if args.action == "start":
        result = start_background(
            repo_root=Path(args.repo_root),
            ystar_gov_root=Path(args.ystar_gov_root),
            port=args.port,
            runtime_timeout_seconds=args.runtime_timeout_seconds,
            allow_live_network_by_default=args.allow_live_network_by_default,
        )
    elif args.action == "stop":
        result = stop_background()
    else:
        result = status_background(port=args.port)
    print(result)
    return 0 if result.get("status") != "started_but_health_failed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
