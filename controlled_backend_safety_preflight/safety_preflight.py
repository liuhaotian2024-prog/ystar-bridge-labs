#!/usr/bin/env python3
"""Safety preflight for controlled L6.11 search and page-read backends."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from controlled_public_page_read_adapter.page_read_adapter import reject_private_or_internal_url
from controlled_search_backend_adapters.controlled_search_backends import (
    ControlledBackendConfig,
    PROVIDER_KEY_ENVS,
    SearchBudgetEnvelope,
)


MAX_ALLOWED_BUDGET = {
    "max_queries": 5,
    "max_search_results_considered": 20,
    "max_pages_opened": 8,
    "max_domains": 5,
    "max_pages_per_domain": 3,
    "max_crawl_depth": 1,
    "max_total_external_reads": 12,
}


@dataclass(frozen=True)
class SafetyPreflightResult:
    decision: str
    backend_mode: str
    page_read_mode: str
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    budget_checks: dict[str, Any] = field(default_factory=dict)
    no_side_effect_guarantees: dict[str, bool] = field(default_factory=dict)
    private_url_rejections: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_safety_preflight(
    config: ControlledBackendConfig,
    budget: SearchBudgetEnvelope,
    candidate_urls: list[str] | None = None,
) -> SafetyPreflightResult:
    blockers: list[str] = []
    warnings: list[str] = []
    budget_checks: dict[str, Any] = {}
    for field, max_allowed in MAX_ALLOWED_BUDGET.items():
        value = getattr(budget, field)
        budget_checks[field] = {"value": value, "max_allowed": max_allowed, "within_limit": value <= max_allowed}
        if value > max_allowed:
            blockers.append(f"budget_exceeds_{field}")

    if config.search_backend_mode == "disabled":
        blockers.append("controlled_search_backend_not_configured")
    if config.page_read_backend_mode == "disabled":
        blockers.append("controlled_public_page_read_adapter_not_configured")
    if config.search_backend_mode in PROVIDER_KEY_ENVS:
        if config.missing_env_names:
            blockers.append("configured_backend_missing_required_environment")
        if not config.search_network_allowed:
            blockers.append("configured_backend_failed_safety_preflight")
    if config.page_read_backend_mode == "stdlib_public_http" and not config.page_read_network_allowed:
        blockers.append("configured_backend_failed_safety_preflight")

    private_url_rejections: dict[str, str] = {}
    for url in candidate_urls or []:
        rejection = reject_private_or_internal_url(url)
        if rejection:
            private_url_rejections[url] = rejection
            blockers.append("private_or_internal_url_rejected")

    if config.search_backend_mode == "fixture" or config.page_read_backend_mode == "fixture":
        warnings.append("fixture_mode_is_demo_evidence_not_real_world_truth")

    no_side_effect_guarantees = {
        "request_methods_limited_to_get": True,
        "no_post_put_patch_delete": True,
        "no_cookies": True,
        "no_auth_headers": True,
        "no_credentials": True,
        "no_form_submission": True,
        "no_login": True,
        "no_account_creation": True,
        "no_payment": True,
        "no_posting_commenting_messaging": True,
        "no_publication": True,
        "no_outreach": True,
        "no_revenue_execution": True,
        "no_mcp_execution": True,
        "no_live_behavior": True,
        "no_cieu_db_write": True,
        "no_brain_memory_writeback": True,
        "no_canonical_update": True,
        "no_direct_y_star_mutation": True,
    }
    return SafetyPreflightResult(
        decision="blocked" if blockers else "pass",
        backend_mode=config.search_backend_mode,
        page_read_mode=config.page_read_backend_mode,
        blockers=sorted(set(blockers)),
        warnings=warnings,
        budget_checks=budget_checks,
        no_side_effect_guarantees=no_side_effect_guarantees,
        private_url_rejections=private_url_rejections,
    )


__all__ = ["SafetyPreflightResult", "run_safety_preflight"]
