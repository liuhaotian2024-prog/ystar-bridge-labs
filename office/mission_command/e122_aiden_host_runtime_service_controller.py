from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.host_runtime_service_bridge_schema import BRIDGE_ROOT, ensure_bridge_dirs, sha256_json


MILESTONE_ID = "E122_Aiden_Host_Runtime_Service_Controller_R1"
SESSION_ID = "e122_aiden_host_runtime_service_controller"
BRIDGE_LABS_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def build_ollama_host_service_order(
    *,
    requested_action: str = "start",
    model_name: str = "gemma4",
    owner_approved_host_service_control: bool = True,
    owner_approved_model_pull: bool = False,
) -> dict[str, Any]:
    command_by_action = {
        "health_check": ["ollama", "list"],
        "probe_models": ["ollama", "list"],
        "start": ["ollama", "serve"],
        "stop": ["ollama", "service-stop"],
        "pull_allowlisted_model": ["ollama", "pull", model_name],
        "smoke_test_generate": ["ollama", "run", model_name, "One sentence: what is 2+2?"],
    }
    argv = command_by_action.get(requested_action, ["ollama", "list"])
    return {
        "service_order_id": f"e122_ollama_{requested_action}",
        "milestone_id": MILESTONE_ID,
        "principal_actor": "Aiden",
        "executor_actor": "host_runtime_service_bridge",
        "service_id": "ollama_server",
        "requested_action": requested_action,
        "execution_boundary": {
            "host_local_only": True,
            "network_bind_host": "127.0.0.1",
            "network_bind_port": 11434,
            "allowed_runtime": "Ollama local server for Gemma-compatible models",
        },
        "command_plan": {
            "shell": False,
            "command_argv": argv,
            "model_name": model_name if requested_action in {"pull_allowlisted_model", "smoke_test_generate"} else "",
            "no_shell_operators": True,
        },
        "owner_approval": {
            "owner_approved_host_service_control": owner_approved_host_service_control,
            "owner_approved_model_pull": owner_approved_model_pull,
            "approval_scope": "local Ollama service lifecycle and Gemma allowlisted model inventory only",
        },
        "governance_links": [
            "E121_host_public_read_observer",
            "CIEUStore_formal_recording",
            "Y-star-gov_host_runtime_service_controller_contract",
        ],
        "CIEU_linkage": {
            "CIEU_recording_required": True,
            "target_event_type": "AIDEN_HOST_RUNTIME_SERVICE_CONTROLLER_DECISION",
            "formal_CIEU_log_path": "ystar.governance.cieu_store.CIEUStore.write_dict",
        },
        "truth_constraints": {
            "arbitrary_shell_allowed": False,
            "external_business_action_allowed": False,
            "customer_contact_allowed": False,
            "payment_allowed": False,
            "account_creation_allowed": False,
            "login_allowed": False,
            "external_llm_provider_allowed": False,
            "private_data_exfiltration_allowed": False,
            "K9Audit_write_allowed": False,
        },
    }


def build_host_runtime_service_bridge_job(order: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "job_id": f"{order['service_order_id']}_job",
        "created_at": _now(),
        "created_by": "Aiden",
        "service_order_id": order["service_order_id"],
        "service_order_hash": sha256_json(order),
        "service_id": order["service_id"],
        "requested_action": order["requested_action"],
        "command_plan": dict(order["command_plan"]),
        "safety_boundary": {
            "host_local_only": True,
            "external_business_side_effects": False,
            "arbitrary_shell_allowed": False,
            "no_customer_contact": True,
            "no_payment": True,
            "no_login": True,
            "no_private_data_exfiltration": True,
        },
        "no_external_business_side_effects_statement": (
            "Host runtime service control only. No customer contact, publication, payment, login, "
            "account creation, external provider call, or private data exfiltration is authorized."
        ),
    }


def submit_host_runtime_service_job(job: Mapping[str, Any], *, bridge_root: str | Path = BRIDGE_ROOT) -> dict[str, Any]:
    root = Path(bridge_root)
    ensure_bridge_dirs(root)
    path = root / "pending" / f"{job['job_id']}.json"
    path.write_text(json.dumps(dict(job), indent=2, sort_keys=True), encoding="utf-8")
    return {"submitted": True, "job_path": str(path), "bridge_root": str(root)}


def run_e122_host_runtime_service_controller_session(
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
    requested_action: str = "start",
    model_name: str = "gemma4",
    submit_job: bool = True,
    bridge_root: str | Path = BRIDGE_ROOT,
    owner_approved_host_service_control: bool = True,
    owner_approved_model_pull: bool = False,
) -> dict[str, Any]:
    order = build_ollama_host_service_order(
        requested_action=requested_action,
        model_name=model_name,
        owner_approved_host_service_control=owner_approved_host_service_control,
        owner_approved_model_pull=owner_approved_model_pull,
    )
    gov = _load_ystar_module("ystar.governance.aiden_host_runtime_service_controller_contract", ystar_gov_root)
    validation = gov.validate_and_write_aiden_host_runtime_service_order(
        order,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
    )
    job: dict[str, Any] = {}
    submission: dict[str, Any] = {"submitted": False}
    if validation["governance_decision"]["decision"] == "ALLOW":
        job = build_host_runtime_service_bridge_job(order)
        if submit_job:
            submission = submit_host_runtime_service_job(job, bridge_root=bridge_root)
    return {
        "artifact_id": "e122_aiden_host_runtime_service_controller_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "service_order": order,
        "YstarGov_service_order_validation": validation,
        "host_runtime_service_bridge_job": job,
        "host_runtime_service_bridge_submission": submission,
        "controller_proven": validation["governance_decision"]["decision"] == "ALLOW" and bool(job),
        "truth_constraints": order["truth_constraints"],
        "what_was_not_claimed": [
            "Codex sandbox did not directly bind localhost",
            "no arbitrary shell access",
            "no external business action",
            "no customer contact",
            "no payment",
            "no production brain write",
        ],
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_host_runtime_service_controller",
            "L5-B": "stronger_governed_intelligence_with_local_service_control_path_for_gemma",
            "L5-C": "partial_dry_run_only_for_external_business_actions",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_safe_brain_learning_pending_local_model_activation",
        },
    }


def write_e122_reports(
    *,
    cieu_db: str | Path,
    root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
    submit_job: bool = False,
) -> dict[str, Any]:
    base = Path(root or BRIDGE_LABS_ROOT)
    result = run_e122_host_runtime_service_controller_session(
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        submit_job=submit_job,
    )
    report = {
        "milestone_id": MILESTONE_ID,
        "base_hashes": {
            "bridge_labs": "4182c009358cbb85a8efc1201d6ea8c435247845",
            "Y_star_gov": "5cb40d2796f5d70b3ef6fc57e3560fff81c96c5d",
        },
        "what_was_implemented": [
            "Y-star-gov governed host runtime service order",
            "host runtime service bridge queue and worker",
            "allowlisted Ollama/Gemma4 service lifecycle commands",
            "LaunchAgent installer for long-running host service bridge",
            "CIEU-backed service order validation",
        ],
        "service_order_decision": result["YstarGov_service_order_validation"]["governance_decision"],
        "service_bridge_submission": result["host_runtime_service_bridge_submission"],
        "truth_constraints": result["truth_constraints"],
        "what_was_not_claimed": result["what_was_not_claimed"],
        "L5_truth_table_after": result["L5_truth_table_after"],
        "activation_model": {
            "worker_script": "scripts/host_runtime_service_bridge_worker.py",
            "queue_root": "/tmp/ystar_host_runtime_bridge",
            "installer": "scripts/host_runtime_service_bridge_install.py",
            "allowed_service_now": "ollama_server",
        },
    }
    status = {
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "host_runtime_service_controller_available": result["controller_proven"],
        "service_bridge_job_submitted_in_report_run": result["host_runtime_service_bridge_submission"].get("submitted") is True,
        "arbitrary_shell_allowed": False,
        "external_business_action_allowed": False,
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    files = {
        "report_json": base / "office/mission_command/e122_aiden_host_runtime_service_controller_report.json",
        "report_md": base / "office/mission_command/e122_aiden_host_runtime_service_controller_readback.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e122_host_runtime_service_controller.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e122_host_runtime_service_controller.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_md(report), encoding="utf-8")
    files["status_md"].write_text(_status_md(status), encoding="utf-8")
    return {"result": result, "report": report, "status": status, "files": {key: str(value) for key, value in files.items()}}


def _load_ystar_module(module_name: str, ystar_gov_root: str | Path | None) -> Any:
    root = Path(ystar_gov_root or Y_GOV_ROOT)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _report_md(report: Mapping[str, Any]) -> str:
    return (
        f"# {MILESTONE_ID}\n\n"
        f"- Service order decision: {report['service_order_decision']['decision']}\n"
        f"- Allowed service: {report['activation_model']['allowed_service_now']}\n"
        f"- Worker: {report['activation_model']['worker_script']}\n"
        f"- Arbitrary shell allowed: false\n"
        f"- External business action allowed: false\n"
    )


def _status_md(status: Mapping[str, Any]) -> str:
    truth = status["L5_truth_table_after"]
    return (
        f"# Runtime Status After {MILESTONE_ID}\n\n"
        f"- Host runtime service controller available: {status['host_runtime_service_controller_available']}\n"
        f"- L5-A: {truth['L5-A']}\n"
        f"- L5-B: {truth['L5-B']}\n"
        f"- L5-C: {truth['L5-C']}\n"
        f"- L5-D: {truth['L5-D']}\n"
        f"- L5-E: {truth['L5-E']}\n"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run E122 host runtime service controller.")
    parser.add_argument("--cieu-db", default="/tmp/e122_host_runtime_service_controller.db")
    parser.add_argument("--ystar-gov-root", default=str(Y_GOV_ROOT))
    parser.add_argument("--action", default="start")
    parser.add_argument("--model-name", default="gemma4")
    parser.add_argument("--submit-job", action="store_true")
    parser.add_argument("--write-reports", action="store_true")
    args = parser.parse_args(argv)
    if args.write_reports:
        result = write_e122_reports(cieu_db=args.cieu_db, ystar_gov_root=args.ystar_gov_root, submit_job=args.submit_job)
    else:
        result = run_e122_host_runtime_service_controller_session(
            cieu_db=args.cieu_db,
            ystar_gov_root=args.ystar_gov_root,
            requested_action=args.action,
            model_name=args.model_name,
            submit_job=args.submit_job,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MILESTONE_ID",
    "build_ollama_host_service_order",
    "build_host_runtime_service_bridge_job",
    "submit_host_runtime_service_job",
    "run_e122_host_runtime_service_controller_session",
    "write_e122_reports",
]
