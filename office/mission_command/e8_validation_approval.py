from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List

from .e8_autonomy_budget import autonomy_budget_from_dict, render_e8_autonomy_budget_template, validate_e8_autonomy_budget
from .e8_risk_controlled_action_model import ActionType, RiskTier, classify_external_action


MANIFEST_PATH = Path("operations/external_validation/e8_external_validation_manifest.json")
MANIFEST_TEMPLATE_PATH = Path("operations/external_validation/e8_external_validation_manifest.template.json")


@dataclass(frozen=True)
class E8ExternalValidationManifest:
    manifest_id: str = ""
    approved_by: str = ""
    approved_at: str = ""
    top_offer: str = ""
    validation_mode: str = ""
    autonomy_budget: Dict[str, Any] = field(default_factory=dict)
    approved_draft_ids: List[str] = field(default_factory=list)
    approved_target_seed_ids: List[str] = field(default_factory=list)
    approved_channels: List[str] = field(default_factory=list)
    allowed_action_types: List[str] = field(default_factory=list)
    forbidden_action_types: List[str] = field(default_factory=list)
    ai_disclosure_required: bool = True
    opt_out_required: bool = True
    no_scraped_leads: bool = True
    no_bulk_outreach: bool = True
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def manifest_from_dict(data: Dict[str, Any] | None) -> E8ExternalValidationManifest:
    data = data or {}
    return E8ExternalValidationManifest(
        manifest_id=str(data.get("manifest_id", "")),
        approved_by=str(data.get("approved_by", "")),
        approved_at=str(data.get("approved_at", "")),
        top_offer=str(data.get("top_offer", "")),
        validation_mode=str(data.get("validation_mode", "")),
        autonomy_budget=dict(data.get("autonomy_budget", {})),
        approved_draft_ids=list(data.get("approved_draft_ids", [])),
        approved_target_seed_ids=list(data.get("approved_target_seed_ids", [])),
        approved_channels=list(data.get("approved_channels", [])),
        allowed_action_types=list(data.get("allowed_action_types", [])),
        forbidden_action_types=list(data.get("forbidden_action_types", [])),
        ai_disclosure_required=bool(data.get("ai_disclosure_required", True)),
        opt_out_required=bool(data.get("opt_out_required", True)),
        no_scraped_leads=bool(data.get("no_scraped_leads", True)),
        no_bulk_outreach=bool(data.get("no_bulk_outreach", True)),
        notes=str(data.get("notes", "")),
    )


def load_e8_external_validation_manifest(repo_root: Path) -> E8ExternalValidationManifest | None:
    path = repo_root / MANIFEST_PATH
    if not path.exists():
        return None
    return manifest_from_dict(json.loads(path.read_text(encoding="utf-8")))


def validate_e8_external_validation_manifest(manifest: E8ExternalValidationManifest | Dict[str, Any] | None) -> List[str]:
    if manifest is None:
        return ["missing_external_validation_manifest"]
    item = manifest if isinstance(manifest, E8ExternalValidationManifest) else manifest_from_dict(manifest)
    errors: List[str] = []
    if not item.manifest_id:
        errors.append("missing_manifest_id")
    if not item.approved_by or item.approved_by.lower() in {"owner", "tbd", "someone"}:
        errors.append("missing_specific_approver")
    if not item.approved_at:
        errors.append("missing_approved_at")
    if not item.top_offer:
        errors.append("missing_top_offer")
    if not item.validation_mode:
        errors.append("missing_validation_mode")
    if not item.approved_draft_ids:
        errors.append("missing_approved_draft_ids")
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
    tier4_actions = [
        action
        for action in item.allowed_action_types
        if classify_external_action(action) == RiskTier.TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK
    ]
    if tier4_actions:
        errors.append("tier4_action_allowed_in_manifest")
    for action in [ActionType.COLLECT_PAYMENT, ActionType.CREATE_ACCOUNT, ActionType.SUBMIT_FORM, ActionType.CORE_WRITEBACK]:
        if action in item.allowed_action_types:
            errors.append(f"forbidden_action_allowed:{action}")
    return list(dict.fromkeys(errors))


def manifest_allows_action(manifest: E8ExternalValidationManifest | Dict[str, Any] | None, action: Dict[str, Any]) -> bool:
    if validate_e8_external_validation_manifest(manifest):
        return False
    item = manifest if isinstance(manifest, E8ExternalValidationManifest) else manifest_from_dict(manifest)
    tier = str(action.get("risk_tier") or classify_external_action(str(action.get("action_type", ""))))
    budget = autonomy_budget_from_dict(item.autonomy_budget)
    return (
        str(action.get("action_type", "")) in item.allowed_action_types
        and str(action.get("channel", "")) in item.approved_channels
        and str(action.get("target_id", "")) in item.approved_target_seed_ids
        and str(action.get("draft_id", "")) in item.approved_draft_ids
        and not validate_e8_autonomy_budget(budget, requested_tier=tier)
    )


def render_e8_manifest_template() -> str:
    template = E8ExternalValidationManifest(
        manifest_id="e8_manifest_owner_to_fill",
        approved_by="OWNER_NAME_REQUIRED",
        approved_at="YYYY-MM-DDTHH:MM:SSZ",
        top_offer="48h AI Ops Operating Room Blueprint",
        validation_mode="owner_operated_3_person_qualitative_validation",
        autonomy_budget=render_e8_autonomy_budget_template(),
        approved_draft_ids=["e8_ai_disclosed_outreach_draft"],
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
        ai_disclosure_required=True,
        opt_out_required=True,
        no_scraped_leads=True,
        no_bulk_outreach=True,
        notes="Owner must replace placeholders. This template does not authorize execution.",
    )
    return json.dumps(template.to_dict(), indent=2, ensure_ascii=False)


def render_e8_manifest_status_or_request(manifest: E8ExternalValidationManifest | None) -> str:
    errors = validate_e8_external_validation_manifest(manifest)
    lines = ["# E8 External Validation Manifest Status / Request", ""]
    if manifest is None:
        lines.extend(
            [
                "- manifest_status: missing",
                "- external_validation_authorized: false",
                "- exact_owner_action: create `operations/external_validation/e8_external_validation_manifest.json` from the template with exact count/channel/target/draft/stop conditions.",
                "",
                "## Template",
                "```json",
                render_e8_manifest_template(),
                "```",
            ]
        )
    else:
        lines.extend(
            [
                f"- manifest_status: {'valid' if not errors else 'invalid'}",
                f"- validation_errors: {', '.join(errors) or 'none'}",
                "```json",
                json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False),
                "```",
            ]
        )
    return "\n".join(lines)
