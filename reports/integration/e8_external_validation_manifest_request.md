# E8 External Validation Manifest Status / Request

- manifest_status: missing
- external_validation_authorized: false
- exact_owner_action: create `operations/external_validation/e8_external_validation_manifest.json` from the template with exact count/channel/target/draft/stop conditions.

## Template
```json
{
  "manifest_id": "e8_manifest_owner_to_fill",
  "approved_by": "OWNER_NAME_REQUIRED",
  "approved_at": "YYYY-MM-DDTHH:MM:SSZ",
  "top_offer": "48h AI Ops Operating Room Blueprint",
  "validation_mode": "owner_operated_3_person_qualitative_validation",
  "autonomy_budget": {
    "budget_id": "e8_standard_3_person_validation",
    "max_external_messages": 3,
    "max_public_posts": 0,
    "max_landing_pages": 0,
    "max_followups_per_target": 0,
    "max_targets": 3,
    "allowed_risk_tiers": [
      "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION"
    ],
    "allowed_channels": [
      "owner_selected_email",
      "owner_selected_dm"
    ],
    "expires_at": "2026-05-08T23:59:59Z",
    "stop_conditions": [
      "any target opts out",
      "message count reaches budget",
      "draft hash changes",
      "recipient asks for no further contact",
      "owner pauses validation"
    ],
    "require_human_review_before_send": true,
    "allow_aiden_execution": false,
    "allow_owner_operated_handoff": true
  },
  "approved_draft_ids": [
    "e8_ai_disclosed_outreach_draft"
  ],
  "approved_target_seed_ids": [
    "target_001",
    "target_002",
    "target_003"
  ],
  "approved_channels": [
    "owner_selected_email"
  ],
  "allowed_action_types": [
    "send_validation_message",
    "request_feedback"
  ],
  "forbidden_action_types": [
    "collect_payment",
    "create_account",
    "submit_form",
    "execute_contract",
    "production_implementation",
    "core_writeback"
  ],
  "ai_disclosure_required": true,
  "opt_out_required": true,
  "no_scraped_leads": true,
  "no_bulk_outreach": true,
  "notes": "Owner must replace placeholders. This template does not authorize execution."
}
```
