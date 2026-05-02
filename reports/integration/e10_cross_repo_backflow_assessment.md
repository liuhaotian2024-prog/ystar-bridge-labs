# E10 Cross-Repo Backflow Assessment

E10 completed the autonomous buyer discovery capability inside bridge-labs Mission Command. The formal governance/runtime repos already provide the policy and preflight substrate, so E10 should not directly modify Y-star-gov or gov-mcp in this milestone.

## Inspected Formal Repos
- Y-star-gov current branch inspected: `backflow/company-runtime-domain-pack`
- Y-star-gov requested branch also inspected by snapshot: `backflow/company-runtime-policy-alignment`
- gov-mcp current branch inspected: `backflow/company-runtime-tools`
- gov-mcp requested branch also inspected by snapshot: `backflow/company-runtime-tool-alignment`

## Y-star-gov Findings
- `permission_tiers.py` defines Tier 0 internal work, Tier 1 read-only external research with budget, Tier 2 preparation-only owner-approved execution, Tier 3 constrained external action, and Tier 4 high-risk blocked/review-gated action.
- `company_action_classifier.py` treats read-only research/public page reads as internal/read-only preparation, customer contact/email/outreach/publication/form/account/live MCP as owner-approval required, and payment/secrets/private runtime artifacts/bulk outreach/lead scraping as blocked.
- `company_runtime_policy.py` checks mission budget for search/public page/read-only research and returns non-executing preflight decisions.
- `escalation_contract.py` supports approve/reject/request_revision/hold escalation envelopes without executing external actions.

## gov-mcp Findings
- `gov_mcp/company_runtime_tools.py` exposes `gov_company_action_preflight`, `gov_company_mission_check`, `gov_company_escalation_check`, `gov_company_record_owner_decision`, `gov_company_admin_rule_check`, `gov_company_value_alignment_check`, and `gov_company_mission_action_preflight`.
- The tools normalize company-runtime decisions and explicitly report `external_action_executed: false`.
- `tests/test_company_runtime_tools.py` verifies internal allowance, email/contact owner approval, payment blocking, budget checks, escalation checks, and non-persistent owner-decision envelopes.

## Candidate Mechanisms For Y-star-gov
- autonomous target discovery policy: define public evidence discovery as Tier 1 when budgeted and no personal scraping/contact occurs.
- proposed vs approved target seed distinction: add a formal `proposed_target_seed` class that cannot authorize contact.
- buyer signal taxonomy: standardize pain, budget, urgency, tool-stack complexity, governance/safety, hiring/job, implementation burden, alternatives, contactability, trust gap, and disconfirming signals.
- target candidate safety policy: require `discovered_by_aiden=true`, `owner_approved_for_contact=false`, `contact_executed=false`, public evidence refs, and no personal contact scraping.
- shortest revenue path scoring governance: treat ranking as M-3 planning evidence, not validation feedback or paid signal.
- owner approval semantics for discovered targets: any transition from proposed target to approved contact must specify target, channel, message/draft hash, count, stop conditions, and execution mode.

## Candidate Mechanisms For gov-mcp
- target discovery preflight: classify autonomous target discovery as Tier 1 read-only when bounded by research budget and no contact.
- target seed proposal validation: verify proposed seeds are public-source-backed and not contact-approved.
- validation batch approval check: verify batch ID, target IDs, draft hash, channel, count, and stop conditions before E11 execution.
- suppression / opt-out check: ensure proposed or approved targets are not opted out or over duplicate limits.
- no-contact assurance tool: confirm a discovery cycle produced no external sending/customer contact/publication/form/payment/account action.
- proposed manifest normalization: convert bridge-labs proposals into owner-reviewable manifest templates without treating them as approval.

## Bridge-Labs Ownership For E10
- Keep E10 buyer signal extraction, candidate registry, scoring, batch proposals, proposed manifest/target seeds, and owner decision packet in bridge-labs for now.
- Use Y-star-gov/gov-mcp only as policy/preflight references until E11 needs formal approval/execution tooling.
- Do not modify Y-star-gov or gov-mcp in E10; backflow should happen as a separate governance/tool-alignment milestone after the bridge-labs behavior stabilizes.

## Recommended Later Backflow Order
1. Add proposed-vs-approved target seed semantics to Y-star-gov company runtime policy.
2. Add gov-mcp validation tools for proposed target seed and validation batch preflight.
3. Add suppression/no-contact assurance checks to gov-mcp before any E11 execution provider is allowed.
4. Backfill cross-repo tests proving proposed target seeds cannot authorize customer contact by themselves.
