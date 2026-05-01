from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .counterfactual_decision_gate import evaluate_counterfactual_gate, maybe_change_default_recommendation
from .counterfactual_reasoning import build_counterfactual_matrix
from .evidence_packet_builder import build_external_evidence_packets, build_internal_evidence_packets
from .opportunity_synthesis_engine import compare_generated_opportunities
from .resource_capability_matrix import build_behavior_capability_matrix
from .tier1_research_runtime import resolve_tier1_research_capability


MIN_PATHS = [
    "Agent Workflow Bottleneck Diagnosis",
    "Founder AI Workflow Audit / CEO Command Brief",
    "Coding-Agent Governance Audit",
    "AI Company Cockpit Setup",
    "Runtime Setup Advisory",
    "Governance Template Paid Support",
    "Agent Governance Evidence Pack",
]


def _path_from_title(opportunities: List[Dict[str, Any]], title: str) -> Dict[str, Any]:
    for opportunity in opportunities:
        if opportunity["title"] == title:
            return opportunity
    return {
        "opportunity_id": "opp_agent_governance_evidence_pack",
        "title": title,
        "generated_from_lens": "proof/evidence lens",
        "buyer": "Founder/operator who wants evidence that AI-agent work is safe, inspectable, and useful before buying implementation.",
        "pain": "They cannot distinguish agent-generated activity from governed value production.",
        "internal_assets": ["CZL", "Mission Command", "Y-star-gov", "gov-mcp", "evidence packets"],
        "external_unknowns": ["whether buyers will pay for evidence-pack preparation before implementation"],
        "behavior_capability_required": ["internal analysis", "sample deliverable", "read-only research planning"],
        "first_experiment": "48h internal evidence pack using the current Mission Command loop and action-wide preflight report.",
        "approval_needed": ["external buyer validation"],
        "m_triangle_alignment": "M-2 evidence discipline converted into M-3 commercial proof.",
        "owner_burden": "Low if packaged as review-only evidence.",
        "confidence": "low_to_medium_internal_only",
        "missing_evidence": ["fresh public buyer demand evidence"],
        "method_score": 8,
    }


def _score(item: Dict[str, Any], external_live_available: bool) -> Dict[str, int]:
    title = item["title"].lower()
    owner_burden = str(item.get("owner_burden", "")).lower()
    required = set(item.get("behavior_capability_required", []))
    base = {
        "time_to_first_signal": 3,
        "time_to_first_cash": 3,
        "internal_asset_fit": 3,
        "behavior_capability_fit": 3,
        "owner_burden_score": 2 if owner_burden.startswith("low") else 1,
        "channel_access": 1,
        "proof_strength": 2,
        "external_evidence_strength": 1 if not external_live_available else 3,
    }
    if "bottleneck" in title:
        base.update({"time_to_first_signal": 5, "behavior_capability_fit": 5, "owner_burden_score": 3})
    if "founder ai workflow" in title:
        base.update({"time_to_first_cash": 4, "proof_strength": 3})
    if "coding-agent governance" in title:
        base.update({"internal_asset_fit": 5, "proof_strength": 4})
    if "cockpit" in title:
        base.update({"internal_asset_fit": 4, "owner_burden_score": 1})
    if "template" in title:
        base.update({"owner_burden_score": 3, "time_to_first_cash": 2})
    if "customer contact" in required:
        base["channel_access"] = 1
    total = sum(base.values())
    base["total"] = total
    return base


def evaluate_money_paths(repo_root: Path) -> Dict[str, Any]:
    opportunities = compare_generated_opportunities(repo_root)
    by_title = [_path_from_title(opportunities, title) for title in MIN_PATHS]
    resolution = resolve_tier1_research_capability(repo_root)
    internal_packets = build_internal_evidence_packets(repo_root)
    external_packets = build_external_evidence_packets(repo_root)
    behavior = build_behavior_capability_matrix(repo_root)
    external_live_available = bool(resolution["live_read_only_available"] and resolution["live_research_executed"])
    counterfactual_cases = build_counterfactual_matrix(by_title, {"repo_root": str(repo_root)})
    gate = evaluate_counterfactual_gate(
        by_title,
        counterfactual_cases,
        behavior,
        {"external": "evidence_backed_live_read_only" if external_live_available else "internal_only_preliminary"},
    )
    rows: List[Dict[str, Any]] = []
    cases_by_title = {case["opportunity_title"]: case for case in counterfactual_cases}
    for item in by_title:
        score = _score(item, external_live_available)
        rows.append(
            {
                "path": item["title"],
                "buyer": item["buyer"],
                "urgent_pain": item["pain"],
                "budget_demand_signal": "internal hypothesis only; live public demand evidence missing",
                "internal_assets": item["internal_assets"],
                "external_evidence": "not available live" if not external_live_available else "live read-only evidence available",
                "behavior_capability": item["behavior_capability_required"],
                "owner_burden": item["owner_burden"],
                "delivery_speed": "48h internal sample possible",
                "trust_gap": "fresh external evidence and owner-approved validation still needed",
                "channel_access": "owner-approved/manual only; no contact executed",
                "proof_assets": [packet["packet_id"] for packet in internal_packets[:3]],
                "48h_validation_experiment": item["first_experiment"],
                "kill_condition": "Kill or downgrade if 48h sample cannot produce crisp buyer pain, low owner burden, and a bounded validation question.",
                "counterfactual_risks": cases_by_title[item["title"]],
                "residual_plan": "Record whether failure is pain, buyer, budget, trust, channel, delivery, or owner burden; keep writeback review-gated.",
                "score": score,
            }
        )
    rows.sort(key=lambda row: int(row["score"]["total"]), reverse=True)
    initial_default = rows[0]
    opportunity_by_path = {item["title"]: item for item in by_title}
    gate_default = maybe_change_default_recommendation(opportunity_by_path.get(initial_default["path"]), by_title, gate)
    default_path = gate_default["title"] if gate_default else initial_default["path"]
    return {
        "evaluation_mode": "internal_evidence_preliminary" if not external_live_available else "live_read_only_evidence_backed",
        "research_resolution": resolution,
        "internal_evidence_packets": internal_packets,
        "external_evidence_packets": external_packets,
        "paths": rows,
        "counterfactual_gate": gate,
        "default_path": default_path,
        "top_two_paths": [rows[0]["path"], rows[1]["path"]],
        "live_research_executed": False,
        "external_action_executed": False,
    }


def build_sample_deliverable(path_row: Dict[str, Any], rank: int) -> Dict[str, Any]:
    path = path_row["path"]
    return {
        "deliverable_id": f"sample_deliverable_{rank}_{''.join(ch.lower() if ch.isalnum() else '_' for ch in path)[:48]}",
        "title": f"Sample: {path}",
        "buyer_scenario": path_row["buyer"],
        "what_customer_receives": [
            "one-page diagnostic brief",
            "current bottleneck / governance / workflow finding summary",
            "48h action recommendation",
            "risk and approval boundary",
        ],
        "what_is_excluded": [
            "no implementation commitment",
            "no customer contact without approval",
            "no account creation",
            "no payment processing",
            "no core writeback",
        ],
        "48h_delivery_outline": [
            "intake hypothesis and evidence review",
            "sample diagnosis / audit checklist",
            "owner-reviewable recommendation",
            "approval-needed validation packet",
        ],
        "evidence_basis": path_row["proof_assets"],
        "pricing_hypothesis": "$750 entry diagnostic, $1500 recommended sprint, $3000 deeper advisory; external quote requires approval.",
        "approval_needed_validation_action": "Owner-approved Tier 1 read-only research first; customer contact is not approved by this deliverable.",
        "kill_condition": path_row["kill_condition"],
        "external_action_executed": False,
    }


def render_money_path_evaluation_markdown(evaluation: Dict[str, Any]) -> str:
    lines = [
        "# E2 Money Path Evaluation",
        "",
        f"- evaluation_mode: {evaluation['evaluation_mode']}",
        f"- default_path: {evaluation['default_path']}",
        f"- top_two_paths: {', '.join(evaluation['top_two_paths'])}",
        f"- live_research_executed: {evaluation['live_research_executed']}",
        "",
        "| Path | Total | Buyer | Pain | Owner burden | External evidence | 48h experiment |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in evaluation["paths"]:
        lines.append(
            f"| {row['path']} | {row['score']['total']} | {row['buyer']} | {row['urgent_pain']} | {row['owner_burden']} | {row['external_evidence']} | {row['48h_validation_experiment']} |"
        )
    lines.extend(["", "## Counterfactual Gate"])
    lines.append(f"- recommended_default_title: {evaluation['counterfactual_gate'].get('recommended_default_title')}")
    lines.append(f"- external_evidence_gap: {evaluation['counterfactual_gate'].get('external_evidence_gap')}")
    lines.extend(["", "## Path Details"])
    for row in evaluation["paths"]:
        lines.extend(
            [
                f"### {row['path']}",
                f"- buyer: {row['buyer']}",
                f"- urgent_pain: {row['urgent_pain']}",
                f"- budget_demand_signal: {row['budget_demand_signal']}",
                f"- internal_assets: {', '.join(row['internal_assets'])}",
                f"- behavior_capability: {', '.join(row['behavior_capability'])}",
                f"- owner_burden: {row['owner_burden']}",
                f"- channel_access: {row['channel_access']}",
                f"- proof_assets: {', '.join(row['proof_assets'])}",
                f"- kill_condition: {row['kill_condition']}",
                f"- highest_counterfactual_risk: {row['counterfactual_risks']['highest_risk_assumption']}",
                f"- residual_plan: {row['residual_plan']}",
            ]
        )
    return "\n".join(lines)


def render_sample_deliverable_markdown(deliverable: Dict[str, Any]) -> str:
    lines = [
        f"# {deliverable['title']}",
        "",
        f"- deliverable_id: {deliverable['deliverable_id']}",
        f"- buyer_scenario: {deliverable['buyer_scenario']}",
        f"- pricing_hypothesis: {deliverable['pricing_hypothesis']}",
        f"- approval_needed_validation_action: {deliverable['approval_needed_validation_action']}",
        f"- kill_condition: {deliverable['kill_condition']}",
        f"- external_action_executed: {deliverable['external_action_executed']}",
        "",
        "## What Customer Receives",
    ]
    lines.extend(f"- {item}" for item in deliverable["what_customer_receives"])
    lines.extend(["", "## What Is Excluded"])
    lines.extend(f"- {item}" for item in deliverable["what_is_excluded"])
    lines.extend(["", "## 48h Delivery Outline"])
    lines.extend(f"- {item}" for item in deliverable["48h_delivery_outline"])
    lines.extend(["", "## Evidence Basis"])
    lines.extend(f"- {item}" for item in deliverable["evidence_basis"])
    return "\n".join(lines)
