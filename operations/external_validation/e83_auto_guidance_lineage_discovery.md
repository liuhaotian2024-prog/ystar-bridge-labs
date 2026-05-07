# E83 Auto Guidance Lineage Discovery

- Artifact: `e83_auto_guidance_lineage_discovery`
- Job: `e83_ystar_gov_autoguidance_semantics_correct_path_integration_R1_20260507T000001Z`
- Repository-discovered correct-path name: `REQUIRE_REVISION`

## Mechanisms
- `ystar_pre_u_require_revision` (Y-star-gov): ['allow', 'warn', 'require_revision', 'escalate', 'deny']
- `ystar_cieu_delta_require_revision` (Y-star-gov): ['allow', 'warn', 'require_revision', 'escalate', 'deny']
- `ystar_hook_contract_require_revision` (Y-star-gov): ['allow', 'warn', 'require_revision', 'deny', 'escalate']
- `ystar_openclaw_redirect_rewrite` (Y-star-gov): ['allow', 'deny', 'escalate', 'redirect', 'invoke', 'inject', 'auto_post', 'rewrite']
- `bridge_labs_review_gated_action_semantics` (bridge-labs): ['ALLOW_INTERNAL', 'REVIEW_GATED', 'NEEDS_OWNER_APPROVAL', 'BLOCKED']
- `gov_mcp_company_preflight_and_provider_promotion` (gov-mcp): ['approve', 'reject', 'request_revision', 'hold', 'promotion_allowed', 'dry_run_denied']

## Safety
- No external action, outreach, publication, payment, L4 execution, or L5 readiness claim.
- No K9Audit/gov-mcp mutation and no parallel Y-star-gov governance engine.
