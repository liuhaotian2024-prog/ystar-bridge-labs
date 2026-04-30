#!/usr/bin/env python3
"""Lane C: service delivery dry-run and fulfillment kit."""

from __future__ import annotations

from common import no_action_receipt, packet, write_json, write_md


OUT = "l7_service_delivery_dry_run_fulfillment_kit"
LANE = "L7.4C"


def build() -> None:
    scenario = {
        **packet("sample_customer_scenario", LANE),
        "fictional_sample_customer": True,
        "customer_name": "SampleCo AI Tools",
        "stage": "seed-stage fictional AI startup",
        "urgent_decision": "which founder workflow should be automated first without creating external-action risk",
        "current_workflow": "founder uses coding agents and manual research notes",
        "private_customer_data_used": False,
    }
    work_order = {
        **packet("sample_governed_observation_work_order", LANE),
        "work_order_id": "l7_4_sample_customer_work_order_001",
        "scope": "fictional internal dry-run only",
        "query_plan": [
            "AI founder workflow audit examples",
            "coding agent governance startup workflow risk",
            "AI automation approval gates founder operations",
        ],
        "budget": {"max_queries": 3, "max_pages_opened": 0, "external_reads": 0},
        "real_customer_observation": False,
    }
    dry_run = {
        **packet("service_delivery_dry_run", LANE),
        "can_deliver_1500_pilot_with_current_tools": True,
        "answer": "Yes, for a narrow internal decision-support pilot using fictional dry-run inputs and existing L7.3 templates.",
        "delivery_time_estimate": "3-5 business days after approved intake",
        "steps": [
            "intake simulation",
            "work-order generation",
            "governed observation plan",
            "evidence packet plan",
            "CEO command brief template",
            "workflow audit template",
            "delivery checklist",
            "CEO/Researcher/Operator/Auditor handoff",
        ],
        "risks_and_bottlenecks": [
            "trust proof is still thin",
            "approved outreach is not yet executed",
            "customer-specific data handling needs review",
        ],
        "external_side_effects": False,
    }
    timeline = {
        **packet("delivery_timeline_template", LANE),
        "timeline": [
            {"day": "day_0", "activity": "approved intake and scope lock"},
            {"day": "day_1", "activity": "workflow framing and observation plan"},
            {"day": "day_2", "activity": "evidence packet and workflow audit draft"},
            {"day": "day_3", "activity": "CEO command brief and auditor review"},
            {"day": "day_4_or_5", "activity": "final internal delivery and feedback request after approval"},
        ],
    }
    qa = {
        **packet("quality_assurance_checklist", LANE),
        "checks": [
            "fictional/sample scenario clearly labeled",
            "evidence trace exists",
            "unsupported claims removed",
            "recommendations linked to caveats",
            "no customer-sensitive content",
            "approval boundary stated",
            "no external side effects",
        ],
    }
    handoffs = {
        **packet("fulfillment_roles_and_handoffs", LANE),
        "handoffs": [
            {"from": "Secretary", "to": "Operator/COO", "artifact": "intake summary"},
            {"from": "Operator/COO", "to": "Researcher", "artifact": "work order"},
            {"from": "Researcher", "to": "Auditor", "artifact": "evidence packet plan"},
            {"from": "Auditor", "to": "CEO", "artifact": "risk/conflict boundary"},
            {"from": "CEO", "to": "Secretary", "artifact": "command brief draft"},
        ],
    }

    write_json(f"{OUT}/service_delivery_dry_run.json", dry_run)
    write_json(f"{OUT}/sample_customer_scenario.json", scenario)
    write_json(f"{OUT}/sample_governed_observation_work_order.json", work_order)
    write_json(f"{OUT}/delivery_timeline_template.json", timeline)
    write_json(f"{OUT}/quality_assurance_checklist.json", qa)
    write_json(f"{OUT}/fulfillment_roles_and_handoffs.json", handoffs)
    write_json(f"{OUT}/delivery_no_action_receipt.json", no_action_receipt("delivery_no_action_receipt", LANE))

    write_md(
        f"{OUT}/service_delivery_dry_run.md",
        """
# Service Delivery Dry-Run

Question: can we actually deliver the USD 1500 pilot using current tools?

Answer: yes, for a narrow internal decision-support pilot. The service can be delivered as a controlled workflow audit plus CEO command brief, as long as customer contact and delivery remain approval-gated.

No real customer was used. No external side effects occurred.
""",
    )
    write_md(
        f"{OUT}/sample_ceo_command_brief_output.md",
        """
# Sample CEO Command Brief Output

Fictional sample only.

Recommendation: automate internal research synthesis first, not external outreach. Keep outbound actions blocked until approval and proof improve.
""",
    )
    write_md(
        f"{OUT}/sample_workflow_audit_output.md",
        """
# Sample Workflow Audit Output

Fictional sample only.

Current bottleneck: founder decision overload around AI tooling.

Fastest improvement: create an approval-gated research-to-brief workflow before automating any external behavior.
""",
    )
    print("L7.4C service delivery dry-run generated")


if __name__ == "__main__":
    build()
