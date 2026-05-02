from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any, Dict, List

from .e10_target_candidate_registry import E10ContactChannelStatus, E10TargetCandidate, E10TargetType


@dataclass(frozen=True)
class E10RevenuePathScore:
    candidate_id: str
    segment: str
    candidate_score: int
    shortest_path_rank: int
    pain_evidence_strength: int
    budget_evidence_strength: int
    urgency_signal: int
    offer_fit: int
    reachability: int
    contact_risk: int
    owner_burden: int
    expected_signal_speed: int
    differentiation_fit: int
    trust_gap: int
    m3_value_relevance: int
    disconfirming_risk: int
    implementation_burden: int
    buyer_process_clarity: int
    reason: str
    what_would_invalidate: str
    recommended_validation_mode: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _presence_score(values: List[str], *, absent: int = 1, present: int = 4) -> int:
    return present if values else absent


def _reachability(candidate: E10TargetCandidate) -> int:
    return {
        E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL: 5,
        E10ContactChannelStatus.OWNER_KNOWN_CONTACT_NEEDED: 3,
        E10ContactChannelStatus.COMMUNITY_PUBLIC_POST_CANDIDATE: 3,
        E10ContactChannelStatus.PUBLIC_ROLE_ONLY_NO_CONTACT: 2,
        E10ContactChannelStatus.NOT_CONTACTABLE_SAFELY: 1,
    }.get(candidate.contact_channel_status, 1)


def _contact_risk(candidate: E10TargetCandidate) -> int:
    return {
        E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL: 2,
        E10ContactChannelStatus.OWNER_KNOWN_CONTACT_NEEDED: 3,
        E10ContactChannelStatus.COMMUNITY_PUBLIC_POST_CANDIDATE: 4,
        E10ContactChannelStatus.PUBLIC_ROLE_ONLY_NO_CONTACT: 4,
        E10ContactChannelStatus.NOT_CONTACTABLE_SAFELY: 5,
    }.get(candidate.contact_channel_status, 5)


def _owner_burden(candidate: E10TargetCandidate) -> int:
    if candidate.contact_channel_status == E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL:
        return 2
    if candidate.contact_channel_status == E10ContactChannelStatus.OWNER_KNOWN_CONTACT_NEEDED:
        return 4
    if candidate.contact_channel_status == E10ContactChannelStatus.COMMUNITY_PUBLIC_POST_CANDIDATE:
        return 4
    return 5


def _recommended_mode(candidate: E10TargetCandidate) -> str:
    if candidate.contact_channel_status == E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL:
        return "owner_operated_3_person_qualitative_validation"
    if candidate.contact_channel_status == E10ContactChannelStatus.COMMUNITY_PUBLIC_POST_CANDIDATE:
        return "public_post_or_landing_pending_Tier3_approval"
    if candidate.contact_channel_status == E10ContactChannelStatus.OWNER_KNOWN_CONTACT_NEEDED:
        return "owner_known_contact_validation_if_owner_can_map_contact"
    return "internal_benchmark_proxy"


def score_e10_candidate(candidate: E10TargetCandidate, rank: int = 0) -> E10RevenuePathScore:
    pain = _presence_score(candidate.pain_signals, absent=2)
    budget = _presence_score(candidate.budget_signals, absent=2)
    urgency = 5 if candidate.urgency_signals else 3 if candidate.implementation_burden_signals else 2
    implementation_burden = _presence_score(candidate.implementation_burden_signals, absent=2)
    governance = _presence_score(candidate.governance_safety_signals, absent=2)
    fit_bonus = 1 if candidate.target_type == E10TargetType.AGENCY_PARTNER else 0
    offer_fit = min(5, max(governance, implementation_burden) + fit_bonus)
    reachability = _reachability(candidate)
    contact_risk = _contact_risk(candidate)
    owner_burden = _owner_burden(candidate)
    expected_signal_speed = 5 if candidate.contact_channel_status == E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL else 3 if reachability >= 3 else 2
    differentiation_fit = min(5, governance + (1 if candidate.implementation_burden_signals else 0))
    trust_gap = 2 if candidate.governance_safety_signals else 3
    m3_value_relevance = 5 if candidate.segment in {"AI consultants/agencies needing governance layer", "teams using agent frameworks or AI workflow tooling"} else 4
    disconfirming_risk = 2 if candidate.budget_signals or candidate.pain_signals else 4
    buyer_process_clarity = 4 if candidate.budget_signals or candidate.contact_channel_status == E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL else 2
    total = (
        pain
        + budget
        + urgency
        + offer_fit
        + reachability
        + (6 - contact_risk)
        + (6 - owner_burden)
        + expected_signal_speed
        + differentiation_fit
        + (6 - trust_gap)
        + m3_value_relevance
        + (6 - disconfirming_risk)
        + implementation_burden
        + buyer_process_clarity
    )
    reason = (
        "Strongest if public evidence shows implementation burden or governance pain plus a low-friction owner-operated contact path. "
        f"Segment={candidate.segment}; contact_status={candidate.contact_channel_status}."
    )
    return E10RevenuePathScore(
        candidate_id=candidate.candidate_id,
        segment=candidate.segment,
        candidate_score=int(total),
        shortest_path_rank=rank,
        pain_evidence_strength=pain,
        budget_evidence_strength=budget,
        urgency_signal=urgency,
        offer_fit=offer_fit,
        reachability=reachability,
        contact_risk=contact_risk,
        owner_burden=owner_burden,
        expected_signal_speed=expected_signal_speed,
        differentiation_fit=differentiation_fit,
        trust_gap=trust_gap,
        m3_value_relevance=m3_value_relevance,
        disconfirming_risk=disconfirming_risk,
        implementation_burden=implementation_burden,
        buyer_process_clarity=buyer_process_clarity,
        reason=reason,
        what_would_invalidate="If the target says existing tools already solve operating-room governance, does not understand the 48h blueprint, or rejects the price range as consulting noise.",
        recommended_validation_mode=_recommended_mode(candidate),
    )


def rank_e10_shortest_revenue_paths(candidates: List[E10TargetCandidate]) -> List[E10RevenuePathScore]:
    scored = [score_e10_candidate(candidate) for candidate in candidates]
    scored.sort(key=lambda row: (row.candidate_score, row.reachability, -row.contact_risk), reverse=True)
    return [
        E10RevenuePathScore(
            **{**score.to_dict(), "shortest_path_rank": index + 1}
        )
        for index, score in enumerate(scored)
    ]


def score_e10_segments(scores: List[E10RevenuePathScore]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[E10RevenuePathScore]] = {}
    for score in scores:
        grouped.setdefault(score.segment, []).append(score)
    rows: List[Dict[str, Any]] = []
    for segment, values in grouped.items():
        top = max(values, key=lambda row: row.candidate_score)
        segment_score = round(mean(row.candidate_score for row in values) + min(len(values), 6), 2)
        rows.append(
            {
                "segment": segment,
                "candidate_count": len(values),
                "segment_score": segment_score,
                "top_candidate_id": top.candidate_id,
                "recommended_validation_mode": top.recommended_validation_mode,
                "reason": (
                    "Ranks by shortest path to paid signal: public pain/budget/urgency evidence, reachability, owner burden, and trust-gap fit."
                ),
            }
        )
    rows.sort(key=lambda row: (row["segment_score"], row["candidate_count"]), reverse=True)
    return rows


def render_e10_shortest_revenue_path_ranking(scores: List[E10RevenuePathScore]) -> str:
    lines = [
        "# E10 Shortest Revenue Path Ranking",
        "",
        "Ranking prioritizes shortest path to a real paid signal, not general market attractiveness.",
        "",
    ]
    for score in scores:
        lines.extend(
            [
                f"## Rank {score.shortest_path_rank}: {score.candidate_id}",
                f"- segment: {score.segment}",
                f"- candidate_score: {score.candidate_score}",
                f"- recommended_validation_mode: {score.recommended_validation_mode}",
                f"- pain_evidence_strength: {score.pain_evidence_strength}",
                f"- budget_evidence_strength: {score.budget_evidence_strength}",
                f"- urgency_signal: {score.urgency_signal}",
                f"- offer_fit: {score.offer_fit}",
                f"- reachability: {score.reachability}",
                f"- contact_risk: {score.contact_risk}",
                f"- owner_burden: {score.owner_burden}",
                f"- expected_signal_speed: {score.expected_signal_speed}",
                f"- differentiation_fit: {score.differentiation_fit}",
                f"- trust_gap: {score.trust_gap}",
                f"- M3_value_relevance: {score.m3_value_relevance}",
                f"- disconfirming_risk: {score.disconfirming_risk}",
                f"- implementation_burden: {score.implementation_burden}",
                f"- buyer_process_clarity: {score.buyer_process_clarity}",
                f"- reason: {score.reason}",
                f"- what_would_invalidate: {score.what_would_invalidate}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def render_e10_segment_opportunity_matrix(segment_scores: List[Dict[str, Any]]) -> str:
    lines = [
        "# E10 Segment Opportunity Matrix",
        "",
        "| rank | segment | candidate_count | segment_score | top_candidate_id | recommended_validation_mode |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for index, row in enumerate(segment_scores, start=1):
        lines.append(
            f"| {index} | {row['segment']} | {row['candidate_count']} | {row['segment_score']} | {row['top_candidate_id']} | {row['recommended_validation_mode']} |"
        )
    lines.extend(["", "## Interpretation"])
    if segment_scores:
        top = segment_scores[0]
        lines.append(
            f"- top_recommended_segment: {top['segment']}. It has the strongest blend of public implementation pain, governance relevance, reachable validation path, and low owner burden."
        )
    lines.append("- paid signal is not claimed until E11 feedback or buyer response exists.")
    return "\n".join(lines)
