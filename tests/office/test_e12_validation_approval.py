from pathlib import Path

from office.mission_command.e12_validation_approval import build_e12_approval_request, validate_e12_approval


ROOT = Path(__file__).resolve().parents[2]


def _valid_approval():
    request = build_e12_approval_request(ROOT)
    request.update(
        {
            "proposal_only": False,
            "this_is_not_approval": False,
            "approval_state": "owner_approved",
            "approval_id": "approval_e12_test",
            "approved_by": "owner",
            "approved_at": "2026-05-02T00:00:00Z",
        }
    )
    return request


def test_e12_proposed_manifest_is_not_approval():
    request = build_e12_approval_request(ROOT)
    errors = validate_e12_approval(request)
    assert "approval_request_or_proposal_is_not_approval" in errors
    assert "approval_state_must_be_owner_approved" in errors


def test_e12_valid_owner_approval_passes_schema():
    assert validate_e12_approval(_valid_approval()) == []


def test_e12_approval_blocks_payment_publication_form_account_core_writeback():
    approval = _valid_approval()
    approval["payment_authorized"] = True
    approval["publication_authorized"] = True
    approval["form_submission_authorized"] = True
    approval["account_creation_authorized"] = True
    approval["core_writeback_authorized"] = True
    errors = validate_e12_approval(approval)
    assert "payment_authorized_blocked_in_e12" in errors
    assert "publication_authorized_blocked_in_e12" in errors
    assert "form_submission_authorized_blocked_in_e12" in errors
    assert "account_creation_authorized_blocked_in_e12" in errors
    assert "core_writeback_authorized_blocked_in_e12" in errors

