from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class StructuredAction:
    action_id: str
    raw_title: str
    source: str
    artifact_only: bool
    preparation_only: bool
    research_read_only: bool
    approval_packet_only: bool
    external_side_effect: bool
    customer_contact: bool
    email_or_message: bool
    publication: bool
    payment: bool
    account_creation: bool
    form_submission: bool
    obligation_dry_run: bool
    residual_candidate: bool
    core_writeback: bool
    repo_modification: bool
    requires_owner_approval: bool
    review_gated: bool
    blocked: bool
    semantic_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _is_preparation_text(text: str) -> bool:
    return _has_any(
        text,
        (
            "prepare ",
            "draft ",
            "define ",
            "create approval packet",
            "approval packet",
            "manual-send validation draft",
            "manual-send packet",
            "do not execute",
            "no-contact",
            "approval gate",
            "approval-gated",
            "owner review",
            "for owner review",
            "review-only",
            "research plan",
            "questions and evidence fields",
        ),
    )


def _is_live_read_only_research(text: str, source: str) -> bool:
    if source == "experiment_tier1_research":
        return True
    return (
        "live read-only research" in text
        or "run read-only research" in text
        or "execute read-only research" in text
        or ("collect public" in text and "evidence" in text and "no contact" in text)
    )


def classify_structured_action(action_dict: Dict[str, Any]) -> StructuredAction:
    action_id = str(action_dict.get("action_id") or "")
    raw_title = str(action_dict.get("action_title") or action_dict.get("raw_title") or action_dict.get("title") or "")
    source = str(action_dict.get("action_source") or action_dict.get("source") or "")
    text = raw_title.lower()

    obligation_dry_run = source == "obligation_draft" or "obligation dry-run" in text
    residual_candidate = source == "residual_candidate" or "residual review candidate" in text
    payment = _has_any(text, ("payment", "pay ", "paid link", "payment link", "process payment"))
    core_writeback = _has_any(text, ("core db", "brain", "memory/cieu", "cieu", "writeback", "core write"))
    account_creation = _has_any(text, ("create account", "account creation", "sign up"))
    form_submission = _has_any(text, ("form submission", "submit form", "form submit"))
    publication = _has_any(text, ("publish public", "publication", "public post", "publish content")) and not _has_any(
        text,
        ("without publication", "no publication", "not publish", "do not publish"),
    )
    email_or_message = _has_any(text, ("send email", "email/message", "send message", "message sending"))
    customer_contact = _has_any(text, ("customer contact", "contact a customer", "contact customer"))
    price_quote = "quote price externally" in text or "external price quote" in text
    repo_modification = _has_any(text, ("modify repo", "repo modification", "external repository modification"))
    approval_packet_only = _has_any(text, ("approval packet", "manual-send packet", "manual-send validation draft")) or (
        "owner must approve" in text and "before any send" in text
    )
    preparation_only = _is_preparation_text(text)
    research_read_only = _is_live_read_only_research(text, source) or (
        "read-only research" in text and "plan" in text
    )

    # The word "external" is often part of a safety boundary or artifact description.
    # It becomes a side effect only when paired with an actual contact/send/publish/submit/payment/account action.
    external_side_effect = any((customer_contact, email_or_message, publication, account_creation, form_submission, price_quote))

    artifact_only = bool(
        preparation_only
        or approval_packet_only
        or source in {"autonomous_internal_actions", "team_task", "experiment_external_validation"}
    ) and not any((payment, customer_contact, email_or_message, publication, account_creation, form_submission, core_writeback))

    if obligation_dry_run:
        reason = "Obligation draft is a dry-run owner-review artifact; it is not registered automatically."
    elif residual_candidate:
        reason = "Residual candidate is review-gated learning material, not an external side effect."
    elif payment:
        reason = "Payment or payment-path creation is blocked in this runtime."
    elif core_writeback:
        reason = "Core DB/brain/memory/CIEU writeback remains review-gated."
    elif external_side_effect:
        reason = "Customer contact, email/message, publication, external price quote, account creation, or form submission requires owner approval."
    elif research_read_only and not preparation_only:
        reason = "Live Tier 1 read-only research execution requires explicit budget and owner approval."
    elif approval_packet_only or artifact_only or preparation_only:
        reason = "This is internal artifact/preparation work; mentioning external gates does not execute an external action."
    else:
        reason = "Safe internal mission work."

    blocked = payment
    review_gated = obligation_dry_run or residual_candidate or core_writeback
    requires_owner_approval = bool(external_side_effect or (research_read_only and not preparation_only))

    return StructuredAction(
        action_id=action_id,
        raw_title=raw_title,
        source=source,
        artifact_only=artifact_only,
        preparation_only=preparation_only,
        research_read_only=research_read_only,
        approval_packet_only=approval_packet_only,
        external_side_effect=external_side_effect,
        customer_contact=customer_contact,
        email_or_message=email_or_message,
        publication=publication,
        payment=payment,
        account_creation=account_creation,
        form_submission=form_submission,
        obligation_dry_run=obligation_dry_run,
        residual_candidate=residual_candidate,
        core_writeback=core_writeback,
        repo_modification=repo_modification,
        requires_owner_approval=requires_owner_approval,
        review_gated=review_gated,
        blocked=blocked,
        semantic_reason=reason,
    )


def decision_from_structured_action(structured_action: StructuredAction | Dict[str, Any]) -> str:
    action = structured_action if isinstance(structured_action, StructuredAction) else StructuredAction(**structured_action)
    if action.blocked:
        return "BLOCKED"
    if action.review_gated:
        return "REVIEW_GATED"
    if action.requires_owner_approval:
        return "NEEDS_OWNER_APPROVAL"
    return "ALLOW_INTERNAL"


def action_class_from_structured_action(structured_action: StructuredAction) -> str:
    if structured_action.payment:
        return "payment_blocked"
    if structured_action.core_writeback:
        return "core_writeback_review_gated"
    if structured_action.obligation_dry_run:
        return "obligation_dry_run"
    if structured_action.residual_candidate:
        return "residual_review_candidate"
    if structured_action.requires_owner_approval and structured_action.research_read_only:
        return "tier1_read_only_research"
    if structured_action.external_side_effect:
        return "external_side_effect"
    if structured_action.artifact_only or structured_action.preparation_only or structured_action.approval_packet_only:
        return "internal_artifact_preparation"
    return "internal_autonomous"


def explain_action_semantics(structured_action: StructuredAction | Dict[str, Any]) -> str:
    action = structured_action if isinstance(structured_action, StructuredAction) else StructuredAction(**structured_action)
    return action.semantic_reason
