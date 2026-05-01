from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Protocol
from urllib.parse import urlparse


FORBIDDEN_ACTIONS = [
    "login",
    "customer_contact",
    "email_or_message",
    "publication",
    "form_submission",
    "payment",
    "account_creation",
    "paywall_bypass",
    "private_data_scraping",
    "secret_or_env_value_reading",
    "core_db_writeback",
    "obligation_registration",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def domain_from_identifier(identifier: str) -> str:
    parsed = urlparse(identifier)
    if parsed.netloc:
        return parsed.netloc.lower()
    return str(identifier).split("/")[0].lower()


@dataclass(frozen=True)
class Tier1ResearchBudget:
    max_search_queries: int = 25
    max_pages_read: int = 40
    max_domains: int = 20
    max_runtime_seconds: int = 300

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Tier1ResearchRequest:
    mission_id: str
    allowed_source_categories: List[str]
    query_plan: List[str]
    page_read_plan: List[str]
    budget: Tier1ResearchBudget
    stop_conditions: List[str]
    forbidden_actions: List[str] = field(default_factory=lambda: list(FORBIDDEN_ACTIONS))

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["budget"] = self.budget.to_dict()
        return data


@dataclass(frozen=True)
class Tier1SourceEvidence:
    source_id: str
    url_or_public_identifier: str
    domain: str
    source_category: str
    retrieved_at: str
    evidence_type: str
    relevant_opportunity_ids: List[str]
    summary: str
    buyer_pain_signal: str
    pricing_signal: str
    competitor_signal: str
    substitute_signal: str
    budget_signal: str
    confidence: str
    limitations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Tier1ResearchReceipt:
    mission_id: str
    live_research_executed: bool
    provider_name: str
    started_at: str
    completed_at: str
    queries_used: List[str]
    pages_read: List[str]
    domains_touched: List[str]
    stopped_reason: str
    safety_boundary: Dict[str, bool]
    external_action_executed: bool
    errors: List[str]
    source_summary_paths: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Tier1ResearchProvider(Protocol):
    provider_name: str

    def available(self) -> bool:
        ...

    def run(self, request: Tier1ResearchRequest) -> tuple[Tier1ResearchReceipt, List[Tier1SourceEvidence]]:
        ...


def safety_boundary() -> Dict[str, bool]:
    return {
        "get_read_only": True,
        "no_login": True,
        "no_contact": True,
        "no_email_or_message": True,
        "no_form_submission": True,
        "no_payment": True,
        "no_publication": True,
        "no_account_creation": True,
        "no_private_data": True,
        "no_secret_value_reading": True,
        "no_core_db_writeback": True,
    }


def validate_request_safety(request: Tier1ResearchRequest) -> List[str]:
    errors: List[str] = []
    forbidden_text = " ".join(request.forbidden_actions).lower()
    for required in FORBIDDEN_ACTIONS:
        if required not in forbidden_text:
            errors.append(f"missing_forbidden_action:{required}")
    for url in request.page_read_plan:
        parsed = urlparse(url)
        if parsed.scheme and parsed.scheme not in {"http", "https"}:
            errors.append(f"non_public_scheme:{url}")
        if parsed.hostname and parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}:
            errors.append(f"private_or_local_url:{url}")
    return errors


def enforce_budget(request: Tier1ResearchRequest) -> List[str]:
    errors: List[str] = []
    if len(request.query_plan) > request.budget.max_search_queries:
        errors.append("budget_exceeded:max_search_queries")
    if len(request.page_read_plan) > request.budget.max_pages_read:
        errors.append("budget_exceeded:max_pages_read")
    domains = {domain_from_identifier(url) for url in request.page_read_plan if url}
    if len(domains) > request.budget.max_domains:
        errors.append("budget_exceeded:max_domains")
    return errors


def validate_source_evidence(source: Tier1SourceEvidence) -> List[str]:
    errors = []
    if not source.url_or_public_identifier:
        errors.append("missing_public_identifier")
    if not source.domain:
        errors.append("missing_domain")
    if not source.source_category:
        errors.append("missing_source_category")
    if not source.summary:
        errors.append("missing_summary")
    return errors


def validate_receipt(receipt: Tier1ResearchReceipt, sources: Iterable[Tier1SourceEvidence]) -> List[str]:
    source_list = list(sources)
    errors: List[str] = []
    if receipt.live_research_executed and not source_list:
        errors.append("live_research_true_without_sources")
    if receipt.live_research_executed and not receipt.source_summary_paths:
        errors.append("live_research_true_without_source_summary_paths")
    if receipt.external_action_executed:
        errors.append("external_action_executed")
    for source in source_list:
        errors.extend(validate_source_evidence(source))
    return errors


class DisabledTier1ResearchProvider:
    provider_name = "disabled_no_safe_search_provider"

    def available(self) -> bool:
        return False

    def run(self, request: Tier1ResearchRequest) -> tuple[Tier1ResearchReceipt, List[Tier1SourceEvidence]]:
        now = utc_now()
        errors = validate_request_safety(request) + enforce_budget(request)
        receipt = Tier1ResearchReceipt(
            mission_id=request.mission_id,
            live_research_executed=False,
            provider_name=self.provider_name,
            started_at=now,
            completed_at=now,
            queries_used=[],
            pages_read=[],
            domains_touched=[],
            stopped_reason="blocked_missing_safe_search_provider",
            safety_boundary=safety_boundary(),
            external_action_executed=False,
            errors=errors or ["provider_unavailable"],
            source_summary_paths=[],
        )
        return receipt, []


class DeterministicFakeTier1ResearchProvider:
    """Offline deterministic provider for tests only; never used as live market evidence."""

    provider_name = "deterministic_fake_test_provider"

    def __init__(self, evidence: List[Tier1SourceEvidence] | None = None) -> None:
        self._evidence = evidence or []

    def available(self) -> bool:
        return True

    def run(self, request: Tier1ResearchRequest) -> tuple[Tier1ResearchReceipt, List[Tier1SourceEvidence]]:
        now = utc_now()
        errors = validate_request_safety(request) + enforce_budget(request)
        if errors:
            return (
                Tier1ResearchReceipt(
                    mission_id=request.mission_id,
                    live_research_executed=False,
                    provider_name=self.provider_name,
                    started_at=now,
                    completed_at=now,
                    queries_used=[],
                    pages_read=[],
                    domains_touched=[],
                    stopped_reason="blocked_by_budget_or_safety",
                    safety_boundary=safety_boundary(),
                    external_action_executed=False,
                    errors=errors,
                    source_summary_paths=[],
                ),
                [],
            )
        pages = request.page_read_plan[: request.budget.max_pages_read]
        domains = sorted({domain_from_identifier(url) for url in pages})
        evidence = self._evidence
        receipt = Tier1ResearchReceipt(
            mission_id=request.mission_id,
            live_research_executed=bool(evidence),
            provider_name=self.provider_name,
            started_at=now,
            completed_at=now,
            queries_used=request.query_plan[: request.budget.max_search_queries],
            pages_read=pages,
            domains_touched=domains,
            stopped_reason="fixture_complete" if evidence else "no_sources_returned",
            safety_boundary=safety_boundary(),
            external_action_executed=False,
            errors=[],
            source_summary_paths=["reports/integration/test_source_summaries.md"] if evidence else [],
        )
        return receipt, evidence


def write_receipt_and_summaries(
    repo_root: Path,
    receipt: Tier1ResearchReceipt,
    sources: List[Tier1SourceEvidence],
    receipt_name: str,
    summaries_name: str,
) -> Dict[str, Path]:
    out_dir = repo_root / "reports" / "integration"
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = out_dir / receipt_name
    summaries_path = out_dir / summaries_name
    receipt_lines = [
        f"# {receipt_name.replace('_', ' ').replace('.md', '').title()}",
        "",
        f"- mission_id: {receipt.mission_id}",
        f"- provider_name: {receipt.provider_name}",
        f"- live_research_executed: {receipt.live_research_executed}",
        f"- queries_used_count: {len(receipt.queries_used)}",
        f"- pages_read_count: {len(receipt.pages_read)}",
        f"- domains_touched_count: {len(receipt.domains_touched)}",
        f"- stopped_reason: {receipt.stopped_reason}",
        f"- external_action_executed: {receipt.external_action_executed}",
        "",
        "## Queries Used",
    ]
    receipt_lines.extend(f"- {item}" for item in receipt.queries_used)
    receipt_lines.extend(["", "## Pages Read"])
    receipt_lines.extend(f"- {item}" for item in receipt.pages_read)
    receipt_lines.extend(["", "## Domains Touched"])
    receipt_lines.extend(f"- {item}" for item in receipt.domains_touched)
    receipt_lines.extend(["", "## Safety Boundary"])
    receipt_lines.extend(f"- {key}: {value}" for key, value in receipt.safety_boundary.items())
    if receipt.errors:
        receipt_lines.extend(["", "## Errors"])
        receipt_lines.extend(f"- {item}" for item in receipt.errors)
    receipt_path.write_text("\n".join(receipt_lines) + "\n", encoding="utf-8")

    summary_lines = [f"# {summaries_name.replace('_', ' ').replace('.md', '').title()}", ""]
    if not sources:
        summary_lines.append("No live public source summaries were produced.")
    for source in sources:
        summary_lines.extend(
            [
                f"## {source.source_id}",
                f"- public_identifier: {source.url_or_public_identifier}",
                f"- domain: {source.domain}",
                f"- source_category: {source.source_category}",
                f"- evidence_type: {source.evidence_type}",
                f"- relevant_opportunity_ids: {', '.join(source.relevant_opportunity_ids)}",
                f"- buyer_pain_signal: {source.buyer_pain_signal}",
                f"- pricing_signal: {source.pricing_signal}",
                f"- competitor_signal: {source.competitor_signal}",
                f"- substitute_signal: {source.substitute_signal}",
                f"- budget_signal: {source.budget_signal}",
                f"- confidence: {source.confidence}",
                f"- limitations: {', '.join(source.limitations)}",
                "",
                source.summary,
                "",
            ]
        )
    summaries_path.write_text("\n".join(summary_lines), encoding="utf-8")
    return {"receipt": receipt_path, "summaries": summaries_path}
