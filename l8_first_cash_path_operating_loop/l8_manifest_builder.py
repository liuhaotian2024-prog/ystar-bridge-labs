#!/usr/bin/env python3
"""Build L8 first cash path manifest and baseline packets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .cockpit_model import build_cockpit_snapshot
from .commercial_action_builder import build_commercial_actions
from .first_cash_path_loader import initialize_first_cash_path
from .first_cash_path_model import GENERATED_AT, LOCAL_URL, OUT, no_action_receipt, write_packet


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def build_manifest(force_actions: bool = False) -> dict[str, Any]:
    cash_path = initialize_first_cash_path()
    action_result = build_commercial_actions(force=force_actions)
    cockpit = build_cockpit_snapshot("l8_cockpit_latest")
    receipt = no_action_receipt()
    write_json(OUT / "l8_no_action_receipt.json", receipt)
    manifest = {
        "schema_version": "v0",
        "milestone_id": "L8.0",
        "packet_type": "l8_manifest",
        "generated_at_utc": GENERATED_AT,
        "first_cash_path_initialized": True,
        "selected_offer": cash_path["selected_offer"],
        "cash_path_id": cash_path["cash_path_id"],
        "commercial_actions_available": len(action_result["actions"]),
        "manual_send_execution_mode": "manual_send_packet",
        "disabled_tool_send_email_future_slot_enabled": False,
        "grant_rfp_path_created_by_default": False,
        "cockpit_snapshot_id": cockpit["cockpit_snapshot_id"],
        "local_url": LOCAL_URL,
        "next_one_command_action": "bash scripts/run_l7_labs_office_web.sh --mode serve",
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "coo_invented": False,
    }
    write_packet("manifests", "l8_manifest", manifest)
    write_json(OUT / "l8_summary.json", manifest)
    write_text(
        OUT / "l8_summary.md",
        f"""
# L8.0 First Cash Path Operating Loop

Selected first cash path:

**{cash_path['selected_offer']}**

The local Office can now initialize the first cash path, build approval-gated commercial actions, create owner decisions, generate manual-send packets after approval, record owner-entered customer feedback, produce commercial residuals, create review-gated learning candidates, and show the full loop in the cockpit.

Run:

`bash scripts/run_l7_labs_office_web.sh --mode serve`

Then open:

`{LOCAL_URL}`

No automatic email sending, customer contact, payment, publication, grant/RFP default route, or core writeback occurs.
""",
    )
    write_text(
        OUT / "README.md",
        """
# L8.0 First Cash Path Operating Loop

This package implements the first local commercial operating loop for Y*Bridge Labs.

Path:

internal autonomous team work -> first cash path package -> owner approval -> manual-send commercial action packet -> owner-marked execution receipt -> customer feedback -> commercial residual -> review-gated learning candidate -> cockpit-visible next decision.

Default offer:

Founder AI Workflow Audit & CEO Command Brief Sprint.

Default execution mode:

manual_send_packet.

The disabled future tool-send email slot is visible but cannot execute in L8.0.
""",
    )
    return manifest


if __name__ == "__main__":
    built = build_manifest()
    print(f"l8_first_cash_path_initialized: {built['first_cash_path_initialized']}")
    print(f"selected_offer: {built['selected_offer']}")
    print(f"next_command: {built['next_one_command_action']}")
