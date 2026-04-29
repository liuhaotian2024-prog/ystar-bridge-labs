"""Portable controlled locator resolver interface for L6.10T.

The default implementation is DisabledNoNetworkResolver. It performs no network
access and returns a typed capability gap. Future live adapters must be
separately approved and gated before use.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol


@dataclass(frozen=True)
class LocatorResolutionRequest:
    request_id: str
    linked_work_order_id: str
    evidence_need_id: str | None
    source_type: str | None
    source_function: str
    observation_question: str | None
    locator_discovery_query: str
    max_queries: int = 1
    max_results: int = 1
    no_fact_inference_from_result: bool = True
    no_snippet_fact_use: bool = True
    no_broad_search: bool = True
    no_crawling: bool = True


@dataclass(frozen=True)
class LocatorResolutionResult:
    concrete_locator_resolved: bool
    locator: str | None
    source_title: str | None
    source_type: str | None
    resolution_method: str
    queries_used: int
    external_reads_used: int
    facts_inferred: bool
    eligible_for_read_only_observation: bool
    error_code: str | None
    blocked_reason: str | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ControlledLocatorResolver(Protocol):
    adapter_id: str
    network_enabled: bool

    def resolve(self, request: LocatorResolutionRequest) -> LocatorResolutionResult:
        """Resolve at most one concrete locator or return a typed blocked result."""


@dataclass(frozen=True)
class ResolverCapability:
    adapter_id: str
    available: bool
    mode: str
    live_external_authority_granted: bool


class DisabledNoNetworkResolver:
    adapter_id = "disabled_no_network_resolver"
    network_enabled = False

    def capability(self) -> ResolverCapability:
        return ResolverCapability(
            adapter_id=self.adapter_id,
            available=True,
            mode="disabled_no_network",
            live_external_authority_granted=False,
        )

    def resolve(self, request: LocatorResolutionRequest) -> LocatorResolutionResult:
        return LocatorResolutionResult(
            concrete_locator_resolved=False,
            locator=None,
            source_title=None,
            source_type=request.source_type,
            resolution_method="disabled_no_network",
            queries_used=0,
            external_reads_used=0,
            facts_inferred=False,
            eligible_for_read_only_observation=False,
            error_code="no_controlled_locator_resolver_available",
            blocked_reason="Default resolver is disabled and has no live external authority.",
        )
