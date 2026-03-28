# HN-Quality Technical Writing Guide
## Distilled from Y* Bridge Labs Series 1 & 2 Production Experience

**Author:** Haotian Liu + Claude (AI strategic advisor)
**Status:** Validated against two full article production cycles
**Target:** Alex (CMO) and future writing agents

---

## Part 1: The Single Most Important Rule

**Every HN article must prove exactly one thing.**

Not two. Not five. One.

Before writing a single word, state your central claim in one sentence:

> "AI governance systems are missing a first-class representation of what should have happened."

If you cannot state it in one sentence, you do not yet know what you are writing. Stop. Think. Then write.

Everything in the article — every example, every paragraph, every sentence — must either prove this claim, set it up, or defend it against the most obvious objection. If a paragraph does none of these three things, delete it.

---

## Part 2: The Paradigm Shift Framework

HN rewards articles that break existing mental models and replace them with better ones. This is the structure:

**Step 1 — The Hook (first 200 words)**
Open with a concrete, instantly-understandable failure case. Not your product. Not a definition. A situation any engineer can recognize in five seconds.

Rules for the hook:
- One specific scenario, not a category
- Numbers make it real: "$5,000" beats "large payment"
- End with a structural observation, not a complaint: "This is not a logging problem. It is a missing design primitive."
- Never start with "We built X" or "X is important because"

**Step 2 — The Existing Answer Is Wrong**
Name what everyone currently does. Then show precisely why it fails — not that it is bad, but that it answers the wrong question entirely.

The framing that works: *"Most [category] systems are designed around a question they can answer: [X]. We start from a different question: [Y]."*

This is more powerful than "existing tools are insufficient" because it reframes the problem rather than attacking solutions.

**Step 3 — The Missing Object**
Introduce your concept not as a feature but as a thing that should exist but doesn't. Name it. Define it precisely. Give it a one-sentence definition that can be quoted and debated:

> "Y* is the machine object that stands for what should be true before an action is allowed to happen."

This sentence must be:
- Short enough to quote in a comment
- Specific enough to be wrong (so people can argue about it)
- Different from existing concepts (goal, reward, policy, log)

**Step 4 — What Changes Once It Exists**
Show 2-3 concrete things that become possible or definable. Not marketing claims. Operational changes. "You are no longer comparing reality to a human expectation. You are comparing it to an explicit predicate recorded before the action ran."

**Step 5 — Honest Boundaries**
State clearly what your concept does NOT solve. This is not weakness — it is the most trust-building section. HN readers will find your limits whether you name them or not. Name them first.

**Step 6 — The Open Question**
End with a genuine unsolved problem that invites debate. Not "what do you think?" but a specific technical or philosophical question that the article's argument naturally raises. The best open questions have defensible positions on multiple sides.

---

## Part 3: Evidence Architecture

**Three tiers of evidence, used in sequence:**

**Tier 1 — Universal case (hook)**
A scenario any engineer anywhere can understand immediately. Does not need to be your own experience. The $5,000 payment example. The employee who submits a reimbursement with no approved budget. Pure setup.

**Tier 2 — Your own real failures**
Your actual experiments, bugs, and incidents. This is where CFO fabrication and CMO audit record forgery go. These prove you are not theorizing — you have lived the problem. Must be specific: names, numbers, actual outputs.

**Tier 3 — Code (in the repo, not the article)**
Source-level excerpts for readers who want to verify. Never put more than 2-3 short code blocks in a HN article. The rest goes in the repo with a single link at the end. Code in the article is for illustration, not proof.

---

## Part 4: What Kills HN Articles

**The four failure modes, ranked by frequency:**

**1. Proving too many things**
The article claims to solve permission enforcement, audit chains, delegation, obligation tracking, supply chain security, and cost reduction. The reader cannot hold one clear idea. Result: polite upvotes, no comments, forgotten by tomorrow.

**2. Leading with the system instead of the problem**
"We built Y*gov, a runtime governance framework for multi-agent AI systems..." The reader has no reason to care yet. Always lead with the problem the reader already has.

**3. The audit/logging trap**
If your concept is genuinely about enforcement at execution time, never let "audit," "log," or "observability" become the main subject of your sentences. These words prime the reader to think post-hoc. Use "enforcement," "execution," "contract," "governed action" as subjects instead.

**4. Terminology front-loading**
CIEU, OmissionEngine, DelegationChain, NonceLedger, MetaLearning — these are real and important. They are not for the first article. Introduce one new term per article. Define it precisely. Move on.

---

## Part 5: The Transparency Declaration

Y* Bridge Labs articles open with a declaration of authorship and context. This is not boilerplate — it is a deliberate stance.

**Why it works on HN:**
- HN rewards authenticity above all else
- Declaring AI authorship preempts the most common attack ("this is AI slop")
- It frames the article as a demonstration of the company's own thesis
- It turns the authorship question into a feature, not a liability

**Template:**
> *Written by [Agent name] ([role]) and Haotian Liu (founder), Y\* Bridge Labs. [One sentence connecting this post to the previous one or to the broader project.] [One sentence stating what this post is about and what it is not about.]*

Keep it under 50 words. Every word must carry information.

---

## Part 6: Length and Density

**Target: 800–1,100 words for the main body.**

HN readers read on screens, often in one sitting. Longer articles are not more authoritative — they are more likely to be abandoned.

Density rules:
- Every paragraph makes one point
- No paragraph longer than 5 sentences
- No section longer than 200 words
- The definition of your central concept must appear by the halfway point

**What to cut:**
- Any paragraph that starts with "Additionally" or "Furthermore"
- Any sentence that restates what the previous sentence just said
- Product features that are not directly required to prove the central claim
- The history of why you started building this

**What never to cut:**
- The concrete opening example
- The one-sentence definition of your central concept
- The "what this does not solve" section
- The open question at the end

---

## Part 7: The Sentence That Gets Quoted

Every great HN post has one sentence that gets copied into comments, cited in other posts, and remembered. You cannot force this — but you can write toward it.

Characteristics of quotable sentences:
- Short (under 20 words)
- Directly contradicts a common assumption
- Can be argued against (too safe = not memorable)
- Does not contain jargon

From our articles:
> "You cannot enforce natural language. You can only enforce predicates."

> "Y\* is the machine object that stands for what should be true before an action is allowed to happen."

> "The proof of governance was itself ungoverned."

Write ten candidate sentences. Keep one.

---

## Part 8: The Review Process

**Before publishing, run this checklist:**

**Structural:**
- [ ] Can I state the central claim in one sentence?
- [ ] Does the opening paragraph contain a concrete, specific example?
- [ ] Is the central concept defined precisely by the midpoint?
- [ ] Is there a "what this does not solve" section?
- [ ] Does the article end with a specific open question, not a generic CTA?

**Tone:**
- [ ] Does the article sound like a person thinking, not a company selling?
- [ ] Is "we" used for honest statements about our own experience, not marketing claims?
- [ ] Are limitations stated before the reader finds them?

**Terminology:**
- [ ] How many new terms are introduced? (Target: 1-2 maximum)
- [ ] Is each new term defined the first time it appears?
- [ ] Are there any terms that only insiders would understand without definition?

**Evidence:**
- [ ] Is the opening example universally understandable?
- [ ] Are the "our own experience" examples specific (names, numbers, actual outputs)?
- [ ] Is code in the repo, not blocking the article flow?

**The test:**
Read the article aloud. If you stumble on a sentence, cut it or rewrite it. If you feel embarrassed reading a paragraph aloud, delete it.

---

## Part 9: Series Architecture

When writing a series, each article must:

1. **Stand alone** — a reader who missed the previous article should still understand and find value
2. **Connect forward** — end with a hook into the next article's problem, not just "stay tuned"
3. **Escalate the abstraction** — Series 1 is empirical (what we observed), Series 2 is conceptual (what the observation reveals), Series 3 is mechanistic (how to solve the harder problem the concept exposes)

The connection sentence at the end of each article should name the specific problem the next article addresses:

> "There is a third case — what happens when a required action never occurs at all — but that requires a different mechanism. That is Series 3."

Not: "Next time we will discuss omission." But: here is exactly why the current concept is insufficient for this case.

---

## Part 10: What We Learned the Hard Way

**Lessons from Series 1 and 2 production:**

1. **"Four quadrants" frameworks kill HN articles.** We tried to introduce a four-situation diagnostic taxonomy (A/B/C/D). Every reviewer told us it felt like a methodology training deck, not a technical post. We deleted it. The insight survived; the framework did not.

2. **Audit language is a trap.** Every time we used "audit chain," "audit record," or "observability," readers mentally categorized us as "a better logging tool." We had to actively replace these words with "enforcement," "execution," and "contract" throughout.

3. **The code appendix belongs in the repo.** We spent two rounds trying to include reproducible code in the article. Every reviewer said it was too heavy. The right answer: one sentence linking to the repo. Engineers who want the code will find it.

4. **Two AI reviewers (Claude + ChatGPT) reviewing the same draft produces better output than one.** They caught different things. Claude caught structural and argument issues. ChatGPT caught HN-specific positioning and length issues. Use both.

5. **The founding story is not the article.** "We built this while trying to run our own company with AI agents" is context for the author bio, not the article. The article is about the idea. The company is evidence the idea is real.

6. **The first sentence of each section does more work than any other.** HN readers scan. If the first sentence of a section does not earn their continued reading, they skip. Write section openers last, after you know what the section proves.

---

*This guide was produced after two full article production cycles: Series 1 (EXP-001 controlled experiment) and Series 2 (Y* conceptual foundation). It should be updated after each subsequent article production cycle.*

*Last updated: 2026-03-28*
*Next review: after Series 3 production*
