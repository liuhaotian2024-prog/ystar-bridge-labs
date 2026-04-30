#!/usr/bin/env python3
"""Build L7.3 approval-ready offer validation and service workflow artifacts.

This builder is intentionally deterministic and offline by default. It converts
the L7.2 shortest-cash recommendation into an internal, human-approval-gated
commercial validation package. It never sends outreach, submits forms, requests
payment, or performs writeback.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "l7_approval_ready_offer_validation_workflow"
GENERATED_AT = "2026-04-30T00:00:00Z"
RUN_ID = "l7_3_offer_validation_workflow_run_001"


POLICY_REFS = {
    "policy_ref": "policy/action_capability_registry.json",
    "revenue_policy_ref": "policy/revenue_action_policy.json",
    "discovery_policy_ref": "policy/discovery_policy.json",
    "approval_state_machine_ref": "policy/approval_state_machine.json",
    "writeback_policy_ref": "policy/writeback_policy.json",
    "secret_scanning_policy_ref": "policy/secret_scanning_policy.json",
}


def packet(packet_type: str) -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "milestone_id": "L7.3",
        "milestone_name": "Approval-Ready Offer Validation and Service Delivery Workflow",
        "run_id": RUN_ID,
        "packet_type": packet_type,
        "generated_at_utc": GENERATED_AT,
        **POLICY_REFS,
    }


def load_json(relative_path: str, default: Any) -> Any:
    path = ROOT / relative_path
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(relative_path: str, data: Any) -> None:
    path = OUT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(relative_path: str, text: str) -> None:
    path = OUT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def build_selected_cash_path(l7_2_summary: dict[str, Any], first_cash: dict[str, Any]) -> dict[str, Any]:
    return {
        **packet("selected_cash_path"),
        "path_id": "path_001",
        "path_name": "Founder AI workflow audit and CEO command brief sprint",
        "why_selected": "It is the L7.2 primary shortest-cash path and can start as a service using existing governed observation, evidence, review, and command-brief capabilities.",
        "shortest_cash_logic": {
            "fewest_new_tools": True,
            "can_start_as_service": True,
            "does_not_require_full_product": True,
            "first_cash_signal": "paid pilot, strong-intent reply, or manually approved discovery call",
            "approval_boundary": "customer contact remains blocked until human approval",
        },
        "first_possible_buyer": first_cash.get(
            "first_possible_buyer",
            "AI startup founder with urgent strategy/research decision",
        ),
        "first_possible_paid_offer": first_cash.get(
            "first_chargeable_deliverable",
            "Done-for-you governed observation + internal CEO command brief",
        ),
        "estimated_paid_signal": l7_2_summary.get(
            "estimated_time_to_paid_signal",
            "7-14 days for strong-intent signal, 14-30 days for first paid pilot after approved outreach",
        ),
        "minimum_tool_needed": first_cash.get(
            "minimum_missing_tool",
            "approval-ready outreach draft and service delivery workflow generator",
        ),
        "bridge_to_long_term_strategy": "The first service creates proof, language, artifacts, and trust that can later become templates, paid support, and productized agent-governance tooling.",
        "key_caveats": [
            "No outreach is sent in L7.3.",
            "All claims are internal-review-ready, not publication-ready.",
            "Payment and customer commitments require separate human approval.",
            "The first buyer hypothesis is not settled truth until validated.",
        ],
    }


def service_offer_definition() -> dict[str, Any]:
    return {
        **packet("service_offer_definition"),
        "offer_name": "Founder AI Workflow Audit & CEO Command Brief Sprint",
        "target_customer": "AI startup founder with an urgent strategy, research, or AI-workflow decision",
        "urgent_problem": "The founder needs a fast, evidence-backed internal decision brief without accidentally creating unsafe automation, unsupported claims, or unapproved external actions.",
        "service_promise": "In a short sprint, produce a governed AI workflow audit, controlled observation summary, risk/caveat map, and CEO-ready command brief for internal decision-making.",
        "deliverables": [
            "Founder intake summary",
            "Current AI workflow audit",
            "Controlled read-only observation plan",
            "Evidence packet and source-quality summary",
            "Risk/conflict boundary",
            "CEO command brief",
            "Recommended next safe action",
            "What not to automate yet list",
        ],
        "delivery_time_hypothesis": "3-5 business days for a narrow pilot after intake is complete",
        "what_is_included": [
            "Internal workflow analysis",
            "Read-only market/research observation within budget",
            "Evidence-backed decision packet",
            "Governance and approval-boundary recommendations",
        ],
        "what_is_not_included": [
            "Autonomous outreach",
            "Publication",
            "Payment processing",
            "Account creation",
            "Legal/compliance certification",
            "Permanent memory or strategy writeback",
        ],
        "required_customer_inputs": [
            "Urgent decision or workflow question",
            "Current AI tools/workflow",
            "Known constraints and risks",
            "Preferred output format",
            "What must not be automated",
        ],
        "output_format": "Internal PDF/Markdown-style command brief plus structured JSON evidence appendix if needed",
        "evidence_basis": [
            "L6.13-L6.16 governed observation and review artifacts",
            "L7.1 offer hypotheses",
            "L7.2 shortest cash realization path analysis",
        ],
        "caveats": [
            "This is a founder-decision support service, not legal advice.",
            "External claims require human review before use.",
            "Customer-sensitive content must be reviewed before delivery.",
        ],
        "trust_boundary": "Trust comes from transparent evidence, caveats, no-action receipts, and human approval gates rather than autonomous claims.",
        "approval_required_before_external_claims": True,
        "publication_status": "internal_review_ready_not_published",
    }


def target_customer_profile() -> dict[str, Any]:
    return {
        **packet("target_customer_profile"),
        "buyer_persona": "AI startup founder or technical operator making an urgent workflow, strategy, or market decision",
        "pain_points": [
            "Too many AI tools and unclear operating boundary",
            "No evidence-backed decision brief for what to automate next",
            "Fear of unsafe automation, unsupported claims, or accidental external action",
            "Founder time is scarce and decisions need fast synthesis",
        ],
        "buying_triggers": [
            "Preparing investor, customer, or product strategy decisions",
            "Adopting coding agents or AI workflow automation",
            "Needing a fast audit before shipping AI-enabled operations",
            "Wanting an internal command brief without hiring a full consultant team",
        ],
        "urgency_signals": [
            "Mentions AI agent workflow confusion",
            "Needs decision support within days or weeks",
            "Has founder-led operations bottleneck",
            "Uses Codex, Claude Code, OpenClaw-like tools, or agent workflows",
        ],
        "disqualification_criteria": [
            "Requests guaranteed revenue outcomes",
            "Requires legal certification",
            "Requires autonomous outreach or account action before approval",
            "Cannot provide a narrow workflow/decision focus",
        ],
        "approved_read_only_discovery_methods": [
            "public founder posts and company pages",
            "public product docs and changelogs",
            "public job posts describing workflow needs",
            "public funding/RFP pages where no login or form submission is needed",
        ],
        "private_data_policy": "Do not collect private personal data or contact any person in this sprint.",
        "why_they_might_pay": "They need a fast, credible internal decision artifact that reduces uncertainty and founder workload.",
        "trust_barriers": [
            "New service category",
            "No public case studies yet",
            "Need to avoid overclaiming agent autonomy",
            "Need human-reviewed outreach and delivery language",
        ],
        "first_conversation_goal": "Confirm whether the founder has a narrow urgent decision that a governed workflow audit and command brief can help resolve.",
        "approval_required_before_contact": True,
    }


def customer_discovery_criteria() -> dict[str, Any]:
    return {
        **packet("customer_discovery_criteria"),
        "read_only_selection_criteria": [
            "AI workflow urgency is visible in public materials",
            "Founder/operator appears to be adopting AI tooling",
            "Decision can be narrowed to one briefable workflow question",
            "No login, payment, private group, or form submission is required to observe fit",
        ],
        "do_not_collect": [
            "private emails",
            "personal phone numbers",
            "non-public financials",
            "credentials",
            "private community content",
        ],
        "contact_status": "blocked_until_human_approved",
        "owner_burden_reduction": "Future discovery should use a read-only candidate finder, not manual URL collection from the owner.",
    }


def outreach_generator_spec() -> dict[str, Any]:
    return {
        **packet("outreach_generator_spec"),
        "purpose": "Generate draft-only outreach messages for human review; never auto-send.",
        "allowed_claims": [
            "We can prepare an internal AI workflow audit and CEO command brief.",
            "The sprint is designed for read-only observation and evidence-backed decision support.",
            "External actions, publication, and payment are not automated.",
        ],
        "claims_requiring_human_review": [
            "Any claim about customer-specific fit",
            "Any quantified ROI or revenue claim",
            "Any mention of compliance suitability",
            "Any statement that implies endorsement by a third party",
        ],
        "forbidden_claims": [
            "Guaranteed revenue",
            "Guaranteed compliance",
            "Autonomous execution without approval",
            "Access to private systems without explicit permission",
        ],
        "personalization_rules": [
            "Use only public, read-only observations.",
            "Avoid sensitive personal details.",
            "Keep personalization optional and caveated.",
            "Do not pretend a relationship exists.",
        ],
        "tone_rules": [
            "Plainspoken",
            "Founder-to-founder respectful",
            "Low pressure",
            "Specific about the internal deliverable",
            "Clear that the message is a draft pending approval",
        ],
        "evidence_caveat_insertion_rules": [
            "Attach evidence basis as internal notes, not external proof claims.",
            "Include caveats where claims are not yet validated by customers.",
            "Keep customer-specific claims out until reviewed.",
        ],
        "approval_requirements": [
            "Human approval before sending",
            "Human review of recipient",
            "Human review of claims",
            "Post-action receipt after any approved send",
        ],
        "no_auto_send": True,
    }


def outreach_drafts() -> list[dict[str, Any]]:
    common = {
        "offer_reference": "Founder AI Workflow Audit & CEO Command Brief Sprint",
        "evidence_basis": [
            "L7.2 selected shortest cash path path_001",
            "L6/L7 governed observation and command brief artifacts",
        ],
        "caveats": [
            "Draft only; not sent.",
            "Recipient and claims require human review.",
            "No payment request is included.",
        ],
        "claims_requiring_human_review": [
            "Any recipient-specific fit statement",
            "Any expected business result",
        ],
        "forbidden_auto_send": True,
        "human_approval_required": True,
        "external_action_status": "blocked_until_human_approved",
    }
    return [
        {
            **packet("outreach_draft_packet"),
            **common,
            "draft_id": "outreach_draft_001",
            "target_customer_type": "AI startup founder with urgent workflow decision",
            "subject": "Draft: quick AI workflow audit + CEO command brief",
            "body": (
                "Hi [Name],\n\n"
                "I am testing a narrow founder-facing service: a governed AI workflow audit and internal CEO command brief. "
                "The point is to help a founder make one urgent AI workflow or strategy decision with evidence, caveats, and clear no-go boundaries.\n\n"
                "The deliverable would be internal only: what we observed, what looks useful, what is risky, what not to automate yet, and the next safe action. "
                "No external actions are automated.\n\n"
                "If this matches a current decision you are facing, I would like to ask whether a small paid pilot would be useful.\n\n"
                "Best,\n[Owner]"
            ),
            "recommended_use": "primary_first_contact_draft",
        },
        {
            **packet("outreach_draft_packet"),
            **common,
            "draft_id": "outreach_draft_002",
            "target_customer_type": "technical founder adopting coding agents",
            "subject": "Draft: reduce AI-agent workflow risk before scaling",
            "body": (
                "Hi [Name],\n\n"
                "I am building a service for founders who are starting to rely on AI agents or coding-agent workflows but want a clearer decision boundary before scaling them.\n\n"
                "The pilot would produce an internal command brief: workflow bottlenecks, evidence-backed opportunities, approval gates, and what should stay blocked until review. "
                "It is designed as decision support, not autonomous execution.\n\n"
                "Would a focused audit around one current workflow decision be worth discussing if the scope stayed small and review-gated?\n\n"
                "Best,\n[Owner]"
            ),
            "recommended_use": "technical_founder_variant",
        },
        {
            **packet("outreach_draft_packet"),
            **common,
            "draft_id": "followup_draft_001",
            "target_customer_type": "founder who did not reply to first draft",
            "subject": "Draft: follow-up on AI workflow audit idea",
            "body": (
                "Hi [Name],\n\n"
                "Quick follow-up on the AI workflow audit idea. The smallest useful version would focus on one decision: what to automate, what not to automate, and what evidence supports the recommendation.\n\n"
                "If that is not timely, no worries. If it is timely, I can send a short scope for review.\n\n"
                "Best,\n[Owner]"
            ),
            "recommended_use": "manual_followup_only_after_human_approval",
        },
    ]


def approval_request(drafts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        **packet("human_approval_request"),
        "approval_id": "l7_3_outreach_approval_request_001",
        "action_type": "customer_outreach_email",
        "draft_ids": [draft["draft_id"] for draft in drafts],
        "selected_draft_recommendation": "outreach_draft_001",
        "evidence_basis": [
            "L7.2 shortest cash path selected path_001",
            "L7.3 service offer definition",
            "L7.3 target customer profile",
        ],
        "risk_summary": [
            "Cold outreach can create trust risk if claims are too strong.",
            "Recipient selection must be reviewed manually.",
            "No payment request or commitment should be included.",
        ],
        "expected_value": "Validate whether a narrow paid pilot has buyer interest without building a full product first.",
        "exact_action_that_would_be_approved": "Owner may manually send one reviewed outreach draft to one reviewed recipient outside this sprint.",
        "exact_actions_still_forbidden": [
            "automatic send",
            "bulk outreach",
            "payment request",
            "form submission",
            "customer commitment",
            "publication",
            "account creation",
        ],
        "default_decision": "blocked_until_human_approved",
        "approval_options": [
            "approve_one_draft_for_manual_send",
            "revise_draft",
            "reject_current_offer",
            "run_more_read_only_validation",
        ],
        "approval_granted": False,
    }


def execution_preflight() -> dict[str, Any]:
    checks = [
        "human approval exists",
        "recipient manually reviewed",
        "message manually reviewed",
        "claims reviewed",
        "no prohibited claims",
        "no secret exposure",
        "no payment request unless separately approved",
        "no form submission",
        "post-action receipt required",
    ]
    return {
        **packet("execution_preflight"),
        "execution_allowed": False,
        "reason": "human_approval_not_yet_granted",
        "checks": [
            {"check": check, "status": "not_satisfied" if check == "human approval exists" else "pending_manual_review"}
            for check in checks
        ],
        "external_action_status": "blocked_until_human_approved",
        "post_action_receipt_required": True,
    }


def service_delivery_workflow() -> dict[str, Any]:
    steps = [
        ("step_001", "Intake", "Secretary", ["customer intake answers"], ["intake summary"], "Completeness and no private credential request", True),
        ("step_002", "Customer workflow/problem framing", "Operator/COO", ["intake summary"], ["workflow problem frame"], "One narrow decision is identified", False),
        ("step_003", "Controlled external observation", "Researcher", ["work order", "budget"], ["source list", "page-read receipts"], "Read-only and budgeted", False),
        ("step_004", "Internal asset/workflow analysis", "Engineer/CTO", ["workflow problem frame"], ["capability gap notes"], "No direct customer system action", False),
        ("step_005", "Evidence packet generation", "Researcher", ["source text", "claims"], ["evidence packets"], "Snippets are not treated as evidence", False),
        ("step_006", "Risk/conflict review", "Auditor", ["evidence packets"], ["risk and conflict boundary"], "Caveats are explicit", False),
        ("step_007", "CEO command brief generation", "CEO", ["evidence", "risk boundary"], ["CEO command brief"], "Recommendations link to evidence", False),
        ("step_008", "Recommendations", "CEO", ["command brief"], ["next action options"], "No external execution is implied", False),
        ("step_009", "Customer-facing summary draft for review", "Secretary", ["command brief"], ["review-only summary draft"], "Customer-sensitive content reviewed", True),
        ("step_010", "Feedback collection", "Operator/COO", ["approved feedback questions"], ["feedback notes"], "Contact requires approval", True),
        ("step_011", "Post-delivery residual review", "Auditor", ["delivery receipt", "feedback"], ["residual review"], "No unreviewed writeback", False),
    ]
    return {
        **packet("service_delivery_workflow"),
        "workflow_name": "Founder AI Workflow Audit & CEO Command Brief Sprint Delivery",
        "paid_pilot_status": "not_executed_in_l7_3",
        "steps": [
            {
                "step_id": step_id,
                "name": name,
                "owner_agent": owner,
                "inputs": inputs,
                "outputs": outputs,
                "quality_check": quality,
                "approval_required": approval,
                "no_go_boundaries": [
                    "no login",
                    "no payment",
                    "no form submission",
                    "no publication",
                    "no customer commitment without approval",
                    "no core writeback",
                ],
            }
            for step_id, name, owner, inputs, outputs, quality, approval in steps
        ],
    }


def customer_intake_template() -> dict[str, Any]:
    questions = [
        "What stage is your company in?",
        "What urgent decision do you need to make?",
        "What AI workflow or tools are you using today?",
        "What pain point is most expensive or risky right now?",
        "What outcome would make this sprint useful?",
        "What constraints should the audit respect?",
        "Which existing tools must be considered?",
        "What risk concerns do you already have?",
        "What is your decision deadline?",
        "What output format would be most useful?",
        "What do you explicitly not want automated?",
    ]
    return {
        **packet("customer_intake_form_template"),
        "template_only": True,
        "live_form_created": False,
        "questions": [{"question_id": f"q_{index:03d}", "question": question} for index, question in enumerate(questions, 1)],
        "privacy_boundary": "Do not request passwords, secrets, private customer data, or regulated data.",
    }


def governed_observation_template() -> dict[str, Any]:
    return {
        **packet("governed_observation_delivery_template"),
        "template_only": True,
        "customer_observation_executed": False,
        "work_order": {
            "work_order_id": "customer_project_work_order_template",
            "scope": "one narrow workflow or strategy decision",
            "approval_required_before_customer_use": True,
        },
        "query_plan": {
            "max_queries": 8,
            "source_preference": ["official", "documentation", "institutional", "reputable secondary"],
            "no_user_url_required": True,
        },
        "source_policy": {
            "public_read_only": True,
            "block_login_payment_form_private_network": True,
            "no_private_data_collection": True,
        },
        "budget": {
            "max_pages_opened": 8,
            "max_domains": 5,
            "max_crawl_depth": 1,
            "max_external_reads": 12,
        },
        "evidence_packet_schema": [
            "source_url",
            "final_url",
            "source_quality_label",
            "page_read_id",
            "extracted_text_excerpt",
            "bounded_claim",
            "support_status",
            "limitations",
        ],
        "conflict_handling": "State conflict and residual; do not overclaim certainty.",
        "no_side_effect_boundary": "No outreach, form submission, login, payment, publication, or writeback.",
        "report_output": "internal command brief plus evidence appendix",
    }


def ceo_command_brief_template() -> dict[str, Any]:
    sections = [
        "Executive summary",
        "What we observed",
        "Evidence basis",
        "Key risks/conflicts",
        "Decision options",
        "Recommended next action",
        "What not to automate yet",
        "Approval boundaries",
    ]
    return {
        **packet("ceo_command_brief_delivery_template"),
        "template_only": True,
        "sections": [{"section_id": f"section_{index:03d}", "title": title} for index, title in enumerate(sections, 1)],
        "customer_delivery_status": "draft_for_review_only",
        "claim_boundary": "Every recommendation must trace to evidence or be labeled as hypothesis.",
    }


def workflow_audit_template() -> dict[str, Any]:
    dimensions = [
        "current AI workflow",
        "decision bottlenecks",
        "evidence gaps",
        "automation risk",
        "governance gaps",
        "approval gaps",
        "owner/team burden",
        "fastest improvement path",
        "tool recommendations",
    ]
    return {
        **packet("workflow_audit_template"),
        "template_only": True,
        "audit_dimensions": [
            {
                "dimension_id": f"audit_{index:03d}",
                "dimension": dimension,
                "output": "finding, evidence basis, risk, and recommended next safe step",
            }
            for index, dimension in enumerate(dimensions, 1)
        ],
    }


def pricing_hypothesis() -> dict[str, Any]:
    return {
        **packet("pricing_hypothesis"),
        "low_pilot_price_usd": 750,
        "mid_pilot_price_usd": 1500,
        "high_pilot_price_usd": 3000,
        "suggested_first_test_price_usd": 1500,
        "value_rationale": "A founder gets a decision-ready internal brief without hiring a full consulting team or building tooling first.",
        "assumptions": [
            "Buyer has an urgent AI workflow or strategy decision.",
            "A narrow 3-5 business day sprint is valuable.",
            "Trust can be established through transparent evidence and caveats.",
        ],
        "risk": [
            "Price may be too high before proof exists.",
            "Buyer may expect implementation instead of decision support.",
            "Trust barrier may require a lower first pilot price.",
        ],
        "when_to_revise": [
            "After three approved discovery conversations",
            "After one paid pilot or strong rejection pattern",
            "If delivery effort exceeds the 3-5 day hypothesis",
        ],
        "payment_execution_status": "not_allowed_in_this_sprint",
        "human_approval_required_before_quoting_externally": True,
    }


def service_quality_checklist() -> dict[str, Any]:
    checks = [
        "evidence trace exists",
        "no unsupported claims",
        "caveats included",
        "conflict status stated",
        "recommendations linked to evidence",
        "customer-sensitive content reviewed",
        "no external side effects occurred",
        "human review completed before delivery",
    ]
    return {
        **packet("service_quality_checklist"),
        "checks": [{"check_id": f"quality_{index:03d}", "check": check, "required": True} for index, check in enumerate(checks, 1)],
        "delivery_allowed_without_review": False,
    }


def feedback_loop() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    questions = {
        **packet("feedback_questions"),
        "customer_contact_status": "not_contacted",
        "questions": [
            "How severe was the original pain?",
            "Would you pay for this if delivered in 3-5 business days?",
            "What trust concerns would stop you?",
            "Was the deliverable clear?",
            "How urgent is this decision?",
            "What price would feel acceptable for a first sprint?",
            "What objections do you have?",
            "Would you refer another founder?",
            "Would you buy a repeat sprint?",
        ],
    }
    guide = {
        **packet("feedback_interview_guide"),
        "guide_status": "draft_only_requires_approval_before_use",
        "interview_flow": [
            "Confirm consent and time box",
            "Ask about pain severity",
            "Show internal-service concept only if approved",
            "Ask willingness-to-pay questions",
            "Capture objections without making commitments",
        ],
    }
    rubric = {
        **packet("feedback_scoring_rubric"),
        "score_dimensions": [
            "pain_severity",
            "willingness_to_pay",
            "trust_concern_level",
            "deliverable_clarity",
            "urgency",
            "repeat_purchase_potential",
        ],
        "scale": "1 low to 5 high",
        "strong_signal_threshold": "average >= 4 with willingness_to_pay >= 4",
    }
    return questions, guide, rubric


def risk_and_claim_boundary() -> tuple[dict[str, Any], dict[str, Any]]:
    risk_register = {
        **packet("risk_register"),
        "risks": [
            {
                "risk_id": "risk_001",
                "description": "Overclaiming revenue or compliance outcomes",
                "severity": "high",
                "mitigation": "Use internal-review-only language and human claim review.",
            },
            {
                "risk_id": "risk_002",
                "description": "Trust gap before first case study",
                "severity": "medium",
                "mitigation": "Start with small paid pilot and transparent artifacts.",
            },
            {
                "risk_id": "risk_003",
                "description": "Customer-sensitive content exposure",
                "severity": "high",
                "mitigation": "Review customer content before delivery and avoid private credentials.",
            },
        ],
    }
    claim_boundary = {
        **packet("claim_boundary"),
        "can_be_claimed": [
            "The service can produce an internal AI workflow audit and CEO command brief.",
            "The workflow is designed around read-only observation and approval gates.",
            "No outreach or payment is automated in this sprint.",
        ],
        "must_not_be_claimed": [
            "Guaranteed revenue",
            "Guaranteed compliance",
            "Guaranteed customer acquisition",
            "Autonomous safe execution without review",
        ],
        "internal_only": [
            "Pricing hypothesis",
            "Draft outreach",
            "Buyer fit assumptions",
            "Unvalidated willingness-to-pay assumptions",
        ],
        "requires_evidence": [
            "Any claim about customer workflow fit",
            "Any market urgency claim",
            "Any competitor or compliance claim",
        ],
        "requires_customer_proof": [
            "Customer satisfaction",
            "Paid conversion",
            "Repeat purchase",
            "Case study",
        ],
        "overclaiming_risks": ["trust damage", "misleading buyer expectations", "premature publication"],
        "compliance_risks": ["unsupported compliance claims", "handling private data", "unclear consent"],
        "trust_risks": ["new service category", "no public proof yet", "AI automation anxiety"],
    }
    return risk_register, claim_boundary


def memory_writeback_candidates() -> tuple[dict[str, Any], dict[str, Any]]:
    candidates = [
        ("l7_3_writeback_candidate_001", "selected cash path", "Record path_001 as selected L7.3 cash validation path."),
        ("l7_3_writeback_candidate_002", "service offer definition", "Record the Founder AI Workflow Audit & CEO Command Brief Sprint offer definition."),
        ("l7_3_writeback_candidate_003", "pricing hypothesis", "Record low/mid/high and first-test pricing hypothesis."),
        ("l7_3_writeback_candidate_004", "delivery workflow", "Record the 11-step service delivery workflow."),
        ("l7_3_writeback_candidate_005", "outreach approval state", "Record that outreach remains blocked until human approval."),
    ]
    data = {
        **packet("memory_writeback_candidates"),
        "candidates": [
            {
                "candidate_id": candidate_id,
                "source_artifact": source,
                "proposed_update": update,
                "target_layer": "agent working memory / secretary archive candidate",
                "evidence_basis": ["L7.2 money path decision", "L7.3 generated workflow artifacts"],
                "reason": "Prepare future reviewed learning without writing permanent state.",
                "expected_value": "Keeps commercial validation context reusable after approval.",
                "risk_if_wrong": "Could over-prioritize an unvalidated offer if written without review.",
                "required_human_approval": True,
                "default_decision": "blocked_until_human_approved",
                "dry_run_only": True,
            }
            for candidate_id, source, update in candidates
        ],
    }
    receipt = {
        **packet("writeback_no_action_receipt"),
        "actual_writeback_occurred": False,
        "dry_run_only": True,
        "default_decision": "blocked_until_human_approved",
        "targets_not_written": ["memory", "brain", "canonical strategy", "CIEU DB"],
    }
    return data, receipt


def owner_review_packet(
    offer: dict[str, Any],
    profile: dict[str, Any],
    pricing: dict[str, Any],
    drafts: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        **packet("owner_review_packet"),
        "first_offer": offer["offer_name"],
        "who_it_is_for": profile["buyer_persona"],
        "why_they_might_pay": profile["why_they_might_pay"],
        "what_we_deliver": offer["deliverables"],
        "pricing_hypothesis": {
            "low": pricing["low_pilot_price_usd"],
            "mid": pricing["mid_pilot_price_usd"],
            "high": pricing["high_pilot_price_usd"],
            "suggested_first_test": pricing["suggested_first_test_price_usd"],
        },
        "how_we_deliver": "Use the L7.3 service delivery workflow: intake, governed observation, evidence packets, risk review, CEO command brief, and feedback loop.",
        "outreach_drafts_ready": [draft["draft_id"] for draft in drafts],
        "recommended_outreach_draft": "outreach_draft_001",
        "what_owner_needs_to_approve": [
            "whether to use this offer for validation",
            "which draft may be manually sent",
            "which recipient is allowed",
            "whether pricing can be quoted externally",
        ],
        "what_remains_blocked": [
            "auto-send",
            "bulk outreach",
            "payment request",
            "customer commitment",
            "publication",
            "actual memory/brain/canonical/CIEU DB writeback",
        ],
        "what_happens_after_approval": [
            "owner manually sends one approved draft to one approved recipient",
            "post-action receipt is created",
            "feedback is captured",
            "offer and pricing are revised from evidence",
        ],
        "next_one_command_action": "bash scripts/run_l7_3_offer_validation_workflow.sh --mode build",
    }


def no_action_receipt() -> dict[str, Any]:
    return {
        **packet("no_action_receipt"),
        "outreach_occurred": False,
        "email_sent_occurred": False,
        "form_submission_occurred": False,
        "publication_occurred": False,
        "payment_occurred": False,
        "account_creation_occurred": False,
        "customer_contact_occurred": False,
        "grant_rfp_submission_occurred": False,
        "mcp_live_behavior_occurred": False,
        "actual_memory_brain_canonical_cieu_db_writeback_occurred": False,
        "secret_printed_stored_in_repo_occurred": False,
        "y_star_gov_modification_occurred": False,
        "gov_mcp_modification_occurred": False,
        "db_log_wal_shm_active_agent_marker_content_read_occurred": False,
        "ask_user_url_occurred": False,
    }


def write_markdown_artifacts(
    selected: dict[str, Any],
    offer: dict[str, Any],
    profile: dict[str, Any],
    generator: dict[str, Any],
    drafts: list[dict[str, Any]],
    approval: dict[str, Any],
    preflight: dict[str, Any],
    workflow: dict[str, Any],
    intake: dict[str, Any],
    observation_template: dict[str, Any],
    brief_template: dict[str, Any],
    audit_template: dict[str, Any],
    pricing: dict[str, Any],
    quality: dict[str, Any],
    feedback_questions: dict[str, Any],
    feedback_guide: dict[str, Any],
    feedback_rubric: dict[str, Any],
    claim_boundary: dict[str, Any],
    owner_packet: dict[str, Any],
) -> None:
    write_md(
        "selected_cash_path/selected_cash_path.md",
        f"""
# Selected Cash Path

**Path:** {selected['path_id']} - {selected['path_name']}

**Why selected:** {selected['why_selected']}

**First possible buyer:** {selected['first_possible_buyer']}

**First possible paid offer:** {selected['first_possible_paid_offer']}

**Estimated paid signal:** {selected['estimated_paid_signal']}

**Minimum tool needed:** {selected['minimum_tool_needed']}

**Caveats**
{bullets(selected['key_caveats'])}
""",
    )
    write_md(
        "service_offer_definition/service_offer_definition.md",
        f"""
# Service Offer Definition

**Offer:** {offer['offer_name']}

**Target customer:** {offer['target_customer']}

**Urgent problem:** {offer['urgent_problem']}

**Service promise:** {offer['service_promise']}

**Deliverables**
{bullets(offer['deliverables'])}

**Not included**
{bullets(offer['what_is_not_included'])}

This offer is internal-review-ready and has not been published.
""",
    )
    write_md(
        "target_customer_selection/target_customer_profile.md",
        f"""
# Target Customer Profile

**Buyer persona:** {profile['buyer_persona']}

**Why they might pay:** {profile['why_they_might_pay']}

**Pain points**
{bullets(profile['pain_points'])}

**Buying triggers**
{bullets(profile['buying_triggers'])}

**Approval before contact:** yes.
""",
    )
    write_md(
        "approval_ready_outreach_generator/outreach_generator_spec.md",
        f"""
# Approval-Ready Outreach Generator Spec

This spec creates draft-only outreach. It never sends messages.

**Allowed claims**
{bullets(generator['allowed_claims'])}

**Claims requiring human review**
{bullets(generator['claims_requiring_human_review'])}

**Forbidden claims**
{bullets(generator['forbidden_claims'])}

**No auto-send:** {generator['no_auto_send']}
""",
    )
    for draft in drafts:
        write_md(
            f"outreach_draft_packets/{draft['draft_id']}.md",
            f"""
# {draft['draft_id']}

**Subject:** {draft['subject']}

```text
{draft['body']}
```

**Status:** draft only, blocked until human approved.

**Forbidden auto-send:** {draft['forbidden_auto_send']}
""",
        )
    write_md(
        "human_approval_request/l7_3_outreach_approval_request.md",
        f"""
# L7.3 Outreach Approval Request

**Approval ID:** {approval['approval_id']}

**Action type:** {approval['action_type']}

**Recommended draft:** {approval['selected_draft_recommendation']}

**Default decision:** {approval['default_decision']}

**Exact action that would be approved:** {approval['exact_action_that_would_be_approved']}

**Actions still forbidden**
{bullets(approval['exact_actions_still_forbidden'])}
""",
    )
    write_md(
        "execution_preflight/outreach_execution_preflight.md",
        f"""
# Outreach Execution Preflight

**Execution allowed:** {str(preflight['execution_allowed']).lower()}

**Reason:** {preflight['reason']}

This sprint does not execute outreach. Approval, recipient review, claim review, and a post-action receipt are required before any future manual send.
""",
    )
    write_md(
        "service_delivery_workflow/service_delivery_workflow.md",
        "# Service Delivery Workflow\n\n"
        + "\n".join(f"- {step['step_id']}: {step['name']} ({step['owner_agent']})" for step in workflow["steps"])
        + "\n",
    )
    write_md(
        "customer_intake_template/customer_intake_form_template.md",
        "# Customer Intake Template\n\nTemplate only. No live form was created.\n\n"
        + "\n".join(f"- {q['question']}" for q in intake["questions"])
        + "\n",
    )
    write_md(
        "governed_observation_delivery_template/governed_observation_delivery_template.md",
        f"""
# Governed Observation Delivery Template

Template only. No real customer observation occurred.

**Scope:** {observation_template['work_order']['scope']}

**No-side-effect boundary:** {observation_template['no_side_effect_boundary']}
""",
    )
    write_md(
        "ceo_command_brief_delivery_template/ceo_command_brief_delivery_template.md",
        "# CEO Command Brief Delivery Template\n\n"
        + "\n".join(f"- {section['title']}" for section in brief_template["sections"])
        + "\n",
    )
    write_md(
        "workflow_audit_template/workflow_audit_template.md",
        "# Workflow Audit Template\n\n"
        + "\n".join(f"- {dim['dimension']}" for dim in audit_template["audit_dimensions"])
        + "\n",
    )
    write_md(
        "pricing_and_payment_hypothesis/pricing_hypothesis.md",
        f"""
# Pricing And Payment Hypothesis

**Low pilot:** ${pricing['low_pilot_price_usd']}

**Mid pilot:** ${pricing['mid_pilot_price_usd']}

**High pilot:** ${pricing['high_pilot_price_usd']}

**Suggested first test:** ${pricing['suggested_first_test_price_usd']}

**Payment execution status:** {pricing['payment_execution_status']}

Human approval is required before quoting externally.
""",
    )
    write_md(
        "service_quality_checklist/service_quality_checklist.md",
        "# Service Quality Checklist\n\n" + "\n".join(f"- {check['check']}" for check in quality["checks"]) + "\n",
    )
    write_md(
        "customer_feedback_loop/feedback_interview_guide.md",
        "# Feedback Interview Guide\n\nDraft only; customer contact requires approval.\n\n"
        + "\n".join(f"- {step}" for step in feedback_guide["interview_flow"])
        + "\n",
    )
    write_md(
        "risk_and_claim_boundary/claim_boundary.md",
        f"""
# Claim Boundary

**Can be claimed**
{bullets(claim_boundary['can_be_claimed'])}

**Must not be claimed**
{bullets(claim_boundary['must_not_be_claimed'])}

**Internal only**
{bullets(claim_boundary['internal_only'])}
""",
    )
    write_md(
        "owner_review_packet/l7_3_owner_review_packet.md",
        f"""
# L7.3 Owner Review Packet

## What is the first offer?
{owner_packet['first_offer']}

## Who is it for?
{owner_packet['who_it_is_for']}

## Why might they pay?
{owner_packet['why_they_might_pay']}

## What would we deliver?
{bullets(owner_packet['what_we_deliver'])}

## How much might we charge?
Suggested first test: ${owner_packet['pricing_hypothesis']['suggested_first_test']} with low/mid/high hypotheses of ${owner_packet['pricing_hypothesis']['low']}, ${owner_packet['pricing_hypothesis']['mid']}, and ${owner_packet['pricing_hypothesis']['high']}.

## How would we deliver it?
{owner_packet['how_we_deliver']}

## What outreach drafts are ready?
{bullets(owner_packet['outreach_drafts_ready'])}

## What do I need to approve?
{bullets(owner_packet['what_owner_needs_to_approve'])}

## What remains blocked?
{bullets(owner_packet['what_remains_blocked'])}

## What happens after approval?
{bullets(owner_packet['what_happens_after_approval'])}

## Next one-command action
`{owner_packet['next_one_command_action']}`
""",
    )
    write_md(
        "l7_3_summary.md",
        f"""
# L7.3 Summary

**Selected offer:** {offer['offer_name']}

**Target customer:** {profile['buyer_persona']}

**Recommended outreach draft:** outreach_draft_001

**Execution allowed:** false

**Owner review packet:** `l7_approval_ready_offer_validation_workflow/owner_review_packet/l7_3_owner_review_packet.md`

No outreach, email, form submission, publication, payment, account creation, customer contact, or core writeback occurred.
""",
    )


def build() -> dict[str, Any]:
    l7_2_summary = load_json("l7_meta_development_money_path_engine/l7_2_summary.json", {})
    first_cash = load_json("shortest_cash_realization_path/first_cash_step_decision.json", {})

    selected = build_selected_cash_path(l7_2_summary, first_cash)
    offer = service_offer_definition()
    profile = target_customer_profile()
    criteria = customer_discovery_criteria()
    generator = outreach_generator_spec()
    drafts = outreach_drafts()
    approval = approval_request(drafts)
    preflight = execution_preflight()
    workflow = service_delivery_workflow()
    intake = customer_intake_template()
    observation_template = governed_observation_template()
    brief_template = ceo_command_brief_template()
    audit_template = workflow_audit_template()
    pricing = pricing_hypothesis()
    quality = service_quality_checklist()
    feedback_questions, feedback_guide, feedback_rubric = feedback_loop()
    risk_register, claim_boundary = risk_and_claim_boundary()
    writeback_candidates, writeback_receipt = memory_writeback_candidates()
    owner_packet = owner_review_packet(offer, profile, pricing, drafts)
    no_action = no_action_receipt()

    summary = {
        **packet("l7_3_summary"),
        "selected_offer": offer["offer_name"],
        "selected_cash_path": selected["path_id"],
        "target_customer": profile["buyer_persona"],
        "pricing_hypothesis": {
            "low": pricing["low_pilot_price_usd"],
            "mid": pricing["mid_pilot_price_usd"],
            "high": pricing["high_pilot_price_usd"],
            "suggested_first_test": pricing["suggested_first_test_price_usd"],
        },
        "outreach_drafts_generated": len(drafts),
        "recommended_outreach_draft": "outreach_draft_001",
        "human_approval_request_generated": True,
        "execution_preflight_generated": True,
        "execution_allowed": False,
        "service_delivery_workflow_generated": True,
        "customer_intake_template_generated": True,
        "delivery_templates_generated": True,
        "feedback_loop_generated": True,
        "risk_claim_boundary_generated": True,
        "memory_writeback_dry_run_generated": True,
        "owner_review_packet_path": "l7_approval_ready_offer_validation_workflow/owner_review_packet/l7_3_owner_review_packet.md",
        "next_one_command_action": "bash scripts/run_l7_3_offer_validation_workflow.sh --mode build",
        "ask_user_url_occurred": False,
        "external_side_effects_occurred": False,
        "customer_contacted": False,
        "email_sent": False,
        "form_submitted": False,
        "payment_occurred": False,
        "publication_occurred": False,
        "core_writeback_occurred": False,
        "secret_printed_stored_in_repo": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "db_log_wal_shm_active_agent_marker_content_read": False,
    }

    write_json("selected_cash_path/selected_cash_path.json", selected)
    write_json("service_offer_definition/service_offer_definition.json", offer)
    write_json("target_customer_selection/target_customer_profile.json", profile)
    write_json("target_customer_selection/customer_discovery_criteria.json", criteria)
    write_json("approval_ready_outreach_generator/outreach_generator_spec.json", generator)
    for draft in drafts:
        write_json(f"outreach_draft_packets/{draft['draft_id']}.json", draft)
    write_json("human_approval_request/l7_3_outreach_approval_request.json", approval)
    write_json("execution_preflight/outreach_execution_preflight.json", preflight)
    write_json("service_delivery_workflow/service_delivery_workflow.json", workflow)
    write_json("customer_intake_template/customer_intake_form_template.json", intake)
    write_json("governed_observation_delivery_template/governed_observation_delivery_template.json", observation_template)
    write_json("ceo_command_brief_delivery_template/ceo_command_brief_delivery_template.json", brief_template)
    write_json("workflow_audit_template/workflow_audit_template.json", audit_template)
    write_json("pricing_and_payment_hypothesis/pricing_hypothesis.json", pricing)
    write_json("service_quality_checklist/service_quality_checklist.json", quality)
    write_json("customer_feedback_loop/feedback_questions.json", feedback_questions)
    write_json("customer_feedback_loop/feedback_scoring_rubric.json", feedback_rubric)
    write_json("risk_and_claim_boundary/risk_register.json", risk_register)
    write_json("risk_and_claim_boundary/claim_boundary.json", claim_boundary)
    write_json("memory_writeback_dry_run/l7_3_memory_writeback_candidates.json", writeback_candidates)
    write_json("memory_writeback_dry_run/l7_3_writeback_no_action_receipt.json", writeback_receipt)
    write_json("owner_review_packet/l7_3_owner_review_packet.json", owner_packet)
    write_json("l7_3_no_action_receipt/l7_3_no_action_receipt.json", no_action)
    write_json("l7_3_summary.json", summary)

    write_markdown_artifacts(
        selected,
        offer,
        profile,
        generator,
        drafts,
        approval,
        preflight,
        workflow,
        intake,
        observation_template,
        brief_template,
        audit_template,
        pricing,
        quality,
        feedback_questions,
        feedback_guide,
        feedback_rubric,
        claim_boundary,
        owner_packet,
    )
    write_json("customer_feedback_loop/feedback_interview_guide.json", feedback_guide)
    return summary


def main() -> None:
    summary = build()
    print(f"selected_offer: {summary['selected_offer']}")
    print(f"recommended_outreach_draft: {summary['recommended_outreach_draft']}")
    print("approval_request_path: l7_approval_ready_offer_validation_workflow/human_approval_request/l7_3_outreach_approval_request.md")
    print(f"owner_review_packet_path: {summary['owner_review_packet_path']}")
    print(f"execution_allowed: {str(summary['execution_allowed']).lower()}")
    print(f"next_command: {summary['next_one_command_action']}")


if __name__ == "__main__":
    main()
