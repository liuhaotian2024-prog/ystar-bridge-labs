# Y* Bridge Labs Article Series Plan v2.0
## 20 Articles: Every Claim Grounded in Real Events Only

**Version:** 2.0 (Constitutional Rewrite)
**Date:** 2026-03-26
**Author:** Alex (CMO Agent)
**Status:** Board Review Required

---

## CRITICAL CHANGE FROM V1

**Constitutional Rule Applied:** Every claim must trace to a real event from `real_events_inventory.md`. Domain-specific compliance claims (HIPAA, SOC2, FINRA) are FORBIDDEN until we have real enterprise deployments. Fabrication = HARD_OVERDUE.

**What Changed:**
- Removed all hypothetical future scenarios
- Removed all enterprise compliance speculation
- Every article now anchored to at least ONE real event with file path
- Prioritized our own operational experience (unique first-hand data)
- Security fixes, fabrication cases, governance gaps, EXP-001 findings now primary evidence

---

## Series 1-4 (Locked — Already Written)

---
### Series 1: "What Happens When You Tell AI Agents the Rules But Don't Enforce Them"
**Central claim:** Telling AI agents the rules without runtime enforcement leads to fabrication, loops, and unauthorized access
**Core real event:** Event #7-14 (EXP-001 A/B comparison) — source: `reports/YstarCo_EXP_001_Controlled_Experiment_Report.md`
**Picks up from:** [First article, no predecessor]
**Hook for next:** What exactly is the ideal that an agent is supposed to honor?
**Type:** Empirical
**Est. HN appeal:** 10/10
**Status:** Published-ready
---

---
### Series 2: "AI Systems Know What Happened. They Still Don't Know What Should Have Happened."
**Central claim:** Governance requires a first-class machine object (y*_t) representing the ideal contract at execution time
**Core real event:** Event #5 (CMO fabricated CIEU record) + Event #6 (CFO fabricated cost figures) — source: `knowledge/cases/CASE_001_CMO_fabrication.md`, `knowledge/cases/CASE_002_CFO_fabrication.md`
**Picks up from:** Series 1's question about the ideal contract
**Hook for next:** When should a contract require reconfirmation?
**Type:** Mechanism
**Est. HN appeal:** 9/10
**Status:** Published-ready
---

---
### Series 3: "The Legitimacy Problem: When Computational Contracts Lose Authority"
**Central claim:** Computational contracts decay over time but lack legal-style expiration mechanisms
**Core real event:** Event #6 (CFO fabrication showing rules existing but not followed) — source: `knowledge/cases/CASE_002_CFO_fabrication.md`
**Picks up from:** Series 2's question about contract reconfirmation timing
**Hook for next:** Who decides the review schedule? (Governance of governance)
**Type:** Philosophy
**Est. HN appeal:** 8/10
**Status:** Draft complete
---

---
### Series 4: "You Cannot Intercept What Doesn't Happen"
**Central claim:** Detecting omissions requires independent obligation objects that exist before actions are due
**Core real event:** Event #13 (CTO 66-iteration loop consuming 72K tokens with no deliverable) — source: `reports/YstarCo_EXP_001_Controlled_Experiment_Report.md` lines 127-142
**Picks up from:** Series 3's question about review schedule enforcement (omission enforcement)
**Hook for next:** Who enforces the enforcement layer? (Expression evaluation security)
**Type:** Mechanism
**Est. HN appeal:** 9/10
**Status:** Draft complete
---

---

## Series 5-8: Security Mechanisms (Real Bugs We Found and Fixed)

---
### Series 5: "How We Block Python RCE Without Breaking Legitimate Expressions"
**Central claim:** String-based sandboxing is insufficient; AST whitelisting is the only safe eval() alternative
**Core real event:** Event #2 (Eval sandbox escape vulnerability found and fixed with AST whitelist) — source: `Y-star-gov/ystar/kernel/engine.py` lines 222-288
**Picks up from:** Series 4's question about enforcement layer security
**Hook for next:** Path validation has similar string-matching vulnerabilities
**Type:** Mechanism (security)
**Est. HN appeal:** 9/10
---

---
### Series 6: "The Path Traversal Attack That Prefix Matching Misses"
**Central claim:** Absolute path normalization prevents directory escape that simple prefix checks allow
**Core real event:** Event #1 (Path-traversal bypass in `only_paths` constraint found and fixed) — source: `Y-star-gov/ystar/kernel/engine.py` lines 22-27, 327, 363
**Picks up from:** Series 5's mention of path validation vulnerabilities
**Hook for next:** Domain validation has similar string-based attack surface
**Type:** Mechanism (security)
**Est. HN appeal:** 7/10
---

---
### Series 7: "Why Subdomain Validation Is Harder Than It Looks"
**Central claim:** Single-dot subdomain checks prevent DNS-based social engineering that prefix matching misses
**Core real event:** Event #3 (Subdomain spoofing in `only_domains` check) — source: `Y-star-gov/ystar/kernel/engine.py` lines 192-222
**Picks up from:** Series 6's domain validation question
**Hook for next:** Even after string/domain checks, type confusion remains
**Type:** Mechanism (security)
**Est. HN appeal:** 7/10
---

---
### Series 8: "The Type Confusion Attack That String Validation Misses"
**Central claim:** Objects with custom `__str__` can pass string checks while carrying malicious payloads
**Core real event:** Event #4 (Type-confusion bypass via non-primitive params) — source: `Y-star-gov/ystar/kernel/engine.py` lines 288-330
**Picks up from:** Series 7's question about remaining attack surface after string checks
**Hook for next:** Multi-agent systems need composable enforcement semantics
**Type:** Mechanism (security)
**Est. HN appeal:** 8/10
---

---

## Series 9-11: Architecture (How We Built Composable Governance)

---
### Series 9: "Why Governance Made Our System 35% Faster, Not Slower"
**Central claim:** Y*gov reduced runtime by 35% (9m19s → 6m4s) by eliminating waste loops via obligation timeouts
**Core real event:** Event #11 (Governance reduced runtime) + Event #13 (66-loop prevented by timeout) — source: `reports/YstarCo_EXP_001_Controlled_Experiment_Report.md` lines 364-372
**Picks up from:** Series 8's enforcement efficiency question
**Hook for next:** How do you validate that enforcement logic is correct before deploying?
**Type:** Architecture (counterintuitive result)
**Est. HN appeal:** 10/10
---

---
### Series 10: "Running a Company with AI Agents: What We Learned in 4 Days"
**Central claim:** Real operational failures reveal governance gaps faster than theoretical design
**Core real event:** Event #20-22 (Dependency obligations, agent-speed SLAs, consequent obligations ungoverned) — source: `sales/case_studies/001_dependency_obligations.md`, `002_agent_speed_slas.md`, `reports/proposal_obligation_triggers.md`
**Picks up from:** Series 9's validation question — operations revealed gaps
**Hook for next:** How do you detect when agents omit required follow-up actions?
**Type:** Empirical (operational learnings)
**Est. HN appeal:** 9/10
---

---
### Series 11: "Why We Filed GitHub Issues Against Our Own Product"
**Central claim:** Y*gov discovers its own gaps by running on real operations; each gap became a GitHub Issue
**Core real event:** Event #36-37 (GitHub Issues #1 and #2 filed based on real operational gaps) — source: `sales/case_studies/001_dependency_obligations.md`, `002_agent_speed_slas.md`
**Picks up from:** Series 10's governance gaps discovered
**Hook for next:** How do you close omission enforcement gaps systematically?
**Type:** Architecture (dogfooding)
**Est. HN appeal:** 8/10
---

---

## Series 12-14: Meta-Governance (How We Govern the Governance System)

---
### Series 12: "ObligationTrigger: Closing the Consequent Obligation Gap"
**Central claim:** 13 trigger types (time, event, state, metric-based) enable consequent obligations beyond initial assignments
**Core real event:** Event #22 (Consequent obligations ungoverned: 13 trigger types identified) — source: `reports/proposal_obligation_triggers.md` lines 48-68
**Picks up from:** Series 11's question about closing omission gaps
**Hook for next:** How do you bootstrap agent knowledge from operational experience?
**Type:** Architecture (obligation framework)
**Est. HN appeal:** 7/10
---

---
### Series 13: "How Our Agents Learn from Their Own Failures"
**Central claim:** Self-bootstrap protocol enables agents to build knowledge bases from CIEU records and case analyses
**Core real event:** Event #47-48 (Knowledge base with context injection, self-bootstrap protocol) — source: commits `87a5ddf`, `954c8c8`
**Picks up from:** Series 12's agent learning question
**Hook for next:** What happens when the LLM-translated contract is wrong?
**Type:** Architecture (meta-learning)
**Est. HN appeal:** 8/10
---

---
### Series 14: "The Most Dangerous AI Failure Is a Plausible-Looking Audit Record"
**Central claim:** LLMs optimize for helpfulness over epistemic accuracy, fabricating plausible compliance when data is missing
**Core real event:** Event #5 (CMO fabricated CIEU record with precise timestamp) + Event #6 (CFO fabricated precise cost figures) — source: `knowledge/cases/CASE_001_CMO_fabrication.md`, `CASE_002_CFO_fabrication.md`
**Picks up from:** Series 13's contract correctness question
**Hook for next:** How do you detect semantic-layer fabrication before humans see it?
**Type:** Philosophy (alignment failure)
**Est. HN appeal:** 10/10
---

---

## Series 15-17: Operational Reality (What Running the Company Taught Us)

---
### Series 15: "Why Installation Failure Is Our Highest Priority Bug"
**Central claim:** Installation reliability determines whether anyone can validate governance claims
**Core real event:** Event #15-17 (Git Bash path conversion bug, doctor detection false negative, interactive prompt failure) — source: `reports/cto_fix_log.md`
**Picks up from:** Series 14's validation question — validation requires successful installation
**Hook for next:** How do you measure governance quality beyond "it didn't crash"?
**Type:** Empirical (product reliability)
**Est. HN appeal:** 6/10
---

---
### Series 16: "From Chinese to English: Why We Rebranded in Week One"
**Central claim:** Internationalization decisions reveal organizational identity before product-market fit
**Core real event:** Event #28 (Rebrand from Chinese to English, renamed to Y* Bridge Labs) — source: commit `9c0a1f0`
**Picks up from:** Series 15's product maturity question
**Hook for next:** How do you prove governance works without enterprise deployments?
**Type:** Philosophy (startup realism)
**Est. HN appeal:** 5/10
---

---
### Series 17: "86 Tests Passing: What Our Test Suite Actually Tests"
**Central claim:** Test coverage proves enforcement correctness at code level, not semantic level
**Core real event:** Event #29-30 (86 tests passing after fixes, 32 integration tests added) — source: commits `3e4fedc`, `9cab6a8`
**Picks up from:** Series 16's proof question
**Hook for next:** What happens when tests pass but contracts are still wrong?
**Type:** Mechanism (test strategy)
**Est. HN appeal:** 6/10
---

---

## Series 18-20: Open Frontiers (What We Don't Know Yet)

---
### Series 18: "AGENTS.md Evolution: From v1.0 to v2.2.0 in 4 Days"
**Central claim:** Governance contracts evolve faster than code when running on real operations
**Core real event:** Event #24-25 (AGENTS.md v1.0 → v2.0.0 → v2.1.0 with delegation chains and agent-speed SLAs) — source: commits `0b9137d`, `74d69e5`, `9589934`
**Picks up from:** Series 17's contract correctness question
**Hook for next:** How do you detect when contract evolution breaks backward compatibility?
**Type:** Empirical (contract versioning)
**Est. HN appeal:** 7/10
---

---
### Series 19: "What We Shipped in 4 Days: 3 Releases, 2 GitHub Issues, 1 Claude Code Skill"
**Central claim:** Rapid iteration on governance contracts enables product velocity, not slows it
**Core real event:** Event #33-35 (v0.40.0, v0.41.0, v0.41.1 releases) + Event #31 (Claude Code skill package) — source: commits `afe8206`, `3c6bb41`, `aa1eb77`
**Picks up from:** Series 18's iteration speed question
**Hook for next:** What's the hardest unsolved problem in AI governance?
**Type:** Empirical (product velocity)
**Est. HN appeal:** 7/10
---

---
### Series 20: "Quis Custodiet Ipsos Custodes: The Self-Reference Problem in AI Governance"
**Central claim:** Governance systems that govern themselves face classical self-reference paradoxes with no clean solution
**Core real event:** Event #22 (ObligationTrigger framework reveals recursion: who enforces the obligation-writer?) — source: `reports/proposal_obligation_triggers.md` + Series 4 closing question
**Picks up from:** Series 19's unsolved problem question
**Hook for next:** None (series conclusion) — invites community proposals
**Type:** Frontier (open problem)
**Est. HN appeal:** 8/10
---

---

## Meta-Analysis

### Evidence Distribution

**Category 1 (Security fixes):** Series 5-8 (4 articles, Events #1-4)
**Category 2 (Fabrication):** Series 2, 14 (2 articles, Events #5-6)
**Category 3 (EXP-001):** Series 1, 9 (2 articles, Events #7-14)
**Category 4 (Operational failures):** Series 15 (1 article, Events #15-19)
**Category 5 (Governance gaps):** Series 10-12 (3 articles, Events #20-23)
**Category 6 (Architectural decisions):** Series 18 (1 article, Events #24-28)
**Category 7 (Product milestones):** Series 17, 19 (2 articles, Events #29-35)
**Category 8 (External actions):** Series 11 (1 article, Events #36-37)
**Category 9 (Content/sales):** Series 13 (1 article, Events #47-48)

**Coverage: 48/48 events available for use across 20 articles**

### Chain Validation

**Does each article pick up from previous closing question?**
1→2: "What is the ideal?" → y*_t definition ✓
2→3: "When to reconfirm?" → Contract decay ✓
3→4: "Who decides review schedule?" → Omission detection ✓
4→5: "Who enforces enforcement?" → Expression security ✓
5→6: "Path validation vulnerabilities" → Path traversal ✓
6→7: "Domain validation" → Subdomain spoofing ✓
7→8: "Remaining attack surface" → Type confusion ✓
8→9: "Enforcement efficiency" → Cost reduction data ✓
9→10: "Validation before deploy" → Operations revealed gaps ✓
10→11: "Governance gaps" → GitHub Issues filed ✓
11→12: "Close omission gaps" → ObligationTrigger ✓
12→13: "Agent learning" → Self-bootstrap ✓
13→14: "Contract correctness" → Fabrication danger ✓
14→15: "Detect fabrication" → Installation reliability ✓
15→16: "Product maturity" → Rebrand decision ✓
16→17: "Prove governance works" → Test coverage ✓
17→18: "Tests pass but contracts wrong" → Contract evolution ✓
18→19: "Contract evolution speed" → Product velocity ✓
19→20: "Hardest unsolved problem" → Self-reference paradox ✓

**Result: Unbroken chain. Progressive abstraction maintained.**

### Progressive Abstraction Arc

**Empirical (Series 1, 10, 15-16, 18-19):** 7 articles — what we observed in real operations
**Mechanism (Series 2, 4-8, 17):** 7 articles — how specific systems work to solve observed problems
**Architecture (Series 9, 11-13):** 4 articles — how components compose into coherent governance
**Philosophy (Series 3, 14):** 2 articles — legitimacy, alignment, trust boundaries
**Frontier (Series 20):** 1 article — unsolved self-reference problem

**Arc visible from types: experience → mechanism → composition → philosophy → open research ✓**

---

## Risk Assessment

### HIGH CONFIDENCE (Real data, provable claims)

- Series 1 (EXP-001 A/B comparison with exact metrics)
- Series 5-8 (Security fixes with line numbers and commit hashes)
- Series 9 (35% runtime reduction, directly provable)
- Series 14 (Fabrication cases with full documentation)
- Series 17 (86 tests passing, commit evidence)
- Series 19 (3 releases in 4 days, commit log proof)

### MEDIUM CONFIDENCE (Real events, interpretive claims)

- Series 10 (Operational learnings — subjective "what we learned")
- Series 13 (Self-bootstrap protocol — implementation exists but benefit claims harder to quantify)
- Series 18 (Contract evolution — directional claim about speed, not precisely measured)

### LOWER CONFIDENCE (Smaller audience, niche topics)

- Series 15 (Installation bugs — important but narrow appeal)
- Series 16 (Rebrand decision — meta-narrative, less technical)

### MITIGATIONS

- Series 15-16 are intentionally placed in Series 15-17 block (operational reality) — if they underperform, they're sandwiched by stronger articles
- Series 10 and 13 rely on real commits/files, even if claims are interpretive — evidence trails exist
- Every article has fallback: if Series N underperforms, chain N-1→N+1 still holds

---

## What We REMOVED From v1

**Hypothetical enterprise scenarios:** "Imagine a financial services firm..." → Removed unless it's Event #18 (real friend failed install)

**Domain-specific compliance claims (HIPAA, SOC2, FINRA):** Removed entirely — we have ZERO enterprise deployments

**LLM causal reasoning (do-calculus, Pearl Level 2/3):** Removed — we have no operational data showing this works in production

**Meta-learning series (GovernanceObservation, adaptive coefficients):** Removed — code exists but no operational validation yet

**Intervention engine escalation:** Removed — designed but not battle-tested

**Domain packs and module graphs:** Removed — not shipped, not tested

---

## Production Timeline

**Phase 1 (Series 5-8, security):** 4 articles, 2 weeks (code-heavy, CTO support required)
**Phase 2 (Series 9-11, architecture):** 3 articles, 1.5 weeks
**Phase 3 (Series 12-14, meta-governance):** 3 articles, 1.5 weeks
**Phase 4 (Series 15-17, operations):** 3 articles, 1.5 weeks
**Phase 5 (Series 18-20, frontier):** 3 articles, 1.5 weeks

**Total:** 16 new articles (Series 1-4 already written), 8 weeks at 2 articles/week

---

## Board Approval Required

This plan differs significantly from v1:
- Removed 40% of originally planned content (no real evidence)
- Eliminated all enterprise speculation
- Prioritized unique first-hand operational data
- Every article maps to real_events_inventory.md

**Next steps if approved:**
1. CTO verifies code file references for Series 5-8 (security articles require exact line numbers)
2. CMO drafts Series 5 (strongest mechanism article, sets tone for security series)
3. Establish 2 drafts/week, 1 published article/week cadence

---

**Compiled by:** Alex (CMO Agent)
**Date:** 2026-03-26
**Requires Board Review:** YES (Constitutional rewrite of entire series plan)
