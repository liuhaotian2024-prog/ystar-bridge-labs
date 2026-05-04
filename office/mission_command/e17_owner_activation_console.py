from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


E17_DECISION_OPTIONS = ["approve_manual_send", "revise_message", "reject_target", "defer", "import_feedback_if_already_sent_manually"]
E17_OFFER = "48h AI Agent Implementation Readiness Review"


@dataclass(frozen=True)
class E17FinalMessagePackage:
    package_id: str
    action_id: str
    target_name: str
    offer: str
    email_subject_options: List[str]
    email_message: str
    linkedin_message: str
    softer_fallback_message: str
    one_follow_up_draft: str
    follow_up_status: str
    truthfulness_constraints: List[str]
    no_send_status: str = "not_sent_by_agent"
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class E17OwnerActivationConsole:
    artifact_id: str
    action_id: str
    target_id: str
    target_name: str
    offer: str
    business_hypothesis: str
    buyer_pain_hypothesis: str
    why_this_target: str
    target_evidence_basis: List[str]
    risk_tier: str
    capability_domain: str
    no_send_status: str
    recommended_owner_action: str
    decision_options: List[str]
    owner_burden_reduction: str
    final_message_package_id: str
    evidence_to_capture_after_manual_send: List[str]
    blocked_actions: List[str]
    e16c1_real_send_blocked: bool
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def build_final_message_package(selected_action: Dict[str, Any]) -> E17FinalMessagePackage:
    target_name = str(selected_action.get("target_name") or selected_action.get("target") or "selected target")
    action_id = str(selected_action.get("action_id", "unknown_action"))
    subject_options = [
        "Quick question on AI-agent implementation readiness",
        "48h readiness review for AI-agent workflows?",
        "Small validation question for AI implementation teams",
    ]
    email_message = (
        f"Hi {target_name} team,\n\n"
        "I am Aiden, an AI-assisted operating agent working with Haotian at Y*Bridge Labs. "
        "We are validating a small 48h AI Agent Implementation Readiness Review for teams or agencies helping clients move AI-agent workflows from experiment to safer operation.\n\n"
        "The review is diagnostic-only: a readiness scorecard, top implementation blockers, a governance/evaluation checklist, and one safe next step. "
        "It does not require production access, credentials, or any deployment change.\n\n"
        "Would this be useful enough to consider a paid diagnostic or a short pilot-prep conversation? "
        "If it is not relevant, no worries; a quick no or a pointer to the right person is completely fine."
    )
    linkedin_message = (
        f"Hi {target_name} team — I’m Aiden, an AI-assisted operating agent working with Haotian at Y*Bridge Labs. "
        "We’re validating a 48h AI Agent Implementation Readiness Review: diagnostic-only, no production access, focused on readiness blockers, governance/eval gaps, and one safe next step. "
        "Would that be useful enough to consider a paid diagnostic or short pilot-prep conversation? No pressure if not relevant."
    )
    softer_fallback = (
        f"Hi {target_name} team, I’m helping Haotian at Y*Bridge Labs pressure-test a 48h AI Agent Implementation Readiness Review. "
        "It is a diagnostic offer, not a deployment pitch: readiness scorecard, blockers, governance/eval checklist, and one safe next step. "
        "Would a review like that be worth exploring, or is this not a current priority?"
    )
    follow_up = (
        "Hi again — just closing the loop on the 48h AI Agent Implementation Readiness Review question. "
        "If this is not relevant, I will not follow up further. If it is relevant, the useful next step would be a short paid-diagnostic fit check."
    )
    constraints = [
        "Do not imply a prior relationship.",
        "Do not claim Y*Bridge Labs has already proven this offer with paying customers unless evidence is imported later.",
        "Do not promise implementation, production access, or guaranteed ROI.",
        "Keep AI transparency explicit.",
        "Keep opt-out / no-pressure language present.",
        "Do not send any follow-up unless positive/clarifying feedback permits it.",
    ]
    return E17FinalMessagePackage(
        package_id=_stable_id("e17_message_package", action_id, target_name),
        action_id=action_id,
        target_name=target_name,
        offer=E17_OFFER,
        email_subject_options=subject_options,
        email_message=email_message,
        linkedin_message=linkedin_message,
        softer_fallback_message=softer_fallback,
        one_follow_up_draft=follow_up,
        follow_up_status="blocked_until_positive_or_clarifying_feedback_and_owner_review",
        truthfulness_constraints=constraints,
    )


def build_owner_activation_console(selected_action: Dict[str, Any], message_package: E17FinalMessagePackage) -> E17OwnerActivationConsole:
    action_id = str(selected_action.get("action_id", "unknown_action"))
    return E17OwnerActivationConsole(
        artifact_id="e17_owner_activation_console",
        action_id=action_id,
        target_id=str(selected_action.get("target_id", "unknown_target")),
        target_name=str(selected_action.get("target_name", "selected target")),
        offer=E17_OFFER,
        business_hypothesis="A low-friction 48h readiness diagnostic can convert AI-agent implementation uncertainty into a paid pilot-prep conversation.",
        buyer_pain_hypothesis=str(selected_action.get("buyer_pain_hypothesis", "AI-agent implementation readiness, workflow bottlenecks, governance risk, and safe next operational step.")),
        why_this_target=str(selected_action.get("selection_reason", "Selected as the lowest-risk complete-identity E16C0 action.")),
        target_evidence_basis=list(selected_action.get("target_evidence_basis", [])),
        risk_tier=str(selected_action.get("risk_tier", "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION")),
        capability_domain=str(selected_action.get("capability_domain", "external_validation_message")),
        no_send_status="agent_no_send_owner_manual_send_only",
        recommended_owner_action="Review one page, choose approve/revise/reject/defer, and if approving manual send, copy one finalized message only.",
        decision_options=E17_DECISION_OPTIONS,
        owner_burden_reduction="Owner sees target, thesis, risk boundary, final message, and feedback fields in one surface instead of hunting through governance artifacts.",
        final_message_package_id=message_package.package_id,
        evidence_to_capture_after_manual_send=[
            "whether owner actually sent the message outside the repo",
            "channel used by owner",
            "sent_at timestamp if owner chooses to record it",
            "raw response summary if any",
            "feedback type",
            "price/meeting/referral/objection/do-not-contact flags",
            "owner notes and any provenance limitations",
        ],
        blocked_actions=[
            "agent email/message send",
            "real provider API call",
            "login or account creation",
            "form submission or publication",
            "payment, contract, or legal commitment",
            "real send receipt generation",
            "core brain/CIEU/memory canonical writeback",
        ],
        e16c1_real_send_blocked=True,
    )


def render_owner_activation_console(console: E17OwnerActivationConsole, message_package: E17FinalMessagePackage) -> str:
    lines = [
        "# E17 Owner Activation Console",
        "",
        "This is the single owner-facing surface for the first commercial signal action. It does not send anything.",
        "",
        f"- target: {console.target_name}",
        f"- offer: {console.offer}",
        f"- action_id: {console.action_id}",
        f"- risk_tier: {console.risk_tier}",
        f"- no_send_status: {console.no_send_status}",
        f"- recommended_owner_action: {console.recommended_owner_action}",
        "",
        "## Why This Target",
        console.why_this_target,
        "",
        "## Business Hypothesis",
        console.business_hypothesis,
        "",
        "## Buyer Pain Hypothesis",
        console.buyer_pain_hypothesis,
        "",
        "## Owner Decision Options",
    ]
    lines.extend(f"- {item}" for item in console.decision_options)
    lines.extend([
        "",
        "## Final Email Message",
        "```text",
        f"Subject: {message_package.email_subject_options[0]}\n\n{message_package.email_message}",
        "```",
        "",
        "## LinkedIn / Manual Message",
        "```text",
        message_package.linkedin_message,
        "```",
        "",
        "## Softer Fallback",
        "```text",
        message_package.softer_fallback_message,
        "```",
        "",
        "## Follow-Up Draft",
        f"Status: {message_package.follow_up_status}",
        "```text",
        message_package.one_follow_up_draft,
        "```",
        "",
        "## Evidence To Capture After Manual Send",
    ])
    lines.extend(f"- {item}" for item in console.evidence_to_capture_after_manual_send)
    lines.extend(["", "## Blocked Actions"])
    lines.extend(f"- {item}" for item in console.blocked_actions)
    return "\n".join(lines).rstrip() + "\n"


def render_final_message_package(package: E17FinalMessagePackage) -> str:
    lines = [
        "# E17 Final Message Package",
        "",
        f"- target: {package.target_name}",
        f"- offer: {package.offer}",
        f"- no_send_status: {package.no_send_status}",
        f"- external_action_executed: {str(package.external_action_executed).lower()}",
        "",
        "## Subject Options",
    ]
    lines.extend(f"- {item}" for item in package.email_subject_options)
    lines.extend([
        "",
        "## Email Version",
        "```text",
        package.email_message,
        "```",
        "",
        "## LinkedIn / Manual Message Version",
        "```text",
        package.linkedin_message,
        "```",
        "",
        "## Softer Fallback Message",
        "```text",
        package.softer_fallback_message,
        "```",
        "",
        "## One Follow-Up Draft",
        f"Status: {package.follow_up_status}",
        "```text",
        package.one_follow_up_draft,
        "```",
        "",
        "## Truthfulness Constraints",
    ])
    lines.extend(f"- {item}" for item in package.truthfulness_constraints)
    return "\n".join(lines).rstrip() + "\n"
