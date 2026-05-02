from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List


SUPPRESSION_REGISTRY_PATH = Path("operations/external_validation/e9_suppression_registry.json")


@dataclass(frozen=True)
class E9SuppressionRegistry:
    opted_out_target_ids: List[str] = field(default_factory=list)
    invalid_target_ids: List[str] = field(default_factory=list)
    out_of_scope_target_ids: List[str] = field(default_factory=list)
    sent_counts_by_target_id: Dict[str, int] = field(default_factory=dict)
    max_duplicate_contacts: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def default_e9_suppression_registry() -> E9SuppressionRegistry:
    return E9SuppressionRegistry()


def load_e9_suppression_registry(repo_root: Path) -> E9SuppressionRegistry:
    path = repo_root / SUPPRESSION_REGISTRY_PATH
    if not path.exists():
        return default_e9_suppression_registry()
    return E9SuppressionRegistry(**json.loads(path.read_text(encoding="utf-8")))


def write_default_e9_suppression_registry(repo_root: Path) -> Path:
    path = repo_root / SUPPRESSION_REGISTRY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(default_e9_suppression_registry().to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def suppression_blocks_target(registry: E9SuppressionRegistry | Dict[str, Any], target_id: str) -> List[str]:
    item = registry if isinstance(registry, E9SuppressionRegistry) else E9SuppressionRegistry(**registry)
    reasons: List[str] = []
    if target_id in item.opted_out_target_ids:
        reasons.append("target_opted_out")
    if target_id in item.invalid_target_ids:
        reasons.append("target_invalid")
    if target_id in item.out_of_scope_target_ids:
        reasons.append("target_out_of_scope")
    if item.sent_counts_by_target_id.get(target_id, 0) >= item.max_duplicate_contacts:
        reasons.append("duplicate_contact_limit_reached")
    return reasons


def render_e9_suppression_registry_status(registry: E9SuppressionRegistry) -> str:
    return "\n".join(
        [
            "# E9 Suppression Registry Status",
            "",
            f"- opted_out_target_ids: {registry.opted_out_target_ids}",
            f"- invalid_target_ids: {registry.invalid_target_ids}",
            f"- out_of_scope_target_ids: {registry.out_of_scope_target_ids}",
            f"- sent_counts_by_target_id: {registry.sent_counts_by_target_id}",
            f"- max_duplicate_contacts: {registry.max_duplicate_contacts}",
            "- suppressions_active: true",
        ]
    )
