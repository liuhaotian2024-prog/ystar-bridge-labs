# E1.5 Action-Wide Preflight Report

Every proposed mission action below was inventoried and preflighted. No action was executed externally.

## Summary
```json
{
  "total_actions": 41,
  "decision_counts": {
    "ALLOW_INTERNAL": 16,
    "NEEDS_OWNER_APPROVAL": 11,
    "BLOCKED": 1,
    "REVIEW_GATED": 13
  },
  "all_actions_preflighted": true,
  "external_action_executed": false
}
```

## Action-Wide Governance Preflight Table
| action_id | source | class | decision | title | external_action_executed |
| --- | --- | --- | --- | --- | --- |
| action_001 | autonomous_internal_actions | internal_autonomous | ALLOW_INTERNAL | Build a 7-day first-revenue decision brief. | False |
| action_002 | autonomous_internal_actions | internal_autonomous | ALLOW_INTERNAL | Compare top money paths using repo evidence and current capabilities. | False |
| action_003 | autonomous_internal_actions | internal_autonomous | ALLOW_INTERNAL | Draft buyer archetypes and offer language for owner review. | False |
| action_004 | autonomous_internal_actions | internal_autonomous | ALLOW_INTERNAL | Prepare read-only research plan within budget. | False |
| action_005 | autonomous_internal_actions | external_or_approval_gated | NEEDS_OWNER_APPROVAL | Create approval packet for any external action, but do not execute it. | False |
| action_006 | approval_needed_actions | external_or_approval_gated | NEEDS_OWNER_APPROVAL | customer contact / select exact external recipient | False |
| action_007 | approval_needed_actions | external_or_approval_gated | NEEDS_OWNER_APPROVAL | send email/message | False |
| action_008 | approval_needed_actions | external_or_approval_gated | NEEDS_OWNER_APPROVAL | publish public content | False |
| action_009 | approval_needed_actions | external_or_approval_gated | NEEDS_OWNER_APPROVAL | quote price externally | False |
| action_010 | approval_needed_actions | external_or_approval_gated | BLOCKED | create payment path | False |
| action_011 | approval_needed_actions | core_writeback_review_gated | REVIEW_GATED | write to core DB/brain/memory/CIEU | False |
| action_012 | team_task | external_or_approval_gated | NEEDS_OWNER_APPROVAL | Aiden Liu: Frame the owner goal, recommend the default path, and keep all external actions approval-gated. Output: Owner decision brief | False |
| action_013 | team_task | internal_autonomous | ALLOW_INTERNAL | Sofia Blake: Turn the first-revenue offer into clear founder/operator language without publication. Output: Review-only positioning and manual message draft | False |
| action_014 | team_task | internal_autonomous | ALLOW_INTERNAL | Marco Rivera: Compare $750 / $1500 / $3000 diagnostic pricing as hypotheses and define validation signals. Output: Pricing hypothesis and cash-signal criteria | False |
| action_015 | team_task | external_or_approval_gated | NEEDS_OWNER_APPROVAL | Zara Johnson: Define no-contact buyer archetypes and the approval gate for any later outreach. Output: Buyer archetype review and approval-needed action list | False |
| action_016 | team_task | internal_autonomous | ALLOW_INTERNAL | Ethan Wright: Define the audit/brief delivery checklist and what can be delivered manually in 7 days. Output: Delivery checklist and feasibility boundary | False |
| action_017 | team_task | external_or_approval_gated | ALLOW_INTERNAL | Jinjin / K9 Scout: Prepare budgeted read-only research questions and evidence fields; do not contact anyone. Output: Read-only research plan | False |
| action_018 | team_task | residual_review_candidate | REVIEW_GATED | Samantha Lin: Record mission decisions, avoided admin burden, approval needs, and residual candidates. Output: Mission receipt and decision log | False |
| action_019 | team_task | internal_autonomous | ALLOW_INTERNAL | Leo / Maya / Ryan / Jordan: Support reusable checklist/tooling only after the offer path is selected. Output: Implementation support notes | False |
| action_020 | experiment_48h_internal | internal_autonomous | ALLOW_INTERNAL | 48h internal diagnosis template for a messy AI-team workflow. | False |
| action_021 | experiment_tier1_research | external_or_approval_gated | NEEDS_OWNER_APPROVAL | Collect public pain-language and pricing-reference evidence under explicit Tier 1 budget; no login, no contact, no submit. | False |
| action_022 | experiment_external_validation | internal_autonomous | ALLOW_INTERNAL | Prepare exact manual-send validation draft for Agent Workflow Bottleneck Diagnosis; owner must approve target, content, and boundary before any send. | False |
| action_023 | experiment_48h_internal | internal_autonomous | ALLOW_INTERNAL | 48h internal sample audit brief using a fictional founder workflow scenario. | False |
| action_024 | experiment_tier1_research | external_or_approval_gated | NEEDS_OWNER_APPROVAL | Collect public pain-language and pricing-reference evidence under explicit Tier 1 budget; no login, no contact, no submit. | False |
| action_025 | experiment_external_validation | internal_autonomous | ALLOW_INTERNAL | Prepare exact manual-send validation draft for Founder AI Workflow Audit / CEO Command Brief; owner must approve target, content, and boundary before any send. | False |
| action_026 | experiment_48h_internal | internal_autonomous | ALLOW_INTERNAL | 48h package the smallest support offer and sample before/after. | False |
| action_027 | experiment_tier1_research | external_or_approval_gated | NEEDS_OWNER_APPROVAL | Collect public pain-language and pricing-reference evidence under explicit Tier 1 budget; no login, no contact, no submit. | False |
| action_028 | experiment_external_validation | internal_autonomous | ALLOW_INTERNAL | Prepare exact manual-send validation draft for Governance Template Paid Support; owner must approve target, content, and boundary before any send. | False |
| action_029 | obligation_draft | obligation_dry_run | REVIEW_GATED | Obligation dry-run draft: Mission owner decision brief | False |
| action_030 | obligation_draft | obligation_dry_run | REVIEW_GATED | Obligation dry-run draft: Aiden Liu mission task | False |
| action_031 | obligation_draft | obligation_dry_run | REVIEW_GATED | Obligation dry-run draft: Sofia Blake mission task | False |
| action_032 | obligation_draft | obligation_dry_run | REVIEW_GATED | Obligation dry-run draft: Marco Rivera mission task | False |
| action_033 | obligation_draft | obligation_dry_run | REVIEW_GATED | Obligation dry-run draft: Zara Johnson mission task | False |
| action_034 | obligation_draft | obligation_dry_run | REVIEW_GATED | Obligation dry-run draft: Ethan Wright mission task | False |
| action_035 | obligation_draft | obligation_dry_run | REVIEW_GATED | Obligation dry-run draft: Jinjin / K9 Scout mission task | False |
| action_036 | obligation_draft | obligation_dry_run | REVIEW_GATED | Obligation dry-run draft: Samantha Lin mission task | False |
| action_037 | obligation_draft | obligation_dry_run | REVIEW_GATED | Obligation dry-run draft: Leo / Maya / Ryan / Jordan mission task | False |
| action_038 | residual_candidate | external_or_approval_gated | NEEDS_OWNER_APPROVAL | Residual review candidate: opp_external_pain_agent_bottleneck | False |
| action_039 | residual_candidate | residual_review_candidate | REVIEW_GATED | Residual review candidate: opp_internal_asset_founder_audit | False |
| action_040 | residual_candidate | residual_review_candidate | REVIEW_GATED | Residual review candidate: opp_low_burden_template_support | False |
| action_041 | next_executable_u | internal_autonomous | ALLOW_INTERNAL | Within 48h, build a one-page comparison brief and one sample deliverable for the top two opportunities, then ask the owner to approve or revise a Tier 1 read-only evidence mission. | False |
