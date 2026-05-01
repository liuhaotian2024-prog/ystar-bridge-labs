from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .internal_world_scan import build_internal_world_scan
from .meta_development_method_kernel import build_meta_development_trace
from .research_capability import ResearchCapabilityAudit, audit_research_capability


MONEY_PATHS = [
    "Founder AI Workflow Audit / CEO Command Brief",
    "AI Company Cockpit Setup",
    "Coding-Agent Governance Audit",
    "Agent Workflow Bottleneck Diagnosis",
    "Runtime Setup Advisory",
    "Governance Template Paid Support",
]


def _score_path(path: str, external_ready: bool) -> Dict[str, object]:
    base = {
        "time_to_first_signal": 3,
        "time_to_first_cash": 4,
        "internal_capability_fit": 4,
        "owner_burden": 3,
        "delivery_feasibility": 4,
        "external_evidence_strength": 1,
        "m3_value_relevance": 4,
    }
    if path == "Founder AI Workflow Audit / CEO Command Brief":
        base.update({"time_to_first_signal": 5, "time_to_first_cash": 5, "delivery_feasibility": 5})
    elif path == "AI Company Cockpit Setup":
        base.update({"internal_capability_fit": 5, "owner_burden": 4, "delivery_feasibility": 3})
    elif path == "Coding-Agent Governance Audit":
        base.update({"internal_capability_fit": 5, "m3_value_relevance": 5, "time_to_first_cash": 4})
    elif path == "Agent Workflow Bottleneck Diagnosis":
        base.update({"time_to_first_signal": 5, "owner_burden": 2, "delivery_feasibility": 5})
    elif path == "Runtime Setup Advisory":
        base.update({"internal_capability_fit": 4, "time_to_first_cash": 3, "owner_burden": 4})
    elif path == "Governance Template Paid Support":
        base.update({"time_to_first_cash": 3, "delivery_feasibility": 3, "m3_value_relevance": 3})

    if external_ready:
        base["external_evidence_strength"] = 4

    total = (
        base["time_to_first_signal"]
        + base["time_to_first_cash"]
        + base["internal_capability_fit"]
        + base["delivery_feasibility"]
        + base["m3_value_relevance"]
        + base["external_evidence_strength"]
        - base["owner_burden"]
    )
    return {"path": path, **base, "total": total}


def build_evidence_gated_money_plan(repo_root: Path) -> Dict[str, object]:
    audit = audit_research_capability(repo_root)
    scan = build_internal_world_scan(repo_root)
    trace = build_meta_development_trace(
        "Aiden，带团队制定未来 7 天最可能产生第一笔真实收入或强付费信号的行动方案。要求不要锁死 Founder AI Workflow Audit，必须比较当前 top money paths。",
        repo_root,
    )
    external_ready = audit.plan_confidence_allowed == "evidence_backed_live_read_only"
    scores = [_score_path(path, external_ready) for path in MONEY_PATHS]
    scores = sorted(scores, key=lambda item: int(item["total"]), reverse=True)
    default = scores[0]
    confidence = "internal_only_preliminary" if not external_ready else "live_read_only_evidence_backed"
    return {
        "evidence_status": {
            "internal_evidence_available": audit.internal_research_verdict == "INTERNAL_RESEARCH_READY",
            "external_evidence_available": external_ready,
            "external_research_verdict": audit.external_research_verdict,
            "confidence_level": confidence,
        },
        "top_money_paths": scores,
        "default_recommendation": {
            "path": default["path"],
            "reason": (
                "Best internal-only default because it has the fastest signal/cash path and strongest manual delivery feasibility. "
                "This is not a fully live-market-evidence-backed recommendation until Tier 1 live read-only research is enabled and run."
            ),
        },
        "team_split": {
            "Aiden": "Own mission synthesis, default recommendation, owner decision brief.",
            "Sofia": "Write review-only positioning and offer language.",
            "Marco": "Define pricing hypotheses and willingness-to-pay signals.",
            "Zara": "Define buyer archetypes and approval-ready external action boundary.",
            "Ethan": "Define delivery checklist and feasibility boundary.",
            "Samantha": "Maintain decision log, evidence index, and residual candidates.",
            "Jinjin/K9 Scout": "Prepare read-only research questions and source criteria.",
            "Engineers": "Support reusable tooling only after path selection.",
        },
        "autonomous_internal_actions": [
            "Prepare a one-page offer brief for the default path.",
            "Prepare a sample CEO Command Brief outline.",
            "Build a read-only research plan and evidence fields.",
            "Convert old sales/content artifacts into historical evidence notes.",
            "Create an approval packet draft for any future outreach.",
        ],
        "approval_needed_actions": [
            "contact a customer",
            "send email/message",
            "publish content",
            "quote price externally",
            "create payment link or process payment",
            "write to core DB/brain/memory/CIEU",
        ],
        "research_gap": audit.external_capability["missing_for_live_research"],
        "next_owner_decision": "Approve a Tier 1 live read-only research mission with explicit budget, or accept this as an internal-only preliminary plan.",
        "internal_scan_money_paths": scan["money_paths"],
        "aiden_inferred_owner_objective": trace["inferred_objective"],
        "anti_prompt_overfit_check": trace["prompt_overfit_risk"],
        "meta_development_method_trace": trace["method_steps"],
        "resource_comparison": trace["resource_comparison"],
        "behavior_capability_matrix": trace["behavior_capabilities"],
        "opportunity_synthesis_by_lens": trace["opportunities"],
        "experiment_design": trace["experiments"],
        "owner_burden_minimization": trace["owner_burden"],
        "residual_plan": trace["residual_plan"],
        "known_unknown": {
            "known": [
                "internal repo context is available",
                "Aiden can compare multiple money paths internally",
                "Y-star-gov/gov-mcp preflight can separate allowed internal work from approval-required external side effects",
            ],
            "unknown": audit.external_capability["missing_for_live_research"],
        },
    }


def render_money_plan_markdown(plan: Dict[str, object]) -> str:
    status = plan["evidence_status"]  # type: ignore[index]
    default = plan["default_recommendation"]  # type: ignore[index]
    lines: List[str] = [
        "# Evidence-Gated 7-Day Money Plan — 2026-05-01",
        "",
        "## Evidence Status",
        f"- Internal evidence available: {status['internal_evidence_available']}",
        f"- External live evidence available: {status['external_evidence_available']}",
        f"- External research verdict: {status['external_research_verdict']}",
        f"- Confidence level: {status['confidence_level']}",
        "",
        "## Aiden Inferred Owner Objective",
        str(plan["aiden_inferred_owner_objective"]),
        "",
        "## Anti Prompt-Overfit Check",
    ]
    check = plan["anti_prompt_overfit_check"]  # type: ignore[index]
    lines.extend(f"- {risk}" for risk in check["risks"])
    lines.extend(
        [
            f"- mitigation: {check['mitigation']}",
            "",
            "## Meta-Development Method Trace",
        ]
    )
    lines.extend(f"- {step}" for step in plan["meta_development_method_trace"])  # type: ignore[index]
    lines.extend(
        [
            "",
            "## Resource Comparison",
        ]
    )
    for item in plan["resource_comparison"]:  # type: ignore[index]
        lines.append(f"- {item['opportunity']}: trust_gap={item['trust_gap']}; owner_burden={item['owner_burden']}")
    lines.extend(
        [
            "",
            "## Behavior Capability Matrix",
        ]
    )
    for item in plan["behavior_capability_matrix"]:  # type: ignore[index]
        lines.append(f"- {item['capability']}: status={item['current_status']}; autonomous_now={item['autonomous_now']}; owner_approval={item['requires_owner_approval']}")
    lines.extend(
        [
            "",
            "## Opportunity Synthesis By Lens",
        ]
    )
    for item in plan["opportunity_synthesis_by_lens"]:  # type: ignore[index]
        lines.append(f"- {item['generated_from_lens']}: {item['title']} — {item['pain']}")
    lines.extend(
        [
            "",
            "## Top Money Paths Compared",
            "| Path | Signal | Cash | Capability | Owner burden | Delivery | External evidence | M-3 | Total |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in plan["top_money_paths"]:  # type: ignore[index]
        lines.append(
            f"| {item['path']} | {item['time_to_first_signal']} | {item['time_to_first_cash']} | {item['internal_capability_fit']} | {item['owner_burden']} | {item['delivery_feasibility']} | {item['external_evidence_strength']} | {item['m3_value_relevance']} | {item['total']} |"
        )
    lines.extend(
        [
            "",
            "## Default Recommendation",
            f"Default: {default['path']}",
            "",
            str(default["reason"]),
            "",
            "## Team Split",
        ]
    )
    for agent, task in plan["team_split"].items():  # type: ignore[index]
        lines.append(f"- {agent}: {task}")
    lines.extend(["", "## Experiment Design Per Top Opportunity"])
    for item in plan["experiment_design"]:  # type: ignore[index]
        lines.append(f"- {item['opportunity']}: 48h={item['48h_internal_experiment']}; metric={item['success_metric']}; kill={item['kill_condition']}")
    lines.extend(["", "## Autonomous Internal Actions"])
    lines.extend(f"- {item}" for item in plan["autonomous_internal_actions"])  # type: ignore[index]
    lines.extend(["", "## Approval-Needed Actions"])
    lines.extend(f"- {item}" for item in plan["approval_needed_actions"])  # type: ignore[index]
    lines.extend(["", "## Research Gap"])
    lines.extend(f"- {item}" for item in plan["research_gap"])  # type: ignore[index]
    lines.extend(["", "## Owner Burden Minimization", str(plan["owner_burden_minimization"])])
    lines.extend(["", "## Residual Plan"])
    lines.extend(f"- {item}" for item in plan["residual_plan"])  # type: ignore[index]
    lines.extend(["", "## What Is Known / Unknown"])
    known_unknown = plan["known_unknown"]  # type: ignore[index]
    lines.append("Known:")
    lines.extend(f"- {item}" for item in known_unknown["known"])
    lines.append("Unknown:")
    lines.extend(f"- {item}" for item in known_unknown["unknown"])
    lines.extend(
        [
            "",
            "## Why This Is Still Internal-Only Preliminary",
            "Configured live read-only research is not available in this trial. The plan uses internal repo evidence and safe architecture checks only, not fresh live market evidence.",
        ]
    )
    lines.extend(
        [
            "",
            "## Next Owner Decision",
            str(plan["next_owner_decision"]),
            "",
            "Safety: no external sending, customer contact, email, payment, publication, or core DB writeback occurred.",
        ]
    )
    return "\n".join(lines)
