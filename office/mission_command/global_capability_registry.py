from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from .capability_clusterer import CapabilityCluster, discover_capability_clusters
from .capability_fingerprint_extractor import extract_capability_fingerprints
from .global_semantic_inventory import build_global_semantic_inventory


ROUTER_BY_CLUSTER = {
    "cluster_target_lifecycle": "office.mission_command.target_lifecycle_router",
    "cluster_evidence_signal_ladder": "office.mission_command.evidence_signal_router",
    "cluster_action_authorization_chain": "office.mission_command.action_authorization_router",
    "cluster_learning_writeback_gate": "office.mission_command.learning_writeback_router",
    "cluster_closure_status_semantics": "office.mission_command.closure_status_router",
    "cluster_counterfactual_protocol": "office.mission_command.counterfactual_router",
}


@dataclass(frozen=True)
class CapabilityRegistryEntry:
    cluster_id: str
    cluster_name: str
    relation_type: str
    conflict_risk: str
    canonical_owner: str
    adapter_owner: str
    router_module: str
    registry_role: str
    discovered_from_evidence: bool
    immediate_code_consolidation_safe: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _entry_from_cluster(cluster: CapabilityCluster) -> CapabilityRegistryEntry:
    router_module = ROUTER_BY_CLUSTER.get(cluster.cluster_id, "")
    if router_module:
        role = "canonical_router"
    elif cluster.duplication_harmful:
        role = "blocked_pending_router"
    else:
        role = "mapped_adapter_or_incubation_source"
    return CapabilityRegistryEntry(
        cluster_id=cluster.cluster_id,
        cluster_name=cluster.cluster_name,
        relation_type=cluster.relation_type,
        conflict_risk=cluster.conflict_risk,
        canonical_owner=cluster.canonical_owner_recommendation,
        adapter_owner="bridge-labs E-series modules remain adapters unless promoted by a future backflow.",
        router_module=router_module,
        registry_role=role,
        discovered_from_evidence=True,
        immediate_code_consolidation_safe=cluster.immediate_code_consolidation_safe,
    )


def build_capability_registry(repo_root: Path) -> Dict[str, Any]:
    inventory = build_global_semantic_inventory(repo_root)
    fingerprints = extract_capability_fingerprints(inventory)
    clusters = discover_capability_clusters(fingerprints)
    entries = [_entry_from_cluster(cluster) for cluster in clusters]
    return {
        "registry_id": "e11_global_runtime_capability_registry",
        "baseline_commit": "98fdfd7e08e7dc86dd7eed16edb69f6a2dd7e2e7",
        "discovery_source": [
            "reports/integration/e11_semantic_capability_inventory.json",
            "reports/integration/e11_capability_fingerprint_index.json",
            "reports/integration/e11_duplicate_overlap_cluster_report.md",
        ],
        "entries": [entry.to_dict() for entry in entries],
    }


def write_capability_registry(repo_root: Path, registry: Dict[str, Any] | None = None) -> Path:
    registry = registry or build_capability_registry(repo_root)
    path = repo_root / "governance" / "runtime_capability_registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_capability_registry(repo_root: Path) -> Dict[str, Any]:
    path = repo_root / "governance" / "runtime_capability_registry.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return build_capability_registry(repo_root)


def register_capability_cluster(registry: Dict[str, Any], entry: CapabilityRegistryEntry) -> Dict[str, Any]:
    entries = [item for item in registry.get("entries", []) if item.get("cluster_id") != entry.cluster_id]
    entries.append(entry.to_dict())
    registry = dict(registry)
    registry["entries"] = sorted(entries, key=lambda item: item["cluster_id"])
    return registry


def get_canonical_owner(registry: Dict[str, Any], cluster_id: str) -> str:
    for entry in registry.get("entries", []):
        if entry.get("cluster_id") == cluster_id:
            return str(entry.get("canonical_owner", ""))
    return ""


def get_adapter_path(registry: Dict[str, Any], cluster_id: str, context: str = "") -> str:
    for entry in registry.get("entries", []):
        if entry.get("cluster_id") == cluster_id:
            router = entry.get("router_module") or "reports/integration/e11_cross_repo_backflow_plan.md"
            return f"{router}:{context}" if context else str(router)
    return ""


def render_capability_registry_report(registry: Dict[str, Any]) -> str:
    entries = registry.get("entries", [])
    lines = [
        "# E11 Capability Registry Report",
        "",
        f"- registry_id: {registry.get('registry_id')}",
        f"- baseline_commit: {registry.get('baseline_commit')}",
        f"- cluster_count: {len(entries)}",
        "- discovery_backed: true",
        "",
        "## Canonical Entries",
    ]
    for entry in entries:
        lines.extend(
            [
                f"### {entry['cluster_id']}: {entry['cluster_name']}",
                f"- relation_type: {entry['relation_type']}",
                f"- conflict_risk: {entry['conflict_risk']}",
                f"- canonical_owner: {entry['canonical_owner']}",
                f"- adapter_owner: {entry['adapter_owner']}",
                f"- router_module: {entry['router_module'] or 'none - mapped through backflow plan/integration map'}",
                f"- registry_role: {entry['registry_role']}",
                f"- discovered_from_evidence: {str(entry['discovered_from_evidence']).lower()}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()

