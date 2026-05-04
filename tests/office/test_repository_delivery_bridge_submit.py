from __future__ import annotations

import json
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_schema import build_job
from repository_delivery_bridge_submit import submit_job


def test_submit_writes_pending_job(tmp_path: Path) -> None:
    payload_root = tmp_path / "payload"
    payload_root.mkdir()
    (payload_root / "x.txt").write_text("x\n")
    payload = tmp_path / "payload.tar.gz"
    with tarfile.open(payload, "w:gz") as tar:
        tar.add(payload_root / "x.txt", arcname="x.txt")
    job = build_job(
        job_id="submit_ok",
        repo_path="/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
        expected_branch="backflow/aiden-ceo-meeting-room",
        expected_base_head="abc",
        payload_path=str(payload),
        allowed_files=["x.txt"],
        validation_commands=[],
        commit_message="test",
        push_branch="backflow/aiden-ceo-meeting-room",
    )
    path = submit_job(job, bridge_root=tmp_path / "bridge")
    assert path.exists()
    assert json.loads(path.read_text())["job_id"] == "submit_ok"

