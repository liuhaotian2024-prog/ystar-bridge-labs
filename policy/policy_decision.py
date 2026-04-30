#!/usr/bin/env python3
"""Deterministic staged policy decisions for commercial agent actions.

This helper is intentionally local, read-only, and secret-free. It loads the
JSON policy registry and converts old blanket "blocked/disabled" behavior into
typed decisions: discovery and drafts can proceed under budget, while external
execution and permanent writeback remain gated by human approval.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


POLICY_DIR = Path(__file__).resolve().parent

DISCOVERY_ACTIONS = {
    "query_planning",
    "controlled_search",
    "public_page_read",
    "bounded_crawl",
    "rss_sitemap_read",
    "source_triage",
    "evidence_extraction",
    "corroboration_conflict_analysis",
    "review_packet_generation",
    "market_research",
    "opportunity_discovery",
    "customer_segment_analysis",
    "pain_point_analysis",
    "competitor_analysis",
    "funding_grant_watch_read_only",
    "RFP_watch_read_only",
}

DRAFT_AND_PLANNING_ACTIONS = {
    "internal_strategy_memo",
    "offer_hypothesis_draft",
    "pricing_hypothesis_draft",
    "outreach_email_draft",
    "grant_application_draft",
    "RFP_response_draft",
    "public_content_draft",
    "approval_request_generation",
    "proposal_draft",
    "revenue_opportunity_packet_generation",
}

EXTERNAL_EXECUTION_ACTIONS = {
    "customer_outreach_send",
    "partner_outreach_send",
    "sending_outreach",
    "grant_application_submit",
    "RFP_submit",
    "submitting_grant_RFP",
    "public_content_publish",
    "publishing_content",
    "account_creation",
    "payment_or_purchase",
    "payment_purchase",
    "contract_or_signature",
    "signing_contracts",
    "social_posting",
    "customer_commitments",
    "autonomous_revenue_execution",
    "MCP_live_behavior",
}

WRITEBACK_CANDIDATE_ACTIONS = {
    "memory_writeback_candidate",
    "brain_update_candidate",
    "canonical_strategy_update_candidate",
    "CIEU_DB_write_candidate",
    "evidence_delta_candidate_generation",
    "strategy_delta_candidate_generation",
    "agent_capability_delta_candidate_generation",
    "dry_run_writeback",
}

ACTUAL_WRITEBACK_ACTIONS = {
    "actual_memory_writeback",
    "actual_brain_writeback",
    "actual_canonical_strategy_writeback",
    "actual_canonical_strategy_mutation",
    "actual_CIEU_DB_write",
}

HARD_FORBIDDEN_ACTIONS = {
    "secret_exposure",
    "api_key_print",
    "credential_exfiltration",
    "raw_db_wal_shm_ingestion",
    "raw_log_secret_ingestion",
    "active_agent_marker_content_ingestion",
    "private_internal_network_access",
    "access_control_bypass",
    "malware_execution",
}

APPROVED_STATES = {"approved_by_human", "execution_allowed", "actual_writeback_after_approval"}


def load_policy_registry() -> dict[str, Any]:
    """Load available policy JSON files without reading secrets or runtime state."""
    registry: dict[str, Any] = {}
    for path in POLICY_DIR.glob("*.json"):
        registry[path.name] = json.loads(path.read_text(encoding="utf-8"))
    return registry


def _decision(
    decision: str,
    reason: str,
    policy_ref: str,
    allowed_stage: str,
    requires_human_approval: bool,
    hard_boundary_preserved: bool,
) -> dict[str, Any]:
    return {
        "decision": decision,
        "reason": reason,
        "policy_ref": policy_ref,
        "allowed_stage": allowed_stage,
        "requires_human_approval": requires_human_approval,
        "hard_boundary_preserved": hard_boundary_preserved,
    }


def _budget_available(budget_state: dict[str, Any] | None) -> bool:
    if not budget_state:
        return True
    if budget_state.get("exhausted") is True:
        return False
    remaining = budget_state.get("remaining")
    return remaining is None or remaining > 0


def decide_action_capability(
    action_type: str,
    requested_stage: str,
    approval_state: str,
    evidence_state: dict[str, Any] | None = None,
    budget_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a typed policy decision for an action/stage request."""
    action = action_type.strip()

    if action in HARD_FORBIDDEN_ACTIONS:
        return _decision(
            "hard_forbidden",
            "Legitimate hard boundary: secrets, raw runtime state, private network, or access-control bypass remain forbidden.",
            "policy/runtime_access_policy.json",
            requested_stage,
            True,
            True,
        )

    if action in DISCOVERY_ACTIONS or requested_stage in {"observe", "search", "read", "extract", "analyze"}:
        if _budget_available(budget_state):
            return _decision(
                "allowed_with_budget",
                "Discovery/read-only analysis is allowed within configured budget.",
                "policy/discovery_policy.json",
                requested_stage,
                False,
                True,
            )
        return _decision(
            "blocked_by_policy",
            "Discovery budget is exhausted; request a new budget or approval before continuing.",
            "policy/discovery_policy.json",
            requested_stage,
            False,
            True,
        )

    if action in DRAFT_AND_PLANNING_ACTIONS or requested_stage in {"draft", "plan", "request_approval"}:
        return _decision(
            "allowed_draft_only",
            "Drafting, internal planning, and approval request generation are allowed; external execution is separate.",
            "policy/revenue_action_policy.json",
            requested_stage,
            False,
            True,
        )

    if action in WRITEBACK_CANDIDATE_ACTIONS or requested_stage in {"writeback_candidate", "dry_run_writeback"}:
        return _decision(
            "allowed_draft_only",
            "Learning is allowed as a candidate or dry-run receipt; permanent writeback remains gated.",
            "policy/writeback_policy.json",
            requested_stage,
            False,
            True,
        )

    if action in ACTUAL_WRITEBACK_ACTIONS or requested_stage == "actual_writeback_after_approval":
        if approval_state in APPROVED_STATES:
            return _decision(
                "allowed_after_human_approval",
                "Actual writeback is allowed only after explicit human approval.",
                "policy/writeback_policy.json",
                requested_stage,
                True,
                True,
            )
        return _decision(
            "blocked_pending_human_review",
            "Permanent memory/brain/canonical/CIEU writeback requires explicit human approval.",
            "policy/writeback_policy.json",
            requested_stage,
            True,
            True,
        )

    if action in EXTERNAL_EXECUTION_ACTIONS or requested_stage == "execute_after_approval":
        if approval_state in APPROVED_STATES:
            return _decision(
                "allowed_after_human_approval",
                "External execution is allowed only after explicit human approval.",
                "policy/approval_state_machine.json",
                requested_stage,
                True,
                True,
            )
        return _decision(
            "blocked_pending_human_review",
            "External side effects remain blocked until human approval.",
            "policy/approval_state_machine.json",
            requested_stage,
            True,
            True,
        )

    if evidence_state and evidence_state.get("missing_required_evidence"):
        return _decision(
            "blocked_pending_evidence",
            "The requested action needs evidence before it can proceed.",
            "policy/action_capability_registry.json",
            requested_stage,
            False,
            True,
        )

    return _decision(
        "blocked_pending_config",
        "Action is not yet mapped; add a registry entry or resolver instead of treating it as a permanent block.",
        "policy/action_capability_registry.json",
        requested_stage,
        False,
        True,
    )


def is_discovery_allowed(action_type: str, budget_state: dict[str, Any] | None) -> dict[str, Any]:
    return decide_action_capability(action_type, "search", "not_required", budget_state=budget_state)


def is_external_execution_allowed(action_type: str, approval_state: str) -> dict[str, Any]:
    return decide_action_capability(action_type, "execute_after_approval", approval_state)


def is_writeback_candidate_allowed(target_layer: str) -> dict[str, Any]:
    return decide_action_capability(f"{target_layer}_candidate", "writeback_candidate", "not_required")


def is_actual_writeback_allowed(target_layer: str, approval_state: str) -> dict[str, Any]:
    action = f"actual_{target_layer}_writeback"
    if target_layer in {"canonical_strategy", "CIEU_DB"}:
        action = f"actual_{target_layer}_write"
    return decide_action_capability(action, "actual_writeback_after_approval", approval_state)


def classify_owner_burden(pattern_or_request: str) -> dict[str, Any]:
    text = pattern_or_request.lower()
    replacements = []
    if "url" in text or "search" in text:
        replacements.extend(["automatic resolver", "controlled search", "host-mediated search bridge"])
    if "export" in text or "env" in text or "key" in text:
        replacements.extend(["safe local config loader", "human-supervised setup flow"])
    if "codex window" in text or "worktree" in text or "merge" in text:
        replacements.extend(["one-command launcher", "lane orchestrator", "local parallel runner"])
    if not replacements:
        replacements.append("owner cockpit")
    return {
        "classification": "owner_manual_burden",
        "policy_ref": "policy/owner_burden_reduction_policy.json",
        "recommended_replacements": sorted(set(replacements)),
        "manual_burden_should_be_default": False,
    }


def explain_decision(decision: dict[str, Any]) -> str:
    return (
        f"{decision['decision']}: {decision['reason']} "
        f"(policy={decision['policy_ref']}, stage={decision['allowed_stage']})"
    )
