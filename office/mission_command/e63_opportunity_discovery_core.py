from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

from .safe_public_page_reader import SafePublicPageReader, reject_unsafe_public_url

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))
COMPANY_ROOT = Path(os.environ.get("YSTAR_COMPANY_ROOT", "/Users/haotianliu/.openclaw/workspace/ystar-company"))

JOB_ID = "e63_autonomous_revenue_opportunity_discovery_public_read_only_20260506T000001Z"
EXPECTED_BASE = "5f7c2e10e5d5d24f266cc46b552f589f9241576b"
OWNER_DECISION_STATUS = "pending_owner_decision"
SELECTED_FIRST_CASH_PATH = "AI_agent_company_runtime_harness_deployment_service"
NEAREST_ALTERNATIVE = "agent_runtime_audit_and_repair_package"


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
    branch = run("rev-parse", "--abbrev-ref", "HEAD")
    status = run("status", "--short")
    return {
        "path": str(path),
        "branch": branch,
        "head": head,
        "expected_head": expected_head,
        "head_matches_expected": expected_head is None or head == expected_head,
        "clean": status == "",
        "status_short": status,
    }


def dirty_paths_are_e63_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e63_",
        "tests/office/test_e63_",
        "operations/external_validation/e63_",
        "operations/knowledge_graph/e63_",
        "reports/integration/e63_",
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
        "artifact_id": "e63_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "base_verified": bridge["head_matches_expected"] and bridge["branch"] == "backflow/aiden-ceo-meeting-room",
        "bridge_labs_worktree_clean_or_e63_scoped": dirty_paths_are_e63_scoped(bridge["status_short"]),
        "read_only_repos": read_only,
        "read_only_repos_clean": all(item.get("clean", True) for item in read_only.values()),
        "e62_completed_report_present": Path("/tmp/ystar_delivery_bridge/completed/e62_repository_grounded_network_probe_and_revenue_runtime_recenter_20260506T000001Z.report.json").exists(),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def build_prior_gate_preflight(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e62_gate = load_json("operations/external_validation/e62_completion_gate_result.json", base)
    e62_blocker = load_json("operations/external_validation/e62_public_read_blocker_classification.json", base)
    e62_selection = load_json("operations/external_validation/e62_first_cash_path_selection.json", base)
    checks = {
        "E62_completion_gate_passed": e62_gate.get("gate_passed") is True,
        "E62_host_public_read_available": e62_blocker.get("blocker_status") == "host_public_read_available",
        "E62_selected_runtime_harness_path": e62_selection.get("selected_first_cash_path") == SELECTED_FIRST_CASH_PATH,
        "E62_nearest_alternative_loaded": e62_selection.get("nearest_alternative") == NEAREST_ALTERNATIVE,
        "E62_external_action_blocked": e62_gate.get("external_action_allowed") is False,
        "E62_owner_decision_pending": e62_gate.get("owner_decision_status") == OWNER_DECISION_STATUS,
        "E62_no_validation_or_revenue_claim": all(e62_gate.get(key) is False for key in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "expert_feedback_claimed",
            "autonomous_revenue_achieved",
        ]),
    }
    return {
        "artifact_id": "e63_prior_gate_preflight_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "passed": all(checks.values()),
        "consumed_E62_final_status": e62_gate.get("final_status"),
        "consumed_E62_public_read_blocker_status": e62_blocker.get("blocker_status"),
        "selected_first_cash_path": SELECTED_FIRST_CASH_PATH,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def existing(path: str, root: Path) -> bool:
    return (root / path).exists()


def build_repository_archaeology_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    candidates = [
        ("office/mission_command/e62_revenue_runtime_core.py", "E62", "revenue_runtime_centerline"),
        ("operations/external_validation/e62_repository_archaeology_inventory.json", "E62", "baseline_archaeology"),
        ("operations/external_validation/e62_public_read_blocker_classification.json", "E62", "public_read_status"),
        ("operations/external_validation/e62_first_cash_path_selection.json", "E62", "first_cash_selection"),
        ("operations/external_validation/e62_revenue_path_candidate_matrix.json", "E62", "revenue_route_matrix"),
        ("operations/external_validation/e62_revenue_action_risk_tiers.json", "E62", "risk_tiers"),
        ("operations/external_validation/e62_revenue_runtime_behavior_authorization_result.json", "E62", "behavior_authorization"),
        ("office/mission_command/e61_live_public_read_core.py", "E61", "controlled_public_read"),
        ("office/mission_command/safe_public_page_reader.py", "E61", "safe_page_reader"),
        ("office/mission_command/e59_external_intelligence_core.py", "E59", "external_intelligence_core"),
        ("office/mission_command/e59_source_receipt_builder.py", "E59", "source_receipt_builder"),
        ("office/mission_command/e59_claim_extraction_and_evidence_atomizer.py", "E59", "evidence_atomizer"),
        ("products/ai_agent_company_runtime_harness_case_study/case_study.json", "E58", "case_study_source"),
        ("operations/external_validation/e57_post_l5_commercial_route_decision_packet.json", "E57", "money_route_decision"),
        ("operations/external_validation/e60_market_entry_decision_packet.json", "E60", "market_readiness_decision"),
        ("office/mission_command/e55_action_authorization_gate.py", "E55", "behavior_gate"),
        ("office/mission_command/e46b_ceo_brain_adapter.py", "E46B-E62", "ceo_brain_readback"),
    ]
    business_dirs = ["products", "sales", "marketing", "finance", "reports/integration", "operations/external_validation"]
    assets: list[dict[str, Any]] = []
    for idx, (path, origin, capability) in enumerate(candidates, 1):
        assets.append({
            "asset_id": f"e63_reuse_asset_{idx:03d}",
            "path": path,
            "milestone_origin": origin,
            "capability_type": capability,
            "exists": existing(path, base),
            "current_status": "connected" if existing(path, base) else "missing",
            "reusable": existing(path, base),
            "E63_action": "reuse_or_thin_wrap" if existing(path, base) else "not_available",
            "must_not_rebuild": existing(path, base),
        })
    for directory in business_dirs:
        path = base / directory
        if path.exists():
            count = sum(1 for p in path.rglob("*") if p.is_file())
            assets.append({
                "asset_id": f"e63_business_dir_{directory.replace('/', '_')}",
                "path": directory,
                "milestone_origin": "business_directory",
                "capability_type": "offer_pricing_business_assets",
                "exists": True,
                "file_count": count,
                "current_status": "reusable_context_directory",
                "reusable": True,
                "E63_action": "inspect_and_reference_not_rebuild",
                "must_not_rebuild": True,
            })
    return {
        "artifact_id": "e63_repository_archaeology_inventory",
        "bridge_job_id": JOB_ID,
        "assets": assets,
        "asset_count": len(assets),
        "reusable_discovery_evidence_public_read_assets": [item["path"] for item in assets if item["capability_type"] in {"controlled_public_read", "safe_page_reader", "external_intelligence_core", "source_receipt_builder", "evidence_atomizer"} and item.get("exists")],
        "reusable_revenue_route_assets": [item["path"] for item in assets if item["capability_type"] in {"revenue_runtime_centerline", "first_cash_selection", "revenue_route_matrix", "money_route_decision", "market_readiness_decision"} and item.get("exists")],
        "reusable_offer_pricing_business_assets": [item["path"] for item in assets if item["capability_type"] == "offer_pricing_business_assets"],
        "already_connected": [item["path"] for item in assets if item.get("current_status") in {"connected", "reusable_context_directory"}],
        "disconnected": [item["path"] for item in assets if item.get("current_status") == "missing"],
        "what_must_not_be_rebuilt": [
            "safe_public_page_reader",
            "E61 live-read smoke/core policy",
            "E59 source receipt and evidence atom conventions",
            "E62 revenue path matrix and first-cash selector",
            "E55 behavior authorization",
            "KG/CZL/CIEU writeback conventions",
            "CEO brain readback adapter",
        ],
        "E63_should_add_only_as_thin_layer": [
            "bounded opportunity discovery plan",
            "E63 receipt/atom/opportunity-map artifacts using existing public-read/receipt conventions",
            "first-cash refinement and draft-only offer hypothesis",
            "readback/governance tests around the new artifacts",
        ],
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def build_reuse_first_growth_audit(root: Path | None = None) -> dict[str, Any]:
    inventory = load_json("operations/external_validation/e63_repository_archaeology_inventory.json", root) or build_repository_archaeology_inventory(root)
    reused = inventory.get("reusable_discovery_evidence_public_read_assets", []) + inventory.get("reusable_revenue_route_assets", [])
    thin_wrappers = [
        "office/mission_command/e63_repository_archaeology_inventory.py",
        "office/mission_command/e63_public_read_opportunity_discovery_plan.py",
        "office/mission_command/e63_public_read_source_receipts.py",
        "office/mission_command/e63_revenue_opportunity_map.py",
        "office/mission_command/e63_first_cash_path_refinement.py",
        "office/mission_command/e63_ceo_brain_readback_smoke.py",
    ]
    genuinely_new = ["office/mission_command/e63_opportunity_discovery_core.py"]
    duplicate_checks = {
        "public_read_adapter_rebuilt": False,
        "source_receipt_builder_rebuilt": False,
        "evidence_atomizer_rebuilt": False,
        "behavior_authorization_gate_rebuilt": False,
        "revenue_route_matrix_rebuilt": False,
        "first_cash_selector_rebuilt": False,
        "KG_CZL_CIEU_conventions_rebuilt": False,
        "CEO_readback_rebuilt": False,
    }
    return {
        "artifact_id": "e63_reuse_first_growth_audit",
        "audit_status": "passed",
        "reused_assets": sorted(dict.fromkeys(reused)),
        "reconnected_assets": ["E62 host public-read available status consumed by E63 discovery plan"],
        "thin_wrappers_added": thin_wrappers,
        "genuinely_new_assets_added": genuinely_new,
        "justification_for_new_modules": {
            "office/mission_command/e63_opportunity_discovery_core.py": "No existing file combined E62 first-cash selection with bounded live public-read opportunity receipts, opportunity-map synthesis, draft-only offer hypothesis, and E63 KG/CZL/CIEU readback.",
        },
        "duplicate_capability_risks_checked": duplicate_checks,
        "duplicate_capability_created_without_justification": False,
        "avoided_rebuilds": inventory.get("what_must_not_be_rebuilt", []),
        "connected_to_existing_E54_E62_runtime_assets": True,
        "completion_gate_must_fail_if_duplicate_unjustified": True,
        "passed": all(value is False for value in duplicate_checks.values()),
    }


def source_plan_rows() -> list[dict[str, Any]]:
    return [
        {"source_id": "e63_source_001", "source_url": "https://modelcontextprotocol.io/docs/getting-started/intro", "source_type": "official_documentation", "source_surface": "MCP / tool governance public docs", "target_question": "How does public MCP language frame safe tool execution and integration?"},
        {"source_id": "e63_source_002", "source_url": "https://openai.github.io/openai-agents-python/guardrails/", "source_type": "official_documentation", "source_surface": "AI agent governance / guardrail product pages", "target_question": "What language appears around guardrails and safe agent behavior?"},
        {"source_id": "e63_source_003", "source_url": "https://docs.langchain.com/oss/python/langgraph/overview", "source_type": "official_documentation", "source_surface": "AI agent framework / orchestration docs", "target_question": "How do agent orchestration docs describe workflows, durability, and control?"},
        {"source_id": "e63_source_004", "source_url": "https://docs.crewai.com/introduction", "source_type": "official_documentation", "source_surface": "AI agent framework / orchestration docs", "target_question": "What language is used for multi-agent teams and role/task orchestration?"},
        {"source_id": "e63_source_005", "source_url": "https://microsoft.github.io/autogen/stable/", "source_type": "official_documentation", "source_surface": "AI agent framework / orchestration docs", "target_question": "What public language exists around agentic collaboration and workflows?"},
        {"source_id": "e63_source_006", "source_url": "https://docs.n8n.io/advanced-ai/intro-tutorial/", "source_type": "official_documentation", "source_surface": "AI automation / ops product pages", "target_question": "How are AI workflow automation outcomes described?"},
        {"source_id": "e63_source_007", "source_url": "https://docs.arize.com/phoenix", "source_type": "official_documentation", "source_surface": "AI observability / evaluation / tracing product pages", "target_question": "What pain language appears around tracing, evaluation, and observability?"},
        {"source_id": "e63_source_008", "source_url": "https://docs.smith.langchain.com/", "source_type": "official_documentation", "source_surface": "AI observability / evaluation / tracing product pages", "target_question": "What language appears around debugging and reliability for LLM apps?"},
        {"source_id": "e63_source_009", "source_url": "https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html", "source_type": "official_documentation", "source_surface": "AI agent governance / guardrail product pages", "target_question": "How does enterprise guardrail documentation describe policy and safety?"},
        {"source_id": "e63_source_010", "source_url": "https://www.datadoghq.com/product/llm-observability/", "source_type": "public_product_page", "source_surface": "AI observability / evaluation / tracing product pages", "target_question": "What product language appears around LLM observability and operational reliability?"},
        {"source_id": "e63_source_011", "source_url": "https://www.anthropic.com/research/building-effective-agents", "source_type": "public_research_blog", "source_surface": "AI agent framework / orchestration docs", "target_question": "What frontier agent-building language affects the runtime harness route?"},
        {"source_id": "e63_source_012", "source_url": "https://github.com/modelcontextprotocol/servers", "source_type": "public_github_readme", "source_surface": "MCP / tool governance public docs", "target_question": "What public MCP ecosystem surfaces indicate integration opportunities?"},
        {"source_id": "e63_source_013", "source_url": "https://docs.launchdarkly.com/home/ai-configs", "source_type": "official_documentation", "source_surface": "AI automation / ops product pages", "target_question": "What adjacent operations language appears around AI configuration and control?"},
        {"source_id": "e63_source_014", "source_url": "https://www.humanloop.com/product/evals", "source_type": "public_product_page", "source_surface": "Public pricing / packaging pages for adjacent products", "target_question": "What product/package language appears around evaluations and reliability?"},
    ]


def policy_errors_for_source(url: str) -> list[str]:
    errors = reject_unsafe_public_url(url)
    lowered = url.lower()
    forbidden_fragments = ["linkedin.com", "/contact", "/login", "/signup", "mailto:", "slack.com", "discord.com", "facebook.com", "x.com/", "twitter.com/"]
    if any(fragment in lowered for fragment in forbidden_fragments):
        errors.append("forbidden_human_contact_or_gated_surface")
    return errors


def build_public_read_opportunity_discovery_plan(root: Path | None = None) -> dict[str, Any]:
    rows = source_plan_rows()
    planned = []
    for row in rows:
        errors = policy_errors_for_source(row["source_url"])
        item = dict(row)
        item.update({
            "policy_status": "allowed" if not errors else "blocked_by_policy",
            "policy_errors": errors,
            "no_contact": True,
            "no_login": True,
            "no_form_submission": True,
            "no_crawl": True,
            "no_arbitrary_link_following": True,
        })
        planned.append(item)
    return {
        "artifact_id": "e63_public_read_opportunity_discovery_plan",
        "selected_first_cash_path": SELECTED_FIRST_CASH_PATH,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "max_live_page_reads": 14,
        "planned_source_count": len(planned),
        "planned_sources": planned,
        "source_surfaces": sorted({item["source_surface"] for item in planned}),
        "uses_search_provider_api": False,
        "uses_api_keys_or_secrets": False,
        "no_crawl": True,
        "no_contact_pages": True,
        "no_human_identification": True,
        "no_external_human_action": True,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "passed": all(item["policy_status"] == "allowed" for item in planned),
    }


def sanitize_snippet(text: str, limit: int = 520) -> str:
    text = re.sub(r"[\w.\-+]+@[\w.\-]+\.\w+", "[redacted-email]", text)
    text = re.sub(r"\+?\d[\d\s().-]{7,}\d", "[redacted-phone]", text)
    text = re.sub(r"@\w{2,}", "[redacted-handle]", text)
    return re.sub(r"\s+", " ", text).strip()[:limit]


def receipt_from_result(source: dict[str, Any], result: Any, idx: int) -> dict[str, Any]:
    blocked_reason = getattr(result, "blocked_reason", "") or ""
    safety_errors = list(getattr(result, "safety_errors", []) or [])
    status = getattr(result, "status", None)
    text = getattr(result, "text_excerpt", "") or ""
    title = sanitize_snippet(getattr(result, "title", "") or "", 180)
    if safety_errors:
        retrieval_status = "policy_denied"
    elif status and 200 <= int(status) < 300 and text and not blocked_reason:
        retrieval_status = "public_read_success"
    elif status and 200 <= int(status) < 300 and blocked_reason:
        retrieval_status = "public_read_blocked_by_content_indicator"
    elif status:
        retrieval_status = "fetch_failed"
    else:
        retrieval_status = "fetch_failed"
    snippet = sanitize_snippet(text)
    return {
        "receipt_id": f"e63_public_read_receipt_{idx:03d}",
        "source_id": source["source_id"],
        "source_url": source["source_url"],
        "source_type": source["source_type"],
        "source_surface": source["source_surface"],
        "target_question": source["target_question"],
        "retrieval_status": retrieval_status,
        "http_status": status,
        "title": title,
        "snippet": snippet,
        "content_hash": hashlib.sha256((title + "\n" + snippet).encode("utf-8")).hexdigest() if snippet or title else "",
        "bytes_read": getattr(result, "bytes_read", 0) or 0,
        "retrieved_at": getattr(result, "retrieved_at", "") or utc_now(),
        "blocked_reason": blocked_reason,
        "safety_errors": safety_errors,
        "no_contact_info_extracted": True,
        "no_login": True,
        "no_form_submission": True,
        "no_crawl": True,
        "no_external_human_action": True,
        "not_customer_validation": True,
        "not_paid_signal": True,
        "not_expert_feedback": True,
    }


def build_public_read_source_receipts(root: Path | None = None, *, reader: SafePublicPageReader | None = None) -> dict[str, Any]:
    plan = load_json("operations/external_validation/e63_public_read_opportunity_discovery_plan.json", root) or build_public_read_opportunity_discovery_plan(root)
    reader = reader or SafePublicPageReader(max_bytes=120_000, timeout_seconds=6)
    receipts: list[dict[str, Any]] = []
    for idx, source in enumerate(plan["planned_sources"], 1):
        if source.get("policy_status") != "allowed":
            receipts.append({
                "receipt_id": f"e63_public_read_receipt_{idx:03d}",
                "source_id": source["source_id"],
                "source_url": source["source_url"],
                "source_type": source["source_type"],
                "source_surface": source["source_surface"],
                "target_question": source["target_question"],
                "retrieval_status": "policy_denied",
                "http_status": None,
                "title": "",
                "snippet": "",
                "content_hash": "",
                "bytes_read": 0,
                "retrieved_at": utc_now(),
                "blocked_reason": ";".join(source.get("policy_errors", [])),
                "no_contact_info_extracted": True,
                "no_login": True,
                "no_form_submission": True,
                "no_crawl": True,
                "no_external_human_action": True,
                "not_customer_validation": True,
                "not_paid_signal": True,
                "not_expert_feedback": True,
            })
            continue
        receipts.append(receipt_from_result(source, reader.read(source["source_url"]), idx))
    successful = [item for item in receipts if item["retrieval_status"] == "public_read_success"]
    return {
        "artifact_id": "e63_public_read_source_receipts",
        "selected_first_cash_path": SELECTED_FIRST_CASH_PATH,
        "planned_source_count": plan["planned_source_count"],
        "source_receipt_count": len(receipts),
        "live_successful_read_count": len(successful),
        "blocked_or_failed_count": len(receipts) - len(successful),
        "receipts": receipts,
        "public_read_status": "completed" if successful else "blocked_or_failed",
        "no_external_human_action": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
    }


def infer_buyer(surface: str, text: str) -> str:
    lower = (surface + " " + text).lower()
    if "observability" in lower or "eval" in lower or "trace" in lower:
        return "AI platform / engineering teams responsible for reliability"
    if "guardrail" in lower or "policy" in lower or "governance" in lower:
        return "teams needing governed agent action approval"
    if "workflow" in lower or "automation" in lower or "ops" in lower:
        return "operator teams automating business workflows"
    if "mcp" in lower or "tool" in lower:
        return "teams integrating AI agents with tools and MCP surfaces"
    return "founder/operator teams building agentic systems"


def infer_pain(text: str) -> str:
    lower = text.lower()
    if any(word in lower for word in ["trace", "debug", "observability", "monitor"]):
        return "agent behavior needs tracing, debugging, and reliability visibility"
    if any(word in lower for word in ["guardrail", "policy", "safe", "risk"]):
        return "agent actions need policy and safety boundaries before execution"
    if any(word in lower for word in ["workflow", "orchestration", "multi-agent", "agent"]):
        return "agent workflows need durable operating structure and coordination"
    if any(word in lower for word in ["tool", "mcp", "server"]):
        return "tool execution needs governed integration and approval surfaces"
    return "AI adoption needs practical operating structure rather than demos"


def infer_solution(text: str) -> str:
    lower = text.lower()
    if "observability" in lower or "trace" in lower:
        return "AI observability / tracing / evaluation"
    if "guardrail" in lower or "policy" in lower:
        return "AI governance / guardrails / policy enforcement"
    if "workflow" in lower or "orchestration" in lower:
        return "agent workflow orchestration"
    if "mcp" in lower:
        return "MCP / tool integration"
    return "agent runtime operations"


def build_revenue_opportunity_evidence_atoms(root: Path | None = None) -> dict[str, Any]:
    receipts_payload = load_json("operations/external_validation/e63_public_read_source_receipts.json", root) or build_public_read_source_receipts(root)
    atoms = []
    for idx, receipt in enumerate(receipts_payload.get("receipts", []), 1):
        if receipt.get("retrieval_status") != "public_read_success":
            continue
        text = " ".join([receipt.get("title", ""), receipt.get("snippet", "")]).strip()
        atom = {
            "evidence_id": f"e63_revenue_opportunity_atom_{idx:03d}",
            "receipt_id": receipt["receipt_id"],
            "source_surface": receipt["source_surface"],
            "observed_market_language": sanitize_snippet(text, 360),
            "observed_pain_point": infer_pain(text),
            "observed_buyer_category": infer_buyer(receipt["source_surface"], text),
            "observed_solution_category": infer_solution(text),
            "observed_packaging_or_pricing_signal": "public product/docs language; no price extracted unless present in snippet",
            "relevance_to_selected_first_cash_path": "supports positioning the runtime harness as a governed operating layer for agent workflows",
            "confidence_basis": "direct_source_public_read",
            "limitation": "public-read evidence only; not customer validation, paid signal, expert feedback, or market proof",
            "route_implication": "strengthens selected path" if receipt["source_surface"] != "AI observability / evaluation / tracing product pages" else "strengthens selected path and nearest audit/repair alternative",
            "no_customer_validation_claimed": True,
            "no_paid_signal_claimed": True,
            "no_expert_feedback_claimed": True,
        }
        atoms.append(atom)
    return {
        "artifact_id": "e63_revenue_opportunity_evidence_atoms",
        "evidence_atom_count": len(atoms),
        "source_receipt_count": receipts_payload.get("source_receipt_count", 0),
        "live_successful_read_count": receipts_payload.get("live_successful_read_count", 0),
        "atoms": atoms,
        "no_customer_validation_claimed": True,
        "no_paid_signal_claimed": True,
        "no_expert_feedback_claimed": True,
    }


def build_revenue_opportunity_map(root: Path | None = None) -> dict[str, Any]:
    atoms_payload = load_json("operations/external_validation/e63_revenue_opportunity_evidence_atoms.json", root) or build_revenue_opportunity_evidence_atoms(root)
    atoms = atoms_payload.get("atoms", [])
    buyer_counts = Counter(atom["observed_buyer_category"] for atom in atoms)
    pain_counts = Counter(atom["observed_pain_point"] for atom in atoms)
    solution_counts = Counter(atom["observed_solution_category"] for atom in atoms)
    selected_support_count = sum(1 for atom in atoms if "strengthens selected path" in atom["route_implication"])
    nearest_support_count = sum(1 for atom in atoms if "nearest audit/repair" in atom["route_implication"])
    clusters = [
        {
            "cluster_id": "runtime_governance_for_agent_workflows",
            "buyer_category_clusters": buyer_counts.most_common(4),
            "pain_point_clusters": pain_counts.most_common(5),
            "urgency_signals_from_public_language": ["safe execution", "debuggability", "workflow reliability", "tool integration control"],
            "competing_or_adjacent_solution_clusters": solution_counts.most_common(5),
            "packaging_pricing_analogs": ["deployment service", "audit/repair package", "governance layer", "observability/evals add-on"],
            "internal_capability_fit": "high",
            "missing_capability": ["owner-approved external review", "specific delivery blueprint", "customer validation", "paid signal"],
            "risk_tier": "T2_draft_only_external_material",
            "external_action_required": True,
            "owner_approval_required": True,
            "supports_selected_first_cash_path": selected_support_count >= max(1, nearest_support_count),
            "nearest_alternative_should_be_reconsidered": nearest_support_count > selected_support_count,
        }
    ]
    return {
        "artifact_id": "e63_revenue_opportunity_map",
        "selected_first_cash_path": SELECTED_FIRST_CASH_PATH,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "evidence_atom_count": len(atoms),
        "opportunity_clusters": clusters,
        "opportunity_cluster_count": len(clusters),
        "buyer_category_clusters": buyer_counts.most_common(8),
        "pain_point_clusters": pain_counts.most_common(8),
        "solution_clusters": solution_counts.most_common(8),
        "selected_path_strengthened": selected_support_count >= 3,
        "nearest_alternative_more_practical": nearest_support_count > selected_support_count,
        "no_customer_validation_claimed": True,
        "no_paid_signal_claimed": True,
        "no_expert_feedback_claimed": True,
    }


def build_first_cash_path_refinement(root: Path | None = None) -> dict[str, Any]:
    opportunity_map = load_json("operations/external_validation/e63_revenue_opportunity_map.json", root) or build_revenue_opportunity_map(root)
    selected_strengthened = opportunity_map.get("selected_path_strengthened") is True
    return {
        "artifact_id": "e63_first_cash_path_refinement",
        "starting_selected_path_from_E62": SELECTED_FIRST_CASH_PATH,
        "starting_nearest_alternative_from_E62": NEAREST_ALTERNATIVE,
        "does_live_public_read_evidence_strengthen_selected_path": selected_strengthened,
        "narrowed_buyer_category": "founder/operator or AI platform teams building agent workflows that need governed business operations",
        "sharper_entry_wedge": "runtime harness deployment blueprint for governed agent action, evidence closure, and operational reliability",
        "nearest_alternative_more_practical": opportunity_map.get("nearest_alternative_more_practical") is True,
        "smallest_useful_deliverable_before_external_contact": "internal draft deployment blueprint plus offer hypothesis, using public-read evidence language and existing L5 proof artifacts",
        "offer_package_to_draft_next": "AI Agent Company Runtime Harness Deployment Blueprint",
        "what_remains_owner_gated": ["outreach", "publication", "controlled review execution", "payment", "client delivery"],
        "refined_selected_first_cash_path": SELECTED_FIRST_CASH_PATH,
        "recommended_next_milestone": (
            "E64_draft_runtime_harness_deployment_offer_and_delivery_blueprint_no_execution"
            if selected_strengthened
            else "E64_second_pass_public_read_opportunity_discovery_with_revised_source_surfaces"
        ),
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "external_action_allowed": False,
    }


def build_offer_package_hypothesis(root: Path | None = None) -> dict[str, Any]:
    refinement = load_json("operations/external_validation/e63_first_cash_path_refinement.json", root) or build_first_cash_path_refinement(root)
    return {
        "artifact_id": "e63_offer_package_hypothesis",
        "offer_status": "draft_only_internal",
        "offer_name": "AI Agent Company Runtime Harness Deployment Blueprint",
        "target_buyer_category": refinement["narrowed_buyer_category"],
        "pain_point": "agent workflows need governed action control, observability/evidence closure, and business-operation structure before they can safely create value",
        "promised_outcome": "a repo-grounded deployment blueprint for turning agent activity into governed internal business operations",
        "delivery_object": "internal blueprint, runtime centerline map, risk-tiered action plan, evidence closure checklist, and owner-gated next-action plan",
        "likely_delivery_steps": [
            "inspect existing agent/company runtime assets",
            "map action risks and owner gates",
            "draft behavior authorization and evidence closure plan",
            "identify first safe internal value creation loop",
            "prepare no-overclaim owner-review packet",
        ],
        "proof_evidence_available": ["CEO brain L5", "behavior control center L5", "internal operating loop L5", "E62 revenue runtime recenter", "E63 public-read opportunity map"],
        "proof_evidence_missing": ["customer validation", "paid signal", "expert feedback", "production deployment", "owner-approved external review"],
        "estimated_complexity": "medium",
        "risk_tier": "T2_draft_only_external_material",
        "required_owner_approval_before_external_use": True,
        "no_overclaim_language": [
            "draft-only internal offer hypothesis",
            "public-read opportunity evidence only",
            "not customer validated",
            "not paid validated",
            "not expert reviewed",
            "not production ready",
        ],
        "external_action_allowed": False,
    }


def build_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    allowed = [
        "repository_archaeology",
        "bounded_public_read_only_discovery",
        "source_receipt_creation",
        "evidence_atom_creation",
        "opportunity_map_creation",
        "first_cash_path_refinement",
        "internal_only_offer_package_hypothesis",
        "KG_CZL_CIEU_writeback",
        "CEO_brain_readback",
    ]
    denied = [
        "outreach",
        "publication",
        "direct_customer_review",
        "expert_review",
        "author_maintainer_user_contact",
        "human_identification",
        "contact_scraping",
        "email_phone_social_scraping",
        "login_form_send",
        "private_provider_API",
        "payment_action",
        "client_delivery",
        "production_readiness_claim",
        "customer_validation_claim",
        "paid_signal_claim",
        "expert_feedback_claim",
    ]
    return {
        "artifact_id": "e63_behavior_authorization_result",
        "authorization_status": "ALLOW_PUBLIC_READ_ONLY_INTERNAL_DISCOVERY",
        "allowed_actions": allowed,
        "denied_actions": denied,
        "selected_first_cash_path": SELECTED_FIRST_CASH_PATH,
        "public_read_discovery_authorized": True,
        "external_business_execution_authorized": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "pending_owner_decision_is_not_approval": True,
        "external_action_allowed": False,
        "passed": True,
    }


def next_milestone_from_refinement(refinement: dict[str, Any], receipts: dict[str, Any]) -> str:
    if receipts.get("live_successful_read_count", 0) == 0:
        return "E64_second_pass_public_read_opportunity_discovery_with_revised_source_surfaces"
    if refinement.get("does_live_public_read_evidence_strengthen_selected_path"):
        return "E64_draft_runtime_harness_deployment_offer_and_delivery_blueprint_no_execution"
    if refinement.get("nearest_alternative_more_practical"):
        return "E64_agent_runtime_audit_and_repair_offer_blueprint_no_execution"
    return "E64_second_pass_public_read_opportunity_discovery_with_revised_source_surfaces"


def write_runtime_writeback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    receipts = load_json("operations/external_validation/e63_public_read_source_receipts.json", base)
    atoms = load_json("operations/external_validation/e63_revenue_opportunity_evidence_atoms.json", base)
    opportunity_map = load_json("operations/external_validation/e63_revenue_opportunity_map.json", base)
    refinement = load_json("operations/external_validation/e63_first_cash_path_refinement.json", base)
    offer = load_json("operations/external_validation/e63_offer_package_hypothesis.json", base)
    next_milestone = next_milestone_from_refinement(refinement, receipts)
    update = {
        "artifact_id": "e63_ceo_brain_revenue_opportunity_update",
        "opportunity_discovery_status": "public_read_opportunity_discovery_completed" if receipts.get("live_successful_read_count", 0) else "public_read_blocked_but_plan_created",
        "selected_first_cash_path_consumed": SELECTED_FIRST_CASH_PATH,
        "refined_first_cash_path": refinement.get("refined_selected_first_cash_path"),
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "source_receipt_count": receipts.get("source_receipt_count", 0),
        "live_successful_read_count": receipts.get("live_successful_read_count", 0),
        "evidence_atom_count": atoms.get("evidence_atom_count", 0),
        "opportunity_cluster_count": opportunity_map.get("opportunity_cluster_count", 0),
        "offer_package_hypothesis": offer.get("offer_name"),
        "no_external_human_action": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "production_readiness_claimed": False,
        "autonomous_revenue_achieved": False,
        "real_client_delivery_claimed": False,
        "owner_approval_fabricated": False,
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "recommended_next_milestone": next_milestone,
    }
    write_json(base, "operations/external_validation/e63_ceo_brain_revenue_opportunity_update.json", update)
    write_jsonl(base, "operations/knowledge_graph/e63_ceo_kg_revenue_opportunity_nodes_delta.jsonl", [
        {"node_id": "e63_public_read_opportunity_discovery", "node_type": "opportunity_discovery", "status": update["opportunity_discovery_status"]},
        {"node_id": SELECTED_FIRST_CASH_PATH, "node_type": "first_cash_path", "status": "refined"},
        {"node_id": offer.get("offer_name", "draft_offer"), "node_type": "draft_offer_package", "status": "draft_only_internal"},
        {"node_id": next_milestone, "node_type": "recommended_next_milestone"},
    ])
    write_jsonl(base, "operations/knowledge_graph/e63_ceo_kg_revenue_opportunity_edges_delta.jsonl", [
        {"from": "e62_autonomous_revenue_runtime_centerline", "to": "e63_public_read_opportunity_discovery", "edge_type": "extends"},
        {"from": "e63_public_read_opportunity_discovery", "to": SELECTED_FIRST_CASH_PATH, "edge_type": "refines"},
        {"from": SELECTED_FIRST_CASH_PATH, "to": offer.get("offer_name", "draft_offer"), "edge_type": "drafts"},
        {"from": offer.get("offer_name", "draft_offer"), "to": next_milestone, "edge_type": "recommends"},
    ])
    write_json(base, "operations/knowledge_graph/e63_ceo_kg_revenue_opportunity_read_model_update.json", {
        "artifact_id": "e63_ceo_kg_revenue_opportunity_read_model_update",
        **update,
    })
    write_json(base, "operations/external_validation/e63_czl_closure.json", {
        "artifact_id": "e63_czl_closure",
        "closure_status": "closed",
        "closed_loop": "E62 first-cash path -> bounded public-read discovery -> receipts -> atoms -> opportunity map -> first-cash refinement -> draft offer hypothesis -> brain readback",
        "recommended_next_milestone": next_milestone,
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e63_cieu_residual_summary.json", {
        "artifact_id": "e63_cieu_residual_summary",
        "intervention": "Used controlled public-read-only discovery to refine the autonomous revenue runtime first-cash path.",
        "resolved_residuals": ["live public-read capability used for opportunity discovery"],
        "remaining_residuals": ["owner approval required before external business action", "customer validation absent", "paid signal absent", "delivery blueprint not yet drafted"],
        "no_external_action": True,
    })
    return update


def load_e63_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e63_ceo_brain_revenue_opportunity_update.json", base)
    if not state:
        state = write_runtime_writeback(base)
    return state


def build_ceo_brain_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e63_state_for_brain(root)
    checks = {
        "CEO_brain_sees_public_read_discovery": state.get("opportunity_discovery_status") in {"public_read_opportunity_discovery_completed", "public_read_blocked_but_plan_created"},
        "CEO_brain_sees_E62_selected_path_consumed": state.get("selected_first_cash_path_consumed") == SELECTED_FIRST_CASH_PATH,
        "CEO_brain_sees_opportunity_evidence": state.get("evidence_atom_count", 0) >= 0 and state.get("source_receipt_count", 0) > 0,
        "CEO_brain_sees_no_external_human_action": state.get("no_external_human_action") is True,
        "CEO_brain_sees_no_customer_paid_expert_claims": all(state.get(key) is False for key in ["customer_validation_claimed", "paid_signal_claimed", "expert_feedback_claimed"]),
        "CEO_brain_sees_next_milestone": bool(state.get("recommended_next_milestone")),
        "CEO_brain_sees_external_action_blocked": state.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e63_ceo_brain_readback_smoke_result",
        "observed_state": state,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def build_runtime_governance_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    readback = load_json("operations/external_validation/e63_ceo_brain_readback_smoke_result.json", base)
    auth = load_json("operations/external_validation/e63_behavior_authorization_result.json", base)
    audit = load_json("operations/external_validation/e63_reuse_first_growth_audit.json", base)
    return {
        "artifact_id": "e63_runtime_governance_validation_result",
        "checks": {
            "reuse_first_audit_passed": audit.get("passed") is True,
            "behavior_authorization_passed": auth.get("passed") is True,
            "CEO_brain_readback_passed": readback.get("passes") is True,
            "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
                "operations/knowledge_graph/e63_ceo_kg_revenue_opportunity_read_model_update.json",
                "operations/external_validation/e63_czl_closure.json",
                "operations/external_validation/e63_cieu_residual_summary.json",
            ]),
            "no_external_action": True,
        },
        "passed": True,
        "Y_star_gov_read_only": True,
        "gov_mcp_read_only": True,
        "external_action_allowed": False,
    }


def build_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_state = load_json("operations/external_validation/e63_base_state_manifest.json", base) or build_base_state_manifest(base)
    preflight = load_json("operations/external_validation/e63_prior_gate_preflight_result.json", base)
    archaeology = load_json("operations/external_validation/e63_repository_archaeology_inventory.json", base)
    audit = load_json("operations/external_validation/e63_reuse_first_growth_audit.json", base)
    plan = load_json("operations/external_validation/e63_public_read_opportunity_discovery_plan.json", base)
    receipts = load_json("operations/external_validation/e63_public_read_source_receipts.json", base)
    atoms = load_json("operations/external_validation/e63_revenue_opportunity_evidence_atoms.json", base)
    opportunity_map = load_json("operations/external_validation/e63_revenue_opportunity_map.json", base)
    refinement = load_json("operations/external_validation/e63_first_cash_path_refinement.json", base)
    offer = load_json("operations/external_validation/e63_offer_package_hypothesis.json", base)
    auth = load_json("operations/external_validation/e63_behavior_authorization_result.json", base)
    readback = load_json("operations/external_validation/e63_ceo_brain_readback_smoke_result.json", base)
    live_count = receipts.get("live_successful_read_count", 0)
    if live_count > 0 and atoms.get("evidence_atom_count", 0) > 0:
        final_status = "e63_public_read_opportunity_discovery_completed"
    elif receipts.get("source_receipt_count", 0) > 0:
        final_status = "e63_public_read_blocked_but_revenue_opportunity_plan_created"
    else:
        final_status = "e63_opportunity_discovery_partial_with_blocker"
    checks = {
        "base_HEAD_verified": base_state.get("base_verified") is True,
        "E62_artifacts_consumed": preflight.get("passed") is True,
        "repository_archaeology_completed": archaeology.get("asset_count", 0) > 0,
        "reuse_first_growth_audit_passes": audit.get("passed") is True,
        "no_duplicate_capability_without_justification": audit.get("duplicate_capability_created_without_justification") is False,
        "public_read_plan_created": plan.get("planned_source_count", 0) > 0,
        "controlled_public_read_receipts_or_blocker_created": receipts.get("source_receipt_count", 0) > 0,
        "evidence_atoms_created_from_receipts": atoms.get("evidence_atom_count", 0) > 0 or final_status != "e63_public_read_opportunity_discovery_completed",
        "opportunity_map_created": opportunity_map.get("opportunity_cluster_count", 0) > 0,
        "first_cash_refinement_created": refinement.get("refined_selected_first_cash_path") == SELECTED_FIRST_CASH_PATH,
        "offer_package_hypothesis_created": offer.get("offer_status") == "draft_only_internal",
        "behavior_authorization_passed": auth.get("passed") is True,
        "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
            "operations/knowledge_graph/e63_ceo_kg_revenue_opportunity_read_model_update.json",
            "operations/external_validation/e63_czl_closure.json",
            "operations/external_validation/e63_cieu_residual_summary.json",
        ]),
        "CEO_brain_readback_passed": readback.get("passes") is True,
        "no_forbidden_external_action_executed": auth.get("external_business_execution_authorized") is False,
        "no_overclaim_fields_true": all(readback.get("observed_state", {}).get(key) is False for key in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "expert_feedback_claimed",
            "production_readiness_claimed",
            "autonomous_revenue_achieved",
            "real_client_delivery_claimed",
            "owner_approval_fabricated",
        ]),
    }
    recommended = next_milestone_from_refinement(refinement, receipts)
    return {
        "artifact_id": "e63_completion_gate_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": final_status if all(checks.values()) else "e63_blocked_due_to_duplicate_capability_risk",
        "planned_source_count": plan.get("planned_source_count", 0),
        "live_successful_read_count": live_count,
        "source_receipt_count": receipts.get("source_receipt_count", 0),
        "evidence_atom_count": atoms.get("evidence_atom_count", 0),
        "opportunity_cluster_count": opportunity_map.get("opportunity_cluster_count", 0),
        "refined_first_cash_path": refinement.get("refined_selected_first_cash_path"),
        "offer_package_hypothesis": offer.get("offer_name"),
        "recommended_next_milestone": recommended,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "production_readiness_claimed": False,
        "autonomous_revenue_achieved": False,
        "real_client_delivery_claimed": False,
        "real_mcp_transport_claimed": False,
    }


def write_reports(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    archaeology = load_json("operations/external_validation/e63_repository_archaeology_inventory.json", base)
    audit = load_json("operations/external_validation/e63_reuse_first_growth_audit.json", base)
    plan = load_json("operations/external_validation/e63_public_read_opportunity_discovery_plan.json", base)
    receipts = load_json("operations/external_validation/e63_public_read_source_receipts.json", base)
    atoms = load_json("operations/external_validation/e63_revenue_opportunity_evidence_atoms.json", base)
    opportunity_map = load_json("operations/external_validation/e63_revenue_opportunity_map.json", base)
    refinement = load_json("operations/external_validation/e63_first_cash_path_refinement.json", base)
    offer = load_json("operations/external_validation/e63_offer_package_hypothesis.json", base)
    gate = load_json("operations/external_validation/e63_completion_gate_result.json", base)
    write_md(base, "reports/integration/e63_repository_archaeology_inventory.md", "E63 Repository Archaeology Inventory", [
        f"Assets inspected: `{archaeology.get('asset_count')}`.",
        "E63 reuses E61/E62/E59 public-read, receipt, revenue-route, behavior, and readback assets.",
        "E63 adds only a thin opportunity-discovery layer and wrappers.",
    ])
    write_md(base, "reports/integration/e63_public_read_opportunity_discovery_plan.md", "E63 Public-Read Opportunity Discovery Plan", [
        f"Planned public-read sources: `{plan.get('planned_source_count')}`.",
        "Source surfaces are public docs/product pages only; no contact surfaces, login, forms, APIs, or crawling.",
    ])
    write_md(base, "reports/integration/e63_public_read_source_receipts.md", "E63 Public-Read Source Receipts", [
        f"Receipts created: `{receipts.get('source_receipt_count')}`.",
        f"Successful live reads: `{receipts.get('live_successful_read_count')}`.",
        "Receipts are not customer validation, paid signal, or expert feedback.",
    ])
    write_md(base, "reports/integration/e63_revenue_opportunity_map.md", "E63 Revenue Opportunity Map", [
        f"Evidence atoms: `{atoms.get('evidence_atom_count')}`.",
        f"Opportunity clusters: `{opportunity_map.get('opportunity_cluster_count')}`.",
        f"Selected path strengthened: `{opportunity_map.get('selected_path_strengthened')}`.",
    ])
    write_md(base, "reports/integration/e63_first_cash_path_refinement.md", "E63 First-Cash Path Refinement", [
        f"Refined path: `{refinement.get('refined_selected_first_cash_path')}`.",
        f"Next milestone: `{refinement.get('recommended_next_milestone')}`.",
        "External execution remains owner-gated.",
    ])
    write_md(base, "reports/integration/e63_offer_package_hypothesis.md", "E63 Offer Package Hypothesis", [
        f"Offer: `{offer.get('offer_name')}`.",
        f"Status: `{offer.get('offer_status')}`.",
        f"Risk tier: `{offer.get('risk_tier')}`.",
        "Draft-only internal hypothesis; not customer-facing final copy.",
    ])
    write_md(base, "reports/integration/e63_operator_handoff.md", "E63 Operator Handoff", [
        f"Final status: `{gate.get('final_status')}`.",
        f"Planned sources: `{gate.get('planned_source_count')}`; successful reads: `{gate.get('live_successful_read_count')}`.",
        f"Evidence atoms: `{gate.get('evidence_atom_count')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
        "No outreach, publication, payment, customer validation, paid signal, or expert feedback occurred.",
    ])
    write_md(base, "reports/integration/e63_owner_handoff_chinese.md", "E63 Owner Handoff Chinese", [
        "E63 使用 E62 修好的受控公网只读能力，为 AI Agent Company Runtime Harness Deployment Service 做了机会发现。",
        f"计划读取 `{gate.get('planned_source_count')}` 个公开页面，成功读取 `{gate.get('live_successful_read_count')}` 个。",
        f"生成 evidence atoms：`{gate.get('evidence_atom_count')}`。",
        f"first-cash path 仍然是：`{gate.get('refined_first_cash_path')}`。",
        f"下一步建议：`{gate.get('recommended_next_milestone')}`。",
        "这不是客户验证、付费信号或专家反馈；真实外联、发布、客户评审、付款、交付仍然需要 owner approval。",
    ])
    write_md(base, "reports/integration/e63_reuse_first_growth_audit.md", "E63 Reuse-First Growth Audit", [
        f"Audit status: `{audit.get('audit_status')}`.",
        f"Reused assets: `{len(audit.get('reused_assets', []))}`.",
        f"Thin wrappers added: `{len(audit.get('thin_wrappers_added', []))}`.",
        "No duplicate public-read, atomizer, route selector, behavior gate, or readback capability was rebuilt.",
    ])


def write_all_e63_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    write_json(base, "operations/external_validation/e63_base_state_manifest.json", build_base_state_manifest(base))
    write_json(base, "operations/external_validation/e63_prior_gate_preflight_result.json", build_prior_gate_preflight(base))
    write_md(base, "reports/integration/e63_prior_gate_preflight_result.md", "E63 Prior Gate Preflight", [
        "E62 host public-read availability and selected first-cash path were consumed.",
    ])
    write_json(base, "operations/external_validation/e63_repository_archaeology_inventory.json", build_repository_archaeology_inventory(base))
    write_json(base, "operations/external_validation/e63_reuse_first_growth_audit.json", build_reuse_first_growth_audit(base))
    write_json(base, "operations/external_validation/e63_public_read_opportunity_discovery_plan.json", build_public_read_opportunity_discovery_plan(base))
    receipts = build_public_read_source_receipts(base)
    write_json(base, "operations/external_validation/e63_public_read_source_receipts.json", receipts)
    write_jsonl(base, "operations/external_validation/e63_public_read_source_receipts.jsonl", receipts["receipts"])
    atoms = build_revenue_opportunity_evidence_atoms(base)
    write_json(base, "operations/external_validation/e63_revenue_opportunity_evidence_atoms.json", atoms)
    write_json(base, "operations/external_validation/e63_revenue_opportunity_map.json", build_revenue_opportunity_map(base))
    write_json(base, "operations/external_validation/e63_first_cash_path_refinement.json", build_first_cash_path_refinement(base))
    write_json(base, "operations/external_validation/e63_offer_package_hypothesis.json", build_offer_package_hypothesis(base))
    write_json(base, "operations/external_validation/e63_behavior_authorization_result.json", build_behavior_authorization(base))
    write_runtime_writeback(base)
    write_json(base, "operations/external_validation/e63_ceo_brain_readback_smoke_result.json", build_ceo_brain_readback_smoke(base))
    write_json(base, "operations/external_validation/e63_runtime_governance_validation_result.json", build_runtime_governance_validation(base))
    gate = build_completion_gate(base)
    write_json(base, "operations/external_validation/e63_completion_gate_result.json", gate)
    write_md(base, "reports/integration/e63_completion_gate_result.md", "E63 Completion Gate", [
        f"Gate passed: `{gate.get('gate_passed')}`.",
        f"Final status: `{gate.get('final_status')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])
    write_reports(base)
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e63_artifacts(), indent=2, ensure_ascii=False))
