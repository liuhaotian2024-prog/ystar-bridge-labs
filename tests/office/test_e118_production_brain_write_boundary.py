from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from office.mission_command.e116_aiden_idle_continuous_learning_runtime import BRAIN_DB
from office.mission_command.e118_production_brain_write_boundary import (
    create_verified_brain_backup,
    run_e118_production_brain_write_boundary_session,
)


YSTAR_ROOT = Path(os.environ.get("E118_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
pytestmark = pytest.mark.skipif(not BRAIN_DB.exists(), reason="E118 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_e118_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_e118_production_write_without_owner_approval_escalates_and_does_not_write(tmp_path):
    brain = _brain_copy(tmp_path)
    result = run_e118_production_brain_write_boundary_session(
        cieu_db=tmp_path / "e118_escalate.db",
        brain_db=brain,
        ystar_gov_root=YSTAR_ROOT,
        owner_explicit_production_write_approval=False,
        create_backup=False,
        force_production_target=True,
        seal_session=False,
    )

    decision = result["YstarGov_production_brain_write_boundary_result"]["governance_decision"]
    assert decision["decision"] == "ESCALATE"
    assert decision["requires_owner_decision"] is True
    assert result["brain_write_result"]["brain_write_performed"] is False
    assert result["production_boundary_proven"] is True


def test_e118_owner_approved_write_requires_verified_backup(tmp_path):
    brain = _brain_copy(tmp_path)
    result = run_e118_production_brain_write_boundary_session(
        cieu_db=tmp_path / "e118_missing_backup.db",
        brain_db=brain,
        ystar_gov_root=YSTAR_ROOT,
        owner_explicit_production_write_approval=True,
        create_backup=False,
        force_production_target=True,
        seal_session=False,
    )

    decision = result["YstarGov_production_brain_write_boundary_result"]["governance_decision"]
    assert decision["decision"] == "REQUIRE_REVISION"
    assert result["brain_write_result"]["brain_write_performed"] is False


def test_e118_verified_backup_allows_test_brain_write(tmp_path):
    brain = _brain_copy(tmp_path)
    result = run_e118_production_brain_write_boundary_session(
        cieu_db=tmp_path / "e118_allow.db",
        brain_db=brain,
        ystar_gov_root=YSTAR_ROOT,
        owner_explicit_production_write_approval=True,
        create_backup=True,
        backup_dir=tmp_path / "backups",
        force_production_target=True,
        seal_session=False,
    )

    decision = result["YstarGov_production_brain_write_boundary_result"]["governance_decision"]
    assert decision["decision"] == "ALLOW"
    assert result["backup_metadata"]["backup_verified"] is True
    assert Path(result["backup_metadata"]["pre_write_backup_path"]).exists()
    assert result["brain_write_result"]["brain_write_performed"] is True
    assert result["brain_write_result"]["node_delta"] >= 1


def test_e118_backup_hash_matches_source(tmp_path):
    brain = _brain_copy(tmp_path)
    backup = create_verified_brain_backup(source_brain_db=brain, backup_dir=tmp_path / "backups")

    assert backup["backup_verified"] is True
    assert backup["pre_write_backup_sha256"] == backup["pre_write_brain_db_sha256"]
    assert Path(backup["pre_write_backup_path"]).exists()
