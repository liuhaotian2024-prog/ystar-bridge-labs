from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
from typing import Any, Dict, List

from .e8_ai_transparency_policy import inject_or_suggest_disclosure, validate_ai_disclosure, validate_external_message_transparency
from .e8_risk_controlled_action_model import RiskTier


@dataclass(frozen=True)
class FrozenDraft:
    draft_id: str
    source_path: str
    content_hash: str
    risk_tier: str
    intended_channel: str
    ai_disclosure_present: bool
    opt_out_present: bool
    not_sent_marker_present: bool
    not_published_marker_present: bool
    approved_for_external_use: bool
    exact_content_excerpt: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def compute_draft_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _freeze(path: Path, draft_id: str, risk_tier: str, channel: str, approved: bool = False) -> FrozenDraft:
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    return FrozenDraft(
        draft_id=draft_id,
        source_path=str(path),
        content_hash=compute_draft_hash(text),
        risk_tier=risk_tier,
        intended_channel=channel,
        ai_disclosure_present=not validate_ai_disclosure(text),
        opt_out_present=any(token in lower for token in ["ignore", "opt out", "no automated follow-up", "stop"]),
        not_sent_marker_present="not sent" in lower,
        not_published_marker_present="not published" in lower,
        approved_for_external_use=approved,
        exact_content_excerpt=text[:800],
    )


def ensure_ai_disclosed_outreach_draft(repo_root: Path) -> Path:
    reports = repo_root / "reports" / "integration"
    source = reports / "e7_outreach_draft.md"
    target = reports / "e8_ai_disclosed_outreach_draft.md"
    source_text = source.read_text(encoding="utf-8")
    improved = "\n\n".join(
        [
            "DRAFT ONLY.",
            "NOT SENT.",
            "AI-DISCLOSED.",
            "OWNER/AUTONOMY-BUDGET APPROVAL REQUIRED.",
            "NO CUSTOMER CONTACT EXECUTED.",
            inject_or_suggest_disclosure(source_text),
        ]
    )
    target.write_text(improved.rstrip() + "\n", encoding="utf-8")
    return target


def freeze_validation_drafts(repo_root: Path) -> List[Dict[str, Any]]:
    reports = repo_root / "reports" / "integration"
    ai_outreach = ensure_ai_disclosed_outreach_draft(repo_root)
    drafts = [
        _freeze(ai_outreach, "e8_ai_disclosed_outreach_draft", RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION, "owner_selected_email"),
        _freeze(reports / "e7_landing_page_draft.md", "e7_landing_page_draft", RiskTier.TIER_3_PUBLIC_BROADCAST_OR_LANDING, "public_web"),
        _freeze(reports / "e7_demo_call_script.md", "e7_demo_call_script", RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION, "owner_selected_call"),
        _freeze(reports / "e7_validation_survey_or_question_set.md", "e7_validation_question_set", RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION, "owner_selected_feedback"),
    ]
    return [draft.to_dict() for draft in drafts]


def verify_draft_hash(draft: Dict[str, Any], provided_hash: str) -> bool:
    return bool(provided_hash and provided_hash == draft.get("content_hash"))


def validate_frozen_draft_transparency(draft: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not draft.get("ai_disclosure_present"):
        errors.append("missing_ai_disclosure")
    if not draft.get("opt_out_present"):
        errors.append("missing_opt_out")
    if not draft.get("not_sent_marker_present"):
        errors.append("missing_not_sent_marker")
    if draft.get("risk_tier") == RiskTier.TIER_3_PUBLIC_BROADCAST_OR_LANDING and not draft.get("not_published_marker_present"):
        errors.append("missing_not_published_marker")
    if draft.get("approved_for_external_use"):
        errors.append("draft_should_not_be_approved_without_manifest")
    return errors


def render_e8_frozen_validation_drafts(drafts: List[Dict[str, Any]]) -> str:
    lines = ["# E8 Frozen Validation Drafts", ""]
    for draft in drafts:
        lines.extend(
            [
                f"## {draft['draft_id']}",
                f"- source_path: {draft['source_path']}",
                f"- content_hash: {draft['content_hash']}",
                f"- risk_tier: {draft['risk_tier']}",
                f"- intended_channel: {draft['intended_channel']}",
                f"- ai_disclosure_present: {draft['ai_disclosure_present']}",
                f"- opt_out_present: {draft['opt_out_present']}",
                f"- not_sent_marker_present: {draft['not_sent_marker_present']}",
                f"- not_published_marker_present: {draft['not_published_marker_present']}",
                f"- approved_for_external_use: {draft['approved_for_external_use']}",
                "### Exact Content Excerpt",
                draft["exact_content_excerpt"],
                "",
            ]
        )
    return "\n".join(lines).rstrip()
