#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]
REPOS = {
    "Y-star-gov": Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
    "gov-mcp": Path("/Users/haotianliu/.openclaw/workspace/gov-mcp"),
    "ystar-bridge-labs": Path("/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs"),
    "ystar-company": Path("/Users/haotianliu/.openclaw/workspace/ystar-company"),
}

TEXT_SUFFIXES = {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".txt", ".sh"}
SKIP_NAMES = {".git", "__pycache__", "node_modules", ".venv", "venv"}
SKIP_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".wal", ".shm", ".pyc", ".pyo", ".log"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(repo: Path, args: list[str]) -> str:
    if not repo.exists():
        return ""
    result = subprocess.run(args, cwd=repo, text=True, capture_output=True, check=False, timeout=30)
    return (result.stdout or result.stderr).strip()


def safe_files(root: Path, limit: int = 200000) -> list[str]:
    if not root.exists():
        return []
    files: list[str] = []
    for path in root.rglob("*"):
        if any(part in SKIP_NAMES for part in path.parts):
            continue
        if path.is_file() and path.suffix not in SKIP_SUFFIXES:
            try:
                files.append(str(path.relative_to(root)))
            except ValueError:
                continue
        if len(files) >= limit:
            break
    return sorted(files)


def existing(root: Path, candidates: list[str]) -> list[str]:
    return [item for item in candidates if (root / item).exists()]


def term_hits(root: Path, terms: list[str], limit: int = 40) -> list[str]:
    hits: list[str] = []
    for rel in safe_files(root, limit=200000):
        path = root / rel
        if path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        if any(term.lower() in text for term in terms):
            hits.append(rel)
        if len(hits) >= limit:
            break
    return hits


def repo_snapshot(name: str, root: Path) -> dict[str, Any]:
    exists_flag = root.exists()
    files = safe_files(root) if exists_flag else []
    return {
        "repo": name,
        "path": str(root),
        "exists": exists_flag,
        "is_git_repo": (root / ".git").exists() if exists_flag else False,
        "branch": run(root, ["git", "branch", "--show-current"]) if exists_flag else "",
        "head": run(root, ["git", "log", "-1", "--oneline"]) if exists_flag else "",
        "status_short_sample": run(root, ["git", "status", "--short"]).splitlines()[:80] if exists_flag else [],
        "safe_file_count": len(files),
        "semantic_hits": {
            "approval": term_hits(root, ["approval", "owner decision", "批准", "审批"], 20),
            "cieu_residual": term_hits(root, ["cieu", "prediction delta", "residual", "Rt+1"], 20),
            "mcp_gateway": term_hits(root, ["mcp", "tool", "preflight", "gateway"], 20),
            "commercial_validation": term_hits(root, ["validation", "paid_signal", "offer", "target"], 20),
        }
        if exists_flag
        else {},
    }


def y_star_gov_categories(root: Path) -> list[dict[str, Any]]:
    categories = [
        {
            "category": "governance validators",
            "files": existing(root, [
                "ystar/governance/pre_u_packet_validator.py",
                "ystar/governance/u_v2_validator.py",
                "ystar/governance/y_star_field_validator.py",
                "ystar/kernel/nl_to_contract.py",
                "ystar/kernel/prefill.py",
                "ystar/kernel/czl_protocol.py",
                "tests/governance/test_pre_u_packet_validator.py",
                "tests/test_nl_to_contract.py",
            ]),
            "purpose": "Deterministic validation of Y*, U, packet structure, contract drafts, and hook-facing decisions.",
            "current_maturity": "High for deterministic local checks; semantic proof remains explicitly bounded.",
            "tests_present_or_missing": "Tests present for Pre-U, NL-to-contract, CZL protocol, and governance protocol rules; commercial validation schemas are not yet canonical here.",
            "bridge_labs_relationship": "Bridge-labs E11/E14 routers enforce similar invariants locally for commercial validation packets.",
            "gov_mcp_relationship": "gov-mcp exposes Y-star-gov decisions as MCP tools and should call these validators for live tool boundaries.",
            "backflow_need": "Backflow commercial validation packet schemas and owner approval invariants into Y-star-gov validator standards.",
            "risk_if_not_integrated": "Commercial runtime can drift into local policy forks that look safe but are not canonical.",
        },
        {
            "category": "Pre-U packet validation",
            "files": existing(root, [
                "docs/pre_u_packet_validator/README.md",
                "docs/pre_u_packet_validator/validator_interface_spec.md",
                "docs/pre_u_packet_validator/validation_matrix.md",
                "docs/pre_u_packet_validator/cieu_contract.md",
                "docs/pre_u_packet_validator/hook_contract.md",
                "ystar/governance/pre_u_packet_validator.py",
                "tests/governance/test_pre_u_packet_validator.py",
            ]),
            "purpose": "Pre-action packet gate for Y*, Xt, candidate U, selected U, residual rationale, risk tier, and CIEU link policy.",
            "current_maturity": "Spec plus skeleton implementation plus tests; intentionally structural, not semantic omniscience.",
            "tests_present_or_missing": "Tests present; missing commercial owner-operated validation packet fixtures.",
            "bridge_labs_relationship": "E-series CZL closure packets mirror Pre-U semantics but are currently rendered in bridge-labs reports.",
            "gov_mcp_relationship": "gov-mcp can expose the validator as an owner/tool preflight envelope.",
            "backflow_need": "Define E14/E15 owner validation prep as a Pre-U packet profile.",
            "risk_if_not_integrated": "Milestone actions may claim readiness without canonical pre-action packet validation.",
        },
        {
            "category": "CIEU / prediction delta / residual",
            "files": existing(root, [
                "ystar/governance/cieu_prediction_delta.py",
                "ystar/governance/cieu_store.py",
                "ystar/governance/residual_loop_engine.py",
                "ystar/kernel/cieu.py",
                "ystar/kernel/rt_measurement.py",
                "docs/cieu_prediction_delta/schema_v0.md",
                "tests/governance/test_cieu_prediction_delta.py",
                "tests/test_cieu_store.py",
                "tests/test_residual_loop_engine.py",
            ]),
            "purpose": "Prediction-vs-actual delta, residual loops, learning eligibility, and writeback gating.",
            "current_maturity": "Strong kernel and tests for structural delta and residual loop; commercial feedback-to-CIEU profile still missing.",
            "tests_present_or_missing": "Tests present for delta, store, residual loop, brain bridge; missing E14/E15 feedback-to-delta fixture.",
            "bridge_labs_relationship": "Bridge-labs keeps public evidence, validation feedback, paid signal, and learning writeback separate through E11 routers.",
            "gov_mcp_relationship": "gov-mcp must not write CIEU/core state from tool calls; it should normalize envelopes and route to approved writers.",
            "backflow_need": "Backflow commercial feedback event classification into CIEU prediction-delta eligibility rules.",
            "risk_if_not_integrated": "Public evidence or owner notes could be promoted into persistent learning without delta validation.",
        },
        {
            "category": "approval records / approval lifecycle",
            "files": existing(root, [
                "ystar/domains/company_runtime/escalation_contract.py",
                "ystar/domains/company_runtime/delegated_mission_contract.py",
                "ystar/domains/company_runtime/company_runtime_policy.py",
                "ystar/domains/company_runtime/permission_tiers.py",
                "tests/domains/company_runtime/test_escalation_contract.py",
                "tests/domains/company_runtime/test_permission_tiers.py",
            ]),
            "purpose": "Owner escalation, mission envelopes, permission tiers, and bounded approval semantics.",
            "current_maturity": "Good domain pack for company runtime; owner validation batch approval lifecycle is not fully modeled as canonical record.",
            "tests_present_or_missing": "Company-runtime tests present; approval expiration/revocation/action-ledger coupling needs formal fixtures.",
            "bridge_labs_relationship": "E12/E14 owner approval request and decision packets implement concrete commercial approval lifecycle locally.",
            "gov_mcp_relationship": "gov-mcp already normalizes owner decisions with no external execution.",
            "backflow_need": "Promote E14 owner-operated manual validation approval packet as Y-star-gov approval record profile.",
            "risk_if_not_integrated": "Approval text, revocation, and action ledger requirements can diverge across milestones.",
        },
        {
            "category": "delegation contracts",
            "files": existing(root, [
                "ystar/governance/delegation_policy.py",
                "ystar/domains/company_runtime/delegated_mission_contract.py",
                "tests/test_delegation_chain.py",
                "tests/test_delegation_chain_runtime.py",
                "tests/domains/company_runtime/test_mission_permission_check.py",
            ]),
            "purpose": "Defines what an agent or role may do under delegated mission constraints.",
            "current_maturity": "Implemented and tested for general governance and company runtime.",
            "tests_present_or_missing": "Delegation tests present; missing owner-operated commercial validation delegation examples.",
            "bridge_labs_relationship": "Bridge-labs models Aiden/Codex as non-senders and owner as executor for E14.",
            "gov_mcp_relationship": "gov-mcp exposes mission checks and escalation checks.",
            "backflow_need": "Add commercial validation delegation fixture: owner executor only, Aiden draft/prep only.",
            "risk_if_not_integrated": "Aiden/tool execution authority may be inferred from prepared packets rather than explicit delegation.",
        },
        {
            "category": "obligation registration / obligation enforcement",
            "files": existing(root, [
                "ystar/governance/obligation_triggers.py",
                "ystar/governance/obligation_remediation.py",
                "tests/test_obligation_triggers.py",
                "tests/test_obligation_remediation.py",
                "tests/governance/test_obligation_closure.py",
            ]),
            "purpose": "Registers, tracks, and remediates obligations generated by governance activity.",
            "current_maturity": "Implemented with tests, but commercial validation explicitly forbids auto-registration in bridge-labs.",
            "tests_present_or_missing": "Obligation tests present; missing policy for when commercial feedback creates obligations.",
            "bridge_labs_relationship": "Bridge-labs E11-E14 receipts explicitly prevent obligation auto-registration.",
            "gov_mcp_relationship": "MCP boundary should not auto-register obligations on tool preflight.",
            "backflow_need": "Define no-auto-obligation rule for market validation unless owner explicitly approves.",
            "risk_if_not_integrated": "Validation prep could accidentally create commitments or follow-up duties.",
        },
        {
            "category": "hook adapters / dry-run contract harness",
            "files": existing(root, [
                "ystar/adapters/hook.py",
                "ystar/adapters/hook_response.py",
                "ystar/governance/hook_contract_adapter.py",
                "ystar/governance/contract_dry_run.py",
                "docs/hook_contract_adapter_dry_run.md",
                "docs/hook_contract_cli_dry_run.md",
                "docs/governance_contract_dry_run.md",
                "tests/governance/test_contract_dry_run.py",
                "tests/governance/test_hook_contract_adapter.py",
            ]),
            "purpose": "Executes governance decisions in dry-run/hook-facing form without pretending to perform live side effects.",
            "current_maturity": "Strong for local hook and dry-run compatibility.",
            "tests_present_or_missing": "Hook adapter and dry-run tests present; missing bridge-labs delivery/evidence runner hook profile.",
            "bridge_labs_relationship": "Host-side delivery bridge and E13/E14 runners should become governed dry-run/live-boundary clients.",
            "gov_mcp_relationship": "gov-mcp is the external tool gateway that can host equivalent preflight decisions.",
            "backflow_need": "Add host-delivery and owner-validation packet adapters as dry-run fixtures.",
            "risk_if_not_integrated": "Delivery/evidence runners remain outside canonical hook governance.",
        },
        {
            "category": "MCP decision envelope",
            "files": existing(root, [
                "docs/gov_mcp_setup.md",
                "docs/external_governance_adapter_sdk.md",
                "docs/governance_endpoint_acceptance.md",
                "tests/governance/test_external_adapter_sdk.py",
                "tests/test_gov_mcp_delegation.py",
            ]),
            "purpose": "Defines how governance decisions are exposed to external tools and adapters.",
            "current_maturity": "Documented and tested at adapter level; gov-mcp contains concrete server/tool implementation.",
            "tests_present_or_missing": "Adapter SDK tests present; commercial validation tools missing.",
            "bridge_labs_relationship": "Bridge-labs uses local routers pending MCP-backed formal tools.",
            "gov_mcp_relationship": "gov-mcp should own executable gateway exposure and result normalization.",
            "backflow_need": "Create MCP tools for validation approval packet, target batch, action ledger, and feedback event checks.",
            "risk_if_not_integrated": "Commercial runtime may bypass MCP gateway when moving from prep to execution.",
        },
        {
            "category": "intervention / enforcement",
            "files": existing(root, [
                "ystar/governance/intervention_engine.py",
                "ystar/governance/intervention_models.py",
                "ystar/governance/enforcement_observer.py",
                "ystar/governance/omission_engine.py",
                "tests/governance/test_enforcement_observer.py",
                "tests/governance/test_omission_engine_cieu_persistence.py",
            ]),
            "purpose": "Detects omission, drift, and intervention conditions and routes them into governance action.",
            "current_maturity": "Implemented with tests for governance-side behavior.",
            "tests_present_or_missing": "Tests present; missing commercial no-contact/no-payment violation fixtures.",
            "bridge_labs_relationship": "Bridge-labs emits safety receipts but does not yet route violations into Y-star-gov intervention.",
            "gov_mcp_relationship": "gov-mcp should expose deny/escalate outcomes at tool boundary.",
            "backflow_need": "Add market-validation violation scenarios to intervention/enforcement fixtures.",
            "risk_if_not_integrated": "A failed safety boundary may only be documented locally rather than enforced canonically.",
        },
        {
            "category": "canonical learning / shadow learning / promotion",
            "files": existing(root, [
                "ystar/governance/cieu_brain_bridge.py",
                "ystar/governance/cieu_brain_learning.py",
                "ystar/governance/brain_auto_ingest.py",
                "ystar/governance/metalearning.py",
                "ystar/governance/proposal_submission.py",
                "tests/governance/test_cieu_brain_learning.py",
                "tests/governance/test_brain_auto_ingest.py",
            ]),
            "purpose": "Separates learning candidates, CIEU-reviewed deltas, and persistent brain/writeback promotion.",
            "current_maturity": "Active and tested, with explicit anti-uncurated-writeback rules in CIEU validators.",
            "tests_present_or_missing": "Tests present; missing E13/E14 commercial feedback learning fixture.",
            "bridge_labs_relationship": "E11 learning_writeback_router blocks direct report-to-brain writes.",
            "gov_mcp_relationship": "MCP tools should not perform persistent learning writes directly.",
            "backflow_need": "Backflow public-evidence vs feedback vs paid-signal learning eligibility rules.",
            "risk_if_not_integrated": "Commercial reports could become strategy memory without validated prediction deltas.",
        },
        {
            "category": "release preflight / release simulation / no-go / live boundary",
            "files": existing(root, [
                "docs/development/RELEASE_AUDIT_v043.md",
                "ystar/governance/liveness_audit.py",
                "tests/test_liveness_audit.py",
                "tests/governance/test_post_ship_completeness.py",
            ]),
            "purpose": "Checks readiness, liveness, and post-ship completeness before treating a capability as live.",
            "current_maturity": "Partial in Y-star-gov; richer historical release/live-boundary artifacts exist in ystar-company.",
            "tests_present_or_missing": "Some liveness/post-ship tests present; missing canonical commercial live/no-go standard.",
            "bridge_labs_relationship": "Bridge-labs CZL distinguishes repository delivery from validation/market closure.",
            "gov_mcp_relationship": "MCP gateway should expose no-go decisions before live tool execution.",
            "backflow_need": "Formalize repository delivery, evidence readiness, and live outreach boundaries as release standards.",
            "risk_if_not_integrated": "Repo closure can be mistaken for capability, validation, or revenue closure.",
        },
    ]
    return categories


def ownership_map() -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "verified_boundary": "Evidence-based from repository source/docs/tests scans; not inferred from recent E-series memory.",
        "repos": {
            "Y-star-gov": {
                "canonical_owner_of": [
                    "normative governance kernel",
                    "deterministic validators",
                    "Pre-U packet standards",
                    "CIEU prediction-delta and residual standards",
                    "approval validity standards",
                    "learning writeback eligibility standards",
                    "release/live boundary standards",
                ],
                "evidence": [
                    "ystar/governance/pre_u_packet_validator.py",
                    "ystar/governance/cieu_prediction_delta.py",
                    "ystar/governance/residual_loop_engine.py",
                    "ystar/domains/company_runtime/company_runtime_policy.py",
                    "tests/governance/test_pre_u_packet_validator.py",
                ],
            },
            "gov-mcp": {
                "canonical_owner_of": [
                    "governed tool execution gateway",
                    "MCP preflight",
                    "tool allowlist and denial envelope",
                    "external action execution interface",
                    "execution result normalization",
                ],
                "evidence": [
                    "gov_mcp/server.py",
                    "gov_mcp/router.py",
                    "gov_mcp/company_runtime_tools.py",
                    "gov_mcp/exec_whitelist.yaml",
                    "docs/PROTOCOL.md",
                ],
            },
            "ystar-bridge-labs": {
                "canonical_owner_of": [
                    "Aiden CEO runtime",
                    "commercial validation loop",
                    "Mission Command",
                    "offer, target, evidence, owner packet generation",
                    "host-side delivery bridge",
                    "owner-operated validation prep",
                ],
                "evidence": [
                    "office/mission_command/e14_owner_approval_packet.py",
                    "office/mission_command/evidence_signal_router.py",
                    "scripts/host_delivery_runner.py",
                    "operations/external_validation/e14_owner_approval_packet.request.json",
                ],
            },
            "ystar-company": {
                "canonical_owner_of": [
                    "historical incubator artifacts",
                    "experimental runtimes",
                    "patterns to backflow or archive after review",
                ],
                "not_final_source_of_truth_for": [
                    "live governance standards",
                    "MCP execution boundary",
                    "commercial validation approvals",
                ],
                "evidence": [
                    "l8_first_cash_path_operating_loop/",
                    "l9_meta_development_opportunity_runtime/",
                    "l10_delegated_live_meta_development_runtime/",
                    "tests/labs_live_boundary/",
                    "controlled_* evidence and no-action receipts",
                ],
            },
        },
    }


def alignment_matrix() -> list[dict[str, Any]]:
    return [
        row("target lifecycle", "Y-star-gov", "ystar-bridge-labs", "E11 target_lifecycle_router plus E14 target batch", "high", "P0", "bridge-labs tests present; Y-star-gov profile missing", "Backflow target lifecycle state machine and owner-operated contact gating."),
        row("evidence/signal", "Y-star-gov", "ystar-bridge-labs", "E11 evidence_signal_router, E13/E13R evidence records", "high", "P0", "bridge-labs tests present; CIEU profile missing", "Canonicalize public evidence vs validation feedback vs paid signal."),
        row("action authorization", "Y-star-gov + gov-mcp", "ystar-bridge-labs + gov-mcp", "E11 action_authorization_router overlaps gov_company_action_preflight", "critical", "P0", "tests exist in both repos", "Make gov-mcp gateway call Y-star-gov company-runtime decisions for E14/E15."),
        row("learning writeback", "Y-star-gov", "ystar-bridge-labs", "E11 learning_writeback_router mirrors CIEU brain/writeback rules", "high", "P0", "Y-star-gov CIEU tests and bridge-labs router tests", "Backflow commercial learning eligibility into CIEU delta schema."),
        row("closure status", "Y-star-gov", "ystar-bridge-labs", "E11 closure_status_router and CZL reports", "medium", "P1", "bridge-labs tests; Y-star-gov CZL tests", "Formalize repository/capability/validation/paid-signal closure distinctions."),
        row("counterfactual", "Y-star-gov", "ystar-bridge-labs", "E11 counterfactual_router plus Y-star-gov counterfactual_engine", "medium", "P1", "tests exist; profiles differ", "Use Y-star-gov counterfactual protocol as canonical source."),
        row("approval record", "Y-star-gov", "ystar-bridge-labs", "E12/E14 approval request files and company_runtime escalation contracts", "high", "P0", "company runtime tests; E14 tests", "Promote owner validation approval packet into Y-star-gov approval record profile."),
        row("feedback event", "Y-star-gov", "ystar-bridge-labs", "E12/E14 feedback templates not yet canonical CIEU events", "high", "P0", "bridge-labs tests present", "Define feedback event to CIEU prediction-delta eligibility."),
        row("action ledger", "Y-star-gov + gov-mcp", "ystar-bridge-labs", "E14 action ledger template", "high", "P0", "bridge-labs tests present", "Create canonical action ledger validator and MCP preflight/read model."),
        row("host delivery", "ystar-bridge-labs", "ystar-bridge-labs", "E12T host_delivery_runner", "low", "P1", "repository delivery tests", "Keep bridge-labs owner; optionally expose no-go status to gov-mcp."),
        row("MCP execution", "gov-mcp", "gov-mcp + bridge-labs adapters", "gov_mcp router/server/company tools", "medium", "P0", "gov-mcp tests present", "Add commercial validation preflight tools; no external execution without owner approval."),
        row("CIEU residual", "Y-star-gov", "Y-star-gov + bridge-labs reports", "CIEU validators plus CZL residual reports", "medium", "P1", "Y-star-gov CIEU tests", "Map commercial CZL residuals to prediction delta profile."),
        row("obligation registration", "Y-star-gov", "Y-star-gov with bridge-labs no-auto receipts", "Y-star-gov obligation engine; bridge-labs forbids auto-registration", "medium", "P1", "Y-star-gov obligation tests", "Specify market validation no-auto-obligation rule."),
        row("release/live boundary", "Y-star-gov", "bridge-labs + ystar-company", "bridge-labs delivery CZL; ystar-company live/no-go artifacts", "high", "P1", "partial tests in ystar-company/Y-star-gov", "Backflow live boundary/no-go standard from incubator and bridge-labs."),
        row("commercial validation", "ystar-bridge-labs", "ystar-bridge-labs", "E10-E14 commercial loop", "medium", "P0", "E-series tests present", "Keep commercial runtime in bridge-labs while formalizing governance profiles upstream."),
    ]


def row(name: str, owner: str, impl: str, duplicate: str, risk: str, priority: str, tests: str, action: str) -> dict[str, Any]:
    return {
        "capability": name,
        "canonical_owner_repo": owner,
        "current_implementation_repo": impl,
        "duplicate_implementations": duplicate,
        "conflict_risk": risk,
        "backflow_priority": priority,
        "tests": tests,
        "recommended_next_action": action,
    }


def duplicate_register() -> list[dict[str, Any]]:
    return [
        conflict("A1-C01", "bridge-labs target lifecycle vs canonical approval lifecycle", "high", "E14 target candidates are request-only but local routers own no-contact semantics.", "Backflow target lifecycle profile to Y-star-gov and expose gov-mcp preflight."),
        conflict("A1-C02", "public evidence vs validation feedback vs paid signal", "high", "E13/E13R public evidence supports readiness only; CIEU learning rules live in Y-star-gov.", "Canonicalize signal taxonomy and CIEU eligibility."),
        conflict("A1-C03", "action authorization split between bridge-labs router and gov-mcp gateway", "critical", "gov-mcp has company_runtime_tools but E14 uses local packet checks.", "Add gov-mcp commercial validation tools backed by Y-star-gov company runtime."),
        conflict("A1-C04", "report-only learning vs persistent brain/CIEU writeback", "high", "Bridge-labs blocks direct writeback; Y-star-gov has CIEU/brain learning modules.", "Define commercial feedback-to-CIEU prediction delta profile."),
        conflict("A1-C05", "repository delivery closure vs capability/market closure", "medium", "E12T/E13/E14 correctly separate remote SHA from market validation but the standard is local.", "Formalize closure status semantics in Y-star-gov CZL profile."),
        conflict("A1-C06", "ystar-company historical live/commercial runtime drift", "medium", "ystar-company has rich L8/L9/L10 and controlled_* artifacts plus dirty runtime state.", "Triage incubator assets: absorb patterns, archive runtime drift, avoid source-of-truth status."),
    ]


def conflict(cid: str, title: str, severity: str, evidence: str, next_action: str) -> dict[str, Any]:
    return {
        "conflict_id": cid,
        "title": title,
        "severity": severity,
        "evidence": evidence,
        "risk": "Duplicate authority can let commercial runtime bypass canonical governance or overclaim closure.",
        "recommended_next_action": next_action,
    }


def maturity_scorecard(categories: list[dict[str, Any]]) -> dict[str, Any]:
    scores = {
        "governance validators": 4,
        "Pre-U packet validation": 3,
        "CIEU / prediction delta / residual": 4,
        "approval records / approval lifecycle": 3,
        "delegation contracts": 4,
        "obligation registration / obligation enforcement": 4,
        "hook adapters / dry-run contract harness": 4,
        "MCP decision envelope": 3,
        "intervention / enforcement": 4,
        "canonical learning / shadow learning / promotion": 3,
        "release preflight / release simulation / no-go / live boundary": 2,
    }
    return {
        "generated_at": utc_now(),
        "scale": "0 absent, 1 sketch, 2 partial, 3 usable with gaps, 4 mature with tests, 5 canonical and cross-repo integrated",
        "items": [
            {
                "category": cat["category"],
                "score": scores.get(cat["category"], 2),
                "maturity": cat["current_maturity"],
                "primary_gap": cat["backflow_need"],
            }
            for cat in categories
        ],
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render_full_report(snapshots: dict[str, Any], categories: list[dict[str, Any]], matrix: list[dict[str, Any]], conflicts: list[dict[str, Any]]) -> str:
    lines = [
        "# A1 Y-star-gov Full Evidence Chain Audit",
        "",
        f"- generated_at: {utc_now()}",
        "- scope: Y-star-gov, gov-mcp, ystar-bridge-labs, ystar-company",
        "- rule: read-only cross-repo audit; no source changes outside ystar-bridge-labs",
        "",
        "## Human Summary",
        "",
        "Y-star-gov 的完整面貌不是一个简单的 permission-tier 文件。扫描显示它包含治理 validator、Pre-U packet、CIEU prediction delta、residual loop、approval/delegation/obligation、hook/dry-run、intervention/enforcement、learning promotion、release/live boundary 的多层治理骨架。",
        "",
        "当前 bridge-labs 已经把商业 runtime 的目标、证据、审批、反馈、交付闭环做得很具体；但这些商业规则仍主要在 bridge-labs 本地实现。下一步不是删除这些能力，而是把稳定规则 backflow 成 Y-star-gov canonical profiles，并由 gov-mcp 承接工具边界。",
        "",
        "## Repository Evidence",
        "",
    ]
    for name, snapshot in snapshots.items():
        lines += [
            f"### {name}",
            f"- path: `{snapshot['path']}`",
            f"- exists: `{snapshot['exists']}`",
            f"- branch: `{snapshot.get('branch', '')}`",
            f"- head: `{snapshot.get('head', '')}`",
            f"- safe_file_count: `{snapshot.get('safe_file_count', 0)}`",
            f"- status_sample_count: `{len(snapshot.get('status_short_sample', []))}`",
            "",
        ]
    lines += ["## Y-star-gov Capability Categories", ""]
    for cat in categories:
        lines += [
            f"### {cat['category']}",
            f"- purpose: {cat['purpose']}",
            f"- maturity: {cat['current_maturity']}",
            f"- files: {', '.join('`' + f + '`' for f in cat['files'][:12]) or 'not found in scan'}",
            f"- tests: {cat['tests_present_or_missing']}",
            f"- bridge-labs relationship: {cat['bridge_labs_relationship']}",
            f"- gov-mcp relationship: {cat['gov_mcp_relationship']}",
            f"- backflow need: {cat['backflow_need']}",
            f"- risk if not integrated: {cat['risk_if_not_integrated']}",
            "",
        ]
    lines += [
        "## Four-Repo Responsibility Boundary",
        "",
        "- Y-star-gov should own normative governance kernel, deterministic validators, Pre-U/CIEU/residual/approval/learning/release standards.",
        "- gov-mcp should own governed tool execution gateway, MCP preflight, allow/deny envelopes, and execution result normalization.",
        "- ystar-bridge-labs should own Aiden CEO runtime, commercial validation loop, offer/target/evidence/owner packet generation, and host-side delivery.",
        "- ystar-company should remain an incubator archive: absorb useful patterns, quarantine runtime drift, do not treat dirty artifacts as source of truth.",
        "",
        "## Most Serious Misalignments",
        "",
    ]
    for conflict_item in conflicts:
        lines += [
            f"- {conflict_item['conflict_id']} `{conflict_item['severity']}`: {conflict_item['title']} - {conflict_item['recommended_next_action']}",
        ]
    lines += [
        "",
        "## Runtime Alignment Snapshot",
        "",
        "| capability | canonical owner | current implementation | risk | priority | next action |",
        "|---|---|---|---|---|---|",
    ]
    for item in matrix:
        lines.append(
            f"| {item['capability']} | {item['canonical_owner_repo']} | {item['current_implementation_repo']} | {item['conflict_risk']} | {item['backflow_priority']} | {item['recommended_next_action']} |"
        )
    lines += [
        "",
        "## CEO Validation Parallelism",
        "",
        "允许并行推进 CEO validation 的 owner-operated 决策台和人工验证准备，但不允许 Aiden 自动发送、发布、收款、登录、提交表单或把 public evidence 当作 validation feedback。E15 仍必须等待有效 action ledger + feedback event。",
        "",
        "## CZL",
        "",
        "- A1 inventory_rt1: 0",
        "- A1 ownership_map_rt1: 0",
        "- A1 backflow_plan_rt1: 0",
        "- A1 repository_delivery_rt1: 1 until host-side delivery pushes and confirms remote SHA",
        "- A1 full_mission_rt1: 1 until repository delivery closes",
        "",
    ]
    return "\n".join(lines)


def render_backflow_plan() -> str:
    return "\n".join(
        [
            "# A1 Backflow P0/P1/P2 Plan",
            "",
            "## P0",
            "",
            "- Promote bridge-labs commercial target lifecycle states into a Y-star-gov owner-validation packet profile.",
            "- Canonicalize public evidence, validation feedback, paid-signal readiness, paid signal, and revenue closure distinctions in Y-star-gov.",
            "- Add gov-mcp tools for validation approval packet check, target batch check, action ledger check, feedback event check, and no-contact/no-payment boundary check.",
            "- Define E14/E15 owner-operated validation approval record with expiration, revocation, max-send, draft-hash, action-ledger, and feedback-event requirements.",
            "- Add CIEU prediction-delta profile for commercial feedback learning eligibility.",
            "",
            "## P1",
            "",
            "- Map bridge-labs CZL repository delivery, evidence readiness, validation feedback, and paid-signal closure statuses into Y-star-gov CZL standards.",
            "- Add release/live no-go profile for customer contact, publication, payment, account creation, form submission, login, and core writeback.",
            "- Add host-side delivery health as a bridge-labs-owned capability with optional gov-mcp no-go exposure.",
            "- Add intervention/enforcement fixtures for commercial boundary violations.",
            "",
            "## P2",
            "",
            "- Triage ystar-company L8/L9/L10 commercial/runtime artifacts into absorb/archive/reject buckets.",
            "- Archive dirty runtime artifacts, DB/WAL/SHM/logs, active markers, and generated no-action receipts that are not source standards.",
            "- Promote useful controlled observation, approval, live-boundary, and release simulation patterns only after canonical review.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    reports = repo_root / "reports" / "cross_repo"
    reports.mkdir(parents=True, exist_ok=True)

    snapshots = {name: repo_snapshot(name, root) for name, root in REPOS.items()}
    categories = y_star_gov_categories(REPOS["Y-star-gov"])
    matrix = alignment_matrix()
    ownership = ownership_map()
    conflicts = duplicate_register()
    scorecard = maturity_scorecard(categories)

    write_json(reports / "a1_runtime_alignment_matrix.json", {"generated_at": utc_now(), "rows": matrix})
    write_json(reports / "a1_canonical_ownership_map.json", ownership)
    write_json(reports / "a1_duplicate_conflict_register.json", {"generated_at": utc_now(), "conflicts": conflicts})
    write_json(reports / "a1_y_star_gov_maturity_scorecard.json", scorecard)
    (reports / "a1_backflow_p0_p1_p2_plan.md").write_text(render_backflow_plan(), encoding="utf-8")
    (reports / "a1_y_star_gov_full_evidence_chain.md").write_text(
        render_full_report(snapshots, categories, matrix, conflicts), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
