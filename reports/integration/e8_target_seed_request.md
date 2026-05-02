# E8 Target Seed Status / Request

- target_seed_status: missing
- external_contact_authorized: false
- exact_owner_action: create `operations/external_validation/e8_target_seeds.json` from the template with real owner-provided non-scraped targets.

## Template
```json
{
  "targets": [
    {
      "target_id": "target_001",
      "target_type": "known_contact",
      "name_or_label": "Owner-provided technical founder or AI-heavy team lead",
      "channel": "owner_selected_email",
      "contact_handle_or_address": "OWNER_TO_FILL",
      "relationship_context": "Owner-provided known contact; not scraped.",
      "why_relevant": "Potential buyer/feedback source for 48h AI Ops Operating Room Blueprint.",
      "approved_for_contact": true,
      "allowed_message_count": 1,
      "opt_out_state": false,
      "notes": "Template only; not approval until owner creates e8_target_seeds.json."
    },
    {
      "target_id": "benchmark_001",
      "target_type": "internal_benchmark_proxy",
      "name_or_label": "Internal benchmark workflow sample",
      "channel": "internal",
      "contact_handle_or_address": "",
      "relationship_context": "No external contact.",
      "why_relevant": "Can test the offer without customer contact.",
      "approved_for_contact": false,
      "allowed_message_count": 0,
      "opt_out_state": false,
      "notes": "Safe internal proxy."
    }
  ]
}
```
