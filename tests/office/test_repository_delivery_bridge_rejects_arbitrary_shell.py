from __future__ import annotations

import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_schema import build_job, validate_job


def test_arbitrary_shell_operator_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "x.txt").write_text("x\n")
    payload = tmp_path / "payload.tar.gz"
    with tarfile.open(payload, "w:gz") as tar:
        tar.add(source / "x.txt", arcname="x.txt")
    job = build_job(
        job_id="bad_shell",
        repo_path="/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
        expected_branch="x",
        expected_base_head="abc",
        payload_path=str(payload),
        allowed_files=["x.txt"],
        validation_commands=["pytest tests || rm -rf /"],
        commit_message="test",
        push_branch="x",
    )
    validation = validate_job(job)
    assert not validation.ok
    assert "arbitrary_shell_operator_blocked" in validation.errors

