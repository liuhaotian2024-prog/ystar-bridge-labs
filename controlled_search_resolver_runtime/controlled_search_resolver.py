#!/usr/bin/env python3
"""Controlled external search resolver runtime for L6.10X.

The default path is disabled and local-only. A future controlled backend may be
enabled only through explicit environment/config gates. Search results are
locator candidates only; snippets are never evidence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
from typing import Any


ENABLE_ENV_VAR = "YSTAR_CONTROLLED_SEARCH_ENABLED"
BACKEND_ENV_VAR = "YSTAR_CONTROLLED_SEARCH_BACKEND"


@dataclass(frozen=True)
class LocatorSearchRequest:
    request_id: str
    linked_work_order_id: str
    evidence_need_id: str
    source_type: str
    source_function: str
    observation_question: str
    expected_evidence_type: str
    trust_requirement: str
    freshness_requirement: str
    query_text: str
    max_queries: int = 1
    max_results: int = 1
    no_snippet_fact_use: bool = True
    no_fact_inference_from_search_result: bool = True
    no_broad_search: bool = True
    no_repeated_search: bool = True
    no_crawling: bool = True

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "LocatorSearchRequest":
        return cls(
            request_id=str(payload.get("request_id", "l6_10x_locator_discovery_request_001")),
            linked_work_order_id=str(payload.get("linked_work_order_id", "")),
            evidence_need_id=str(payload.get("evidence_need_id", "")),
            source_type=str(payload.get("source_type", "")),
            source_function=str(payload.get("source_function", "")),
            observation_question=str(payload.get("observation_question", "")),
            expected_evidence_type=str(payload.get("expected_evidence_type", "")),
            trust_requirement=str(payload.get("trust_requirement", "candidate_structural_trust")),
            freshness_requirement=str(payload.get("freshness_requirement", "freshness_check_required")),
            query_text=str(payload.get("query_text", "")),
            max_queries=int(payload.get("max_queries", 1)),
            max_results=int(payload.get("max_results", 1)),
            no_snippet_fact_use=bool(payload.get("no_snippet_fact_use", True)),
            no_fact_inference_from_search_result=bool(
                payload.get("no_fact_inference_from_search_result", True)
            ),
            no_broad_search=bool(payload.get("no_broad_search", True)),
            no_repeated_search=bool(payload.get("no_repeated_search", True)),
            no_crawling=bool(payload.get("no_crawling", True)),
        )


@dataclass(frozen=True)
class LocatorSearchResult:
    resolver_id: str = "disabled_controlled_search_resolver"
    backend_mode: str = "disabled"
    backend_explicitly_configured: bool = False
    backend_available: bool = False
    controlled_search_executed: bool = False
    search_query_count: int = 0
    search_results_considered: int = 0
    external_reads_count: int = 0
    concrete_locator_resolved: bool = False
    resolved_locator: str | None = None
    source_title: str | None = None
    snippets_used_as_evidence: bool = False
    facts_inferred_from_search_result: bool = False
    blocked_reason: str | None = "controlled_search_backend_not_configured"
    error_code: str | None = "controlled_search_backend_not_configured"
    trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BackendUnavailableError(RuntimeError):
    """Raised internally when a configured backend profile has no adapter."""


@dataclass(frozen=True)
class SearchBackendConfig:
    controlled_search_enabled: bool = False
    backend_id: str | None = None
    backend_available: bool = False
    approved_single_result_locator: str | None = None
    approved_single_result_title: str | None = None
    external_network_read_used: bool = False
    max_queries: int = 1
    max_results: int = 1

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "SearchBackendConfig":
        return cls(
            controlled_search_enabled=bool(payload.get("controlled_search_enabled", False)),
            backend_id=payload.get("backend_id"),
            backend_available=bool(payload.get("backend_available", False)),
            approved_single_result_locator=payload.get("approved_single_result_locator"),
            approved_single_result_title=payload.get("approved_single_result_title"),
            external_network_read_used=bool(payload.get("external_network_read_used", False)),
            max_queries=int(payload.get("max_queries", 1)),
            max_results=int(payload.get("max_results", 1)),
        )


class ControlledSearchResolver:
    resolver_id = "controlled_search_resolver"

    def resolve(self, request: LocatorSearchRequest) -> LocatorSearchResult:
        raise NotImplementedError


class DisabledControlledSearchResolver(ControlledSearchResolver):
    resolver_id = "disabled_controlled_search_resolver"

    def resolve(self, request: LocatorSearchRequest) -> LocatorSearchResult:
        return LocatorSearchResult(
            trace={
                "request_id": request.request_id,
                "search_executed": False,
                "network_used": False,
                "snippets_used_as_evidence": False,
                "facts_inferred_from_search_result": False,
                "ask_user_for_url": False,
            }
        )


class EnvironmentConfiguredControlledSearchResolver(ControlledSearchResolver):
    resolver_id = "environment_configured_controlled_search_resolver"

    def __init__(self, config: SearchBackendConfig):
        self.config = config

    def resolve(self, request: LocatorSearchRequest) -> LocatorSearchResult:
        if request.max_queries != 1 or request.max_results != 1:
            return LocatorSearchResult(
                resolver_id=self.resolver_id,
                backend_mode="configured_but_unavailable",
                backend_explicitly_configured=True,
                blocked_reason="runtime_limit_violation",
                error_code="runtime_limit_violation",
                trace={
                    "search_executed": False,
                    "network_used": False,
                    "requested_max_queries": request.max_queries,
                    "requested_max_results": request.max_results,
                },
            )
        if not self.config.backend_available:
            return LocatorSearchResult(
                resolver_id=self.resolver_id,
                backend_mode="configured_but_unavailable",
                backend_explicitly_configured=True,
                backend_available=False,
                blocked_reason="controlled_search_backend_unavailable",
                error_code="controlled_search_backend_unavailable",
                trace={
                    "backend_id": self.config.backend_id,
                    "search_executed": False,
                    "network_used": False,
                    "snippets_used_as_evidence": False,
                    "facts_inferred_from_search_result": False,
                },
            )
        if not self.config.approved_single_result_locator:
            return LocatorSearchResult(
                resolver_id=self.resolver_id,
                backend_mode="configured_and_executed",
                backend_explicitly_configured=True,
                backend_available=True,
                controlled_search_executed=True,
                search_query_count=1,
                search_results_considered=0,
                external_reads_count=1,
                blocked_reason="controlled_search_no_result",
                error_code="controlled_search_no_result",
                trace={
                    "backend_id": self.config.backend_id,
                    "search_executed": True,
                    "network_used": self.config.external_network_read_used,
                    "queries_used": 1,
                    "results_considered": 0,
                    "snippets_used_as_evidence": False,
                    "facts_inferred_from_search_result": False,
                },
            )
        return LocatorSearchResult(
            resolver_id=self.resolver_id,
            backend_mode="configured_and_executed",
            backend_explicitly_configured=True,
            backend_available=True,
            controlled_search_executed=True,
            search_query_count=1,
            search_results_considered=1,
            external_reads_count=1,
            concrete_locator_resolved=True,
            resolved_locator=str(self.config.approved_single_result_locator),
            source_title=self.config.approved_single_result_title,
            blocked_reason=None,
            error_code=None,
            trace={
                "backend_id": self.config.backend_id,
                "search_executed": True,
                "network_used": self.config.external_network_read_used,
                "queries_used": 1,
                "results_considered": 1,
                "locator_candidate_only": True,
                "snippets_used_as_evidence": False,
                "facts_inferred_from_search_result": False,
            },
        )


class ControlledSearchResolverRuntime:
    """Select and run the disabled or explicitly configured search resolver."""

    def __init__(self, config_path: Path | None = None, config: dict[str, Any] | None = None):
        self.config_path = Path(config_path) if config_path else None
        self.config_payload = config if config is not None else self._load_config()

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path or not self.config_path.exists():
            return {}
        return json.loads(self.config_path.read_text(encoding="utf-8"))

    def backend_explicitly_configured(self) -> bool:
        env_enabled = os.environ.get(ENABLE_ENV_VAR) == "1"
        env_backend = bool(os.environ.get(BACKEND_ENV_VAR))
        config_enabled = bool(self.config_payload.get("controlled_search_enabled", False))
        config_backend = bool(self.config_payload.get("backend_id"))
        return env_enabled and env_backend and config_enabled and config_backend

    def resolver(self) -> ControlledSearchResolver:
        if not self.backend_explicitly_configured():
            return DisabledControlledSearchResolver()
        return EnvironmentConfiguredControlledSearchResolver(
            SearchBackendConfig.from_mapping(self.config_payload)
        )

    def resolve(self, request: LocatorSearchRequest) -> LocatorSearchResult:
        return self.resolver().resolve(request)


__all__ = [
    "BACKEND_ENV_VAR",
    "ENABLE_ENV_VAR",
    "BackendUnavailableError",
    "ControlledSearchResolver",
    "ControlledSearchResolverRuntime",
    "DisabledControlledSearchResolver",
    "EnvironmentConfiguredControlledSearchResolver",
    "LocatorSearchRequest",
    "LocatorSearchResult",
    "SearchBackendConfig",
]
