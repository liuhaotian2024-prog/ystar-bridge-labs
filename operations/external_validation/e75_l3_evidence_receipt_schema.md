# E75 L3 Evidence Receipt Schema

- Status: template_only_no_execution
- Real receipts generated in E75: false

## Fields
- `source_id`: stable internal id for the source
- `source_title`: public source title
- `source_url_or_locator`: URL or public locator; no private locator
- `source_category`: must match owner-approved allowlist category
- `access_mode`: public_read_only
- `access_time`: UTC timestamp for future E76 read
- `public_read_only_confirmed`: boolean
- `login_required`: boolean, must be false unless owner explicitly approves a special case
- `interaction_required`: boolean, must be false
- `evidence_type`: market_language, category_presence, pricing_analog, demand_proxy, behavior_proxy, or exclusion
- `relevant_claims_supported`: bounded list of supported hypotheses
- `quote_or_summary_boundary`: short quote or summary limit, copyright-safe
- `risk_flags`: overclaim, login, contact, paywall, privacy, relevance, or none
- `allowed_by_owner_scope`: boolean
- `included_in_synthesis`: boolean
- `exclusion_reason`: required if excluded
