#!/usr/bin/env python3
"""Deterministic local opportunity discovery for L9 meta-development."""

from __future__ import annotations

from typing import Any

from .evidence_basis_builder import build_evidence_basis
from .internal_asset_inventory import build_internal_asset_inventory
from .opportunity_model import OWNER_GOAL, base_packet, now_iso, write_packet


SEED_OPPORTUNITIES = [
    {
        "opportunity_id": "opp_founder_ai_workflow_audit",
        "title": "Founder AI Workflow Audit & CEO Command Brief Sprint",
        "category": "founder_operator_service",
        "customer_profile": "AI startup founder or technical operator with urgent workflow and decision bottlenecks.",
        "problem_statement": "Founder needs a fast governed diagnostic of agent workflow risk, execution bottleneck, and next action plan.",
        "proposed_value": "Done-for-you workflow audit and CEO command brief.",
        "asset_ids": ["asset_l80_cash_loop", "asset_templates_and_service_design", "asset_controlled_observation"],
        "revenue_mechanism": "Paid diagnostic sprint.",
        "signal_days": 7,
        "cash_days": 21,
        "cost": 2,
        "confidence": "medium_high",
    },
    {
        "opportunity_id": "opp_ai_company_cockpit_setup",
        "title": "AI Company Cockpit Setup Sprint",
        "category": "runtime_setup_service",
        "customer_profile": "Founder/operator who wants a local AI team cockpit and approval-gated operating loop.",
        "problem_statement": "Small teams lack a visible AI operating room for tasks, approvals, and commercial loops.",
        "proposed_value": "Install/setup advisory for a Labs-style local cockpit and task loop.",
        "asset_ids": ["asset_l75_labs_office", "asset_l76_scheduler", "asset_legacy_team"],
        "revenue_mechanism": "Setup sprint plus support.",
        "signal_days": 10,
        "cash_days": 30,
        "cost": 3,
        "confidence": "medium",
    },
    {
        "opportunity_id": "opp_coding_agent_governance_audit",
        "title": "Coding-Agent Governance Audit",
        "category": "audit_compliance_service",
        "customer_profile": "Team using Codex/Claude Code/OpenClaw-like tools with code, secrets, or approval risk.",
        "problem_statement": "Teams want coding-agent speed without uncontrolled writes, secrets leakage, or unsafe deploy behavior.",
        "proposed_value": "Audit current coding-agent workflow and produce practical governance checklist.",
        "asset_ids": ["asset_y_governance", "asset_controlled_observation", "asset_open_source_background"],
        "revenue_mechanism": "Audit package and implementation support.",
        "signal_days": 14,
        "cash_days": 30,
        "cost": 3,
        "confidence": "medium_high",
    },
    {
        "opportunity_id": "opp_agent_workflow_bottleneck_diagnosis",
        "title": "Agent Workflow Bottleneck Diagnosis",
        "category": "diagnostic_service",
        "customer_profile": "Founder or operator whose AI-agent workflow feels slow, brittle, or hard to trust.",
        "problem_statement": "Agent workflows often fail at handoffs, memory, approval gates, and delivery proof.",
        "proposed_value": "Bottleneck map plus next-tool recommendation.",
        "asset_ids": ["asset_l76_scheduler", "asset_residual_learning", "asset_templates_and_service_design"],
        "revenue_mechanism": "Short diagnostic plus optional implementation support.",
        "signal_days": 7,
        "cash_days": 21,
        "cost": 2,
        "confidence": "medium",
    },
    {
        "opportunity_id": "opp_internal_ai_operations_audit",
        "title": "Internal AI Operations Audit for Small Teams",
        "category": "operations_audit_service",
        "customer_profile": "Small team adopting AI tools across research, code, docs, and decisions.",
        "problem_statement": "Teams lack a safe operating protocol for internal AI work.",
        "proposed_value": "Internal AI workflow audit with low-risk improvement plan.",
        "asset_ids": ["asset_y_governance", "asset_l75_labs_office", "asset_founder_context"],
        "revenue_mechanism": "Service sprint and follow-on templates.",
        "signal_days": 14,
        "cash_days": 35,
        "cost": 3,
        "confidence": "medium",
    },
    {
        "opportunity_id": "opp_governance_template_paid_support",
        "title": "Governance Template Paid Support",
        "category": "paid_support_route",
        "customer_profile": "Builder using open templates who needs customization and support.",
        "problem_statement": "Templates are useful but teams need help adapting them safely.",
        "proposed_value": "Paid support for governance templates and approval loops.",
        "asset_ids": ["asset_open_source_background", "asset_y_governance", "asset_l80_cash_loop"],
        "revenue_mechanism": "Open-source plus paid support.",
        "signal_days": 21,
        "cash_days": 45,
        "cost": 2,
        "confidence": "medium_low",
    },
    {
        "opportunity_id": "opp_runtime_setup_advisory",
        "title": "Y*Bridge Labs Runtime Setup Advisory",
        "category": "advisory_and_setup_service",
        "customer_profile": "Founder who wants to build a self-governed AI agent company runtime.",
        "problem_statement": "The meta-development architecture is hard to design from scratch.",
        "proposed_value": "Advisory sprint on local office, approval gates, commercial loops, and learning residuals.",
        "asset_ids": ["asset_founder_context", "asset_l75_labs_office", "asset_l80_cash_loop"],
        "revenue_mechanism": "Advisory sprint.",
        "signal_days": 14,
        "cash_days": 30,
        "cost": 2,
        "confidence": "medium",
    },
    {
        "opportunity_id": "opp_open_source_paid_support_package",
        "title": "Open-Source-to-Paid-Support Package",
        "category": "productized_support_route",
        "customer_profile": "Developers adopting agent governance/runtime templates.",
        "problem_statement": "Open artifacts need onboarding, configuration, and support to become useful.",
        "proposed_value": "Packaged templates plus paid support and implementation sessions.",
        "asset_ids": ["asset_open_source_background", "asset_templates_and_service_design", "asset_y_governance"],
        "revenue_mechanism": "Paid support around open artifacts.",
        "signal_days": 30,
        "cash_days": 60,
        "cost": 4,
        "confidence": "medium_low",
    },
]


def discover_opportunities(force: bool = False) -> dict[str, Any]:
    assets = build_internal_asset_inventory()
    opportunities = []
    for seed in SEED_OPPORTUNITIES:
        evidence = build_evidence_basis(
            seed["opportunity_id"],
            seed["asset_ids"] + ["owner_goal"],
            f"Opportunity synthesized from internal assets and owner goal: {OWNER_GOAL}",
            seed["confidence"],
        )
        packet = {
            **base_packet("opportunity_candidate"),
            "opportunity_id": seed["opportunity_id"],
            "title": seed["title"],
            "category": seed["category"],
            "customer_profile": seed["customer_profile"],
            "problem_statement": seed["problem_statement"],
            "proposed_value": seed["proposed_value"],
            "internal_asset_match": seed["asset_ids"],
            "revenue_mechanism": seed["revenue_mechanism"],
            "estimated_time_to_signal": f"{seed['signal_days']} days",
            "estimated_time_to_cash": f"{seed['cash_days']} days",
            "implementation_cost": seed["cost"],
            "confidence": seed["confidence"],
            "evidence_basis_id": evidence["evidence_basis_id"],
            "risk_boundary": "Manual-send and owner approval only; no customer contact or external action by default.",
            "current_status": "candidate",
            "generated_by": ["Aiden", "Zara", "Marco", "Sofia", "Jinjin", "Ethan", "Samantha"],
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "closed_category_enum": False,
        }
        opportunities.append(write_packet("opportunity_candidates", packet["opportunity_id"], packet))
    return {"ok": True, "asset_inventory": assets, "opportunities": opportunities, "opportunity_count": len(opportunities), "force": force}

