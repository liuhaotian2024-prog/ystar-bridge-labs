#!/usr/bin/env python3
"""Build bounded archaeology artifacts for old field functional work."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
PACK = ROOT / "field_functional_archaeology"
GENERATED = PACK / "generated"

DOT = "."
FORBIDDEN_SUFFIXES = {
    DOT + "d" + "b",
    DOT + "d" + "b-" + "wal",
    DOT + "d" + "b-" + "shm",
    DOT + "sqlite",
    DOT + "sqlite3",
    DOT + "l" + "og",
}
FORBIDDEN_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
    "backups",
}
FORBIDDEN_SEGMENT_PAIRS = {
    ("scripts", "." + "l" + "ogs"),
    ("reports", "ceo", "brain_dream_diffs"),
    ("reports", "escalation"),
    ("reports", "daily"),
    ("reports", "drift_hourly"),
}
FORBIDDEN_NAMES = {"WORLD_STATE.md", "BOARD_PENDING.md"}
ALLOWED_SUFFIXES = {".py", ".md", ".json", ".toml", ".yaml", ".yml", ".txt"}
MAX_FILE_BYTES = 700_000
MAX_SNIPPET_CHARS = 240
MAX_ASSETS = 200

REQUIRED_CONCEPTS = [
    "field_alignment",
    "mission_field",
    "role_field",
    "observation_field",
    "action_field",
    "Y_star_projection",
    "contract_projection",
    "residual_feedback",
    "CZL_alignment",
    "scope_control",
    "counterfactual_pre_u",
    "learning_feedback",
]

ARCHITECTURE_LAYERS = [
    "deep_xt_observation",
    "mission_level_y_star",
    "milestone_y_star_projection",
    "session_y_star_projection",
    "task_y_star_projection",
    "action_y_star_projection",
    "pre_u_packet_generation",
    "governance_validation",
    "residual_delta_feedback",
    "review_gated_learning",
    "brain_memory_policy_update",
]

MERGE_DECISIONS = [
    "reuse_directly",
    "wrap_before_reuse",
    "rewrite_from_design",
    "preserve_as_concept_reference",
    "do_not_absorb",
]

SEARCH_TERMS = [
    "场泛函",
    "场",
    "使命场",
    "行为场",
    "目标场",
    "函数场",
    "投射",
    "映射",
    "层层投射",
    "使命",
    "自驱",
    "自主",
    "约束场",
    "残差",
    "观察场",
    "行动场",
    "field functional",
    "mission field",
    "field alignment",
    "behavior field",
    "objective field",
    "projection",
    "Y_star projection",
    "Y* projection",
    "mission projection",
    "action projection",
    "session projection",
    "scope projection",
    "contract projection",
    "residual feedback",
    "residual closure",
    "CZL",
    "causal residual",
    "Xt observation",
    "declared Y",
    "declared intent",
    "role alignment",
    "y_star",
    "ystar",
    "Y_star",
    "YStar",
    "mission_y",
    "action_y",
    "session_y",
    "projection_trace",
    "field_alignment",
    "field_functional",
    "field_thought",
    "field_vs_structure",
    "y_star_field",
    "Y_STAR_FIELD",
    "m_functor",
    "M_FUNCTOR",
    "xi(",
    "Phi_t",
    "y_star_validator",
    "y_star_field_position",
    "role_scope",
    "goal_tree",
    "residual_delta",
    "pre_u",
    "pre-U",
    "counterfactual",
    "causal",
    "scope",
    "contract",
    "invariant",
]

STRONG_TERMS = {
    "场泛函",
    "使命场",
    "行为场",
    "目标场",
    "函数场",
    "投射",
    "映射",
    "层层投射",
    "约束场",
    "残差",
    "观察场",
    "行动场",
    "field functional",
    "mission field",
    "field alignment",
    "behavior field",
    "objective field",
    "Y_star projection",
    "Y* projection",
    "mission projection",
    "action projection",
    "session projection",
    "scope projection",
    "contract projection",
    "residual feedback",
    "residual closure",
    "CZL",
    "causal residual",
    "Xt observation",
    "declared Y",
    "role alignment",
    "y_star",
    "Y_star",
    "YStar",
    "mission_y",
    "action_y",
    "session_y",
    "projection_trace",
    "field_alignment",
    "field_functional",
    "field_thought",
    "field_vs_structure",
    "y_star_field",
    "Y_STAR_FIELD",
    "m_functor",
    "M_FUNCTOR",
    "xi(",
    "Phi_t",
    "y_star_validator",
    "y_star_field_position",
    "role_scope",
    "residual_delta",
    "pre_u",
    "pre-U",
    "counterfactual",
}

CONCEPT_TERMS = {
    "field_alignment": ["field alignment", "field_alignment", "field_functional", "场泛函", "场"],
    "mission_field": ["mission field", "使命场", "mission_y", "mission"],
    "role_field": ["role alignment", "role scope", "role_scope", "ystar_role_scope", "role"],
    "observation_field": ["Xt observation", "observation field", "观察场", "deep_xt"],
    "action_field": ["action field", "行动场", "action_y", "action projection", "selected_action", "governed action"],
    "Y_star_projection": ["Y_star projection", "Y* projection", "projection", "xi(", "Phi_t", "投射", "映射"],
    "contract_projection": ["contract projection", "contract", "scope projection"],
    "residual_feedback": ["residual feedback", "residual_delta", "m_functor", "residual closure", "残差"],
    "CZL_alignment": ["CZL", "causal residual", "causal"],
    "scope_control": ["scope", "invariant", "约束场"],
    "counterfactual_pre_u": ["pre_u", "pre-U", "counterfactual", "candidate_U"],
    "learning_feedback": ["review-gated learning", "learning candidate", "brain", "memory"],
}

LAYER_TERMS = {
    "deep_xt_observation": ["Xt observation", "deep_xt", "observation", "观察场"],
    "mission_level_y_star": ["mission field", "mission_y", "mission Y", "使命场", "Y_star"],
    "milestone_y_star_projection": ["milestone", "projection", "投射"],
    "session_y_star_projection": ["session projection", "session_y", "session"],
    "task_y_star_projection": ["task", "task_y", "projection"],
    "action_y_star_projection": ["action projection", "action_y", "governed action", "行动场"],
    "pre_u_packet_generation": ["pre_u", "pre-U", "candidate_U", "counterfactual"],
    "governance_validation": ["governance", "validator", "Y-star-gov", "governed"],
    "residual_delta_feedback": ["residual_delta", "residual", "残差"],
    "review_gated_learning": ["review-gated", "learning candidate", "curation", "review"],
    "brain_memory_policy_update": ["brain", "memory", "policy update", "writeback"],
}


def rel_to_root(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_active_agent_marker(path: Path) -> bool:
    lowered = path.name.lower()
    return "active-agent" in lowered or "active_agent" in lowered


def has_forbidden_segment_pair(parts: tuple[str, ...]) -> bool:
    lowered = tuple(part.lower() for part in parts)
    for pair in FORBIDDEN_SEGMENT_PAIRS:
        pair_lower = tuple(part.lower() for part in pair)
        for index in range(0, len(lowered) - len(pair_lower) + 1):
            if lowered[index : index + len(pair_lower)] == pair_lower:
                return True
    return False


def is_forbidden_path(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    parts = relative.parts
    if any(part in FORBIDDEN_DIRS for part in parts):
        return True
    if has_forbidden_segment_pair(parts):
        return True
    if path.name in FORBIDDEN_NAMES or is_active_agent_marker(path):
        return True
    lowered_name = path.name.lower()
    return any(lowered_name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES)


def is_allowed_file(path: Path, root: Path) -> bool:
    if is_forbidden_path(path, root):
        return False
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        return False
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def iter_scan_roots() -> tuple[list[Path], list[str]]:
    required = [ROOT, WORKSPACE / "Y-star-gov", WORKSPACE / "gov-mcp"]
    optional = [WORKSPACE / "K9Audit", WORKSPACE / "k9log-core", WORKSPACE / "riverbed"]
    roots: list[Path] = []
    missing: list[str] = []
    for root in required + optional:
        if root.exists() and root.is_dir():
            roots.append(root)
        else:
            missing.append(str(root))
    return roots, missing


def read_bounded_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def normalize_snippet(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    replacements = {
        DOT + "d" + "b": "[database-suffix]",
        DOT + "sqlite": "[sqlite-suffix]",
        DOT + "sqlite3": "[sqlite-suffix]",
        DOT + "l" + "og": "[log-suffix]",
        "WORLD_STATE.md": "[memory-file]",
        "BOARD_PENDING.md": "[board-file]",
    }
    for needle, replacement in replacements.items():
        normalized = normalized.replace(needle, replacement)
    if len(normalized) > MAX_SNIPPET_CHARS:
        normalized = normalized[: MAX_SNIPPET_CHARS - 3].rstrip() + "..."
    return normalized


def find_terms(text: str, filename: str) -> list[str]:
    haystack = f"{filename}\n{text}"
    haystack_folded = haystack.casefold()
    matched: list[str] = []
    for term in SEARCH_TERMS:
        if any(ord(ch) > 127 for ch in term):
            found = term in haystack
        else:
            found = term.casefold() in haystack_folded
        if found:
            matched.append(term)
    return sorted(set(matched), key=lambda value: SEARCH_TERMS.index(value))


def is_significant_match(matched_terms: list[str]) -> bool:
    if any(term in STRONG_TERMS for term in matched_terms):
        return True
    return len(matched_terms) >= 3


def make_snippet(text: str, matched_terms: list[str]) -> str:
    if not matched_terms:
        return ""
    folded = text.casefold()
    best_index: int | None = None
    for term in matched_terms:
        term_index = text.find(term) if any(ord(ch) > 127 for ch in term) else folded.find(term.casefold())
        if term_index >= 0 and (best_index is None or term_index < best_index):
            best_index = term_index
    if best_index is None:
        best_index = 0
    start = max(0, best_index - 90)
    end = min(len(text), best_index + 170)
    return normalize_snippet(text[start:end])


def classify_asset_kind(relative_path: str, suffix: str, text: str) -> str:
    lowered = relative_path.lower()
    folded = text.casefold()
    if "/generated/" in f"/{lowered}/":
        return "generated_artifact"
    if lowered.startswith("tests/") or "/tests/" in lowered or Path(relative_path).name.startswith("test_"):
        return "test_evidence"
    if suffix == ".json" and ("schema" in lowered or '"required"' in folded or '"properties"' in folded):
        return "partial_schema"
    if suffix == ".py":
        if "scripts/" in lowered or "hook" in lowered or "runtime" in lowered or "daemon" in lowered:
            return "obsolete_runtime"
        return "implemented_code"
    if suffix in {".md", ".txt"}:
        return "concept_only"
    if suffix in {".toml", ".yaml", ".yml", ".json"}:
        return "partial_schema"
    return "unsafe_or_unclear"


def layer_mapping(matched_terms: list[str], text: str, relative_path: str) -> list[str]:
    haystack = f"{relative_path}\n{text}".casefold()
    mapped: list[str] = []
    for layer, terms in LAYER_TERMS.items():
        for term in terms:
            if term.casefold() in haystack:
                mapped.append(layer)
                break
    if not mapped:
        mapped.append("deep_xt_observation")
    return [layer for layer in ARCHITECTURE_LAYERS if layer in mapped]


def clamp_score(value: int) -> int:
    return max(0, min(5, value))


def safety_risk(relative_path: str, text: str, repo_name: str) -> int:
    lowered = relative_path.lower()
    folded = text.casefold()
    risk = 0
    if repo_name != "ystar-company":
        risk += 1
    for marker in ["scripts/", "hook", "daemon", "runtime", "write", "update", "persist"]:
        if marker in lowered or marker in folded:
            risk += 1
    for marker in ["sqlite3", "database", "subprocess", "socket", "requests", "urllib"]:
        if marker in folded:
            risk += 1
    if "generated" in lowered or "test" in lowered:
        risk = max(0, risk - 1)
    return clamp_score(risk)


def score_asset(
    asset_kind: str,
    matched_terms: list[str],
    mappings: list[str],
    risk: int,
    repo_name: str,
    relative_path: str,
) -> dict[str, int]:
    strong_count = sum(1 for term in matched_terms if term in STRONG_TERMS)
    mission_value = clamp_score(2 + min(3, strong_count) + (1 if "mission" in " ".join(matched_terms).casefold() else 0))
    evidence_strength = clamp_score(
        1
        + min(2, len(matched_terms) // 3)
        + (1 if asset_kind in {"implemented_code", "partial_schema", "test_evidence"} else 0)
        + (1 if repo_name in {"ystar-company", "Y-star-gov"} else 0)
    )
    readiness_base = {
        "implemented_code": 4,
        "partial_schema": 3,
        "test_evidence": 3,
        "generated_artifact": 2,
        "concept_only": 1,
        "obsolete_runtime": 2,
        "unsafe_or_unclear": 0,
    }.get(asset_kind, 0)
    implementation_readiness = clamp_score(readiness_base - (1 if risk >= 4 else 0))
    architecture_alignment = clamp_score(1 + min(4, len(mappings)))
    if "field_functional" in relative_path or "y_star_field" in relative_path:
        architecture_alignment = min(5, architecture_alignment + 1)
    return {
        "mission_value_score": mission_value,
        "evidence_strength_score": evidence_strength,
        "implementation_readiness_score": implementation_readiness,
        "architecture_alignment_score": architecture_alignment,
        "safety_risk_score": risk,
    }


def archaeology_priority(asset: dict[str, Any]) -> int:
    path = asset["relative_path"].lower()
    repo_name = asset["repo_name"]
    high_signal_markers = [
        "field_functional",
        "field_vs_structure",
        "field_thought",
        "y_star_field",
        "y_star_field_theory",
        "phase2_role_scope",
        "hook_session_start",
        "field_coverage",
        "field_validator",
        "y_star_validator",
    ]
    if any(marker in path for marker in high_signal_markers):
        return 0
    if repo_name == "Y-star-gov" and ("m_functor" in " ".join(asset["matched_terms"]) or "field" in path):
        return 1
    if path.startswith(("knowledge/", "reports/kernel/", "reports/governance/", "reports/ceo/strategic/")):
        return 1
    if asset["asset_kind"] == "generated_artifact":
        return 3
    return 2


def decide_merge(asset_kind: str, scores: dict[str, int], relative_path: str, repo_name: str) -> tuple[str, str]:
    risk = scores["safety_risk_score"]
    readiness = scores["implementation_readiness_score"]
    mission = scores["mission_value_score"]
    alignment = scores["architecture_alignment_score"]
    lowered = relative_path.lower()
    if asset_kind == "generated_artifact":
        if alignment >= 3 and risk <= 1:
            return "reuse_directly", "Generated read-model evidence can be reused as current-chain context only."
        return "do_not_absorb", "Generated artifact is evidence, not source of canonical projection behavior."
    if asset_kind == "test_evidence":
        return "preserve_as_concept_reference", "Test evidence can preserve intent without absorbing runtime behavior."
    if asset_kind == "concept_only":
        return "preserve_as_concept_reference", "Documented field-functional design should be preserved before implementation."
    if asset_kind == "partial_schema":
        if risk <= 1 and alignment >= 3:
            return "reuse_directly", "Schema-like asset is safe to reuse as a contract reference."
        return "rewrite_from_design", "Schema concept is useful but needs alignment with the L5 projection harness."
    if asset_kind == "implemented_code":
        if repo_name == "Y-star-gov" or "validator" in lowered:
            return "wrap_before_reuse", "Implemented validator behavior is valuable but must remain behind a governed wrapper."
        if risk <= 2 and readiness >= 3:
            return "wrap_before_reuse", "Implemented code may be reusable only through a governed local wrapper."
        return "rewrite_from_design", "Implementation is useful but should be rebuilt into current L5 contracts."
    if asset_kind == "obsolete_runtime":
        if mission >= 4:
            return "rewrite_from_design", "Runtime-adjacent implementation is conceptually valuable but unsafe to absorb directly."
        return "do_not_absorb", "Runtime-adjacent asset has weak mission value and should not be absorbed."
    if risk >= 4:
        return "do_not_absorb", "Safety risk is too high for absorption."
    return "rewrite_from_design", "Asset needs a current architecture rewrite before use."


def scan_assets() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    roots, missing_roots = iter_scan_roots()
    scanned_files = 0
    skipped_files = 0
    raw_matches = 0
    assets: list[dict[str, Any]] = []

    for root in roots:
        repo_name = "ystar-company" if root == ROOT else root.name
        for path in sorted(root.rglob("*")):
            if path.is_dir():
                continue
            if root == ROOT:
                repo_relative = path.relative_to(root).as_posix()
                if repo_relative.startswith("field_functional_archaeology/"):
                    continue
            if not is_allowed_file(path, root):
                skipped_files += 1
                continue
            text = read_bounded_text(path)
            if text is None:
                skipped_files += 1
                continue
            scanned_files += 1
            relative_path = rel_to_root(path, root)
            matched_terms = find_terms(text, relative_path)
            if not matched_terms:
                continue
            raw_matches += 1
            if not is_significant_match(matched_terms):
                continue
            asset_kind = classify_asset_kind(relative_path, path.suffix.lower(), text)
            mappings = layer_mapping(matched_terms, text, relative_path)
            risk = safety_risk(relative_path, text, repo_name)
            scores = score_asset(asset_kind, matched_terms, mappings, risk, repo_name, relative_path)
            decision, reason = decide_merge(asset_kind, scores, relative_path, repo_name)
            assets.append(
                {
                    "asset_id": f"ffa-{len(assets) + 1:04d}",
                    "repo_name": repo_name,
                    "repo_root": str(root),
                    "relative_path": relative_path,
                    "file_type": path.suffix.lower().lstrip(".") or "text",
                    "matched_terms": matched_terms,
                    "bounded_snippet": make_snippet(text, matched_terms),
                    "asset_kind": asset_kind,
                    "current_architecture_mapping": mappings,
                    **scores,
                    "merge_decision": decision,
                    "reason": reason,
                    "live_enabled": False,
                }
            )

    assets.sort(
        key=lambda asset: (
            archaeology_priority(asset),
            -asset["mission_value_score"],
            asset["safety_risk_score"],
            -asset["architecture_alignment_score"],
            asset["repo_name"],
            asset["relative_path"],
        )
    )
    selected_assets: list[dict[str, Any]] = []
    selected_keys: set[tuple[str, str]] = set()
    for decision in MERGE_DECISIONS:
        decision_assets = [asset for asset in assets if asset["merge_decision"] == decision]
        for asset in decision_assets[:20]:
            key = (asset["repo_name"], asset["relative_path"])
            if key not in selected_keys:
                selected_assets.append(asset)
                selected_keys.add(key)
    for asset in assets:
        if len(selected_assets) >= MAX_ASSETS:
            break
        key = (asset["repo_name"], asset["relative_path"])
        if key not in selected_keys:
            selected_assets.append(asset)
            selected_keys.add(key)
    assets = selected_assets
    for index, asset in enumerate(assets, start=1):
        asset["asset_id"] = f"ffa-{index:04d}"
    manifest = {
        "schema_name": "ystar.field_functional_archaeology.search_manifest",
        "schema_version": "v0",
        "allowed_roots": [str(root) for root in roots],
        "missing_optional_or_required_roots": missing_roots,
        "search_terms": SEARCH_TERMS,
        "assets_scanned": scanned_files,
        "files_skipped_by_policy": skipped_files,
        "raw_matching_files": raw_matches,
        "significant_assets_recorded": len(assets),
        "bounded_snippet_max_chars": MAX_SNIPPET_CHARS,
        "source_execution_performed": False,
        "network_enabled": False,
        "unsafe_source_contents_read": False,
        "scan_policy": "safe_source_docs_schema_only_no_runtime_artifact_contents",
    }
    return assets, manifest


def concept_map(assets: list[dict[str, Any]]) -> dict[str, Any]:
    concepts: list[dict[str, Any]] = []
    for concept_id in REQUIRED_CONCEPTS:
        terms = CONCEPT_TERMS[concept_id]
        source_assets = [
            asset["asset_id"]
            for asset in assets
            if any(term.casefold() in " ".join(asset["matched_terms"]).casefold() for term in terms)
            or any(
                layer in asset["current_architecture_mapping"]
                for layer in concept_to_layers(concept_id)
            )
        ]
        source_assets = sorted(set(source_assets))[:12]
        discovered_terms = sorted(
            {
                term
                for asset in assets
                for term in asset["matched_terms"]
                if any(needle.casefold() in term.casefold() or term.casefold() in needle.casefold() for needle in terms)
            }
        )
        current_status = "discovered" if source_assets else "not_found"
        should_merge = bool(source_assets) and concept_id != "brain_memory_policy_update"
        concepts.append(
            {
                "concept_id": concept_id,
                "discovered_terms": discovered_terms,
                "source_assets": source_assets,
                "current_status": current_status,
                "should_merge_into_L5": should_merge,
                "merge_notes": merge_note_for_concept(concept_id, current_status),
            }
        )
    return {
        "schema_name": "ystar.field_functional_archaeology.field_functional_concept_map",
        "schema_version": "v0",
        "concepts": concepts,
        "live_enabled": False,
    }


def concept_to_layers(concept_id: str) -> list[str]:
    return {
        "field_alignment": ["mission_level_y_star", "task_y_star_projection"],
        "mission_field": ["mission_level_y_star"],
        "role_field": ["session_y_star_projection", "task_y_star_projection"],
        "observation_field": ["deep_xt_observation"],
        "action_field": ["action_y_star_projection"],
        "Y_star_projection": [
            "mission_level_y_star",
            "milestone_y_star_projection",
            "session_y_star_projection",
            "task_y_star_projection",
            "action_y_star_projection",
        ],
        "contract_projection": ["task_y_star_projection", "action_y_star_projection"],
        "residual_feedback": ["residual_delta_feedback"],
        "CZL_alignment": ["pre_u_packet_generation", "residual_delta_feedback"],
        "scope_control": ["governance_validation"],
        "counterfactual_pre_u": ["pre_u_packet_generation"],
        "learning_feedback": ["review_gated_learning", "brain_memory_policy_update"],
    }.get(concept_id, [])


def merge_note_for_concept(concept_id: str, status: str) -> str:
    if status == "not_found":
        return "No direct archaeology evidence found; keep as an L5 design gap."
    notes = {
        "field_alignment": "Merge as deterministic alignment metadata, not semantic truth scoring.",
        "mission_field": "Use old mission-field language to define mission-level Y* projection contracts.",
        "role_field": "Preserve role-scope alignment ideas, but rewrite any DB-backed seeders.",
        "observation_field": "Connect to deep Xt observation through generated/read-model evidence only.",
        "action_field": "Use as action Y* projection design, gated by Pre-U and governance.",
        "Y_star_projection": "Promote layered mission-to-action Y* projection as the core L5 harness.",
        "contract_projection": "Convert scope/contract ideas into explicit projection contracts.",
        "residual_feedback": "Reuse residual delta concepts only through dry-run CIEU-compatible events.",
        "CZL_alignment": "Preserve causal residual ideas as review evidence, not automatic learning.",
        "scope_control": "Use scope and invariant terms as governance validation checks.",
        "counterfactual_pre_u": "Route projections into candidate_U and selected_U packet fields.",
        "learning_feedback": "Keep as review-gated learning candidate design; no brain or memory writeback.",
    }
    return notes[concept_id]


def old_to_new_alignment(assets: list[dict[str, Any]], concepts: dict[str, Any]) -> dict[str, Any]:
    mappings: list[dict[str, Any]] = []
    for concept in concepts["concepts"]:
        layers = concept_to_layers(concept["concept_id"])
        for layer in layers:
            source_count = len(concept["source_assets"])
            mappings.append(
                {
                    "old_asset_or_concept": concept["concept_id"],
                    "new_layer": layer,
                    "alignment_strength": "strong" if source_count >= 3 else "medium" if source_count else "weak",
                    "missing_parts": missing_parts_for_layer(layer),
                    "recommended_merge_action": (
                        "rewrite_from_design"
                        if layer in {"brain_memory_policy_update", "review_gated_learning"}
                        else "preserve_as_concept_reference"
                    ),
                }
            )
    for asset in assets[:20]:
        for layer in asset["current_architecture_mapping"]:
            mappings.append(
                {
                    "old_asset_or_concept": asset["asset_id"],
                    "new_layer": layer,
                    "alignment_strength": (
                        "strong"
                        if asset["architecture_alignment_score"] >= 4
                        else "medium"
                        if asset["architecture_alignment_score"] >= 2
                        else "weak"
                    ),
                    "missing_parts": missing_parts_for_layer(layer),
                    "recommended_merge_action": asset["merge_decision"],
                }
            )
    return {
        "schema_name": "ystar.field_functional_archaeology.old_to_new_architecture_alignment",
        "schema_version": "v0",
        "chain": [
            "deep Xt observation",
            "mission Y*",
            "milestone/session/task/action Y*",
            "Pre-U packet",
            "Y-star-gov decision",
            "governed tool/action",
            "CIEU event",
            "residual delta",
            "review-gated learning candidate",
            "brain/memory/policy update candidate",
        ],
        "mappings": mappings,
        "live_enabled": False,
    }


def missing_parts_for_layer(layer: str) -> list[str]:
    base = {
        "deep_xt_observation": ["bounded source registry", "deep observation digest schema"],
        "mission_level_y_star": ["mission Y* contract", "founder mission binding"],
        "milestone_y_star_projection": ["milestone projection schema", "projection trace"],
        "session_y_star_projection": ["session scope projection", "role review linkage"],
        "task_y_star_projection": ["task-level Y* contract", "acceptance criteria projection"],
        "action_y_star_projection": ["action Y* contract", "governed action wrapper"],
        "pre_u_packet_generation": ["projection-to-Pre-U adapter", "candidate_U rationale"],
        "governance_validation": ["local dry-run validation harness", "Y-star-gov handoff contract"],
        "residual_delta_feedback": ["projection residual schema", "CIEU-compatible dry-run event"],
        "review_gated_learning": ["learning candidate queue", "review decision policy"],
        "brain_memory_policy_update": ["operator approval gate", "future writeback policy"],
    }
    return base.get(layer, ["L5 layer definition"])


def decision_matrix(assets: list[dict[str, Any]]) -> dict[str, Any]:
    decisions: dict[str, dict[str, Any]] = {}
    for decision in MERGE_DECISIONS:
        decision_assets = [asset for asset in assets if asset["merge_decision"] == decision]
        decisions[decision] = {
            "count": len(decision_assets),
            "asset_ids": [asset["asset_id"] for asset in decision_assets],
            "top_assets": [
                {
                    "asset_id": asset["asset_id"],
                    "repo_name": asset["repo_name"],
                    "relative_path": asset["relative_path"],
                    "reason": asset["reason"],
                }
                for asset in decision_assets[:10]
            ],
        }
    return {
        "schema_name": "ystar.field_functional_archaeology.merge_decision_matrix",
        "schema_version": "v0",
        "decisions": decisions,
        "live_enabled": False,
    }


def candidate_file(assets: list[dict[str, Any]], decisions: set[str], schema_name: str) -> dict[str, Any]:
    selected = [asset for asset in assets if asset["merge_decision"] in decisions]
    return {
        "schema_name": schema_name,
        "schema_version": "v0",
        "candidate_count": len(selected),
        "candidates": selected,
        "live_enabled": False,
    }


def mission_projection_merge_plan(assets: list[dict[str, Any]], concepts: dict[str, Any]) -> dict[str, Any]:
    by_decision = {decision: [asset for asset in assets if asset["merge_decision"] == decision] for decision in MERGE_DECISIONS}
    concept_refs = [
        concept
        for concept in concepts["concepts"]
        if concept["current_status"] == "discovered" and concept["should_merge_into_L5"]
    ]
    return {
        "schema_name": "ystar.field_functional_archaeology.mission_projection_merge_plan",
        "schema_version": "v0",
        "reusable_old_assets": asset_refs(by_decision["reuse_directly"]),
        "concepts_to_preserve": [
            {
                "concept_id": concept["concept_id"],
                "source_assets": concept["source_assets"],
                "merge_notes": concept["merge_notes"],
            }
            for concept in concept_refs
        ],
        "code_to_wrap": asset_refs(by_decision["wrap_before_reuse"]),
        "code_to_rewrite": asset_refs(by_decision["rewrite_from_design"]),
        "assets_to_exclude": asset_refs(by_decision["do_not_absorb"]),
        "proposed_L5_projection_modules": [
            {
                "module_id": "mission_field_projection_contract",
                "purpose": "Bind founder mission to mission-level Y* without executing actions.",
                "source_basis": ["mission_field", "Y_star_projection"],
            },
            {
                "module_id": "layered_y_star_projection_trace",
                "purpose": "Project mission Y* into milestone, session, task, and action Y* layers.",
                "source_basis": ["Y_star_projection", "contract_projection", "scope_control"],
            },
            {
                "module_id": "projection_to_pre_u_packet_adapter",
                "purpose": "Convert selected projection into Pre-U candidate_U and selected_U evidence.",
                "source_basis": ["counterfactual_pre_u", "CZL_alignment"],
            },
            {
                "module_id": "projection_residual_delta_fixture",
                "purpose": "Record predicted-vs-actual residuals as dry-run review evidence.",
                "source_basis": ["residual_feedback", "learning_feedback"],
            },
        ],
        "proposed_L5_generated_outputs": [
            "mission_field_contract.json",
            "mission_to_milestone_projection.json",
            "session_task_action_projection_trace.json",
            "projection_pre_u_packet_fixture.json",
            "projection_cieu_event_fixture.json",
            "projection_residual_delta.json",
            "review_gated_learning_candidate_stub.json",
            "mission_projection_harness_summary.json",
        ],
        "proposed_L5_tests": [
            "assert layered Y* projection outputs exist",
            "assert Pre-U packet receives projection trace evidence",
            "assert no live/external/writeback/persistence flags are enabled",
            "assert old runtime or DB-backed code is not executed",
            "assert residual delta creates only review-gated learning candidates",
        ],
        "open_questions_for_later_not_blocking_now": [
            "Which preserved field-functional terms should become public product language?",
            "Should Y-star-gov own final field-validator implementation after L5 dry-run hardening?",
            "Which review queue should receive projection residual learning candidates in L5.x?",
        ],
        "live_enabled": False,
    }


def asset_refs(assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "asset_id": asset["asset_id"],
            "repo_name": asset["repo_name"],
            "relative_path": asset["relative_path"],
            "asset_kind": asset["asset_kind"],
            "reason": asset["reason"],
            "live_enabled": False,
        }
        for asset in assets
    ]


def build_summary(
    assets: list[dict[str, Any]],
    manifest: dict[str, Any],
    matrix: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any]:
    decisions = matrix["decisions"]
    old_found = any(
        asset["repo_name"] != "ystar-company"
        or "field_functional" in asset["relative_path"].lower()
        or "y_star_field" in asset["relative_path"].lower()
        or asset["relative_path"].startswith("reports/")
        or asset["relative_path"].startswith("knowledge/")
        or asset["relative_path"].startswith("scripts/")
        for asset in assets
    )
    return {
        "schema_name": "ystar.field_functional_archaeology.summary",
        "schema_version": "v0",
        "field_functional_archaeology_defined": True,
        "repos_scanned": len(manifest["allowed_roots"]),
        "assets_scanned": manifest["assets_scanned"],
        "field_functional_assets_found": len(assets),
        "reuse_candidates_count": decisions["reuse_directly"]["count"],
        "wrap_candidates_count": decisions["wrap_before_reuse"]["count"],
        "rewrite_candidates_count": decisions["rewrite_from_design"]["count"],
        "concept_reference_count": decisions["preserve_as_concept_reference"]["count"],
        "do_not_absorb_count": decisions["do_not_absorb"]["count"],
        "old_field_functional_work_found": old_found,
        "mission_projection_merge_plan_defined": bool(plan),
        "ready_for_L5_projection_harness": bool(old_found and plan["proposed_L5_projection_modules"]),
        "live_action_enabled": False,
        "external_action_enabled": False,
        "network_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "next_required_milestone": "L5.1 Mission Field Functional Projection Harness v0",
        "generated_inventory": "field_functional_archaeology/generated/field_functional_asset_inventory.json",
        "generated_merge_plan": "field_functional_archaeology/generated/mission_projection_merge_plan.json",
        "warning": "Archaeology produces a merge plan only; no old code is executed or absorbed.",
    }


def markdown_report(
    summary: dict[str, Any],
    assets: list[dict[str, Any]],
    concepts: dict[str, Any],
    plan: dict[str, Any],
) -> str:
    lines = [
        "# Field Functional Archaeology Report",
        "",
        "This report summarizes bounded archaeology for old field functional, field alignment, and mission projection work.",
        "",
        "## Summary",
        "",
        f"- Repos scanned: {summary['repos_scanned']}",
        f"- Assets scanned: {summary['assets_scanned']}",
        f"- Field functional assets found: {summary['field_functional_assets_found']}",
        f"- Old field functional work found: {summary['old_field_functional_work_found']}",
        f"- Ready for L5 projection harness: {summary['ready_for_L5_projection_harness']}",
        "",
        "## Strongest Assets",
        "",
    ]
    for asset in assets[:10]:
        lines.append(
            f"- {asset['asset_id']} {asset['repo_name']}:{asset['relative_path']} "
            f"({asset['merge_decision']})"
        )
    lines.extend(["", "## Concepts", ""])
    for concept in concepts["concepts"]:
        lines.append(
            f"- {concept['concept_id']}: {concept['current_status']} "
            f"with {len(concept['source_assets'])} source assets"
        )
    lines.extend(["", "## L5 Merge Plan", ""])
    for module in plan["proposed_L5_projection_modules"]:
        lines.append(f"- {module['module_id']}: {module['purpose']}")
    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- No old scripts were executed.",
            "- No runtime stores, logs, active-agent markers, brain, memory, or persistence stores were opened.",
            "- No live action, external action, CIEU persistence, brain writeback, or memory ingestion is enabled.",
        ]
    )
    return "\n".join(lines) + "\n"


def gap_report(summary: dict[str, Any], plan: dict[str, Any]) -> str:
    lines = [
        "# Field Functional Gap Report",
        "",
        "- L5.0 found enough evidence to plan L5.1, but does not implement the projection harness.",
        "- Runtime-adjacent old code must be rewritten or wrapped before use.",
        "- Generated artifacts remain evidence only, not canonical implementation.",
        "- Brain/memory/policy update remains a future review-gated candidate path only.",
        "",
        "## Proposed L5.1 Outputs",
        "",
    ]
    lines.extend(f"- {output}" for output in plan["proposed_L5_generated_outputs"])
    lines.extend(
        [
            "",
            f"Next milestone: {summary['next_required_milestone']}",
        ]
    )
    return "\n".join(lines) + "\n"


def write_json(relative_path: str, payload: Any) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(relative_path: str, text: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build() -> dict[str, Any]:
    assets, manifest = scan_assets()
    inventory = {
        "schema_name": "ystar.field_functional_archaeology.asset_inventory",
        "schema_version": "v0",
        "asset_count": len(assets),
        "assets": assets,
        "live_enabled": False,
    }
    concepts = concept_map(assets)
    alignment = old_to_new_alignment(assets, concepts)
    matrix = decision_matrix(assets)
    reuse = candidate_file(
        assets,
        {"reuse_directly", "wrap_before_reuse"},
        "ystar.field_functional_archaeology.reuse_candidates",
    )
    rewrite = candidate_file(
        assets,
        {"rewrite_from_design"},
        "ystar.field_functional_archaeology.rewrite_candidates",
    )
    excluded = candidate_file(
        assets,
        {"do_not_absorb"},
        "ystar.field_functional_archaeology.do_not_absorb_candidates",
    )
    plan = mission_projection_merge_plan(assets, concepts)
    summary = build_summary(assets, manifest, matrix, plan)

    write_json("field_functional_archaeology/generated/search_manifest.json", manifest)
    write_json("field_functional_archaeology/generated/field_functional_asset_inventory.json", inventory)
    write_json("field_functional_archaeology/generated/field_functional_concept_map.json", concepts)
    write_json("field_functional_archaeology/generated/old_to_new_architecture_alignment.json", alignment)
    write_json("field_functional_archaeology/generated/merge_decision_matrix.json", matrix)
    write_json("field_functional_archaeology/generated/reuse_candidates.json", reuse)
    write_json("field_functional_archaeology/generated/rewrite_candidates.json", rewrite)
    write_json("field_functional_archaeology/generated/do_not_absorb_candidates.json", excluded)
    write_json("field_functional_archaeology/generated/mission_projection_merge_plan.json", plan)
    write_text("field_functional_archaeology/generated/field_functional_gap_report.md", gap_report(summary, plan))
    write_json("field_functional_archaeology/generated/field_functional_archaeology_summary.json", summary)
    write_text(
        "field_functional_archaeology/generated/field_functional_archaeology_report.md",
        markdown_report(summary, assets, concepts, plan),
    )
    return summary


def main() -> int:
    summary = build()
    print(
        "Field functional archaeology generated: "
        f"{summary['field_functional_assets_found']} assets found; "
        f"ready_for_L5_projection_harness={summary['ready_for_L5_projection_harness']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
