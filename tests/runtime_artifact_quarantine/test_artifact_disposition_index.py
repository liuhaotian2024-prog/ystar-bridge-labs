from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_BUILDER = ROOT / "runtime_artifact_quarantine" / "tools" / "build_runtime_artifact_manifest.py"
CANDIDATE_BUILDER = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "tools" / "build_markdown_report_candidates.py"
QUEUE_BUILDER = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "review_queue" / "tools" / "build_candidate_review_queue.py"
DISPOSITION_BUILDER = ROOT / "runtime_artifact_quarantine" / "backlog_disposition" / "tools" / "build_artifact_disposition_index.py"
QUARANTINE_MANIFEST = ROOT / "runtime_artifact_quarantine" / "generated" / "runtime_artifact_manifest.json"
DISPOSITION_INDEX = ROOT / "runtime_artifact_quarantine" / "backlog_disposition" / "generated" / "artifact_disposition_index.json"
DISPOSITION_MANIFEST = ROOT / "runtime_artifact_quarantine" / "backlog_disposition" / "generated" / "disposition_manifest.json"

FORBIDDEN_DIRECT_READ_CLASSES = {
    "DB_CORE",
    "BACKUP_DB",
    "DB_SIDECARE",
    "LOG_RUNTIME",
    "ACTIVE_AGENT_MARKER",
    "DAEMON_STATE",
    "CACHE_SENTINEL",
    "PYCACHE",
    "UNKNOWN_RUNTIME_ARTIFACT",
}
FORBIDDEN_CONTENT_MARKERS = [
    "sqlite format 3",
    "begin transaction",
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


def test_artifact_disposition_index_covers_quarantine_backlog_safely() -> None:
    run_script(MANIFEST_BUILDER)
    run_script(CANDIDATE_BUILDER)
    run_script(QUEUE_BUILDER)
    run_script(DISPOSITION_BUILDER)

    assert DISPOSITION_INDEX.exists()
    assert DISPOSITION_MANIFEST.exists()

    quarantine = load_json(QUARANTINE_MANIFEST)
    disposition = load_json(DISPOSITION_INDEX)
    manifest = load_json(DISPOSITION_MANIFEST)
    records = disposition["records"]

    assert len(records) == len(quarantine["artifacts"])
    assert disposition["summary"]["total_artifacts"] == len(quarantine["artifacts"])
    assert disposition["summary"]["artifacts_with_disposition"] == len(quarantine["artifacts"])
    assert manifest["artifacts_with_disposition"] == len(quarantine["artifacts"])

    paths = {record["artifact_path"] for record in records}
    manifest_paths = {artifact["path"] for artifact in quarantine["artifacts"]}
    assert paths == manifest_paths

    for record in records:
        assert record["source_in_quarantine_manifest"] is True
        assert record["ingestion_status"] == "not_ingested"
        assert record["evidence_scoring_status"] == "not_started"
        assert record["brain_writeback_allowed"] is False
        assert record["memory_ingestion_allowed"] is False
        assert record["cieu_write_allowed"] is False
        assert "direct_brain_writeback" in record["forbidden_next_steps"]
        assert "direct_memory_ingestion" in record["forbidden_next_steps"]
        assert "direct_cieu_write" in record["forbidden_next_steps"]
        if record["artifact_class"] in FORBIDDEN_DIRECT_READ_CLASSES:
            assert record["direct_read_allowed"] is False
            assert record["forbidden_direct_read"] is True
        if record["review_id"]:
            assert record["review_status"] == "pending_review"

    source = DISPOSITION_BUILDER.read_text(encoding="utf-8")
    assert "with path.open" in source
    assert "QUARANTINE_MANIFEST_REF" in source
    assert "CANDIDATE_INDEX_REF" in source
    assert "REVIEW_QUEUE_REF" in source
    assert "reports/ceo/brain_dream_diffs" not in source
    assert "scripts/.logs" not in source

    rendered = json.dumps(disposition).lower()
    for marker in FORBIDDEN_CONTENT_MARKERS:
        assert marker not in rendered
