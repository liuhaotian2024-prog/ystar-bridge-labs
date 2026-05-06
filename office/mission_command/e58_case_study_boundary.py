from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
PRODUCT_DIR = Path("products/ai_agent_company_runtime_harness_case_study")
CASE_STUDY_ID = "ai_agent_company_runtime_harness_case_study_e58"
CASE_STUDY_VERSION = "0.1-owner-review"
SELECTED_ROUTE = "AI_agent_company_runtime_harness_case_study"
NEAREST_ALTERNATIVE = "full_governed_execution_causal_audit_proof_stack"
NEXT_MILESTONE = "E59_external_world_intelligence_L5_convergence"


def write_json(root: Path, rel: str, data: dict[str, Any]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def build_case_study_boundary() -> dict[str, Any]:
    return {
        "artifact_id": "e58_case_study_boundary",
        "case_study_name": "AI Agent Company Runtime Harness Case Study",
        "one_sentence_definition": "An owner-reviewable internal L5 proof showing how an AI-agent-operated company can maintain a CEO brain, behavior control center, governed internal operating loop, evidence closure, anti-drift governance, and post-L5 commercial route selection without external-action overclaiming.",
        "current_proof_level": [
            "internal_L5_runtime_harness_proof",
            "not_external_market_validation",
            "not_customer_validation",
            "not_paid_signal",
            "not_real_mcp_transport_closure",
            "not_published",
            "not_externally_reviewed",
        ],
        "supported_claims": [
            "CEO brain reached L5 cognitive center.",
            "Behavior control center reached L5.",
            "Internal company operating loop reached L5.",
            "Internal action selection, authorization, dry-run execution, evidence capture, writeback, readback, and self-evaluation are proven locally.",
            "Commercial route selection was rerun after L5 and selected the harness case study route.",
            "External action remained blocked throughout.",
        ],
        "unsupported_claims": [
            "market demand",
            "customer validation",
            "paid demand",
            "expert review",
            "real MCP transport closure",
            "production readiness",
            "enterprise compliance readiness",
            "latest external technology comparison",
            "external-world intelligence L5",
        ],
        "allowed_language": [
            "internal L5 proof",
            "owner-reviewable case study",
            "AI agent company runtime harness",
            "governed internal operating loop",
            "evidence-backed internal runtime",
            "not externally validated",
            "no customer or paid signal claim",
        ],
        "forbidden_language": [
            "validated by customers",
            "production-ready",
            "enterprise-proven",
            "paid demand exists",
            "real MCP transport closed",
            "customer-approved",
            "expert-reviewed",
            "externally validated",
            "published",
            "market-proven",
        ],
        "external_action_allowed": False,
        "owner_decision_status": "pending_owner_decision",
        "no_external_action": True,
    }


def build_case_study_json() -> dict[str, Any]:
    boundary = build_case_study_boundary()
    return {
        "case_study_id": CASE_STUDY_ID,
        "case_study_version": CASE_STUDY_VERSION,
        "selected_route_from_E57": SELECTED_ROUTE,
        "nearest_alternative_from_E57": NEAREST_ALTERNATIVE,
        "created_from_milestones": ["E50A", "E50B", "E50C", "E51", "E52", "E53", "E54", "E55", "E56", "E57"],
        "proof_level": "internal_L5_runtime_harness_proof",
        "target_reader": "owner / internal reviewer",
        "supported_claims": boundary["supported_claims"],
        "unsupported_claims": boundary["unsupported_claims"],
        "architecture_components": ["CEO brain", "behavior control center", "internal company loop", "anti-drift governance", "capability centerline binding", "Y-star-gov", "gov-mcp", "KG/CZL/CIEU", "K9Audit context"],
        "evidence_chain": [
            "E50A gov-mcp tool-layer allow/deny proof",
            "E52 Governed Agent Action Proof Packet",
            "E54 CEO brain L5",
            "E55 behavior control center L5",
            "E56 internal company operating loop L5",
            "E57 post-L5 money route retest",
        ],
        "no_go_boundaries": [
            "no outreach",
            "no publication",
            "no customer validation claim",
            "no paid signal claim",
            "no real MCP transport claim",
            "owner approval required before external action",
        ],
        "external_intelligence_gap": "External World Intelligence / Technology Capture / Market Learning L5 is not complete.",
        "E59_required_before_market_contact": True,
        "owner_approval_required_before_external_action": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "externally_validated": False,
        "publication_status": "not_published",
        "outreach_status": "not_contacted",
        "next_recommended_milestone": NEXT_MILESTONE,
    }


def write_case_study_boundary(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_case_study_boundary()
    write_json(root, "operations/external_validation/e58_case_study_boundary.json", data)
    write_md(root, "reports/integration/e58_case_study_boundary.md", "E58 Case Study Boundary", [
        f"Case study name: `{data['case_study_name']}`",
        "Proof level: `internal_L5_runtime_harness_proof`",
        "External intelligence L5 complete: `false`",
    ])
    return data


def write_case_study_product(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    product = root / PRODUCT_DIR
    product.mkdir(parents=True, exist_ok=True)
    case_study = build_case_study_json()
    write_json(root, str(PRODUCT_DIR / "case_study.json"), case_study)
    source_manifest = {
        "artifact_id": "e58_case_study_source_artifact_manifest",
        "sources": [
            {"source_id": "e54_brain_l5", "path": "operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json"},
            {"source_id": "e55_behavior_l5", "path": "operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json"},
            {"source_id": "e56_internal_loop_l5", "path": "operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json"},
            {"source_id": "e57_route_decision", "path": "operations/external_validation/e57_post_l5_commercial_route_decision_packet.json"},
            {"source_id": "e52_proof_packet", "path": "products/governed_agent_action_proof_packet/proof_packet.json"},
        ],
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
    }
    write_json(root, str(PRODUCT_DIR / "source_artifact_manifest.json"), source_manifest)
    write_json(root, str(PRODUCT_DIR / "case_study_validation_result.json"), {"artifact_id": "e58_case_study_validation_result", "status": "pending_until_e58_completion_gate", "external_action_allowed": False})
    docs = {
        "README.md": ["AI Agent Company Runtime Harness Case Study", "Owner-reviewable internal L5 proof package. This is not market validation and not an external action."],
        "executive_brief.md": ["Executive Brief", "The case study explains the internal L5 runtime proof and why E59 external world intelligence is required before market contact."],
        "technical_architecture.md": ["Technical Architecture", "CEO brain, behavior control center, internal company loop, anti-drift, capability binding, Y-star-gov, gov-mcp, KG/CZL/CIEU, and K9Audit context."],
        "proof_chain.md": ["Proof Chain", "E54 CEO brain L5 -> E55 behavior L5 -> E56 internal loop L5 -> E57 post-L5 money route retest -> E58 case study package."],
        "timeline.md": ["Timeline", "E50A tool-layer proof; E50B counterfactual route; E52 proof packet; E54/E55/E56 L5 runtime; E57 route shift; E58 package."],
        "runtime_harness_map.md": ["Runtime Harness Map", "Cognition centerline: CEO brain. Behavior centerline: behavior control center. Evidence centerline: KG/CZL/CIEU. Governance boundary: Y-star-gov and gov-mcp. Commercial route layer: E57 decision."],
        "what_this_proves.md": ["What This Proves", "Internal L5 runtime harness proof with governed dry-run behavior and evidence-backed readback."],
        "what_this_does_not_prove.md": [
            "What This Does Not Prove",
            "No customer validation. No paid signal. No real MCP transport claim. No external review. No outreach. No publication. No production readiness claim.",
            "External World Intelligence / Technology Capture / Market Learning L5 is not complete. E59 required before market contact.",
        ],
        "commercial_route_shift.md": ["Commercial Route Shift", "E57 shifted from proof-packet-only evidence to the AI agent company runtime harness case study because L5 runtime proof became the stronger commercial object."],
        "no_overclaim_boundary.md": [
            "No-Overclaim Boundary",
            "Allowed: internal L5 proof, owner-reviewable case study, governed internal operating loop, and evidence-backed internal runtime.",
            "No customer validation. No paid signal. No real MCP transport claim. No external review. No outreach. No publication.",
            "External World Intelligence / Technology Capture / Market Learning L5 is not complete. E59 required before market contact.",
            "owner approval required before external action.",
        ],
        "owner_review_guide.md": ["Owner Review Guide", "Review clarity, proof chain, limitations, E59 gap, and whether to approve only the next internal capability milestone. This does not approve outreach."],
    }
    for name, lines in docs.items():
        write_md(root, str(PRODUCT_DIR / name), lines[0], lines[1:])
    return case_study
