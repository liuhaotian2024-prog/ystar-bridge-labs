import json
from pathlib import Path

from office.mission_command.global_capability_registry import get_adapter_path, get_canonical_owner, load_capability_registry


ROOT = Path(__file__).resolve().parents[2]


def test_capability_registry_has_cluster_ids_and_canonical_owners_if_registry_needed():
    registry = load_capability_registry(ROOT)
    ids = {entry["cluster_id"] for entry in registry["entries"]}
    assert "cluster_target_lifecycle" in ids
    assert "cluster_action_authorization_chain" in ids
    assert get_canonical_owner(registry, "cluster_action_authorization_chain")
    assert get_adapter_path(registry, "cluster_target_lifecycle").endswith("target_lifecycle_router")


def test_capability_registry_file_is_machine_readable():
    path = ROOT / "governance" / "runtime_capability_registry.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["registry_id"] == "e11_global_runtime_capability_registry"
    assert len(payload["entries"]) >= 6

