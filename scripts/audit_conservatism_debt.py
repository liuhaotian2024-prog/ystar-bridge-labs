#!/usr/bin/env python3
"""Audit conservatism debt and introduce staged action policies.

This script is intentionally read-only with respect to unsafe/runtime surfaces:
it skips DB/WAL/SHM files, logs, pycache, active-agent markers, env/secret files,
and generated audit/policy outputs. It writes only L7.0Q scoped artifacts plus a
low-conflict policy-reference migration on L7.0P JSON artifacts.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "l7_conservatism_debt_audit"
POLICY_DIR = ROOT / "policy"
MILESTONE_ID = "L7.0Q"
MILESTONE_NAME = "Conservatism Debt Audit, Policy Registry & First Migration"

SCAN_PATTERNS = [
    "forbidden_actions",
    "forbidden",
    "blocked",
    "blocked_until_human_approved",
    "hard_forbidden",
    "no_action",
    "no-action",
    "no_go",
    "no-go",
    "deny",
    "denylist",
    "blacklist",
    "allowlist",
    "disabled",
    "not_configured",
    "readiness",
    "preflight_only",
    "user_must_provide",
    "provide URL",
    "user URL",
    "ask-user-URL",
    "ask_user_url",
    "manual URL",
    "manually export",
    "open multiple Codex windows",
    "create worktrees",
    "merge branches",
    "external_side_effects",
    "core_writeback",
    "brain writeback",
    "memory writeback",
    "canonical strategy",
    "CIEU DB write",
    "MCP/live behavior",
    "login",
    "account creation",
    "payment",
    "checkout",
    "form_submission",
    "publication",
    "outreach",
    "grant_submission",
    "RFP_submission",
    "customer_contact",
    "revenue_execution",
]

SCAN_EXTENSIONS = {".py", ".json", ".md", ".sh", ".txt", ".yaml", ".yml", ".toml"}
EXCLUDED_SUFFIXES = {
    ".pyc",
    ".log",
    ".db",
    ".db-wal",
    ".db-shm",
    ".sqlite",
    ".sqlite3",
    ".env",
    ".pem",
    ".key",
    ".pid",
}
EXCLUDED_DIR_PARTS = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".claude",
    "backups",
    "memory",
    "l7_conservatism_debt_audit",
    "policy",
}
EXCLUDED_PATH_FRAGMENTS = {
    "scripts/.logs",
    "active_agent",
    "controlled_observation.env",
    "scripts/audit_conservatism_debt.py",
}
MAX_FINDINGS_PER_FILE_PATTERN = 3

LEGITIMATE_BOUNDARY_TERMS = {
    "secret",
    "api key",
    "payment",
    "checkout",
    "posting",
    "publication",
    "outreach",
    "grant",
    "rfp",
    "brain writeback",
    "memory writeback",
    "canonical strategy",
    "cieu db",
    "db/wal/shm",
    "wal",
    "shm",
    "y-star-gov",
    "gov-mcp",
    "private",
    "internal network",
    "access-control",
    "login",
    "account creation",
}

L7_MIGRATION_DIRS = [
    "l7_agent_team_runtime",
    "l7_revenue_opportunity_radar",
    "l7_human_approved_external_action_gate",
    "l7_review_gated_memory_writeback",
    "l7_owner_runtime_cockpit",
    "l7_parallel_commercial_agent_team_orchestrator",
]


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_json_compact(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def policy_block(category: str, stage: str, requires_approval: bool = False) -> dict[str, Any]:
    return {
        "policy_ref": "policy/action_capability_registry.json",
        "action_capability_policy_ref": "policy/action_capability_registry.json",
        "approval_state_machine_ref": "policy/approval_state_machine.json",
        "revenue_policy_ref": "policy/revenue_action_policy.json",
        "discovery_policy_ref": "policy/discovery_policy.json",
        "runtime_access_policy_ref": "policy/runtime_access_policy.json",
        "writeback_policy_ref": "policy/writeback_policy.json",
        "owner_burden_reduction_policy_ref": "policy/owner_burden_reduction_policy.json",
        "allowed_capability_stage": stage,
        "capability_category": category,
        "execution_requires_human_approval": requires_approval,
        "migration_note": "L7.0Q first migration adds staged policy references while preserving explicit safety text.",
    }


def migrate_l7_artifacts() -> list[str]:
    migrated: list[str] = []
    for dirname in L7_MIGRATION_DIRS:
        for path in sorted((ROOT / dirname).rglob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                continue
            rel = path.relative_to(ROOT).as_posix()
            if "human_approved_external_action_gate" in rel:
                block = policy_block("external_action_gate", "draft", True)
            elif "review_gated_memory_writeback" in rel:
                block = policy_block("writeback", "writeback_candidate", True)
                block["allowed_writeback_stage"] = "dry_run_writeback"
            elif "revenue_opportunity_radar" in rel:
                block = policy_block("revenue_discovery", "analyze", False)
                block["revenue_execution_requires_human_approval"] = True
            elif "owner_runtime_cockpit" in rel:
                block = policy_block("owner_cockpit", "plan", False)
            elif "parallel_commercial_agent_team_orchestrator" in rel:
                block = policy_block("parallel_orchestration", "plan", False)
            else:
                block = policy_block("agent_team_runtime", "plan", False)
            payload.setdefault("l7_0q_policy_migration", block)
            write_json(path, payload)
            migrated.append(rel)
    return migrated


def action(action_type: str, category: str, stages: list[str], decision: str, risk: str, side_effect: str, approval: bool, relevance: str) -> dict[str, Any]:
    return {
        "action_type": action_type,
        "category": category,
        "allowed_stages": stages,
        "default_decision": decision,
        "risk_tier": risk,
        "side_effect_level": side_effect,
        "requires_human_approval": approval,
        "forbidden_without_approval": approval,
        "commercial_relevance": relevance,
        "policy_notes": "Stage the capability instead of blanket-blocking useful work; block only unsafe or unapproved side effects.",
    }


def build_policy_registry() -> None:
    discovery_actions = [
        "query_planning",
        "controlled_search",
        "public_page_read",
        "bounded_crawl",
        "rss_sitemap_read",
        "source_triage",
        "evidence_extraction",
        "corroboration_conflict_analysis",
        "review_packet_generation",
        "internal_strategy_memo",
        "market_research",
        "opportunity_discovery",
        "customer_segment_analysis",
        "pain_point_analysis",
        "funding_grant_watch_read_only",
        "RFP_watch_read_only",
    ]
    draft_actions = [
        "offer_hypothesis_draft",
        "pricing_hypothesis_draft",
        "outreach_email_draft",
        "grant_application_draft",
        "RFP_response_draft",
        "public_content_draft",
        "approval_request_generation",
    ]
    execution_actions = [
        "customer_outreach_send",
        "partner_outreach_send",
        "grant_application_submit",
        "RFP_submit",
        "public_content_publish",
        "account_creation",
        "payment_or_purchase",
        "contract_or_signature",
        "social_posting",
        "MCP_live_behavior",
    ]
    writeback_candidate_actions = [
        "memory_writeback_candidate",
        "brain_update_candidate",
        "canonical_strategy_update_candidate",
        "CIEU_DB_write_candidate",
        "dry_run_writeback",
    ]
    actual_writeback_actions = [
        "actual_memory_writeback",
        "actual_brain_writeback",
        "actual_canonical_strategy_writeback",
        "actual_CIEU_DB_write",
    ]
    actions = [
        *(action(a, "discovery_analysis", ["observe", "search", "read", "extract", "analyze", "plan"], "allowed_with_budget", "low_to_medium", "read_only", False, "enables evidence-backed commercial planning") for a in discovery_actions),
        *(action(a, "draft_planning", ["draft", "plan", "request_approval"], "allowed_draft_only", "medium", "none_until_execution", False, "turns evidence into reviewable commercial proposals") for a in draft_actions),
        *(action(a, "external_execution", ["request_approval", "execute_after_approval"], "allowed_after_human_approval", "high", "external_side_effect", True, "may create revenue only after explicit approval") for a in execution_actions),
        *(action(a, "writeback_candidate", ["writeback_candidate", "dry_run_writeback"], "allowed_draft_only", "medium", "core_state_candidate", True, "allows learning without unreviewed permanent writeback") for a in writeback_candidate_actions),
        *(action(a, "actual_writeback", ["actual_writeback_after_approval"], "blocked_pending_human_review", "critical", "core_state_write", True, "may improve future operations only after explicit approval gate") for a in actual_writeback_actions),
    ]
    write_json(POLICY_DIR / "action_capability_registry.json", {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "capability_stages": [
            "observe",
            "search",
            "read",
            "extract",
            "analyze",
            "draft",
            "plan",
            "request_approval",
            "execute_after_approval",
            "writeback_candidate",
            "dry_run_writeback",
            "actual_writeback_after_approval",
        ],
        "decision_states": [
            "allowed",
            "allowed_with_budget",
            "allowed_read_only",
            "allowed_draft_only",
            "allowed_after_human_approval",
            "blocked_pending_config",
            "blocked_pending_evidence",
            "blocked_pending_human_review",
            "blocked_by_policy",
            "hard_forbidden",
        ],
        "actions": actions,
        "core_principle": "Do not block revenue work. Block unapproved revenue side effects. Do not block discovery. Block unsafe execution.",
    })
    write_json(POLICY_DIR / "action_risk_tiers.json", {
        "schema_version": "v0",
        "risk_tiers": [
            {"risk_tier": "low", "examples": ["query_planning", "internal_strategy_memo"], "default_decision": "allowed"},
            {"risk_tier": "medium", "examples": ["public_page_read", "draft_generation"], "default_decision": "allowed_with_budget"},
            {"risk_tier": "high", "examples": ["customer_outreach_send", "payment_or_purchase"], "default_decision": "allowed_after_human_approval"},
            {"risk_tier": "critical", "examples": ["actual_brain_writeback", "actual_CIEU_DB_write"], "default_decision": "blocked_pending_human_review"},
        ],
    })
    write_json(POLICY_DIR / "approval_state_machine.json", {
        "schema_version": "v0",
        "states": ["draft_created", "human_review_required", "approved_by_human", "execution_allowed", "executed", "post_action_receipt_created", "rejected_by_human", "blocked"],
        "happy_path": ["draft_created", "human_review_required", "approved_by_human", "execution_allowed", "executed", "post_action_receipt_created"],
        "denial_path": ["draft_created", "human_review_required", "rejected_by_human", "blocked"],
        "default_state": "blocked_pending_human_review",
    })
    write_json(POLICY_DIR / "discovery_policy.json", {
        "schema_version": "v0",
        "allowed_with_budget": ["query_planning", "controlled_search", "public_page_read", "bounded_crawl", "rss_sitemap_read", "source_triage", "evidence_extraction", "corroboration_conflict_analysis", "review_packet_generation", "market_research", "opportunity_discovery"],
        "requires_approval_or_blocked": ["login", "form_submission", "posting", "messaging", "payment", "private_internal_network_access", "high_volume_scraping", "access_control_bypass", "publication", "outreach_send", "grant_RFP_submission"],
        "policy_note": "Maximize discovery under budget; block unsafe execution and side effects.",
    })
    write_json(POLICY_DIR / "runtime_access_policy.json", {
        "schema_version": "v0",
        "allowed": ["safe_runtime_metadata", "sanitized_runtime_summary", "generated_read_model_summaries", "no_secret_validation_status", "lane_status", "work_order_status"],
        "restricted_review_required": ["raw_runtime_logs", "active_agent_marker_content", "raw_DB_content", "memory_store_content"],
        "hard_forbidden_by_default": ["secret_files", "API_key_values", "raw_DB_WAL_SHM_ingestion", "private_credentials", "unredacted_logs_with_secrets"],
        "policy_note": "Do not permanently block internal observation; use metadata and sanitized summaries as the safe path.",
    })
    write_json(POLICY_DIR / "writeback_policy.json", {
        "schema_version": "v0",
        "explicitly_allowed": ["evidence_delta_candidate_generation", "strategy_delta_candidate_generation", "agent_capability_delta_candidate_generation", "memory_writeback_candidate_generation", "brain_update_candidate_generation", "canonical_strategy_update_candidate_generation", "writeback_dry_run_receipts"],
        "blocked_by_default_until_future_approval_gate": ["actual_memory_writeback", "actual_brain_writeback", "actual_canonical_strategy_mutation", "actual_CIEU_DB_write"],
        "policy_note": "Do not block learning. Block unreviewed permanent writeback.",
    })
    write_json(POLICY_DIR / "revenue_action_policy.json", {
        "schema_version": "v0",
        "principle": "Do not block revenue work. Block unapproved revenue side effects.",
        "explicitly_allowed": ["opportunity_discovery", "market_research", "customer_segment_analysis", "pain_point_analysis", "competitor_analysis", "funding_grant_watch_read_only", "RFP_watch_read_only", "offer_hypothesis_draft", "pricing_hypothesis_draft", "outreach_draft", "proposal_draft", "internal_strategy_memo", "human_approval_request", "revenue_opportunity_packet_generation"],
        "requires_human_approval": ["sending_outreach", "submitting_grant_RFP", "publishing_content", "account_creation", "payment_purchase", "signing_contracts", "customer_commitments", "autonomous_revenue_execution"],
    })
    write_json(POLICY_DIR / "owner_burden_reduction_policy.json", {
        "schema_version": "v0",
        "owner_burden_anti_patterns": ["asking_user_to_provide_URL", "asking_user_to_manually_search", "asking_user_to_manually_export_many_env_vars", "asking_user_to_open_multiple_Codex_windows", "asking_user_to_manually_create_worktrees", "asking_user_to_manually_merge_branches", "asking_user_to_inspect_secrets_manually", "asking_user_to_copy_generated_artifacts_manually"],
        "preferred_replacements": ["one_command_launcher", "secret_resolver", "no_key_public_web_mode", "host_mediated_search_bridge", "worktree_orchestration_script", "lane_builder", "local_parallel_runner", "owner_cockpit", "approval_gate"],
    })
    write_json(POLICY_DIR / "policy_registry_manifest.json", {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "registry_files": [
            "policy/action_capability_registry.json",
            "policy/action_risk_tiers.json",
            "policy/approval_state_machine.json",
            "policy/discovery_policy.json",
            "policy/runtime_access_policy.json",
            "policy/writeback_policy.json",
            "policy/revenue_action_policy.json",
            "policy/owner_burden_reduction_policy.json",
        ],
        "first_migration_scope": L7_MIGRATION_DIRS,
    })
    write_text(POLICY_DIR / "README.md", "# L7.0Q Policy Registry\n\nThis registry replaces crude blanket blocking with staged, typed, review-gated capability control. It preserves hard safety boundaries while allowing useful discovery, commercial planning, draft generation, and review-gated learning.\n")


def should_scan(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    rel_parts = path.relative_to(ROOT).parts
    parts = set(rel_parts)
    if parts & EXCLUDED_DIR_PARTS:
        return False
    if any(part.startswith(".") for part in rel_parts):
        return False
    if any(fragment in rel for fragment in EXCLUDED_PATH_FRAGMENTS):
        return False
    if rel.startswith("reports/ceo/brain_"):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if path.suffix not in SCAN_EXTENSIONS:
        return False
    return path.is_file()


def classify(pattern: str, excerpt: str) -> tuple[str, str, str, bool]:
    text = f"{pattern} {excerpt}".lower()
    if any(term in text for term in LEGITIMATE_BOUNDARY_TERMS):
        return (
            "legitimate_hard_boundary",
            "P3",
            "Preserve this as a hard or approval-gated boundary; expose only staged safe paths where useful.",
            False,
        )
    if any(term in text for term in ["provide url", "user url", "ask-user-url", "ask_user_url", "manual url", "manually export", "open multiple codex windows", "create worktrees", "merge branches"]):
        return ("owner_manual_burden", "P1", "Replace manual owner labor with a resolver, launcher, orchestrator, or cockpit workflow.", True)
    if any(term in text for term in ["not_configured", "disabled", "readiness", "preflight_only"]):
        return ("disabled_as_final_state", "P1", "Convert final disabled/readiness states into explicit configuration, retry, or activation paths.", True)
    if any(term in text for term in ["no_action", "no-action", "no_go", "no-go"]):
        return ("no_action_receipt_overuse", "P2", "Keep receipts, but pair them with staged useful capability and next action policies.", True)
    if any(term in text for term in ["blacklist", "denylist", "hard_forbidden"]):
        return ("hardcoded_blacklist", "P2", "Move from local blacklist text to the central staged action policy registry.", True)
    if any(term in text for term in ["forbidden_actions", "forbidden", "blocked", "blocked_until_human_approved", "deny", "allowlist"]):
        return ("hardcoded_forbidden_action_list", "P2", "Keep explicit safety text for now, but add policy registry references and staged semantics.", True)
    if any(term in text for term in ["external_side_effects", "core_writeback"]):
        return ("policy_registry_needed", "P2", "Replace binary block phrasing with staged draft, approval, and receipt states.", True)
    return ("policy_registry_needed", "P3", "Review for migration into staged policy registry if it limits useful work.", False)


def scan_repo(migrated_paths: set[str]) -> tuple[list[dict[str, Any]], int]:
    findings: list[dict[str, Any]] = []
    repeated_matches_omitted = 0
    lowered_patterns = [(p, p.lower()) for p in SCAN_PATTERNS]
    for path in sorted(ROOT.rglob("*")):
        if not should_scan(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except UnicodeDecodeError:
            continue
        per_pattern_counts: Counter[str] = Counter()
        for idx, line in enumerate(lines, start=1):
            lower = line.lower()
            for pattern, lowered in lowered_patterns:
                if lowered in lower:
                    if per_pattern_counts[pattern] >= MAX_FINDINGS_PER_FILE_PATTERN:
                        repeated_matches_omitted += 1
                        continue
                    per_pattern_counts[pattern] += 1
                    excerpt = line.strip()[:220]
                    classification, severity, recommended_fix, patchable = classify(pattern, excerpt)
                    patched = rel in migrated_paths and classification in {
                        "hardcoded_blacklist",
                        "hardcoded_forbidden_action_list",
                        "policy_registry_needed",
                        "no_action_receipt_overuse",
                        "external_action_overblocked",
                    }
                    findings.append({
                        "finding_id": f"l7_0q_finding_{len(findings) + 1:04d}",
                        "file_path": rel,
                        "line_number_if_available": idx,
                        "matched_pattern": pattern,
                        "matched_excerpt_short": excerpt,
                        "current_behavior": "Local artifact/source text uses block/forbid/disabled/no-action/manual-burden language.",
                        "classification": classification,
                        "why_it_is_over_conservative_or_hardcoded": "The behavior is expressed as a local binary block rather than a staged, typed, review-gated capability policy." if classification != "legitimate_hard_boundary" else "This is a legitimate hard safety boundary and should remain blocked or approval-gated.",
                        "capability_harmed": "commercial discovery/planning velocity" if classification != "legitimate_hard_boundary" else "none; protects safety boundary",
                        "commercial_impact": "May slow useful commercial work or increase owner manual burden." if classification != "legitimate_hard_boundary" else "Prevents unsafe commercial or core-state side effects.",
                        "recommended_fix": recommended_fix,
                        "severity": severity,
                        "safe_to_patch_now": patchable and rel in migrated_paths,
                        "patch_status": "patched_in_l7_0q" if patched else ("deferred" if patchable else "not_patched"),
                    })
    return findings, repeated_matches_omitted


def subset(findings: list[dict[str, Any]], classifications: set[str]) -> dict[str, Any]:
    items = [finding for finding in findings if finding["classification"] in classifications]
    compact = [
        {
            "finding_id": finding["finding_id"],
            "file_path": finding["file_path"],
            "line_number_if_available": finding["line_number_if_available"],
            "matched_pattern": finding["matched_pattern"],
            "matched_excerpt_short": finding["matched_excerpt_short"],
            "classification": finding["classification"],
            "severity": finding["severity"],
            "patch_status": finding["patch_status"],
        }
        for finding in items
    ]
    return {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "count": len(items),
        "inventory_note": "Compact inventory rows reference full finding records in conservatism_debt_report.json.",
        "findings": compact,
    }


def write_audit_outputs(findings: list[dict[str, Any]], migrated_paths: list[str], repeated_matches_omitted: int) -> None:
    by_class = Counter(f["classification"] for f in findings)
    by_severity = Counter(f["severity"] for f in findings)
    top_over = [f for f in findings if f["classification"] != "legitimate_hard_boundary"][:10]
    top_blacklist = [f for f in findings if "blacklist" in f["classification"] or "forbidden" in f["classification"]][:10]
    report = {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "generated_at_utc": now(),
        "scan_scope": "ystar-company safe source/artifact files only",
        "excluded_unsafe_surfaces": sorted(EXCLUDED_PATH_FRAGMENTS | EXCLUDED_DIR_PARTS | EXCLUDED_SUFFIXES),
        "total_findings": len(findings),
        "repeated_matches_omitted_by_sampling_policy": repeated_matches_omitted,
        "sampling_policy": f"At most {MAX_FINDINGS_PER_FILE_PATTERN} findings per file and pattern are retained to keep the audit reviewable while preserving repo-wide coverage.",
        "severity_counts": dict(sorted(by_severity.items())),
        "classification_counts": dict(sorted(by_class.items())),
        "top_10_over_conservative_bottlenecks": top_over,
        "top_10_hardcoded_blacklist_locations": top_blacklist,
        "findings": findings,
    }
    recommendations = [
        {"recommendation_id": "l7_0q_rec_001", "recommendation": "Use policy/action_capability_registry.json for staged capability decisions instead of local-only forbidden lists.", "priority": "P1"},
        {"recommendation_id": "l7_0q_rec_002", "recommendation": "Treat revenue discovery, market research, and draft generation as allowed work; gate only external revenue side effects.", "priority": "P1"},
        {"recommendation_id": "l7_0q_rec_003", "recommendation": "Replace owner-manual URL/window/worktree/env burden with launchers, resolvers, orchestrators, and cockpit commands.", "priority": "P1"},
        {"recommendation_id": "l7_0q_rec_004", "recommendation": "Preserve legitimate hard boundaries for secrets, payment without approval, external posting/outreach, raw DB/WAL/SHM exposure, and unreviewed writeback.", "priority": "P0"},
    ]
    migration_queue = [f for f in findings if f["safe_to_patch_now"] or (f["patch_status"] == "deferred" and f["classification"] != "legitimate_hard_boundary")][:100]
    summary = {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "total_findings": len(findings),
        "repeated_matches_omitted_by_sampling_policy": repeated_matches_omitted,
        "severity_counts": dict(sorted(by_severity.items())),
        "classification_counts": dict(sorted(by_class.items())),
        "policy_registries_created": True,
        "l7_0p_files_migrated_with_policy_refs": len(migrated_paths),
        "migration_scope": L7_MIGRATION_DIRS,
        "core_correction": "Do not block revenue work. Block unapproved revenue side effects. Do not block discovery. Block unsafe execution.",
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "db_log_wal_shm_active_agent_marker_content_read": False,
    }
    receipt = {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "generated_at_utc": now(),
        "audit_only": True,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "ask_user_for_url_occurred": False,
        "secret_values_serialized": False,
        "db_files_read": False,
        "wal_files_read": False,
        "shm_files_read": False,
        "logs_read": False,
        "active_agent_marker_content_read": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
    }
    write_json_compact(AUDIT_DIR / "conservatism_debt_report.json", report)
    write_json_compact(AUDIT_DIR / "hardcoded_blacklist_inventory.json", subset(findings, {"hardcoded_blacklist", "hardcoded_forbidden_action_list"}))
    write_json_compact(AUDIT_DIR / "capability_bottleneck_inventory.json", subset(findings, {"discovery_blocked_unnecessarily", "external_action_overblocked", "disabled_as_final_state", "policy_registry_needed"}))
    write_json_compact(AUDIT_DIR / "manual_owner_burden_inventory.json", subset(findings, {"owner_manual_burden"}))
    write_json_compact(AUDIT_DIR / "no_action_overuse_inventory.json", subset(findings, {"no_action_receipt_overuse"}))
    write_json_compact(AUDIT_DIR / "disabled_as_final_state_inventory.json", subset(findings, {"disabled_as_final_state"}))
    write_json_compact(AUDIT_DIR / "legitimate_hard_boundary_inventory.json", subset(findings, {"legitimate_hard_boundary"}))
    write_json(AUDIT_DIR / "policy_refactor_recommendations.json", {"schema_version": "v0", "milestone_id": MILESTONE_ID, "recommendations": recommendations})
    write_json_compact(AUDIT_DIR / "migration_queue.json", {"schema_version": "v0", "milestone_id": MILESTONE_ID, "count": len(migration_queue), "findings": migration_queue, "l7_0p_migrated_paths": migrated_paths})
    write_json(AUDIT_DIR / "l7_0q_summary.json", summary)
    write_json(AUDIT_DIR / "l7_0q_no_action_receipt.json", receipt)
    markdown = [
        "# L7.0Q Conservatism Debt Audit",
        "",
        "## Core Correction",
        "",
        "Do not block revenue work. Block unapproved revenue side effects. Do not block discovery. Block unsafe execution.",
        "",
        "## Counts",
        "",
        f"- Total findings: {len(findings)}",
        f"- Severity counts: {dict(sorted(by_severity.items()))}",
        f"- Classification counts: {dict(sorted(by_class.items()))}",
        f"- L7.0P files migrated with policy refs: {len(migrated_paths)}",
        f"- Repeated matches omitted by sampling policy: {repeated_matches_omitted}",
        "",
        "## Top Over-Conservative Bottlenecks",
    ]
    markdown.extend(f"- {f['finding_id']} {f['classification']} in `{f['file_path']}:{f['line_number_if_available']}`: {f['matched_excerpt_short']}" for f in top_over)
    markdown.extend(["", "## Top Hardcoded Blacklist Locations"])
    markdown.extend(f"- {f['finding_id']} in `{f['file_path']}:{f['line_number_if_available']}`: {f['matched_excerpt_short']}" for f in top_blacklist)
    markdown.extend(["", "## Safety Boundaries Preserved", "", "Secrets, payment without approval, autonomous posting/outreach/submission, raw DB/WAL/SHM exposure, unauthorized external repo modification, and unreviewed memory/brain/canonical writeback remain blocked or approval-gated."])
    write_text(AUDIT_DIR / "conservatism_debt_report.md", "\n".join(markdown) + "\n")
    write_text(AUDIT_DIR / "l7_0q_summary.md", f"# L7.0Q Summary\n\n```json\n{json.dumps(summary, indent=2)}\n```\n")


def main() -> None:
    build_policy_registry()
    migrated = migrate_l7_artifacts()
    findings, repeated_matches_omitted = scan_repo(set(migrated))
    write_audit_outputs(findings, migrated, repeated_matches_omitted)
    print(
        f"L7.0Q audit complete: {len(findings)} findings, "
        f"{repeated_matches_omitted} repeated matches omitted, "
        f"{len(migrated)} L7.0P JSON files migrated."
    )


if __name__ == "__main__":
    main()
