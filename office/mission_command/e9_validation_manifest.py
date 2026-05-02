from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List

from .e8_autonomy_budget import render_e8_autonomy_budget_template, validate_e8_autonomy_budget
from .e8_risk_controlled_action_model import ActionType, RiskTier, classify_external_action


E9_MANIFEST_PATH = Path("operations/external_validation/e9_external_validation_manifest.json")
E9_MANIFEST_TEMPLATE_PATH = Path("operations/external_validation/e9_external_validation_manifest.template.json")


@dataclass(frozen=True)
class E9ExternalValidationManifest:
    manifest_id: str = ""
    approved_by: str = ""
    approved_at: str = ""
    top_offer: str = ""
    validation_mode: str = ""
    autonomy_budget: Dict[str, Any] = field(default_factory=dict)
    approved_draft_ids: List[str] = field(default_factory=list)
    approved_draft_hashes: Dict[str, str] = field(default_factory=dict)
    approved_target_seed_ids: List[str] = field(default_factory=list)
    approved_channels: List[str] = field(default_factory=list)
    allowed_action_types: List[str] = field(default_factory=list)
    forbidden_action_types: List[str] = field(default_factory=list)
    ai_disclosure_required: bool = True
    opt_out_required: bool = True
    no_scraped_leads: bool = True
    no_bulk_outreach: bool = True
    progressive_autonomy_level: str = "L2_owner_operated_handoff"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def e9_manifest_from_dict(data: Dict[str, Any] | None) -> E9ExternalValidationManifest:
    data = data or {}
    return E9ExternalValidationManifest(
        manifest_id=str(data.get("manifest_id", "")),
        approved_by=str(data.get("approved_by", "")),
        approved_at=str(data.get("approved_at", "")),
        top_offer=str(data.get("top_offer", "")),
        validation_mode=str(data.get("validation_mode", "")),
        autonomy_budget=dict(data.get("autonomy_budget", {})),
        approved_draft_ids=list(data.get("approved_draft_ids", [])),
        approved_draft_hashes=dict(data.get("approved_draft_hashes", {})),
        approved_target_seed_ids=list(data.get("approved_target_seed_ids", [])),
        approved_channels=list(data.get("approved_channels", [])),
        allowed_action_types=list(data.get("allowed_action_types", [])),
        forbidden_action_types=list(data.get("forbidden_action_types", [])),
        ai_disclosure_required=bool(data.get("ai_disclosure_required", True)),
        opt_out_required=bool(data.get("opt_out_required", True)),
        no_scraped_leads=bool(data.get("no_scraped_leads", True)),
        no_bulk_outreach=bool(data.get("no_bulk_outreach", True)),
        progressive_autonomy_level=str(data.get("progressive_autonomy_level", "L2_owner_operated_handoff")),
        notes=str(data.get("notes", "")),
    )


def load_e9_validation_manifest(repo_root: Path) -> E9ExternalValidationManifest | None:
    path = repo_root / E9_MANIFEST_PATH
    if not path.exists():
        return None
    return e9_manifest_from_dict(json.loads(path.read_text(encoding="utf-8")))


def _placeholder(value: str) -> bool:
    lower = value.lower()
    return any(token in lower for token in ["owner_to_fill", "owner_name_required", "tbd", "placeholder", "template", "yyyy-mm-dd"])


def validate_e9_validation_manifest(manifest: E9ExternalValidationManifest | Dict[str, Any] | None) -> List[str]:
    if manifest is None:
        return ["missing_e9_validation_manifest"]
    item = manifest if isinstance(manifest, E9ExternalValidationManifest) else e9_manifest_from_dict(manifest)
    errors: List[str] = []
    for name in ["manifest_id", "approved_by", "approved_at", "top_offer", "validation_mode"]:
        value = str(getattr(item, name))
        if not value:
            errors.append(f"missing_{name}")
        elif _placeholder(value):
            errors.append(f"placeholder_{name}")
    if not item.approved_draft_ids:
        errors.append("missing_approved_draft_ids")
    if not item.approved_draft_hashes:
        errors.append("missing_exact_draft_hash")
    for draft_id in item.approved_draft_ids:
        if not item.approved_draft_hashes.get(draft_id) or _placeholder(str(item.approved_draft_hashes.get(draft_id, ""))):
            errors.append("missing_exact_draft_hash")
    if not item.approved_target_seed_ids and "contact" in item.validation_mode:
        errors.append("missing_approved_target_seed_ids")
    if not item.approved_channels:
        errors.append("missing_approved_channels")
    if not item.allowed_action_types:
        errors.append("missing_allowed_action_types")
    if not item.ai_disclosure_required:
        errors.append("ai_disclosure_required_false")
    if not item.opt_out_required:
        errors.append("opt_out_required_false")
    if not item.no_scraped_leads:
        errors.append("scraped_leads_not_forbidden")
    if not item.no_bulk_outreach:
        errors.append("bulk_outreach_not_forbidden")
    errors.extend(validate_e8_autonomy_budget(item.autonomy_budget))
    for action in item.allowed_action_types:
        if classify_external_action(action) == RiskTier.TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK:
            errors.append("tier4_action_allowed_in_e9")
    for action in [ActionType.COLLECT_PAYMENT, ActionType.CREATE_ACCOUNT, ActionType.SUBMIT_FORM, ActionType.CORE_WRITEBACK]:
        if action in item.allowed_action_types:
            errors.append(f"forbidden_action_allowed:{action}")
    return list(dict.fromkeys(errors))


def e9_manifest_allows_action(manifest: E9ExternalValidationManifest | Dict[str, Any] | None, action: Dict[str, Any]) -> bool:
    if validate_e9_validation_manifest(manifest):
        return False
    item = manifest if isinstance(manifest, E9ExternalValidationManifest) else e9_manifest_from_dict(manifest)
    return (
        str(action.get("action_type", "")) in item.allowed_action_types
        and str(action.get("target_id", "")) in item.approved_target_seed_ids
        and str(action.get("channel", "")) in item.approved_channels
        and str(action.get("draft_id", "")) in item.approved_draft_ids
        and str(action.get("draft_hash", "")) == item.approved_draft_hashes.get(str(action.get("draft_id", "")))
    )


def render_e9_manifest_template() -> str:
    template = E9ExternalValidationManifest(
        manifest_id="OWNER_TO_FILL_E9_MANIFEST_ID",
        approved_by="OWNER_NAME_REQUIRED",
        approved_at="YYYY-MM-DDTHH:MM:SSZ",
        top_offer="48h AI Ops Operating Room Blueprint",
        validation_mode="owner_operated_3_person_qualitative_validation",
        autonomy_budget=render_e8_autonomy_budget_template(),
        approved_draft_ids=["e8_ai_disclosed_outreach_draft"],
        approved_draft_hashes={"e8_ai_disclosed_outreach_draft": "OWNER_TO_FILL_EXACT_HASH_FROM_E9_DRAFT_BINDING"},
        approved_target_seed_ids=["target_001", "target_002", "target_003"],
        approved_channels=["owner_selected_email"],
        allowed_action_types=[ActionType.SEND_VALIDATION_MESSAGE, ActionType.REQUEST_FEEDBACK],
        forbidden_action_types=[
            ActionType.COLLECT_PAYMENT,
            ActionType.CREATE_ACCOUNT,
            ActionType.SUBMIT_FORM,
            ActionType.EXECUTE_CONTRACT,
            ActionType.PRODUCTION_IMPLEMENTATION,
            ActionType.CORE_WRITEBACK,
        ],
        notes="Template only. It does not authorize Aiden to send, publish, collect payment, submit forms, or create accounts.",
    )
    return json.dumps(template.to_dict(), indent=2, ensure_ascii=False)


def write_e9_manifest_template(repo_root: Path) -> Path:
    path = repo_root / E9_MANIFEST_TEMPLATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_e9_manifest_template() + "\n", encoding="utf-8")
    return path


def render_e9_manifest_status_or_request(manifest: E9ExternalValidationManifest | None) -> str:
    errors = validate_e9_validation_manifest(manifest)
    lines = ["# E9 Manifest Status / Request", ""]
    if manifest is None:
        lines.extend(
            [
                "- manifest_status: missing",
                "- template_is_approval: false",
                "- external_validation_authorized: false",
                "- exact_owner_action: create `operations/external_validation/e9_external_validation_manifest.json` from the template with specific approver, exact draft hash, target IDs, channel, count, expiry, and stop conditions.",
                "",
                "## Template",
                "```json",
                render_e9_manifest_template(),
                "```",
            ]
        )
    else:
        lines.extend(
            [
                f"- manifest_status: {'valid' if not errors else 'invalid'}",
                f"- validation_errors: {', '.join(errors) or 'none'}",
                "- template_is_approval: false",
                "```json",
                json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False),
                "```",
            ]
        )
    return "\n".join(lines)
