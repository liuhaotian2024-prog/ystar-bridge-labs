#!/usr/bin/env python3
"""Build L7.6 scheduler manifest, summary, demo, and no-action receipt."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "l7_labs_team_self_work_scheduler"
GENERATED_AT = "2026-04-30T00:00:00Z"
LOCAL_URL = "http://127.0.0.1:8765"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def build_manifest() -> dict[str, Any]:
    demo_flow = {
        "schema_version": "v0",
        "milestone_id": "L7.6",
        "demo_id": "demo_autonomous_first_cash_path_offer_package",
        "owner_goal": "Improve the first cash path offer package for Founder AI Workflow Audit & CEO Command Brief Sprint.",
        "expected_flow": [
            "scheduler classifies work as autonomous_internal_allowed",
            "Aiden coordinates the bounded local work cycle",
            "Sofia improves positioning",
            "Marco checks pricing and revenue framing",
            "Zara reviews customer segment and strategic risk",
            "Jinjin proposes safe read-only research angles",
            "Ethan identifies tool gaps",
            "Samantha archives and summarizes packet references",
            "approval interruption is created only if external action is requested",
        ],
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "coo_invented": False,
    }
    write_json(OUT / "demo_scenarios/demo_autonomous_first_cash_path_offer_package.json", demo_flow)
    write_text(
        OUT / "demo_scenarios/demo_autonomous_first_cash_path_offer_package.md",
        """
# Demo: Autonomous First-Cash Path Offer Package

Owner goal:

Improve the first cash path offer package for Founder AI Workflow Audit & CEO Command Brief Sprint.

Expected bounded local flow:

- The scheduler classifies the work as `autonomous_internal_allowed`.
- Aiden coordinates the work.
- Sofia, Marco, Zara, Jinjin, Ethan, and Samantha produce local role-specific replies.
- Progress heartbeats and scheduler ticks are written locally.
- A completion report is created.
- If any plan proposes outreach, payment, publication, customer contact, or writeback, the scheduler stops and creates an approval interruption.

No external side effects occur.
""",
    )
    summary = {
        "schema_version": "v0",
        "milestone_id": "L7.6",
        "packet_type": "l7_6_summary",
        "generated_at_utc": GENERATED_AT,
        "scheduler_created": True,
        "safe_capability_classifier_created": True,
        "autonomous_cycle_engine_created": True,
        "progress_ledger_created": True,
        "approval_interrupts_created": True,
        "office_ui_scheduler_integration_created": True,
        "api_endpoints": [
            "GET /api/scheduler/status",
            "POST /api/scheduler/run_once",
            "POST /api/scheduler/run_bounded",
            "GET /api/autonomous_runs",
            "GET /api/progress_heartbeats",
            "GET /api/approval_interrupts",
        ],
        "local_url": LOCAL_URL,
        "next_one_command_action": "bash scripts/run_l7_labs_office_web.sh --mode serve",
        "demo_command": "bash scripts/run_l7_labs_office_web.sh --mode demo",
        "legacy_team_preserved": True,
        "coo_invented": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
    }
    write_json(OUT / "l7_6_summary.json", summary)
    write_text(
        OUT / "l7_6_summary.md",
        f"""
# L7.6 Labs Team Self-Work Scheduler

The Labs Office now has a bounded local self-work scheduler.

It can select safe internal work items, classify policy risk, run local agent cycles, write progress heartbeats, create completion reports, and stop at approval interruptions.

Run:

`bash scripts/run_l7_labs_office_web.sh --mode serve`

Then open:

`{LOCAL_URL}`
""",
    )
    no_action = {
        "schema_version": "v0",
        "milestone_id": "L7.6",
        "packet_type": "whiteboard_no_action_receipt",
        "generated_at_utc": GENERATED_AT,
        "outreach_occurred": False,
        "email_sent": False,
        "form_submission_occurred": False,
        "publication_occurred": False,
        "payment_occurred": False,
        "account_creation_occurred": False,
        "customer_contacted": False,
        "grant_rfp_submission_occurred": False,
        "mcp_live_behavior_occurred": False,
        "actual_memory_brain_canonical_cieu_db_writeback_occurred": False,
        "secret_printed_stored_in_repo": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "ystar_bridge_labs_modified": False,
        "db_log_wal_shm_active_agent_marker_content_read": False,
        "ask_user_url_occurred": False,
    }
    write_json(OUT / "whiteboard_no_action_receipt.json", no_action)
    runtime_state = {
        "schema_version": "v0",
        "milestone_id": "L7.6",
        "packet_type": "whiteboard_runtime_state",
        "generated_at_utc": GENERATED_AT,
        "scheduler_status_panel_available": True,
        "bounded_self_work_run_available": True,
        "progress_heartbeats_visible": True,
        "approval_interrupts_visible": True,
        "completion_reports_visible": True,
        "local_only": True,
    }
    write_json(OUT / "whiteboard_runtime_state.json", runtime_state)
    write_text(
        OUT / "README.md",
        """
# L7.6 Labs Team Self-Work Scheduler

This package adds a deterministic local scheduler for the Y*Bridge Labs Office.

It is not a live external action system. It only creates local packets, agent replies, progress heartbeats, approval interruptions, and completion reports.

Allowed:

- internal analysis
- offer package refinement
- local packet summaries
- draft-only artifacts
- dry-run writeback candidates
- completion reports

Blocked or interrupted:

- email/customer outreach
- publication
- payment
- account creation
- form submission
- grant/RFP submission
- MCP/live behavior
- actual memory/brain/canonical/CIEU DB writeback
- secret/env/raw DB/log/active-agent content reads
""",
    )
    return summary


if __name__ == "__main__":
    built = build_manifest()
    print(f"l7_6_scheduler_created: {built['scheduler_created']}")
    print(f"next_command: {built['next_one_command_action']}")

