from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_BUILDER = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "tools" / "build_markdown_report_candidates.py"
QUEUE_BUILDER = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "review_queue" / "tools" / "build_candidate_review_queue.py"
CANDIDATES = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "generated" / "markdown_report_candidates.json"
QUEUE = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "review_queue" / "generated" / "candidate_review_queue.json"
QUEUE_MANIFEST = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "review_queue" / "generated" / "review_queue_manifest.json"

FORBIDDEN_ACTIONS = {
    "direct_brain_writeback",
    "direct_memory_ingestion",
    "direct_cieu_write",
    "runtime_recovery",
}
FORBIDDEN_MARKERS = [
    ".db",
    ".db-wal",
    ".db-shm",
    "scripts/.logs",
    "active_agent",
    "__pycache__",
]


def run_script(path: Path) -> None:
    result = subprocess.run(
        ["python3", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_candidate_review_queue_is_pending_and_not_ingested() -> None:
    run_script(CANDIDATE_BUILDER)
    run_script(QUEUE_BUILDER)

    assert QUEUE.exists()
    assert QUEUE_MANIFEST.exists()

    candidate_index = load_json(CANDIDATES)
    queue = load_json(QUEUE)
    manifest = load_json(QUEUE_MANIFEST)

    assert queue["review_count"] == candidate_index["candidate_count"]
    assert manifest["review_count"] == queue["review_count"]
    assert queue["default_review_status"] == "pending_review"
    assert queue["default_ingestion_status"] == "not_ingested"

    for entry in queue["entries"]:
        assert entry["review_status"] == "pending_review"
        assert entry["ingestion_status"] == "not_ingested"
        assert FORBIDDEN_ACTIONS.issubset(set(entry["forbidden_actions"]))
        assert "direct_brain_writeback" not in entry["allowed_review_actions"]
        assert "direct_memory_ingestion" not in entry["allowed_review_actions"]
        assert "direct_cieu_write" not in entry["allowed_review_actions"]
        assert entry["generated_from_candidate_index_ref"].endswith("markdown_report_candidates.json")

    source = QUEUE_BUILDER.read_text(encoding="utf-8")
    assert "bounded_read_markdown" not in source
    assert "SOURCE_MANIFEST" not in source
    assert "markdown_report_candidates.json" in source

    rendered = json.dumps(queue).lower()
    for marker in FORBIDDEN_MARKERS:
        assert marker not in rendered
