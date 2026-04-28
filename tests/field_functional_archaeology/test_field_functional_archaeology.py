from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "field_functional_archaeology"
GENERATED = PACK / "generated"
BUILDER = PACK / "tools" / "build_field_functional_archaeology.py"

JSON_OUTPUTS = [
    "search_manifest.json",
    "field_functional_asset_inventory.json",
    "field_functional_concept_map.json",
    "old_to_new_architecture_alignment.json",
    "merge_decision_matrix.json",
    "reuse_candidates.json",
    "rewrite_candidates.json",
    "do_not_absorb_candidates.json",
    "mission_projection_merge_plan.json",
    "field_functional_archaeology_summary.json",
]

FORBIDDEN_CONTENT_FIELDS = {
    "full_source",
    "source_content",
    "file_content",
    "raw_content",
    "full_text",
}


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


@pytest.fixture(scope="module", autouse=True)
def generated_archaeology() -> None:
    run_builder()


def load_json(name: str) -> Any:
    path = GENERATED / name
    assert path.exists(), f"missing generated file: {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def walk_json(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def test_generated_json_outputs_are_valid() -> None:
    for name in JSON_OUTPUTS:
        load_json(name)


def test_required_archaeology_outputs_exist() -> None:
    assert load_json("search_manifest.json")["schema_name"].endswith("search_manifest")
    assert load_json("field_functional_asset_inventory.json")["asset_count"] > 0
    assert load_json("field_functional_concept_map.json")["concepts"]
    assert load_json("old_to_new_architecture_alignment.json")["mappings"]
    assert load_json("merge_decision_matrix.json")["decisions"]
    assert load_json("mission_projection_merge_plan.json")["proposed_L5_projection_modules"]
    assert load_json("field_functional_archaeology_summary.json")["field_functional_archaeology_defined"] is True


def test_inventory_uses_bounded_snippets_and_exact_merge_decisions() -> None:
    inventory = load_json("field_functional_asset_inventory.json")
    allowed_decisions = {
        "reuse_directly",
        "wrap_before_reuse",
        "rewrite_from_design",
        "preserve_as_concept_reference",
        "do_not_absorb",
    }

    assert inventory["asset_count"] == len(inventory["assets"])
    for asset in inventory["assets"]:
        assert len(asset["bounded_snippet"]) <= 240
        assert asset["merge_decision"] in allowed_decisions
        assert asset["live_enabled"] is False
        assert 0 <= asset["mission_value_score"] <= 5
        assert 0 <= asset["evidence_strength_score"] <= 5
        assert 0 <= asset["implementation_readiness_score"] <= 5
        assert 0 <= asset["architecture_alignment_score"] <= 5
        assert 0 <= asset["safety_risk_score"] <= 5


def test_no_full_source_or_raw_content_fields_are_generated() -> None:
    for name in JSON_OUTPUTS:
        payload = load_json(name)
        for node in walk_json(payload):
            assert not (set(node) & FORBIDDEN_CONTENT_FIELDS), f"{name} includes forbidden content field"


def test_summary_and_plan_remain_disabled_and_ready_for_l5_1() -> None:
    summary = load_json("field_functional_archaeology_summary.json")
    plan = load_json("mission_projection_merge_plan.json")
    matrix = load_json("merge_decision_matrix.json")

    assert summary["old_field_functional_work_found"] is True
    assert summary["mission_projection_merge_plan_defined"] is True
    assert summary["ready_for_L5_projection_harness"] is True
    assert summary["next_required_milestone"] == "L5.1 Mission Field Functional Projection Harness v0"
    assert summary["reuse_candidates_count"] == matrix["decisions"]["reuse_directly"]["count"]
    assert summary["wrap_candidates_count"] == matrix["decisions"]["wrap_before_reuse"]["count"]
    assert summary["rewrite_candidates_count"] == matrix["decisions"]["rewrite_from_design"]["count"]
    assert summary["concept_reference_count"] == matrix["decisions"]["preserve_as_concept_reference"]["count"]
    assert summary["do_not_absorb_count"] == matrix["decisions"]["do_not_absorb"]["count"]
    assert plan["live_enabled"] is False

    disabled = [
        "live_action_enabled",
        "external_action_enabled",
        "network_enabled",
        "cieu_persistence_enabled",
        "brain_writeback_enabled",
        "memory_ingestion_enabled",
    ]
    for field in disabled:
        assert summary[field] is False


def test_archaeology_found_expected_old_field_functional_evidence() -> None:
    assets = load_json("field_functional_asset_inventory.json")["assets"]
    paths = {asset["relative_path"] for asset in assets}

    assert "reports/kernel/field_functional_audit_20260423.md" in paths
    assert "reports/ceo/strategic/Y_STAR_FIELD_THEORY_SPEC.md" in paths
    assert "knowledge/ceo/wisdom/meta/field_vs_structure_duality.md" in paths
    assert "scripts/hook_session_start.py" in paths
    assert "scripts/phase2_role_scope_seed.py" in paths
    assert "ystar/governance/y_star_field_validator.py" in paths


def test_builder_source_is_static_and_non_runtime() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "import sqlite3" not in source
    assert "subprocess.run" not in source
    assert "requests." not in source
    assert "urllib.request" not in source
    assert "scripts/.logs" not in source
    assert ".db-wal" not in source
    assert ".db-shm" not in source
