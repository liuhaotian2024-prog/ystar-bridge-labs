
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))

PREPARATION_SCOPES = {
    'prepare_review_material_only',
    'prepare_single_controlled_first_user_review_plan',
    'prepare_non_sent_outreach_draft',
    'prepare_reviewer_category_criteria',
}
EXTERNAL_ACTION_SCOPES = {
    'send_outreach', 'publish_packet', 'submit_form', 'identify_real_reviewer', 'collect_contact_info',
}
NEVER_ALLOWED_CLAIM_SCOPES = {'claim_customer_validation', 'claim_paid_signal'}
VALID_DECISIONS = {
    'approve_prepare_single_controlled_first_user_review',
    'request_packet_revision',
    'require_real_mcp_transport_first',
    'require_more_local_demo_evidence',
    'reject_external_review_for_now',
}


def build_owner_approval_record_schema() -> dict[str, Any]:
    return {
        'artifact_id': 'e53_owner_approval_record_schema',
        'required_fields': ['approval_id', 'packet_id', 'owner_decision', 'approved_scope', 'prohibited_scope', 'approval_conditions', 'approval_timestamp', 'approval_source', 'source_evidence', 'expires_at', 'revocable', 'requires_revalidation_before_external_action', 'no_external_action_executed'],
        'allowed_preparation_scopes': sorted(PREPARATION_SCOPES),
        'external_action_scopes_require_later_explicit_approval': sorted(EXTERNAL_ACTION_SCOPES),
        'never_valid_claim_scopes': sorted(NEVER_ALLOWED_CLAIM_SCOPES),
        'no_external_action': True,
    }


def build_pending_placeholder() -> dict[str, Any]:
    return {
        'approval_id': 'e53_pending_owner_decision_placeholder',
        'packet_id': 'governed_agent_action_proof_packet_e52',
        'owner_decision': None,
        'approved_scope': [],
        'prohibited_scope': sorted(EXTERNAL_ACTION_SCOPES | NEVER_ALLOWED_CLAIM_SCOPES | {'payment', 'production_readiness_claim', 'real_mcp_transport_claim'}),
        'approval_conditions': ['owner must explicitly approve any next external step in a future record'],
        'approval_timestamp': None,
        'approval_source': None,
        'source_evidence': None,
        'expires_at': None,
        'revocable': True,
        'requires_revalidation_before_external_action': True,
        'no_external_action_executed': True,
        'owner_decision_status': 'pending_owner_decision',
        'no_external_action_allowed': True,
    }


def _expired(value: str | None) -> bool:
    if not value:
        return False
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')) < datetime.now(timezone.utc)
    except Exception:
        return True


def validate_owner_approval_record(record: dict[str, Any] | None) -> dict[str, Any]:
    if not record or record.get('owner_decision_status') == 'pending_owner_decision' or not record.get('owner_decision'):
        return {'artifact_id': 'e53_owner_approval_validation_result', 'status': 'pending_owner_decision', 'valid': False, 'owner_decision_status': 'pending_owner_decision', 'external_action_allowed': False, 'failures': [], 'no_external_action': True}
    failures: list[dict[str, Any]] = []
    if record.get('owner_decision') not in VALID_DECISIONS:
        failures.append({'reason': 'ambiguous_or_unknown_owner_decision', 'severity': 'P0'})
    if not record.get('source_evidence'):
        failures.append({'reason': 'missing_source_evidence', 'severity': 'P0'})
    if not record.get('approval_source'):
        failures.append({'reason': 'missing_approval_source', 'severity': 'P1'})
    scopes = set(record.get('approved_scope') or [])
    if scopes & NEVER_ALLOWED_CLAIM_SCOPES:
        failures.append({'reason': 'approval_attempts_customer_validation_or_paid_signal_claim', 'severity': 'P0', 'scopes': sorted(scopes & NEVER_ALLOWED_CLAIM_SCOPES)})
    if scopes & EXTERNAL_ACTION_SCOPES and record.get('explicit_external_action_scope') is not True:
        failures.append({'reason': 'external_action_scope_without_explicit_owner_scope', 'severity': 'P0', 'scopes': sorted(scopes & EXTERNAL_ACTION_SCOPES)})
    if record.get('no_external_action_executed') is not True:
        failures.append({'reason': 'approval_record_claims_external_action_executed', 'severity': 'P0'})
    if record.get('revocable') is not True or record.get('requires_revalidation_before_external_action') is not True:
        failures.append({'reason': 'approval_record_missing_revocable_or_revalidation_boundary', 'severity': 'P1'})
    if _expired(record.get('expires_at')):
        failures.append({'reason': 'approval_expired', 'severity': 'P0'})
    status = 'valid' if not failures else 'invalid'
    return {'artifact_id': 'e53_owner_approval_validation_result', 'status': status, 'valid': not failures, 'owner_decision_status': 'owner_approval_validated' if not failures else 'invalid_owner_approval_record', 'external_action_allowed': False, 'failures': failures, 'approved_scope': sorted(scopes), 'no_external_action': True}


def render_schema_markdown(schema: dict[str, Any]) -> str:
    return '\n'.join(['# E53 Owner Approval Record Schema', '', 'Owner approval must be explicit, sourced, revocable, and revalidated before any external action.', '', 'Preparation scopes:', *[f"- {s}" for s in schema['allowed_preparation_scopes']], '', 'External action scopes require a later explicit approval record and are not executed in E53.', ''])


def render_validation_markdown(result: dict[str, Any]) -> str:
    return '\n'.join(['# E53 Owner Approval Validation', '', f"Status: `{result['status']}`", f"Owner decision status: `{result['owner_decision_status']}`", f"External action allowed: `{result['external_action_allowed']}`", '', 'No owner approval was fabricated.', ''])


def write_owner_approval_artifacts(output_root: Path | None = None, record: dict[str, Any] | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    schema = build_owner_approval_record_schema()
    placeholder = build_pending_placeholder() if record is None else record
    validation = validate_owner_approval_record(placeholder)
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e53_owner_approval_record_schema.json').write_text(json.dumps(schema, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'operations/external_validation/e53_owner_approval_record_placeholder.json').write_text(json.dumps(placeholder, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'operations/external_validation/e53_owner_approval_validation_result.json').write_text(json.dumps(validation, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e53_owner_approval_record_schema.md').write_text(render_schema_markdown(schema), encoding='utf-8')
    (root / 'reports/integration/e53_owner_approval_validation_result.md').write_text(render_validation_markdown(validation), encoding='utf-8')
    return {'schema': schema, 'placeholder': placeholder, 'validation': validation}


if __name__ == '__main__':
    print(json.dumps(write_owner_approval_artifacts(), indent=2, ensure_ascii=False))
