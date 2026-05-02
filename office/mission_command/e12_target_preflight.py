from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .target_lifecycle_router import route_target_lifecycle


E12_APPROVED_TARGETS_PATH = Path("operations/external_validation/e12_target_seeds.json")
E12_TARGET_REQUEST_PATH = Path("operations/external_validation/e12_target_seeds.request.json")
E10_PROPOSED_TARGETS_PATH = Path("operations/external_validation/e10_target_seeds.proposed.json")


@dataclass(frozen=True)
class E12TargetPreflightResult:
    target_id: str
    target_label: str
    lifecycle_state: str
    owner_approved_for_contact: bool
    preflight_allowed: bool
    contact_allowed: bool
    execution_allowed: bool
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_e12_target_seed_request(repo_root: Path) -> Dict[str, Any]:
    proposal = _load_json(repo_root / E10_PROPOSED_TARGETS_PATH)
    targets = []
    for item in proposal.get("targets", []):
        targets.append(
            {
                **item,
                "approval_state": "proposed",
                "proposal_only": True,
                "this_is_not_approval": True,
                "owner_approved_for_contact": False,
                "contact_executed": False,
                "owner_action_needed": "Set approval_state=owner_approved, owner_approved_for_contact=true, and provide an approved non-scraped channel/contact value if contact is approved.",
            }
        )
    return {
        "request_type": "e12_target_seed_approval_request",
        "proposal_only": True,
        "contact_authorized": False,
        "contact_executed": False,
        "recommended_batch_id": proposal.get("recommended_batch_id", "batch_ai_ops_agency_governance_layer"),
        "targets": targets,
    }


def write_e12_target_seed_request(repo_root: Path) -> Path:
    path = repo_root / E12_TARGET_REQUEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_e12_target_seed_request(repo_root), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_e12_target_seed(target: Dict[str, Any], approved_target_ids: List[str] | None = None) -> List[str]:
    errors: List[str] = []
    approved_target_ids = approved_target_ids or []
    if target.get("proposal_only") is True or target.get("this_is_not_approval") is True:
        errors.append("proposed_target_seed_is_not_approval")
    if target.get("approval_state") not in {"owner_approved", None} and target.get("owner_approved_for_contact") is not True:
        errors.append("target_approval_state_not_owner_approved")
    if target.get("owner_approved_for_contact") is not True:
        errors.append("owner_approved_for_contact_required")
    if approved_target_ids and target.get("target_id") not in approved_target_ids:
        errors.append("target_not_in_approved_manifest")
    contact = str(target.get("contact_handle_or_address", ""))
    if "OWNER_TO_" in contact or not contact.strip():
        errors.append("approved_contact_or_public_general_channel_required")
    if "scraped" in contact.lower() or target.get("scraped_personal_contact") is True:
        errors.append("scraped_personal_contact_blocked")
    if target.get("opt_out_state") in {"opted_out", "stop_requested", True}:
        errors.append("target_opted_out_or_suppressed")
    if int(target.get("allowed_message_count") or 0) <= 0:
        errors.append("allowed_message_count_required")
    return list(dict.fromkeys(errors))


def load_e12_target_preflight(repo_root: Path, approved_target_ids: List[str] | None = None) -> List[E12TargetPreflightResult]:
    request_path = write_e12_target_seed_request(repo_root)
    approved_targets = _load_json(repo_root / E12_APPROVED_TARGETS_PATH)
    source = approved_targets if approved_targets else _load_json(request_path)
    results: List[E12TargetPreflightResult] = []
    for target in source.get("targets", []):
        errors = validate_e12_target_seed(target, approved_target_ids)
        routed = route_target_lifecycle(target)
        results.append(
            E12TargetPreflightResult(
                target_id=str(target.get("target_id", "unknown_target")),
                target_label=str(target.get("name_or_label", target.get("target_id", "unknown_target"))),
                lifecycle_state=routed.state.value,
                owner_approved_for_contact=target.get("owner_approved_for_contact") is True,
                preflight_allowed=routed.preflight_allowed and not errors,
                contact_allowed=routed.contact_allowed and not errors,
                execution_allowed=routed.execution_allowed and not errors,
                errors=errors or ([routed.blocked_reason] if routed.blocked_reason else []),
            )
        )
    if not results:
        results.append(
            E12TargetPreflightResult(
                target_id="missing_targets",
                target_label="missing_targets",
                lifecycle_state="missing",
                owner_approved_for_contact=False,
                preflight_allowed=False,
                contact_allowed=False,
                execution_allowed=False,
                errors=["missing_e12_target_seeds"],
            )
        )
    return results


def render_e12_target_preflight(results: List[E12TargetPreflightResult]) -> str:
    lines = ["# E12 Target Lifecycle Preflight", ""]
    for result in results:
        lines.extend(
            [
                f"## {result.target_id}",
                f"- label: {result.target_label}",
                f"- lifecycle_state: {result.lifecycle_state}",
                f"- owner_approved_for_contact: {str(result.owner_approved_for_contact).lower()}",
                f"- preflight_allowed: {str(result.preflight_allowed).lower()}",
                f"- contact_allowed: {str(result.contact_allowed).lower()}",
                f"- execution_allowed: {str(result.execution_allowed).lower()}",
                f"- errors: {', '.join(result.errors) or 'none'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()
