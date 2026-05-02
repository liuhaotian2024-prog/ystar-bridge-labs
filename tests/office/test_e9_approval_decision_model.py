from office.mission_command.e9_approval_decision_model import E9ApprovalDecision, E9ApprovalDecisionType, validate_e9_approval_decision


def test_approval_decision_model_supports_approve_edit_reject_hold_escalate():
    for decision in [
        E9ApprovalDecisionType.APPROVE,
        E9ApprovalDecisionType.EDIT,
        E9ApprovalDecisionType.REJECT,
        E9ApprovalDecisionType.HOLD,
        E9ApprovalDecisionType.ESCALATE,
    ]:
        assert decision


def test_approval_decision_reject_requires_reason_and_edit_requires_change():
    assert "missing_reason" in validate_e9_approval_decision(E9ApprovalDecision("d1", "a1", "reject", "owner"))
    assert "edit_requires_changed_field" in validate_e9_approval_decision(E9ApprovalDecision("d2", "a1", "edit", "owner"))
