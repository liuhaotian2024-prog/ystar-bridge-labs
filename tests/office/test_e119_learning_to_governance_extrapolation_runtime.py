from __future__ import annotations

import os
from pathlib import Path

from office.mission_command.e119_learning_to_governance_extrapolation_runtime import (
    build_e119_self_governance_update_proposal,
    run_e119_learning_to_governance_extrapolation_session,
)


YSTAR_ROOT = Path(os.environ.get("E119_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def test_e119_proposal_contains_class_level_extrapolation():
    proposal = build_e119_self_governance_update_proposal()

    assert proposal["class_of_issue"]["issue_class_id"] == "point_fix_without_generalization"
    assert len(proposal["observed_point_failures"]) >= 2
    assert len(proposal["extrapolation_to_other_cases"]) >= 3
    assert proposal["proposed_contract_amendment"]["auto_apply"] is False
    assert proposal["truth_constraints"]["direct_contract_write_attempted"] is False


def test_e119_session_writes_cieu_and_pending_owner_proposal(tmp_path):
    result = run_e119_learning_to_governance_extrapolation_session(
        cieu_db=tmp_path / "e119.db",
        root=tmp_path,
        ystar_gov_root=YSTAR_ROOT,
        write_pending=True,
        seal_session=False,
    )

    decision = result["YstarGov_self_governance_proposal_result"]["governance_decision"]
    pattern_decision = result["Aiden_operating_pattern_result"]["governance_decision"]
    assert pattern_decision["decision"] == "ALLOW"
    assert decision["decision"] == "ALLOW"
    assert decision["requires_owner_decision"] is True
    assert result["self_governance_proposal_proven"] is True
    assert Path(result["pending_proposal_path"]).exists()
    assert result["truth_constraints"]["contract_patch_applied"] is False


def test_e119_session_can_validate_without_writing_pending_file(tmp_path):
    result = run_e119_learning_to_governance_extrapolation_session(
        cieu_db=tmp_path / "e119_no_pending.db",
        root=tmp_path,
        ystar_gov_root=YSTAR_ROOT,
        write_pending=False,
        seal_session=False,
    )

    assert result["YstarGov_self_governance_proposal_result"]["governance_decision"]["decision"] == "ALLOW"
    assert result["Aiden_operating_pattern_result"]["governance_decision"]["decision"] == "ALLOW"
    assert result["pending_proposal_path"] == ""
