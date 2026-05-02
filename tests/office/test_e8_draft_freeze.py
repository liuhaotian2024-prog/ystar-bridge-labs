from pathlib import Path

from office.mission_command.e8_draft_freeze import freeze_validation_drafts, validate_frozen_draft_transparency, verify_draft_hash


ROOT = Path(__file__).resolve().parents[2]


def test_frozen_drafts_record_hashes():
    drafts = freeze_validation_drafts(ROOT)
    assert drafts
    assert all(draft["content_hash"] for draft in drafts)


def test_draft_hash_mismatch_blocks_preflight():
    draft = freeze_validation_drafts(ROOT)[0]
    assert verify_draft_hash(draft, draft["content_hash"])
    assert not verify_draft_hash(draft, "wronghash")


def test_ai_disclosed_outreach_draft_passes_transparency_freeze():
    draft = freeze_validation_drafts(ROOT)[0]
    assert draft["draft_id"] == "e8_ai_disclosed_outreach_draft"
    assert draft["ai_disclosure_present"] is True
    assert draft["opt_out_present"] is True
    assert "draft_should_not_be_approved_without_manifest" not in validate_frozen_draft_transparency(draft)
