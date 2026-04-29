#!/usr/bin/env python3
"""Controlled search backend registry for L6.11.

The default path is disabled and never performs network access. Fixture mode is
deterministic and local-only. Provider modes are explicit opt-in stubs that
validate environment/configuration without printing or storing secret values.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SEARCH_BACKEND_ENV = "YSTAR_CONTROLLED_SEARCH_BACKEND"
SEARCH_ALLOW_NETWORK_ENV = "YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK"
PAGE_READ_BACKEND_ENV = "YSTAR_CONTROLLED_PAGE_READ_BACKEND"
PAGE_READ_ALLOW_NETWORK_ENV = "YSTAR_CONTROLLED_PAGE_READ_ALLOW_NETWORK"

PROVIDER_KEY_ENVS = {
    "brave_search_api": "BRAVE_SEARCH_API_KEY",
    "tavily_search_api": "TAVILY_API_KEY",
    "serpapi": "SERPAPI_API_KEY",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def domain_from_url(url: str) -> str:
    return urlparse(url).netloc.lower()


@dataclass(frozen=True)
class ControlledBackendConfig:
    search_backend_mode: str = "disabled"
    page_read_backend_mode: str = "disabled"
    search_network_allowed: bool = False
    page_read_network_allowed: bool = False
    required_env_present: dict[str, bool] = field(default_factory=dict)
    missing_env_names: list[str] = field(default_factory=list)
    fixture_results_path: str | None = None
    fixture_pages_path: str | None = None

    @classmethod
    def from_environment(
        cls, base_dir: Path | None = None, overrides: dict[str, Any] | None = None
    ) -> "ControlledBackendConfig":
        overrides = overrides or {}
        search_mode = str(
            overrides.get("search_backend_mode")
            or os.environ.get(SEARCH_BACKEND_ENV)
            or "disabled"
        )
        page_mode = str(
            overrides.get("page_read_backend_mode")
            or os.environ.get(PAGE_READ_BACKEND_ENV)
            or "disabled"
        )
        search_network_allowed = bool(
            overrides.get("search_network_allowed", os.environ.get(SEARCH_ALLOW_NETWORK_ENV) == "1")
        )
        page_read_network_allowed = bool(
            overrides.get(
                "page_read_network_allowed",
                os.environ.get(PAGE_READ_ALLOW_NETWORK_ENV) == "1",
            )
        )
        required_env_present: dict[str, bool] = {}
        missing_env_names: list[str] = []
        required_key = PROVIDER_KEY_ENVS.get(search_mode)
        if required_key:
            present = bool(os.environ.get(required_key))
            required_env_present[required_key] = present
            if not present:
                missing_env_names.append(required_key)
        base = Path(base_dir) if base_dir else Path.cwd()
        fixture_results = overrides.get("fixture_results_path") or str(
            base / "controlled_backend_fixture_runtime" / "fixture_search_results.json"
        )
        fixture_pages = overrides.get("fixture_pages_path") or str(
            base / "controlled_backend_fixture_runtime" / "fixture_pages.json"
        )
        return cls(
            search_backend_mode=search_mode,
            page_read_backend_mode=page_mode,
            search_network_allowed=search_network_allowed,
            page_read_network_allowed=page_read_network_allowed,
            required_env_present=required_env_present,
            missing_env_names=missing_env_names,
            fixture_results_path=fixture_results,
            fixture_pages_path=fixture_pages,
        )

    def receipt(self) -> dict[str, Any]:
        blockers: list[str] = []
        if self.search_backend_mode == "disabled":
            blockers.append("controlled_search_backend_not_configured")
        if self.page_read_backend_mode == "disabled":
            blockers.append("controlled_public_page_read_adapter_not_configured")
        if self.missing_env_names:
            blockers.append("configured_backend_missing_required_environment")
        if self.search_backend_mode in PROVIDER_KEY_ENVS and not self.search_network_allowed:
            blockers.append("configured_backend_failed_safety_preflight")
        if self.page_read_backend_mode == "stdlib_public_http" and not self.page_read_network_allowed:
            blockers.append("configured_backend_failed_safety_preflight")
        return {
            "backend_mode": self.search_backend_mode,
            "page_read_mode": self.page_read_backend_mode,
            "network_allowed": self.search_network_allowed or self.page_read_network_allowed,
            "search_network_allowed": self.search_network_allowed,
            "page_read_network_allowed": self.page_read_network_allowed,
            "required_env_present": self.required_env_present,
            "missing_env_names": self.missing_env_names,
            "safety_preflight_decision": "blocked" if blockers else "pass",
            "blockers": blockers,
            "no_action_guarantees": {
                "ask_user_for_url": False,
                "secret_values_serialized": False,
                "login": False,
                "payment": False,
                "form_submission": False,
                "posting_commenting_messaging": False,
                "publication": False,
                "outreach": False,
                "revenue_execution": False,
                "mcp_execution": False,
                "live_behavior": False,
                "cieu_db_write": False,
                "brain_memory_writeback": False,
                "canonical_update": False,
                "direct_y_star_mutation": False,
            },
        }


@dataclass(frozen=True)
class SearchQueryEnvelope:
    query_id: str
    query_text: str
    query_category: str
    max_results: int = 4

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "SearchQueryEnvelope":
        return cls(
            query_id=str(payload.get("query_id", "")),
            query_text=str(payload.get("query_text", "")),
            query_category=str(payload.get("query_category", "")),
            max_results=int(payload.get("max_results", 4)),
        )


@dataclass(frozen=True)
class SearchBudgetEnvelope:
    max_queries: int = 5
    max_search_results_considered: int = 20
    max_pages_opened: int = 8
    max_domains: int = 5
    max_pages_per_domain: int = 3
    max_crawl_depth: int = 1
    max_total_external_reads: int = 12

    @classmethod
    def from_mapping(cls, payload: dict[str, Any] | None) -> "SearchBudgetEnvelope":
        payload = payload or {}
        return cls(
            max_queries=int(payload.get("max_queries", 5)),
            max_search_results_considered=int(payload.get("max_search_results_considered", 20)),
            max_pages_opened=int(payload.get("max_pages_opened", 8)),
            max_domains=int(payload.get("max_domains", 5)),
            max_pages_per_domain=int(payload.get("max_pages_per_domain", 3)),
            max_crawl_depth=int(payload.get("max_crawl_depth", 1)),
            max_total_external_reads=int(payload.get("max_total_external_reads", 12)),
        )


@dataclass(frozen=True)
class ControlledSearchRequestEnvelope:
    request_id: str
    selected_work_order_id: str
    queries: list[SearchQueryEnvelope]
    budget: SearchBudgetEnvelope

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "ControlledSearchRequestEnvelope":
        return cls(
            request_id=str(payload.get("request_id", "l6_11_controlled_search_request")),
            selected_work_order_id=str(payload.get("selected_work_order_id", "")),
            queries=[
                SearchQueryEnvelope.from_mapping(item) for item in payload.get("queries", [])
            ],
            budget=SearchBudgetEnvelope.from_mapping(payload.get("budget")),
        )


@dataclass(frozen=True)
class NormalizedSearchResult:
    result_id: str
    query_id: str
    query_text: str
    rank: int
    title: str
    url: str
    snippet: str
    source_domain: str
    backend_name: str
    retrieved_at_utc: str
    result_type: str
    is_sponsored_or_ad_if_known: bool | None
    safety_flags: dict[str, Any]
    trust_initial_label: str
    evidence_eligible: bool


@dataclass(frozen=True)
class ControlledSearchExecutionResult:
    backend_mode: str
    backend_name: str
    backend_explicitly_configured: bool
    search_executed: bool
    search_query_count: int
    search_results_considered: int
    external_reads_count: int
    result_candidates: list[dict[str, Any]]
    snippets_used_as_evidence: bool
    facts_inferred_from_snippets: bool
    asked_user_for_url: bool
    blocked_reason: str | None
    error_code: str | None
    network_used: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ControlledSearchBackend:
    backend_name = "base"

    def run(
        self,
        request: ControlledSearchRequestEnvelope,
        config: ControlledBackendConfig,
    ) -> ControlledSearchExecutionResult:
        raise NotImplementedError


class DisabledSearchBackend(ControlledSearchBackend):
    backend_name = "disabled"

    def run(
        self,
        request: ControlledSearchRequestEnvelope,
        config: ControlledBackendConfig,
    ) -> ControlledSearchExecutionResult:
        return ControlledSearchExecutionResult(
            backend_mode="disabled",
            backend_name=self.backend_name,
            backend_explicitly_configured=False,
            search_executed=False,
            search_query_count=0,
            search_results_considered=0,
            external_reads_count=0,
            result_candidates=[],
            snippets_used_as_evidence=False,
            facts_inferred_from_snippets=False,
            asked_user_for_url=False,
            blocked_reason="controlled_search_backend_not_configured",
            error_code="controlled_search_backend_not_configured",
            network_used=False,
        )


class FixtureSearchBackend(ControlledSearchBackend):
    backend_name = "fixture"

    def run(
        self,
        request: ControlledSearchRequestEnvelope,
        config: ControlledBackendConfig,
    ) -> ControlledSearchExecutionResult:
        fixture_path = Path(config.fixture_results_path or "")
        raw_results = json.loads(fixture_path.read_text(encoding="utf-8")).get("results", [])
        query_by_id = {query.query_id: query for query in request.queries[: request.budget.max_queries]}
        normalized: list[dict[str, Any]] = []
        for raw in raw_results:
            if len(normalized) >= request.budget.max_search_results_considered:
                break
            query_id = str(raw.get("query_id", ""))
            if query_id not in query_by_id:
                continue
            query = query_by_id[query_id]
            url = str(raw.get("url", ""))
            result = NormalizedSearchResult(
                result_id=str(raw.get("result_id", f"fixture_result_{len(normalized) + 1:03d}")),
                query_id=query.query_id,
                query_text=query.query_text,
                rank=int(raw.get("rank", len(normalized) + 1)),
                title=str(raw.get("title", "")),
                url=url,
                snippet=str(raw.get("snippet", "")),
                source_domain=str(raw.get("source_domain") or domain_from_url(url)),
                backend_name=self.backend_name,
                retrieved_at_utc=str(raw.get("retrieved_at_utc") or utc_now()),
                result_type=str(raw.get("result_type", "fixture_locator_candidate")),
                is_sponsored_or_ad_if_known=raw.get("is_sponsored_or_ad_if_known"),
                safety_flags=dict(raw.get("safety_flags", {})),
                trust_initial_label=str(raw.get("trust_initial_label", "fixture_demo")),
                evidence_eligible=bool(raw.get("evidence_eligible", True)),
            )
            normalized.append(asdict(result))
        return ControlledSearchExecutionResult(
            backend_mode="fixture",
            backend_name=self.backend_name,
            backend_explicitly_configured=True,
            search_executed=True,
            search_query_count=min(len(request.queries), request.budget.max_queries),
            search_results_considered=len(normalized),
            external_reads_count=0,
            result_candidates=normalized,
            snippets_used_as_evidence=False,
            facts_inferred_from_snippets=False,
            asked_user_for_url=False,
            blocked_reason=None,
            error_code=None,
            network_used=False,
        )


class ApiSearchBackendStub(ControlledSearchBackend):
    def __init__(self, backend_name: str):
        self.backend_name = backend_name

    def run(
        self,
        request: ControlledSearchRequestEnvelope,
        config: ControlledBackendConfig,
    ) -> ControlledSearchExecutionResult:
        required_env = PROVIDER_KEY_ENVS[self.backend_name]
        if not config.required_env_present.get(required_env, False):
            reason = "configured_backend_missing_required_environment"
        elif not config.search_network_allowed:
            reason = "configured_backend_failed_safety_preflight"
        else:
            reason = "configured_backend_adapter_stub_not_executed_without_provider_transport"
        return ControlledSearchExecutionResult(
            backend_mode=self.backend_name,
            backend_name=self.backend_name,
            backend_explicitly_configured=True,
            search_executed=False,
            search_query_count=0,
            search_results_considered=0,
            external_reads_count=0,
            result_candidates=[],
            snippets_used_as_evidence=False,
            facts_inferred_from_snippets=False,
            asked_user_for_url=False,
            blocked_reason=reason,
            error_code=reason,
            network_used=False,
        )


class ControlledSearchBackendRegistry:
    def __init__(self, config: ControlledBackendConfig):
        self.config = config

    def backend(self) -> ControlledSearchBackend:
        if self.config.search_backend_mode == "fixture":
            return FixtureSearchBackend()
        if self.config.search_backend_mode in PROVIDER_KEY_ENVS:
            return ApiSearchBackendStub(self.config.search_backend_mode)
        return DisabledSearchBackend()

    def run(self, request_payload: dict[str, Any]) -> ControlledSearchExecutionResult:
        request = ControlledSearchRequestEnvelope.from_mapping(request_payload)
        return self.backend().run(request, self.config)


__all__ = [
    "ControlledBackendConfig",
    "ControlledSearchBackendRegistry",
    "ControlledSearchExecutionResult",
    "ControlledSearchRequestEnvelope",
    "DisabledSearchBackend",
    "FixtureSearchBackend",
    "PROVIDER_KEY_ENVS",
    "PAGE_READ_ALLOW_NETWORK_ENV",
    "PAGE_READ_BACKEND_ENV",
    "SEARCH_ALLOW_NETWORK_ENV",
    "SEARCH_BACKEND_ENV",
    "SearchBudgetEnvelope",
    "SearchQueryEnvelope",
]
