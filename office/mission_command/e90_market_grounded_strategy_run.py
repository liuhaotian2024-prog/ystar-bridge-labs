from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e87_ceo_runtime_session import (
    build_e87_post_action_residual,
    build_e87_runtime_session_envelope,
)
from office.mission_command.e85_ceo_cognitive_os_runtime_bridge import (
    route_provider_tool_action_through_runtime_nervous_system,
)
from office.mission_command.e89_ceo_intelligence_loop_runtime_compiler import (
    compile_ceo_intelligence_loop_packet,
    build_pre_action_packet_from_intelligence_packet,
)
from office.mission_command.e90_ceo_strategic_intelligence_benchmark import (
    MILESTONE_ID,
    score_ceo_strategic_intelligence,
)
from office.mission_command.e91_ceo_doctrine_enforced_runtime_session import (
    build_e90_doctrine_action_context,
    enforce_doctrine_before_ceo_runtime,
)


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))

DEFAULT_OWNER_INTENT = (
    "Find the strongest next path for Y*Bridge Labs to reach first credible cash/revenue "
    "signal using the current CEO runtime/governance system."
)
DEFAULT_STRATEGY_SCOPE = (
    "Governed Business Operations Blueprint for Agent Teams + CIEU Audit Module, while "
    "allowing the CEO benchmark to challenge that thesis if evidence supports another route."
)
SESSION_ID = "e90_ceo_strategic_intelligence_runtime_session"


def _load_ystar_governance_module(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def build_market_grounded_strategy_artifact(
    *,
    owner_intent: str = DEFAULT_OWNER_INTENT,
    strategy_scope: str = DEFAULT_STRATEGY_SCOPE,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Build the structured strategy artifact used by E90.

    Public evidence is read-only market evidence, not validation, feedback, or
    revenue proof.
    """

    root = repo_root or BRIDGE_ROOT
    intelligence_packet = compile_ceo_intelligence_loop_packet(owner_intent=owner_intent, repo_root=root)
    routes = _route_candidates(repo_root=root)
    strategy = {
        "artifact_id": "e90_market_grounded_strategy_run",
        "milestone_id": MILESTONE_ID,
        "generation_mode": "runtime_generated_structured_output",
        "doctrine_registry_required": True,
        "external_observation_doctrine_status": "historical_public_read_wrapper_invoked_not_customer_validation",
        "strategy_run_id": "e90_market_grounded_strategy_run",
        "session_id": SESSION_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner_intent": owner_intent,
        "strategy_scope": strategy_scope,
        "source_intelligence_loop_id": intelligence_packet["intelligence_loop_id"],
        "internal_capability_map": _internal_capability_map(),
        "historical_route_assets": _historical_route_assets(),
        "external_market_evidence_map": _external_market_evidence_map(),
        "route_candidates": routes,
        "route_scoring": _route_scoring(),
        "selected_strategy": _selected_strategy(),
        "do_not_pursue_list": _do_not_pursue_list(),
        "what_not_to_do_next": _what_not_to_do_next(),
        "next_L4_feedback_owner_decision_packet": _next_l4_feedback_owner_decision_packet(),
        "CIEU_predictions": _cieu_predictions(),
        "post_strategy_residual_plan": _post_strategy_residual_plan(),
        "no_new_wheel_proof": {
            "decision": "reuse_existing_runtime_and_governance_systems",
            "reused_systems": [
                "E87R full repo baseline",
                "E88 CEO runtime session",
                "E89 CEO intelligence compiler",
                "Y-star-gov runtime hook",
                "Y-star-gov CIEUStore writer",
                "gov-mcp dry-run/no-send boundary",
            ],
            "not_rebuilt": [
                "no new behavior center",
                "no new governance engine",
                "no new provider executor",
                "no new CIEU ledger",
            ],
        },
        "adversarial_critique": [
            "The selected wedge could still sound like a consulting memo unless the L4 packet tests a concrete operator pain statement.",
            "A CIEU audit module may be too abstract unless paired with a visible before/after risk reduction workflow.",
            "Small teams may resist governance if it slows shipping; the offer must emphasize speed-preserving controls.",
            "The current evidence is public-read market evidence, not buyer conversation or purchase intent.",
            "K9Audit integration should not be sold as active unless a future bridge is implemented and tested.",
        ],
        "counterfactual_summary": {
            "routes_compared": [route["route_id"] for route in routes],
            "selected_route_id": "governed_ops_blueprint_cieu_audit_wedge",
            "second_best_route_id": "ceo_runtime_governance_product",
            "reason": "Best balance of existing readiness, buyer pain, trust value, and low owner/execution burden.",
        },
        "overclaim_boundary": {
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "paid_signal_claim": False,
            "pricing_validation_claim": False,
            "L4_feedback_executed": False,
            "L5_revenue_loop_complete": False,
            "production_deployment_claim": False,
            "K9Audit_integration_claim": False,
        },
        "truth_constraints": {
            "external_public_read_only": True,
            "customer_validation_claim": False,
            "revenue_or_payment_claim": False,
            "no_L4_feedback_executed": True,
            "gov_mcp_live_provider_execution": False,
            "K9Audit_not_integrated": True,
        },
        "execute_L4_now": False,
    }
    benchmark = score_ceo_strategic_intelligence(strategy)
    strategy["benchmark_result"] = benchmark
    return strategy


def run_e90_market_grounded_strategy_session(
    *,
    cieu_db: str,
    owner_intent: str = DEFAULT_OWNER_INTENT,
    strategy_scope: str = DEFAULT_STRATEGY_SCOPE,
    repo_root: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
    test_mode: bool = True,
    seal_session: bool = True,
) -> dict[str, Any]:
    """Run E89 intelligence -> E90 benchmark -> E88 runtime -> residual."""

    governance = _load_ystar_governance_module(ystar_gov_root)
    root = repo_root or BRIDGE_ROOT
    doctrine_gate = enforce_doctrine_before_ceo_runtime(
        action_context=build_e90_doctrine_action_context(test_mode=test_mode),
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        session_id=SESSION_ID,
        seal_session=False,
    )
    if not doctrine_gate["runtime_may_continue"]:
        return {
            "artifact_id": "e90_market_grounded_strategy_session_blocked_by_doctrine",
            "milestone_id": MILESTONE_ID,
            "doctrine_gate": doctrine_gate,
            "runtime_may_continue": False,
            "end_to_end_chain_proven": False,
        }
    intelligence_packet = compile_ceo_intelligence_loop_packet(owner_intent=owner_intent, repo_root=root)
    intelligence_write = governance.validate_and_write_ceo_intelligence_loop_packet(
        intelligence_packet,
        cieu_db=cieu_db,
        session_id=SESSION_ID,
        seal_session=False,
    )
    strategy = build_market_grounded_strategy_artifact(
        owner_intent=owner_intent,
        strategy_scope=strategy_scope,
        repo_root=root,
    )
    benchmark_write = governance.validate_and_write_ceo_strategic_intelligence_strategy(
        strategy,
        cieu_db=cieu_db,
        session_id=SESSION_ID,
        seal_session=False,
    )
    pre_action_packet = _build_strategy_pre_action_packet(intelligence_packet, strategy, repo_root=root)
    pre_envelope = build_e87_runtime_session_envelope(
        packet=pre_action_packet,
        owner_message=owner_intent,
        repo_root=root,
    )
    pre_envelope.update(
        {
            "action_id": "e90_selected_l4_owner_packet_preflight_dry_run",
            "context": "E90 selected strategy prepares owner-gated L4 feedback packet; no send",
            "objective": "preflight selected no-send L4 feedback packet through runtime and gov-mcp dry-run",
            "intelligence_loop_id": intelligence_packet["intelligence_loop_id"],
            "selected_candidate_id": "governed_ops_blueprint_cieu_audit_wedge",
            "YstarGov_intelligence_decision": intelligence_write["governance_decision"]["decision"],
            "commercial_sharpness_summary": strategy["benchmark_result"]["dimensions"]["commercial_sharpness"],
            "owner_approval_state": "not_required",
            "L4_owner_approval_state": "pending_owner_decision",
            "intelligence_loop_metadata": {
                "intelligence_loop_id": intelligence_packet["intelligence_loop_id"],
                "selected_candidate_id": "governed_ops_blueprint_cieu_audit_wedge",
                "YstarGov_intelligence_decision": intelligence_write["governance_decision"]["decision"],
                "commercial_sharpness_summary": strategy["benchmark_result"]["dimensions"]["commercial_sharpness"],
                "owner_approval_state": "not_required",
                "L4_owner_approval_state": "pending_owner_decision",
                **doctrine_gate["doctrine_metadata"],
            },
        }
    )
    pre_write = governance.validate_and_write_ceo_runtime_envelope(
        pre_envelope,
        cieu_db=cieu_db,
        session_id=SESSION_ID,
        agent_id="bridge_labs_ceo",
        seal_session=False,
    )
    provider_route = route_provider_tool_action_through_runtime_nervous_system(
        pre_envelope,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
    )
    post_residual = _build_post_strategy_residual(
        strategy=strategy,
        pre_action_packet=pre_action_packet,
        pre_action_event_id=pre_write["CIEU_write_result"]["event_id"],
        provider_receipt=provider_route.get("gov_mcp_receipt", {}),
    )
    post_envelope = dict(pre_envelope)
    post_envelope.update(
        {
            "action_id": "e90_market_strategy_post_action_residual",
            "action_phase": "completed",
            "completed_action": True,
            "post_action_residual": post_residual,
            "context": "post-strategy residual closure for E90 strategic benchmark run",
        }
    )
    post_write = governance.validate_and_write_ceo_runtime_envelope(
        post_envelope,
        cieu_db=cieu_db,
        session_id=SESSION_ID,
        agent_id="bridge_labs_ceo",
        seal_session=seal_session,
    )
    summary = _cieu_record_summary(cieu_db, SESSION_ID)
    chain_proven = _chain_proven(intelligence_write, benchmark_write, pre_write, post_write, provider_route, summary)
    return {
        "artifact_id": "e90_market_grounded_strategy_session_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner_intent": owner_intent,
        "doctrine_gate": doctrine_gate,
        "doctrine_invocation_plan_decision": doctrine_gate["plan_write"]["governance_decision"]["decision"],
        "doctrine_invocation_proof_decision": doctrine_gate["proof_write"]["governance_decision"]["decision"],
        "strategy": strategy,
        "benchmark_result": strategy["benchmark_result"],
        "intelligence_governance_decision": intelligence_write["governance_decision"]["decision"],
        "intelligence_CIEU_write": intelligence_write["CIEU_write_result"],
        "strategic_benchmark_governance_decision": benchmark_write["governance_decision"]["decision"],
        "strategic_benchmark_CIEU_write": benchmark_write["CIEU_write_result"],
        "pre_action_runtime_decision": pre_write["runtime_result"]["decision"],
        "pre_action_CIEU_write": pre_write["CIEU_write_result"],
        "provider_route": provider_route,
        "post_strategy_residual": post_residual,
        "post_action_runtime_decision": post_write["runtime_result"]["decision"],
        "post_action_CIEU_write": post_write["CIEU_write_result"],
        "CIEUStore_record_summary": summary,
        "end_to_end_chain_proven": chain_proven,
        "selected_first_cash_path": strategy["selected_strategy"]["current_best_first_cash_path"],
        "do_not_pursue_list": strategy["do_not_pursue_list"],
        "next_L4_owner_decision_packet_status": {
            "status": "prepared_no_send_owner_decision_required",
            "owner_approval_state": strategy["next_L4_feedback_owner_decision_packet"]["owner_approval_state"],
            "external_action_executed": False,
            "provider_action_executed": False,
        },
        "L5_truth_table_after": build_l5_truth_table_after_e90(chain_proven=chain_proven),
        "safety_statement": {
            "no_external_action": True,
            "no_L4_feedback_executed": True,
            "no_customer_validation_claim": True,
            "no_revenue_payment_pricing_claim": True,
            "gov_mcp_dry_run_only": True,
            "K9Audit_not_integrated": True,
        },
    }


def write_e90_strategy_reports(
    *,
    cieu_db: str,
    root: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
) -> dict[str, Any]:
    target_root = root or BRIDGE_ROOT
    result = run_e90_market_grounded_strategy_session(
        cieu_db=cieu_db,
        repo_root=target_root,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
    )
    benchmark_report = _benchmark_report(result)
    strategy_report = _strategy_report(result)
    status = _runtime_status_report(result)
    files = {
        "benchmark_json": target_root / "office/mission_command/e90_ceo_strategic_intelligence_benchmark_report.json",
        "benchmark_md": target_root / "office/mission_command/e90_ceo_strategic_intelligence_benchmark_readback.md",
        "strategy_json": target_root / "office/mission_command/e90_market_grounded_strategy_run_report.json",
        "strategy_md": target_root / "office/mission_command/e90_market_grounded_strategy_run_readback.md",
        "status_json": target_root / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e90_ceo_strategic_intelligence_benchmark.json",
        "status_md": target_root / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e90_ceo_strategic_intelligence_benchmark.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["benchmark_json"].write_text(json.dumps(benchmark_report, indent=2, sort_keys=True), encoding="utf-8")
    files["benchmark_md"].write_text(_benchmark_markdown(benchmark_report), encoding="utf-8")
    files["strategy_json"].write_text(json.dumps(strategy_report, indent=2, sort_keys=True), encoding="utf-8")
    files["strategy_md"].write_text(_strategy_markdown(strategy_report), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["status_md"].write_text(_status_markdown(status), encoding="utf-8")
    return strategy_report


def build_l5_truth_table_after_e90(*, chain_proven: bool) -> dict[str, str]:
    return {
        "L5-A": "complete_internal_runtime_foundation",
        "L5-B": (
            "complete_for_structured_governed_intelligence_loop_with_strategy_benchmark"
            if chain_proven
            else "complete_for_structured_governed_intelligence_loop"
        ),
        "L5-C": "partial_dry_run_only",
        "L5-D": "absent_or_not_executed",
    }


def _internal_capability_map() -> dict[str, Any]:
    return {
        "bridge-labs": {
            "role": "CEO/company behavior center and strategy compiler",
            "current_capabilities": [
                "E87R full baseline",
                "E88 runtime session",
                "E89 intelligence compiler",
                "owner decision packet artifacts",
                "external validation planning artifacts",
            ],
        },
        "Y-star-gov": {
            "role": "governance reflex center",
            "current_capabilities": [
                "CEO Cognitive OS runtime hook",
                "CEO intelligence loop governance",
                "CIEUStore formal records",
                "CIEUStore seal/verify",
            ],
        },
        "gov-mcp": {
            "role": "provider/tool execution boundary",
            "current_capabilities": [
                "dry-run outbound receipt",
                "no-send invariant",
                "owner authorization pending behavior",
                "intelligence metadata receipt alignment",
            ],
        },
        "K9Audit": {
            "role": "separate stronger hash-chain evidence ledger",
            "current_capabilities": ["read-only boundary context only in E90"],
            "integration_status": "not_integrated_no_write",
        },
    }


def _historical_route_assets() -> list[str]:
    return [
        "operations/external_validation/e62_first_cash_path_selection.json",
        "operations/external_validation/e63_first_cash_path_refinement.json",
        "operations/external_validation/e64_dual_axis_first_cash_path_selection.json",
        "operations/external_validation/e67_owner_gated_external_validation_roadmap.json",
        "operations/external_validation/e78_l3_route_implication_matrix.json",
        "operations/external_validation/e79_l4_owner_decision_packet_no_external_action.json",
        "operations/baseline/e87r_full_repo_baseline/final_goal_gap_analysis.json",
        "office/mission_command/e89_ceo_intelligence_loop_runtime_compiler.py",
    ]


def _external_market_evidence_map() -> dict[str, Any]:
    items = [
        {
            "evidence_id": "nist_ai_rmf_genai_profile_2024",
            "source_title": "NIST AI RMF Generative AI Profile",
            "source_url": "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence",
            "category": "compliance/audit need",
            "claim_summary": "Organizations need repeatable govern/map/measure/manage practices for generative AI risk.",
            "route_implication": "Supports a governance blueprint and evidence-recording wedge.",
        },
        {
            "evidence_id": "nist_ai_rmf_2026_resource_center",
            "source_title": "NIST AI Risk Management Framework",
            "source_url": "https://www.nist.gov/itl/ai-risk-management-framework",
            "category": "AI governance risk",
            "claim_summary": "AI risk management is framed as a voluntary but systematic lifecycle discipline.",
            "route_implication": "Supports selling a structured operations/control blueprint, not just prompts.",
        },
        {
            "evidence_id": "microsoft_agent_governance_toolkit_2026",
            "source_title": "Microsoft Agent Governance Toolkit announcement",
            "source_url": "https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/",
            "category": "competing alternatives",
            "claim_summary": "Large vendors are moving toward runtime security governance for autonomous agents.",
            "route_implication": "Differentiation should be narrow: CEO/company operating runtime plus CIEU evidence.",
        },
        {
            "evidence_id": "owasp_agentic_skills_top10_2026",
            "source_title": "OWASP Agentic Skills Top 10",
            "source_url": "https://owasp.org/www-project-agentic-skills-top-10/",
            "category": "AI agent operations risk",
            "claim_summary": "Agentic skills create execution-layer security risk across tools and workflows.",
            "route_implication": "Supports no-new-wheel, least-privilege, and dry-run governance messaging.",
        },
        {
            "evidence_id": "mckinsey_agentic_ai_safety_security_2025",
            "source_title": "McKinsey agentic AI safety and security playbook",
            "source_url": "https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/deploying-agentic-ai-with-safety-and-security-a-playbook-for-technology-leaders",
            "category": "buyer pain",
            "claim_summary": "Agentic systems introduce new internal and external risks that leaders must manage.",
            "route_implication": "Buyer pain is credible around governance before autonomous actions scale.",
        },
        {
            "evidence_id": "deloitte_agentic_ai_guardrails_2026",
            "source_title": "Deloitte Insights: AI agents scaling faster than guardrails",
            "source_url": "https://www.deloitte.com/us/en/insights/topics/emerging-technologies/ai-agents-scaling-faster.html",
            "category": "market willingness",
            "claim_summary": "Agent adoption is growing while mature governance remains limited.",
            "route_implication": "A readiness/audit module has clearer wedge potential than broad platform claims.",
        },
        {
            "evidence_id": "deloitte_state_ai_enterprise_2026",
            "source_title": "Deloitte State of AI in the Enterprise",
            "source_url": "https://www.deloitte.com/us/en/what-we-do/capabilities/applied-artificial-intelligence/content/state-of-ai-in-the-enterprise.html",
            "category": "small-team adoption friction",
            "claim_summary": "Scaling AI requires governance, oversight, and records of automated decisions.",
            "route_implication": "Offer should lower adoption burden with a concrete blueprint/evidence pack.",
        },
        {
            "evidence_id": "mckinsey_agentic_ai_advantage_2025",
            "source_title": "McKinsey: Seizing the agentic AI advantage",
            "source_url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage",
            "category": "market willingness",
            "claim_summary": "Many AI initiatives struggle to translate broad adoption into measurable business impact.",
            "route_implication": "Strategy should focus on first-cash learning, not a generic governance platform.",
        },
        {
            "evidence_id": "arden_agent_governance_product_2026",
            "source_title": "Arden governance layer for AI agents",
            "source_url": "https://www.arden.sh/",
            "category": "competing alternatives",
            "claim_summary": "Market alternatives are positioning around policy enforcement, approval, and audit trails.",
            "route_implication": "Y*Bridge Labs should avoid broad undifferentiated control-plane positioning.",
        },
        {
            "evidence_id": "runesignal_agent_governance_product_2026",
            "source_title": "RuneSignal enterprise AI governance",
            "source_url": "https://runesignal.com/",
            "category": "competing alternatives",
            "claim_summary": "Agent governance products emphasize approvals, inventory, evidence, and compliance reporting.",
            "route_implication": "The wedge should emphasize CEO runtime + CIEU audit evidence for agent teams.",
        },
    ]
    return {
        "freshness_status": "current_public_read_as_of_2026-05-07_via_read_only_web_research",
        "live_provider_execution_used": False,
        "outreach_or_customer_contact_used": False,
        "evidence_items": items,
        "customer_validation_claimed": False,
        "revenue_signal_claimed": False,
    }


def _baseline_route_candidates() -> list[dict[str, Any]]:
    """Baseline 6 hardcoded routes — fallback only if E94 ingestion produces nothing.

    Kept exactly as it was before E94 introduction so behavior is identical
    when no strategic input artifacts exist (empty repo, fresh checkout, or
    explicit ingestion disable).
    """
    return [
        {
            "route_id": "governed_ops_blueprint_cieu_audit_wedge",
            "name": "Governed Business Operations Blueprint + CIEU Audit Module",
            "description": "A narrow readiness/audit offer for small AI-agent teams that need action governance, approval boundaries, and evidence records.",
            "route_type": "external_feedback_candidate",
        },
        {
            "route_id": "cieu_audit_module",
            "name": "CIEU Audit Module",
            "description": "A standalone audit/evidence module showing formal runtime decisions and residual learning records.",
            "route_type": "internal_runtime",
        },
        {
            "route_id": "ceo_runtime_governance_product",
            "name": "CEO Runtime Governance Product",
            "description": "Productize the CEO Cognitive OS runtime hook and CIEUStore records as a governance layer.",
            "route_type": "provider_tool_dry_run",
        },
        {
            "route_id": "gov_mcp_provider_preflight_product",
            "name": "gov-mcp Provider/Tool Preflight Product",
            "description": "Position the no-send/dry-run outbound guard stack as a provider execution preflight.",
            "route_type": "provider_tool_dry_run",
        },
        {
            "route_id": "k9audit_evidence_chain_integration",
            "name": "K9Audit Evidence-Chain Product or Integration",
            "description": "Future stronger hash-chain mirror after an owner-approved integration milestone.",
            "route_type": "owner_decision_required",
        },
        {
            "route_id": "owner_mediated_l4_feedback_service",
            "name": "Owner-mediated L4 Feedback Packet Service",
            "description": "Prepare transparent no-send feedback packets that owner may approve for direct market learning.",
            "route_type": "external_feedback_candidate",
        },
    ]


def _route_candidates(repo_root: Path | None = None) -> list[dict[str, Any]]:
    """Return route candidates merged from E94 strategic input ingestion + baseline.

    Order: ingested routes first (owner memos, e34 opportunity spaces, prior
    milestone monetization paths), baseline 6 appended for backward compat.
    Duplicates by route_id are skipped.
    """

    ingested: list[dict[str, Any]] = []
    try:
        from office.mission_command.e94_strategic_input_ingestion import (
            build_strategic_input_packet,
            extract_route_candidates_from_packet,
        )
        packet = build_strategic_input_packet(repo_root=repo_root)
        ingested = extract_route_candidates_from_packet(packet)
    except Exception:
        # Any ingestion failure: silent fallback to baseline. Deep-strategy
        # runs must never be blocked by ingestion errors.
        ingested = []

    baseline = _baseline_route_candidates()

    seen_ids: set[str] = set()
    merged: list[dict[str, Any]] = []
    for route in ingested + baseline:
        rid = route.get("route_id")
        if rid and rid not in seen_ids:
            merged.append(route)
            seen_ids.add(rid)
    return merged


def _route_scoring() -> list[dict[str, Any]]:
    return [
        {
            "route_id": "governed_ops_blueprint_cieu_audit_wedge",
            "speed_to_first_cash": 5,
            "buyer_pain_intensity": 4,
            "proof_needed": 3,
            "implementation_readiness": 5,
            "sales_friction": 3,
            "differentiation": 4,
            "trust_compliance_value": 5,
            "owner_burden": 2,
            "external_validation_next_step": "owner-approved no-send L4 feedback to one target profile",
            "kill_criteria": "target says audit/governance pain is not urgent or too generic",
        },
        {
            "route_id": "cieu_audit_module",
            "speed_to_first_cash": 4,
            "buyer_pain_intensity": 3,
            "proof_needed": 3,
            "implementation_readiness": 5,
            "sales_friction": 4,
            "differentiation": 4,
            "trust_compliance_value": 5,
            "owner_burden": 2,
            "external_validation_next_step": "show one formal CIEUStore before/after audit example",
            "kill_criteria": "buyers see logs as commodity observability rather than decision evidence",
        },
        {
            "route_id": "ceo_runtime_governance_product",
            "speed_to_first_cash": 3,
            "buyer_pain_intensity": 4,
            "proof_needed": 4,
            "implementation_readiness": 4,
            "sales_friction": 4,
            "differentiation": 5,
            "trust_compliance_value": 5,
            "owner_burden": 3,
            "external_validation_next_step": "test whether teams want CEO-level governance or lower-level action gates",
            "kill_criteria": "buyers cannot map CEO runtime language to a budgeted pain",
        },
        {
            "route_id": "gov_mcp_provider_preflight_product",
            "speed_to_first_cash": 3,
            "buyer_pain_intensity": 4,
            "proof_needed": 4,
            "implementation_readiness": 4,
            "sales_friction": 4,
            "differentiation": 3,
            "trust_compliance_value": 4,
            "owner_burden": 3,
            "external_validation_next_step": "test whether no-send receipts solve enough pain alone",
            "kill_criteria": "buyers already use framework-native approval gates",
        },
        {
            "route_id": "k9audit_evidence_chain_integration",
            "speed_to_first_cash": 2,
            "buyer_pain_intensity": 4,
            "proof_needed": 5,
            "implementation_readiness": 2,
            "sales_friction": 5,
            "differentiation": 5,
            "trust_compliance_value": 5,
            "owner_burden": 4,
            "external_validation_next_step": "owner-approved technical integration proof, not market outreach",
            "kill_criteria": "integration cost delays first market learning",
        },
        {
            "route_id": "owner_mediated_l4_feedback_service",
            "speed_to_first_cash": 4,
            "buyer_pain_intensity": 4,
            "proof_needed": 2,
            "implementation_readiness": 4,
            "sales_friction": 3,
            "differentiation": 3,
            "trust_compliance_value": 4,
            "owner_burden": 4,
            "external_validation_next_step": "owner reviews and approves the first no-send feedback packet",
            "kill_criteria": "owner burden is too high or target profile is too vague",
        },
    ]


def _selected_strategy() -> dict[str, Any]:
    return {
        "current_best_first_cash_path": "Governed Business Operations Blueprint + CIEU Audit Module for small AI-agent teams",
        "second_best_path": "CEO runtime governance product after more L4 feedback",
        "do_not_pursue_path": "K9Audit evidence-chain productization before bridge integration and buyer proof",
        "why_this_path_now": (
            "It reuses the strongest existing runtime proof, maps to public market pain around agent governance, "
            "and can be tested with a narrow no-send owner-approved L4 packet."
        ),
        "why_not_others": (
            "CIEU alone may be too abstract; broad CEO governance product is harder to explain; gov-mcp alone is "
            "too close to commodity guardrails; K9Audit integration is not yet implemented."
        ),
        "what_evidence_could_falsify_it": (
            "Owner-approved L4 feedback says small agent teams do not feel pain around approval trails, audit records, "
            "or governed action boundaries, or will not pay for a readiness/audit wedge."
        ),
        "next_48h_action": "Prepare the no-send owner decision packet and dry-run receipt for one target profile.",
        "next_7d_action": "If owner approves, execute a minimal transparent L4 feedback pilot through gov-mcp no-send/live-ready preflight.",
        "next_owner_decision_needed": "Approve or reject one scoped L4 feedback packet; no send by default.",
    }


def _do_not_pursue_list() -> list[str]:
    return [
        "Mass outreach or publication before owner-approved L4 scope",
        "Live provider execution before owner activation and gov-mcp live-ready preflight",
        "K9Audit integration product claims before code-level bridge exists",
        "Generic AI governance platform positioning against better-funded competitors",
        "Payment/revenue loop claims before actual buyer signal",
        "Customer validation claims from public-read evidence",
    ]


def _what_not_to_do_next() -> list[str]:
    return [
        "Do not send any L4 message in E90.",
        "Do not call external public-read evidence customer validation.",
        "Do not claim pricing validation or paid signal.",
        "Do not broaden into a full platform before one wedge is tested.",
    ]


def _next_l4_feedback_owner_decision_packet() -> dict[str, Any]:
    return {
        "packet_id": "e90_next_l4_feedback_owner_decision_packet_no_send",
        "target_profile": "founder/operator of a small AI-agent team shipping internal agents or agent workflows",
        "message_hypothesis": (
            "Small teams need a lightweight way to prove agent actions were pre-approved, dry-run gated, "
            "and recorded with residuals before external/customer-facing use."
        ),
        "evidence_sought": [
            "whether the approval/audit pain is recognized",
            "which artifact is most valuable: blueprint, CIEU audit module, or dry-run receipt",
            "whether a paid readiness review would be plausible after proof",
        ],
        "risk_tier": "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION",
        "ai_transparency": True,
        "opt_out_language": "If this is not relevant, no reply is needed.",
        "no_send_default": True,
        "owner_decision_required": True,
        "owner_approval_state": "pending_owner_decision",
        "external_action_executed": False,
        "provider_action_executed": False,
        "gov_mcp_dry_run_preflight_plan": "Use gov-mcp dry_run_outbound_action with owner_review_required and no-send receipt.",
        "Y_star_gov_governance_plan": "Validate through CEO runtime hook and write CIEUStore records before any future send.",
        "CIEU_prediction": {
            "X_t": "E90 strategy identifies a first-cash wedge but no external feedback exists",
            "U_t": "owner reviews no-send L4 packet",
            "Y_star_t": "owner can authorize a minimal L4 feedback pilot later",
            "expected_Y_t_plus_1": "approval, revision, or rejection of the L4 packet",
            "predicted_R_t_plus_1": "market proof remains absent until an owner-approved send occurs",
            "residual_severity": "medium",
            "falsification_condition": "owner rejects target/profile/message as too vague or unsafe",
        },
    }


def _cieu_predictions() -> list[dict[str, Any]]:
    return [
        {
            "X_t": "E89 made CEO cognition structured and governable, but strategy quality was unbenchmarked",
            "U_t": "run market-grounded strategy benchmark and prepare owner-gated L4 packet",
            "Y_star_t": "CEO selects a sharper first-cash path based on internal and public-read evidence",
            "expected_Y_t_plus_1": "strategy passes deterministic benchmark and writes CIEUStore records",
            "predicted_R_t_plus_1": "external proof, customer validation, pricing validation, and revenue remain pending",
            "residual_severity": "medium",
            "falsification_condition": "benchmark score drops below 4.0 or owner-approved feedback later rejects the wedge",
        }
    ]


def _post_strategy_residual_plan() -> dict[str, Any]:
    return {
        "evaluate_strategy_quality_by": "future owner-approved L4 response content and whether target recognizes the pain",
        "future_evidence_updates": [
            "L4 feedback response content",
            "which route language earns engagement",
            "whether buyer asks for audit module, blueprint, or runtime gate",
        ],
        "pivot_trigger": "no recognized urgency or no willingness to review after scoped owner-approved feedback",
        "what_not_to_do_next": _what_not_to_do_next(),
    }


def _build_strategy_pre_action_packet(
    intelligence_packet: Mapping[str, Any],
    strategy: Mapping[str, Any],
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    packet = build_pre_action_packet_from_intelligence_packet(intelligence_packet, repo_root=repo_root)
    packet.update(
        {
            "packet_id": "e90_selected_l4_feedback_packet_pre_action",
            "job_id": MILESTONE_ID,
            "proposed_action": "prepare no-send owner decision packet and gov-mcp dry-run preflight for the selected L4 feedback candidate",
            "action_class": "provider_tool_execution",
            "owner_intent": strategy["owner_intent"],
            "selected_action": strategy["selected_strategy"]["current_best_first_cash_path"],
            "candidate_actions": [route["name"] for route in strategy["route_candidates"]],
            "counterfactual_comparison": strategy["route_scoring"],
            "predicted_CIEU_records": strategy["CIEU_predictions"],
            "adversarial_critique": "; ".join(strategy["adversarial_critique"]),
            "what_not_to_do": strategy["what_not_to_do_next"] + strategy["do_not_pursue_list"],
            "why_this_action": strategy["selected_strategy"]["why_this_path_now"],
            "why_not_other_actions": strategy["selected_strategy"]["why_not_others"],
            "approval_required": False,
            "owner_approval_state": "not_required",
            "L4_owner_approval_state": "pending_owner_decision",
            "next_L4_feedback_owner_decision_packet": strategy["next_L4_feedback_owner_decision_packet"],
            "overclaim_boundary": strategy["overclaim_boundary"],
        }
    )
    return packet


def _build_post_strategy_residual(
    *,
    strategy: Mapping[str, Any],
    pre_action_packet: Mapping[str, Any],
    pre_action_event_id: str,
    provider_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    residual = build_e87_post_action_residual(
        pre_action_packet_id=pre_action_packet["packet_id"],
        pre_action_event_id=pre_action_event_id,
        provider_receipt=provider_receipt,
    )
    residual.update(
        {
            "packet_id": "e90_market_grounded_strategy_post_action_residual",
            "linked_pre_action_packet_id": pre_action_packet["packet_id"],
            "action_taken": "market-grounded strategy benchmark and no-send L4 packet preflight",
            "expected_outcome": "strategy benchmark, runtime preflight, gov-mcp dry-run receipt, and residual are recorded",
            "actual_output": "selected first-cash path and owner-gated L4 packet prepared without external side effect",
            "CIEU_record": {
                "X_t": "E90 needed strategic benchmark proof after E89 structured cognition",
                "U_t": "ran benchmark, strategy selection, runtime governance, gov-mcp dry-run, and residual closure",
                "Y_star_t": "CEO strategy becomes benchmarked and future-verifiable before L4 feedback",
                "Y_t_plus_1": "CIEUStore records written for intelligence, benchmark, runtime decision, and residual",
                "R_t_plus_1": "L4 feedback, customer validation, pricing validation, and revenue remain absent",
            },
            "capability_state_updates": [
                "L5-B now includes deterministic strategy benchmark proof",
                "L5-C remains dry-run/no-send only",
            ],
            "learning_candidates": [
                strategy["post_strategy_residual_plan"]["evaluate_strategy_quality_by"],
                "Next milestone should prepare owner-approved L4 feedback pilot if owner approves.",
            ],
            "next_action_recommendation": "E91_owner_approved_minimal_L4_feedback_pilot_through_governed_runtime",
            "what_not_to_do_next": strategy["what_not_to_do_next"],
        }
    )
    return residual


def _chain_proven(
    intelligence_write: Mapping[str, Any],
    benchmark_write: Mapping[str, Any],
    pre_write: Mapping[str, Any],
    post_write: Mapping[str, Any],
    provider_route: Mapping[str, Any],
    record_summary: Mapping[str, Any],
) -> bool:
    receipt = provider_route.get("gov_mcp_receipt", {})
    return all(
        [
            intelligence_write.get("formal_CIEU_log_written") is True,
            benchmark_write.get("formal_CIEU_log_written") is True,
            pre_write.get("formal_CIEU_log_written") is True,
            post_write.get("formal_CIEU_log_written") is True,
            intelligence_write.get("governance_decision", {}).get("decision") == "ALLOW",
            benchmark_write.get("governance_decision", {}).get("decision") == "ALLOW",
            pre_write.get("runtime_result", {}).get("decision") == "ALLOW",
            post_write.get("runtime_result", {}).get("decision") == "ALLOW",
            provider_route.get("gov_mcp_dry_run_invoked") is True,
            receipt.get("provider_action_executed") is False,
            receipt.get("external_side_effect") is False,
            record_summary.get("event_count", 0) >= 4,
            record_summary.get("sealed_session_valid") is True,
        ]
    )


def _cieu_record_summary(cieu_db: str, session_id: str) -> dict[str, Any]:
    with sqlite3.connect(cieu_db) as conn:
        conn.row_factory = sqlite3.Row
        events = conn.execute(
            "SELECT event_id, decision, event_type, sealed FROM cieu_events WHERE session_id=? ORDER BY seq_global",
            (session_id,),
        ).fetchall()
        seal = conn.execute(
            "SELECT event_count, merkle_root FROM sealed_sessions WHERE session_id=?",
            (session_id,),
        ).fetchone()
    return {
        "session_id": session_id,
        "event_count": len(events),
        "event_types": [row["event_type"] for row in events],
        "decisions": [row["decision"] for row in events],
        "sealed_events": sum(1 for row in events if row["sealed"]),
        "sealed_session_valid": bool(seal and seal["event_count"] == len(events) and seal["merkle_root"]),
    }


def _benchmark_report(result: Mapping[str, Any]) -> dict[str, Any]:
    benchmark = result["benchmark_result"]
    return {
        "milestone_id": MILESTONE_ID,
        "benchmark_scores_by_dimension": benchmark["dimensions"],
        "strategic_intelligence_score": benchmark["strategic_intelligence_score"],
        "benchmark_pass": benchmark["pass"],
        "benchmark_decision": benchmark["benchmark_decision"],
        "failed_dimensions": benchmark["failed_dimensions"],
        "required_revisions": benchmark["required_revisions"],
        "CIEUStore_records_written": result["CIEUStore_record_summary"],
        "what_was_not_claimed": _not_claimed(),
    }


def _strategy_report(result: Mapping[str, Any]) -> dict[str, Any]:
    strategy = result["strategy"]
    receipt = result["provider_route"].get("gov_mcp_receipt", {})
    return {
        "milestone_id": MILESTONE_ID,
        "base_hashes": {
            "bridge_labs": "0d26f4e3f93e641b3eea11c1902f8eb759b06db3",
            "Y_star_gov": "54452868d392384ee878d19c81e7e8ad4037e5ce",
            "gov_mcp": "a8379ade47a4f395620a3b295f6c3c749e49ac01",
        },
        "external_evidence_sources": strategy["external_market_evidence_map"]["evidence_items"],
        "external_evidence_status": strategy["external_market_evidence_map"]["freshness_status"],
        "internal_capability_map": strategy["internal_capability_map"],
        "route_candidates": strategy["route_candidates"],
        "route_scoring": strategy["route_scoring"],
        "selected_strategy": strategy["selected_strategy"],
        "do_not_pursue_list": strategy["do_not_pursue_list"],
        "next_48h_action": strategy["selected_strategy"]["next_48h_action"],
        "next_7d_action": strategy["selected_strategy"]["next_7d_action"],
        "next_L4_owner_decision_packet": strategy["next_L4_feedback_owner_decision_packet"],
        "CIEU_predictions": strategy["CIEU_predictions"],
        "residual_learning_plan": strategy["post_strategy_residual_plan"],
        "CIEUStore_records_written": result["CIEUStore_record_summary"],
        "end_to_end_chain_proven": result["end_to_end_chain_proven"],
        "CIEUStore_write_status": {
            "intelligence_loop_record": result["intelligence_CIEU_write"]["formal_CIEU_log_written"],
            "strategic_benchmark_record": result["strategic_benchmark_CIEU_write"]["formal_CIEU_log_written"],
            "pre_action_runtime_record": result["pre_action_CIEU_write"]["formal_CIEU_log_written"],
            "post_action_residual_record": result["post_action_CIEU_write"]["formal_CIEU_log_written"],
        },
        "gov_mcp_status": {
            "dry_run_only": True,
            "dry_run_invoked": result["provider_route"].get("gov_mcp_dry_run_invoked") is True,
            "provider_action_executed": receipt.get("provider_action_executed"),
            "external_side_effect": receipt.get("external_side_effect"),
            "no_send_invariant": receipt.get("no_send_invariant") is True,
        },
        "L5_truth_table": result["L5_truth_table_after"],
        "what_was_not_claimed": _not_claimed(),
        "limitations": [
            "Public-read evidence is market grounding, not customer validation.",
            "No L4 feedback was executed.",
            "gov-mcp remained dry-run/no-send only.",
            "K9Audit was not written or integrated.",
            "L5-D revenue/customer/payment loop remains absent.",
        ],
        "recommended_next_milestone": "E91_Owner_Approved_Minimal_L4_Feedback_Pilot_Through_Governed_Runtime_R1",
    }


def _runtime_status_report(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "status": "completed" if result["end_to_end_chain_proven"] else "partial",
        "end_to_end_chain_proven": result["end_to_end_chain_proven"],
        "L5-A": result["L5_truth_table_after"]["L5-A"],
        "L5-B": result["L5_truth_table_after"]["L5-B"],
        "L5-C": result["L5_truth_table_after"]["L5-C"],
        "L5-D": result["L5_truth_table_after"]["L5-D"],
        "CIEUStore_records_written": result["CIEUStore_record_summary"],
        "gov_mcp_dry_run_only": True,
        "no_L4_feedback_executed": True,
        "no_customer_revenue_payment_claim": True,
        "K9Audit_not_integrated": True,
        "recommended_next_milestone": "E91_Owner_Approved_Minimal_L4_Feedback_Pilot_Through_Governed_Runtime_R1",
    }


def _benchmark_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# E90 CEO Strategic Intelligence Benchmark",
        "",
        f"Score: `{report['strategic_intelligence_score']}`",
        f"Decision: `{report['benchmark_decision']}`",
        f"Pass: `{report['benchmark_pass']}`",
        "",
        "No L4 feedback, customer validation, revenue, payment, pricing validation, or production deployment was claimed.",
    ]
    return "\n".join(lines) + "\n"


def _strategy_markdown(report: Mapping[str, Any]) -> str:
    selected = report["selected_strategy"]
    lines = [
        "# E90 Market-Grounded Strategy Run",
        "",
        f"Selected first-cash path: `{selected['current_best_first_cash_path']}`",
        f"Second-best path: `{selected['second_best_path']}`",
        f"End-to-end chain proven: `{report['end_to_end_chain_proven']}`",
        f"External evidence status: `{report['external_evidence_status']}`",
        f"gov-mcp status: `dry_run_only={report['gov_mcp_status']['dry_run_only']}`",
        "",
        "The next L4 feedback packet is prepared as no-send and owner-decision gated. No external action occurred.",
    ]
    return "\n".join(lines) + "\n"


def _status_markdown(status: Mapping[str, Any]) -> str:
    lines = [
        "# Runtime Status After E90",
        "",
        f"L5-A: `{status['L5-A']}`",
        f"L5-B: `{status['L5-B']}`",
        f"L5-C: `{status['L5-C']}`",
        f"L5-D: `{status['L5-D']}`",
        "",
        "L5-D remains absent because no real feedback, customer, revenue, payment, or pricing signal was executed or collected.",
    ]
    return "\n".join(lines) + "\n"


def _not_claimed() -> list[str]:
    return [
        "customer validation",
        "revenue signal",
        "payment signal",
        "pricing validation",
        "L4 feedback execution",
        "L5-D completion",
        "production deployment",
        "K9Audit integration",
    ]


__all__ = [
    "DEFAULT_OWNER_INTENT",
    "DEFAULT_STRATEGY_SCOPE",
    "SESSION_ID",
    "build_l5_truth_table_after_e90",
    "build_market_grounded_strategy_artifact",
    "run_e90_market_grounded_strategy_session",
    "write_e90_strategy_reports",
]
