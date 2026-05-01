from pathlib import Path

from office.mission_command.e4_cycle import build_e4_cycle


ROOT = Path(__file__).resolve().parents[2]


def test_sample_top1_has_four_concrete_findings():
    sample = build_e4_cycle(ROOT)["samples"][0]
    assert len(sample["diagnostic_findings"]) >= 4
    assert sample["alternatives"]["competitors"]
    assert sample["why_buyer_might_not_choose_us"]


def test_sample_top2_has_four_concrete_findings():
    sample = build_e4_cycle(ROOT)["samples"][1]
    assert len(sample["diagnostic_findings"]) >= 4
    assert sample["alternatives"]["substitutes"]


def test_sample_deliverables_require_owner_approval_before_external_use():
    for sample in build_e4_cycle(ROOT)["samples"]:
        assert sample["owner_approval_needed_before_external_use"] is True
        assert sample["external_action_executed"] is False
