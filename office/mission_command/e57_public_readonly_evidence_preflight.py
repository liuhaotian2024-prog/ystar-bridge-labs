from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, write_json, write_md


def run_public_readonly_evidence_preflight() -> dict[str, Any]:
    return {
        "artifact_id": "e57_public_readonly_evidence_preflight",
        "safe_public_readonly_observation_available": False,
        "repo_controlled_page_read_adapter_available": False,
        "session_network_available_for_repo_runtime": False,
        "existing_E50B_observation_context_available": True,
        "blocker": "external_page_read_adapter_unavailable",
        "secondary_blocker": "network_disabled",
        "decision": "skip_live_refresh_and_use_internal_existing_evidence_only",
        "boundaries": {
            "no_contact": True,
            "no_login": True,
            "no_form_submission": True,
            "no_personal_contact_scraping": True,
            "no_send_or_publish": True,
            "not_customer_validation": True,
            "not_paid_signal": True,
        },
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_public_readonly_evidence_preflight(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_public_readonly_evidence_preflight()
    write_json(root, "operations/external_validation/e57_public_readonly_evidence_preflight.json", data)
    write_md(root, "reports/integration/e57_public_readonly_evidence_preflight.md", "E57 Public Read-Only Evidence Preflight", [
        f"Safe observation available: `{data['safe_public_readonly_observation_available']}`",
        f"Blocker: `{data['blocker']}`",
        "Live evidence refresh is skipped; route retest proceeds with internal and prior public-read-only evidence only.",
    ])
    return data

