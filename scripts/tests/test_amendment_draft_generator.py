"""Test: AmendmentDraftGenerator — agent-driven bounded self-modification proposals.

Covers: tier classification + markdown generation + CIEU event emission + CZL-159 header.
"""
import json
import os
import sys
import tempfile
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amendment_draft_generator import (
    AmendmentDraftGenerator, AmendmentDraft, TIER_DESCRIPTIONS,
)


def test_propose_creates_markdown_file(tmp_path):
    gen = AmendmentDraftGenerator(
        reports_dir=tmp_path / "reports" / "cto",
        cieu_log_path=tmp_path / "logs" / "amendments.jsonl",
    )
    d = gen.propose_amendment(
        gap="test gap", current_behavior="test current",
        proposed_change="test proposed", tier="low",
    )
    assert Path(d.draft_path).exists()
    assert d.amendment_id.startswith("AMENDMENT_DRAFT_")
    assert d.tier == "low"


def test_markdown_has_czl159_header(tmp_path):
    gen = AmendmentDraftGenerator(
        reports_dir=tmp_path / "reports" / "cto",
        cieu_log_path=tmp_path / "logs" / "amendments.jsonl",
    )
    d = gen.propose_amendment(
        gap="gap", current_behavior="cur", proposed_change="prop", tier="medium",
    )
    md = Path(d.draft_path).read_text()
    assert "Audience:" in md
    assert "Research basis:" in md
    assert "Synthesis:" in md
    assert "Purpose:" in md


def test_tier_affects_template(tmp_path):
    gen = AmendmentDraftGenerator(
        reports_dir=tmp_path / "reports" / "cto",
        cieu_log_path=tmp_path / "logs" / "amendments.jsonl",
    )
    low = gen.propose_amendment(
        gap="g", current_behavior="c", proposed_change="p", tier="low",
    )
    high = gen.propose_amendment(
        gap="g", current_behavior="c", proposed_change="p", tier="high",
    )
    low_md = Path(low.draft_path).read_text()
    high_md = Path(high.draft_path).read_text()
    assert "Board必审" in high_md or "48h cooldown" in high_md
    assert "24h Board silence" in low_md or "lightweight" in low_md


def test_cieu_event_emitted(tmp_path):
    cieu_log = tmp_path / "logs" / "amendments.jsonl"
    gen = AmendmentDraftGenerator(
        reports_dir=tmp_path / "reports" / "cto",
        cieu_log_path=cieu_log,
    )
    d = gen.propose_amendment(
        gap="gap", current_behavior="cur", proposed_change="prop", tier="medium",
        title="test title",
    )
    assert cieu_log.exists()
    lines = cieu_log.read_text().strip().split("\n")
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["event_type"] == "SELF_MOD_PROPOSAL"
    assert event["tier"] == "medium"
    assert event["title"] == "test title"
    assert event["amendment_id"] == d.amendment_id


def test_invalid_tier_raises(tmp_path):
    gen = AmendmentDraftGenerator(
        reports_dir=tmp_path / "reports" / "cto",
        cieu_log_path=tmp_path / "logs" / "amendments.jsonl",
    )
    with pytest.raises(ValueError):
        gen.propose_amendment(
            gap="g", current_behavior="c", proposed_change="p", tier="critical",
        )


def test_multiple_proposals_accumulate_in_jsonl(tmp_path):
    cieu_log = tmp_path / "logs" / "amendments.jsonl"
    gen = AmendmentDraftGenerator(
        reports_dir=tmp_path / "reports" / "cto",
        cieu_log_path=cieu_log,
    )
    for i in range(3):
        gen.propose_amendment(
            gap=f"gap{i}", current_behavior=f"cur{i}",
            proposed_change=f"prop{i}", tier="low",
        )
    lines = cieu_log.read_text().strip().split("\n")
    assert len(lines) == 3


def test_tier_descriptions_complete():
    """All 3 tiers must have risk/examples/approval/required_evidence fields."""
    for tier in ["low", "medium", "high"]:
        info = TIER_DESCRIPTIONS[tier]
        assert "risk" in info
        assert "examples" in info
        assert "approval" in info
        assert "required_evidence" in info
