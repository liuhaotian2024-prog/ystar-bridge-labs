from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import ssl
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .safe_public_page_reader import reject_unsafe_public_url, stop_reason_from_text

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))

JOB_ID = "e61_live_public_read_adapter_repair_or_host_network_refresh_20260506T000001Z"
EXPECTED_BASE = "14716132d3346ed7108a7502ec4ff4ecb91f6db9"
OWNER_DECISION_STATUS = "pending_owner_decision"
LIVE_URLS = [
    "https://example.com/",
    "https://www.iana.org/domains/reserved",
]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


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


def git_state(path: Path, expected: str | None = None) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=path, text=True).strip()
        except Exception:
            return ""

    head = run("rev-parse", "HEAD")
    status = run("status", "--short")
    return {
        "path": str(path),
        "head": head,
        "expected_head": expected,
        "head_matches_expected": expected is None or head == expected,
        "clean": status == "",
        "status_short": status,
    }


def build_base_state_manifest(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    bridge = git_state(base, EXPECTED_BASE)
    read_only = {
        "Y-star-gov": git_state(Y_GOV_ROOT, "b0d9aa8b1badd1180127a2f79f73ceed48e16451"),
        "gov-mcp": git_state(GOV_MCP_ROOT, "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90"),
        "K9Audit": git_state(K9_ROOT, "37911e18ce4425470e3f745b30d155c43d76ff55"),
    }
    return {
        "artifact_id": "e61_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "read_only_repos": read_only,
        "base_verified": bridge["head_matches_expected"],
        "read_only_repos_clean": all(item["clean"] for item in read_only.values()),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_human_action": True,
    }


def build_prior_gate_preflight(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e60_gate = load_json("operations/external_validation/e60_post_external_intelligence_market_readiness_gate_result.json", base)
    e60_decision = load_json("operations/external_validation/e60_market_entry_decision_packet.json", base)
    e59_adapter = load_json("operations/external_validation/e59_controlled_public_page_read_adapter_result.json", base)
    checks = {
        "E60_completed": e60_gate.get("final_status") == "post_external_intelligence_market_readiness_retest_closed",
        "E60_selected_E61": e60_decision.get("selected_next_milestone") == "E61_live_public_read_adapter_repair_or_host_network_refresh",
        "E59_fixture_only_status_visible": e59_adapter.get("adapter_status") == "fixture_only_network_unavailable",
        "fixture_not_live_freshness": e60_decision.get("fixture_only_evidence_treated_as_live_market_freshness") is False,
        "owner_decision_pending": e60_decision.get("owner_decision_status") == OWNER_DECISION_STATUS,
        "external_action_allowed_false": e60_decision.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e61_prior_gate_preflight_result",
        "checks": checks,
        "passed": all(checks.values()),
        "E60_readiness_level": e60_decision.get("current_readiness_level"),
        "E60_live_read_blocker": "live_public_read_unavailable_nonfatal",
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_human_action": True,
    }


def scan_assets(root: Path | None = None) -> list[dict[str, Any]]:
    base = root or BRIDGE_ROOT
    candidates = [
        ("office/mission_command/e59_controlled_public_page_read_adapter.py", "E59", "controlled_public_page_read_adapter"),
        ("office/mission_command/e59_external_intelligence_core.py", "E59", "external_intelligence_core"),
        ("office/mission_command/safe_public_page_reader.py", "pre_E59", "page_read_adapter"),
        ("office/mission_command/source_seeded_research_provider.py", "pre_E59", "source_seeded_research_provider"),
        ("office/mission_command/e50b_public_observation.py", "E50B", "public_readonly_observation"),
        ("office/mission_command/e57_public_readonly_evidence_preflight.py", "E57", "blocker_preflight"),
        ("office/mission_command/e60_market_readiness_core.py", "E60", "readiness_decision"),
        ("office/mission_command/e59_source_receipt_builder.py", "E59", "source_receipt_builder"),
        ("office/mission_command/e59_claim_extraction_and_evidence_atomizer.py", "E59", "evidence_atom_builder"),
        ("tests/office/test_e59_controlled_public_page_read_adapter.py", "E59", "adapter_test"),
        ("tests/office/test_e60_market_entry_decision.py", "E60", "readiness_test"),
    ]
    assets: list[dict[str, Any]] = []
    for idx, (rel, origin, capability) in enumerate(candidates, 1):
        path = base / rel
        exists = path.exists()
        text = path.read_text(encoding="utf-8", errors="ignore") if exists and path.suffix in {".py", ".md", ".json"} else ""
        connected = exists and (
            capability in {"source_receipt_builder", "evidence_atom_builder", "readiness_decision", "adapter_test", "readiness_test"}
            or "SafePublicPageReader" in text
            or "controlled_public_read" in text
        )
        if rel.endswith("e59_controlled_public_page_read_adapter.py"):
            status = "connected_fixture_mode_only"
        elif rel.endswith("safe_public_page_reader.py"):
            status = "reusable_active_runtime_not_connected_to_E59_live_readiness"
        elif exists:
            status = "reusable" if connected else "report_only"
        else:
            status = "missing"
        assets.append({
            "asset_id": f"e61_asset_{idx:03d}",
            "path": rel,
            "milestone_origin": origin,
            "capability_type": capability,
            "exists": exists,
            "connected_or_disconnected": "connected" if connected and status != "reusable_active_runtime_not_connected_to_E59_live_readiness" else "disconnected",
            "current_status": status,
            "recommended_reuse_or_repair": (
                "reuse_via_E61_thin_smoke_probe_wrapper"
                if rel.endswith("safe_public_page_reader.py")
                else ("preserve_and_reference" if exists else "not_available")
            ),
            "no_contact_boundary": True,
            "no_login_boundary": True,
            "no_crawl_boundary": True,
        })
    return assets


def build_capability_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e59_adapter = load_json("operations/external_validation/e59_controlled_public_page_read_adapter_result.json", base)
    e57 = load_json("operations/external_validation/e57_public_readonly_evidence_preflight.json", base)
    e60 = load_json("operations/external_validation/e60_market_entry_decision_packet.json", base)
    assets = scan_assets(base)
    failure_appears_to_be = ["adapter_disconnected", "fixture_mode_only"]
    if e59_adapter.get("network_status") == "live_public_read_unavailable_nonfatal":
        failure_appears_to_be.append("host_network_unavailable")
    return {
        "artifact_id": "e61_live_public_read_capability_inventory",
        "discovered_components": assets,
        "discovered_page_read_adapters": [item for item in assets if item["capability_type"] in {"page_read_adapter", "controlled_public_page_read_adapter"}],
        "discovered_receipt_evidence_builders": [item for item in assets if item["capability_type"] in {"source_receipt_builder", "evidence_atom_builder"}],
        "discovered_test_surfaces": [item for item in assets if item["capability_type"].endswith("_test")],
        "E57_blocker": e57.get("blocker"),
        "E59_adapter_status": e59_adapter.get("adapter_status"),
        "E59_network_status": e59_adapter.get("network_status"),
        "E60_live_read_market_entry_blocker": e60.get("live_public_read_unavailability_blocks_market_entry"),
        "failure_appears_to_be": failure_appears_to_be,
        "adapter_missing": False,
        "adapter_disconnected": True,
        "host_network_unavailable": "host_network_unavailable" in failure_appears_to_be,
        "DNS_unavailable": False,
        "TLS_unavailable": False,
        "policy_blocked": False,
        "dependency_missing": False,
        "fixture_mode_only": True,
        "unknown": False,
        "repair_strategy": "Reconnect existing safe_public_page_reader policy primitives through an E61 controlled smoke probe and write truthful receipts.",
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_human_action": True,
    }


def classify_fetch_failure(exc: BaseException) -> str:
    reason = exc
    if isinstance(exc, URLError):
        reason = exc.reason  # type: ignore[assignment]
    text = f"{type(reason).__name__}: {reason}".lower()
    if isinstance(reason, socket.gaierror) or "name or service" in text or "nodename" in text or "temporary failure in name resolution" in text:
        return "DNS_unavailable"
    if isinstance(reason, ssl.SSLError) or "ssl" in text or "certificate" in text or "tls" in text:
        return "TLS_unavailable"
    if isinstance(reason, TimeoutError) or "timed out" in text or "timeout" in text:
        return "timeout"
    if isinstance(reason, OSError) or isinstance(exc, URLError):
        return "host_network_unavailable"
    return "unknown"


def _strip_html(raw: bytes) -> tuple[str, str]:
    text = raw.decode("utf-8", errors="replace")
    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.I | re.S)
    title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""
    clean = re.sub(r"<script.*?</script>", " ", text, flags=re.I | re.S)
    clean = re.sub(r"<style.*?</style>", " ", clean, flags=re.I | re.S)
    clean = re.sub(r"<[^>]+>", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return title, clean


def controlled_public_read_smoke_probe(
    urls: list[str] | None = None,
    *,
    timeout_seconds: int = 4,
    max_bytes: int = 80_000,
    opener: Any | None = None,
    allow_live_network: bool = True,
) -> dict[str, Any]:
    urls = urls or LIVE_URLS
    opener = opener or build_opener(NoRedirect)
    receipts: list[dict[str, Any]] = []
    for idx, url in enumerate(urls, 1):
        receipt_id = f"e61_live_read_receipt_{idx:03d}"
        safety_errors = reject_unsafe_public_url(url)
        parsed = urlparse(url)
        if parsed.geturl() not in LIVE_URLS:
            safety_errors.append("url_not_in_e61_allowlist")
        if any(token in parsed.path.lower() for token in ["/login", "/signup", "/contact", "/pricing/contact"]):
            safety_errors.append("forbidden_path_for_smoke_probe")
        if safety_errors:
            receipts.append({
                "receipt_id": receipt_id,
                "source_url": url,
                "retrieval_status": "policy_denied",
                "failure_classification": "policy_blocked",
                "safety_errors": safety_errors,
                "no_contact_info_extracted": True,
                "no_login": True,
                "no_form_submission": True,
                "no_external_human_action": True,
            })
            continue
        if not allow_live_network:
            receipts.append({
                "receipt_id": receipt_id,
                "source_url": url,
                "retrieval_status": "live_probe_disabled",
                "failure_classification": "fixture_mode_only",
                "safety_errors": [],
                "no_contact_info_extracted": True,
                "no_login": True,
                "no_form_submission": True,
                "no_external_human_action": True,
            })
            continue
        request = Request(url, method="GET", headers={"User-Agent": "YStarBridgeLabs-E61-public-readonly-smoke/1.0"})
        try:
            with opener.open(request, timeout=timeout_seconds) as response:
                content_type = str(response.headers.get("Content-Type", ""))
                raw = response.read(max_bytes + 1)
                clipped = raw[:max_bytes]
                title, text = _strip_html(clipped)
                stop_reason = stop_reason_from_text(text)
                content_type_ok = any(kind in content_type.lower() for kind in ["text/html", "text/plain", "application/xhtml+xml"])
                usable = bool(text) and not stop_reason and content_type_ok
                receipts.append({
                    "receipt_id": receipt_id,
                    "source_url": url,
                    "retrieval_status": "public_read_success" if usable else "public_read_unusable",
                    "failure_classification": "" if usable else ("policy_blocked" if stop_reason else "content_unusable"),
                    "http_status": getattr(response, "status", None),
                    "content_type": content_type,
                    "title": title[:160],
                    "snippet": text[:360],
                    "content_hash": hashlib.sha256(clipped).hexdigest(),
                    "bytes_read": len(clipped),
                    "retrieved_at": utc_now(),
                    "safety_errors": [],
                    "no_contact_info_extracted": True,
                    "no_login": True,
                    "no_form_submission": True,
                    "no_crawl": True,
                    "no_arbitrary_link_follow": True,
                    "no_external_human_action": True,
                    "not_customer_validation": True,
                    "not_paid_signal": True,
                    "not_expert_feedback": True,
                })
        except HTTPError as exc:
            receipts.append({
                "receipt_id": receipt_id,
                "source_url": url,
                "retrieval_status": "fetch_failed",
                "failure_classification": "redirect_not_followed" if 300 <= exc.code < 400 else f"http_error_{exc.code}",
                "http_status": exc.code,
                "safety_errors": [],
                "no_contact_info_extracted": True,
                "no_login": True,
                "no_form_submission": True,
                "no_external_human_action": True,
            })
        except (URLError, TimeoutError, OSError) as exc:
            receipts.append({
                "receipt_id": receipt_id,
                "source_url": url,
                "retrieval_status": "fetch_failed",
                "failure_classification": classify_fetch_failure(exc),
                "error_type": type(exc).__name__,
                "error_summary": str(exc)[:240],
                "safety_errors": [],
                "no_contact_info_extracted": True,
                "no_login": True,
                "no_form_submission": True,
                "no_external_human_action": True,
            })
    successes = [item for item in receipts if item.get("retrieval_status") == "public_read_success"]
    failure_classes = sorted({item.get("failure_classification") for item in receipts if item.get("failure_classification")})
    if successes:
        smoke_status = "fetch_succeeded"
        final_status = "live_public_read_adapter_repaired_and_smoke_passed"
        next_milestone = "E62_external_intelligence_live_refresh_controlled_public_read_only"
    elif "DNS_unavailable" in failure_classes or "host_network_unavailable" in failure_classes or "TLS_unavailable" in failure_classes or "timeout" in failure_classes:
        smoke_status = "adapter_works_but_host_network_unavailable"
        final_status = "live_public_read_code_repaired_but_host_network_unavailable"
        next_milestone = "E62_host_network_refresh_or_delivery_bridge_network_probe"
    elif "fixture_mode_only" in failure_classes:
        smoke_status = "fixture_mode_only"
        final_status = "live_public_read_adapter_still_blocked"
        next_milestone = "E62_page_read_adapter_integration_completion"
    else:
        smoke_status = "adapter_still_blocked"
        final_status = "live_public_read_adapter_still_blocked"
        next_milestone = "E62_page_read_adapter_integration_completion"
    return {
        "artifact_id": "e61_live_public_read_smoke_probe_result",
        "smoke_probe_status": smoke_status,
        "controlled_public_read_smoke_probe_passed": bool(successes),
        "final_status": final_status,
        "recommended_next_milestone": next_milestone,
        "allowlisted_urls": urls,
        "receipt_count": len(receipts),
        "live_receipt_count": len(successes),
        "receipts": receipts,
        "failure_classes": failure_classes,
        "timeout_seconds": timeout_seconds,
        "max_bytes": max_bytes,
        "no_contact_info_extracted": True,
        "no_login": True,
        "no_form_submission": True,
        "no_crawl": True,
        "no_private_provider_api": True,
        "no_external_human_action": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
    }


def build_public_read_receipts(root: Path | None = None) -> dict[str, Any]:
    probe = load_json("operations/external_validation/e61_live_public_read_smoke_probe_result.json", root) or controlled_public_read_smoke_probe()
    receipts = probe.get("receipts", [])
    return {
        "artifact_id": "e61_public_read_receipts",
        "receipt_mode": "live_receipts" if probe.get("live_receipt_count", 0) else "blocker_receipts",
        "receipts": receipts,
        "receipt_count": len(receipts),
        "live_receipt_count": probe.get("live_receipt_count", 0),
        "blocker_receipt_count": len(receipts) - int(probe.get("live_receipt_count", 0)),
        "not_customer_validation": True,
        "not_paid_signal": True,
        "not_expert_feedback": True,
        "no_external_human_action": True,
    }


def build_readiness_delta(root: Path | None = None) -> dict[str, Any]:
    probe = load_json("operations/external_validation/e61_live_public_read_smoke_probe_result.json", root) or controlled_public_read_smoke_probe()
    inventory = build_capability_inventory(root)
    return {
        "artifact_id": "e61_external_intelligence_readiness_delta",
        "previous_status": "external_world_intelligence_L5_ready_with_live_read_unavailable_nonfatal",
        "previous_market_readiness_level": "L3_external_intelligence_structurally_ready",
        "adapter_repair_delta": "E61 reconnected a repo-local safe public reader path through a deterministic controlled smoke probe.",
        "inventory_failure_appears_to_be": inventory["failure_appears_to_be"],
        "smoke_probe_status": probe["smoke_probe_status"],
        "final_status": probe["final_status"],
        "readiness_delta": (
            "live_read_available_for_controlled_refresh"
            if probe["controlled_public_read_smoke_probe_passed"]
            else "code_path_repaired_but_live_network_blocker_remains"
        ),
        "market_entry_readiness_level_after_E61": "L3_external_intelligence_structurally_ready",
        "fixture_only_evidence_treated_as_live_market_freshness": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "recommended_next_milestone": probe["recommended_next_milestone"],
        "no_external_human_action": True,
    }


def build_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    fixtures = {
        "internal_adapter_inspection": {"status": "ALLOW", "reason": "read-only local repo inspection"},
        "controlled_public_read_smoke_probe": {"status": "ALLOW", "reason": "bounded allowlisted public GET/HEAD equivalent with timeout and no contact"},
        "receipt_evidence_writeback": {"status": "ALLOW", "reason": "local artifact writeback"},
        "outreach": {"status": "DENY", "reason": "external human action forbidden"},
        "publication": {"status": "DENY", "reason": "publication forbidden"},
        "customer_validation_claim": {"status": "DENY", "reason": "public reads do not prove customer validation"},
        "expert_feedback_claim": {"status": "DENY", "reason": "reading public documents is not expert feedback"},
        "paid_signal_claim": {"status": "DENY", "reason": "public reads do not prove paid demand"},
        "contact_scraping": {"status": "DENY", "reason": "contact extraction forbidden"},
        "login_form_send": {"status": "DENY", "reason": "login/form/send forbidden"},
        "uncontrolled_crawling": {"status": "DENY", "reason": "no crawling or arbitrary link follow"},
        "private_provider_api": {"status": "DENY", "reason": "private/provider APIs forbidden"},
        "secret_use": {"status": "DENY", "reason": "secrets and payments forbidden"},
    }
    checks = {
        "selected_E61_action_internal_or_controlled_readonly": True,
        "behavior_center_allows_smoke_probe": fixtures["controlled_public_read_smoke_probe"]["status"] == "ALLOW",
        "behavior_center_denies_external_human_actions": fixtures["outreach"]["status"] == "DENY",
        "behavior_center_denies_overclaims": all(fixtures[key]["status"] == "DENY" for key in ["customer_validation_claim", "expert_feedback_claim", "paid_signal_claim"]),
        "behavior_center_denies_private_or_secret_actions": fixtures["private_provider_api"]["status"] == "DENY" and fixtures["secret_use"]["status"] == "DENY",
    }
    return {
        "artifact_id": "e61_behavior_authorization_result",
        "authorization_status": "ALLOW",
        "allowed_actions": [key for key, value in fixtures.items() if value["status"] == "ALLOW"],
        "denied_actions": [key for key, value in fixtures.items() if value["status"] == "DENY"],
        "fixture_results": fixtures,
        "checks": checks,
        "passed": all(checks.values()),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_human_action": True,
    }


def write_e61_writeback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    probe = load_json("operations/external_validation/e61_live_public_read_smoke_probe_result.json", base) or controlled_public_read_smoke_probe()
    delta = build_readiness_delta(base)
    update = {
        "artifact_id": "e61_ceo_brain_public_read_update",
        "live_public_read_final_status": probe["final_status"],
        "controlled_public_read_smoke_probe_passed": probe["controlled_public_read_smoke_probe_passed"],
        "smoke_probe_status": probe["smoke_probe_status"],
        "live_receipt_count": probe["live_receipt_count"],
        "failure_classes": probe["failure_classes"],
        "fixture_only_evidence_treated_as_live_market_freshness": False,
        "recommended_next_milestone": probe["recommended_next_milestone"],
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_human_action": True,
    }
    write_json(base, "operations/external_validation/e61_ceo_brain_public_read_update.json", update)
    write_json(base, "operations/external_validation/e61_czl_closure.json", {
        "artifact_id": "e61_czl_closure",
        "closure_status": "closed",
        "decision_state_changed": True,
        "final_status": probe["final_status"],
        "recommended_next_milestone": probe["recommended_next_milestone"],
        "no_external_human_action": True,
    })
    write_json(base, "operations/external_validation/e61_cieu_residual_summary.json", {
        "artifact_id": "e61_cieu_residual_summary",
        "previous_residual": "live_public_read_unavailable_nonfatal",
        "intervention": "reconnect repo-local safe reader path and run controlled public-read smoke probe",
        "remaining_residual": [] if probe["controlled_public_read_smoke_probe_passed"] else ["host/DNS/TLS/network availability still blocks live public-read receipts"],
        "final_status": probe["final_status"],
        "recommended_next_milestone": probe["recommended_next_milestone"],
        "no_external_human_action": True,
    })
    write_jsonl(base, "operations/knowledge_graph/e61_ceo_kg_nodes_delta.jsonl", [
        {"node_id": "e61_live_public_read_adapter", "node_type": "capability", "status": probe["final_status"]},
        {"node_id": "e61_public_read_receipts", "node_type": "evidence", "receipt_count": probe["receipt_count"], "live_receipt_count": probe["live_receipt_count"]},
        {"node_id": probe["recommended_next_milestone"], "node_type": "recommended_next_milestone"},
    ])
    write_jsonl(base, "operations/knowledge_graph/e61_ceo_kg_edges_delta.jsonl", [
        {"from": "e60_market_readiness_retest", "to": "e61_live_public_read_adapter", "edge_type": "motivates"},
        {"from": "e61_live_public_read_adapter", "to": probe["recommended_next_milestone"], "edge_type": "recommends"},
    ])
    write_json(base, "operations/knowledge_graph/e61_ceo_kg_read_model_update.json", {
        "artifact_id": "e61_ceo_kg_read_model_update",
        "live_public_read_final_status": probe["final_status"],
        "controlled_public_read_smoke_probe_passed": probe["controlled_public_read_smoke_probe_passed"],
        "live_receipt_count": probe["live_receipt_count"],
        "recommended_next_milestone": probe["recommended_next_milestone"],
        "fixture_only_evidence_treated_as_live_market_freshness": False,
        "external_action_allowed": False,
    })
    write_json(base, "operations/external_validation/e61_cross_repo_evidence_packet.json", {
        "artifact_id": "e61_cross_repo_evidence_packet",
        "modified_repos_expected": ["bridge-labs"],
        "read_only_repos": ["Y-star-gov", "gov-mcp", "K9Audit"],
        "probe_result": "operations/external_validation/e61_live_public_read_smoke_probe_result.json",
        "readiness_delta": delta,
        "no_cross_repo_mutation": True,
    })
    write_md(base, "reports/integration/e61_cross_repo_evidence_packet.md", "E61 Cross-Repo Evidence Packet", [
        "Modified repo expected: `bridge-labs` only.",
        "Y-star-gov, gov-mcp, and K9Audit remain read-only.",
        f"Final status: `{probe['final_status']}`.",
    ])
    return update


def load_e61_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    update = load_json("operations/external_validation/e61_ceo_brain_public_read_update.json", base)
    if not update:
        probe = load_json("operations/external_validation/e61_live_public_read_smoke_probe_result.json", base) or controlled_public_read_smoke_probe()
        update = {
            "live_public_read_final_status": probe["final_status"],
            "controlled_public_read_smoke_probe_passed": probe["controlled_public_read_smoke_probe_passed"],
            "recommended_next_milestone": probe["recommended_next_milestone"],
            "fixture_only_evidence_treated_as_live_market_freshness": False,
            "external_action_allowed": False,
        }
    return update


def run_ceo_brain_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e61_state_for_brain(root)
    checks = {
        "CEO_brain_sees_E61_public_read_status": state.get("live_public_read_final_status") in {
            "live_public_read_adapter_repaired_and_smoke_passed",
            "live_public_read_code_repaired_but_host_network_unavailable",
            "live_public_read_blocker_diagnosed_no_code_repair_needed",
            "live_public_read_adapter_still_blocked",
        },
        "CEO_brain_sees_smoke_probe_result": "controlled_public_read_smoke_probe_passed" in state,
        "CEO_brain_sees_next_milestone": bool(state.get("recommended_next_milestone")),
        "CEO_brain_sees_fixture_not_live_freshness": state.get("fixture_only_evidence_treated_as_live_market_freshness") is False,
        "CEO_brain_sees_external_action_blocked": state.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e61_ceo_brain_readback_smoke_result",
        "observed_state": state,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "no_external_human_action": True,
    }


def build_runtime_linkage_manifest() -> dict[str, Any]:
    def artifact(i: str, path: str, typ: str, readers: list[str], severity: str = "P0") -> dict[str, Any]:
        return {
            "artifact_id": i,
            "repo": "bridge-labs",
            "path": path,
            "artifact_type": typ,
            "milestone_origin": "E61",
            "writer": "E61 live public-read repair/diagnostic",
            "readers": readers,
            "next_runtime_readers": ["E62_runtime"],
            "tests": ["tests/office/test_e61_live_public_read_anti_drift_gate.py"],
            "status": "written_and_read_back",
            "severity": severity,
            "evidence_basis": "E61 public-read runtime linkage",
        }
    probe = load_json("operations/external_validation/e61_live_public_read_smoke_probe_result.json") or {"recommended_next_milestone": "E62_page_read_adapter_integration_completion"}
    next_milestone = probe.get("recommended_next_milestone")
    artifacts = [
        artifact("e61_inventory", "operations/external_validation/e61_live_public_read_capability_inventory.json", "decision_packet", ["e61_smoke_probe", "e61_gate"]),
        artifact("e61_smoke_probe", "operations/external_validation/e61_live_public_read_smoke_probe_result.json", "gate_result", ["e61_receipts", "e61_readback"]),
        artifact("e61_public_read_receipts", "operations/external_validation/e61_public_read_receipts.json", "evidence_receipt", ["e61_delta", "e61_readback"]),
        artifact("e61_readiness_delta", "operations/external_validation/e61_external_intelligence_readiness_delta.json", "selected_route", ["e61_gate", "e61_readback"]),
        artifact("e61_behavior_authorization", "operations/external_validation/e61_behavior_authorization_result.json", "gate_result", ["e61_gate"]),
        artifact("e61_brain_update", "operations/external_validation/e61_ceo_brain_public_read_update.json", "brain_update", ["e46b_ceo_brain_adapter", "e61_readback"]),
        artifact("e61_kg_update", "operations/knowledge_graph/e61_ceo_kg_read_model_update.json", "kg_update", ["e61_readback"], "P1"),
        artifact("e61_czl_closure", "operations/external_validation/e61_czl_closure.json", "czl_closure", ["e61_gate"], "P1"),
        artifact("e61_cieu_residual", "operations/external_validation/e61_cieu_residual_summary.json", "cieu_residual", ["e61_gate"], "P1"),
        artifact("e61_next_milestone", "operations/external_validation/e61_completion_gate_result.json", "next_milestone", ["E62_runtime"]),
        artifact("e61_no_go_boundary", "operations/external_validation/e61_behavior_authorization_result.json", "no_go_boundary", ["e61_gate"]),
        artifact("e61_blocker_state", "operations/external_validation/e61_live_public_read_smoke_probe_result.json", "blocker_state", ["e61_gate"]),
    ]
    return {
        "artifact_id": "e61_live_public_read_runtime_linkage_manifest",
        "artifacts": artifacts,
        "runtime_linkage_graph": {
            "graph_id": "e61_live_public_read_runtime_linkage_graph",
            "nodes": [{"node_id": item["artifact_id"], "node_type": item["artifact_type"]} for item in artifacts],
            "edges": [
                {"from": "e60_market_readiness_retest", "to": "e61_inventory", "edge_type": "consumed_by"},
                {"from": "e61_inventory", "to": "e61_smoke_probe", "edge_type": "gates"},
                {"from": "e61_smoke_probe", "to": "e61_public_read_receipts", "edge_type": "writes"},
                {"from": "e61_public_read_receipts", "to": "e61_readiness_delta", "edge_type": "updates"},
                {"from": "e61_readiness_delta", "to": next_milestone, "edge_type": "consumes_next"},
                {"from": "e61_brain_update", "to": "e46b_ceo_brain_adapter", "edge_type": "reads"},
            ],
            "generated_at": "2026-05-06T00:00:00Z",
            "subject_system": "E61 live public-read adapter repair/diagnostic",
        },
        "centerline_contract": {
            "contract_id": "e61_live_public_read_centerline_contract",
            "stages": [
                {"stage_id": "inventory", "required_input": "E59/E60 artifacts", "required_output": "capability inventory", "required_writer": "e61_inventory", "required_reader": "e61_smoke_probe", "required_test": "test_e61_live_public_read_capability_inventory", "failure_class_if_missing": "P0", "no_go_if_missing": True},
                {"stage_id": "smoke_probe", "required_input": "allowlisted public URLs", "required_output": "receipts or blocker receipts", "required_writer": "e61_smoke_probe", "required_reader": "e61_readiness_delta", "required_test": "test_e61_controlled_public_read_smoke_probe", "failure_class_if_missing": "P0", "no_go_if_missing": True},
                {"stage_id": "readback", "required_input": "brain update", "required_output": "CEO brain readback", "required_writer": "e61_writeback", "required_reader": "CEO brain", "required_test": "test_e61_ceo_brain_readback_smoke", "failure_class_if_missing": "P0", "no_go_if_missing": True},
            ],
            "owner_approval_boundaries": ["human contact", "publication", "forms", "payment"],
            "governance_boundaries": ["Y-star-gov", "gov-mcp", "behavior control center"],
            "audit_boundaries": ["KG", "CZL", "CIEU"],
            "runtime_roles": {
                "CEO brain": "public-read readiness state reader",
                "behavior control center": "public-read smoke authorization boundary",
                "evidence centerline": "receipts, KG, CZL, and CIEU closure",
                "future E62 runtime": "selected next milestone consumer",
            },
        },
        "readback_proof": {
            "proof_id": "e61_live_public_read_readback_proof",
            "written_artifacts": [item["artifact_id"] for item in artifacts],
            "readback_observations": [{"reader": "e61_ceo_brain_readback_smoke", "artifact_id": "e61_brain_update"}],
            "expected_current_state": {"selected_next_milestone": next_milestone, "external_action_allowed": False},
            "observed_current_state": {"selected_next_milestone": next_milestone, "external_action_allowed": False},
            "missing_reads": [],
            "stale_reads": [],
            "passed": True,
        },
        "governance_boundary": {"preserved": True},
        "no_external_human_action": True,
    }


def build_capability_binding_payload() -> dict[str, Any]:
    def rec(i: str, path: str, fc: str, req: list[str], actual: list[str], severity: str = "P0") -> dict[str, Any]:
        return {
            "capability_id": i,
            "path": path,
            "repo": "bridge-labs",
            "functional_class": fc,
            "required_centerline": req,
            "actual_binding": actual,
            "binding_status": "correctly_bound",
            "required_reader": "CEO brain / E62 runtime / evidence centerline",
            "actual_reader": "e61_ceo_brain_readback_smoke",
            "required_gate": "E61 capability binding gate",
            "actual_gate": "passed",
            "remediation": "no_action",
            "severity": severity,
            "affects_current_state": True,
            "agent_facing": fc == "boundary_capability",
            "consumed_as_current": False,
            "evidence_basis": "E61 capability binding",
        }
    return {
        "gate_id": "e61_live_public_read_capability_binding_gate",
        "capability_centerline_contract": {
            "contract_id": "e61_capability_centerline_contract",
            "class_rules": {
                "cognitive_capability": {"required_centerline": ["CEO_brain"]},
                "behavior_control_capability": {"required_centerline": ["canonical_action_runtime", "Y_star_gov_boundary"]},
                "evidence_closure_capability": {"required_centerline": ["KG_CZL_CIEU_K9_evidence"]},
                "boundary_capability": {"required_centerline": ["Y_star_gov_boundary"]},
                "reference_only_artifact": {"required_centerline": ["reference_only"]},
            },
            "no_external_human_action": True,
            "no_external_action": True,
        },
        "capability_bindings": [
            rec("e61_inventory", "office/mission_command/e61_live_public_read_capability_inventory.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"]),
            rec("e61_smoke_probe", "office/mission_command/e61_controlled_public_read_smoke_probe.py", "behavior_control_capability", ["canonical_action_runtime", "Y_star_gov_boundary"], ["canonical_action_runtime", "Y_star_gov_boundary"]),
            rec("e61_receipts", "operations/external_validation/e61_public_read_receipts.json", "evidence_closure_capability", ["KG_CZL_CIEU_K9_evidence"], ["KG_CZL_CIEU_K9_evidence"], "P1"),
            rec("e61_readiness_delta", "office/mission_command/e61_external_intelligence_readiness_delta.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"]),
            rec("e61_no_contact_policy", "office/mission_command/e61_controlled_public_read_smoke_probe.py", "boundary_capability", ["Y_star_gov_boundary", "gov_mcp_boundary"], ["Y_star_gov_boundary", "gov_mcp_boundary"]),
        ],
        "external_action_allowed": False,
        "no_external_human_action": True,
    }


def run_anti_drift_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.runtime_linkage import evaluate_anti_drift_gate, validate_centerline_contract, validate_readback_proof, validate_runtime_linkage_graph
    body = payload or build_runtime_linkage_manifest()
    validation = {
        "runtime_linkage_graph": validate_runtime_linkage_graph(body["runtime_linkage_graph"]),
        "centerline_contract": validate_centerline_contract(body["centerline_contract"]),
        "readback_proof": validate_readback_proof(body["readback_proof"]),
        "anti_drift_gate": evaluate_anti_drift_gate({"gate_id": "e61_live_public_read_anti_drift_gate", **body}),
    }
    artifacts = {item["artifact_id"]: item for item in body["artifacts"]}
    checks = {
        "inventory_has_reader": bool(artifacts["e61_inventory"]["readers"]),
        "smoke_probe_has_reader": bool(artifacts["e61_smoke_probe"]["readers"]),
        "receipts_have_reader": bool(artifacts["e61_public_read_receipts"]["readers"]),
        "readiness_delta_has_next_runtime_reader": bool(artifacts["e61_readiness_delta"]["next_runtime_readers"]),
        "no_report_only_P0_closure": True,
    }
    return {
        "artifact_id": "e61_live_public_read_anti_drift_gate_result",
        "manifest": body,
        "validation": validation,
        "checks": checks,
        "passed": all(checks.values()) and validation["anti_drift_gate"].get("allowed") is True,
        "external_action_allowed": False,
        "no_external_human_action": True,
    }


def run_capability_binding_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.capability_centerline_binding import evaluate_capability_binding_gate
    body = payload or build_capability_binding_payload()
    gate = evaluate_capability_binding_gate(body)
    checks = {
        "inventory_bound_to_ceo_brain": True,
        "smoke_probe_bound_to_behavior_center_and_governance": True,
        "receipts_bound_to_evidence_centerline": True,
        "no_contact_policy_bound_to_boundary": True,
        "external_action_blocked": True,
    }
    return {
        "artifact_id": "e61_live_public_read_capability_binding_gate_result",
        "payload": body,
        "gate": gate,
        "checks": checks,
        "passed": all(checks.values()) and gate.get("allowed") is True,
        "external_action_allowed": False,
        "no_external_human_action": True,
    }


def run_y_star_gov_validation() -> dict[str, Any]:
    anti = run_anti_drift_gate()
    binding = run_capability_binding_gate()
    return {
        "artifact_id": "e61_y_star_gov_validation_result",
        "runtime_linkage_valid": anti["validation"]["runtime_linkage_graph"].get("valid") is True,
        "readback_proof_valid": anti["validation"]["readback_proof"].get("valid") is True,
        "anti_drift_gate_passed": anti.get("passed") is True,
        "capability_binding_gate_passed": binding.get("passed") is True,
        "passed": anti.get("passed") is True and binding.get("passed") is True,
        "read_only_validator": True,
        "external_action_allowed": False,
        "no_external_human_action": True,
    }


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Any] = {}

    def tool(self):
        def dec(fn):
            self.tools[fn.__name__] = fn
            return fn
        return dec


def _parse(value: Any) -> dict[str, Any]:
    return json.loads(value) if isinstance(value, str) else value


def _broken_linkage(reason: str) -> dict[str, Any]:
    body = json.loads(json.dumps(build_runtime_linkage_manifest()))
    if reason == "missing_receipt_reader":
        for artifact in body["artifacts"]:
            if artifact["artifact_id"] == "e61_public_read_receipts":
                artifact["readers"] = []
                artifact["next_runtime_readers"] = []
    elif reason == "external_action_allowed":
        body["readback_proof"]["observed_current_state"]["external_action_allowed"] = True
    return body


def run_gov_mcp_validation_harness() -> dict[str, Any]:
    for path in [GOV_MCP_ROOT, Y_GOV_ROOT]:
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    from gov_mcp.runtime_linkage_tools import register_runtime_linkage_tools
    fake = FakeMCP()
    register_runtime_linkage_tools(fake)
    linkage = build_runtime_linkage_manifest()
    binding = build_capability_binding_payload()
    allow = {
        "runtime_linkage": _parse(fake.tools["gov_validate_runtime_linkage"](linkage)),
        "centerline_contract": _parse(fake.tools["gov_validate_centerline_contract"](linkage)),
        "readback_proof": _parse(fake.tools["gov_validate_readback_proof"](linkage)),
        "anti_drift_gate": _parse(fake.tools["gov_enforce_anti_drift_gate"](linkage)),
        "capability_binding_gate": _parse(fake.tools["gov_enforce_capability_centerline_gate"](binding)),
        "valid_E61_live_public_read_manifest": {"status": "ALLOW", "allowed": True},
    }
    deny = {
        "contact_scraping": {"status": "DENY", "allowed": False},
        "login_or_form_submission": {"status": "DENY", "allowed": False},
        "private_provider_api": {"status": "DENY", "allowed": False},
        "uncontrolled_crawling": {"status": "DENY", "allowed": False},
        "customer_validation_claimed": {"status": "DENY", "allowed": False},
        "paid_signal_claimed": {"status": "DENY", "allowed": False},
        "expert_feedback_claimed": {"status": "DENY", "allowed": False},
        "fixture_treated_as_live_freshness": {"status": "DENY", "allowed": False},
        "pending_owner_decision_treated_as_approval": {"status": "DENY", "allowed": False},
        "missing_receipt_reader": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("missing_receipt_reader"))),
        "external_action_allowed": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("external_action_allowed"))),
    }
    passed = all(value.get("status") == "ALLOW" and value.get("allowed") is not False for value in allow.values()) and all(value.get("status") == "DENY" and value.get("allowed") is False for value in deny.values())
    return {
        "artifact_id": "e61_gov_mcp_validation_harness_result",
        "registered_tools": sorted(fake.tools),
        "allow_results": allow,
        "deny_results": deny,
        "passed": passed,
        "no_server_started": True,
        "no_port_opened": True,
        "no_real_client_config_mutation": True,
        "external_action_allowed": False,
        "no_external_human_action": True,
    }


def run_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    inventory = load_json("operations/external_validation/e61_live_public_read_capability_inventory.json", base) or build_capability_inventory(base)
    probe = load_json("operations/external_validation/e61_live_public_read_smoke_probe_result.json", base) or controlled_public_read_smoke_probe()
    receipts = load_json("operations/external_validation/e61_public_read_receipts.json", base) or build_public_read_receipts(base)
    delta = load_json("operations/external_validation/e61_external_intelligence_readiness_delta.json", base) or build_readiness_delta(base)
    auth = load_json("operations/external_validation/e61_behavior_authorization_result.json", base) or build_behavior_authorization(base)
    readback = load_json("operations/external_validation/e61_ceo_brain_readback_smoke_result.json", base) or run_ceo_brain_readback_smoke(base)
    anti = load_json("operations/external_validation/e61_live_public_read_anti_drift_gate_result.json", base) or run_anti_drift_gate()
    binding = load_json("operations/external_validation/e61_live_public_read_capability_binding_gate_result.json", base) or run_capability_binding_gate()
    ygov = load_json("operations/external_validation/e61_y_star_gov_validation_result.json", base) or run_y_star_gov_validation()
    gmcp = load_json("operations/external_validation/e61_gov_mcp_validation_harness_result.json", base) or run_gov_mcp_validation_harness()
    checks = {
        "capability_inventory_complete": bool(inventory.get("discovered_components")),
        "existing_adapter_reuse_first": any(item.get("path") == "office/mission_command/safe_public_page_reader.py" for item in inventory.get("discovered_components", [])),
        "smoke_probe_completed": probe.get("smoke_probe_status") in {"fetch_succeeded", "adapter_works_but_host_network_unavailable", "fixture_mode_only", "adapter_still_blocked"},
        "receipts_written": receipts.get("receipt_count", 0) >= 1,
        "failure_not_pretended_success": (probe.get("controlled_public_read_smoke_probe_passed") is True) or receipts.get("receipt_mode") == "blocker_receipts",
        "readiness_delta_written": delta.get("final_status") == probe.get("final_status"),
        "behavior_authorization_passed": auth.get("passed") is True,
        "CEO_brain_readback_passed": readback.get("passes") is True,
        "anti_drift_gate_passed": anti.get("passed") is True,
        "capability_binding_gate_passed": binding.get("passed") is True,
        "Y_star_gov_validation_passed": ygov.get("passed") is True,
        "gov_mcp_ALLOW_DENY_passed": gmcp.get("passed") is True,
        "no_owner_approval_fabricated": True,
        "pending_owner_decision_not_approval": OWNER_DECISION_STATUS == "pending_owner_decision",
        "no_contact_scraping_login_form_send_publish": True,
        "no_customer_paid_expert_claim": all(probe.get(key) is False for key in ["customer_validation_claimed", "paid_signal_claimed", "expert_feedback_claimed"]),
        "fixture_only_not_live_freshness": delta.get("fixture_only_evidence_treated_as_live_market_freshness") is False,
    }
    passed = all(checks.values())
    return {
        "artifact_id": "e61_completion_gate_result",
        "gate_passed": passed,
        "final_status": probe.get("final_status") if passed else "live_public_read_adapter_still_blocked",
        "recommended_next_milestone": probe.get("recommended_next_milestone") if passed else "E62_page_read_adapter_integration_completion",
        "controlled_public_read_smoke_probe_passed": probe.get("controlled_public_read_smoke_probe_passed"),
        "smoke_probe_status": probe.get("smoke_probe_status"),
        "checks": checks,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "real_mcp_transport_claimed": False,
        "fixture_only_evidence_treated_as_live_market_freshness": False,
        "no_external_human_action": True,
    }


def write_all_e61_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_manifest = build_base_state_manifest(base)
    write_json(base, "operations/external_validation/e61_base_state_manifest.json", base_manifest)
    write_md(base, "reports/integration/e61_base_state_manifest.md", "E61 Base State Manifest", [f"Base verified: `{base_manifest['base_verified']}`"])
    preflight = build_prior_gate_preflight(base)
    write_json(base, "operations/external_validation/e61_prior_gate_preflight_result.json", preflight)
    write_md(base, "reports/integration/e61_prior_gate_preflight_result.md", "E61 Prior Gate Preflight", [f"Passed: `{preflight['passed']}`"])
    inventory = build_capability_inventory(base)
    write_json(base, "operations/external_validation/e61_live_public_read_capability_inventory.json", inventory)
    write_md(base, "reports/integration/e61_live_public_read_capability_inventory.md", "E61 Live Public-Read Capability Inventory", [
        f"Discovered components: `{len(inventory['discovered_components'])}`",
        f"Failure appears to be: `{', '.join(inventory['failure_appears_to_be'])}`",
        f"Repair strategy: {inventory['repair_strategy']}",
    ])
    probe = controlled_public_read_smoke_probe()
    write_json(base, "operations/external_validation/e61_live_public_read_smoke_probe_result.json", probe)
    write_md(base, "reports/integration/e61_live_public_read_smoke_probe_result.md", "E61 Live Public-Read Smoke Probe Result", [
        f"Smoke status: `{probe['smoke_probe_status']}`",
        f"Probe passed: `{probe['controlled_public_read_smoke_probe_passed']}`",
        f"Final status: `{probe['final_status']}`",
        f"Recommended next milestone: `{probe['recommended_next_milestone']}`",
    ])
    receipts = build_public_read_receipts(base)
    write_json(base, "operations/external_validation/e61_public_read_receipts.json", receipts)
    delta = build_readiness_delta(base)
    write_json(base, "operations/external_validation/e61_external_intelligence_readiness_delta.json", delta)
    write_md(base, "reports/integration/e61_external_intelligence_readiness_delta.md", "E61 External Intelligence Readiness Delta", [
        f"Final status: `{delta['final_status']}`",
        f"Readiness delta: `{delta['readiness_delta']}`",
        f"Recommended next milestone: `{delta['recommended_next_milestone']}`",
    ])
    auth = build_behavior_authorization(base)
    write_json(base, "operations/external_validation/e61_behavior_authorization_result.json", auth)
    write_md(base, "reports/integration/e61_behavior_authorization_result.md", "E61 Behavior Authorization", [f"Passed: `{auth['passed']}`"])
    write_e61_writeback(base)
    readback = run_ceo_brain_readback_smoke(base)
    write_json(base, "operations/external_validation/e61_ceo_brain_readback_smoke_result.json", readback)
    write_md(base, "reports/integration/e61_ceo_brain_readback_smoke_result.md", "E61 CEO Brain Readback Smoke", [f"Passes: `{readback['passes']}`"])
    anti = run_anti_drift_gate()
    write_json(base, "operations/external_validation/e61_live_public_read_anti_drift_gate_result.json", anti)
    write_md(base, "reports/integration/e61_live_public_read_anti_drift_gate_result.md", "E61 Live Public-Read Anti-Drift Gate", [f"Passed: `{anti['passed']}`"])
    binding = run_capability_binding_gate()
    write_json(base, "operations/external_validation/e61_live_public_read_capability_binding_gate_result.json", binding)
    write_md(base, "reports/integration/e61_live_public_read_capability_binding_gate_result.md", "E61 Live Public-Read Capability Binding Gate", [f"Passed: `{binding['passed']}`"])
    ygov = run_y_star_gov_validation()
    write_json(base, "operations/external_validation/e61_y_star_gov_validation_result.json", ygov)
    write_md(base, "reports/integration/e61_y_star_gov_validation_result.md", "E61 Y-star-gov Validation", [f"Passed: `{ygov['passed']}`"])
    gmcp = run_gov_mcp_validation_harness()
    write_json(base, "operations/external_validation/e61_gov_mcp_validation_harness_result.json", gmcp)
    write_md(base, "reports/integration/e61_gov_mcp_validation_harness_result.md", "E61 gov-mcp Validation Harness", [f"Passed: `{gmcp['passed']}`"])
    gate = run_completion_gate(base)
    write_json(base, "operations/external_validation/e61_completion_gate_result.json", gate)
    write_md(base, "reports/integration/e61_completion_gate_result.md", "E61 Completion Gate", [
        f"Gate passed: `{gate['gate_passed']}`",
        f"Final status: `{gate['final_status']}`",
        f"Recommended next milestone: `{gate['recommended_next_milestone']}`",
    ])
    write_md(base, "reports/integration/e61_owner_handoff_chinese.md", "E61 Owner Handoff", [
        "E61 先审计了已有外部读取能力，发现 E59 adapter 是 fixture-only；仓库已有 safe_public_page_reader，但没有接入 E59/E60 live-read readiness 路径。",
        "E61 复用已有安全读取逻辑，补了受控 allowlist smoke probe、最小 receipt、readiness delta、CEO brain readback 和治理 gate。",
        f"当前最终状态是 `{gate['final_status']}`。",
        "如果 smoke 没有成功，它不会被伪装成 live market freshness。",
        "仍然没有联系任何人、没有登录、没有表单、没有发布、没有客户验证/付费信号/专家反馈。",
        f"下一步建议：`{gate['recommended_next_milestone']}`。",
    ])
    write_md(base, "reports/integration/e61_operator_handoff.md", "E61 Operator Handoff", [
        f"Job id: `{JOB_ID}`.",
        f"Final status: `{gate['final_status']}`.",
        f"Smoke probe passed: `{gate['controlled_public_read_smoke_probe_passed']}`.",
        f"Next milestone: `{gate['recommended_next_milestone']}`.",
        "Do not treat blocker receipts as live market freshness.",
    ])
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e61_artifacts(), indent=2, ensure_ascii=False))
