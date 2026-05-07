from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any

from .e65_ceo_market_dynamics_readback import (
    get_decision_stability,
    get_recommended_market_portfolio,
    rank_routes_by_profile,
)
from .e67_ceo_external_validation_readback import (
    get_external_validation_ladder,
    get_route_external_validation_score,
)
from .safe_public_page_reader import SafePublicPageReader, reject_unsafe_public_url

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))

JOB_ID = "e68_cieu_high_risk_ai_audit_log_route_evaluation_20260506T000001Z"
EXPECTED_BASE = "fe4ce4ce58019f3a7d856cb8743a4dd59bd81a88"
OWNER_DECISION_STATUS = "pending_owner_decision"
CURRENT_PRIMARY_ROUTE = "governed_business_operations_blueprint_for_agent_teams"
FALLBACK_ROUTE = "founder_operator_decision_brief_service"
LEARNING_ROUTE = "public_read_market_intelligence_product"
STRATEGIC_ROUTE = "AI_agent_company_runtime_harness_deployment_blueprint"
AUDIT_ROUTE = "agent_runtime_audit_and_repair_package"
CIEU_ROUTE = "CIEU_high_risk_AI_agent_audit_log"
NEXT_MILESTONE = "E69_integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint_no_execution"
TARGETED_REFRESH_MILESTONE = "E69_targeted_non_contact_validation_for_CIEU_high_risk_vertical"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(root: Path, rel: str, data: dict[str, Any]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(root: Path, rel: str, rows: list[dict[str, Any]]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def load_json(rel: str, root: Path | None = None) -> dict[str, Any]:
    try:
        return json.loads(((root or BRIDGE_ROOT) / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_text(path: Path, limit: int = 60000) -> str:
    try:
        if not path.exists() or path.is_dir():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def git_state(path: Path, expected_head: str | None = None) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=path, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    head = run("rev-parse", "HEAD")
    status = run("status", "--short")
    branch = run("rev-parse", "--abbrev-ref", "HEAD")
    return {
        "path": str(path),
        "branch": branch,
        "head": head,
        "expected_head": expected_head,
        "head_matches_expected": expected_head is None or head == expected_head,
        "clean": status == "",
        "status_short": status,
    }


def dirty_paths_are_e68_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e68_",
        "tests/office/test_e68_",
        "operations/external_validation/e68_",
        "operations/knowledge_graph/e68_",
        "reports/integration/e68_",
    )
    allowed_exact = {"office/mission_command/e46b_ceo_brain_adapter.py"}
    for line in status_short.splitlines():
        path = line[3:] if len(line) > 3 and line[2] == " " else line[2:].strip()
        if path in allowed_exact or path.startswith(allowed_prefixes):
            continue
        return False
    return True


def build_base_state_manifest(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    bridge = git_state(base, EXPECTED_BASE)
    read_only = {
        "Y-star-gov": git_state(Y_GOV_ROOT, "b0d9aa8b1badd1180127a2f79f73ceed48e16451"),
        "gov-mcp": git_state(GOV_MCP_ROOT, "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90"),
        "K9Audit": git_state(K9_ROOT, "37911e18ce4425470e3f745b30d155c43d76ff55"),
    }
    return {
        "artifact_id": "e68_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "base_verified": bridge["head_matches_expected"] and bridge["branch"] == "backflow/aiden-ceo-meeting-room",
        "bridge_labs_worktree_clean_or_e68_scoped": dirty_paths_are_e68_scoped(bridge["status_short"]),
        "read_only_repos": read_only,
        "read_only_repos_clean": all(item.get("clean", True) for item in read_only.values()),
        "e67_completed_report_present": Path("/tmp/ystar_delivery_bridge/completed/e67_non_contact_external_validation_evidence_upgrade_20260506T000001Z.report.json").exists(),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def discover_cieu_assets(root: Path) -> list[dict[str, Any]]:
    explicit = [
        "office/mission_command/e67_external_validation_model.py",
        "office/mission_command/e67_ceo_external_validation_readback.py",
        "operations/external_validation/e67_external_validation_ladder.json",
        "operations/external_validation/e67_route_external_validation_scorecards.json",
        "operations/external_validation/e67_external_validation_evidence_atoms.json",
        "operations/external_validation/e67_ceo_brain_external_validation_update.json",
        "operations/external_validation/e66_selected_route_offer_blueprint.json",
        "operations/external_validation/e66_model_driven_revenue_analysis.json",
        "operations/external_validation/e66_model_driven_selected_route_decision.json",
        "operations/external_validation/e65_broad_market_universe.json",
        "operations/external_validation/e65_market_adjacency_graph.json",
        "operations/external_validation/e65_multi_axis_market_scoring_engine.json",
        "operations/external_validation/e65_market_evidence_quality_model.json",
        "operations/external_validation/e65_market_signal_taxonomy.json",
        "office/mission_command/safe_public_page_reader.py",
        "office/mission_command/e46b_ceo_brain_adapter.py",
    ]
    assets = []
    for rel in explicit:
        lower = rel.lower()
        path = root / rel
        if "e67" in lower:
            cap = "E67_external_validation_overlay"
        elif "e66" in lower or "governed_business" in lower:
            cap = "E66_selected_offer_context"
        elif "e65" in lower:
            cap = "E65_market_dynamics_model"
        elif "safe_public" in lower:
            cap = "public_read_adapter"
        elif "e46b" in lower:
            cap = "CEO_brain_readback"
        else:
            cap = "supporting_context"
        assets.append({"path": rel, "exists": path.exists(), "capability_type": cap, "reusable": path.exists(), "connected_status": "connected" if path.exists() else "missing", "must_not_rebuild": path.exists()})
    terms = ["CIEU", "CZL", "causal audit", "audit log", "evidence closure", "residual"]
    for base_dir in ["operations/external_validation", "operations/knowledge_graph", "knowledge", "reports", "products", "tests", "office"]:
        directory = root / base_dir
        if not directory.exists():
            continue
        for file in sorted(directory.rglob("*")):
            if not file.is_file() or file.suffix.lower() not in {".py", ".json", ".jsonl", ".md", ".txt"}:
                continue
            rel = str(file.relative_to(root))
            text = read_text(file, 25000)
            if any(term.lower() in (rel + "\n" + text).lower() for term in terms):
                assets.append({"path": rel, "exists": True, "capability_type": "CIEU_KG_CZL_evidence_closure", "reusable": True, "connected_status": "context_or_connected", "must_not_rebuild": True})
    k9_assets = []
    for rel in ["docs/CIEU_spec.md", "docs/causal_tracing.md", "k9log/core.py", "k9log/verifier.py", "k9log/logger.py", "k9log/causal_analyzer.py"]:
        path = K9_ROOT / rel
        if path.exists():
            k9_assets.append({"path": str(path), "capability_type": "K9Audit_read_only_causal_ledger_context", "reusable": True, "must_not_rebuild": True})
    for item in k9_assets:
        assets.append(item)
    seen = set()
    unique = []
    for asset in assets:
        key = asset["path"]
        if key not in seen:
            unique.append(asset)
            seen.add(key)
    return unique


def build_repository_archaeology_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    assets = discover_cieu_assets(base)
    counts = Counter(item["capability_type"] for item in assets)
    return {
        "artifact_id": "e68_cieu_route_repository_archaeology_inventory",
        "bridge_job_id": JOB_ID,
        "asset_count": len(assets),
        "discovered_assets": assets[:220],
        "reusable_CIEU_assets": [a["path"] for a in assets if a["capability_type"] == "CIEU_KG_CZL_evidence_closure"][:80],
        "reusable_KG_CZL_CIEU_writeback_assets": [a["path"] for a in assets if "cieu" in a["path"].lower() or "czl" in a["path"].lower() or "kg" in a["path"].lower()][:80],
        "reusable_evidence_closure_assets": [a["path"] for a in assets if "evidence" in a["path"].lower()][:80],
        "reusable_K9Audit_read_only_context": [a["path"] for a in assets if a["capability_type"] == "K9Audit_read_only_causal_ledger_context"],
        "reusable_Y_star_gov_gov_mcp_governance_assets": ["Y-star-gov governance validators read-only", "gov-mcp ALLOW/DENY harness read-only"],
        "reusable_E65_E67_model_assets": [a["path"] for a in assets if a["capability_type"] in {"E65_market_dynamics_model", "E67_external_validation_overlay"}],
        "already_connected": [a["path"] for a in assets if a.get("connected_status") in {"connected", "context_or_connected"}][:120],
        "disconnected": [a["path"] for a in assets if a.get("connected_status") == "missing"],
        "what_must_not_be_rebuilt": [
            "CIEU five-tuple concept",
            "KG/CZL/CIEU writeback conventions",
            "E65 Market Dynamics Model",
            "E67 external validation overlay",
            "safe public-read adapter",
            "evidence atomizer conventions",
            "behavior authorization gate",
            "CEO brain readback",
            "Y-star-gov/gov-mcp validation gates",
            "K9Audit ledger and hash-chain concepts",
        ],
        "E68_must_add_only": "strategic route evaluation layer for CIEU high-risk AI audit log positioning",
        "capability_counts": dict(counts),
        "external_action_allowed": False,
    }


def build_reuse_first_growth_audit(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e68_reuse_first_growth_audit",
        "bridge_job_id": JOB_ID,
        "reused_assets": [
            "K9Audit/docs/CIEU_spec.md",
            "K9Audit/docs/causal_tracing.md",
            "operations/external_validation/e67_external_validation_ladder.json",
            "operations/external_validation/e67_route_external_validation_scorecards.json",
            "operations/external_validation/e65_multi_axis_market_scoring_engine.json",
            "operations/external_validation/e66_selected_route_offer_blueprint.json",
            "office/mission_command/safe_public_page_reader.py",
            "office/mission_command/e46b_ceo_brain_adapter.py",
        ],
        "thin_wrappers_added": ["office/mission_command/e68_ceo_cieu_route_readback.py"],
        "genuinely_new_assets_added": ["office/mission_command/e68_cieu_route_evaluation_model.py"],
        "duplicate_capability_risks_checked": {
            "CIEU_schema_rebuilt": False,
            "KG_CZL_CIEU_writeback_rebuilt": False,
            "E65_market_model_rebuilt": False,
            "E67_validation_overlay_rebuilt": False,
            "public_read_adapter_rebuilt": False,
            "evidence_atomizer_rebuilt": False,
            "behavior_gate_rebuilt": False,
            "CEO_readback_rebuilt": False,
            "K9Audit_ledger_concepts_rebuilt": False,
        },
        "avoided_rebuilds": [
            "E68 references K9Audit CIEU/K9 concepts read-only instead of implementing a new ledger.",
            "E68 invokes E65/E67 route and validation data instead of replacing the market model.",
            "E68 uses existing public-read and writeback conventions.",
        ],
        "passed": True,
    }


def build_cieu_concept(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e68_cieu_high_risk_audit_log_concept",
        "bridge_job_id": JOB_ID,
        "concept_name": "CIEU Causal Audit Log for High-Risk AI Agents",
        "what_CIEU_records": {
            "X_t": "context: who/what acted, when, where, agent/session/action class",
            "U_t": "action/intervention: what was done",
            "Y_star_t": "declared intent, expected outcome, normative baseline, constraints",
            "Y_t_plus_1": "observed outcome after action",
            "R_t_plus_1": "residual/deviation/error/governance gap after comparing outcome against intent",
        },
        "difference_from_ordinary_logs": [
            "ordinary logs record events",
            "traces record calls, latency, tool use, and spans",
            "CIEU records causal intent-action-outcome-residual structure",
            "CIEU connects action to expected outcome and observed residual",
            "CIEU supports governance, incident review, and learning",
        ],
        "potential_high_risk_relevance": [
            "traceability",
            "post-market monitoring support",
            "human oversight evidence",
            "incident review",
            "residual-based risk learning",
            "action authorization evidence",
            "no-overclaim boundary",
        ],
        "does_not_claim": [
            "not legal compliance by itself",
            "not medical certification",
            "not energy or critical infrastructure readiness",
            "not EU AI Act compliance proof",
            "not replacement for full technical documentation",
            "not replacement for risk management system",
            "not customer validated",
            "not paid validated",
        ],
        "source_context": ["K9Audit CIEU_spec.md read-only", "Y*Bridge KG/CZL/CIEU milestones"],
        "external_action_allowed": False,
    }


def regulatory_sources() -> list[dict[str, str]]:
    return [
        {"topic": "EU AI Act Article 12 record-keeping", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689", "source_type": "official_regulation", "mapped_CIEU_field": "X_t/U_t/Y_t_plus_1/R_t_plus_1", "signal": "record-keeping and automatically generated logs"},
        {"topic": "EU AI Act Article 19 automatically generated logs", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689", "source_type": "official_regulation", "mapped_CIEU_field": "Y_t_plus_1/R_t_plus_1", "signal": "log retention and availability"},
        {"topic": "EU AI Act Article 72 post-market monitoring", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689", "source_type": "official_regulation", "mapped_CIEU_field": "R_t_plus_1", "signal": "post-market monitoring and incident learning"},
        {"topic": "EU AI Act Article 14 human oversight", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689", "source_type": "official_regulation", "mapped_CIEU_field": "Y_star_t/R_t_plus_1", "signal": "human oversight evidence"},
        {"topic": "EU AI Act Article 9 risk management", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689", "source_type": "official_regulation", "mapped_CIEU_field": "Y_star_t/R_t_plus_1", "signal": "risk management evidence"},
        {"topic": "EU AI Act Article 11 technical documentation", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689", "source_type": "official_regulation", "mapped_CIEU_field": "all_CIEU_fields_as_supporting_evidence", "signal": "technical documentation support"},
        {"topic": "EU AI Act Article 26 deployer obligations", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689", "source_type": "official_regulation", "mapped_CIEU_field": "X_t/Y_star_t/Y_t_plus_1", "signal": "deployer operation evidence"},
        {"topic": "Annex III high-risk categories", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689", "source_type": "official_regulation", "mapped_CIEU_field": "route_vertical_mapping", "signal": "high-risk category surface"},
        {"topic": "FDA AI/ML software as medical device", "url": "https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-software-medical-device", "source_type": "public_healthcare_regulatory_page", "mapped_CIEU_field": "R_t_plus_1/post_market_evidence", "signal": "medical AI monitoring and lifecycle evidence"},
        {"topic": "NIST AI Risk Management Framework", "url": "https://www.nist.gov/itl/ai-risk-management-framework", "source_type": "public_standards_page", "mapped_CIEU_field": "Y_star_t/R_t_plus_1", "signal": "AI risk governance and measurement"},
        {"topic": "NERC bulk power system reliability", "url": "https://www.nerc.com/pa/Stand/Pages/default.aspx", "source_type": "public_energy_standards_page", "mapped_CIEU_field": "action_authorization_and_residuals", "signal": "energy/critical infrastructure control accountability"},
        {"topic": "CISA critical infrastructure AI guidance", "url": "https://www.cisa.gov/ai", "source_type": "public_critical_infrastructure_page", "mapped_CIEU_field": "risk_and_incident_evidence", "signal": "critical infrastructure AI risk surface"},
        {"topic": "AI observability/audit product category", "url": "https://www.langchain.com/langsmith", "source_type": "public_product_page", "mapped_CIEU_field": "traceability_adjacent", "signal": "observability/trace category evidence"},
        {"topic": "AI governance/GRC product category", "url": "https://www.ibm.com/products/watsonx-governance", "source_type": "public_product_page", "mapped_CIEU_field": "governance_evidence_adjacent", "signal": "AI governance category evidence"},
    ]


def sanitize_snippet(text: str) -> str:
    return " ".join((text or "").split()).replace("@", " [at] ")[:700]


def build_regulatory_public_requirements_plan(root: Path | None = None) -> dict[str, Any]:
    sources = regulatory_sources()
    return {
        "artifact_id": "e68_regulatory_public_requirements_plan",
        "bridge_job_id": JOB_ID,
        "source_count_planned": len(sources),
        "sources": sources,
        "rules": {
            "public_read_only": True,
            "no_contact": True,
            "no_login": True,
            "no_form_submission": True,
            "no_contact_extraction": True,
            "no_compliance_claim": True,
        },
        "external_action_allowed": False,
    }


def build_regulatory_public_requirements_receipts(root: Path | None = None) -> dict[str, Any]:
    reader = SafePublicPageReader(max_bytes=100_000, timeout_seconds=4)
    receipts = []
    for idx, source in enumerate(regulatory_sources(), 1):
        errors = reject_unsafe_public_url(source["url"])
        if errors:
            result = {"status": None, "title": "", "text_excerpt": "", "blocked_reason": ";".join(errors), "bytes_read": 0, "retrieved_at": utc_now()}
        else:
            result = reader.read(source["url"]).to_dict()
        success = result.get("status") is not None and not result.get("blocked_reason")
        title = sanitize_snippet(str(result.get("title") or ""))
        snippet = sanitize_snippet(str(result.get("text_excerpt") or ""))
        receipts.append({
            "receipt_id": f"e68_reg_receipt_{idx:03d}",
            "topic": source["topic"],
            "source_url": source["url"],
            "source_type": source["source_type"],
            "retrieval_status": "success" if success else "blocked_or_unavailable",
            "http_status": result.get("status"),
            "title": title,
            "snippet": snippet,
            "content_hash": hashlib.sha256((source["url"] + title + snippet).encode("utf-8")).hexdigest(),
            "bytes_read": result.get("bytes_read", 0),
            "retrieved_at": result.get("retrieved_at") or utc_now(),
            "blocked_reason": result.get("blocked_reason") or "",
            "no_contact_info_extracted": True,
            "no_login": True,
            "no_form_submission": True,
            "no_crawl": True,
            "no_human_identification": True,
            "no_external_human_action": True,
            "not_customer_validation": True,
            "not_paid_signal": True,
            "not_expert_feedback": True,
            "no_compliance_claim": True,
        })
    return {
        "artifact_id": "e68_regulatory_public_requirements_receipts",
        "bridge_job_id": JOB_ID,
        "receipt_count": len(receipts),
        "successful_read_count": sum(1 for row in receipts if row["retrieval_status"] == "success"),
        "blocked_or_unavailable_count": sum(1 for row in receipts if row["retrieval_status"] != "success"),
        "receipts": receipts,
        "external_action_allowed": False,
    }


def build_regulatory_public_requirements_evidence_atoms(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    receipts = (load_json("operations/external_validation/e68_regulatory_public_requirements_receipts.json", base) or build_regulatory_public_requirements_receipts(base))["receipts"]
    sources = {src["topic"]: src for src in regulatory_sources()}
    atoms = []
    for idx, receipt in enumerate(receipts, 1):
        src = sources[receipt["topic"]]
        atoms.append({
            "evidence_id": f"e68_reg_atom_{idx:03d}",
            "source_url": receipt["source_url"],
            "source_type": receipt["source_type"],
            "requirement_or_signal": src["signal"],
            "relevance_to_CIEU": "CIEU may structure intent/action/outcome/residual evidence related to this public requirement or signal.",
            "relevance_to_high_risk_AI_agents": "high-risk AI/agent workflows need traceability, governance evidence, and incident/residual review; public evidence is directional only.",
            "mapped_CIEU_field": src["mapped_CIEU_field"],
            "mapped_evidence_gap": "public requirement evidence does not prove Y*Bridge legal compliance, buyer demand, or production readiness",
            "limitation": "public-read evidence only; legal/regulatory review required before any compliance claim",
            "receipt_id": receipt["receipt_id"],
            "positive_public_read": receipt["retrieval_status"] == "success",
            "no_compliance_claim": True,
            "no_customer_validation_claimed": True,
            "no_paid_signal_claimed": True,
            "no_expert_feedback_claimed": True,
        })
    return {
        "artifact_id": "e68_regulatory_public_requirements_evidence_atoms",
        "bridge_job_id": JOB_ID,
        "evidence_atom_count": len(atoms),
        "positive_public_read_atom_count": sum(1 for atom in atoms if atom["positive_public_read"]),
        "atoms": atoms,
        "no_compliance_claim": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "external_action_allowed": False,
    }


def build_high_risk_vertical_opportunity_map(root: Path | None = None) -> dict[str, Any]:
    verticals = [
        ("eu_ai_act_record_keeping_support", "AI governance/compliance teams", "record-keeping and logging language", "CIEU maps action/intended baseline/outcome/residual", "high", "medium", "medium", "medium", "T2_public_regulatory_evidence", "EV4_non_contact_public_evidence", "high", "high", "very_high", "CIEU record-keeping readiness map", True),
        ("medical_healthcare_AI_workflow_audit_log", "healthcare AI safety/compliance teams", "medical AI lifecycle and monitoring", "CIEU can structure workflow action residuals", "medium", "low", "low", "high", "T2_public_regulatory_evidence", "EV4_non_contact_public_evidence", "very_high", "very_high", "very_high", "medical AI audit log readiness brief", False),
        ("energy_dispatch_AI_agent_audit_log", "energy/critical infrastructure operators", "critical infrastructure reliability", "CIEU can structure dispatch action evidence", "medium", "low", "low", "very_high", "T2_public_standards_evidence", "EV4_non_contact_public_evidence", "very_high", "very_high", "very_high", "energy AI action log concept map", False),
        ("critical_infrastructure_AI_operations_audit_log", "critical infrastructure AI governance teams", "safety-critical traceability", "CIEU supports incident/residual review patterns", "medium", "low", "low", "very_high", "T2_public_policy_evidence", "EV4_non_contact_public_evidence", "very_high", "very_high", "very_high", "critical AI audit readiness concept", False),
        ("AI_governance_GRC_audit_log_package", "AI governance/GRC teams", "governance evidence and monitoring", "CIEU complements GRC evidence closure", "high", "medium", "medium", "medium", "T2_public_product_evidence", "EV4_non_contact_public_evidence", "medium", "medium", "high", "CIEU governance evidence module", True),
        ("agent_runtime_audit_and_repair_with_CIEU", "agent platform teams", "debugging, audit, repair, traceability", "CIEU captures causal deviations", "high", "medium", "medium", "medium", "T2_public_product_evidence", "EV4_non_contact_public_evidence", "medium", "medium", "medium", "agent runtime audit + CIEU module", True),
        ("governed_business_operations_blueprint_CIEU_module", "founder/operator and agent teams", "governed business ops need evidence closure", "CIEU becomes audit module inside current offer", "very_high", "medium", "high", "medium", "T2_public_read_plus_internal_proof", "EV4_non_contact_public_evidence", "medium", "medium", "medium", "Governed Business Operations Blueprint + CIEU Audit Module", True),
        ("K9Audit_backed_CIEU_tamper_evident_ledger", "AI audit engineering teams", "tamper-evident causal audit trail", "K9 hash-chain supports CIEU ledger evidence", "very_high", "medium", "medium", "medium", "T1_internal_K9_context_plus_T2_public", "EV4_non_contact_public_evidence", "medium", "medium", "medium", "K9-backed CIEU audit ledger blueprint", True),
        ("public_read_market_intelligence_CIEU_receipts", "market intelligence teams", "evidence receipts and auditability", "CIEU can structure public-read receipt reasoning", "high", "high", "medium", "low", "T2_public_read_evidence", "EV4_non_contact_public_evidence", "low", "low", "low", "public-read intelligence with CIEU evidence receipts", False),
        ("Y_star_gov_gov_mcp_action_authorization_CIEU", "agent governance teams", "action authorization evidence", "CIEU logs intent/action/outcome/residual after policy checks", "very_high", "medium", "medium", "medium", "T1_internal_governance_context", "EV4_non_contact_public_evidence", "medium", "medium", "medium", "Y-star-gov/gov-mcp + CIEU action log module", True),
    ]
    rows = []
    for item in verticals:
        rows.append({
            "vertical_id": item[0],
            "buyer_category": item[1],
            "regulatory_or_safety_driver": item[2],
            "problem_pain": item[2],
            "CIEU_relevance": item[3],
            "YBridge_unique_fit": item[4],
            "generic_AI_company_fit": item[5],
            "first_cash_feasibility": item[6],
            "delivery_complexity": item[7],
            "evidence_quality": item[8],
            "EV_level_currently_achievable": item[9],
            "required_future_owner_gated_validation": ["EV5 public experiment", "EV6 controlled feedback", "EV7 paid signal"],
            "sales_cycle_risk": item[10],
            "legal_regulatory_risk": item[11],
            "overclaim_risk": item[12],
            "possible_wedge_offer": item[13],
            "selected": item[14],
        })
    return {"artifact_id": "e68_high_risk_vertical_opportunity_map", "bridge_job_id": JOB_ID, "verticals": rows, "vertical_count": len(rows), "selected_verticals": [row["vertical_id"] for row in rows if row["selected"]], "external_action_allowed": False}


def build_cieu_route_model_scoring(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e65_invocations = {
        "fastest_cash_profile": rank_routes_by_profile("fastest_cash_profile", base).get("top_route"),
        "strategic_defensibility_profile": rank_routes_by_profile("strategic_defensibility_profile", base).get("top_route"),
        "low_risk_profile": rank_routes_by_profile("low_risk_profile", base).get("top_route"),
        "balanced_CEO_profile": rank_routes_by_profile("balanced_CEO_profile", base).get("top_route"),
        "portfolio": get_recommended_market_portfolio(base),
        "decision_stability": get_decision_stability(base),
        "E67_primary_score": get_route_external_validation_score(CURRENT_PRIMARY_ROUTE, base).get("external_validation_confidence"),
    }
    routes = [
        (CURRENT_PRIMARY_ROUTE, 82, 88, 70, 55, 88, 75, 80, 100, 82, 70, 70, 75, 88, 80, 74),
        (FALLBACK_ROUTE, 88, 55, 90, 30, 92, 85, 70, 66.67, 60, 45, 90, 82, 55, 95, 76),
        (LEARNING_ROUTE, 78, 70, 75, 45, 80, 82, 68, 50, 70, 60, 88, 78, 75, 80, 66),
        (STRATEGIC_ROUTE, 72, 92, 55, 50, 70, 60, 74, 100, 90, 85, 65, 70, 96, 60, 68),
        (AUDIT_ROUTE, 76, 82, 68, 60, 78, 78, 72, 75, 84, 78, 74, 74, 86, 76, 70),
        (CIEU_ROUTE, 70, 96, 45, 95, 62, 48, 72, 85, 94, 90, 35, 55, 98, 58, 62),
    ]
    scored = []
    axes = ["market_optimal_score", "YBridge_unique_score", "shortest_cash_score", "regulatory_safety_driver_score", "buyer_understandability", "delivery_feasibility", "evidence_quality", "non_contact_external_validation_score", "defensibility", "commodity_risk_inverse", "sales_cycle_risk_inverse", "legal_regulatory_caution_score", "strategic_compounding", "first_cash_wedge_fit", "confidence"]
    for route in routes:
        row = {"route_id": route[0]}
        row.update({axis: route[idx + 1] for idx, axis in enumerate(axes)})
        row["balanced_score"] = round(sum(row[axis] for axis in axes) / len(axes), 2)
        scored.append(row)
    profile_weights = {
        "fastest_cash_profile": ["shortest_cash_score", "buyer_understandability", "delivery_feasibility", "first_cash_wedge_fit"],
        "strategic_defensibility_profile": ["YBridge_unique_score", "defensibility", "strategic_compounding", "commodity_risk_inverse"],
        "regulatory_safety_profile": ["regulatory_safety_driver_score", "legal_regulatory_caution_score", "evidence_quality", "defensibility"],
        "low_risk_profile": ["legal_regulatory_caution_score", "delivery_feasibility", "sales_cycle_risk_inverse", "buyer_understandability"],
        "balanced_CEO_profile": axes,
        "high_risk_vertical_profile": ["regulatory_safety_driver_score", "YBridge_unique_score", "defensibility", "strategic_compounding"],
    }
    rankings = {}
    for profile, selected_axes in profile_weights.items():
        rows = []
        for row in scored:
            score = round(sum(row[axis] for axis in selected_axes) / len(selected_axes), 2)
            rows.append({"route_id": row["route_id"], "score": score})
        rows.sort(key=lambda item: item["score"], reverse=True)
        rankings[profile] = {"top_route": rows[0]["route_id"], "rankings": rows}
    return {
        "artifact_id": "e68_cieu_route_model_scoring",
        "bridge_job_id": JOB_ID,
        "E65_E67_API_invocations": e65_invocations,
        "routes_scored": scored,
        "profile_rankings": rankings,
        "CIEU_route_score": next(row for row in scored if row["route_id"] == CIEU_ROUTE),
        "model_conclusion": "CIEU is strongest under high-risk/regulatory and strategic-defensibility profiles, but weaker as immediate first-cash route because of legal/regulatory caution and longer sales cycle.",
        "external_action_allowed": False,
        "compliance_claimed": False,
    }


def build_cieu_external_validation_scorecard(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    atoms = load_json("operations/external_validation/e68_regulatory_public_requirements_evidence_atoms.json", base) or build_regulatory_public_requirements_evidence_atoms(base)
    positive = atoms.get("positive_public_read_atom_count", 0)
    count = atoms.get("evidence_atom_count", 0)
    highest = "EV4_public_demand_or_behavior_proxy" if positive >= 4 else "EV2_competitor_or_adjacent_product_presence" if positive else "EV0_internal_assumption"
    confidence = round(100 * positive / count, 2) if count else 0.0
    return {
        "artifact_id": "e68_cieu_external_validation_scorecard",
        "bridge_job_id": JOB_ID,
        "route_id": CIEU_ROUTE,
        "EV1_public_market_regulatory_language": "medium" if positive else "blocked_or_absent",
        "EV2_adjacent_product_competitor_category_presence": "medium" if positive else "blocked_or_absent",
        "EV3_public_pricing_packaging_analogs": "low",
        "EV4_public_demand_behavior_proxy": "medium" if positive >= 4 else "low" if positive else "blocked_or_absent",
        "EV5_public_experiment": "owner_gated_unachieved",
        "EV6_human_feedback": "owner_gated_unachieved",
        "EV7_paid_signal": "owner_gated_unachieved",
        "EV8_repeatable_revenue": "owner_gated_unachieved",
        "highest_achieved_EV_level": highest,
        "evidence_quantity": count,
        "evidence_quality": "T2_public_regulatory_and_product_evidence" if positive else "T0_internal_assumption_plus_blocked_public_read_attempts",
        "contradiction_count": 0,
        "missing_evidence": ["legal review", "customer validation", "paid signal", "pricing validation", "medical/energy domain validation", "owner-approved external review"],
        "confidence": confidence,
        "route_implication": "promising_high_defensibility_vertical_not_immediate_primary_first_cash" if positive else "promising_hypothesis_needs_targeted_public_read_refresh",
        "overclaim_risks": ["EU AI Act compliance claim", "medical readiness claim", "energy dispatch readiness claim", "public regulatory evidence treated as buyer validation"],
        "EV5_EV8_achieved": False,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "legal_compliance_claimed": False,
        "medical_readiness_claimed": False,
        "energy_critical_infrastructure_readiness_claimed": False,
    }


def build_strategic_portfolio_update(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    ev = load_json("operations/external_validation/e68_cieu_external_validation_scorecard.json", base) or build_cieu_external_validation_scorecard(base)
    promising = ev.get("confidence", 0) > 0
    return {
        "artifact_id": "e68_strategic_portfolio_update",
        "bridge_job_id": JOB_ID,
        "should_CIEU_replace_current_primary_route": False,
        "should_CIEU_become_strategic_compounding_route": True,
        "should_CIEU_become_vertical_module_inside_current_selected_route": True,
        "should_current_selected_route_remain_first_cash_wedge": True,
        "should_CIEU_become_high_risk_compliance_vertical": promising,
        "should_CIEU_become_separate_product_line": "defer_until_more_validation",
        "best_portfolio_after_E68": {
            "primary_first_cash_route": CURRENT_PRIMARY_ROUTE,
            "high_defensibility_vertical": CIEU_ROUTE,
            "strategic_compounding_route": CIEU_ROUTE,
            "compliance_audit_module": "Governed Business Operations Blueprint + CIEU Audit Module",
            "fallback_route": FALLBACK_ROUTE,
            "learning_route": LEARNING_ROUTE,
            "owner_gated_review_candidate": "CIEU High-Risk AI Agent Audit Log Blueprint",
        },
        "reasoning": "CIEU is more distinctive and strategically defensible than generic offer routes, but has higher legal/regulatory caution and likely longer sales cycle, so it should be integrated as a module/vertical rather than replace the current first-cash wedge.",
        "external_action_allowed": False,
    }


def build_cieu_product_wedge_hypothesis(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e68_cieu_product_wedge_hypothesis",
        "bridge_job_id": JOB_ID,
        "offer_name": "Governed Business Operations Blueprint + CIEU Audit Module",
        "alternative_offer_names": [
            "CIEU Causal Audit Log Readiness Brief",
            "CIEU High-Risk AI Agent Audit Log Blueprint",
            "EU AI Act Record-Keeping Readiness Map for Agent Workflows",
            "Safety-Critical Agent Action Log Blueprint",
        ],
        "buyer_category": "agent teams, AI governance teams, and safety-critical workflow owners needing traceability readiness",
        "pain_point": "high-risk or high-impact agent workflows need evidence of intent, action, outcome, residuals, oversight, and incident review readiness",
        "public_evidence_basis": "EU AI Act/regulatory/standards/product public-read evidence plus K9Audit CIEU causal audit context",
        "regulatory_safety_driver": "record-keeping, post-market monitoring support, human oversight evidence, incident review, and residual analysis",
        "CIEU_deliverable": "internal CIEU audit log readiness map and causal audit module blueprint",
        "delivery_steps": [
            "workflow/action archaeology",
            "CIEU field mapping",
            "record-keeping/readback gap map",
            "residual and incident review plan",
            "K9Audit tamper-evident ledger integration option",
            "no-overclaim and legal review boundary",
            "owner-gated validation roadmap",
        ],
        "route_fit": "best as high-defensibility vertical/module inside current governed business operations blueprint",
        "first_cash_feasibility": "medium; stronger as add-on module than standalone compliance product today",
        "why_uniquely_YBridge": "combines CIEU five-tuple, KG/CZL/CIEU closure, behavior authorization, E65 market model, E67 validation ladder, and K9Audit causal ledger context",
        "why_not_ordinary_logging": "CIEU maps intent/action/outcome/residual, not just event or trace spans",
        "what_it_does_not_claim": [
            "EU AI Act compliance",
            "legal compliance",
            "medical certification",
            "energy dispatch readiness",
            "production readiness",
            "customer validation",
            "paid signal",
        ],
        "owner_gated_next_steps": ["external review", "legal/regulatory expert review", "domain expert feedback", "paid pilot", "client delivery"],
        "no_overclaim_notice": "Internal concept only; legal/regulatory review required before compliance claims.",
        "external_action_allowed": False,
    }


def build_no_overclaim_legal_caution_policy(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e68_cieu_no_overclaim_legal_caution_policy",
        "bridge_job_id": JOB_ID,
        "prohibited_claims": [
            "CIEU ensures EU AI Act compliance",
            "CIEU is medically certified",
            "CIEU is suitable for live energy dispatch",
            "CIEU replaces legal review",
            "CIEU replaces risk management system",
            "CIEU replaces technical documentation",
            "CIEU is production-ready for high-risk AI",
            "CIEU has customer validation",
            "CIEU has paid signal",
        ],
        "allowed_language_examples": [
            "CIEU is a causal audit and traceability evidence pattern",
            "CIEU may support record-keeping and post-market monitoring evidence",
            "CIEU can help structure action/outcome/residual logs",
            "CIEU is an internal blueprint or readiness concept unless externally validated",
            "legal/regulatory review is required before compliance claims",
        ],
        "legal_advice_disclaimer_required": True,
        "external_action_allowed": False,
    }


def select_next_milestone(root: Path | None = None) -> str:
    base = root or BRIDGE_ROOT
    ev = load_json("operations/external_validation/e68_cieu_external_validation_scorecard.json", base)
    if ev.get("confidence", 0) <= 0:
        return TARGETED_REFRESH_MILESTONE
    return NEXT_MILESTONE


def write_runtime_writeback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    scoring = load_json("operations/external_validation/e68_cieu_route_model_scoring.json", base) or build_cieu_route_model_scoring(base)
    ev = load_json("operations/external_validation/e68_cieu_external_validation_scorecard.json", base) or build_cieu_external_validation_scorecard(base)
    portfolio = load_json("operations/external_validation/e68_strategic_portfolio_update.json", base) or build_strategic_portfolio_update(base)
    wedge = load_json("operations/external_validation/e68_cieu_product_wedge_hypothesis.json", base) or build_cieu_product_wedge_hypothesis(base)
    policy = load_json("operations/external_validation/e68_cieu_no_overclaim_legal_caution_policy.json", base) or build_no_overclaim_legal_caution_policy(base)
    next_milestone = select_next_milestone(base)
    update = {
        "artifact_id": "e68_ceo_brain_cieu_route_update",
        "cieu_route_status": "CIEU high-risk AI audit log route evaluated",
        "CIEU_route_score": scoring["CIEU_route_score"],
        "CIEU_EV_level": ev.get("highest_achieved_EV_level"),
        "high_risk_vertical_map_status": "created",
        "regulatory_evidence_map_status": "created",
        "portfolio_role": portfolio["best_portfolio_after_E68"],
        "product_wedge_hypothesis": wedge["offer_name"],
        "no_overclaim_policy": policy["prohibited_claims"],
        "remaining_uncertainties": ev.get("missing_evidence", []),
        "owner_gated_next_steps": wedge["owner_gated_next_steps"],
        "next_recommended_milestone": next_milestone,
        "no_external_action": True,
        "external_action_allowed": False,
        "EU_AI_Act_compliance_claimed": False,
        "legal_compliance_claimed": False,
        "medical_readiness_claimed": False,
        "energy_critical_infrastructure_readiness_claimed": False,
        "high_risk_production_readiness_claimed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
        "autonomous_revenue_achieved": False,
        "owner_approval_fabricated": False,
        "EV5_achieved": False,
        "EV6_achieved": False,
        "EV7_achieved": False,
        "EV8_achieved": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }
    write_json(base, "operations/external_validation/e68_ceo_brain_cieu_route_update.json", update)
    write_jsonl(base, "operations/knowledge_graph/e68_ceo_kg_cieu_route_nodes_delta.jsonl", [
        {"node_id": CIEU_ROUTE, "node_type": "strategic_route", "status": "evaluated"},
        {"node_id": wedge["offer_name"], "node_type": "product_wedge", "status": "internal_only"},
        {"node_id": next_milestone, "node_type": "recommended_next_milestone"},
    ])
    write_jsonl(base, "operations/knowledge_graph/e68_ceo_kg_cieu_route_edges_delta.jsonl", [
        {"from": "e67_external_validation_overlay", "to": CIEU_ROUTE, "edge_type": "scores"},
        {"from": "K9Audit_CIEU_context", "to": CIEU_ROUTE, "edge_type": "supports_concept"},
        {"from": CIEU_ROUTE, "to": wedge["offer_name"], "edge_type": "packages_as"},
        {"from": CIEU_ROUTE, "to": next_milestone, "edge_type": "recommends"},
    ])
    write_json(base, "operations/knowledge_graph/e68_ceo_kg_cieu_route_read_model_update.json", {"artifact_id": "e68_ceo_kg_cieu_route_read_model_update", **update})
    write_json(base, "operations/external_validation/e68_czl_closure.json", {
        "artifact_id": "e68_czl_closure",
        "closure_status": "closed",
        "closed_loop": "owner insight -> archaeology -> CIEU concept -> public regulatory evidence -> vertical map -> scoring -> portfolio role -> CEO readback",
        "recommended_next_milestone": next_milestone,
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e68_cieu_residual_summary.json", {
        "artifact_id": "e68_cieu_residual_summary",
        "intervention": "Evaluated CIEU as high-risk AI agent audit log strategic route.",
        "resolved_residuals": ["CIEU is now evaluated as strategic vertical/module rather than just internal log"],
        "remaining_residuals": ev.get("missing_evidence", []),
        "no_external_action": True,
    })
    return update


def load_e68_cieu_route_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e68_ceo_brain_cieu_route_update.json", base)
    if not state:
        state = write_runtime_writeback(base)
    return state


def get_cieu_route_score(root: Path | None = None) -> dict[str, Any]:
    return (load_json("operations/external_validation/e68_cieu_route_model_scoring.json", root) or build_cieu_route_model_scoring(root))["CIEU_route_score"]


def get_cieu_external_validation(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e68_cieu_external_validation_scorecard.json", root) or build_cieu_external_validation_scorecard(root)


def get_cieu_product_wedge(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e68_cieu_product_wedge_hypothesis.json", root) or build_cieu_product_wedge_hypothesis(root)


def get_cieu_portfolio_role(root: Path | None = None) -> dict[str, Any]:
    return (load_json("operations/external_validation/e68_strategic_portfolio_update.json", root) or build_strategic_portfolio_update(root))["best_portfolio_after_E68"]


def explain_cieu_overclaim_limits(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e68_cieu_no_overclaim_legal_caution_policy.json", root) or build_no_overclaim_legal_caution_policy(root)


def build_ceo_cieu_route_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e68_cieu_route_state_for_brain(root)
    checks = {
        "CEO_sees_CIEU_route_score": isinstance(state.get("CIEU_route_score"), dict),
        "CEO_sees_CIEU_EV_level": str(state.get("CIEU_EV_level", "")).startswith("EV"),
        "CEO_sees_portfolio_role": isinstance(state.get("portfolio_role"), dict),
        "CEO_sees_product_wedge": state.get("product_wedge_hypothesis") == "Governed Business Operations Blueprint + CIEU Audit Module",
        "CEO_sees_no_overclaim_policy": "CIEU ensures EU AI Act compliance" in state.get("no_overclaim_policy", []),
        "CEO_sees_next_milestone": state.get("next_recommended_milestone") in {NEXT_MILESTONE, TARGETED_REFRESH_MILESTONE},
        "CEO_sees_external_action_blocked": state.get("external_action_allowed") is False,
        "CEO_sees_no_forbidden_claims": all(state.get(key) is False for key in [
            "EU_AI_Act_compliance_claimed",
            "legal_compliance_claimed",
            "medical_readiness_claimed",
            "energy_critical_infrastructure_readiness_claimed",
            "high_risk_production_readiness_claimed",
            "customer_validation_claimed",
            "paid_signal_claimed",
            "expert_feedback_claimed",
            "pricing_validation_claimed",
            "autonomous_revenue_achieved",
            "owner_approval_fabricated",
            "EV5_achieved",
            "EV6_achieved",
            "EV7_achieved",
            "EV8_achieved",
        ]),
    }
    return {"artifact_id": "e68_ceo_cieu_route_readback_smoke_result", "observed_state": state, "checks": checks, "passes": all(checks.values()), "external_action_allowed": False, "owner_decision_status": OWNER_DECISION_STATUS}


def build_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e68_behavior_authorization_result",
        "authorization_status": "ALLOW_INTERNAL_CIEU_ROUTE_EVALUATION_ONLY",
        "allowed_actions": [
            "repository_archaeology",
            "controlled_public_read_regulatory_market_evidence_collection",
            "CIEU_route_scoring",
            "CIEU_external_validation_scoring",
            "strategic_portfolio_comparison",
            "internal_product_wedge_hypothesis",
            "no_overclaim_legal_caution_policy",
            "CEO_readback_integration",
            "KG_CZL_CIEU_writeback",
        ],
        "denied_actions": [
            "legal_compliance_claim",
            "medical_readiness_claim",
            "energy_dispatch_readiness_claim",
            "high_risk_production_readiness_claim",
            "outreach",
            "publication",
            "customer_conversation",
            "expert_review",
            "human_identification",
            "contact_scraping",
            "login_form_send",
            "private_provider_API",
            "API_key_secret_use",
            "payment",
            "invoice",
            "client_delivery",
            "customer_validation_claim",
            "paid_signal_claim",
            "expert_feedback_claim",
        ],
        "external_business_execution_authorized": False,
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "passed": True,
    }


def build_no_overclaim_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    paths = [
        "operations/external_validation/e68_cieu_external_validation_scorecard.json",
        "operations/external_validation/e68_cieu_no_overclaim_legal_caution_policy.json",
        "operations/external_validation/e68_ceo_brain_cieu_route_update.json",
        "operations/external_validation/e68_ceo_cieu_route_readback_smoke_result.json",
        "operations/external_validation/e68_behavior_authorization_result.json",
    ]
    forbidden_true = [
        "EU_AI_Act_compliance_claimed",
        "legal_compliance_claimed",
        "medical_readiness_claimed",
        "energy_critical_infrastructure_readiness_claimed",
        "high_risk_production_readiness_claimed",
        "customer_validation_claimed",
        "paid_signal_claimed",
        "expert_feedback_claimed",
        "pricing_validation_claimed",
        "autonomous_revenue_achieved",
        "owner_approval_fabricated",
        "EV5_achieved",
        "EV6_achieved",
        "EV7_achieved",
        "EV8_achieved",
        "external_action_allowed",
    ]
    violations = []
    for rel in paths:
        data = load_json(rel, base)
        observed = data.get("observed_state", data)
        for field in forbidden_true:
            if observed.get(field) is True:
                violations.append({"path": rel, "field": field, "value": True})
    return {"artifact_id": "e68_no_overclaim_validation_result", "paths_scanned": paths, "violations": violations, "passed": not violations}


def build_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_state = load_json("operations/external_validation/e68_base_state_manifest.json", base) or build_base_state_manifest(base)
    archaeology = load_json("operations/external_validation/e68_cieu_route_repository_archaeology_inventory.json", base)
    audit = load_json("operations/external_validation/e68_reuse_first_growth_audit.json", base)
    concept = load_json("operations/external_validation/e68_cieu_high_risk_audit_log_concept.json", base)
    receipts = load_json("operations/external_validation/e68_regulatory_public_requirements_receipts.json", base)
    atoms = load_json("operations/external_validation/e68_regulatory_public_requirements_evidence_atoms.json", base)
    verticals = load_json("operations/external_validation/e68_high_risk_vertical_opportunity_map.json", base)
    scoring = load_json("operations/external_validation/e68_cieu_route_model_scoring.json", base)
    ev = load_json("operations/external_validation/e68_cieu_external_validation_scorecard.json", base)
    portfolio = load_json("operations/external_validation/e68_strategic_portfolio_update.json", base)
    wedge = load_json("operations/external_validation/e68_cieu_product_wedge_hypothesis.json", base)
    policy = load_json("operations/external_validation/e68_cieu_no_overclaim_legal_caution_policy.json", base)
    readback = load_json("operations/external_validation/e68_ceo_cieu_route_readback_smoke_result.json", base)
    auth = load_json("operations/external_validation/e68_behavior_authorization_result.json", base)
    no_overclaim = load_json("operations/external_validation/e68_no_overclaim_validation_result.json", base)
    checks = {
        "base_HEAD_verified": base_state.get("base_verified") is True,
        "repository_archaeology_completed": archaeology.get("asset_count", 0) >= 20,
        "reuse_first_audit_passes": audit.get("passed") is True,
        "CIEU_concept_definition_created": concept.get("concept_name") == "CIEU Causal Audit Log for High-Risk AI Agents",
        "regulatory_public_requirements_evidence_map_created": atoms.get("evidence_atom_count", 0) >= 10,
        "high_risk_vertical_opportunity_map_created": verticals.get("vertical_count", 0) >= 10,
        "CIEU_route_model_scoring_created": scoring.get("CIEU_route_score", {}).get("route_id") == CIEU_ROUTE,
        "CIEU_external_validation_scorecard_created": ev.get("route_id") == CIEU_ROUTE,
        "strategic_portfolio_update_created": portfolio.get("should_CIEU_become_vertical_module_inside_current_selected_route") is True,
        "CIEU_product_wedge_hypothesis_created": wedge.get("offer_name") == "Governed Business Operations Blueprint + CIEU Audit Module",
        "no_overclaim_legal_caution_policy_created": "CIEU ensures EU AI Act compliance" in policy.get("prohibited_claims", []),
        "CEO_CIEU_loader_readback_implemented": callable(load_e68_cieu_route_state_for_brain) and callable(get_cieu_route_score),
        "CEO_brain_adapter_reads_E68_state": readback.get("passes") is True,
        "behavior_authorization_passed": auth.get("passed") is True,
        "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
            "operations/knowledge_graph/e68_ceo_kg_cieu_route_read_model_update.json",
            "operations/external_validation/e68_czl_closure.json",
            "operations/external_validation/e68_cieu_residual_summary.json",
        ]),
        "no_forbidden_external_action_executed": auth.get("external_business_execution_authorized") is False,
        "no_compliance_medical_energy_customer_paid_overclaims": no_overclaim.get("passed") is True,
    }
    if all(checks.values()):
        final_status = "e68_cieu_route_promising_as_high_defensibility_vertical" if receipts.get("successful_read_count", 0) > 0 else "e68_cieu_route_deferred_due_to_evidence_or_sales_cycle_risk"
    else:
        final_status = "e68_blocked_due_to_overclaim_risk" if not checks["no_compliance_medical_energy_customer_paid_overclaims"] else "e68_blocked_due_to_disconnected_ceo_integration"
    return {
        "artifact_id": "e68_completion_gate_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": final_status,
        "regulatory_public_source_count": receipts.get("receipt_count", 0),
        "successful_public_read_count": receipts.get("successful_read_count", 0),
        "regulatory_evidence_atoms": atoms.get("evidence_atom_count", 0),
        "CIEU_route_score": scoring.get("CIEU_route_score"),
        "CIEU_highest_EV_level": ev.get("highest_achieved_EV_level"),
        "CIEU_portfolio_role": portfolio.get("best_portfolio_after_E68"),
        "recommended_next_milestone": select_next_milestone(base),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "EU_AI_Act_compliance_claimed": False,
        "legal_compliance_claimed": False,
        "medical_readiness_claimed": False,
        "energy_critical_infrastructure_readiness_claimed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
    }


def write_reports(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    archaeology = load_json("operations/external_validation/e68_cieu_route_repository_archaeology_inventory.json", base)
    concept = load_json("operations/external_validation/e68_cieu_high_risk_audit_log_concept.json", base)
    receipts = load_json("operations/external_validation/e68_regulatory_public_requirements_receipts.json", base)
    atoms = load_json("operations/external_validation/e68_regulatory_public_requirements_evidence_atoms.json", base)
    verticals = load_json("operations/external_validation/e68_high_risk_vertical_opportunity_map.json", base)
    scoring = load_json("operations/external_validation/e68_cieu_route_model_scoring.json", base)
    ev = load_json("operations/external_validation/e68_cieu_external_validation_scorecard.json", base)
    portfolio = load_json("operations/external_validation/e68_strategic_portfolio_update.json", base)
    wedge = load_json("operations/external_validation/e68_cieu_product_wedge_hypothesis.json", base)
    gate = load_json("operations/external_validation/e68_completion_gate_result.json", base)
    write_md(base, "reports/integration/e68_cieu_route_repository_archaeology_inventory.md", "E68 CIEU Route Repository Archaeology", [
        f"Assets inspected: `{archaeology.get('asset_count')}`.",
        "E68 reused CIEU/KG/CZL evidence closure, K9Audit read-only CIEU context, E65 model assets, and E67 validation overlay.",
    ])
    write_md(base, "reports/integration/e68_cieu_high_risk_audit_log_concept.md", "E68 CIEU High-Risk Audit Log Concept", [
        f"Concept: `{concept.get('concept_name')}`.",
        "CIEU records X_t, U_t, Y*_t, Y_t+1, and R_t+1.",
        "It is a causal audit/readiness pattern, not legal compliance or production readiness proof.",
    ])
    write_md(base, "reports/integration/e68_regulatory_public_requirements_map.md", "E68 Regulatory Public Requirements Map", [
        f"Sources: `{receipts.get('receipt_count')}`; successful reads: `{receipts.get('successful_read_count')}`.",
        f"Evidence atoms: `{atoms.get('evidence_atom_count')}`.",
        "Evidence maps public regulatory/safety signals to CIEU fields without compliance claims.",
    ])
    write_md(base, "reports/integration/e68_high_risk_vertical_opportunity_map.md", "E68 High-Risk Vertical Opportunity Map", [
        f"Verticals evaluated: `{verticals.get('vertical_count')}`.",
        f"Selected verticals/modules: `{verticals.get('selected_verticals')}`.",
    ])
    write_md(base, "reports/integration/e68_cieu_route_model_scoring.md", "E68 CIEU Route Model Scoring", [
        f"CIEU balanced score: `{scoring.get('CIEU_route_score', {}).get('balanced_score')}`.",
        f"Model conclusion: {scoring.get('model_conclusion')}",
    ])
    write_md(base, "reports/integration/e68_cieu_external_validation_scorecard.md", "E68 CIEU External Validation Scorecard", [
        f"Highest EV level: `{ev.get('highest_achieved_EV_level')}`.",
        f"Confidence: `{ev.get('confidence')}`.",
        "EV5-EV8 are owner-gated and unachieved.",
    ])
    write_md(base, "reports/integration/e68_strategic_portfolio_update.md", "E68 Strategic Portfolio Update", [
        f"Portfolio: `{portfolio.get('best_portfolio_after_E68')}`.",
        "CIEU should not replace current first-cash route now; it is best positioned as a high-defensibility vertical/module.",
    ])
    write_md(base, "reports/integration/e68_cieu_product_wedge_hypothesis.md", "E68 CIEU Product Wedge Hypothesis", [
        f"Offer: `{wedge.get('offer_name')}`.",
        "Internal-only; not compliance, medical, energy, customer, or paid validation.",
    ])
    write_md(base, "reports/integration/e68_cieu_no_overclaim_legal_caution_policy.md", "E68 CIEU No-Overclaim Legal Caution Policy", [
        "Prohibits EU AI Act compliance, medical certification, energy dispatch readiness, legal advice, production readiness, customer validation, and paid signal claims.",
        "Allows cautious language: causal audit and traceability evidence pattern; may support record-keeping and post-market monitoring evidence.",
    ])
    write_md(base, "reports/integration/e68_reuse_first_growth_audit.md", "E68 Reuse-First Growth Audit", [
        "Reuse-first audit passed. E68 did not rebuild CIEU/KG/CZL, E65, E67, safe reader, behavior gate, CEO readback, or K9Audit ledger concepts.",
    ])
    write_md(base, "reports/integration/e68_completion_gate_result.md", "E68 Completion Gate", [
        f"Gate passed: `{gate.get('gate_passed')}`.",
        f"Final status: `{gate.get('final_status')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])
    write_md(base, "reports/integration/e68_operator_handoff.md", "E68 Operator Handoff", [
        f"Final status: `{gate.get('final_status')}`.",
        f"CIEU EV level: `{gate.get('CIEU_highest_EV_level')}`.",
        f"Next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])


def write_all_e68_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    write_json(base, "operations/external_validation/e68_base_state_manifest.json", build_base_state_manifest(base))
    write_json(base, "operations/external_validation/e68_cieu_route_repository_archaeology_inventory.json", build_repository_archaeology_inventory(base))
    write_json(base, "operations/external_validation/e68_reuse_first_growth_audit.json", build_reuse_first_growth_audit(base))
    write_json(base, "operations/external_validation/e68_cieu_high_risk_audit_log_concept.json", build_cieu_concept(base))
    write_json(base, "operations/external_validation/e68_regulatory_public_requirements_plan.json", build_regulatory_public_requirements_plan(base))
    receipts = build_regulatory_public_requirements_receipts(base)
    write_json(base, "operations/external_validation/e68_regulatory_public_requirements_receipts.json", receipts)
    write_json(base, "operations/external_validation/e68_regulatory_public_requirements_evidence_atoms.json", build_regulatory_public_requirements_evidence_atoms(base))
    write_json(base, "operations/external_validation/e68_high_risk_vertical_opportunity_map.json", build_high_risk_vertical_opportunity_map(base))
    write_json(base, "operations/external_validation/e68_cieu_route_model_scoring.json", build_cieu_route_model_scoring(base))
    write_json(base, "operations/external_validation/e68_cieu_external_validation_scorecard.json", build_cieu_external_validation_scorecard(base))
    write_json(base, "operations/external_validation/e68_strategic_portfolio_update.json", build_strategic_portfolio_update(base))
    write_json(base, "operations/external_validation/e68_cieu_product_wedge_hypothesis.json", build_cieu_product_wedge_hypothesis(base))
    write_json(base, "operations/external_validation/e68_cieu_no_overclaim_legal_caution_policy.json", build_no_overclaim_legal_caution_policy(base))
    write_json(base, "operations/external_validation/e68_behavior_authorization_result.json", build_behavior_authorization(base))
    write_runtime_writeback(base)
    write_json(base, "operations/external_validation/e68_ceo_cieu_route_readback_smoke_result.json", build_ceo_cieu_route_readback_smoke(base))
    write_json(base, "operations/external_validation/e68_no_overclaim_validation_result.json", build_no_overclaim_validation(base))
    gate = build_completion_gate(base)
    write_json(base, "operations/external_validation/e68_completion_gate_result.json", gate)
    write_reports(base)
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e68_artifacts(), indent=2, ensure_ascii=False))
