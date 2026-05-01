from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def _text(name: str) -> str:
    return (REPORTS / name).read_text(encoding="utf-8")


def test_outreach_draft_is_marked_not_sent():
    text = _text("e7_outreach_draft.md")
    assert "DRAFT ONLY." in text
    assert "NOT SENT." in text
    assert "NO CUSTOMER CONTACT EXECUTED." in text


def test_landing_page_draft_is_marked_not_published():
    text = _text("e7_landing_page_draft.md")
    assert "DRAFT ONLY." in text
    assert "NOT PUBLISHED." in text
    assert "CTA is not active" in text


def test_demo_call_script_is_marked_owner_approval_required():
    text = _text("e7_demo_call_script.md")
    assert "OWNER APPROVAL REQUIRED BEFORE EXTERNAL USE." in text
    assert "NOT SENT." in text


def test_survey_question_set_is_marked_owner_approval_required():
    text = _text("e7_validation_survey_or_question_set.md")
    assert "OWNER APPROVAL REQUIRED BEFORE EXTERNAL USE." in text
    assert "NOT PUBLISHED." in text


def test_drafts_do_not_claim_external_execution():
    combined = "\n".join(
        _text(name)
        for name in [
            "e7_outreach_draft.md",
            "e7_landing_page_draft.md",
            "e7_demo_call_script.md",
            "e7_validation_survey_or_question_set.md",
        ]
    )
    assert "NO CUSTOMER CONTACT EXECUTED." in combined
    assert "sent to" not in combined.lower()
    assert "published at" not in combined.lower()
