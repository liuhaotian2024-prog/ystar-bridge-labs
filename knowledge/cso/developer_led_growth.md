# Developer-Led Growth — CSO Knowledge Base

## Peter Levine's Open Source GTM Model

**Definition**: Go-to-market strategy where open source adoption creates enterprise sales pipeline. Developer love becomes IT budget. Model used by MongoDB, HashiCorp, Databricks.

**When to use**: When product has open source or free tier, targets developers first, then sells enterprise features to their employers.

**Step-by-step**:
1. Open Core Strategy: Free Y*gov for individual developers (basic CIEU audit). Enterprise features (compliance packs, SSO, multi-tenant) are paid.
2. Adoption Metrics: Track GitHub stars, pip installs, monthly active developers. Goal: 10K+ free users creates 50-100 enterprise leads.
3. Developer Love: Make install trivial (`pip install ystar && ystar hook-install`). Documentation must be exceptional. Response time on GitHub issues <24hrs.
4. Usage Signal Detection: Monitor which companies have 5+ employees using free tier. Auto-alert CSO for outreach.
5. Enterprise Conversion Motion: "I see 12 developers at [Company] are using Y*gov. Want to talk about centralized governance and compliance reporting?"

**Common mistakes**:
- Paywalling core functionality too early (kills adoption)
- Enterprise version is completely different product (migration friction)
- Not instrumenting free tier to detect company usage patterns
- Treating GitHub issues as support burden instead of community building
- Expecting developers to pay (they don't have budgets; their bosses do)

---

## Product-Led Growth (PLG) Mechanics

**Definition**: Acquisition, conversion, and expansion driven by product itself, not sales team. Users self-serve signup, experience value, then convert to paid. Inverse of enterprise sales where sales happens before product usage.

**When to use**: Y*gov's developer tier (Type C customers). Free trial → individual paid → team plan → enterprise.

**Step-by-step**:
1. Activation Milestone: Define "aha moment." For Y*gov: generating first CIEU audit report. Goal: user hits this within 10 minutes of install.
2. Time-to-Value Optimization: Remove all friction. One command install. Auto-detect Claude Code. Pre-populate sample audit.
3. Usage-Based Triggers: "You've run 100 audits this month. Upgrade to Team plan for unlimited audits + Slack alerts."
4. In-Product Upgrade Path: When user hits free tier limit, show upgrade modal with one-click purchase (Stripe). No sales call required.
5. Expansion Hooks: "Invite teammates" feature. Viral coefficient >1 means exponential growth.

**Common mistakes**:
- Requiring credit card before trial (kills signups)
- Activation milestone is too far into product (user churns before value)
- No clear path from free to paid (user loves product but doesn't know upgrade exists)
- Upgrade CTAs are annoying instead of helpful (show upgrade option when user hits limit, not randomly)
- Not measuring conversion funnel (signup → activation → paid conversion → retention)

---

## Bottom-Up Adoption → Enterprise Expansion

**Definition**: Individual developer uses free tool → team adopts → IT/compliance discovers it → CSO sells enterprise deal. Reverse of top-down sales.

**When to use**: Y*gov's primary GTM motion. Developers install for personal projects, compliance officers discover it during audit.

**Step-by-step**:
1. Land (Developer): Free tier marketed on GitHub, Dev.to, Hacker News. SEO for "AI agent governance", "Claude Code audit trail".
2. Expand (Team): When 3+ developers from same company domain sign up, auto-send: "Want a team workspace? First 5 seats free."
3. Discover (IT/Compliance): Usage spike triggers notification to IT. Or: developer shows audit report to compliance officer during review.
4. Qualify (CSO): Compliance officer reaches out ("We have 30 developers using this, need enterprise compliance pack"). This is a hot inbound lead.
5. Close (Enterprise): CSO negotiates site license, compliance domain packs (FDA/SEC/SOC2), SSO, SLA.

**Common mistakes**:
- Blocking team formation in free tier (you want organic spread)
- Not tracking company-level signals (5 users from microsoft.com means opportunity)
- Treating inbound enterprise leads same as cold outbound (they're pre-qualified — fast-track them)
- IT bans the tool due to security concerns (must have security docs ready: SOC2, pen test results)

---

## Developer Community Building

**Definition**: Creating ecosystem where developers help each other, contribute code, advocate for product. Reduces support costs and creates organic growth.

**When to use**: Ongoing. Start when you have 100+ users.

**Step-by-step**:
1. GitHub Discussions: Enable on Y*gov repo. Seed with questions: "How are you using Y*gov?" "Feature requests?"
2. Discord/Slack Community: Create #support, #show-and-tell, #feature-requests channels. CSO monitors #show-and-tell for enterprise user signals.
3. Contributor Recognition: "Top 10 Contributors" page. Send swag. Highlight contributions in monthly newsletter.
4. Office Hours: Monthly "Ask Me Anything" with CTO. Recorded and posted to YouTube.
5. Case Studies: "How [Company] uses Y*gov for FDA compliance." Tag contributor, share on socials. Becomes sales asset.

**Common mistakes**:
- Creating community then ignoring it (kills engagement)
- Over-moderating (let developers be opinionated)
- Not converting community members into champions (invite top contributors to advisory board)
- Using community as free support (you still need to answer questions yourself)
- No moderation guidelines (toxicity kills communities)

---

## Freemium-to-Paid Conversion Optimization

**Definition**: Systematic improvement of conversion rate from free users to paying customers.

**When to use**: After 500+ free users. Before that, focus on product-market fit.

**Step-by-step**:
1. Instrument Funnel: Track every step. Signup → install → first audit → 10 audits → upgrade click → payment → active paid user.
2. Identify Drop-off Points: Where do users churn? If 50% never generate first audit, problem is activation. If users hit limits but don't upgrade, problem is pricing communication.
3. A/B Test Pricing Page: Test $29/mo vs $49/mo. Test annual discount (save 20% vs 2 months free). Test feature comparison table.
4. Reduce Friction: One-click upgrade (Stripe pre-filled). Grandfather existing usage (don't lose their audit history).
5. Win-Back Campaigns: Email users who hit free limit but didn't upgrade. "Your audit trail is waiting. Upgrade to unlock."

**Kyle Poyar PLG Benchmarks** (for calibration):
- Free-to-paid conversion: 3-5% is good, 10%+ is exceptional
- Time to convert: 30-90 days median
- Annual vs monthly: 40% choose annual if discount is 20%+
- Viral coefficient: 0.5 = sustainable, 1.0+ = exponential growth

**Common mistakes**:
- Optimizing pricing before product-market fit (premature)
- No urgency to upgrade (add: "Your free trial ends in 7 days")
- Upgrade flow has bugs (test the payment process yourself weekly)
- Not offering annual plans (annual = better cash flow + lower churn)
- Complicated pricing (keep it simple: Individual/Team/Enterprise)

---

## Usage Signal Detection for Enterprise Upsell

**Definition**: Monitoring free tier usage to identify companies ready for enterprise sales conversation.

**When to use**: Continuous background process. CSO reviews signals weekly.

**Step-by-step**:
1. Domain Clustering: Group users by email domain. 5+ users from @acme.com = enterprise signal.
2. Usage Intensity: Track audit volume. If free tier user is running 50+ audits/month, they're power users (likely to pay).
3. Feature Limit Hits: When user hits free tier constraint (e.g., "only 3 compliance packs in free tier"), trigger outreach email.
4. Job Title Enrichment: Use Clearbit/Apollo to append job titles. If user is "VP Engineering" or "Chief Compliance Officer," they have budget.
5. Outreach Automation: Auto-send: "Hi [Name], I see [X] people from [Company] are using Y*gov. Want to discuss an enterprise plan with centralized billing and compliance features?"

**Common mistakes**:
- Spamming every free user (only contact enterprise signals)
- Generic outreach (personalize: "I see you generated 47 CIEU audits last month")
- Reaching out too early (wait for real usage, not just signup)
- Not tracking response rates (if <5% reply, your targeting is wrong)

---

## Developer Marketing Channels

**When to use**: Continuous. Developers don't respond to traditional ads.

**Ranked by effectiveness for Y*gov**:

1. Hacker News Launch: "Show HN: Y*gov — governance for AI agent swarms." Top 10 = 5K+ visitors.
2. GitHub SEO: Detailed README with keywords: "AI agent governance", "Claude Code audit", "LLM compliance". GitHub ranks well on Google.
3. Technical Blog Posts: "How we built CIEU audit chains" on Y*gov blog. Cross-post to Dev.to, Medium, Hacker Noon.
4. Conference Talks: Apply to speak at PyCon, AI Engineer Summit. Topic: "Governing AI agent swarms in production."
5. Developer Podcasts: Reach out to Changelog, Software Engineering Daily. Topic: "Why AI agents need governance."
6. YouTube Tutorials: "How to audit your Claude Code agents in 5 minutes." SEO keyword targeting.
7. Reddit: r/ClaudeAI, r/programming, r/MachineLearning. No self-promotion — answer questions, mention Y*gov when relevant.

**Common mistakes**:
- Posting promotional content (developers hate ads — teach, don't sell)
- Not responding to comments (engagement matters more than post quality)
- Giving up after one post (consistency required — post weekly for 6 months)

---

## Quick Reference Checklist

For each free tier user, ask:
- [ ] Have they generated first audit report? (activation)
- [ ] Are they from a known company domain? (enterprise signal)
- [ ] Have they hit free tier limits? (conversion opportunity)
- [ ] Are there 3+ colleagues from same company? (expansion signal)
- [ ] Have they engaged in community? (potential champion)

If 3+ boxes checked, move to CSO outreach list.
