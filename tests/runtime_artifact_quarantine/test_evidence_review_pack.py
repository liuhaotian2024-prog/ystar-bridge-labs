from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_BUILDER = ROOT / "runtime_artifact_quarantine" / "tools" / "build_runtime_artifact_manifest.py"
CANDIDATE_BUILDER = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "tools" / "build_markdown_report_candidates.py"
QUEUE_BUILDER = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "review_queue" / "tools" / "build_candidate_review_queue.py"
DISPOSITION_BUILDER = ROOT / "runtime_artifact_quarantine" / "backlog_disposition" / "tools" / "build_artifact_disposition_index.py"
EVIDENCE_BUILDER = ROOT / "runtime_artifact_quarantine" / "evidence_review" / "tools" / "build_evidence_review_pack.py"

REVIEW_QUEUE = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "review_queue" / "generated" / "candidate_review_queue.json"
EVIDENCE_SCORES = ROOT / "runtime_artifact_quarantine" / "evidence_review" / "generated" / "evidence_scores.json"
DECISIONS = ROOT / "runtime_artifact_quarantine" / "evidence_review" / "generated" / "review_decision_stub.json"
ROUTES = ROOT / "runtime_artifact_quarantine" / "evidence_review" / "generated" / "hint_routing_index.json"
MANIFEST = ROOT / "runtime_artifact_quarantine" / "evidence_review" / "generated" / "evidence_review_manifest.json"

FORBIDDEN_CONTENT_MARKERS = [
    "sqlite format 3",
    "begin transaction",
    "scripts/.logs/",
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


def test_evidence_review_pack_is_structural_and_not_approved() -> None:
    run_script(MANIFEST_BUILDER)
    run_script(CANDIDATE_BUILDER)
    run_script(QUEUE_BUILDER)
    run_script(DISPOSITION_BUILDER)
    run_script(EVIDENCE_BUILDER)

    review_queue = load_json(REVIEW_QUEUE)
    evidence = load_json(EVIDENCE_SCORES)
    decisions = load_json(DECISIONS)
    routes = load_json(ROUTES)
    manifest = load_json(MANIFEST)

    assert evidence["summary"]["candidates_scored"] == review_queue["review_count"]
    assert decisions["decision_stubs_created"] == review_queue["review_count"]
    assert manifest["summary"]["automatic_approvals"] == 0

    decision_by_review = {decision["review_id"]: decision for decision in decisions["decisions"]}
    assert set(decision_by_review) == {entry["review_id"] for entry in review_queue["entries"]}

    for record in evidence["records"]:
        assert record["semantic_truth_status"] == "not_evaluated"
        assert record["contradiction_status"] == "not_checked"
        assert record["confidence_level"] != "high"
        assert record["brain_writeback_allowed"] is False
        assert record["memory_ingestion_allowed"] is False
        assert record["cieu_write_allowed"] is False

    for decision in decisions["decisions"]:
        assert decision["decision_status"] == "undecided"
        assert decision["decision"] == "none"
        assert decision["approved_use_scope"] == []
        assert decision["brain_writeback_allowed"] is False
        assert decision["memory_ingestion_allowed"] is False
        assert decision["cieu_write_allowed"] is False

    for route in routes["routes"]:
        assert route["status"] == "not_approved"
        assert route["ingestion_status"] == "not_ingested"
        assert route["forbidden_next_step"] == "direct_brain_writeback"

    source = EVIDENCE_BUILDER.read_text(encoding="utf-8")
    assert "CANDIDATE_INDEX_REF" in source
    assert "REVIEW_QUEUE_REF" in source
    assert "DISPOSITION_INDEX_REF" in source
    assert "reports/ceo/brain_dream_diffs" not in source
    assert "scripts/.logs" not in source

    rendered = json.dumps({"evidence": evidence, "decisions": decisions, "routes": routes}).lower()
    for marker in FORBIDDEN_CONTENT_MARKERS:
        assert marker not in rendered
