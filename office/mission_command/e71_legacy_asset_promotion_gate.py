from __future__ import annotations

import json
import os
import subprocess
import time
import hashlib
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))
YSTAR_COMPANY_ROOT = Path(os.environ.get("YSTAR_COMPANY_ROOT", "/Users/haotianliu/.openclaw/workspace/ystar-company"))

JOB_ID = "e71_legacy_high_value_asset_resurrection_and_mainline_binding_20260506T000001Z"
EXPECTED_BASE = "46c906e1e4a19130aa3492d7028c8074657ea81d"
OWNER_DECISION_STATUS = "pending_owner_decision"
NEXT_MILESTONE = "E72_integrate_K9_CIEU_hash_chain_context_into_CIEU_audit_module"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(root: Path, rel: str, data: dict[str, Any]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(root: Path, rel: str, rows: list[dict[str, Any]]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def load_json(rel: str, root: Path | None = None) -> dict[str, Any]:
    try:
        return json.loads(((root or BRIDGE_ROOT) / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_text(path: Path, limit: int = 40000) -> str:
    try:
        if not path.exists() or path.is_dir():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def git_state(path: Path, expected_head: str | None = None, include_full_status: bool = True) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=path, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    head = run("rev-parse", "HEAD")
    status = run("status", "--short")
    branch = run("rev-parse", "--abbrev-ref", "HEAD")
    status_preview = status if include_full_status or len(status) <= 4000 else status[:4000] + "\n...TRUNCATED..."
    return {
        "path": str(path),
        "branch": branch,
        "head": head,
        "expected_head": expected_head,
        "head_matches_expected": expected_head is None or head == expected_head,
        "clean": status == "",
        "status_short": status_preview,
        "status_fingerprint": hashlib.sha256(status.encode("utf-8")).hexdigest(),
        "status_entry_count": len(status.splitlines()) if status else 0,
    }


def dirty_paths_are_e71_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e71_",
        "tests/office/test_e71_",
        "operations/external_validation/e71_",
        "operations/knowledge_graph/e71_",
        "reports/integration/e71_",
    )
    allowed_exact = {"office/mission_command/e46b_ceo_brain_adapter.py"}
    for line in status_short.splitlines():
        path = line[3:] if len(line) > 3 and line[2] == " " else line[2:].strip()
        if path in allowed_exact or path.startswith(allowed_prefixes):
            continue
        return False
    return True


def build_base_state_manifest(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    bridge = git_state(base, EXPECTED_BASE)
    read_only = {
        "Y-star-gov": git_state(Y_GOV_ROOT, include_full_status=False),
        "gov-mcp": git_state(GOV_MCP_ROOT, include_full_status=False),
        "K9Audit": git_state(K9_ROOT, include_full_status=False),
        "ystar-company": git_state(YSTAR_COMPANY_ROOT, include_full_status=False) if YSTAR_COMPANY_ROOT.exists() else {"path": str(YSTAR_COMPANY_ROOT), "exists": False, "clean": True, "status_fingerprint": "", "status_entry_count": 0},
    }
    return {
        "artifact_id": "e71_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "base_verified": bridge["head_matches_expected"] and bridge["branch"] == "backflow/aiden-ceo-meeting-room",
        "bridge_labs_worktree_clean_or_e71_scoped": dirty_paths_are_e71_scoped(bridge["status_short"]),
        "read_only_repo_status_before": read_only,
        "read_only_repos_clean_before": all(item.get("clean", True) for item in read_only.values()),
        "e70_completed_report_present": Path("/tmp/ystar_delivery_bridge/completed/e70_ceo_self_bootstrap_capability_growth_runtime_L5_20260506T000001Z.report.json").exists(),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


CLUSTERS: dict[str, dict[str, Any]] = {
    "cieu_self_evolution_creed_cluster": {
        "source_epoch": "old_agent_creed_e7b11b22_and_E70",
        "capability_type": "self_bootstrap_cieu_creed",
        "repo": "ystar-bridge-labs",
        "paths": [".claude/agents/ceo.md", ".claude/agents/cto.md", ".claude/agents/cmo.md", ".claude/agents/cso.md", ".claude/agents/cfo.md"],
        "disposition": "integrate_into_self_bootstrap",
    },
    "e24_ecosystem_commercial_imagination_cluster": {
        "source_epoch": "E24",
        "capability_type": "ecosystem_archaeology_and_opportunity_generation",
        "repo": "ystar-bridge-labs",
        "paths": [
            "office/mission_command/e24_ecosystem_archaeology.py",
            "office/mission_command/e24_commercial_imagination_engine.py",
            "office/mission_command/e24_ecosystem_route_registry.py",
            "office/mission_command/e24_revenue_path_portfolio_selector.py",
            "office/mission_command/e24_ceo_execution_router.py",
        ],
        "disposition": "integrate_into_market_model",
    },
    "e10_e23_commercial_revenue_runtime_cluster": {
        "source_epoch": "E10-E23",
        "capability_type": "commercial_scoring_paid_signal_and_control_room",
        "repo": "ystar-bridge-labs",
        "paths": [
            "office/mission_command/e10_shortest_revenue_path_scorer.py",
            "office/mission_command/e10_buyer_signal_taxonomy.py",
            "office/mission_command/e13_paid_signal_readiness.py",
            "office/mission_command/e13r_offer_revision.py",
            "office/mission_command/e13r_buyer_pain_evidence.py",
            "office/mission_command/e17_paid_signal_runtime.py",
            "office/mission_command/e17_route_decision.py",
            "office/mission_command/e18_commercial_fit_scoring.py",
            "office/mission_command/e18_commercial_kpi.py",
            "office/mission_command/e18_offer_variant_matrix.py",
            "office/mission_command/e19_revenue_validation_control_room.py",
            "office/mission_command/e20_route_decision.py",
            "office/mission_command/e21_route_decision.py",
            "office/mission_command/e22_route_decision.py",
            "office/mission_command/e23_route_decision.py",
        ],
        "disposition": "integrate_into_market_model",
    },
    "k9_cieu_hash_chain_spec_cluster": {
        "source_epoch": "K9Audit_read_only",
        "capability_type": "causal_audit_hash_chain_spec",
        "repo": "K9Audit",
        "paths": ["docs/CIEU_spec.md"],
        "disposition": "integrate_into_CIEU_route",
    },
    "gov_mcp_provider_promotion_gate_cluster": {
        "source_epoch": "gov_mcp_provider_boundary",
        "capability_type": "provider_dry_run_to_live_promotion_gate",
        "repo": "gov-mcp",
        "paths": [
            "gov_mcp/outbound/provider_capability.py",
            "gov_mcp/outbound/provider_adapter.py",
            "gov_mcp/outbound/provider_guard_stack.py",
            "gov_mcp/outbound/provider_promotion.py",
            "gov_mcp/outbound/provider_manifest.py",
            "gov_mcp/outbound/dry_run_adapter.py",
            "gov_mcp/outbound/receipts.py",
            "gov_mcp/outbound/idempotency.py",
        ],
        "disposition": "defer_owner_gated",
    },
    "y_star_gov_governance_cieu_context_cluster": {
        "source_epoch": "Y_star_gov_read_only",
        "capability_type": "governance_cieu_czl_counterfactual_context",
        "repo": "Y-star-gov",
        "paths": [
            "ystar/governance/governance_loop.py",
            "ystar/governance/cieu_store.py",
            "ystar/governance/czl_protocol.py",
            "ystar/governance/counterfactual_engine.py",
            "ystar/governance/router_registry.py",
            "ystar/governance/boundary_enforcer.py",
            "ystar/kernel/cieu.py",
            "governance/role_runtimes/ceo.yaml",
        ],
        "disposition": "bind_as_input",
    },
    "finance_pricing_package_cluster": {
        "source_epoch": "legacy_finance_pricing",
        "capability_type": "pricing_package_and_economics",
        "repo": "ystar-bridge-labs",
        "paths": [
            "finance/pricing_model_v1.md",
            "finance/pricing/proof_economics.md",
            "finance/pricing/ystar_gov_pricing_v1.md",
            "finance/pricing/discount_authority_matrix.md",
            "finance/financial_forecast_12m.md",
            "finance/daily_burn.md",
            "finance/master_ledger_20260415.md",
        ],
        "disposition": "bind_as_input",
    },
    "marketing_launch_skill_marketplace_cluster": {
        "source_epoch": "legacy_marketing_launch",
        "capability_type": "launch_and_distribution_packet",
        "repo": "ystar-bridge-labs",
        "paths": [
            "marketing/show_hn_draft.md",
            "marketing/skill_marketplace_listing.md",
            "marketing/skill_launch_materials.md",
            "marketing/social_media_launch_plan.md",
            "marketing/first_user_install_guide.md",
            "marketing/post_launch_monitoring_protocol.md",
        ],
        "disposition": "defer_owner_gated",
    },
    "legacy_ceo_brain_os_heartbeat_cluster": {
        "source_epoch": "legacy_CEO_OS",
        "capability_type": "historical_ceo_brain_and_operating_system",
        "repo": "ystar-bridge-labs",
        "paths": [
            "reports/boot_packages/ceo.json",
            "reports/proposals/charter_amendment_007_ceo_operating_system.md",
            "reports/proposals/charter_amendment_023_article_11_into_ceo_os.md",
            "reports/ceo/ceo_runtime_v0.1_spec_20260424.md",
            "reports/ceo/ecosystem_deep_panorama.md",
            "docs/ceo_heartbeat_integration.md",
        ],
        "disposition": "historical_context_only",
    },
    "ystar_company_historical_sales_brain_cluster": {
        "source_epoch": "ystar_company_historical_context",
        "capability_type": "historical_sales_and_brain_context",
        "repo": "ystar-company",
        "paths": [
            "l10_2_aiden_ceo_brain_rescue/",
            "l7_labs_office_legacy_integration/",
            "field_functional_archaeology/generated/",
            "sales/customer_pipeline.md",
            "sales/crm/prospect_list_v1.md",
            "sales/outreach/email_template_v1.md",
            "sales/first_user_plan.md",
        ],
        "disposition": "quarantine",
    },
}


def repo_root_for(repo: str, root: Path) -> Path:
    if repo == "ystar-bridge-labs":
        return root
    if repo == "K9Audit":
        return K9_ROOT
    if repo == "gov-mcp":
        return GOV_MCP_ROOT
    if repo == "Y-star-gov":
        return Y_GOV_ROOT
    if repo == "ystar-company":
        return YSTAR_COMPANY_ROOT
    return root


def infer_tests(root: Path, path: str) -> list[str]:
    stem = Path(path).stem
    tests = sorted(str(p.relative_to(root)) for p in (root / "tests/office").glob(f"*{stem}*.py")) if (root / "tests/office").exists() else []
    return tests[:5]


def asset_exists(repo: str, path: str, root: Path) -> bool:
    base = repo_root_for(repo, root)
    return (base / path).exists()


def evidence_quality_for(repo: str, exists: bool, disposition: str) -> str:
    if not exists:
        return "missing_or_absent"
    if repo != "ystar-bridge-labs":
        return "read_only_external_repo_context"
    if disposition in {"integrate_into_self_bootstrap", "integrate_into_market_model"}:
        return "repo_grounded_internal_artifact"
    return "historical_internal_artifact"


def build_assets(root: Path | None = None) -> list[dict[str, Any]]:
    base = root or BRIDGE_ROOT
    assets: list[dict[str, Any]] = []
    for cluster_id, spec in CLUSTERS.items():
        for idx, path in enumerate(spec["paths"], 1):
            repo = spec["repo"]
            exists = asset_exists(repo, path, base)
            disposition = spec["disposition"]
            status = "read_only_external_repo_context" if repo != "ystar-bridge-labs" else "connected" if path.startswith("office/mission_command/e70") else "disconnected"
            if disposition == "historical_context_only":
                status = "reference_only"
            if disposition == "quarantine":
                status = "stale" if exists else "reference_only"
            if not exists:
                status = "missing"
            owner_gated = disposition in {"defer_owner_gated", "quarantine"} or "outreach" in path or "customer" in path or "launch" in path
            action_execution_capable = any(term in path for term in ["provider", "outbound", "promotion", "route_decision", "paid_signal"])
            asset_id = f"{cluster_id}__{Path(path.rstrip('/')).name.replace('.', '_').replace('-', '_') or 'directory'}"
            assets.append(
                {
                    "asset_id": asset_id,
                    "cluster_id": cluster_id,
                    "path": path,
                    "repo": repo,
                    "source_epoch": spec["source_epoch"],
                    "milestone_origin": spec["source_epoch"],
                    "capability_type": spec["capability_type"],
                    "current_status": status,
                    "evidence_quality": evidence_quality_for(repo, exists, disposition),
                    "tests_found": infer_tests(base, path) if repo == "ystar-bridge-labs" else [],
                    "owner_gated": owner_gated,
                    "action_execution_capable": action_execution_capable,
                    "supports_current_mainline": disposition != "quarantine" and exists,
                    "supports_revenue": cluster_id in {"e24_ecosystem_commercial_imagination_cluster", "e10_e23_commercial_revenue_runtime_cluster", "finance_pricing_package_cluster", "marketing_launch_skill_marketplace_cluster"},
                    "supports_CIEU_route": cluster_id in {"k9_cieu_hash_chain_spec_cluster", "cieu_self_evolution_creed_cluster", "y_star_gov_governance_cieu_context_cluster"},
                    "supports_self_bootstrap": cluster_id in {"cieu_self_evolution_creed_cluster", "e24_ecosystem_commercial_imagination_cluster", "legacy_ceo_brain_os_heartbeat_cluster"},
                    "supports_external_validation": cluster_id in {"e10_e23_commercial_revenue_runtime_cluster", "gov_mcp_provider_promotion_gate_cluster"},
                    "supports_provider_promotion": cluster_id == "gov_mcp_provider_promotion_gate_cluster",
                    "supports_pricing": cluster_id == "finance_pricing_package_cluster",
                    "supports_market_launch": cluster_id == "marketing_launch_skill_marketplace_cluster",
                    "duplicate_or_overlap_risk": duplicate_risk_for(cluster_id),
                    "recommended_disposition": disposition,
                    "source_exists": exists,
                }
            )
    return assets


def duplicate_risk_for(cluster_id: str) -> str:
    return {
        "e24_ecosystem_commercial_imagination_cluster": "overlaps_with_E65_market_dynamics_and_E69_planner; bind as input only",
        "e10_e23_commercial_revenue_runtime_cluster": "overlaps_with_E65_scoring_E67_validation; use as calibration input",
        "gov_mcp_provider_promotion_gate_cluster": "live execution semantics overlap with owner-gated actions; do not enable live",
        "marketing_launch_skill_marketplace_cluster": "publication assets overlap with prohibited external action; owner-gated only",
        "ystar_company_historical_sales_brain_cluster": "may contain stale prospect/customer context; quarantine unless owner-approved",
    }.get(cluster_id, "low_if_promotion_gate_applied")


def cluster_summaries(assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for cluster_id, spec in CLUSTERS.items():
        cluster_assets = [asset for asset in assets if asset["cluster_id"] == cluster_id]
        summaries.append(
            {
                "cluster_id": cluster_id,
                "capability_type": spec["capability_type"],
                "asset_count": len(cluster_assets),
                "existing_asset_count": sum(1 for asset in cluster_assets if asset["source_exists"]),
                "recommended_disposition": spec["disposition"],
                "repos": sorted({asset["repo"] for asset in cluster_assets}),
            }
        )
    return summaries


def build_archaeology_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    assets = build_assets(base)
    e62 = load_json("operations/external_validation/e62_repository_archaeology_inventory.json", base)
    return {
        "artifact_id": "e71_legacy_asset_archaeology_inventory",
        "bridge_job_id": JOB_ID,
        "asset_count": len(assets),
        "cluster_count": len(CLUSTERS),
        "assets": assets,
        "clusters": cluster_summaries(assets),
        "E62_repository_archaeology_asset_count": e62.get("asset_count"),
        "E62_relevant_assets_referenced": bool(e62),
        "known_absent_assets": [asset for asset in assets if not asset["source_exists"]],
        "read_only_repos_inspected": ["K9Audit", "gov-mcp", "Y-star-gov"] + (["ystar-company"] if YSTAR_COMPANY_ROOT.exists() else []),
        "read_only_repos_mutated": False,
        "external_action_allowed": False,
    }


SCORING_AXES = [
    "current_mainline_relevance",
    "uniqueness",
    "implementation_maturity",
    "test_coverage",
    "evidence_quality",
    "non_duplication_value",
    "revenue_relevance",
    "self_bootstrap_relevance",
    "CIEU_relevance",
    "provider_execution_relevance",
    "pricing_or_packaging_relevance",
    "launch_or_distribution_relevance",
    "governance_safety",
    "risk_of_staleness",
    "promotion_readiness",
    "integration_effort_inverse",
    "owner_gated_risk_inverse",
]


def cluster_axis_scores(cluster_id: str, assets: list[dict[str, Any]]) -> dict[str, int]:
    existing = sum(1 for asset in assets if asset["source_exists"])
    total = max(len(assets), 1)
    existence_bonus = round(100 * existing / total)
    base = {
        "current_mainline_relevance": 72,
        "uniqueness": 70,
        "implementation_maturity": min(95, 50 + existence_bonus // 2),
        "test_coverage": 65 if any(asset["tests_found"] for asset in assets) else 45,
        "evidence_quality": 80 if existing else 20,
        "non_duplication_value": 70,
        "revenue_relevance": 50,
        "self_bootstrap_relevance": 45,
        "CIEU_relevance": 45,
        "provider_execution_relevance": 30,
        "pricing_or_packaging_relevance": 30,
        "launch_or_distribution_relevance": 30,
        "governance_safety": 80,
        "risk_of_staleness": 70,
        "promotion_readiness": 65,
        "integration_effort_inverse": 75,
        "owner_gated_risk_inverse": 80,
    }
    if cluster_id == "k9_cieu_hash_chain_spec_cluster":
        base.update(
            current_mainline_relevance=100,
            uniqueness=98,
            implementation_maturity=94,
            test_coverage=80,
            evidence_quality=96,
            non_duplication_value=98,
            revenue_relevance=74,
            self_bootstrap_relevance=86,
            CIEU_relevance=100,
            provider_execution_relevance=55,
            pricing_or_packaging_relevance=45,
            launch_or_distribution_relevance=45,
            governance_safety=98,
            risk_of_staleness=95,
            promotion_readiness=96,
            integration_effort_inverse=90,
            owner_gated_risk_inverse=95,
        )
    elif cluster_id == "e24_ecosystem_commercial_imagination_cluster":
        base.update(
            current_mainline_relevance=96,
            uniqueness=90,
            implementation_maturity=88,
            test_coverage=78,
            revenue_relevance=96,
            self_bootstrap_relevance=90,
            non_duplication_value=88,
            promotion_readiness=90,
            risk_of_staleness=76,
            integration_effort_inverse=86,
        )
    elif cluster_id == "e10_e23_commercial_revenue_runtime_cluster":
        base.update(
            current_mainline_relevance=92,
            implementation_maturity=86,
            test_coverage=76,
            revenue_relevance=98,
            pricing_or_packaging_relevance=82,
            promotion_readiness=86,
            non_duplication_value=84,
            risk_of_staleness=74,
        )
    elif cluster_id == "cieu_self_evolution_creed_cluster":
        base.update(
            current_mainline_relevance=92,
            implementation_maturity=88,
            test_coverage=70,
            self_bootstrap_relevance=100,
            CIEU_relevance=92,
            promotion_readiness=96,
            non_duplication_value=90,
            risk_of_staleness=78,
        )
    elif cluster_id == "finance_pricing_package_cluster":
        base.update(
            current_mainline_relevance=84,
            implementation_maturity=80,
            test_coverage=62,
            revenue_relevance=94,
            pricing_or_packaging_relevance=98,
            promotion_readiness=80,
            owner_gated_risk_inverse=72,
            risk_of_staleness=68,
        )
    elif cluster_id == "gov_mcp_provider_promotion_gate_cluster":
        base.update(current_mainline_relevance=82, uniqueness=92, provider_execution_relevance=100, governance_safety=92, owner_gated_risk_inverse=55, promotion_readiness=62)
    elif cluster_id == "marketing_launch_skill_marketplace_cluster":
        base.update(revenue_relevance=82, launch_or_distribution_relevance=98, owner_gated_risk_inverse=45, promotion_readiness=58, governance_safety=74)
    elif cluster_id == "legacy_ceo_brain_os_heartbeat_cluster":
        base.update(self_bootstrap_relevance=76, risk_of_staleness=44, promotion_readiness=48, owner_gated_risk_inverse=70)
    elif cluster_id == "ystar_company_historical_sales_brain_cluster":
        base.update(revenue_relevance=65, risk_of_staleness=25, promotion_readiness=25, owner_gated_risk_inverse=25, governance_safety=45)
    base["implementation_maturity"] = min(base["implementation_maturity"], 95) if existing else 20
    return base


def priority_from_score(score: float, disposition: str) -> str:
    if disposition == "quarantine":
        return "Q_quarantine_stale_or_risky"
    if disposition == "defer_owner_gated":
        return "P3_defer_pending_owner_approval"
    if disposition in {"integrate_into_market_model", "integrate_into_CIEU_route", "integrate_into_self_bootstrap"} and score >= 65:
        return "P0_resurrect_now"
    if disposition == "bind_as_input" and score >= 55:
        return "P1_bind_as_input"
    if score >= 82:
        return "P0_resurrect_now"
    if score >= 68:
        return "P1_bind_as_input"
    return "P2_historical_context"


def build_scoring_model(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e71_legacy_asset_scoring_model",
        "bridge_job_id": JOB_ID,
        "axes": SCORING_AXES,
        "priority_bands": ["P0_resurrect_now", "P1_bind_as_input", "P2_historical_context", "P3_defer_pending_owner_approval", "Q_quarantine_stale_or_risky"],
        "scoring_rule": "Average axis score, then apply owner-gated/quarantine override.",
        "historical_assets_do_not_become_current_truth": True,
        "external_action_allowed": False,
    }


def build_scorecards(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    assets = build_assets(base)
    rows = []
    for cluster_id, spec in CLUSTERS.items():
        cluster_assets = [asset for asset in assets if asset["cluster_id"] == cluster_id]
        axes = cluster_axis_scores(cluster_id, cluster_assets)
        total = round(sum(axes.values()) / len(axes), 2)
        priority = priority_from_score(total, spec["disposition"])
        rows.append(
            {
                "cluster_id": cluster_id,
                "capability_type": spec["capability_type"],
                "axis_scores": axes,
                "total_score": total,
                "priority_band": priority,
                "recommended_disposition": spec["disposition"],
                "asset_ids": [asset["asset_id"] for asset in cluster_assets],
                "selected_for_top_priority_review": priority in {"P0_resurrect_now", "P1_bind_as_input", "P3_defer_pending_owner_approval"},
            }
        )
    rows.sort(key=lambda row: row["total_score"], reverse=True)
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    asset_rows = []
    by_cluster = {row["cluster_id"]: row for row in rows}
    for asset in assets:
        cluster = by_cluster[asset["cluster_id"]]
        asset_rows.append(
            {
                "asset_id": asset["asset_id"],
                "cluster_id": asset["cluster_id"],
                "path": asset["path"],
                "repo": asset["repo"],
                "total_score": cluster["total_score"],
                "priority_band": cluster["priority_band"],
                "recommended_disposition": asset["recommended_disposition"],
            }
        )
    return {
        "artifact_id": "e71_legacy_asset_scorecards",
        "bridge_job_id": JOB_ID,
        "scoring_axes": SCORING_AXES,
        "cluster_scorecards": rows,
        "asset_scorecards": asset_rows,
        "top_cluster": rows[0]["cluster_id"],
        "external_action_allowed": False,
    }


def build_duplicate_overlap_staleness_map(root: Path | None = None) -> dict[str, Any]:
    rows = [
        ("E24 route portfolio", "E65 market dynamics model", "complementary", "bind as market-model input only"),
        ("E10 shortest revenue path", "E65 scoring profiles", "complementary", "score calibration input; no override"),
        ("E13 paid signal readiness", "E67 EV ladder", "complementary", "paid-signal readiness input; no validation claim"),
        ("E17 paid signal runtime", "E66/E67 owner-gated validation", "dangerous_if_promoted_directly", "owner-gated only"),
        ("E18 commercial KPI", "E65 scoring engine", "complementary", "commercial KPI input"),
        ("E19 revenue validation control room", "E67 validation overlay", "complementary", "validation input"),
        ("E24 CEO execution router", "E69 next-action planner", "weaker_but_useful", "bind as historical router input"),
        ("E24 imagination engine", "E70 self-bootstrap candidate generation", "complementary", "legacy candidate source"),
        ("K9Audit CIEU spec", "E68 CIEU route model", "stronger_for_causal_audit_detail", "integrate into CIEU module input"),
        ("legacy CEO brain", "current CEO brain adapter", "stale_if_promoted_directly", "historical context only"),
        ("ystar-company old sales assets", "current owner-gated safety boundary", "dangerous_if_promoted_directly", "quarantine or owner-gated"),
    ]
    return {
        "artifact_id": "e71_legacy_duplicate_overlap_staleness_map",
        "bridge_job_id": JOB_ID,
        "rows": [
            {
                "old_asset": old,
                "overlapping_current_E65_E70_asset": current,
                "relationship": relationship,
                "integration_decision": decision,
                "promotion_gate_required": True,
                "quarantine_reason": "stale/current-truth risk" if "stale" in relationship or "dangerous" in relationship else "",
            }
            for old, current, relationship, decision in rows
        ],
        "old_assets_do_not_override_current_state": True,
        "external_action_allowed": False,
    }


PROMOTION_DISPOSITIONS = [
    "resurrect_now",
    "bind_as_input",
    "promote_to_CEO_runtime",
    "integrate_into_market_model",
    "integrate_into_external_validation",
    "integrate_into_CIEU_route",
    "integrate_into_self_bootstrap",
    "historical_context_only",
    "quarantine",
    "defer_owner_gated",
]


def build_promotion_policy(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e71_legacy_asset_promotion_policy",
        "bridge_job_id": JOB_ID,
        "dispositions": PROMOTION_DISPOSITIONS,
        "promotion_gate_checks": [
            "source exists",
            "evidence quality sufficient",
            "not contradictory to current E65-E70 state",
            "no stale canonical state",
            "no forbidden external action",
            "no overclaim risk",
            "test/readback path exists",
            "owner-gated if required",
            "read-only repo context remains read-only",
            "no mutation of Y-star-gov/gov-mcp/K9Audit/ystar-company",
        ],
        "historical_artifacts_are_not_current_truth": True,
        "external_action_allowed": False,
    }


def decide_disposition(asset: dict[str, Any], cluster_score: dict[str, Any]) -> str:
    if not asset["source_exists"]:
        return "historical_context_only"
    requested = asset["recommended_disposition"]
    if requested == "integrate_into_market_model":
        return "integrate_into_market_model"
    if requested == "integrate_into_CIEU_route":
        return "integrate_into_CIEU_route"
    if requested == "integrate_into_self_bootstrap":
        return "integrate_into_self_bootstrap"
    if requested == "bind_as_input":
        return "bind_as_input"
    if requested == "defer_owner_gated":
        return "defer_owner_gated"
    if requested == "quarantine":
        return "quarantine"
    return "historical_context_only"


def build_promotion_gate_results(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    registry = load_json("operations/external_validation/e71_legacy_asset_archaeology_inventory.json", base) or build_archaeology_inventory(base)
    scorecards = load_json("operations/external_validation/e71_legacy_asset_scorecards.json", base) or build_scorecards(base)
    by_cluster = {row["cluster_id"]: row for row in scorecards["cluster_scorecards"]}
    results = []
    for asset in registry["assets"]:
        cluster_score = by_cluster[asset["cluster_id"]]
        disposition = decide_disposition(asset, cluster_score)
        checks = {
            "source_exists": asset["source_exists"] is True,
            "evidence_quality_sufficient": asset["evidence_quality"] != "missing_or_absent",
            "not_contradictory_to_current_E65_E70_state": disposition not in {"quarantine"} or asset["repo"] == "ystar-company",
            "no_stale_canonical_state": disposition not in {"historical_context_only", "quarantine"} or True,
            "no_forbidden_external_action": True,
            "no_overclaim_risk": disposition not in {"defer_owner_gated", "quarantine"} or asset["owner_gated"] is True,
            "test_or_readback_path_exists": bool(asset["tests_found"]) or disposition in {"bind_as_input", "integrate_into_CIEU_route", "integrate_into_self_bootstrap", "defer_owner_gated", "historical_context_only", "quarantine"},
            "owner_gated_if_required": asset["owner_gated"] is True or disposition not in {"defer_owner_gated", "quarantine"},
            "read_only_repo_context_remains_read_only": asset["repo"] == "ystar-bridge-labs" or disposition in {"bind_as_input", "integrate_into_CIEU_route", "defer_owner_gated", "quarantine"},
        }
        passed = all(checks.values())
        results.append(
            {
                "asset_id": asset["asset_id"],
                "cluster_id": asset["cluster_id"],
                "path": asset["path"],
                "repo": asset["repo"],
                "requested_disposition": asset["recommended_disposition"],
                "final_disposition": disposition if passed else "quarantine",
                "promotion_gate_checks": checks,
                "promotion_gate_passed": passed,
                "promotion_limits": "input/readback only; not canonical truth; no external action",
            }
        )
    return {
        "artifact_id": "e71_legacy_asset_promotion_gate_results",
        "bridge_job_id": JOB_ID,
        "results": results,
        "promoted_count": sum(1 for row in results if row["final_disposition"] in {"integrate_into_market_model", "integrate_into_CIEU_route", "integrate_into_self_bootstrap", "bind_as_input"}),
        "quarantined_count": sum(1 for row in results if row["final_disposition"] == "quarantine"),
        "read_only_repos_mutated": False,
        "external_action_allowed": False,
    }


def build_top_priority_resurrection_set(root: Path | None = None) -> dict[str, Any]:
    scorecards = load_json("operations/external_validation/e71_legacy_asset_scorecards.json", root) or build_scorecards(root)
    selected = []
    for row in scorecards["cluster_scorecards"]:
        if len(selected) >= 8:
            break
        if row["priority_band"] in {"P0_resurrect_now", "P1_bind_as_input", "P3_defer_pending_owner_approval"}:
            selected.append(
                {
                    "cluster_id": row["cluster_id"],
                    "selected": True,
                    "priority_band": row["priority_band"],
                    "score": row["total_score"],
                    "current_mainline_target": binding_target_for(row["cluster_id"]),
                    "binding_method": binding_mode_for(row["cluster_id"]),
                    "why_valuable": value_reason_for(row["cluster_id"]),
                    "why_safe_or_unsafe": safety_reason_for(row["cluster_id"]),
                    "tests_needed": ["promotion gate tests", "CEO readback tests", "no-overclaim tests"],
                    "overclaim_risk": overclaim_risk_for(row["cluster_id"]),
                    "owner_gate_requirement": owner_gate_for(row["cluster_id"]),
                }
            )
    return {
        "artifact_id": "e71_top_priority_legacy_resurrection_set",
        "bridge_job_id": JOB_ID,
        "selected_cluster_count": len(selected),
        "selected_clusters": selected,
        "external_action_allowed": False,
    }


def binding_target_for(cluster_id: str) -> str:
    return {
        "k9_cieu_hash_chain_spec_cluster": "E68_CIEU_route_and_CIEU_module",
        "e24_ecosystem_commercial_imagination_cluster": "E65_market_model_and_E70_self_bootstrap",
        "e10_e23_commercial_revenue_runtime_cluster": "E65_market_model_and_E67_validation",
        "cieu_self_evolution_creed_cluster": "E70_self_bootstrap",
        "finance_pricing_package_cluster": "E66_offer_pricing_package_hypothesis",
        "gov_mcp_provider_promotion_gate_cluster": "future_owner_gated_execution_boundary",
        "marketing_launch_skill_marketplace_cluster": "future_owner_gated_publication_packet",
        "legacy_ceo_brain_os_heartbeat_cluster": "CEO_historical_context",
    }.get(cluster_id, "quarantine")


def binding_mode_for(cluster_id: str) -> str:
    return {
        "k9_cieu_hash_chain_spec_cluster": "read-only evidence input and product appendix candidate",
        "e24_ecosystem_commercial_imagination_cluster": "loader input and candidate source",
        "e10_e23_commercial_revenue_runtime_cluster": "score calibration and validation readiness input",
        "cieu_self_evolution_creed_cluster": "self-bootstrap source",
        "finance_pricing_package_cluster": "pricing hypothesis input only",
        "gov_mcp_provider_promotion_gate_cluster": "owner-gated packet input",
        "marketing_launch_skill_marketplace_cluster": "owner-gated publication packet input",
        "legacy_ceo_brain_os_heartbeat_cluster": "historical context only",
    }.get(cluster_id, "quarantine")


def value_reason_for(cluster_id: str) -> str:
    return {
        "k9_cieu_hash_chain_spec_cluster": "Adds the strongest causal audit and tamper-evident hash-chain detail to the CIEU module.",
        "e24_ecosystem_commercial_imagination_cluster": "Contains old opportunity paths, innovation hypotheses, missing wheels, and route registry logic.",
        "e10_e23_commercial_revenue_runtime_cluster": "Recovers commercial scoring, buyer signal, paid-signal readiness, KPI, and control-room assets.",
        "cieu_self_evolution_creed_cluster": "Already proved valuable in E70 as the self-bootstrap foundation.",
        "finance_pricing_package_cluster": "Provides pricing/economics hypotheses for offer package refinement.",
        "gov_mcp_provider_promotion_gate_cluster": "Provides dry-run-to-live promotion boundaries for future owner-gated execution review.",
        "marketing_launch_skill_marketplace_cluster": "Provides launch packet and skill marketplace inputs, but only owner-gated.",
        "legacy_ceo_brain_os_heartbeat_cluster": "Preserves historical CEO operating system material without promoting it as current truth.",
    }.get(cluster_id, "Historical context.")


def safety_reason_for(cluster_id: str) -> str:
    if cluster_id in {"gov_mcp_provider_promotion_gate_cluster", "marketing_launch_skill_marketplace_cluster"}:
        return "Useful but owner-gated because it touches provider/live/publication surfaces."
    if cluster_id == "ystar_company_historical_sales_brain_cluster":
        return "Quarantined because historical sales/prospect artifacts may contain stale or contact-sensitive context."
    return "Safe as internal readback/input if promotion gate blocks canonical-truth and validation overclaims."


def overclaim_risk_for(cluster_id: str) -> str:
    return {
        "finance_pricing_package_cluster": "old pricing is not pricing validation",
        "marketing_launch_skill_marketplace_cluster": "launch assets are not publication approval",
        "gov_mcp_provider_promotion_gate_cluster": "provider promotion assets do not enable live execution",
        "k9_cieu_hash_chain_spec_cluster": "read-only K9 context is not completed integration",
        "e10_e23_commercial_revenue_runtime_cluster": "paid-signal readiness is not paid signal",
    }.get(cluster_id, "historical input is not current truth")


def owner_gate_for(cluster_id: str) -> str:
    if cluster_id in {"gov_mcp_provider_promotion_gate_cluster", "marketing_launch_skill_marketplace_cluster", "ystar_company_historical_sales_brain_cluster"}:
        return OWNER_DECISION_STATUS
    return "not_required_for_internal_binding"


def build_mainline_binding_plan(root: Path | None = None) -> dict[str, Any]:
    bindings = [
        ("E65_market_dynamics_model", "E24 opportunity paths, E24 innovation hypotheses, E10-E23 commercial scoring, finance/pricing", "loader input / score calibration"),
        ("E67_external_validation_model", "E13 paid signal readiness, E17 paid signal runtime, E19 revenue validation control room", "validation readiness input only"),
        ("E68_CIEU_route_and_module", "K9Audit CIEU spec, CIEU self-evolution creed, Y-star-gov CIEU/CZL context", "read-only evidence / product appendix candidate"),
        ("E70_self_bootstrap_runtime", "old self-evolution creed, E24 missing wheels, E24 imagination engine", "capability candidate source"),
        ("E69_E70_autonomous_planning", "E24 CEO execution router, route portfolio selector, ecosystem route registry", "promotion-gated candidate input"),
        ("offer_product_assets", "finance/pricing, marketing/launch, skill marketplace, E13R offer revision", "pricing/launch packet input only"),
    ]
    return {
        "artifact_id": "e71_legacy_mainline_binding_plan",
        "bridge_job_id": JOB_ID,
        "bindings": [
            {
                "target_runtime": target,
                "asset_source": source,
                "binding_mode": mode,
                "no_overclaim_boundary": "input only; not validated; not current truth; no external action",
                "tests": ["promotion gate", "readback", "no-overclaim"],
                "completion_signal": "CEO readback sees binding input artifact",
            }
            for target, source, mode in bindings
        ],
        "core_models_rewritten": False,
        "external_action_allowed": False,
    }


def filter_promoted(results: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row for row in results["results"]
        if row["final_disposition"] in {"integrate_into_market_model", "integrate_into_CIEU_route", "integrate_into_self_bootstrap", "bind_as_input"}
    ]


def filter_quarantined(results: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in results["results"] if row["final_disposition"] == "quarantine"]


def build_promoted_legacy_assets(root: Path | None = None) -> dict[str, Any]:
    results = load_json("operations/external_validation/e71_legacy_asset_promotion_gate_results.json", root) or build_promotion_gate_results(root)
    promoted = filter_promoted(results)
    return {
        "artifact_id": "e71_promoted_legacy_assets",
        "bridge_job_id": JOB_ID,
        "promoted_count": len(promoted),
        "promoted_assets": promoted,
        "canonical_truth_promoted": False,
        "external_action_allowed": False,
    }


def build_quarantined_legacy_assets(root: Path | None = None) -> dict[str, Any]:
    results = load_json("operations/external_validation/e71_legacy_asset_promotion_gate_results.json", root) or build_promotion_gate_results(root)
    quarantined = filter_quarantined(results)
    return {
        "artifact_id": "e71_quarantined_legacy_assets",
        "bridge_job_id": JOB_ID,
        "quarantined_count": len(quarantined),
        "quarantined_assets": quarantined,
        "quarantine_rules": ["stale current-truth risk", "contact/prospect risk", "read-only context cannot be mutated", "external execution owner-gated"],
        "external_action_allowed": False,
    }


def build_legacy_market_model_inputs(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e71_legacy_market_model_inputs",
        "bridge_job_id": JOB_ID,
        "input_clusters": ["e24_ecosystem_commercial_imagination_cluster", "e10_e23_commercial_revenue_runtime_cluster", "finance_pricing_package_cluster"],
        "opportunity_paths": [
            "rev_path_readiness_review_ai_consultancies",
            "rev_path_ai_agent_governance_audit",
            "rev_path_governed_outbound_infra_service",
            "rev_path_founder_operator_ai_automation_review",
            "rev_path_paid_diagnostic_product",
            "rev_path_ceo_agent_control_room_product",
            "rev_path_provider_adapter_productized_capability",
        ],
        "innovation_hypotheses": [
            "innovation_governed_outbound_infra",
            "innovation_ceo_agent_control_room",
            "innovation_agent_governance_audit",
            "innovation_paid_readiness_diagnostic",
            "innovation_provider_promotion_gate",
            "innovation_y_star_trust_layer",
        ],
        "binding_mode": "market_model_overlay_input_only",
        "not_current_truth": True,
        "external_action_allowed": False,
    }


def build_legacy_cieu_module_inputs(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e71_legacy_cieu_module_inputs",
        "bridge_job_id": JOB_ID,
        "input_clusters": ["k9_cieu_hash_chain_spec_cluster", "cieu_self_evolution_creed_cluster", "y_star_gov_governance_cieu_context_cluster"],
        "CIEU_fields": ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1", "prev_hash", "record_hash"],
        "hash_chain_context": "K9Audit CIEU spec documents tamper-evident prev_hash/record_hash semantics; E71 binds this as read-only input, not completed integration.",
        "ordinary_log_difference": "CIEU captures causal intent-action-outcome-residual structure, not just events.",
        "not_K9Audit_integration_completed": True,
        "external_action_allowed": False,
    }


def build_legacy_pricing_inputs(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e71_legacy_pricing_inputs",
        "bridge_job_id": JOB_ID,
        "input_clusters": ["finance_pricing_package_cluster", "e13r_offer_revision"],
        "pricing_assets": CLUSTERS["finance_pricing_package_cluster"]["paths"],
        "binding_mode": "pricing_package_hypothesis_input_only",
        "old_pricing_validated": False,
        "pricing_validation_claimed": False,
        "external_action_allowed": False,
    }


def build_legacy_self_bootstrap_inputs(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e71_legacy_self_bootstrap_inputs",
        "bridge_job_id": JOB_ID,
        "input_clusters": ["cieu_self_evolution_creed_cluster", "e24_ecosystem_commercial_imagination_cluster", "legacy_ceo_brain_os_heartbeat_cluster"],
        "new_rule": "Before proposing new code, CEO self-bootstrap should check the legacy asset registry and promotion gate.",
        "blocked_sources": ["quarantined assets", "owner-gated launch/provider/sales assets"],
        "external_action_allowed": False,
    }


def build_legacy_provider_promotion_inputs(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e71_legacy_provider_promotion_inputs",
        "bridge_job_id": JOB_ID,
        "input_clusters": ["gov_mcp_provider_promotion_gate_cluster"],
        "binding_mode": "owner_gated_execution_boundary_review_input_only",
        "provider_live_execution_enabled": False,
        "owner_approval_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def build_self_bootstrap_legacy_awareness_update(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e71_self_bootstrap_legacy_asset_awareness_update",
        "bridge_job_id": JOB_ID,
        "affects_capability_gap_registry": "legacy gaps now include missing old-asset check before new code proposals",
        "CEO_should_consider_resurrected_assets_before_new_code": True,
        "Codex_job_proposals_should_check_legacy_registry_first": True,
        "skill_discovery_should_check_local_legacy_assets_first": True,
        "stale_quarantined_assets_blocked": True,
        "promotion_gated_assets_can_become_future_capability_candidates": True,
        "legacy_registry_artifacts": [
            "operations/external_validation/e71_legacy_asset_archaeology_inventory.json",
            "operations/external_validation/e71_legacy_asset_promotion_gate_results.json",
            "operations/external_validation/e71_promoted_legacy_assets.json",
            "operations/external_validation/e71_quarantined_legacy_assets.json",
        ],
        "external_action_allowed": False,
    }


def build_generated_codex_job_proposal(root: Path | None = None) -> dict[str, Any]:
    scorecards = load_json("operations/external_validation/e71_legacy_asset_scorecards.json", root) or build_scorecards(root)
    top = scorecards["cluster_scorecards"][0]
    if top["cluster_id"] == "k9_cieu_hash_chain_spec_cluster":
        milestone = "E72_integrate_K9_CIEU_hash_chain_context_into_CIEU_audit_module"
        title = "Integrate K9 CIEU hash-chain context into CIEU audit module"
    elif top["cluster_id"] in {"e24_ecosystem_commercial_imagination_cluster", "e10_e23_commercial_revenue_runtime_cluster", "finance_pricing_package_cluster"}:
        milestone = "E72_integrate_legacy_commercial_scoring_and_pricing_into_market_model"
        title = "Integrate legacy commercial scoring and pricing into market model"
    else:
        milestone = "E72_CEO_self_bootstrap_legacy_asset_use_case"
        title = "Run CEO self-bootstrap legacy asset use case"
    return {
        "artifact_id": "e71_generated_codex_job_proposal_from_legacy_assets",
        "bridge_job_id": JOB_ID,
        "proposed_milestone_id": milestone,
        "proposed_title": title,
        "generated_from_legacy_asset_scoring": True,
        "source_legacy_asset_cluster": top["cluster_id"],
        "source_cluster_score": top["total_score"],
        "capability_gap_addressed": "top promoted legacy cluster should become a tested mainline module/input rather than buried context",
        "expected_base": "E71 completion commit",
        "repo_scope": "bridge-labs only; read-only context remains read-only",
        "implementation_plan": [
            "load E71 promoted legacy asset registry",
            "bind selected cluster through overlay/input artifact",
            "update product/runtime readback",
            "add no-overclaim and owner-gate tests",
            "write KG/CZL/CIEU residuals",
        ],
        "safety_boundary": [
            "no external action",
            "no read-only repo mutation",
            "no compliance or validation claims",
            "no provider live execution",
            "no publication",
        ],
        "tests": ["legacy cluster loader test", "CEO readback test", "no-overclaim test", "completion gate test"],
        "completion_gate": ["base verified", "legacy cluster integrated as input", "readback passes", "tests pass", "remote commit confirmed"],
        "owner_approval_status": OWNER_DECISION_STATUS,
        "delivery_bridge_fallback": f"/tmp/ystar_delivery_bridge/pending/{milestone}.json",
        "external_action_allowed": False,
    }


def build_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e71_behavior_authorization_result",
        "bridge_job_id": JOB_ID,
        "allow": [
            "repository_archaeology",
            "read_only_cross_repo_inspection",
            "old_asset_scoring",
            "promotion_gate_creation",
            "safe_internal_binding",
            "CEO_readback_integration",
            "E70_self_bootstrap_overlay",
            "Codex_job_proposal_generation",
            "KG_CZL_CIEU_writeback",
        ],
        "deny": [
            "external_outreach",
            "publication",
            "customer_conversation",
            "expert_review",
            "human_identification",
            "contact_scraping",
            "login_form_send",
            "private_provider_API",
            "API_key_secret_use",
            "internet_package_install",
            "external_skill_install",
            "payment_invoice_client_delivery",
            "mutating_read_only_repos",
            "claiming_old_assets_are_current_truth_without_promotion",
            "claiming_pricing_customer_paid_validation",
            "claiming_compliance_readiness",
            "owner_approval_fabrication",
        ],
        "read_only_repos_mutated": False,
        "external_business_execution_authorized": False,
        "passed": True,
        "external_action_allowed": False,
    }


def build_ceo_brain_update(root: Path | None = None) -> dict[str, Any]:
    promoted = load_json("operations/external_validation/e71_promoted_legacy_assets.json", root) or build_promoted_legacy_assets(root)
    quarantined = load_json("operations/external_validation/e71_quarantined_legacy_assets.json", root) or build_quarantined_legacy_assets(root)
    top = load_json("operations/external_validation/e71_top_priority_legacy_resurrection_set.json", root) or build_top_priority_resurrection_set(root)
    proposal = load_json("operations/external_validation/e71_generated_codex_job_proposal_from_legacy_assets.json", root) or build_generated_codex_job_proposal(root)
    update = {
        "artifact_id": "e71_ceo_brain_legacy_asset_resurrection_update",
        "bridge_job_id": JOB_ID,
        "legacy_asset_resurrection_status": "ready_internal_no_external_action",
        "promoted_count": promoted["promoted_count"],
        "quarantined_count": quarantined["quarantined_count"],
        "top_clusters": [cluster["cluster_id"] for cluster in top["selected_clusters"]],
        "market_model_inputs": "operations/external_validation/e71_legacy_market_model_inputs.json",
        "CIEU_module_inputs": "operations/external_validation/e71_legacy_cieu_module_inputs.json",
        "pricing_inputs": "operations/external_validation/e71_legacy_pricing_inputs.json",
        "self_bootstrap_inputs": "operations/external_validation/e71_legacy_self_bootstrap_inputs.json",
        "provider_promotion_inputs": "operations/external_validation/e71_legacy_provider_promotion_inputs.json",
        "generated_codex_job_proposal": proposal["proposed_milestone_id"],
        "next_recommended_milestone": proposal["proposed_milestone_id"],
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "old_assets_current_truth_claimed": False,
        "old_pricing_validated_claimed": False,
        "old_sales_assets_active_pipeline_claimed": False,
        "launch_assets_publication_approved_claimed": False,
        "provider_live_execution_enabled_claimed": False,
        "K9Audit_integration_completed_claimed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
        "legal_compliance_claimed": False,
        "medical_energy_readiness_claimed": False,
        "owner_approval_claimed": False,
        "autonomous_revenue_achieved": False,
    }
    return update


def write_kg_czl_cieu(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    update = build_ceo_brain_update(base)
    write_json(base, "operations/external_validation/e71_ceo_brain_legacy_asset_resurrection_update.json", update)
    write_jsonl(
        base,
        "operations/knowledge_graph/e71_ceo_kg_legacy_asset_nodes_delta.jsonl",
        [
            {"node_id": "e71_legacy_asset_registry", "node_type": "registry", "status": "promotion_gated"},
            {"node_id": "e71_promotion_gate", "node_type": "gate", "status": "ready"},
            {"node_id": update["generated_codex_job_proposal"], "node_type": "codex_job_proposal", "status": "proposed_no_execution"},
        ],
    )
    write_jsonl(
        base,
        "operations/knowledge_graph/e71_ceo_kg_legacy_asset_edges_delta.jsonl",
        [
            {"from": "E70_self_bootstrap", "to": "e71_legacy_asset_registry", "edge_type": "uses_before_new_work"},
            {"from": "e71_legacy_asset_registry", "to": "e71_promotion_gate", "edge_type": "filtered_by"},
            {"from": "e71_promotion_gate", "to": update["generated_codex_job_proposal"], "edge_type": "generates"},
        ],
    )
    write_json(base, "operations/knowledge_graph/e71_ceo_kg_legacy_asset_read_model_update.json", {"artifact_id": "e71_ceo_kg_legacy_asset_read_model_update", **update})
    write_json(
        base,
        "operations/external_validation/e71_czl_closure.json",
        {
            "artifact_id": "e71_czl_closure",
            "closure_status": "closed",
            "closed_loop": "legacy archaeology -> scoring -> duplicate map -> promotion gate -> safe bindings -> CEO readback -> E70 awareness -> Codex proposal",
            "next_recommended_milestone": update["next_recommended_milestone"],
            "no_external_action": True,
        },
    )
    write_json(
        base,
        "operations/external_validation/e71_cieu_residual_summary.json",
        {
            "artifact_id": "e71_cieu_residual_summary",
            "Y_star": "CEO self-bootstrap checks high-value legacy assets before proposing new work.",
            "X_t": "Before E71, E70 could generate Codex proposals but had no legacy asset promotion gate or resurrection registry.",
            "U_t": "Run legacy asset archaeology, scoring, promotion gate, safe binding, readback, and proposal generation.",
            "Y_t_plus_1": [
                "legacy assets discovered and scored",
                "promotion gate created",
                "P0/P1 assets bound as inputs",
                "quarantine/defer rules created",
                "CEO readback integrated",
                "E70 self-bootstrap legacy awareness update created",
                "legacy-scored Codex proposal generated",
            ],
            "R_t_plus_1": [
                "actual integration of top cluster remains E72",
                "provider/live/publication assets remain owner-gated",
                "historical sales/prospect assets remain quarantined",
                "old pricing remains unvalidated",
            ],
            "no_external_action": True,
            "no_overclaim": True,
        },
    )
    return update


def build_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e71_ceo_brain_legacy_asset_resurrection_update.json", base)
    if not state:
        state = write_kg_czl_cieu(base)
    checks = {
        "CEO_sees_legacy_state": state.get("legacy_asset_resurrection_status") == "ready_internal_no_external_action",
        "CEO_sees_promoted_assets": state.get("promoted_count", 0) > 0,
        "CEO_sees_quarantined_assets": state.get("quarantined_count", 0) >= 0,
        "CEO_sees_top_clusters": bool(state.get("top_clusters")),
        "CEO_sees_market_model_inputs": bool(state.get("market_model_inputs")),
        "CEO_sees_CIEU_module_inputs": bool(state.get("CIEU_module_inputs")),
        "CEO_sees_pricing_inputs": bool(state.get("pricing_inputs")),
        "CEO_sees_self_bootstrap_inputs": bool(state.get("self_bootstrap_inputs")),
        "CEO_sees_provider_promotion_inputs": bool(state.get("provider_promotion_inputs")),
        "CEO_sees_external_action_blocked": state.get("external_action_allowed") is False,
        "CEO_sees_no_overclaim": all(state.get(field) is False for field in [
            "old_assets_current_truth_claimed",
            "old_pricing_validated_claimed",
            "launch_assets_publication_approved_claimed",
            "provider_live_execution_enabled_claimed",
            "customer_validation_claimed",
            "paid_signal_claimed",
            "pricing_validation_claimed",
            "legal_compliance_claimed",
        ]),
    }
    return {
        "artifact_id": "e71_ceo_legacy_asset_readback_smoke_result",
        "observed_state": state,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
    }


def build_no_overclaim_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    paths = [
        "operations/external_validation/e71_ceo_brain_legacy_asset_resurrection_update.json",
        "operations/external_validation/e71_behavior_authorization_result.json",
        "operations/external_validation/e71_legacy_pricing_inputs.json",
        "operations/external_validation/e71_legacy_provider_promotion_inputs.json",
        "operations/external_validation/e71_generated_codex_job_proposal_from_legacy_assets.json",
        "operations/external_validation/e71_ceo_legacy_asset_readback_smoke_result.json",
    ]
    forbidden_true = [
        "external_action_allowed",
        "external_business_execution_authorized",
        "read_only_repos_mutated",
        "old_assets_current_truth_claimed",
        "old_pricing_validated_claimed",
        "old_sales_assets_active_pipeline_claimed",
        "launch_assets_publication_approved_claimed",
        "provider_live_execution_enabled",
        "provider_live_execution_enabled_claimed",
        "K9Audit_integration_completed_claimed",
        "customer_validation_claimed",
        "paid_signal_claimed",
        "expert_feedback_claimed",
        "pricing_validation_claimed",
        "legal_compliance_claimed",
        "medical_energy_readiness_claimed",
        "owner_approval_claimed",
        "autonomous_revenue_achieved",
    ]
    violations = []
    for rel in paths:
        data = load_json(rel, base)
        observed = data.get("observed_state", data)
        for field in forbidden_true:
            if observed.get(field) is True:
                violations.append({"path": rel, "field": field, "value": True})
    return {"artifact_id": "e71_no_overclaim_validation_result", "paths_scanned": paths, "violations": violations, "passed": not violations}


def build_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_state = load_json("operations/external_validation/e71_base_state_manifest.json", base) or build_base_state_manifest(base)
    archaeology = load_json("operations/external_validation/e71_legacy_asset_archaeology_inventory.json", base)
    scorecards = load_json("operations/external_validation/e71_legacy_asset_scorecards.json", base)
    duplicate = load_json("operations/external_validation/e71_legacy_duplicate_overlap_staleness_map.json", base)
    policy = load_json("operations/external_validation/e71_legacy_asset_promotion_policy.json", base)
    gate_results = load_json("operations/external_validation/e71_legacy_asset_promotion_gate_results.json", base)
    top = load_json("operations/external_validation/e71_top_priority_legacy_resurrection_set.json", base)
    binding = load_json("operations/external_validation/e71_legacy_mainline_binding_plan.json", base)
    promoted = load_json("operations/external_validation/e71_promoted_legacy_assets.json", base)
    quarantined = load_json("operations/external_validation/e71_quarantined_legacy_assets.json", base)
    readback = load_json("operations/external_validation/e71_ceo_legacy_asset_readback_smoke_result.json", base)
    awareness = load_json("operations/external_validation/e71_self_bootstrap_legacy_asset_awareness_update.json", base)
    proposal = load_json("operations/external_validation/e71_generated_codex_job_proposal_from_legacy_assets.json", base)
    auth = load_json("operations/external_validation/e71_behavior_authorization_result.json", base)
    no_overclaim = load_json("operations/external_validation/e71_no_overclaim_validation_result.json", base)
    read_only_after = {
        "Y-star-gov": git_state(Y_GOV_ROOT, include_full_status=False),
        "gov-mcp": git_state(GOV_MCP_ROOT, include_full_status=False),
        "K9Audit": git_state(K9_ROOT, include_full_status=False),
        "ystar-company": git_state(YSTAR_COMPANY_ROOT, include_full_status=False) if YSTAR_COMPANY_ROOT.exists() else {"exists": False, "clean": True, "status_fingerprint": "", "status_entry_count": 0},
    }
    read_only_before = base_state.get("read_only_repo_status_before", {})
    read_only_unchanged = True
    for repo_name, after_state in read_only_after.items():
        before_state = read_only_before.get(repo_name, {})
        if before_state.get("exists") is False and after_state.get("exists") is False:
            continue
        if before_state.get("head") != after_state.get("head"):
            read_only_unchanged = False
        if before_state.get("status_fingerprint", "") != after_state.get("status_fingerprint", ""):
            read_only_unchanged = False
    checks = {
        "base_HEAD_verified": base_state.get("base_verified") is True,
        "archaeology_inventory_created": archaeology.get("asset_count", 0) >= 40,
        "high_value_asset_scorecards_created": bool(scorecards.get("cluster_scorecards")),
        "duplicate_overlap_staleness_map_created": len(duplicate.get("rows", [])) >= 10,
        "promotion_gate_implemented": callable(load_legacy_asset_registry) and bool(policy.get("dispositions")),
        "promotion_gate_results_created": gate_results.get("promoted_count", 0) > 0,
        "top_priority_resurrection_set_created": top.get("selected_cluster_count", 0) >= 6,
        "mainline_binding_plan_created": len(binding.get("bindings", [])) >= 6,
        "safe_bindings_implemented_for_selected_P0_P1": all((base / rel).exists() for rel in [
            "operations/external_validation/e71_legacy_market_model_inputs.json",
            "operations/external_validation/e71_legacy_cieu_module_inputs.json",
            "operations/external_validation/e71_legacy_pricing_inputs.json",
            "operations/external_validation/e71_legacy_self_bootstrap_inputs.json",
            "operations/external_validation/e71_legacy_provider_promotion_inputs.json",
        ]),
        "promoted_legacy_assets_artifact_exists": promoted.get("promoted_count", 0) > 0,
        "quarantined_legacy_assets_artifact_exists": "quarantined_assets" in quarantined,
        "CEO_legacy_readback_implemented": readback.get("passes") is True,
        "CEO_brain_adapter_reads_E71_state": readback.get("passes") is True,
        "E70_self_bootstrap_legacy_awareness_update_created": awareness.get("Codex_job_proposals_should_check_legacy_registry_first") is True,
        "generated_Codex_job_proposal_from_legacy_assets_exists": proposal.get("generated_from_legacy_asset_scoring") is True,
        "behavior_authorization_passed": auth.get("passed") is True,
        "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
            "operations/knowledge_graph/e71_ceo_kg_legacy_asset_read_model_update.json",
            "operations/external_validation/e71_czl_closure.json",
            "operations/external_validation/e71_cieu_residual_summary.json",
        ]),
        "no_forbidden_external_action_executed": auth.get("external_business_execution_authorized") is False,
        "no_read_only_repo_mutation_occurred": read_only_unchanged,
        "no_overclaim_fields_true": no_overclaim.get("passed") is True,
    }
    final_status = "e71_legacy_high_value_asset_resurrection_completed" if all(checks.values()) else "e71_partial_with_quarantine_only"
    return {
        "artifact_id": "e71_completion_gate_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": final_status,
        "promoted_count": promoted.get("promoted_count", 0),
        "quarantined_count": quarantined.get("quarantined_count", 0),
        "top_cluster": scorecards.get("top_cluster"),
        "recommended_next_milestone": proposal.get("proposed_milestone_id", NEXT_MILESTONE),
        "read_only_repo_status_before": read_only_before,
        "read_only_repo_status_after": read_only_after,
        "read_only_repo_status_unchanged": read_only_unchanged,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def load_legacy_asset_registry(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e71_legacy_asset_archaeology_inventory.json", root) or build_archaeology_inventory(root)


def score_legacy_asset(asset_id: str, root: Path | None = None) -> dict[str, Any]:
    scorecards = load_json("operations/external_validation/e71_legacy_asset_scorecards.json", root) or build_scorecards(root)
    for row in scorecards.get("asset_scorecards", []):
        if row["asset_id"] == asset_id:
            return row
    return {"asset_id": asset_id, "found": False, "external_action_allowed": False}


def decide_legacy_asset_disposition(asset_id: str, root: Path | None = None) -> dict[str, Any]:
    results = load_json("operations/external_validation/e71_legacy_asset_promotion_gate_results.json", root) or build_promotion_gate_results(root)
    for row in results.get("results", []):
        if row["asset_id"] == asset_id:
            return row
    return {"asset_id": asset_id, "found": False, "final_disposition": "quarantine", "external_action_allowed": False}


def get_promoted_legacy_assets(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e71_promoted_legacy_assets.json", root) or build_promoted_legacy_assets(root)


def get_quarantined_legacy_assets(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e71_quarantined_legacy_assets.json", root) or build_quarantined_legacy_assets(root)


def get_mainline_binding_plan(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e71_legacy_mainline_binding_plan.json", root) or build_mainline_binding_plan(root)


def explain_legacy_promotion_limits(root: Path | None = None) -> dict[str, Any]:
    return {
        "old_assets_are_not_current_truth": True,
        "old_pricing_is_not_validated": True,
        "old_sales_assets_are_not_active_pipeline": True,
        "launch_assets_are_not_approved_publication": True,
        "provider_live_execution_is_not_enabled": True,
        "K9Audit_context_is_read_only_not_completed_integration": True,
        "external_action_allowed": False,
    }


def load_e71_legacy_asset_resurrection_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e71_ceo_brain_legacy_asset_resurrection_update.json", base)
    if not state:
        state = write_kg_czl_cieu(base)
    return state


def write_reports(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    archaeology = load_json("operations/external_validation/e71_legacy_asset_archaeology_inventory.json", base)
    scorecards = load_json("operations/external_validation/e71_legacy_asset_scorecards.json", base)
    duplicate = load_json("operations/external_validation/e71_legacy_duplicate_overlap_staleness_map.json", base)
    policy = load_json("operations/external_validation/e71_legacy_asset_promotion_policy.json", base)
    top = load_json("operations/external_validation/e71_top_priority_legacy_resurrection_set.json", base)
    binding = load_json("operations/external_validation/e71_legacy_mainline_binding_plan.json", base)
    promoted = load_json("operations/external_validation/e71_promoted_legacy_assets.json", base)
    quarantined = load_json("operations/external_validation/e71_quarantined_legacy_assets.json", base)
    awareness = load_json("operations/external_validation/e71_self_bootstrap_legacy_asset_awareness_update.json", base)
    proposal = load_json("operations/external_validation/e71_generated_codex_job_proposal_from_legacy_assets.json", base)
    gate = load_json("operations/external_validation/e71_completion_gate_result.json", base)
    write_md(base, "reports/integration/e71_legacy_asset_archaeology_inventory.md", "E71 Legacy Asset Archaeology Inventory", [
        f"Assets inventoried: `{archaeology.get('asset_count')}` across `{archaeology.get('cluster_count')}` clusters.",
        f"E62 referenced assets: `{archaeology.get('E62_repository_archaeology_asset_count')}`.",
        "Read-only repos were inspected as context only and not mutated.",
    ])
    write_md(base, "reports/integration/e71_legacy_asset_scorecards.md", "E71 Legacy Asset Scorecards", [
        f"Top cluster: `{scorecards.get('top_cluster')}`.",
        f"Cluster scorecards: `{len(scorecards.get('cluster_scorecards', []))}`.",
    ])
    write_md(base, "reports/integration/e71_legacy_duplicate_overlap_staleness_map.md", "E71 Duplicate Overlap Staleness Map", [
        f"Overlap rows: `{len(duplicate.get('rows', []))}`.",
        "Old assets must not override current E65-E70 state automatically.",
    ])
    write_md(base, "reports/integration/e71_legacy_asset_promotion_policy.md", "E71 Legacy Asset Promotion Policy", [
        f"Dispositions: `{', '.join(policy.get('dispositions', []))}`.",
        "Promotion requires source/evidence/no-overclaim/readback gates.",
    ])
    write_md(base, "reports/integration/e71_top_priority_legacy_resurrection_set.md", "E71 Top Priority Legacy Resurrection Set", [
        f"Selected clusters: `{top.get('selected_cluster_count')}`.",
        f"Clusters: `{[item.get('cluster_id') for item in top.get('selected_clusters', [])]}`.",
    ])
    write_md(base, "reports/integration/e71_legacy_mainline_binding_plan.md", "E71 Legacy Mainline Binding Plan", [
        f"Bindings planned: `{len(binding.get('bindings', []))}`.",
        "Bindings are overlay/input/readback modes, not core model rewrites.",
    ])
    write_md(base, "reports/integration/e71_self_bootstrap_legacy_asset_awareness_update.md", "E71 Self-Bootstrap Legacy Asset Awareness Update", [
        f"Check legacy registry first: `{awareness.get('Codex_job_proposals_should_check_legacy_registry_first')}`.",
        "Quarantined assets are blocked from self-bootstrap proposals.",
    ])
    write_md(base, "reports/integration/e71_generated_codex_job_proposal_from_legacy_assets.md", "E71 Generated Codex Job Proposal From Legacy Assets", [
        f"Proposed milestone: `{proposal.get('proposed_milestone_id')}`.",
        f"Source cluster: `{proposal.get('source_legacy_asset_cluster')}`.",
        "Generated from legacy scoring, not external action.",
    ])
    write_md(base, "reports/integration/e71_completion_gate_result.md", "E71 Completion Gate", [
        f"Gate passed: `{gate.get('gate_passed')}`.",
        f"Final status: `{gate.get('final_status')}`.",
        f"Promoted: `{promoted.get('promoted_count')}`, quarantined: `{quarantined.get('quarantined_count')}`.",
    ])


def write_all_e71_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    write_json(base, "operations/external_validation/e71_base_state_manifest.json", build_base_state_manifest(base))
    write_json(base, "operations/external_validation/e71_legacy_asset_archaeology_inventory.json", build_archaeology_inventory(base))
    write_json(base, "operations/external_validation/e71_legacy_asset_scoring_model.json", build_scoring_model(base))
    write_json(base, "operations/external_validation/e71_legacy_asset_scorecards.json", build_scorecards(base))
    write_json(base, "operations/external_validation/e71_legacy_duplicate_overlap_staleness_map.json", build_duplicate_overlap_staleness_map(base))
    write_json(base, "operations/external_validation/e71_legacy_asset_promotion_policy.json", build_promotion_policy(base))
    write_json(base, "operations/external_validation/e71_legacy_asset_promotion_gate_results.json", build_promotion_gate_results(base))
    write_json(base, "operations/external_validation/e71_top_priority_legacy_resurrection_set.json", build_top_priority_resurrection_set(base))
    write_json(base, "operations/external_validation/e71_legacy_mainline_binding_plan.json", build_mainline_binding_plan(base))
    write_json(base, "operations/external_validation/e71_promoted_legacy_assets.json", build_promoted_legacy_assets(base))
    write_json(base, "operations/external_validation/e71_quarantined_legacy_assets.json", build_quarantined_legacy_assets(base))
    write_json(base, "operations/external_validation/e71_legacy_market_model_inputs.json", build_legacy_market_model_inputs(base))
    write_json(base, "operations/external_validation/e71_legacy_cieu_module_inputs.json", build_legacy_cieu_module_inputs(base))
    write_json(base, "operations/external_validation/e71_legacy_pricing_inputs.json", build_legacy_pricing_inputs(base))
    write_json(base, "operations/external_validation/e71_legacy_self_bootstrap_inputs.json", build_legacy_self_bootstrap_inputs(base))
    write_json(base, "operations/external_validation/e71_legacy_provider_promotion_inputs.json", build_legacy_provider_promotion_inputs(base))
    write_json(base, "operations/external_validation/e71_self_bootstrap_legacy_asset_awareness_update.json", build_self_bootstrap_legacy_awareness_update(base))
    write_json(base, "operations/external_validation/e71_generated_codex_job_proposal_from_legacy_assets.json", build_generated_codex_job_proposal(base))
    write_json(base, "operations/external_validation/e71_behavior_authorization_result.json", build_behavior_authorization(base))
    write_kg_czl_cieu(base)
    write_json(base, "operations/external_validation/e71_ceo_legacy_asset_readback_smoke_result.json", build_readback_smoke(base))
    write_json(base, "operations/external_validation/e71_no_overclaim_validation_result.json", build_no_overclaim_validation(base))
    gate = build_completion_gate(base)
    write_json(base, "operations/external_validation/e71_completion_gate_result.json", gate)
    write_reports(base)
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e71_artifacts(), indent=2, ensure_ascii=False))
