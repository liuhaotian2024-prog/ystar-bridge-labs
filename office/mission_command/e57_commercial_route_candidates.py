from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))

OWNER_STATUS = "pending_owner_decision"
OLD_E50B_ROUTE = "package_governed_agent_action_proof_packet"
SELECTED_ROUTE = "AI_agent_company_runtime_harness_case_study"
NEAREST_ALTERNATIVE = "full_governed_execution_causal_audit_proof_stack"
NEXT_MILESTONE = "E58_package_AI_agent_company_runtime_harness_case_study"


def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(root: Path, rel: str, data: dict[str, Any]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def _route(
    route_id: str,
    description: str,
    value_object: str,
    persona: str,
    proof_support: list[str],
    missing: list[str],
    blocker: str,
    owner_required: bool,
    external_required: bool,
    real_mcp_dep: bool,
    customer_dep: bool,
    paid_dep: bool,
    cash: float,
    proof: float,
    gov_risk: float,
    commercial_risk: float,
    reversibility: float,
    allowed_now: bool,
    allowed_type: str,
) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "description": description,
        "value_object": value_object,
        "target_persona_category": persona,
        "current_proof_support": proof_support,
        "missing_evidence": missing,
        "blocker_state": blocker,
        "owner_approval_required": owner_required,
        "external_action_required": external_required,
        "real_mcp_transport_dependency": real_mcp_dep,
        "customer_validation_dependency": customer_dep,
        "paid_signal_dependency": paid_dep,
        "near_term_cash_potential": cash,
        "proof_strength": proof,
        "governance_risk": gov_risk,
        "commercial_risk": commercial_risk,
        "reversibility": reversibility,
        "no_overclaim_boundary": ["no customer validation claim", "no paid signal claim", "no real MCP transport claim", "owner approval required before external action"],
        "allowed_now": allowed_now,
        "allowed_action_type": allowed_type,
    }


def build_commercial_route_candidates() -> dict[str, Any]:
    support_l5 = ["CEO brain L5", "behavior control center L5", "internal company loop L5", "E52 proof packet", "E51 anti-drift/capability gates"]
    routes = [
        _route("governed_agent_action_proof_packet_owner_review_path", "Continue the E52 proof packet owner-review path.", "owner-reviewable proof packet", "AI agent builder / governance-minded developer", ["E50A tool-layer allow/deny", "E52 packet", "E53 owner gate"], ["owner approval", "external reviewer feedback"], "pending_owner_decision", True, False, False, False, False, .56, .78, .10, .20, .92, True, "owner_review_only"),
        _route("controlled_single_first_user_review_after_owner_approval", "Prepare for one controlled first-user review only after explicit owner approval.", "review protocol", "MCP power user / AI ops lead", ["E52 packet", "E53 protocol"], ["explicit owner approval", "review evidence"], "owner_approval_missing", True, True, False, True, False, .72, .64, .34, .36, .62, False, "owner_approval_required"),
        _route("real_mcp_transport_gate_first", "Close real MCP package/client transport before market-facing work.", "technical transport proof", "developer tooling evaluator", ["E50A tool-layer proof"], ["real MCP transport proof"], "real_mcp_transport_not_closed", False, False, True, False, False, .34, .50, .08, .22, .76, True, "internal_analysis"),
        _route("gov_mcp_integration_service", "Package a gov-mcp integration service wedge.", "integration service", "AI ops / platform engineer", ["E50A tool-layer proof", "E51 gov-mcp tools"], ["real integration case", "external review"], "real_mcp_transport_not_closed", True, True, True, True, False, .70, .62, .22, .31, .70, False, "owner_approval_required"),
        _route("Y_star_gov_standalone_governance_kernel_wedge", "Lead with Y-star-gov standalone policy/kernel wedge.", "governance kernel", "governance-minded developer", ["Y-star-gov validators", "anti-drift gates"], ["market language", "external review"], "commercial_positioning_unclear", True, False, False, True, False, .45, .66, .12, .34, .84, True, "internal_analysis"),
        _route("K9Audit_causal_audit_wedge", "Lead with causal audit evidence wedge.", "audit/evidence concept", "AI audit / compliance developer", ["KG/CZL/CIEU artifacts", "K9Audit context"], ["K9 write integration", "case proof"], "K9_write_integration_not_closed", False, False, False, False, False, .48, .58, .14, .38, .78, True, "internal_analysis"),
        _route("full_governed_execution_causal_audit_proof_stack", "Package the full governed execution + causal audit + proof packet stack.", "full proof stack", "AI ops lead / agent platform owner", support_l5, ["real MCP transport", "external review"], "real_mcp_transport_not_closed", True, False, True, True, False, .74, .80, .18, .24, .72, True, "internal_analysis"),
        _route("AI_agent_company_runtime_harness_case_study", "Package the L5 internal company runtime as a case study/harness.", "company runtime harness case study", "AI agent builder / founder-operator", support_l5, ["owner review", "external feedback later"], "owner_approval_missing_for_external_review", True, False, False, True, False, .76, .86, .12, .20, .88, True, "internal_analysis"),
        _route("paid_setup_or_advisory_service", "Offer paid setup/advisory around governed agents.", "service offer", "startup / SMB operator", ["proof packet", "L5 internal loop"], ["owner approval", "offer validation", "payment evidence"], "no_paid_signal_and_no_owner_approval", True, True, False, True, True, .82, .50, .42, .54, .48, False, "owner_approval_required"),
        _route("public_readonly_market_observation_refresh", "Run bounded public-read-only market observation refresh.", "evidence refresh", "internal CEO runtime", ["E50B observation pattern"], ["repo-controlled adapter or safe source seed"], "external_page_read_adapter_unavailable", False, False, False, False, False, .42, .46, .16, .22, .90, False, "public_readonly_observation"),
        _route("wait_for_owner_decision", "Hold external-review track until owner decides.", "safe pause", "owner", ["E53 owner gate"], ["owner decision"], "pending_owner_decision", False, False, False, False, False, .18, .44, .04, .46, .96, True, "internal_analysis"),
        _route("direct_customer_outreach_now", "Direct customer outreach immediately.", "outreach attempt", "external human", [], ["owner approval", "recipient identity", "contact evidence"], "denied_owner_approval_missing", True, True, False, True, True, .80, .08, .96, .88, .12, False, "denied"),
    ]
    return {
        "artifact_id": "e57_commercial_route_candidates",
        "route_count": len(routes),
        "routes": routes,
        "rules": {
            "direct_customer_outreach_now": "deny",
            "controlled_single_first_user_review_after_owner_approval": "owner_approval_required",
            "public_readonly_market_observation_refresh": "blocked unless safe adapter exists",
            "no_route_claims_customer_validation_or_paid_signal": True,
        },
        "owner_decision_status": OWNER_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_commercial_route_candidates(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_commercial_route_candidates()
    write_json(root, "operations/external_validation/e57_commercial_route_candidates.json", data)
    write_md(root, "reports/integration/e57_commercial_route_candidates.md", "E57 Commercial Route Candidates", [
        f"Route count: `{data['route_count']}`",
        "Direct customer outreach: `denied`",
        "No route claims customer validation, paid signal, or real MCP transport closure.",
    ])
    return data
