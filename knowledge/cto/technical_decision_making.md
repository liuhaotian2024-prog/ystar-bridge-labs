# Technical Decision-Making Framework

## Build vs Buy Framework

**Definition**: Deciding whether to create custom solution or use existing tool/service.

### When to Build
- Core differentiator (competitive advantage)
- Existing solutions don't meet requirements
- Requirements change frequently (need control)
- Long-term cost of buying exceeds building
- Security/compliance requires on-premise

### When to Buy
- Commodity functionality (auth, payments, email)
- Faster time to market critical
- Vendor has domain expertise you lack
- Not enough team capacity to maintain
- Free tier or low cost covers needs

### Decision Steps
1. Define requirements (must-have vs nice-to-have)
2. Research: Find 3-5 existing solutions
3. Evaluate: Score each on features, cost, vendor stability, lock-in risk
4. Estimate: Build cost (eng-months × loaded salary) vs buy (5-year TCO)
5. Prototype: Spike hardest part (1-2 days) to validate estimate
6. Decide: Document decision in ADR (see below)

### Evaluation Scorecard
| Criteria | Weight | Option A | Option B | Build |
|----------|--------|----------|----------|-------|
| Features | 30% | | | |
| Cost (5yr) | 25% | | | |
| Reliability | 20% | | | |
| Lock-in | 15% | | | |
| Team skill | 10% | | | |

Multiply score × weight, sum per option.

### Common Mistakes
- Underestimating maintenance (initial build is 20% of lifetime cost)
- Not-invented-here syndrome (rebuilding for ego)
- Ignoring opportunity cost (building X means not building Y)
- Evaluating only year 1 cost (vendors increase pricing)
- Building before validating need (might not need feature at all)

## RFC/Design Doc Process

**Definition**: Written proposal for significant technical changes.
- Forces thinking before coding
- Creates space for feedback
- Documents decisions for future

### When to Write RFC
- Changes affecting multiple systems
- New public API or breaking changes
- Architectural shifts (monolith to microservices)
- Estimated >2 weeks of work
- High uncertainty (spike needed before commit)

Skip for: bug fixes, minor refactors, documentation updates

### RFC Template
1. Title and author
2. Status (Draft / Review / Approved / Deprecated)
3. Summary (2-3 sentences)
4. Motivation (why now? what problem?)
5. Proposed solution (how it works, diagrams)
6. Alternatives considered (and why rejected)
7. Open questions
8. Timeline and milestones

### RFC Workflow
1. Author drafts RFC (1-3 pages, not a novel)
2. Share with team, collect feedback (async comments, 3-5 days)
3. Hold review meeting if controversial (30-60min)
4. Revise based on feedback
5. Approve and commit to repo (docs/rfcs/001-feature-name.md)
6. Reference RFC in related PRs

### Common Mistakes
- Writing code before RFC (sunk cost bias blocks feedback)
- RFC too detailed (over-specifying implementation)
- No alternatives section (looks like you didn't explore)
- Skipping RFC for "quick" project that grows (accumulates debt)
- Not updating RFC when design changes (documentation drift)

## Architecture Decision Records (ADR)

**Definition**: Lightweight document capturing one decision and rationale.
- Shorter than RFC (0.5-1 page)
- Immutable (never edit, only supersede)
- Numbered sequentially (001, 002, ...)

### When to Write ADR
- Choosing database (Postgres vs MongoDB)
- Selecting framework (FastAPI vs Flask)
- Adopting tool (GitHub Actions vs Jenkins)
- Defining standard (REST vs GraphQL)

Every build vs buy decision should produce ADR.

### ADR Template
```
# ADR-005: Use Anthropic Claude for agent runtime

## Status
Accepted

## Context
Y*gov needs LLM provider for agent execution. Requirements:
- Function calling support
- >100K context window
- SOC2 compliance

## Decision
Use Anthropic Claude API as primary provider, with OpenAI fallback.

## Consequences
Positive:
- Best-in-class context window
- Strong safety features
- SDK quality

Negative:
- Vendor lock-in risk
- Cost higher than self-hosted

## Alternatives Considered
- OpenAI GPT-4: Smaller context window
- Self-hosted LLaMA: Compliance burden, infra cost
```

### Common Mistakes
- Writing ADR after implementation (should guide, not justify)
- Editing old ADRs (breaks history, use superseding ADR instead)
- No consequences section (every decision has tradeoffs)
- Storing in wiki instead of Git (loses version history)

## Tech Stack Evaluation Criteria

**Definition**: Systematic assessment of languages, frameworks, tools.

### Evaluation Dimensions
1. Team expertise (can we support it?)
2. Community size (StackOverflow questions, GitHub stars)
3. Hiring pool (can we find talent?)
4. Maturity (production-ready or beta?)
5. Performance (benchmarks for our use case)
6. License (open source? Commercial terms?)
7. Vendor stability (company health, funding)
8. Ecosystem (libraries, integrations)

### Scoring Process
1. Weight dimensions (not all equal for your context)
2. Score each option 1-5 per dimension
3. Multiply score × weight
4. Sum total score
5. Pick highest, but check gut feel (numbers aren't everything)

### Red Flags (Automatic Disqualifiers)
- Abandoned project (no commits in 12+ months)
- Single maintainer for critical infrastructure
- No security updates for known CVEs
- Incompatible license (AGPL for proprietary product)
- No clear upgrade path from current version

### Common Mistakes
- Choosing based on hype (wait for maturity curve)
- Ignoring hiring market (cool tech, no engineers)
- Not prototyping (looks good, integrates poorly)
- Analysis paralysis (diminishing returns after 3 options)

## Refactoring Decision Framework (Martin Fowler)

**Definition**: Improving code structure without changing external behavior.

### When to Refactor
- Before adding feature (make change easy, then make easy change)
- During code review (opportunistic refactoring)
- When touching code third time (rule of three)
- When onboarding is slow (complexity tax visible)

Don't refactor:
- When rewrite is cheaper (see below)
- Right before major deadline (risk vs reward)
- Code you'll delete soon

### Refactoring Process
1. Ensure tests pass (establish baseline)
2. Make small change (rename, extract function)
3. Run tests (verify behavior unchanged)
4. Commit (incremental commits, easy revert)
5. Repeat

Never: change behavior and structure simultaneously.

### Refactoring Checklist
- [ ] Test coverage >70% before starting
- [ ] Each refactor step takes <30min
- [ ] Tests pass after each step
- [ ] Can explain improvement to teammate

### Common Mistakes
- Big bang refactor (change everything, break everything)
- No tests (can't verify correctness)
- Refactoring + feature in same PR (too much to review)
- Perfectionism (done is better than perfect)

## Rewrite vs Iterate Decision

**Definition**: When to rebuild from scratch vs incrementally improve.

### When to Rewrite
- Technology obsolete (Python 2, Flash)
- Core assumptions changed (single-tenant to multi-tenant)
- Faster to rewrite than understand (rare, be honest)
- Codebase <10K lines (manageable scope)

### When to Iterate
- System is making money (don't kill golden goose)
- Team knows codebase (knowledge in code, not docs)
- Requirements unclear (rewrite will be equally messy)
- Large codebase (>50K lines, multi-year rewrite risk)

### The Strangler Fig Pattern (Safer Than Rewrite)
1. Build new system alongside old
2. Migrate one feature at a time
3. Route traffic to new implementation
4. Delete old code when fully migrated
5. Repeat

Reduces risk, delivers value incrementally.

### Decision Checklist
- [ ] Estimated rewrite time (multiply by 3 for reality)
- [ ] Can we maintain old system during rewrite?
- [ ] Do we understand why old system failed?
- [ ] Will requirements stay stable during rewrite?
- [ ] Have we tried strangler fig pattern?

If all yes, rewrite. Otherwise, iterate.

### Common Mistakes
- Rewriting working code (you'll reintroduce old bugs)
- Not migrating old features (users revolt)
- Underestimating scope (always 3x longer than planned)
- Ignoring sunk cost (falling for fallacy)
- No kill criteria (zombie rewrites that never ship)

## Applied to Y*gov

### Recent Decisions
- **Build governance framework** (core differentiator, no existing solution)
- **Buy LLM API** (Anthropic Claude - commodity, faster than training)
- **Build CLI tool** (control over UX, integrates with unique CIEU format)
- **Buy CI/CD** (GitHub Actions - standard, low cost)

### Decision Velocity
- Small decisions (<1 day work): CTO decides, inform CEO
- Medium decisions (1-2 weeks): Write ADR, CEO approves
- Large decisions (>2 weeks): Write RFC, board review

Every technical decision logged in Git, never in Slack.
