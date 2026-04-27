from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "tools" / "build_markdown_report_candidates.py"
CANDIDATES = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "generated" / "markdown_report_candidates.json"
MINING_MANIFEST = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "generated" / "mining_manifest.json"

ALLOWED_CLASSES = {
    "DREAM_REPORT",
    "DAILY_REPORT",
    "DRIFT_REPORT",
    "ESCALATION_REPORT",
    "WHITELIST_REPORT",
}
FORBIDDEN_MARKERS = [
    ".db",
    ".db-wal",
    ".db-shm",
    ".wal",
    ".shm",
    "scripts/.logs",
    "active_agent",
    "__pycache__",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_markdown_report_candidate_builder_outputs_bounded_candidate_index() -> None:
    result = subprocess.run(
        ["python3", str(BUILDER.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert CANDIDATES.exists()
    assert MINING_MANIFEST.exists()

    data = load_json(CANDIDATES)
    mining_manifest = load_json(MINING_MANIFEST)

    assert data["ingestion_status"] == "candidate_only"
    assert data["forbidden_next_step"] == "direct_brain_writeback"
    assert data["allowed_next_step"] == "human_review_or_curated_queue"
    assert set(data["classes_seen"]).issubset(ALLOWED_CLASSES)
    assert mining_manifest["files_selected"] == data["candidate_count"]

    bounds = data["bounds"]
    for candidate in data["candidates"]:
        assert candidate["artifact_class"] in ALLOWED_CLASSES
        assert candidate["ingestion_status"] == "candidate_only"
        assert candidate["forbidden_next_step"] == "direct_brain_writeback"
        assert len(candidate["snippet"]) <= bounds["max_chars_per_file"]
        assert len(candidate["snippet"].splitlines()) <= bounds["max_lines_per_file"]

    rendered = json.dumps(data).lower()
    for marker in FORBIDDEN_MARKERS:
        assert marker not in rendered
