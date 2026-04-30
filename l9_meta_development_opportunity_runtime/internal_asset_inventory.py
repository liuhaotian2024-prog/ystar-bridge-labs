#!/usr/bin/env python3
"""Build internal asset inventory for L9 opportunity discovery."""

from __future__ import annotations

from typing import Any

from .opportunity_model import base_packet, write_packet


ASSETS = [
    ("asset_l75_labs_office", "L7.5 Labs Office UI", "office_ui", "Local whiteboard, agent rooms, work board, timeline, and approval queue.", "l7_real_labs_office_web_ui", "operational", True, "Reusable owner-facing workspace for opportunity and execution loops.", ["Aiden", "Samantha", "Ryan"], ["l7_labs_whiteboard_collaboration_runtime/l7_5_summary.json"], ["Local deterministic worker replies only."]),
    ("asset_l76_scheduler", "L7.6 Self-Work Scheduler", "scheduler", "Bounded autonomous internal work cycles with heartbeats and approval interruptions.", "l7_labs_team_self_work_scheduler", "operational", True, "Lets the team advance safe internal opportunity work without owner micromanagement.", ["Aiden", "Ethan", "Samantha"], ["l7_labs_team_self_work_scheduler/l7_6_summary.json"], ["Not an LLM autonomous worker yet."]),
    ("asset_l80_cash_loop", "L8 First Cash Path Operating Loop", "commercial_loop", "Owner approval, manual-send packets, feedback, residuals, learning candidates.", "l8_first_cash_path_operating_loop", "operational", True, "Converts selected opportunities into approval-gated commercial actions.", ["Zara", "Marco", "Sofia", "Samantha"], ["l8_first_cash_path_operating_loop/l8_summary.json"], ["Manual-send only."]),
    ("asset_controlled_observation", "Controlled Observation Lineage", "evidence_loop", "L6 controlled read-only observation and evidence packet lineage as capability reference.", "l6 controlled observation artifacts", "proven_reference", True, "Supports evidence-oriented delivery and opportunity validation planning.", ["Jinjin", "Aiden"], ["l6_real_controlled_external_observation_mission_sprint"], ["Not executed by default in L9."]),
    ("asset_y_governance", "Y* Governance Concepts", "governance_kernel", "Approval boundaries, no-action receipts, staged policies, residual learning posture.", "policy/ and L7 governance artifacts", "maturing", True, "Trust differentiator for AI workflow and agent governance offerings.", ["Maya", "Zara", "Aiden"], ["policy/policy_registry_manifest.json"], ["Must stay practical, not governance-only."]),
    ("asset_residual_learning", "CIEU / Residual Learning Model", "research_asset", "Residual and review-gated learning candidate pattern.", "L8 residual/learning packets", "maturing", True, "Turns market feedback into safe iteration without permanent writeback.", ["Samantha", "Marco", "Aiden"], ["l8_first_cash_path_operating_loop"], ["No direct writeback in this sprint."]),
    ("asset_legacy_team", "Recovered Y*Bridge Labs Team Identity", "delivery_asset", "Aiden, Ethan, Sofia, Marco, Zara, Samantha, engineers, Jinjin/K9 Scout.", "l7_labs_office_legacy_integration", "operational", True, "Lets opportunity work be assigned to real legacy roles, not fake roles.", ["Aiden", "Ethan", "Sofia", "Marco", "Zara", "Samantha", "Jinjin"], ["l7_labs_office_legacy_integration/original_team_registry/original_team_registry.json"], ["Role behavior is deterministic/local in current runtime."]),
    ("asset_templates_and_service_design", "Service Design and Templates", "service_design", "Offer, workflow audit, CEO command brief, intake, feedback, proof boundaries.", "l7_approval_ready_offer_validation_workflow", "usable", True, "Can seed service packages beyond one offer.", ["Sofia", "Zara", "Ethan"], ["l7_approval_ready_offer_validation_workflow"], ["Needs real market feedback."]),
    ("asset_open_source_background", "Open-Source Governance / Tooling Background", "open_source_asset", "Template/tooling route for paid support and implementation packages.", "repo artifacts and public-facing project history", "early", True, "Supports productized template and paid support routes.", ["Ethan", "Zara"], ["l7_meta_development_money_path_engine"], ["Requires packaging and proof."]),
    ("asset_founder_context", "Founder System-Design Narrative", "founder_experience", "Owner-led narrative around building a self-governed AI agent company runtime.", "L6/L7/L8 outputs", "strong_internal", True, "Differentiates advisory and setup services for founder/operators.", ["Haotian", "Aiden", "Sofia"], ["l7_meta_development_money_path_engine/owner_review_packet"], ["Needs concise external story before outreach."]),
]


def build_internal_asset_inventory() -> dict[str, Any]:
    assets = []
    for asset in ASSETS:
        asset_id, title, asset_type, description, location, maturity, reusable, relevance, agents, evidence, limitations = asset
        assets.append(
            {
                "asset_id": asset_id,
                "title": title,
                "asset_type": asset_type,
                "description": description,
                "current_location": location,
                "maturity_level": maturity,
                "reusable_capability": reusable,
                "commercial_relevance": relevance,
                "related_agents": agents,
                "evidence_refs": evidence,
                "limitations": limitations,
            }
        )
    packet = {
        **base_packet("internal_asset_inventory"),
        "inventory_id": "internal_asset_inventory_latest",
        "assets": assets,
        "asset_count": len(assets),
        "closed_asset_type_enum": False,
    }
    return write_packet("internal_asset_inventory", packet["inventory_id"], packet)


def list_assets() -> list[dict[str, Any]]:
    return build_internal_asset_inventory()["assets"]

