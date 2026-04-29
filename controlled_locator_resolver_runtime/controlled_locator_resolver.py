#!/usr/bin/env python3
"""Portable controlled locator resolver runtime for L6.10U.

The default runtime is local-only. It can resolve a locator from a repo-local
seed registry, can expose an environment-gated search adapter only when an
explicit config enables it, and otherwise returns a blocked disabled result.
It does not perform network access by default.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
from typing import Any


RUNTIME_LIMITS = {
    "max_selected_work_orders": 1,
    "max_locator_resolution_attempts": 1,
    "max_search_queries": 1,
    "max_seed_registry_lookups": 1,
    "max_concrete_locators_returned": 1,
    "max_pages_read": 1,
    "max_total_external_reads": 2,
    "max_crawled_links": 0,
    "max_followed_links_except_normal_redirect": 0,
    "max_login_attempts": 0,
    "max_forms_submitted": 0,
    "max_messages_sent": 0,
    "max_payments": 0,
}


@dataclass(frozen=True)
class LocatorResolutionRequest:
    request_id: str
    linked_work_order_id: str
    evidence_need_id: str
    source_type: str
    source_function: str
    observation_question: str
    locator_discovery_query: str
    max_queries: int = 1
    max_results: int = 1
    no_fact_inference_from_result: bool = True
    no_snippet_fact_use: bool = True
    no_broad_search: bool = True
    no_crawling: bool = True

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "LocatorResolutionRequest":
        return cls(
            request_id=str(payload.get("request_id", "l6_10u_locator_resolution_request_001")),
            linked_work_order_id=str(payload.get("linked_work_order_id", "")),
            evidence_need_id=str(payload.get("evidence_need_id", "")),
            source_type=str(payload.get("source_type", "")),
            source_function=str(payload.get("source_function", "")),
            observation_question=str(payload.get("observation_question", "")),
            locator_discovery_query=str(payload.get("locator_discovery_query", "")),
            max_queries=int(payload.get("max_queries", 1)),
            max_results=int(payload.get("max_results", 1)),
            no_fact_inference_from_result=bool(
                payload.get("no_fact_inference_from_result", True)
            ),
            no_snippet_fact_use=bool(payload.get("no_snippet_fact_use", True)),
            no_broad_search=bool(payload.get("no_broad_search", True)),
            no_crawling=bool(payload.get("no_crawling", True)),
        )


@dataclass(frozen=True)
class LocatorResolutionResult:
    resolver_mode: str
    resolver_id: str
    seed_registry_lookup_count: int = 0
    search_query_count: int = 0
    external_reads_count: int = 0
    concrete_locator_resolved: bool = False
    locator: str | None = None
    source_title: str | None = None
    source_type: str | None = None
    facts_inferred_from_resolution: bool = False
    eligible_for_read_only_observation: bool = False
    blocked_reason: str | None = None
    error_code: str | None = None
    trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BaseControlledLocatorResolver:
    resolver_id = "base_controlled_locator_resolver"
    resolver_mode = "base"

    def resolve(self, request: LocatorResolutionRequest) -> LocatorResolutionResult:
        raise NotImplementedError


class SeedRegistryResolver(BaseControlledLocatorResolver):
    resolver_id = "seed_registry_resolver"
    resolver_mode = "seed_registry"

    def __init__(self, registry_path: Path):
        self.registry_path = Path(registry_path)

    def _load_entries(self) -> list[dict[str, Any]]:
        if not self.registry_path.exists():
            return []
        payload = json.loads(self.registry_path.read_text(encoding="utf-8"))
        return list(payload.get("seed_locators", []))

    @staticmethod
    def _matches(request: LocatorResolutionRequest, entry: dict[str, Any]) -> bool:
        work_order_ids = set(entry.get("work_order_ids", []))
        evidence_need_ids = set(entry.get("evidence_need_ids", []))
        source_types = set(entry.get("source_types", []))
        source_functions = set(entry.get("source_functions", []))
        return any(
            [
                request.linked_work_order_id and request.linked_work_order_id in work_order_ids,
                request.evidence_need_id and request.evidence_need_id in evidence_need_ids,
                request.source_type and request.source_type in source_types,
                request.source_function and request.source_function in source_functions,
            ]
        )

    def resolve(self, request: LocatorResolutionRequest) -> LocatorResolutionResult:
        entries = self._load_entries()
        matching = [entry for entry in entries if self._matches(request, entry)]
        if not matching:
            return LocatorResolutionResult(
                resolver_mode=self.resolver_mode,
                resolver_id=self.resolver_id,
                seed_registry_lookup_count=1,
                blocked_reason="no_seed_locator_available",
                error_code="no_seed_locator_available",
                trace={
                    "registry_path": str(self.registry_path),
                    "entries_considered": len(entries),
                    "matches_returned": 0,
                    "network_used": False,
                    "facts_inferred_from_resolution": False,
                },
            )

        entry = matching[0]
        locator = entry.get("locator")
        return LocatorResolutionResult(
            resolver_mode=self.resolver_mode,
            resolver_id=self.resolver_id,
            seed_registry_lookup_count=1,
            concrete_locator_resolved=bool(locator),
            locator=locator,
            source_title=entry.get("source_title"),
            source_type=entry.get("source_type") or request.source_type,
            eligible_for_read_only_observation=bool(
                entry.get("eligible_for_read_only_observation", False)
            ),
            blocked_reason=None if locator else "seed_entry_missing_locator",
            error_code=None if locator else "seed_entry_missing_locator",
            trace={
                "registry_path": str(self.registry_path),
                "entries_considered": len(entries),
                "matches_returned": 1,
                "network_used": False,
                "facts_inferred_from_resolution": False,
            },
        )


class EnvironmentGatedSearchResolver(BaseControlledLocatorResolver):
    resolver_id = "environment_gated_controlled_search_resolver"
    resolver_mode = "environment_gated_search"

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def _enabled(self) -> bool:
        config_enabled = bool(self.config.get("environment_gated_search_enabled", False))
        env_enabled = os.environ.get("YSTAR_CONTROLLED_LOCATOR_SEARCH_ENABLED") == "1"
        return config_enabled and env_enabled

    def resolve(self, request: LocatorResolutionRequest) -> LocatorResolutionResult:
        if not self._enabled():
            return LocatorResolutionResult(
                resolver_mode=self.resolver_mode,
                resolver_id=self.resolver_id,
                blocked_reason="no_controlled_search_resolver_enabled",
                error_code="no_controlled_search_resolver_enabled",
                trace={
                    "search_executed": False,
                    "network_used": False,
                    "facts_inferred_from_resolution": False,
                },
            )

        locator = self.config.get("approved_single_result_locator")
        if not locator:
            return LocatorResolutionResult(
                resolver_mode=self.resolver_mode,
                resolver_id=self.resolver_id,
                search_query_count=1,
                external_reads_count=1,
                blocked_reason="controlled_search_enabled_but_no_result_provider",
                error_code="controlled_search_enabled_but_no_result_provider",
                trace={
                    "search_executed": True,
                    "queries_used": 1,
                    "results_considered": 0,
                    "network_used": False,
                    "facts_inferred_from_resolution": False,
                },
            )

        return LocatorResolutionResult(
            resolver_mode=self.resolver_mode,
            resolver_id=self.resolver_id,
            search_query_count=1,
            external_reads_count=1,
            concrete_locator_resolved=True,
            locator=str(locator),
            source_title=self.config.get("approved_single_result_title"),
            source_type=request.source_type,
            facts_inferred_from_resolution=False,
            eligible_for_read_only_observation=False,
            trace={
                "search_executed": True,
                "queries_used": 1,
                "results_considered": 1,
                "network_used": bool(self.config.get("external_network_read_used", False)),
                "facts_inferred_from_resolution": False,
                "snippet_used_as_fact": False,
            },
        )


class DisabledResolver(BaseControlledLocatorResolver):
    resolver_id = "disabled_resolver"
    resolver_mode = "disabled"

    def resolve(self, request: LocatorResolutionRequest) -> LocatorResolutionResult:
        return LocatorResolutionResult(
            resolver_mode=self.resolver_mode,
            resolver_id=self.resolver_id,
            blocked_reason="no_enabled_locator_resolution_path",
            error_code="no_enabled_locator_resolution_path",
            trace={
                "network_used": False,
                "search_executed": False,
                "facts_inferred_from_resolution": False,
                "fake_locator_returned": False,
            },
        )


class ControlledLocatorResolverRuntime:
    """Run one bounded resolver attempt in seed, search, then disabled order."""

    def __init__(
        self,
        root: Path,
        registry_path: Path | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.root = Path(root)
        self.registry_path = registry_path or (
            self.root / "controlled_locator_resolver_runtime" / "seed_locator_registry.json"
        )
        self.config = config or {}

    def resolve(self, request: LocatorResolutionRequest) -> LocatorResolutionResult:
        seed_result = SeedRegistryResolver(self.registry_path).resolve(request)
        if seed_result.concrete_locator_resolved:
            return seed_result

        search_result = EnvironmentGatedSearchResolver(self.config).resolve(request)
        if search_result.concrete_locator_resolved:
            return LocatorResolutionResult(
                **{
                    **search_result.to_dict(),
                    "seed_registry_lookup_count": seed_result.seed_registry_lookup_count,
                    "trace": {
                        "seed_registry": seed_result.trace,
                        "environment_gated_search": search_result.trace,
                    },
                }
            )

        disabled_result = DisabledResolver().resolve(request)
        return LocatorResolutionResult(
            resolver_mode=disabled_result.resolver_mode,
            resolver_id=disabled_result.resolver_id,
            seed_registry_lookup_count=seed_result.seed_registry_lookup_count,
            search_query_count=search_result.search_query_count,
            external_reads_count=search_result.external_reads_count,
            concrete_locator_resolved=False,
            locator=None,
            source_title=None,
            source_type=request.source_type,
            facts_inferred_from_resolution=False,
            eligible_for_read_only_observation=False,
            blocked_reason="no_enabled_locator_resolution_path",
            error_code="no_enabled_locator_resolution_path",
            trace={
                "seed_registry": seed_result.trace,
                "environment_gated_search": search_result.trace,
                "disabled": disabled_result.trace,
            },
        )


def write_trace(path: Path, result: LocatorResolutionResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8")


__all__ = [
    "LocatorResolutionRequest",
    "LocatorResolutionResult",
    "BaseControlledLocatorResolver",
    "SeedRegistryResolver",
    "EnvironmentGatedSearchResolver",
    "DisabledResolver",
    "ControlledLocatorResolverRuntime",
    "RUNTIME_LIMITS",
]
