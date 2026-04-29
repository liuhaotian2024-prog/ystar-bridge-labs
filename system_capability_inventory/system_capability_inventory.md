# System Capability Inventory

```json
{
  "schema_version": "v0",
  "milestone_id": "L6.16",
  "capabilities": [
    {
      "capability_id": "self_governance_baseline",
      "current_status": "operational_reference_boundary",
      "evidence_commit_or_artifact": "L5/L6 governance artifacts and L6.15 decision boundary",
      "what_it_can_do": "Keep planning, observation, and writeback separated by explicit gates.",
      "what_it_cannot_do": "Authorize external action or core memory updates by itself.",
      "next_upgrade": "Durable human approval records for specific action classes."
    },
    {
      "capability_id": "external_observation_boundary",
      "current_status": "operational",
      "evidence_commit_or_artifact": "L6.2-L6.4 boundary and preflight artifacts",
      "what_it_can_do": "Define public read-only observation and no-action constraints.",
      "what_it_cannot_do": "Bypass search/page-read backend preflight.",
      "next_upgrade": "Add richer source policies for new mission domains."
    },
    {
      "capability_id": "controlled_search",
      "current_status": "operational_with_configured_backend",
      "evidence_commit_or_artifact": "2120094e and ca21363d",
      "what_it_can_do": "Run budgeted provider-backed search under explicit environment configuration.",
      "what_it_cannot_do": "Treat search snippets as evidence or run unbounded searches.",
      "next_upgrade": "Provider rate-limit and duplicate-result handling."
    },
    {
      "capability_id": "controlled_public_page_read",
      "current_status": "operational_with_resilience",
      "evidence_commit_or_artifact": "ca21363d",
      "what_it_can_do": "Read public HTTP/HTTPS pages by GET and turn blocked pages into structured residuals.",
      "what_it_cannot_do": "Login, submit forms, execute JavaScript, or access private/internal networks.",
      "next_upgrade": "Better HTML/PDF extraction and domain-specific readability heuristics."
    },
    {
      "capability_id": "bounded_crawl",
      "current_status": "operational_limited_depth",
      "evidence_commit_or_artifact": "L6.13/L6.14 run reports",
      "what_it_can_do": "Use depth <= 1 and budgeted pages/domains for evidence discovery.",
      "what_it_cannot_do": "High-volume crawling, scraping loops, or access-control bypass.",
      "next_upgrade": "Explicit domain allow/deny policy and canonical URL de-duplication."
    },
    {
      "capability_id": "evidence_packet_generation",
      "current_status": "operational",
      "evidence_commit_or_artifact": "real_evidence_packets and second_pass_evidence_packets",
      "what_it_can_do": "Create bounded evidence packets from page-read content.",
      "what_it_cannot_do": "Promote one source into settled truth without review.",
      "next_upgrade": "Improve excerpt quality and structured claim extraction."
    },
    {
      "capability_id": "source_quality_matrix",
      "current_status": "operational_basic",
      "evidence_commit_or_artifact": "real_source_quality_matrix and source_quality_update_matrix",
      "what_it_can_do": "Classify source quality labels and limitations.",
      "what_it_cannot_do": "Replace human source judgment or guarantee truth.",
      "next_upgrade": "Add stronger provenance and freshness parsing."
    },
    {
      "capability_id": "conflict_corroboration_matrix",
      "current_status": "operational",
      "evidence_commit_or_artifact": "corroboration_conflict_update",
      "what_it_can_do": "Represent supported, conflicted, unresolved, and insufficient evidence states.",
      "what_it_cannot_do": "Resolve policy or market truth without sufficient reviewed evidence.",
      "next_upgrade": "Add third-pass conflict-specific query executor."
    },
    {
      "capability_id": "second_pass_observation",
      "current_status": "completed",
      "evidence_commit_or_artifact": "2fc6fd82",
      "what_it_can_do": "Target unresolved conflicts with a second controlled observation pass.",
      "what_it_cannot_do": "Authorize external action from bounded conflict alone.",
      "next_upgrade": "Optional third pass focused on primary sources."
    },
    {
      "capability_id": "bounded_conflict_decision",
      "current_status": "human_review_ready",
      "evidence_commit_or_artifact": "conflict_resolution_decision_packet",
      "what_it_can_do": "Bound uncertainty enough to support caveated internal planning.",
      "what_it_cannot_do": "Declare unresolved claims settled.",
      "next_upgrade": "Human adjudication and optional additional observation."
    },
    {
      "capability_id": "human_review_packet",
      "current_status": "human_review_ready_with_bounded_conflict",
      "evidence_commit_or_artifact": "47b78c53 / human_review_packet",
      "what_it_can_do": "Translate evidence state into reviewable planning boundaries.",
      "what_it_cannot_do": "Grant external-use approval.",
      "next_upgrade": "Human approval workflow with recorded decisions."
    },
    {
      "capability_id": "planning_eligibility_matrix",
      "current_status": "operational",
      "evidence_commit_or_artifact": "planning_eligibility_matrix",
      "what_it_can_do": "Separate safe internal planning from blocked external and core-writeback actions.",
      "what_it_cannot_do": "Execute blocked actions.",
      "next_upgrade": "Attach approval IDs to future action proposals."
    },
    {
      "capability_id": "governed_planning_candidates",
      "current_status": "operational_review_only",
      "evidence_commit_or_artifact": "governed_planning_candidates",
      "what_it_can_do": "Propose internal planning steps with caveats and forbidden scopes.",
      "what_it_cannot_do": "Send messages, publish, pay, or write memory.",
      "next_upgrade": "Convert selected candidate into a review-gated work order."
    },
    {
      "capability_id": "read_model_console_visibility",
      "current_status": "extended_in_l6_16",
      "evidence_commit_or_artifact": "console_read_model/generated/l6_16_ceo_command_brief_internal_strategy_memo_summary.json",
      "what_it_can_do": "Expose owner-facing brief/memo status in the local console.",
      "what_it_cannot_do": "Act outside the repository or modify core state.",
      "next_upgrade": "Add one-command owner dashboard refresh flow."
    }
  ]
}
```
