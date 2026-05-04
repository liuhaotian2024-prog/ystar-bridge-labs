from __future__ import annotations

import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_schema import build_job, is_forbidden_path, payload_manifest_allowed_files, validate_job


def make_payload(tmp_path: Path) -> Path:
    source = tmp_path / "payload"
    source.mkdir()
    (source / "x.txt").write_text("x\n")
    payload = tmp_path / "payload.tar.gz"
    with tarfile.open(payload, "w:gz") as tar:
        tar.add(source / "x.txt", arcname="x.txt")
    return payload


def test_valid_job_is_accepted(tmp_path: Path) -> None:
    payload = make_payload(tmp_path)
    job = build_job(
        job_id="ok",
        repo_path="/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
        expected_branch="backflow/aiden-ceo-meeting-room",
        expected_base_head="abc",
        payload_path=str(payload),
        allowed_files=["x.txt"],
        validation_commands=["pytest tests/office/test_x.py -q"],
        commit_message="test: x",
        push_branch="backflow/aiden-ceo-meeting-room",
    )
    assert validate_job(job).ok


def test_force_push_and_remote_mutation_are_rejected(tmp_path: Path) -> None:
    payload = make_payload(tmp_path)
    job = build_job(
        job_id="bad",
        repo_path="/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
        expected_branch="x",
        expected_base_head="abc",
        payload_path=str(payload),
        allowed_files=["x.txt"],
        validation_commands=[],
        commit_message="test",
        push_branch="x",
    )
    job["no_force_push"] = False
    job["no_remote_url_mutation"] = False
    validation = validate_job(job)
    assert not validation.ok
    assert "force_push_not_allowed" in validation.errors
    assert "remote_url_mutation_not_allowed" in validation.errors


def test_credential_safety_test_filename_is_allowed() -> None:
    assert not is_forbidden_path("tests/office/test_repository_delivery_bridge_sanitizes_credentials.py")


def test_real_secret_bearing_paths_are_rejected() -> None:
    forbidden = [
        ".env",
        ".env.local",
        "secrets.json",
        "credentials.json",
        "config/credentials.json",
        ".ssh/id_rsa",
        "keys/private.pem",
        "config/api_token.json",
    ]
    for path in forbidden:
        assert is_forbidden_path(path), path


def test_job_allows_credential_redaction_test_but_rejects_real_credentials_json(tmp_path: Path) -> None:
    payload = make_payload(tmp_path)
    job = build_job(
        job_id="safe_credential_test",
        repo_path="/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
        expected_branch="backflow/aiden-ceo-meeting-room",
        expected_base_head="abc",
        payload_path=str(payload),
        allowed_files=["tests/office/test_repository_delivery_bridge_sanitizes_credentials.py"],
        validation_commands=[],
        commit_message="test",
        push_branch="backflow/aiden-ceo-meeting-room",
    )
    assert validate_job(job).ok

    bad = dict(job)
    bad["allowed_files"] = ["config/credentials.json"]
    validation = validate_job(bad)
    assert not validation.ok
    assert "forbidden_allowed_file:config/credentials.json" in validation.errors


def test_payload_manifest_allowed_files_includes_all_new_bridge_tests_and_skips_transients(tmp_path: Path) -> None:
    payload = tmp_path / "bridge_payload.tar.gz"
    files = [
        "tests/office/test_repository_delivery_bridge_clean_generated_files.py",
        "tests/office/test_repository_delivery_bridge_install_semantics.py",
        "tests/office/test_repository_delivery_bridge_rejects_persistent_unsafe_files.py",
        "scripts/repository_delivery_bridge_worker.py",
        "tests/__pycache__/x.pyc",
        ".DS_Store",
        "__MACOSX/._junk",
    ]
    with tarfile.open(payload, "w:gz") as tar:
        for rel in files:
            source = tmp_path / rel
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("x\n")
            tar.add(source, arcname=rel)
    allowed = payload_manifest_allowed_files(payload)
    assert "tests/office/test_repository_delivery_bridge_clean_generated_files.py" in allowed
    assert "tests/office/test_repository_delivery_bridge_install_semantics.py" in allowed
    assert "tests/office/test_repository_delivery_bridge_rejects_persistent_unsafe_files.py" in allowed
    assert "scripts/repository_delivery_bridge_worker.py" in allowed
    assert "tests/__pycache__/x.pyc" not in allowed
    assert ".DS_Store" not in allowed
    assert "__MACOSX/._junk" not in allowed
