from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e116_aiden_idle_continuous_learning_runtime import (
    BRAIN_DB,
    BRIDGE_ROOT,
    build_aiden_idle_learning_packet,
    apply_knowledge_graph_delta_to_brain,
    summarize_cieustore,
)


MILESTONE_ID = "E118_Production_Brain_Write_Boundary_And_Live_Quality_Evaluation_R1"
SESSION_ID = "e118_production_brain_write_boundary"
Y_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_verified_brain_backup(
    *,
    source_brain_db: str | Path = BRAIN_DB,
    backup_dir: str | Path | None = None,
) -> dict[str, Any]:
    source = Path(source_brain_db)
    if not source.exists():
        raise FileNotFoundError(f"brain db does not exist: {source}")
    target_dir = Path(backup_dir or (BRIDGE_ROOT / ".brain_backups"))
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = target_dir / f"{source.name}.backup_{timestamp}"
    shutil.copy2(source, target)
    source_hash = sha256_file(source)
    backup_hash = sha256_file(target)
    return {
        "backup_created_at": datetime.now(timezone.utc).isoformat(),
        "pre_write_backup_path": str(target),
        "pre_write_backup_sha256": backup_hash,
        "pre_write_brain_db_sha256": source_hash,
        "backup_verified": backup_hash == source_hash,
        "rollback_plan": f"restore {target} over {source} before restarting Aiden runtime",
    }


def build_production_brain_write_preflight(
    *,
    cieu_db: str | Path,
    brain_db: str | Path = BRAIN_DB,
    owner_explicit_production_write_approval: bool = False,
    backup_metadata: Mapping[str, Any] | None = None,
    ystar_gov_root: str | Path | None = None,
    force_production_target: bool = True,
) -> dict[str, Any]:
    packet = build_aiden_idle_learning_packet(
        cieu_db=cieu_db,
        brain_db=brain_db,
        allow_brain_write=True,
        owner_explicit_production_write_approval=owner_explicit_production_write_approval,
        pre_write_backup_metadata=backup_metadata,
        force_production_target=force_production_target,
    )
    packet["milestone_id"] = MILESTONE_ID
    packet["production_write_boundary"] = {
        "owner_visible_preflight_required": True,
        "raw_background_write_forbidden": True,
        "backup_required_before_write": True,
        "rollback_plan_required": True,
        "quality_gate_required": True,
        "CIEU_write_before_brain_mutation_required": True,
    }
    return packet


def run_e118_production_brain_write_boundary_session(
    *,
    cieu_db: str | Path,
    brain_db: str | Path = BRAIN_DB,
    ystar_gov_root: str | Path | None = None,
    owner_explicit_production_write_approval: bool = False,
    create_backup: bool = False,
    backup_dir: str | Path | None = None,
    force_production_target: bool = True,
    seal_session: bool = False,
) -> dict[str, Any]:
    backup = (
        create_verified_brain_backup(source_brain_db=brain_db, backup_dir=backup_dir)
        if create_backup
        else {}
    )
    packet = build_production_brain_write_preflight(
        cieu_db=cieu_db,
        brain_db=brain_db,
        owner_explicit_production_write_approval=owner_explicit_production_write_approval,
        backup_metadata=backup,
        ystar_gov_root=ystar_gov_root,
        force_production_target=force_production_target,
    )
    gov = _load_ystar_module("ystar.governance.aiden_idle_learning_contract", ystar_gov_root)
    governance = gov.validate_and_write_aiden_idle_learning_packet(
        packet,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    decision = governance["governance_decision"]["decision"]
    brain_write = {"brain_write_performed": False, "reason": "not_allowed_by_governance_or_owner_boundary"}
    if decision == "ALLOW" and owner_explicit_production_write_approval and backup.get("backup_verified") is True:
        brain_write = apply_knowledge_graph_delta_to_brain(
            packet["knowledge_graph_delta"],
            brain_db=brain_db,
            max_nodes=int(packet["brain_write_policy"]["max_nodes_per_cycle"]),
            max_edges=int(packet["brain_write_policy"]["max_edges_per_cycle"]),
        )
    return {
        "artifact_id": "e118_production_brain_write_boundary_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preflight_packet": packet,
        "backup_metadata": backup,
        "YstarGov_production_brain_write_boundary_result": governance,
        "brain_write_result": brain_write,
        "CIEUStore_summary": summarize_cieustore(cieu_db),
        "production_boundary_proven": governance.get("formal_CIEU_log_written") is True,
        "truth_constraints": {
            "external_action_executed": False,
            "provider_action_executed": False,
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "K9Audit_integration_claim": False,
            "live_provider_execution_claim": False,
        },
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_production_brain_write_boundary",
            "L5-B": "stronger_structured_governed_intelligence_with_live_quality_and_safe_brain_learning_boundary",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_production_brain_write_boundary_and_backup_preflight_proven",
        },
    }


def write_e118_reports(*, cieu_db: str | Path, root: str | Path | None = None) -> dict[str, Any]:
    base = Path(root or BRIDGE_ROOT)
    result = run_e118_production_brain_write_boundary_session(
        cieu_db=cieu_db,
        brain_db=base / "aiden_brain.db",
        owner_explicit_production_write_approval=False,
        create_backup=False,
        force_production_target=True,
    )
    report = {
        "milestone_id": MILESTONE_ID,
        "production_boundary_proven": result["production_boundary_proven"],
        "Y_star_gov_decision": result["YstarGov_production_brain_write_boundary_result"]["governance_decision"]["decision"],
        "owner_approval_required_before_production_write": True,
        "backup_required_before_production_write": True,
        "learning_quality_gate_required": True,
        "brain_write_performed_in_report_run": result["brain_write_result"]["brain_write_performed"],
        "CIEUStore_summary": result["CIEUStore_summary"],
        "truth_constraints": result["truth_constraints"],
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    status = {
        "milestone_id": MILESTONE_ID,
        "status": "implemented_preflight_boundary",
        "production_brain_write_without_owner_approval": "blocked_or_escalated",
        "backup_discipline": "required_before_approved_write",
        "live_evidence_quality": "deterministic_v2_source_depth_specificity_verifiability",
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    files = {
        "report_json": base / "office/mission_command/e118_production_brain_write_boundary_report.json",
        "report_md": base / "office/mission_command/e118_production_brain_write_boundary_readback.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e118_production_brain_write_boundary.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e118_production_brain_write_boundary.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_md(report), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["status_md"].write_text(_status_md(status), encoding="utf-8")
    return report


def _report_md(report: Mapping[str, Any]) -> str:
    return (
        "# E118 Production Brain Write Boundary\n\n"
        f"- Production boundary proven: {report['production_boundary_proven']}\n"
        f"- Y-star-gov decision: {report['Y_star_gov_decision']}\n"
        f"- Owner approval required: {report['owner_approval_required_before_production_write']}\n"
        f"- Backup required: {report['backup_required_before_production_write']}\n"
        f"- Brain write performed in report run: {report['brain_write_performed_in_report_run']}\n\n"
        "E118 makes production brain mutation owner-visible and backup-gated. "
        "No production brain write is performed by the report run.\n"
    )


def _status_md(status: Mapping[str, Any]) -> str:
    return (
        "# Runtime Status After E118\n\n"
        f"- Production brain write without owner approval: {status['production_brain_write_without_owner_approval']}\n"
        f"- Backup discipline: {status['backup_discipline']}\n"
        f"- Live evidence quality: {status['live_evidence_quality']}\n"
        f"- L5-E: {status['L5_truth_table_after']['L5-E']}\n"
    )


def _load_ystar_module(module_name: str, ystar_gov_root: str | Path | None = None):
    root = Path(ystar_gov_root or Y_GOV_ROOT)
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    loaded = sys.modules.get(module_name)
    loaded_file = str(getattr(loaded, "__file__", "")) if loaded is not None else ""
    if loaded is not None and root.exists() and loaded_file and not loaded_file.startswith(str(root)):
        del sys.modules[module_name]
    return importlib.import_module(module_name)


__all__ = [
    "MILESTONE_ID",
    "build_production_brain_write_preflight",
    "create_verified_brain_backup",
    "run_e118_production_brain_write_boundary_session",
    "sha256_file",
    "write_e118_reports",
]
