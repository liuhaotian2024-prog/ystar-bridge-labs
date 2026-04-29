#!/usr/bin/env python3
"""Explicit opt-in controlled search resolver for L6.10V.

The default behavior is blocked and local-only. This module does not implement
web search itself; it only gates an explicitly configured single-result backend
fixture or future approved backend behind both config and environment flags.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
from typing import Any


ENABLE_ENV_VAR = "YSTAR_ENABLE_CONTROLLED_LOCATOR_SEARCH"


@dataclass(frozen=True)
class ExplicitSearchResolutionRequest:
    request_id: str
    linked_work_order_id: str
    source_type: str
    observation_question: str
    locator_discovery_query: str
    max_queries: int = 1
    max_results: int = 1
    no_snippet_fact_use: bool = True
    no_fact_inference_from_search_result: bool = True
    no_broad_search: bool = True
    no_repeated_search: bool = True
    no_crawling: bool = True

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "ExplicitSearchResolutionRequest":
        return cls(
            request_id=str(payload.get("request_id", "l6_10v_locator_resolution_v_request_001")),
            linked_work_order_id=str(payload.get("linked_work_order_id", "")),
            source_type=str(payload.get("source_type", "")),
            observation_question=str(payload.get("observation_question", "")),
            locator_discovery_query=str(payload.get("locator_discovery_query", "")),
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
class ExplicitSearchResolutionResult:
    resolver_id: str = "explicit_controlled_search_resolver"
    resolver_enabled: bool = False
    backend_available: bool = False
    controlled_search_query_count: int = 0
    external_reads_count: int = 0
    concrete_locator_resolved: bool = False
    resolved_locator: str | None = None
    source_title: str | None = None
    facts_inferred_from_resolution: bool = False
    snippets_used_as_evidence: bool = False
    error_code: str | None = "controlled_search_resolver_disabled_by_default"
    blocked_reason: str | None = "controlled_search_resolver_disabled_by_default"
    trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExplicitControlledSearchResolver:
    """Gate a future one-query locator resolver behind explicit opt-in flags."""

    def __init__(self, config_path: Path | None = None, config: dict[str, Any] | None = None):
        self.config_path = Path(config_path) if config_path else None
        self.config = config if config is not None else self._load_config()

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path or not self.config_path.exists():
            return {}
        return json.loads(self.config_path.read_text(encoding="utf-8"))

    def enabled(self) -> bool:
        config_enabled = bool(self.config.get("controlled_search_enabled", False))
        env_enabled = os.environ.get(ENABLE_ENV_VAR) == "1"
        guard_allows_one_query = int(self.config.get("max_queries", 1)) == 1
        return config_enabled and env_enabled and guard_allows_one_query

    def resolve(self, request: ExplicitSearchResolutionRequest) -> ExplicitSearchResolutionResult:
        if not self.enabled():
            return ExplicitSearchResolutionResult(
                trace={
                    "config_enabled": bool(self.config.get("controlled_search_enabled", False)),
                    "env_flag_required": ENABLE_ENV_VAR,
                    "env_flag_enabled": os.environ.get(ENABLE_ENV_VAR) == "1",
                    "search_executed": False,
                    "network_used": False,
                    "facts_inferred_from_resolution": False,
                }
            )

        backend_available = bool(self.config.get("controlled_search_backend_available", False))
        if not backend_available:
            return ExplicitSearchResolutionResult(
                resolver_enabled=True,
                backend_available=False,
                controlled_search_query_count=1,
                external_reads_count=0,
                error_code="controlled_search_backend_unavailable",
                blocked_reason="controlled_search_backend_unavailable",
                trace={
                    "search_requested": True,
                    "queries_used": 1,
                    "results_considered": 0,
                    "network_used": False,
                    "snippets_used_as_evidence": False,
                    "facts_inferred_from_resolution": False,
                },
            )

        locator = self.config.get("approved_single_result_locator")
        if not locator:
            return ExplicitSearchResolutionResult(
                resolver_enabled=True,
                backend_available=True,
                controlled_search_query_count=1,
                external_reads_count=1,
                error_code="controlled_search_no_result",
                blocked_reason="controlled_search_no_result",
                trace={
                    "search_requested": True,
                    "queries_used": 1,
                    "results_considered": 0,
                    "network_used": bool(self.config.get("external_network_read_used", False)),
                    "snippets_used_as_evidence": False,
                    "facts_inferred_from_resolution": False,
                },
            )

        return ExplicitSearchResolutionResult(
            resolver_enabled=True,
            backend_available=True,
            controlled_search_query_count=1,
            external_reads_count=1,
            concrete_locator_resolved=True,
            resolved_locator=str(locator),
            source_title=self.config.get("approved_single_result_title"),
            facts_inferred_from_resolution=False,
            snippets_used_as_evidence=False,
            error_code=None,
            blocked_reason=None,
            trace={
                "search_requested": True,
                "queries_used": 1,
                "results_considered": 1,
                "network_used": bool(self.config.get("external_network_read_used", False)),
                "snippets_used_as_evidence": False,
                "facts_inferred_from_resolution": False,
                "locator_candidate_only": True,
            },
        )


__all__ = [
    "ENABLE_ENV_VAR",
    "ExplicitControlledSearchResolver",
    "ExplicitSearchResolutionRequest",
    "ExplicitSearchResolutionResult",
]
