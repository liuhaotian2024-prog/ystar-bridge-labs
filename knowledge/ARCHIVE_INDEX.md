# Archive Index — Y* Bridge Labs
# Auto-maintained by Secretary Agent (Samantha Lin)
# Last updated: 2026-04-16 (taxonomy reorganization, Board CZL dispatch)
#
# [MARKER] real-time archival duty activated 2026-04-16 by Board
#   rule_id: realtime_artifact_archival_czl
#   charter: agents/Secretary.md §长期自主任务（CZL duties）
#   SLA: new artifact → indexed ≤30 min + CIEU ARTIFACT_ARCHIVED emit
#   scope: reports/ knowledge/ products/ content/ governance/ + git commits + L3+ subagent deliverables + Board coined phrases
#   out-of-scope (this marker): historical backlog sweep — separate dispatch
#
# [TAXONOMY v2 2026-04-16] — 8 top-level sections, sub-categorized by owner / theme / time.
#   Lookup discipline: Board says "X 在哪" → Secretary scans sections in order 1→8;
#   if not in index, fallback grep across repo and append entry under correct section + emit CIEU.
#   Orphan policy: zero. Every prior entry from v1 ad-hoc list is reclassified below.

---

## 1. Constitutional Doctrines

Charter, governance protocols, agent contracts. Highest authority — modifications require Board L3 approval and DNA_LOG entry.

### 1.1 Root Charter Files
- [AGENTS.md](../AGENTS.md) — Y*gov governance contract, all iron rules
- [CLAUDE.md](../CLAUDE.md) — Project-level Claude Code instructions, boot protocol
- [CZL.md](../CZL.md) — Long-term autonomous duty registry
- [README.md](../README.md) — Public-facing project description
- [HISTORY.md](../HISTORY.md) — Constitutional history log
- [SOUL.md](../SOUL.md) — Mission statement
- [USER.md](../USER.md) — Board (Haotian) preferences
- [IDENTITY.md](../IDENTITY.md) — Identity protocol
- [TOOLS.md](../TOOLS.md) — Tool inventory
- [OKR.md](../OKR.md) — Objectives & key results
- [HEARTBEAT.md](../HEARTBEAT.md) — Liveness signal contract
- [SUBSYSTEM_INDEX.md](../SUBSYSTEM_INDEX.md) — Subsystem registry
- [OPERATIONS.md](../OPERATIONS.md) — Operations runbook
- [DISPATCH.md](../DISPATCH.md) — Dispatch protocol
- [DIRECTIVE_TRACKER.md](../DIRECTIVE_TRACKER.md) — Board directive ledger
- [BOARD_PENDING.md](../BOARD_PENDING.md) — Pending Board approvals queue
- [BOARD_BRIEFING_20260404.md](../BOARD_BRIEFING_20260404.md) — Historical Board briefing

### 1.2 Governance Protocols (governance/)
- [BOARD_CHARTER_AMENDMENTS.md](../governance/BOARD_CHARTER_AMENDMENTS.md) — Amendment ledger (AMENDMENT-001..N)
- [DNA_LOG.md](../governance/DNA_LOG.md) — Override + escape-hatch audit log
- [WORKING_STYLE.md](../governance/WORKING_STYLE.md) — 11-article working style (Article 11 = autonomous methodology)
- [INTERNAL_GOVERNANCE.md](../governance/INTERNAL_GOVERNANCE.md)
- [INNER_DRIVE_PROTOCOL.md](../governance/INNER_DRIVE_PROTOCOL.md)
- [CONTINUITY_PROTOCOL.md](../governance/CONTINUITY_PROTOCOL.md)
- [ETHICS.md](../governance/ETHICS.md)
- [CALENDAR.md](../governance/CALENDAR.md)
- [TEMP_LAW.md](../governance/TEMP_LAW.md) — Temporary laws pending consolidation
- [agent_id_canonical.json](../governance/agent_id_canonical.json) — Canonical agent_id registry
- [canonical_hashes.json](../governance/canonical_hashes.json)
- [ceo_dispatch_self_check.md](../governance/ceo_dispatch_self_check.md)
- [ceo_midstream_checkin_protocol.md](../governance/ceo_midstream_checkin_protocol.md)
- [cieu_event_taxonomy.md](../governance/cieu_event_taxonomy.md) — CIEU event vocabulary
- [CIEU_VIDEO_METHODOLOGY.md](../governance/CIEU_VIDEO_METHODOLOGY.md)
- [CSO_INTEL_PROTOCOL.md](../governance/CSO_INTEL_PROTOCOL.md)
- [czl_unified_communication_protocol_v1.md](../governance/czl_unified_communication_protocol_v1.md)
- [forget_guard_rules.yaml](../governance/forget_guard_rules.yaml) — ForgetGuard deny rules
- [priority_brief_schema.md](../governance/priority_brief_schema.md)
- [sub_agent_atomic_dispatch.md](../governance/sub_agent_atomic_dispatch.md)
- [sub_agent_boot_prompt_template.md](../governance/sub_agent_boot_prompt_template.md)

### 1.3 Agent Charters (agents/)
- [agents/CEO.md](../agents/CEO.md) — Aiden charter
- [agents/CTO.md](../agents/CTO.md) — Ethan charter
- [agents/CMO.md](../agents/CMO.md)
- [agents/CSO.md](../agents/CSO.md)
- [agents/CFO.md](../agents/CFO.md)
- [agents/Secretary.md](../agents/Secretary.md) — 663-line Samantha charter (canonical)

---

## 2. Engineering Deliverables

Source code, tests, packaging artifacts. Owner: CTO + 4 engineers (Leo / Maya / Ryan / Jordan). Lives in `Y-star-gov/` sibling repo + this repo's `gov_mcp/`, `scripts/`, `tests/`.

### 2.1 Source & Symlinks
- [ystar/](../ystar) → symlink to `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar`
- [gov_mcp/](../gov_mcp) — Local gov MCP server source
- [scripts/](../scripts) — 184 operational scripts (boot, hooks, CIEU helpers)
- [tests/](../tests) — 127 test files

### 2.2 Engineering Knowledge (knowledge/{cto,eng-*}/)
- [knowledge/cto/competitive_architecture.md](../knowledge/cto/competitive_architecture.md)
- [knowledge/cto/engineering_culture.md](../knowledge/cto/engineering_culture.md)
- [knowledge/cto/metalearning_technical.md](../knowledge/cto/metalearning_technical.md)
- [knowledge/cto/microsoft_deep_analysis.md](../knowledge/cto/microsoft_deep_analysis.md)
- [knowledge/cto/pre_commit_checklist.md](../knowledge/cto/pre_commit_checklist.md)
- [knowledge/cto/session_recovery_2026_03_29.md](../knowledge/cto/session_recovery_2026_03_29.md)
- [knowledge/cto/system_reliability.md](../knowledge/cto/system_reliability.md)
- [knowledge/cto/technical_community_research.md](../knowledge/cto/technical_community_research.md)
- [knowledge/cto/technical_decision_making.md](../knowledge/cto/technical_decision_making.md)
- [knowledge/cto/three_layer_architecture_2026-04-04.md](../knowledge/cto/three_layer_architecture_2026-04-04.md)
- [knowledge/cto/three_layer_architecture.md](../knowledge/cto/three_layer_architecture.md)
- [knowledge/cto/2026-04-03-session-learnings.md](../knowledge/cto/2026-04-03-session-learnings.md)
- [knowledge/eng-kernel/](../knowledge/eng-kernel) — Kernel engineer (Leo) workspace
- [knowledge/eng-governance/](../knowledge/eng-governance) — Gov engineer (Maya) workspace
- [knowledge/eng-platform/](../knowledge/eng-platform) — Platform engineer (Ryan) workspace
- [knowledge/eng-domains/](../knowledge/eng-domains) — Domain engineer (Jordan) workspace
- [knowledge/eng-governance-gap-enforcement-spec.md](../knowledge/eng-governance-gap-enforcement-spec.md)
- [knowledge/jordan/](../knowledge/jordan) — Jordan personal workspace

### 2.3 Engineering Reports (reports/cto/, reports/cti, reports/eng-*)
- [reports/cto_code_assessment.md](../reports/cto_code_assessment.md)
- [reports/cto_deep_research_findings.md](../reports/cto_deep_research_findings.md)
- [reports/cto_fix_log.md](../reports/cto_fix_log.md)
- [reports/cto_self_check_2026-04-03.md](../reports/cto_self_check_2026-04-03.md)
- [reports/cto-board-directive-008-skill-verification.md](../reports/cto-board-directive-008-skill-verification.md)
- [reports/cto/day3_plugin_packaging_20260416.md](../reports/cto/day3_plugin_packaging_20260416.md) — NEW 2026-04-16
- [reports/k9_verification_results.md](../reports/k9_verification_results.md)
- [reports/path_b_acceptance_checklist.md](../reports/path_b_acceptance_checklist.md)
- [reports/path_b_acceptance_test_results.md](../reports/path_b_acceptance_test_results.md)
- [reports/cli_test_coverage_2026-04-03.md](../reports/cli_test_coverage_2026-04-03.md)
- [reports/cli_test_coverage_executive_summary.md](../reports/cli_test_coverage_executive_summary.md)
- [reports/CLI_TEST_COVERAGE_README.md](../reports/CLI_TEST_COVERAGE_README.md)
- [reports/cli_test_priority_matrix.md](../reports/cli_test_priority_matrix.md)
- [reports/cli_test_week1_complete.md](../reports/cli_test_week1_complete.md)
- [reports/PLATFORM_DEFENSE_ANALYSIS.md](../reports/PLATFORM_DEFENSE_ANALYSIS.md)
- [reports/SECRET_EXPOSURE_VERIFICATION.md](../reports/SECRET_EXPOSURE_VERIFICATION.md)
- [reports/MCP_TOOL_POISONING_ANALYSIS.md](../reports/MCP_TOOL_POISONING_ANALYSIS.md)
- [reports/isolation_investigation_2026-04-03.md](../reports/isolation_investigation_2026-04-03.md)

---

## 3. Reports

Cross-departmental reports, daily/event/audit. CEO consolidates. New `reports/` subdirs: `cto/`, `ceo/`, `drift_hourly/`.

### 3.1 CEO Reports
- [reports/ceo_board_report_directive001_reexecution.md](../reports/ceo_board_report_directive001_reexecution.md)
- [reports/ceo_execution_plan_001.md](../reports/ceo_execution_plan_001.md)
- [reports/ceo_leadership_brief.md](../reports/ceo_leadership_brief.md)
- [reports/ceo/agent_id_audit_integrity_20260416.md](../reports/ceo/agent_id_audit_integrity_20260416.md) — NEW 2026-04-16
- [reports/ceo/campaign_v7_business_pivot_plan_20260415.md](../reports/ceo/campaign_v7_business_pivot_plan_20260415.md) — NEW
- [reports/ceo/three_dimensional_audit_rebuttal_20260416.md](../reports/ceo/three_dimensional_audit_rebuttal_20260416.md) — NEW 2026-04-16

### 3.2 Autonomous Session Summaries
- [reports/autonomous_session_2_summary.md](../reports/autonomous_session_2_summary.md)
- [reports/autonomous_session_summary.md](../reports/autonomous_session_summary.md)
- [reports/autonomous_work_2026-04-03.md](../reports/autonomous_work_2026-04-03.md)

### 3.3 Board Directives
- [reports/board_directive_001.md](../reports/board_directive_001.md)

### 3.4 Tech Debt & Gap Analyses
- [reports/design_debt_analysis_2026-04-03.md](../reports/design_debt_analysis_2026-04-03.md)
- [reports/full_system_tech_debt_2026-04-03_v2.md](../reports/full_system_tech_debt_2026-04-03_v2.md)
- [reports/full_system_tech_debt_2026-04-03.md](../reports/full_system_tech_debt_2026-04-03.md)
- [reports/gap_analysis_20260403.md](../reports/gap_analysis_20260403.md)
- [reports/tech_debt_master_plan_2026-04-03.md](../reports/tech_debt_master_plan_2026-04-03.md)
- [reports/tech_debt_master_plan_v2_complete.md](../reports/tech_debt_master_plan_v2_complete.md)
- [reports/tech_debt.md](../reports/tech_debt.md)
- [reports/tombstone_scan_20260416.md](../reports/tombstone_scan_20260416.md) — NEW 2026-04-16

### 3.5 Experiment Reports
- [reports/EXP_001_reproducible_code.md](../reports/EXP_001_reproducible_code.md)
- [reports/YstarCo_EXP_001_Controlled_Experiment_Report.md](../reports/YstarCo_EXP_001_Controlled_Experiment_Report.md)
- [reports/V1_EXPERIMENT_PLAN.md](../reports/V1_EXPERIMENT_PLAN.md)
- [reports/V1_LAYER_REPORTS.md](../reports/V1_LAYER_REPORTS.md)
- [reports/SIM-001_measurement_framework.md](../reports/SIM-001_measurement_framework.md)
- [reports/SIM-001_tech_risk_audit.md](../reports/SIM-001_tech_risk_audit.md)
- [reports/SIM-001_user_journey_scripts.md](../reports/SIM-001_user_journey_scripts.md)
- [reports/pretrain_verification_2026-04-05.md](../reports/pretrain_verification_2026-04-05.md)

### 3.6 CMO/CSO/CFO Reports
- [reports/cmo_market_perspective.md](../reports/cmo_market_perspective.md)
- [reports/market_demand_analysis.md](../reports/market_demand_analysis.md)
- [reports/MARKET_INTEL_DRAFT.md](../reports/MARKET_INTEL_DRAFT.md)
- [reports/MARKET_INTEL_FINAL.md](../reports/MARKET_INTEL_FINAL.md)
- [reports/SHOW_HN_POSITIONING.md](../reports/SHOW_HN_POSITIONING.md)
- [reports/X_API_EVALUATION.md](../reports/X_API_EVALUATION.md)
- [reports/VS_LANGSMITH_COMPARISON.md](../reports/VS_LANGSMITH_COMPARISON.md)
- [reports/notebooklm_plan_ceo.md](../reports/notebooklm_plan_ceo.md)
- [reports/notebooklm_plan_cfo.md](../reports/notebooklm_plan_cfo.md)
- [reports/notebooklm_plan_cmo.md](../reports/notebooklm_plan_cmo.md)
- [reports/notebooklm_plan_cso.md](../reports/notebooklm_plan_cso.md)
- [reports/notebooklm_plan_cto.md](../reports/notebooklm_plan_cto.md)

### 3.7 Drift / Hourly Audit
- [reports/drift_hourly/20260416_0100.md](../reports/drift_hourly/20260416_0100.md) — NEW
- [reports/drift_hourly/20260416_0400.md](../reports/drift_hourly/20260416_0400.md) — NEW

### 3.8 Org & Architecture
- [reports/org_design_v1.md](../reports/org_design_v1.md)
- [reports/ystar_gov_deep_research_report.md](../reports/ystar_gov_deep_research_report.md)
- [reports/ystar_governance_report_001.md](../reports/ystar_governance_report_001.md)
- [reports/proposal_obligation_triggers.md](../reports/proposal_obligation_triggers.md)
- [reports/patent_ystar_t_provisional_draft.md](../reports/patent_ystar_t_provisional_draft.md)

---

## 4. Lessons & Methodology

Distilled methodology assets. CEO/CMO/CSO/CFO/CTO knowledge bases + cross-role lessons. Owner: each role-lead + Secretary curates index.

### 4.1 CEO Knowledge
- [knowledge/ceo/bootstrap_guide.md](../knowledge/ceo/bootstrap_guide.md)
- [knowledge/ceo/CEO_MISSION_FRAMEWORK.md](../knowledge/ceo/CEO_MISSION_FRAMEWORK.md)
- [knowledge/ceo/chatgpt_codebase_analysis_reconciliation.md](../knowledge/ceo/chatgpt_codebase_analysis_reconciliation.md)
- [knowledge/ceo/cieu_liveness_guide.md](../knowledge/ceo/cieu_liveness_guide.md)
- [knowledge/ceo/current_status.md](../knowledge/ceo/current_status.md)
- [knowledge/ceo/decision_making.md](../knowledge/ceo/decision_making.md)
- [knowledge/ceo/methodology_convergence.md](../knowledge/ceo/methodology_convergence.md)
- [knowledge/ceo/methodology_v1.md](../knowledge/ceo/methodology_v1.md)
- [knowledge/ceo/organization_building.md](../knowledge/ceo/organization_building.md)
- [knowledge/ceo/session_recovery_2026_03_29.md](../knowledge/ceo/session_recovery_2026_03_29.md)
- [knowledge/ceo/strategy_frameworks.md](../knowledge/ceo/strategy_frameworks.md)
- [knowledge/ceo/team_dna.md](../knowledge/ceo/team_dna.md)
- [knowledge/ceo/threat_landscape_2026_03.md](../knowledge/ceo/threat_landscape_2026_03.md)
- [knowledge/ceo/strategy/STRAT-001_governance_moat_vs_bounty_speed_20260416.md](../knowledge/ceo/strategy/STRAT-001_governance_moat_vs_bounty_speed_20260416.md) — **[STRAT-001]** Governance Moat vs Bounty Speed (2026-04-16) — when CZL governance is competitive moat vs disadvantage, market positioning recommendations (trust-race over speed-race), governance-as-data secondary monetization

### 4.2 CFO Knowledge
- [knowledge/cfo/burn_rate_calculation.md](../knowledge/cfo/burn_rate_calculation.md)
- [knowledge/cfo/pricing_strategy.md](../knowledge/cfo/pricing_strategy.md)
- [knowledge/cfo/saas_metrics.md](../knowledge/cfo/saas_metrics.md)
- [knowledge/cfo/token_recording_guide.md](../knowledge/cfo/token_recording_guide.md)
- [knowledge/cfo/unit_economics.md](../knowledge/cfo/unit_economics.md)

### 4.3 CMO Knowledge
- [knowledge/cmo/content_strategy.md](../knowledge/cmo/content_strategy.md)
- [knowledge/cmo/developer_marketing.md](../knowledge/cmo/developer_marketing.md)
- [knowledge/cmo/hn_writing_guide.md](../knowledge/cmo/hn_writing_guide.md)
- [knowledge/cmo/platform_research_jinjin_2026_03_30.md](../knowledge/cmo/platform_research_jinjin_2026_03_30.md)
- [knowledge/cmo/positioning_framework.md](../knowledge/cmo/positioning_framework.md)
- [knowledge/cmo/real_world_operations_research.md](../knowledge/cmo/real_world_operations_research.md)
- [knowledge/cmo/session_recovery_2026_03_29.md](../knowledge/cmo/session_recovery_2026_03_29.md)
- [knowledge/cmo/theory/deployment_planning.md](../knowledge/cmo/theory/deployment_planning.md) — NEW

### 4.4 CSO Knowledge
- [knowledge/cso/developer_led_growth.md](../knowledge/cso/developer_led_growth.md)
- [knowledge/cso/enterprise_sales_process.md](../knowledge/cso/enterprise_sales_process.md)
- [knowledge/cso/patent_law_knowhow.md](../knowledge/cso/patent_law_knowhow.md)
- [knowledge/cso/qualification_frameworks.md](../knowledge/cso/qualification_frameworks.md)
- [knowledge/cso/user_engagement_research.md](../knowledge/cso/user_engagement_research.md)

### 4.5 Cases (Lessons from Failures)
- [knowledge/cases/CASE_001_CMO_fabrication.md](../knowledge/cases/CASE_001_CMO_fabrication.md)
- [knowledge/cases/CASE_002_CFO_fabrication.md](../knowledge/cases/CASE_002_CFO_fabrication.md)
- [knowledge/cases/CASE_003_baseline_not_triggered.md](../knowledge/cases/CASE_003_baseline_not_triggered.md)
- [knowledge/cases/CASE_004_directive_subtasks_lost.md](../knowledge/cases/CASE_004_directive_subtasks_lost.md)
- [knowledge/cases/CASE_005_cross_model_governance.md](../knowledge/cases/CASE_005_cross_model_governance.md)
- [knowledge/cases/CASE_006_content_too_long.md](../knowledge/cases/CASE_006_content_too_long.md)
- [knowledge/cases/README.md](../knowledge/cases/README.md)

### 4.6 Bootstrap & Emergency
- [knowledge/bootstrap_log.md](../knowledge/bootstrap_log.md)
- [knowledge/emergency_procedures.md](../knowledge/emergency_procedures.md)

### 4.7 Secretary Knowledge & Shared
- [knowledge/secretary/](../knowledge/secretary) — Role definition, SOP, cases, gaps
- [knowledge/shared/](../knowledge/shared) — Cross-role shared assets (e.g., unified_work_protocol_20260415.md)

---

## 5. Decisions

Board-level decisions, archived per `agents/Secretary.md §决策记录流程`.

### 5.1 Decision Records (knowledge/decisions/)
- [knowledge/decisions/2026_04_16/session_decisions_summary.md](../knowledge/decisions/2026_04_16/session_decisions_summary.md) — **2026-04-16 CZL session**: Campaign v6 close-out (W1-W11), Action Model v2 + Restart Preparation Model (constitutional), Reply Taxonomy blacklist-to-whitelist shift, Formal Methods 6-layer stack, trust ladder normalize + 9 engineer charter fix, 5 engineer gauntlets, 3-dimensional governance audit
- [knowledge/decisions/2026_04_09_board_pending_history_archive.md](../knowledge/decisions/2026_04_09_board_pending_history_archive.md)
- [knowledge/decisions/2026-04-05_discord_token.md](../knowledge/decisions/2026-04-05_discord_token.md)
- [knowledge/decisions/30day_mining_plant_2026-04-15/](../knowledge/decisions/30day_mining_plant_2026-04-15)

### 5.2 Current Tasks Ledger
- [knowledge/CURRENT_TASKS.md](../knowledge/CURRENT_TASKS.md)

### 5.3 Charter Amendments (cross-referenced from §1.2)
See `governance/BOARD_CHARTER_AMENDMENTS.md` for AMENDMENT-001 through current.

---

## 6. Memory & Continuity

Session memory, handoffs, world state. Owner: Secretary + auto-snapshots from boot/close hooks.

### 6.1 Active Memory (memory/)
- [memory/INDEX.md](../memory/INDEX.md)
- [memory/WORLD_STATE.md](../memory/WORLD_STATE.md)
- [memory/continuation.json](../memory/continuation.json)
- [memory/session_summary_20260415.md](../memory/session_summary_20260415.md)
- [memory/session_summary_20260416.md](../memory/session_summary_20260416.md) — NEW
- [memory/working_memory_snapshot_roundtrip_test.json](../memory/working_memory_snapshot_roundtrip_test.json)
- [memory/archive/](../memory/archive)
- [memory/boot_packages/](../memory/boot_packages) — Per-role boot bundles (AMENDMENT-010 11-category)
- [memory/claude_code_memory_mirror/](../memory/claude_code_memory_mirror)

### 6.2 Roadmap
- [roadmap/GOV_A2A_plan.md](../roadmap/GOV_A2A_plan.md)
- [roadmap/SIM-001_product_gaps.md](../roadmap/SIM-001_product_gaps.md)

---

## 7. Theory Papers & Whitepaper

Academic-grade artifacts: arxiv drafts, whitepapers, patent.

### 7.1 Arxiv Papers
- [content/arxiv/PAPER_COMPLETE_BRIEF.md](../content/arxiv/PAPER_COMPLETE_BRIEF.md)
- [content/arxiv/path_a_paper_outline.md](../content/arxiv/path_a_paper_outline.md)
- [content/arxiv/pearl_architecture_argument.md](../content/arxiv/pearl_architecture_argument.md)

### 7.2 Whitepapers
- [content/whitepaper/enterprise_compliance_audit_trails.md](../content/whitepaper/enterprise_compliance_audit_trails.md)

### 7.3 Patent
- See §3.8 [reports/patent_ystar_t_provisional_draft.md](../reports/patent_ystar_t_provisional_draft.md)

### 7.4 Product Documentation (content/product/, products/)
- [content/product/architecture_onepage.md](../content/product/architecture_onepage.md)
- [content/product/integrated_demo.md](../content/product/integrated_demo.md)
- [content/product/integration_quickstart.md](../content/product/integration_quickstart.md)
- [content/product/path_a_demo_package.md](../content/product/path_a_demo_package.md)
- [content/product/path_a_demo.md](../content/product/path_a_demo.md)
- [content/product/path_b_demo.md](../content/product/path_b_demo.md)
- [products/](../products) — `ystar-gov/` product docs root

---

## 8. Sales & External Content

External-facing content: blog, articles, social, outreach, sales collateral. Owner: CMO + CSO.

### 8.1 Articles (content/articles/)
- [content/articles/001_what_is_ystar_code_review.md](../content/articles/001_what_is_ystar_code_review.md)
- [content/articles/001_what_is_ystar.md](../content/articles/001_what_is_ystar.md)
- [content/articles/002_EXP001_HN_ready.md](../content/articles/002_EXP001_HN_ready.md)
- [content/articles/003_what_is_ystar_HN_ready.md](../content/articles/003_what_is_ystar_HN_ready.md)
- [content/articles/004_contract_validity_HN_draft.md](../content/articles/004_contract_validity_HN_draft.md)
- [content/articles/004_omission_detection_code_review.md](../content/articles/004_omission_detection_code_review.md)
- [content/articles/004_omission_detection_SAVED_for_series4.md](../content/articles/004_omission_detection_SAVED_for_series4.md)
- [content/articles/005_ab_experiment_report.md](../content/articles/005_ab_experiment_report.md)
- [content/articles/005_ast_whitelisting_HN_draft.md](../content/articles/005_ast_whitelisting_HN_draft.md)
- [content/articles/series2_ceo_false_completion_draft.md](../content/articles/series2_ceo_false_completion_draft.md)
- [content/articles/series3_jinjin_cross_model_draft.md](../content/articles/series3_jinjin_cross_model_draft.md)
- [content/articles/series5_code_verification.md](../content/articles/series5_code_verification.md)
- [content/articles/series5_cto_summary.md](../content/articles/series5_cto_summary.md)

### 8.2 Blog Posts (content/blog/)
- [content/blog/001-introducing-ystar-gov.md](../content/blog/001-introducing-ystar-gov.md)
- [content/blog/001-linkedin-announcement.md](../content/blog/001-linkedin-announcement.md)
- [content/blog/launch_post_draft.md](../content/blog/launch_post_draft.md)

### 8.3 Social (LinkedIn / X / Telegram)
- [content/linkedin/001_company_founding.md](../content/linkedin/001_company_founding.md)
- [content/linkedin/2026-04-05_cmo_first_day_v2.md](../content/linkedin/2026-04-05_cmo_first_day_v2.md)
- [content/linkedin/2026-04-05_cmo_first_day.md](../content/linkedin/2026-04-05_cmo_first_day.md)
- [content/x_twitter/10_HIGHLIGHTS.md](../content/x_twitter/10_HIGHLIGHTS.md)
- [content/x_twitter/2026-04-05_day11.md](../content/x_twitter/2026-04-05_day11.md)
- [content/x_twitter/CONTENT_STRATEGY.md](../content/x_twitter/CONTENT_STRATEGY.md)
- [content/x_twitter/CSO_TARGET_ACCOUNTS.md](../content/x_twitter/CSO_TARGET_ACCOUNTS.md)
- [content/x_twitter/daily_template.md](../content/x_twitter/daily_template.md)
- [content/x_twitter/THREAD_01_cmo_fabrication.md](../content/x_twitter/THREAD_01_cmo_fabrication.md)
- [content/telegram/2026-04-05_first_autonomous.md](../content/telegram/2026-04-05_first_autonomous.md)

### 8.4 Outreach (content/outreach/)
- [content/outreach/journalist_pitch.md](../content/outreach/journalist_pitch.md)
- [content/outreach/product_hunt_plan.md](../content/outreach/product_hunt_plan.md)
- [content/outreach/show_hn_v048.md](../content/outreach/show_hn_v048.md)

### 8.5 Content Pipeline & Strategy
- [content/article_pipeline.md](../content/article_pipeline.md)
- [content/article_series_plan_v2.md](../content/article_series_plan_v2.md)
- [content/article_series_plan.md](../content/article_series_plan.md)
- [content/cmo_k9audit_content_ideas.md](../content/cmo_k9audit_content_ideas.md)
- [content/cto_concept_scan.md](../content/cto_concept_scan.md)
- [content/real_events_inventory.md](../content/real_events_inventory.md)

### 8.6 Drafts (drafts/)
- [drafts/DOMAIN_REGISTRATION.md](../drafts/DOMAIN_REGISTRATION.md)
- [drafts/FRONTEND_EVALUATION.md](../drafts/FRONTEND_EVALUATION.md)
- [drafts/FRONTEND_PROMOTION_PLAN.md](../drafts/FRONTEND_PROMOTION_PLAN.md)
- [drafts/MANIFESTO_v2.md](../drafts/MANIFESTO_v2.md)
- [drafts/MANIFESTO.md](../drafts/MANIFESTO.md)
- [drafts/MARKET_RESEARCH_ALLIES.md](../drafts/MARKET_RESEARCH_ALLIES.md)
- [drafts/README_REWRITE.md](../drafts/README_REWRITE.md)

### 8.7 Sales & Marketing Collateral
- [sales/](../sales) — CRM + sales materials
- [marketing/](../marketing) — Marketing assets
- [finance/](../finance) — Financial models (CFO domain)

---

# Lookup Cheatsheet

| Need | Section |
|---|---|
| Constitutional rule / amendment | §1 |
| Code, tests, engineering report | §2 |
| Daily/event/audit report | §3 |
| Methodology, lessons, role knowledge | §4 |
| Board decision record | §5 |
| Session memory, handoff, world state | §6 |
| Whitepaper, arxiv, patent, product doc | §7 |
| External content, blog, social, sales | §8 |
