from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List


DISCLOSURE_OPTIONS = [
    "I’m Aiden, an AI-assisted CEO/runtime agent for Y*Bridge Labs. I’m testing whether this 48h offer is useful before asking anyone to buy it.",
    "This is an AI-assisted validation request from Y*Bridge Labs. No automated follow-up will happen unless you reply or opt in.",
    "I’m helping build and test Y*Bridge Labs’ AI company runtime. This message is part of a small, bounded validation test.",
]


@dataclass(frozen=True)
class AITransparencyPolicy:
    required_disclosure_texts: List[str]
    forbidden_identity_patterns: List[str]
    allowed_sender_modes: List[str]
    opt_out_language_required: bool
    no_impersonation: bool
    no_fake_human_identity: bool
    no_false_customer_validation_claim: bool
    no_false_urgency: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


DEFAULT_POLICY = AITransparencyPolicy(
    required_disclosure_texts=DISCLOSURE_OPTIONS,
    forbidden_identity_patterns=[
        "i am a human",
        "not an ai",
        "human founder",
        "sent personally by the founder",
        "we already validated with customers",
        "customers already proved",
        "urgent limited-time offer",
    ],
    allowed_sender_modes=["aiden_ai_disclosed", "owner_manual_send_with_disclosure", "company_account_ai_disclosed"],
    opt_out_language_required=True,
    no_impersonation=True,
    no_fake_human_identity=True,
    no_false_customer_validation_claim=True,
    no_false_urgency=True,
)


def _lower(text: str) -> str:
    return text.lower()


def validate_ai_disclosure(text: str) -> List[str]:
    lower = _lower(text)
    errors: List[str] = []
    if not any(token in lower for token in ["ai-assisted", "ai assisted", "aiden", "ai company runtime", "ai/runtime"]):
        errors.append("missing_ai_or_ai_assisted_disclosure")
    if any(pattern in lower for pattern in DEFAULT_POLICY.forbidden_identity_patterns):
        errors.append("forbidden_or_deceptive_identity_pattern")
    return errors


def validate_external_message_transparency(text: str) -> List[str]:
    lower = _lower(text)
    errors = validate_ai_disclosure(text)
    if not any(token in lower for token in ["ignore", "opt out", "no reply", "no-response", "no automated follow-up", "stop"]):
        errors.append("missing_opt_out_or_ignore_language")
    if any(token in lower for token in ["you have this problem", "you definitely need", "customer validation already happened"]):
        errors.append("misleading_problem_or_validation_claim")
    if "urgent" in lower and "validation" not in lower:
        errors.append("deceptive_urgency_risk")
    return list(dict.fromkeys(errors))


def inject_or_suggest_disclosure(text: str) -> str:
    if not validate_external_message_transparency(text):
        return text
    return (
        f"{DISCLOSURE_OPTIONS[0]}\n\n"
        f"{text.strip()}\n\n"
        "If this is not useful, please ignore it; no automated follow-up will happen unless you reply or opt in."
    )


def render_e8_ai_transparency_policy() -> str:
    lines = [
        "# E8 AI Transparency And Anti-Deception Policy",
        "",
        "Aiden must not impersonate a human. Any external validation message or public draft must disclose AI or AI-assisted status.",
        "",
        "## Required Disclosure Options",
    ]
    lines.extend(f"- {item}" for item in DEFAULT_POLICY.required_disclosure_texts)
    lines.extend(["", "## Allowed Sender Modes"])
    lines.extend(f"- {item}" for item in DEFAULT_POLICY.allowed_sender_modes)
    lines.extend(["", "## Forbidden Identity / Claim Patterns"])
    lines.extend(f"- {item}" for item in DEFAULT_POLICY.forbidden_identity_patterns)
    lines.extend(
        [
            "",
            "## Validation Rules",
            "- AI / AI-assisted disclosure required.",
            "- No fake human name or hidden automation.",
            "- No false claim that customer validation already happened.",
            "- No claim that recipient has a problem.",
            "- No pressure or deceptive urgency.",
            "- Opt-out, ignore, or no-response language required for outreach.",
        ]
    )
    return "\n".join(lines)
