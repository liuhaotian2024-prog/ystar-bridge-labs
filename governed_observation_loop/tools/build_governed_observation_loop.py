#!/usr/bin/env python3
"""Build a deterministic governed read-only observation loop snapshot.

The loop reads only generated/read-model JSON. It does not execute tools, use
network access, persist CIEU, or mutate brain/memory.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "governed_observation_loop" / "generated"


def load_json(relative_path: str, default: Any | None = None) -> Any:
    path = ROOT / relative_path
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"refusing path outside repository: {relative_path}") from exc
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(relative_path: str, payload: dict[str, Any]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(relative_path: str, text: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def source(source_id: str, path: str, source_type: str, notes: str) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "source_path": path,
        "source_type": source_type,
        "safe_to_read_now": True,
        "raw_runtime_artifact": False,
        "requires_network": False,
        "requires_credentials": False,
        "governance_notes": notes,
    }


def build_source_registry(triage_buckets: dict[str, Any]) -> dict[str, Any]:
    sources = [
        source(
            "console-readiness-summary",
            "console_read_model/generated/readiness_summary.json",
            "console_read_model_summary",
            "generated console readiness summary",
        ),
        source(
            "console-team-snapshot",
            "console_read_model/generated/team_console_snapshot.json",
            "console_read_model_snapshot",
            "generated team console snapshot",
        ),
        source(
            "live-readiness-summary",
            "console_read_model/generated/live_readiness_summary.json",
            "live_readiness_summary",
            "generated live readiness summary",
        ),
        source(
            "live-boundary-summary",
            "console_read_model/generated/live_boundary_summary.json",
            "live_boundary_summary",
            "generated live boundary summary",
        ),
        source(
            "cieu-boundary-summary",
            "console_read_model/generated/cieu_boundary_summary.json",
            "cieu_boundary_summary",
            "generated CIEU boundary summary",
        ),
        source(
            "autonomy-inventory-summary",
            "console_read_model/generated/autonomy_inventory_summary.json",
            "autonomy_inventory_summary",
            "generated company autonomy inventory summary",
        ),
        source(
            "autonomous-cycle-summary",
            "console_read_model/generated/autonomous_cycle_summary.json",
            "autonomous_cycle_summary",
            "generated autonomous work cycle summary",
        ),
        source(
            "legacy-triage-summary",
            "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
            "legacy_asset_triage_summary",
            "generated legacy triage summary",
        ),
    ]

    adoptable = triage_buckets.get("buckets", {}).get("A_adopt_now_read_only", [])[:5]
    for index, asset in enumerate(adoptable, start=1):
        path = asset.get("source_path", "")
        if "/generated/" not in path and not path.startswith("console_read_model/"):
            continue
        sources.append(
            source(
                f"triage-adoptable-{index:02d}",
                path,
                "triaged_read_only_asset",
                "A bucket asset referenced read-only; not executed or absorbed",
            )
        )

    return {
        "schema_name": "ystar.governed_observation_loop.generated.observation_source_registry",
        "schema_version": "v0",
        "source_count": len(sources),
        "sources": sources,
    }


def build_observation_tick(inputs: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    mission = inputs["mission"]
    triage = inputs["triage_summary"]
    cycle = inputs["cycle_summary"]
    live = inputs["live_readiness"]
    boundary = inputs["live_boundary"]
    cieu = inputs["cieu_boundary"]
    candidates = [
        {
            "candidate_id": "obs-work-001",
            "title": "Wrap the read-only observation loop as a governed tool",
            "recommended_owner_agent": "Ryan-Platform",
            "risk_tier": "low",
            "live_enabled": False,
        },
        {
            "candidate_id": "obs-work-002",
            "title": "Create a mission dashboard from generated summaries",
            "recommended_owner_agent": "Samantha-Secretary",
            "risk_tier": "low",
            "live_enabled": False,
        },
        {
            "candidate_id": "obs-work-003",
            "title": "Prepare governed wrapper specs for top triaged assets",
            "recommended_owner_agent": "Maya-Governance",
            "risk_tier": "medium",
            "live_enabled": False,
        },
    ]
    return {
        "schema_name": "ystar.governed_observation_loop.generated.observation_tick",
        "schema_version": "v0",
        "tick_id": "observation-tick-001",
        "created_at": "stable_tick_001",
        "mission_id": mission.get("mission_id"),
        "observation_sources_used": [item["source_id"] for item in registry["sources"]],
        "observed_state": {
            "mission_bounded_autonomy": mission.get("mission_bounded_autonomy"),
            "legacy_assets_scored": triage.get("assets_scored"),
            "autonomous_cycle_defined": cycle.get("autonomous_work_cycle_defined"),
            "dry_run_governance_ready": live.get("dry_run_governance_ready"),
            "live_boundary_defined": boundary.get("live_boundary_defined"),
            "cieu_boundary_defined": cieu.get("cieu_runtime_boundary_defined"),
        },
        "detected_changes_or_findings": [
            "legacy asset triage is available for absorption planning",
            "read-only observation can be performed from generated summaries",
            "live execution remains blocked",
        ],
        "blocked_risks": [
            "live action execution remains disabled",
            "external communication remains disabled",
            "CIEU persistence remains disabled",
            "brain and memory writeback remain disabled",
        ],
        "safe_opportunities": [
            "use generated summaries as a recurring observation surface",
            "turn top triage candidates into governed read-only wrappers",
            "produce next work recommendations without executing actions",
        ],
        "work_item_candidates": candidates,
        "real_action_executed": False,
        "external_action_executed": False,
    }


def build_mission_dashboard(inputs: dict[str, Any], tick: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_observation_loop.generated.mission_dashboard_snapshot",
        "schema_version": "v0",
        "mission": inputs["mission"].get("founder_defined_mission"),
        "current_milestone_chain": [
            "L4.1 capability inventory",
            "L4.2 autonomous work cycle simulator",
            "L4.3 legacy triage and read-only observation loop",
        ],
        "live_readiness": {
            "dry_run_governance_ready": inputs["live_readiness"].get("dry_run_governance_ready"),
            "minimal_live_loop_ready": inputs["live_readiness"].get("minimal_live_loop_ready"),
        },
        "live_boundary": {
            "defined": inputs["live_boundary"].get("live_boundary_defined"),
            "enabled": inputs["live_boundary"].get("live_action_execution_enabled"),
        },
        "cieu_boundary": {
            "defined": inputs["cieu_boundary"].get("cieu_runtime_boundary_defined"),
            "persistence_enabled": inputs["cieu_boundary"].get("persistence_enabled"),
        },
        "autonomy_inventory": {
            "defined": inputs["inventory_observation"].get("schema_name") is not None,
            "channels": len(inputs["inventory_observation"].get("channels", [])),
        },
        "autonomous_work_cycle": {
            "defined": inputs["cycle_summary"].get("autonomous_work_cycle_defined"),
            "next_required_milestone": inputs["cycle_summary"].get("next_required_milestone"),
        },
        "legacy_asset_triage": {
            "defined": inputs["triage_summary"].get("legacy_asset_triage_defined"),
            "assets_scored": inputs["triage_summary"].get("assets_scored"),
            "bucket_counts": inputs["triage_summary"].get("bucket_counts", {}),
        },
        "observation_loop_status": {
            "read_only_observation_loop_defined": True,
            "tick_id": tick["tick_id"],
            "real_action_executed": False,
        },
        "top_risks": tick["blocked_risks"],
        "top_opportunities": tick["safe_opportunities"],
        "next_recommended_work": "L4.4 First Governed Read-Only Observation Tool Wrapper v0",
    }


def build_company_state_digest(inputs: dict[str, Any], tick: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_observation_loop.generated.company_state_digest",
        "schema_version": "v0",
        "what_the_company_knows_now": [
            "dry-run governance stack exists",
            "legacy assets are triaged before absorption",
            "generated summaries can be observed safely",
        ],
        "what_it_can_safely_observe": [
            "console read-model summaries",
            "live readiness and boundary summaries",
            "CIEU boundary summaries",
            "autonomy inventory and work-cycle summaries",
            "legacy triage summaries",
        ],
        "what_it_can_safely_do_now": [
            "generate read-only observation ticks",
            "recommend next work candidates",
            "prepare wrapper specs without executing tools",
        ],
        "what_remains_blocked": tick["blocked_risks"],
        "what_should_be_wrapped_next": [
            "read-only observation loop",
            "mission dashboard generator",
            "top legacy triage candidates",
        ],
        "live_enabled": False,
        "network_used": False,
    }


def build_work_candidates(tick: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    for item in tick["work_item_candidates"]:
        candidates.append(
            {
                **item,
                "requires_y_star_gov": item["risk_tier"] != "low",
                "requires_operator_approval": item["risk_tier"] != "low",
                "requires_cieu_event": True,
                "rationale": "derived from read-only observation tick",
            }
        )
    return {
        "schema_name": "ystar.governed_observation_loop.generated.observation_to_work_item_candidates",
        "schema_version": "v0",
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def build_summary(work_candidates: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_observation_loop.generated.governed_observation_loop_summary",
        "schema_version": "v0",
        "governed_observation_loop_defined": True,
        "read_only_observation_loop_defined": True,
        "observation_source_registry_defined": True,
        "observation_tick_generated": True,
        "mission_dashboard_snapshot_defined": True,
        "company_state_digest_defined": True,
        "observation_to_work_item_candidates_defined": work_candidates.get("candidate_count", 0) >= 3,
        "observation_to_work_item_candidate_count": work_candidates.get("candidate_count", 0),
        "mission_bounded_autonomy_supported": True,
        "step_by_step_human_prompting_reduced": True,
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "git_push_enabled": False,
        "daemon_control_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "email_or_external_communication_enabled": False,
        "next_required_milestone": "L4.4 First Governed Read-Only Observation Tool Wrapper v0",
        "generated_registry": "governed_observation_loop/generated/observation_source_registry.json",
        "generated_tick": "governed_observation_loop/generated/observation_tick_001.json",
        "generated_dashboard": "governed_observation_loop/generated/mission_dashboard_snapshot.json",
        "generated_digest": "governed_observation_loop/generated/company_state_digest.json",
        "warning": "Observation loop is read-only and executes no actions.",
    }


def build_report(summary: dict[str, Any], dashboard: dict[str, Any], digest: dict[str, Any]) -> str:
    lines = [
        "# Governed Observation Loop Report",
        "",
        "This report summarizes one deterministic read-only observation tick.",
        "",
        "## Mission",
        str(dashboard.get("mission")),
        "",
        "## Top Risks",
    ]
    lines.extend(f"- {risk}" for risk in dashboard.get("top_risks", []))
    lines.extend(["", "## Top Opportunities"])
    lines.extend(f"- {opportunity}" for opportunity in dashboard.get("top_opportunities", []))
    lines.extend(["", "## Company State"])
    lines.extend(f"- {item}" for item in digest.get("what_the_company_knows_now", []))
    lines.extend(
        [
            "",
            "## Safety",
            f"- real_action_executed: {summary['real_action_executed']}",
            f"- live_action_enabled: {summary['live_action_enabled']}",
            f"- cieu_persistence_enabled: {summary['cieu_persistence_enabled']}",
            "",
            f"Next: {summary['next_required_milestone']}",
        ]
    )
    return "\n".join(lines) + "\n"


def load_inputs() -> dict[str, Any]:
    return {
        "triage_buckets": load_json("legacy_asset_triage/generated/asset_absorption_buckets.json", {}),
        "triage_top": load_json("legacy_asset_triage/generated/top_absorption_candidates.json", {}),
        "triage_summary": load_json("legacy_asset_triage/generated/legacy_asset_triage_summary.json", {}),
        "mission": load_json("company_autonomous_work_cycle/generated/mission_profile.json", {}),
        "cycle_observation": load_json("company_autonomous_work_cycle/generated/company_observation_snapshot.json", {}),
        "cycle_summary": load_json("company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json", {}),
        "inventory_observation": load_json("company_autonomy_inventory/generated/observation_capability_map.json", {}),
        "inventory_resources": load_json("company_autonomy_inventory/generated/resource_sensing_map.json", {}),
        "inventory_actions": load_json("company_autonomy_inventory/generated/action_capability_map.json", {}),
        "live_readiness": load_json("labs_live_readiness/generated/live_readiness_report.json", {}),
        "live_boundary": load_json("labs_live_boundary/generated/live_boundary_summary.json", {}),
        "cieu_boundary": load_json("labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_summary.json", {}),
        "console_snapshot": load_json("console_read_model/generated/team_console_snapshot.json", {}),
    }


def main() -> int:
    GENERATED.mkdir(parents=True, exist_ok=True)
    inputs = load_inputs()
    registry = build_source_registry(inputs["triage_buckets"])
    tick = build_observation_tick(inputs, registry)
    dashboard = build_mission_dashboard(inputs, tick)
    digest = build_company_state_digest(inputs, tick)
    work_candidates = build_work_candidates(tick)
    summary = build_summary(work_candidates)

    write_json("governed_observation_loop/generated/observation_source_registry.json", registry)
    write_json("governed_observation_loop/generated/observation_tick_001.json", tick)
    write_json("governed_observation_loop/generated/mission_dashboard_snapshot.json", dashboard)
    write_json("governed_observation_loop/generated/company_state_digest.json", digest)
    write_json("governed_observation_loop/generated/observation_to_work_item_candidates.json", work_candidates)
    write_json("governed_observation_loop/generated/governed_observation_loop_summary.json", summary)
    write_text("governed_observation_loop/generated/governed_observation_loop_report.md", build_report(summary, dashboard, digest))

    print("Governed Observation Loop Builder: PASS")
    print(f"observation_sources: {registry['source_count']}")
    print(f"work_item_candidates: {work_candidates['candidate_count']}")
    print(f"next_required_milestone: {summary['next_required_milestone']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
