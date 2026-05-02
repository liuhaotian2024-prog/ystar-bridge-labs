from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .e9_draft_binding import bind_e9_frozen_drafts
from .e10_target_candidate_registry import E10TargetCandidate
from .e10_validation_batch_builder import E10ValidationBatch


E10_PROPOSED_MANIFEST_PATH = Path("operations/external_validation/e10_external_validation_manifest.proposed.json")
E10_PROPOSED_TARGET_SEEDS_PATH = Path("operations/external_validation/e10_target_seeds.proposed.json")


def _draft_hash(repo_root: Path, draft_id: str) -> str:
    for binding in bind_e9_frozen_drafts(repo_root, None):
        if binding.draft_id == draft_id:
            return binding.draft_hash
    return "DRAFT_HASH_NOT_FOUND"


def build_e10_external_validation_manifest_proposal(repo_root: Path, batch: E10ValidationBatch) -> Dict[str, Any]:
    return {
        "proposal_only": True,
        "template_is_approval": False,
        "external_contact_authorized": False,
        "publication_authorized": False,
        "payment_form_account_actions_authorized": False,
        "manifest_id": "OWNER_TO_REVIEW_E10_PROPOSED_MANIFEST",
        "approved_by": "OWNER_TO_FILL_IF_APPROVED",
        "approved_at": "OWNER_TO_FILL_IF_APPROVED",
        "top_offer": "48h AI Ops Operating Room Blueprint",
        "recommended_batch_id": batch.batch_id,
        "validation_mode": batch.validation_mode,
        "autonomy_budget": {
            "budget_id": "OWNER_TO_FILL_E11_BUDGET",
            "max_external_messages": len(batch.target_candidate_ids),
            "max_public_posts": 0,
            "max_landing_pages": 0,
            "max_followups_per_target": 0,
            "max_targets": len(batch.target_candidate_ids),
            "allowed_risk_tiers": ["TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION"],
            "allowed_channels": [batch.recommended_channel],
            "expires_at": "OWNER_TO_FILL_EXPIRY",
            "stop_conditions": batch.stop_conditions,
            "require_human_review_before_send": True,
            "allow_aiden_execution": False,
            "allow_owner_operated_handoff": True,
        },
        "approved_draft_ids": [batch.draft_id],
        "approved_draft_hashes": {batch.draft_id: _draft_hash(repo_root, batch.draft_id)},
        "approved_target_seed_ids": batch.target_candidate_ids,
        "approved_channels": [batch.recommended_channel],
        "allowed_action_types": ["send_validation_message", "request_feedback"],
        "forbidden_action_types": [
            "collect_payment",
            "create_account",
            "submit_form",
            "publish_post",
            "publish_landing_page",
            "execute_contract",
            "production_implementation",
            "core_writeback",
        ],
        "ai_disclosure_required": True,
        "opt_out_required": True,
        "no_scraped_leads": True,
        "no_bulk_outreach": True,
        "notes": "Generated proposal for owner review only. It does not authorize Aiden to contact, send, publish, collect payment, submit forms, create accounts, or write core memory.",
    }


def build_e10_target_seeds_proposal(batch: E10ValidationBatch, candidates: List[E10TargetCandidate]) -> Dict[str, Any]:
    by_id = {candidate.candidate_id: candidate for candidate in candidates}
    targets: List[Dict[str, Any]] = []
    for candidate_id in batch.target_candidate_ids:
        candidate = by_id[candidate_id]
        targets.append(
            {
                "target_id": candidate.candidate_id,
                "target_type": candidate.target_type,
                "name_or_label": candidate.target_name_or_label,
                "source_public_url": candidate.public_url,
                "source_ids": candidate.source_ids,
                "segment": candidate.segment,
                "channel": batch.recommended_channel,
                "contact_handle_or_address": "OWNER_TO_REVIEW_AND_FILL_IF_APPROVED",
                "relationship_context": "Autonomously discovered public candidate; not owner-approved for contact yet.",
                "why_relevant": "Public evidence suggests implementation burden, governance need, budget proxy, or reachable validation path for the 48h AI Ops Operating Room Blueprint.",
                "discovered_by_aiden": True,
                "owner_approved_for_contact": False,
                "contact_executed": False,
                "allowed_message_count": 1,
                "opt_out_state": False,
                "notes": "Proposal only. No scraped personal contact and no external contact executed.",
            }
        )
    return {
        "proposal_only": True,
        "contact_authorized": False,
        "contact_executed": False,
        "recommended_batch_id": batch.batch_id,
        "targets": targets,
    }


def write_e10_manifest_and_target_proposals(
    repo_root: Path,
    batch: E10ValidationBatch,
    candidates: List[E10TargetCandidate],
) -> Tuple[Path, Path, Dict[str, Any], Dict[str, Any]]:
    manifest = build_e10_external_validation_manifest_proposal(repo_root, batch)
    targets = build_e10_target_seeds_proposal(batch, candidates)
    manifest_path = repo_root / E10_PROPOSED_MANIFEST_PATH
    targets_path = repo_root / E10_PROPOSED_TARGET_SEEDS_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    targets_path.write_text(json.dumps(targets, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest_path, targets_path, manifest, targets


def render_e10_manifest_target_proposal(manifest_path: Path, targets_path: Path, manifest: Dict[str, Any], targets: Dict[str, Any]) -> str:
    return "\n".join(
        [
            "# E10 Manifest and Target Seed Proposal",
            "",
            f"- proposed_manifest_path: {manifest_path}",
            f"- proposed_target_seeds_path: {targets_path}",
            "- proposal_only: true",
            "- external_contact_authorized: false",
            "- publication_authorized: false",
            "- payment_form_account_actions_authorized: false",
            f"- recommended_batch_id: {manifest['recommended_batch_id']}",
            f"- proposed_target_count: {len(targets['targets'])}",
            f"- draft_ids: {', '.join(manifest['approved_draft_ids'])}",
            f"- draft_hashes: {manifest['approved_draft_hashes']}",
            "",
            "## Owner Review Required",
            "- Owner must edit/approve target IDs, channel, draft hash, count, stop conditions, and execution mode before E11 contact.",
            "- `owner_approved_for_contact` remains false in this proposal.",
            "- Proposed target seeds are not approval and are not a sending instruction.",
        ]
    )
