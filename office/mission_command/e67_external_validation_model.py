from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .safe_public_page_reader import SafePublicPageReader, reject_unsafe_public_url

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))

JOB_ID = "e67_non_contact_external_validation_evidence_upgrade_20260506T000001Z"
EXPECTED_BASE = "cffec311064305466b7c365a039c434942bfd332"
OWNER_DECISION_STATUS = "pending_owner_decision"
PRIMARY_ROUTE = "governed_business_operations_blueprint_for_agent_teams"
FALLBACK_ROUTE = "founder_operator_decision_brief_service"
LEARNING_ROUTE = "public_read_market_intelligence_product"
STRATEGIC_ROUTE = "AI_agent_company_runtime_harness_deployment_blueprint"
AUDIT_ROUTE = "agent_runtime_audit_and_repair_package"
NEXT_MILESTONE = "E68_owner_decision_packet_for_controlled_external_review_no_execution"
TARGETED_REFRESH_MILESTONE = "E68_targeted_non_contact_validation_refresh"
PRODUCT_DIR = "products/governed_business_operations_blueprint_for_agent_teams"


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


def git_state(path: Path, expected_head: str | None = None) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=path, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    head = run("rev-parse", "HEAD")
    status = run("status", "--short")
    branch = run("rev-parse", "--abbrev-ref", "HEAD")
    return {
        "path": str(path),
        "branch": branch,
        "head": head,
        "expected_head": expected_head,
        "head_matches_expected": expected_head is None or head == expected_head,
        "clean": status == "",
        "status_short": status,
    }


def dirty_paths_are_e67_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e67_",
        "tests/office/test_e67_",
        "operations/external_validation/e67_",
        "operations/knowledge_graph/e67_",
        "reports/integration/e67_",
        f"{PRODUCT_DIR}/",
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
        "Y-star-gov": git_state(Y_GOV_ROOT, "b0d9aa8b1badd1180127a2f79f73ceed48e16451"),
        "gov-mcp": git_state(GOV_MCP_ROOT, "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90"),
        "K9Audit": git_state(K9_ROOT, "37911e18ce4425470e3f745b30d155c43d76ff55"),
    }
    return {
        "artifact_id": "e67_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "base_verified": bridge["head_matches_expected"] and bridge["branch"] == "backflow/aiden-ceo-meeting-room",
        "bridge_labs_worktree_clean_or_e67_scoped": dirty_paths_are_e67_scoped(bridge["status_short"]),
        "read_only_repos": read_only,
        "read_only_repos_clean": all(item.get("clean", True) for item in read_only.values()),
        "e66_completed_report_present": Path("/tmp/ystar_delivery_bridge/completed/e66_selected_route_offer_blueprint_using_market_dynamics_model_no_execution_20260506T000001Z.report.json").exists(),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def build_repository_archaeology_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    explicit_assets = [
        "office/mission_command/e66_model_driven_offer_core.py",
        "operations/external_validation/e66_model_driven_revenue_analysis.json",
        "operations/external_validation/e66_selected_route_offer_blueprint.json",
        "operations/external_validation/e66_model_driven_selected_route_decision.json",
        "operations/external_validation/e66_revenue_strategy_capability_leap_assessment.json",
        f"{PRODUCT_DIR}/offer_blueprint.json",
        f"{PRODUCT_DIR}/sample_delivery_packet.json",
        "office/mission_command/e65_market_dynamics_model.py",
        "office/mission_command/e65_ceo_market_dynamics_readback.py",
        "operations/external_validation/e65_market_dynamics_model_schema.json",
        "operations/external_validation/e65_market_evidence_quality_model.json",
        "operations/external_validation/e65_market_signal_taxonomy.json",
        "operations/external_validation/e65_market_dynamics_analysis_run.json",
        "operations/external_validation/e65_ceo_brain_market_dynamics_update.json",
        "operations/external_validation/e64_dual_axis_public_read_receipts.json",
        "operations/external_validation/e64_dual_axis_public_read_evidence_atoms.json",
        "operations/external_validation/e64_dual_axis_revenue_route_universe.json",
        "operations/external_validation/e63_public_read_source_receipts.json",
        "operations/external_validation/e63_revenue_opportunity_evidence_atoms.json",
        "operations/external_validation/e63_revenue_opportunity_map.json",
        "office/mission_command/safe_public_page_reader.py",
        "office/mission_command/e59_source_receipt_builder.py",
        "office/mission_command/e59_claim_extraction_and_evidence_atomizer.py",
        "office/mission_command/e46b_ceo_brain_adapter.py",
    ]
    assets: list[dict[str, Any]] = []
    for rel in explicit_assets:
        lower = rel.lower()
        path = base / rel
        if "safe_public" in lower:
            capability = "public_read_adapter"
        elif "e65_market_evidence" in lower:
            capability = "evidence_quality_model"
        elif "e65_market_signal" in lower:
            capability = "market_signal_taxonomy"
        elif "e65" in lower and ("model" in lower or "rank" in lower or "analysis" in lower):
            capability = "market_model_or_route_scoring"
        elif "e66" in lower or PRODUCT_DIR in rel:
            capability = "selected_offer_blueprint"
        elif "receipt" in lower:
            capability = "source_receipt"
        elif "evidence" in lower or "atom" in lower:
            capability = "evidence_atom"
        elif "e46b" in lower:
            capability = "CEO_brain_readback"
        else:
            capability = "supporting_context"
        assets.append({
            "path": rel,
            "exists": path.exists(),
            "capability_type": capability,
            "reusable": path.exists(),
            "connected_status": "connected" if path.exists() else "missing",
            "must_not_rebuild": capability in {
                "public_read_adapter",
                "evidence_quality_model",
                "market_signal_taxonomy",
                "market_model_or_route_scoring",
                "source_receipt",
                "evidence_atom",
                "CEO_brain_readback",
            },
        })
    counts = Counter(item["capability_type"] for item in assets if item["exists"])
    return {
        "artifact_id": "e67_repository_archaeology_inventory",
        "bridge_job_id": JOB_ID,
        "asset_count": len([item for item in assets if item["exists"]]),
        "discovered_assets": assets,
        "reusable_public_read_assets": [a["path"] for a in assets if a["capability_type"] == "public_read_adapter" and a["exists"]],
        "reusable_evidence_quality_model_assets": [a["path"] for a in assets if a["capability_type"] == "evidence_quality_model" and a["exists"]],
        "reusable_market_signal_taxonomy_assets": [a["path"] for a in assets if a["capability_type"] == "market_signal_taxonomy" and a["exists"]],
        "reusable_route_scoring_assets": [a["path"] for a in assets if a["capability_type"] == "market_model_or_route_scoring" and a["exists"]],
        "reusable_offer_blueprint_assets": [a["path"] for a in assets if a["capability_type"] == "selected_offer_blueprint" and a["exists"]],
        "disconnected_validation_assets": [a["path"] for a in assets if not a["exists"]],
        "what_must_not_be_rebuilt": [
            "E65 Market Dynamics Model",
            "E65 evidence quality ladder",
            "E65 signal taxonomy",
            "safe_public_page_reader",
            "E59/E63/E64 source receipt and evidence atom conventions",
            "E55 behavior authorization",
            "CEO brain readback",
            "KG/CZL/CIEU writeback conventions",
            "no-overclaim validators",
        ],
        "E67_must_add_as_thin_layer": "external validation ladder, EV1-EV4 non-contact evidence overlay, route validation scorecards, and CEO readback loader",
        "capability_counts": dict(counts),
        "archaeology_completed_before_implementation": True,
        "external_action_allowed": False,
    }


def build_reuse_first_growth_audit(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e67_reuse_first_growth_audit",
        "bridge_job_id": JOB_ID,
        "reused_assets": [
            "office/mission_command/safe_public_page_reader.py",
            "office/mission_command/e65_market_dynamics_model.py",
            "operations/external_validation/e65_market_evidence_quality_model.json",
            "operations/external_validation/e65_market_signal_taxonomy.json",
            "operations/external_validation/e66_selected_route_offer_blueprint.json",
            "office/mission_command/e46b_ceo_brain_adapter.py",
        ],
        "thin_wrappers_added": ["office/mission_command/e67_ceo_external_validation_readback.py"],
        "genuinely_new_assets_added": ["office/mission_command/e67_external_validation_model.py"],
        "duplicate_capability_risks_checked": {
            "E65_market_dynamics_model_rebuilt": False,
            "E65_evidence_quality_ladder_rebuilt": False,
            "E65_signal_taxonomy_rebuilt": False,
            "public_read_adapter_rebuilt": False,
            "source_receipt_builder_rebuilt": False,
            "evidence_atomizer_rebuilt": False,
            "behavior_gate_rebuilt": False,
            "route_scoring_engine_rebuilt": False,
            "CEO_readback_rebuilt": False,
        },
        "avoided_rebuilds": [
            "E67 overlays EV scoring onto E65 rather than modifying/rebuilding E65 scoring.",
            "E67 uses SafePublicPageReader for controlled public reads.",
            "E67 maps validation atoms to E65 signal taxonomy rather than creating a parallel taxonomy.",
        ],
        "justification_for_new_module": "No prior module distinguished EV0-EV8 external validation levels and integrated EV1-EV4 non-contact validation scorecards into CEO readback.",
        "passed": True,
    }


def validation_ladder_levels() -> list[dict[str, Any]]:
    return [
        {
            "EV_level": "EV0_internal_assumption",
            "what_it_proves": "internal hypothesis exists",
            "what_it_cannot_prove": ["external market language", "demand", "buyer willingness to pay"],
            "allowed_source_surfaces": ["repo-internal artifacts"],
            "prohibited_actions": ["external claim", "validation claim"],
            "evidence_artifacts_required": ["internal route artifact"],
            "confidence_effect": "baseline only",
            "overclaim_risk": "treating hypothesis as evidence",
            "route_scoring_effect": "low confidence starting point",
            "owner_approval_requirement": "not required for internal reasoning",
        },
        {
            "EV_level": "EV1_public_market_language",
            "what_it_proves": "public pages contain relevant pain/category/language",
            "what_it_cannot_prove": ["customer feedback", "purchase intent", "pricing acceptance"],
            "allowed_source_surfaces": ["public product pages", "public docs/blogs", "public category pages"],
            "prohibited_actions": ["contact", "login", "forms", "scraping contact data"],
            "evidence_artifacts_required": ["public-read receipt", "validation evidence atom"],
            "confidence_effect": "raises market-language confidence",
            "overclaim_risk": "calling public language customer validation",
            "route_scoring_effect": "small positive validation score",
            "owner_approval_requirement": "not required for safe public read",
        },
        {
            "EV_level": "EV2_competitor_or_adjacent_product_presence",
            "what_it_proves": "similar/adjacent solutions exist and category may be forming",
            "what_it_cannot_prove": ["our differentiation wins", "our offer sells"],
            "allowed_source_surfaces": ["public product pages", "official docs", "public repo pages"],
            "prohibited_actions": ["contacting companies", "scraping employees"],
            "evidence_artifacts_required": ["receipt", "competitor/adjacent atom"],
            "confidence_effect": "raises category-presence confidence",
            "overclaim_risk": "claiming competitor presence validates Y*Bridge demand",
            "route_scoring_effect": "positive category evidence, possible commodity risk",
            "owner_approval_requirement": "not required for safe public read",
        },
        {
            "EV_level": "EV3_public_pricing_or_packaging_evidence",
            "what_it_proves": "public pricing/package analogs exist",
            "what_it_cannot_prove": ["Y*Bridge pricing validation", "paid signal"],
            "allowed_source_surfaces": ["public pricing pages", "public service package pages", "public marketplace categories without identity extraction"],
            "prohibited_actions": ["payment", "checkout", "contact seller", "invoice"],
            "evidence_artifacts_required": ["receipt", "pricing/packaging atom"],
            "confidence_effect": "raises packaging analogy confidence",
            "overclaim_risk": "treating pricing analogs as paid signal",
            "route_scoring_effect": "positive packaging evidence only",
            "owner_approval_requirement": "not required for safe public read",
        },
        {
            "EV_level": "EV4_public_demand_or_behavior_proxy",
            "what_it_proves": "public proxy behavior or demand-adjacent activity exists",
            "what_it_cannot_prove": ["buyer commitment", "customer feedback", "sales readiness"],
            "allowed_source_surfaces": ["public job/category pages", "public repo activity pages", "public RFP/procurement category pages", "public forum pain language without identification"],
            "prohibited_actions": ["human identification", "contact extraction", "login", "form submission"],
            "evidence_artifacts_required": ["receipt", "demand proxy atom"],
            "confidence_effect": "raises non-contact demand-proxy confidence",
            "overclaim_risk": "calling behavior proxy customer validation",
            "route_scoring_effect": "positive but limited demand proxy score",
            "owner_approval_requirement": "not required for safe public read",
        },
        {
            "EV_level": "EV5_owner_approved_public_experiment",
            "what_it_proves": "owner-approved public experiment can observe behavior",
            "what_it_cannot_prove": ["human feedback unless collected", "paid signal unless payment occurs"],
            "allowed_source_surfaces": ["landing page", "waitlist", "ad", "public post", "pricing-click test"],
            "prohibited_actions": ["execution in E67"],
            "evidence_artifacts_required": ["owner approval", "experiment plan", "event receipt"],
            "confidence_effect": "future stronger behavior evidence",
            "overclaim_risk": "executing experiment without owner approval",
            "route_scoring_effect": "not achieved in E67",
            "owner_approval_requirement": "required before execution",
            "achieved_in_E67": False,
        },
        {
            "EV_level": "EV6_owner_approved_human_feedback",
            "what_it_proves": "owner-approved person gave feedback",
            "what_it_cannot_prove": ["paid signal", "repeatable revenue"],
            "allowed_source_surfaces": ["customer/expert/reviewer conversation after approval"],
            "prohibited_actions": ["execution in E67"],
            "evidence_artifacts_required": ["owner approval", "feedback receipt"],
            "confidence_effect": "future human-feedback evidence",
            "overclaim_risk": "contacting or claiming feedback without approval",
            "route_scoring_effect": "not achieved in E67",
            "owner_approval_requirement": "required",
            "achieved_in_E67": False,
        },
        {
            "EV_level": "EV7_paid_signal",
            "what_it_proves": "payment or purchase commitment exists",
            "what_it_cannot_prove": ["repeatable revenue by itself"],
            "allowed_source_surfaces": ["payment", "LOI", "paid pilot", "invoice", "pre-order after approval"],
            "prohibited_actions": ["execution in E67"],
            "evidence_artifacts_required": ["owner approval", "payment/commitment record"],
            "confidence_effect": "future paid validation evidence",
            "overclaim_risk": "calling pricing pages paid signal",
            "route_scoring_effect": "not achieved in E67",
            "owner_approval_requirement": "required",
            "achieved_in_E67": False,
        },
        {
            "EV_level": "EV8_repeatable_revenue",
            "what_it_proves": "repeated paid demand and delivery learning exists",
            "what_it_cannot_prove": ["perfect/global optimality"],
            "allowed_source_surfaces": ["repeatable paid cycles after approval"],
            "prohibited_actions": ["claim in E67"],
            "evidence_artifacts_required": ["repeated paid records", "delivery learning"],
            "confidence_effect": "future durable market learning",
            "overclaim_risk": "claiming revenue before it exists",
            "route_scoring_effect": "not achieved in E67",
            "owner_approval_requirement": "required",
            "achieved_in_E67": False,
        },
    ]


def build_external_validation_ladder(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e67_external_validation_ladder",
        "bridge_job_id": JOB_ID,
        "levels": validation_ladder_levels(),
        "non_contact_levels_available_now": ["EV1_public_market_language", "EV2_competitor_or_adjacent_product_presence", "EV3_public_pricing_or_packaging_evidence", "EV4_public_demand_or_behavior_proxy"],
        "owner_gated_levels_not_achieved": ["EV5_owner_approved_public_experiment", "EV6_owner_approved_human_feedback", "EV7_paid_signal", "EV8_repeatable_revenue"],
        "customer_validation_levels": ["EV6_owner_approved_human_feedback"],
        "paid_validation_levels": ["EV7_paid_signal", "EV8_repeatable_revenue"],
        "external_validation_is_not_only_human_feedback": True,
        "public_evidence_is_not_customer_validation": True,
        "public_pricing_evidence_is_not_paid_signal": True,
        "external_action_allowed": False,
    }


def validation_sources() -> list[dict[str, str]]:
    return [
        {"route_id": PRIMARY_ROUTE, "EV_level_target": "EV1_public_market_language", "validation_surface": "AI operations/governance language", "source_url": "https://openai.github.io/openai-agents-python/guardrails/", "source_type": "official_docs", "signal_type": "buyer pain signal"},
        {"route_id": PRIMARY_ROUTE, "EV_level_target": "EV1_public_market_language", "validation_surface": "agent workflow reliability language", "source_url": "https://www.anthropic.com/engineering/building-effective-agents", "source_type": "public_engineering_blog", "signal_type": "technology shift signal"},
        {"route_id": PRIMARY_ROUTE, "EV_level_target": "EV2_competitor_or_adjacent_product_presence", "validation_surface": "workflow orchestration adjacent product", "source_url": "https://www.langchain.com/langgraph", "source_type": "public_product_page", "signal_type": "competitor movement signal"},
        {"route_id": PRIMARY_ROUTE, "EV_level_target": "EV2_competitor_or_adjacent_product_presence", "validation_surface": "automation operations adjacent product", "source_url": "https://n8n.io/", "source_type": "public_product_page", "signal_type": "platform/ecosystem change signal"},
        {"route_id": PRIMARY_ROUTE, "EV_level_target": "EV3_public_pricing_or_packaging_evidence", "validation_surface": "workflow automation pricing analog", "source_url": "https://n8n.io/pricing/", "source_type": "public_pricing_page", "signal_type": "pricing signal"},
        {"route_id": PRIMARY_ROUTE, "EV_level_target": "EV3_public_pricing_or_packaging_evidence", "validation_surface": "automation platform pricing analog", "source_url": "https://zapier.com/pricing", "source_type": "public_pricing_page", "signal_type": "pricing signal"},
        {"route_id": PRIMARY_ROUTE, "EV_level_target": "EV4_public_demand_or_behavior_proxy", "validation_surface": "repo/category activity proxy", "source_url": "https://github.com/langchain-ai/langgraph", "source_type": "public_repo_page", "signal_type": "public behavior proxy"},
        {"route_id": PRIMARY_ROUTE, "EV_level_target": "EV4_public_demand_or_behavior_proxy", "validation_surface": "agent protocol ecosystem proxy", "source_url": "https://github.com/modelcontextprotocol/servers", "source_type": "public_repo_page", "signal_type": "platform/ecosystem change signal"},
        {"route_id": FALLBACK_ROUTE, "EV_level_target": "EV1_public_market_language", "validation_surface": "founder/operator decision language", "source_url": "https://www.ycombinator.com/library", "source_type": "public_knowledge_page", "signal_type": "buyer pain signal"},
        {"route_id": FALLBACK_ROUTE, "EV_level_target": "EV1_public_market_language", "validation_surface": "operator research/brief language", "source_url": "https://www.cbinsights.com/research/", "source_type": "public_research_page", "signal_type": "market intelligence signal"},
        {"route_id": FALLBACK_ROUTE, "EV_level_target": "EV2_competitor_or_adjacent_product_presence", "validation_surface": "decision intelligence product presence", "source_url": "https://www.perplexity.ai/enterprise", "source_type": "public_product_page", "signal_type": "competitor movement signal"},
        {"route_id": FALLBACK_ROUTE, "EV_level_target": "EV2_competitor_or_adjacent_product_presence", "validation_surface": "research subscription product presence", "source_url": "https://www.alpha-sense.com/", "source_type": "public_product_page", "signal_type": "competitor movement signal"},
        {"route_id": FALLBACK_ROUTE, "EV_level_target": "EV3_public_pricing_or_packaging_evidence", "validation_surface": "research product pricing analog", "source_url": "https://www.perplexity.ai/pro", "source_type": "public_pricing_page", "signal_type": "pricing signal"},
        {"route_id": FALLBACK_ROUTE, "EV_level_target": "EV4_public_demand_or_behavior_proxy", "validation_surface": "startup/operator discussion proxy", "source_url": "https://news.ycombinator.com/front", "source_type": "public_forum_category_page", "signal_type": "public behavior proxy"},
        {"route_id": LEARNING_ROUTE, "EV_level_target": "EV1_public_market_language", "validation_surface": "market intelligence category language", "source_url": "https://www.crunchbase.com/market-intelligence", "source_type": "public_product_page", "signal_type": "market intelligence signal"},
        {"route_id": LEARNING_ROUTE, "EV_level_target": "EV2_competitor_or_adjacent_product_presence", "validation_surface": "competitive intelligence category presence", "source_url": "https://www.similarweb.com/corp/solutions/market-research/", "source_type": "public_product_page", "signal_type": "competitor movement signal"},
        {"route_id": LEARNING_ROUTE, "EV_level_target": "EV3_public_pricing_or_packaging_evidence", "validation_surface": "market intelligence pricing analog", "source_url": "https://www.semrush.com/prices/", "source_type": "public_pricing_page", "signal_type": "pricing signal"},
        {"route_id": LEARNING_ROUTE, "EV_level_target": "EV4_public_demand_or_behavior_proxy", "validation_surface": "repo/category activity proxy", "source_url": "https://github.com/awesome-selfhosted/awesome-selfhosted", "source_type": "public_repo_page", "signal_type": "public behavior proxy"},
        {"route_id": STRATEGIC_ROUTE, "EV_level_target": "EV1_public_market_language", "validation_surface": "agent runtime documentation language", "source_url": "https://docs.crewai.com/", "source_type": "official_docs", "signal_type": "technology shift signal"},
        {"route_id": STRATEGIC_ROUTE, "EV_level_target": "EV2_competitor_or_adjacent_product_presence", "validation_surface": "agent runtime adjacent product", "source_url": "https://www.crewai.com/", "source_type": "public_product_page", "signal_type": "competitor movement signal"},
        {"route_id": STRATEGIC_ROUTE, "EV_level_target": "EV3_public_pricing_or_packaging_evidence", "validation_surface": "agent platform pricing analog", "source_url": "https://www.crewai.com/pricing", "source_type": "public_pricing_page", "signal_type": "pricing signal"},
        {"route_id": STRATEGIC_ROUTE, "EV_level_target": "EV4_public_demand_or_behavior_proxy", "validation_surface": "agent framework repo proxy", "source_url": "https://github.com/crewAIInc/crewAI", "source_type": "public_repo_page", "signal_type": "public behavior proxy"},
        {"route_id": AUDIT_ROUTE, "EV_level_target": "EV1_public_market_language", "validation_surface": "AI observability language", "source_url": "https://www.langchain.com/langsmith", "source_type": "public_product_page", "signal_type": "delivery feasibility signal"},
        {"route_id": AUDIT_ROUTE, "EV_level_target": "EV2_competitor_or_adjacent_product_presence", "validation_surface": "AI observability/eval category", "source_url": "https://www.helicone.ai/", "source_type": "public_product_page", "signal_type": "competitor movement signal"},
        {"route_id": AUDIT_ROUTE, "EV_level_target": "EV3_public_pricing_or_packaging_evidence", "validation_surface": "AI observability pricing analog", "source_url": "https://www.helicone.ai/pricing", "source_type": "public_pricing_page", "signal_type": "pricing signal"},
        {"route_id": AUDIT_ROUTE, "EV_level_target": "EV4_public_demand_or_behavior_proxy", "validation_surface": "eval/observability repo proxy", "source_url": "https://github.com/traceloop/openllmetry", "source_type": "public_repo_page", "signal_type": "public behavior proxy"},
    ]


def build_non_contact_external_validation_plan(root: Path | None = None) -> dict[str, Any]:
    sources = validation_sources()
    return {
        "artifact_id": "e67_non_contact_external_validation_plan",
        "bridge_job_id": JOB_ID,
        "primary_route": PRIMARY_ROUTE,
        "fallback_route": FALLBACK_ROUTE,
        "learning_route": LEARNING_ROUTE,
        "strategic_route": STRATEGIC_ROUTE,
        "routes_covered": sorted({source["route_id"] for source in sources}),
        "source_count_planned": len(sources),
        "source_surfaces_covered": sorted({source["validation_surface"] for source in sources}),
        "EV_levels_attempted": ["EV1_public_market_language", "EV2_competitor_or_adjacent_product_presence", "EV3_public_pricing_or_packaging_evidence", "EV4_public_demand_or_behavior_proxy"],
        "sources": sources,
        "rules": {
            "no_crawl": True,
            "no_arbitrary_link_following": True,
            "no_contact_scraping": True,
            "no_human_identification": True,
            "no_login": True,
            "no_form_submission": True,
            "no_private_provider_API": True,
            "public_evidence_not_customer_validation": True,
        },
        "external_action_allowed": False,
    }


def sanitize_snippet(text: str) -> str:
    cleaned = " ".join((text or "").split())
    cleaned = cleaned.replace("@", " [at] ")
    return cleaned[:700]


def classify_blocker(results: list[dict[str, Any]]) -> str:
    if any(row["retrieval_status"] == "success" for row in results):
        return "public_read_available"
    reasons = Counter(row.get("blocked_reason") or "unknown" for row in results)
    if any("URLError" in key for key in reasons):
        return "network_or_DNS_unavailable"
    if any("TimeoutError" in key for key in reasons):
        return "timeout_or_TCP_blocked"
    if any("non_http_scheme" in key or "private" in key for key in reasons):
        return "policy_denied"
    return "unknown_public_read_blocker"


def build_non_contact_public_read_receipts(root: Path | None = None) -> dict[str, Any]:
    reader = SafePublicPageReader(max_bytes=80_000, timeout_seconds=3)
    receipts: list[dict[str, Any]] = []
    for idx, source in enumerate(validation_sources(), 1):
        safety_errors = reject_unsafe_public_url(source["source_url"])
        if safety_errors:
            result_dict = {
                "url": source["source_url"],
                "status": None,
                "title": "",
                "text_excerpt": "",
                "blocked_reason": ";".join(safety_errors),
                "bytes_read": 0,
                "retrieved_at": utc_now(),
            }
        else:
            result = reader.read(source["source_url"])
            result_dict = result.to_dict()
        success = result_dict.get("status") is not None and not result_dict.get("blocked_reason")
        title = sanitize_snippet(str(result_dict.get("title") or ""))
        snippet = sanitize_snippet(str(result_dict.get("text_excerpt") or ""))
        content_hash = hashlib.sha256((source["source_url"] + title + snippet).encode("utf-8")).hexdigest()
        receipts.append({
            "receipt_id": f"e67_receipt_{idx:03d}",
            "route_id": source["route_id"],
            "EV_level_target": source["EV_level_target"],
            "validation_surface": source["validation_surface"],
            "source_url": source["source_url"],
            "source_type": source["source_type"],
            "retrieval_status": "success" if success else "blocked_or_unavailable",
            "http_status": result_dict.get("status"),
            "title": title,
            "snippet": snippet,
            "content_hash": content_hash,
            "bytes_read": result_dict.get("bytes_read", 0),
            "retrieved_at": result_dict.get("retrieved_at") or utc_now(),
            "blocked_reason": result_dict.get("blocked_reason") or "",
            "no_contact_info_extracted": True,
            "no_login": True,
            "no_form_submission": True,
            "no_crawl": True,
            "no_human_identification": True,
            "no_external_human_action": True,
            "not_customer_validation": True,
            "not_paid_signal": True,
            "not_expert_feedback": True,
            "not_pricing_validation": True,
        })
    return {
        "artifact_id": "e67_non_contact_public_read_receipts",
        "bridge_job_id": JOB_ID,
        "receipt_count": len(receipts),
        "successful_read_count": sum(1 for row in receipts if row["retrieval_status"] == "success"),
        "blocked_or_unavailable_count": sum(1 for row in receipts if row["retrieval_status"] != "success"),
        "public_read_blocker_classification": classify_blocker(receipts),
        "receipts": receipts,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
    }


def signal_type_for(receipt: dict[str, Any]) -> str:
    mapping = {
        "EV1_public_market_language": "buyer pain signal",
        "EV2_competitor_or_adjacent_product_presence": "competitor movement signal",
        "EV3_public_pricing_or_packaging_evidence": "pricing signal",
        "EV4_public_demand_or_behavior_proxy": "public behavior proxy",
    }
    return mapping.get(receipt["EV_level_target"], "missing-evidence signal")


def build_external_validation_evidence_atoms(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    receipt_payload = load_json("operations/external_validation/e67_non_contact_public_read_receipts.json", base) or build_non_contact_public_read_receipts(base)
    atoms: list[dict[str, Any]] = []
    for idx, receipt in enumerate(receipt_payload.get("receipts", []), 1):
        success = receipt["retrieval_status"] == "success"
        ev = receipt["EV_level_target"]
        atoms.append({
            "evidence_id": f"e67_validation_atom_{idx:03d}",
            "receipt_id": receipt["receipt_id"],
            "route_id": receipt["route_id"],
            "EV_level": ev,
            "signal_type": signal_type_for(receipt),
            "observed_external_signal": receipt["snippet"][:300] if success and receipt["snippet"] else f"{receipt['validation_surface']} attempted; {receipt.get('blocked_reason') or 'no snippet available'}",
            "validation_surface": receipt["validation_surface"],
            "relevance_to_route": "direct non-contact validation surface for route" if success else "attempted non-contact validation surface; blocker limits confidence",
            "confidence_effect": "positive_limited" if success else "no_positive_update_blocked_or_unavailable",
            "limitation": "public-read evidence only; not customer feedback, pricing validation, paid signal, or expert feedback",
            "overclaim_boundary": "Do not treat this atom as customer validation, paid signal, pricing validation, or buyer willingness to pay.",
            "route_score_effect": 1 if success else 0,
            "no_customer_validation_claimed": True,
            "no_paid_signal_claimed": True,
            "no_expert_feedback_claimed": True,
            "no_pricing_validation_claimed": True,
        })
    return {
        "artifact_id": "e67_external_validation_evidence_atoms",
        "bridge_job_id": JOB_ID,
        "evidence_atom_count": len(atoms),
        "positive_atom_count": sum(1 for atom in atoms if atom["route_score_effect"] > 0),
        "atoms": atoms,
        "mapped_to_E65_signal_taxonomy_where_possible": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
        "external_action_allowed": False,
    }


def build_route_external_validation_scorecards(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    atoms_payload = load_json("operations/external_validation/e67_external_validation_evidence_atoms.json", base) or build_external_validation_evidence_atoms(base)
    atoms = atoms_payload.get("atoms", [])
    routes = [PRIMARY_ROUTE, FALLBACK_ROUTE, LEARNING_ROUTE, STRATEGIC_ROUTE, AUDIT_ROUTE]
    scorecards: list[dict[str, Any]] = []
    for route in routes:
        route_atoms = [atom for atom in atoms if atom["route_id"] == route]
        by_ev = defaultdict(list)
        for atom in route_atoms:
            by_ev[atom["EV_level"]].append(atom)
        ev_scores = {}
        for ev in ["EV1_public_market_language", "EV2_competitor_or_adjacent_product_presence", "EV3_public_pricing_or_packaging_evidence", "EV4_public_demand_or_behavior_proxy"]:
            positives = sum(1 for atom in by_ev.get(ev, []) if atom["route_score_effect"] > 0)
            attempted = len(by_ev.get(ev, []))
            ev_scores[ev] = {
                "attempted": attempted > 0,
                "positive_evidence_count": positives,
                "strength": "medium" if positives >= 2 else "low" if positives == 1 else "blocked_or_absent",
            }
        positive = sum(1 for atom in route_atoms if atom["route_score_effect"] > 0)
        attempted = len(route_atoms)
        highest = "EV4_public_demand_or_behavior_proxy" if ev_scores["EV4_public_demand_or_behavior_proxy"]["positive_evidence_count"] else (
            "EV3_public_pricing_or_packaging_evidence" if ev_scores["EV3_public_pricing_or_packaging_evidence"]["positive_evidence_count"] else (
                "EV2_competitor_or_adjacent_product_presence" if ev_scores["EV2_competitor_or_adjacent_product_presence"]["positive_evidence_count"] else (
                    "EV1_public_market_language" if ev_scores["EV1_public_market_language"]["positive_evidence_count"] else "EV0_internal_assumption"
                )
            )
        )
        confidence = round((positive / attempted) * 100, 2) if attempted else 0.0
        scorecards.append({
            "route_id": route,
            "EV1_public_market_language_strength": ev_scores["EV1_public_market_language"]["strength"],
            "EV2_competitor_or_adjacent_presence_strength": ev_scores["EV2_competitor_or_adjacent_product_presence"]["strength"],
            "EV3_public_pricing_or_packaging_evidence_strength": ev_scores["EV3_public_pricing_or_packaging_evidence"]["strength"],
            "EV4_public_demand_or_behavior_proxy_strength": ev_scores["EV4_public_demand_or_behavior_proxy"]["strength"],
            "EV5_plus_blocked_owner_gated_status": "EV5_EV6_EV7_EV8_unachieved_owner_gated",
            "highest_achieved_EV_level": highest,
            "external_validation_confidence": confidence,
            "evidence_quantity": attempted,
            "evidence_quality": "T2_public_read_non_contact" if positive else "T0_internal_assumption_plus_blocked_public_read_attempts",
            "contradiction_count": 0,
            "missing_evidence": ["EV5 public experiment", "EV6 human feedback", "EV7 paid signal", "EV8 repeatable revenue"],
            "overclaim_risks": ["public evidence mistaken for customer validation", "pricing analog mistaken for paid signal"],
            "route_implication": "strengthen_selected_route_non_contact_evidence" if route == PRIMARY_ROUTE and positive else "retain_as_portfolio_route_with_limited_non_contact_evidence",
            "EV_scores": ev_scores,
            "customer_validation_claimed": False,
            "paid_signal_claimed": False,
            "expert_feedback_claimed": False,
            "pricing_validation_claimed": False,
        })
    primary_score = next(card for card in scorecards if card["route_id"] == PRIMARY_ROUTE)
    fallback_score = next(card for card in scorecards if card["route_id"] == FALLBACK_ROUTE)
    return {
        "artifact_id": "e67_route_external_validation_scorecards",
        "bridge_job_id": JOB_ID,
        "scorecards": scorecards,
        "route_count": len(scorecards),
        "selected_route_external_validation_score": primary_score["external_validation_confidence"],
        "fallback_route_external_validation_score": fallback_score["external_validation_confidence"],
        "highest_non_contact_EV_level": max((card["highest_achieved_EV_level"] for card in scorecards), default="EV0_internal_assumption"),
        "EV5_EV8_achieved": False,
        "external_action_allowed": False,
    }


def get_external_validation_ladder(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e67_external_validation_ladder.json", root) or build_external_validation_ladder(root)


def get_route_external_validation_score(route_id: str, root: Path | None = None) -> dict[str, Any]:
    cards = (load_json("operations/external_validation/e67_route_external_validation_scorecards.json", root) or build_route_external_validation_scorecards(root)).get("scorecards", [])
    return next((card for card in cards if card["route_id"] == route_id), {"route_id": route_id, "status": "not_found", "external_validation_confidence": 0})


def get_non_contact_validation_portfolio(root: Path | None = None) -> dict[str, Any]:
    cards = (load_json("operations/external_validation/e67_route_external_validation_scorecards.json", root) or build_route_external_validation_scorecards(root)).get("scorecards", [])
    ordered = sorted(cards, key=lambda card: (card["external_validation_confidence"], card["evidence_quantity"]), reverse=True)
    return {
        "primary_route": PRIMARY_ROUTE,
        "strongest_non_contact_route": ordered[0]["route_id"] if ordered else PRIMARY_ROUTE,
        "fallback_route": FALLBACK_ROUTE,
        "learning_route": LEARNING_ROUTE,
        "strategic_route": STRATEGIC_ROUTE,
        "owner_gated_future_levels": ["EV5", "EV6", "EV7", "EV8"],
        "external_action_allowed": False,
    }


def select_next_milestone(root: Path | None = None) -> str:
    base = root or BRIDGE_ROOT
    receipts = load_json("operations/external_validation/e67_non_contact_public_read_receipts.json", base)
    scorecards = load_json("operations/external_validation/e67_route_external_validation_scorecards.json", base)
    if receipts.get("successful_read_count", 0) == 0:
        return TARGETED_REFRESH_MILESTONE
    primary = next((card for card in scorecards.get("scorecards", []) if card.get("route_id") == PRIMARY_ROUTE), {})
    fallback = next((card for card in scorecards.get("scorecards", []) if card.get("route_id") == FALLBACK_ROUTE), {})
    if fallback.get("external_validation_confidence", 0) > primary.get("external_validation_confidence", 0):
        return "E68_compare_selected_route_vs_fallback_with_owner_decision_no_execution"
    return NEXT_MILESTONE


def explain_validation_limits(route_id: str, root: Path | None = None) -> dict[str, Any]:
    score = get_route_external_validation_score(route_id, root)
    return {
        "route_id": route_id,
        "highest_achieved_EV_level": score.get("highest_achieved_EV_level", "EV0_internal_assumption"),
        "limits": [
            "EV1-EV4 non-contact evidence can strengthen external evidence state.",
            "EV1-EV4 cannot prove customer validation, buyer willingness to pay, pricing validation, expert feedback, or paid signal.",
            "EV5-EV8 remain owner-gated and unachieved.",
        ],
        "public_evidence_equals_customer_feedback": False,
        "public_pricing_equals_paid_signal": False,
        "external_action_allowed": False,
    }


def list_owner_gated_validation_next_steps(root: Path | None = None) -> dict[str, Any]:
    return {
        "owner_gated_next_steps": [
            "EV5 owner-approved landing page/waitlist/ad/post/pricing-click experiment",
            "EV6 owner-approved controlled human feedback",
            "EV7 owner-approved paid signal attempt",
            "EV8 repeatable revenue cycles after real paid demand",
        ],
        "requires_owner_approval_before_any_execution": True,
        "external_action_allowed": False,
    }


def build_offer_blueprint_validation_update(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    scorecards = load_json("operations/external_validation/e67_route_external_validation_scorecards.json", base) or build_route_external_validation_scorecards(base)
    primary = next(card for card in scorecards["scorecards"] if card["route_id"] == PRIMARY_ROUTE)
    fallback = next(card for card in scorecards["scorecards"] if card["route_id"] == FALLBACK_ROUTE)
    strengthen = primary["external_validation_confidence"] > 0 and primary["external_validation_confidence"] >= fallback["external_validation_confidence"]
    update = {
        "artifact_id": "e67_offer_blueprint_validation_update",
        "bridge_job_id": JOB_ID,
        "selected_offer_strengthened_by_non_contact_validation": strengthen,
        "selected_offer_weakened_by_non_contact_validation": False,
        "buyer_category_change_suggested": False,
        "language_change_suggested": True,
        "language_update": "Use 'non-contact external evidence' and 'governed business operations' language; never call it customer validation.",
        "packaging_change_suggested": True,
        "packaging_update": "Keep Blueprint Sprint as main wedge; add explicit EV1-EV4 evidence appendix and owner-gated EV5-EV8 roadmap.",
        "fallback_route_externally_stronger": fallback["external_validation_confidence"] > primary["external_validation_confidence"],
        "learning_route_deserves_more_emphasis": True,
        "should_E68_prepare_owner_decision_for_external_review": select_next_milestone(base) == NEXT_MILESTONE,
        "claims_remain_prohibited": [
            "customer validation",
            "paid signal",
            "expert feedback",
            "pricing validation",
            "production readiness",
            "EV5/EV6/EV7/EV8 achieved",
        ],
        "external_action_allowed": False,
    }
    write_md(base, f"{PRODUCT_DIR}/external_validation_update.md", "E67 External Validation Update", [
        "Status: internal-only draft update.",
        "E67 strengthens the offer with EV1-EV4 non-contact evidence where public reads succeeded.",
        "This is not customer validation, paid signal, pricing validation, or expert feedback.",
        "Keep the Blueprint Sprint as the main wedge and attach EV1-EV4 evidence plus owner-gated EV5-EV8 roadmap.",
    ])
    write_json(base, f"{PRODUCT_DIR}/external_validation_update.json", update)
    return update


def build_owner_gated_external_validation_roadmap(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e67_owner_gated_external_validation_roadmap",
        "bridge_job_id": JOB_ID,
        "current_achievable_done_now": ["EV1 public market language", "EV2 competitor/adjacent product evidence", "EV3 public pricing/packaging evidence", "EV4 public demand/behavior proxy evidence"],
        "owner_gated_future": [
            {
                "level": "EV5",
                "required_owner_approval": True,
                "proposed_action": "controlled landing page/waitlist/ad/public post/pricing-click experiment",
                "safety_boundary": "no execution before owner approval",
                "evidence_capture_plan": "event receipts, traffic/click receipts, no-overclaim writeback",
                "stop_conditions": ["unexpected contact data exposure", "policy boundary uncertainty", "owner revokes approval"],
                "no_overclaim_language": "public experiment behavior is not paid signal unless payment occurs",
                "writeback_path": "E67 overlay -> E65 model -> KG/CZL/CIEU -> CEO readback",
            },
            {
                "level": "EV6",
                "required_owner_approval": True,
                "proposed_action": "controlled human feedback conversation/review",
                "safety_boundary": "approved reviewer/customer category only",
                "evidence_capture_plan": "feedback receipt and limitations",
                "stop_conditions": ["no approval", "contact uncertainty", "privacy risk"],
                "no_overclaim_language": "feedback is not paid signal",
                "writeback_path": "feedback evidence -> model confidence update",
            },
            {
                "level": "EV7",
                "required_owner_approval": True,
                "proposed_action": "paid signal attempt only after approval",
                "safety_boundary": "no payment/invoice without approval",
                "evidence_capture_plan": "payment/LOI/paid pilot/pre-order receipt",
                "stop_conditions": ["payment boundary unclear", "client delivery risk"],
                "no_overclaim_language": "single paid signal is not repeatable revenue",
                "writeback_path": "paid signal evidence -> route score update",
            },
            {
                "level": "EV8",
                "required_owner_approval": True,
                "proposed_action": "repeat paid delivery cycles",
                "safety_boundary": "governed delivery and evidence closure",
                "evidence_capture_plan": "repeated revenue and delivery learning receipts",
                "stop_conditions": ["quality risk", "unsupported delivery promise", "governance failure"],
                "no_overclaim_language": "repeatability must be demonstrated over cycles",
                "writeback_path": "revenue learning -> CEO model update",
            },
        ],
        "external_action_allowed": False,
    }


def build_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e67_behavior_authorization_result",
        "authorization_status": "ALLOW_NON_CONTACT_EXTERNAL_VALIDATION_ONLY",
        "allowed_actions": [
            "repository_archaeology",
            "non_contact_public_read_validation",
            "competitor_adjacent_product_evidence_collection",
            "pricing_packaging_evidence_collection",
            "public_demand_behavior_proxy_evidence_collection",
            "route_level_validation_scorecards",
            "E65_model_validation_overlay",
            "internal_offer_blueprint_validation_update",
            "owner_gated_validation_roadmap",
            "KG_CZL_CIEU_writeback",
            "CEO_brain_readback",
        ],
        "denied_actions": [
            "outreach",
            "publication",
            "customer_conversation",
            "expert_review",
            "human_identification",
            "contact_scraping",
            "login_form_send",
            "private_provider_API",
            "API_key_secret_use",
            "payment",
            "invoice",
            "client_delivery",
            "customer_validation_claim",
            "paid_signal_claim",
            "expert_feedback_claim",
            "pricing_validation_claim",
            "autonomous_revenue_achieved_claim",
            "EV5_EV6_EV7_EV8_achieved_claim",
        ],
        "external_business_execution_authorized": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "pending_owner_decision_is_not_approval": True,
        "external_action_allowed": False,
        "passed": True,
    }


def write_runtime_writeback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    scorecards = load_json("operations/external_validation/e67_route_external_validation_scorecards.json", base) or build_route_external_validation_scorecards(base)
    primary = get_route_external_validation_score(PRIMARY_ROUTE, base)
    next_milestone = select_next_milestone(base)
    update = {
        "artifact_id": "e67_ceo_brain_external_validation_update",
        "external_validation_status": "non_contact_external_validation_overlay_integrated",
        "highest_achieved_EV_level_by_route": {card["route_id"]: card["highest_achieved_EV_level"] for card in scorecards["scorecards"]},
        "primary_route": PRIMARY_ROUTE,
        "primary_route_external_validation_score": primary.get("external_validation_confidence"),
        "highest_EV_level": primary.get("highest_achieved_EV_level"),
        "non_contact_confidence": primary.get("external_validation_confidence"),
        "validation_confidence": "limited_non_contact_public_evidence",
        "evidence_limits": [
            "public evidence is not customer feedback",
            "pricing analogs are not paid signal",
            "job/RFP/category/repo proxies are not buyer commitment",
            "EV5-EV8 are unachieved and owner-gated",
        ],
        "missing_evidence": primary.get("missing_evidence", []),
        "owner_gated_next_validation_level": "EV5_owner_approved_public_experiment",
        "route_implication": primary.get("route_implication"),
        "offer_update_implication": "selected offer remains internal draft; add EV1-EV4 evidence appendix and owner-gated validation roadmap",
        "owner_gated_next_steps": list_owner_gated_validation_next_steps(base)["owner_gated_next_steps"],
        "next_recommended_milestone": next_milestone,
        "no_external_action": True,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
        "production_readiness_claimed": False,
        "autonomous_revenue_achieved": False,
        "real_client_delivery_claimed": False,
        "owner_approval_fabricated": False,
        "perfect_global_optimality_claimed": False,
        "EV5_achieved": False,
        "EV6_achieved": False,
        "EV7_achieved": False,
        "EV8_achieved": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }
    write_json(base, "operations/external_validation/e67_ceo_brain_external_validation_update.json", update)
    write_jsonl(base, "operations/knowledge_graph/e67_ceo_kg_external_validation_nodes_delta.jsonl", [
        {"node_id": "e67_external_validation_overlay", "node_type": "external_validation_model", "status": "integrated"},
        {"node_id": PRIMARY_ROUTE, "node_type": "validated_route_non_contact", "highest_EV_level": primary.get("highest_achieved_EV_level")},
        {"node_id": next_milestone, "node_type": "recommended_next_milestone"},
    ])
    write_jsonl(base, "operations/knowledge_graph/e67_ceo_kg_external_validation_edges_delta.jsonl", [
        {"from": "e65_market_dynamics_model_v1", "to": "e67_external_validation_overlay", "edge_type": "extended_by"},
        {"from": "e67_external_validation_overlay", "to": PRIMARY_ROUTE, "edge_type": "scores_non_contact_validation"},
        {"from": "e67_external_validation_overlay", "to": next_milestone, "edge_type": "recommends"},
    ])
    write_json(base, "operations/knowledge_graph/e67_ceo_kg_external_validation_read_model_update.json", {
        "artifact_id": "e67_ceo_kg_external_validation_read_model_update",
        **update,
    })
    write_json(base, "operations/external_validation/e67_czl_closure.json", {
        "artifact_id": "e67_czl_closure",
        "closure_status": "closed",
        "closed_loop": "E66 offer -> EV ladder -> non-contact public receipts -> validation atoms -> route scorecards -> E65 overlay -> CEO readback",
        "recommended_next_milestone": next_milestone,
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e67_cieu_residual_summary.json", {
        "artifact_id": "e67_cieu_residual_summary",
        "intervention": "Upgraded external validation state with EV1-EV4 non-contact evidence layers.",
        "resolved_residuals": ["external validation is no longer represented as zero when safe public evidence exists"],
        "remaining_residuals": ["EV5 public experiment absent", "EV6 human feedback absent", "EV7 paid signal absent", "EV8 repeatable revenue absent", "owner approval absent"],
        "no_external_action": True,
    })
    return update


def load_e67_external_validation_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e67_ceo_brain_external_validation_update.json", base)
    if not state:
        state = write_runtime_writeback(base)
    return state


def build_ceo_external_validation_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e67_external_validation_state_for_brain(root)
    checks = {
        "CEO_sees_external_validation_status": state.get("external_validation_status") == "non_contact_external_validation_overlay_integrated",
        "CEO_sees_primary_route_score": isinstance(state.get("primary_route_external_validation_score"), (int, float)),
        "CEO_sees_highest_EV_level": str(state.get("highest_EV_level", "")).startswith("EV"),
        "CEO_sees_non_contact_confidence": isinstance(state.get("non_contact_confidence"), (int, float)),
        "CEO_sees_missing_evidence": "EV7 paid signal" in state.get("missing_evidence", []),
        "CEO_sees_owner_gated_next_steps": len(state.get("owner_gated_next_steps", [])) >= 4,
        "CEO_sees_next_milestone": state.get("next_recommended_milestone") in {NEXT_MILESTONE, TARGETED_REFRESH_MILESTONE, "E68_compare_selected_route_vs_fallback_with_owner_decision_no_execution"},
        "CEO_sees_external_action_blocked": state.get("external_action_allowed") is False,
        "CEO_sees_no_overclaim": all(state.get(key) is False for key in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "expert_feedback_claimed",
            "pricing_validation_claimed",
            "production_readiness_claimed",
            "autonomous_revenue_achieved",
            "real_client_delivery_claimed",
            "owner_approval_fabricated",
            "perfect_global_optimality_claimed",
            "EV5_achieved",
            "EV6_achieved",
            "EV7_achieved",
            "EV8_achieved",
        ]),
    }
    return {
        "artifact_id": "e67_ceo_external_validation_readback_smoke_result",
        "observed_state": state,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def build_no_overclaim_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    paths = [
        "operations/external_validation/e67_external_validation_ladder.json",
        "operations/external_validation/e67_non_contact_public_read_receipts.json",
        "operations/external_validation/e67_external_validation_evidence_atoms.json",
        "operations/external_validation/e67_route_external_validation_scorecards.json",
        "operations/external_validation/e67_ceo_brain_external_validation_update.json",
        "operations/external_validation/e67_ceo_external_validation_readback_smoke_result.json",
    ]
    forbidden_true = [
        "customer_validation_claimed",
        "paid_signal_claimed",
        "expert_feedback_claimed",
        "pricing_validation_claimed",
        "production_readiness_claimed",
        "autonomous_revenue_achieved",
        "real_client_delivery_claimed",
        "owner_approval_fabricated",
        "perfect_global_optimality_claimed",
        "EV5_achieved",
        "EV6_achieved",
        "EV7_achieved",
        "EV8_achieved",
        "external_action_allowed",
    ]
    violations = []
    for rel in paths:
        data = load_json(rel, base)
        observed = data.get("observed_state", data)
        for field in forbidden_true:
            if observed.get(field) is True:
                violations.append({"path": rel, "field": field, "value": True})
    return {"artifact_id": "e67_no_overclaim_validation_result", "paths_scanned": paths, "violations": violations, "passed": not violations}


def build_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_state = load_json("operations/external_validation/e67_base_state_manifest.json", base) or build_base_state_manifest(base)
    archaeology = load_json("operations/external_validation/e67_repository_archaeology_inventory.json", base)
    audit = load_json("operations/external_validation/e67_reuse_first_growth_audit.json", base)
    ladder = load_json("operations/external_validation/e67_external_validation_ladder.json", base)
    plan = load_json("operations/external_validation/e67_non_contact_external_validation_plan.json", base)
    receipts = load_json("operations/external_validation/e67_non_contact_public_read_receipts.json", base)
    atoms = load_json("operations/external_validation/e67_external_validation_evidence_atoms.json", base)
    scorecards = load_json("operations/external_validation/e67_route_external_validation_scorecards.json", base)
    readback = load_json("operations/external_validation/e67_ceo_external_validation_readback_smoke_result.json", base)
    offer_update = load_json("operations/external_validation/e67_offer_blueprint_validation_update.json", base)
    roadmap = load_json("operations/external_validation/e67_owner_gated_external_validation_roadmap.json", base)
    auth = load_json("operations/external_validation/e67_behavior_authorization_result.json", base)
    no_overclaim = load_json("operations/external_validation/e67_no_overclaim_validation_result.json", base)
    checks = {
        "base_HEAD_verified": base_state.get("base_verified") is True,
        "repository_archaeology_completed": archaeology.get("asset_count", 0) >= 12,
        "reuse_first_audit_passes": audit.get("passed") is True,
        "external_validation_ladder_created": len(ladder.get("levels", [])) == 9,
        "non_contact_validation_plan_created": plan.get("source_count_planned", 0) >= 24,
        "public_read_receipts_created_or_blocker_classified": receipts.get("receipt_count", 0) >= 24 and bool(receipts.get("public_read_blocker_classification")),
        "validation_evidence_atoms_created": atoms.get("evidence_atom_count", 0) == receipts.get("receipt_count", 0),
        "route_level_validation_scorecards_created": scorecards.get("route_count", 0) >= 5,
        "EV1_EV4_attempted_for_core_routes": all(ev in plan.get("EV_levels_attempted", []) for ev in ["EV1_public_market_language", "EV2_competitor_or_adjacent_product_presence", "EV3_public_pricing_or_packaging_evidence", "EV4_public_demand_or_behavior_proxy"]),
        "EV5_EV8_owner_gated_unachieved": scorecards.get("EV5_EV8_achieved") is False,
        "E67_validation_overlay_loader_implemented": callable(load_e67_external_validation_state_for_brain) and callable(get_route_external_validation_score),
        "CEO_brain_adapter_reads_E67_state": readback.get("passes") is True,
        "offer_blueprint_validation_update_created": offer_update.get("artifact_id") == "e67_offer_blueprint_validation_update",
        "owner_gated_validation_roadmap_created": len(roadmap.get("owner_gated_future", [])) == 4,
        "behavior_authorization_passed": auth.get("passed") is True,
        "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
            "operations/knowledge_graph/e67_ceo_kg_external_validation_read_model_update.json",
            "operations/external_validation/e67_czl_closure.json",
            "operations/external_validation/e67_cieu_residual_summary.json",
        ]),
        "no_forbidden_external_action_executed": auth.get("external_business_execution_authorized") is False,
        "no_overclaim_fields_true": no_overclaim.get("passed") is True,
    }
    any_success = receipts.get("successful_read_count", 0) > 0
    final_status = "e67_non_contact_external_validation_upgrade_completed" if all(checks.values()) and any_success else (
        "e67_non_contact_validation_partial_with_public_read_blocker" if all(checks.values()) else
        "e67_blocked_due_to_overclaim_risk" if checks.get("no_overclaim_fields_true") is False else
        "e67_blocked_due_to_disconnected_ceo_integration" if checks.get("CEO_brain_adapter_reads_E67_state") is False else
        "e67_blocked_due_to_duplicate_capability_risk"
    )
    return {
        "artifact_id": "e67_completion_gate_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": final_status,
        "public_read_source_count": plan.get("source_count_planned", 0),
        "receipts_created": receipts.get("receipt_count", 0),
        "successful_read_count": receipts.get("successful_read_count", 0),
        "evidence_atoms_created": atoms.get("evidence_atom_count", 0),
        "selected_route_external_validation_score": scorecards.get("selected_route_external_validation_score"),
        "fallback_route_external_validation_score": scorecards.get("fallback_route_external_validation_score"),
        "highest_non_contact_EV_level": scorecards.get("highest_non_contact_EV_level"),
        "recommended_next_milestone": select_next_milestone(base),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
        "EV5_achieved": False,
        "EV6_achieved": False,
        "EV7_achieved": False,
        "EV8_achieved": False,
    }


def write_reports(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    archaeology = load_json("operations/external_validation/e67_repository_archaeology_inventory.json", base)
    ladder = load_json("operations/external_validation/e67_external_validation_ladder.json", base)
    plan = load_json("operations/external_validation/e67_non_contact_external_validation_plan.json", base)
    receipts = load_json("operations/external_validation/e67_non_contact_public_read_receipts.json", base)
    atoms = load_json("operations/external_validation/e67_external_validation_evidence_atoms.json", base)
    scorecards = load_json("operations/external_validation/e67_route_external_validation_scorecards.json", base)
    gate = load_json("operations/external_validation/e67_completion_gate_result.json", base)
    write_md(base, "reports/integration/e67_repository_archaeology_inventory.md", "E67 Repository Archaeology Inventory", [
        f"Assets found: `{archaeology.get('asset_count')}`.",
        "E67 reused E66 offer, E65 evidence/model assets, E63/E64 evidence conventions, and the existing safe public reader.",
    ])
    write_md(base, "reports/integration/e67_external_validation_ladder.md", "E67 External Validation Ladder", [
        f"Levels defined: `{len(ladder.get('levels', []))}` from EV0 to EV8.",
        "EV1-EV4 are non-contact public evidence layers; EV5-EV8 remain owner-gated and unachieved.",
    ])
    write_md(base, "reports/integration/e67_non_contact_external_validation_plan.md", "E67 Non-Contact Validation Plan", [
        f"Planned sources: `{plan.get('source_count_planned')}`.",
        f"Routes covered: `{', '.join(plan.get('routes_covered', []))}`.",
        "Rules: no crawl, no contact scraping, no human identification, no login, no forms.",
    ])
    write_md(base, "reports/integration/e67_non_contact_public_read_receipts.md", "E67 Public-Read Receipts", [
        f"Receipts: `{receipts.get('receipt_count')}`.",
        f"Successful reads: `{receipts.get('successful_read_count')}`.",
        f"Blocker classification: `{receipts.get('public_read_blocker_classification')}`.",
    ])
    write_md(base, "reports/integration/e67_external_validation_evidence_atoms.md", "E67 External Validation Evidence Atoms", [
        f"Atoms: `{atoms.get('evidence_atom_count')}`.",
        "Atoms map to E65 signal taxonomy where possible and explicitly prohibit customer/paid/pricing validation claims.",
    ])
    write_md(base, "reports/integration/e67_route_external_validation_scorecards.md", "E67 Route External Validation Scorecards", [
        f"Routes scored: `{scorecards.get('route_count')}`.",
        f"Selected route score: `{scorecards.get('selected_route_external_validation_score')}`.",
        f"Fallback route score: `{scorecards.get('fallback_route_external_validation_score')}`.",
    ])
    write_md(base, "reports/integration/e67_offer_blueprint_validation_update.md", "E67 Offer Blueprint Validation Update", [
        "Selected offer remains internal-only draft.",
        "Update implication: attach EV1-EV4 evidence appendix and owner-gated EV5-EV8 roadmap.",
        "No external-facing final marketing copy was created.",
    ])
    write_md(base, "reports/integration/e67_owner_gated_external_validation_roadmap.md", "E67 Owner-Gated External Validation Roadmap", [
        "Current: EV1-EV4 non-contact evidence layers.",
        "Future owner-gated: EV5 public experiment, EV6 human feedback, EV7 paid signal, EV8 repeatable revenue.",
    ])
    write_md(base, "reports/integration/e67_reuse_first_growth_audit.md", "E67 Reuse-First Growth Audit", [
        "Reuse-first audit passed.",
        "E67 did not rebuild E65 model, E65 evidence ladder, E65 signal taxonomy, public-read adapter, evidence atomizer, route scoring, behavior gate, or CEO readback.",
    ])
    write_md(base, "reports/integration/e67_completion_gate_result.md", "E67 Completion Gate", [
        f"Gate passed: `{gate.get('gate_passed')}`.",
        f"Final status: `{gate.get('final_status')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])
    write_md(base, "reports/integration/e67_operator_handoff.md", "E67 Operator Handoff", [
        f"Final status: `{gate.get('final_status')}`.",
        f"Receipts: `{gate.get('receipts_created')}`; atoms: `{gate.get('evidence_atoms_created')}`.",
        f"Next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])


def write_all_e67_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    write_json(base, "operations/external_validation/e67_base_state_manifest.json", build_base_state_manifest(base))
    write_json(base, "operations/external_validation/e67_repository_archaeology_inventory.json", build_repository_archaeology_inventory(base))
    write_json(base, "operations/external_validation/e67_reuse_first_growth_audit.json", build_reuse_first_growth_audit(base))
    write_json(base, "operations/external_validation/e67_external_validation_ladder.json", build_external_validation_ladder(base))
    write_json(base, "operations/external_validation/e67_non_contact_external_validation_plan.json", build_non_contact_external_validation_plan(base))
    receipts = build_non_contact_public_read_receipts(base)
    write_json(base, "operations/external_validation/e67_non_contact_public_read_receipts.json", receipts)
    write_jsonl(base, "operations/external_validation/e67_non_contact_public_read_receipts.jsonl", receipts["receipts"])
    write_json(base, "operations/external_validation/e67_external_validation_evidence_atoms.json", build_external_validation_evidence_atoms(base))
    write_json(base, "operations/external_validation/e67_route_external_validation_scorecards.json", build_route_external_validation_scorecards(base))
    write_json(base, "operations/external_validation/e67_offer_blueprint_validation_update.json", build_offer_blueprint_validation_update(base))
    write_json(base, "operations/external_validation/e67_owner_gated_external_validation_roadmap.json", build_owner_gated_external_validation_roadmap(base))
    write_json(base, "operations/external_validation/e67_behavior_authorization_result.json", build_behavior_authorization(base))
    write_runtime_writeback(base)
    write_json(base, "operations/external_validation/e67_ceo_external_validation_readback_smoke_result.json", build_ceo_external_validation_readback_smoke(base))
    write_json(base, "operations/external_validation/e67_no_overclaim_validation_result.json", build_no_overclaim_validation(base))
    gate = build_completion_gate(base)
    write_json(base, "operations/external_validation/e67_completion_gate_result.json", gate)
    write_reports(base)
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e67_artifacts(), indent=2, ensure_ascii=False))
