from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List


E14_DRAFT_ID = "e14_manual_owner_operated_ai_agent_readiness_review_v1"


@dataclass(frozen=True)
class E14ManualValidationDraft:
    draft_id: str
    draft_text: str
    draft_hash: str
    ai_transparency_present: bool
    opt_out_ignore_present: bool
    no_existing_validation_claim: bool
    no_fake_urgency: bool
    no_tracking_or_attachment: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def default_e14_manual_draft() -> str:
    return """Subject: Quick question on AI-agent implementation readiness

Hi,

I am Aiden, an AI-assisted CEO/runtime agent for Y*Bridge Labs, working with Haotian. I am not pretending to be a human teammate, and this is a small owner-operated validation note before we ask anyone to buy anything.

We are testing a 48h AI Agent Implementation Readiness Review for teams or agencies trying to deploy AI agents/coding agents safely. The review maps implementation readiness, workflow bottlenecks, governance risks, and the safest next operational step.

Would this kind of 48h readiness review be useful enough to justify a paid diagnostic or pilot-prep conversation?

No pressure, no automated follow-up, and it is completely fine to ignore this. If this is not relevant, please disregard.
"""


def hash_draft(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]


def build_e14_manual_validation_draft(text: str | None = None) -> E14ManualValidationDraft:
    draft = text or default_e14_manual_draft()
    lowered = draft.lower()
    return E14ManualValidationDraft(
        draft_id=E14_DRAFT_ID,
        draft_text=draft,
        draft_hash=hash_draft(draft),
        ai_transparency_present="ai-assisted" in lowered and "aiden" in lowered,
        opt_out_ignore_present="ignore" in lowered and "no automated follow-up" in lowered,
        no_existing_validation_claim="validated" not in lowered and "customers already" not in lowered,
        no_fake_urgency="urgent" not in lowered and "limited time" not in lowered,
        no_tracking_or_attachment="http://" not in lowered and "https://" not in lowered and "attachment" not in lowered,
    )


def validate_e14_manual_draft(draft: E14ManualValidationDraft) -> List[str]:
    errors: List[str] = []
    if not draft.ai_transparency_present:
        errors.append("ai_transparency_required")
    if not draft.opt_out_ignore_present:
        errors.append("opt_out_or_ignore_language_required")
    if not draft.no_existing_validation_claim:
        errors.append("must_not_claim_existing_customer_validation")
    if not draft.no_fake_urgency:
        errors.append("fake_urgency_not_allowed")
    if not draft.no_tracking_or_attachment:
        errors.append("links_or_attachments_require_separate_approval")
    return errors


def write_e14_manual_draft(repo_root: Path) -> Path:
    draft = build_e14_manual_validation_draft()
    path = repo_root / "operations" / "external_validation" / "e14_manual_send_draft.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# E14 Manual-Send Validation Draft",
                "",
                f"- draft_id: {draft.draft_id}",
                f"- draft_hash: {draft.draft_hash}",
                "- owner_operated_only: true",
                "- aiden_sent: false",
                "",
                "```text",
                draft.draft_text.rstrip(),
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path
