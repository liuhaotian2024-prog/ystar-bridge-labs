from __future__ import annotations

import subprocess
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_schema import build_job
from repository_delivery_bridge_worker import (
    cleanup_generated_files,
    cleanup_transient_dirty_paths,
    is_transient_generated_path,
    process_job,
)


def test_cleanup_removes_transient_generated_files_without_touching_git_or_sources(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    (repo / "module.py").write_text("x = 1\n")
    nested_pycache_dirs = [
        "__pycache__",
        "gov_mcp/__pycache__",
        "scripts/__pycache__",
        "scripts/tests/__pycache__",
        "tests/__pycache__",
        "tests/governance/__pycache__",
        "tests/hook/__pycache__",
        "tests/kernel/__pycache__",
    ]
    for rel in nested_pycache_dirs:
        cache = repo / rel
        cache.mkdir(parents=True)
        (cache / "module.pyc").write_bytes(b"pyc")
    exact_dirty_examples = [
        "gov_mcp/__pycache__/__init__.cpython-311.pyc",
        "gov_mcp/__pycache__/__main__.cpython-311.pyc",
        "scripts/__pycache__/_cieu_helpers.cpython-311.pyc",
        "scripts/tests/__pycache__/test_x.cpython-311-pytest.pyc",
        "tests/__pycache__/conftest.cpython-311-pytest.pyc",
        "tests/governance/__pycache__/test_y.pyc",
        "tests/hook/__pycache__/test_z.pyc",
        "tests/kernel/__pycache__/test_k.pyc",
    ]
    for rel in exact_dirty_examples:
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"pyc")
    (repo / ".pytest_cache").mkdir()
    (repo / ".pytest_cache" / "v" / "cache").mkdir(parents=True)
    (repo / ".pytest_cache" / "v" / "cache" / "nodeids").write_text("cache")
    (repo / ".mypy_cache").mkdir()
    (repo / ".ruff_cache").mkdir()
    (repo / "nested" / "a" / "b" / ".ruff_cache").mkdir(parents=True)
    (repo / "nested" / "a" / "b" / ".ruff_cache" / "file").write_text("cache")
    (repo / "nested" / "a" / "b" / ".mypy_cache").mkdir(parents=True)
    (repo / "nested" / "a" / "b" / ".mypy_cache" / "file").write_text("cache")
    (repo / ".DS_Store").write_text("ds")
    (repo / "x").mkdir()
    (repo / "x" / "._foo.py").write_text("apple")
    (repo / "__MACOSX").mkdir()
    (repo / "__MACOSX" / "foo").write_text("apple")
    (repo / ".env").write_text("TOKEN=secret\n")
    (repo / "credentials.json").write_text("{}\n")
    (repo / "secrets.json").write_text("{}\n")
    (repo / ".git" / "objects" / "keep.pyc").write_bytes(b"do-not-touch")
    removed = cleanup_generated_files(repo)
    assert "module.py" not in removed
    assert (repo / "module.py").exists()
    assert (repo / ".git").exists()
    assert (repo / ".git" / "objects" / "keep.pyc").exists()
    for rel in nested_pycache_dirs:
        assert not (repo / rel).exists(), rel
    for rel in exact_dirty_examples:
        assert not (repo / rel).exists(), rel
    assert not (repo / ".pytest_cache").exists()
    assert not (repo / "nested" / "a" / "b" / ".ruff_cache").exists()
    assert not (repo / "nested" / "a" / "b" / ".mypy_cache").exists()
    assert not (repo / ".DS_Store").exists()
    assert not (repo / "x" / "._foo.py").exists()
    assert not (repo / "__MACOSX").exists()
    assert (repo / ".env").exists()
    assert (repo / "credentials.json").exists()
    assert (repo / "secrets.json").exists()


def test_worker_cleans_pycache_created_by_validation_before_dirty_set(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "README.md").write_text("initial\n")
    (repo / "make_cache.py").write_text("import pathlib\npathlib.Path('__pycache__').mkdir(exist_ok=True)\npathlib.Path('__pycache__/x.pyc').write_bytes(b'x')\n")
    subprocess.run(["git", "add", "README.md", "make_cache.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True, check=True).stdout.strip()
    branch = subprocess.run(["git", "branch", "--show-current"], cwd=repo, text=True, capture_output=True, check=True).stdout.strip()
    source = tmp_path / "source"
    source.mkdir()
    (source / "safe.txt").write_text("safe\n")
    payload = tmp_path / "payload.tar.gz"
    with tarfile.open(payload, "w:gz") as tar:
        tar.add(source / "safe.txt", arcname="safe.txt")
    (repo / "__pycache__").mkdir()
    (repo / "__pycache__" / "x.pyc").write_bytes(b"x")
    job = build_job(
        job_id="cleanup_validation",
        repo_path=str(repo),
        expected_branch=branch,
        expected_base_head=head,
        payload_path=str(payload),
        allowed_files=["safe.txt"],
        validation_commands=["python3.11 -m py_compile make_cache.py"],
        commit_message="test",
        push_branch=branch,
    )
    job["allow_temp_repo_for_smoke_test"] = True
    report = process_job(job, push=False)
    assert report["status"] == "DRY_RUN_COMPLETED"
    assert report["cleanup_before"]
    assert "cleanup_after_validation" in report
    assert "cleanup_before_dirty_validation" in report
    assert report["cleanup_after_validation"]
    assert not (repo / "__pycache__").exists()


def test_transient_classifier_only_covers_generated_paths() -> None:
    assert is_transient_generated_path("gov_mcp/__pycache__/__init__.cpython-311.pyc")
    assert is_transient_generated_path("forbidden_dirty:tests/kernel/__pycache__/test_k.pyc")
    assert is_transient_generated_path("nested/a/b/.ruff_cache/file")
    assert is_transient_generated_path("x/._foo.py")
    assert not is_transient_generated_path(".env")
    assert not is_transient_generated_path("credentials.json")
    assert not is_transient_generated_path("state.db")


def test_cleanup_transient_dirty_paths_handles_forbidden_dirty_prefixes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    dirty_files = [
        "gov_mcp/__pycache__/__init__.cpython-311.pyc",
        "gov_mcp/__pycache__/__main__.cpython-311.pyc",
        "scripts/__pycache__/_cieu_helpers.cpython-311.pyc",
        "scripts/tests/__pycache__/test_aiden_cluster_daemon.cpython-311-pytest-9.0.2.pyc",
        "tests/__pycache__/conftest.cpython-311-pytest-9.0.2.pyc",
        "tests/governance/__pycache__/test_dream_manual_gate.cpython-311-pytest-9.0.2.pyc",
        "tests/hook/__pycache__/test_brain_writeback_wiring.cpython-311-pytest-9.0.2.pyc",
        "tests/kernel/__pycache__/test_brain_writeback_semantic.cpython-311-pytest-9.0.2.pyc",
    ]
    source_files = [
        "gov_mcp/__init__.py",
        "scripts/_cieu_helpers.py",
        "tests/conftest.py",
        "tests/governance/test_dream_manual_gate.py",
    ]
    for rel in dirty_files + source_files:
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith(".pyc"):
            path.write_bytes(b"pyc")
        else:
            path.write_text("# source\n")
    (repo / ".git" / "objects" / "__pycache__").mkdir(parents=True)
    (repo / ".git" / "objects" / "__pycache__" / "keep.pyc").write_bytes(b"keep")
    (repo / ".env").write_text("TOKEN=secret\n")
    (repo / "credentials.json").write_text("{}\n")
    (repo / "secrets.json").write_text("{}\n")

    removed = cleanup_transient_dirty_paths(repo, [f"forbidden_dirty:{path}" for path in dirty_files])
    assert removed
    for rel in dirty_files:
        assert not (repo / rel).exists(), rel
    for cache_dir in [
        "gov_mcp/__pycache__",
        "scripts/__pycache__",
        "scripts/tests/__pycache__",
        "tests/__pycache__",
        "tests/governance/__pycache__",
        "tests/hook/__pycache__",
        "tests/kernel/__pycache__",
    ]:
        assert not (repo / cache_dir).exists(), cache_dir
    for rel in source_files:
        assert (repo / rel).exists(), rel
    assert (repo / ".git" / "objects" / "__pycache__" / "keep.pyc").exists()
    assert (repo / ".env").exists()
    assert (repo / "credentials.json").exists()
    assert (repo / "secrets.json").exists()


def test_cleanup_transient_dirty_paths_rejects_absolute_traversal_git_and_persistent_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    for rel in [".env", "credentials.json", "secrets.json", "safe.py"]:
        (repo / rel).write_text("x\n")
    removed = cleanup_transient_dirty_paths(
        repo,
        [
            "/tmp/outside/__pycache__/x.pyc",
            "../repo/__pycache__/x.pyc",
            ".git/objects/__pycache__/x.pyc",
            ".env",
            "credentials.json",
            "secrets.json",
        ],
    )
    assert removed == []
    assert (repo / ".env").exists()
    assert (repo / "credentials.json").exists()
    assert (repo / "secrets.json").exists()
    assert (repo / "safe.py").exists()
