from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Dict, List


TARGET_SEEDS_PATH = Path("operations/external_validation/e8_target_seeds.json")
TARGET_SEEDS_TEMPLATE_PATH = Path("operations/external_validation/e8_target_seeds.template.json")


@dataclass(frozen=True)
class E8ValidationTarget:
    target_id: str
    target_type: str
    name_or_label: str
    channel: str
    contact_handle_or_address: str
    relationship_context: str
    why_relevant: str
    approved_for_contact: bool
    allowed_message_count: int
    opt_out_state: bool
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def target_from_dict(data: Dict[str, Any]) -> E8ValidationTarget:
    return E8ValidationTarget(
        target_id=str(data.get("target_id", "")),
        target_type=str(data.get("target_type", "")),
        name_or_label=str(data.get("name_or_label", "")),
        channel=str(data.get("channel", "")),
        contact_handle_or_address=str(data.get("contact_handle_or_address", "")),
        relationship_context=str(data.get("relationship_context", "")),
        why_relevant=str(data.get("why_relevant", "")),
        approved_for_contact=bool(data.get("approved_for_contact", False)),
        allowed_message_count=int(data.get("allowed_message_count", 0) or 0),
        opt_out_state=bool(data.get("opt_out_state", False)),
        notes=str(data.get("notes", "")),
    )


def load_e8_target_seeds(repo_root: Path) -> List[E8ValidationTarget]:
    path = repo_root / TARGET_SEEDS_PATH
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("targets", payload if isinstance(payload, list) else [])
    return [target_from_dict(item) for item in raw]


def validate_e8_target(target: E8ValidationTarget | Dict[str, Any]) -> List[str]:
    item = target if isinstance(target, E8ValidationTarget) else target_from_dict(target)
    errors: List[str] = []
    if not item.target_id:
        errors.append("missing_target_id")
    if item.target_type not in {"known_contact", "founder_peer", "expert", "internal_benchmark_proxy", "public_audience"}:
        errors.append("invalid_target_type")
    if not item.name_or_label:
        errors.append("missing_name_or_label")
    if not item.channel:
        errors.append("missing_channel")
    if item.target_type in {"known_contact", "founder_peer", "expert"} and not item.contact_handle_or_address:
        errors.append("missing_contact_handle_or_address")
    if "scraped" in item.relationship_context.lower() or "scraped" in item.notes.lower():
        errors.append("scraped_contact_not_allowed")
    if item.target_type != "internal_benchmark_proxy" and not item.approved_for_contact:
        errors.append("target_not_approved_for_contact")
    if item.allowed_message_count <= 0 and item.target_type != "internal_benchmark_proxy":
        errors.append("missing_allowed_message_count")
    if item.opt_out_state:
        errors.append("target_opted_out")
    return list(dict.fromkeys(errors))


def validate_e8_target_seeds(targets: List[E8ValidationTarget | Dict[str, Any]]) -> List[str]:
    if not targets:
        return ["missing_target_seeds"]
    errors: List[str] = []
    for target in targets:
        target_id = target.target_id if isinstance(target, E8ValidationTarget) else str(target.get("target_id", "unknown"))
        errors.extend(f"{target_id}:{error}" for error in validate_e8_target(target))
    return errors


def target_allows_action(target: E8ValidationTarget | Dict[str, Any] | None, action: Dict[str, Any]) -> bool:
    if target is None or validate_e8_target(target):
        return False
    item = target if isinstance(target, E8ValidationTarget) else target_from_dict(target)
    return (
        str(action.get("target_id", "")) == item.target_id
        and str(action.get("channel", "")) == item.channel
        and item.approved_for_contact
        and not item.opt_out_state
        and item.allowed_message_count > 0
    )


def render_e8_target_seed_template() -> str:
    payload = {
        "targets": [
            {
                "target_id": "target_001",
                "target_type": "known_contact",
                "name_or_label": "Owner-provided technical founder or AI-heavy team lead",
                "channel": "owner_selected_email",
                "contact_handle_or_address": "OWNER_TO_FILL",
                "relationship_context": "Owner-provided known contact; not scraped.",
                "why_relevant": "Potential buyer/feedback source for 48h AI Ops Operating Room Blueprint.",
                "approved_for_contact": True,
                "allowed_message_count": 1,
                "opt_out_state": False,
                "notes": "Template only; not approval until owner creates e8_target_seeds.json.",
            },
            {
                "target_id": "benchmark_001",
                "target_type": "internal_benchmark_proxy",
                "name_or_label": "Internal benchmark workflow sample",
                "channel": "internal",
                "contact_handle_or_address": "",
                "relationship_context": "No external contact.",
                "why_relevant": "Can test the offer without customer contact.",
                "approved_for_contact": False,
                "allowed_message_count": 0,
                "opt_out_state": False,
                "notes": "Safe internal proxy.",
            },
        ]
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def render_e8_target_seed_status_or_request(targets: List[E8ValidationTarget]) -> str:
    errors = validate_e8_target_seeds(targets)
    lines = ["# E8 Target Seed Status / Request", ""]
    if not targets:
        lines.extend(
            [
                "- target_seed_status: missing",
                "- external_contact_authorized: false",
                "- exact_owner_action: create `operations/external_validation/e8_target_seeds.json` from the template with real owner-provided non-scraped targets.",
                "",
                "## Template",
                "```json",
                render_e8_target_seed_template(),
                "```",
            ]
        )
    else:
        lines.extend([f"- target_seed_status: {'valid' if not errors else 'invalid'}", f"- validation_errors: {', '.join(errors) or 'none'}", "", "## Targets"])
        for target in targets:
            lines.append(f"- {target.target_id}: {target.name_or_label} / {target.channel} / approved={target.approved_for_contact}")
    return "\n".join(lines)
