from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
JOB_ID = "e75_l3_read_only_external_research_owner_decision_packet_finalization_20260507T000001Z"
EXPECTED_BASE = "07759e0e3b9683845aeb9e93e043b8440c6b4063"
EXPECTED_BRANCH = "backflow/aiden-ceo-meeting-room"
OWNER_DECISION_STATUS = "pending_owner_decision"
CURRENT_ROUTE = "governed_business_operations_blueprint_for_agent_teams"
CURRENT_PRODUCT = "Governed Business Operations Blueprint for Agent Teams + CIEU Audit Module"
NEXT_MILESTONE_PENDING = "E76_Await_or_Record_Owner_Decision_for_L3_Read_Only_Research"
FUTURE_APPROVED_E76 = "E76_Owner_Approved_L3_Read_Only_External_Research_Pilot"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_json(rel: str, root: Path | None = None) -> dict[str, Any]:
    try:
        return json.loads(((root or BRIDGE_ROOT) / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(root: Path, rel: str, data: dict[str, Any]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def git_state(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT

    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=base, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    return {
        "branch": run("branch", "--show-current"),
        "head": run("rev-parse", "HEAD"),
        "expected_branch": EXPECTED_BRANCH,
        "expected_head": EXPECTED_BASE,
    }


def base_verified(root: Path | None = None) -> bool:
    state = git_state(root)
    return state["branch"] == EXPECTED_BRANCH and state["head"] == EXPECTED_BASE


def load_required_context(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    return {
        "E73": {
            "responsibility_matrix": load_json("operations/external_validation/e73_ecosystem_responsibility_matrix.json", base),
            "no_new_wheel_policy": load_json("operations/external_validation/e73_no_new_wheel_policy.json", base),
            "readiness_gate": load_json("operations/external_validation/e73_ceo_real_work_readiness_gate.json", base),
            "self_architecture_protocol": load_json("operations/external_validation/e73_ceo_self_architecture_protocol.json", base),
            "owner_closure": load_json("operations/external_validation/e73_owner_readable_closure_report.json", base),
        },
        "E74": {
            "work_cycle_plan": load_json("operations/external_validation/e74_l2_internal_work_cycle_plan.json", base),
            "reuse_map": load_json("operations/external_validation/e74_existing_artifact_reuse_map.json", base),
            "readiness_packet": load_json("operations/external_validation/e74_owner_facing_l3_readiness_packet.json", base),
            "allowlist_proposal": load_json("operations/external_validation/e74_l3_allowlist_proposal_no_execution.json", base),
            "residual": load_json("operations/external_validation/e74_cieu_residual_for_l2_work_cycle.json", base),
            "readback": load_json("operations/external_validation/e74_ceo_l2_work_readback.json", base),
            "next_proposal": load_json("operations/external_validation/e74_generated_next_milestone_proposal.json", base),
            "completion": load_json("operations/external_validation/e74_completion_report.json", base),
        },
        "product": {
            "cieu_audit_module": load_json("products/governed_business_operations_blueprint_for_agent_teams/cieu_audit_module.json", base),
            "updated_offer": load_json("products/governed_business_operations_blueprint_for_agent_teams/updated_offer_blueprint_with_cieu_module.json", base),
        },
    }


def research_questions() -> dict[str, list[str]]:
    return {
        "A_buyer_problem_evidence": [
            "Are there public signs that agent teams, AI automation teams, or founders struggle with governed business operations, action boundaries, auditability, or controlled delegation?",
            "What buyer language appears around this pain: governance, oversight, auditability, operating controls, control rooms, delegated action, or traceability?",
            "Which buyer profiles appear most relevant for a first read-only evidence pass?",
        ],
        "B_product_offer_evidence": [
            "Are there public examples of demand for AI agent governance, audit trails, tool-call oversight, or operational control rooms?",
            "Which adjacent products/services already exist, and what categories do they use?",
            "What gaps remain unserved or confusing enough to support a productized readiness package hypothesis?",
        ],
        "C_CIEU_audit_module_evidence": [
            "Does causal audit or intent-action-outcome traceability appear commercially meaningful in public language?",
            "Is CIEU more buyer-readable as governance evidence, compliance-readiness support, incident review support, or operational assurance?",
            "What proof would be needed before any stronger claim is made?",
        ],
        "D_first_cash_route_evidence": [
            "Is the offer better positioned as a founder/operator diagnostic, agent-team governance blueprint, internal control-room setup, audit-readiness package, or consulting/productized service?",
            "Which positioning appears easiest to explain without compliance or production overclaim?",
        ],
        "E_pricing_packaging_signal": [
            "What public pricing analogs exist for readiness reviews, governance audits, AI observability, control-room setup, or audit-readiness packages?",
            "What package structures are visible in adjacent services?",
            "What pricing claims remain forbidden without direct validation?",
        ],
    }


def source_allowlist() -> list[dict[str, Any]]:
    return [
        {"category_id": "official_agent_framework_docs", "category": "Official docs from AI agent frameworks and tool ecosystems", "allowed_use": "market language and workflow-control context"},
        {"category_id": "ai_governance_observability_security_vendor_pages", "category": "Public product pages from adjacent AI governance, agent observability, security, and audit vendors", "allowed_use": "category and product/offer analogs"},
        {"category_id": "ai_infrastructure_public_blogs", "category": "Public blog posts from AI infrastructure companies", "allowed_use": "buyer/problem and product language"},
        {"category_id": "public_github_repos_issues", "category": "Public GitHub repos and issue discussions where no login is required", "allowed_use": "implementation pain and public behavior proxy only"},
        {"category_id": "public_standards_regulatory_guidance", "category": "Public standards/regulatory guidance pages", "allowed_use": "high-level requirement language; no compliance claim"},
        {"category_id": "public_founder_operator_discussions", "category": "Public founder/operator discussions accessible without login", "allowed_use": "public behavior proxy only; no outreach"},
        {"category_id": "public_job_posts", "category": "Public job posts", "allowed_use": "market demand proxy only; no recruitment/outreach"},
        {"category_id": "public_pricing_pages", "category": "Public pricing pages from adjacent products", "allowed_use": "pricing analog only; no pricing validation claim"},
        {"category_id": "public_conference_talks_transcripts", "category": "Public conference talks/transcripts accessible without login", "allowed_use": "market language and problem framing"},
        {"category_id": "public_vendor_case_studies", "category": "Public case studies from vendors", "allowed_use": "category/problem analog only; no customer validation claim for Y*Bridge"},
    ]


def source_denylist() -> list[str]:
    return [
        "private communities",
        "login-gated pages",
        "paid databases or paid reports",
        "personal social profiles for outreach",
        "customer contact lists",
        "scraped emails, phone numbers, or handles",
        "anything requiring account creation",
        "anything requiring API keys or credentials",
        "anything that triggers posting, messaging, forms, transactions, or terms acceptance on behalf of owner",
    ]


def action_allowlist() -> list[str]:
    return [
        "read public pages",
        "read public documentation",
        "read public market pages",
        "read public competitor/product pages",
        "read public community discussions only if no login is required",
        "record citations and receipts",
        "summarize evidence",
        "map evidence to buyer/problem/product assumptions",
    ]


def action_denylist() -> list[str]:
    return [
        "contacting customers",
        "contacting experts",
        "sending emails or messages",
        "submitting forms",
        "posting comments",
        "joining communities",
        "scraping behind login",
        "accepting terms on behalf of owner",
        "payment actions",
        "creating accounts",
        "API calls requiring credentials",
        "publication",
        "advertising",
        "claiming customer validation",
        "claiming paid signal",
        "claiming compliance/legal proof",
        "claiming production readiness",
    ]


def forbidden_claims_after_future_l3() -> list[str]:
    return [
        "customer validation",
        "expert validation",
        "paid signal",
        "pricing validation",
        "legal compliance",
        "regulatory certification",
        "production deployment",
        "live audit ledger",
        "live provider execution",
        "L4 external action readiness",
        "L5 revenue readiness",
    ]


def allowed_claims_after_future_l3() -> list[str]:
    return [
        "public-read evidence collected",
        "non-contact market signal",
        "public proxy evidence",
        "source-backed hypothesis refinement",
        "readiness or non-readiness for next owner decision",
    ]


def receipt_schema() -> dict[str, Any]:
    fields = {
        "source_id": "stable internal id for the source",
        "source_title": "public source title",
        "source_url_or_locator": "URL or public locator; no private locator",
        "source_category": "must match owner-approved allowlist category",
        "access_mode": "public_read_only",
        "access_time": "UTC timestamp for future E76 read",
        "public_read_only_confirmed": "boolean",
        "login_required": "boolean, must be false unless owner explicitly approves a special case",
        "interaction_required": "boolean, must be false",
        "evidence_type": "market_language, category_presence, pricing_analog, demand_proxy, behavior_proxy, or exclusion",
        "relevant_claims_supported": "bounded list of supported hypotheses",
        "quote_or_summary_boundary": "short quote or summary limit, copyright-safe",
        "risk_flags": "overclaim, login, contact, paywall, privacy, relevance, or none",
        "allowed_by_owner_scope": "boolean",
        "included_in_synthesis": "boolean",
        "exclusion_reason": "required if excluded",
    }
    return {
        "artifact_id": "e75_l3_evidence_receipt_schema",
        "bridge_job_id": JOB_ID,
        "schema_status": "template_only_no_execution",
        "fields": fields,
        "sample_placeholder_receipt": {
            "source_id": "TEMPLATE_ONLY_DO_NOT_TREAT_AS_SOURCE",
            "source_title": "Placeholder only",
            "source_url_or_locator": "not_applicable_E75_no_browsing",
            "source_category": "placeholder",
            "access_mode": "not_accessed",
            "access_time": None,
            "public_read_only_confirmed": False,
            "login_required": None,
            "interaction_required": None,
            "evidence_type": "template_only",
            "relevant_claims_supported": [],
            "quote_or_summary_boundary": "no quote collected in E75",
            "risk_flags": ["template_only"],
            "allowed_by_owner_scope": False,
            "included_in_synthesis": False,
            "exclusion_reason": "E75 does not execute external research",
        },
        "real_receipts_generated_in_E75": False,
        "external_action_allowed": False,
    }


def build_source_allowlist_and_denylist(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e75_l3_source_allowlist_and_denylist",
        "bridge_job_id": JOB_ID,
        "allowlist_status": "proposed_for_owner_approval_not_executed",
        "allowed_source_categories": source_allowlist(),
        "denylisted_source_categories": source_denylist(),
        "allowed_future_L3_actions": action_allowlist(),
        "denied_future_L3_actions": action_denylist(),
        "even_if_E76_is_later_approved_E76_remains_read_only_non_contact": True,
        "owner_approval_required_before_use": True,
        "external_action_allowed": False,
    }


def build_owner_approval_form(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e75_l3_owner_approval_form",
        "bridge_job_id": JOB_ID,
        "approval_status": OWNER_DECISION_STATUS,
        "decision_options": [
            {
                "option_id": "APPROVE_L3_READ_ONLY_RESEARCH_PILOT",
                "meaning": "Owner approves a future E76 read-only research pilot within the exact boundaries of this packet.",
                "selected": False,
            },
            {
                "option_id": "APPROVE_WITH_SCOPE_REDUCTION",
                "meaning": "Owner approves only a narrower source set, smaller question set, or smaller evidence budget.",
                "selected": False,
            },
            {
                "option_id": "REQUEST_MORE_L2_INTERNAL_WORK",
                "meaning": "Owner does not approve external research yet and requests more internal packaging, pricing, buyer hypothesis, or source planning.",
                "selected": False,
            },
            {
                "option_id": "REJECT_L3_FOR_NOW",
                "meaning": "Owner declines L3 and keeps CEO at L2 only.",
                "selected": False,
            },
        ],
        "empty_owner_fields": {
            "owner_selected_option": None,
            "approved_source_categories": [],
            "approved_research_questions": [],
            "approved_source_count_cap": None,
            "approved_timebox": None,
            "approval_notes": None,
            "approved_by": None,
            "approval_timestamp": None,
        },
        "approval_granted": False,
        "external_action_allowed": False,
    }


def build_l3_owner_decision_packet(root: Path | None = None) -> dict[str, Any]:
    context = load_required_context(root)
    e74_packet = context["E74"]["readiness_packet"]
    e74_allowlist = context["E74"]["allowlist_proposal"]
    return {
        "artifact_id": "e75_l3_owner_decision_packet",
        "bridge_job_id": JOB_ID,
        "title": "L3 Controlled Read-Only External Research Owner Decision Packet",
        "packet_status": "owner_decision_ready_no_execution",
        "approval_status": OWNER_DECISION_STATUS,
        "decision_requested_from_owner": "Choose approve, approve-with-scope-reduction, request more L2 internal work, or reject L3 for now.",
        "current_selected_route": CURRENT_ROUTE,
        "current_product_context": CURRENT_PRODUCT,
        "what_E74_already_answered": [
            "L2 internal autonomous work is operational.",
            "The owner-facing L3 readiness packet exists.",
            "L3 should remain read-only and non-contact.",
            "L4 and L5 are not ready.",
            "The next step should be owner decision preparation rather than more construction.",
        ],
        "why_L3_research_is_now_appropriate": [
            "E73 adjudicated L2 ready and L3 conditionally ready.",
            "E74 produced a concrete internal packet and source-category plan.",
            "The selected offer now has enough internal framing to test public market language without contact.",
            "The main missing evidence is external public-read evidence, not another internal runtime mechanism.",
        ],
        "what_L3_is_supposed_to_learn": [
            "which buyer/problem language is most public and understandable",
            "which adjacent categories and products already exist",
            "whether CIEU audit-module framing is commercially meaningful",
            "which first-cash packaging path is easiest to explain",
            "what pricing/package analogs are visible publicly without claiming pricing validation",
        ],
        "research_questions": research_questions(),
        "source_category_allowlist": source_allowlist(),
        "source_category_denylist": source_denylist(),
        "action_allowlist": action_allowlist(),
        "action_denylist": action_denylist(),
        "maximum_scope_and_budget": {
            "maximum_source_pages": 30,
            "recommended_source_pages": "20-30",
            "maximum_source_categories": 6,
            "maximum_search_themes": 5,
            "maximum_run_duration": "one controlled milestone",
            "receipts_required_for_every_source": True,
            "public_read_only": True,
            "abort_if_source_requires_login_payment_account_creation_or_interactive_action": True,
            "abort_if_source_category_drifts_beyond_owner_approved_allowlist": True,
        },
        "evidence_receipt_requirements": list(receipt_schema()["fields"].keys()),
        "no_overclaim_controls": {
            "forbidden_after_future_L3": forbidden_claims_after_future_l3(),
            "allowed_after_future_L3": allowed_claims_after_future_l3(),
            "public_evidence_is_not_customer_validation": True,
            "pricing_analogs_are_not_pricing_validation": True,
            "regulatory_public_pages_are_not_compliance_proof": True,
        },
        "abort_conditions": e74_allowlist.get("abort_conditions", [
            "source requires login/payment/account creation/interactive action",
            "research drifts toward contact or publication",
            "no-overclaim checks fail",
        ]),
        "post_run_evaluation_criteria": [
            "Were at least three source categories covered within owner-approved scope?",
            "Did public evidence strengthen, weaken, or redirect the buyer/problem hypothesis?",
            "Did public evidence clarify CIEU module language without creating compliance overclaim risk?",
            "Did pricing/package analogs inform package shape without claiming validation?",
            "Does the evidence support another owner decision, a narrowed L3 refresh, or return to L2 packaging?",
        ],
        "future_CIEU_residual_template": {
            "X_t": "owner-approved E76 L3 public-read-only research context",
            "U_t": "read approved public sources and record receipts",
            "Y_star_t": "source-backed hypothesis refinement without contact or overclaim",
            "Y_t_plus_1": "evidence receipts, synthesis, route implication, no-overclaim result",
            "R_t_plus_1": "remaining gaps and next owner decision",
        },
        "L4_L5_non_readiness_reminder": {
            "L4_external_action_ready": False,
            "L5_revenue_work_ready": False,
            "reason": "No owner-approved outbound action, customer validation, paid signal, pricing validation, legal/compliance review, or customer pipeline controls exist yet.",
        },
        "owner_decision_options": build_owner_approval_form(root)["decision_options"],
        "E76_execution_prompt_draft_status": "disabled_unless_owner_approval_explicitly_granted",
        "references_to_E74": {
            "E74_packet_status": e74_packet.get("packet_status"),
            "E74_completion_status": context["E74"]["completion"].get("final_status"),
            "E74_next_milestone": context["E74"]["next_proposal"].get("selected_next_milestone"),
        },
        "external_action_allowed": False,
        "L3_executed": False,
        "owner_approval_granted": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "live_ledger_claimed": False,
        "L4_ready_claimed": False,
        "L5_ready_claimed": False,
    }


def build_future_e76_disabled_prompt(root: Path | None = None) -> dict[str, Any]:
    packet = build_l3_owner_decision_packet(root)
    return {
        "artifact_id": "e75_future_E76_disabled_execution_prompt_draft",
        "bridge_job_id": JOB_ID,
        "proposed_future_milestone": FUTURE_APPROVED_E76,
        "draft_status": "disabled_pending_explicit_owner_approval",
        "execution_disabled": True,
        "owner_approval_required": True,
        "owner_approval_granted": False,
        "expected_base_placeholder": "<fill with current bridge-labs HEAD after E75>",
        "owner_approval_field_required": {
            "owner_selected_option": "APPROVE_L3_READ_ONLY_RESEARCH_PILOT or APPROVE_WITH_SCOPE_REDUCTION",
            "approved_source_categories": "required non-empty subset of E75 allowlist",
            "approved_source_count_cap": "required",
            "approved_timebox": "required",
            "approval_timestamp": "required",
        },
        "inherited_allowlist": packet["source_category_allowlist"],
        "no_contact_boundary": action_denylist(),
        "public_read_only_research_instructions": [
            "Only read owner-approved public source categories.",
            "Do not log in, submit forms, post, message, pay, call private APIs, or collect contact data.",
            "Create one receipt per source.",
            "Synthesize public evidence as proxy evidence only.",
        ],
        "receipt_schema": receipt_schema()["fields"],
        "synthesis_requirements": [
            "answer approved research questions",
            "score evidence quality and limitations",
            "map findings to buyer/problem/product assumptions",
            "state whether evidence strengthens, weakens, or redirects the current route",
            "recommend next owner decision",
        ],
        "no_overclaim_controls": {
            "forbidden_after_future_L3": forbidden_claims_after_future_l3(),
            "allowed_after_future_L3": allowed_claims_after_future_l3(),
        },
        "stop_abort_conditions": packet["abort_conditions"],
        "output_artifacts": [
            "E76 source receipt log",
            "E76 evidence atom map",
            "E76 synthesis report",
            "E76 route implication scorecard",
            "E76 no-overclaim validation",
            "E76 CIEU residual",
            "E76 owner decision packet",
        ],
        "tests_or_checks": [
            "all sources are owner-approved public-read only",
            "no login/contact/payment/publication occurred",
            "receipt schema complete",
            "forbidden claims absent",
            "L4/L5 not falsely marked ready",
        ],
        "external_action_allowed_in_E75": False,
    }


def build_cieu_residual(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e75_cieu_residual_for_owner_decision_packet",
        "bridge_job_id": JOB_ID,
        "X_t": {
            "context": "E74 completed L2 internal work; L3 is ready for owner decision finalization, not execution.",
            "boundary": "no external action, no browsing, no contact, no approval fabrication, bridge-labs-only artifacts.",
        },
        "U_t": {
            "action": "Finalize owner decision packet for future L3 controlled read-only external research.",
            "execution_status": "internal_decision_preparation_only",
        },
        "Y_star_t": {
            "intended_outcome": "Owner receives a complete approve/reject/narrow/request-more-internal-work packet.",
            "constraints": [
                "no external action",
                "no approval fabrication",
                "no overclaim",
                "no duplicate K9/Y-star-gov/gov-mcp core mechanism",
            ],
        },
        "Y_t_plus_1": {
            "actual_outputs": [
                "final decision packet",
                "owner approval form",
                "source allowlist and denylist",
                "action allowlist and denylist",
                "evidence receipt schema",
                "disabled future E76 prompt draft",
                "CEO readback",
            ],
            "L3_executed": False,
        },
        "R_t_plus_1": {
            "residuals": [
                "owner approval still pending",
                "L3 not executed",
                "no external evidence collected yet",
                "L4/L5 not ready",
                "pricing/customer/paid/compliance evidence absent",
            ],
            "next_U": NEXT_MILESTONE_PENDING,
        },
        "external_action_allowed": False,
        "no_overclaim": True,
    }


def build_generated_next_milestone_proposal(root: Path | None = None) -> dict[str, Any]:
    approval = build_owner_approval_form(root)
    return {
        "artifact_id": "e75_generated_next_milestone_proposal",
        "bridge_job_id": JOB_ID,
        "owner_decision_status": approval["approval_status"],
        "selected_next_milestone": NEXT_MILESTONE_PENDING,
        "decision_state_routing": {
            "pending_owner_decision": NEXT_MILESTONE_PENDING,
            "APPROVE_L3_READ_ONLY_RESEARCH_PILOT": FUTURE_APPROVED_E76,
            "APPROVE_WITH_SCOPE_REDUCTION": "E76_L3_Read_Only_Research_Scope_Narrowing_R1",
            "REQUEST_MORE_L2_INTERNAL_WORK": "E76_Return_to_L2_Internal_Work_or_Commercial_Packaging",
            "REJECT_L3_FOR_NOW": "E76_Return_to_L2_Internal_Work_or_Commercial_Packaging",
        },
        "why_selected": "Owner approval remains pending, so the next milestone must await or record owner decision rather than executing L3.",
        "next_step_is_decision_not_construction": True,
        "external_action_allowed": False,
    }


def build_ceo_readback(root: Path | None = None) -> dict[str, Any]:
    packet = build_l3_owner_decision_packet(root)
    allowlist = build_source_allowlist_and_denylist(root)
    proposal = build_generated_next_milestone_proposal(root)
    return {
        "artifact_id": "e75_ceo_readback",
        "bridge_job_id": JOB_ID,
        "E75_status": "owner_decision_packet_finalized_no_execution",
        "what_E75_produced": packet["title"],
        "L3_executed": False,
        "owner_approved_L3": False,
        "owner_approval_status": OWNER_DECISION_STATUS,
        "proposed_source_categories": [row["category"] for row in allowlist["allowed_source_categories"]],
        "forbidden_actions": allowlist["denied_future_L3_actions"],
        "decision_requested_from_owner": packet["decision_requested_from_owner"],
        "if_owner_approves": FUTURE_APPROVED_E76,
        "if_owner_rejects_or_narrows": {
            "APPROVE_WITH_SCOPE_REDUCTION": "E76_L3_Read_Only_Research_Scope_Narrowing_R1",
            "REQUEST_MORE_L2_INTERNAL_WORK": "E76_Return_to_L2_Internal_Work_or_Commercial_Packaging",
            "REJECT_L3_FOR_NOW": "E76_Return_to_L2_Internal_Work_or_Commercial_Packaging",
        },
        "L2_ready": True,
        "L3_ready_for_owner_decision_not_executed": True,
        "L4_ready": False,
        "L5_ready": False,
        "next_recommended_milestone": proposal["selected_next_milestone"],
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "live_ledger_claimed": False,
    }


def build_completion_report(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    packet = load_json("operations/external_validation/e75_l3_owner_decision_packet.json", base)
    allowlist = load_json("operations/external_validation/e75_l3_source_allowlist_and_denylist.json", base)
    schema = load_json("operations/external_validation/e75_l3_evidence_receipt_schema.json", base)
    approval = load_json("operations/external_validation/e75_l3_owner_approval_form.json", base)
    disabled = load_json("operations/external_validation/e75_future_E76_disabled_execution_prompt_draft.json", base)
    residual = load_json("operations/external_validation/e75_cieu_residual_for_owner_decision_packet.json", base)
    readback = load_json("operations/external_validation/e75_ceo_readback.json", base)
    proposal = load_json("operations/external_validation/e75_generated_next_milestone_proposal.json", base)
    checks = {
        "base_verified": base_verified(base),
        "final_owner_packet_exists": packet.get("packet_status") == "owner_decision_ready_no_execution",
        "approval_pending": approval.get("approval_status") == OWNER_DECISION_STATUS and approval.get("approval_granted") is False,
        "allowlist_and_denylist_exist": bool(allowlist.get("allowed_source_categories")) and bool(allowlist.get("denylisted_source_categories")),
        "evidence_receipt_schema_exists": bool(schema.get("fields")) and schema.get("real_receipts_generated_in_E75") is False,
        "disabled_E76_prompt_exists": disabled.get("execution_disabled") is True and disabled.get("owner_approval_granted") is False,
        "CIEU_residual_complete": all(key in residual for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]),
        "CEO_readback_exists": readback.get("E75_status") == "owner_decision_packet_finalized_no_execution",
        "next_milestone_depends_on_owner_decision": proposal.get("owner_decision_status") == OWNER_DECISION_STATUS and proposal.get("selected_next_milestone") == NEXT_MILESTONE_PENDING,
        "no_L3_execution": packet.get("L3_executed") is False and readback.get("L3_executed") is False,
        "no_forbidden_claims": all(packet.get(key) is False for key in [
            "external_action_allowed",
            "customer_validation_claimed",
            "paid_signal_claimed",
            "pricing_validation_claimed",
            "compliance_legal_claimed",
            "production_deployment_claimed",
            "live_ledger_claimed",
            "L4_ready_claimed",
            "L5_ready_claimed",
        ]),
    }
    return {
        "artifact_id": "e75_completion_report",
        "bridge_job_id": JOB_ID,
        "base": git_state(base),
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": "e75_l3_owner_decision_packet_finalized_no_execution" if all(checks.values()) else "e75_partial_with_internal_blocker",
        "what_E75_finalized": "L3 controlled read-only external research owner decision packet.",
        "L3_executed": False,
        "owner_approval_status": OWNER_DECISION_STATUS,
        "evidence_receipt_schema_status": schema.get("schema_status"),
        "disabled_E76_prompt_status": disabled.get("draft_status"),
        "L2_ready": True,
        "L3_ready_for_owner_decision_not_executed": True,
        "L4_ready": False,
        "L5_ready": False,
        "next_recommended_milestone": NEXT_MILESTONE_PENDING,
        "next_step_type": "owner_decision_not_construction",
        "external_action_allowed": False,
        "read_only_repos_mutated": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "live_ledger_claimed": False,
        "duplicate_K9_Y_star_gov_gov_mcp_core_implementation": False,
    }


def _lines_decision_packet(packet: dict[str, Any]) -> list[str]:
    lines = [
        f"- Status: {packet['packet_status']}",
        f"- Approval status: {packet['approval_status']}",
        f"- Current route: `{packet['current_selected_route']}`",
        f"- Current product context: {packet['current_product_context']}",
        "",
        "## Decision Requested",
        packet["decision_requested_from_owner"],
        "",
        "## Why L3 Is Appropriate Now",
        *[f"- {item}" for item in packet["why_L3_research_is_now_appropriate"]],
        "",
        "## What L3 Should Learn",
        *[f"- {item}" for item in packet["what_L3_is_supposed_to_learn"]],
        "",
        "## Research Questions",
    ]
    for group, questions in packet["research_questions"].items():
        lines.append(f"### {group}")
        lines.extend(f"- {question}" for question in questions)
    lines.extend([
        "",
        "## Owner Decision Options",
        *[f"- {row['option_id']}: {row['meaning']}" for row in packet["owner_decision_options"]],
        "",
        "## No-Overclaim Controls",
        "- Forbidden after future L3: " + ", ".join(packet["no_overclaim_controls"]["forbidden_after_future_L3"]),
        "- Allowed after future L3: " + ", ".join(packet["no_overclaim_controls"]["allowed_after_future_L3"]),
        "",
        "## L4/L5 Reminder",
        f"- L4 ready: {packet['L4_L5_non_readiness_reminder']['L4_external_action_ready']}",
        f"- L5 ready: {packet['L4_L5_non_readiness_reminder']['L5_revenue_work_ready']}",
    ])
    return lines


def _lines_allowlist(data: dict[str, Any]) -> list[str]:
    return [
        f"- Status: {data['allowlist_status']}",
        "",
        "## Allowed Source Categories",
        *[f"- {row['category_id']}: {row['category']}" for row in data["allowed_source_categories"]],
        "",
        "## Denylisted Source Categories",
        *[f"- {item}" for item in data["denylisted_source_categories"]],
        "",
        "## Allowed Future L3 Actions",
        *[f"- {item}" for item in data["allowed_future_L3_actions"]],
        "",
        "## Denied Future L3 Actions",
        *[f"- {item}" for item in data["denied_future_L3_actions"]],
    ]


def _lines_schema(data: dict[str, Any]) -> list[str]:
    return [
        f"- Status: {data['schema_status']}",
        "- Real receipts generated in E75: false",
        "",
        "## Fields",
        *[f"- `{key}`: {value}" for key, value in data["fields"].items()],
    ]


def _lines_form(data: dict[str, Any]) -> list[str]:
    return [
        f"- Approval status: {data['approval_status']}",
        f"- Approval granted: {data['approval_granted']}",
        "",
        "## Options",
        *[f"- {row['option_id']}: {row['meaning']}" for row in data["decision_options"]],
        "",
        "## Empty Owner Fields",
        *[f"- `{key}`: {value}" for key, value in data["empty_owner_fields"].items()],
    ]


def _lines_e76(data: dict[str, Any]) -> list[str]:
    return [
        f"- Future milestone: {data['proposed_future_milestone']}",
        f"- Draft status: {data['draft_status']}",
        f"- Execution disabled: {data['execution_disabled']}",
        f"- Owner approval granted: {data['owner_approval_granted']}",
        "",
        "## Public-Read Instructions",
        *[f"- {item}" for item in data["public_read_only_research_instructions"]],
        "",
        "## Stop Conditions",
        *[f"- {item}" for item in data["stop_abort_conditions"]],
        "",
        "## Output Artifacts",
        *[f"- {item}" for item in data["output_artifacts"]],
    ]


def _lines_residual(data: dict[str, Any]) -> list[str]:
    return [
        "## X_t",
        json.dumps(data["X_t"], indent=2, ensure_ascii=False),
        "",
        "## U_t",
        json.dumps(data["U_t"], indent=2, ensure_ascii=False),
        "",
        "## Y_star_t",
        json.dumps(data["Y_star_t"], indent=2, ensure_ascii=False),
        "",
        "## Y_t_plus_1",
        json.dumps(data["Y_t_plus_1"], indent=2, ensure_ascii=False),
        "",
        "## R_t_plus_1",
        json.dumps(data["R_t_plus_1"], indent=2, ensure_ascii=False),
    ]


def _lines_readback(data: dict[str, Any]) -> list[str]:
    return [
        f"- E75 status: {data['E75_status']}",
        f"- Produced: {data['what_E75_produced']}",
        f"- L3 executed: {data['L3_executed']}",
        f"- Owner approved L3: {data['owner_approved_L3']}",
        f"- Owner approval status: {data['owner_approval_status']}",
        f"- Decision requested: {data['decision_requested_from_owner']}",
        f"- If owner approves: {data['if_owner_approves']}",
        f"- L4 ready: {data['L4_ready']}",
        f"- L5 ready: {data['L5_ready']}",
        f"- Next milestone: {data['next_recommended_milestone']}",
    ]


def _lines_completion(data: dict[str, Any]) -> list[str]:
    return [
        f"- Final status: {data['final_status']}",
        f"- Gate passed: {data['gate_passed']}",
        f"- Finalized: {data['what_E75_finalized']}",
        f"- L3 executed: {data['L3_executed']}",
        f"- Owner approval status: {data['owner_approval_status']}",
        f"- Evidence receipt schema: {data['evidence_receipt_schema_status']}",
        f"- Disabled E76 prompt: {data['disabled_E76_prompt_status']}",
        f"- L2 ready: {data['L2_ready']}",
        f"- L3 ready for owner decision, not executed: {data['L3_ready_for_owner_decision_not_executed']}",
        f"- L4 ready: {data['L4_ready']}",
        f"- L5 ready: {data['L5_ready']}",
        f"- Next milestone: {data['next_recommended_milestone']}",
        f"- Next step type: {data['next_step_type']}",
        "- Safety: no external action, no approval fabrication, no forbidden validation/paid/compliance/production/live-ledger claims.",
    ]


def write_all_e75_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    packet = build_l3_owner_decision_packet(base)
    allowlist = build_source_allowlist_and_denylist(base)
    schema = receipt_schema()
    form = build_owner_approval_form(base)
    e76 = build_future_e76_disabled_prompt(base)
    residual = build_cieu_residual(base)
    readback = build_ceo_readback(base)
    proposal = build_generated_next_milestone_proposal(base)

    write_json(base, "operations/external_validation/e75_l3_owner_decision_packet.json", packet)
    write_md(base, "operations/external_validation/e75_l3_owner_decision_packet.md", "L3 Controlled Read-Only External Research Owner Decision Packet", _lines_decision_packet(packet))
    write_json(base, "operations/external_validation/e75_l3_source_allowlist_and_denylist.json", allowlist)
    write_md(base, "operations/external_validation/e75_l3_source_allowlist_and_denylist.md", "E75 L3 Source Allowlist And Denylist", _lines_allowlist(allowlist))
    write_json(base, "operations/external_validation/e75_l3_evidence_receipt_schema.json", schema)
    write_md(base, "operations/external_validation/e75_l3_evidence_receipt_schema.md", "E75 L3 Evidence Receipt Schema", _lines_schema(schema))
    write_json(base, "operations/external_validation/e75_l3_owner_approval_form.json", form)
    write_md(base, "operations/external_validation/e75_l3_owner_approval_form.md", "E75 L3 Owner Approval Form", _lines_form(form))
    write_json(base, "operations/external_validation/e75_future_E76_disabled_execution_prompt_draft.json", e76)
    write_md(base, "operations/external_validation/e75_future_E76_disabled_execution_prompt_draft.md", "E75 Future E76 Disabled Execution Prompt Draft", _lines_e76(e76))
    write_json(base, "operations/external_validation/e75_cieu_residual_for_owner_decision_packet.json", residual)
    write_md(base, "operations/external_validation/e75_cieu_residual_for_owner_decision_packet.md", "E75 CIEU Residual For Owner Decision Packet", _lines_residual(residual))
    write_json(base, "operations/external_validation/e75_ceo_readback.json", readback)
    write_md(base, "operations/external_validation/e75_ceo_readback.md", "E75 CEO Readback", _lines_readback(readback))
    write_json(base, "operations/external_validation/e75_generated_next_milestone_proposal.json", proposal)
    report = build_completion_report(base)
    write_json(base, "operations/external_validation/e75_completion_report.json", report)
    write_md(base, "operations/external_validation/e75_completion_report.md", "E75 Completion Report", _lines_completion(report))
    return report


if __name__ == "__main__":
    print(json.dumps(write_all_e75_artifacts(), indent=2, ensure_ascii=False))
