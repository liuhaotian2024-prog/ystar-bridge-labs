# README Standards — 10-Dimension Evaluation Framework

**Owner**: CMO (Sofia Blake)  
**Status**: [L2 IMPL] — Active standard for weekly README audit  
**Last updated**: 2026-04-15  
**Applies to**: ystar-company, Y-star-gov, gov-mcp, K9Audit

---

## Purpose

READMEs are the first (and often only) touchpoint for developers evaluating a tool. A README that fails on clarity, install friction, or evidence-backed claims loses the reader before they ever try the product. This framework defines 10 measurable dimensions for README quality, drawn from mature developer-first companies and Y* Bridge Labs' operational reality.

---

## 10 Dimensions

### D1: Install Friction (0-10 scale)
**What it measures**: Time and steps from "I want to try this" to "I see it working"

**Scoring**:
- 10: ≤2 commands, ≤30 seconds, auto-detects environment, zero config required  
  _Example_: Stripe's "pip install stripe" → API key → first call in docs  
  _External benchmark_: [Stripe API Quick Start](https://docs.stripe.com/payments-api/tour) — 3 steps, <60s
- 7-9: 3-5 commands, ≤2 minutes, minimal manual config  
  _Example_: Next.js "npx create-next-app" → "npm run dev"  
  _External benchmark_: [Next.js Installation](https://nextjs.org/docs/getting-started/installation) — 2 commands
- 4-6: 6-10 commands, requires reading docs, some troubleshooting expected  
- 1-3: >10 commands, multi-file edits, platform-specific workarounds  
- 0: Undocumented or requires external knowledge to install

**Testable**: Run install instructions on clean VM, measure wall-clock time + command count

---

### D2: Value Prop Clarity (0-10 scale)
**What it measures**: Can a developer articulate "what this does and why I need it" after reading the first 3 paragraphs?

**Scoring**:
- 10: Opening statement = {who uses it} + {what pain it solves} + {why alternatives fail}  
  _Example_: Y-star-gov "Your AI agents are doing things you don't know about. Not because they are malicious — because nothing stops them."  
  _External benchmark_: [Supabase README](https://github.com/supabase/supabase) — "Postgres development platform building Firebase features with enterprise-grade open source tools"
- 7-9: Opening statement = {category} + {unique capability}  
  _Example_: gov-mcp "Governed execution for any AI agent framework. Install in 30 seconds."
- 4-6: Vague benefit claim ("faster", "better", "easier") without specifics  
- 1-3: Feature list with no problem statement  
- 0: No opening value prop, jumps straight to installation

**Testable**: Ask 3 developers to read first 3 paragraphs, then state the value prop in one sentence. 3/3 correct = 10, 2/3 = 7, 1/3 = 4, 0/3 = 0

---

### D3: Evidence Backing (0-10 scale)
**What it measures**: Are performance claims, security claims, and problem statements backed by data?

**Scoring**:
- 10: Every quantitative claim has source (benchmark file, experiment ID, commit hash, external study)  
  _Example_: Y-star-gov "check() 0.042ms mean — 2.4× faster than Microsoft AGT benchmark" + link to `benchmarks/check_latency.py`  
  _External benchmark_: [Vercel Edge Network Performance](https://vercel.com/docs/edge-network/performance) — cites p50/p99 with timestamp
- 7-9: Most claims backed, 1-2 unverified assertions  
- 4-6: Some claims backed, but critical metrics lack sources  
- 1-3: Generic claims ("fast", "secure") with no numbers  
- 0: Fabricated data or no evidence

**Testable**: Count claims → count citations → % coverage. 100% = 10, 80% = 8, 50% = 5, <20% = 1

---

### D4: Competitive Differentiation (0-10 scale)
**What it measures**: Does the README explicitly name competitors and state what's different?

**Scoring**:
- 10: Named competitors + comparison table OR paragraph explaining "vs X, we do Y"  
  _Example_: Y-star-gov "vs LangSmith/Langfuse/Arize: They are observability tools. Y*gov is enforcement."  
  _External benchmark_: [Tailwind CSS "Why not inline styles?"](https://tailwindcss.com/docs/utility-first#why-not-inline-styles) — addresses objections head-on
- 7-9: Implicit differentiation (describes unique capability without naming competitors)  
- 4-6: Vague "unlike others" claim with no specifics  
- 1-3: No differentiation section  
- 0: Actively misleading (claims uniqueness on non-unique features)

**Testable**: Search README for competitor names OR unique technical terms (e.g., "causal AI", "deterministic enforcement"). Present = 7+, absent = ≤3

---

### D5: Failure/Limitation Honesty (0-10 scale)
**What it measures**: Does the README disclose what the product does NOT do or what has failed?

**Scoring**:
- 10: Explicit "Limitations" or "Not Yet Available" section with roadmap dates  
  _Example_: gov-mcp "Limitations (Honest Assessment)" — lists 6 items with "Implemented" / "Roadmap"  
  _External benchmark_: [Stripe API Versioning](https://docs.stripe.com/sdks/versioning) — "Breaking changes" section with migration guides
- 7-9: Acknowledges one category of limitation (e.g., "Phase 1: observability only, not interception")  
- 4-6: Buried disclaimer in FAQ or footnote  
- 1-3: No limitations disclosed  
- 0: Misleading omission (e.g., claims "production-ready" when key features missing)

**Testable**: Search for "limitation", "not yet", "roadmap", "known issue". Present with specifics = 10, generic disclaimer = 5, absent = 0

---

### D6: Real-World Evidence (0-10 scale)
**What it measures**: Does the README cite real incidents, real users, or real operational data?

**Scoring**:
- 10: Named incidents OR operational metrics with dates + commit hashes OR customer case studies  
  _Example_: ystar-company "Day 1 (2026-03-26) Company founded. CMO fabricated data — CASE-001"  
  _Example_: K9Audit "March 4, 2026 staging URL in prod config → K9 trace output"  
  _External benchmark_: [Cloudflare outage postmortem](https://blog.cloudflare.com/cloudflare-outage-on-july-17-2020/) — real incidents with timelines
- 7-9: Operational metrics without specific incidents (e.g., "50 agents, 1000 checks, zero leaks")  
- 4-6: Synthetic benchmarks only (no real-world data)  
- 1-3: Hypothetical scenarios ("Imagine if...")  
- 0: No real-world evidence

**Testable**: Count {date + incident} OR {date + metric + commit} references. ≥3 = 10, 1-2 = 7, 0 = 0

---

### D7: CLI/API Discoverability (0-10 scale)
**What it measures**: Can a developer find the command/function they need without leaving the README?

**Scoring**:
- 10: Command reference table OR API import list with one-line descriptions  
  _Example_: Y-star-gov "CLI Reference" — 25 commands with descriptions  
  _Example_: gov-mcp "Tools (38)" — 7-category table  
  _External benchmark_: [Stripe API Reference](https://docs.stripe.com/api) — left sidebar with all endpoints
- 7-9: Commands mentioned inline with examples  
- 4-6: "See docs for full API" with external link  
- 1-3: No API/CLI reference  
- 0: Outdated or incorrect command syntax

**Testable**: Search README for command reference table OR function import block. Present = 10, examples only = 7, "see docs" = 4, absent = 0

---

### D8: Troubleshooting Coverage (0-10 scale)
**What it measures**: Does the README preemptively address common failure modes?

**Scoring**:
- 10: Dedicated "Troubleshooting" section with ≥3 symptom→fix pairs  
  _Example_: Y-star-gov "Troubleshooting" — 4 issues (install fails, doctor reports issues, hook not firing, tests failing)  
  _External benchmark_: [Next.js Deployment Troubleshooting](https://nextjs.org/docs/pages/building-your-application/deploying#troubleshooting) — 7 common errors with fixes
- 7-9: Inline troubleshooting hints (e.g., "If X fails, run Y")  
- 4-6: FAQ with 1-2 troubleshooting items  
- 1-3: "Contact support" with no self-service guidance  
- 0: No troubleshooting section

**Testable**: Count symptom→fix pairs. ≥3 = 10, 1-2 = 7, 0 = 0

---

### D9: Narrative-to-Action Ratio (0-10 scale)
**What it measures**: Balance between "why this matters" (narrative) and "what to do now" (action)

**Scoring**:
- 10: Opening narrative (1-3 paragraphs) → immediate action (install snippet) → deeper narrative (problem/solution) → more action (CLI examples)  
  _Example_: gov-mcp opens with 2-line install snippet at line 6-7, before "Why" section  
  _External benchmark_: [Vercel Quickstart](https://vercel.com/docs/getting-started) — "Deploy in 60 seconds" button before "What is Vercel"
- 7-9: Narrative-heavy opening, but install snippet within first 200 lines  
- 4-6: Install snippet buried after 500+ lines of text  
- 1-3: All narrative, no actionable commands  
- 0: All commands, no context (man page style)

**Testable**: Line number of first install command. ≤50 lines = 10, 51-200 = 7, 201-500 = 4, >500 = 1

---

### D10: Maintenance Signal (0-10 scale)
**What it measures**: Does the README reflect active maintenance or abandonment?

**Scoring**:
- 10: "Last updated" date ≤30 days + version badge + recent activity proof (e.g., "Day 18 operations" or "v0.48.0 shipped 2026-04-10")  
  _Example_: Y-star-gov "v0.48.0 · MIT License · Y* Bridge Labs" + "New in v0.48.0: CIEU Evidence Grading"
- 7-9: Version badge + "Last updated" ≤90 days  
- 4-6: No date, but content references recent tech (e.g., "Claude Code", "MCP 2024-11-05")  
- 1-3: No version, no date, references deprecated tech  
- 0: "WIP" / "Coming soon" with no recent commits

**Testable**: Check for version badge OR "Last updated" metadata. Present + ≤30d = 10, ≤90d = 7, inferred recent = 4, none = 0

---

## Composite Score

**Total score**: Sum of 10 dimensions (max 100)

**Grading**:
- 90-100: **Best-in-class** (Stripe / Vercel / Supabase tier)
- 75-89: **Strong** (clear value, evidence-backed, minor gaps)
- 60-74: **Functional** (adequate for existing users, friction for new users)
- 40-59: **Weak** (significant gaps, loses readers)
- 0-39: **Failing** (unusable for new users, must rewrite)

---

## Audit Frequency

**Weekly** (Sunday EOD deadline, per ForgetGuard rule `cmo_weekly_readme_audit_missed`)

Each audit produces:
1. `reports/cmo/readme_audit_YYYY-WW.md` — scores for all 4 repos
2. Week-over-week delta (gaps closed, new gaps introduced)
3. Top 3 priority fixes for next week

---

## Sources

- [Stripe API Quick Start](https://docs.stripe.com/payments-api/tour) — Install friction benchmark
- [Stripe Developer Experience Teardown (Moesif)](https://www.moesif.com/blog/best-practices/api-product-management/the-stripe-developer-experience-and-docs-teardown/) — Personalization + language flexibility
- [Supabase README](https://github.com/supabase/supabase) — Value prop clarity
- [Vercel Edge Network Performance](https://vercel.com/docs/edge-network/performance) — Evidence backing (p50/p99 latency)
- [Tailwind CSS "Why not inline styles?"](https://tailwindcss.com/docs/utility-first#why-not-inline-styles) — Competitive differentiation
- [Stripe API Versioning](https://docs.stripe.com/sdks/versioning) — Failure honesty (breaking changes)
- [Cloudflare Outage Postmortem](https://blog.cloudflare.com/cloudflare-outage-on-july-17-2020/) — Real-world evidence
- [Next.js Deployment Troubleshooting](https://nextjs.org/docs/pages/building-your-application/deploying#troubleshooting) — Troubleshooting coverage

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-04-15 | Initial 10-dimension framework created | Sofia Blake (CMO) |
