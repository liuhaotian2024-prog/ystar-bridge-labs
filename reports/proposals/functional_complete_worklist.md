# Y*gov Functional-Complete Worklist
# Source: ChatGPT module-level audit + team F1-F6 + team consensus
# Date: 2026-03-31

## Three Constraints (from Chairman)
1. Foundation first — no upper-layer bypass
2. I/O independent — not bound to any specific agent runtime
3. Minimal hardcoding — adaptive parameters wherever possible

---

## Wave 1: In Progress (CTO F1-F6)

| # | Task | Status |
|---|------|--------|
| F1 | Path A hardcoded → PathAPolicy | 🔄 CTO executing |
| F2 | Path B hardcoded → PathBPolicy | 🔄 CTO executing |
| F3 | Constitution provider as default path | 🔄 CTO executing |
| F4 | README badges 238→304, v0.42→v0.43 | 🔄 CTO executing |
| F5 | DirectLiNGAM dedicated tests | 🔄 CTO executing |
| F6 | PathBPolicy (fail matrix) | 🔄 CTO executing |

## Wave 2: Foundation Sovereignty (P0 — from ChatGPT audit)

### N1. Unified Compiler Entry Point
- New: `ystar/kernel/compiler.py`
- `compile_source(source_ref, source_text, source_type) -> CompiledContractBundle`
- Bundle contains: contract, source_hash, version, diagnostics, confidence
- All contract creation goes through here — Path A/B/GovernanceLoop consume bundles
- nl_to_contract.py becomes provider implementation, not direct entry

### N2. Constitution Bundle Provider
- New: `ystar/kernel/contract_provider.py`
- `resolve_constitution(source_ref) -> ConstitutionBundle`
- Path A/B stop reading MD files directly
- Delete: direct file open in meta_agent.py and path_b_agent.py as main path
- Provider becomes the ONLY way to get constitution hash/version

### N3. Scope Encoding Module
- New: `ystar/kernel/scope_encoding.py`
- `encode_module_scope(modules) -> List[str]` (produces "module:X" prefixes)
- `encode_external_scope(agent_id) -> List[str]`
- `encode_external_domain_scope(domain) -> List[str]`
- Path A/B stop doing prefix string concatenation internally
- engine.py uses decoder from same module

### N4. GovernanceLoop Compiler Integration
- File: `ystar/governance/governance_loop.py`
- Delete: `from ystar.kernel.prefill import prefill as _prefill`
- Replace: `propose_from_nl()` uses compiler.compile_source()
- GovernanceLoop consumes compiled bundles, not raw text

## Wave 3: Engineering Polish (P1)

### N5. Bridge Suggestion Candidates (real, not empty)
- File: `ystar/governance/experience_bridge.py`
- `generate_suggestion_candidates()` returns actual GovernanceSuggestion drafts
- Based on aggregated patterns and gap attribution
- Bridge evolves from metric bridge → governance suggestion bus

### N6. Delegation Policy External
- New: `ystar/governance/delegation_policy.py`
- `build_handoff_chain(governance_bundle, agent_bundle) -> DelegationChain`
- Path A stops hand-assembling parent/child contracts in handoff registration

### N7. GovernanceLoop Suggestion Policy
- File: `ystar/governance/governance_loop.py`
- Extract hardcoded rule_a_delegation, ±20%, add_domain_pack into GovernanceSuggestionPolicy
- GovernanceLoop becomes orchestrator, not strategy owner

### N8. OmissionEngine Escalation Policy Externalization
- File: `ystar/governance/omission_engine.py`
- Extract reminder/escalation/hard-overdue timing into policy objects
- Different domains can have different escalation rhythms

## Wave 4: Real Runtime Validation (P2)

### N9. Non-Mock Scenario Tests
- New: `tests/test_runtime_real.py`
- Path A with real SQLite CIEU, real omission store, real compiler bundle
- Path B with real constraint application, real disconnect flow
- A+B+Bridge with real data flow through all layers
- No Mock() for core infrastructure

### N10. Architecture Regression Tests
- Add to `tests/test_architecture.py`:
  - path_a does not directly open constitution files as main path
  - path_b does not directly open constitution files as main path
  - governance_loop does not import prefill directly

---

## Execution Order
1. Wait for CTO F1-F6 to complete (Wave 1)
2. N1+N2+N3 together (Wave 2 foundation — most critical)
3. N4 (GovernanceLoop follows compiler)
4. N5+N6+N7+N8 (Wave 3 engineering)
5. N9+N10 (Wave 4 validation)
