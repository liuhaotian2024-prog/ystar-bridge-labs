from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from .action_authorization_router import ActionAuthorizationRequest, authorize_external_action
from .e13_evidence_records import E13_OPPORTUNITY_PATHS


ALLOWED_SOURCE_CLASSES = [
    "public_web_page",
    "public_docs",
    "public_pricing_page",
    "public_blog_post",
    "public_github_page",
    "public_forum_or_community",
    "public_marketplace_or_agency_page",
]


E13_FORBIDDEN_ACTIONS = [
    "customer_contact",
    "email_or_message",
    "publication",
    "payment",
    "account_creation",
    "form_submission",
    "login",
    "private_data_collection",
    "personal_contact_scraping",
    "high_volume_crawling",
    "secret_reading",
    "core_brain_cieu_memory_writeback",
    "obligation_auto_registration",
]


COUNTERFACTUAL_QUESTIONS = [
    "What if buyer pain is real but not budgeted?",
    "What if buyers want implementation instead of diagnostic?",
    "What if AI consultants are better channel partners than direct buyers?",
    "What if coding-agent governance is more urgent than AI Ops operating room?",
    "What if trust gap blocks paid conversion?",
    "What if the first cash path should be smaller/manual?",
    "What if content/publication beats direct outreach?",
    "What if no path has enough evidence?",
]


@dataclass(frozen=True)
class E13EvidenceMissionRequest:
    request_id: str
    mission_id: str
    entry_repository_delivery_rt1: int
    top_offer: str
    default_path: str
    opportunity_paths: List[str]
    allowed_source_classes: List[str]
    source_urls: List[Dict[str, Any]]
    budget: Dict[str, int]
    forbidden_actions: List[str]
    counterfactual_questions: List[str]
    run_public_collection_if_sources_available: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_default_e13_request(source_urls: List[Dict[str, Any]] | None = None) -> E13EvidenceMissionRequest:
    return E13EvidenceMissionRequest(
        request_id="e13_tier1_live_read_only_evidence_mission",
        mission_id="E13_tier1_host_side_live_read_only_evidence_mission",
        entry_repository_delivery_rt1=0,
        top_offer="48h AI Ops Operating Room Blueprint",
        default_path="Agent Workflow Bottleneck Diagnosis",
        opportunity_paths=E13_OPPORTUNITY_PATHS,
        allowed_source_classes=ALLOWED_SOURCE_CLASSES,
        source_urls=source_urls or [],
        budget={"max_sources": 30, "max_bytes_per_source": 120000, "max_runtime_seconds": 300},
        forbidden_actions=E13_FORBIDDEN_ACTIONS,
        counterfactual_questions=COUNTERFACTUAL_QUESTIONS,
        run_public_collection_if_sources_available=True,
    )


def validate_e13_request(request: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if request.get("entry_repository_delivery_rt1") != 0:
        errors.append("e13_entry_requires_e12t_repository_delivery_rt1_zero")
    if len(request.get("opportunity_paths", [])) < 7:
        errors.append("must_compare_at_least_seven_opportunity_paths")
    for path in E13_OPPORTUNITY_PATHS:
        if path not in request.get("opportunity_paths", []):
            errors.append(f"missing_opportunity_path: {path}")
    source_classes = set(request.get("allowed_source_classes", []))
    unknown = source_classes - set(ALLOWED_SOURCE_CLASSES)
    if unknown:
        errors.append("unknown_source_class: " + ",".join(sorted(unknown)))
    forbidden = set(request.get("forbidden_actions", []))
    for action in E13_FORBIDDEN_ACTIONS:
        if action not in forbidden:
            errors.append(f"missing_forbidden_action: {action}")
    budget = request.get("budget", {})
    if int(budget.get("max_sources", 0)) > 50:
        errors.append("max_sources_exceeds_tier1_budget")
    return list(dict.fromkeys(errors))


def e13_blocks_external_side_effects() -> bool:
    request = ActionAuthorizationRequest(
        action_id="e13_forbidden_external_action_probe",
        action_type="send_validation_message",
        risk_tier="Tier 2",
        target_lifecycle_state="discovered_candidate",
        owner_approval_present=False,
        manifest_valid=False,
        channel_approved=False,
        draft_hash_valid=False,
        y_star_gov_decision="owner_approval_missing",
        gov_mcp_gateway_available=True,
        gov_mcp_preflight_passed=False,
        execution_provider_available=False,
        no_forbidden_side_effects=False,
    )
    return not authorize_external_action(request).allowed


def render_e13_tier1_evidence_mission(request: Dict[str, Any], status: str, evidence_count: int) -> str:
    lines = [
        "# E13 Tier-1 Evidence Mission",
        "",
        f"- mission_id: {request.get('mission_id')}",
        f"- top_offer: {request.get('top_offer')}",
        f"- default_path: {request.get('default_path')}",
        f"- status: {status}",
        f"- evidence_count: {evidence_count}",
        f"- public_evidence_is_validation_feedback: false",
        f"- readiness_is_revenue: false",
        "",
        "## Opportunity Paths Compared",
    ]
    lines.extend(f"- {path}" for path in request.get("opportunity_paths", []))
    lines.extend(["", "## Counterfactual Questions"])
    lines.extend(f"- {question}" for question in request.get("counterfactual_questions", []))
    lines.extend(["", "## Forbidden Actions"])
    lines.extend(f"- {action}" for action in request.get("forbidden_actions", []))
    return "\n".join(lines)
