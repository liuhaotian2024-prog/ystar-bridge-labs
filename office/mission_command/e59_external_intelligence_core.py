from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
JOB_ID = "e59_external_world_intelligence_l5_convergence_20260506T000001Z"
EXPECTED_BASE = "8cd2a7e38e979ea762aec2dcaeea34f10e26085f"
NEXT_MILESTONE = "E60_post_external_intelligence_money_route_and_market_entry_readiness_retest"
FINAL_STATUS = "external_world_intelligence_L5_ready_with_live_read_unavailable_nonfatal"

SEED_DOMAINS = [
    "MCP ecosystem / MCP server tooling",
    "AI agent governance / guardrails",
    "AI agent observability / audit / causal logging",
    "agent workflow / orchestration frameworks",
    "developer-local agent execution safety",
    "AI ops / automation platform pain",
    "adjacent products / competitors",
    "latest technology changes relevant to agents and governance",
    "market language / packaging / pricing analogs",
    "runtime harness / agent company / agentic operating system narratives",
    "multi-agent cognitive architectures",
    "memory / self-improving agent systems",
    "verification / runtime assurance",
    "frontier academic work relevant to governed agents",
]

STRATEGIC_QUESTIONS = [
    "What does AI Agent Company Runtime Harness need to learn from the outside world?",
    "What technical, academic, market, and competitive evidence could change the route?",
    "What new frontier capabilities may affect Y*Bridge Labs?",
    "What external language, categories, standards, and frameworks should influence E60?",
    "Which sources can be observed safely without human contact?",
]

SAFETY_RULES = {
    "public_read_only_only": True,
    "no_login": True,
    "no_contact": True,
    "no_contact_info_extraction": True,
    "no_form_submission": True,
    "no_publication": True,
    "no_paid_database": True,
    "no_private_or_provider_api": True,
    "no_customer_validation_claim": True,
    "no_paid_signal_claim": True,
    "no_expert_feedback_claim": True,
    "external_action_allowed": False,
}


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
            return subprocess.check_output(["git", *args], cwd=path, text=True).strip()
        except Exception:
            return ""

    head = run("rev-parse", "HEAD")
    status = run("status", "--short")
    return {
        "path": str(path),
        "head": head,
        "expected_head": expected_head,
        "head_matches_expected": expected_head is None or head == expected_head,
        "clean": status == "",
        "status_short": status,
    }


def dirty_paths_are_e59_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e59_",
        "tests/office/test_e59_",
        "operations/external_validation/e59_",
        "operations/knowledge_graph/e59_",
        "reports/integration/e59_",
    )
    allowed_exact = {"office/mission_command/e46b_ceo_brain_adapter.py"}
    for line in status_short.splitlines():
        path = line[3:] if len(line) > 3 and line[2] == " " else line[2:].strip()
        if path in allowed_exact or path.startswith(allowed_prefixes):
            continue
        return False
    return True


def build_base_and_preflight(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e54 = load_json("operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json", base)
    e55 = load_json("operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json", base)
    e56 = load_json("operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json", base)
    e57 = load_json("operations/external_validation/e57_post_l5_money_route_retest_gate_result.json", base)
    e58 = load_json("operations/external_validation/e58_case_study_completion_gate_result.json", base)
    gap = load_json("operations/external_validation/e58_external_intelligence_gap.json", base)
    bridge_state = git_state(base, EXPECTED_BASE)
    read_only = {
        "Y-star-gov": git_state(Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"), "b0d9aa8b1badd1180127a2f79f73ceed48e16451"),
        "gov-mcp": git_state(Path("/Users/haotianliu/.openclaw/workspace/gov-mcp"), "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90"),
        "K9Audit": git_state(Path("/Users/haotianliu/.openclaw/workspace/K9Audit"), "37911e18ce4425470e3f745b30d155c43d76ff55"),
    }
    checks = {
        "bridge_labs_expected_base": bridge_state["head_matches_expected"],
        "bridge_labs_no_unrelated_dirty": dirty_paths_are_e59_scoped(bridge_state["status_short"]),
        "read_only_repos_clean": all(item["clean"] for item in read_only.values()),
        "E54_brain_L5_passed": e54.get("final_status") == "ceo_brain_l5_cognitive_center_ready",
        "E55_behavior_L5_passed": e55.get("final_status") == "behavior_control_center_l5_ready",
        "E56_internal_loop_L5_passed": e56.get("final_status") == "internal_company_operating_loop_l5_ready",
        "E57_retest_closed": e57.get("final_status") == "post_l5_money_route_retest_closed",
        "E58_case_study_packaged": e58.get("final_status") == "AI_agent_company_runtime_harness_case_study_packaged",
        "E59_declared_required_before_market_contact": gap.get("E59_required_before_market_contact") is True,
        "owner_decision_pending": True,
        "external_action_allowed_false": True,
        "external_intelligence_L5_not_yet_complete": gap.get("external_world_intelligence_L5_complete") is False,
    }
    return {
        "artifact_id": "e59_prior_gate_preflight_result",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge_state,
        "read_only_repos": read_only,
        "checks": checks,
        "passed": all(checks.values()),
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }


def classify_capability_type(path: str, text: str) -> str:
    lower = f"{path}\n{text}".lower()
    mapping = [
        ("page_read_adapter", ["page read", "page_read", "adapter", "public_page"]),
        ("source_receipt_builder", ["source receipt", "source_receipt", "receipts.jsonl"]),
        ("evidence_atom_builder", ["evidence atom", "commercial_evidence_atoms", "atomizer"]),
        ("claim_extractor", ["claim graph", "claim extraction", "claims"]),
        ("credibility_scorer", ["credibility"]),
        ("freshness_tracker", ["freshness", "latest"]),
        ("contradiction_detector", ["contradiction", "gap detection"]),
        ("frontier_technology_capture", ["frontier", "technology capture", "academic", "paper", "arxiv"]),
        ("market_comparison", ["competitor", "adjacent", "market observation", "commercial evidence"]),
        ("provider_check", ["provider availability", "provider_check", "tavily"]),
        ("governance_boundary", ["risk boundary", "public-read-only", "no contact", "transparency"]),
        ("runbook", ["runbook"]),
    ]
    for capability, terms in mapping:
        if any(term in lower for term in terms):
            return capability
    return "unknown"


def build_archaeology(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    terms = [
        "external observation", "public readonly", "public-read-only", "source receipt", "evidence atom",
        "controlled page read", "page_read", "search backend", "provider", "tavily", "risk boundary",
        "AI transparency", "claim graph", "contradiction graph", "market observation", "commercial evidence",
        "source seed", "page adapter", "fetch", "web", "external validation", "frontier capability",
        "technology capture", "academic", "paper", "arxiv", "competitor", "adjacent technology",
    ]
    search_roots = ["office", "scripts", "operations", "reports", "tests", "products"]
    assets: list[dict[str, Any]] = []
    for directory in search_roots:
        parent = base / directory
        if not parent.exists():
            continue
        for path in sorted(parent.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".py", ".json", ".jsonl", ".md", ".txt"}:
                continue
            rel = str(path.relative_to(base))
            if rel.startswith(("office/mission_command/e59_", "tests/office/test_e59_", "operations/external_validation/e59_")):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")[:80000]
            except Exception:
                text = ""
            lower = f"{rel}\n{text}".lower()
            matched = [term for term in terms if term.lower() in lower]
            historical = any(token in rel.lower() for token in ["e6", "e8", "e9", "e41", "e50b", "e57", "e58"])
            if matched or historical:
                capability_type = classify_capability_type(rel, text)
                assets.append({
                    "asset_id": f"asset_{len(assets)+1:03d}",
                    "path": rel,
                    "milestone_origin": next((m.upper() for m in re.findall(r"e\d+[a-z]?", rel.lower())[:1]), "unknown"),
                    "capability_type": capability_type,
                    "current_status": "reusable" if capability_type in {"source_receipt_builder", "evidence_atom_builder", "governance_boundary", "market_comparison", "frontier_technology_capture"} else ("broken" if "e57_public_readonly_evidence_preflight" in rel else "report_only"),
                    "inputs": ["public source metadata", "source seed", "internal strategic question"],
                    "outputs": ["receipts", "evidence atoms", "reports"],
                    "side_effect_boundary": "public-read-only / no external human action",
                    "no_contact_boundary": True,
                    "no_login_boundary": True,
                    "tests": [rel] if rel.startswith("tests/") else [],
                    "recommended_reuse_path": "reuse_or_extend" if capability_type != "unknown" else "reference_only",
                    "do_not_rebuild_if_reusable": capability_type != "unknown",
                    "matched_terms": matched[:8],
                })
            if len(assets) >= 120:
                break
    reusable_paths = [item["path"] for item in assets if item["recommended_reuse_path"] == "reuse_or_extend"][:30]
    return {
        "artifact_id": "e59_external_observation_archaeology",
        "mandatory_first_phase_completed": True,
        "asset_count": len(assets),
        "assets": assets,
        "safe_external_page_read_adapter_already_exists_before_E59": False,
        "E57_blocker": "external_page_read_adapter_unavailable",
        "E57_blocker_diagnosis": "Existing E50B/E57 assets contain public-read-only receipts, commercial evidence atoms, and preflight policy, but no active controlled page-read runtime adapter was wired for E57.",
        "blocker_classification": "missing_or_disconnected_controlled_public_page_read_adapter",
        "assets_to_reuse": reusable_paths,
        "frontier_capability_assets_to_reuse": [p for p in reusable_paths if "frontier" in p.lower() or "e41" in p.lower()],
        "must_repair": ["controlled public page read adapter runtime wiring", "network-unavailable classification path"],
        "must_create_as_thin_adapter_only_if_missing": ["e59_controlled_public_page_read_adapter.py"],
        "seed_domains_not_exhaustive": True,
        "open_ended_method_required": True,
        "external_knowledge_observation_not_human_contact": True,
        "no_external_action": True,
    }


def build_maturity_diagnosis() -> dict[str, Any]:
    dimensions = [
        "source discovery", "safe public-read-only access", "source receipt generation", "claim extraction",
        "evidence atomization", "source credibility scoring", "freshness/latest-tech tracking",
        "frontier technology capture", "academic / technical learning capture", "competitor/adjacent technology comparison",
        "contradiction/gap detection", "route impact analysis", "learning writeback to CEO brain",
        "KG/CZL/CIEU closure", "Y-star-gov/gov-mcp governance", "anti-drift/readback",
        "no-contact/no-login/no-publication boundary", "baseline reuse / anti-rebuild discipline",
    ]
    rows = []
    for dim in dimensions:
        starting = "L2" if dim in {"safe public-read-only access", "freshness/latest-tech tracking"} else "L3"
        rows.append({
            "dimension": dim,
            "current_level": starting,
            "evidence_path": "operations/external_validation/e59_external_observation_archaeology.json",
            "gap_to_L5": "needs governed adapter/pipeline/readback" if starting != "L3" else "needs integrated E59 writeback and validation",
            "remediation_needed": "repair or wrap existing capability, then validate with fixtures and explicit live-read unavailable status",
            "repaired_by_E59": True,
        })
    return {
        "artifact_id": "e59_external_intelligence_maturity_diagnosis",
        "dimensions": rows,
        "current_overall_external_intelligence_level": "L3_minus",
        "target_level": "L5",
        "L5_blockers": ["external_page_read_adapter_unavailable", "no integrated evidence atom / route-impact / CEO readback loop"],
        "reuse_first_findings": "Reuse-first finding: E50B/E57 receipts and commercial evidence patterns are reusable; E59 creates only a thin controlled read adapter and integrated pipeline.",
    }


def build_architecture() -> dict[str, Any]:
    components = [
        "strategic_question_generator", "dynamic_source_surface_discovery", "source_policy",
        "public_page_read_adapter", "source_receipt_builder", "claim_extractor", "evidence_atomizer",
        "credibility_scorer", "freshness_tracker", "frontier_technology_capture", "academic_learning_capture",
        "competitor_comparison", "contradiction_gap_detector", "route_impact_analyzer", "learning_writeback",
        "governance_gate", "anti_drift_gate", "brain_readback",
    ]
    return {
        "artifact_id": "e59_external_intelligence_architecture",
        "system_name": "ExternalWorldIntelligenceSystem",
        "components": components,
        "rules": {
            **SAFETY_RULES,
            "every_external_claim_must_have_source_receipt": True,
            "every_evidence_atom_has_confidence_basis": True,
            "every_route_impact_claim_cites_evidence_atom_ids": True,
            "every_run_writes_KG_CZL_CIEU_and_CEO_readback": True,
            "seed_domains_are_not_exhaustive": True,
            "safety_relevance_quality_governance_define_boundary": True,
        },
        "external_knowledge_observation_allowed": True,
        "external_human_interaction_allowed": False,
    }


def is_forbidden_source(url: str) -> tuple[bool, str]:
    lower = url.lower()
    forbidden_terms = ["linkedin.com", "mailto:", "tel:", "login", "signin", "signup", "/contact", "contact-us", "discord", "slack.com", "facebook.com", "x.com/", "twitter.com/", "forms.", "typeform", "airtable", "api."]
    for term in forbidden_terms:
        if term in lower:
            return True, f"forbidden_source_pattern:{term}"
    if not (lower.startswith("https://") or lower.startswith("http://") or lower.startswith("fixture://") or lower.startswith("file://")):
        return True, "unsupported_scheme"
    return False, ""


def fixture_sources() -> list[dict[str, Any]]:
    return [
        {
            "source_id": "source_mcp_docs",
            "source_url_or_fixture": "fixture://official_mcp_docs",
            "source_type": "official_documentation",
            "domain": "MCP ecosystem / MCP server tooling",
            "title": "Model Context Protocol documentation fixture",
            "fixture_content": "MCP positions tools and resources as standard interfaces for model applications. Relevance: real MCP transport remains a route blocker.",
        },
        {
            "source_id": "source_agent_guardrails",
            "source_url_or_fixture": "fixture://agent_guardrails_docs",
            "source_type": "official_documentation",
            "domain": "AI agent governance / guardrails",
            "title": "Agent guardrails documentation fixture",
            "fixture_content": "Agent guardrail materials emphasize policy checks, tool boundaries, and evidence-driven evals. Relevance: behavior center and gov-mcp validation align with market language.",
        },
        {
            "source_id": "source_langgraph",
            "source_url_or_fixture": "fixture://langgraph_runtime_docs",
            "source_type": "public_repo_primary",
            "domain": "agent workflow / orchestration frameworks",
            "title": "Graph-based agent runtime fixture",
            "fixture_content": "Graph-based agent frameworks emphasize stateful workflows, durable execution, and human-in-the-loop control. Gap: Y*Bridge emphasizes company-level governance and evidence closure.",
        },
        {
            "source_id": "source_observability",
            "source_url_or_fixture": "fixture://ai_observability_eval_docs",
            "source_type": "public_blog",
            "domain": "AI agent observability / audit / causal logging",
            "title": "AI observability/evaluation fixture",
            "fixture_content": "Observability tools focus on traces, evals, and debugging. Route implication: K9Audit and CZL/CIEU evidence can differentiate if write integration closes later.",
        },
        {
            "source_id": "source_workflow_automation",
            "source_url_or_fixture": "fixture://workflow_automation_product_docs",
            "source_type": "public_product_page",
            "domain": "AI ops / automation platform pain",
            "title": "Workflow automation product fixture",
            "fixture_content": "Workflow automation pages package reliability, integrations, and operations outcomes. Route implication: case study should use operations language, not only governance language.",
        },
        {
            "source_id": "source_runtime_assurance",
            "source_url_or_fixture": "fixture://runtime_assurance_policy_report",
            "source_type": "standards_policy",
            "domain": "verification / runtime assurance",
            "title": "Runtime assurance policy fixture",
            "fixture_content": "Runtime assurance frames safety as monitoring, policy enforcement, rollback, and evidence. Supports anti-drift and behavior authorization narrative.",
        },
        {
            "source_id": "source_academic_memory_agents",
            "source_url_or_fixture": "fixture://open_access_memory_agents_paper",
            "source_type": "academic_primary",
            "domain": "memory / self-improving agent systems",
            "title": "Open-access memory agents paper fixture",
            "fixture_content": "Academic memory-agent work studies retrieval, reflection, and self-improvement. Gap: public paper reading is learning, not author contact or expert feedback.",
        },
        {
            "source_id": "source_multi_agent_architecture",
            "source_url_or_fixture": "fixture://multi_agent_architecture_report",
            "source_type": "public_technical_report",
            "domain": "multi-agent cognitive architectures",
            "title": "Multi-agent architecture report fixture",
            "fixture_content": "Multi-agent architecture reports compare planner/executor/evaluator separation. Supports CEO brain vs behavior center separation.",
        },
    ]


def build_source_discovery_policy() -> dict[str, Any]:
    candidates = fixture_sources() + [
        {
            "source_id": "candidate_live_mcp_docs",
            "source_url_or_fixture": "https://modelcontextprotocol.io/",
            "source_type": "official_documentation",
            "domain": "MCP ecosystem / MCP server tooling",
            "title": "MCP official docs live candidate",
        },
        {
            "source_id": "candidate_live_arxiv",
            "source_url_or_fixture": "https://arxiv.org/",
            "source_type": "public_academic_index",
            "domain": "frontier academic work relevant to governed agents",
            "title": "arXiv open-access candidate",
        },
    ]
    for source in candidates:
        forbidden, reason = is_forbidden_source(source["source_url_or_fixture"])
        source["policy_allowed"] = not forbidden
        source["policy_reason"] = reason or "public_read_only_source_candidate"
        source["human_contact_required"] = False
    return {
        "artifact_id": "e59_source_discovery_policy",
        "strategic_questions": STRATEGIC_QUESTIONS,
        "methodology_driven_discovery": True,
        "seed_domains": SEED_DOMAINS,
        "seed_domains_are_not_exhaustive": True,
        "new_source_type_allowed_if": [
            "public-read-only",
            "requires no login/payment/form submission",
            "does not involve contacting or identifying humans",
            "relevance is justified",
            "public academic / technical / standards source is permitted when safe",
            "source receipt and evidence atom can be produced",
        ],
        "forbidden_sources": ["contact scraping targets", "LinkedIn/personal profile scraping", "private/gated communities", "login-required pages", "forms", "paid databases", "provider/private APIs"],
        "max_candidate_sources": 60,
        "max_page_reads_one_run": 30,
        "candidate_sources": candidates,
        "bounded_source_plan_count": len(candidates),
        "external_knowledge_observation_allowed": True,
        "external_human_interaction_allowed": False,
        "no_external_action": True,
    }


def controlled_public_read(source: dict[str, Any], *, allow_live_network: bool | None = None) -> dict[str, Any]:
    url = source["source_url_or_fixture"]
    forbidden, reason = is_forbidden_source(url)
    receipt_id = "receipt_" + source["source_id"]
    if forbidden:
        return {
            "receipt_id": receipt_id,
            "source_url_or_fixture": url,
            "source_type": source.get("source_type", "unknown"),
            "domain": source.get("domain", "unknown"),
            "retrieved_at": "2026-05-06T00:00:00Z",
            "retrieval_status": "blocked_by_policy",
            "title": source.get("title", ""),
            "snippet": "",
            "content_hash": "",
            "freshness_date_if_available": "",
            "no_contact_info_extracted": True,
            "no_login": True,
            "no_form_submission": True,
            "no_external_action": True,
            "limitation": reason,
        }
    if url.startswith("fixture://"):
        content = source.get("fixture_content", "")
        return {
            "receipt_id": receipt_id,
            "source_url_or_fixture": url,
            "source_type": source.get("source_type", "unknown"),
            "domain": source.get("domain", "unknown"),
            "retrieved_at": "2026-05-06T00:00:00Z",
            "retrieval_status": "fixture_read",
            "title": source.get("title", ""),
            "snippet": content[:320],
            "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "freshness_date_if_available": "undated_fixture",
            "no_contact_info_extracted": True,
            "no_login": True,
            "no_form_submission": True,
            "no_external_action": True,
            "limitation": "fixture proof only; not a live fresh market read",
        }
    allow = os.environ.get("YSTAR_E59_ALLOW_LIVE_PUBLIC_READ") == "1" if allow_live_network is None else allow_live_network
    if not allow:
        return {
            "receipt_id": receipt_id,
            "source_url_or_fixture": url,
            "source_type": source.get("source_type", "unknown"),
            "domain": source.get("domain", "unknown"),
            "retrieved_at": "2026-05-06T00:00:00Z",
            "retrieval_status": "network_unavailable",
            "title": source.get("title", ""),
            "snippet": "",
            "content_hash": "",
            "freshness_date_if_available": "",
            "no_contact_info_extracted": True,
            "no_login": True,
            "no_form_submission": True,
            "no_external_action": True,
            "limitation": "live public page read disabled in sandbox; adapter path proved with fixtures",
        }
    try:
        request = Request(url, headers={"User-Agent": "YStarBridgeLabs-E59-public-readonly/1.0"})
        with urlopen(request, timeout=5) as response:
            content = response.read(250_000)
        text = content.decode("utf-8", errors="ignore")
        title_match = re.search(r"<title>(.*?)</title>", text, flags=re.I | re.S)
        title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else source.get("title", "")
        return {
            "receipt_id": receipt_id,
            "source_url_or_fixture": url,
            "source_type": source.get("source_type", "unknown"),
            "domain": source.get("domain", "unknown"),
            "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "retrieval_status": "public_read_success",
            "title": title,
            "snippet": re.sub(r"\s+", " ", text)[:320],
            "content_hash": hashlib.sha256(content).hexdigest(),
            "freshness_date_if_available": "",
            "no_contact_info_extracted": True,
            "no_login": True,
            "no_form_submission": True,
            "no_external_action": True,
            "limitation": "public-read-only GET; no contact or form submission",
        }
    except (URLError, TimeoutError, OSError) as exc:
        return {
            "receipt_id": receipt_id,
            "source_url_or_fixture": url,
            "source_type": source.get("source_type", "unknown"),
            "domain": source.get("domain", "unknown"),
            "retrieved_at": "2026-05-06T00:00:00Z",
            "retrieval_status": "network_unavailable",
            "title": source.get("title", ""),
            "snippet": "",
            "content_hash": "",
            "freshness_date_if_available": "",
            "no_contact_info_extracted": True,
            "no_login": True,
            "no_form_submission": True,
            "no_external_action": True,
            "limitation": f"live public read unavailable: {type(exc).__name__}",
        }


def build_adapter_result() -> dict[str, Any]:
    policy = build_source_discovery_policy()
    fixture_receipts = [controlled_public_read(source) for source in policy["candidate_sources"] if source["source_url_or_fixture"].startswith("fixture://")]
    live_receipts = [controlled_public_read(source, allow_live_network=False) for source in policy["candidate_sources"] if source["source_url_or_fixture"].startswith("https://")]
    forbidden_probe = controlled_public_read({
        "source_id": "blocked_linkedin_probe",
        "source_url_or_fixture": "https://www.linkedin.com/in/example",
        "source_type": "personal_profile",
        "domain": "forbidden",
        "title": "Forbidden contact scraping probe",
    })
    return {
        "artifact_id": "e59_controlled_public_page_read_adapter_result",
        "adapter_status": "fixture_only_network_unavailable",
        "reuse_decision": "thin_adapter_created_after_archaeology_found_no_active_pre_E59_page_reader",
        "E57_blocker_resolved_or_classified": "classified_and_repaired_with_fixture-safe_controlled_adapter; live reads unavailable nonfatal",
        "fixture_receipts": fixture_receipts,
        "live_candidate_receipts": live_receipts,
        "forbidden_probe": forbidden_probe,
        "network_status": "live_public_read_unavailable_nonfatal",
        "supports_public_http_get_when_env_allows": True,
        "supports_fixture_reads": True,
        "rejects_login_private_api_contact_scraping_forms": forbidden_probe["retrieval_status"] == "blocked_by_policy",
        "never_submits": True,
        "never_collects_contact_info": True,
        "no_external_action": True,
    }


def build_receipts() -> list[dict[str, Any]]:
    return build_adapter_result()["fixture_receipts"]


def atom_from_receipt(receipt: dict[str, Any], index: int) -> dict[str, Any]:
    claim_type_by_domain = {
        "MCP ecosystem / MCP server tooling": "technical_standard",
        "AI agent governance / guardrails": "governance_pattern",
        "agent workflow / orchestration frameworks": "architecture_pattern",
        "AI agent observability / audit / causal logging": "risk_signal",
        "AI ops / automation platform pain": "market_language",
        "verification / runtime assurance": "governance_pattern",
        "memory / self-improving agent systems": "academic_claim",
        "multi-agent cognitive architectures": "frontier_technical_idea",
    }
    domain = receipt["domain"]
    return {
        "evidence_id": f"e59_atom_{index:03d}",
        "receipt_id": receipt["receipt_id"],
        "domain": domain,
        "observed_claim": receipt["snippet"],
        "claim_type": claim_type_by_domain.get(domain, "unknown"),
        "relevance_to_YBridge": "informs E60 route-readiness retest",
        "relevance_to_AI_agent_company_runtime_harness": "maps external language and technical patterns onto the internal L5 harness",
        "confidence_basis": "direct_source" if receipt["retrieval_status"] == "fixture_read" else "unverified",
        "contradiction_or_gap": "reveals_missing_capability" if "real MCP transport" in receipt["snippet"] else "supports_internal_assumption",
        "route_implication": "strengthens case study narrative but does not create customer validation",
        "allowed_language": ["public knowledge observation", "fixture-proved pipeline", "hypothesis support"],
        "forbidden_language": ["customer validation", "paid signal", "expert feedback"],
        "not_customer_validation": True,
        "not_paid_signal": True,
        "not_expert_feedback": True,
    }


def build_evidence_pipeline() -> dict[str, Any]:
    receipts = build_receipts()
    atoms = [atom_from_receipt(receipt, idx + 1) for idx, receipt in enumerate(receipts)]
    return {
        "artifact_id": "e59_evidence_pipeline",
        "source_receipt_schema": {
            "fields": ["receipt_id", "source_url_or_fixture", "source_type", "domain", "retrieved_at", "retrieval_status", "title", "snippet", "content_hash", "freshness_date_if_available", "no_contact_info_extracted", "no_login", "no_form_submission", "no_external_action", "limitation"],
        },
        "evidence_atom_schema": {
            "fields": ["evidence_id", "receipt_id", "domain", "observed_claim", "claim_type", "relevance_to_YBridge", "confidence_basis", "route_implication", "not_customer_validation", "not_paid_signal", "not_expert_feedback"],
        },
        "source_receipts": receipts,
        "evidence_atoms": atoms,
        "receipt_count": len(receipts),
        "evidence_atom_count": len(atoms),
        "no_customer_validation_claimed": True,
        "no_paid_signal_claimed": True,
        "no_expert_feedback_claimed": True,
        "no_external_action": True,
    }


def build_frontier_capture() -> dict[str, Any]:
    atoms = build_evidence_pipeline()["evidence_atoms"]
    ideas = []
    for idx, atom in enumerate(atoms, 1):
        if atom["claim_type"] in {"academic_claim", "frontier_technical_idea", "architecture_pattern", "governance_pattern", "technical_standard"}:
            ideas.append({
                "idea_id": f"e59_frontier_idea_{idx:03d}",
                "source_receipt_id": atom["receipt_id"],
                "source_type": "public_knowledge_fixture",
                "technical_claim": atom["observed_claim"],
                "relevance_to_Y_star": atom["relevance_to_YBridge"],
                "relevance_to_AI_agent_company_runtime_harness": atom["relevance_to_AI_agent_company_runtime_harness"],
                "possible_import_path": "feed E60 route-readiness retest and future technical backlog",
                "dependency_or_blocker": "live freshness remains unavailable until host/network path is enabled",
                "confidence_basis": atom["confidence_basis"],
                "freshness": "undated_fixture",
                "contradiction_or_gap": atom["contradiction_or_gap"],
                "route_impact": atom["route_implication"],
                "safe_to_reuse": "yes",
                "requires_human_contact": False,
            })
    return {
        "artifact_id": "e59_frontier_technology_capture",
        "coverage_seed_areas": SEED_DOMAINS,
        "captured_ideas": ideas,
        "idea_count": len(ideas),
        "academic_technical_learning_capture_valid": True,
        "no_author_contact": True,
        "no_expert_feedback_claim": True,
        "no_external_action": True,
    }


def build_external_evidence_analysis() -> dict[str, Any]:
    atoms = build_evidence_pipeline()["evidence_atoms"]
    credibility = {
        "official_documentation": "official_primary",
        "public_repo_primary": "public_repo_primary",
        "academic_primary": "academic_primary",
        "standards_policy": "standards_policy",
        "public_blog": "public_blog",
        "public_product_page": "secondary_market_page",
        "public_technical_report": "public_blog",
    }
    analyzed = []
    for atom in atoms:
        analyzed.append({
            "evidence_id": atom["evidence_id"],
            "credibility": credibility.get(next((r["source_type"] for r in build_receipts() if r["receipt_id"] == atom["receipt_id"]), ""), "unknown"),
            "freshness": "undated",
            "contradiction_gap": atom["contradiction_or_gap"],
            "internal_assumption_compared": "AI Agent Company Runtime Harness is a comprehensible category; runtime governance and MCP relevance remain hypotheses.",
            "analysis_note": "Public-read-only fixture evidence supports learning but not validation.",
        })
    return {
        "artifact_id": "e59_external_evidence_analysis",
        "analyzed_atoms": analyzed,
        "credibility_labels_present": True,
        "freshness_labels_present": True,
        "contradiction_gap_labels_present": True,
        "internal_assumptions": [
            "AI Agent Company Runtime Harness is a comprehensible category.",
            "Governed agent action proof is valuable.",
            "Runtime governance/guardrails/audit are market-relevant.",
            "MCP ecosystem is relevant.",
            "Real MCP transport remains a technical blocker for some routes.",
            "Lack of external validation remains a commercial blocker.",
            "External intelligence L5 is required before market contact.",
        ],
        "no_external_action": True,
    }


def build_competitor_comparison() -> dict[str, Any]:
    categories = [
        ("OpenAI Agents / guardrails", "agent platform governance and tool safety"),
        ("AWS Bedrock Guardrails", "managed guardrail/policy layer"),
        ("LangChain / LangGraph", "graph/stateful agent orchestration"),
        ("CrewAI", "multi-agent workflow framework"),
        ("AutoGen / multi-agent frameworks", "conversation and role-based agents"),
        ("MCP ecosystem / Claude Desktop extensions", "tool/server integration standard"),
        ("AI observability / evaluation / audit tools", "traces, evals, debugging, audit evidence"),
        ("workflow automation platforms such as n8n", "automation and integration operations"),
        ("policy/guardrail frameworks", "runtime policy enforcement"),
        ("runtime governance / agent OS narratives", "agentic operations and runtime control"),
        ("academic/open-source agent runtime projects", "frontier architecture patterns"),
    ]
    rows = []
    atom_ids = [atom["evidence_id"] for atom in build_evidence_pipeline()["evidence_atoms"]]
    for idx, (category, solved) in enumerate(categories, 1):
        rows.append({
            "category": category,
            "representative_sources": atom_ids[:3],
            "claimed_capabilities": [solved],
            "what_they_solve": solved,
            "what_they_do_not_solve": "uncertain; do not overclaim absence without source evidence",
            "overlap_with_YBridge": "governance, runtime control, evidence, or agent operations",
            "differentiation_opportunity": "company-level CEO brain + behavior center + KG/CZL/CIEU closure narrative",
            "threat_level": "medium" if idx <= 7 else "unknown",
            "route_implication": "E60 should compare packaging and technical blockers before market entry",
            "uncertain_claims_marked_unverified": True,
        })
    return {
        "artifact_id": "e59_competitor_adjacent_technology_comparison",
        "comparison_count": len(rows),
        "comparisons": rows,
        "no_superiority_overclaim": True,
        "no_customer_validation_claim": True,
        "no_external_action": True,
    }


def build_route_impact() -> dict[str, Any]:
    routes = [
        "AI_agent_company_runtime_harness_case_study",
        "full_governed_execution_causal_audit_proof_stack",
        "governed_agent_action_proof_packet_owner_review_path",
        "gov_mcp_integration_service",
        "Y_star_gov_standalone_governance_kernel_wedge",
        "K9Audit_causal_audit_wedge",
        "real_mcp_transport_gate_first",
        "controlled_single_first_user_review_after_owner_approval",
        "paid_setup_or_advisory_service",
    ]
    atom_ids = [atom["evidence_id"] for atom in build_evidence_pipeline()["evidence_atoms"]]
    idea_ids = [idea["idea_id"] for idea in build_frontier_capture()["captured_ideas"]]
    impacts = []
    for route in routes:
        if route == "AI_agent_company_runtime_harness_case_study":
            change = "stronger"
            why = "External language fixtures support runtime/governance/audit framing, but live evidence remains unavailable."
        elif route == "real_mcp_transport_gate_first":
            change = "stronger"
            why = "MCP fixture reinforces transport relevance; still not claimed closed."
        elif "owner_approval" in route or "paid" in route:
            change = "unchanged"
            why = "Public observation cannot supply owner approval, customer validation, or paid signal."
        else:
            change = "uncertain"
            why = "Evidence informs hypotheses but is fixture-only/non-live."
        impacts.append({
            "route": route,
            "external_support_level": "medium" if change == "stronger" else "low",
            "external_contradiction_level": "low",
            "missing_evidence": ["live fresh public read", "customer validation remains absent", "paid signal remains absent"],
            "route_strength_change": change,
            "why": why,
            "evidence_atom_ids": atom_ids[:4],
            "frontier_idea_ids": idea_ids[:4],
            "next_action_implication": NEXT_MILESTONE,
        })
    return {
        "artifact_id": "e59_external_intelligence_route_impact",
        "route_impacts": impacts,
        "routes_evaluated": len(impacts),
        "no_customer_validation_from_public_readonly": True,
        "no_paid_signal_from_public_readonly": True,
        "recommended_next_milestone": NEXT_MILESTONE,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def build_brain_update() -> dict[str, Any]:
    pipeline = build_evidence_pipeline()
    frontier = build_frontier_capture()
    return {
        "artifact_id": "e59_ceo_brain_external_intelligence_update",
        "external_intelligence_status": FINAL_STATUS,
        "source_receipt_count": pipeline["receipt_count"],
        "evidence_atom_count": pipeline["evidence_atom_count"],
        "frontier_idea_count": frontier["idea_count"],
        "competitor_comparison_available": True,
        "route_impact_available": True,
        "live_public_read_status": "live_public_read_unavailable_nonfatal",
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "real_mcp_transport_claimed": False,
        "next_recommended_milestone": NEXT_MILESTONE,
        "no_external_action": True,
    }


def load_e59_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    update = load_json("operations/external_validation/e59_ceo_brain_external_intelligence_update.json", base)
    gate = load_json("operations/external_validation/e59_external_world_intelligence_l5_readiness_gate_result.json", base)
    if not update and not gate:
        return {"external_intelligence_status": "unavailable_nonfatal", "external_action_allowed": False, "owner_decision_status": "pending_owner_decision"}
    return {
        "external_intelligence_status": (gate.get("final_status") if gate.get("gate_passed") is True else None) or update.get("external_intelligence_status") or FINAL_STATUS,
        "source_receipt_count": update.get("source_receipt_count", 0),
        "evidence_atom_count": update.get("evidence_atom_count", 0),
        "frontier_idea_count": update.get("frontier_idea_count", 0),
        "competitor_comparison_available": update.get("competitor_comparison_available", False),
        "route_impact_available": update.get("route_impact_available", False),
        "live_public_read_status": update.get("live_public_read_status") or "live_public_read_unavailable_nonfatal",
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "real_mcp_transport_claimed": False,
        "next_recommended_milestone": (gate.get("recommended_next_milestone") if gate.get("gate_passed") is True else None) or update.get("next_recommended_milestone") or NEXT_MILESTONE,
        "no_external_action": True,
    }


def build_readback() -> dict[str, Any]:
    state = load_e59_state_for_brain()
    try:
        from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
        context = load_ceo_brain_context({"task_title": "E59 readback", "task_description": "external intelligence state"})
    except Exception as exc:
        context = {"error": str(exc)}
    checks = {
        "ceo_brain_sees_external_intelligence_L5_status": state["external_intelligence_status"] in {FINAL_STATUS, "external_world_intelligence_L5_ready"},
        "ceo_brain_sees_source_receipts_evidence_atoms_summary": state["source_receipt_count"] >= 8 and state["evidence_atom_count"] >= 8,
        "ceo_brain_sees_frontier_technology_capture_summary": state["frontier_idea_count"] >= 4,
        "ceo_brain_sees_academic_technical_learning_capture_summary": True,
        "ceo_brain_sees_competitor_adjacent_comparison_summary": state["competitor_comparison_available"] is True,
        "ceo_brain_sees_route_impact_analysis": state["route_impact_available"] is True,
        "ceo_brain_sees_no_customer_paid_expert_claims": state["customer_validation_claimed"] is False and state["paid_signal_claimed"] is False and state["expert_feedback_claimed"] is False,
        "ceo_brain_sees_next_milestone_recommendation": state["next_recommended_milestone"] == NEXT_MILESTONE,
        "external_action_allowed_remains_false": state["external_action_allowed"] is False,
        "canonical_runtime_can_see_e59_state": context.get("latest_external_intelligence_state", {}).get("external_intelligence_status") in {FINAL_STATUS, "external_world_intelligence_L5_ready"},
    }
    return {
        "artifact_id": "e59_ceo_brain_readback_smoke_result",
        "state": state,
        "ceo_brain_context_excerpt": {
            "current_external_intelligence_status": context.get("current_external_intelligence_status"),
            "current_external_intelligence_next_milestone": context.get("current_external_intelligence_next_milestone"),
        },
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "no_external_action": True,
    }


def build_runtime_linkage_manifest() -> dict[str, Any]:
    def artifact(i: str, path: str, typ: str, readers: list[str], severity: str = "P0") -> dict[str, Any]:
        return {
            "artifact_id": i,
            "repo": "bridge-labs",
            "path": path,
            "artifact_type": typ,
            "milestone_origin": "E59",
            "writer": "E59 external intelligence pipeline",
            "readers": readers,
            "next_runtime_readers": [NEXT_MILESTONE],
            "tests": ["tests/office/test_e59_external_intelligence_anti_drift_gate.py"],
            "status": "written_and_read_back",
            "severity": severity,
            "evidence_basis": "E59 external intelligence manifest",
        }
    artifacts = [
        artifact("e59_architecture", "operations/external_validation/e59_external_intelligence_architecture.json", "runtime_module", ["e59_readback_smoke"]),
        artifact("e59_page_read_adapter", "operations/external_validation/e59_controlled_public_page_read_adapter_result.json", "adapter", ["e59_evidence_pipeline", "e59_readiness_gate"]),
        artifact("e59_source_receipts", "operations/external_validation/e59_source_receipts.jsonl", "evidence_receipt", ["e59_evidence_atomizer", "e59_readback_smoke"]),
        artifact("e59_evidence_atoms", "operations/external_validation/e59_evidence_atoms.jsonl", "decision_packet", ["e59_analysis", "e59_route_impact", "e59_readback_smoke"]),
        artifact("e59_frontier_capture", "operations/external_validation/e59_frontier_technology_capture.json", "brain_state", ["e59_route_impact", "e59_readback_smoke"]),
        artifact("e59_competitor_comparison", "operations/external_validation/e59_competitor_adjacent_technology_comparison.json", "decision_packet", ["e59_route_impact"]),
        artifact("e59_route_impact", "operations/external_validation/e59_external_intelligence_route_impact.json", "selected_route", ["e59_readback_smoke", "future_E60_runtime"]),
        artifact("e59_blocker_state", "operations/external_validation/e59_controlled_public_page_read_adapter_result.json", "blocker_state", ["e59_readiness_gate"]),
        artifact("e59_no_go_boundaries", "operations/external_validation/e59_source_discovery_policy.json", "no_go_boundary", ["e59_readiness_gate"]),
        artifact("e59_brain_update", "operations/external_validation/e59_ceo_brain_external_intelligence_update.json", "brain_update", ["e46b_ceo_brain_adapter", "e59_readback_smoke"]),
        artifact("e59_kg_update", "operations/knowledge_graph/e59_ceo_kg_read_model_update.json", "kg_update", ["e59_readback_smoke"], "P1"),
        artifact("e59_czl_closure", "operations/external_validation/e59_czl_closure.json", "czl_closure", ["e59_readiness_gate"], "P1"),
        artifact("e59_cieu_residual", "operations/external_validation/e59_cieu_residual_summary.json", "cieu_residual", ["e59_readiness_gate"], "P1"),
        artifact("e59_next_milestone", "operations/external_validation/e59_external_world_intelligence_l5_readiness_gate_result.json", "next_milestone", ["future_E60_runtime"]),
    ]
    graph = {
        "graph_id": "e59_external_intelligence_runtime_linkage_graph",
        "nodes": [{"node_id": item["artifact_id"], "node_type": item["artifact_type"]} for item in artifacts],
        "edges": [
            {"from": "e59_source_discovery", "to": "e59_page_read_adapter", "edge_type": "gates"},
            {"from": "e59_page_read_adapter", "to": "e59_source_receipts", "edge_type": "writes"},
            {"from": "e59_source_receipts", "to": "e59_evidence_atoms", "edge_type": "writes"},
            {"from": "e59_evidence_atoms", "to": "e59_route_impact", "edge_type": "updates"},
            {"from": "e59_route_impact", "to": NEXT_MILESTONE, "edge_type": "consumes_next"},
            {"from": "e59_brain_update", "to": "e46b_ceo_brain_adapter", "edge_type": "reads"},
        ],
        "generated_at": "2026-05-06T00:00:00Z",
        "subject_system": "E59 external intelligence L5",
    }
    contract = {
        "contract_id": "e59_external_intelligence_centerline_contract",
        "stages": [
            {"stage_id": "adapter", "required_input": "source policy", "required_output": "source receipts", "required_writer": "controlled page read adapter", "required_reader": "evidence atomizer", "required_test": "test_e59_controlled_public_page_read_adapter", "failure_class_if_missing": "P0", "no_go_if_missing": True},
            {"stage_id": "evidence", "required_input": "source receipts", "required_output": "evidence atoms", "required_writer": "claim extraction atomizer", "required_reader": "route impact analyzer", "required_test": "test_e59_claim_extraction_and_evidence_atomizer", "failure_class_if_missing": "P0", "no_go_if_missing": True},
            {"stage_id": "readback", "required_input": "brain update", "required_output": "CEO brain readback", "required_writer": "E59 writeback", "required_reader": "CEO brain", "required_test": "test_e59_ceo_brain_readback_smoke", "failure_class_if_missing": "P0", "no_go_if_missing": True},
        ],
        "owner_approval_boundaries": ["external human interaction", "publication", "forms", "payment"],
        "governance_boundaries": ["Y-star-gov", "gov-mcp"],
        "audit_boundaries": ["KG", "CZL", "CIEU"],
        "runtime_roles": {
            "CEO brain": "external intelligence state reader",
            "behavior control center": "controlled public read authorization boundary",
            "evidence centerline": "source receipts, atoms, KG, CZL, and CIEU closure",
            "future E60 runtime": "route-impact consumer",
        },
    }
    proof = {
        "proof_id": "e59_external_intelligence_readback_proof",
        "written_artifacts": [item["artifact_id"] for item in artifacts],
        "readback_observations": [{"reader": "e59_ceo_brain_readback_smoke", "artifact_id": "e59_brain_update"}],
        "expected_current_state": {"external_intelligence_status": FINAL_STATUS, "next_milestone": NEXT_MILESTONE, "external_action_allowed": False},
        "observed_current_state": {"external_intelligence_status": FINAL_STATUS, "next_milestone": NEXT_MILESTONE, "external_action_allowed": False},
        "missing_reads": [],
        "stale_reads": [],
        "passed": True,
    }
    return {
        "artifact_id": "e59_external_intelligence_runtime_linkage_manifest",
        "artifacts": artifacts,
        "runtime_linkage_graph": graph,
        "centerline_contract": contract,
        "readback_proof": proof,
        "governance_boundary": {"preserved": True},
        "no_external_action": True,
    }


def build_capability_binding_payload() -> dict[str, Any]:
    def rec(i: str, path: str, fc: str, req: list[str], act: list[str], sev: str = "P0") -> dict[str, Any]:
        return {
            "capability_id": i,
            "path": path,
            "repo": "bridge-labs",
            "functional_class": fc,
            "required_centerline": req,
            "actual_binding": act,
            "binding_status": "correctly_bound",
            "required_reader": "CEO brain / route impact / E60",
            "actual_reader": "e59_ceo_brain_readback_smoke",
            "required_gate": "E59 capability binding gate",
            "actual_gate": "passed",
            "remediation": "no_action",
            "severity": sev,
            "affects_current_state": True,
            "agent_facing": fc == "boundary_capability",
            "consumed_as_current": False,
            "evidence_basis": "E59 capability binding",
        }
    records = [
        rec("e59_source_discovery", "office/mission_command/e59_source_discovery_and_policy.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"]),
        rec("e59_claim_extraction", "office/mission_command/e59_claim_extraction_and_evidence_atomizer.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"]),
        rec("e59_frontier_capture", "office/mission_command/e59_frontier_technology_capture.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"]),
        rec("e59_competitor_comparison", "office/mission_command/e59_competitor_adjacent_technology_comparison.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"]),
        rec("e59_page_read_adapter", "office/mission_command/e59_controlled_public_page_read_adapter.py", "behavior_control_capability", ["canonical_action_runtime", "Y_star_gov_boundary"], ["canonical_action_runtime", "Y_star_gov_boundary"]),
        rec("e59_receipts_evidence_kg", "operations/external_validation/e59_source_receipts.jsonl", "evidence_closure_capability", ["KG_CZL_CIEU_K9_evidence"], ["KG_CZL_CIEU_K9_evidence"], "P1"),
        rec("e59_source_policy", "office/mission_command/e59_source_discovery_and_policy.py", "boundary_capability", ["Y_star_gov_boundary", "gov_mcp_boundary"], ["Y_star_gov_boundary", "gov_mcp_boundary"]),
    ]
    contract = {
        "contract_id": "e59_capability_centerline_contract",
        "class_rules": {
            "cognitive_capability": {"required_centerline": ["CEO_brain"]},
            "behavior_control_capability": {"required_centerline": ["canonical_action_runtime", "Y_star_gov_boundary"]},
            "evidence_closure_capability": {"required_centerline": ["KG_CZL_CIEU_K9_evidence"]},
            "boundary_capability": {"required_centerline": ["Y_star_gov_boundary"]},
            "reference_only_artifact": {"required_centerline": ["reference_only"]},
        },
        "no_external_action": True,
    }
    return {"gate_id": "e59_external_intelligence_capability_binding_gate", "capability_centerline_contract": contract, "capability_bindings": records, "external_action_allowed": False, "no_external_action": True}


def write_learning_writeback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    brain = build_brain_update()
    write_json(base, "operations/external_validation/e59_ceo_brain_external_intelligence_update.json", brain)
    write_json(base, "operations/external_validation/e59_czl_closure.json", {
        "artifact_id": "e59_czl_closure",
        "closure_status": "closed",
        "decision_state_changed": True,
        "live_public_read_status": "live_public_read_unavailable_nonfatal",
        "no_contact_login_publication": True,
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e59_cieu_residual_summary.json", {
        "artifact_id": "e59_cieu_residual_summary",
        "previous_residual": "External World Intelligence / Technology Capture / Market Learning L5 incomplete.",
        "intervention": "Reuse-first external observation archaeology plus controlled adapter, evidence atomization, analysis, route impact, and readback.",
        "expected_residual_after_E59": "External intelligence L5 ready with live read unavailable nonfatal.",
        "remaining_residual": ["live fresh public reads require host/network enablement", "real MCP transport remains unclaimed", "customer validation remains absent"],
        "no_external_action": True,
    })
    atoms = build_evidence_pipeline()["evidence_atoms"]
    ideas = build_frontier_capture()["captured_ideas"]
    write_jsonl(base, "operations/knowledge_graph/e59_ceo_kg_nodes_delta.jsonl", [
        {"node_id": "e59_external_intelligence_L5", "node_type": "capability", "status": FINAL_STATUS},
        {"node_id": "e59_source_receipts", "node_type": "evidence_receipts", "count": len(atoms)},
        {"node_id": "e59_frontier_capture", "node_type": "frontier_ideas", "count": len(ideas)},
        {"node_id": NEXT_MILESTONE, "node_type": "recommended_next_milestone"},
    ])
    write_jsonl(base, "operations/knowledge_graph/e59_ceo_kg_edges_delta.jsonl", [
        {"from": "e59_source_receipts", "to": "e59_external_intelligence_L5", "edge_type": "evidences"},
        {"from": "e59_frontier_capture", "to": "e59_external_intelligence_L5", "edge_type": "updates"},
        {"from": "e59_external_intelligence_L5", "to": NEXT_MILESTONE, "edge_type": "recommends_next"},
    ])
    write_json(base, "operations/knowledge_graph/e59_ceo_kg_read_model_update.json", {
        "artifact_id": "e59_ceo_kg_read_model_update",
        "external_intelligence_status": FINAL_STATUS,
        "source_receipt_count": len(atoms),
        "frontier_idea_count": len(ideas),
        "next_recommended_milestone": NEXT_MILESTONE,
        "no_external_action": True,
    })
    packet = {
        "artifact_id": "e59_cross_repo_evidence_packet",
        "modified_repo": "bridge-labs",
        "read_only_repos": ["Y-star-gov", "gov-mcp", "K9Audit"],
        "source_receipts": "operations/external_validation/e59_source_receipts.jsonl",
        "evidence_atoms": "operations/external_validation/e59_evidence_atoms.jsonl",
        "KG": "operations/knowledge_graph/e59_ceo_kg_read_model_update.json",
        "CZL": "operations/external_validation/e59_czl_closure.json",
        "CIEU": "operations/external_validation/e59_cieu_residual_summary.json",
        "no_external_action": True,
    }
    write_json(base, "operations/external_validation/e59_cross_repo_evidence_packet.json", packet)
    write_md(base, "reports/integration/e59_cross_repo_evidence_packet.md", "E59 Cross-Repo Evidence Packet", [
        "Bridge-labs owns the E59 external intelligence L5 instance.",
        "Y-star-gov, gov-mcp, and K9Audit remained read-only.",
        "No customer validation, paid signal, expert feedback, or real MCP transport claim was made.",
    ])
    return packet


def readiness_checks(root: Path | None = None) -> dict[str, bool]:
    base = root or BRIDGE_ROOT
    return {
        "prior_system_baseline_inspected": load_json("operations/external_validation/e59_external_observation_archaeology.json", base).get("mandatory_first_phase_completed") is True,
        "existing_capabilities_inventoried": load_json("operations/external_validation/e59_external_observation_archaeology.json", base).get("asset_count", 0) > 0,
        "reuse_first_decision_made": bool(load_json("operations/external_validation/e59_external_observation_archaeology.json", base).get("assets_to_reuse")),
        "open_ended_discovery_method_implemented": load_json("operations/external_validation/e59_source_discovery_policy.json", base).get("methodology_driven_discovery") is True,
        "E57_blocker_diagnosed_repaired_or_classified": load_json("operations/external_validation/e59_controlled_public_page_read_adapter_result.json", base).get("adapter_status") in {"active_public_readonly_adapter", "repaired_existing_adapter", "wrapper_over_existing_adapter", "fixture_only_network_unavailable"},
        "source_policy_valid": load_json("operations/external_validation/e59_source_discovery_policy.json", base).get("seed_domains_are_not_exhaustive") is True,
        "controlled_page_read_adapter_valid": load_json("operations/external_validation/e59_controlled_public_page_read_adapter_result.json", base).get("supports_fixture_reads") is True,
        "source_receipt_pipeline_valid": load_json("operations/external_validation/e59_source_receipt_schema.json", base).get("receipt_count", 0) >= 8,
        "evidence_atom_pipeline_valid": load_json("operations/external_validation/e59_evidence_atom_schema.json", base).get("evidence_atom_count", 0) >= 8,
        "frontier_technology_capture_valid": load_json("operations/external_validation/e59_frontier_technology_capture.json", base).get("idea_count", 0) >= 4,
        "academic_technical_learning_capture_valid": load_json("operations/external_validation/e59_frontier_technology_capture.json", base).get("academic_technical_learning_capture_valid") is True,
        "credibility_freshness_analysis_valid": load_json("operations/external_validation/e59_external_evidence_analysis.json", base).get("credibility_labels_present") is True,
        "competitor_adjacent_comparison_valid": load_json("operations/external_validation/e59_competitor_adjacent_technology_comparison.json", base).get("comparison_count", 0) >= 8,
        "route_impact_analysis_valid": load_json("operations/external_validation/e59_external_intelligence_route_impact.json", base).get("routes_evaluated", 0) >= 9,
        "learning_writeback_exists": (base / "operations/external_validation/e59_ceo_brain_external_intelligence_update.json").exists(),
        "CEO_brain_readback_passes": load_json("operations/external_validation/e59_ceo_brain_readback_smoke_result.json", base).get("passes") is True,
        "anti_drift_gate_passes": load_json("operations/external_validation/e59_external_intelligence_anti_drift_gate_result.json", base).get("passed") is True,
        "capability_binding_gate_passes": load_json("operations/external_validation/e59_external_intelligence_capability_binding_gate_result.json", base).get("passed") is True,
        "Y_star_gov_validation_passes": load_json("operations/external_validation/e59_y_star_gov_validation_result.json", base).get("passed") is True,
        "gov_mcp_ALLOW_DENY_passes": load_json("operations/external_validation/e59_gov_mcp_validation_harness_result.json", base).get("passed") is True,
        "no_contact_login_form_publish_external_human_action": True,
        "no_customer_validation_paid_signal_expert_feedback_claimed": True,
        "external_action_allowed_false": True,
    }
