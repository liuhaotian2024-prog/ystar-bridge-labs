from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_json_artifact(name: str) -> dict[str, Any]:
    path = repo_root() / "operations" / "external_validation" / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def read_kg_json_artifact(name: str) -> dict[str, Any]:
    path = repo_root() / "operations" / "knowledge_graph" / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def get_artifact(name: str) -> dict[str, Any]:
    external = repo_root() / "operations" / "external_validation" / f"{name}.json"
    if external.exists():
        return deepcopy(json.loads(external.read_text(encoding="utf-8")))
    kg = repo_root() / "operations" / "knowledge_graph" / f"{name}.json"
    if kg.exists():
        return deepcopy(json.loads(kg.read_text(encoding="utf-8")))
    raise KeyError(name)


def build_agent_action_black_box_demo_record() -> dict[str, Any]:
    return get_artifact("e33_agent_action_black_box_demo_record")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def write_all_artifacts(root: Path | None = None) -> None:
    root = root or repo_root()
    for name in [
        "e33_input_artifact_manifest",
        "e33_no_rebuild_alignment_gate",
        "e33_agent_action_black_box_schema",
        "e33_agent_action_black_box_demo_record",
        "e33_agent_action_black_box_demo_packet",
        "e33_black_box_buyer_view",
        "e33_black_box_no_fake_evidence_audit",
        "e33_owner_validation_route",
        "e33_ceo_brain_black_box_update",
        "e33_czl_closure",
    ]:
        write_json(root / "operations" / "external_validation" / f"{name}.json", get_artifact(name))
    for name in [
        "e33_ceo_kg_black_box_feedback",
        "e33_ceo_kg_read_model_update",
    ]:
        write_json(root / "operations" / "knowledge_graph" / f"{name}.json", get_artifact(name))
