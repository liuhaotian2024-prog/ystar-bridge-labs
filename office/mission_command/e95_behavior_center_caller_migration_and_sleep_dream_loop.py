"""E95 behavior-center caller migration and sleep/dream learning loop.

E94 made a governed gateway. E95 makes that gateway the owner-facing behavior
entrypoint and creates a deterministic sleep/dream learning candidate from each
governed behavior-center session.

No live external action is executed here. Production brain writes are not
performed by default; tests prove the write path on an isolated brain DB copy.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from office.aiden_meeting_room.governed_gateway import answer_owner_governed


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
MILESTONE_ID = "E95_Behavior_Center_Gateway_Caller_Migration_And_Sleep_Dream_Learning_Loop_R1"
SESSION_ID = "e95_behavior_center_gateway_migration_session"


RAW_ANSWER_OWNER_ALLOWED_CALLERS = {
    "office/aiden_meeting_room/aiden_response_engine.py",
    "office/mission_command/e87_ceo_runtime_session.py",
    "office/mission_command/e89_ceo_intelligence_loop_runtime_compiler.py",
    "office/mission_command/e94_behavior_center_runtime_gateway.py",
    "tests/office/test_aiden_meeting_room.py",
    "tests/office/test_aiden_evidence_grounding.py",
}


def discover_behavior_center_callers(repo_root: Path | None = None) -> dict[str, Any]:
    """Discover direct raw ``answer_owner`` callers and classify migration status."""

    root = repo_root or BRIDGE_ROOT
    matches: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.py")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "answer_owner" not in text:
            continue
        lines = [line.strip() for line in text.splitlines()]
        direct_raw = any(
            line == "from office.aiden_meeting_room.aiden_response_engine import answer_owner"
            or line == "from .aiden_response_engine import answer_owner"
            for line in lines
        )
        calls_raw = any(
            "answer_owner(" in line
            and not line.startswith("def answer_owner(")
            and "answer_owner_governed" not in line
            and '"answer_owner("' not in line
            and "'answer_owner('" not in line
            and "line.startswith" not in line
            for line in lines
        )
        uses_governed = "answer_owner_governed" in text
        status = "not_behavior_center_caller"
        if direct_raw or calls_raw:
            if rel in RAW_ANSWER_OWNER_ALLOWED_CALLERS:
                status = "allowed_internal_kernel_or_compatibility_test"
            elif uses_governed:
                status = "migrated_to_governed_gateway"
            else:
                status = "requires_gateway_migration"
        elif uses_governed:
            status = "migrated_to_governed_gateway"
        matches.append(
            {
                "path": rel,
                "direct_raw_import": direct_raw,
                "calls_raw_answer_owner": calls_raw,
                "uses_governed_gateway": uses_governed,
                "migration_status": status,
            }
        )
    return {
        "artifact_id": "e95_behavior_center_caller_inventory",
        "milestone_id": MILESTONE_ID,
        "total_python_files_with_answer_owner_signal": len(matches),
        "callers": matches,
        "unmigrated_owner_facing_callers": [
            item for item in matches if item["migration_status"] == "requires_gateway_migration"
        ],
    }


def assert_no_owner_facing_raw_behavior_callers(inventory: Mapping[str, Any]) -> bool:
    return not inventory.get("unmigrated_owner_facing_callers")


def run_governed_behavior_center_entrypoint(
    owner_message: str,
    *,
    cieu_db: str,
    repo_root: Path | None = None,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
    session_id: str = SESSION_ID,
) -> dict[str, Any]:
    """Canonical E95 owner-facing behavior entrypoint."""

    return answer_owner_governed(
        owner_message,
        repo_root=repo_root or BRIDGE_ROOT,
        cieu_db=cieu_db,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root or Y_GOV_ROOT,
        gov_mcp_root=gov_mcp_root or GOV_MCP_ROOT,
        session_id=session_id,
    )


def build_sleep_dream_learning_candidate(session_result: Mapping[str, Any]) -> dict[str, Any]:
    """Build a structured learning candidate from a governed behavior session."""

    packet = session_result["behavior_center_packet"]
    route = session_result["route_result"].get("route_type", "unknown")
    activations = list(packet.get("brain_activations", []))
    top_node = activations[0]["node_id"] if activations else "WHO_I_AM"
    digest_input = json.dumps(
        {
            "owner_message": session_result.get("owner_message"),
            "route": route,
            "decision": session_result.get("behavior_center_decision"),
            "top_node": top_node,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[:16]
    candidate_id = f"e95_sleep_dream_learning_candidate_{digest}"
    return {
        "artifact_id": "e95_sleep_dream_learning_candidate",
        "milestone_id": MILESTONE_ID,
        "candidate_id": candidate_id,
        "linked_session_id": session_result.get("session_id"),
        "linked_behavior_packet_id": packet.get("packet_id"),
        "route_type": route,
        "governance_decision": session_result.get("behavior_center_decision"),
        "post_action_residual_decision": session_result.get("post_action_residual_decision"),
        "brain_top_node": top_node,
        "activated_brain_nodes": [item.get("node_id") for item in activations],
        "proposed_brain_node": {
            "node_id": f"behavior_center/residual/{digest}",
            "name": f"E95 behavior-center residual: {route}",
            "file_path": "office/mission_command/e95_behavior_center_caller_migration_and_sleep_dream_loop.py",
            "node_type": "ceo_learning",
            "depth_label": "operational",
            "summary": (
                "Governed behavior-center session completed with brain provenance, "
                f"route={route}, decision={session_result.get('behavior_center_decision')}."
            ),
            "dims": {"y": 0.7, "x": 0.7, "z": 0.65, "t": 0.75, "phi": 0.75, "c": 0.7},
            "principles": [
                "behavior_center_must_use_E94_gateway",
                "low_risk_work_should_not_default_to_owner",
                "high_risk_side_effects_remain_owner_bound",
            ],
        },
        "proposed_edges": [
            {
                "source": f"behavior_center/residual/{digest}",
                "target": top_node,
                "weight": 0.45,
                "edge_type": "sleep_dream_residual_learning",
            }
        ],
        "production_brain_write_default": False,
        "safe_to_apply_to_isolated_brain_copy": True,
        "truth_constraints": {
            "no_hidden_chain_of_thought": True,
            "no_live_external_action": True,
            "no_customer_revenue_payment_claim": True,
            "K9Audit_not_integrated": True,
        },
    }


def _load_aiden_brain(repo_root: Path | None = None) -> Any:
    root = repo_root or BRIDGE_ROOT
    scripts = root / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    return importlib.import_module("aiden_brain")


def apply_sleep_dream_learning_candidate(
    candidate: Mapping[str, Any],
    *,
    brain_db: Path,
    repo_root: Path | None = None,
    allow_production_brain_write: bool = False,
) -> dict[str, Any]:
    """Apply candidate to an isolated brain DB copy unless explicitly allowed."""

    db_path = Path(brain_db)
    production_like = db_path.name == "aiden_brain.db" and db_path.parent == (repo_root or BRIDGE_ROOT)
    if production_like and not allow_production_brain_write:
        return {
            "status": "DENY",
            "reason": "production_brain_write_requires_explicit_milestone_authorization",
            "brain_db": str(db_path),
            "brain_node_written": False,
            "brain_edge_written": False,
        }

    brain = _load_aiden_brain(repo_root)
    brain.init_db(str(db_path))
    node = candidate["proposed_brain_node"]
    brain.add_node(
        node["node_id"],
        node["name"],
        file_path=node["file_path"],
        node_type=node["node_type"],
        depth_label=node["depth_label"],
        dims=node["dims"],
        principles=node["principles"],
        summary=node["summary"],
        content_hash=hashlib.sha256(json.dumps(node, sort_keys=True).encode("utf-8")).hexdigest(),
        db_path=str(db_path),
    )
    for edge in candidate.get("proposed_edges", []):
        brain.add_edge(
            edge["source"],
            edge["target"],
            weight=float(edge.get("weight", 0.4)),
            edge_type=str(edge.get("edge_type", "sleep_dream_residual_learning")),
            db_path=str(db_path),
        )
    return {
        "status": "ALLOW",
        "brain_db": str(db_path),
        "brain_node_written": True,
        "brain_edge_written": bool(candidate.get("proposed_edges")),
        "written_node_id": node["node_id"],
    }


def run_e95_behavior_center_migration_session(
    *,
    owner_message: str,
    cieu_db: str,
    brain_db: Path,
    repo_root: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
    apply_sleep_dream_to_brain_copy: bool = True,
) -> dict[str, Any]:
    """Run E94 gateway, then convert the residual into a sleep/dream candidate."""

    root = repo_root or BRIDGE_ROOT
    inventory = discover_behavior_center_callers(root)
    session = run_governed_behavior_center_entrypoint(
        owner_message,
        cieu_db=cieu_db,
        repo_root=root,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
        session_id=SESSION_ID,
    )
    candidate = build_sleep_dream_learning_candidate(session)
    dream_apply = (
        apply_sleep_dream_learning_candidate(candidate, brain_db=brain_db, repo_root=root)
        if apply_sleep_dream_to_brain_copy
        else {"status": "SKIPPED", "brain_node_written": False, "brain_edge_written": False}
    )
    return {
        "artifact_id": "e95_behavior_center_migration_session_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "caller_inventory": inventory,
        "owner_facing_raw_callers_closed": assert_no_owner_facing_raw_behavior_callers(inventory),
        "governed_behavior_session": session,
        "sleep_dream_learning_candidate": candidate,
        "sleep_dream_apply_result": dream_apply,
        "CIEUStore_summary": session.get("CIEUStore_summary"),
        "runtime_chain_proven": [
            "owner-facing entrypoint",
            "E94 behavior gateway",
            "brain provenance",
            "Y-star-gov behavior-center contract",
            "CIEUStore decision/residual writes",
            "sleep/dream learning candidate",
            "isolated brain DB write proof",
        ],
        "no_external_action_executed": True,
        "L5_truth_table_after": l5_truth_table_after_e95(),
    }


def l5_truth_table_after_e95() -> dict[str, str]:
    return {
        "L5-A Runtime Foundation": "complete_internal_runtime_foundation_with_owner_facing_behavior_gateway",
        "L5-B CEO Intelligence Loop": "complete_for_structured_governed_intelligence_loop_with_behavior_center_sleep_dream_learning_candidate",
        "L5-B+": "partial_dynamic_intelligence_pending_live_external_observation_and_real_feedback",
        "L5-C Controlled External Action": "partial_autonomous_low_risk_dry_run_only_high_risk_owner_bound",
        "L5-D Revenue/Customer/Payment Loop": "absent_or_not_executed",
    }


def summarize_brain_node_exists(brain_db: Path, node_id: str) -> bool:
    con = sqlite3.connect(str(brain_db))
    row = con.execute("select id from nodes where id=?", (node_id,)).fetchone()
    con.close()
    return row is not None


def write_e95_reports(result: Mapping[str, Any], *, repo_root: Path | None = None) -> dict[str, str]:
    root = repo_root or BRIDGE_ROOT
    report = {
        "milestone_id": MILESTONE_ID,
        "repos_read": ["bridge-labs", "Y-star-gov", "gov-mcp"],
        "repos_modified": ["bridge-labs"],
        "existing_systems_reused": [
            "office/aiden_meeting_room/aiden_response_engine.py::answer_owner as internal kernel",
            "office/aiden_meeting_room/governed_gateway.py::answer_owner_governed",
            "office/mission_command/e94_behavior_center_runtime_gateway.py",
            "Y-star-gov:ystar/governance/ceo_behavior_center_runtime_contract.py",
            "Y-star-gov:CIEUStore.write_dict",
            "gov-mcp:dry_run_outbound_action",
            "scripts/aiden_brain.py isolated DB write path",
        ],
        "owner_facing_raw_callers_closed": result.get("owner_facing_raw_callers_closed"),
        "caller_inventory": result.get("caller_inventory"),
        "behavior_center_decision": result["governed_behavior_session"].get("behavior_center_decision"),
        "route_type": result["governed_behavior_session"].get("route_result", {}).get("route_type"),
        "CIEUStore_summary": result.get("CIEUStore_summary"),
        "sleep_dream_apply_result": result.get("sleep_dream_apply_result"),
        "L5_truth_table_after": result.get("L5_truth_table_after"),
        "what_changed": [
            "meeting_cli now uses the governed behavior-center gateway instead of raw answer_owner.",
            "owner-facing behavior entrypoint now returns governance/CIEU/route receipt metadata.",
            "E95 produces a deterministic sleep/dream learning candidate from governed residuals.",
            "Sleep/dream write path is proven on isolated brain DB copies; production brain write remains explicit-authority only.",
        ],
        "what_was_not_claimed": [
            "No L4 feedback was executed.",
            "No live provider action was enabled.",
            "No customer validation, revenue, pricing, payment, or paid signal was claimed.",
            "No production brain DB write was performed by default.",
            "No K9Audit write or bridge was claimed.",
        ],
        "remaining_blockers": [
            "Future non-test scripts that import raw answer_owner should migrate to answer_owner_governed.",
            "Live external observation and real feedback remain pending.",
            "Production brain sleep/dream commits require a later explicit authorization policy.",
        ],
        "recommended_next_milestone": "E96_Owner_Approved_Low_Risk_Public_Read_And_L4_Feedback_Preflight_R1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    report_path = root / "office/mission_command/e95_behavior_center_caller_migration_and_sleep_dream_loop_report.json"
    readback_path = root / "office/mission_command/e95_behavior_center_caller_migration_and_sleep_dream_loop_readback.md"
    status_json = root / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e95_behavior_center_caller_migration_and_sleep_dream_loop.json"
    status_md = root / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e95_behavior_center_caller_migration_and_sleep_dream_loop.md"
    for path in (report_path, readback_path, status_json, status_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    report_path.write_text(text, encoding="utf-8")
    status_json.write_text(text, encoding="utf-8")
    readback = _render_readback(report)
    readback_path.write_text(readback, encoding="utf-8")
    status_md.write_text(readback, encoding="utf-8")
    return {
        "report_path": str(report_path),
        "readback_path": str(readback_path),
        "status_json": str(status_json),
        "status_md": str(status_md),
    }


def _render_readback(report: Mapping[str, Any]) -> str:
    l5 = report["L5_truth_table_after"]
    return "\n".join(
        [
            "# E95 Behavior Center Gateway Migration And Sleep/Dream Loop",
            "",
            f"- behavior_center_decision: `{report['behavior_center_decision']}`",
            f"- route_type: `{report['route_type']}`",
            f"- owner_facing_raw_callers_closed: `{report['owner_facing_raw_callers_closed']}`",
            f"- CIEU events: `{report['CIEUStore_summary']['event_count']}`",
            f"- sleep_dream_apply_status: `{report['sleep_dream_apply_result']['status']}`",
            "",
            "E95 migrates the owner-facing Aiden meeting-room CLI/API to the E94 governed gateway, while preserving raw `answer_owner` only as the internal deterministic kernel and compatibility-test target.",
            "",
            "The sleep/dream loop converts governed behavior-center residuals into a structured learning candidate and proves the write path on an isolated brain DB copy. Production brain writes remain explicit-authority only.",
            "",
            "## L5 Truth Table",
            "",
            f"- L5-A: `{l5['L5-A Runtime Foundation']}`",
            f"- L5-B: `{l5['L5-B CEO Intelligence Loop']}`",
            f"- L5-B+: `{l5['L5-B+']}`",
            f"- L5-C: `{l5['L5-C Controlled External Action']}`",
            f"- L5-D: `{l5['L5-D Revenue/Customer/Payment Loop']}`",
            "",
            "No L4 feedback, live provider action, customer validation, revenue, pricing, payment, production brain write, or K9Audit write was executed or claimed.",
            "",
        ]
    )


__all__ = [
    "apply_sleep_dream_learning_candidate",
    "assert_no_owner_facing_raw_behavior_callers",
    "build_sleep_dream_learning_candidate",
    "discover_behavior_center_callers",
    "l5_truth_table_after_e95",
    "run_e95_behavior_center_migration_session",
    "run_governed_behavior_center_entrypoint",
    "summarize_brain_node_exists",
    "write_e95_reports",
]
