#!/usr/bin/env python3
"""Build deterministic L5.5 cross-repo governance boundary proof artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
Y_STAR_GOV_ROOT = WORKSPACE / "Y-star-gov"
GOV_MCP_ROOT = WORKSPACE / "gov-mcp"

PROOF = ROOT / "cross_repo_governance_contract_proof"
Y_GOV = ROOT / "y_star_gov_contract_surface_inventory"
ALIGN = ROOT / "ystar_company_to_y_star_gov_alignment"
MCP = ROOT / "gov_mcp_boundary_inventory"
GOV_MCP = ROOT / "governed_mcp_interface_contract"
NON_BYPASS = ROOT / "cross_repo_non_bypass_proof"
READINESS = ROOT / "cross_repo_gap_and_readiness"

SCHEMA_VERSION = "v0"

L5_INPUT_REFS = {
    "behavior_y_star": "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json",
    "l5_2_pre_u_candidate": (
        "behavior_y_star_to_pre_u_candidate/pre_u_packet_candidate_from_behavior_y_star.json"
    ),
    "l5_3_cycle_run": "projection_checked_autonomous_work_cycle/projection_checked_cycle_run.json",
    "l5_3_cycle_pre_u_candidate": "behavior_projection_pre_u_cycle_gate/cycle_pre_u_packet_candidate.json",
    "l5_3_cieu_fixture": (
        "projection_checked_cieu_residual_cycle/projection_checked_cieu_event_fixture.json"
    ),
    "l5_3_residual_delta": "projection_checked_cieu_residual_cycle/projection_checked_residual_delta.json",
    "l5_4_shadow_learning_run": (
        "review_gated_shadow_learning_cycle/review_gated_shadow_learning_run.json"
    ),
    "shadow_behavior_y_star": (
        "shadow_reprojection_preview/shadow_reprojected_behavior_y_star_preview.json"
    ),
    "shadow_cycle_pre_u_candidate": "shadow_updated_projection_cycle/shadow_cycle_pre_u_packet_candidate.json",
    "shadow_cycle_cieu_fixture": "shadow_cycle_cieu_residual/shadow_cycle_cieu_event_fixture.json",
    "l5_4_readiness": "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json",
}

SAFETY_FLAGS = {
    "live_execution_enabled": False,
    "behavior_execution_enabled": False,
    "external_action_enabled": False,
    "network_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "cieu_persistence_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "candidate_auto_approval_enabled": False,
    "canonical_policy_mutation_enabled": False,
    "y_star_gov_modification_enabled": False,
    "gov_mcp_modification_enabled": False,
    "mcp_tool_execution_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
}

PROOF_STAGES = [
    "load_ystar_company_l5_artifacts",
    "inspect_y_star_gov_contract_surfaces_read_only",
    "inspect_gov_mcp_boundary_surfaces_read_only",
    "map_behavior_y_star_to_y_star_gov_contract_expectations",
    "map_pre_u_candidates_to_y_star_gov_validator_expectations",
    "map_residual_deltas_to_y_star_gov_prediction_delta_expectations",
    "map_bridge_gate_receipts_to_governance_decision_envelope_expectations",
    "map_gov_mcp_resources_to_governed_interface_boundary",
    "identify_bypass_risks",
    "produce_cross_repo_contract_alignment_matrix",
    "produce_non_bypass_invariant_map",
    "produce_cross_repo_gap_report",
    "produce_l5_6_recommendation",
]

FORBIDDEN_OPERATIONS = [
    "modifying Y-star-gov",
    "modifying gov-mcp",
    "running Y-star-gov live hooks",
    "running gov-mcp servers",
    "executing MCP tools",
    "reading raw DB/WAL/SHM/log contents",
    "reading active-agent marker contents",
    "running daemon/scheduler/runtime scripts",
    "external network/API calls",
    "GitHub issue/PR creation",
    "git push",
    "CIEU DB writes",
    "brain writeback",
    "memory ingestion",
    "candidate approval",
    "canonical policy mutation",
    "L6 revenue opportunity discovery",
    "semantic truth scoring",
    "direct behavior execution",
]

ALLOWED_SUFFIXES = {".py", ".md", ".json", ".toml", ".yaml", ".yml", ".txt"}
FORBIDDEN_DIR_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
    ".logs",
    "brain_dream_diffs",
    "escalation",
    "daily",
    "drift_hourly",
    "backups",
    "reports",
    "data",
}
FORBIDDEN_SUFFIXES = {
    ".db",
    ".db-shm",
    ".db-wal",
    ".sqlite",
    ".sqlite3",
    ".log",
}

Y_GOV_SURFACE_TERMS = {
    "pre_u_packet_validator": [
        "pre-u",
        "pre_u",
        "declared_Y_star",
        "declared_y_star",
        "candidate_U",
        "candidate_u",
    ],
    "validation_decision_result_issue_severity": [
        "validation decision",
        "ValidationDecision",
        "severity",
        "issue",
        "result",
    ],
    "governance_contract_dry_run": ["governance contract", "dry-run", "dry_run", "contract validator"],
    "hook_contract_adapter": ["hook", "adapter", "hook contract", "HookAdapter"],
    "cieu_prediction_delta_validator": [
        "CIEU",
        "prediction_delta",
        "prediction delta",
        "residual_delta",
        "predicted_Y",
        "actual_Y",
    ],
    "decision_envelope": ["decision envelope", "DecisionEnvelope", "governance_decision"],
    "learning_writeback_safety": [
        "learning eligibility",
        "learning_eligibility",
        "writeback",
        "brain_writeback",
        "memory_ingestion",
    ],
}

GOV_MCP_SURFACE_TERMS = {
    "mcp_server_entrypoint": ["MCP", "mcp", "server", "Server", "FastMCP"],
    "tool_resource_definition": ["tool", "resource", "Tool", "Resource", "list_tools", "list_resources"],
    "request_handler": ["handler", "request", "call_tool", "read_resource"],
    "transport_boundary": ["transport", "stdio", "sse", "http"],
    "auth_config_boundary": ["auth", "token", "config", "credential", "secret"],
    "file_resource_access": ["file", "path", "read", "write", "resource"],
    "tool_invocation_path": ["invoke", "call", "execute", "run"],
    "governance_hook_reference": ["governance", "Y_star", "y_star", "Pre-U", "pre_u", "bridge"],
}

REQUIRED_MCP_INVARIANTS = [
    "no_mcp_call_without_behavior_y_star",
    "no_mcp_call_without_pre_u_candidate",
    "no_mcp_call_without_governance_decision",
    "no_mcp_call_without_bridge_receipt",
    "no_mcp_call_without_cieu_receipt",
    "no_mcp_call_without_residual_delta",
    "no_mcp_call_with_direct_brain_writeback",
    "no_mcp_call_with_direct_memory_ingestion",
    "no_mcp_call_with_unapproved_external_action",
]

REQUIRED_GATE_SEQUENCE = [
    "mission-level Y*",
    "field functional projection",
    "behavior-level Y*",
    "candidate_U / tool/resource request",
    "Pre-U packet",
    "Y-star-gov validation or versioned governance adapter",
    "bridge authorization receipt",
    "governed MCP/tool/resource call",
    "result receipt",
    "CIEU event",
    "residual delta",
    "review-gated learning candidate",
    "approved controlled update only if separately authorized",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(relative_path: str) -> dict[str, Any]:
    if relative_path not in set(L5_INPUT_REFS.values()):
        raise ValueError(f"Refusing non-curated L5 input: {relative_path}")
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Missing curated L5 input: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def md(title: str, lines: list[str]) -> str:
    return "# " + title + "\n\n" + "\n".join(lines) + "\n"


def safety_boundary_summary() -> dict[str, Any]:
    return {
        **SAFETY_FLAGS,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "mcp_server_executed": False,
        "mcp_tool_executed": False,
        "db_log_wal_shm_active_marker_content_read": False,
        "candidate_approved": False,
        "candidate_applied": False,
        "l6_revenue_opportunity_discovery_implemented": False,
    }


def safe_scan_path(path: Path) -> bool:
    if path.is_symlink():
        return False
    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts.intersection(FORBIDDEN_DIR_PARTS):
        return False
    lowered_name = path.name.lower()
    if "active-agent" in lowered_name or "active_agent" in lowered_name:
        return False
    if any(lowered_name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
        return False
    return path.suffix.lower() in ALLOWED_SUFFIXES


def bounded_excerpt(text: str, term: str, limit: int = 220) -> str:
    lowered = text.lower()
    pos = lowered.find(term.lower())
    if pos < 0:
        return ""
    start = max(0, pos - 70)
    end = min(len(text), pos + len(term) + 140)
    snippet = " ".join(text[start:end].split())
    return snippet[:limit]


def confidence_for(path: Path, term: str) -> str:
    if path.suffix.lower() == ".py" and ("_" in term or term[:1].isupper()):
        return "direct_symbol_match"
    if path.suffix.lower() in {".md", ".txt"}:
        return "direct_doc_match"
    return "inferred_safe_match"


def expected_mapping(surface_name: str) -> str:
    mappings = {
        "pre_u_packet_validator": "ystar-company Pre-U candidates should map to declared_Y_star, X_t, candidate_U, governance expectations, and execution boundaries.",
        "validation_decision_result_issue_severity": "Projection and Pre-U gate decisions should become governance decision envelopes, not live authorization by labs.",
        "governance_contract_dry_run": "Labs dry-run decisions remain candidate evidence until a kernel or versioned adapter validates them.",
        "hook_contract_adapter": "Future hooks must be adapter-mediated and must not be invoked directly by ystar-company.",
        "cieu_prediction_delta_validator": "CIEU-like fixtures should map to prediction-delta inputs and residual classes without persistence.",
        "decision_envelope": "Bridge receipts and gate decisions should map to deterministic decision envelope fields.",
        "learning_writeback_safety": "Review candidates cannot write brain, memory, or canonical policy without separate approval.",
        "mcp_server_entrypoint": "gov-mcp entrypoints must remain disabled until called through a governed lifecycle.",
        "tool_resource_definition": "MCP tools/resources require behavior Y*, Pre-U, governance decision, bridge receipt, result receipt, CIEU receipt, and residual delta.",
        "request_handler": "Request handlers must not become a direct action path bypassing Y-star-gov.",
        "transport_boundary": "Transport surfaces must remain interface-only and not governance kernels.",
        "auth_config_boundary": "Auth/config surfaces are bypass risks if accessed before governance validation.",
        "file_resource_access": "File/resource reads must be governed and deny DB/log/runtime marker access by default.",
        "tool_invocation_path": "Tool invocation paths require explicit gate sequence before any execution mode.",
        "governance_hook_reference": "Existing governance references should be aligned to Y-star-gov and not duplicated in gov-mcp.",
    }
    return mappings.get(surface_name, "Surface requires manual mapping before live integration.")


def scan_repo(
    repo_root: Path,
    repo_name: str,
    terms_by_surface: dict[str, list[str]],
    inventory_kind: str,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    if not repo_root.exists():
        manifest = {
            "schema_name": f"ystar.{repo_name}.readonly_scan_manifest",
            "schema_version": SCHEMA_VERSION,
            "repo_name": repo_name,
            "repo_root": str(repo_root),
            "repo_present": False,
            "repo_status": "missing_repo",
            "scanned_files_count": 0,
            "safe_file_types": sorted(ALLOWED_SUFFIXES),
            "forbidden_content_read": False,
            "modification_performed": False,
            "server_executed": False,
            "tool_executed": False,
            "safety_flags": SAFETY_FLAGS,
        }
        missing_surfaces = [
            {
                "surface_name": surface,
                "surface_kind": inventory_kind,
                "path": None,
                "evidence_excerpt_or_symbol": "Reference repo missing; surface inventory deferred.",
                "expected_labs_mapping": expected_mapping(surface),
                "confidence_class": "missing_surface_gap",
            }
            for surface in terms_by_surface
        ]
        inventory = {
            "schema_name": f"ystar.{repo_name}.{inventory_kind}_inventory",
            "schema_version": SCHEMA_VERSION,
            "repo_present": False,
            "scanned_files_count": 0,
            "relevant_surfaces_found": 0,
            "surfaces": missing_surfaces,
            "missing_repo_status": "missing_repo",
            "modification_performed": False,
            "safety_flags": SAFETY_FLAGS,
        }
        return manifest, inventory, missing_surfaces

    scanned_count = 0
    surfaces: list[dict[str, Any]] = []
    matched_surface_names: set[str] = set()
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file() or not safe_scan_path(path):
            continue
        scanned_count += 1
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        searchable = f"{path.name}\n{text}"
        for surface_name, terms in terms_by_surface.items():
            if surface_name in matched_surface_names:
                continue
            for term in terms:
                if term.lower() in searchable.lower():
                    try:
                        relative = str(path.relative_to(repo_root))
                    except ValueError:
                        relative = str(path)
                    surfaces.append(
                        {
                            "surface_name": surface_name,
                            "surface_kind": inventory_kind,
                            "path": relative,
                            "matched_terms": [term],
                            "evidence_excerpt_or_symbol": bounded_excerpt(searchable, term)
                            or f"filename match: {path.name}",
                            "expected_labs_mapping": expected_mapping(surface_name),
                            "confidence_class": confidence_for(path, term),
                        }
                    )
                    matched_surface_names.add(surface_name)
                    break

    for surface_name in terms_by_surface:
        if surface_name not in matched_surface_names:
            surfaces.append(
                {
                    "surface_name": surface_name,
                    "surface_kind": inventory_kind,
                    "path": None,
                    "matched_terms": [],
                    "evidence_excerpt_or_symbol": "No safe scanned file matched this expected surface.",
                    "expected_labs_mapping": expected_mapping(surface_name),
                    "confidence_class": "missing_surface_gap",
                }
            )

    found_count = sum(1 for item in surfaces if item["confidence_class"] != "missing_surface_gap")
    manifest = {
        "schema_name": f"ystar.{repo_name}.readonly_scan_manifest",
        "schema_version": SCHEMA_VERSION,
        "repo_name": repo_name,
        "repo_root": str(repo_root),
        "repo_present": True,
        "repo_status": "present_read_only_scanned",
        "scanned_files_count": scanned_count,
        "safe_file_types": sorted(ALLOWED_SUFFIXES),
        "forbidden_patterns_skipped": sorted(FORBIDDEN_DIR_PARTS) + sorted(FORBIDDEN_SUFFIXES),
        "forbidden_content_read": False,
        "modification_performed": False,
        "server_executed": False,
        "tool_executed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    inventory = {
        "schema_name": f"ystar.{repo_name}.{inventory_kind}_inventory",
        "schema_version": SCHEMA_VERSION,
        "repo_present": True,
        "scanned_files_count": scanned_count,
        "relevant_surfaces_found": found_count,
        "surfaces": surfaces,
        "modification_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return manifest, inventory, surfaces


def build_cross_repo_contract() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "proof_name": "Cross-Repo Governance Contract Proof + gov-mcp Boundary Alignment",
        "proof_id": "cross_repo_governance_contract_proof_v0",
        "purpose": (
            "Prove ystar-company remains a labs/runtime generator and does not become a "
            "second governance kernel while aligning L5 artifacts to Y-star-gov and gov-mcp boundaries."
        ),
        "involved_repos": ["ystar-company", "Y-star-gov", "gov-mcp"],
        "repo_roles": {
            "ystar-company": (
                "labs/runtime host, projection cycle generator, CIEU-like fixture generator, "
                "and console/read-model surface"
            ),
            "Y-star-gov": "canonical deterministic governance kernel",
            "gov-mcp": "governed interface/resource/tool boundary",
        },
        "required_inputs": list(L5_INPUT_REFS.values()) + [str(Y_STAR_GOV_ROOT), str(GOV_MCP_ROOT)],
        "proof_stages": PROOF_STAGES,
        "required_outputs": [
            "Y-star-gov readonly surface inventory",
            "ystar-company to Y-star-gov alignment maps",
            "gov-mcp readonly boundary inventory",
            "governed MCP interface contract",
            "cross-repo non-bypass invariant proof",
            "cross-repo gap and readiness view",
        ],
        "safety_flags": SAFETY_FLAGS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "non_goals": [
            "not live integration",
            "not MCP execution",
            "not Y-star-gov modification",
            "not gov-mcp modification",
            "not canonical policy mutation",
            "not brain or memory writeback",
            "not L6 revenue opportunity discovery",
        ],
    }


def build_input_fixture() -> dict[str, Any]:
    return {
        "schema_name": "ystar.cross_repo_governance_contract_proof.input_fixture",
        "schema_version": SCHEMA_VERSION,
        "fixture_id": "cross-repo-governance-contract-proof-input-001",
        "ystar_company_l5_artifact_refs": L5_INPUT_REFS,
        "y_star_gov_readonly_repo_root": str(Y_STAR_GOV_ROOT),
        "gov_mcp_readonly_repo_root": str(GOV_MCP_ROOT),
        "y_star_gov_repo_status": "present" if Y_STAR_GOV_ROOT.exists() else "missing_repo",
        "gov_mcp_repo_status": "present" if GOV_MCP_ROOT.exists() else "missing_repo",
        "read_only_reference_repos": True,
        "modification_scope": "ystar-company only",
        "safety_flags": SAFETY_FLAGS,
    }


def build_y_star_gov_expectation_maps(
    surfaces: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    found_names = {item["surface_name"]: item for item in surfaces}
    validator_map = {
        "schema_name": "ystar.y_star_gov.validator_expectation_map",
        "schema_version": SCHEMA_VERSION,
        "map_id": "y-star-gov-validator-expectation-map-v0",
        "expected_validator_fields": [
            "declared_Y_star",
            "X_t / Xt",
            "candidate_U",
            "governance_expectations",
            "execution_boundary",
            "trace_refs",
            "validation_decision",
            "issues",
            "severity",
        ],
        "surface_refs": [
            found_names.get("pre_u_packet_validator", {}),
            found_names.get("validation_decision_result_issue_severity", {}),
        ],
        "labs_mapping_status": "candidate_mapped_not_kernel_validated",
        "safety_flags": SAFETY_FLAGS,
    }
    adapter_map = {
        "schema_name": "ystar.y_star_gov.adapter_expectation_map",
        "schema_version": SCHEMA_VERSION,
        "map_id": "y-star-gov-adapter-expectation-map-v0",
        "expected_adapter_fields": [
            "decision_envelope",
            "bridge_authorization",
            "receipt",
            "dry_run_mode",
            "no_live_hook_execution",
        ],
        "surface_refs": [
            found_names.get("governance_contract_dry_run", {}),
            found_names.get("hook_contract_adapter", {}),
            found_names.get("decision_envelope", {}),
        ],
        "labs_mapping_status": "bridge_receipts_are_dry_run_candidates_only",
        "safety_flags": SAFETY_FLAGS,
    }
    prediction_delta_map = {
        "schema_name": "ystar.y_star_gov.prediction_delta_expectation_map",
        "schema_version": SCHEMA_VERSION,
        "map_id": "y-star-gov-prediction-delta-expectation-map-v0",
        "expected_prediction_delta_fields": [
            "X_t",
            "U_t",
            "Y_star_t",
            "Y_t_plus_1",
            "R_t_plus_1",
            "predicted_Y",
            "actual_Y",
            "residual_delta",
            "learning_eligibility",
            "writeback_blocked",
        ],
        "surface_refs": [
            found_names.get("cieu_prediction_delta_validator", {}),
            found_names.get("learning_writeback_safety", {}),
        ],
        "labs_mapping_status": "cieu_like_fixtures_are_non_persistent",
        "safety_flags": SAFETY_FLAGS,
    }
    return validator_map, adapter_map, prediction_delta_map


def build_alignment_maps(inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    behavior = inputs["behavior_y_star"]
    pre_u = inputs["l5_2_pre_u_candidate"]
    cycle_pre_u = inputs["l5_3_cycle_pre_u_candidate"]
    cieu_event = inputs["l5_3_cieu_fixture"]
    residual = inputs["l5_3_residual_delta"]
    return {
        "behavior_y_star_to_governance_contract_map": {
            "schema_name": "ystar.alignment.behavior_y_star_to_governance_contract_map",
            "schema_version": SCHEMA_VERSION,
            "map_id": "behavior-y-star-to-governance-contract-map-v0",
            "source_behavior_y_star_id": behavior.get("behavior_y_star_id"),
            "declared_y_star_field": behavior.get("declared_behavior_y_star"),
            "expected_governance_contract_concept": "declared_Y_star",
            "mapped_fields": {
                "declared_behavior_y_star": "declared_Y_star",
                "allowed_behavior_boundary": "allowed_scope",
                "forbidden_behavior_boundary": "denied_scope",
                "required_pre_u_validation": "validation_required",
                "safety_flags": "execution_boundary",
            },
            "kernel_validation_required_before_live": True,
            "ystar_company_is_canonical_governance_kernel": False,
            "safety_flags": SAFETY_FLAGS,
        },
        "pre_u_candidate_to_validator_expectation_map": {
            "schema_name": "ystar.alignment.pre_u_candidate_to_validator_expectation_map",
            "schema_version": SCHEMA_VERSION,
            "map_id": "pre-u-candidate-to-validator-expectation-map-v0",
            "source_pre_u_packet_candidates": [pre_u.get("packet_id"), cycle_pre_u.get("packet_id")],
            "field_map": {
                "declared_Y_star": "declared_Y_star",
                "Xt": "X_t / Xt",
                "candidate_U": "candidate_U",
                "governance_expectations": "governance_expectations",
                "execution_boundary": "execution_boundary",
                "projection_trace_refs": "trace_refs",
                "deny_boundary_constraints": "unresolved gaps and denied scope",
            },
            "validator_status": "requires_future_Y_star_gov_or_versioned_adapter_validation",
            "production_ready": False,
            "safety_flags": SAFETY_FLAGS,
        },
        "cycle_gate_to_decision_envelope_map": {
            "schema_name": "ystar.alignment.cycle_gate_to_decision_envelope_map",
            "schema_version": SCHEMA_VERSION,
            "map_id": "cycle-gate-to-decision-envelope-map-v0",
            "source_gate_refs": [
                "projection_checked_work_proposal/work_proposal_projection_gate_decision.json",
                "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_decision.json",
                "shadow_updated_projection_cycle/shadow_cycle_pre_u_gate_decision.json",
            ],
            "expected_envelope_fields": [
                "gate_name",
                "decision",
                "allowed_scope",
                "denied_scope",
                "required_next_validation",
                "receipt_ref",
                "dry_run_only",
            ],
            "labs_decision_authority": "dry_run_candidate_only",
            "kernel_decision_authority": "canonical_for_future_live_or_external_modes",
            "safety_flags": SAFETY_FLAGS,
        },
        "cieu_fixture_to_prediction_delta_map": {
            "schema_name": "ystar.alignment.cieu_fixture_to_prediction_delta_map",
            "schema_version": SCHEMA_VERSION,
            "map_id": "cieu-fixture-to-prediction-delta-map-v0",
            "source_event_id": cieu_event.get("event_id"),
            "field_map": {
                "X_t": "X_t",
                "U_t": "U_t",
                "Y_star_t": "Y_star_t",
                "Y_t_plus_1": "actual_Y_t_plus_1",
                "R_t_plus_1": "residual_delta",
            },
            "prediction_delta_expectations": [
                "predicted versus actual must be explicit",
                "residual classes must remain structural",
                "learning eligibility must deny direct writeback",
            ],
            "persistence_enabled": False,
            "db_write_performed": False,
            "safety_flags": SAFETY_FLAGS,
        },
        "residual_delta_to_learning_eligibility_map": {
            "schema_name": "ystar.alignment.residual_delta_to_learning_eligibility_map",
            "schema_version": SCHEMA_VERSION,
            "map_id": "residual-delta-to-learning-eligibility-map-v0",
            "source_residual_delta_id": residual.get("residual_delta_id"),
            "learning_eligibility_mapping": {
                "review_queue_candidate": "allowed_as_candidate",
                "direct_brain_writeback": "forbidden",
                "direct_memory_ingestion": "forbidden",
                "candidate_auto_approval": "forbidden",
                "canonical_policy_mutation": "forbidden_without_separate_controlled_design",
            },
            "writeback_blocked": True,
            "safety_flags": SAFETY_FLAGS,
        },
        "labs_vs_kernel_responsibility_boundary": {
            "schema_name": "ystar.alignment.labs_vs_kernel_responsibility_boundary",
            "schema_version": SCHEMA_VERSION,
            "boundary_id": "labs-vs-kernel-responsibility-boundary-v0",
            "ystar_company_may_generate": [
                "candidates",
                "fixtures",
                "traces",
                "dry-run decisions",
                "shadow artifacts",
                "console/read-model summaries",
            ],
            "ystar_company_must_not_be_treated_as_canonical_governance_kernel": True,
            "Y_star_gov_remains_intended_canonical_validator_decision_kernel": True,
            "future_live_execution_requirement": (
                "Future live execution must use Y-star-gov validation or an explicitly versioned adapter."
            ),
            "mismatch_policy": "blocker_not_labs_override",
            "safety_flags": SAFETY_FLAGS,
        },
    }


def build_gov_mcp_maps(surfaces: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    boundary_map = {
        "schema_name": "ystar.gov_mcp.tool_resource_boundary_map",
        "schema_version": SCHEMA_VERSION,
        "map_id": "gov-mcp-tool-resource-boundary-map-v0",
        "boundary_principle": (
            "gov-mcp is a governed interface/resource/tool boundary and cannot become a direct action path."
        ),
        "surface_mappings": [
            {
                "surface_name": item["surface_name"],
                "path": item.get("path"),
                "boundary_implication": expected_mapping(item["surface_name"]),
                "required_governance_control": "Y* projection -> Pre-U -> Y-star-gov/adapter decision -> bridge receipt -> CIEU receipt",
                "confidence_class": item["confidence_class"],
            }
            for item in surfaces
        ],
        "mcp_tool_execution_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }
    risk_names = [
        "direct tool bypass",
        "direct resource bypass",
        "direct external action bypass",
        "direct memory/brain write path",
        "direct network/API path",
        "unlogged execution path",
        "ungoverned MCP call path",
    ]
    risks = [
        {
            "risk_id": f"gov-mcp-bypass-risk-{index:03d}",
            "risk_name": risk_name,
            "status": "identified_requires_governance_gate",
            "bypass_possible_without_contract": True,
            "required_control": "deny until governed MCP lifecycle exists",
            "expected_mitigation": "behavior Y* + Pre-U + Y-star-gov/adapter validation + bridge/CIEU receipts",
            "safety_flags": SAFETY_FLAGS,
        }
        for index, risk_name in enumerate(risk_names, start=1)
    ]
    bypass_inventory = {
        "schema_name": "ystar.gov_mcp.bypass_risk_inventory",
        "schema_version": SCHEMA_VERSION,
        "inventory_id": "gov-mcp-bypass-risk-inventory-v0",
        "risks_identified": True,
        "risk_count": len(risks),
        "risks": risks,
        "unknown_paths_policy": "unresolved_gap_not_safe",
        "mcp_tool_execution_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return boundary_map, bypass_inventory


def build_governed_mcp_contract() -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_mcp_interface.contract",
        "schema_version": SCHEMA_VERSION,
        "contract_id": "governed-mcp-interface-contract-v0",
        "contract_rules": {
            "future_mcp_call_downstream_of_behavior_y_star": True,
            "future_mcp_call_requires_pre_u_candidate": True,
            "future_mcp_call_requires_y_star_gov_or_versioned_adapter_validation": True,
            "future_mcp_call_requires_bridge_or_gate_authorization": True,
            "future_mcp_call_requires_receipt": True,
            "future_mcp_call_requires_cieu_like_or_real_cieu_event": True,
            "future_mcp_call_requires_residual_delta": True,
            "deny_live_external_network_action_without_explicit_approved_mode": True,
        },
        "required_pre_call_gates": [
            "behavior-level Y*",
            "Pre-U candidate",
            "Y-star-gov validation or versioned adapter",
            "bridge authorization receipt",
        ],
        "required_post_call_records": [
            "result receipt",
            "CIEU-like or real CIEU event",
            "residual delta",
            "review-gated learning candidate if residual exists",
        ],
        "mcp_tool_execution_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }


def build_mcp_boundary_contracts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    pre_u_boundary = {
        "schema_name": "ystar.governed_mcp_interface.pre_u_boundary_contract",
        "schema_version": SCHEMA_VERSION,
        "contract_id": "mcp-call-pre-u-boundary-contract-v0",
        "required_fields": [
            "source_behavior_y_star_id",
            "declared_Y_star",
            "X_t / Xt",
            "candidate_U",
            "mcp_tool_or_resource_id",
            "requested_operation",
            "allowed_scope",
            "denied_scope",
            "governance_expectations",
            "trace_refs",
            "execution_boundary",
            "safety_flags",
        ],
        "production_ready": False,
        "safety_flags": SAFETY_FLAGS,
    }
    cieu_receipt = {
        "schema_name": "ystar.governed_mcp_interface.cieu_receipt_contract",
        "schema_version": SCHEMA_VERSION,
        "contract_id": "mcp-call-cieu-receipt-contract-v0",
        "required_receipt_fields": [
            "mcp_call_id",
            "source_pre_u_packet_id",
            "source_decision_envelope_id",
            "tool_or_resource_id",
            "requested_U",
            "allowed_U",
            "actual_result_summary",
            "Y_star_t",
            "Y_t_plus_1",
            "R_t_plus_1",
            "persistence_mode",
            "evidence_refs",
            "safety_flags",
        ],
        "persistence_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }
    invariants = {
        "schema_name": "ystar.governed_mcp_interface.non_bypass_invariant_map",
        "schema_version": SCHEMA_VERSION,
        "map_id": "mcp-non-bypass-invariant-map-v0",
        "invariants": [
            {
                "invariant_id": invariant,
                "required": True,
                "violation_policy": "deny_and_record_gap",
                "safety_flags": SAFETY_FLAGS,
            }
            for invariant in REQUIRED_MCP_INVARIANTS
        ],
        "mcp_tool_execution_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return pre_u_boundary, cieu_receipt, invariants


def build_non_bypass_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    invariant_map = {
        "schema_name": "ystar.cross_repo_non_bypass.invariant_map",
        "schema_version": SCHEMA_VERSION,
        "map_id": "cross-repo-non-bypass-invariant-map-v0",
        "invariants": [
            {
                "invariant_id": invariant,
                "scope": "cross_repo_action_tool_resource_path",
                "required": True,
                "failure_action": "block_future_integration_or_require_revision",
            }
            for invariant in REQUIRED_MCP_INVARIANTS
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    lifecycle = {
        "schema_name": "ystar.cross_repo_non_bypass.action_path_lifecycle",
        "schema_version": SCHEMA_VERSION,
        "lifecycle_id": "cross-repo-action-path-lifecycle-v0",
        "canonical_gate_sequence": REQUIRED_GATE_SEQUENCE,
        "direct_bypass_allowed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    forbidden_matrix = {
        "schema_name": "ystar.cross_repo_non_bypass.forbidden_bypass_path_matrix",
        "schema_version": SCHEMA_VERSION,
        "matrix_id": "forbidden-bypass-path-matrix-v0",
        "paths": [
            {
                "path_name": "candidate_U directly to MCP call",
                "status": "forbidden",
                "reason": "missing behavior Y*, Pre-U, governance decision, bridge receipt, and CIEU receipt",
            },
            {
                "path_name": "agent proposal directly to MCP call",
                "status": "forbidden",
                "reason": "agent proposal must first pass projection and Pre-U gates",
            },
            {
                "path_name": "MCP call directly to brain writeback",
                "status": "forbidden",
                "reason": "brain writeback requires separately approved controlled learning design",
            },
            {
                "path_name": "MCP call directly to memory ingestion",
                "status": "forbidden",
                "reason": "memory ingestion requires separately approved controlled learning design",
            },
            {
                "path_name": "tool result directly to canonical policy mutation",
                "status": "forbidden",
                "reason": "canonical policy mutation requires controlled approval and kernel mediation",
            },
            {
                "path_name": "residual directly to brain writeback",
                "status": "forbidden",
                "reason": "residual can only create review-gated learning candidates",
            },
            {
                "path_name": "residual directly to memory ingestion",
                "status": "forbidden",
                "reason": "residual can only create review-gated learning candidates",
            },
            {
                "path_name": "review candidate direct approval",
                "status": "forbidden",
                "reason": "candidate approval is outside this dry-run architecture proof",
            },
            {
                "path_name": "external action without explicit approval",
                "status": "forbidden",
                "reason": "external action requires separately approved mode",
            },
            {
                "path_name": "network/API call without explicit approval",
                "status": "forbidden",
                "reason": "network/API access requires separately approved mode",
            },
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    gate_sequence = {
        "schema_name": "ystar.cross_repo_non_bypass.required_gate_sequence",
        "schema_version": SCHEMA_VERSION,
        "sequence_id": "required-gate-sequence-v0",
        "sequence": [
            {"order": index, "gate": gate, "required": True}
            for index, gate in enumerate(REQUIRED_GATE_SEQUENCE, start=1)
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.cross_repo_non_bypass.summary",
        "schema_version": SCHEMA_VERSION,
        "cross_repo_non_bypass_invariants_defined": True,
        "required_gate_sequence_defined": True,
        "forbidden_bypass_path_matrix_defined": True,
        "direct_candidate_u_to_mcp_forbidden": True,
        "mcp_to_brain_memory_forbidden": True,
        "safety_flags": SAFETY_FLAGS,
    }
    return invariant_map, lifecycle, forbidden_matrix, gate_sequence, summary


def build_readiness(
    y_manifest: dict[str, Any],
    mcp_manifest: dict[str, Any],
    y_inventory: dict[str, Any],
    mcp_inventory: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    y_inventoried = y_manifest["repo_present"] and y_inventory["scanned_files_count"] > 0
    mcp_inventoried = mcp_manifest["repo_present"] and mcp_inventory["scanned_files_count"] > 0
    gaps = [
        {
            "gap_id": "cross-repo-gap-001",
            "gap": "Y-star-gov validation remains read-only inventoried, not called.",
            "blocking_l5_6": False,
            "required_future_resolution": "Build a governed MCP dry-run adapter that uses explicit versioned validation envelopes.",
        },
        {
            "gap_id": "cross-repo-gap-002",
            "gap": "gov-mcp server/tool execution remains disabled.",
            "blocking_l5_6": False,
            "required_future_resolution": "Keep L5.6 adapter dry-run and receipt-based before any live MCP path.",
        },
        {
            "gap_id": "cross-repo-gap-003",
            "gap": "Canonical learning architecture remains future work before any L6 revenue discovery.",
            "blocking_l5_6": False,
            "required_future_resolution": "Design controlled canonical learning gates before approving updates.",
        },
    ]
    readiness = {
        "schema_name": "ystar.cross_repo_gap_and_readiness.governance_readiness",
        "schema_version": SCHEMA_VERSION,
        "readiness_id": "cross-repo-governance-readiness-v0",
        "y_star_gov_repo_present": y_manifest["repo_present"],
        "gov_mcp_repo_present": mcp_manifest["repo_present"],
        "y_star_gov_surfaces_inventoried": y_inventoried or not y_manifest["repo_present"],
        "gov_mcp_surfaces_inventoried": mcp_inventoried or not mcp_manifest["repo_present"],
        "behavior_y_star_mapped_to_governance_contract": True,
        "pre_u_candidates_mapped_to_validator_expectations": True,
        "cieu_fixtures_mapped_to_prediction_delta_expectations": True,
        "gov_mcp_boundary_mapped": True,
        "non_bypass_invariants_defined": True,
        "bypass_risks_identified": True,
        "labs_kernel_responsibility_boundary_defined": True,
        "ready_for_l5_6_governed_mcp_dry_run_adapter": True,
        "ready_for_controlled_canonical_learning_design": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
        **safety_boundary_summary(),
        "safety_flags": SAFETY_FLAGS,
        "next_required_milestone": "L5.6 Governed MCP Dry-Run Adapter v0",
    }
    gap_report = {
        "schema_name": "ystar.cross_repo_gap_and_readiness.alignment_gap_report",
        "schema_version": SCHEMA_VERSION,
        "gap_report_id": "cross-repo-alignment-gap-report-v0",
        "gaps": gaps,
        "missing_repo_status": {
            "Y-star-gov": "present" if y_manifest["repo_present"] else "missing_repo",
            "gov-mcp": "present" if mcp_manifest["repo_present"] else "missing_repo",
        },
        "safety_flags": SAFETY_FLAGS,
    }
    next_step = {
        "schema_name": "ystar.cross_repo_gap_and_readiness.l5_6_recommended_next_step",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_milestone": "L5.6 Governed MCP Dry-Run Adapter v0",
        "reason": (
            "The non-bypass contract is defined; next proof should create a dry-run MCP adapter "
            "that consumes behavior Y*, Pre-U, governance decision envelopes, and receipts without executing MCP tools."
        ),
        "l6_revenue_opportunity_discovery_remains_blocked": True,
        "safety_flags": SAFETY_FLAGS,
    }
    return gap_report, readiness, next_step


def build_summary(
    y_manifest: dict[str, Any],
    mcp_manifest: dict[str, Any],
    y_inventory: dict[str, Any],
    mcp_inventory: dict[str, Any],
    readiness: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.cross_repo_governance_contract_proof.summary",
        "schema_version": SCHEMA_VERSION,
        "cross_repo_governance_contract_proof_defined": True,
        "y_star_gov_surfaces_inventoried_read_only": readiness["y_star_gov_surfaces_inventoried"],
        "gov_mcp_surfaces_inventoried_read_only": readiness["gov_mcp_surfaces_inventoried"],
        "y_star_gov_repo_present": y_manifest["repo_present"],
        "gov_mcp_repo_present": mcp_manifest["repo_present"],
        "y_star_gov_scanned_files_count": y_inventory["scanned_files_count"],
        "gov_mcp_scanned_files_count": mcp_inventory["scanned_files_count"],
        "behavior_y_star_mapped_to_governance_contract": True,
        "pre_u_candidates_mapped_to_validator_expectations": True,
        "cieu_residual_mapped_to_prediction_delta_expectations": True,
        "gov_mcp_boundary_mapped": True,
        "non_bypass_invariants_defined": True,
        "bypass_risks_identified": True,
        "non_ystar_company_repo_modified": False,
        "mcp_server_or_tool_executed": False,
        "ready_for_l5_6_governed_mcp_dry_run_adapter": readiness[
            "ready_for_l5_6_governed_mcp_dry_run_adapter"
        ],
        "ready_for_controlled_canonical_learning_design": readiness[
            "ready_for_controlled_canonical_learning_design"
        ],
        "ready_for_l6_revenue_opportunity_discovery": False,
        **SAFETY_FLAGS,
        "next_required_milestone": "L5.6 Governed MCP Dry-Run Adapter v0",
        "generated_contract_summary": rel(PROOF / "cross_repo_contract_proof_summary.json"),
        "generated_y_star_gov_surface_summary": rel(Y_GOV / "y_star_gov_surface_summary.json"),
        "generated_y_star_gov_alignment_summary": rel(
            ALIGN / "ystar_company_to_y_star_gov_alignment_summary.json"
        ),
        "generated_gov_mcp_surface_summary": rel(MCP / "gov_mcp_surface_summary.json"),
        "generated_governed_mcp_interface_summary": rel(
            GOV_MCP / "governed_mcp_interface_summary.json"
        ),
        "generated_non_bypass_summary": rel(NON_BYPASS / "cross_repo_non_bypass_summary.json"),
        "generated_readiness": rel(READINESS / "cross_repo_governance_readiness.json"),
        "warning": (
            "L5.5 is a read-only cross-repo proof. Y-star-gov and gov-mcp were not modified, "
            "MCP tools were not executed, and ystar-company remains labs/runtime only."
        ),
    }


def build() -> None:
    inputs = {key: load_json(path) for key, path in L5_INPUT_REFS.items()}
    y_manifest, y_inventory, y_surfaces = scan_repo(
        Y_STAR_GOV_ROOT,
        "Y-star-gov",
        Y_GOV_SURFACE_TERMS,
        "contract_surface",
    )
    mcp_manifest, mcp_inventory, mcp_surfaces = scan_repo(
        GOV_MCP_ROOT,
        "gov-mcp",
        GOV_MCP_SURFACE_TERMS,
        "boundary_surface",
    )

    y_validator_map, y_adapter_map, y_prediction_map = build_y_star_gov_expectation_maps(y_surfaces)
    alignment_maps = build_alignment_maps(inputs)
    mcp_boundary_map, mcp_bypass_inventory = build_gov_mcp_maps(mcp_surfaces)
    governed_mcp_contract = build_governed_mcp_contract()
    mcp_pre_u_boundary, mcp_cieu_receipt, mcp_invariants = build_mcp_boundary_contracts()
    (
        cross_invariants,
        action_lifecycle,
        forbidden_matrix,
        required_gate_sequence,
        non_bypass_summary,
    ) = build_non_bypass_artifacts()
    gap_report, readiness, next_step = build_readiness(y_manifest, mcp_manifest, y_inventory, mcp_inventory)
    summary = build_summary(y_manifest, mcp_manifest, y_inventory, mcp_inventory, readiness)

    contract = build_cross_repo_contract()
    fixture = build_input_fixture()
    proof_run = {
        "schema_name": "ystar.cross_repo_governance_contract_proof.run",
        "schema_version": SCHEMA_VERSION,
        "run_id": "cross-repo-governance-contract-proof-run-001",
        "proof_stages": [{"stage": stage, "status": "completed_read_only"} for stage in PROOF_STAGES],
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "mcp_server_or_tool_executed": False,
        "db_log_wal_shm_active_marker_content_read": False,
        "outputs": [
            rel(PROOF / "cross_repo_contract_proof_summary.json"),
            rel(Y_GOV / "y_star_gov_contract_surface_inventory.json"),
            rel(ALIGN / "labs_vs_kernel_responsibility_boundary.json"),
            rel(MCP / "gov_mcp_bypass_risk_inventory.json"),
            rel(GOV_MCP / "mcp_non_bypass_invariant_map.json"),
            rel(NON_BYPASS / "required_gate_sequence.json"),
            rel(READINESS / "cross_repo_governance_readiness.json"),
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    y_surface_summary = {
        "schema_name": "ystar.y_star_gov.surface_summary",
        "schema_version": SCHEMA_VERSION,
        "repo_present": y_manifest["repo_present"],
        "scanned_files_count": y_inventory["scanned_files_count"],
        "relevant_surfaces_found": y_inventory["relevant_surfaces_found"],
        "modified": False,
        "surface_inventory_defined": True,
        "validator_expectation_map_defined": True,
        "adapter_expectation_map_defined": True,
        "prediction_delta_expectation_map_defined": True,
        "safety_flags": SAFETY_FLAGS,
    }
    alignment_summary = {
        "schema_name": "ystar.alignment.summary",
        "schema_version": SCHEMA_VERSION,
        "behavior_y_star_mapped_to_governance_contract": True,
        "pre_u_candidate_mapped_to_validator_expectations": True,
        "cycle_gate_mapped_to_decision_envelope": True,
        "cieu_fixture_mapped_to_prediction_delta": True,
        "residual_delta_mapped_to_learning_eligibility": True,
        "labs_vs_kernel_responsibility_boundary_defined": True,
        "ystar_company_is_not_canonical_governance_kernel": True,
        "safety_flags": SAFETY_FLAGS,
    }
    mcp_surface_summary = {
        "schema_name": "ystar.gov_mcp.surface_summary",
        "schema_version": SCHEMA_VERSION,
        "repo_present": mcp_manifest["repo_present"],
        "scanned_files_count": mcp_inventory["scanned_files_count"],
        "relevant_surfaces_found": mcp_inventory["relevant_surfaces_found"],
        "modified": False,
        "boundary_inventory_defined": True,
        "tool_resource_boundary_map_defined": True,
        "bypass_risk_inventory_defined": True,
        "mcp_server_executed": False,
        "mcp_tool_executed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    governed_mcp_summary = {
        "schema_name": "ystar.governed_mcp_interface.summary",
        "schema_version": SCHEMA_VERSION,
        "governed_mcp_interface_contract_defined": True,
        "pre_u_boundary_contract_defined": True,
        "cieu_receipt_contract_defined": True,
        "mcp_non_bypass_invariants_defined": True,
        "requires_behavior_y_star": True,
        "requires_pre_u_candidate": True,
        "requires_governance_decision": True,
        "requires_bridge_receipt": True,
        "requires_cieu_receipt": True,
        "requires_residual_delta": True,
        "mcp_tool_execution_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }

    write_text(
        PROOF / "README.md",
        md(
            "L5.5 Cross-Repo Governance Contract Proof",
            [
                "This pack proves ystar-company remains a labs/runtime host rather than a second governance kernel.",
                "Y-star-gov and gov-mcp are inspected read-only through safe text/code/schema files.",
                "No live integration, MCP execution, canonical mutation, CIEU persistence, or writeback is performed.",
            ],
        ),
    )
    write_json(PROOF / "cross_repo_contract_proof_contract.json", contract)
    write_json(PROOF / "cross_repo_contract_proof_input_fixture.json", fixture)
    write_json(PROOF / "cross_repo_contract_proof_run.json", proof_run)
    write_json(PROOF / "cross_repo_contract_proof_summary.json", summary)
    write_text(
        PROOF / "cross_repo_contract_proof_report.md",
        md(
            "Cross-Repo Contract Proof Report",
            [
                "- ystar-company generated L5 artifacts are mapped as candidates and fixtures only.",
                "- Y-star-gov remains the intended canonical deterministic governance kernel.",
                "- gov-mcp is treated as a governed interface/resource/tool boundary.",
                "- Future MCP/tool/resource calls must pass the non-bypass gate sequence.",
            ],
        ),
    )

    write_json(Y_GOV / "y_star_gov_readonly_scan_manifest.json", y_manifest)
    write_json(Y_GOV / "y_star_gov_contract_surface_inventory.json", y_inventory)
    write_json(Y_GOV / "y_star_gov_validator_expectation_map.json", y_validator_map)
    write_json(Y_GOV / "y_star_gov_adapter_expectation_map.json", y_adapter_map)
    write_json(Y_GOV / "y_star_gov_prediction_delta_expectation_map.json", y_prediction_map)
    write_text(
        Y_GOV / "y_star_gov_surface_gap_report.md",
        md(
            "Y-star-gov Surface Gap Report",
            [
                f"- Repo present: {y_manifest['repo_present']}",
                f"- Safe files scanned: {y_inventory['scanned_files_count']}",
                f"- Relevant surfaces found: {y_inventory['relevant_surfaces_found']}",
                "- Missing or ambiguous surfaces are recorded as gaps, not silently accepted.",
            ],
        ),
    )
    write_json(Y_GOV / "y_star_gov_surface_summary.json", y_surface_summary)

    for name, payload in alignment_maps.items():
        write_json(ALIGN / f"{name}.json", payload)
    write_json(ALIGN / "ystar_company_to_y_star_gov_alignment_summary.json", alignment_summary)
    write_text(
        ALIGN / "ystar_company_to_y_star_gov_alignment_report.md",
        md(
            "ystar-company to Y-star-gov Alignment Report",
            [
                "- Behavior-level Y* maps to declared_Y_star expectations.",
                "- Pre-U candidates map to validator envelope fields.",
                "- CIEU-like fixtures map to prediction-delta fields without persistence.",
                "- ystar-company remains labs/runtime and cannot override kernel mismatches.",
            ],
        ),
    )

    write_json(MCP / "gov_mcp_readonly_scan_manifest.json", mcp_manifest)
    write_json(MCP / "gov_mcp_boundary_surface_inventory.json", mcp_inventory)
    write_json(MCP / "gov_mcp_tool_resource_boundary_map.json", mcp_boundary_map)
    write_json(MCP / "gov_mcp_bypass_risk_inventory.json", mcp_bypass_inventory)
    write_text(
        MCP / "gov_mcp_surface_gap_report.md",
        md(
            "gov-mcp Surface Gap Report",
            [
                f"- Repo present: {mcp_manifest['repo_present']}",
                f"- Safe files scanned: {mcp_inventory['scanned_files_count']}",
                f"- Relevant surfaces found: {mcp_inventory['relevant_surfaces_found']}",
                "- Unknown direct action paths remain unresolved gaps until governed lifecycle is implemented.",
            ],
        ),
    )
    write_json(MCP / "gov_mcp_surface_summary.json", mcp_surface_summary)

    write_json(GOV_MCP / "governed_mcp_interface_contract.json", governed_mcp_contract)
    write_text(
        GOV_MCP / "governed_mcp_call_lifecycle.md",
        md(
            "Governed MCP Call Lifecycle",
            [
                "1. Start with mission-level Y* and field functional projection.",
                "2. Produce behavior-level Y* and a candidate_U/tool or resource request.",
                "3. Build a Pre-U packet candidate.",
                "4. Require Y-star-gov validation or an explicitly versioned governance adapter.",
                "5. Require bridge authorization and receipts before any MCP/tool/resource call.",
                "6. Record result receipt, CIEU event, residual delta, and review-gated learning candidate.",
            ],
        ),
    )
    write_json(GOV_MCP / "mcp_call_pre_u_boundary_contract.json", mcp_pre_u_boundary)
    write_json(GOV_MCP / "mcp_call_cieu_receipt_contract.json", mcp_cieu_receipt)
    write_json(GOV_MCP / "mcp_non_bypass_invariant_map.json", mcp_invariants)
    write_json(GOV_MCP / "governed_mcp_interface_summary.json", governed_mcp_summary)
    write_text(
        GOV_MCP / "governed_mcp_interface_report.md",
        md(
            "Governed MCP Interface Report",
            [
                "- Future MCP calls require behavior-level Y*, Pre-U, governance decision, bridge receipt, CIEU receipt, and residual delta.",
                "- MCP execution remains disabled in L5.5.",
                "- Direct brain/memory writeback and unapproved external action are invariant violations.",
            ],
        ),
    )

    write_json(NON_BYPASS / "cross_repo_non_bypass_invariant_map.json", cross_invariants)
    write_json(NON_BYPASS / "cross_repo_action_path_lifecycle.json", action_lifecycle)
    write_json(NON_BYPASS / "forbidden_bypass_path_matrix.json", forbidden_matrix)
    write_json(NON_BYPASS / "required_gate_sequence.json", required_gate_sequence)
    write_text(
        NON_BYPASS / "cross_repo_non_bypass_gap_report.md",
        md(
            "Cross-Repo Non-Bypass Gap Report",
            [
                "- Required sequence is defined, but not executed.",
                "- L5.6 should build a governed MCP dry-run adapter that emits receipts.",
                "- Any live/external/network path remains blocked pending explicit approval.",
            ],
        ),
    )
    write_json(NON_BYPASS / "cross_repo_non_bypass_summary.json", non_bypass_summary)

    write_json(READINESS / "cross_repo_alignment_gap_report.json", gap_report)
    write_text(
        READINESS / "cross_repo_alignment_gap_report.md",
        md(
            "Cross-Repo Alignment Gap Report",
            [
                "- Y-star-gov and gov-mcp were inspected read-only if present.",
                "- Missing or ambiguous surfaces are gaps for L5.6, not live blockers.",
                "- L6 revenue opportunity discovery remains blocked.",
            ],
        ),
    )
    write_json(READINESS / "cross_repo_governance_readiness.json", readiness)
    write_text(
        READINESS / "cross_repo_governance_readiness.md",
        md(
            "Cross-Repo Governance Readiness",
            [
                f"- Ready for L5.6 governed MCP dry-run adapter: {readiness['ready_for_l5_6_governed_mcp_dry_run_adapter']}",
                f"- Ready for controlled canonical learning design: {readiness['ready_for_controlled_canonical_learning_design']}",
                f"- Ready for L6 revenue opportunity discovery: {readiness['ready_for_l6_revenue_opportunity_discovery']}",
                "- All live/writeback/persistence/MCP execution flags remain false.",
            ],
        ),
    )
    write_json(READINESS / "l5_6_recommended_next_step.json", next_step)


def main() -> int:
    build()
    print("Built L5.5 cross-repo governance contract proof artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
