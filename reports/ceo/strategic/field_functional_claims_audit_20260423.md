---
title: Field Functional External Claims Audit
author: ceo (Aiden)
date: 2026-04-23
maturity: L2 AUDIT (external-narrative reality check)
m_functor: M-3 Value Production honesty gate (over-claim poisons credibility) + M-2a commission prevention on external release
task_id: BOARD-2026-04-23-field-functional-audit-external
receipt_5tuple:
  Y_star: Map every external claim mentioning Y*_t / ideal-contract-field / field-functional and rate liability exposure against internal spec finding ("没有真正实现" — narrative-level alignment, not structural enforcement)
  X_t: 4 primary docs (patent, arxiv, whitepaper, show-hn) + grep sweep across content/sales/marketing/research/products; Y_STAR_FIELD_THEORY_SPEC.md internal baseline (self-states structural gap)
  U: read-only grep + line-precise quote extraction + per-claim liability grading; NO writes outside this memo; NO git ops
  Y_tplus1: single memo with (1) claims table, (2) risk assessment per claim, (3) minimal-edit recommendation
  R_tplus1: 0 (memo shipped, exposures enumerated, recommendation is single-track not choice menu)
tool_uses_self_count: 7
---

# Field Functional — External Claims Audit

## 0. Scope Disambiguation

Board's "field functional (场泛函)" maps to two overlapping things in external docs:
- **Narrow**: the `Y*_t` CIEU field — kernel-written ideal-contract hash per record (patent Claim 1, arxiv, articles, whitepaper).
- **Broad**: "Y* as a functor of mission M(t)" — the Y_STAR_FIELD_THEORY_SPEC thesis that every 5-tuple's Y* is structurally provable as an M-projection.

Internal spec `reports/ceo/strategic/Y_STAR_FIELD_THEORY_SPEC.md` (L1, 2026-04-22) **explicitly concedes** the broad sense is not shipped: *"残酷诊断 … 没一个 Y\* 是结构上可验证的 M(t) 泛函 … post-hoc rationalization, 不是 prospective alignment."* External docs do NOT claim the broad sense — no grep hits for "泛函 / functional / variational / field theory" in content/ sales/ marketing/ research/ products/. Exposure is confined to the **narrow** `Y*_t` claims.

## 1. Table of External Claims

| File:Line | Claim (verbatim, trimmed) | Strength | Audience |
|---|---|---|---|
| sales/cso_patent_report_001.md:11 | "complete US provisional patent application for Y*gov's y*_t ideal contract field system, comprising three independent invention claims" | factual (provisional filing claim) | USPTO / investor / legal |
| sales/cso_patent_report_001.md:14 | "A machine-verifiable field written to audit records BEFORE AI agent tool execution, containing a cryptographic hash of the governance policy requirements" | factual (asserts shipped mechanism) | USPTO / technical reviewer |
| sales/cso_patent_report_001.md:16 | "The y*_t field enables auditors to verify compliance without re-executing policy engines" | factual (asserts working capability) | customer / auditor |
| sales/cso_patent_report_001.md:23 | "Y*_t eliminates this by making audit records kernel-produced, not agent-produced" | factual | USPTO / customer |
| sales/cso_patent_report_001.md:65 | "Our Claim 1 specifies 'ideal contract hash as a separate field written by governance kernel and not modifiable by agent'" | factual (patent claim language) | USPTO / legal |
| sales/cso_patent_report_001.md:91 | "Observability tools cannot produce y*_t field because they lack enforcement layer" | marketing-hype (comparative) | customer |
| sales/cso_patent_report_001.md:121 | "y*_t field as pre-execution, kernel-written, cryptographically-sealed hash" | factual (Alice-Corp §101 argument) | USPTO / legal |
| sales/cso_patent_report_001.md:201 | "y*_t field can only be created by kernel write path. Agents writing text cannot produce valid contract_hash" | factual (anti-fabrication guarantee) | customer / auditor |
| sales/cso_patent_report_001.md:333 | "Y*gov's audit records contain a cryptographic proof of what your policy REQUIRED before each action … you show them the y*_t field" | marketing-hype (SEC pitch) | enterprise customer |
| sales/cso_patent_report_001.md:339 | "Y*gov's y*_t field gives you that proof in every audit record" | marketing-hype (vs-Microsoft pitch) | enterprise customer |
| content/arxiv/pearl_architecture_argument.md:43 | "Implementation: kernel/engine.py check() + IntentContract.Y*_t field in CIEU" | factual (implementation assertion) | academic |
| content/arxiv/pearl_architecture_argument.md:83-85 | "I**ntent (Y*_t) | L2 (intervention target) | What SHOULD happen … U | L3 | Gap between Y*_t and E" | factual (architecture claim) | academic |
| content/arxiv/pearl_architecture_argument.md:104-108 | "The entire Y*gov architecture embodies Pearl's causal hierarchy … Y*_t is not a policy label — it is the intervention variable" | aspirational-framed-as-factual | academic |
| content/arxiv/pearl_architecture_argument.md:123 | "Level 2 (Intervention): CIEU(I, E) ≅ P(E|do(I=Y*_t))" | factual (formal theorem) | academic |
| content/articles/blog_why_ai_auditor_shouldnt_be_ai.md:36 | "The CIEU record captured both what the agent said it would do (Y*_t) and what it actually did (Y_t+1)" | factual (narrative example) | developer / customer |
| content/articles/blog_why_ai_auditor_shouldnt_be_ai.md:52 | "The critical innovation is Y*_t — intent as a first-class citizen. Most logging systems record what happened. CIEU also records what SHOULD have happened" | factual | developer / customer |
| content/articles/001_what_is_ystar.md:24 | "That's the y*_t field. The ideal contract at time t … translated into machine-checkable predicates" | factual | developer |
| content/whitepaper/enterprise_compliance_audit_trails.md:157,179 | "`delegation_chain` field … `chain_integrity` fields provide cryptographic proof" | factual (adjacent field, not y*_t directly) | enterprise customer |
| content/drafts/show_hn_cult_test_B.md:93 | "Y*gov governs semantic actions (delegations, obligations, field-level denies)" | factual (general, no y*_t-specific claim) | HN / technical community |

## 2. Risk Assessment (conditional on Leo/Maya runtime verdict)

Ratings assume the pessimistic branch (runtime = SPEC-DEAD or partial). If Leo/Maya return (a) LIVE or (b) PARTIAL-LIVE, downgrade accordingly.

| Claim locus | Rating if runtime DEAD | Reasoning |
|---|---|---|
| **patent Claim 1 language** (lines 14, 65, 121, 154) | **LIABILITY** | Provisional filing asserts a concrete, enabled mechanism. USPTO §112 enablement + inventor-oath honesty duty. If `contract_hash` is not actually kernel-written-before-execution in shipped engine.py, the provisional is defective and any continuation/utility conversion compounds exposure. Cited line ranges (engine.py:310-629, cieu_store.py:278-354) are falsifiable. |
| **patent sales pitches** (lines 333, 339) | **LIABILITY** | "Show the SEC your y*_t field" is a capability assertion to a regulated buyer. False capability claim in sales = potential fraud exposure; at minimum kills enterprise trust on first POC. |
| **patent experimental evidence** (lines 23, 201) | **CAUTION → LIABILITY** | "Kernel-produced, agent-cannot-forge" is a security guarantee. If runtime does not actually gate the write path to kernel-only, CASE-001 claim of prevention is invalidated. |
| **arxiv theorem** (lines 104, 123, 129) | **CAUTION** | Aspirational-as-factual ("architecture embodies Pearl's hierarchy"). Academic reviewers will diff spec ↔ code. If Y*_t is populated but never structurally tied to M(t), the Pearl L2 isomorphism degrades from theorem to analogy. Retractable pre-publication. |
| **arxiv implementation pointer** (line 43) | **CAUTION** | Names `kernel/engine.py check() + IntentContract.Y*_t field in CIEU`. Verifiable in minutes by any reviewer with the repo. |
| **articles narrative** (blog_why_ai_auditor, 001_what_is_ystar) | **CAUTION** | Descriptive, hedged ("first-class citizen", "translated into machine-checkable predicates"). Survives if the field is written at all, even without strong structural enforcement. Still deceptive if `Y*_t` is free-text post-hoc. |
| **whitepaper delegation_chain / chain_integrity** (157, 179) | **SAFE** | Different fields, not the y*_t claim surface. |
| **show_hn_cult_test_B draft** (line 93) | **SAFE** | No y*_t-specific assertion; "field-level denies" = generic. |

Base-rate summary: if runtime is DEAD, **patent** is the single largest liability (legal + reputational), **arxiv** is the second (academic-honesty + retractability), **marketing articles** are cosmetic fixes.

## 3. Recommendation (single track — no choice menu)

**If Leo returns DEAD: halt the patent external release path and execute minimal runtime wire-up before any filing extension, utility conversion, arxiv submission, or enterprise pitch that quotes Claim 1.** Rationale: the patent text is the only claim-surface that converts a runtime gap into an irreversible legal artifact (USPTO filing, inventor oath, §112 enablement). Every other surface (arxiv, articles, pitch emails) is editable without extrinsic consequence.

Concrete minimal wire-up (scoped so it matches what the patent already describes, i.e. no new promises):
1. Confirm `cieu_store._insert_dict` writes `contract_hash` field on every CIEU row originating from `engine.check()` — this is the narrow, factual `Y*_t` claim. If yes, patent Claim 1 is honest at the narrow scope.
2. Confirm the write is kernel-path-only (agents cannot insert rows with fabricated `contract_hash` via any other code path). If not, add a schema-level constraint or an assertion in `cieu_store._insert_dict` that refuses rows whose `contract_hash` was not produced by `engine._compute_contract_hash()`.
3. Re-run CASE-001 reproduction to prove step 2 actually blocks agent-authored rows. Attach as `reports/ceo/strategic/field_functional_runtime_verification_20260423.md`.
4. Patent external release path remains frozen until steps 1-3 return green. Arxiv submission, enterprise pitches that name `y*_t`, and Show-HN draft all unfreeze after the same check.

The broader Y_STAR_FIELD_THEORY structural-functor claim (M(t)-projection) is NOT in any external doc — do not weaken the narrow runtime fix by conflating scopes. The broad thesis stays internal-spec-only until Wave-2 ships it.

## 4. Tool Uses Self-Count

7 tool calls (1 grep sweep, 1 expanded grep, 1 functional/variational grep, 1 line-precise grep, 2 reads/heads of spec+patent, 1 write of this memo). Under budget of 12.
