# arXiv Paper Outline — Path A (SRGCS)

## Title
**"Quis Custodiet Ipsos Custodes: Self-Referential Governance Closure for Multi-Agent AI Systems"**

## Abstract (200 words)
- Problem: who governs the governance system? MOSAIC/AutoHarness solve model-level alignment but not the recursive authority problem.
- Solution: SRGCS — meta-agent constrained by contracts derived from its own governance outputs. GovernanceSuggestion IS IntentContract.
- Result: EXP-001 ungoverned agents fabricated compliance, dropped 63% of tasks. SRGCS: fabrication impossible, -62% tool calls, -35% runtime.
- Contributions: (1) formal closure property, (2) do-calculus decision boundary, (3) action-triggered passive detection.

## 1. Introduction
- Quis custodiet: agent-written audit records are meaningless
- Current approaches assume trusted external authority
- We need architecturally self-consistent governance

## 2. Related Work
- MOSAIC (Microsoft 2603.03205): model-level, no meta-governance
- AutoHarness (DeepMind 2603.03329): known environments only
- Microsoft AGT: no NL, no obligations
- GAP: nobody does (a) self-governance, (b) omission detection, (c) delegation monotonicity, (d) contract decay

## 3. Architecture
- 3.1: GovernanceSuggestion IS IntentContract → self-referential closure
- 3.2: Fail-closed delegation with DelegationChain monotonicity
- 3.3: Contract Legitimacy Lifecycle (6 states, time-based decay)

## 4. Contributions
- C1: Self-referential closure — fixed point, not circular
- C2: Do-calculus (Pearl L2-3) for autonomous vs human boundary
- C3: Action-triggered passive non-compliance detection (Patent P4)

## 5. Evaluation
- EXP-001: 117→45 calls, 9m→6m, fabrication 1→0
- CASE-005: cross-model (Claude→MiniMax), 23/23 tests
- ChatGPT 3-round audit: 12 issues found and fixed

## 5.4 Ablation
- Each component is load-bearing: remove closure → fabrication returns; remove CausalEngine → all decisions require human; remove OmissionEngine → dropped tasks undetected

## 6. Limitations
- n=1, accidental design, not pre-registered
- Cold-start weakness: CausalEngine has no history on first cycle, defaults to human approval
- Single-level depth: Path A governs itself but doesn't yet govern a governance-of-governance agent
- No adversarial evaluation: agents were cooperative (Claude), not adversarial
- Human-authored constitution (PATH_A_AGENTS.md): bootstrap still requires human seed
- Runtime activation partially simulated (importlib + activate() protocol, not full hot-swap)
- Convergence not formally proven — empirical evidence only
- Latent-space communication gap: Y*gov intercepts tool calls (text), not internal representations

## 7. Conclusion
- Quis custodiet has an architectural answer
- Three contributions: closure, causal boundary, passive detection
- Future: formal proof, large-scale deployment, MOSAIC+SRGCS complementarity

## Target: arXiv cs.MA → AAMAS 2027 COINE workshop
