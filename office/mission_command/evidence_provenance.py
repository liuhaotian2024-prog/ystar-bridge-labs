from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from .tier1_public_research import (
    Tier1ResearchBudget,
    Tier1ResearchReceipt,
    Tier1SourceEvidence,
    safety_boundary,
    utc_now,
    validate_receipt,
    validate_source_evidence,
)


class EvidenceProviderMode:
    DISABLED = "disabled"
    FIXTURE_ONLY = "fixture_only"
    SOURCE_SEED_LIVE_PUBLIC_READ_ONLY = "source_seed_live_public_read_only"
    SEARCH_PROVIDER_LIVE_PUBLIC_READ_ONLY = "search_provider_live_public_read_only"
    BLOCKED_MISSING_PROVIDER = "blocked_missing_provider"
    BLOCKED_MISSING_SOURCE_SEEDS = "blocked_missing_source_seeds"


LIVE_MODES = {
    EvidenceProviderMode.SOURCE_SEED_LIVE_PUBLIC_READ_ONLY,
    EvidenceProviderMode.SEARCH_PROVIDER_LIVE_PUBLIC_READ_ONLY,
}


@dataclass(frozen=True)
class EvidenceRunBundle:
    run_id: str
    mission_id: str
    provider_name: str
    provider_mode: str
    live_public_read_only: bool
    fixture_only: bool
    validated_live: bool
    receipt: Dict[str, Any]
    sources: List[Dict[str, Any]]
    source_summary_paths: List[str]
    validation_errors: List[str]
    budget: Dict[str, Any]
    safety_boundary: Dict[str, bool]
    started_at: str
    completed_at: str
    blocked_reason: str
    exact_unblock_action: List[str]
    external_action_executed: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _source_from_dict(source: Dict[str, Any]) -> Tier1SourceEvidence:
    return Tier1SourceEvidence(
        source_id=str(source.get("source_id", "")),
        url_or_public_identifier=str(source.get("url_or_public_identifier", "")),
        domain=str(source.get("domain", "")),
        source_category=str(source.get("source_category", "")),
        retrieved_at=str(source.get("retrieved_at", "")),
        evidence_type=str(source.get("evidence_type", "")),
        relevant_opportunity_ids=list(source.get("relevant_opportunity_ids", [])),
        summary=str(source.get("summary", "")),
        buyer_pain_signal=str(source.get("buyer_pain_signal", "")),
        pricing_signal=str(source.get("pricing_signal", "")),
        competitor_signal=str(source.get("competitor_signal", "")),
        substitute_signal=str(source.get("substitute_signal", "")),
        budget_signal=str(source.get("budget_signal", "")),
        confidence=str(source.get("confidence", "")),
        limitations=list(source.get("limitations", [])),
    )


def _receipt_from_dict(receipt: Dict[str, Any]) -> Tier1ResearchReceipt:
    return Tier1ResearchReceipt(
        mission_id=str(receipt.get("mission_id", "")),
        live_research_executed=bool(receipt.get("live_research_executed", False)),
        provider_name=str(receipt.get("provider_name", "")),
        started_at=str(receipt.get("started_at", "")),
        completed_at=str(receipt.get("completed_at", "")),
        queries_used=list(receipt.get("queries_used", [])),
        pages_read=list(receipt.get("pages_read", [])),
        domains_touched=list(receipt.get("domains_touched", [])),
        stopped_reason=str(receipt.get("stopped_reason", "")),
        safety_boundary=dict(receipt.get("safety_boundary", {})),
        external_action_executed=bool(receipt.get("external_action_executed", False)),
        errors=list(receipt.get("errors", [])),
        source_summary_paths=list(receipt.get("source_summary_paths", [])),
    )


def validate_evidence_run_bundle(bundle: EvidenceRunBundle | Dict[str, Any]) -> List[str]:
    data = bundle.to_dict() if isinstance(bundle, EvidenceRunBundle) else dict(bundle)
    errors: List[str] = []
    provider_mode = str(data.get("provider_mode", ""))
    sources = [_source_from_dict(item) for item in data.get("sources", [])]
    receipt = _receipt_from_dict(data.get("receipt", {}))
    errors.extend(validate_receipt(receipt, sources))
    if provider_mode not in {
        EvidenceProviderMode.DISABLED,
        EvidenceProviderMode.FIXTURE_ONLY,
        EvidenceProviderMode.SOURCE_SEED_LIVE_PUBLIC_READ_ONLY,
        EvidenceProviderMode.SEARCH_PROVIDER_LIVE_PUBLIC_READ_ONLY,
        EvidenceProviderMode.BLOCKED_MISSING_PROVIDER,
        EvidenceProviderMode.BLOCKED_MISSING_SOURCE_SEEDS,
    }:
        errors.append("invalid_provider_mode")
    if data.get("external_action_executed"):
        errors.append("external_action_executed")
    if data.get("fixture_only") and data.get("validated_live"):
        errors.append("fixture_cannot_be_validated_live")
    if data.get("validated_live") and provider_mode not in LIVE_MODES:
        errors.append("validated_live_requires_live_provider_mode")
    if data.get("validated_live") and not data.get("live_public_read_only"):
        errors.append("validated_live_requires_live_public_read_only")
    if data.get("validated_live") and not data.get("source_summary_paths"):
        errors.append("validated_live_requires_source_summary_paths")
    if data.get("validated_live") and not sources:
        errors.append("validated_live_requires_sources")
    for source in sources:
        errors.extend(validate_source_evidence(source))
        if not source.retrieved_at:
            errors.append(f"source_missing_retrieved_at:{source.source_id}")
        if not source.relevant_opportunity_ids:
            errors.append(f"source_missing_relevant_opportunity_ids:{source.source_id}")
    if receipt.live_research_executed and provider_mode not in LIVE_MODES:
        errors.append("receipt_live_true_requires_live_provider_mode")
    return list(dict.fromkeys(errors))


def evidence_bundle_is_market_backing_eligible(bundle: EvidenceRunBundle | Dict[str, Any]) -> bool:
    data = bundle.to_dict() if isinstance(bundle, EvidenceRunBundle) else dict(bundle)
    return bool(data.get("validated_live")) and not validate_evidence_run_bundle(data)


def build_evidence_run_bundle(
    *,
    run_id: str,
    mission_id: str,
    provider_name: str,
    provider_mode: str,
    receipt: Dict[str, Any] | None = None,
    sources: List[Dict[str, Any]] | None = None,
    source_summary_paths: List[str] | None = None,
    budget: Dict[str, Any] | None = None,
    blocked_reason: str = "",
    exact_unblock_action: List[str] | None = None,
    fixture_only: bool = False,
) -> EvidenceRunBundle:
    now = utc_now()
    receipt_payload = receipt or {
        "mission_id": mission_id,
        "live_research_executed": False,
        "provider_name": provider_name,
        "started_at": now,
        "completed_at": now,
        "queries_used": [],
        "pages_read": [],
        "domains_touched": [],
        "stopped_reason": blocked_reason or provider_mode,
        "safety_boundary": safety_boundary(),
        "external_action_executed": False,
        "errors": [blocked_reason] if blocked_reason else [],
        "source_summary_paths": source_summary_paths or [],
    }
    source_payload = sources or []
    summary_paths = source_summary_paths or list(receipt_payload.get("source_summary_paths", []))
    live_mode = provider_mode in LIVE_MODES
    preliminary = {
        "run_id": run_id,
        "mission_id": mission_id,
        "provider_name": provider_name,
        "provider_mode": provider_mode,
        "live_public_read_only": bool(live_mode and receipt_payload.get("live_research_executed") and source_payload),
        "fixture_only": fixture_only or provider_mode == EvidenceProviderMode.FIXTURE_ONLY,
        "validated_live": False,
        "receipt": receipt_payload,
        "sources": source_payload,
        "source_summary_paths": summary_paths,
        "validation_errors": [],
        "budget": budget or Tier1ResearchBudget().to_dict(),
        "safety_boundary": dict(receipt_payload.get("safety_boundary", safety_boundary())),
        "started_at": str(receipt_payload.get("started_at", now)),
        "completed_at": str(receipt_payload.get("completed_at", now)),
        "blocked_reason": blocked_reason,
        "exact_unblock_action": exact_unblock_action or [],
        "external_action_executed": bool(receipt_payload.get("external_action_executed", False)),
    }
    validation_errors = validate_evidence_run_bundle(preliminary)
    validated_live = (
        not validation_errors
        and preliminary["live_public_read_only"]
        and not preliminary["fixture_only"]
        and bool(summary_paths)
    )
    final = dict(preliminary)
    final["validated_live"] = validated_live
    final["validation_errors"] = validate_evidence_run_bundle(final)
    return EvidenceRunBundle(**final)


def render_evidence_provenance_report(bundle: EvidenceRunBundle | Dict[str, Any]) -> str:
    data = bundle.to_dict() if isinstance(bundle, EvidenceRunBundle) else dict(bundle)
    lines = [
        "# E5 Evidence Provenance Report",
        "",
        f"- run_id: {data.get('run_id')}",
        f"- mission_id: {data.get('mission_id')}",
        f"- provider_name: {data.get('provider_name')}",
        f"- provider_mode: {data.get('provider_mode')}",
        f"- live_public_read_only: {data.get('live_public_read_only')}",
        f"- fixture_only: {data.get('fixture_only')}",
        f"- validated_live: {data.get('validated_live')}",
        f"- market_backing_eligible: {evidence_bundle_is_market_backing_eligible(data)}",
        f"- external_action_executed: {data.get('external_action_executed')}",
        f"- blocked_reason: {data.get('blocked_reason') or 'none'}",
        "",
        "## Source Summary Paths",
    ]
    paths = data.get("source_summary_paths", [])
    lines.extend(f"- {item}" for item in paths) if paths else lines.append("- none")
    lines.extend(["", "## Sources"])
    sources = data.get("sources", [])
    if not sources:
        lines.append("- none")
    for source in sources:
        lines.extend(
            [
                f"### {source.get('source_id')}",
                f"- public_identifier: {source.get('url_or_public_identifier')}",
                f"- domain: {source.get('domain')}",
                f"- category: {source.get('source_category')}",
                f"- relevant_opportunity_ids: {', '.join(source.get('relevant_opportunity_ids', []))}",
                f"- summary: {source.get('summary')}",
            ]
        )
    lines.extend(["", "## Validation Errors"])
    errors = data.get("validation_errors", [])
    lines.extend(f"- {item}" for item in errors) if errors else lines.append("- none")
    if data.get("exact_unblock_action"):
        lines.extend(["", "## Exact Unblock Action"])
        lines.extend(f"- {item}" for item in data["exact_unblock_action"])
    return "\n".join(lines)
