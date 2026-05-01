from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .evidence_provenance import (
    EvidenceProviderMode,
    EvidenceRunBundle,
    build_evidence_run_bundle,
)
from .public_source_seed_model import (
    PublicSourceSeedPlan,
    validate_public_source_seed,
)
from .safe_public_page_reader import SafePublicPageReader
from .tier1_public_research import (
    Tier1ResearchReceipt,
    Tier1ResearchRequest,
    Tier1SourceEvidence,
    domain_from_identifier,
    safety_boundary,
    utc_now,
    write_receipt_and_summaries,
)


class SourceSeededPublicResearchProvider:
    provider_name = "source_seeded_public_page_read"

    def __init__(self, reader: SafePublicPageReader | Any | None = None) -> None:
        self.reader = reader or SafePublicPageReader()

    def available(self) -> bool:
        return bool(self.reader and self.reader.available())

    def run(
        self,
        repo_root: Path,
        request: Tier1ResearchRequest,
        seed_plan: PublicSourceSeedPlan,
    ) -> EvidenceRunBundle:
        started = utc_now()
        errors: List[str] = []
        sources: List[Tier1SourceEvidence] = []
        pages_read: List[str] = []
        domains: List[str] = []
        if not seed_plan.seeds:
            receipt = Tier1ResearchReceipt(
                mission_id=request.mission_id,
                live_research_executed=False,
                provider_name=self.provider_name,
                started_at=started,
                completed_at=utc_now(),
                queries_used=[],
                pages_read=[],
                domains_touched=[],
                stopped_reason="blocked_missing_public_source_seeds",
                safety_boundary=safety_boundary(),
                external_action_executed=False,
                errors=["missing_public_source_seeds"],
                source_summary_paths=[],
            )
            return build_evidence_run_bundle(
                run_id="e5_source_seeded_blocked_missing_seeds",
                mission_id=request.mission_id,
                provider_name=self.provider_name,
                provider_mode=EvidenceProviderMode.BLOCKED_MISSING_SOURCE_SEEDS,
                receipt=receipt.to_dict(),
                sources=[],
                source_summary_paths=[],
                budget=request.budget.to_dict(),
                blocked_reason="missing owner-approved public source seeds",
                exact_unblock_action=[
                    "Add 10-20 owner-approved public no-login URLs to research/public_source_seeds/e5_public_source_seeds.json.",
                    "Group seeds by opportunity family and include relevant opportunity IDs.",
                ],
            )
        for seed in seed_plan.seeds:
            seed_errors = validate_public_source_seed(seed)
            if seed_errors:
                errors.extend(f"{seed.seed_id}:{error}" for error in seed_errors)
                continue
            if len(pages_read) >= request.budget.max_pages_read:
                errors.append("budget_exceeded:max_pages_read")
                break
            domain = domain_from_identifier(seed.url)
            if domain not in domains and len(domains) >= request.budget.max_domains:
                errors.append("budget_exceeded:max_domains")
                break
            result = self.reader.read(seed.url)
            if result.domain and result.domain not in domains:
                domains.append(result.domain)
            if result.blocked_reason or result.safety_errors or not result.text_excerpt:
                errors.append(f"{seed.seed_id}:{result.blocked_reason or ';'.join(result.safety_errors) or 'empty_page'}")
                continue
            pages_read.append(seed.url)
            text = result.text_excerpt
            lower = text.lower()
            pricing_signal = ""
            if any(token in lower for token in ["pricing", "$", "price", "plan", "subscription"]):
                pricing_signal = "pricing or plan language visible in public page excerpt"
            competitor_signal = seed.source_category if any(token in seed.source_category.lower() for token in ["vendor", "consultant", "product", "service"]) else ""
            substitute_signal = "DIY/internal process alternative likely" if any(token in lower for token in ["template", "guide", "checklist", "docs"]) else ""
            budget_signal = "budget proxy requires human review of source excerpt" if pricing_signal else ""
            sources.append(
                Tier1SourceEvidence(
                    source_id=f"e5_source_{len(sources) + 1:03d}_{seed.seed_id}",
                    url_or_public_identifier=seed.url,
                    domain=result.domain,
                    source_category=seed.source_category,
                    retrieved_at=result.retrieved_at,
                    evidence_type="live_public_read_only",
                    relevant_opportunity_ids=seed.relevant_opportunity_ids,
                    summary=text[:500],
                    buyer_pain_signal=f"Seed sought {', '.join(seed.evidence_sought)}; excerpt: {text[:220]}",
                    pricing_signal=pricing_signal,
                    competitor_signal=competitor_signal,
                    substitute_signal=substitute_signal,
                    budget_signal=budget_signal,
                    confidence="low_to_medium_public_page_excerpt",
                    limitations=[
                        "Deterministic extraction from page excerpt only.",
                        "No customer contact or private source verification.",
                    ],
                )
            )
        receipt = Tier1ResearchReceipt(
            mission_id=request.mission_id,
            live_research_executed=bool(sources),
            provider_name=self.provider_name,
            started_at=started,
            completed_at=utc_now(),
            queries_used=[],
            pages_read=pages_read,
            domains_touched=domains,
            stopped_reason="source_seeded_complete" if sources else "blocked_no_valid_public_source_summaries",
            safety_boundary=safety_boundary(),
            external_action_executed=False,
            errors=errors,
            source_summary_paths=["reports/integration/e5_external_source_summaries.md"] if sources else [],
        )
        paths = write_receipt_and_summaries(
            repo_root,
            receipt,
            sources,
            "e5_tier1_research_budget_receipt.md",
            "e5_external_source_summaries.md",
        ) if sources else {}
        return build_evidence_run_bundle(
            run_id="e5_source_seeded_public_page_read",
            mission_id=request.mission_id,
            provider_name=self.provider_name,
            provider_mode=EvidenceProviderMode.SOURCE_SEED_LIVE_PUBLIC_READ_ONLY if sources else EvidenceProviderMode.BLOCKED_MISSING_SOURCE_SEEDS,
            receipt=receipt.to_dict(),
            sources=[source.to_dict() for source in sources],
            source_summary_paths=[str(paths["summaries"])] if paths else [],
            budget=request.budget.to_dict(),
            blocked_reason="" if sources else "no valid public source summaries",
            exact_unblock_action=[] if sources else ["Provide valid owner-approved public no-login seed URLs."],
        )
