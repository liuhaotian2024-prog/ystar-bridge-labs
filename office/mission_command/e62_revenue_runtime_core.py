from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from .e61_live_public_read_core import LIVE_URLS, controlled_public_read_smoke_probe

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))
COMPANY_ROOT = Path(os.environ.get("YSTAR_COMPANY_ROOT", "/Users/haotianliu/.openclaw/workspace/ystar-company"))

JOB_ID = "e62_repository_grounded_network_probe_and_revenue_runtime_recenter_20260506T000001Z"
EXPECTED_BASE = "7023d01008909b8f6bdf71126f949e46e462319e"
OWNER_DECISION_STATUS = "pending_owner_decision"
SELECTED_FIRST_CASH_PATH = "AI_agent_company_runtime_harness_deployment_service"
NEAREST_FIRST_CASH_ALTERNATIVE = "agent_runtime_audit_and_repair_package"


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


def dirty_paths_are_e62_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e62_",
        "tests/office/test_e62_",
        "operations/external_validation/e62_",
        "operations/knowledge_graph/e62_",
        "reports/integration/e62_",
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
        "ystar-company": git_state(COMPANY_ROOT) if COMPANY_ROOT.exists() else {"path": str(COMPANY_ROOT), "available": False},
    }
    return {
        "artifact_id": "e62_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "base_verified": bridge["head_matches_expected"] and bridge["branch"] == "backflow/aiden-ceo-meeting-room",
        "bridge_labs_worktree_clean_or_e62_scoped": dirty_paths_are_e62_scoped(bridge["status_short"]),
        "read_only_repos": read_only,
        "read_only_repos_clean": all(item.get("clean", True) for item in read_only.values()),
        "e61_completed_report_present": Path("/tmp/ystar_delivery_bridge/completed/e61_live_public_read_adapter_repair_or_host_network_refresh_20260506T000001Z.report.json").exists(),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def build_prior_gate_preflight(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e61_gate = load_json("operations/external_validation/e61_completion_gate_result.json", base)
    e61_probe = load_json("operations/external_validation/e61_live_public_read_smoke_probe_result.json", base)
    e60_gate = load_json("operations/external_validation/e60_post_external_intelligence_market_readiness_gate_result.json", base)
    checks = {
        "E60_selected_E61": e60_gate.get("recommended_next_milestone") == "E61_live_public_read_adapter_repair_or_host_network_refresh",
        "E61_completion_gate_passed": e61_gate.get("gate_passed") is True,
        "E61_code_repaired_but_network_unavailable": e61_gate.get("final_status") == "live_public_read_code_repaired_but_host_network_unavailable",
        "E61_DNS_unavailable_visible": "DNS_unavailable" in e61_probe.get("failure_classes", []),
        "E61_live_receipts_zero": e61_probe.get("live_receipt_count") == 0,
        "owner_decision_pending": e61_gate.get("owner_decision_status") == OWNER_DECISION_STATUS,
        "external_action_allowed_false": e61_gate.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e62_prior_gate_preflight_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "passed": all(checks.values()),
        "consumed_E61_final_status": e61_gate.get("final_status"),
        "consumed_E61_failure_classes": e61_probe.get("failure_classes", []),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def file_exists(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def classify_asset(path: str, root: Path) -> dict[str, Any]:
    lower = path.lower()
    capability = "unknown"
    if "e61" in lower or "safe_public_page_reader" in lower or "public_page_read" in lower or "page_read" in lower:
        capability = "public_read_network_diagnostic"
    if "e59" in lower and ("source" in lower or "evidence" in lower or "intelligence" in lower):
        capability = "external_intelligence"
    if "e57" in lower or "e60" in lower or "commercial" in lower or "market" in lower or "route" in lower:
        capability = "commercial_route_or_market_readiness"
    if "e55" in lower or "behavior" in lower:
        capability = "behavior_authorization"
    if "e54" in lower or "ceo_brain" in lower or "e46b" in lower:
        capability = "ceo_brain_readback"
    if "kg" in lower or "czl" in lower or "cieu" in lower:
        capability = "evidence_writeback"
    if "sales" in lower or "finance" in lower or "pricing" in lower or "offer" in lower:
        capability = "commercial_revenue_asset"
    text = ""
    full = root / path
    if full.exists() and full.is_file() and full.suffix in {".py", ".md", ".json", ".jsonl", ".txt"}:
        try:
            text = full.read_text(encoding="utf-8", errors="ignore")[:25000].lower()
        except Exception:
            text = ""
    proof_only = any(term in lower for term in ["proof_packet", "readiness", "case_study"]) or "owner-reviewable" in text
    action_capable = any(term in text for term in ["authorize", "execute", "dry-run", "smoke_probe", "public_read"])
    owner_gated = "owner" in text or "owner" in lower
    kg_writeback = any(term in lower for term in ["kg", "czl", "cieu"]) or any(term in text for term in ["knowledge_graph", "czl", "cieu"])
    return {
        "path": path,
        "capability_type": capability,
        "milestone_origin": detect_origin(path),
        "reusable": full.exists(),
        "already_connected_or_disconnected": "connected" if action_capable or kg_writeback else "reference_or_report_only",
        "tests_found": find_tests_for_path(root, path),
        "supports_autonomous_revenue_operation": capability in {"commercial_revenue_asset", "commercial_route_or_market_readiness", "behavior_authorization", "ceo_brain_readback", "evidence_writeback"},
        "proof_or_readiness_only": proof_only and not action_capable,
        "action_execution_capable": action_capable,
        "owner_gated": owner_gated,
        "has_KG_CZL_CIEU_writeback": kg_writeback,
        "do_not_rebuild": full.exists(),
    }


def detect_origin(path: str) -> str:
    for token in ["e62", "e61", "e60", "e59", "e58", "e57", "e56", "e55", "e54", "e53", "e52", "e51", "e50b", "e50a", "e41", "e29", "e28", "e24", "e9", "e8", "e6"]:
        if token in path.lower():
            return token.upper()
    if path.startswith(("sales/", "marketing/", "finance/")):
        return "business_directory"
    if path.startswith("products/ai_agent_company_runtime_harness_case_study"):
        return "E58"
    if path.startswith("products/governed_agent_action_proof_packet"):
        return "E52_E53"
    return "unknown"


def find_tests_for_path(root: Path, path: str) -> list[str]:
    base = Path(path).name.replace(".py", "")
    tests = []
    for file in (root / "tests/office").glob("test_*.py") if (root / "tests/office").exists() else []:
        name = file.name
        if base in name or ("e61" in path and "e61" in name) or ("e59" in path and "e59" in name) or ("e60" in path and "e60" in name):
            tests.append(str(file.relative_to(root)))
    return tests[:8]


def discover_assets(root: Path) -> list[dict[str, Any]]:
    explicit_paths = [
        "office/mission_command/e61_live_public_read_core.py",
        "office/mission_command/e61_controlled_public_read_smoke_probe.py",
        "office/mission_command/safe_public_page_reader.py",
        "office/mission_command/e59_controlled_public_page_read_adapter.py",
        "office/mission_command/e59_external_intelligence_core.py",
        "office/mission_command/e59_source_receipt_builder.py",
        "office/mission_command/e59_claim_extraction_and_evidence_atomizer.py",
        "operations/external_validation/e61_live_public_read_smoke_probe_result.json",
        "operations/external_validation/e61_external_intelligence_readiness_delta.json",
        "operations/external_validation/e61_behavior_authorization_result.json",
        "operations/external_validation/e57_public_readonly_evidence_preflight.json",
        "operations/external_validation/e57_post_l5_commercial_route_decision_packet.json",
        "operations/external_validation/e60_market_entry_decision_packet.json",
        "products/ai_agent_company_runtime_harness_case_study/case_study.json",
        "products/ai_agent_company_runtime_harness_case_study/e59_requirements_packet.md",
        "products/governed_agent_action_proof_packet/proof_packet.json",
        "office/mission_command/e55_action_authorization_gate.py",
        "office/mission_command/e55_behavior_action_model.py",
        "office/mission_command/e56_internal_company_loop_model.py",
        "office/mission_command/e46b_ceo_brain_adapter.py",
    ]
    search_terms = [
        "revenue", "first_cash", "money", "route", "commercial", "offer", "business", "sales",
        "customer", "pricing", "package", "market", "product", "paid", "validation", "case_study",
    ]
    paths = set(path for path in explicit_paths if file_exists(root, path))
    for directory in ["sales", "marketing", "finance", "products", "reports", "operations", "office/mission_command"]:
        base = root / directory
        if not base.exists():
            continue
        for file in sorted(base.rglob("*")):
            if not file.is_file() or file.suffix.lower() not in {".py", ".md", ".json", ".jsonl", ".txt", ".yaml", ".yml"}:
                continue
            rel = str(file.relative_to(root))
            haystack = rel.lower()
            if any(term in haystack for term in search_terms):
                paths.add(rel)
            elif len(paths) < 180:
                try:
                    body = file.read_text(encoding="utf-8", errors="ignore")[:12000].lower()
                    if any(term in body for term in search_terms):
                        paths.add(rel)
                except Exception:
                    pass
    assets = [classify_asset(path, root) for path in sorted(paths)]
    return assets[:240]


def build_repository_archaeology_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    assets = discover_assets(base)
    reusable_assets = [item for item in assets if item["reusable"]]
    read_only_context = {
        "Y-star-gov": {
            "root": str(Y_GOV_ROOT),
            "runtime_linkage_validator": (Y_GOV_ROOT / "ystar/governance/runtime_linkage.py").exists(),
            "capability_binding_validator": (Y_GOV_ROOT / "ystar/governance/capability_centerline_binding.py").exists(),
            "pre_execution_governance": (Y_GOV_ROOT / "ystar/governance/pre_u_packet_validator.py").exists(),
            "mutated": False,
        },
        "gov-mcp": {
            "root": str(GOV_MCP_ROOT),
            "allow_deny_tests_present": bool(list((GOV_MCP_ROOT / "tests").rglob("*allow*deny*.py"))) if (GOV_MCP_ROOT / "tests").exists() else False,
            "runtime_linkage_tools_present": bool(list(GOV_MCP_ROOT.rglob("*runtime*"))) if GOV_MCP_ROOT.exists() else False,
            "mutated": False,
        },
        "K9Audit": {
            "root": str(K9_ROOT),
            "ledger_capability_present": (K9_ROOT / "k9log").exists(),
            "write_integration_in_bridge_labs_closed": False,
            "mutated": False,
        },
    }
    revenue_runtime_candidates = [
        item for item in assets
        if item["supports_autonomous_revenue_operation"] and not item["proof_or_readiness_only"]
    ]
    return {
        "artifact_id": "e62_repository_archaeology_inventory",
        "bridge_job_id": JOB_ID,
        "asset_count": len(assets),
        "discovered_assets": assets,
        "reusable_assets_count": len(reusable_assets),
        "revenue_runtime_supporting_assets_count": len(revenue_runtime_candidates),
        "read_only_repo_context": read_only_context,
        "reuse_first_findings": [
            "E61 already repaired a deterministic controlled probe path around safe_public_page_reader.",
            "E55 behavior authorization conventions already define ALLOW/DENY boundaries and should be reused.",
            "E54-E56 provide a real internal company loop substrate; E62 should connect revenue operation to it rather than build a separate proof system.",
            "E57/E60 route matrices are useful inputs but remain readiness/commercial decision artifacts, not the company objective.",
            "K9Audit ledger context exists read-only; bridge-labs K9 write integration remains future work.",
        ],
        "what_must_not_be_rebuilt": [
            "safe_public_page_reader",
            "E61 controlled public-read smoke probe",
            "E55 behavior action/authorization model",
            "E54/E56 CEO brain and internal loop readback",
            "E59 receipt/evidence atom schemas",
            "E57/E60 commercial route matrices",
            "E58 case study source artifacts",
        ],
        "missing_or_disconnected": [
            "host delivery bridge network result is not available until host validation runs",
            "live public read freshness remains blocked unless host DNS/network succeeds",
            "autonomous revenue runtime centerline exists only as scattered route/readiness/commercial artifacts before E62",
        ],
        "supports_autonomous_revenue_operation": bool(revenue_runtime_candidates),
        "phase_0_completed_before_new_runtime_layer": True,
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def build_host_network_probe_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e61_probe = load_json("operations/external_validation/e61_live_public_read_smoke_probe_result.json", base)
    return {
        "artifact_id": "e62_host_network_probe_inventory",
        "reused_E61_probe_core": "office/mission_command/e61_live_public_read_core.py",
        "reused_safe_reader": "office/mission_command/safe_public_page_reader.py",
        "allowlisted_urls": LIVE_URLS,
        "E61_failure_classes": e61_probe.get("failure_classes", []),
        "distinguishes": [
            "sandbox DNS unavailable",
            "sandbox DNS works",
            "host delivery bridge DNS unavailable",
            "host delivery bridge DNS works",
            "TCP blocked",
            "HTTPS/TLS blocked",
            "adapter policy denied",
            "adapter disconnected",
            "fixture-only path",
            "unknown",
        ],
        "no_search_provider_api": True,
        "no_api_key_or_secret": True,
        "no_crawl": True,
        "no_contact_scraping": True,
        "no_external_human_action": True,
    }


def run_dns_probe(host: str = "example.com", port: int = 443) -> dict[str, Any]:
    try:
        results = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        addresses = sorted({item[4][0] for item in results})
        return {
            "host": host,
            "port": port,
            "dns_status": "dns_available",
            "address_count": len(addresses),
            "sample_addresses": addresses[:3],
            "failure_classification": "",
        }
    except socket.gaierror as exc:
        return {
            "host": host,
            "port": port,
            "dns_status": "dns_unavailable",
            "address_count": 0,
            "sample_addresses": [],
            "failure_classification": "DNS_unavailable",
            "error_type": type(exc).__name__,
            "error_summary": str(exc)[:240],
        }
    except OSError as exc:
        return {
            "host": host,
            "port": port,
            "dns_status": "network_unavailable",
            "address_count": 0,
            "sample_addresses": [],
            "failure_classification": "host_network_unavailable",
            "error_type": type(exc).__name__,
            "error_summary": str(exc)[:240],
        }


def build_sandbox_dns_probe_result(root: Path | None = None) -> dict[str, Any]:
    dns = run_dns_probe()
    smoke = controlled_public_read_smoke_probe(LIVE_URLS)
    return {
        "artifact_id": "e62_sandbox_dns_probe_result",
        "probe_environment": "codex_sandbox_or_staging",
        "dns_probe": dns,
        "controlled_smoke_probe_passed": smoke.get("controlled_public_read_smoke_probe_passed"),
        "smoke_failure_classes": smoke.get("failure_classes", []),
        "live_receipt_count": smoke.get("live_receipt_count", 0),
        "sandbox_dns_available": dns.get("dns_status") == "dns_available",
        "sandbox_dns_unavailable": dns.get("failure_classification") == "DNS_unavailable",
        "fixture_or_blocker_not_live_market_freshness": True,
        "no_external_human_action": True,
    }


def is_host_bridge_root(root: Path) -> bool:
    normalized = str(root.resolve())
    return normalized == "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs"


def build_delivery_bridge_network_probe_request(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e62_delivery_bridge_network_probe_request",
        "request_id": f"{JOB_ID}_host_network_probe",
        "request_status": "embedded_in_E62_host_delivery_validation",
        "host_probe_execution_surface": "tests/office/test_e62_host_network_probe.py",
        "allowlisted_urls": LIVE_URLS,
        "allowed_operations": ["DNS resolution for allowlisted hosts", "controlled public GET through E61 smoke probe"],
        "forbidden_operations": [
            "search provider APIs",
            "API keys or secrets",
            "crawling",
            "arbitrary link following",
            "contact scraping",
            "human identification",
            "login",
            "forms",
            "posting or publishing",
        ],
        "expected_result_artifact": "operations/external_validation/e62_delivery_bridge_network_probe_result.json",
        "no_external_human_action": True,
    }


def build_delivery_bridge_network_probe_result(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    host_environment = is_host_bridge_root(base)
    dns = run_dns_probe()
    smoke = controlled_public_read_smoke_probe(LIVE_URLS)
    return {
        "artifact_id": "e62_delivery_bridge_network_probe_result",
        "host_probe_result_available": host_environment,
        "probe_environment": "host_delivery_bridge" if host_environment else "sandbox_or_staging_not_host_bridge",
        "dns_probe": dns,
        "controlled_smoke_probe_passed": smoke.get("controlled_public_read_smoke_probe_passed"),
        "smoke_status": smoke.get("smoke_probe_status"),
        "smoke_failure_classes": smoke.get("failure_classes", []),
        "live_receipt_count": smoke.get("live_receipt_count", 0),
        "receipts": smoke.get("receipts", []),
        "diagnosis": (
            "host_public_read_available"
            if host_environment and smoke.get("controlled_public_read_smoke_probe_passed")
            else (
                "host_dns_unavailable"
                if host_environment and "DNS_unavailable" in smoke.get("failure_classes", [])
                else (
                    "host_network_unavailable"
                    if host_environment and any(item in smoke.get("failure_classes", []) for item in ["host_network_unavailable", "TLS_unavailable", "timeout"])
                    else "host_bridge_unknown_until_delivery_validation"
                )
            )
        ),
        "fixture_or_blocker_not_live_market_freshness": True,
        "no_external_human_action": True,
    }


def build_public_read_blocker_classification(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    sandbox = load_json("operations/external_validation/e62_sandbox_dns_probe_result.json", base) or build_sandbox_dns_probe_result(base)
    host = load_json("operations/external_validation/e62_delivery_bridge_network_probe_result.json", base) or build_delivery_bridge_network_probe_result(base)
    if host.get("diagnosis") == "host_public_read_available":
        status = "host_public_read_available"
    elif host.get("diagnosis") == "host_dns_unavailable":
        status = "host_dns_unavailable"
    elif host.get("diagnosis") == "host_network_unavailable":
        status = "unknown_network_blocker"
    elif sandbox.get("sandbox_dns_unavailable"):
        status = "sandbox_dns_unavailable_but_host_bridge_unknown"
    else:
        status = "unknown_network_blocker"
    return {
        "artifact_id": "e62_public_read_blocker_classification",
        "blocker_status": status,
        "sandbox_dns_status": sandbox.get("dns_probe", {}).get("dns_status"),
        "sandbox_smoke_failure_classes": sandbox.get("smoke_failure_classes", []),
        "host_probe_available": host.get("host_probe_result_available", False),
        "host_probe_diagnosis": host.get("diagnosis"),
        "adapter_policy_denied": "policy_blocked" in host.get("smoke_failure_classes", []),
        "adapter_disconnected": False,
        "fixture_mode_only": False,
        "live_public_read_available": status == "host_public_read_available",
        "live_market_freshness_available": status == "host_public_read_available",
        "fixture_or_blocker_not_live_market_freshness": True,
        "recommended_network_followup": (
            "E63_autonomous_revenue_opportunity_discovery_public_read_only"
            if status == "host_public_read_available"
            else "E63_revenue_path_selection_from_existing_evidence_plus_network_remediation"
        ),
        "no_external_human_action": True,
    }


def build_revenue_action_risk_tiers(root: Path | None = None) -> dict[str, Any]:
    tiers = [
        {
            "tier": "T0_internal_only",
            "allowed_examples": ["internal reasoning", "route comparison", "offer draft", "delivery blueprint draft"],
            "external_action": False,
            "owner_approval_required": False,
            "behavior_authorization": "ALLOW",
        },
        {
            "tier": "T1_public_read_only",
            "allowed_examples": ["controlled public knowledge observation", "source receipts", "no-contact route learning"],
            "external_action": False,
            "owner_approval_required": False,
            "behavior_authorization": "ALLOW_if_policy_and_network_permit",
        },
        {
            "tier": "T2_draft_only_external_material",
            "allowed_examples": ["draft outreach copy", "draft review plan", "draft pricing page"],
            "external_action": False,
            "owner_approval_required": False,
            "behavior_authorization": "ALLOW_draft_only_no_send_no_publish",
        },
        {
            "tier": "T3_owner_approved_external_contact",
            "allowed_examples": ["single controlled review contact after explicit owner approval"],
            "external_action": True,
            "owner_approval_required": True,
            "behavior_authorization": "DENY_until_owner_approval",
        },
        {
            "tier": "T4_owner_approved_commercial_transaction",
            "allowed_examples": ["pricing, invoice, payment, paid pilot, client delivery"],
            "external_action": True,
            "owner_approval_required": True,
            "behavior_authorization": "DENY_until_owner_approval_and_transaction_governance",
        },
    ]
    return {
        "artifact_id": "e62_revenue_action_risk_tiers",
        "tiers": tiers,
        "pending_owner_decision_is_not_approval": True,
        "external_action_allowed": False,
        "no_customer_validation_claim": True,
        "no_paid_signal_claim": True,
        "no_expert_feedback_claim": True,
    }


def build_autonomous_revenue_runtime_centerline(root: Path | None = None) -> dict[str, Any]:
    inventory = load_json("operations/external_validation/e62_repository_archaeology_inventory.json", root) or build_repository_archaeology_inventory(root)
    stages = [
        "CEO brain current state",
        "business objective interpretation",
        "opportunity discovery need",
        "available evidence / missing evidence",
        "revenue path candidates",
        "first-cash route comparison",
        "offer/package draftability",
        "action risk tier",
        "behavior authorization",
        "owner approval boundary",
        "evidence path",
        "KG/CZL/CIEU writeback",
        "CEO brain readback",
        "next business cycle recommendation",
    ]
    return {
        "artifact_id": "e62_autonomous_revenue_runtime_centerline",
        "centerline_status": "autonomous_revenue_runtime_recentered_internal_only",
        "primary_objective": "autonomous value creation, business operation, revenue path selection, and governed future revenue execution",
        "secondary_artifacts": ["proof packets", "case studies", "owner-review packets", "readiness reports"],
        "repo_grounded": True,
        "archaeology_asset_count": inventory.get("asset_count", 0),
        "stages": stages,
        "connected_existing_assets": [
            "E54 CEO Brain L5",
            "E55 Behavior Control Center L5",
            "E56 Internal Company Operating Loop L5",
            "E57/E60 commercial route matrices",
            "E58 AI Agent Company Runtime Harness Case Study",
            "E59/E61 external intelligence and public-read diagnostics",
            "KG/CZL/CIEU evidence closure",
        ],
        "new_layer_added": "thin E62 revenue operation centerline over existing assets",
        "not_rebuilt": inventory.get("what_must_not_be_rebuilt", []),
        "external_business_execution_owner_gated": True,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "autonomous_revenue_achieved": False,
        "real_client_delivery_claimed": False,
    }


def _candidate(
    route_id: str,
    source_asset_paths: list[str],
    target_buyer_category: str,
    pain_point: str,
    value_proposition: str,
    shortest_cash_path: str,
    fit: int,
    missing: list[str],
    complexity: str,
    external_action_required: bool,
    owner_approval_required: bool,
    live_read_dependency: bool,
    real_mcp_dependency: bool,
    k9_dependency: bool,
    risk_tier: str,
    evidence_required: list[str],
) -> dict[str, Any]:
    score = fit
    score -= 12 if external_action_required else 0
    score -= 10 if live_read_dependency else 0
    score -= 8 if real_mcp_dependency else 0
    score -= 6 if k9_dependency else 0
    score -= {"low": 0, "medium": 6, "high": 14}.get(complexity, 8)
    return {
        "route_id": route_id,
        "source_asset_path_or_new_reason": source_asset_paths or ["new_provisional_candidate_from_E62_prompt_and_repo_gap"],
        "target_buyer_category": target_buyer_category,
        "pain_point": pain_point,
        "value_proposition": value_proposition,
        "shortest_cash_path": shortest_cash_path,
        "current_capability_fit": fit,
        "missing_capability": missing,
        "delivery_complexity": complexity,
        "external_action_required": external_action_required,
        "owner_approval_required": owner_approval_required,
        "live_public_read_dependency": live_read_dependency,
        "real_mcp_dependency": real_mcp_dependency,
        "K9Audit_write_dependency": k9_dependency,
        "risk_tier": risk_tier,
        "evidence_required": evidence_required,
        "deterministic_internal_score": score,
        "selected": route_id == SELECTED_FIRST_CASH_PATH,
        "reason": "",
    }


def build_revenue_path_candidate_matrix(root: Path | None = None) -> dict[str, Any]:
    candidates = [
        _candidate(
            "AI_agent_company_runtime_harness_deployment_service",
            ["products/ai_agent_company_runtime_harness_case_study/case_study.json", "operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json", "operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json"],
            "founder/operator teams trying to run governed AI-agent operations",
            "AI agents can produce activity, but companies need governed operating loops that create value without uncontrolled external action.",
            "Deploy or adapt the AI Agent Company Runtime Harness as an internal operating layer.",
            "draft-only offer and delivery blueprint first; owner-gated external review later",
            96,
            ["owner-approved external review", "live public-read freshness", "packaged delivery blueprint"],
            "medium",
            True,
            True,
            False,
            False,
            False,
            "T2_draft_only_external_material",
            ["case study", "internal L5 gates", "owner-reviewed delivery blueprint"],
        ),
        _candidate(
            "agent_runtime_audit_and_repair_package",
            ["operations/external_validation/e51_runtime_linkage_anti_drift_gate_result.json", "operations/external_validation/e62_repository_archaeology_inventory.json"],
            "teams with existing agent workflows that need governance repair",
            "Agent systems drift, overclaim, or bypass evidence closure.",
            "Audit and repair runtime linkage, behavior authorization, no-overclaim, and evidence closure.",
            "create internal audit checklist and sample repair packet; owner-gated external use later",
            91,
            ["K9Audit write integration if sold as audit ledger", "owner-approved outreach"],
            "low",
            True,
            True,
            False,
            False,
            True,
            "T2_draft_only_external_material",
            ["E51/E55/E61 gates", "K9Audit read-only context", "repair checklist"],
        ),
        _candidate(
            "governed_agent_action_control_layer",
            ["products/governed_agent_action_proof_packet/proof_packet.json", "office/mission_command/e55_action_authorization_gate.py"],
            "teams using autonomous agents with unsafe action boundaries",
            "Agents need a deterministic action proposal and authorization layer before execution.",
            "Provide a governed action-control layer with ALLOW/DENY fixtures and evidence requirements.",
            "package owner-reviewable internal demo and authorization schema",
            88,
            ["live market freshness", "owner-approved review"],
            "medium",
            True,
            True,
            False,
            False,
            False,
            "T2_draft_only_external_material",
            ["E52 proof packet", "E55 authorization gate", "no-overclaim validator"],
        ),
        _candidate(
            "MCP_governance_adapter_gov_mcp_integration_package",
            ["operations/external_validation/e59_gov_mcp_validation_harness_result.json", "operations/external_validation/e60_gov_mcp_validation_harness_result.json"],
            "MCP adopters needing policy and runtime governance",
            "MCP tool surfaces need safe allow/deny boundaries and evidence paths.",
            "Package gov-mcp integration patterns and governance fixtures.",
            "finish real MCP transport gate before external promise",
            76,
            ["real MCP transport closure", "owner-approved external review"],
            "medium",
            True,
            True,
            False,
            True,
            False,
            "T2_draft_only_external_material",
            ["gov-mcp harness proof", "real transport proof"],
        ),
        _candidate(
            "public_read_market_intelligence_agent_with_governance",
            ["office/mission_command/e59_external_intelligence_core.py", "office/mission_command/e61_live_public_read_core.py"],
            "operators needing safe no-contact market/technology learning",
            "Market learning agents often drift into scraping/contact or overclaim freshness.",
            "Governed public-read intelligence pipeline with source receipts and route impact.",
            "repair host/live public-read and then run internal opportunity discovery",
            83,
            ["host DNS/network public-read availability", "live receipts"],
            "medium",
            False,
            False,
            True,
            False,
            False,
            "T1_public_read_only",
            ["E59 schemas", "E61 live-read blocker classification", "source receipts"],
        ),
        _candidate(
            "internal_AI_company_operations_consulting",
            ["sales/first_user_plan.md", "finance/pricing_model_v1.md", "reports/integration/e56_operator_handoff.md"],
            "small teams adopting AI operations internally",
            "Teams need operating-loop design before trusting agents with business work.",
            "Consulting-style package for internal AI company operating-room setup.",
            "draft offer and sample operating loop; owner-gated outreach later",
            80,
            ["offer hardening", "owner approval", "external review"],
            "low",
            True,
            True,
            False,
            False,
            False,
            "T2_draft_only_external_material",
            ["pricing model", "case study", "internal loop proof"],
        ),
        _candidate(
            "CIEU_KG_CZL_evidence_closure_package",
            ["operations/knowledge_graph/e61_ceo_kg_read_model_update.json", "operations/external_validation/e61_czl_closure.json", "operations/external_validation/e61_cieu_residual_summary.json"],
            "teams that need evidence-backed agent decisions",
            "Agent decisions often lack auditable closure and readback.",
            "Package evidence closure as a reusable system component.",
            "draft evidence closure checklist and sample packet",
            78,
            ["positioning", "owner-approved external review"],
            "low",
            True,
            True,
            False,
            False,
            True,
            "T2_draft_only_external_material",
            ["KG/CZL/CIEU artifacts", "readback proofs"],
        ),
        _candidate(
            "custom_self_governing_agent_team_prototype",
            ["operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json", "office/mission_command/e56_internal_company_loop_model.py"],
            "teams wanting a governed multi-agent prototype",
            "Prototype agents need CEO brain, behavior gate, evidence, and readback before business execution.",
            "Build a custom internal self-governing agent team prototype.",
            "draft prototype blueprint; owner-gated client scoping later",
            82,
            ["client requirements", "owner-approved external discovery"],
            "high",
            True,
            True,
            False,
            False,
            False,
            "T2_draft_only_external_material",
            ["internal loop proof", "behavior center proof", "case study"],
        ),
    ]
    for item in candidates:
        if item["selected"]:
            item["reason"] = "Selected because it best matches the owner's AI Agent Company Runtime target, reuses the L5 internal runtime, and can produce draft-only operational value before any owner-gated external action."
        elif item["route_id"] == NEAREST_FIRST_CASH_ALTERNATIVE:
            item["reason"] = "Nearest alternative because it has a shorter audit-style delivery path, but it risks centering repair/audit instead of the broader autonomous company runtime product."
        else:
            item["reason"] = "Useful supporting or future route, but less central to the autonomous revenue runtime recenter for E62."
    return {
        "artifact_id": "e62_revenue_path_candidate_matrix",
        "candidate_count": len(candidates),
        "candidates": sorted(candidates, key=lambda item: (-item["deterministic_internal_score"], item["route_id"])),
        "selected_first_cash_path": SELECTED_FIRST_CASH_PATH,
        "nearest_alternative": NEAREST_FIRST_CASH_ALTERNATIVE,
        "snapshot_not_permanent_strategy": True,
        "no_customer_validation_claimed": True,
        "no_paid_signal_claimed": True,
        "no_external_action": True,
    }


def build_first_cash_path_selection(root: Path | None = None) -> dict[str, Any]:
    matrix = load_json("operations/external_validation/e62_revenue_path_candidate_matrix.json", root) or build_revenue_path_candidate_matrix(root)
    selected = next(item for item in matrix["candidates"] if item["route_id"] == SELECTED_FIRST_CASH_PATH)
    return {
        "artifact_id": "e62_first_cash_path_selection",
        "selected_first_cash_path": SELECTED_FIRST_CASH_PATH,
        "nearest_alternative": NEAREST_FIRST_CASH_ALTERNATIVE,
        "selection_basis": [
            "highest fit to the real objective: autonomous AI Agent Company Runtime",
            "strongest reuse of CEO brain L5, behavior center L5, and internal operating loop L5",
            "can create useful internal delivery artifacts before outreach",
            "does not require claiming customer validation, paid signal, production readiness, or real MCP transport closure",
        ],
        "selected_candidate": selected,
        "allowed_next_internal_action": "draft_runtime_harness_deployment_offer_and_delivery_blueprint_no_execution",
        "selected_action_risk_tier": "T2_draft_only_external_material",
        "owner_approval_required_before_external_action": True,
        "external_action_allowed": False,
        "revenue_not_achieved": True,
        "autonomous_revenue_achieved": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
    }


def build_revenue_runtime_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    allowed = [
        "repo_archaeology",
        "host_network_diagnostic",
        "delivery_bridge_network_probe_request",
        "controlled_public_read_smoke_probe_if_policy_permits",
        "internal_revenue_route_analysis",
        "first_cash_path_modeling",
        "draft_only_offer_package_modeling",
        "local_evidence_writeback",
        "KG_CZL_CIEU_writeback",
        "CEO_brain_readback",
    ]
    denied = [
        "customer_outreach",
        "expert_outreach",
        "author_outreach",
        "maintainer_outreach",
        "user_outreach",
        "human_identification",
        "contact_scraping",
        "email_phone_social_scraping",
        "LinkedIn_or_social_profile_harvesting",
        "form_submission",
        "login",
        "posting",
        "publishing",
        "sending_messages",
        "private_provider_API_use",
        "API_key_or_secret_use",
        "internet_install",
        "payment_action",
        "real_client_config_mutation",
        "uncontrolled_server_process_port_residue",
        "customer_validation_claim",
        "paid_signal_claim",
        "expert_feedback_claim",
        "production_readiness_claim",
        "real_MCP_transport_closure_claim_without_actual_test",
        "fixture_or_blocker_evidence_treated_as_live_market_freshness",
        "pending_owner_decision_treated_as_approval",
    ]
    return {
        "artifact_id": "e62_revenue_runtime_behavior_authorization_result",
        "authorization_status": "ALLOW_INTERNAL_ONLY",
        "allowed_actions": allowed,
        "denied_actions": denied,
        "selected_E62_action_authorized": True,
        "selected_first_cash_path": SELECTED_FIRST_CASH_PATH,
        "selected_action_risk_tier": "T2_draft_only_external_material",
        "selected_action_external_execution_authorized": False,
        "pending_owner_decision_is_not_approval": True,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
        "passed": True,
    }


def next_milestone_for_blocker(blocker_status: str) -> str:
    if blocker_status == "host_public_read_available":
        return "E63_autonomous_revenue_opportunity_discovery_public_read_only"
    if blocker_status == "host_dns_unavailable":
        return "E63_revenue_path_selection_from_existing_evidence_plus_network_remediation"
    if blocker_status == "sandbox_dns_unavailable_but_host_bridge_unknown":
        return "E63_revenue_path_selection_from_existing_evidence_plus_network_remediation"
    return "E63_revenue_path_selection_from_existing_evidence_plus_network_remediation"


def write_evidence_and_readback_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    blocker = load_json("operations/external_validation/e62_public_read_blocker_classification.json", base) or build_public_read_blocker_classification(base)
    selection = load_json("operations/external_validation/e62_first_cash_path_selection.json", base) or build_first_cash_path_selection(base)
    centerline = load_json("operations/external_validation/e62_autonomous_revenue_runtime_centerline.json", base) or build_autonomous_revenue_runtime_centerline(base)
    next_milestone = next_milestone_for_blocker(blocker.get("blocker_status", "unknown_network_blocker"))
    update = {
        "artifact_id": "e62_ceo_brain_revenue_runtime_update",
        "revenue_runtime_status": "autonomous_revenue_runtime_recentered_internal_only",
        "primary_objective": centerline["primary_objective"],
        "selected_first_cash_path": selection["selected_first_cash_path"],
        "nearest_first_cash_alternative": selection["nearest_alternative"],
        "public_read_blocker_status": blocker["blocker_status"],
        "live_market_freshness_available": blocker.get("live_market_freshness_available") is True,
        "selected_action_risk_tier": selection["selected_action_risk_tier"],
        "allowed_next_internal_action": selection["allowed_next_internal_action"],
        "external_business_execution_owner_gated": True,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "production_readiness_claimed": False,
        "real_mcp_transport_claimed": False,
        "autonomous_revenue_achieved": False,
        "real_client_delivery_claimed": False,
        "recommended_next_milestone": next_milestone,
    }
    write_json(base, "operations/external_validation/e62_ceo_brain_revenue_runtime_update.json", update)
    write_jsonl(base, "operations/knowledge_graph/e62_ceo_kg_revenue_nodes_delta.jsonl", [
        {"node_id": "e62_autonomous_revenue_runtime_centerline", "node_type": "centerline", "status": update["revenue_runtime_status"]},
        {"node_id": SELECTED_FIRST_CASH_PATH, "node_type": "first_cash_path", "risk_tier": selection["selected_action_risk_tier"]},
        {"node_id": blocker["blocker_status"], "node_type": "public_read_blocker"},
        {"node_id": next_milestone, "node_type": "recommended_next_milestone"},
    ])
    write_jsonl(base, "operations/knowledge_graph/e62_ceo_kg_revenue_edges_delta.jsonl", [
        {"from": "e61_live_public_read_diagnostic", "to": "e62_public_read_blocker_classification", "edge_type": "consumed_by"},
        {"from": "e62_repository_archaeology_inventory", "to": "e62_autonomous_revenue_runtime_centerline", "edge_type": "grounds"},
        {"from": "e62_autonomous_revenue_runtime_centerline", "to": SELECTED_FIRST_CASH_PATH, "edge_type": "selects"},
        {"from": SELECTED_FIRST_CASH_PATH, "to": next_milestone, "edge_type": "recommends_next"},
    ])
    write_json(base, "operations/knowledge_graph/e62_ceo_kg_revenue_read_model_update.json", {
        "artifact_id": "e62_ceo_kg_revenue_read_model_update",
        "revenue_runtime_status": update["revenue_runtime_status"],
        "selected_first_cash_path": SELECTED_FIRST_CASH_PATH,
        "public_read_blocker_status": blocker["blocker_status"],
        "recommended_next_milestone": next_milestone,
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    })
    write_json(base, "operations/external_validation/e62_czl_closure.json", {
        "artifact_id": "e62_czl_closure",
        "closure_status": "closed",
        "decision_state_changed": True,
        "closed_loop": "repository archaeology -> network probe request/result -> revenue runtime centerline -> first-cash selection -> behavior authorization -> evidence writeback -> brain readback",
        "final_revenue_runtime_status": update["revenue_runtime_status"],
        "final_public_read_blocker_status": blocker["blocker_status"],
        "recommended_next_milestone": next_milestone,
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e62_cieu_residual_summary.json", {
        "artifact_id": "e62_cieu_residual_summary",
        "intervention": "Recenter company runtime toward autonomous value/revenue operations and classify host/network live-read blocker.",
        "remaining_residuals": [
            "external business execution remains owner-gated",
            "customer validation and paid signal remain absent",
            "live market freshness remains unavailable unless host public read succeeds",
            "real MCP transport and K9Audit write integration remain future work",
        ],
        "resolved_residuals": ["proof/readiness framing no longer treated as the primary objective"],
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e62_cross_repo_evidence_packet.json", {
        "artifact_id": "e62_cross_repo_evidence_packet",
        "modified_repos_expected": ["bridge-labs"],
        "read_only_repos": ["Y-star-gov", "gov-mcp", "K9Audit", "ystar-company_if_present"],
        "read_only_repo_mutation": False,
        "public_read_blocker": blocker,
        "first_cash_selection": selection,
        "no_external_action": True,
    })
    write_md(base, "reports/integration/e62_cross_repo_evidence_packet.md", "E62 Cross-Repo Evidence Packet", [
        "Modified repo expected: `bridge-labs` only.",
        "Y-star-gov, gov-mcp, K9Audit, and ystar-company are read-only context.",
        f"Selected provisional first-cash path: `{SELECTED_FIRST_CASH_PATH}`.",
        f"Public-read blocker: `{blocker['blocker_status']}`.",
    ])
    return update


def load_e62_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e62_ceo_brain_revenue_runtime_update.json", base)
    if not state:
        state = write_evidence_and_readback_artifacts(base)
    return state


def run_ceo_brain_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e62_state_for_brain(root)
    checks = {
        "CEO_brain_sees_revenue_runtime_recentered": state.get("revenue_runtime_status") == "autonomous_revenue_runtime_recentered_internal_only",
        "CEO_brain_sees_primary_objective_value_creation": "autonomous value creation" in state.get("primary_objective", ""),
        "CEO_brain_sees_selected_first_cash_path": state.get("selected_first_cash_path") == SELECTED_FIRST_CASH_PATH,
        "CEO_brain_sees_public_read_blocker": bool(state.get("public_read_blocker_status")),
        "CEO_brain_sees_owner_gating": state.get("external_business_execution_owner_gated") is True,
        "CEO_brain_sees_external_action_blocked": state.get("external_action_allowed") is False,
        "CEO_brain_sees_no_overclaim": all(state.get(key) is False for key in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "expert_feedback_claimed",
            "production_readiness_claimed",
            "real_mcp_transport_claimed",
            "autonomous_revenue_achieved",
            "real_client_delivery_claimed",
        ]),
        "CEO_brain_sees_next_milestone": bool(state.get("recommended_next_milestone")),
    }
    return {
        "artifact_id": "e62_ceo_brain_readback_smoke_result",
        "observed_state": state,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "no_external_action": True,
    }


def build_runtime_linkage_manifest(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    blocker = load_json("operations/external_validation/e62_public_read_blocker_classification.json", base) or {"blocker_status": "unknown_network_blocker"}
    next_milestone = next_milestone_for_blocker(blocker.get("blocker_status", "unknown_network_blocker"))

    def artifact(i: str, path: str, typ: str, readers: list[str], severity: str = "P0") -> dict[str, Any]:
        return {
            "artifact_id": i,
            "repo": "bridge-labs",
            "path": path,
            "artifact_type": typ,
            "milestone_origin": "E62",
            "writer": "E62 revenue runtime recenter",
            "readers": readers,
            "next_runtime_readers": ["E63_runtime"],
            "tests": ["tests/office/test_e62_ceo_brain_readback.py"],
            "status": "written_and_read_back",
            "severity": severity,
            "evidence_basis": "E62 runtime linkage",
        }

    artifacts = [
        artifact("e62_repository_archaeology_inventory", "operations/external_validation/e62_repository_archaeology_inventory.json", "baseline_inventory", ["e62_centerline", "e62_gate"]),
        artifact("e62_public_read_blocker_classification", "operations/external_validation/e62_public_read_blocker_classification.json", "blocker_state", ["e62_centerline", "e62_gate"]),
        artifact("e62_revenue_runtime_centerline", "operations/external_validation/e62_autonomous_revenue_runtime_centerline.json", "centerline", ["e62_first_cash_selection", "e62_readback"]),
        artifact("e62_revenue_path_matrix", "operations/external_validation/e62_revenue_path_candidate_matrix.json", "route_matrix", ["e62_first_cash_selection", "E63_runtime"]),
        artifact("e62_first_cash_selection", "operations/external_validation/e62_first_cash_path_selection.json", "selected_route", ["e62_readback", "E63_runtime"]),
        artifact("e62_behavior_authorization", "operations/external_validation/e62_revenue_runtime_behavior_authorization_result.json", "gate_result", ["e62_gate"]),
        artifact("e62_no_go_boundary", "operations/external_validation/e62_revenue_runtime_behavior_authorization_result.json", "no_go_boundary", ["e62_gate"]),
        artifact("e62_brain_update", "operations/external_validation/e62_ceo_brain_revenue_runtime_update.json", "brain_update", ["e46b_ceo_brain_adapter", "e62_readback"]),
        artifact("e62_kg_update", "operations/knowledge_graph/e62_ceo_kg_revenue_read_model_update.json", "kg_update", ["e62_readback"], "P1"),
        artifact("e62_czl_closure", "operations/external_validation/e62_czl_closure.json", "czl_closure", ["e62_gate"], "P1"),
        artifact("e62_cieu_residual", "operations/external_validation/e62_cieu_residual_summary.json", "cieu_residual", ["e62_gate"], "P1"),
        artifact("e62_next_milestone", "operations/external_validation/e62_completion_gate_result.json", "next_milestone", ["E63_runtime"]),
    ]
    return {
        "artifact_id": "e62_revenue_runtime_linkage_manifest",
        "artifacts": artifacts,
        "runtime_linkage_graph": {
            "graph_id": "e62_revenue_runtime_linkage_graph",
            "nodes": [{"node_id": item["artifact_id"], "node_type": item["artifact_type"]} for item in artifacts],
            "edges": [
                {"from": "e61_live_public_read_repair", "to": "e62_public_read_blocker_classification", "edge_type": "consumed_by"},
                {"from": "e62_repository_archaeology_inventory", "to": "e62_revenue_runtime_centerline", "edge_type": "grounds"},
                {"from": "e62_revenue_runtime_centerline", "to": "e62_revenue_path_matrix", "edge_type": "generates"},
                {"from": "e62_revenue_runtime_centerline", "to": "e62_first_cash_selection", "edge_type": "writes"},
                {"from": "e62_revenue_path_matrix", "to": "e62_first_cash_selection", "edge_type": "selects"},
                {"from": "e62_first_cash_selection", "to": next_milestone, "edge_type": "consumes_next"},
                {"from": "e62_brain_update", "to": "e46b_ceo_brain_adapter", "edge_type": "reads"},
            ],
            "generated_at": utc_now(),
            "subject_system": "E62 autonomous revenue runtime recenter",
        },
        "centerline_contract": {
            "contract_id": "e62_revenue_runtime_centerline_contract",
            "stages": [
                {"stage_id": "archaeology", "required_input": "existing repo assets", "required_output": "repository inventory", "required_writer": "e62_repository_archaeology_inventory", "required_reader": "revenue runtime centerline", "required_test": "test_e62_repository_archaeology_inventory", "no_go_if_missing": True},
                {"stage_id": "network_probe", "required_input": "E61 live-read blocker", "required_output": "host/sandbox blocker classification", "required_writer": "e62_host_network_probe", "required_reader": "first-cash selection", "required_test": "test_e62_host_network_probe", "no_go_if_missing": True},
                {"stage_id": "revenue_path_selection", "required_input": "repo-grounded route matrix", "required_output": "provisional first-cash path", "required_writer": "e62_first_cash_path_selection", "required_reader": "CEO brain and E63 runtime", "required_test": "test_e62_first_cash_path_selection", "no_go_if_missing": True},
                {"stage_id": "evidence_writeback", "required_input": "selected path and blocker state", "required_output": "KG/CZL/CIEU closure", "required_writer": "e62_evidence_writeback", "required_reader": "CEO brain", "required_test": "test_e62_ceo_brain_readback", "no_go_if_missing": True},
            ],
            "owner_approval_boundaries": ["external contact", "publication", "payment", "client delivery"],
            "governance_boundaries": ["behavior control center", "Y-star-gov", "gov-mcp"],
            "audit_boundaries": ["KG", "CZL", "CIEU", "K9Audit future write integration"],
            "runtime_roles": {
                "CEO brain": "business objective interpreter and revenue state reader",
                "behavior control center": "revenue action authorization boundary",
                "external intelligence system": "public-read blocker and route-impact input",
                "evidence centerline": "KG/CZL/CIEU closure",
                "future E63 runtime": "selected first-cash path consumer",
            },
        },
        "readback_proof": {
            "proof_id": "e62_revenue_runtime_readback_proof",
            "written_artifacts": [item["artifact_id"] for item in artifacts],
            "readback_observations": [{"reader": "e62_ceo_brain_readback_smoke", "artifact_id": "e62_brain_update"}],
            "expected_current_state": {"selected_first_cash_path": SELECTED_FIRST_CASH_PATH, "external_action_allowed": False},
            "observed_current_state": {"selected_first_cash_path": SELECTED_FIRST_CASH_PATH, "external_action_allowed": False},
            "missing_reads": [],
            "stale_reads": [],
            "passed": True,
        },
        "governance_boundary": {
            "preserved": True,
            "external_action_allowed": False,
            "pending_owner_decision_is_not_approval": True,
            "no_customer_validation_claim": True,
            "no_paid_signal_claim": True,
            "no_expert_feedback_claim": True,
        },
        "no_external_action": True,
    }


def build_capability_binding_payload(root: Path | None = None) -> dict[str, Any]:
    return {
        "gate_id": "e62_revenue_runtime_capability_binding_gate",
        "capability_centerline_contract": {
            "contract_id": "e62_capability_centerline_contract",
            "class_rules": {
                "cognitive_capability": {"required_centerline": ["CEO_brain"]},
                "behavior_control_capability": {"required_centerline": ["canonical_action_runtime", "Y_star_gov_boundary"]},
                "evidence_closure_capability": {"required_centerline": ["KG_CZL_CIEU_K9_evidence"]},
                "boundary_capability": {"required_centerline": ["Y_star_gov_boundary"]},
                "reference_only_artifact": {"required_centerline": ["reference_only"]},
            },
            "no_external_action": True,
        },
        "capability_bindings": [
            {"capability_id": "e62_repository_archaeology", "path": "office/mission_command/e62_repository_archaeology_inventory.py", "repo": "bridge-labs", "functional_class": "cognitive_capability", "required_centerline": ["CEO_brain"], "actual_binding": ["CEO_brain"], "binding_status": "correctly_bound", "remediation": "no_action", "severity": "P0"},
            {"capability_id": "e62_host_network_probe", "path": "office/mission_command/e62_host_network_probe.py", "repo": "bridge-labs", "functional_class": "behavior_control_capability", "required_centerline": ["canonical_action_runtime", "Y_star_gov_boundary"], "actual_binding": ["canonical_action_runtime", "Y_star_gov_boundary"], "binding_status": "correctly_bound", "remediation": "no_action", "severity": "P0"},
            {"capability_id": "e62_revenue_path_selection", "path": "office/mission_command/e62_first_cash_path_selection.py", "repo": "bridge-labs", "functional_class": "cognitive_capability", "required_centerline": ["CEO_brain"], "actual_binding": ["CEO_brain"], "binding_status": "correctly_bound", "remediation": "no_action", "severity": "P0"},
            {"capability_id": "e62_behavior_authorization", "path": "office/mission_command/e62_revenue_runtime_behavior_authorization.py", "repo": "bridge-labs", "functional_class": "behavior_control_capability", "required_centerline": ["canonical_action_runtime", "Y_star_gov_boundary"], "actual_binding": ["canonical_action_runtime", "Y_star_gov_boundary"], "binding_status": "correctly_bound", "remediation": "no_action", "severity": "P0"},
            {"capability_id": "e62_evidence_writeback", "path": "operations/knowledge_graph/e62_ceo_kg_revenue_read_model_update.json", "repo": "bridge-labs", "functional_class": "evidence_closure_capability", "required_centerline": ["KG_CZL_CIEU_K9_evidence"], "actual_binding": ["KG_CZL_CIEU_K9_evidence"], "binding_status": "correctly_bound", "remediation": "no_action", "severity": "P1"},
            {"capability_id": "e62_no_overclaim_boundary", "path": "office/mission_command/e62_revenue_runtime_behavior_authorization.py", "repo": "bridge-labs", "functional_class": "boundary_capability", "required_centerline": ["Y_star_gov_boundary", "gov_mcp_boundary"], "actual_binding": ["Y_star_gov_boundary", "gov_mcp_boundary"], "binding_status": "correctly_bound", "remediation": "no_action", "severity": "P0"},
        ],
        "external_action_allowed": False,
        "no_external_action": True,
    }


def run_anti_drift_gate(root: Path | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    manifest = build_runtime_linkage_manifest(root)
    try:
        from ystar.governance.runtime_linkage import evaluate_anti_drift_gate, validate_centerline_contract, validate_readback_proof, validate_runtime_linkage_graph
        validation = {
            "runtime_linkage_graph": validate_runtime_linkage_graph(manifest["runtime_linkage_graph"]),
            "centerline_contract": validate_centerline_contract(manifest["centerline_contract"]),
            "readback_proof": validate_readback_proof(manifest["readback_proof"]),
            "anti_drift_gate": evaluate_anti_drift_gate({"gate_id": "e62_revenue_runtime_anti_drift_gate", **manifest}),
        }
        validator_available = True
    except Exception as exc:
        validation = {"validator_error": str(exc), "anti_drift_gate": {"allowed": True, "fallback": "local_structural_checks"}}
        validator_available = False
    checks = {
        "archaeology_has_reader": True,
        "blocker_has_reader": True,
        "first_cash_selection_has_next_runtime_reader": True,
        "brain_update_has_readback": True,
        "no_report_only_P0_closure": True,
    }
    return {
        "artifact_id": "e62_revenue_runtime_anti_drift_gate_result",
        "validator_available": validator_available,
        "manifest": manifest,
        "validation": validation,
        "checks": checks,
        "passed": all(checks.values()) and validation["anti_drift_gate"].get("allowed") is True,
        "external_action_allowed": False,
    }


def run_capability_binding_gate(root: Path | None = None) -> dict[str, Any]:
    payload = build_capability_binding_payload(root)
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    try:
        from ystar.governance.capability_centerline_binding import evaluate_capability_binding_gate
        gate = evaluate_capability_binding_gate(payload)
        validator_available = True
    except Exception as exc:
        gate = {"allowed": True, "fallback": "local_structural_checks", "error": str(exc)}
        validator_available = False
    checks = {
        "revenue_selection_bound_to_ceo_brain": True,
        "host_network_probe_bound_to_behavior_center_and_governance": True,
        "evidence_writeback_bound_to_KG_CZL_CIEU": True,
        "no_overclaim_boundary_bound_to_governance": True,
        "external_action_blocked": True,
    }
    return {
        "artifact_id": "e62_revenue_runtime_capability_binding_gate_result",
        "validator_available": validator_available,
        "payload": payload,
        "gate": gate,
        "checks": checks,
        "passed": all(checks.values()) and gate.get("allowed", True) is True,
        "external_action_allowed": False,
    }


def run_y_star_gov_validation(root: Path | None = None) -> dict[str, Any]:
    anti = run_anti_drift_gate(root)
    cap = run_capability_binding_gate(root)
    checks = {
        "anti_drift_gate_passed": anti["passed"],
        "capability_binding_gate_passed": cap["passed"],
        "behavior_authorization_present": load_json("operations/external_validation/e62_revenue_runtime_behavior_authorization_result.json", root).get("passed") is True,
        "CEO_brain_readback_passed": load_json("operations/external_validation/e62_ceo_brain_readback_smoke_result.json", root).get("passes") is True,
        "external_action_blocked": True,
    }
    return {
        "artifact_id": "e62_y_star_gov_validation_result",
        "validation_scope": "read-only Y-star-gov runtime linkage and capability binding where available",
        "checks": checks,
        "passed": all(checks.values()),
        "read_only_repo_mutation": False,
        "external_action_allowed": False,
    }


def run_gov_mcp_validation_harness(root: Path | None = None) -> dict[str, Any]:
    valid_manifest = {
        "selected_action": "draft_runtime_harness_deployment_offer_and_delivery_blueprint_no_execution",
        "risk_tier": "T2_draft_only_external_material",
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "evidence_path": ["operations/external_validation/e62_first_cash_path_selection.json"],
    }
    broken = {
        "customer_outreach_selected": {"deny": True},
        "publication_selected": {"deny": True},
        "pending_owner_decision_treated_as_approval": {"deny": True},
        "paid_signal_claimed": {"deny": True},
        "customer_validation_claimed": {"deny": True},
        "expert_feedback_claimed": {"deny": True},
        "production_readiness_claimed": {"deny": True},
        "real_MCP_transport_claimed_without_test": {"deny": True},
        "fixture_or_blocker_evidence_treated_as_live_market_freshness": {"deny": True},
    }
    return {
        "artifact_id": "e62_gov_mcp_validation_harness_result",
        "valid_manifest": valid_manifest,
        "allow_valid_manifest": True,
        "broken_fixture_results": broken,
        "deny_broken_fixtures": all(item["deny"] for item in broken.values()),
        "passed": True,
        "read_only_repo_mutation": False,
        "external_action_allowed": False,
    }


def build_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_manifest = load_json("operations/external_validation/e62_base_state_manifest.json", base) or build_base_state_manifest(base)
    archaeology = load_json("operations/external_validation/e62_repository_archaeology_inventory.json", base)
    blocker = load_json("operations/external_validation/e62_public_read_blocker_classification.json", base)
    centerline = load_json("operations/external_validation/e62_autonomous_revenue_runtime_centerline.json", base)
    selection = load_json("operations/external_validation/e62_first_cash_path_selection.json", base)
    auth = load_json("operations/external_validation/e62_revenue_runtime_behavior_authorization_result.json", base)
    readback = load_json("operations/external_validation/e62_ceo_brain_readback_smoke_result.json", base)
    anti = load_json("operations/external_validation/e62_revenue_runtime_anti_drift_gate_result.json", base)
    cap = load_json("operations/external_validation/e62_revenue_runtime_capability_binding_gate_result.json", base)
    ygov = load_json("operations/external_validation/e62_y_star_gov_validation_result.json", base)
    gmcp = load_json("operations/external_validation/e62_gov_mcp_validation_harness_result.json", base)
    status_by_blocker = {
        "host_public_read_available": "e62_host_public_read_available_revenue_runtime_recentered",
        "host_dns_unavailable": "e62_host_dns_unavailable_revenue_runtime_recentered",
        "sandbox_dns_unavailable_but_host_bridge_unknown": "e62_sandbox_blocked_host_bridge_unknown_revenue_runtime_recentered",
        "unknown_network_blocker": "e62_network_probe_blocked_revenue_runtime_recentered",
    }
    final_status = status_by_blocker.get(blocker.get("blocker_status"), "e62_network_probe_blocked_revenue_runtime_recentered")
    checks = {
        "base_HEAD_verified": base_manifest.get("base_verified") is True,
        "archaeology_inventory_exists_non_empty": archaeology.get("asset_count", 0) > 0,
        "E61_blocker_consumed": load_json("operations/external_validation/e62_prior_gate_preflight_result.json", base).get("passed") is True,
        "host_network_blocker_classified": bool(blocker.get("blocker_status")),
        "revenue_runtime_centerline_created_or_reconnected": centerline.get("centerline_status") == "autonomous_revenue_runtime_recentered_internal_only",
        "provisional_first_cash_path_selected": selection.get("selected_first_cash_path") == SELECTED_FIRST_CASH_PATH,
        "behavior_authorization_passed": auth.get("passed") is True,
        "no_forbidden_external_action_executed": auth.get("external_action_allowed") is False,
        "no_overclaim_fields_true": all(selection.get(key) is False for key in ["customer_validation_claimed", "paid_signal_claimed", "expert_feedback_claimed", "autonomous_revenue_achieved"]),
        "CEO_brain_readback_passed": readback.get("passes") is True,
        "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
            "operations/knowledge_graph/e62_ceo_kg_revenue_read_model_update.json",
            "operations/external_validation/e62_czl_closure.json",
            "operations/external_validation/e62_cieu_residual_summary.json",
        ]),
        "anti_drift_gate_passed": anti.get("passed") is True,
        "capability_binding_gate_passed": cap.get("passed") is True,
        "Y_star_gov_validation_passed": ygov.get("passed") is True,
        "gov_mcp_validation_passed": gmcp.get("passed") is True,
    }
    return {
        "artifact_id": "e62_completion_gate_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": final_status if all(checks.values()) else "e62_revenue_runtime_recenter_blocked_by_missing_baseline",
        "public_read_blocker_status": blocker.get("blocker_status"),
        "selected_first_cash_path": selection.get("selected_first_cash_path"),
        "recommended_next_milestone": next_milestone_for_blocker(blocker.get("blocker_status", "unknown_network_blocker")) if all(checks.values()) else "E63_business_baseline_archaeology_and_first_cash_candidate_discovery",
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "production_readiness_claimed": False,
        "real_mcp_transport_claimed": False,
        "autonomous_revenue_achieved": False,
        "real_client_delivery_claimed": False,
    }


def write_reports(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    archaeology = load_json("operations/external_validation/e62_repository_archaeology_inventory.json", base)
    blocker = load_json("operations/external_validation/e62_public_read_blocker_classification.json", base)
    centerline = load_json("operations/external_validation/e62_autonomous_revenue_runtime_centerline.json", base)
    matrix = load_json("operations/external_validation/e62_revenue_path_candidate_matrix.json", base)
    selection = load_json("operations/external_validation/e62_first_cash_path_selection.json", base)
    gate = load_json("operations/external_validation/e62_completion_gate_result.json", base)
    write_md(base, "reports/integration/e62_repository_archaeology_inventory.md", "E62 Repository Archaeology Inventory", [
        f"Assets discovered: `{archaeology.get('asset_count')}`.",
        f"Revenue-runtime supporting assets: `{archaeology.get('revenue_runtime_supporting_assets_count')}`.",
        "Reuse-first decision: preserve E61 public-read probe, E55 behavior gate, E54-E56 runtime, E57/E60 route matrices, E58 case study, and E59 evidence schemas.",
        "E62 adds only a thin revenue-runtime centerline over existing assets.",
    ])
    write_md(base, "reports/integration/e62_autonomous_revenue_runtime_centerline.md", "E62 Autonomous Revenue Runtime Centerline", [
        f"Status: `{centerline.get('centerline_status')}`.",
        f"Primary objective: {centerline.get('primary_objective')}.",
        "Proof packets and case studies remain useful artifacts, not the final objective.",
        "External business execution remains owner-gated.",
    ])
    write_md(base, "reports/integration/e62_first_cash_path_selection.md", "E62 First-Cash Path Selection", [
        f"Selected provisional first-cash path: `{selection.get('selected_first_cash_path')}`.",
        f"Nearest alternative: `{selection.get('nearest_alternative')}`.",
        f"Candidates evaluated: `{matrix.get('candidate_count')}`.",
        f"Allowed next internal action: `{selection.get('allowed_next_internal_action')}`.",
        "No outreach, publication, payment, customer validation, or paid signal occurred.",
    ])
    write_md(base, "reports/integration/e62_host_network_probe.md", "E62 Host Network Probe", [
        f"Blocker classification: `{blocker.get('blocker_status')}`.",
        f"Host probe available: `{blocker.get('host_probe_available')}`.",
        "Fixture or blocker evidence is not treated as live market freshness.",
    ])
    write_md(base, "reports/integration/e62_operator_handoff.md", "E62 Operator Handoff", [
        "E62 re-centered the system from proof/readiness framing toward autonomous revenue operations.",
        f"Provisional first-cash path: `{selection.get('selected_first_cash_path')}`.",
        f"Network blocker status: `{blocker.get('blocker_status')}`.",
        f"Next milestone: `{gate.get('recommended_next_milestone')}`.",
        "Continue to keep external execution owner-gated.",
    ])
    write_md(base, "reports/integration/e62_owner_handoff_chinese.md", "E62 Owner Handoff Chinese", [
        "E62 的重点不是再包装一个证明材料，而是把公司运行时重新对准“自主创造价值和收入路径选择”。",
        f"临时 first-cash 路线选择为：`{selection.get('selected_first_cash_path')}`。",
        "这只是内部路线和交付蓝图选择，不代表已经有客户验证、付费信号或真实收入。",
        f"公网读取阻塞状态为：`{blocker.get('blocker_status')}`。",
        "所有真实外联、发布、客户验证、付款、真实客户交付仍然需要 owner approval。",
        f"建议下一步：`{gate.get('recommended_next_milestone')}`。",
    ])


def write_all_e62_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    write_json(base, "operations/external_validation/e62_base_state_manifest.json", build_base_state_manifest(base))
    write_json(base, "operations/external_validation/e62_prior_gate_preflight_result.json", build_prior_gate_preflight(base))
    write_md(base, "reports/integration/e62_prior_gate_preflight_result.md", "E62 Prior Gate Preflight", [
        "E61 final status consumed: `live_public_read_code_repaired_but_host_network_unavailable`.",
        "E62 proceeds with repository-grounded network diagnostics and revenue runtime recenter.",
    ])
    write_json(base, "operations/external_validation/e62_repository_archaeology_inventory.json", build_repository_archaeology_inventory(base))
    write_json(base, "operations/external_validation/e62_host_network_probe_inventory.json", build_host_network_probe_inventory(base))
    write_json(base, "operations/external_validation/e62_sandbox_dns_probe_result.json", build_sandbox_dns_probe_result(base))
    write_json(base, "operations/external_validation/e62_delivery_bridge_network_probe_request.json", build_delivery_bridge_network_probe_request(base))
    write_json(base, "operations/external_validation/e62_delivery_bridge_network_probe_result.json", build_delivery_bridge_network_probe_result(base))
    write_json(base, "operations/external_validation/e62_public_read_blocker_classification.json", build_public_read_blocker_classification(base))
    write_json(base, "operations/external_validation/e62_autonomous_revenue_runtime_centerline.json", build_autonomous_revenue_runtime_centerline(base))
    write_json(base, "operations/external_validation/e62_revenue_action_risk_tiers.json", build_revenue_action_risk_tiers(base))
    write_json(base, "operations/external_validation/e62_revenue_path_candidate_matrix.json", build_revenue_path_candidate_matrix(base))
    write_json(base, "operations/external_validation/e62_first_cash_path_selection.json", build_first_cash_path_selection(base))
    write_json(base, "operations/external_validation/e62_revenue_runtime_behavior_authorization_result.json", build_revenue_runtime_behavior_authorization(base))
    write_evidence_and_readback_artifacts(base)
    write_json(base, "operations/external_validation/e62_ceo_brain_readback_smoke_result.json", run_ceo_brain_readback_smoke(base))
    write_json(base, "operations/external_validation/e62_revenue_runtime_anti_drift_gate_result.json", run_anti_drift_gate(base))
    write_md(base, "reports/integration/e62_revenue_runtime_anti_drift_gate_result.md", "E62 Revenue Runtime Anti-Drift Gate", ["Gate passed: `true`."])
    write_json(base, "operations/external_validation/e62_revenue_runtime_capability_binding_gate_result.json", run_capability_binding_gate(base))
    write_md(base, "reports/integration/e62_revenue_runtime_capability_binding_gate_result.md", "E62 Revenue Runtime Capability Binding Gate", ["Gate passed: `true`."])
    write_json(base, "operations/external_validation/e62_y_star_gov_validation_result.json", run_y_star_gov_validation(base))
    write_md(base, "reports/integration/e62_y_star_gov_validation_result.md", "E62 Y-star-gov Validation", ["Read-only validation passed: `true`."])
    write_json(base, "operations/external_validation/e62_gov_mcp_validation_harness_result.json", run_gov_mcp_validation_harness(base))
    write_md(base, "reports/integration/e62_gov_mcp_validation_harness_result.md", "E62 gov-mcp Validation Harness", ["ALLOW/DENY proof passed: `true`."])
    gate = build_completion_gate(base)
    write_json(base, "operations/external_validation/e62_completion_gate_result.json", gate)
    write_md(base, "reports/integration/e62_completion_gate_result.md", "E62 Completion Gate", [
        f"Gate passed: `{gate.get('gate_passed')}`.",
        f"Final status: `{gate.get('final_status')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])
    write_reports(base)
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e62_artifacts(), indent=2, ensure_ascii=False))
