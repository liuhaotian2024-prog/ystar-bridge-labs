#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

try:
    from host_runtime_service_bridge_schema import (
        BRIDGE_ROOT,
        ensure_bridge_dirs,
        is_safe_service_job_path,
        validate_service_job,
    )
except ModuleNotFoundError:  # importable as scripts.host_runtime_service_bridge_worker in tests.
    from scripts.host_runtime_service_bridge_schema import (
        BRIDGE_ROOT,
        ensure_bridge_dirs,
        is_safe_service_job_path,
        validate_service_job,
    )


def run(args: list[str], *, timeout: int = 30) -> dict[str, Any]:
    completed = subprocess.run(args, text=True, capture_output=True, timeout=timeout, check=False)
    return {
        "command": args,
        "returncode": completed.returncode,
        "stdout": (completed.stdout or "").strip(),
        "stderr": (completed.stderr or "").strip(),
    }


def process_job_file(job_file: Path, *, bridge_root: Path = BRIDGE_ROOT) -> dict[str, Any]:
    ensure_bridge_dirs(bridge_root)
    running = bridge_root / "running" / job_file.name
    job_file.rename(running)
    job = json.loads(running.read_text(encoding="utf-8"))
    report = process_job(job, bridge_root=bridge_root)
    target_dir = bridge_root / ("completed" if report["status"] == "SERVICE_ACTION_SUCCEEDED" else "failed")
    target_json = target_dir / f"{job['job_id']}.report.json"
    target_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    running.rename(target_dir / running.name)
    return report


def process_job(job: dict[str, Any], *, bridge_root: Path = BRIDGE_ROOT) -> dict[str, Any]:
    report: dict[str, Any] = {
        "job_id": job.get("job_id"),
        "service_order_id": job.get("service_order_id"),
        "service_id": job.get("service_id"),
        "requested_action": job.get("requested_action"),
        "status": "SERVICE_ACTION_BLOCKED",
        "commands": [],
        "external_business_side_effects": False,
        "started_at": time.time(),
    }
    validation = validate_service_job(job)
    if not validation.ok:
        report["failure_code"] = "JOB_INVALID"
        report["errors"] = validation.errors
        return report

    action = str(job["requested_action"])
    plan = job["command_plan"]
    argv = [str(part) for part in plan["command_argv"]]
    if action == "start":
        result = start_ollama(argv, bridge_root=bridge_root)
    elif action == "stop":
        result = stop_ollama(bridge_root=bridge_root)
    elif action in {"health_check", "probe_models"}:
        result = run(argv, timeout=30)
    elif action == "pull_allowlisted_model":
        result = run(argv, timeout=1800)
    elif action == "smoke_test_generate":
        result = run(argv, timeout=180)
        result = sanitize_local_model_smoke_output(result)
    else:  # pragma: no cover - schema prevents this.
        result = {"returncode": 2, "stdout": "", "stderr": "unsupported action", "command": argv}
    report["commands"].append(result)
    report["finished_at"] = time.time()
    if result.get("returncode") == 0:
        report["status"] = "SERVICE_ACTION_SUCCEEDED"
        report["failure_code"] = "SERVICE_ACTION_SUCCEEDED"
    else:
        report["failure_code"] = "SERVICE_ACTION_FAILED"
    return report


def sanitize_local_model_smoke_output(result: dict[str, Any]) -> dict[str, Any]:
    """Keep model health proof while avoiding raw reasoning transcript capture."""

    cleaned = dict(result)
    stdout = str(cleaned.get("stdout") or "")
    sanitized = re.sub(r"(?is)thinking\.\.\..*?\.\.\.done thinking\.\s*", "", stdout).strip()
    if sanitized != stdout:
        cleaned["stdout"] = sanitized
        cleaned["stdout_sanitized"] = True
        cleaned["redaction_reason"] = "removed local model thinking transcript from service bridge report"
    return cleaned


def start_ollama(argv: list[str], *, bridge_root: Path = BRIDGE_ROOT) -> dict[str, Any]:
    service_dir = bridge_root / "services" / "ollama_server"
    service_dir.mkdir(parents=True, exist_ok=True)
    pid_file = service_dir / "ollama.pid"
    log_file = bridge_root / "logs" / "ollama_server.log"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            os.kill(pid, 0)
            return {"command": argv, "returncode": 0, "stdout": f"ollama already running pid={pid}", "stderr": ""}
        except Exception:
            pid_file.unlink(missing_ok=True)
    with log_file.open("ab") as log:
        process = subprocess.Popen(argv, stdout=log, stderr=log, start_new_session=True)
    pid_file.write_text(str(process.pid), encoding="utf-8")
    time.sleep(2)
    health = run([argv[0], "list"], timeout=20)
    if health["returncode"] != 0:
        return {"command": argv, "returncode": health["returncode"], "stdout": f"started pid={process.pid}", "stderr": health["stderr"]}
    return {"command": argv, "returncode": 0, "stdout": f"started pid={process.pid}\n{health['stdout']}", "stderr": health["stderr"]}


def stop_ollama(*, bridge_root: Path = BRIDGE_ROOT) -> dict[str, Any]:
    pid_file = bridge_root / "services" / "ollama_server" / "ollama.pid"
    if not pid_file.exists():
        return {"command": ["ollama", "service-stop"], "returncode": 0, "stdout": "ollama pid file not present", "stderr": ""}
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
        os.kill(pid, signal.SIGTERM)
        pid_file.unlink(missing_ok=True)
        return {"command": ["ollama", "service-stop"], "returncode": 0, "stdout": f"terminated pid={pid}", "stderr": ""}
    except Exception as exc:
        return {"command": ["ollama", "service-stop"], "returncode": 1, "stdout": "", "stderr": str(exc)}


def run_once(*, bridge_root: Path = BRIDGE_ROOT) -> int:
    ensure_bridge_dirs(bridge_root)
    exit_code = 0
    for job_file in sorted((bridge_root / "pending").glob("*.json")):
        if not is_safe_service_job_path(job_file):
            continue
        report = process_job_file(job_file, bridge_root=bridge_root)
        if report.get("status") != "SERVICE_ACTION_SUCCEEDED":
            exit_code = 2
    return exit_code


def daemon_loop(*, bridge_root: Path = BRIDGE_ROOT, poll_interval: float = 5.0) -> int:
    ensure_bridge_dirs(bridge_root)
    while True:
        run_once(bridge_root=bridge_root)
        time.sleep(poll_interval)


def main() -> int:
    parser = argparse.ArgumentParser(description="Y* host runtime service bridge worker.")
    parser.add_argument("--bridge-root", default=str(BRIDGE_ROOT))
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--daemon", action="store_true")
    parser.add_argument("--poll-interval", type=float, default=5.0)
    args = parser.parse_args()
    root = Path(args.bridge_root)
    if args.daemon:
        return daemon_loop(bridge_root=root, poll_interval=args.poll_interval)
    return run_once(bridge_root=root)


if __name__ == "__main__":
    raise SystemExit(main())
