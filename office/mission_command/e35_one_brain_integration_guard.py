from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_artifact(name: str) -> dict[str, Any]:
    external = repo_root() / "operations" / "external_validation" / f"{name}.json"
    if external.exists():
        return deepcopy(json.loads(external.read_text(encoding="utf-8")))
    kg = repo_root() / "operations" / "knowledge_graph" / f"{name}.json"
    if kg.exists():
        return deepcopy(json.loads(kg.read_text(encoding="utf-8")))
    raise KeyError(name)


def build_one_brain_integration_guard() -> dict[str, Any]:
    return get_artifact("e35_one_brain_integration_guard")
