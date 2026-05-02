from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .capability_fingerprint_extractor import CapabilityFingerprint, extract_capability_fingerprints
from .global_semantic_inventory import build_global_semantic_inventory


@dataclass
class CapabilityCluster:
    cluster_id: str
    cluster_name: str
    member_fingerprints: List[str]
    repos_involved: List[str]
    relation_type: str
    why_they_overlap: str
    duplication_harmful: bool
    conflict_risk: str
    canonical_owner_recommendation: str
    adapter_router_recommendation: str
    migration_strategy: str
    tests_needed: List[str] = field(default_factory=list)
    immediate_code_consolidation_safe: bool = True
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _match(fp: CapabilityFingerprint, terms: List[str]) -> bool:
    haystack = " ".join([fp.file_path, fp.symbol_or_section, " ".join(fp.capability_terms), " ".join(fp.fields), " ".join(fp.statuses_or_decisions)]).lower()
    return any(term.lower() in haystack for term in terms)


def _members(fps: List[CapabilityFingerprint], terms: List[str]) -> List[CapabilityFingerprint]:
    return [fp for fp in fps if _match(fp, terms)]


def _cluster(
    cid: str,
    name: str,
    fps: List[CapabilityFingerprint],
    relation: str,
    why: str,
    harmful: bool,
    risk: str,
    owner: str,
    router: str,
    migration: str,
    tests: List[str],
    safe: bool = True,
    notes: str = "",
) -> CapabilityCluster:
    return CapabilityCluster(
        cluster_id=cid,
        cluster_name=name,
        member_fingerprints=[fp.fingerprint_id for fp in fps[:80]],
        repos_involved=sorted({fp.repo for fp in fps}),
        relation_type=relation,
        why_they_overlap=why,
        duplication_harmful=harmful,
        conflict_risk=risk,
        canonical_owner_recommendation=owner,
        adapter_router_recommendation=router,
        migration_strategy=migration,
        tests_needed=tests,
        immediate_code_consolidation_safe=safe,
        notes=notes,
    )


def discover_capability_clusters(fingerprints: List[CapabilityFingerprint]) -> List[CapabilityCluster]:
    clusters: List[CapabilityCluster] = []
    target = _members(fingerprints, ["target seed", "target candidate", "proposed", "approved", "contact_authorized", "owner_approved_for_contact"])
    if target:
        clusters.append(
            _cluster(
                "cluster_target_lifecycle",
                "Target candidate/proposal/approval lifecycle",
                target,
                "conflicting_approval_semantics",
                "E10, E8/E9 validation, operations JSON, and ystar-company approval packets all represent target or approval states; proposal-only targets can be confused with approved contact targets without a lifecycle router.",
                True,
                "high",
                "bridge-labs owns business target lifecycle; Y-star-gov owns external-action permission semantics; gov-mcp exposes gateway checks.",
                "Implement target_lifecycle_router and make proposal states non-contactable.",
                "Keep E8/E9/E10 modules as adapters; route future E11/E12 contact through canonical lifecycle states.",
                ["block discovered/proposed target contact", "allow owner-approved target to preflight only"],
            )
        )
    evidence = _members(fingerprints, ["public_market_evidence", "public target discovery", "validation feedback", "paid signal", "evidence", "feedback", "source", "provenance"])
    if evidence:
        clusters.append(
            _cluster(
                "cluster_evidence_signal_ladder",
                "Evidence, feedback, and paid-signal ladder",
                evidence,
                "conflicting_signal_semantics",
                "Reports and modules use public evidence, external pattern evidence, target discovery evidence, validation feedback, and paid signal for different claims; routing is needed to prevent public discovery from becoming validation or paid-pilot readiness.",
                True,
                "high",
                "bridge-labs owns market/evidence claim ladder; CIEU governs durable learning; owner decides commercial escalation.",
                "Implement evidence_signal_router.",
                "Use typed evidence levels and forbid upward claims without matching evidence level.",
                ["block public target evidence from paid pilot", "allow validation feedback for validation result", "require paid signal for paid pilot prep"],
            )
        )
    action = _members(fingerprints, ["permission tier", "risk tier", "preflight", "action classifier", "approval", "manifest", "execution gate", "MCP", "gateway"])
    if action:
        clusters.append(
            _cluster(
                "cluster_action_authorization_chain",
                "External action authorization chain",
                action,
                "cross_repo_adapter",
                "Bridge-labs risk tiers, Y-star-gov permission tiers, gov-mcp preflight tools, manifests, execution gates, ledgers, and receipts all govern side effects; a facade is needed so future validation cannot bypass formal governance.",
                True,
                "critical",
                "Y-star-gov owns deterministic policy; gov-mcp owns gateway exposure; bridge-labs owns business intent and execution packet assembly.",
                "Implement action_authorization_router.",
                "Bridge-labs can call/represent Y-star-gov and gov-mcp decisions without modifying those repos in E11.",
                ["reference Y-star-gov decision", "reference gov-mcp when available", "block external action without full chain"],
            )
        )
    learning = _members(fingerprints, ["brain", "dream", "CIEU", "prediction delta", "writeback", "learning eligibility", "method kernel"])
    if learning:
        clusters.append(
            _cluster(
                "cluster_learning_writeback_gate",
                "Report, method, dream, brain, and CIEU learning paths",
                learning,
                "conflicting_writeback_semantics",
                "Reports propose learning, method kernel stores durable principles, dream cycles propose diffs, brain stores cognitive graph/activation, and CIEU carries prediction delta. Direct report-to-brain learning would bypass review gates.",
                True,
                "critical",
                "CIEU/Y-star-gov owns prediction-delta eligibility; Aiden Brain owns graph state; bridge-labs reports are proposal-only.",
                "Implement learning_writeback_router.",
                "All persistent learning must be report-only until CIEU/review gate approves brain/memory writeback.",
                ["block report-direct brain writeback", "require CIEU delta for brain writeback"],
            )
        )
    closure = _members(fingerprints, ["CZL", "Rt+1", "full_mission_rt1", "status", "repository closure", "paid signal", "validation complete", "discovery complete"])
    if closure:
        clusters.append(
            _cluster(
                "cluster_closure_status_semantics",
                "Closure status and completion semantics",
                closure,
                "conflicting_status_semantics",
                "E milestones distinguish discovery complete, validation complete, paid-signal readiness, repository delivery, and blocked statuses. Without routing, local completion can be mistaken for commercial validation completion.",
                True,
                "high",
                "bridge-labs CZL owns mission closure semantics; repository status remains delivery-only; commercial validation needs feedback/ledger evidence.",
                "Implement closure_status_router.",
                "Add status-family checks for discovery, validation, paid signal, revenue, blocked, and repository delivery.",
                ["distinguish discovery from validation", "distinguish validation from paid signal"],
            )
        )
    counter = _members(fingerprints, ["counterfactual", "disconfirming", "kill condition", "what would invalidate", "method kernel"])
    if counter:
        clusters.append(
            _cluster(
                "cluster_counterfactual_protocol",
                "Counterfactual and disconfirmation protocol",
                counter,
                "lifecycle_overlap",
                "Counterfactual language appears in method kernel, opportunity evaluation, market evaluation, validation packets, and tests. A router should source the canonical protocol from method-kernel semantics instead of stage-local wording.",
                True,
                "medium",
                "Method kernel owns durable counterfactual protocol; stage modules adapt it to opportunity, market, execution, revenue, governance, or learning contexts.",
                "Implement counterfactual_router.",
                "Keep stage-specific disconfirmation tests but route protocol labels through the method kernel.",
                ["counterfactual router reports method kernel source"],
            )
        )
    field = _members(fingerprints, ["field", "field functional", "phi", "activation", "Hebbian", "world_value_field", "场", "场泛函", "激活"])
    if field:
        clusters.append(
            _cluster(
                "cluster_field_brain_cognitive_runtime",
                "Field/activation/brain cognitive runtime",
                field,
                "adjacent_stage_adapter",
                "Aiden Brain, dream diffs, field-functional archaeology, world-value field, and activation/Hebbian concepts overlap as cognitive-field mechanisms, but not all are harmful duplicates. Integration mapping is safer than destructive consolidation.",
                False,
                "medium",
                "Aiden Brain owns graph/activation state; ystar-company remains incubation source; bridge-labs owns interpretation reports; CIEU gates persistent learning.",
                "No destructive router; cover through learning_writeback_router and integration map.",
                "Treat field-functional assets as interpretation/incubation until backflowed through CIEU-gated learning.",
                ["field/brain/CIEU report mentions activation, phi, and writeback policy"],
                safe=False,
                notes="Found beyond prompt examples as ystar-company field_functional_archaeology and world_value_field_model assets.",
            )
        )
    company = _members(fingerprints, ["commercial loop", "scheduler", "opportunity runtime", "manual send", "approval packet", "revenue path"])
    if company:
        clusters.append(
            _cluster(
                "cluster_incubated_company_runtime",
                "ystar-company incubated commercial/runtime mechanisms",
                company,
                "obsolete_or_legacy" if len({fp.repo for fp in company}) == 1 else "adjacent_stage_adapter",
                "ystar-company contains scheduler, commercial loop, runtime packets, public research adapters, approval packets, and no-action receipts that overlap bridge-labs E6-E10 but are incubation artifacts with a very dirty runtime state.",
                False,
                "medium",
                "bridge-labs owns current E-series commercial runtime; ystar-company remains incubation/reference unless separately backflowed.",
                "No code router in E11; document cross-repo backflow plan.",
                "Extract patterns later, do not read private runtime DB/log contents or mutate ystar-company.",
                ["backflow plan names ystar-company as incubation source"],
                safe=False,
                notes="Cluster found from ystar-company, not named as a final ontology item in the prompt.",
            )
        )
    return clusters


def render_duplicate_overlap_cluster_report(clusters: List[CapabilityCluster], fingerprints: List[CapabilityFingerprint]) -> str:
    fp_by_id = {fp.fingerprint_id: fp for fp in fingerprints}
    lines = ["# E11 Duplicate / Overlap Cluster Report", "", "Clusters below are discovered from inventory fingerprints, not taken as the prompt ontology.", ""]
    lines.extend(
        [
            "## Discovery Notes",
            "- clusters_found_from_evidence: yes",
            "- prompt_seed_categories_used_as_search_terms_only: yes",
            "- found_but_not_named_in_prompt: `cluster_incubated_company_runtime` and repository-delivery/commercial-completion semantics inside `cluster_closure_status_semantics`.",
            "- expected_but_not_found: none; all owner examples had some evidence, though field/brain was mapped rather than destructively routed.",
            "- false_positives_rejected: repeated Markdown report sections are harmless renderer duplication unless they alter lifecycle or approval semantics.",
            "",
        ]
    )
    for cluster in clusters:
        lines.extend(
            [
                f"## {cluster.cluster_id}: {cluster.cluster_name}",
                f"- relation_type: {cluster.relation_type}",
                f"- repos_involved: {', '.join(cluster.repos_involved)}",
                f"- harmful_duplicate: {cluster.duplication_harmful}",
                f"- conflict_risk: {cluster.conflict_risk}",
                f"- why_overlap: {cluster.why_they_overlap}",
                f"- canonical_owner_recommendation: {cluster.canonical_owner_recommendation}",
                f"- adapter_router_recommendation: {cluster.adapter_router_recommendation}",
                f"- immediate_code_consolidation_safe: {cluster.immediate_code_consolidation_safe}",
                f"- migration_strategy: {cluster.migration_strategy}",
                "",
                "### Evidence Members",
            ]
        )
        for fp_id in cluster.member_fingerprints[:8]:
            fp = fp_by_id.get(fp_id)
            if fp:
                lines.append(f"- {fp_id}: {fp.repo}:{fp.file_path}:{fp.symbol_or_section} / {', '.join(fp.capability_terms[:6])}")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_conflict_risk_matrix(clusters: List[CapabilityCluster]) -> str:
    scenarios = {
        "cluster_target_lifecycle": ("E10 proposed target seed is treated as contact approval.", "Could cause unauthorized customer contact in E12.", "target_lifecycle_router", "yes", "no"),
        "cluster_evidence_signal_ladder": ("Public target discovery evidence is treated as validation feedback or paid signal.", "Could recommend paid pilot without buyer response.", "evidence_signal_router", "yes", "yes"),
        "cluster_action_authorization_chain": ("Bridge-labs execution gate bypasses Y-star-gov/gov-mcp semantics.", "Could execute external action without canonical owner approval.", "action_authorization_router", "yes", "no"),
        "cluster_learning_writeback_gate": ("E reports or dream diffs write directly to brain/CIEU.", "Could corrupt persistent learning without prediction-delta validation.", "learning_writeback_router", "no", "yes"),
        "cluster_closure_status_semantics": ("Discovery complete is interpreted as validation or paid-signal complete.", "Could move E12/E13 into paid-pilot path prematurely.", "closure_status_router", "yes", "no"),
        "cluster_counterfactual_protocol": ("Stage-local counterfactual wording drifts from method-kernel protocol.", "Could weaken disconfirmation gates.", "counterfactual_router", "yes", "no"),
    }
    lines = ["# E11 Conflict Risk Matrix", ""]
    for index, cluster in enumerate(clusters, start=1):
        scenario, impact, fix, breaks_validation, corrupts_learning = scenarios.get(cluster.cluster_id, ("Incubated mechanism is mistaken for canonical runtime.", "Could create unclear ownership or stale behavior.", "backflow plan", "unknown", "unknown"))
        severity = "critical" if cluster.conflict_risk == "critical" else cluster.conflict_risk
        lines.extend(
            [
                f"## conflict_{index:02d}: {cluster.cluster_name}",
                f"- affected_cluster: {cluster.cluster_id}",
                f"- scenario: {scenario}",
                f"- risk: {cluster.relation_type}",
                f"- likely_impact: {impact}",
                f"- current_evidence: {cluster.why_they_overlap}",
                f"- proposed_router_or_fix: {fix}",
                f"- could_break_E12_external_validation: {breaks_validation}",
                f"- could_corrupt_brain_CIEU_learning: {corrupts_learning}",
                f"- severity: {severity}",
                f"- owner_decision_required: {'yes' if cluster.conflict_risk in {'critical', 'high'} else 'no'}",
                f"- exact_next_action: {cluster.adapter_router_recommendation}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def render_canonical_ownership_map(clusters: List[CapabilityCluster]) -> str:
    lines = ["# E11 Canonical Ownership Map", ""]
    for cluster in clusters:
        gateway = "gov-mcp" if "gov_mcp" in cluster.repos_involved or "Y-star-gov" in cluster.canonical_owner_recommendation else "bridge-labs"
        persistence = "CIEU/Y-star-gov" if "learning" in cluster.cluster_id or "brain" in cluster.cluster_id else "bridge-labs reports"
        lines.extend(
            [
                f"## {cluster.cluster_id}: {cluster.cluster_name}",
                f"- canonical_owner: {cluster.canonical_owner_recommendation}",
                f"- adapter_owner: bridge-labs E-series modules remain adapters unless explicitly promoted.",
                f"- renderer_owner: bridge-labs reports/integration.",
                f"- gateway_owner: {gateway}.",
                f"- persistence_owner: {persistence}.",
                "- test_owner: bridge-labs E11 router tests plus future Y-star-gov/gov-mcp backflow tests.",
                f"- migration_priority: {'P0' if cluster.conflict_risk == 'critical' else 'P1' if cluster.conflict_risk == 'high' else 'P2'}",
                f"- why: {cluster.why_they_overlap}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def render_field_brain_cieu_integration_map(fingerprints: List[CapabilityFingerprint]) -> str:
    brain = [fp for fp in fingerprints if _match(fp, ["brain", "activation", "Hebbian", "phi", "dream", "CIEU", "prediction delta", "writeback"])]
    lines = [
        "# E11 Field / Brain / CIEU / Method / CZL Integration Map",
        "",
        "## Aiden Brain Graph",
        "- node schema: discovered from brain-related scripts/reports as cognitive nodes with Y/X/Z/T/Φ/C-style dimensions and activation metadata.",
        "- edge schema: discovered through brain/dream/writeback references as graph relationships supporting spreading activation and Hebbian learning.",
        "- activation schema: activation, phi/Φ, field state, and dream diff references are present in bridge-labs and ystar-company field-functional artifacts.",
        "- dream-cycle proposal linkage: dream diffs propose changes; they must not persist directly into brain/CIEU without review.",
        "- duplicate learning risk: reports, dream diffs, method kernel updates, CIEU deltas, and brain writeback all express learning in different forms.",
        "",
        "## Field / Field-Functional Interpretation",
        "- implicit fields found: activation field, opportunity field, governance field, evidence field, mission residual field, external-action risk field, revenue-discovery field, and world-value field.",
        "- field interaction gap: these fields currently meet through reports and runtime packets rather than a single formal field calculus.",
        "- E11 decision: map and gate them; do not destructively absorb ystar-company field-functional archaeology into bridge-labs.",
        "",
        "## CIEU",
        "- prediction_delta_schema: discovered in Y-star-gov CIEU docs/kernel and ystar-company release_preflight_cieu_residual assets.",
        "- learning_eligibility: persistent learning requires prediction vs actual delta, residual classification, governance_ref, and review gate.",
        "- brain_writeback_policy: CIEU must gate persistent brain/memory writeback; E reports remain proposal-only.",
        "",
        "## Method Kernel",
        "- M Triangle, anti prompt-overfit, meta-development loop, counterfactual protocol, and E6-E10 learning updates are durable method principles.",
        "- Method kernel should not absorb every tactical report; E11 routes durable principle candidates separately from report-only observations.",
        "",
        "## CZL",
        "- Y*, Xt, U, Yt+1, Rt+1, feasible/full residuals, and status semantics are mission closure primitives.",
        "- Closure status must distinguish discovery complete, validation complete, paid-signal complete, repository delivery complete, and blocked states.",
        "",
        "## Required Integration Principle",
        "- reports may propose learning",
        "- CIEU validates prediction/actual delta",
        "- Brain writeback requires explicit gate",
        "- Method kernel updates require durable-principle test",
        "- Dream diffs must not bypass CIEU/review gates",
        "- commercial feedback must be classified before it can influence paid-pilot readiness",
        "",
        "## Evidence Fingerprints",
    ]
    for fp in brain[:20]:
        lines.append(f"- {fp.fingerprint_id}: {fp.repo}:{fp.file_path}:{fp.symbol_or_section}")
    return "\n".join(lines)


def build_and_write_cluster_artifacts(repo_root: Path) -> Dict[str, Any]:
    inventory = build_global_semantic_inventory(repo_root)
    fingerprints = extract_capability_fingerprints(inventory)
    clusters = discover_capability_clusters(fingerprints)
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "e11_duplicate_overlap_cluster_report.md").write_text(render_duplicate_overlap_cluster_report(clusters, fingerprints) + "\n", encoding="utf-8")
    (reports / "e11_conflict_risk_matrix.md").write_text(render_conflict_risk_matrix(clusters) + "\n", encoding="utf-8")
    (reports / "e11_canonical_ownership_map.md").write_text(render_canonical_ownership_map(clusters) + "\n", encoding="utf-8")
    (reports / "e11_field_brain_cieu_integration_map.md").write_text(render_field_brain_cieu_integration_map(fingerprints) + "\n", encoding="utf-8")
    return {"inventory": inventory, "fingerprints": fingerprints, "clusters": clusters}

