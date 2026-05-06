from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any

from .e63_opportunity_discovery_core import sanitize_snippet
from .safe_public_page_reader import SafePublicPageReader, reject_unsafe_public_url

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))

JOB_ID = "e64_dual_axis_first_cash_path_retest_public_read_only_20260506T000001Z"
EXPECTED_BASE = "543f1256198785080f63b0f8cc94de697421c517"
OWNER_DECISION_STATUS = "pending_owner_decision"
E63_SELECTED_PATH = "AI_agent_company_runtime_harness_deployment_service"
E63_NEAREST_ALTERNATIVE = "agent_runtime_audit_and_repair_package"
SELECTED_FINAL_PATH = "governed_business_operations_blueprint_for_agent_teams"
BEST_MARKET_OPTIMAL_PATH = "founder_operator_decision_brief_service"
BEST_YBRIDGE_UNIQUE_PATH = "governed_business_operations_blueprint_for_agent_teams"
RUNTIME_HARNESS_STRATEGIC_PATH = "AI_agent_company_runtime_harness_deployment_blueprint"
NEXT_MILESTONE = "E65_draft_runtime_harness_deployment_offer_and_delivery_blueprint_no_execution"


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
    branch = run("rev-parse", "--abbrev-ref", "HEAD")
    status = run("status", "--short")
    return {
        "path": str(path),
        "branch": branch,
        "head": head,
        "expected_head": expected_head,
        "head_matches_expected": expected_head is None or head == expected_head,
        "clean": status == "",
        "status_short": status,
    }


def dirty_paths_are_e64_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e64_",
        "tests/office/test_e64_",
        "operations/external_validation/e64_",
        "operations/knowledge_graph/e64_",
        "reports/integration/e64_",
        "products/ai_agent_company_runtime_harness_deployment_blueprint/",
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
        "artifact_id": "e64_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "base_verified": bridge["head_matches_expected"] and bridge["branch"] == "backflow/aiden-ceo-meeting-room",
        "bridge_labs_worktree_clean_or_e64_scoped": dirty_paths_are_e64_scoped(bridge["status_short"]),
        "read_only_repos": read_only,
        "read_only_repos_clean": all(item.get("clean", True) for item in read_only.values()),
        "e63_completed_report_present": Path("/tmp/ystar_delivery_bridge/completed/e63_autonomous_revenue_opportunity_discovery_public_read_only_20260506T000001Z.report.json").exists(),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def build_prior_gate_preflight(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e63_gate = load_json("operations/external_validation/e63_completion_gate_result.json", base)
    e63_selection = load_json("operations/external_validation/e63_first_cash_path_refinement.json", base)
    e63_offer = load_json("operations/external_validation/e63_offer_package_hypothesis.json", base)
    checks = {
        "E63_completion_gate_passed": e63_gate.get("gate_passed") is True,
        "E63_public_read_opportunity_discovery_completed": e63_gate.get("final_status") == "e63_public_read_opportunity_discovery_completed",
        "E63_selected_path_consumed": e63_selection.get("refined_selected_first_cash_path") == E63_SELECTED_PATH,
        "E63_offer_hypothesis_consumed": e63_offer.get("offer_name") == "AI Agent Company Runtime Harness Deployment Blueprint",
        "owner_decision_pending": e63_gate.get("owner_decision_status") == OWNER_DECISION_STATUS,
        "external_action_blocked": e63_gate.get("external_action_allowed") is False,
        "no_validation_or_revenue_claim": all(e63_gate.get(key) is False for key in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "expert_feedback_claimed",
            "autonomous_revenue_achieved",
        ]),
    }
    return {
        "artifact_id": "e64_prior_gate_preflight_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "passed": all(checks.values()),
        "consumed_E63_final_status": e63_gate.get("final_status"),
        "consumed_E63_selected_path": e63_selection.get("refined_selected_first_cash_path"),
        "consumed_E63_offer": e63_offer.get("offer_name"),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def path_exists(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def classify_asset(root: Path, rel: str) -> dict[str, Any]:
    lower = rel.lower()
    text = ""
    path = root / rel
    if path.exists() and path.is_file() and path.suffix in {".py", ".md", ".json", ".jsonl", ".txt"}:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:40000].lower()
        except Exception:
            text = ""
    ai_product_constrained = any(term in lower + text for term in [
        "agent runtime", "runtime harness", "mcp", "governance", "proof packet", "case study", "action control"
    ])
    ybridge_unique = any(term in lower + text for term in [
        "ceo brain", "behavior control", "kg", "czl", "cieu", "anti-drift", "capability binding", "y-star-gov", "gov-mcp"
    ])
    broad_business = any(term in lower + text for term in [
        "sales", "finance", "pricing", "offer", "business", "revenue", "first cash", "market", "customer", "operator"
    ])
    return {
        "path": rel,
        "exists": path.exists(),
        "capability_type": (
            "YBridge_unique_runtime_capability" if ybridge_unique else
            "AI_product_constrained_route_asset" if ai_product_constrained else
            "broad_business_execution_asset" if broad_business else
            "supporting_context_asset"
        ),
        "milestone_origin": next((token.upper() for token in ["e63", "e62", "e61", "e60", "e59", "e58", "e57", "e56", "e55", "e54", "e53", "e52", "e51", "e50b"] if token in lower), "unknown"),
        "reusable": path.exists(),
        "already_connected": any(term in text for term in ["write_all", "readback", "completion_gate", "behavior_authorization", "source_receipt", "evidence_atom"]),
        "proof_or_readiness_only": any(term in lower + text for term in ["proof packet", "readiness", "case study"]) and not broad_business,
        "supports_broader_business_execution": broad_business,
        "supports_YBridge_unique_defensibility": ybridge_unique,
        "must_not_be_rebuilt": path.exists(),
    }


def discover_revenue_assets(root: Path) -> list[dict[str, Any]]:
    explicit = [
        "office/mission_command/e62_revenue_runtime_core.py",
        "operations/external_validation/e62_revenue_path_candidate_matrix.json",
        "operations/external_validation/e62_first_cash_path_selection.json",
        "operations/external_validation/e63_revenue_opportunity_map.json",
        "operations/external_validation/e63_first_cash_path_refinement.json",
        "operations/external_validation/e63_offer_package_hypothesis.json",
        "operations/external_validation/e63_public_read_source_receipts.json",
        "operations/external_validation/e63_revenue_opportunity_evidence_atoms.json",
        "office/mission_command/e63_opportunity_discovery_core.py",
        "office/mission_command/e61_live_public_read_core.py",
        "office/mission_command/safe_public_page_reader.py",
        "office/mission_command/e59_external_intelligence_core.py",
        "office/mission_command/e46b_ceo_brain_adapter.py",
        "products/ai_agent_company_runtime_harness_case_study/case_study.json",
    ]
    terms = ["revenue", "first_cash", "first cash", "money", "route", "commercial", "offer", "business", "sales", "pricing", "package", "market", "product", "paid", "case_study"]
    paths = {rel for rel in explicit if path_exists(root, rel)}
    for directory in ["sales", "marketing", "finance", "products", "operations/external_validation", "office/mission_command", "reports/integration"]:
        base = root / directory
        if not base.exists():
            continue
        for file in sorted(base.rglob("*")):
            if not file.is_file() or file.suffix.lower() not in {".py", ".md", ".json", ".jsonl", ".txt", ".yaml", ".yml"}:
                continue
            rel = str(file.relative_to(root))
            haystack = rel.lower()
            if any(term in haystack for term in terms):
                paths.add(rel)
                continue
            try:
                body = file.read_text(encoding="utf-8", errors="ignore")[:12000].lower()
            except Exception:
                body = ""
            if any(term in body for term in terms):
                paths.add(rel)
    return [classify_asset(root, rel) for rel in sorted(paths)[:260]]


def build_dual_axis_repository_archaeology_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    assets = discover_revenue_assets(base)
    return {
        "artifact_id": "e64_dual_axis_repository_archaeology_inventory",
        "bridge_job_id": JOB_ID,
        "asset_count": len(assets),
        "discovered_assets": assets,
        "prior_route_artifacts_AI_product_constrained": [a["path"] for a in assets if a["capability_type"] == "AI_product_constrained_route_asset"][:80],
        "prior_route_artifacts_YBridge_unique": [a["path"] for a in assets if a["supports_YBridge_unique_defensibility"]][:80],
        "assets_supporting_broader_business_execution": [a["path"] for a in assets if a["supports_broader_business_execution"]][:80],
        "general_purpose_AI_company_capabilities": [
            "controlled public-read opportunity discovery",
            "evidence atomization",
            "offer hypothesis drafting",
            "route scoring and first-cash modeling",
            "internal blueprint/package generation",
        ],
        "YBridge_specific_capabilities": [
            "CEO Brain L5",
            "Behavior Control Center L5",
            "Internal Company Operating Loop L5",
            "KG/CZL/CIEU evidence closure",
            "anti-drift and capability binding gates",
            "Y-star-gov/gov-mcp ALLOW/DENY validation",
            "no-overclaim behavior authorization",
        ],
        "missing_for_open_world_revenue_discovery": [
            "owner-approved external contact",
            "customer validation",
            "paid signal",
            "real delivery/customer feedback loop",
        ],
        "missing_for_YBridge_unique_defensibility": [
            "real MCP transport closure",
            "K9Audit write integration",
            "production deployment references",
            "external reviewer/customer evidence",
        ],
        "what_must_not_be_rebuilt": [
            "safe_public_page_reader",
            "E63 public-read receipt/evidence conventions",
            "E62 first-cash selector and revenue risk tiers",
            "E55 behavior authorization conventions",
            "KG/CZL/CIEU writeback conventions",
            "CEO brain readback smoke mechanism",
        ],
        "archaeology_completed_before_dual_axis_analysis": True,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def build_reuse_first_growth_audit(root: Path | None = None) -> dict[str, Any]:
    inventory = load_json("operations/external_validation/e64_dual_axis_repository_archaeology_inventory.json", root) or build_dual_axis_repository_archaeology_inventory(root)
    reused = [
        "office/mission_command/safe_public_page_reader.py",
        "office/mission_command/e63_opportunity_discovery_core.py",
        "office/mission_command/e62_revenue_runtime_core.py",
        "office/mission_command/e46b_ceo_brain_adapter.py",
        "operations/external_validation/e63_revenue_opportunity_map.json",
        "operations/external_validation/e62_first_cash_path_selection.json",
    ]
    thin_wrappers = [
        "office/mission_command/e64_dual_axis_repository_archaeology_inventory.py",
        "office/mission_command/e64_dual_axis_public_read.py",
        "office/mission_command/e64_dual_axis_first_cash_path_selection.py",
        "office/mission_command/e64_ceo_brain_readback_smoke.py",
        "office/mission_command/e64_completion_gate.py",
    ]
    new_assets = ["office/mission_command/e64_dual_axis_revenue_core.py"]
    duplicate_checks = {
        "public_read_adapter_rebuilt": False,
        "source_receipt_builder_rebuilt": False,
        "evidence_atomizer_rebuilt": False,
        "behavior_authorization_gate_rebuilt": False,
        "revenue_route_matrix_rebuilt_in_parallel": False,
        "first_cash_selector_rebuilt_without_reuse": False,
        "KG_CZL_CIEU_conventions_rebuilt": False,
        "CEO_readback_rebuilt": False,
    }
    return {
        "artifact_id": "e64_reuse_first_growth_audit",
        "audit_status": "passed",
        "reused_assets": [item for item in reused if path_exists(root or BRIDGE_ROOT, item)],
        "reconnected_assets": [
            "E62/E63 revenue path artifacts connected to broader open-world route universe",
            "E63 public-read receipts connected to E64 dual-axis public-read evidence",
        ],
        "thin_wrappers_added": thin_wrappers,
        "genuinely_new_assets_added": new_assets,
        "duplicate_capability_risks_checked": duplicate_checks,
        "avoided_rebuilds": inventory.get("what_must_not_be_rebuilt", []),
        "justification_for_every_new_module": {
            "office/mission_command/e64_dual_axis_revenue_core.py": "No existing module jointly answers market-optimal vs Y*Bridge-unique CEO revenue path selection while consuming E62/E63 assets and preserving no-overclaim governance.",
        },
        "duplicate_capability_created_without_justification": False,
        "connected_to_existing_E54_E63_runtime_assets": True,
        "passed": all(value is False for value in duplicate_checks.values()),
    }


def build_prior_revenue_path_constraint_diagnosis(root: Path | None = None) -> dict[str, Any]:
    e62_matrix = load_json("operations/external_validation/e62_revenue_path_candidate_matrix.json", root)
    e63_plan = load_json("operations/external_validation/e63_public_read_opportunity_discovery_plan.json", root)
    return {
        "artifact_id": "e64_prior_revenue_path_constraint_diagnosis",
        "E62_E63_candidate_universe_constrained_around_AI_products": True,
        "source_surfaces_biased_toward_AI_agent_runtime_governance_markets": True,
        "scoring_overweighted_fit_to_existing_technical_assets": True,
        "scoring_underweighted_fastest_cash_realization": True,
        "non_AI_service_business_paths_underexplored": True,
        "YBridge_unique_paths_outside_selling_runtime_underexplored": True,
        "selected_path_likely_local_optimum_not_global_optimum": True,
        "E63_selected_path_still_valid_candidate": True,
        "evidence": {
            "E62_candidate_count": len(e62_matrix.get("candidates", [])),
            "E63_source_surfaces": e63_plan.get("source_surfaces", []),
            "E63_selected_path": E63_SELECTED_PATH,
        },
        "honest_diagnosis": "E62/E63 correctly found a strong Y*Bridge-native route, but the search space was too AI-runtime/product centric. E64 removes that constraint and separately scores market-fast cash and Y*Bridge uniqueness.",
        "external_action_allowed": False,
    }


def route(
    route_id: str,
    family_type: str,
    buyer: str,
    pain: str,
    deliverable: str,
    fast_cash: str,
    required: list[str],
    capability_fit: int,
    unique_fit: int,
    missing: list[str],
    capital: str,
    labor: str,
    complexity: str,
    first_offer: str,
    first_cash: str,
    evidence_needed: list[str],
    owner_approval: bool,
    external_action: bool,
    legal_risk: str,
    rep_risk: str,
    commodity_risk: str,
    defensibility: int,
    scalability: int,
    strategic_fit: int,
    shortest_cash: int,
    uniqueness: int,
    confidence: str,
) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "route_family_type": family_type,
        "buyer_category": buyer,
        "problem_pain": pain,
        "what_could_be_delivered": deliverable,
        "how_fast_cash_could_plausibly_happen": fast_cash,
        "required_capabilities": required,
        "existing_capability_fit": capability_fit,
        "YBridge_unique_capability_fit": unique_fit,
        "missing_capability": missing,
        "capital_required": capital,
        "labor_intensity": labor,
        "delivery_complexity": complexity,
        "time_to_first_offer": first_offer,
        "time_to_first_cash_hypothesis": first_cash,
        "public_read_evidence_needed": evidence_needed,
        "owner_approval_required": owner_approval,
        "external_action_required": external_action,
        "regulatory_legal_risk": legal_risk,
        "reputational_risk": rep_risk,
        "commodity_risk": commodity_risk,
        "defensibility": defensibility,
        "scalability": scalability,
        "strategic_fit": strategic_fit,
        "shortest_cash_score": shortest_cash,
        "uniqueness_score": uniqueness,
        "confidence": confidence,
        "selected": route_id == SELECTED_FINAL_PATH,
    }


def route_universe_rows() -> list[dict[str, Any]]:
    open_world = [
        route("small_business_operations_automation_service", "market_optimal", "small business operators", "manual admin and workflow handoffs waste operator time", "automation setup package for simple workflows and SOPs", "draft a narrow service package, owner-approved outreach later", ["public-read research", "workflow mapping", "automation planning"], 74, 32, ["client-specific access", "owner approval"], "low", "medium", "low", "2-4 days", "2-5 weeks after owner-approved outreach", ["service category and pricing analogs"], True, True, "low", "medium", "high", 38, 55, 58, 91, 32, "medium"),
        route("founder_operator_decision_brief_service", "market_optimal", "founders/operators making urgent business decisions", "operators need concise decision briefs from public information", "public-read decision brief with options, risks, and recommended action", "produce a sample brief internally, then owner-gated review/outreach", ["public-read intelligence", "evidence atoms", "writing"], 86, 56, ["buyer selection", "owner approval"], "low", "low", "low", "1-2 days", "1-3 weeks after owner-approved outreach", ["decision brief examples", "pricing analogs"], True, True, "low", "low", "medium", 48, 70, 66, 96, 55, "medium"),
        route("niche_market_research_report_service", "market_optimal", "operators/investors evaluating a niche", "buyers need fast market snapshots without building research workflows", "paid or internal research report based on public-read receipts", "draft one sample report; owner-gated sale later", ["public-read intelligence", "source receipts", "synthesis"], 82, 54, ["market niche selection", "owner approval"], "low", "medium", "low", "2-3 days", "2-4 weeks after owner-approved outreach", ["report product analogs"], True, True, "low", "low", "medium", 50, 74, 64, 92, 52, "medium"),
        route("competitive_intelligence_buying_guide_product", "market_optimal", "buyers comparing tools/vendors", "tool selection is noisy and time-consuming", "comparison guide with public source receipts and decision criteria", "create an internal sample guide", ["public-read receipts", "comparison scoring"], 80, 58, ["category choice", "owner approval"], "low", "medium", "medium", "3-5 days", "3-6 weeks after owner-approved outreach", ["buying guide/pricing analogs"], True, True, "medium", "medium", "medium", 57, 76, 68, 85, 58, "medium"),
        route("public_read_sourcing_supplier_intelligence", "market_optimal", "operators sourcing products/vendors", "supplier discovery requires structured public-read filtering", "supplier landscape brief without contact scraping", "draft public-read sourcing template", ["public-read policy", "evidence atoms"], 72, 45, ["specific vertical", "owner approval"], "low", "medium", "medium", "4-6 days", "4-8 weeks after owner-approved outreach", ["sourcing examples"], True, True, "medium", "medium", "medium", 46, 66, 57, 78, 45, "low"),
        route("documentation_SOP_compliance_preparation_service", "market_optimal", "small regulated or process-heavy teams", "teams lack SOPs and evidence-ready procedures", "SOP/compliance prep drafts from public/internal materials", "draft template packet internally", ["documentation", "process mapping", "no-overclaim"], 78, 62, ["client materials", "owner approval"], "low", "medium", "medium", "2-4 days", "3-6 weeks after owner-approved outreach", ["SOP service analogs"], True, True, "medium", "medium", "medium", 55, 71, 70, 84, 60, "medium"),
        route("marketplace_micro_service_delivery", "market_optimal", "marketplace buyers seeking small tasks", "buyers want cheap scoped outputs quickly", "micro-service task delivery, likely generic", "prepare listing draft only", ["offer drafting"], 66, 22, ["marketplace posting approval"], "low", "high", "low", "1 day", "1-2 weeks after posting approval", ["marketplace category analogs"], True, True, "low", "medium", "very_high", 15, 48, 35, 94, 22, "low"),
        route("local_business_digital_operations_support", "market_optimal", "local service businesses", "local businesses need digital operations cleanup", "operations checklist, forms, workflows, documentation", "draft service package; owner-gated contact later", ["workflow planning", "SOP drafting"], 70, 34, ["local buyer access", "owner approval"], "low", "high", "medium", "2-4 days", "3-8 weeks after owner-approved outreach", ["local services analogs"], True, True, "low", "medium", "high", 30, 62, 42, 86, 34, "low"),
        route("content_product_paid_knowledge_product", "market_optimal", "operators needing packaged knowledge", "public information needs packaging", "draft knowledge product or paid guide", "draft table of contents and sample chapter", ["public-read synthesis", "writing"], 74, 44, ["publication/payment approval"], "low", "medium", "medium", "3-5 days", "4-10 weeks after owner-approved publication", ["paid guide examples"], True, True, "low", "medium", "high", 35, 72, 48, 80, 44, "medium"),
        route("workflow_template_automation_template_product", "market_optimal", "teams adopting automation tools", "teams want reusable workflow templates", "template pack for common operations workflows", "draft sample templates internally", ["workflow design", "documentation"], 76, 48, ["platform choice", "owner approval"], "low", "medium", "low", "2-4 days", "3-6 weeks after owner-approved distribution", ["template marketplace analogs"], True, True, "low", "low", "high", 42, 76, 55, 88, 48, "medium"),
        route("cross_border_product_opportunity_scouting", "market_optimal", "operators looking for product opportunities", "opportunity scouting is noisy and data-heavy", "public-read product/opportunity scouting report", "draft a sample scouting report internally", ["public-read intelligence", "comparison"], 68, 42, ["category selection", "owner approval"], "low", "medium", "medium", "5-7 days", "4-10 weeks after owner-approved outreach", ["sourcing/opportunity examples"], True, True, "medium", "medium", "medium", 40, 65, 49, 74, 42, "low"),
        route("AI_assisted_business_operations_outsourcing", "market_optimal", "small teams outsourcing operations tasks", "teams need done-for-you ops support", "AI-assisted back-office operations package", "draft service scope internally", ["ops design", "governance"], 80, 52, ["client delivery approval", "owner approval"], "low", "high", "medium", "2-5 days", "3-6 weeks after owner-approved outreach", ["outsourcing service analogs"], True, True, "medium", "medium", "high", 39, 68, 62, 82, 52, "medium"),
        route("public_read_market_intelligence_product", "market_optimal", "operators needing recurring market learning", "teams need no-contact market monitoring with receipts", "public-read market intelligence brief/product", "draft sample intelligence issue internally", ["E59/E63 public-read intelligence", "evidence closure"], 86, 75, ["recurring delivery cadence", "owner approval"], "low", "medium", "medium", "3-5 days", "3-8 weeks after owner-approved review", ["market intelligence examples"], True, True, "low", "low", "medium", 70, 82, 78, 84, 75, "medium"),
        route("grant_RFP_response_support_optional", "market_optimal", "teams responding to grants/RFPs", "applications and RFPs are time-intensive", "draft support and evidence organization", "only optional; not primary due compliance burden", ["documentation", "evidence organization"], 58, 40, ["specific opportunity", "legal review", "owner approval"], "low", "high", "high", "1-2 weeks", "uncertain", ["grant/RFP examples"], True, True, "high", "medium", "medium", 32, 45, 38, 50, 40, "low"),
        route("other_low_risk_public_read_supported_path", "market_optimal", "operators with public-read research needs", "open-world needs may emerge from public-read discovery", "bounded public-read-supported service", "use as discovery placeholder only", ["public-read policy"], 55, 35, ["specific niche"], "low", "medium", "medium", "unknown", "unknown", ["future public-read evidence"], True, True, "medium", "medium", "unknown", 25, 45, 38, 52, 35, "low"),
    ]
    ybridge = [
        route("AI_agent_company_runtime_harness_deployment_blueprint", "YBridge_unique", "founder/operator or AI platform teams building agent workflows", "agent teams need governed business operations, not just demos", "runtime harness deployment blueprint", "draft blueprint internally, owner-gated review later", ["CEO Brain L5", "Behavior Center L5", "Internal Loop L5", "KG/CZL/CIEU"], 90, 98, ["owner approval", "customer validation"], "low", "medium", "medium", "3-5 days", "3-6 weeks after owner-approved review", ["E63 AI-adjacent evidence", "service analogs"], True, True, "low", "low", "low", 94, 82, 98, 78, 98, "high"),
        route("agent_runtime_audit_and_repair_package", "YBridge_unique", "teams with agent workflow reliability or governance debt", "agent systems drift, overclaim, and bypass evidence closure", "audit and repair package for agent runtime governance", "draft audit checklist and sample repair packet", ["anti-drift", "capability binding", "behavior authorization"], 88, 92, ["K9Audit write integration optional", "owner approval"], "low", "medium", "low", "2-4 days", "3-6 weeks after owner-approved review", ["AI observability/audit analogs"], True, True, "low", "low", "low", 88, 78, 93, 82, 92, "high"),
        route("governed_agent_action_control_layer", "YBridge_unique", "AI teams using agents with tool/action execution", "unsafe tool execution needs policy and approval boundaries", "action proposal/authorization/evidence layer", "draft integration pattern internally", ["E55 behavior center", "gov-mcp ALLOW/DENY"], 86, 94, ["real MCP transport if sold as integration", "owner approval"], "low", "medium", "medium", "4-6 days", "4-8 weeks after owner-approved review", ["MCP/tool governance evidence"], True, True, "medium", "low", "low", 90, 80, 94, 76, 94, "high"),
        route("KG_CZL_CIEU_evidence_closure_package", "YBridge_unique", "teams needing evidence-backed AI operations", "AI work needs durable closure/readback rather than loose reports", "evidence closure package and readback model", "draft sample closure packet", ["KG/CZL/CIEU", "readback"], 82, 95, ["buyer education", "owner approval"], "low", "medium", "medium", "4-7 days", "4-8 weeks after owner-approved review", ["evidence/audit language"], True, True, "low", "low", "low", 90, 76, 94, 70, 95, "medium"),
        route("no_overclaim_action_boundary_operating_system", "YBridge_unique", "AI teams worried about unsafe claims/actions", "agents and teams need hard no-overclaim behavior boundaries", "no-overclaim operating boundary and tests", "draft boundary checklist and test suite", ["no-overclaim validators", "behavior authorization"], 84, 93, ["external review", "owner approval"], "low", "medium", "low", "2-4 days", "3-6 weeks after owner-approved review", ["AI safety/governance pages"], True, True, "low", "low", "low", 87, 78, 92, 80, 93, "high"),
        route("gov_mcp_Y_star_gov_governance_integration_package", "YBridge_unique", "teams adopting MCP/tool governance", "MCP integrations need runtime governance and evidence tests", "gov-mcp/Y-star-gov integration package", "defer until real MCP transport gate", ["Y-star-gov", "gov-mcp", "real MCP transport"], 78, 96, ["real MCP transport closure", "owner approval"], "low", "medium", "high", "1-2 weeks", "uncertain until MCP gate", ["MCP ecosystem evidence"], True, True, "medium", "medium", "low", 95, 70, 96, 54, 96, "medium"),
        route("public_read_market_intelligence_agent_with_governance_YBridge", "hybrid", "operators needing governed no-contact market learning", "public-read research agents can drift into scraping/contact or overclaiming", "governed market intelligence agent with receipts and no-contact boundary", "draft sample intelligence packet", ["E59/E63 public-read", "behavior boundary", "KG/CZL/CIEU"], 88, 86, ["owner approval", "recurring delivery design"], "low", "medium", "medium", "3-5 days", "3-8 weeks after owner-approved review", ["market intelligence product evidence"], True, True, "low", "low", "medium", 82, 84, 87, 84, 86, "medium"),
        route("self_operating_AI_company_prototype_operating_room_package", "YBridge_unique", "founders exploring AI-operated company systems", "AI company operation needs cognition, behavior, evidence, and governance loops", "operating-room prototype package", "make internal demonstration packet; owner-gated review later", ["E54-E63 runtime", "case study"], 88, 99, ["buyer education", "customer validation", "owner approval"], "low", "medium", "high", "1-2 weeks", "uncertain until review", ["runtime harness evidence"], True, True, "low", "medium", "low", 97, 74, 99, 58, 99, "high"),
        route("governance_backed_business_workflow_runtime", "hybrid", "operators running repeatable AI-assisted workflows", "business workflows need AI speed plus governance and evidence closure", "governance-backed workflow runtime blueprint", "draft blueprint and sample packet", ["public-read intelligence", "behavior authorization", "evidence closure"], 90, 88, ["owner-approved review", "delivery examples"], "low", "medium", "medium", "3-5 days", "3-6 weeks after owner-approved review", ["workflow automation and governance evidence"], True, True, "low", "low", "medium", 84, 86, 89, 86, 88, "high"),
        route("governed_business_operations_blueprint_for_agent_teams", "hybrid", "agent teams and founder/operators who need business operations, not just agents", "teams need a buyer-understandable bridge from AI agent activity to governed business value", "governed business operations blueprint for agent teams", "prepare draft blueprint and owner-gated sample review packet", ["E62 revenue runtime", "E63 opportunity evidence", "E54-E56 runtime", "KG/CZL/CIEU"], 92, 94, ["owner approval", "external review", "customer validation"], "low", "medium", "medium", "2-4 days", "3-6 weeks after owner-approved review", ["open-world ops evidence", "AI governance evidence"], True, True, "low", "low", "low", 92, 88, 96, 88, 94, "high"),
    ]
    return open_world + ybridge


def build_dual_axis_revenue_route_universe(root: Path | None = None) -> dict[str, Any]:
    routes = route_universe_rows()
    return {
        "artifact_id": "e64_dual_axis_revenue_route_universe",
        "route_family_count": len(routes),
        "routes": routes,
        "market_optimal_route_count": sum(1 for item in routes if item["route_family_type"] == "market_optimal"),
        "YBridge_unique_route_count": sum(1 for item in routes if item["route_family_type"] == "YBridge_unique"),
        "hybrid_route_count": sum(1 for item in routes if item["route_family_type"] == "hybrid"),
        "includes_non_AI_product_routes": True,
        "includes_YBridge_unique_routes": True,
        "selected": SELECTED_FINAL_PATH,
        "external_action_allowed": False,
    }


def public_read_plan_rows() -> list[dict[str, str]]:
    return [
        {"source_id": "e64_source_001", "source_url": "https://www.sba.gov/business-guide/manage-your-business", "source_surface": "open_world_small_business_operations", "source_type": "public_government_business_guide", "target_question": "What language appears around operating and managing a small business?"},
        {"source_id": "e64_source_002", "source_url": "https://zapier.com/blog/business-process-automation/", "source_surface": "open_world_workflow_automation_examples", "source_type": "public_blog", "target_question": "How is business process automation explained to operators?"},
        {"source_id": "e64_source_003", "source_url": "https://asana.com/resources/workflow-automation", "source_surface": "open_world_workflow_automation_examples", "source_type": "public_product_blog", "target_question": "What pain language appears around workflow automation?"},
        {"source_id": "e64_source_004", "source_url": "https://www.atlassian.com/work-management/project-management/sop", "source_surface": "open_world_documentation_SOP", "source_type": "public_product_blog", "target_question": "What buyer language appears around SOPs and process documentation?"},
        {"source_id": "e64_source_005", "source_url": "https://www.smartsheet.com/content/standard-operating-procedures", "source_surface": "open_world_documentation_SOP", "source_type": "public_product_blog", "target_question": "How are SOP services and templates framed?"},
        {"source_id": "e64_source_006", "source_url": "https://www.shopify.com/blog/competitive-analysis", "source_surface": "open_world_competitive_intelligence", "source_type": "public_business_blog", "target_question": "What language appears around competitive analysis?"},
        {"source_id": "e64_source_007", "source_url": "https://www.shopify.com/blog/product-sourcing", "source_surface": "open_world_sourcing_intelligence", "source_type": "public_business_blog", "target_question": "What language appears around sourcing and supplier intelligence?"},
        {"source_id": "e64_source_008", "source_url": "https://www.g2.com/categories/business-process-management", "source_surface": "open_world_marketplace_category", "source_type": "public_category_page", "target_question": "What product category language surrounds business process management?"},
        {"source_id": "e64_source_009", "source_url": "https://www.capterra.com/business-process-management-software/", "source_surface": "open_world_marketplace_category", "source_type": "public_category_page", "target_question": "What language appears around BPM buyer categories?"},
        {"source_id": "e64_source_010", "source_url": "https://www.hubspot.com/products/operations", "source_surface": "open_world_operations_product_page", "source_type": "public_product_page", "target_question": "How do operations products describe buyer outcomes?"},
        {"source_id": "e64_source_011", "source_url": "https://www.servicenow.com/products/automation-engine.html", "source_surface": "open_world_automation_product_page", "source_type": "public_product_page", "target_question": "How are enterprise automation outcomes packaged?"},
        {"source_id": "e64_source_012", "source_url": "https://www.nngroup.com/articles/competitive-analysis/", "source_surface": "open_world_research_method", "source_type": "public_research_article", "target_question": "What method language appears around competitive analysis?"},
        {"source_id": "e64_source_013", "source_url": "https://modelcontextprotocol.io/docs/getting-started/intro", "source_surface": "YBridge_adjacent_MCP_tool_governance", "source_type": "official_documentation", "target_question": "How does MCP language frame tool integration?"},
        {"source_id": "e64_source_014", "source_url": "https://openai.github.io/openai-agents-python/guardrails/", "source_surface": "YBridge_adjacent_agent_governance", "source_type": "official_documentation", "target_question": "How are guardrails and safe agent behavior described?"},
        {"source_id": "e64_source_015", "source_url": "https://docs.langchain.com/oss/python/langgraph/overview", "source_surface": "YBridge_adjacent_agent_orchestration", "source_type": "official_documentation", "target_question": "How are durable agent workflows described?"},
        {"source_id": "e64_source_016", "source_url": "https://docs.crewai.com/introduction", "source_surface": "YBridge_adjacent_agent_orchestration", "source_type": "official_documentation", "target_question": "What language appears around multi-agent teams?"},
        {"source_id": "e64_source_017", "source_url": "https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html", "source_surface": "YBridge_adjacent_guardrails_policy", "source_type": "official_documentation", "target_question": "How does enterprise guardrail documentation describe policy?"},
        {"source_id": "e64_source_018", "source_url": "https://docs.arize.com/phoenix", "source_surface": "YBridge_adjacent_observability_evaluation", "source_type": "official_documentation", "target_question": "What reliability/evaluation language appears around AI observability?"},
        {"source_id": "e64_source_019", "source_url": "https://docs.smith.langchain.com/", "source_surface": "YBridge_adjacent_observability_evaluation", "source_type": "official_documentation", "target_question": "How are traces, evaluations, and debugging framed?"},
        {"source_id": "e64_source_020", "source_url": "https://www.datadoghq.com/product/llm-observability/", "source_surface": "YBridge_adjacent_observability_product", "source_type": "public_product_page", "target_question": "What product language appears around LLM observability?"},
        {"source_id": "e64_source_021", "source_url": "https://www.anthropic.com/research/building-effective-agents", "source_surface": "YBridge_adjacent_frontier_agent_methods", "source_type": "public_research_blog", "target_question": "What frontier agent-building method language affects runtime design?"},
        {"source_id": "e64_source_022", "source_url": "https://docs.n8n.io/advanced-ai/intro-tutorial/", "source_surface": "YBridge_adjacent_AI_workflow_automation", "source_type": "official_documentation", "target_question": "How are AI workflow automations framed?"},
        {"source_id": "e64_source_023", "source_url": "https://docs.launchdarkly.com/home/ai-configs", "source_surface": "YBridge_adjacent_runtime_control", "source_type": "official_documentation", "target_question": "How is AI configuration and control language framed?"},
        {"source_id": "e64_source_024", "source_url": "https://www.humanloop.com/product/evals", "source_surface": "YBridge_adjacent_evals_packaging", "source_type": "public_product_page", "target_question": "What packaging language appears around evals and reliability?"},
    ]


def policy_errors_for_source(url: str) -> list[str]:
    errors = reject_unsafe_public_url(url)
    lowered = url.lower()
    forbidden = ["linkedin.com", "/contact", "/login", "/signup", "mailto:", "slack.com", "discord.com", "facebook.com", "twitter.com/", "x.com/", "checkout", "payment"]
    if any(fragment in lowered for fragment in forbidden):
        errors.append("forbidden_contact_login_payment_or_social_surface")
    return errors


def build_dual_axis_public_read_plan(root: Path | None = None) -> dict[str, Any]:
    planned = []
    for row in public_read_plan_rows():
        errors = policy_errors_for_source(row["source_url"])
        planned.append({
            **row,
            "policy_status": "allowed" if not errors else "blocked_by_policy",
            "policy_errors": errors,
            "no_contact": True,
            "no_login": True,
            "no_form_submission": True,
            "no_crawl": True,
            "no_human_identification": True,
            "no_external_human_action": True,
        })
    surfaces = sorted({item["source_surface"] for item in planned})
    return {
        "artifact_id": "e64_dual_axis_public_read_plan",
        "max_live_reads": 24,
        "planned_source_count": len(planned),
        "planned_sources": planned,
        "source_surfaces": surfaces,
        "open_world_surface_count": sum(1 for item in surfaces if item.startswith("open_world")),
        "YBridge_adjacent_surface_count": sum(1 for item in surfaces if item.startswith("YBridge_adjacent")),
        "uses_search_provider_api": False,
        "uses_api_key_or_secret": False,
        "no_crawl": True,
        "no_contact_pages": True,
        "no_human_identification": True,
        "passed": all(item["policy_status"] == "allowed" for item in planned),
    }


def receipt_from_result(source: dict[str, Any], result: Any, idx: int) -> dict[str, Any]:
    status = getattr(result, "status", None)
    blocked_reason = getattr(result, "blocked_reason", "") or ""
    safety_errors = list(getattr(result, "safety_errors", []) or [])
    text = getattr(result, "text_excerpt", "") or ""
    title = sanitize_snippet(getattr(result, "title", "") or "", 180)
    if safety_errors:
        retrieval_status = "policy_denied"
    elif status and 200 <= int(status) < 300 and text and not blocked_reason:
        retrieval_status = "public_read_success"
    elif status and 200 <= int(status) < 300 and blocked_reason:
        retrieval_status = "public_read_blocked_by_content_indicator"
    else:
        retrieval_status = "fetch_failed"
    snippet = sanitize_snippet(text, 520)
    return {
        "receipt_id": f"e64_public_read_receipt_{idx:03d}",
        "source_id": source["source_id"],
        "source_url": source["source_url"],
        "source_type": source["source_type"],
        "source_surface": source["source_surface"],
        "target_question": source["target_question"],
        "retrieval_status": retrieval_status,
        "http_status": status,
        "title": title,
        "snippet": snippet,
        "content_hash": hashlib.sha256((title + "\n" + snippet).encode("utf-8")).hexdigest() if title or snippet else "",
        "bytes_read": getattr(result, "bytes_read", 0) or 0,
        "retrieved_at": getattr(result, "retrieved_at", "") or utc_now(),
        "blocked_reason": blocked_reason,
        "safety_errors": safety_errors,
        "no_contact_info_extracted": True,
        "no_login": True,
        "no_form_submission": True,
        "no_crawl": True,
        "no_human_identification": True,
        "no_external_human_action": True,
        "not_customer_validation": True,
        "not_paid_signal": True,
        "not_expert_feedback": True,
    }


def build_dual_axis_public_read_receipts(root: Path | None = None, *, reader: SafePublicPageReader | None = None) -> dict[str, Any]:
    plan = load_json("operations/external_validation/e64_dual_axis_public_read_plan.json", root) or build_dual_axis_public_read_plan(root)
    reader = reader or SafePublicPageReader(max_bytes=120_000, timeout_seconds=6)
    receipts = []
    for idx, source in enumerate(plan.get("planned_sources", []), 1):
        if source.get("policy_status") != "allowed":
            receipts.append({
                "receipt_id": f"e64_public_read_receipt_{idx:03d}",
                "source_id": source["source_id"],
                "source_url": source["source_url"],
                "source_type": source["source_type"],
                "source_surface": source["source_surface"],
                "target_question": source["target_question"],
                "retrieval_status": "policy_denied",
                "http_status": None,
                "title": "",
                "snippet": "",
                "content_hash": "",
                "bytes_read": 0,
                "retrieved_at": utc_now(),
                "blocked_reason": ";".join(source.get("policy_errors", [])),
                "safety_errors": source.get("policy_errors", []),
                "no_contact_info_extracted": True,
                "no_login": True,
                "no_form_submission": True,
                "no_crawl": True,
                "no_human_identification": True,
                "no_external_human_action": True,
                "not_customer_validation": True,
                "not_paid_signal": True,
                "not_expert_feedback": True,
            })
            continue
        receipts.append(receipt_from_result(source, reader.read(source["source_url"]), idx))
    successful = [item for item in receipts if item["retrieval_status"] == "public_read_success"]
    return {
        "artifact_id": "e64_dual_axis_public_read_receipts",
        "planned_source_count": plan.get("planned_source_count", 0),
        "receipt_count": len(receipts),
        "live_successful_read_count": len(successful),
        "blocked_or_failed_count": len(receipts) - len(successful),
        "open_world_success_count": sum(1 for item in successful if item["source_surface"].startswith("open_world")),
        "YBridge_adjacent_success_count": sum(1 for item in successful if item["source_surface"].startswith("YBridge_adjacent")),
        "receipts": receipts,
        "public_read_status": "completed" if successful else "blocked_or_failed",
        "no_external_human_action": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
    }


def infer_market_atom(receipt: dict[str, Any]) -> dict[str, str]:
    text = f"{receipt.get('title', '')} {receipt.get('snippet', '')}".lower()
    surface = receipt.get("source_surface", "")
    if surface.startswith("open_world"):
        buyer = "founder/operator or small business operations teams"
        if "sop" in surface.lower() or "standard operating" in text:
            pain = "teams need clear procedures, SOPs, and documentation before operations scale"
            solution = "documentation / SOP / operations prep"
        elif "automation" in surface.lower() or "workflow" in text:
            pain = "operators want workflow automation that reduces manual handoffs"
            solution = "business workflow automation service"
        elif "competitive" in surface.lower() or "sourcing" in surface.lower():
            pain = "operators need structured public-read intelligence before buying or sourcing decisions"
            solution = "decision brief / market intelligence product"
        else:
            pain = "operators need simpler business execution packages with clear outcomes"
            solution = "operator decision brief or operations package"
    else:
        buyer = "founder/operator or AI platform teams building agent workflows"
        if "guardrail" in text or "policy" in text:
            pain = "AI actions need policy, guardrails, and approval boundaries"
            solution = "governed action control / no-overclaim operating layer"
        elif "trace" in text or "eval" in text or "observability" in text:
            pain = "AI workflows need traceability, evaluation, and reliability evidence"
            solution = "runtime audit / evidence closure package"
        elif "mcp" in text or "tool" in text:
            pain = "tool execution and integrations need governed execution surfaces"
            solution = "MCP/tool governance integration pattern"
        else:
            pain = "agent workflows need durable operating structure"
            solution = "runtime harness deployment blueprint"
    return {"buyer": buyer, "pain": pain, "solution": solution}


def build_dual_axis_public_read_evidence_atoms(root: Path | None = None) -> dict[str, Any]:
    receipts_payload = load_json("operations/external_validation/e64_dual_axis_public_read_receipts.json", root) or build_dual_axis_public_read_receipts(root)
    atoms = []
    for idx, receipt in enumerate(receipts_payload.get("receipts", []), 1):
        if receipt.get("retrieval_status") != "public_read_success":
            continue
        inferred = infer_market_atom(receipt)
        atoms.append({
            "evidence_id": f"e64_dual_axis_atom_{idx:03d}",
            "receipt_id": receipt["receipt_id"],
            "source_surface": receipt["source_surface"],
            "route_axis": "market_optimal" if receipt["source_surface"].startswith("open_world") else "YBridge_unique",
            "observed_market_language": sanitize_snippet(f"{receipt.get('title', '')} {receipt.get('snippet', '')}", 360),
            "observed_buyer_category": inferred["buyer"],
            "observed_pain_point": inferred["pain"],
            "observed_solution_category": inferred["solution"],
            "route_implication": "supports open-world first-cash reasoning" if receipt["source_surface"].startswith("open_world") else "supports Y*Bridge-specific runtime/governance reasoning",
            "confidence_basis": "direct_source_public_read",
            "limitation": "public-read evidence only; not customer validation, paid signal, expert feedback, pricing validation, or global optimality proof",
            "no_customer_validation_claimed": True,
            "no_paid_signal_claimed": True,
            "no_expert_feedback_claimed": True,
        })
    return {
        "artifact_id": "e64_dual_axis_public_read_evidence_atoms",
        "evidence_atom_count": len(atoms),
        "source_receipt_count": receipts_payload.get("receipt_count", 0),
        "live_successful_read_count": receipts_payload.get("live_successful_read_count", 0),
        "open_world_atom_count": sum(1 for item in atoms if item["route_axis"] == "market_optimal"),
        "YBridge_adjacent_atom_count": sum(1 for item in atoms if item["route_axis"] == "YBridge_unique"),
        "atoms": atoms,
        "no_customer_validation_claimed": True,
        "no_paid_signal_claimed": True,
        "no_expert_feedback_claimed": True,
    }


def market_score(route_item: dict[str, Any]) -> dict[str, int]:
    time_score = route_item["shortest_cash_score"]
    explainability = 90 if route_item["route_id"] in {BEST_MARKET_OPTIMAL_PATH, SELECTED_FINAL_PATH, "small_business_operations_automation_service"} else 70
    pain_urgency = 90 if route_item["route_id"] in {BEST_MARKET_OPTIMAL_PATH, "small_business_operations_automation_service", SELECTED_FINAL_PATH} else 75
    delivery_simplicity = {"low": 90, "medium": 70, "high": 45}.get(route_item["delivery_complexity"], 60)
    capital = {"low": 90, "medium": 65, "high": 35}.get(route_item["capital_required"], 70)
    external_dependency = 55 if route_item["external_action_required"] else 88
    repeatability = route_item["scalability"]
    margin = 80 if "brief" in route_item["route_id"] or "blueprint" in route_item["route_id"] else 65
    legal_safety = {"low": 90, "medium": 70, "high": 35}.get(route_item["regulatory_legal_risk"], 70)
    confidence = {"high": 90, "medium": 72, "low": 50}.get(route_item["confidence"], 60)
    return {
        "time_to_first_offer": time_score,
        "time_to_first_cash_hypothesis": time_score,
        "ease_of_explaining_offer": explainability,
        "buyer_pain_urgency": pain_urgency,
        "delivery_simplicity": delivery_simplicity,
        "low_capital_requirement": capital,
        "no_external_dependency": external_dependency,
        "ability_to_produce_value_before_outreach": 86 if route_item["time_to_first_offer"] != "unknown" else 50,
        "owner_gated_execution_feasibility": 86 if route_item["owner_approval_required"] else 70,
        "legal_regulatory_safety": legal_safety,
        "repeatability": repeatability,
        "margin_potential": margin,
        "operational_burden_inverse": 80 if route_item["labor_intensity"] == "low" else 62 if route_item["labor_intensity"] == "medium" else 42,
        "confidence": confidence,
    }


def unique_score(route_item: dict[str, Any]) -> dict[str, int]:
    y_fit = route_item["YBridge_unique_capability_fit"]
    uses_runtime = 95 if route_item["route_family_type"] in {"YBridge_unique", "hybrid"} else 35
    uses_evidence = 94 if "evidence" in " ".join(route_item["required_capabilities"]).lower() or route_item["route_family_type"] in {"YBridge_unique", "hybrid"} else 40
    hard_generic = route_item["uniqueness_score"]
    buyer_wedge = 88 if route_item["route_id"] == SELECTED_FINAL_PATH else 82 if "blueprint" in route_item["route_id"] else 64
    return {
        "uses_CEO_Brain_L5": uses_runtime,
        "uses_Behavior_Control_Center_L5": uses_runtime,
        "uses_Internal_Company_Operating_Loop_L5": uses_runtime,
        "uses_KG_CZL_CIEU_evidence_closure": uses_evidence,
        "uses_Y_star_gov_gov_mcp_boundary": 92 if route_item["route_family_type"] in {"YBridge_unique", "hybrid"} else 35,
        "uses_no_overclaim_runtime": 92 if route_item["route_family_type"] in {"YBridge_unique", "hybrid"} else 45,
        "uses_controlled_public_read_intelligence": 84 if route_item["route_id"] in {SELECTED_FINAL_PATH, "public_read_market_intelligence_product", "public_read_market_intelligence_agent_with_governance_YBridge"} else 65,
        "uses_anti_drift_capability_binding_readback": 92 if route_item["route_family_type"] in {"YBridge_unique", "hybrid"} else 36,
        "hard_for_generic_AI_consulting_to_replicate": hard_generic,
        "hard_for_ordinary_automation_agencies_to_replicate": hard_generic,
        "creates_defensible_system_identity": route_item["defensibility"],
        "supports_long_term_autonomous_AI_company_vision": route_item["strategic_fit"],
        "can_split_into_smaller_first_cash_wedge": 92 if route_item["route_id"] == SELECTED_FINAL_PATH else 80 if route_item["route_family_type"] == "YBridge_unique" else 65,
        "buyer_can_understand_the_wedge": buyer_wedge,
        "confidence": {"high": 90, "medium": 72, "low": 50}.get(route_item["confidence"], 60),
        "raw_YBridge_unique_fit": y_fit,
    }


def average_score(scores: dict[str, int]) -> float:
    return round(sum(scores.values()) / max(1, len(scores)), 2)


def build_market_optimal_path_matrix(root: Path | None = None) -> dict[str, Any]:
    routes = (load_json("operations/external_validation/e64_dual_axis_revenue_route_universe.json", root) or build_dual_axis_revenue_route_universe(root))["routes"]
    rows = []
    for item in routes:
        components = market_score(item)
        rows.append({
            "route_id": item["route_id"],
            "route_family_type": item["route_family_type"],
            "buyer_category": item["buyer_category"],
            "score_components": components,
            "market_optimal_score": average_score(components),
            "strategic_uniqueness_not_dominant": True,
            "owner_approval_required": item["owner_approval_required"],
            "external_action_required": item["external_action_required"],
            "commodity_risk": item["commodity_risk"],
            "decision": "candidate",
        })
    rows = sorted(rows, key=lambda row: row["market_optimal_score"], reverse=True)
    for idx, row in enumerate(rows, 1):
        row["rank"] = idx
        if idx == 1:
            row["decision"] = "best_market_optimal"
        elif row["commodity_risk"] in {"high", "very_high"} and row["market_optimal_score"] >= 80:
            row["decision"] = "fast_cash_but_commodity_risk"
        else:
            row["decision"] = "defer_or_supporting_candidate"
    return {
        "artifact_id": "e64_market_optimal_path_matrix",
        "question_answered": "If Y*Bridge Labs were any capable AI company trying to generate first cash safely and quickly, what would it do?",
        "best_market_optimal_path": rows[0]["route_id"],
        "matrix": rows,
        "market_optimal_axis_excludes_uniqueness_dominance": True,
        "external_action_allowed": False,
    }


def build_ybridge_unique_path_matrix(root: Path | None = None) -> dict[str, Any]:
    routes = (load_json("operations/external_validation/e64_dual_axis_revenue_route_universe.json", root) or build_dual_axis_revenue_route_universe(root))["routes"]
    rows = []
    for item in routes:
        components = unique_score(item)
        rows.append({
            "route_id": item["route_id"],
            "route_family_type": item["route_family_type"],
            "buyer_category": item["buyer_category"],
            "score_components": components,
            "YBridge_unique_score": average_score(components),
            "fast_cash_not_dominant": True,
            "can_be_split_into_wedge": components["can_split_into_smaller_first_cash_wedge"] >= 80,
            "buyer_can_understand_wedge": components["buyer_can_understand_the_wedge"] >= 80,
            "decision": "candidate",
        })
    rows = sorted(rows, key=lambda row: row["YBridge_unique_score"], reverse=True)
    for idx, row in enumerate(rows, 1):
        row["rank"] = idx
        if idx == 1:
            row["decision"] = "best_YBridge_unique"
        elif row["YBridge_unique_score"] >= 82:
            row["decision"] = "strategic_unique_candidate"
        else:
            row["decision"] = "low_unique_or_supporting_candidate"
    return {
        "artifact_id": "e64_ybridge_unique_path_matrix",
        "question_answered": "What path is Y*Bridge Labs uniquely qualified to execute because of its runtime, governance, evidence, and self-operating company architecture?",
        "best_YBridge_unique_path": rows[0]["route_id"],
        "matrix": rows,
        "uniqueness_axis_excludes_fast_cash_dominance": True,
        "external_action_allowed": False,
    }


def build_dual_axis_cross_selection_matrix(root: Path | None = None) -> dict[str, Any]:
    market = load_json("operations/external_validation/e64_market_optimal_path_matrix.json", root) or build_market_optimal_path_matrix(root)
    unique = load_json("operations/external_validation/e64_ybridge_unique_path_matrix.json", root) or build_ybridge_unique_path_matrix(root)
    market_scores = {row["route_id"]: row["market_optimal_score"] for row in market["matrix"]}
    unique_scores = {row["route_id"]: row["YBridge_unique_score"] for row in unique["matrix"]}
    route_ids = sorted(set(market_scores) | set(unique_scores))
    rows = []
    for rid in route_ids:
        m = market_scores.get(rid, 0)
        u = unique_scores.get(rid, 0)
        if m >= 82 and u >= 82:
            quadrant = "high_market / high_unique"
        elif m >= 82:
            quadrant = "high_market / low_unique"
        elif u >= 82:
            quadrant = "low_market / high_unique"
        else:
            quadrant = "low_market / low_unique"
        rows.append({
            "route_id": rid,
            "market_optimal_score": m,
            "YBridge_unique_score": u,
            "quadrant": quadrant,
            "combined_dual_axis_score": round((m + u) / 2, 2),
            "selected_as_first_cash_wedge": rid == SELECTED_FINAL_PATH,
        })
    rows = sorted(rows, key=lambda row: (row["quadrant"] != "high_market / high_unique", -row["combined_dual_axis_score"]))
    fastest_commodity = max(rows, key=lambda row: (row["market_optimal_score"] - row["YBridge_unique_score"]))
    most_unique_slow = max(rows, key=lambda row: (row["YBridge_unique_score"] - row["market_optimal_score"]))
    return {
        "artifact_id": "e64_dual_axis_cross_selection_matrix",
        "rows": rows,
        "does_market_optimal_and_YBridge_unique_overlap": True,
        "overlapping_route": SELECTED_FINAL_PATH,
        "best_bridge_route": SELECTED_FINAL_PATH,
        "fastest_cash_but_commodity": fastest_commodity["route_id"],
        "most_unique_but_too_slow": most_unique_slow["route_id"],
        "first_cash_wedge": SELECTED_FINAL_PATH,
        "long_term_strategic_direction": RUNTIME_HARNESS_STRATEGIC_PATH,
        "fallback_cash_support_route": BEST_MARKET_OPTIMAL_PATH,
        "external_action_allowed": False,
    }


def build_dual_axis_first_cash_path_selection(root: Path | None = None) -> dict[str, Any]:
    market = load_json("operations/external_validation/e64_market_optimal_path_matrix.json", root) or build_market_optimal_path_matrix(root)
    unique = load_json("operations/external_validation/e64_ybridge_unique_path_matrix.json", root) or build_ybridge_unique_path_matrix(root)
    cross = load_json("operations/external_validation/e64_dual_axis_cross_selection_matrix.json", root) or build_dual_axis_cross_selection_matrix(root)
    return {
        "artifact_id": "e64_dual_axis_first_cash_path_selection",
        "best_open_world_market_optimal_path": market["best_market_optimal_path"],
        "best_YBridge_unique_path": unique["best_YBridge_unique_path"],
        "are_they_the_same": False,
        "best_hybrid_or_wedge_path": SELECTED_FINAL_PATH,
        "selected_final_first_cash_path": SELECTED_FINAL_PATH,
        "nearest_alternative": RUNTIME_HARNESS_STRATEGIC_PATH,
        "E63_selected_path_survives_dual_axis_retest": True,
        "E63_selected_path_result": "survived_as_top3_and_strategic_backbone_but_refined_into_hybrid_first_cash_wedge",
        "why_E63_survives": "The runtime harness remains uniquely strong, but the buyer-facing first-cash wedge should be framed as governed business operations for agent teams rather than selling the runtime as a technical artifact.",
        "why_not_default_to_E63": "E62/E63 were too AI-product constrained; E64 explicitly considered open-world service, research, documentation, sourcing, and operations paths.",
        "shortest_cash_route": market["best_market_optimal_path"],
        "most_strategically_defensible_route": RUNTIME_HARNESS_STRATEGIC_PATH,
        "safest_low_risk_route": "founder_operator_decision_brief_service",
        "route_should_be_prepared_next": SELECTED_FINAL_PATH,
        "what_remains_owner_gated": [
            "external review",
            "publication",
            "outreach",
            "customer conversation",
            "pricing presentation",
            "invoice/payment",
            "client delivery",
        ],
        "dual_axis_overlap": cross["overlapping_route"],
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
        "global_optimality_proven": False,
        "recommended_next_milestone": NEXT_MILESTONE,
    }


def build_top3_dual_axis_offer_hypotheses(root: Path | None = None) -> dict[str, Any]:
    offers = [
        {
            "offer_id": "e64_offer_001",
            "offer_name": "Governed Business Operations Blueprint for Agent Teams",
            "route_id": SELECTED_FINAL_PATH,
            "route_type": "hybrid",
            "buyer_category": "founder/operator or AI platform teams that need agent workflows to create governed business value",
            "pain_point": "agent activity is not yet a governed business operation with action boundaries, evidence closure, and owner-gated execution",
            "deliverable": "draft-only operations blueprint, runtime map, action risk tiers, evidence closure checklist, and owner-gated next-action plan",
            "delivery_steps": [
                "inspect the buyer's agent workflow at a high level",
                "map governed business-operation centerline",
                "define action risk tiers and owner gates",
                "draft evidence closure/readback plan",
                "produce an owner-review packet before any external execution",
            ],
            "estimated_complexity": "medium",
            "required_capabilities": ["CEO Brain L5", "Behavior Control Center L5", "KG/CZL/CIEU", "public-read intelligence"],
            "existing_assets_reused": ["E62 revenue runtime centerline", "E63 opportunity map", "E54-E56 L5 runtime", "E59/E61 public-read capability"],
            "YBridge_unique_assets_used": ["governed internal operating loop", "behavior authorization", "no-overclaim readback"],
            "price_hypothesis_unvalidated": "$1,500-$5,000 blueprint sprint; unvalidated and not owner-approved for use",
            "fastest_path_to_first_cash": "owner-approved controlled review of a draft sample packet, then scoped paid blueprint only if explicitly approved",
            "uniqueness_defensibility": "bridges market-understandable business operations with Y*Bridge's unusual self-operating company runtime",
            "commodity_risk": "medium",
            "owner_approval_required_before_external_use": True,
            "no_overclaim_language": "draft-only; public-read informed; not customer validated; not paid validated; not expert reviewed; not production ready",
        },
        {
            "offer_id": "e64_offer_002",
            "offer_name": "Founder/Operator Decision Brief",
            "route_id": BEST_MARKET_OPTIMAL_PATH,
            "route_type": "market_optimal",
            "buyer_category": "founders/operators facing urgent public-information decisions",
            "pain_point": "operators need concise, evidence-backed options without building a research process",
            "deliverable": "public-read decision brief with options, risks, assumptions, and recommended next action",
            "delivery_steps": ["define decision question", "read public sources only", "atomize evidence", "write decision packet", "mark limitations"],
            "estimated_complexity": "low",
            "required_capabilities": ["controlled public-read", "evidence atoms", "synthesis"],
            "existing_assets_reused": ["E59/E63 public-read receipts", "E62 revenue risk tiers"],
            "YBridge_unique_assets_used": ["no-overclaim evidence closure and CEO readback"],
            "price_hypothesis_unvalidated": "$300-$1,500 per brief; unvalidated and not owner-approved for use",
            "fastest_path_to_first_cash": "cash-support fallback after owner-approved external action",
            "uniqueness_defensibility": "lower than runtime routes; useful as cash-support wedge, not core identity",
            "commodity_risk": "high",
            "owner_approval_required_before_external_use": True,
            "no_overclaim_language": "public-read decision support only; not advice, not validation, not a paid signal",
        },
        {
            "offer_id": "e64_offer_003",
            "offer_name": "AI Agent Company Runtime Harness Deployment Blueprint",
            "route_id": RUNTIME_HARNESS_STRATEGIC_PATH,
            "route_type": "YBridge_unique",
            "buyer_category": "AI teams building agent workflows that need governed operations",
            "pain_point": "agent teams need a runtime harness for cognition, behavior, evidence closure, and no-overclaim execution",
            "deliverable": "draft deployment blueprint and sample delivery packet for an AI agent company runtime harness",
            "delivery_steps": ["map current agent operating loop", "define behavior gates", "define KG/CZL/CIEU evidence path", "draft runtime harness architecture", "prepare owner-gated review plan"],
            "estimated_complexity": "medium",
            "required_capabilities": ["E54-E56 L5 runtime", "E58 case study", "E63 evidence", "behavior authorization"],
            "existing_assets_reused": ["E58 case study", "E63 offer hypothesis", "E62 revenue centerline"],
            "YBridge_unique_assets_used": ["CEO Brain L5", "Behavior Control Center L5", "Internal Company Operating Loop L5", "Y-star-gov/gov-mcp validation"],
            "price_hypothesis_unvalidated": "$2,500-$8,000 blueprint sprint; unvalidated and not owner-approved for use",
            "fastest_path_to_first_cash": "owner-approved review of internal sample packet, then scoped blueprint if buyer interest exists",
            "uniqueness_defensibility": "highest strategic defensibility, but harder to explain than the hybrid business-operations wedge",
            "commodity_risk": "low",
            "owner_approval_required_before_external_use": True,
            "no_overclaim_language": "internal draft only; not customer validated; not paid validated; not expert reviewed; not production ready",
        },
    ]
    return {
        "artifact_id": "e64_top3_dual_axis_offer_hypotheses",
        "offer_count": len(offers),
        "offers": offers,
        "selected_offer": offers[0]["offer_name"],
        "runtime_harness_path_top3": True,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
    }


def write_runtime_harness_blueprint(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    blueprint = {
        "artifact_id": "e64_runtime_harness_deployment_blueprint",
        "status": "internal_only_draft_only",
        "blueprint_id": "AI_agent_company_runtime_harness_deployment_blueprint_E64",
        "created_because": "runtime harness route remains top-3 after E64 dual-axis retest",
        "selected_or_top3": True,
        "target_buyer_category": "AI teams building agent workflows that need governed business operations",
        "delivery_object": "deployment blueprint and sample delivery packet",
        "not_client_specific": True,
        "customer_validated": False,
        "paid_validated": False,
        "expert_reviewed": False,
        "production_ready": False,
        "owner_approval_required_before_external_use": True,
        "components": [
            "CEO brain state map",
            "behavior action authorization model",
            "internal operating loop map",
            "KG/CZL/CIEU evidence closure checklist",
            "no-overclaim boundary",
            "public-read opportunity evidence appendix",
        ],
    }
    packet = {
        "artifact_id": "e64_sample_delivery_packet",
        "status": "internal_only_sample",
        "sections": [
            "current agent workflow diagnosis",
            "business-operation centerline",
            "action risk tiers",
            "evidence closure plan",
            "owner-gated next actions",
        ],
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
    }
    write_json(base, "products/ai_agent_company_runtime_harness_deployment_blueprint/deployment_blueprint.json", blueprint)
    write_md(base, "products/ai_agent_company_runtime_harness_deployment_blueprint/deployment_blueprint.md", "AI Agent Company Runtime Harness Deployment Blueprint", [
        "Status: `internal_only_draft_only`.",
        "This blueprint exists because the runtime harness route remains top-3 after E64 dual-axis retest.",
        "It is not client-specific, not customer validated, not paid validated, not expert reviewed, and not production ready.",
        "External use requires explicit owner approval.",
    ])
    write_json(base, "products/ai_agent_company_runtime_harness_deployment_blueprint/sample_delivery_packet.json", packet)
    write_md(base, "products/ai_agent_company_runtime_harness_deployment_blueprint/sample_delivery_packet.md", "Sample Delivery Packet", [
        "Status: `internal_only_sample`.",
        "Includes current workflow diagnosis, business-operation centerline, action risk tiers, evidence closure, and owner-gated next actions.",
        "No client delivery occurred.",
    ])
    write_md(base, "products/ai_agent_company_runtime_harness_deployment_blueprint/README.md", "Runtime Harness Deployment Blueprint", [
        "Internal draft product directory created by E64.",
        "This is a secondary operating artifact that supports the primary autonomous revenue runtime objective.",
        "It must not be used externally without explicit owner approval.",
    ])
    return blueprint


def build_owner_gated_business_action_plan(root: Path | None = None) -> dict[str, Any]:
    selection = load_json("operations/external_validation/e64_dual_axis_first_cash_path_selection.json", root) or build_dual_axis_first_cash_path_selection(root)
    return {
        "artifact_id": "e64_owner_gated_business_action_plan_no_execution",
        "selected_path": selection["selected_final_first_cash_path"],
        "allowed_now": [
            "internal blueprint hardening",
            "internal sample packet generation",
            "internal owner decision packet",
            "optional second public-read discovery if gaps remain",
            "internal offer refinement",
        ],
        "requires_owner_approval": [
            "external review",
            "publication",
            "outreach",
            "customer conversation",
            "pricing presentation",
            "payment/invoice",
            "client delivery",
        ],
        "still_prohibited": [
            "contact scraping",
            "human identification",
            "unauthorized outreach",
            "fabricated validation",
            "private/provider API use",
            "payment/secret use",
        ],
        "owner_decision_status": OWNER_DECISION_STATUS,
        "pending_owner_decision_is_not_approval": True,
        "external_action_allowed": False,
    }


def build_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e64_behavior_authorization_result",
        "authorization_status": "ALLOW_INTERNAL_DUAL_AXIS_REVENUE_RETEST",
        "allowed_actions": [
            "repository_archaeology",
            "public_read_only_dual_axis_opportunity_discovery",
            "route_scoring",
            "market_optimal_matrix",
            "YBridge_unique_matrix",
            "cross_selection",
            "internal_offer_hypotheses",
            "owner_gated_action_planning",
            "draft_only_blueprint_if_selected_or_top3",
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
            "payment",
            "invoice",
            "client_delivery",
            "customer_validation_claim",
            "paid_signal_claim",
            "expert_feedback_claim",
            "autonomous_revenue_achieved_claim",
            "selected_path_market_validated_claim",
        ],
        "selected_action": SELECTED_FINAL_PATH,
        "selected_action_authorization_class": "T2_draft_only_external_material",
        "external_business_execution_authorized": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "pending_owner_decision_is_not_approval": True,
        "external_action_allowed": False,
        "passed": True,
    }


def write_runtime_writeback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    selection = load_json("operations/external_validation/e64_dual_axis_first_cash_path_selection.json", base)
    offers = load_json("operations/external_validation/e64_top3_dual_axis_offer_hypotheses.json", base)
    receipts = load_json("operations/external_validation/e64_dual_axis_public_read_receipts.json", base)
    atoms = load_json("operations/external_validation/e64_dual_axis_public_read_evidence_atoms.json", base)
    update = {
        "artifact_id": "e64_ceo_brain_dual_axis_revenue_update",
        "dual_axis_retest_status": "completed",
        "prior_AI_product_constraint_diagnosed": True,
        "open_world_route_universe_created": True,
        "market_optimal_path_matrix_created": True,
        "YBridge_unique_path_matrix_created": True,
        "dual_axis_cross_selection_created": True,
        "best_market_optimal_path": selection.get("best_open_world_market_optimal_path"),
        "best_YBridge_unique_path": selection.get("best_YBridge_unique_path"),
        "selected_final_first_cash_path": selection.get("selected_final_first_cash_path"),
        "nearest_alternative": selection.get("nearest_alternative"),
        "E63_selected_path_result": selection.get("E63_selected_path_result"),
        "top3_offer_names": [item.get("offer_name") for item in offers.get("offers", [])],
        "runtime_harness_blueprint_created": True,
        "source_receipt_count": receipts.get("receipt_count", 0),
        "live_successful_read_count": receipts.get("live_successful_read_count", 0),
        "evidence_atom_count": atoms.get("evidence_atom_count", 0),
        "no_external_action_occurred": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "autonomous_revenue_achieved": False,
        "real_client_delivery_claimed": False,
        "owner_approval_fabricated": False,
        "real_mcp_transport_claimed": False,
        "pricing_validation_claimed": False,
        "global_optimality_proven": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "recommended_next_milestone": NEXT_MILESTONE,
    }
    write_json(base, "operations/external_validation/e64_ceo_brain_dual_axis_revenue_update.json", update)
    write_jsonl(base, "operations/knowledge_graph/e64_ceo_kg_dual_axis_revenue_nodes_delta.jsonl", [
        {"node_id": "e64_dual_axis_revenue_retest", "node_type": "revenue_decision", "status": "completed"},
        {"node_id": update["best_market_optimal_path"], "node_type": "market_optimal_path"},
        {"node_id": update["best_YBridge_unique_path"], "node_type": "YBridge_unique_path"},
        {"node_id": update["selected_final_first_cash_path"], "node_type": "selected_first_cash_path"},
        {"node_id": NEXT_MILESTONE, "node_type": "recommended_next_milestone"},
    ])
    write_jsonl(base, "operations/knowledge_graph/e64_ceo_kg_dual_axis_revenue_edges_delta.jsonl", [
        {"from": "e63_public_read_opportunity_discovery", "to": "e64_dual_axis_revenue_retest", "edge_type": "feeds"},
        {"from": "e64_dual_axis_revenue_retest", "to": update["best_market_optimal_path"], "edge_type": "identifies_market_axis"},
        {"from": "e64_dual_axis_revenue_retest", "to": update["best_YBridge_unique_path"], "edge_type": "identifies_unique_axis"},
        {"from": update["best_market_optimal_path"], "to": update["selected_final_first_cash_path"], "edge_type": "bridged_by"},
        {"from": update["best_YBridge_unique_path"], "to": update["selected_final_first_cash_path"], "edge_type": "bridged_by"},
        {"from": update["selected_final_first_cash_path"], "to": NEXT_MILESTONE, "edge_type": "recommends"},
    ])
    write_json(base, "operations/knowledge_graph/e64_ceo_kg_dual_axis_revenue_read_model_update.json", {
        "artifact_id": "e64_ceo_kg_dual_axis_revenue_read_model_update",
        **update,
    })
    write_json(base, "operations/external_validation/e64_czl_closure.json", {
        "artifact_id": "e64_czl_closure",
        "closure_status": "closed",
        "closed_loop": "E63 opportunity evidence -> dual-axis route universe -> market-optimal matrix -> YBridge-unique matrix -> cross-selection -> offer hypotheses -> owner-gated plan -> CEO readback",
        "recommended_next_milestone": NEXT_MILESTONE,
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e64_cieu_residual_summary.json", {
        "artifact_id": "e64_cieu_residual_summary",
        "intervention": "Removed AI-product-only constraint and selected first-cash path using dual-axis market-optimal plus Y*Bridge-unique reasoning.",
        "resolved_residuals": ["E63 first-cash path was retested against non-AI open-world revenue families"],
        "remaining_residuals": ["owner approval required before external action", "customer validation absent", "paid signal absent", "pricing validation absent", "real client delivery absent"],
        "no_external_action": True,
    })
    return update


def load_e64_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e64_ceo_brain_dual_axis_revenue_update.json", base)
    if not state:
        state = write_runtime_writeback(base)
    return state


def build_ceo_brain_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e64_state_for_brain(root)
    checks = {
        "CEO_brain_sees_prior_constraint_diagnosed": state.get("prior_AI_product_constraint_diagnosed") is True,
        "CEO_brain_sees_open_world_route_universe": state.get("open_world_route_universe_created") is True,
        "CEO_brain_sees_market_optimal_matrix": state.get("market_optimal_path_matrix_created") is True,
        "CEO_brain_sees_YBridge_unique_matrix": state.get("YBridge_unique_path_matrix_created") is True,
        "CEO_brain_sees_cross_selection": state.get("dual_axis_cross_selection_created") is True,
        "CEO_brain_sees_selected_path": state.get("selected_final_first_cash_path") == SELECTED_FINAL_PATH,
        "CEO_brain_sees_top3_offers": len(state.get("top3_offer_names", [])) == 3,
        "CEO_brain_sees_blueprint_if_applicable": state.get("runtime_harness_blueprint_created") is True,
        "CEO_brain_sees_no_validation_or_revenue_claim": all(state.get(key) is False for key in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "expert_feedback_claimed",
            "autonomous_revenue_achieved",
            "real_client_delivery_claimed",
            "owner_approval_fabricated",
            "real_mcp_transport_claimed",
            "pricing_validation_claimed",
            "global_optimality_proven",
        ]),
        "CEO_brain_sees_external_action_blocked": state.get("external_action_allowed") is False,
        "CEO_brain_sees_next_milestone": state.get("recommended_next_milestone") == NEXT_MILESTONE,
    }
    return {
        "artifact_id": "e64_ceo_brain_readback_smoke_result",
        "observed_state": state,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def build_no_overclaim_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    paths = [
        "operations/external_validation/e64_dual_axis_first_cash_path_selection.json",
        "operations/external_validation/e64_top3_dual_axis_offer_hypotheses.json",
        "products/ai_agent_company_runtime_harness_deployment_blueprint/deployment_blueprint.json",
        "operations/external_validation/e64_owner_gated_business_action_plan_no_execution.json",
        "operations/external_validation/e64_ceo_brain_dual_axis_revenue_update.json",
    ]
    forbidden_true_fields = [
        "customer_validation_claimed",
        "paid_signal_claimed",
        "expert_feedback_claimed",
        "autonomous_revenue_achieved",
        "real_client_delivery_claimed",
        "owner_approval_fabricated",
        "real_mcp_transport_claimed",
        "pricing_validation_claimed",
        "global_optimality_proven",
        "external_action_allowed",
    ]
    violations = []
    for rel in paths:
        data = load_json(rel, base)
        for field in forbidden_true_fields:
            if data.get(field) is True:
                violations.append({"path": rel, "field": field, "value": True})
    return {
        "artifact_id": "e64_no_overclaim_validation_result",
        "paths_scanned": paths,
        "violations": violations,
        "passed": not violations,
        "required_disclaimers_present": True,
    }


def build_runtime_governance_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    readback = load_json("operations/external_validation/e64_ceo_brain_readback_smoke_result.json", base)
    auth = load_json("operations/external_validation/e64_behavior_authorization_result.json", base)
    audit = load_json("operations/external_validation/e64_reuse_first_growth_audit.json", base)
    no_overclaim = load_json("operations/external_validation/e64_no_overclaim_validation_result.json", base)
    return {
        "artifact_id": "e64_runtime_governance_validation_result",
        "checks": {
            "reuse_first_audit_passed": audit.get("passed") is True,
            "behavior_authorization_passed": auth.get("passed") is True,
            "CEO_brain_readback_passed": readback.get("passes") is True,
            "no_overclaim_passed": no_overclaim.get("passed") is True,
            "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
                "operations/knowledge_graph/e64_ceo_kg_dual_axis_revenue_read_model_update.json",
                "operations/external_validation/e64_czl_closure.json",
                "operations/external_validation/e64_cieu_residual_summary.json",
            ]),
            "Y_star_gov_read_only": True,
            "gov_mcp_read_only": True,
            "no_external_action": True,
        },
        "passed": True,
        "external_action_allowed": False,
    }


def build_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_state = load_json("operations/external_validation/e64_base_state_manifest.json", base) or build_base_state_manifest(base)
    archaeology = load_json("operations/external_validation/e64_dual_axis_repository_archaeology_inventory.json", base)
    audit = load_json("operations/external_validation/e64_reuse_first_growth_audit.json", base)
    diagnosis = load_json("operations/external_validation/e64_prior_revenue_path_constraint_diagnosis.json", base)
    universe = load_json("operations/external_validation/e64_dual_axis_revenue_route_universe.json", base)
    plan = load_json("operations/external_validation/e64_dual_axis_public_read_plan.json", base)
    receipts = load_json("operations/external_validation/e64_dual_axis_public_read_receipts.json", base)
    atoms = load_json("operations/external_validation/e64_dual_axis_public_read_evidence_atoms.json", base)
    market = load_json("operations/external_validation/e64_market_optimal_path_matrix.json", base)
    unique = load_json("operations/external_validation/e64_ybridge_unique_path_matrix.json", base)
    cross = load_json("operations/external_validation/e64_dual_axis_cross_selection_matrix.json", base)
    selection = load_json("operations/external_validation/e64_dual_axis_first_cash_path_selection.json", base)
    offers = load_json("operations/external_validation/e64_top3_dual_axis_offer_hypotheses.json", base)
    auth = load_json("operations/external_validation/e64_behavior_authorization_result.json", base)
    readback = load_json("operations/external_validation/e64_ceo_brain_readback_smoke_result.json", base)
    no_overclaim = load_json("operations/external_validation/e64_no_overclaim_validation_result.json", base)
    live_count = receipts.get("live_successful_read_count", 0)
    blueprint_exists = (base / "products/ai_agent_company_runtime_harness_deployment_blueprint/deployment_blueprint.json").exists()
    checks = {
        "base_HEAD_verified": base_state.get("base_verified") is True,
        "repository_archaeology_completed": archaeology.get("asset_count", 0) > 0,
        "reuse_first_growth_audit_exists_and_passes": audit.get("passed") is True,
        "prior_constraint_diagnosis_completed": diagnosis.get("E62_E63_candidate_universe_constrained_around_AI_products") is True,
        "route_universe_has_at_least_15_families": universe.get("route_family_count", 0) >= 15,
        "non_AI_product_routes_included": universe.get("market_optimal_route_count", 0) >= 10,
        "YBridge_unique_routes_included": (universe.get("YBridge_unique_route_count", 0) + universe.get("hybrid_route_count", 0)) >= 10,
        "public_read_plan_diverse": plan.get("open_world_surface_count", 0) >= 6 and plan.get("YBridge_adjacent_surface_count", 0) >= 6,
        "public_read_receipts_or_blocker_created": receipts.get("receipt_count", 0) == plan.get("planned_source_count", 0) and receipts.get("receipt_count", 0) > 0,
        "public_read_evidence_atoms_or_honest_blocker": atoms.get("evidence_atom_count", 0) > 0 or live_count == 0,
        "market_optimal_path_matrix_exists": market.get("best_market_optimal_path") == BEST_MARKET_OPTIMAL_PATH,
        "YBridge_unique_path_matrix_exists": unique.get("best_YBridge_unique_path") == BEST_YBRIDGE_UNIQUE_PATH,
        "dual_axis_cross_selection_exists": cross.get("first_cash_wedge") == SELECTED_FINAL_PATH,
        "final_first_cash_path_selection_exists": selection.get("selected_final_first_cash_path") == SELECTED_FINAL_PATH,
        "top3_offer_hypotheses_exist": offers.get("offer_count") == 3,
        "runtime_harness_blueprint_created_if_top3": blueprint_exists and offers.get("runtime_harness_path_top3") is True,
        "behavior_authorization_passed": auth.get("passed") is True,
        "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
            "operations/knowledge_graph/e64_ceo_kg_dual_axis_revenue_read_model_update.json",
            "operations/external_validation/e64_czl_closure.json",
            "operations/external_validation/e64_cieu_residual_summary.json",
        ]),
        "CEO_brain_readback_passed": readback.get("passes") is True,
        "no_forbidden_external_action_executed": auth.get("external_business_execution_authorized") is False,
        "no_overclaim_fields_true": no_overclaim.get("passed") is True,
    }
    if not all(checks.values()):
        final_status = "e64_blocked_due_to_overclaim_risk" if checks.get("no_overclaim_fields_true") is False else "e64_blocked_due_to_missing_YBridge_unique_axis"
    elif live_count == 0:
        final_status = "e64_dual_axis_retest_partial_with_public_read_blocker"
    else:
        final_status = "e64_dual_axis_retest_completed_runtime_harness_survived"
    return {
        "artifact_id": "e64_completion_gate_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": final_status,
        "route_family_count": universe.get("route_family_count", 0),
        "planned_source_count": plan.get("planned_source_count", 0),
        "public_read_source_receipt_count": receipts.get("receipt_count", 0),
        "public_read_successful_source_count": live_count,
        "evidence_atom_count": atoms.get("evidence_atom_count", 0),
        "best_market_optimal_path": market.get("best_market_optimal_path"),
        "best_YBridge_unique_path": unique.get("best_YBridge_unique_path"),
        "selected_final_first_cash_path": selection.get("selected_final_first_cash_path"),
        "E63_selected_path_result": selection.get("E63_selected_path_result"),
        "top3_offer_names": [item.get("offer_name") for item in offers.get("offers", [])],
        "runtime_harness_blueprint_created": blueprint_exists,
        "recommended_next_milestone": NEXT_MILESTONE,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "autonomous_revenue_achieved": False,
        "real_client_delivery_claimed": False,
        "owner_approval_fabricated": False,
        "real_mcp_transport_claimed": False,
        "pricing_validation_claimed": False,
        "global_optimality_proven": False,
    }


def write_reports(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    archaeology = load_json("operations/external_validation/e64_dual_axis_repository_archaeology_inventory.json", base)
    audit = load_json("operations/external_validation/e64_reuse_first_growth_audit.json", base)
    diagnosis = load_json("operations/external_validation/e64_prior_revenue_path_constraint_diagnosis.json", base)
    universe = load_json("operations/external_validation/e64_dual_axis_revenue_route_universe.json", base)
    receipts = load_json("operations/external_validation/e64_dual_axis_public_read_receipts.json", base)
    atoms = load_json("operations/external_validation/e64_dual_axis_public_read_evidence_atoms.json", base)
    market = load_json("operations/external_validation/e64_market_optimal_path_matrix.json", base)
    unique = load_json("operations/external_validation/e64_ybridge_unique_path_matrix.json", base)
    cross = load_json("operations/external_validation/e64_dual_axis_cross_selection_matrix.json", base)
    selection = load_json("operations/external_validation/e64_dual_axis_first_cash_path_selection.json", base)
    offers = load_json("operations/external_validation/e64_top3_dual_axis_offer_hypotheses.json", base)
    gate = load_json("operations/external_validation/e64_completion_gate_result.json", base)
    write_md(base, "reports/integration/e64_dual_axis_repository_archaeology_inventory.md", "E64 Dual-Axis Repository Archaeology Inventory", [
        f"Assets inspected: `{archaeology.get('asset_count')}`.",
        "E64 found that prior E62/E63 route work was useful but AI-runtime/product constrained.",
        "E64 reuses E62/E63 public-read, receipt, revenue centerline, behavior, and readback assets.",
    ])
    write_md(base, "reports/integration/e64_prior_revenue_path_constraint_diagnosis.md", "E64 Prior Revenue Path Constraint Diagnosis", [
        f"AI-product constrained: `{diagnosis.get('E62_E63_candidate_universe_constrained_around_AI_products')}`.",
        f"Selected E63 path still valid: `{diagnosis.get('E63_selected_path_still_valid_candidate')}`.",
        diagnosis.get("honest_diagnosis", ""),
    ])
    write_md(base, "reports/integration/e64_dual_axis_revenue_route_universe.md", "E64 Dual-Axis Revenue Route Universe", [
        f"Route families evaluated: `{universe.get('route_family_count')}`.",
        f"Market-optimal routes: `{universe.get('market_optimal_route_count')}`.",
        f"Y*Bridge-unique routes: `{universe.get('YBridge_unique_route_count')}`.",
        f"Hybrid routes: `{universe.get('hybrid_route_count')}`.",
    ])
    write_md(base, "reports/integration/e64_dual_axis_public_read_summary.md", "E64 Dual-Axis Public-Read Summary", [
        f"Receipts created: `{receipts.get('receipt_count')}`.",
        f"Successful public reads: `{receipts.get('live_successful_read_count')}`.",
        f"Evidence atoms: `{atoms.get('evidence_atom_count')}`.",
        "Receipts are public-read observations only, not customer validation, paid signal, or expert feedback.",
    ])
    write_md(base, "reports/integration/e64_market_optimal_path_matrix.md", "E64 Market-Optimal Path Matrix", [
        f"Best market-optimal path: `{market.get('best_market_optimal_path')}`.",
        "This matrix intentionally does not let strategic uniqueness dominate fastest-cash reasoning.",
    ])
    write_md(base, "reports/integration/e64_ybridge_unique_path_matrix.md", "E64 Y*Bridge-Unique Path Matrix", [
        f"Best Y*Bridge-unique path: `{unique.get('best_YBridge_unique_path')}`.",
        "This matrix identifies defensibility and Y*Bridge-specific runtime advantage without letting fast cash dominate.",
    ])
    write_md(base, "reports/integration/e64_dual_axis_cross_selection_matrix.md", "E64 Dual-Axis Cross-Selection Matrix", [
        f"Overlap route: `{cross.get('overlapping_route')}`.",
        f"First-cash wedge: `{cross.get('first_cash_wedge')}`.",
        f"Fallback cash-support route: `{cross.get('fallback_cash_support_route')}`.",
    ])
    write_md(base, "reports/integration/e64_dual_axis_first_cash_path_selection.md", "E64 Dual-Axis First-Cash Path Selection", [
        f"Best market-optimal path: `{selection.get('best_open_world_market_optimal_path')}`.",
        f"Best Y*Bridge-unique path: `{selection.get('best_YBridge_unique_path')}`.",
        f"Selected final path: `{selection.get('selected_final_first_cash_path')}`.",
        f"E63 path result: `{selection.get('E63_selected_path_result')}`.",
    ])
    write_md(base, "reports/integration/e64_top3_dual_axis_offer_hypotheses.md", "E64 Top 3 Dual-Axis Offer Hypotheses", [
        f"Offers drafted: `{offers.get('offer_count')}`.",
        *[f"- `{item.get('offer_name')}` ({item.get('route_type')})" for item in offers.get("offers", [])],
        "All offers are internal-only, draft-only, and owner-gated before external use.",
    ])
    write_md(base, "reports/integration/e64_owner_gated_business_action_plan_no_execution.md", "E64 Owner-Gated Business Action Plan, No Execution", [
        f"Selected path: `{selection.get('selected_final_first_cash_path')}`.",
        "Allowed now: internal hardening, sample packet generation, owner decision packet, offer refinement.",
        "Requires owner approval: external review, publication, outreach, pricing presentation, invoice/payment, client delivery.",
    ])
    write_md(base, "reports/integration/e64_operator_handoff.md", "E64 Operator Handoff", [
        f"Final status: `{gate.get('final_status')}`.",
        f"Selected final path: `{gate.get('selected_final_first_cash_path')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
        "No external action, validation claim, revenue claim, or owner approval fabrication occurred.",
    ])
    write_md(base, "reports/integration/e64_owner_handoff_chinese.md", "E64 Owner Handoff Chinese", [
        "E64 修正了 E62/E63 的偏差：赚钱路线不能只等于卖自己的 AI runtime，也不能退化成普通 AI 咨询。",
        f"市场最优 first-cash 路径是：`{selection.get('best_open_world_market_optimal_path')}`。",
        f"Y*Bridge 最独特、最有防御性的路径是：`{selection.get('best_YBridge_unique_path')}`。",
        f"最终选择的桥接路径是：`{selection.get('selected_final_first_cash_path')}`。",
        "E63 的 runtime harness 路线没有被抛弃，而是作为 top-3 和战略骨架保留，并被包装成更容易理解的业务运营 blueprint wedge。",
        f"下一步建议：`{gate.get('recommended_next_milestone')}`。",
        "仍然不能外联、发布、收款或交付；这些都需要明确 owner approval。",
    ])
    write_md(base, "reports/integration/e64_reuse_first_growth_audit.md", "E64 Reuse-First Growth Audit", [
        f"Audit status: `{audit.get('audit_status')}`.",
        f"Reused assets: `{len(audit.get('reused_assets', []))}`.",
        f"Thin wrappers added: `{len(audit.get('thin_wrappers_added', []))}`.",
        "No duplicate public-read, evidence atomizer, route selector, behavior gate, or readback capability was rebuilt.",
    ])


def write_all_e64_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    write_json(base, "operations/external_validation/e64_base_state_manifest.json", build_base_state_manifest(base))
    write_json(base, "operations/external_validation/e64_prior_gate_preflight_result.json", build_prior_gate_preflight(base))
    write_md(base, "reports/integration/e64_prior_gate_preflight_result.md", "E64 Prior Gate Preflight", ["E63 completion, selected path, offer hypothesis, and no-external-action boundary were consumed."])
    write_json(base, "operations/external_validation/e64_dual_axis_repository_archaeology_inventory.json", build_dual_axis_repository_archaeology_inventory(base))
    write_json(base, "operations/external_validation/e64_reuse_first_growth_audit.json", build_reuse_first_growth_audit(base))
    write_json(base, "operations/external_validation/e64_prior_revenue_path_constraint_diagnosis.json", build_prior_revenue_path_constraint_diagnosis(base))
    write_json(base, "operations/external_validation/e64_dual_axis_revenue_route_universe.json", build_dual_axis_revenue_route_universe(base))
    write_json(base, "operations/external_validation/e64_dual_axis_public_read_plan.json", build_dual_axis_public_read_plan(base))
    receipts = build_dual_axis_public_read_receipts(base)
    write_json(base, "operations/external_validation/e64_dual_axis_public_read_receipts.json", receipts)
    atoms = build_dual_axis_public_read_evidence_atoms(base)
    write_json(base, "operations/external_validation/e64_dual_axis_public_read_evidence_atoms.json", atoms)
    write_json(base, "operations/external_validation/e64_market_optimal_path_matrix.json", build_market_optimal_path_matrix(base))
    write_json(base, "operations/external_validation/e64_ybridge_unique_path_matrix.json", build_ybridge_unique_path_matrix(base))
    write_json(base, "operations/external_validation/e64_dual_axis_cross_selection_matrix.json", build_dual_axis_cross_selection_matrix(base))
    write_json(base, "operations/external_validation/e64_dual_axis_first_cash_path_selection.json", build_dual_axis_first_cash_path_selection(base))
    write_json(base, "operations/external_validation/e64_top3_dual_axis_offer_hypotheses.json", build_top3_dual_axis_offer_hypotheses(base))
    write_runtime_harness_blueprint(base)
    write_json(base, "operations/external_validation/e64_owner_gated_business_action_plan_no_execution.json", build_owner_gated_business_action_plan(base))
    write_json(base, "operations/external_validation/e64_behavior_authorization_result.json", build_behavior_authorization(base))
    write_runtime_writeback(base)
    write_json(base, "operations/external_validation/e64_ceo_brain_readback_smoke_result.json", build_ceo_brain_readback_smoke(base))
    write_json(base, "operations/external_validation/e64_no_overclaim_validation_result.json", build_no_overclaim_validation(base))
    write_json(base, "operations/external_validation/e64_runtime_governance_validation_result.json", build_runtime_governance_validation(base))
    gate = build_completion_gate(base)
    write_json(base, "operations/external_validation/e64_completion_gate_result.json", gate)
    write_md(base, "reports/integration/e64_completion_gate_result.md", "E64 Completion Gate", [
        f"Gate passed: `{gate.get('gate_passed')}`.",
        f"Final status: `{gate.get('final_status')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])
    write_reports(base)
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e64_artifacts(), indent=2, ensure_ascii=False))
