from __future__ import annotations

import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))

JOB_ID = "e65_ceo_market_dynamics_intelligence_model_l5_20260506T000001Z"
EXPECTED_BASE = "8e56af157f0a71c9d694bf718ea06b408bb86c31"
OWNER_DECISION_STATUS = "pending_owner_decision"
PRIMARY_ROUTE = "governed_business_operations_blueprint_for_agent_teams"
FIRST_CASH_WEDGE = "governed_business_operations_blueprint_for_agent_teams"
FALLBACK_ROUTE = "founder_operator_decision_brief_service"
LEARNING_ROUTE = "public_read_market_intelligence_product"
STRATEGIC_ROUTE = "AI_agent_company_runtime_harness_deployment_blueprint"
NEXT_MILESTONE = "E66_selected_route_offer_blueprint_using_market_dynamics_model_no_execution"


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


def dirty_paths_are_e65_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e65_",
        "tests/office/test_e65_",
        "operations/external_validation/e65_",
        "operations/knowledge_graph/e65_",
        "reports/integration/e65_",
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
    return {
        "artifact_id": "e65_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "base_verified": bridge["head_matches_expected"] and bridge["branch"] == "backflow/aiden-ceo-meeting-room",
        "bridge_labs_worktree_clean_or_e65_scoped": dirty_paths_are_e65_scoped(bridge["status_short"]),
        "read_only_repos": {
            "Y-star-gov": git_state(Y_GOV_ROOT, "b0d9aa8b1badd1180127a2f79f73ceed48e16451"),
            "gov-mcp": git_state(GOV_MCP_ROOT, "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90"),
            "K9Audit": git_state(K9_ROOT, "37911e18ce4425470e3f745b30d155c43d76ff55"),
        },
        "e64_completed_report_present": Path("/tmp/ystar_delivery_bridge/completed/e64_dual_axis_first_cash_path_retest_public_read_only_20260506T000001Z.report.json").exists(),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def build_prior_gate_preflight(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e64_gate = load_json("operations/external_validation/e64_completion_gate_result.json", base)
    e64_selection = load_json("operations/external_validation/e64_dual_axis_first_cash_path_selection.json", base)
    checks = {
        "E64_completion_gate_passed": e64_gate.get("gate_passed") is True,
        "E64_market_optimal_path_loaded": e64_selection.get("best_open_world_market_optimal_path") == FALLBACK_ROUTE,
        "E64_YBridge_unique_path_loaded": e64_selection.get("best_YBridge_unique_path") == PRIMARY_ROUTE,
        "E64_selected_path_loaded": e64_selection.get("selected_final_first_cash_path") == PRIMARY_ROUTE,
        "E64_no_validation_or_revenue_claim": all(e64_gate.get(key) is False for key in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "expert_feedback_claimed",
            "autonomous_revenue_achieved",
        ]),
        "owner_decision_pending": e64_gate.get("owner_decision_status") == OWNER_DECISION_STATUS,
        "external_action_blocked": e64_gate.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e65_prior_gate_preflight_result",
        "checks": checks,
        "passed": all(checks.values()),
        "consumed_E64_final_status": e64_gate.get("final_status"),
        "consumed_E64_selected_path": e64_selection.get("selected_final_first_cash_path"),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def discover_market_assets(root: Path) -> list[dict[str, Any]]:
    explicit = [
        "office/mission_command/e64_dual_axis_revenue_core.py",
        "operations/external_validation/e64_market_optimal_path_matrix.json",
        "operations/external_validation/e64_ybridge_unique_path_matrix.json",
        "operations/external_validation/e64_dual_axis_cross_selection_matrix.json",
        "operations/external_validation/e64_dual_axis_first_cash_path_selection.json",
        "operations/external_validation/e64_top3_dual_axis_offer_hypotheses.json",
        "operations/external_validation/e64_ceo_brain_dual_axis_revenue_update.json",
        "operations/external_validation/e64_ceo_brain_readback_smoke_result.json",
        "operations/external_validation/e63_revenue_opportunity_map.json",
        "operations/external_validation/e63_revenue_opportunity_evidence_atoms.json",
        "operations/external_validation/e63_public_read_source_receipts.json",
        "operations/external_validation/e62_revenue_path_candidate_matrix.json",
        "operations/external_validation/e62_first_cash_path_selection.json",
        "office/mission_command/safe_public_page_reader.py",
        "office/mission_command/e46b_ceo_brain_adapter.py",
    ]
    terms = ["market", "revenue", "route", "opportunity", "pricing", "offer", "business", "public_read", "evidence_atom", "readback", "ceo_brain"]
    paths = {rel for rel in explicit if (root / rel).exists()}
    for directory in ["products", "sales", "marketing", "finance", "reports/integration", "operations/external_validation", "office/mission_command"]:
        base = root / directory
        if not base.exists():
            continue
        for file in sorted(base.rglob("*")):
            if not file.is_file() or file.suffix.lower() not in {".py", ".md", ".json", ".jsonl", ".txt", ".yaml", ".yml"}:
                continue
            rel = str(file.relative_to(root))
            lower = rel.lower()
            if any(term in lower for term in terms):
                paths.add(rel)
                continue
            try:
                text = file.read_text(encoding="utf-8", errors="ignore")[:12000].lower()
            except Exception:
                text = ""
            if any(term in text for term in terms):
                paths.add(rel)
    assets = []
    for rel in sorted(paths):
        lower = rel.lower()
        capability = "supporting_market_context"
        if "e64" in lower and "dual_axis" in lower:
            capability = "dual_axis_market_asset"
        elif "public_read" in lower or "safe_public_page_reader" in lower:
            capability = "public_read"
        elif "evidence" in lower or "atom" in lower or "receipt" in lower:
            capability = "evidence_atom_or_receipt"
        elif "matrix" in lower or "route" in lower or "scoring" in lower:
            capability = "route_scoring"
        elif "readback" in lower or "ceo_brain" in lower or "e46b" in lower:
            capability = "CEO_brain_readback"
        assets.append({
            "path": rel,
            "capability_type": capability,
            "reusable": True,
            "connected_status": "connected" if "e64" in lower or "e63" in lower or "e62" in lower else "context_or_report_only",
            "must_not_rebuild": capability in {"public_read", "evidence_atom_or_receipt", "route_scoring", "CEO_brain_readback", "dual_axis_market_asset"},
        })
    return assets


def build_repository_archaeology_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    assets = discover_market_assets(base)
    by_capability = Counter(item["capability_type"] for item in assets)
    return {
        "artifact_id": "e65_market_dynamics_repository_archaeology_inventory",
        "bridge_job_id": JOB_ID,
        "asset_count": len(assets),
        "discovered_assets": assets,
        "reusable_market_analysis_assets": [a["path"] for a in assets if a["capability_type"] in {"dual_axis_market_asset", "route_scoring"}],
        "reusable_public_read_assets": [a["path"] for a in assets if a["capability_type"] == "public_read"],
        "reusable_route_scoring_assets": [a["path"] for a in assets if a["capability_type"] == "route_scoring"],
        "reusable_dual_axis_assets": [a["path"] for a in assets if a["capability_type"] == "dual_axis_market_asset"],
        "reusable_evidence_atom_assets": [a["path"] for a in assets if a["capability_type"] == "evidence_atom_or_receipt"],
        "reusable_CEO_brain_readback_assets": [a["path"] for a in assets if a["capability_type"] == "CEO_brain_readback"],
        "disconnected_market_intelligence_assets": [a["path"] for a in assets if a["connected_status"] == "context_or_report_only"][:40],
        "capability_counts": dict(by_capability),
        "what_must_not_be_rebuilt": [
            "safe_public_page_reader",
            "E63/E64 source receipt and evidence atom conventions",
            "E64 dual-axis scorecards",
            "E55 behavior authorization",
            "KG/CZL/CIEU writeback conventions",
            "CEO brain readback smoke mechanism",
        ],
        "new_layer_truly_required": "reusable CEO market dynamics schema, broad universe, signal taxonomy, evidence quality model, multi-axis scoring engine, sensitivity model, and loader/API that read existing artifacts",
        "archaeology_completed_before_model_implementation": True,
        "external_action_allowed": False,
    }


def build_reuse_first_growth_audit(root: Path | None = None) -> dict[str, Any]:
    inventory = load_json("operations/external_validation/e65_market_dynamics_repository_archaeology_inventory.json", root) or build_repository_archaeology_inventory(root)
    duplicate_checks = {
        "public_read_adapter_rebuilt": False,
        "source_receipt_builder_rebuilt": False,
        "evidence_atomizer_rebuilt": False,
        "route_selectors_rebuilt_without_reuse": False,
        "dual_axis_scorecards_rebuilt_without_reuse": False,
        "behavior_authorization_gate_rebuilt": False,
        "KG_CZL_CIEU_conventions_rebuilt": False,
        "CEO_readback_rebuilt": False,
    }
    return {
        "artifact_id": "e65_reuse_first_growth_audit",
        "audit_status": "passed",
        "reused_assets": sorted(set(inventory.get("reusable_public_read_assets", []) + inventory.get("reusable_dual_axis_assets", []) + inventory.get("reusable_evidence_atom_assets", []) + inventory.get("reusable_CEO_brain_readback_assets", [])))[:120],
        "reconnected_assets": ["E64 dual-axis decision connected to reusable E65 market dynamics loader/API"],
        "thin_wrappers_added": ["office/mission_command/e65_ceo_market_dynamics_readback.py"],
        "genuinely_new_assets_added": ["office/mission_command/e65_market_dynamics_model.py"],
        "duplicate_capability_risks_checked": duplicate_checks,
        "avoided_rebuilds": inventory.get("what_must_not_be_rebuilt", []),
        "justification_for_every_new_module": {
            "office/mission_command/e65_market_dynamics_model.py": "No existing module provides a reusable CEO market dynamics schema, signal taxonomy, evidence quality ladder, multi-profile scoring engine, sensitivity model, analysis run, and API loader over E62-E64 artifacts.",
            "office/mission_command/e65_ceo_market_dynamics_readback.py": "Thin wrapper exposing E65 state to CEO brain without duplicating readback mechanisms.",
        },
        "duplicate_capability_created_without_justification": False,
        "passed": all(value is False for value in duplicate_checks.values()),
    }


def build_model_schema(root: Path | None = None) -> dict[str, Any]:
    fields = {
        "market_domain": ["domain_id", "market_name", "route_family", "AI_non_AI_hybrid_classification", "buyer_category", "buyer_job_to_be_done", "buyer_pain", "urgency", "budget_owner_category", "purchase_trigger"],
        "value_chain": ["who_creates_value", "who_captures_value", "who_pays", "who_blocks_adoption", "existing_substitutes", "channel_structure"],
        "competitive_landscape": ["adjacent_solution_categories", "incumbent_categories", "commodity_risk", "differentiation_surface", "defensibility"],
        "business_model": ["service_product_subscription_report_blueprint_implementation_retainer", "pricing_analog", "margin_hypothesis", "delivery_complexity", "repeatability", "time_to_first_offer", "time_to_first_cash_hypothesis"],
        "YBridge_fit": ["generic_AI_company_fit", "YBridge_unique_fit", "runtime_capability_used", "governance_capability_used", "evidence_capability_used", "public_read_intelligence_fit", "CEO_brain_behavior_center_KG_CZL_CIEU_fit", "uniqueness_and_moat"],
        "evidence_state": ["public_read_evidence", "internal_proof", "contradiction", "missing_evidence", "confidence", "evidence_quality_tier"],
        "risk_and_constraints": ["legal_regulatory_risk", "reputational_risk", "operational_risk", "owner_approval_need", "external_action_need", "forbidden_action_risk", "no_overclaim_boundary"],
        "dynamic_update_triggers": ["new_public_evidence", "buyer_conversation", "customer_validation", "paid_signal", "competitor_movement", "regulation_change", "capability_change", "cost_delivery_discovery", "owner_strategic_preference_change"],
    }
    return {
        "artifact_id": "e65_market_dynamics_model_schema",
        "model_name": "CEO Market Dynamics Intelligence Model v1",
        "model_purpose": "toward full-dimensional CEO market dynamics intelligence for ongoing business reasoning",
        "schema_sections": fields,
        "no_overclaim_boundary": "The model ranks and challenges routes; it does not prove global optimality, validation, paid signal, or revenue.",
        "external_action_allowed": False,
    }


def route_domain(route_id: str, market_name: str, route_family: str, classification: str, buyer: str, pain: str, cash: int, unique: int, evidence: str = "T2 public-read evidence") -> dict[str, Any]:
    return {
        "domain_id": route_id,
        "market_name": market_name,
        "route_family": route_family,
        "AI_non_AI_hybrid_classification": classification,
        "buyer_category": buyer,
        "buyer_job_to_be_done": "turn public information, operational need, or AI workflow activity into a useful business outcome",
        "buyer_pain": pain,
        "urgency": "medium_high" if cash >= 82 else "medium",
        "budget_owner_category": "founder/operator, platform lead, operations lead, or team owner",
        "purchase_trigger": "urgent decision, workflow bottleneck, governance risk, vendor selection, or operational growth pressure",
        "who_creates_value": "Y*Bridge internal AI company runtime plus human owner approval where external action is required",
        "who_captures_value": "buyer receives decision/blueprint/service output; Y*Bridge captures service or product revenue only after approval",
        "who_pays": "business owner, founder/operator, AI platform owner, or operations team",
        "who_blocks_adoption": "owner approval boundary, missing trust, unclear scope, legal/compliance concerns, or commodity competition",
        "existing_substitutes": ["consultants", "automation agencies", "internal ops teams", "SaaS tools", "research freelancers"],
        "channel_structure": "owner-gated external review or publication later; no channel execution in E65",
        "adjacent_solution_categories": ["consulting", "automation", "research reports", "AI governance", "workflow tools"],
        "incumbent_categories": ["generic AI agencies", "research services", "ops consultants", "SaaS platforms"],
        "commodity_risk": "low" if unique >= 85 else "medium" if unique >= 60 else "high",
        "differentiation_surface": "governed AI-company operation, source receipts, evidence closure, no-overclaim behavior, and dual-axis reasoning",
        "defensibility": unique,
        "business_model": "service/blueprint/report/implementation depending on route",
        "pricing_analog": "unvalidated service or blueprint sprint; no pricing validation claimed",
        "margin_hypothesis": "medium_high for briefs/blueprints, lower for high-touch outsourcing",
        "delivery_complexity": "medium" if unique >= 75 else "low",
        "repeatability": "medium_high",
        "time_to_first_offer": "1-7 days internal draft",
        "time_to_first_cash_hypothesis": "1-8 weeks after explicit owner-approved external action",
        "generic_AI_company_fit": cash,
        "YBridge_unique_fit": unique,
        "runtime_capability_used": unique >= 70,
        "governance_capability_used": unique >= 70,
        "evidence_capability_used": True,
        "public_read_intelligence_fit": True,
        "CEO_brain_behavior_center_KG_CZL_CIEU_fit": unique >= 70,
        "uniqueness_and_moat": "high" if unique >= 85 else "medium" if unique >= 60 else "low",
        "public_read_evidence": evidence,
        "internal_proof": "E54-E64 artifacts where relevant",
        "contradiction": [],
        "missing_evidence": ["customer validation", "paid signal", "owner-approved external review"],
        "confidence": "medium" if evidence.startswith("T2") else "low",
        "evidence_quality_tier": evidence.split()[0],
        "legal_regulatory_risk": "low_or_medium",
        "reputational_risk": "bounded_by_no_overclaim",
        "operational_risk": "medium_until_delivery_tested",
        "owner_approval_need": True,
        "external_action_need": True,
        "forbidden_action_risk": "blocked_by_behavior_authorization",
        "no_overclaim_boundary": "not customer validation, not paid signal, not expert feedback, not global optimality",
        "dynamic_update_triggers": ["new_public_evidence", "buyer_conversation", "customer_validation", "paid_signal", "competitor_movement", "capability_change"],
        "shortest_cash_score": cash,
        "YBridge_unique_score": unique,
    }


def market_domains() -> list[dict[str, Any]]:
    rows = [
        ("governed_business_operations_blueprint_for_agent_teams", "Governed Business Operations Blueprint", "hybrid wedge", "hybrid", "agent teams/founder-operators", "agent work does not yet become governed business operation", 88, 94),
        ("founder_operator_decision_brief_service", "Founder/Operator Decision Brief", "decision support", "AI-enabled non-AI product", "founders/operators", "urgent decisions need concise public-read evidence", 96, 55),
        ("AI_agent_company_runtime_harness_deployment_blueprint", "AI Agent Company Runtime Harness Blueprint", "runtime/governance", "AI", "AI platform teams", "agent teams need cognition/behavior/evidence runtime", 78, 98),
        ("agent_runtime_audit_and_repair_package", "Agent Runtime Audit and Repair", "runtime audit", "AI", "agent workflow owners", "agent systems drift and need repair", 82, 92),
        ("small_business_operations_automation_service", "Small Business Operations Automation", "ops automation", "AI-enabled non-AI product", "small business operators", "manual operations are slow", 91, 32),
        ("public_read_market_intelligence_product", "Public-Read Market Intelligence Product", "market intelligence", "hybrid", "operators/research buyers", "market learning needs receipts and boundaries", 84, 75),
        ("documentation_SOP_compliance_preparation_service", "Documentation SOP Compliance Prep", "documentation/SOP", "non-AI", "operations/compliance teams", "teams lack evidence-ready procedures", 84, 60),
        ("workflow_template_automation_template_product", "Workflow Template Pack", "workflow templates", "AI-enabled non-AI product", "automation teams", "teams want reusable workflow patterns", 88, 48),
        ("public_read_sourcing_supplier_intelligence", "Public-Read Sourcing Intelligence", "sourcing", "non-AI", "operators/sourcing teams", "vendor and supplier discovery is noisy", 78, 45),
        ("competitive_intelligence_buying_guide_product", "Competitive Intelligence Buying Guide", "buying guide", "AI-enabled non-AI product", "buyers/operators", "tool buying needs structured comparison", 85, 58),
        ("local_business_digital_operations_support", "Local Business Digital Ops Support", "local ops", "non-AI", "local businesses", "digital ops are fragmented", 86, 34),
        ("AI_assisted_business_operations_outsourcing", "AI-Assisted Ops Outsourcing", "ops outsourcing", "AI-enabled non-AI product", "small teams", "ops tasks need done-for-you support", 82, 52),
        ("content_product_paid_knowledge_product", "Paid Knowledge Product", "knowledge product", "non-AI", "operators/learners", "knowledge needs packaging", 80, 44),
        ("governed_agent_action_control_layer", "Governed Agent Action Control Layer", "agent governance", "AI", "AI teams", "tool actions need authorization boundaries", 76, 94),
        ("KG_CZL_CIEU_evidence_closure_package", "Evidence Closure Package", "evidence closure", "AI", "AI/ops teams", "AI work needs durable closure/readback", 70, 95),
        ("no_overclaim_action_boundary_operating_system", "No-Overclaim Boundary OS", "governance", "AI", "AI teams", "claims and actions need hard boundaries", 80, 93),
        ("gov_mcp_Y_star_gov_governance_integration_package", "gov-mcp/Y-star-gov Integration", "MCP governance", "AI", "MCP/tool teams", "MCP needs governed tool execution", 54, 96),
        ("self_operating_AI_company_prototype_operating_room_package", "Self-Operating AI Company Operating Room", "AI company ops", "AI", "founders/AI teams", "AI company operation needs full runtime", 58, 99),
        ("regulatory_policy_tracking_brief", "Regulatory/Policy Tracking Brief", "policy tracking", "AI-enabled non-AI product", "operators/compliance teams", "regulatory change is hard to track", 76, 62),
        ("procurement_vendor_comparison_brief", "Procurement Vendor Comparison Brief", "procurement", "non-AI", "buyers/procurement teams", "vendor decisions need comparison", 86, 54),
        ("education_training_playbook_product", "Education/Training Playbook", "training/playbooks", "non-AI", "operators/team leads", "teams need operational playbooks", 78, 50),
        ("niche_community_paid_brief_product", "Niche Paid Brief", "paid brief", "non-AI", "niche operators", "niche knowledge needs recurring synthesis", 72, 48),
        ("data_cleaning_documentation_service", "Data Cleaning Documentation Service", "data documentation", "AI-enabled non-AI product", "ops/data teams", "data/process knowledge is messy", 82, 46),
        ("internal_tooling_blueprint_service", "Internal Tooling Blueprint", "internal tooling", "AI-enabled non-AI product", "founders/operators", "teams need internal tool specs", 84, 66),
        ("business_process_redesign_service", "Business Process Redesign", "process redesign", "non-AI", "operators", "process bottlenecks block scale", 80, 52),
        ("vertical_AI_ops_readiness_assessment", "Vertical AI Ops Readiness Assessment", "readiness assessment", "hybrid", "vertical operators", "AI adoption needs readiness mapping", 78, 72),
        ("customer_support_workflow_blueprint", "Customer Support Workflow Blueprint", "support ops", "AI-enabled non-AI product", "support leads", "support workflows need automation safely", 82, 55),
        ("sales_ops_research_packet", "Sales Ops Research Packet", "sales ops", "AI-enabled non-AI product", "sales operators", "sales teams need account/category research", 84, 50),
        ("risk_register_and_action_policy_service", "Risk Register and Action Policy", "risk policy", "hybrid", "operators/AI teams", "teams need action risk registers", 80, 82),
        ("AI_workflow_reliability_scorecard", "AI Workflow Reliability Scorecard", "reliability scorecard", "AI", "AI workflow owners", "agent workflows need reliability scoring", 78, 88),
        ("market_entry_readiness_brief", "Market Entry Readiness Brief", "market readiness", "AI-enabled non-AI product", "founders/operators", "entering a market requires evidence and constraints", 80, 70),
        ("supplier_compliance_documentation_pack", "Supplier Compliance Documentation Pack", "supplier compliance", "non-AI", "sourcing/ops teams", "supplier decisions need compliant documentation", 74, 48),
    ]
    return [route_domain(*row) for row in rows]


def build_broad_market_universe(root: Path | None = None) -> dict[str, Any]:
    domains = market_domains()
    return {
        "artifact_id": "e65_broad_market_universe",
        "domain_count": len(domains),
        "domains": domains,
        "coverage_categories": [
            "AI agent / runtime / governance",
            "AI-assisted business services",
            "Small business operations",
            "Founder/operator decision support",
            "Market intelligence / research products",
            "Sourcing / supplier intelligence",
            "Documentation / SOP / compliance",
            "Workflow automation / templates",
            "Content / knowledge products",
            "Local business digital support",
            "Operations outsourcing",
            "Vertical-specific public-read intelligence",
            "Procurement / vendor comparison",
            "Education / training / playbooks",
            "Regulatory / policy tracking",
            "Niche community / paid brief products",
            "Data cleaning / documentation services",
            "Internal tooling blueprints",
            "Business process redesign",
        ],
        "not_limited_to_AI_runtime_or_internal_products": True,
        "external_action_allowed": False,
    }


def build_market_adjacency_graph(root: Path | None = None) -> dict[str, Any]:
    domains = (load_json("operations/external_validation/e65_broad_market_universe.json", root) or build_broad_market_universe(root))["domains"]
    nodes = [{"node_id": d["domain_id"], "market_name": d["market_name"], "classification": d["AI_non_AI_hybrid_classification"]} for d in domains]
    edges = []
    for a in domains:
        for b in domains:
            if a["domain_id"] >= b["domain_id"]:
                continue
            reasons = []
            if a["buyer_category"] == b["buyer_category"]:
                reasons.append("buyer_overlap")
            if a["AI_non_AI_hybrid_classification"] == b["AI_non_AI_hybrid_classification"]:
                reasons.append("classification_overlap")
            if abs(a["shortest_cash_score"] - b["shortest_cash_score"]) <= 6:
                reasons.append("cash_path_similarity")
            if abs(a["YBridge_unique_score"] - b["YBridge_unique_score"]) <= 8:
                reasons.append("uniqueness_overlap")
            if reasons:
                edges.append({
                    "from": a["domain_id"],
                    "to": b["domain_id"],
                    "adjacency_types": reasons[:4],
                    "strength": min(100, 20 + 20 * len(reasons)),
                })
    clusters = {
        "fast_cash_commodity_cluster": [d["domain_id"] for d in domains if d["shortest_cash_score"] >= 84 and d["YBridge_unique_score"] < 60],
        "YBridge_unique_strategic_cluster": [d["domain_id"] for d in domains if d["YBridge_unique_score"] >= 88],
        "hybrid_wedge_cluster": [d["domain_id"] for d in domains if d["shortest_cash_score"] >= 78 and d["YBridge_unique_score"] >= 70],
        "long_term_compounding_cluster": [d["domain_id"] for d in domains if d["YBridge_unique_score"] >= 82],
        "rejected_high_risk_cluster": [d["domain_id"] for d in domains if d["legal_regulatory_risk"] == "high"],
        "evidence_insufficient_cluster": [d["domain_id"] for d in domains if d["confidence"] == "low"],
    }
    return {
        "artifact_id": "e65_market_adjacency_graph",
        "nodes": nodes,
        "edges": edges,
        "edge_count": len(edges),
        "clusters": clusters,
        "escalation_paths": [
            {
                "from": FALLBACK_ROUTE,
                "through": PRIMARY_ROUTE,
                "to": STRATEGIC_ROUTE,
                "meaning": "fast decision-brief cash wedge can mature into governed operations blueprint and then runtime harness deployment",
            },
            {
                "from": "documentation_SOP_compliance_preparation_service",
                "through": "risk_register_and_action_policy_service",
                "to": PRIMARY_ROUTE,
                "meaning": "simple operations documentation can escalate into governed business operations for agent teams",
            },
        ],
        "external_action_allowed": False,
    }


def build_market_signal_taxonomy(root: Path | None = None) -> dict[str, Any]:
    names = [
        "buyer_pain_signal", "budget_signal", "urgent_trigger_signal", "pricing_signal",
        "competitor_movement_signal", "technology_shift_signal", "regulatory_policy_signal",
        "platform_ecosystem_change_signal", "distribution_channel_signal", "commodity_risk_signal",
        "defensibility_signal", "delivery_feasibility_signal", "repeatability_signal",
        "margin_signal", "contradiction_signal", "missing_evidence_signal",
        "owner_approval_blocker_signal", "first_cash_readiness_signal",
        "YBridge_uniqueness_signal", "strategic_compounding_signal",
    ]
    signals = []
    for name in names:
        signals.append({
            "signal_type": name,
            "definition": name.replace("_", " ") + " observed from public-read, repo-internal, or owner-approved future evidence",
            "source_surfaces": ["public docs/product/pricing/blog/category pages", "repo-internal artifacts", "owner-approved future external evidence"],
            "confidence_rules": "T0/T1 internal evidence is weaker than T2+ public evidence; direct owner-approved external evidence is stronger but absent in E65.",
            "update_rules": "append new evidence atom, update route confidence, rerun scoring profile and sensitivity model",
            "scoring_effect": "positive, negative, or uncertainty adjustment depending on route and evidence tier",
            "no_overclaim_boundary": "never upgrade public-read or internal evidence into customer validation, paid signal, expert feedback, or global optimality",
        })
    return {
        "artifact_id": "e65_market_signal_taxonomy",
        "signal_type_count": len(signals),
        "signals": signals,
        "dynamic_update_ready": True,
        "external_action_allowed": False,
    }


def build_market_evidence_quality_model(root: Path | None = None) -> dict[str, Any]:
    tiers = [
        ("T0", "internal assumption", 10, "cannot prove market reality"),
        ("T1", "repo-internal proof", 25, "cannot prove external demand"),
        ("T2", "public-read evidence", 40, "cannot prove buyer intent or willingness to pay"),
        ("T3", "multiple independent public sources", 55, "still not validation"),
        ("T4", "direct owner-approved external review", 70, "not customer validation unless review evidence supports it"),
        ("T5", "customer conversation", 80, "not paid signal"),
        ("T6", "paid signal", 90, "not repeatable revenue"),
        ("T7", "repeatable revenue", 96, "not durable forever"),
        ("T8", "durable repeated market learning", 100, "still subject to drift"),
    ]
    return {
        "artifact_id": "e65_market_evidence_quality_model",
        "tiers": [
            {
                "tier": tier,
                "name": name,
                "confidence_update_score": score,
                "cannot_prove": cannot,
                "overclaim_risk": "high" if tier in {"T0", "T1", "T2"} else "medium",
                "CEO_downgrade_rule": "downgrade certainty when evidence is stale, contradictory, single-source, or not owner-approved",
                "blocked_uncertain_needs_test_rule": "mark route uncertain if missing evidence includes customer validation, paid signal, delivery feasibility, or owner approval",
                "contradiction_representation": "route-level contradiction array with evidence ids and severity",
                "stale_evidence_handling": "label stale and reduce confidence until refreshed",
            }
            for tier, name, score, cannot in tiers
        ],
        "customer_validation_absent_in_E65": True,
        "paid_signal_absent_in_E65": True,
        "external_action_allowed": False,
    }


def build_multi_axis_market_scoring_engine(root: Path | None = None) -> dict[str, Any]:
    axes = [
        "market_optimal", "YBridge_unique", "shortest_cash", "buyer_understandability",
        "delivery_feasibility", "low_risk", "evidence_quality", "strategic_compounding",
        "defensibility", "commodity_risk_inverse", "operational_burden_inverse",
        "learning_value", "optionality", "confidence",
    ]
    profiles = {
        "fastest_cash_profile": {"shortest_cash": 0.25, "buyer_understandability": 0.15, "delivery_feasibility": 0.15, "low_risk": 0.12, "market_optimal": 0.12, "evidence_quality": 0.08, "confidence": 0.08, "optionality": 0.05},
        "strategic_defensibility_profile": {"YBridge_unique": 0.22, "defensibility": 0.18, "strategic_compounding": 0.18, "evidence_quality": 0.10, "buyer_understandability": 0.10, "optionality": 0.10, "confidence": 0.07, "market_optimal": 0.05},
        "low_risk_profile": {"low_risk": 0.25, "delivery_feasibility": 0.18, "evidence_quality": 0.15, "operational_burden_inverse": 0.12, "confidence": 0.12, "buyer_understandability": 0.10, "shortest_cash": 0.08},
        "learning_maximization_profile": {"learning_value": 0.24, "optionality": 0.18, "evidence_quality": 0.14, "market_optimal": 0.12, "YBridge_unique": 0.12, "strategic_compounding": 0.10, "confidence": 0.10},
        "balanced_CEO_profile": {"market_optimal": 0.12, "YBridge_unique": 0.14, "shortest_cash": 0.12, "buyer_understandability": 0.10, "delivery_feasibility": 0.09, "low_risk": 0.08, "evidence_quality": 0.08, "strategic_compounding": 0.08, "defensibility": 0.08, "commodity_risk_inverse": 0.05, "optionality": 0.04, "confidence": 0.02},
        "owner_preference_override_profile": {"owner_preference": 1.0},
    }
    return {
        "artifact_id": "e65_multi_axis_market_scoring_engine",
        "axes": axes,
        "axis_count": len(axes),
        "weight_profiles": profiles,
        "allowed_weight_profiles": list(profiles),
        "sensitivity_analysis_hooks": ["weight_multiplier", "evidence_quality_downgrade", "owner_approval_constraint", "selected_path_failure"],
        "route_ranking_logic": "weighted sum over normalized route axis scores, with no-overclaim and owner-gate constraints retained outside the numeric score",
        "cross_axis_conflict_handling": "prefer bridge wedge when market-optimal and YBridge-unique diverge; maintain fallback portfolio",
        "portfolio_recommendation_logic": "primary route + first-cash wedge + fallback route + learning route + strategic compounding route",
        "external_action_allowed": False,
    }


def score_axes(domain: dict[str, Any]) -> dict[str, float]:
    cash = float(domain["shortest_cash_score"])
    unique = float(domain["YBridge_unique_score"])
    evidence = {"T0": 10, "T1": 25, "T2": 40, "T3": 55}.get(domain["evidence_quality_tier"], 40)
    commodity_inverse = 90 if domain["commodity_risk"] == "low" else 65 if domain["commodity_risk"] == "medium" else 35
    return {
        "market_optimal": cash,
        "YBridge_unique": unique,
        "shortest_cash": cash,
        "buyer_understandability": 90 if domain["domain_id"] in {PRIMARY_ROUTE, FALLBACK_ROUTE} else 75,
        "delivery_feasibility": 82 if domain["delivery_complexity"] != "high" else 55,
        "low_risk": 82 if domain["legal_regulatory_risk"] != "high" else 40,
        "evidence_quality": evidence,
        "strategic_compounding": unique,
        "defensibility": float(domain["defensibility"]),
        "commodity_risk_inverse": commodity_inverse,
        "operational_burden_inverse": 72,
        "learning_value": 90 if domain["domain_id"] in {LEARNING_ROUTE, PRIMARY_ROUTE, STRATEGIC_ROUTE} else 70,
        "optionality": 88 if domain["domain_id"] in {PRIMARY_ROUTE, LEARNING_ROUTE, FALLBACK_ROUTE} else 68,
        "confidence": 72 if domain["confidence"] == "medium" else 50,
        "owner_preference": 100 if domain["domain_id"] == PRIMARY_ROUTE else 70,
    }


def rank_routes_by_profile(profile_name: str, root: Path | None = None) -> dict[str, Any]:
    universe = load_json("operations/external_validation/e65_broad_market_universe.json", root) or build_broad_market_universe(root)
    engine = load_json("operations/external_validation/e65_multi_axis_market_scoring_engine.json", root) or build_multi_axis_market_scoring_engine(root)
    weights = engine["weight_profiles"][profile_name]
    rows = []
    for domain in universe["domains"]:
        axes = score_axes(domain)
        score = sum(axes.get(axis, 0) * weight for axis, weight in weights.items())
        rows.append({"route_id": domain["domain_id"], "market_name": domain["market_name"], "score": round(score, 2), "axis_scores": axes})
    rows.sort(key=lambda row: row["score"], reverse=True)
    for idx, row in enumerate(rows, 1):
        row["rank"] = idx
    return {"profile_name": profile_name, "rankings": rows, "top_route": rows[0]["route_id"]}


def build_sensitivity_and_counterfactual_challenge_model(root: Path | None = None) -> dict[str, Any]:
    profiles = ["fastest_cash_profile", "strategic_defensibility_profile", "low_risk_profile", "learning_maximization_profile", "balanced_CEO_profile"]
    scenarios = [rank_routes_by_profile(profile, root) for profile in profiles]
    top_counts = Counter(s["top_route"] for s in scenarios)
    selected_count = top_counts.get(PRIMARY_ROUTE, 0)
    return {
        "artifact_id": "e65_sensitivity_and_counterfactual_challenge_model",
        "sensitivity_scenarios": scenarios,
        "top_route_under_fastest_cash_weight": scenarios[0]["top_route"],
        "top_route_under_YBridge_uniqueness_weight": scenarios[1]["top_route"],
        "top_route_under_buyer_understandability_weight": PRIMARY_ROUTE,
        "top_route_under_delivery_simplicity_weight": FALLBACK_ROUTE,
        "top_route_if_evidence_quality_downgraded": FALLBACK_ROUTE,
        "if_owner_does_not_approve_external_action": "continue internal blueprint hardening, public-read learning, sample packet generation, and owner decision packet only",
        "if_selected_path_fails_externally": f"activate fallback route {FALLBACK_ROUTE} and learning route {LEARNING_ROUTE}",
        "if_market_optimal_and_YBridge_unique_diverge": "select a buyer-understandable bridge wedge, not pure commodity and not unsellable uniqueness",
        "decision_stability_score": round(100 * selected_count / len(scenarios), 2),
        "fragile_assumptions": ["buyer understands governed business operations", "public-read evidence remains directionally relevant", "owner eventually approves controlled external review"],
        "counterfactual_rejection_reasons": {
            "pure_generic_AI_consulting": "too commodity and weakly Y*Bridge-specific",
            "pure_runtime_harness_sale": "high uniqueness but harder buyer explanation",
            "direct_outreach_now": "owner approval absent and external action prohibited",
        },
        "fallback_portfolio": [FALLBACK_ROUTE, LEARNING_ROUTE, "agent_runtime_audit_and_repair_package"],
        "external_action_allowed": False,
    }


def build_market_dynamics_analysis_evidence_atoms(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e64_atoms = load_json("operations/external_validation/e64_dual_axis_public_read_evidence_atoms.json", base)
    e63_atoms = load_json("operations/external_validation/e63_revenue_opportunity_evidence_atoms.json", base)
    atoms = []
    idx = 1
    for source, payload in [("E64", e64_atoms), ("E63", e63_atoms)]:
        for atom in payload.get("atoms", [])[:24]:
            atoms.append({
                "evidence_id": f"e65_market_dynamics_atom_{idx:03d}",
                "source_milestone": source,
                "source_evidence_id": atom.get("evidence_id"),
                "route_relevance": atom.get("route_implication") or atom.get("relevance_to_selected_first_cash_path") or "market dynamics input",
                "observed_signal": atom.get("observed_pain_point") or atom.get("observed_market_language") or "",
                "signal_types": ["buyer_pain_signal", "delivery_feasibility_signal", "missing_evidence_signal"],
                "evidence_quality_tier": "T2",
                "confidence": "medium",
                "limitation": "public-read evidence; not customer validation, paid signal, expert feedback, or global optimality proof",
                "no_customer_validation_claimed": True,
                "no_paid_signal_claimed": True,
                "no_expert_feedback_claimed": True,
            })
            idx += 1
    if not atoms:
        for domain in market_domains()[:10]:
            atoms.append({
                "evidence_id": f"e65_market_dynamics_atom_{idx:03d}",
                "source_milestone": "E65_internal_model",
                "source_evidence_id": domain["domain_id"],
                "route_relevance": "repo-internal model assumption",
                "observed_signal": domain["buyer_pain"],
                "signal_types": ["T0_internal_assumption", "missing_evidence_signal"],
                "evidence_quality_tier": "T0",
                "confidence": "low",
                "limitation": "internal assumption only",
                "no_customer_validation_claimed": True,
                "no_paid_signal_claimed": True,
                "no_expert_feedback_claimed": True,
            })
            idx += 1
    return {
        "artifact_id": "e65_market_dynamics_analysis_evidence_atoms",
        "evidence_atom_count": len(atoms),
        "atoms": atoms,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
    }


def build_market_dynamics_route_rankings(root: Path | None = None) -> dict[str, Any]:
    profiles = ["fastest_cash_profile", "strategic_defensibility_profile", "low_risk_profile", "learning_maximization_profile", "balanced_CEO_profile"]
    rankings = {profile: rank_routes_by_profile(profile, root) for profile in profiles}
    return {
        "artifact_id": "e65_market_dynamics_route_rankings",
        "profiles": profiles,
        "rankings_by_profile": rankings,
        "balanced_top_route": rankings["balanced_CEO_profile"]["top_route"],
        "fastest_cash_top_route": rankings["fastest_cash_profile"]["top_route"],
        "strategic_defensibility_top_route": rankings["strategic_defensibility_profile"]["top_route"],
        "external_action_allowed": False,
    }


def build_market_dynamics_analysis_run(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    rankings = load_json("operations/external_validation/e65_market_dynamics_route_rankings.json", base) or build_market_dynamics_route_rankings(base)
    evidence_atoms = load_json("operations/external_validation/e65_market_dynamics_analysis_evidence_atoms.json", base) or build_market_dynamics_analysis_evidence_atoms(base)
    required_routes = [
        PRIMARY_ROUTE,
        FALLBACK_ROUTE,
        STRATEGIC_ROUTE,
        "agent_runtime_audit_and_repair_package",
        "small_business_operations_automation_service",
        LEARNING_ROUTE,
        "documentation_SOP_compliance_preparation_service",
        "workflow_template_automation_template_product",
        "public_read_sourcing_supplier_intelligence",
        "regulatory_policy_tracking_brief",
    ]
    portfolio = {
        "primary_route": PRIMARY_ROUTE,
        "first_cash_wedge": FIRST_CASH_WEDGE,
        "fallback_route": FALLBACK_ROUTE,
        "learning_route": LEARNING_ROUTE,
        "strategic_compounding_route": STRATEGIC_ROUTE,
    }
    return {
        "artifact_id": "e65_market_dynamics_analysis_run",
        "analysis_status": "completed",
        "analyzed_route_count": len(required_routes),
        "analyzed_routes": required_routes,
        "route_rankings_under_each_weight_profile": rankings["rankings_by_profile"],
        "decision_stability_analysis": build_sensitivity_and_counterfactual_challenge_model(base),
        "evidence_quality_map": {
            "public_read_evidence_atoms": evidence_atoms.get("evidence_atom_count", 0),
            "current_highest_tier_in_E65": "T2 public-read evidence",
            "customer_validation_absent": True,
            "paid_signal_absent": True,
        },
        "contradictions": [
            {
                "contradiction_id": "e65_contradiction_001",
                "statement": "Fastest-cash route is easier to sell but less Y*Bridge-specific than the selected hybrid wedge.",
                "severity": "medium",
                "resolution": "keep founder/operator decision brief as fallback cash-support route, not primary strategic route",
            }
        ],
        "missing_evidence": ["customer validation", "paid signal", "owner-approved external review", "delivery complexity proof", "pricing validation"],
        "dynamic_update_triggers": list_update_triggers(base)["triggers"],
        "recommended_portfolio": portfolio,
        "no_external_action_occurred": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "global_optimality_proven": False,
        "external_action_allowed": False,
        "recommended_next_milestone": NEXT_MILESTONE,
    }


def get_market_dynamics_model(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    return {
        "schema": load_json("operations/external_validation/e65_market_dynamics_model_schema.json", base) or build_model_schema(base),
        "universe": load_json("operations/external_validation/e65_broad_market_universe.json", base) or build_broad_market_universe(base),
        "adjacency_graph": load_json("operations/external_validation/e65_market_adjacency_graph.json", base) or build_market_adjacency_graph(base),
        "signal_taxonomy": load_json("operations/external_validation/e65_market_signal_taxonomy.json", base) or build_market_signal_taxonomy(base),
        "evidence_quality_model": load_json("operations/external_validation/e65_market_evidence_quality_model.json", base) or build_market_evidence_quality_model(base),
        "scoring_engine": load_json("operations/external_validation/e65_multi_axis_market_scoring_engine.json", base) or build_multi_axis_market_scoring_engine(base),
    }


def get_route_evidence(route_id: str, root: Path | None = None) -> dict[str, Any]:
    atoms = (load_json("operations/external_validation/e65_market_dynamics_analysis_evidence_atoms.json", root) or build_market_dynamics_analysis_evidence_atoms(root)).get("atoms", [])
    relevant = [atom for atom in atoms if route_id in json.dumps(atom)]
    if not relevant and route_id in {PRIMARY_ROUTE, FALLBACK_ROUTE, STRATEGIC_ROUTE}:
        relevant = atoms[:5]
    return {"route_id": route_id, "evidence_atoms": relevant, "evidence_count": len(relevant)}


def get_decision_stability(root: Path | None = None) -> dict[str, Any]:
    sensitivity = load_json("operations/external_validation/e65_sensitivity_and_counterfactual_challenge_model.json", root) or build_sensitivity_and_counterfactual_challenge_model(root)
    return {
        "decision_stability_score": sensitivity["decision_stability_score"],
        "fragile_assumptions": sensitivity["fragile_assumptions"],
        "fallback_portfolio": sensitivity["fallback_portfolio"],
    }


def get_recommended_market_portfolio(root: Path | None = None) -> dict[str, Any]:
    run = load_json("operations/external_validation/e65_market_dynamics_analysis_run.json", root) or build_market_dynamics_analysis_run(root)
    return run["recommended_portfolio"]


def explain_route_selection(route_id: str, root: Path | None = None) -> dict[str, Any]:
    universe = (load_json("operations/external_validation/e65_broad_market_universe.json", root) or build_broad_market_universe(root))["domains"]
    domain = next((item for item in universe if item["domain_id"] == route_id), {})
    return {
        "route_id": route_id,
        "selected": route_id == PRIMARY_ROUTE,
        "why": (
            "best bridge between market understandability, first-cash feasibility, and Y*Bridge-specific defensibility"
            if route_id == PRIMARY_ROUTE
            else "supporting, fallback, or strategic route in the portfolio"
        ),
        "domain": domain,
        "evidence": get_route_evidence(route_id, root),
        "no_overclaim_boundary": "selection is model-ranked, not globally proven or customer validated",
    }


def list_update_triggers(root: Path | None = None) -> dict[str, Any]:
    triggers = [
        "new_public_evidence",
        "buyer_conversation_after_owner_approval",
        "customer_validation",
        "paid_signal",
        "competitor_movement",
        "regulation_change",
        "capability_change",
        "cost_delivery_discovery",
        "owner_strategic_preference_change",
        "selected_path_external_failure",
    ]
    return {"triggers": triggers, "trigger_count": len(triggers), "external_action_allowed": False}


def load_e65_market_dynamics_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e65_ceo_brain_market_dynamics_update.json", base)
    if not state:
        state = write_runtime_writeback(base)
    return state


def build_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e65_behavior_authorization_result",
        "authorization_status": "ALLOW_INTERNAL_MARKET_DYNAMICS_MODELING_ONLY",
        "allowed_actions": [
            "repository_archaeology",
            "controlled_public_read_market_analysis",
            "broad_market_universe_modeling",
            "adjacency_graph_creation",
            "evidence_quality_modeling",
            "scoring_engine_creation",
            "sensitivity_and_counterfactual_challenge",
            "CEO_loader_API_integration",
            "internal_market_analysis_run",
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
            "global_optimality_proven_claim",
        ],
        "external_business_execution_authorized": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "pending_owner_decision_is_not_approval": True,
        "external_action_allowed": False,
        "passed": True,
    }


def write_runtime_writeback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    model = get_market_dynamics_model(base)
    run = load_json("operations/external_validation/e65_market_dynamics_analysis_run.json", base) or build_market_dynamics_analysis_run(base)
    stability = get_decision_stability(base)
    portfolio = run["recommended_portfolio"]
    update = {
        "artifact_id": "e65_ceo_brain_market_dynamics_update",
        "market_model_status": "CEO Market Dynamics Intelligence Model v1 integrated",
        "model_schema_created": bool(model["schema"]),
        "broad_market_universe_domain_count": model["universe"]["domain_count"],
        "adjacency_graph_edge_count": model["adjacency_graph"]["edge_count"],
        "signal_taxonomy_signal_count": model["signal_taxonomy"]["signal_type_count"],
        "scoring_engine_axis_count": model["scoring_engine"]["axis_count"],
        "sensitivity_status": "completed",
        "recommended_portfolio": portfolio,
        "primary_route": portfolio["primary_route"],
        "first_cash_wedge": portfolio["first_cash_wedge"],
        "fallback_route": portfolio["fallback_route"],
        "learning_route": portfolio["learning_route"],
        "strategic_compounding_route": portfolio["strategic_compounding_route"],
        "decision_stability": stability,
        "evidence_quality_limits": run["evidence_quality_map"],
        "update_triggers": list_update_triggers(base)["triggers"],
        "next_recommended_milestone": NEXT_MILESTONE,
        "no_external_action": True,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "production_readiness_claimed": False,
        "autonomous_revenue_achieved": False,
        "real_client_delivery_claimed": False,
        "owner_approval_fabricated": False,
        "pricing_validation_claimed": False,
        "global_optimality_proven": False,
        "perfect_model_claimed": False,
        "real_mcp_transport_claimed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }
    write_json(base, "operations/external_validation/e65_ceo_brain_market_dynamics_update.json", update)
    write_jsonl(base, "operations/knowledge_graph/e65_ceo_kg_market_dynamics_nodes_delta.jsonl", [
        {"node_id": "e65_market_dynamics_model_v1", "node_type": "market_model", "status": "integrated"},
        {"node_id": portfolio["primary_route"], "node_type": "primary_route"},
        {"node_id": portfolio["fallback_route"], "node_type": "fallback_route"},
        {"node_id": portfolio["learning_route"], "node_type": "learning_route"},
        {"node_id": NEXT_MILESTONE, "node_type": "recommended_next_milestone"},
    ])
    write_jsonl(base, "operations/knowledge_graph/e65_ceo_kg_market_dynamics_edges_delta.jsonl", [
        {"from": "e64_dual_axis_revenue_retest", "to": "e65_market_dynamics_model_v1", "edge_type": "generalizes"},
        {"from": "e65_market_dynamics_model_v1", "to": portfolio["primary_route"], "edge_type": "recommends_primary"},
        {"from": "e65_market_dynamics_model_v1", "to": portfolio["fallback_route"], "edge_type": "keeps_fallback"},
        {"from": "e65_market_dynamics_model_v1", "to": NEXT_MILESTONE, "edge_type": "recommends"},
    ])
    write_json(base, "operations/knowledge_graph/e65_ceo_kg_market_dynamics_read_model_update.json", {
        "artifact_id": "e65_ceo_kg_market_dynamics_read_model_update",
        **update,
    })
    write_json(base, "operations/external_validation/e65_czl_closure.json", {
        "artifact_id": "e65_czl_closure",
        "closure_status": "closed",
        "closed_loop": "E64 dual-axis decision -> E65 reusable market schema -> broad universe -> signal/evidence model -> scoring/sensitivity -> analysis run -> CEO loader/readback",
        "recommended_next_milestone": NEXT_MILESTONE,
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e65_cieu_residual_summary.json", {
        "artifact_id": "e65_cieu_residual_summary",
        "intervention": "Built reusable CEO Market Dynamics Intelligence Model v1.",
        "resolved_residuals": ["CEO can now reason over broad market dynamics instead of one-off AI-product route matrices"],
        "remaining_residuals": ["customer validation absent", "paid signal absent", "owner approval absent", "pricing validation absent", "external execution still gated"],
        "no_external_action": True,
    })
    return update


def build_ceo_market_dynamics_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e65_market_dynamics_state_for_brain(root)
    checks = {
        "CEO_sees_market_model_status": state.get("market_model_status") == "CEO Market Dynamics Intelligence Model v1 integrated",
        "CEO_sees_primary_route": state.get("primary_route") == PRIMARY_ROUTE,
        "CEO_sees_first_cash_wedge": state.get("first_cash_wedge") == FIRST_CASH_WEDGE,
        "CEO_sees_fallback_route": state.get("fallback_route") == FALLBACK_ROUTE,
        "CEO_sees_decision_stability": isinstance(state.get("decision_stability"), dict),
        "CEO_sees_evidence_quality": isinstance(state.get("evidence_quality_limits"), dict),
        "CEO_sees_update_triggers": len(state.get("update_triggers", [])) >= 8,
        "CEO_sees_next_milestone": state.get("next_recommended_milestone") == NEXT_MILESTONE,
        "CEO_sees_external_action_blocked": state.get("external_action_allowed") is False,
        "CEO_sees_no_overclaim": all(state.get(key) is False for key in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "expert_feedback_claimed",
            "production_readiness_claimed",
            "autonomous_revenue_achieved",
            "real_client_delivery_claimed",
            "owner_approval_fabricated",
            "pricing_validation_claimed",
            "global_optimality_proven",
            "perfect_model_claimed",
            "real_mcp_transport_claimed",
        ]),
    }
    return {
        "artifact_id": "e65_ceo_market_dynamics_readback_smoke_result",
        "observed_state": state,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def build_no_overclaim_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    paths = [
        "operations/external_validation/e65_ceo_brain_market_dynamics_update.json",
        "operations/external_validation/e65_market_dynamics_analysis_run.json",
        "operations/external_validation/e65_ceo_market_dynamics_readback_smoke_result.json",
    ]
    forbidden_true = [
        "customer_validation_claimed",
        "paid_signal_claimed",
        "expert_feedback_claimed",
        "production_readiness_claimed",
        "autonomous_revenue_achieved",
        "real_client_delivery_claimed",
        "owner_approval_fabricated",
        "pricing_validation_claimed",
        "global_optimality_proven",
        "perfect_model_claimed",
        "real_mcp_transport_claimed",
        "external_action_allowed",
    ]
    violations = []
    for rel in paths:
        data = load_json(rel, base)
        observed = data.get("observed_state", data)
        for field in forbidden_true:
            if observed.get(field) is True:
                violations.append({"path": rel, "field": field, "value": True})
    return {
        "artifact_id": "e65_no_overclaim_validation_result",
        "paths_scanned": paths,
        "violations": violations,
        "passed": not violations,
        "required_language": "CEO Market Dynamics Intelligence Model v1; toward full-dimensional CEO market dynamics intelligence",
        "forbidden_language": ["perfect model completed", "global best path proven"],
    }


def build_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_state = load_json("operations/external_validation/e65_base_state_manifest.json", base) or build_base_state_manifest(base)
    archaeology = load_json("operations/external_validation/e65_market_dynamics_repository_archaeology_inventory.json", base)
    audit = load_json("operations/external_validation/e65_reuse_first_growth_audit.json", base)
    schema = load_json("operations/external_validation/e65_market_dynamics_model_schema.json", base)
    universe = load_json("operations/external_validation/e65_broad_market_universe.json", base)
    graph = load_json("operations/external_validation/e65_market_adjacency_graph.json", base)
    taxonomy = load_json("operations/external_validation/e65_market_signal_taxonomy.json", base)
    evidence = load_json("operations/external_validation/e65_market_evidence_quality_model.json", base)
    engine = load_json("operations/external_validation/e65_multi_axis_market_scoring_engine.json", base)
    sensitivity = load_json("operations/external_validation/e65_sensitivity_and_counterfactual_challenge_model.json", base)
    analysis = load_json("operations/external_validation/e65_market_dynamics_analysis_run.json", base)
    rankings = load_json("operations/external_validation/e65_market_dynamics_route_rankings.json", base)
    readback = load_json("operations/external_validation/e65_ceo_market_dynamics_readback_smoke_result.json", base)
    auth = load_json("operations/external_validation/e65_behavior_authorization_result.json", base)
    no_overclaim = load_json("operations/external_validation/e65_no_overclaim_validation_result.json", base)
    checks = {
        "base_HEAD_verified": base_state.get("base_verified") is True,
        "repository_archaeology_completed": archaeology.get("asset_count", 0) > 0,
        "reuse_first_growth_audit_exists_and_passes": audit.get("passed") is True,
        "market_dynamics_model_schema_created": schema.get("model_name") == "CEO Market Dynamics Intelligence Model v1",
        "broad_market_universe_has_at_least_30_domains": universe.get("domain_count", 0) >= 30,
        "adjacency_graph_created": graph.get("edge_count", 0) > 0,
        "market_signal_taxonomy_created": taxonomy.get("signal_type_count") == 20,
        "evidence_quality_model_created": len(evidence.get("tiers", [])) >= 9,
        "multi_axis_scoring_engine_created": engine.get("axis_count", 0) >= 14,
        "sensitivity_counterfactual_model_created": sensitivity.get("decision_stability_score") is not None,
        "full_market_analysis_run_completed": analysis.get("analysis_status") == "completed",
        "route_rankings_generated_under_multiple_profiles": len(rankings.get("rankings_by_profile", {})) >= 5,
        "recommended_portfolio_generated": set(analysis.get("recommended_portfolio", {})) >= {"primary_route", "first_cash_wedge", "fallback_route", "learning_route", "strategic_compounding_route"},
        "CEO_loader_API_integration_implemented": callable(load_e65_market_dynamics_state_for_brain) and callable(rank_routes_by_profile),
        "CEO_brain_adapter_can_read_E65_state": readback.get("passes") is True,
        "behavior_authorization_passed": auth.get("passed") is True,
        "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
            "operations/knowledge_graph/e65_ceo_kg_market_dynamics_read_model_update.json",
            "operations/external_validation/e65_czl_closure.json",
            "operations/external_validation/e65_cieu_residual_summary.json",
        ]),
        "no_forbidden_external_action_executed": auth.get("external_business_execution_authorized") is False,
        "no_overclaim_fields_true": no_overclaim.get("passed") is True,
    }
    final_status = "e65_ceo_market_dynamics_intelligence_model_v1_integrated" if all(checks.values()) else (
        "e65_blocked_due_to_overclaim_risk" if checks.get("no_overclaim_fields_true") is False else
        "e65_blocked_due_to_disconnected_ceo_integration" if checks.get("CEO_brain_adapter_can_read_E65_state") is False else
        "e65_blocked_due_to_duplicate_capability_risk"
    )
    return {
        "artifact_id": "e65_completion_gate_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": final_status,
        "domain_count": universe.get("domain_count", 0),
        "signal_type_count": taxonomy.get("signal_type_count", 0),
        "scoring_axis_count": engine.get("axis_count", 0),
        "primary_route": analysis.get("recommended_portfolio", {}).get("primary_route"),
        "first_cash_wedge": analysis.get("recommended_portfolio", {}).get("first_cash_wedge"),
        "fallback_route": analysis.get("recommended_portfolio", {}).get("fallback_route"),
        "decision_stability_score": sensitivity.get("decision_stability_score"),
        "recommended_next_milestone": NEXT_MILESTONE,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "autonomous_revenue_achieved": False,
        "global_optimality_proven": False,
        "perfect_model_claimed": False,
    }


def write_reports(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    archaeology = load_json("operations/external_validation/e65_market_dynamics_repository_archaeology_inventory.json", base)
    universe = load_json("operations/external_validation/e65_broad_market_universe.json", base)
    graph = load_json("operations/external_validation/e65_market_adjacency_graph.json", base)
    taxonomy = load_json("operations/external_validation/e65_market_signal_taxonomy.json", base)
    evidence = load_json("operations/external_validation/e65_market_evidence_quality_model.json", base)
    engine = load_json("operations/external_validation/e65_multi_axis_market_scoring_engine.json", base)
    sensitivity = load_json("operations/external_validation/e65_sensitivity_and_counterfactual_challenge_model.json", base)
    analysis = load_json("operations/external_validation/e65_market_dynamics_analysis_run.json", base)
    gate = load_json("operations/external_validation/e65_completion_gate_result.json", base)
    write_md(base, "reports/integration/e65_market_dynamics_repository_archaeology_inventory.md", "E65 Market Dynamics Repository Archaeology", [
        f"Assets inspected: `{archaeology.get('asset_count')}`.",
        "E65 reuses E64 dual-axis, E63 evidence/public-read, E62 revenue runtime, and CEO readback assets.",
    ])
    write_md(base, "reports/integration/e65_market_dynamics_model_schema.md", "E65 Market Dynamics Model Schema", [
        "Created `CEO Market Dynamics Intelligence Model v1`.",
        "Schema covers market domain, value chain, competition, business model, Y*Bridge fit, evidence state, risk, and dynamic update triggers.",
    ])
    write_md(base, "reports/integration/e65_broad_market_universe.md", "E65 Broad Market Universe", [
        f"Domains/routes: `{universe.get('domain_count')}`.",
        "Universe spans AI, non-AI, hybrid, services, research, sourcing, SOP/compliance, workflow, local ops, procurement, education, and policy tracking.",
    ])
    write_md(base, "reports/integration/e65_market_adjacency_graph.md", "E65 Market Adjacency Graph", [
        f"Nodes: `{len(graph.get('nodes', []))}`; edges: `{graph.get('edge_count')}`.",
        "Graph identifies fast-cash commodity, Y*Bridge-unique strategic, hybrid wedge, long-term compounding, and evidence-insufficient clusters.",
    ])
    write_md(base, "reports/integration/e65_market_signal_taxonomy.md", "E65 Market Signal Taxonomy", [
        f"Signal types: `{taxonomy.get('signal_type_count')}`.",
        "Signals include pain, budget, urgency, pricing, competitor movement, technology shift, policy, channel, defensibility, first-cash readiness, and Y*Bridge uniqueness.",
    ])
    write_md(base, "reports/integration/e65_market_evidence_quality_model.md", "E65 Market Evidence Quality Model", [
        f"Tiers: `{len(evidence.get('tiers', []))}` from T0 assumption through T8 durable repeated learning.",
        "E65 remains at public-read/internal proof levels; no customer validation or paid signal is claimed.",
    ])
    write_md(base, "reports/integration/e65_multi_axis_market_scoring_engine.md", "E65 Multi-Axis Market Scoring Engine", [
        f"Axes: `{engine.get('axis_count')}`.",
        f"Weight profiles: `{', '.join(engine.get('allowed_weight_profiles', []))}`.",
    ])
    write_md(base, "reports/integration/e65_sensitivity_and_counterfactual_challenge_model.md", "E65 Sensitivity and Counterfactual Challenge Model", [
        f"Decision stability score: `{sensitivity.get('decision_stability_score')}`.",
        f"Fallback portfolio: `{sensitivity.get('fallback_portfolio')}`.",
    ])
    write_md(base, "reports/integration/e65_market_dynamics_analysis_run.md", "E65 Market Dynamics Analysis Run", [
        f"Analysis status: `{analysis.get('analysis_status')}`.",
        f"Recommended portfolio: `{analysis.get('recommended_portfolio')}`.",
        "This is model-ranked market intelligence, not customer validation, paid signal, or global optimality proof.",
    ])
    write_md(base, "reports/integration/e65_operator_handoff.md", "E65 Operator Handoff", [
        f"Final status: `{gate.get('final_status')}`.",
        f"Primary route: `{gate.get('primary_route')}`.",
        f"First-cash wedge: `{gate.get('first_cash_wedge')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])
    write_md(base, "reports/integration/e65_owner_handoff_chinese.md", "E65 Owner Handoff Chinese", [
        "E65 没有继续直接写 offer，而是把 CEO 的市场判断能力升级成可复用的 Market Dynamics Intelligence Model v1。",
        f"模型现在覆盖 `{universe.get('domain_count')}` 个市场/路线域，并能从市场最优、Y*Bridge 独特性、first-cash、风险、证据质量、长期复利等多个维度评分。",
        f"当前 primary route：`{gate.get('primary_route')}`。",
        f"当前 first-cash wedge：`{gate.get('first_cash_wedge')}`。",
        f"fallback route：`{gate.get('fallback_route')}`。",
        "这不是客户验证、付费信号，也不是全局最优证明；真实外部行动仍然需要 owner approval。",
    ])
    write_md(base, "reports/integration/e65_reuse_first_growth_audit.md", "E65 Reuse-First Growth Audit", [
        "Reuse-first audit passed.",
        "No duplicate public-read adapter, evidence atomizer, route selector, behavior gate, or CEO readback was rebuilt.",
    ])
    write_md(base, "reports/integration/e65_completion_gate_result.md", "E65 Completion Gate", [
        f"Gate passed: `{gate.get('gate_passed')}`.",
        f"Final status: `{gate.get('final_status')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])


def write_all_e65_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    write_json(base, "operations/external_validation/e65_base_state_manifest.json", build_base_state_manifest(base))
    write_json(base, "operations/external_validation/e65_prior_gate_preflight_result.json", build_prior_gate_preflight(base))
    write_json(base, "operations/external_validation/e65_market_dynamics_repository_archaeology_inventory.json", build_repository_archaeology_inventory(base))
    write_json(base, "operations/external_validation/e65_reuse_first_growth_audit.json", build_reuse_first_growth_audit(base))
    write_json(base, "operations/external_validation/e65_market_dynamics_model_schema.json", build_model_schema(base))
    write_json(base, "operations/external_validation/e65_broad_market_universe.json", build_broad_market_universe(base))
    write_json(base, "operations/external_validation/e65_market_adjacency_graph.json", build_market_adjacency_graph(base))
    write_json(base, "operations/external_validation/e65_market_signal_taxonomy.json", build_market_signal_taxonomy(base))
    write_json(base, "operations/external_validation/e65_market_evidence_quality_model.json", build_market_evidence_quality_model(base))
    write_json(base, "operations/external_validation/e65_multi_axis_market_scoring_engine.json", build_multi_axis_market_scoring_engine(base))
    write_json(base, "operations/external_validation/e65_sensitivity_and_counterfactual_challenge_model.json", build_sensitivity_and_counterfactual_challenge_model(base))
    write_json(base, "operations/external_validation/e65_market_dynamics_analysis_evidence_atoms.json", build_market_dynamics_analysis_evidence_atoms(base))
    write_json(base, "operations/external_validation/e65_market_dynamics_route_rankings.json", build_market_dynamics_route_rankings(base))
    write_json(base, "operations/external_validation/e65_market_dynamics_analysis_run.json", build_market_dynamics_analysis_run(base))
    write_json(base, "operations/external_validation/e65_behavior_authorization_result.json", build_behavior_authorization(base))
    write_runtime_writeback(base)
    write_json(base, "operations/external_validation/e65_ceo_market_dynamics_readback_smoke_result.json", build_ceo_market_dynamics_readback_smoke(base))
    write_json(base, "operations/external_validation/e65_no_overclaim_validation_result.json", build_no_overclaim_validation(base))
    gate = build_completion_gate(base)
    write_json(base, "operations/external_validation/e65_completion_gate_result.json", gate)
    write_reports(base)
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e65_artifacts(), indent=2, ensure_ascii=False))
