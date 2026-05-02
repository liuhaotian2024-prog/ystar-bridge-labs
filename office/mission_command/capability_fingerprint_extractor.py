from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .global_semantic_inventory import build_global_semantic_inventory


@dataclass
class CapabilityFingerprint:
    fingerprint_id: str
    repo: str
    branch_or_ref: str
    file_path: str
    symbol_or_section: str
    artifact_type: str
    capability_terms: List[str]
    fields: List[str] = field(default_factory=list)
    statuses_or_decisions: List[str] = field(default_factory=list)
    lifecycle_states: List[str] = field(default_factory=list)
    side_effect_boundary: str = "unknown"
    evidence_or_learning_role: str = "unknown"
    owner_or_actor: str = "unknown"
    persistence_behavior: str = "unknown"
    can_execute_external_action: bool = False
    can_write_memory_or_cieu: bool = False
    can_mutate_brain: bool = False
    source_snippet_summary: str = ""
    confidence: float = 0.6

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _artifact_type(source_type: str, symbol: str, file_path: str) -> str:
    lower = f"{symbol} {file_path}".lower()
    if source_type == "json":
        return "operation_template" if "operations/" in file_path else "json_schema"
    if source_type == "markdown":
        if "method" in lower or "kernel" in lower:
            return "method_kernel_rule"
        return "report_section"
    if "test_" in symbol or "/tests/" in file_path:
        return "test_assertion"
    if "brain" in lower:
        return "brain_schema"
    if "dream" in lower:
        return "dream_cycle"
    if "cieu" in lower:
        return "cieu_schema"
    if "mcp" in lower or "gateway" in lower:
        return "gateway_tool"
    if symbol and symbol[:1].isupper():
        return "dataclass" if "dataclass" in lower else "enum"
    return "function" if symbol else "code_module"


def _side_effect_boundary(text: str) -> str:
    lower = text.lower()
    if any(token in lower for token in ["payment", "account creation", "form submission", "publication", "customer contact", "send_validation_message"]):
        return "external_action_or_high_risk_boundary"
    if any(token in lower for token in ["writeback", "cieu", "brain", "memory"]):
        return "persistent_learning_boundary"
    if any(token in lower for token in ["read-only", "public page", "search"]):
        return "read_only_boundary"
    return "internal_report_or_renderer"


def _learning_role(text: str) -> str:
    lower = text.lower()
    if "feedback" in lower or "validation signal" in lower:
        return "validation_feedback_or_signal"
    if "evidence" in lower or "provenance" in lower or "source" in lower:
        return "evidence_provenance"
    if "cieu" in lower or "prediction delta" in lower:
        return "prediction_delta_learning_gate"
    if "brain" in lower or "dream" in lower or "writeback" in lower:
        return "brain_or_dream_learning"
    if "method kernel" in lower or "method" in lower:
        return "method_principle"
    return "operational_control"


def _owner_or_actor(repo: str, text: str) -> str:
    lower = text.lower()
    if repo == "y_star_gov":
        return "Y-star-gov deterministic governance"
    if repo == "gov_mcp":
        return "gov-mcp gateway"
    if "owner" in lower or "approval" in lower:
        return "owner_review"
    if "aiden" in lower:
        return "Aiden CEO"
    return "runtime"


def _persistence_behavior(text: str) -> str:
    lower = text.lower()
    if "writeback" in lower or "cieu" in lower or "brain" in lower:
        if any(token in lower for token in ["blocked", "review", "gate", "eligibility"]):
            return "review_gated_persistence"
        return "persistence_risk"
    if "report" in lower or "render" in lower:
        return "report_only"
    return "non_persistent_or_unknown"


def _symbols(item: Dict[str, Any]) -> List[str]:
    symbols = []
    symbols.extend(item.get("classes", []))
    symbols.extend(item.get("functions", []))
    symbols.extend(item.get("headings", [])[:8])
    if item.get("artifact_type") == "json":
        symbols.extend(key for key in item.get("json_keys", [])[:12] if "." not in key and "[]" not in key)
    return symbols or [Path(item["file_path"]).name]


def extract_capability_fingerprints(inventory: Dict[str, Any]) -> List[CapabilityFingerprint]:
    repos = inventory["repos"]
    fingerprints: List[CapabilityFingerprint] = []
    for item in inventory["files"]:
        text = " ".join(
            [
                item.get("file_path", ""),
                " ".join(item.get("capability_terms", [])),
                " ".join(item.get("fields", [])),
                " ".join(item.get("statuses_or_decisions", [])),
                " ".join(item.get("json_keys", [])),
                item.get("snippet", ""),
            ]
        )
        if not item.get("capability_terms") and not item.get("statuses_or_decisions") and not item.get("json_keys"):
            continue
        for symbol in _symbols(item)[:10]:
            fingerprint_id = f"fp_{len(fingerprints)+1:04d}"
            artifact = _artifact_type(item.get("artifact_type", ""), symbol, item["file_path"])
            lower = text.lower()
            fingerprints.append(
                CapabilityFingerprint(
                    fingerprint_id=fingerprint_id,
                    repo=item["repo"],
                    branch_or_ref=repos.get(item["repo"], {}).get("branch") or repos.get(item["repo"], {}).get("head") or "unknown",
                    file_path=item["file_path"],
                    symbol_or_section=symbol,
                    artifact_type=artifact,
                    capability_terms=item.get("capability_terms", []),
                    fields=item.get("fields", []) + item.get("json_keys", [])[:80],
                    statuses_or_decisions=item.get("statuses_or_decisions", []),
                    lifecycle_states=item.get("lifecycle_strings", []),
                    side_effect_boundary=_side_effect_boundary(text),
                    evidence_or_learning_role=_learning_role(text),
                    owner_or_actor=_owner_or_actor(item["repo"], text),
                    persistence_behavior=_persistence_behavior(text),
                    can_execute_external_action=any(token in lower for token in ["send_validation_message", "customer contact", "publication", "payment"]),
                    can_write_memory_or_cieu=any(token in lower for token in ["cieu write", "core writeback", "memory writeback", "cieu_db_write", "cieu db write"]),
                    can_mutate_brain=any(token in lower for token in ["brain writeback", "mutate brain", "approved_brain_writeback"]),
                    source_snippet_summary=item.get("snippet", "")[:240].replace("\n", " "),
                    confidence=0.85 if item.get("capability_terms") else 0.55,
                )
            )
    return fingerprints


def write_capability_fingerprint_index(repo_root: Path) -> Path:
    inventory = build_global_semantic_inventory(repo_root)
    fingerprints = extract_capability_fingerprints(inventory)
    path = repo_root / "reports" / "integration" / "e11_capability_fingerprint_index.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"fingerprint_count": len(fingerprints), "fingerprints": [fp.to_dict() for fp in fingerprints]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path

