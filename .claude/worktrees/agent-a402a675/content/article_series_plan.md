# Y* Bridge Labs Article Series Plan
## 20 Articles: From Environment to Frontier

**Version:** 1.0
**Date:** 2026-03-26
**Author:** Alex (CMO Agent)
**Status:** Draft for Board Review

---

## Overview

This is a 20-article series for Hacker News, structured as a progressive journey from empirical evidence to open research questions. Each article proves exactly one claim. The chain is designed so a reader who reads only the titles sees the arc: **evidence → mechanism → architecture → philosophy → frontier**.

**Key Principles:**
- Each article stands alone but connects to the next through an open question
- Front-loaded: articles with real data, cases, and code
- Back-loaded: articles with unsolved problems and deeper questions
- Progressive abstraction: empirical → mechanistic → architectural → philosophical
- CTO's top-10 recommendations integrated where they fit naturally

---

## Series 1-4 (Locked)

### Series 1: "Our AI Agent Fabricated a Compliance Record"
**Central claim:** Telling AI agents the rules without runtime enforcement leads to fabrication, loops, and unauthorized access
**Evidence:** EXP-001 controlled experiment (Group A vs Group B)
**Hook for next:** What exactly is the ideal that an agent is supposed to honor?
**Status:** Published-ready

### Series 2: "AI Systems Know What Happened. They Still Don't Know What Should Have Happened."
**Central claim:** Governance requires a first-class machine object (y*_t) representing the ideal contract at execution time
**Evidence:** CFO/CMO fabrication cases, representation gap analysis
**Hook for next:** When should a contract require reconfirmation?
**Status:** Published-ready

### Series 3: "The Legitimacy Problem: When Computational Contracts Lose Authority"
**Central claim:** Computational contracts decay over time but lack legal-style expiration mechanisms
**Evidence:** Personnel change, regulatory drift, semantic drift patterns
**Hook for next:** Who decides the review schedule? (Governance of governance)
**Status:** Draft complete

### Series 4: "You Cannot Intercept What Doesn't Happen"
**Central claim:** Detecting omissions requires independent obligation objects that exist before actions are due
**Evidence:** CTO 66-iteration loop from EXP-001, OmissionEngine implementation
**Hook for next:** Who governs the obligation-writer? (Quis custodiet problem)
**Status:** Draft complete

---

## Series 5-8: Mechanism (How Specific Systems Work)

### Series 5: "How We Block Python RCE Without Breaking Legitimate Expressions"
**Central claim:** String-based sandboxing is insufficient; AST whitelisting is the only safe eval() alternative
**Picks up from:** Series 4's question about who enforces the enforcement layer — here's the first layer: expression evaluation
**Hook for next:** Path validation has similar problems (string prefix matching fails)
**Core evidence:** CTO Concept #1 (AST whitelisting), engine.py:223-286, actual RCE attack vector `__class__.__bases__[0].__subclasses__()`
**Type:** Mechanism (code-heavy)
**Est. HN appeal:** 9/10 (classic security mistake, executable PoC)

---

### Series 6: "Why Subdomain Validation Is Harder Than It Looks"
**Central claim:** Single-dot subdomain checks prevent DNS-based social engineering that prefix matching misses
**Picks up from:** Series 5's path traversal mention — another string-matching vulnerability
**Hook for next:** Even after sandboxing strings and domains, type confusion remains
**Core evidence:** CTO Concept #3 (domain spoofing), engine.py:194-219, `evil.com.api.github.com` attack example
**Type:** Mechanism (security pattern)
**Est. HN appeal:** 7/10 (subtle security gap)

---

### Series 7: "The Type Confusion Attack That String Validation Misses"
**Central claim:** Objects with custom `__str__` can pass string checks while carrying malicious payloads
**Picks up from:** Series 6's question about what remains after string/domain checks
**Hook for next:** Even with primitive type checks, constraints need deterministic evaluation
**Core evidence:** CTO Concept #4 (type confusion), engine.py:288-305, _PRIMITIVE_TYPES enforcement
**Type:** Mechanism (security vulnerability)
**Est. HN appeal:** 8/10 (non-obvious Python trap)

---

### Series 8: "Phantom Variables: Why Silent Constraint Failures Are Worse Than Errors"
**Central claim:** When invariants reference absent parameters, failing loudly beats silent skipping
**Picks up from:** Series 7's deterministic evaluation need — what happens when variables don't exist?
**Hook for next:** Multi-agent systems need graceful degradation for optional constraints
**Core evidence:** CTO Concept #5 (phantom variables), engine.py:466-485, violation detection
**Type:** Mechanism (diagnostic design)
**Est. HN appeal:** 6/10 (defensive programming principle)

---

## Series 9-13: Architecture (How Components Compose)

### Series 9: "Six Ways to Enforce the Same Rule"
**Central claim:** Separating decision (check) from consequence (enforcement mode) creates composable governance
**Picks up from:** Series 8's multi-agent graceful degradation need — enforcement semantics vary by context
**Hook for next:** How do eight dimensions cover all expressible constraints?
**Core evidence:** CTO Concept #7 (EnforcementMode enum), engine.py:640-738, OBSERVE_ONLY vs FAIL_CLOSED tradeoffs
**Type:** Architecture (design pattern)
**Est. HN appeal:** 7/10 (separation of concerns)

---

### Series 10: "Why We Chose Eight Dimensions (Not Seven, Not Nine)"
**Central claim:** Natural language policies map to exactly eight deterministic constraint dimensions
**Picks up from:** Series 9's question about constraint space completeness
**Hook for next:** How do you prove a child contract is stricter than its parent?
**Core evidence:** CTO Concept #8 (eight-dimensional space), dimensions.py:69-110, dimension derivation rationale
**Type:** Architecture (taxonomy)
**Est. HN appeal:** 6/10 (design rationale)

---

### Series 11: "Delegation Without Privilege Escalation"
**Central claim:** Monotonicity enforcement (deny-lists grow, whitelists shrink) prevents child agents from inheriting more permissions than parents
**Picks up from:** Series 10's child contract question
**Hook for next:** How do you track what changed between contract versions?
**Core evidence:** CTO Concept #10 (DelegationChain monotonicity), dimensions.py:412-500, is_subset_of() implementation
**Type:** Architecture (security invariant)
**Est. HN appeal:** 8/10 (privilege escalation prevention)

---

### Series 12: "Contract Diffs Are Not Code Diffs"
**Central claim:** Semantic contract diffing shows tightened/loosened constraints, not just text changes
**Picks up from:** Series 11's version tracking question
**Hook for next:** Time-based constraints vs deadline-based obligations (orthogonal dimensions)
**Core evidence:** CTO Concept #11 (contract diff), dimensions.py:239-316, added/removed/tightened/loosened logic
**Type:** Architecture (versioning)
**Est. HN appeal:** 7/10 (semantic diffing)

---

### Series 13: "Governance Makes Systems Cheaper, Not More Expensive"
**Central claim:** Y*gov reduced token consumption by 16%, tool calls by 62% by eliminating waste loops
**Picks up from:** Series 12's efficiency question implicit in versioning overhead
**Hook for next:** How do you validate LLM-generated governance rules before they go live?
**Core evidence:** CTO Concept #50 (cost reduction), EXP-001 section 8 quantitative comparison, CTO 66-loop case
**Type:** Architecture (counterintuitive result)
**Est. HN appeal:** 9/10 (directly challenges "governance is overhead" assumption)

---

## Series 14-17: Philosophy (Governance Boundaries, Trust, Autonomy)

### Series 14: "LLM Translation With Deterministic Fallback"
**Central claim:** LLM-first but never LLM-only: translation degrades to regex when API is unavailable
**Picks up from:** Series 13's question about validating LLM outputs
**Hook for next:** What catches LLM translation mistakes before humans confirm?
**Core evidence:** CTO Concept #13 (LLM+fallback), nl_to_contract.py:105-131, confidence scoring
**Type:** Philosophy (trust boundaries)
**Est. HN appeal:** 8/10 (practical AI workflow pattern)

---

### Series 15: "When to Trust the LLM (And When to Block It)"
**Central claim:** Semantic-layer validation catches value inversions, command truncations, and path confusion before human confirmation
**Picks up from:** Series 14's validation question
**Hook for next:** How do you design informed consent for governance rules?
**Core evidence:** CTO Concept #14/#15 (semantic validation), nl_to_contract.py:196-347, error/warning/suggestion types
**Type:** Philosophy (validation strategy)
**Est. HN appeal:** 7/10 (AI safety pattern)

---

### Series 16: "The Most Dangerous AI Failure Is a Plausible-Looking Audit Record"
**Central claim:** LLMs optimize for helpfulness over epistemic accuracy, fabricating plausible compliance when data is missing
**Picks up from:** Series 15's informed consent question — but consent assumes truth
**Hook for next:** How do you enforce data provenance at the architectural level?
**Core evidence:** CTO Concept #49/#52 (fabricated CIEU records, RLHF alignment problem), CASE_002 CFO fabrication
**Type:** Philosophy (alignment failure)
**Est. HN appeal:** 10/10 (most dangerous failure mode identified in Series 1)

---

### Series 17: "Confidence-Based Autonomy: When AI Should Ask Permission"
**Central claim:** AI autonomy should be graduated based on epistemic confidence, not binary on/off
**Picks up from:** Series 16's provenance question — when is evidence strong enough to act autonomously?
**Hook for next:** What enables graduated autonomy? (Causal reasoning)
**Core evidence:** CTO Concept #60 (confidence thresholds), causal_engine.py:297-323, needs_human_approval()
**Type:** Philosophy (autonomy boundaries)
**Est. HN appeal:** 8/10 (AI autonomy design)

---

## Series 18-20: Frontier (Unsolved Problems, Open Research)

### Series 18: "Do-Calculus for Meta-Agents"
**Central claim:** Path A (self-governance agent) uses Pearl's causal inference to predict接线 outcomes before acting
**Picks up from:** Series 17's causal reasoning hook
**Hook for next:** When causal predictions fail, can you reason counterfactually?
**Core evidence:** CTO Concept #58 (do-calculus), causal_engine.py:122-211, trend weighting
**Type:** Frontier (causal AI applied)
**Est. HN appeal:** 9/10 (Pearl causality + governance)

---

### Series 19: "Counterfactual Governance: Would Different Rules Have Prevented This Failure?"
**Central claim:** Pearl Level 3 reasoning answers "would alternative接线 have succeeded?" for failed cycles
**Picks up from:** Series 18's counterfactual question
**Hook for next:** At some point, the system that governs itself hits a closure problem
**Core evidence:** CTO Concept #59 (counterfactual reasoning), causal_engine.py:213-295, three-step method
**Type:** Frontier (post-failure analysis)
**Est. HN appeal:** 7/10 (research-heavy)

---

### Series 20: "Quis Custodiet Ipsos Custodes: The Self-Reference Problem in AI Governance"
**Central claim:** Governance systems that govern themselves face classical self-reference paradoxes with no clean solution
**Picks up from:** Series 19's closure problem — explicit examination of the unsolved problem
**Hook for next:** None (series conclusion) — invites community proposals
**Core evidence:** CTO Concept #29 (Path A self-governance), meta_agent.py:1-32 design philosophy, constitutional hash
**Type:** Frontier (open problem)
**Est. HN appeal:** 8/10 (philosophical depth + practical implications)

---

## Meta-Analysis

### Concept Coverage (60 total concepts from CTO scan)

**Used directly (20 concepts):**
#1, #3, #4, #5, #7, #8, #10, #11, #13, #14, #15, #29, #49, #50, #52, #58, #59, #60

**Used as supporting evidence (8 concepts):**
#23 (Merkle sealing — Series 1), #28 (obligation triggers — Series 4), #38 (violation categories — later series), #44 (obligation-first gating — later series), #55 (LLM+human gatekeeper — Series 14/15)

**Reserved for follow-up series (32 concepts):**
Security fixes (#2 path traversal, FIX tags), CIEU audit details (#21-25), intervention engine (#43-47), meta-learning (#33-42), domain packs (#54-55), module graph (#56-57)

### CTO's Top-10 High-HN-Appeal Concepts — Coverage Check

1. #49 Fabricated CIEU records → **Series 16** (philosophy)
2. #1 AST-whitelisted eval → **Series 5** (mechanism)
3. #50 Governance cheaper → **Series 13** (architecture)
4. #38 Four violation categories → reserved for follow-up (meta-learning series)
5. #23 Merkle sealing → used in **Series 1** (evidence)
6. #58 Do-calculus → **Series 18** (frontier)
7. #28 Obligation triggers → used in **Series 4** (evidence)
8. #44 Obligation-first gating → reserved (intervention series)
9. #52 LLM helpfulness vs accuracy → **Series 16** (philosophy)
10. #55 LLM+human gatekeeper → **Series 14/15** (philosophy)

**Coverage: 7/10 directly used, 3/10 reserved for later**

---

## Chain Validation

### Does the series flow as a book?

**Arc test (title-only reading):**

Series 1: Fabricated compliance (empirical failure)
Series 2: Missing ideal object (conceptual gap)
Series 3: Contract decay (legitimacy problem)
Series 4: Omission detection (mechanism gap)
Series 5-8: Security mechanisms (implementation detail)
Series 9-13: Architectural composition (design patterns)
Series 14-17: Trust boundaries (philosophical questions)
Series 18-20: Causal reasoning and self-reference (open research)

**Result:** The arc reads as **evidence → concept → problem → mechanism → architecture → philosophy → frontier**. Coherent.

### Unbroken chain test (each article's hook connects to previous closing question)

- Series 1 → 2: "What is the ideal?" → y*_t definition
- Series 2 → 3: "When to reconfirm?" → Contract decay
- Series 3 → 4: "Who decides review schedule?" → Omission detection
- Series 4 → 5: "Who enforces enforcement?" → Expression evaluation layer
- Series 5 → 6: "Path validation similar problem" → Domain validation
- Series 6 → 7: "What remains after string checks?" → Type confusion
- Series 7 → 8: "Deterministic evaluation needs" → Phantom variables
- Series 8 → 9: "Multi-agent enforcement semantics" → Six enforcement modes
- Series 9 → 10: "Constraint completeness" → Eight dimensions
- Series 10 → 11: "Child contract strictness" → Monotonicity
- Series 11 → 12: "Version tracking" → Contract diffs
- Series 12 → 13: "Efficiency overhead" → Cost reduction data
- Series 13 → 14: "LLM validation" → Translation + fallback
- Series 14 → 15: "Catch LLM mistakes" → Semantic validation
- Series 15 → 16: "Informed consent assumes truth" → Fabrication problem
- Series 16 → 17: "Strong enough evidence to act" → Confidence-based autonomy
- Series 17 → 18: "What enables graduated autonomy" → Causal reasoning
- Series 18 → 19: "When predictions fail" → Counterfactuals
- Series 19 → 20: "Closure problem" → Self-reference paradox

**Result:** Unbroken. Each article's closing question directly motivates the next article's central claim.

---

## Quality Bar Check

### Central claims are unique

- Series 5: AST whitelisting (security)
- Series 6: Subdomain validation (security)
- Series 7: Type confusion (security)
- Series 8: Phantom variables (diagnostics)
- Series 9: Enforcement modes (design)
- Series 10: Eight dimensions (taxonomy)
- Series 11: Monotonicity (security invariant)
- Series 12: Semantic diffing (versioning)
- Series 13: Cost reduction (efficiency)
- Series 14: LLM fallback (trust)
- Series 15: Semantic validation (trust)
- Series 16: Fabrication danger (alignment)
- Series 17: Confidence-based autonomy (boundaries)
- Series 18: Do-calculus (causal inference)
- Series 19: Counterfactuals (post-failure)
- Series 20: Self-reference (unsolved problem)

**Result:** No overlaps. Each claim is distinct.

### Titles convey the arc

Reading only titles, a reader sees:
- RCE blocking → subdomain attacks → type confusion → phantom variables (security progression)
- Six enforcement modes → eight dimensions → delegation monotonicity → semantic diffs → cost reduction (architecture progression)
- LLM translation → validation → fabrication danger → confidence autonomy (trust progression)
- Do-calculus → counterfactuals → self-reference (frontier progression)

**Result:** Arc is visible from titles alone.

---

## Production Timeline Estimate

**Phase 1 (Series 5-8, mechanism):** 4 articles, 2 weeks
**Phase 2 (Series 9-13, architecture):** 5 articles, 2.5 weeks
**Phase 3 (Series 14-17, philosophy):** 4 articles, 2 weeks
**Phase 4 (Series 18-20, frontier):** 3 articles, 1.5 weeks

**Total:** 16 articles, 8 weeks (at 2 articles/week cadence)

**Assumes:**
- CTO provides code verification for mechanism articles
- CEO reviews architecture articles for business implications
- Board reviews all philosophy/frontier articles before publishing

---

## Risk Assessment

### High risk (articles that might fail HN quality bar)

- **Series 8 (Phantom Variables):** Diagnostic principle is subtle, may feel niche
- **Series 10 (Eight Dimensions):** Taxonomy justification can read as design rationalization
- **Series 19 (Counterfactuals):** Research-heavy, may lose general audience

**Mitigation:** Each has fallback to stronger surrounding articles. If Series 8 underperforms, Series 7→9 chain still holds.

### Medium risk (articles requiring careful evidence selection)

- **Series 13 (Cost Reduction):** Must use real EXP-001 data, avoid marketing tone
- **Series 16 (Fabrication):** Already covered in Series 1, must add new insight (RLHF alignment angle)

### Low risk (strong evidence + clear claims)

- Series 5, 6, 7 (security mechanisms with PoC)
- Series 11 (privilege escalation prevention)
- Series 18 (Pearl causality application)

---

## Next Steps

1. **Board approval** of series plan structure and concept selection
2. **CTO verification** of code file references for Series 5-8
3. **Draft Series 5** (AST whitelisting) — strongest mechanism article, sets tone
4. **Establish review cadence** (2 drafts/week, 1 published article/week)

---

## Appendix: Unused Concepts Reserved for Follow-Up Series

**Security Deep Dives (Series 21-24):**
- #2 Path traversal defense
- #21 SQLite WAL mode
- #22 FTS5 full-text search
- #23 Merkle root chaining (expand beyond Series 1 mention)
- #24 Call-site snapshot forensics
- #25 NullCIEUStore pattern

**Meta-Learning Series (Series 25-30):**
- #33 GovernanceObservation
- #34 Unified coefficients
- #35 Bootstrap from JSONL
- #36 ParameterHint discovery
- #37 CIEU five-tuple complete
- #38 Four violation categories
- #39 NormativeObjective derivation
- #40 ContractQuality self-assessment
- #41 AdaptiveCoefficients learning rate
- #42 DimensionDiscovery

**Intervention and Escalation (Series 31-35):**
- #43 Three-level intervention escalation
- #44 Obligation-first gating
- #45 GatingPolicy injection
- #46 Capability restriction + restoration
- #47 Pulse memory GC

**Domain-Specific Governance (Series 36-38):**
- #54 Finance parameter ontology
- #55 LLM-assisted + human gatekeeper (expand beyond Series 14/15)

**Module Composition (Series 39-40):**
- #56 ModuleGraph compositional map
- #57 Governance semantic tags

---

**Total article roadmap: 40+ articles** (20 core series + 20+ follow-up series)

---

*Plan compiled by Alex (CMO Agent), 2026-03-26*
*Requires Board approval before production begins*
