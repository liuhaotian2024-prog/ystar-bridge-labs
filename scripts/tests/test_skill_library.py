"""Test: SkillLibrary — register + retrieve + bulk import."""
import os
import sys
import tempfile
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skill_library import SkillLibrary, bulk_import_from_scripts


def test_register_and_count(tmp_path):
    lib = SkillLibrary(db_path=tmp_path / "test.db")
    sid = lib.register_skill("run k9 patrol", "/scripts/k9_patrol.sh")
    assert sid > 0
    assert lib.count() == 1


def test_register_idempotent(tmp_path):
    lib = SkillLibrary(db_path=tmp_path / "test.db")
    lib.register_skill("foo", "/scripts/foo.py")
    lib.register_skill("foo2", "/scripts/foo.py")  # same path
    assert lib.count() == 1


def test_retrieve_by_token(tmp_path):
    lib = SkillLibrary(db_path=tmp_path / "test.db")
    lib.register_skill("run k9 patrol daily", "/scripts/k9.sh")
    lib.register_skill("commit push automation", "/scripts/auto_commit.py")
    results = lib.retrieve("k9 patrol", limit=3)
    assert len(results) >= 1
    assert any("k9" in r["trigger"].lower() for r in results)


def test_increment_success(tmp_path):
    lib = SkillLibrary(db_path=tmp_path / "test.db")
    sid = lib.register_skill("foo", "/scripts/foo.py")
    lib.increment_success(sid)
    row = lib.conn.execute(
        "SELECT success_count FROM skills WHERE skill_id=?", (sid,)
    ).fetchone()
    assert row[0] == 1


def test_bulk_import_from_real_scripts(tmp_path):
    lib = SkillLibrary(db_path=tmp_path / "test.db")
    scripts = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts")
    n = bulk_import_from_scripts(lib, scripts)
    assert n >= 20, f"expected >=20 skills imported, got {n}"
    assert lib.count() >= 20
