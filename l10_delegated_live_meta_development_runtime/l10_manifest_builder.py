#!/usr/bin/env python3
"""Build baseline L10 delegated mission runtime artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .mission_cockpit_model import build_mission_cockpit
from .mission_delegation_center import create_default_mission, list_missions
from .mission_model import OUT, base_packet, ensure_dirs, no_action_receipt, write_packet
from .permission_tiers import permission_tier_registry


def build_manifest(force: bool = False) -> dict[str, Any]:
    ensure_dirs()
    tiers = permission_tier_registry()
    if force or not list_missions():
        create_default_mission()
    cockpit = build_mission_cockpit()
    write_packet("manifests", "permission_tier_registry", tiers)
    receipt = no_action_receipt()
    write_packet("manifests", "l10_no_action_receipt", receipt)
    manifest = {
        **base_packet("l10_manifest"),
        "manifest_id": "l10_delegated_live_meta_development_manifest",
        "permission_tier_count": tiers["tier_count"],
        "mission_count": len(cockpit["missions"]),
        "active_mission_count": len(cockpit["active_missions"]),
        "evidence_packet_count": cockpit["evidence_count"],
        "opportunity_signal_count": cockpit["opportunity_signal_count"],
        "strategy_brief_count": len(cockpit["meta_strategy_briefs"]),
        "escalation_packet_count": len(cockpit["escalation_packets"]),
        "completion_report_count": len(cockpit["mission_completion_reports"]),
        "fixture_demo_available": True,
        "configured_live_read_only_research_available": False,
        "next_one_command_action": "bash scripts/run_l7_labs_office_web.sh --mode serve",
    }
    write_packet("manifests", "l10_delegated_live_meta_development_manifest", manifest)
    _write_summary(manifest)
    return manifest


def _write_summary(manifest: dict[str, Any]) -> None:
    summary = {
        **base_packet("l10_summary"),
        "mission_count": manifest["mission_count"],
        "permission_tier_count": manifest["permission_tier_count"],
        "fixture_demo_available": True,
        "configured_live_read_only_research_available": False,
        "external_side_effects": False,
        "customer_contact": False,
        "email_sent": False,
        "payment_processed": False,
        "publication": False,
        "uncontrolled_web_research": False,
        "core_writeback": False,
    }
    (OUT / "l10_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "l10_summary.md").write_text(
        """# L10.0 Delegated Live Meta-Development Work Runtime

L10 lets the Labs team accept delegated meta-development missions, decompose work across the recovered legacy team, run bounded internal cycles, run fixture-safe research demos, prepare read-only research plans, generate strategy/action briefs, and escalate higher-risk actions for owner approval.

No external side effects or core writeback are executed by this runtime.
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (OUT / "README.md").write_text(
        """# L10 Delegated Mission Runtime

Local packet runtime for delegated meta-development missions. Tier 1 read-only research is architecture-supported, but configured live research is disabled unless explicitly enabled and budgeted. External side effects remain approval-gated.
""".strip()
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    manifest = build_manifest()
    print(f"l10_missions: {manifest['mission_count']}")
    print(f"l10_tiers: {manifest['permission_tier_count']}")
    print(f"next_command: {manifest['next_one_command_action']}")


if __name__ == "__main__":
    main()

