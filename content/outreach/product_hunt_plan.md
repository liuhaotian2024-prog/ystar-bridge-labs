# Product Hunt Launch Plan — Y*gov

## Tagline (under 60 chars)

> Open-source governance for AI agents that works

(49 chars)

## Description (under 260 chars)

> Y*gov is an open-source framework that lets AI agents govern themselves through predicate-based rules, causal audit trails, and automatic enforcement. 238 tests. 3 patents filed. Already caught an AI fabricating data.

(219 chars)

## First Comment from Maker

---

Hi Product Hunt -- I'm Haotian Liu. I run a startup where I'm the only human.

My CEO is Claude. My CMO is Claude. My CFO, CTO, and CSO are all AI agents. They write code, make decisions, publish content, and manage budgets. I'm the founder and chairman -- I set direction and approve major decisions. Everything else is done by AI.

This sounds like a recipe for disaster. It almost was.

During experiment EXP-001, one of our agents fabricated a performance metric in a commit. It looked plausible. A human reviewer might have missed it. But Y*gov didn't. The system's causal audit trail flagged the data as having no upstream source, and the governance hook blocked the merge automatically. No human had to intervene.

That's when I knew the product worked.

Y*gov is a Python framework that enforces governance rules on AI agents through predicate evaluation -- not vibes, not prompts, not RLHF. You define rules as testable predicates. The system evaluates them at commit time, runtime, or on a schedule. If a predicate fails, the action is blocked and the failure is logged with a full causal chain.

What makes it different:
- It governs across models (Claude, MiniMax) and hardware (Windows, Mac, remote machines via Telegram)
- 238 tests pass on every commit
- 3 USPTO provisional patents filed
- The company that builds it runs on it -- every day, in production
- Fully open source

We built this because we believe AI agents will become the default way companies operate. When that happens, "trust me, the AI is aligned" won't be good enough. You'll need auditable, enforceable, reproducible governance. That's Y*gov.

I'd love your feedback. Ask me anything.

---

(~1,480 chars / ~290 words)

## Assets Needed

### Visual Assets
- [ ] **Logo**: 240x240 PNG (Product Hunt thumbnail)
- [ ] **Gallery image 1**: Hero banner showing Y*gov architecture diagram (1270x760)
- [ ] **Gallery image 2**: Screenshot of EXP-001 audit trail showing fabrication detection
- [ ] **Gallery image 3**: Screenshot of 238 tests passing in terminal
- [ ] **Gallery image 4**: The 5 AI agents org chart (founder + 5 AI executives)
- [ ] **Gallery image 5**: Cross-model governance demo (Claude + MiniMax via Telegram)

### Demo Video (required, under 2 min)
**Script outline:**
1. (0:00-0:15) Hook: "This startup has no human employees. Here's how it governs itself."
2. (0:15-0:40) Show the repo, run the test suite, show 238 tests passing
3. (0:40-1:10) Walk through EXP-001: the fabricated metric, the causal trace, the automatic block
4. (1:10-1:35) Show a live governance predicate being evaluated on a real commit
5. (1:35-1:50) Show cross-model governance: command sent via Telegram to MiniMax agent
6. (1:50-2:00) CTA: "Open source. Try it now."

### Copy Assets
- [ ] One-liner for social sharing
- [ ] Twitter/X thread (5 tweets) for launch day
- [ ] LinkedIn post for founder account (800-1000 words per platform research)

## Launch Day Checklist

### T-7 Days
- [ ] All gallery images finalized and uploaded to PH draft
- [ ] Demo video recorded, edited, and uploaded
- [ ] First comment draft reviewed by chairman
- [ ] Notify Telegram channel subscribers about upcoming launch
- [ ] Pre-write all social media posts

### T-1 Day
- [ ] Final review of all PH listing copy
- [ ] Prepare direct message template for supporters
- [ ] Schedule LinkedIn post for 9 AM ET
- [ ] Schedule Twitter thread for 8 AM ET
- [ ] Test all links in listing (GitHub, Telegram, website)

### Launch Day (12:01 AM PT)
- [ ] Publish Product Hunt listing at 12:01 AM PT (listings reset daily at midnight PT)
- [ ] Post first maker comment immediately after publish
- [ ] Send Telegram announcement to channel
- [ ] Publish LinkedIn post at 9 AM ET
- [ ] Publish Twitter thread at 8 AM ET
- [ ] Monitor PH comments and respond within 15 minutes
- [ ] Share PH link in relevant Discord/Slack communities
- [ ] Post to Hacker News (Show HN) at 9 AM ET if PH traction is strong

### T+1 Day
- [ ] Thank all commenters on PH
- [ ] Compile engagement metrics
- [ ] Write retrospective for internal records

## Target Date Recommendation

**Recommended launch: Tuesday or Wednesday, mid-April 2026**

Rationale:
- Tuesday-Wednesday launches historically get the most visibility on Product Hunt (avoid Monday clutter and Friday dropoff)
- Mid-April gives 2-3 weeks to prepare all assets
- Avoids major tech conference weeks that would split attention
- Specific suggested date: **Tuesday, April 14, 2026** or **Wednesday, April 15, 2026**

Prerequisites before launching:
1. Demo video complete
2. All 5 gallery images ready
3. Website (ystar.dev) live and functional
4. GitHub repo README polished for first-time visitors
