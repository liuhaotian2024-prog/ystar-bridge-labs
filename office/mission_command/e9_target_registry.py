from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Dict, List


E9_TARGET_SEEDS_PATH = Path("operations/external_validation/e9_target_seeds.json")
E9_TARGET_SEEDS_TEMPLATE_PATH = Path("operations/external_validation/e9_target_seeds.template.json")


@dataclass(frozen=True)
class E9ValidationTarget:
    target_id: str
    target_type: str
    name_or_label: str
    channel: str
    contact_handle_or_address: str
    relationship_context: str
    why_relevant: str
    owner_provided: bool
    approved_for_contact: bool
    allowed_message_count: int
    opt_out_state: bool
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def e9_target_from_dict(data: Dict[str, Any]) -> E9ValidationTarget:
    return E9ValidationTarget(
        target_id=str(data.get("target_id", "")),
        target_type=str(data.get("target_type", "")),
        name_or_label=str(data.get("name_or_label", "")),
        channel=str(data.get("channel", "")),
        contact_handle_or_address=str(data.get("contact_handle_or_address", "")),
        relationship_context=str(data.get("relationship_context", "")),
        why_relevant=str(data.get("why_relevant", "")),
        owner_provided=bool(data.get("owner_provided", False)),
        approved_for_contact=bool(data.get("approved_for_contact", False)),
        allowed_message_count=int(data.get("allowed_message_count", 0) or 0),
        opt_out_state=bool(data.get("opt_out_state", False)),
        notes=str(data.get("notes", "")),
    )


def load_e9_target_seeds(repo_root: Path) -> List[E9ValidationTarget]:
    path = repo_root / E9_TARGET_SEEDS_PATH
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("targets", payload if isinstance(payload, list) else [])
    return [e9_target_from_dict(item) for item in raw]


def validate_e9_target(target: E9ValidationTarget | Dict[str, Any]) -> List[str]:
    item = target if isinstance(target, E9ValidationTarget) else e9_target_from_dict(target)
    errors: List[str] = []
    if not item.target_id:
        errors.append("missing_target_id")
    if item.target_type not in {"known_contact", "founder_peer", "expert", "internal_benchmark_proxy", "public_audience"}:
        errors.append("invalid_target_type")
    if not item.owner_provided and item.target_type != "internal_benchmark_proxy":
        errors.append("target_not_owner_provided")
    if "invented" in (item.relationship_context + " " + item.notes).lower():
        errors.append("invented_contact_not_allowed")
    if "scraped" in (item.relationship_context + " " + item.notes).lower():
        errors.append("scraped_contact_not_allowed")
    if item.target_type in {"known_contact", "founder_peer", "expert"} and not item.contact_handle_or_address:
        errors.append("missing_contact_handle_or_address")
    if item.target_type != "internal_benchmark_proxy" and not item.approved_for_contact:
        errors.append("target_not_approved_for_contact")
    if item.target_type != "internal_benchmark_proxy" and item.allowed_message_count <= 0:
        errors.append("missing_allowed_message_count")
    if item.opt_out_state:
        errors.append("target_opted_out")
    return list(dict.fromkeys(errors))


def validate_e9_target_seeds(targets: List[E9ValidationTarget | Dict[str, Any]]) -> List[str]:
    if not targets:
        return ["missing_e9_target_seeds"]
    errors: List[str] = []
    for target in targets:
        item = target if isinstance(target, E9ValidationTarget) else e9_target_from_dict(target)
        errors.extend(f"{item.target_id or 'unknown'}:{error}" for error in validate_e9_target(item))
    return errors


def e9_target_allows_action(target: E9ValidationTarget | Dict[str, Any] | None, action: Dict[str, Any]) -> bool:
    if target is None or validate_e9_target(target):
        return False
    item = target if isinstance(target, E9ValidationTarget) else e9_target_from_dict(target)
    return item.target_id == action.get("target_id") and item.channel == action.get("channel") and item.approved_for_contact and not item.opt_out_state


def render_e9_target_seed_template() -> str:
    payload = {
        "targets": [
            {
                "target_id": "target_001",
                "target_type": "known_contact",
                "name_or_label": "Owner-provided technical founder or AI-heavy team lead",
                "channel": "owner_selected_email",
                "contact_handle_or_address": "OWNER_TO_FILL",
                "relationship_context": "Owner-provided known contact; not scraped and not invented.",
                "why_relevant": "Potential feedback source for 48h AI Ops Operating Room Blueprint.",
                "owner_provided": True,
                "approved_for_contact": True,
                "allowed_message_count": 1,
                "opt_out_state": False,
                "notes": "Template only; not approval until owner creates e9_target_seeds.json.",
            },
            {
                "target_id": "benchmark_001",
                "target_type": "internal_benchmark_proxy",
                "name_or_label": "Internal benchmark workflow sample",
                "channel": "internal",
                "contact_handle_or_address": "",
                "relationship_context": "No external contact.",
                "why_relevant": "Can test the offer without customer contact.",
                "owner_provided": False,
                "approved_for_contact": False,
                "allowed_message_count": 0,
                "opt_out_state": False,
                "notes": "Safe internal proxy only.",
            },
        ]
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def write_e9_target_seed_template(repo_root: Path) -> Path:
    path = repo_root / E9_TARGET_SEEDS_TEMPLATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_e9_target_seed_template() + "\n", encoding="utf-8")
    return path


def render_e9_target_seed_status_or_request(targets: List[E9ValidationTarget]) -> str:
    errors = validate_e9_target_seeds(targets)
    lines = ["# E9 Target Seed Status / Request", ""]
    if not targets:
        lines.extend(
            [
                "- target_seed_status: missing",
                "- external_contact_authorized: false",
                "- exact_owner_action: create `operations/external_validation/e9_target_seeds.json` from the template with real owner-provided, non-scraped targets.",
                "",
                "## Template",
                "```json",
                render_e9_target_seed_template(),
                "```",
            ]
        )
    else:
        lines.extend([f"- target_seed_status: {'valid' if not errors else 'invalid'}", f"- validation_errors: {', '.join(errors) or 'none'}", "", "## Targets"])
        lines.extend(f"- {target.target_id}: {target.name_or_label} / approved={target.approved_for_contact}" for target in targets)
    return "\n".join(lines)
