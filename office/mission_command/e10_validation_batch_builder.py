from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from .e10_shortest_revenue_path_scorer import E10RevenuePathScore
from .e10_target_candidate_registry import E10ContactChannelStatus, E10TargetCandidate


@dataclass(frozen=True)
class E10ValidationBatch:
    batch_id: str
    batch_name: str
    target_segment: str
    target_candidate_ids: List[str]
    validation_mode: str
    recommended_channel: str
    draft_id: str
    risk_tier: str
    expected_signal: str
    stop_conditions: List[str]
    success_criteria: List[str]
    disconfirming_criteria: List[str]
    owner_approval_required: str
    why_this_is_shortest_path: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _candidate_ids_for_segment(candidates: List[E10TargetCandidate], segment: str, limit: int = 3) -> List[str]:
    selected = [
        candidate.candidate_id
        for candidate in candidates
        if candidate.segment == segment and candidate.contact_channel_status == E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL
    ]
    if len(selected) < limit:
        selected.extend(candidate.candidate_id for candidate in candidates if candidate.segment == segment and candidate.candidate_id not in selected)
    return selected[:limit]


def _ranked_candidate_ids_for_segment(
    candidates: List[E10TargetCandidate],
    scores: List[E10RevenuePathScore],
    segment: str,
    limit: int = 3,
) -> List[str]:
    candidate_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    selected: List[str] = []
    for score in scores:
        candidate = candidate_by_id.get(score.candidate_id)
        if not candidate or candidate.segment != segment:
            continue
        if candidate.contact_channel_status == E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL:
            selected.append(candidate.candidate_id)
    if len(selected) < limit:
        selected.extend(candidate_id for candidate_id in _candidate_ids_for_segment(candidates, segment, limit) if candidate_id not in selected)
    return selected[:limit]


def build_e10_validation_batches(candidates: List[E10TargetCandidate], scores: List[E10RevenuePathScore]) -> List[E10ValidationBatch]:
    top_segment = scores[0].segment if scores else "AI consultants/agencies needing governance layer"
    recommended_ids = _ranked_candidate_ids_for_segment(candidates, scores, top_segment, limit=3)
    hiring_ids = _candidate_ids_for_segment(
        candidates,
        "teams hiring for AI ops / LLMOps / AI evaluation / automation",
        limit=3,
    )
    tooling_ids = _candidate_ids_for_segment(candidates, "teams using agent frameworks or AI workflow tooling", limit=3)
    if len(tooling_ids) < 3:
        tooling_ids.extend(_candidate_ids_for_segment(candidates, "open-source teams/projects needing governance/support", limit=3 - len(tooling_ids)))
    batches = [
        E10ValidationBatch(
            batch_id="batch_ai_ops_agency_governance_layer",
            batch_name="AI Ops agency partner governance-layer feedback",
            target_segment=top_segment,
            target_candidate_ids=recommended_ids,
            validation_mode="owner_operated_3_person_qualitative_validation",
            recommended_channel="owner_selected_email_or_public_general_channel_after_owner_review",
            draft_id="e8_ai_disclosed_outreach_draft",
            risk_tier="Tier 2 candidate; owner approval required before contact",
            expected_signal="Fast qualitative signal on whether agencies/consultants would use a 48h operating-room blueprint as a governance layer or pre-implementation artifact.",
            stop_conditions=[
                "any recipient opts out or asks not to be contacted",
                "owner approval count is exhausted",
                "message or channel differs from approved manifest",
                "target asks for commercial terms beyond validation feedback",
            ],
            success_criteria=[
                "buyer asks for example deliverable",
                "buyer says the blueprint would help pre-implementation scoping",
                "buyer identifies a real workflow that could be analyzed",
                "buyer accepts or does not reject the $750-$3,000 hypothesis range",
            ],
            disconfirming_criteria=[
                "agency says existing implementation discovery already solves this",
                "agency sees it as generic consulting",
                "agency cannot identify a decision owner or repeatable use case",
            ],
            owner_approval_required="Approve exact targets, channel, draft hash, one-message count, stop conditions, and whether Aiden may execute or owner will operate handoff.",
            why_this_is_shortest_path=(
                "This is the shortest path because agency/consultant targets publicly show implementation burden, governance need, and general contactability; one owner-operated batch can generate partner-channel feedback quickly."
            ),
        ),
        E10ValidationBatch(
            batch_id="batch_llmops_hiring_signal",
            batch_name="LLMOps hiring-signal founder/operator feedback",
            target_segment="teams hiring for AI ops / LLMOps / AI evaluation / automation",
            target_candidate_ids=hiring_ids,
            validation_mode="owner_known_contact_validation_if_owner_can_map_contact",
            recommended_channel="owner_known_contact_needed",
            draft_id="e8_ai_disclosed_outreach_draft",
            risk_tier="Tier 2 candidate; owner must map safe contact before outreach",
            expected_signal="Tests whether teams with public LLMOps hiring urgency would value a 48h blueprint before staffing or tool expansion.",
            stop_conditions=[
                "owner cannot map a known safe contact",
                "target requires scraped personal contact",
                "recipient opts out",
                "response indicates hiring need is unrelated to operating-room governance",
            ],
            success_criteria=[
                "target asks about implementation scope",
                "target offers a workflow sample",
                "target asks how the blueprint complements hiring/tooling",
            ],
            disconfirming_criteria=[
                "target says the job opening is not a buying trigger",
                "target needs full-time staffing only",
                "target has no urgency outside internal hiring process",
            ],
            owner_approval_required="Owner must provide known contact mapping or select no-contact internal benchmark mode.",
            why_this_is_shortest_path="Hiring pages show urgency and budget proxy, but contactability is weaker than agency pages, making this the second path.",
        ),
        E10ValidationBatch(
            batch_id="batch_tooling_internal_benchmark_proxy",
            batch_name="AI tooling/open-source internal benchmark",
            target_segment="teams using agent frameworks or AI workflow tooling",
            target_candidate_ids=tooling_ids[:3],
            validation_mode="internal_benchmark_proxy",
            recommended_channel="internal",
            draft_id="e8_ai_disclosed_outreach_draft",
            risk_tier="Tier 0 internal only unless owner later approves external mode",
            expected_signal="Tests the blueprint against public tooling evidence without contacting anyone, producing a lower-risk but lower-signal validation artifact.",
            stop_conditions=[
                "benchmark cannot map evidence into a concrete workflow",
                "benchmark becomes generic tool comparison",
                "owner burden exceeds one review cycle",
            ],
            success_criteria=[
                "benchmark yields a concrete before/after operating-room map",
                "benchmark identifies buyer questions for E11",
                "benchmark sharpens the draft without external contact",
            ],
            disconfirming_criteria=[
                "public tooling docs already cover the entire operating-room need",
                "Y*Bridge wedge cannot be differentiated from vendor onboarding",
            ],
            owner_approval_required="No external approval needed for internal benchmark; external publication/contact still requires separate manifest.",
            why_this_is_shortest_path="Lowest risk and owner burden, but weaker signal than direct agency/founder feedback.",
        ),
    ]
    return batches


def render_e10_validation_batch_proposals(batches: List[E10ValidationBatch]) -> str:
    lines = [
        "# E10 Validation Batch Proposals",
        "",
        f"- batch_count: {len(batches)}",
        "- batch_1_is_recommended_shortest_path: true",
        "- no_contact_executed: true",
        "- no_publication_executed: true",
        "",
    ]
    for batch in batches:
        lines.extend(
            [
                f"## {batch.batch_id}: {batch.batch_name}",
                f"- target_segment: {batch.target_segment}",
                f"- target_candidate_ids: {', '.join(batch.target_candidate_ids)}",
                f"- validation_mode: {batch.validation_mode}",
                f"- recommended_channel: {batch.recommended_channel}",
                f"- draft_id: {batch.draft_id}",
                f"- risk_tier: {batch.risk_tier}",
                f"- expected_signal: {batch.expected_signal}",
                f"- owner_approval_required: {batch.owner_approval_required}",
                f"- why_this_is_shortest_path: {batch.why_this_is_shortest_path}",
                "",
                "### Stop Conditions",
            ]
        )
        lines.extend(f"- {item}" for item in batch.stop_conditions)
        lines.extend(["", "### Success Criteria"])
        lines.extend(f"- {item}" for item in batch.success_criteria)
        lines.extend(["", "### Disconfirming Criteria"])
        lines.extend(f"- {item}" for item in batch.disconfirming_criteria)
        lines.append("")
    return "\n".join(lines).rstrip()
