#!/usr/bin/env python3
"""Build deterministic legacy asset triage from compact generated inventory.

This builder reads only curated/generated inventory and simulator outputs. It
does not scan raw runtime artifacts, execute tools, or approve any asset for
live use.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "legacy_asset_triage" / "generated"

ALLOWED_BUCKETS = [
    "A_adopt_now_read_only",
    "B_wrap_as_governed_tool",
    "C_rewrite_from_design",
    "D_quarantine_as_evidence_ore",
    "E_retire_do_not_use",
]

READ_ONLY_CLASSES = {
    "console_and_read_model",
    "resource_sensing",
    "repo_or_code_observation",
    "reporting_or_status",
    "testing_or_validation",
    "safety_or_quarantine",
}

ACTION_CLASSES = {
    "action_execution",
    "auto_commit_or_git_action",
    "hook_or_gate",
    "scheduler_or_daemon",
    "mcp_or_external_interface",
    "cli_or_terminal_tool",
}

DESIGN_REWRITE_CLASSES = {
    "brain_and_memory",
    "cieu_helpers_or_audit",
    "market_or_web_observation",
}


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


def clamp(value: int) -> int:
    return max(0, min(5, value))


def has_any(asset: dict[str, Any], classes: set[str]) -> bool:
    return bool(set(asset.get("capability_classes", [])) & classes)


def mission_value_score(asset: dict[str, Any]) -> int:
    score = 1
    if has_any(asset, READ_ONLY_CLASSES):
        score += 2
    if has_any(asset, {"governance_bridge", "pre_u_counterfactual", "cieu_event_boundary"}):
        score += 2
    if asset.get("repo_name") == "ystar-company":
        score += 1
    if "company_" in asset.get("relative_path", "") or "console_read_model" in asset.get("relative_path", ""):
        score += 1
    return clamp(score)


def evidence_strength_score(asset: dict[str, Any]) -> int:
    score = min(3, len(asset.get("evidence_terms", [])) // 2)
    if asset.get("bounded_snippet"):
        score += 1
    if asset.get("actionability_level") in {"source_available", "test_available", "generated_summary"}:
        score += 1
    return clamp(score)


def action_power_score(asset: dict[str, Any]) -> int:
    score = 0
    if has_any(asset, ACTION_CLASSES):
        score += 3
    if has_any(asset, {"auto_commit_or_git_action", "scheduler_or_daemon", "action_execution"}):
        score += 2
    if asset.get("actionability_level") == "runtime_candidate_disabled":
        score += 1
    return clamp(score)


def safety_risk_score(asset: dict[str, Any]) -> int:
    risk = asset.get("risk_tier")
    score = {"low": 1, "medium": 3, "high": 4, "blocked": 5}.get(risk, 2)
    if has_any(asset, {"auto_commit_or_git_action", "scheduler_or_daemon"}):
        score += 1
    return clamp(score)


def governance_fit_score(asset: dict[str, Any]) -> int:
    score = 2
    if asset.get("governance_required"):
        score += 1
    if has_any(asset, {"governance_bridge", "safety_or_quarantine", "cieu_event_boundary"}):
        score += 2
    if asset.get("can_be_tool_registry_candidate"):
        score += 1
    return clamp(score)


def reuse_cost_score(asset: dict[str, Any]) -> int:
    score = {"low": 1, "medium": 3, "high": 4, "blocked": 5}.get(asset.get("risk_tier"), 2)
    if asset.get("repo_name") != "ystar-company":
        score += 1
    if asset.get("actionability_level") == "documentation_only":
        score -= 1
    if asset.get("actionability_level") == "runtime_candidate_disabled":
        score += 1
    return clamp(score)


def architecture_alignment_score(asset: dict[str, Any]) -> int:
    score = 1
    if asset.get("repo_name") == "ystar-company":
        score += 2
    if has_any(asset, {"console_and_read_model", "governance_bridge", "cieu_event_boundary", "safety_or_quarantine"}):
        score += 2
    if has_any(asset, {"market_or_web_observation", "scheduler_or_daemon"}):
        score -= 1
    return clamp(score)


def absorption_bucket(asset: dict[str, Any], scores: dict[str, int]) -> str:
    classes = set(asset.get("capability_classes", []))
    level = asset.get("actionability_level")
    path = asset.get("relative_path", "")

    if level == "generated_summary" or path.startswith("console_read_model/") or "/generated/" in path:
        if scores["safety_risk_score"] <= 2:
            return "A_adopt_now_read_only"
    if scores["evidence_strength_score"] <= 1 and level == "documentation_only":
        return "E_retire_do_not_use"
    if scores["mission_value_score"] <= 2 and scores["evidence_strength_score"] <= 2:
        return "E_retire_do_not_use"
    if asset.get("repo_name") != "ystar-company" and scores["mission_value_score"] <= 3:
        return "D_quarantine_as_evidence_ore"
    if classes & ACTION_CLASSES:
        if (
            asset.get("can_be_tool_registry_candidate")
            and scores["mission_value_score"] >= 4
            and scores["governance_fit_score"] >= 3
        ):
            return "B_wrap_as_governed_tool"
        if scores["mission_value_score"] >= 3:
            return "C_rewrite_from_design"
        return "D_quarantine_as_evidence_ore"
    if classes & DESIGN_REWRITE_CLASSES and scores["safety_risk_score"] >= 3:
        return "C_rewrite_from_design"
    if scores["mission_value_score"] >= 3 and scores["safety_risk_score"] <= 2:
        return "A_adopt_now_read_only"
    if scores["evidence_strength_score"] <= 2:
        return "D_quarantine_as_evidence_ore"
    return "C_rewrite_from_design"


def score_asset(asset: dict[str, Any]) -> dict[str, Any]:
    scores = {
        "mission_value_score": mission_value_score(asset),
        "evidence_strength_score": evidence_strength_score(asset),
        "action_power_score": action_power_score(asset),
        "safety_risk_score": safety_risk_score(asset),
        "governance_fit_score": governance_fit_score(asset),
        "reuse_cost_score": reuse_cost_score(asset),
        "architecture_alignment_score": architecture_alignment_score(asset),
    }
    bucket = absorption_bucket(asset, scores)
    return {
        "asset_id": asset.get("asset_id"),
        "repo_name": asset.get("repo_name"),
        "source_path": asset.get("relative_path"),
        "file_type": asset.get("file_type"),
        "capability_classes": asset.get("capability_classes", []),
        "actionability_level": asset.get("actionability_level"),
        "risk_tier": asset.get("risk_tier"),
        "governance_required": asset.get("governance_required"),
        "can_be_tool_registry_candidate": asset.get("can_be_tool_registry_candidate"),
        "recommended_owner_agent": (asset.get("likely_owner_agent_candidates") or ["Aiden-CEO"])[0],
        "evidence_terms": asset.get("evidence_terms", [])[:8],
        **scores,
        "absorption_bucket": bucket,
        "live_enabled": False,
        "scoring_method": "deterministic_metadata_rules",
    }


def build_matrix(assets: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [score_asset(asset) for asset in assets]
    return {
        "schema_name": "ystar.legacy_asset_triage.generated.asset_value_risk_matrix",
        "schema_version": "v0",
        "assets_scored": len(scored),
        "score_range": [0, 5],
        "semantic_truth_scoring_performed": False,
        "llm_scoring_used": False,
        "assets": scored,
    }


def bucket_counts(scored: list[dict[str, Any]]) -> dict[str, int]:
    counts = {bucket: 0 for bucket in ALLOWED_BUCKETS}
    for asset in scored:
        counts[asset["absorption_bucket"]] += 1
    return counts


def build_buckets(scored: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = {bucket: [] for bucket in ALLOWED_BUCKETS}
    for asset in scored:
        buckets[asset["absorption_bucket"]].append(
            {
                "asset_id": asset["asset_id"],
                "source_path": asset["source_path"],
                "bucket": asset["absorption_bucket"],
                "mission_value_score": asset["mission_value_score"],
                "safety_risk_score": asset["safety_risk_score"],
                "recommended_owner_agent": asset["recommended_owner_agent"],
                "live_enabled": False,
            }
        )
    return {
        "schema_name": "ystar.legacy_asset_triage.generated.asset_absorption_buckets",
        "schema_version": "v0",
        "allowed_buckets": ALLOWED_BUCKETS,
        "bucket_counts": bucket_counts(scored),
        "buckets": buckets,
        "blind_absorption_allowed": False,
        "blanket_rewrite_allowed": False,
        "live_actions_enabled": False,
    }


def build_top_candidates(scored: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = sorted(
        [
            asset
            for asset in scored
            if asset["absorption_bucket"] in {"A_adopt_now_read_only", "B_wrap_as_governed_tool"}
        ],
        key=lambda asset: (
            -asset["mission_value_score"],
            asset["safety_risk_score"],
            -asset["architecture_alignment_score"],
            asset["source_path"],
        ),
    )[:7]
    candidates = []
    for asset in ranked:
        wrapper = (
            "read_only_source_reference"
            if asset["absorption_bucket"] == "A_adopt_now_read_only"
            else "disabled_governed_tool_wrapper"
        )
        candidates.append(
            {
                "asset_id": asset["asset_id"],
                "source_path": asset["source_path"],
                "bucket": asset["absorption_bucket"],
                "why_valuable": "high mission value with deterministic evidence from compact inventory",
                "risk_notes": "must remain read-only or wrapped; no live execution is enabled",
                "required_governance_wrapper": wrapper,
                "recommended_owner_agent": asset["recommended_owner_agent"],
                "recommended_next_step": "review as governed observation or wrapper candidate",
                "live_enabled": False,
            }
        )
    return {
        "schema_name": "ystar.legacy_asset_triage.generated.top_absorption_candidates",
        "schema_version": "v0",
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def build_backlog(top_candidates: dict[str, Any]) -> dict[str, Any]:
    candidates = top_candidates.get("candidates", [])
    seed_refs = [candidate["asset_id"] for candidate in candidates[:3]]
    items = [
        (
            "absorb-001",
            "Adopt safe read-only generated summaries into observation registry",
            "A_adopt_now_read_only",
            "Samantha-Secretary",
            "low",
        ),
        (
            "absorb-002",
            "Wrap highest-value CLI or validation assets as disabled governed tools",
            "B_wrap_as_governed_tool",
            "Ryan-Platform",
            "medium",
        ),
        (
            "absorb-003",
            "Rewrite risky historical action patterns from design only",
            "C_rewrite_from_design",
            "Ethan-CTO",
            "medium",
        ),
        (
            "absorb-004",
            "Keep weak historical evidence in quarantine until curation exists",
            "D_quarantine_as_evidence_ore",
            "Maya-Governance",
            "medium",
        ),
        (
            "absorb-005",
            "Retire stale or low-value duplicates from autonomy planning",
            "E_retire_do_not_use",
            "Aiden-CEO",
            "low",
        ),
    ]
    backlog = []
    for backlog_id, title, bucket, owner, risk in items:
        backlog.append(
            {
                "backlog_id": backlog_id,
                "title": title,
                "asset_refs": seed_refs,
                "target_bucket": bucket,
                "recommended_owner_agent": owner,
                "risk_tier": risk,
                "requires_y_star_gov": risk != "low",
                "requires_operator_approval": bucket != "A_adopt_now_read_only",
                "requires_cieu_event": True,
                "live_enabled": False,
                "acceptance_criteria": [
                    "uses only curated/generated source references",
                    "keeps live execution disabled",
                    "documents required wrapper or review path",
                ],
                "notes": "triage backlog item only; no absorption is executed",
            }
        )
    return {
        "schema_name": "ystar.legacy_asset_triage.generated.governed_absorption_backlog",
        "schema_version": "v0",
        "backlog_count": len(backlog),
        "items": backlog,
    }


def build_retired_or_quarantined(scored: list[dict[str, Any]]) -> dict[str, Any]:
    assets = [
        {
            "asset_id": asset["asset_id"],
            "source_path": asset["source_path"],
            "bucket": asset["absorption_bucket"],
            "risk_tier": asset["risk_tier"],
            "reason": "not safe or valuable enough for direct absorption",
            "live_enabled": False,
        }
        for asset in scored
        if asset["absorption_bucket"] in {"D_quarantine_as_evidence_ore", "E_retire_do_not_use"}
    ]
    return {
        "schema_name": "ystar.legacy_asset_triage.generated.retired_or_quarantined_assets",
        "schema_version": "v0",
        "asset_count": len(assets),
        "assets": assets[:100],
        "truncated_for_read_model": len(assets) > 100,
    }


def build_summary(scored: list[dict[str, Any]], top_candidates: dict[str, Any], backlog: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.legacy_asset_triage.generated.legacy_asset_triage_summary",
        "schema_version": "v0",
        "legacy_asset_triage_defined": True,
        "assets_scored": len(scored),
        "absorption_buckets_defined": True,
        "bucket_counts": bucket_counts(scored),
        "top_absorption_candidates_defined": bool(top_candidates.get("candidates")),
        "top_absorption_candidate_count": top_candidates.get("candidate_count", 0),
        "governed_absorption_backlog_defined": backlog.get("backlog_count", 0) >= 5,
        "governed_absorption_backlog_count": backlog.get("backlog_count", 0),
        "blind_absorption_allowed": False,
        "blanket_rewrite_allowed": False,
        "live_actions_enabled": False,
        "external_actions_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "cieu_persistence_enabled": False,
        "next_required_milestone": "L4.4 First Governed Read-Only Observation Tool Wrapper v0",
        "generated_matrix": "legacy_asset_triage/generated/asset_value_risk_matrix.json",
        "generated_buckets": "legacy_asset_triage/generated/asset_absorption_buckets.json",
        "generated_top_candidates": "legacy_asset_triage/generated/top_absorption_candidates.json",
        "generated_backlog": "legacy_asset_triage/generated/governed_absorption_backlog.json",
        "warning": "Triage is classification only; no asset is absorbed or enabled.",
    }


def build_manifest(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.legacy_asset_triage.generated.legacy_asset_triage_manifest",
        "schema_version": "v0",
        "generated_by": "legacy_asset_triage/tools/build_legacy_asset_triage.py",
        "inputs": [
            "company_autonomy_inventory/generated/existing_asset_inventory.json",
            "company_autonomy_inventory/generated/governed_tool_registry_candidates.json",
            "company_autonomy_inventory/generated/action_capability_map.json",
            "company_autonomy_inventory/generated/observation_capability_map.json",
            "company_autonomy_inventory/generated/resource_sensing_map.json",
            "company_autonomy_inventory/generated/agent_role_capability_matrix.json",
            "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json",
            "company_autonomous_work_cycle/generated/next_task_recommendations.json",
        ],
        "generated_files": [
            "legacy_asset_triage/generated/asset_value_risk_matrix.json",
            "legacy_asset_triage/generated/asset_absorption_buckets.json",
            "legacy_asset_triage/generated/governed_absorption_backlog.json",
            "legacy_asset_triage/generated/top_absorption_candidates.json",
            "legacy_asset_triage/generated/retired_or_quarantined_assets.json",
            "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
            "legacy_asset_triage/generated/legacy_asset_triage_report.md",
        ],
        "assets_scored": summary["assets_scored"],
        "live_actions_enabled": False,
        "raw_runtime_artifacts_read": False,
        "semantic_truth_scoring_performed": False,
    }


def build_report(summary: dict[str, Any], top_candidates: dict[str, Any]) -> str:
    lines = [
        "# Legacy Asset Triage Report",
        "",
        "Legacy assets were scored from compact generated inventory metadata only.",
        "",
        "## Bucket Counts",
    ]
    for bucket, count in summary["bucket_counts"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "## Top Absorption Candidates"])
    for candidate in top_candidates.get("candidates", []):
        lines.append(f"- {candidate['asset_id']}: {candidate['source_path']} ({candidate['bucket']})")
    lines.extend(
        [
            "",
            "## Safety",
            "- blind_absorption_allowed: false",
            "- blanket_rewrite_allowed: false",
            "- live_actions_enabled: false",
            "- no CIEU persistence, memory ingestion, or brain writeback is enabled",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    GENERATED.mkdir(parents=True, exist_ok=True)
    inventory = load_json("company_autonomy_inventory/generated/existing_asset_inventory.json", {"assets": []})
    assets = inventory.get("assets", [])

    matrix = build_matrix(assets)
    scored = matrix["assets"]
    buckets = build_buckets(scored)
    top_candidates = build_top_candidates(scored)
    backlog = build_backlog(top_candidates)
    retired = build_retired_or_quarantined(scored)
    summary = build_summary(scored, top_candidates, backlog)
    manifest = build_manifest(summary)

    write_json("legacy_asset_triage/generated/asset_value_risk_matrix.json", matrix)
    write_json("legacy_asset_triage/generated/asset_absorption_buckets.json", buckets)
    write_json("legacy_asset_triage/generated/governed_absorption_backlog.json", backlog)
    write_json("legacy_asset_triage/generated/top_absorption_candidates.json", top_candidates)
    write_json("legacy_asset_triage/generated/retired_or_quarantined_assets.json", retired)
    write_json("legacy_asset_triage/generated/legacy_asset_triage_summary.json", summary)
    write_json("legacy_asset_triage/generated/legacy_asset_triage_manifest.json", manifest)
    write_text("legacy_asset_triage/generated/legacy_asset_triage_report.md", build_report(summary, top_candidates))

    print("Legacy Asset Triage Builder: PASS")
    print(f"assets_scored: {summary['assets_scored']}")
    print(f"top_absorption_candidates: {summary['top_absorption_candidate_count']}")
    print(f"next_required_milestone: {summary['next_required_milestone']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
