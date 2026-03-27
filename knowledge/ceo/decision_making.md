# CEO Decision-Making Frameworks

## Bezos's Reversible vs. Irreversible Decisions

**Definition**: Type 1 decisions are irreversible (one-way doors). Type 2 decisions are reversible (two-way doors). Treat them differently.

**Decision Classification**:
| Type 1 (Irreversible) | Type 2 (Reversible) |
|-----------------------|---------------------|
| Major pivots | Feature experiments |
| Key hires/fires | Pricing tests |
| Fundraising terms | Marketing channels |
| Legal commitments | Tool choices |
| Public statements | Process changes |

**Step-by-Step Execution**:
1. Ask: "If this fails, can we undo it within 3 months at acceptable cost?"
2. If YES (Type 2): Decide fast, delegate down, bias toward action
3. If NO (Type 1): Slow down, gather data, involve Board, document reasoning

**Application at Y* Bridge Labs**:
- Type 2: Let department agents decide autonomously
- Type 1: Escalate to Board (Haotian) for confirmation

**Common Mistakes**:
- Treating all decisions as Type 1 (paralysis)
- Treating Type 1 as Type 2 (reckless)
- Not recognizing when reversible decisions become irreversible at scale

---

## Andy Grove's Disagree-and-Commit

**Definition**: Debate vigorously until decision point, then execute fully regardless of personal disagreement.

**When to Use**:
- Cross-department decisions with conflicting recommendations
- Time-sensitive choices where consensus is impossible
- After healthy debate has reached diminishing returns

**Step-by-Step Execution**:
1. **Ensure Real Debate**: All stakeholders share concerns openly
2. **Set Decision Deadline**: "We decide by [time], then commit"
3. **Make the Call**: CEO decides based on evidence and believability
4. **Document Dissent**: Record who disagreed and why (for learning)
5. **Full Commitment**: Dissenters execute with full effort
6. **Retrospective**: After results, review who was right

**Application at Y* Bridge Labs**:
- CTO/CMO disagree on launch timing? Set deadline, decide, commit.
- Record in CIEU for accountability and learning.

**Common Mistakes**:
- Skipping real debate (false consensus)
- Half-hearted commitment after decision
- Using it to override without listening
- Never revisiting to learn who was right

---

## Ray Dalio's Believability-Weighted Decision Making

**Definition**: Weight opinions by track record and demonstrated expertise, not seniority.

**Believability Criteria**:
1. Has succeeded at the thing in question 3+ times
2. Can articulate cause-effect relationships
3. Has been stress-tested on their reasoning

**Step-by-Step Execution**:
1. **Map the Decision Domain**: What expertise is relevant?
2. **Assess Believability**: Who has demonstrated success in this domain?
3. **Weight Votes**: Believable opinions count more (e.g., 3x weight)
4. **Synthesize**: Don't average - understand why believable people disagree
5. **Decide**: Go with believability-weighted consensus unless you have strong reason

**Application at Y* Bridge Labs**:
- Technical decisions: CTO's opinion weighs heaviest
- Market decisions: CMO/CSO weigh heaviest
- Financial decisions: CFO weighs heaviest
- CEO synthesizes across domains

**Common Mistakes**:
- Confusing confidence with believability
- Equal weighting all opinions (democracy fallacy)
- Ignoring low-believability insights that may be valid
- Not building believability record over time

---

## First Principles Thinking

**Definition**: Decompose problems to fundamental truths, then rebuild reasoning from scratch.

**When to Use**:
- Industry "best practices" feel wrong
- Entering new territory without precedent
- Costs seem impossibly high

**Step-by-Step Execution**:
1. **State the Problem**: What are we trying to achieve?
2. **List Assumptions**: What does everyone "know" about this?
3. **Question Each**: "Why is this true? What if it weren't?"
4. **Find Fundamentals**: What's actually, provably true?
5. **Rebuild**: Design solution from fundamentals, ignoring convention

**Y* Bridge Labs Example**:
- Assumption: "Enterprise software needs a sales team"
- Question: Why? (Trust, customization, integration help)
- Fundamentals: Customers need confidence and successful deployment
- Rebuild: Dog-fooding + transparent CIEU audit + self-service = trust without sales team?

**Common Mistakes**:
- Stopping at "industry standard" as fundamental
- Over-applying (not everything needs first principles)
- Ignoring legitimate reasons for conventions

---

## Pre-Mortem Analysis

**Definition**: Imagine the project failed, then work backward to identify causes.

**When to Use**: Before major launches, investments, or commitments.

**Step-by-Step Execution**:
1. **Set the Scene**: "It's 6 months from now. This initiative failed completely."
2. **Individual Brainstorm** (5 min): Each person lists reasons for failure
3. **Share and Cluster**: Group similar failure modes
4. **Probability Assessment**: Rate likelihood of each (High/Medium/Low)
5. **Mitigation Planning**: For High/Medium, define prevention or detection measures
6. **Update Plan**: Incorporate mitigations before proceeding

**Pre-Mortem Template**:
```
Initiative: [Name]
Imagined Failure Date: [6 months out]

| Failure Mode | Likelihood | Early Warning Sign | Mitigation |
|--------------|------------|-------------------|------------|
| [What went wrong] | H/M/L | [How we'd detect it] | [Prevention] |
```

**Common Mistakes**:
- Groupthink (need individual brainstorm first)
- Listing only external factors (look internal too)
- No concrete mitigations
- Doing it but ignoring results
