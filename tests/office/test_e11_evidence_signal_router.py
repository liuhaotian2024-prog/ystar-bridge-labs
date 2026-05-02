from office.mission_command.evidence_signal_router import EvidenceClaimType, EvidenceSignalType, route_evidence_signal


def test_evidence_router_blocks_public_target_discovery_from_paid_pilot_if_router_implemented():
    decision = route_evidence_signal(EvidenceSignalType.PUBLIC_TARGET_DISCOVERY_EVIDENCE, EvidenceClaimType.PAID_PILOT_PREP)
    assert decision.allowed is False
    assert decision.required_upgrade == "paid_signal"


def test_evidence_router_allows_validation_feedback_to_support_validation_result_if_router_implemented():
    decision = route_evidence_signal(EvidenceSignalType.VALIDATION_FEEDBACK, EvidenceClaimType.VALIDATION_RESULT)
    assert decision.allowed is True


def test_evidence_router_requires_paid_signal_for_paid_pilot_prep_if_router_implemented():
    feedback_decision = route_evidence_signal(EvidenceSignalType.VALIDATION_FEEDBACK, EvidenceClaimType.PAID_PILOT_PREP)
    paid_decision = route_evidence_signal(EvidenceSignalType.PAID_SIGNAL, EvidenceClaimType.PAID_PILOT_PREP)
    assert feedback_decision.allowed is False
    assert paid_decision.allowed is True

