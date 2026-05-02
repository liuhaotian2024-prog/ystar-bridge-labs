from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from .e8_draft_freeze import freeze_validation_drafts, validate_frozen_draft_transparency, verify_draft_hash


@dataclass(frozen=True)
class E9DraftBinding:
    draft_id: str
    draft_hash: str
    source_path: str
    intended_channel: str
    ai_disclosure_present: bool
    opt_out_present: bool
    approved_by_manifest: bool
    binding_errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def bind_e9_frozen_drafts(repo_root: Path, manifest: Any | None = None) -> List[E9DraftBinding]:
    drafts = freeze_validation_drafts(repo_root)
    approved_ids = set(getattr(manifest, "approved_draft_ids", []) or [])
    approved_hashes = getattr(manifest, "approved_draft_hashes", {}) or {}
    bindings: List[E9DraftBinding] = []
    for draft in drafts:
        errors = validate_frozen_draft_transparency(draft)
        approved = draft["draft_id"] in approved_ids and verify_draft_hash(draft, approved_hashes.get(draft["draft_id"], ""))
        if draft["draft_id"] in approved_ids and not approved:
            errors.append("manifest_draft_hash_mismatch")
        bindings.append(
            E9DraftBinding(
                draft_id=draft["draft_id"],
                draft_hash=draft["content_hash"],
                source_path=draft["source_path"],
                intended_channel=draft["intended_channel"],
                ai_disclosure_present=bool(draft["ai_disclosure_present"]),
                opt_out_present=bool(draft["opt_out_present"]),
                approved_by_manifest=approved,
                binding_errors=list(dict.fromkeys(errors)),
            )
        )
    return bindings


def validate_e9_draft_binding(binding: E9DraftBinding | Dict[str, Any]) -> List[str]:
    item = binding if isinstance(binding, E9DraftBinding) else E9DraftBinding(**binding)
    errors = list(item.binding_errors)
    if not item.ai_disclosure_present:
        errors.append("draft_requires_ai_disclosure")
    if not item.opt_out_present:
        errors.append("draft_requires_opt_out")
    return list(dict.fromkeys(errors))


def render_e9_frozen_approved_draft_binding(bindings: List[E9DraftBinding]) -> str:
    lines = ["# E9 Frozen Approved Draft Binding", ""]
    for binding in bindings:
        lines.extend(
            [
                f"## {binding.draft_id}",
                f"- draft_hash: {binding.draft_hash}",
                f"- source_path: {binding.source_path}",
                f"- intended_channel: {binding.intended_channel}",
                f"- ai_disclosure_present: {binding.ai_disclosure_present}",
                f"- opt_out_present: {binding.opt_out_present}",
                f"- approved_by_manifest: {binding.approved_by_manifest}",
                f"- binding_errors: {', '.join(binding.binding_errors) or 'none'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()
