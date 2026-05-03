# B2R Progressive Capability Unlock

## Level 0: internal_only
- domains: internal only
- owner role: not a micro-operator
- stop conditions: dirty repo, test failure

## Level 1: public_read_only
- domains: public_readonly_observation
- owner role: sets research boundary
- stop conditions: login required, private data

## Level 2: authenticated_read_only
- domains: authenticated_readonly_observation
- owner role: approves account constitution
- stop conditions: credential missing, MFA required, write scope

## Level 3: authenticated_draft_or_form_fill
- domains: authenticated_draft_creation, form_fill_draft, publication_draft
- owner role: approves channel constitution
- stop conditions: submit required, public visibility

## Level 4: low_risk_submit_or_publication
- domains: low_risk_form_submission, governed_publication, low_risk_account_creation
- owner role: hard exceptions only
- stop conditions: high claim, regulated form, payment required

## Level 5: external_validation_messaging
- domains: external_validation_message, feedback_capture
- owner role: sets validation constitution
- stop conditions: opt-out, negative feedback, complaint

## Level 6: financial_legal_customer_system_core_writeback_hard_gate
- domains: payment_or_contract_gate, core_writeback_gate
- owner role: explicit hard approval required
- stop conditions: payment, contract, legal, customer system, core writeback
