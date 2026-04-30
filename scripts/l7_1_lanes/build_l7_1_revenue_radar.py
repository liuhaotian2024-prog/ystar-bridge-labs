#!/usr/bin/env python3
"""Build L7.1 revenue radar lane outputs."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

from common import artifact_ref, base_no_action_receipt, base_packet, current_observation_config, lane_summary, simple_md, write_json, write_text


LANE_ID = "L7.1B"
LANE_NAME = "Revenue Radar Real Read-Only Opportunity Scan"
OUT = "l7_revenue_opportunity_radar_l7_1"
REAL_QUERY = "governed AI agent evidence workflow commercial opportunity startup founders"


def run_real_search_if_configured(config: dict) -> dict:
    """Run one bounded real search/page-read attempt when explicit config exists.

    This function never prints or serializes secret values. Provider failures are
    returned as structured blockers/residuals.
    """
    if not config["configured_for_real_read_only_scan"]:
        return {"executed": False, "results": [], "pages": [], "blockers": config["missing_requirements"]}

    backend = config["search_backend"]
    if backend != "tavily_search_api":
        return {
            "executed": False,
            "results": [],
            "pages": [],
            "blockers": [f"{backend}_real_adapter_not_enabled_for_l7_1"],
        }

    key = os.environ.get("TAVILY_API_KEY", "")
    if not key:
        return {"executed": False, "results": [], "pages": [], "blockers": ["TAVILY_API_KEY_present"]}

    try:
        body = json.dumps({"query": REAL_QUERY, "max_results": 3, "search_depth": "basic"}).encode("utf-8")
        request = urllib.request.Request(
            "https://api.tavily.com/search",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + key,
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=12) as response:
            payload = json.loads(response.read(200000).decode("utf-8", errors="replace"))
        results = []
        for idx, item in enumerate(payload.get("results", [])[:3], start=1):
            url = item.get("url", "")
            parsed = urllib.parse.urlparse(url)
            results.append(
                {
                    "result_id": f"l7_1_real_search_result_{idx:03d}",
                    "title": item.get("title", ""),
                    "url": url,
                    "source_domain": parsed.netloc,
                    "snippet_is_evidence": False,
                    "locator_only": True,
                }
            )
        return {"executed": True, "results": results, "pages": [], "blockers": []}
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        return {
            "executed": False,
            "results": [],
            "pages": [],
            "blockers": ["real_search_provider_error"],
            "error_type": type(exc).__name__,
        }


def opportunity_packets() -> list[dict]:
    refs = [
        artifact_ref("ceo_command_brief/l6_16_ceo_command_brief.json"),
        artifact_ref("internal_strategy_memo/l6_16_internal_strategy_memo.json"),
        artifact_ref("l7_revenue_opportunity_radar/opportunity_packets/opportunity_packet_001.json"),
    ]
    return [
        {
            "opportunity_id": "l7_1_opportunity_001",
            "market_area": "governed AI research-to-strategy workflows",
            "customer_segment": "AI startup founders and owner-operators who need evidence-backed decisions before outreach or publication",
            "pain_point": "Generic agents can research, but owners need proof, caveats, approval gates, and no accidental side effects.",
            "possible_offer_type": "controlled observation plus CEO command brief package",
            "evidence_basis": refs,
            "source_urls_or_artifact_refs": refs,
            "urgency": "high_for_teams_using_agentic_research",
            "feasibility": "high",
            "willingness_to_pay_hypothesis": "moderate_to_high_if_output reduces founder research time and external-risk anxiety",
            "competition_risk_notes": "Competes with generic research agents; differentiator is governed evidence loop and approval gates.",
            "next_safe_step": "draft internal offer hypothesis and pricing hypothesis",
            "human_approval_required_before_external_action": True,
        },
        {
            "opportunity_id": "l7_1_opportunity_002",
            "market_area": "owner cockpit for commercial agent teams",
            "customer_segment": "solo founders coordinating AI agents across research, operations, engineering, and revenue",
            "pain_point": "They need one cockpit showing what agents can do, what is blocked, and what moves toward revenue next.",
            "possible_offer_type": "private owner cockpit setup and weekly governed opportunity radar",
            "evidence_basis": refs,
            "source_urls_or_artifact_refs": refs,
            "urgency": "medium_high",
            "feasibility": "medium_high",
            "willingness_to_pay_hypothesis": "moderate while cockpit remains internal; higher after approved execution support exists",
            "competition_risk_notes": "Project management tools show tasks; few show evidence-grounded autonomy boundaries.",
            "next_safe_step": "build cockpit v2 and approval queue workflow",
            "human_approval_required_before_external_action": True,
        },
    ]


def build() -> None:
    config = current_observation_config()
    configured = config["configured_for_real_read_only_scan"]
    real_attempt = run_real_search_if_configured(config)
    classification = "fixture_revenue_scan_executed"
    if real_attempt["executed"]:
        classification = "partial_real_scan_no_action"
    elif configured:
        classification = "partial_real_scan_no_action"
    elif not configured:
        classification = "real_revenue_scan_blocked_by_config"

    packets = opportunity_packets()
    for idx, packet in enumerate(packets, start=1):
        packet_payload = {
            **base_packet("opportunity_packet"),
            **packet,
            "run_classification": classification,
            "real_or_fixture": "fixture_regression_proof" if classification != "partial_real_scan_no_action" else "real_config_detected_no_external_action",
            "forbidden_actions": [
                "outreach_send",
                "posting",
                "form_submission",
                "grant_submission",
                "payment",
                "account_creation",
                "customer_contact",
            ],
            "read_only_revenue_work_allowed": True,
            "draft_and_planning_allowed": True,
            "actual_execution_blocked_until_approval": True,
        }
        write_json(f"{OUT}/opportunity_packets/opportunity_packet_{idx:03d}.json", packet_payload)

    market_areas = {
        **base_packet("market_area_candidates"),
        "market_areas": [
            "governed AI research-to-strategy workflows",
            "owner cockpit for commercial agent teams",
            "read-only funding and policy radar for AI governance companies",
        ],
    }
    write_json(f"{OUT}/market_area_candidates.json", market_areas)

    segments = {
        **base_packet("customer_segment_candidates"),
        "segments": [
            "AI startup founders",
            "solo owner-operators using AI agents",
            "regulated-market product teams evaluating AI workflow automation",
        ],
    }
    write_json(f"{OUT}/customer_segment_candidates.json", segments)

    pains = {
        **base_packet("pain_point_candidates"),
        "pain_points": [
            "need evidence-backed decisions without accidental publication or outreach",
            "need one owner-facing cockpit for agent team progress",
            "need approval-gated path from research to revenue action",
        ],
    }
    write_json(f"{OUT}/pain_point_candidates.json", pains)

    funding = {
        **base_packet("funding_grant_watch_read_only"),
        "watch_mode": "read_only",
        "submission_authorized": False,
        "forms_authorized": False,
        "candidate_topics": ["AI assurance", "agent governance", "responsible AI operations"],
    }
    write_json(f"{OUT}/funding_grant_watch_read_only.json", funding)

    risks = {
        **base_packet("revenue_risk_register"),
        "risks": [
            {"risk_id": "l7_1_revenue_risk_001", "risk": "overclaiming market demand", "mitigation": "keep offer internal until human review"},
            {"risk_id": "l7_1_revenue_risk_002", "risk": "external action before approval", "mitigation": "route through L7.1 approval workflow"},
        ],
    }
    write_json(f"{OUT}/revenue_risk_register.json", risks)

    report = {
        **base_packet("real_read_only_revenue_scan_report"),
        "run_classification": classification,
        "config": config,
        "query_count": 0,
        "real_query_text": REAL_QUERY if real_attempt["executed"] else None,
        "search_results_considered": len(real_attempt["results"]),
        "pages_opened": 0,
        "domains_touched": 0,
        "external_reads_used": 1 if real_attempt["executed"] else 0,
        "real_search_executed": real_attempt["executed"],
        "real_search_results": real_attempt["results"],
        "opportunity_packets_generated": len(packets),
        "exact_activation_blocker": real_attempt["blockers"],
        "manual_url_request_occurred": False,
        "note": "Offline fixture path produced commercial opportunity packets; real scan remains available through repo-external controlled observation config.",
    }
    write_json(f"{OUT}/real_read_only_revenue_scan_report.json", report)
    write_text(
        f"{OUT}/real_read_only_revenue_scan_report.md",
        simple_md(
            "L7.1 Revenue Radar",
            [
                ("Run Classification", classification),
                ("Opportunities", "Generated two internal opportunity packets focused on governed AI research and owner cockpit workflows."),
                ("Side Effects", "No outreach, posting, form submission, payment, account creation, or grant/RFP submission occurred."),
            ],
        ),
    )
    write_json(f"{OUT}/revenue_no_action_receipt.json", base_no_action_receipt(LANE_ID, LANE_NAME))
    summary = lane_summary(LANE_ID, LANE_NAME, OUT, "completed", {"run_classification": classification, "opportunity_packets_generated": len(packets)})
    write_json(f"{OUT}/l7_1_revenue_radar_summary.json", summary)


if __name__ == "__main__":
    build()
