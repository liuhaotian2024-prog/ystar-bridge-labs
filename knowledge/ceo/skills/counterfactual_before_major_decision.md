# Counterfactual Reasoning Before Major Decisions

## When to Use This

**Trigger**: You are about to make a strategic decision, major choice, or policy change.

**Mandatory when**:
- Decision affects >1 agent or >1 sprint timeline
- Decision involves resource allocation (Board approval, budget, external partnerships)
- Decision sets precedent (new policy, governance change, architectural direction)
- You used keywords: "decide", "决策", "strategic", "战略", "we should commit to X"

**NOT required for**:
- Routine execution within established plans
- Reversible tactical choices (can undo in <1 day)
- Board-explicit directives (Board already did counterfactual analysis)

---

## Core Pattern

Before committing to decision X, MUST explore 3 counterfactual scenarios:

### Step 1: State Your Decision
Write one sentence: "I propose we do X because Y."

Example: "I propose we build video content first (before blog posts) because visual demos convert better on Show HN."

### Step 2: Inversion — What If We Do the Opposite?
- What does NOT-X look like?
- What benefits does NOT-X have that X lacks?
- Under what conditions would NOT-X be the right choice?

Example: "If we do blog posts first: faster to produce, better SEO, easier to update. This would be right if our audience is technical researchers who prefer text depth over video demos."

### Step 3: Failure Mode — How Does X Fail?
- What assumptions must hold for X to succeed?
- What happens if those assumptions break?
- What early warning signals detect failure?

Example: "Video strategy fails if: (1) AI-generated faces look uncanny and damage credibility, (2) target audience doesn't watch videos (reading culture in dev tools space), (3) videos become outdated faster than we can update them. Early warning: low view counts in first 2 weeks."

### Step 4: Regret Minimization — Which Failure Hurts Less?
- If X fails, how bad is the damage? (reversible? sunk cost?)
- If NOT-X was correct and we chose X, what did we lose?
- Which regret is easier to live with?

Example: "If video strategy fails: wasted 1 week of CMO time, but we still have blog posts as fallback. If blog-first was correct: lost early momentum on Show HN (videos get more upvotes), but blog content is still valuable long-term. Verdict: video failure is cheaper regret (1 week vs. missed launch window)."

### Step 5: Decision with Escape Hatch
Finalize decision X with explicit:
- **Commit**: what we're doing
- **Abort condition**: when we kill this and pivot
- **Fallback**: what we do if we abort

Example:
- Commit: build 5 videos, publish by Day 7
- Abort: if <100 views total after 2 weeks, pivot to blog-heavy strategy
- Fallback: repurpose video scripts into long-form blog posts

---

## Common Mistakes

1. **Counterfactual = strawman**: making NOT-X intentionally weak to justify X.
   - Fix: Steelman NOT-X. What's the BEST argument against your decision?

2. **Skipping Step 4 (regret)**: treating all mistakes as equally bad.
   - Fix: Reversible mistakes are cheap. Irreversible mistakes (vendor lock-in, public commitments) need more scrutiny.

3. **No abort condition**: infinite commitment to sunk cost.
   - Fix: Every major decision needs a "kill switch" metric. Define it upfront.

4. **Counterfactual theater**: doing this after you already decided, just to check a box.
   - Fix: If counterfactual reveals new info, you MUST update your decision. Otherwise it's fake rigor.

5. **Analysis paralysis**: spending more time on counterfactual than execution.
   - Fix: Time-box to 15 minutes. If decision is still unclear, escalate to Board.

---

## Example

**Decision**: Should Y* Bridge Labs open-source Y*gov now or wait until 10K users?

### Step 1: Proposal
"Open-source Y*gov on Day 1 because transparency builds trust in governance tools."

### Step 2: Inversion
"If we wait until 10K users: we can iterate faster without public scrutiny, avoid early critics poisoning perception, control narrative when we open-source ('battle-tested at scale'). This would be right if early adopters are risk-averse enterprises who need social proof before trusting governance tools."

### Step 3: Failure Mode
"Open-source-now fails if: (1) competitors copy our code before we establish brand, (2) early messy commits damage credibility, (3) premature community building drains team bandwidth. Early warning: GitHub issues flood with feature requests we can't prioritize."

### Step 4: Regret Minimization
"If open-source-now fails: we gave away competitive advantage, but we built community goodwill and recruited contributors. If closed-source-first was correct: we missed the 'indie hacker authenticity' wave (HN loves Day 1 open source), but we controlled quality narrative. Verdict: open-source regret is cheaper (competitors need months to productize our code, but missed HN momentum is gone forever)."

### Step 5: Decision
- **Commit**: Open-source on Day 1 (GitHub public repo at Show HN launch)
- **Abort condition**: If 3+ competitors ship Y*gov clones within 1 month AND our differentiation is unclear, pivot to "open core" model (governance engine open, enterprise features proprietary)
- **Fallback**: Emphasize operational expertise (Y* Bridge Labs as case study) over code availability

**Outcome**: Board approved open-source Day 1. Counterfactual analysis surfaced the "competitor clone" risk, leading to backup plan (open core model) that didn't exist before this exercise.

---

**Board Wisdom**: "反事实不是为了找到完美决策——是为了提前看到决策会在哪里失败，这样你就不会被失败surprise。"

Counterfactual isn't about finding the perfect choice. It's about seeing where your choice will break, so failure doesn't surprise you.
