from datetime import datetime, timedelta, timezone
from office.mission_command.e53_owner_approval_record import build_pending_placeholder, validate_owner_approval_record

def test_pending_placeholder_blocks_external_action():
    result = validate_owner_approval_record(build_pending_placeholder())
    assert result["status"] == "pending_owner_decision"
    assert result["external_action_allowed"] is False

def test_missing_source_evidence_fails():
    record = {"approval_id":"x","packet_id":"governed_agent_action_proof_packet_e52","owner_decision":"approve_prepare_single_controlled_first_user_review","approved_scope":["prepare_single_controlled_first_user_review_plan"],"no_external_action_executed":True,"revocable":True,"requires_revalidation_before_external_action":True}
    result = validate_owner_approval_record(record)
    assert result["status"] == "invalid"
    assert any(f["reason"] == "missing_source_evidence" for f in result["failures"])

def test_outreach_without_explicit_scope_fails():
    record = {"approval_id":"x","packet_id":"governed_agent_action_proof_packet_e52","owner_decision":"approve_prepare_single_controlled_first_user_review","approved_scope":["send_outreach"],"approval_source":"repo","source_evidence":"x","no_external_action_executed":True,"revocable":True,"requires_revalidation_before_external_action":True}
    result = validate_owner_approval_record(record)
    assert result["status"] == "invalid"
    assert any(f["reason"] == "external_action_scope_without_explicit_owner_scope" for f in result["failures"])

def test_expired_approval_fails():
    record = {"approval_id":"x","packet_id":"governed_agent_action_proof_packet_e52","owner_decision":"approve_prepare_single_controlled_first_user_review","approved_scope":["prepare_single_controlled_first_user_review_plan"],"approval_source":"repo","source_evidence":"x","expires_at":(datetime.now(timezone.utc)-timedelta(days=1)).isoformat(),"no_external_action_executed":True,"revocable":True,"requires_revalidation_before_external_action":True}
    result = validate_owner_approval_record(record)
    assert result["status"] == "invalid"
    assert any(f["reason"] == "approval_expired" for f in result["failures"])
