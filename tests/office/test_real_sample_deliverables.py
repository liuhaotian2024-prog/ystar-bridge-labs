from pathlib import Path

from office.mission_command.e3_cycle import build_e3_cycle


ROOT = Path(__file__).resolve().parents[2]


def test_sample_deliverable_top1_has_actual_findings():
    cycle = build_e3_cycle(ROOT)
    sample = cycle["sample_deliverables"][0]
    assert len(sample["diagnostic_findings"]) >= 3
    assert sample["owner_approval_needed_before_external_use"] is True
    assert sample["external_action_executed"] is False


def test_sample_deliverable_top2_has_actual_findings():
    cycle = build_e3_cycle(ROOT)
    sample = cycle["sample_deliverables"][1]
    assert len(sample["diagnostic_findings"]) >= 3
    assert "implementation" in sample["what_is_excluded"]
