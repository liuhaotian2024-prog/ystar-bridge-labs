from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "legacy_asset_triage" / "tools" / "build_legacy_asset_triage.py"
GENERATED = ROOT / "legacy_asset_triage" / "generated"

JSON_OUTPUTS = [
    "legacy_asset_triage_manifest.json",
    "asset_value_risk_matrix.json",
    "asset_absorption_buckets.json",
    "governed_absorption_backlog.json",
    "top_absorption_candidates.json",
    "retired_or_quarantined_assets.json",
    "legacy_asset_triage_summary.json",
]

ALLOWED_BUCKETS = {
    "A_adopt_now_read_only",
    "B_wrap_as_governed_tool",
    "C_rewrite_from_design",
    "D_quarantine_as_evidence_ore",
    "E_retire_do_not_use",
}

FORBIDDEN_STRINGS = [
    ".db",
    ".db-wal",
    ".db-shm",
    ".sqlite",
    ".sqlite3",
    "scripts/.logs",
    "active_agent",
]


def run_builder() -> None:
    result = subprocess.run(
        ["python3", str(BUILDER.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def load_json(name: str) -> dict:
    path = GENERATED / name
    assert path.exists(), f"missing generated file: {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_legacy_triage_outputs_and_summary() -> None:
    run_builder()

    for name in JSON_OUTPUTS:
        load_json(name)

    summary = load_json("legacy_asset_triage_summary.json")
    assert summary["legacy_asset_triage_defined"] is True
    assert summary["assets_scored"] > 0
    assert summary["absorption_buckets_defined"] is True
    assert summary["top_absorption_candidates_defined"] is True
    assert summary["governed_absorption_backlog_defined"] is True
    assert summary["blind_absorption_allowed"] is False
    assert summary["blanket_rewrite_allowed"] is False
    assert summary["live_actions_enabled"] is False
    assert summary["external_actions_enabled"] is False
    assert summary["brain_writeback_enabled"] is False
    assert summary["memory_ingestion_enabled"] is False
    assert summary["cieu_persistence_enabled"] is False
    assert summary["next_required_milestone"] == "L4.4 First Governed Read-Only Observation Tool Wrapper v0"


def test_assets_have_exactly_one_allowed_bucket() -> None:
    run_builder()

    matrix = load_json("asset_value_risk_matrix.json")
    buckets = load_json("asset_absorption_buckets.json")

    assert set(buckets["allowed_buckets"]) == ALLOWED_BUCKETS
    seen = set()
    for asset in matrix["assets"]:
        bucket = asset.get("absorption_bucket")
        assert bucket in ALLOWED_BUCKETS
        assert asset["asset_id"] not in seen
        seen.add(asset["asset_id"])
        assert asset["live_enabled"] is False

    bucket_members = []
    for bucket, members in buckets["buckets"].items():
        assert bucket in ALLOWED_BUCKETS
        for member in members:
            assert member["bucket"] == bucket
            assert member["live_enabled"] is False
            bucket_members.append(member["asset_id"])

    assert sorted(bucket_members) == sorted(seen)


def test_candidates_and_backlog_are_disabled() -> None:
    run_builder()

    top = load_json("top_absorption_candidates.json")
    backlog = load_json("governed_absorption_backlog.json")
    retired = load_json("retired_or_quarantined_assets.json")

    assert 3 <= top["candidate_count"] <= 7
    for candidate in top["candidates"]:
        assert candidate["bucket"] in ALLOWED_BUCKETS
        assert candidate["live_enabled"] is False

    assert backlog["backlog_count"] >= 5
    for item in backlog["items"]:
        assert item["target_bucket"] in ALLOWED_BUCKETS
        assert item["live_enabled"] is False

    for asset in retired["assets"]:
        assert asset["bucket"] in {"D_quarantine_as_evidence_ore", "E_retire_do_not_use"}
        assert asset["live_enabled"] is False


def test_generated_outputs_avoid_forbidden_runtime_dependencies() -> None:
    run_builder()

    for path in GENERATED.iterdir():
        if path.suffix not in {".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for marker in FORBIDDEN_STRINGS:
            assert marker.lower() not in text, f"{marker} appeared in {path.name}"


def test_builder_source_is_non_runtime() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "import subprocess" not in source
    assert "import sqlite3" not in source
    assert "scripts/.logs" not in source
    assert ".db-wal" not in source
    assert ".db-shm" not in source
