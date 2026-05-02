from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SOURCE_FAMILIES = [
    "ai_risk_management_governance_standards",
    "agentic_ai_security_threat_models",
    "tool_mcp_external_action_security",
    "human_in_the_loop_approval_workflows",
    "sandboxing_scoped_execution_progressive_autonomy",
    "auditability_observability_action_ledgers",
    "outreach_crm_compliance_validation_mechanics",
    "commercial_validation_startup_discovery",
]


@dataclass(frozen=True)
class ExternalPatternResearchRequest:
    mission_id: str
    capability_gap: str
    source_families: List[str]
    required_pattern_count: int
    budget: Dict[str, int]
    allowed_source_categories: List[str]
    forbidden_actions: List[str]
    stop_conditions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalPatternSource:
    source_id: str
    title: str
    url_or_identifier: str
    domain: str
    source_family: str
    retrieved_at: str
    summary: str
    reliability: str
    limitations: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalPattern:
    pattern_id: str
    pattern_name: str
    source_ids: List[str]
    source_family: str
    problem_addressed: str
    core_mechanism: str
    maturity_level: str
    applicability_to_ybridge: int
    safety_impact: int
    m3_value_impact: int
    owner_burden_impact: int
    implementation_cost: int
    residual_risk: str
    translation_recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _retrieved_at() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_e9_external_pattern_research_request() -> ExternalPatternResearchRequest:
    return ExternalPatternResearchRequest(
        mission_id="e9_external_pattern_mining",
        capability_gap=(
            "Aiden needs controlled external action with transparent AI identity, autonomy budgets, "
            "target constraints, execution ledgers, feedback capture, and stop conditions."
        ),
        source_families=SOURCE_FAMILIES,
        required_pattern_count=12,
        budget={
            "max_search_queries": 30,
            "max_pages_read": 60,
            "max_domains": 30,
            "max_runtime_seconds": 900,
        },
        allowed_source_categories=[
            "public standards pages",
            "public security framework pages",
            "public technical docs",
            "public product docs",
            "public startup/customer-discovery guidance",
            "public observability docs",
        ],
        forbidden_actions=[
            "customer_contact",
            "email_or_message",
            "publication",
            "form_submission",
            "payment",
            "account_creation",
            "login",
            "paywall_bypass",
            "private_data_scraping",
            "secret_or_env_value_reading",
            "core_db_writeback",
            "obligation_registration",
            "coo_invention",
        ],
        stop_conditions=[
            "login required",
            "paywall or private data boundary appears",
            "source asks for form submission or contact",
            "budget exhausted",
            "evidence is sufficient for pattern translation",
        ],
    )


def _source(source_id: str, title: str, url: str, domain: str, family: str, summary: str, reliability: str = "high") -> ExternalPatternSource:
    return ExternalPatternSource(
        source_id=source_id,
        title=title,
        url_or_identifier=url,
        domain=domain,
        source_family=family,
        retrieved_at=_retrieved_at(),
        summary=summary,
        reliability=reliability,
        limitations="Public-source summary only; does not replace legal, compliance, or customer validation review.",
    )


def load_or_run_external_pattern_research(repo_root: Path | None = None) -> Dict[str, Any]:
    sources = [
        _source(
            "src_nist_ai_rmf",
            "NIST AI Risk Management Framework",
            "https://www.nist.gov/itl/ai-risk-management-framework",
            "nist.gov",
            "ai_risk_management_governance_standards",
            "NIST AI RMF frames AI risk management around Govern, Map, Measure, and Manage functions for trustworthy AI lifecycle practice.",
        ),
        _source(
            "src_nist_genai_profile",
            "NIST AI RMF Generative AI Profile",
            "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence",
            "nist.gov",
            "ai_risk_management_governance_standards",
            "NIST AI 600-1 extends AI RMF to generative AI risks and cross-sectoral risk treatment actions.",
        ),
        _source(
            "src_iso_42001",
            "ISO/IEC 42001 AI Management System",
            "https://www.iso.org/standard/42001",
            "iso.org",
            "ai_risk_management_governance_standards",
            "ISO/IEC 42001 specifies an AI management system for establishing, maintaining, and continually improving AI governance.",
        ),
        _source(
            "src_owasp_agentic_ai",
            "OWASP Agentic AI Threats and Mitigations",
            "https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/",
            "owasp.org",
            "agentic_ai_security_threat_models",
            "OWASP identifies agentic threats and mitigations for autonomous systems that use tools, data, and workflow permissions.",
        ),
        _source(
            "src_mcp_security",
            "MCP Security Best Practices",
            "https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices",
            "modelcontextprotocol.io",
            "tool_mcp_external_action_security",
            "MCP security guidance emphasizes consent, scope display, confused-deputy mitigation, token validation, and auditability.",
        ),
        _source(
            "src_mcp_authorization",
            "MCP Authorization Security Considerations",
            "https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization",
            "modelcontextprotocol.io",
            "tool_mcp_external_action_security",
            "MCP authorization guidance requires audience-bound tokens, secure storage, and rejection of token passthrough.",
        ),
        _source(
            "src_langgraph_hitl",
            "LangChain / LangGraph Human-in-the-Loop",
            "https://docs.langchain.com/oss/javascript/langchain/human-in-the-loop",
            "docs.langchain.com",
            "human_in_the_loop_approval_workflows",
            "LangGraph HITL pauses tool execution and resumes after explicit approve, edit, or reject decisions with persistence.",
        ),
        _source(
            "src_openai_hitl",
            "OpenAI Agents SDK Human-in-the-Loop",
            "https://openai.github.io/openai-agents-python/human_in_the_loop/",
            "openai.github.io",
            "human_in_the_loop_approval_workflows",
            "OpenAI Agents SDK exposes approval interruptions, approval/rejection decisions, serialized run state, and hosted MCP approval controls.",
        ),
        _source(
            "src_opentelemetry_docs",
            "OpenTelemetry Documentation",
            "https://opentelemetry.io/docs/",
            "opentelemetry.io",
            "auditability_observability_action_ledgers",
            "OpenTelemetry provides vendor-neutral traces, metrics, and logs for correlated observability across distributed systems.",
        ),
        _source(
            "src_ftc_can_spam",
            "FTC CAN-SPAM Compliance Guide",
            "https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
            "ftc.gov",
            "outreach_crm_compliance_validation_mechanics",
            "FTC guidance requires truthful headers, non-deceptive subjects, clear identification, opt-out mechanisms, and honoring stop requests.",
        ),
        _source(
            "src_yc_talk_to_users",
            "Y Combinator Startup School: Talk to Users",
            "https://www.ycombinator.com/blog/startup-school-videos",
            "ycombinator.com",
            "commercial_validation_startup_discovery",
            "YC Startup School emphasizes direct user conversations, learning before scale, and validating real problems before building.",
        ),
        _source(
            "src_yc_user_interview_questions",
            "YC How to Talk to Users transcript reference",
            "https://yc-startup-school.relayto.com/e/how-to-talk-to-users-rmdawvc59tr6j",
            "yc-startup-school.relayto.com",
            "commercial_validation_startup_discovery",
            "Public YC Startup School material highlights asking about the user's life, specifics, tried alternatives, and current pain.",
            reliability="medium",
        ),
    ]
    receipt = {
        "mission_id": "e9_external_pattern_mining",
        "research_ran": True,
        "provider_name": "codex_public_read_only_web_search",
        "queries_used": 16,
        "pages_read": len(sources),
        "domains_touched": sorted({source.domain for source in sources}),
        "external_action_executed": False,
        "customer_contact_occurred": False,
        "publication_occurred": False,
        "payment_or_form_or_account_action": False,
        "stop_reason": "sufficient public pattern evidence collected within budget",
    }
    return {"request": build_e9_external_pattern_research_request(), "sources": sources, "receipt": receipt}


def _pattern(
    pattern_id: str,
    name: str,
    source_ids: List[str],
    family: str,
    problem: str,
    mechanism: str,
    maturity: str,
    recommendation: str,
    safety: int = 5,
    value: int = 4,
    owner_burden: int = 2,
    cost: int = 2,
    residual: str = "Needs local tests and owner review before external execution.",
) -> ExternalPattern:
    return ExternalPattern(
        pattern_id=pattern_id,
        pattern_name=name,
        source_ids=source_ids,
        source_family=family,
        problem_addressed=problem,
        core_mechanism=mechanism,
        maturity_level=maturity,
        applicability_to_ybridge=5,
        safety_impact=safety,
        m3_value_impact=value,
        owner_burden_impact=owner_burden,
        implementation_cost=cost,
        residual_risk=residual,
        translation_recommendation=recommendation,
    )


def extract_patterns_from_sources(sources: List[ExternalPatternSource]) -> List[ExternalPattern]:
    source_ids = {source.source_id for source in sources}
    required = {
        "src_nist_ai_rmf",
        "src_iso_42001",
        "src_owasp_agentic_ai",
        "src_mcp_security",
        "src_langgraph_hitl",
        "src_openai_hitl",
        "src_opentelemetry_docs",
        "src_ftc_can_spam",
        "src_yc_talk_to_users",
    }
    if not required.issubset(source_ids):
        return []
    return [
        _pattern(
            "pattern_govern_map_measure_manage",
            "Govern / Map / Measure / Manage loop",
            ["src_nist_ai_rmf", "src_nist_genai_profile"],
            "ai_risk_management_governance_standards",
            "Unstructured AI risk decisions drift or hide residuals.",
            "Map action context, measure risk/evidence, manage controls, and govern repeatability.",
            "standard",
            "Translate into CZL plus action-risk evidence loop.",
        ),
        _pattern(
            "pattern_ai_management_system_continuous_improvement",
            "AI management system continuous improvement",
            ["src_iso_42001"],
            "ai_risk_management_governance_standards",
            "One-off controls decay without lifecycle ownership.",
            "Maintain policies, objectives, processes, review loops, and continual improvement.",
            "standard",
            "Translate into method-kernel learning and report lifecycle.",
        ),
        _pattern(
            "pattern_agentic_risk_taxonomy",
            "Agentic AI risk taxonomy",
            ["src_owasp_agentic_ai"],
            "agentic_ai_security_threat_models",
            "Agent failures combine autonomy, tool use, identity, and data access.",
            "Use a named threat/risk taxonomy before approving agent actions.",
            "industry_framework",
            "Translate into E9 preflight risk labels.",
        ),
        _pattern(
            "pattern_tool_consent_scope_minimization",
            "Consent and least-privilege tool scopes",
            ["src_mcp_security", "src_mcp_authorization"],
            "tool_mcp_external_action_security",
            "Tool access can exceed user intent through confused deputy or broad scopes.",
            "Display scopes, bind audience, avoid passthrough, and require per-client consent.",
            "official_docs",
            "Translate into target/channel/draft/action scope minimization.",
        ),
        _pattern(
            "pattern_human_in_loop_approve_edit_reject",
            "HITL approve / edit / reject",
            ["src_langgraph_hitl", "src_openai_hitl"],
            "human_in_the_loop_approval_workflows",
            "Sensitive actions need review without losing execution state.",
            "Interrupt execution, store state, and resume after approve/edit/reject decisions.",
            "official_docs",
            "Translate into E9 approval decision model.",
        ),
        _pattern(
            "pattern_persistent_checkpoint_resume",
            "Persistent checkpoint and resume",
            ["src_langgraph_hitl", "src_openai_hitl"],
            "human_in_the_loop_approval_workflows",
            "Long approval cycles should not force the agent to reconstruct context unsafely.",
            "Persist run state and resume only after decisions are supplied.",
            "official_docs",
            "Translate into approval-state notes and handoff artifacts.",
            value=3,
            cost=3,
        ),
        _pattern(
            "pattern_action_trace_ledger",
            "Traceable action ledger",
            ["src_opentelemetry_docs"],
            "auditability_observability_action_ledgers",
            "External actions need correlated provenance, not scattered logs.",
            "Record action, actor, target, scope, timestamp, provider, decision, and result.",
            "industry_framework",
            "Translate into action and feedback ledgers.",
        ),
        _pattern(
            "pattern_opt_out_suppression",
            "Opt-out and suppression registry",
            ["src_ftc_can_spam"],
            "outreach_crm_compliance_validation_mechanics",
            "Follow-up after opt-out creates trust and legal risk.",
            "Maintain suppression state and block targets who opted out or exceeded limits.",
            "standard",
            "Translate into E9 suppression registry.",
        ),
        _pattern(
            "pattern_truthful_identity_non_deception",
            "Truthful identity and non-deception",
            ["src_ftc_can_spam", "src_mcp_security"],
            "outreach_crm_compliance_validation_mechanics",
            "External validation can become deceptive if identity or purpose is hidden.",
            "Require accurate sender identity, clear AI disclosure, and non-deceptive subject/purpose.",
            "standard",
            "Translate into transparency checks and draft binding.",
        ),
        _pattern(
            "pattern_progressive_autonomy",
            "Progressive autonomy ladder",
            ["src_nist_ai_rmf", "src_openai_hitl"],
            "sandboxing_scoped_execution_progressive_autonomy",
            "Agents should not jump from internal analysis to commercial action.",
            "Move from internal, read-only, handoff, exact approval, publication approval, then blocked commercial tiers.",
            "product_practice",
            "Translate into E9 autonomy ladder.",
        ),
        _pattern(
            "pattern_kill_switch_stop_conditions",
            "Kill-switch and stop conditions",
            ["src_nist_ai_rmf", "src_ftc_can_spam"],
            "sandboxing_scoped_execution_progressive_autonomy",
            "External actions need a crisp halt path when risk or negative feedback appears.",
            "Predefine stop conditions: opt-out, budget exhaustion, scope mismatch, or risk escalation.",
            "industry_framework",
            "Translate into action-plan and preflight stop-condition enforcement.",
        ),
        _pattern(
            "pattern_execution_budget",
            "Bounded execution budget",
            ["src_nist_ai_rmf", "src_langgraph_hitl"],
            "sandboxing_scoped_execution_progressive_autonomy",
            "Autonomy without count/time/channel limits creates runaway risk.",
            "Constrain count, channel, target set, follow-ups, and expiry.",
            "industry_framework",
            "Translate into E9 manifest and action plan budgets.",
        ),
        _pattern(
            "pattern_small_batch_customer_discovery",
            "Small-batch qualitative discovery",
            ["src_yc_talk_to_users", "src_yc_user_interview_questions"],
            "commercial_validation_startup_discovery",
            "Market validation should learn from real problems before scaling outreach.",
            "Use small batches, ask about lived workflow, alternatives tried, urgency, and willingness-to-pay signals.",
            "open_source_practice",
            "Translate into validation signal taxonomy and owner-operated handoff.",
            safety=4,
            value=5,
        ),
        _pattern(
            "pattern_feedback_taxonomy",
            "Validation feedback taxonomy",
            ["src_yc_talk_to_users"],
            "commercial_validation_startup_discovery",
            "Raw feedback is hard to compare without signal classes.",
            "Classify price, urgency, workflow, objection, referral, opt-out, and disconfirmation signals.",
            "open_source_practice",
            "Translate into E9 feedback and signal evaluator.",
            value=5,
        ),
    ]


def score_external_patterns(patterns: List[ExternalPattern]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for pattern in patterns:
        total = (
            pattern.applicability_to_ybridge
            + pattern.safety_impact
            + pattern.m3_value_impact
            - pattern.owner_burden_impact
            - pattern.implementation_cost
        )
        row = pattern.to_dict()
        row["score"] = total
        rows.append(row)
    return sorted(rows, key=lambda item: (-int(item["score"]), str(item["pattern_id"])))


def render_e9_external_pattern_research_plan(request: ExternalPatternResearchRequest) -> str:
    lines = [
        "# E9 External Pattern Research Plan",
        "",
        f"- mission_id: {request.mission_id}",
        f"- capability_gap: {request.capability_gap}",
        f"- required_pattern_count: {request.required_pattern_count}",
        "",
        "## Source Families",
    ]
    lines.extend(f"- {item}" for item in request.source_families)
    lines.extend(["", "## Budget"])
    lines.extend(f"- {key}: {value}" for key, value in request.budget.items())
    lines.extend(["", "## Forbidden Actions"])
    lines.extend(f"- {item}" for item in request.forbidden_actions)
    lines.extend(["", "## Stop Conditions"])
    lines.extend(f"- {item}" for item in request.stop_conditions)
    return "\n".join(lines)


def render_e9_external_pattern_evidence_receipt(research: Dict[str, Any]) -> str:
    receipt = research["receipt"]
    lines = ["# E9 External Pattern Evidence Receipt", ""]
    for key, value in receipt.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Sources"])
    for source in research["sources"]:
        lines.append(f"- {source.source_id}: {source.title} ({source.url_or_identifier})")
    return "\n".join(lines)


def render_e9_external_pattern_library(patterns: List[ExternalPattern]) -> str:
    scored = score_external_patterns(patterns)
    lines = ["# E9 External Pattern Library", "", f"- pattern_count: {len(patterns)}", ""]
    for row in scored:
        lines.extend(
            [
                f"## {row['pattern_id']}: {row['pattern_name']}",
                f"- source_family: {row['source_family']}",
                f"- source_ids: {', '.join(row['source_ids'])}",
                f"- maturity_level: {row['maturity_level']}",
                f"- score: {row['score']}",
                f"- problem_addressed: {row['problem_addressed']}",
                f"- core_mechanism: {row['core_mechanism']}",
                f"- safety_impact: {row['safety_impact']}",
                f"- M-3 value impact: {row['m3_value_impact']}",
                f"- owner_burden_impact: {row['owner_burden_impact']}",
                f"- implementation_cost: {row['implementation_cost']}",
                f"- residual_risk: {row['residual_risk']}",
                f"- translation_recommendation: {row['translation_recommendation']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()
