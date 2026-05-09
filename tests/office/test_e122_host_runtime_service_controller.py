from __future__ import annotations

import json
import os
from pathlib import Path

from office.mission_command.e122_aiden_host_runtime_service_controller import (
    build_host_runtime_service_bridge_job,
    build_ollama_host_service_order,
    run_e122_host_runtime_service_controller_session,
    submit_host_runtime_service_job,
)
from scripts.host_runtime_service_bridge_schema import validate_service_job
from scripts.host_runtime_service_bridge_worker import process_job, sanitize_local_model_smoke_output


def test_service_order_builds_local_ollama_start_plan() -> None:
    order = build_ollama_host_service_order()
    assert order["service_id"] == "ollama_server"
    assert order["requested_action"] == "start"
    assert order["command_plan"]["command_argv"] == ["ollama", "serve"]
    assert order["truth_constraints"]["arbitrary_shell_allowed"] is False


def test_bridge_job_schema_allows_structured_ollama_start() -> None:
    job = build_host_runtime_service_bridge_job(build_ollama_host_service_order())
    validation = validate_service_job(job)
    assert validation.ok is True


def test_bridge_job_schema_rejects_shell_injection() -> None:
    job = build_host_runtime_service_bridge_job(build_ollama_host_service_order())
    job["command_plan"] = {"shell": True, "command_argv": ["sh", "-c", "ollama serve; curl example.com"]}
    validation = validate_service_job(job)
    assert validation.ok is False
    assert "shell_execution_forbidden" in validation.errors


def test_submit_host_runtime_service_job_writes_pending_file(tmp_path: Path) -> None:
    job = build_host_runtime_service_bridge_job(build_ollama_host_service_order())
    result = submit_host_runtime_service_job(job, bridge_root=tmp_path)
    path = Path(result["job_path"])
    assert path.exists()
    assert json.loads(path.read_text())["service_id"] == "ollama_server"


def test_controller_session_writes_cieu_and_job(tmp_path: Path) -> None:
    result = run_e122_host_runtime_service_controller_session(
        cieu_db=tmp_path / "e122.db",
        ystar_gov_root=Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov")),
        bridge_root=tmp_path / "runtime_bridge",
        submit_job=True,
    )
    assert result["YstarGov_service_order_validation"]["governance_decision"]["decision"] == "ALLOW"
    assert result["host_runtime_service_bridge_submission"]["submitted"] is True
    assert Path(result["host_runtime_service_bridge_submission"]["job_path"]).exists()


def test_worker_processes_health_check_with_fake_runner(monkeypatch, tmp_path: Path) -> None:
    calls = []

    def fake_run(args, *, timeout=30):
        calls.append(args)
        return {"command": args, "returncode": 0, "stdout": "NAME\\ngemma4:latest", "stderr": ""}

    monkeypatch.setattr("scripts.host_runtime_service_bridge_worker.run", fake_run)
    order = build_ollama_host_service_order(requested_action="probe_models")
    job = build_host_runtime_service_bridge_job(order)
    report = process_job(job, bridge_root=tmp_path)
    assert report["status"] == "SERVICE_ACTION_SUCCEEDED"
    assert calls == [["ollama", "list"]]


def test_smoke_output_sanitizes_local_model_thinking_transcript() -> None:
    result = sanitize_local_model_smoke_output(
        {
            "command": ["ollama", "run", "gemma4:e4b", "One sentence: what is 2+2?"],
            "returncode": 0,
            "stdout": "Thinking...\nprivate reasoning\n...done thinking.\n\nThe answer is four.",
            "stderr": "",
        }
    )
    assert result["stdout"] == "The answer is four."
    assert result["stdout_sanitized"] is True
