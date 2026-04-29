#!/usr/bin/env python3
"""Budgeted controlled search runtime for L6.10X.

The default runtime is disabled and performs no network access. A future backend
may be used only when explicit config and environment gates are enabled. Search
snippets are metadata only and never evidence.
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
class SearchQuery:
    query_id: str
    query_text: str
    query_category: str
    max_results: int


@dataclass(frozen=True)
class SearchBudget:
    max_queries: int = 5
    max_search_results_considered: int = 20
    max_pages_opened: int = 8
    max_domains: int = 5
    max_pages_per_domain: int = 3
    max_crawl_depth: int = 1
    max_total_external_reads: int = 12


@dataclass(frozen=True)
class ControlledSearchRequest:
    request_id: str
    selected_work_order_id: str
    queries: list[SearchQuery]
    budget: SearchBudget
    snippets_are_evidence: bool = False
    facts_inferred_from_snippets: bool = False

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "ControlledSearchRequest":
        budget_payload = payload.get("budget", {})
        queries = [
            SearchQuery(
                query_id=str(item.get("query_id", "")),
                query_text=str(item.get("query_text", "")),
                query_category=str(item.get("query_category", "")),
                max_results=int(item.get("max_results", 1)),
            )
            for item in payload.get("queries", [])
        ]
        return cls(
            request_id=str(payload.get("request_id", "l6_10x_controlled_search_request")),
            selected_work_order_id=str(payload.get("selected_work_order_id", "")),
            queries=queries,
            budget=SearchBudget(
                max_queries=int(budget_payload.get("max_queries", 5)),
                max_search_results_considered=int(
                    budget_payload.get("max_search_results_considered", 20)
                ),
                max_pages_opened=int(budget_payload.get("max_pages_opened", 8)),
                max_domains=int(budget_payload.get("max_domains", 5)),
                max_pages_per_domain=int(budget_payload.get("max_pages_per_domain", 3)),
                max_crawl_depth=int(budget_payload.get("max_crawl_depth", 1)),
                max_total_external_reads=int(budget_payload.get("max_total_external_reads", 12)),
            ),
            snippets_are_evidence=bool(payload.get("snippets_are_evidence", False)),
            facts_inferred_from_snippets=bool(payload.get("facts_inferred_from_snippets", False)),
        )


@dataclass(frozen=True)
class ControlledSearchResult:
    backend_mode: str
    backend_explicitly_configured: bool = False
    search_executed: bool = False
    search_query_count: int = 0
    search_results_considered: int = 0
    external_reads_count: int = 0
    result_candidates: list[dict[str, Any]] = field(default_factory=list)
    snippets_used_as_evidence: bool = False
    facts_inferred_from_snippets: bool = False
    blocked_reason: str | None = "controlled_search_backend_required"
    error_code: str | None = "controlled_search_backend_required"
    trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ControlledSearchBackend:
    backend_id = "base_controlled_search_backend"

    def run(self, request: ControlledSearchRequest) -> ControlledSearchResult:
        raise NotImplementedError


class DisabledControlledSearchBackend(ControlledSearchBackend):
    backend_id = "disabled_controlled_search_backend"

    def run(self, request: ControlledSearchRequest) -> ControlledSearchResult:
        return ControlledSearchResult(
            backend_mode="disabled",
            trace={
                "request_id": request.request_id,
                "network_used": False,
                "search_executed": False,
                "queries_planned": len(request.queries),
                "manual_url_request": False,
            },
        )


class ConfiguredSingleBatchSearchBackend(ControlledSearchBackend):
    backend_id = "configured_single_batch_search_backend"

    def __init__(self, config: dict[str, Any]):
        self.config = config

    def run(self, request: ControlledSearchRequest) -> ControlledSearchResult:
        if not self.config.get("backend_available", False):
            return ControlledSearchResult(
                backend_mode="configured_but_unavailable",
                backend_explicitly_configured=True,
                blocked_reason="controlled_search_backend_unavailable",
                error_code="controlled_search_backend_unavailable",
                trace={"network_used": False, "search_executed": False},
            )
        candidates = list(self.config.get("result_candidates", []))[
            : request.budget.max_search_results_considered
        ]
        return ControlledSearchResult(
            backend_mode="configured_and_executed",
            backend_explicitly_configured=True,
            search_executed=True,
            search_query_count=min(len(request.queries), request.budget.max_queries),
            search_results_considered=len(candidates),
            external_reads_count=min(len(request.queries), request.budget.max_queries),
            result_candidates=candidates,
            blocked_reason=None,
            error_code=None,
            trace={
                "network_used": bool(self.config.get("external_network_read_used", False)),
                "search_executed": True,
                "snippets_used_as_evidence": False,
                "facts_inferred_from_snippets": False,
            },
        )


class ControlledSearchRuntime:
    def __init__(self, config_path: Path | None = None, config: dict[str, Any] | None = None):
        self.config_path = Path(config_path) if config_path else None
        self.config = config if config is not None else self._load_config()

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path or not self.config_path.exists():
            return {}
        return json.loads(self.config_path.read_text(encoding="utf-8"))

    def explicitly_configured(self) -> bool:
        return (
            os.environ.get(ENABLE_ENV_VAR) == "1"
            and bool(os.environ.get(BACKEND_ENV_VAR))
            and bool(self.config.get("controlled_search_enabled", False))
            and bool(self.config.get("backend_id"))
        )

    def backend(self) -> ControlledSearchBackend:
        if not self.explicitly_configured():
            return DisabledControlledSearchBackend()
        return ConfiguredSingleBatchSearchBackend(self.config)

    def run(self, request: ControlledSearchRequest) -> ControlledSearchResult:
        if self.config.get("l6_11_backend_registry_enabled") or self.config.get("search_backend_mode"):
            return self._run_l6_11_registry(request)
        return self.backend().run(request)

    def _run_l6_11_registry(self, request: ControlledSearchRequest) -> ControlledSearchResult:
        from controlled_search_backend_adapters.controlled_search_backends import (
            ControlledBackendConfig,
            ControlledSearchBackendRegistry,
        )

        registry_config = ControlledBackendConfig.from_environment(
            Path.cwd(),
            overrides={
                "search_backend_mode": self.config.get("search_backend_mode", "disabled"),
                "page_read_backend_mode": self.config.get("page_read_backend_mode", "disabled"),
                "search_network_allowed": self.config.get("search_network_allowed", False),
                "page_read_network_allowed": self.config.get("page_read_network_allowed", False),
                "fixture_results_path": self.config.get("fixture_results_path"),
                "fixture_pages_path": self.config.get("fixture_pages_path"),
            },
        )
        result = ControlledSearchBackendRegistry(registry_config).run(
            {
                "request_id": request.request_id,
                "selected_work_order_id": request.selected_work_order_id,
                "queries": [asdict(query) for query in request.queries],
                "budget": asdict(request.budget),
            }
        )
        payload = result.to_dict()
        error_code = payload.get("error_code")
        return ControlledSearchResult(
            backend_mode=payload.get("backend_mode", "disabled"),
            backend_explicitly_configured=payload.get("backend_explicitly_configured", False),
            search_executed=payload.get("search_executed", False),
            search_query_count=payload.get("search_query_count", 0),
            search_results_considered=payload.get("search_results_considered", 0),
            external_reads_count=payload.get("external_reads_count", 0),
            result_candidates=payload.get("result_candidates", []),
            snippets_used_as_evidence=payload.get("snippets_used_as_evidence", False),
            facts_inferred_from_snippets=payload.get("facts_inferred_from_snippets", False),
            blocked_reason=payload.get("blocked_reason", error_code),
            error_code=error_code,
            trace={
                "l6_11_backend_registry_enabled": True,
                "network_used": payload.get("network_used", False),
                "asked_user_for_url": payload.get("asked_user_for_url", False),
                "backend_name": payload.get("backend_name"),
            },
        )


__all__ = [
    "BACKEND_ENV_VAR",
    "ENABLE_ENV_VAR",
    "ConfiguredSingleBatchSearchBackend",
    "ControlledSearchBackend",
    "ControlledSearchRequest",
    "ControlledSearchResult",
    "ControlledSearchRuntime",
    "DisabledControlledSearchBackend",
    "SearchBudget",
    "SearchQuery",
]
