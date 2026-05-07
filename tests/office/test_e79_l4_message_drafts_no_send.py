import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e79_l4_message_drafts_are_not_sent_and_short():
    drafts = _load("operations/external_validation/e79_l4_message_drafts_no_send.json")

    assert drafts["status"] == "draft_only_not_sent"
    assert drafts["messages_sent"] is False
    assert drafts["external_action_allowed"] is False
    assert len(drafts["drafts"]) == 3
    for draft in drafts["drafts"]:
        assert draft["not_sent"] is True
        assert draft["clear_feedback_question"]
        assert len(draft["body"].split()) <= 90
        lower_body = draft["body"].lower()
        assert (
            "not compliance" in lower_body
            or "not legal compliance" in lower_body
            or "does not claim compliance" in lower_body
        )


def test_e79_concept_note_is_draft_only_not_published():
    concept = _load("operations/external_validation/e79_l4_concept_note_draft_no_publication.json")

    assert concept["status"] == "draft_only_no_publication"
    assert concept["published"] is False
    assert concept["external_action_allowed"] is False
    assert "Agent Ops Control Review" == concept["title"]
    assert "CIEU means" in concept["plain_language_CIEU"]
