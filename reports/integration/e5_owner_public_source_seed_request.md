# E5 Owner Public Source Seed Request

E5 can run source-seeded public page-read research without a search provider, but only if owner-approved public URLs are provided.

Please provide 10-20 public, no-login URLs. These seed URLs authorize only read-only public page inspection; they do not authorize customer contact.

## Requested Opportunity Families
- MCP/tool-use boundary/security
- coding-agent governance
- AI workflow bottleneck
- founder decision-support
- AI incident/postmortem
- AI ops implementation
- partner enablement
- open-source paid support
- agent team onboarding/training
- content-to-lead diagnostic

## Seed JSON Location
- `research/public_source_seeds/e5_public_source_seeds.json`

## Required Fields Per Seed
- seed_id
- url
- opportunity_family
- relevant_opportunity_ids
- source_category
- evidence_sought
- owner_approved: true

## Forbidden
- login
- customer_contact
- email_or_message
- publication
- form_submission
- payment
- account_creation
- paywall_bypass
- private_data_scraping
- secret_or_env_value_reading
- core_db_writeback
- obligation_registration
