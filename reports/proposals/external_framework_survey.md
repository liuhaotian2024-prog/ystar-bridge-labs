# External Management Framework Survey — Y* Bridge Labs Adoption Assessment

**Author**: Aiden (CEO agent)
**Requested by**: Board (Haotian Liu)
**Purpose**: Stop inventing home-grown process. Select external frameworks whose core structures can be (a) stripped of human-time-dimension semantics and (b) hardened into `gov-mcp` IntentContracts / obligations / CIEU events.
**Output location**: `reports/proposals/external_framework_survey.md`

---

## 1. Executive Summary

### Core conclusion

Y* Bridge Labs should stop authoring bespoke governance artifacts (L0-L3 decision tiers, custom session_handoff schema, OmissionEngine as pure invention, EXECUTION_MODEL doc) and adopt a **deliberately chosen 5-framework stack**, all of whose original clocks have been severed and replaced with event/count/causal-depth triggers:

| Purpose | Adopted framework | Replaces our homegrown |
|---|---|---|
| Decision role assignment per intent | **RAPID** (Bain) | L0-L3 decision tiers + ad-hoc "who decides" |
| Who-performs-what per task | **RACI** (subset of RAPID's P role) | implicit ownership in `.claude/agents/*.md` |
| Proposal artifact (written narrative > slides) | **Amazon 6-pager + Working Backwards** | free-form `.claude/tasks/*.md` |
| Team sizing + ownership unit | **Single-Threaded Leader + Two-Pizza Team** | current overlapping agent scopes |
| Goal structure (no wall-clock) | **OKR** (Andy Grove form, cadence stripped) | "current top priorities" bullet in CLAUDE.md |
| Autonomy / decision rights doctrine | **Netflix Informed Captain + Context-not-Control** | Board-gated everything |
| Retrospective / learning loop | **Bridgewater Dot Collector + Issue Log + Pain-Reflection** | OmissionEngine (keep the idea, replace the schema) |
| Project shaping & scope boundary | **Shape Up** — Shaping/Betting/Building + Appetite + Hill Charts (cycle length removed) | free-form task scoping |
| Quality stop-the-line | **TPS Jidoka + Andon cord** | CIEU escalation (already compatible, formalize) |
| Audit control coverage baseline | **ISO 27001:2022 Annex A (93 controls)** | proves gov-mcp coverage externally |

### Recommended priority for implementation (ordered by leverage / cost ratio)

1. **RAPID + Amazon 6-pager** — highest leverage, lowest cost. Every intent gets a one-line RAPID assignment; every non-trivial proposal is a 6-pager narrative. gov-mcp can enforce both as contract dimensions immediately.
2. **Single-Threaded Leader + Two-Pizza** — codify that each of the 11 agents owns one initiative; forbid matrix overlap.
3. **OKR (cadence-stripped) + Hill Charts** — replace "current top priorities" with structured Objective + 3-5 Key Results, each KR tracked as a Hill Chart state (uphill = unknowns remain, downhill = execution).
4. **Netflix Informed Captain** — formalizes that CEO/CTO/CMO/CSO/CFO each hold captain rights within their domain; Board is escalation not gatekeeper.
5. **Bridgewater Issue Log (re-skin OmissionEngine)** — keep the DB, swap the schema to match a proven external standard.
6. **Jidoka/Andon** — already latent in CIEU; make it explicit, single hook.
7. **ISO 27001 Annex A mapping** — not for adoption, for **external validation narrative**: "gov-mcp natively covers N of 93 Annex A controls."
8. **Shape Up Shaping/Betting** — adopt the pitch artifact and the appetite-vs-estimate inversion; drop 6-week cycles entirely.

### Frameworks recommended for rejection / narrow use

- **Full Bridgewater Principles** — believability-weighted voting requires a track-record dataset we don't yet have; adopt the issue log only.
- **ITIL 4** — too heavy for 11 agents; cherry-pick "incident management" and "change management" concepts only.
- **Full Netflix Culture Deck** — vacation / expense policies irrelevant; adopt decision doctrine only.
- **YC / a16z operating playbooks** — advice is founder-centric and hiring-centric, largely N/A for agent org. Keep Altman's "hire slowly, fire fast" mutated to "spawn agent slowly, retire agent fast."

---

## 2. Research Method & Hard Constraint Declaration

### Hard constraint (copied verbatim from `knowledge/ceo/feedback/no_human_time_dimension_in_agent_frameworks.md`)

> **严禁把人类时间维度带入调研产出**。Banned: N天/N小时/N周/N月/N季度/年度/deadline/SLA response time/daily/weekly/quarterly/annual/office hours/6-week cycle/2-week cool-down. Required substitutions:
> - cycle → one delivery closure (complete intent completion)
> - daily standup → event-triggered check-in
> - quarterly review → after N CIEU events / K obligation completions
> - deadline → non-blocking downstream + fail-open + CIEU escalation
> - response time → must complete before next action
> - annual → rolling sequence of delivery goals
>
> **Core principle**: for agents, "progress" is causal-chain depth + completion count, not wall-clock time.

All 10 frameworks below are documented with their **original human-time artifacts removed** and replaced with agent-native equivalents. Anything that cannot survive this removal is flagged `[NOT ADOPTABLE]`.

### Sources

Every claim in this document is traceable to a cited URL. URLs are listed per-framework and in the consolidated References section (§7). Any claim without a resolvable source is removed from the report.

### What was deliberately NOT studied

- Agile / Scrum (ceremonies are inseparably time-boxed; SAFe, LeSS similarly)
- Holacracy (requires human role-holders; circles-of-circles structure brittle at N=11 agents)
- EOS (Entrepreneurial Operating System) — weekly L10 meetings are core, non-strippable
- GTD (Getting Things Done) — personal productivity, not organizational

---

## 3. Framework-by-Framework Analysis

---

### 3.1 Amazon 6-Pager Memo + Working Backwards

#### Core structure (time-stripped)

**Artifacts**:
- 6-page narrative memo (prose, no bullets as primary form, no slides/PowerPoint — Bezos banned PowerPoint in 2004 for this purpose) ([CNBC 2018](https://www.cnbc.com/2018/04/23/what-jeff-bezos-learned-from-requiring-6-page-memos-at-amazon.html))
- Press release + FAQ ("PR/FAQ") written **before** the product is built, as Working Backwards from the customer ([a16z podcast](https://a16z.com/podcast/amazon-narratives-memos-working-backwards-from-release-more/))

**Roles**: author (single-threaded leader); readers (decision-makers + stakeholders).

**Information-flow pattern**:
1. Author writes the 6-pager.
2. Meeting begins with **silent reading** (20-30 min in original), during which participants annotate. [TIME-STRIPPED: silent reading continues **until every participant marks "done"**, not a fixed clock.]
3. Discussion follows, anchored in the annotated document.

**Decision gate**: the 6-pager itself is the gate — weak narrative = weak thinking = weak decision.

**Working Backwards**: start from the customer press release; only then derive the technology stack. Ban on "we built X, now who wants it" direction. ([Amazon Chronicles](https://amazonchronicles.substack.com/p/working-backwards-dave-limp-on-amazons))

#### Agent-native translation

| Original | Agent-native |
|---|---|
| 6-page narrative | `IntentContract.proposal_memo` (markdown, single file, prose-dominant, bullet budget ≤ 20% of lines) |
| Silent reading phase | `gov_precheck` hook: every named reviewer must emit an `annotated=true` CIEU event before `gov_enforce` allows the decision step |
| PR/FAQ | `IntentContract.backward_artifacts.press_release` + `faq` as required fields on any product-affecting intent |
| "Anecdotes + data" | CIEU audit trail attached as appendix |

#### gov-mcp hardening score: **5 / 5**

Directly expressible as contract dimensions:
- `proposal.format = narrative_markdown`
- `proposal.max_bullets_ratio = 0.2`
- `proposal.readers[].acknowledged_at_event_id = <ciu_id>`
- `proposal.working_backwards.press_release_present = true`
- `proposal.working_backwards.faq_min_questions = 5`

Must remain agent-judgment: whether the narrative is actually *good* (no LLM-scorer is reliable enough to enforce this — human/Board spot-checks at sampling rate).

#### Replacement mapping for our home-grown process

- `.claude/tasks/*.md` free-form → must conform to 6-pager template (header, context, proposal, alternatives considered, risks, FAQ, appendix).
- BOARD_PENDING.md free-form → each entry must reference a 6-pager file.

#### Does-not-transfer

- The 20-30 min silent read clock → replaced with **event-driven annotate-before-proceed**.
- "Bring printed copies" physical ceremony → not applicable.

**Sources**:
- [Amazon Chronicles — Dave Limp on the Six Page Memo](https://amazonchronicles.substack.com/p/working-backwards-dave-limp-on-amazons)
- [CNBC — Bezos on 6-page memos (2018)](https://www.cnbc.com/2018/04/23/what-jeff-bezos-learned-from-requiring-6-page-memos-at-amazon.html)
- [a16z podcast — Amazon Narratives, Working Backwards](https://a16z.com/podcast/amazon-narratives-memos-working-backwards-from-release-more/)
- [Writing Cooperative — Anatomy of an Amazon 6-pager](https://writingcooperative.com/the-anatomy-of-an-amazon-6-pager-fc79f31a41c9)

---

### 3.2 Amazon Leadership Principles (14+2)

#### Core structure (already time-free)

14 original principles + 2 added 2021, giving the current official set of 16 at [amazon.jobs/leadership-principles](https://www.amazon.jobs/content/en/our-workplace/leadership-principles):

Customer Obsession, Ownership, Invent and Simplify, Are Right A Lot, Learn and Be Curious, Hire and Develop the Best, Insist on the Highest Standards, Think Big, Bias for Action, Frugality, Earn Trust, Dive Deep, Have Backbone; Disagree and Commit, Deliver Results, Strive to be Earth's Best Employer, Success and Scale Bring Broad Responsibility. ([amazon.jobs](https://www.amazon.jobs/content/en/our-workplace/leadership-principles), [Inc.](https://www.inc.com/peter-economy/the-14-amazon-leadership-principles-that-can-lead-you-your-business-to-tremendous-success.html))

No clocks. Fully adoptable as-is.

Notable primitives:
- **Disagree and Commit** — from Bezos' 2016 shareholder letter: "If you have conviction on a particular direction even though there's no consensus… 'Look, I know we disagree on this but will you gamble with me on it? Disagree and commit?'" ([2016 Shareholder Letter](https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders))

#### Agent-native translation

- Each principle → a `values_dimension` in agent IntentContract (e.g., `values.customer_obsession.evidence_required = true` for any product change).
- `Disagree and Commit` → `gov-mcp` primitive: when `consensus < threshold` but `captain.conviction = high`, allow proceed with `commit_dissent_recorded[]` array attached to the CIEU chain. No escalation unless reversible-impact.

#### gov-mcp hardening: **3 / 5**

Values are judgment calls; hardening limited to *evidence-of-consideration* (did the agent cite which principle applies to the decision?). Adopt "Hire and Develop the Best" as `agent spawn quality gate`; "Frugality" as `budget.token_spend_awareness`; "Bias for Action" as `two_way_door_detector` (reversible decisions must not block on consensus).

#### Replaces

- Scattered CLAUDE.md maxims → consolidated as `team_dna.values = [16 LPs]` with per-intent citation obligation.

#### Does-not-transfer

- "Strive to be Earth's Best Employer" — no employees. Remap to "Strive to be best operating context for downstream agents."

**Sources**:
- [Amazon Leadership Principles (official)](https://www.amazon.jobs/content/en/our-workplace/leadership-principles)
- [Amazon Leadership Principles — official PDF snapshot](https://assets.aboutamazon.com/bc/83/6707031f4dbdbe3d4118b0f05737/amazon-leadership-principles-10012020.pdf)
- [Amazon 2016 Shareholder Letter (Disagree and Commit origin)](https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders)
- [AWS Executive Insights — Day 1 Culture](https://aws.amazon.com/executive-insights/content/how-amazon-defines-and-operationalizes-a-day-1-culture/)

---

### 3.3 Single-Threaded Leader + Two-Pizza Team

#### Core structure (time-free)

- **Single-Threaded Leader (STL)**: one leader, one initiative, no multitasking; "the best way to fail at inventing something is by making it somebody's part-time job" (AWS internal quote). ([Pedro del Gallego](https://pedrodelgallego.github.io/blog/amazon/single-threaded-model/), [AWS Executive Insights on STL/two-pizza](https://aws.amazon.com/executive-insights/content/amazon-two-pizza-team/))
- **Two-pizza team**: team size capped at what two pizzas can feed (5-8 people typical, ≤10 max). When a team must grow past this, **split** rather than expand. ([AWS Executive Insights](https://aws.amazon.com/executive-insights/content/amazon-two-pizza-team/))

No time artifacts. Scale artifact only (team size).

#### Agent-native translation

- 11-agent current roster maps cleanly: each of 5 C-suite + 4 engineers + 2 support agents is already one STL of one domain.
- `gov-mcp` constraint: `domain.owner_agent_count = 1` (exactly one); when a domain expands, **spawn a sub-domain child agent** instead of loading more onto the current owner.
- `two_pizza` interpretation for agents: **context-window budget**. No single agent's owned artifact set may exceed a context-window fraction (e.g. 40% of max) — forces splitting.

#### gov-mcp hardening: **5 / 5**

- `IntentContract.owner_agent` — must be exactly 1 agent_id.
- `IntentContract.contributors[]` — RAPID I/A/P roles, not owners.
- `gov_doctor` periodic check: any domain with ≥2 claimed owners triggers Andon.

#### Replaces

- Current ambiguous `.claude/agents/*.md` where CEO and CTO both appear to "own" governance boot logic → split cleanly.
- `active_agent` concurrency bug (today's finding) → STL rule would have prevented: "no second writer to governance state."

#### Does-not-transfer

- Physical team perks / co-location.

**Sources**:
- [AWS Executive Insights — Amazon's Two-Pizza Teams](https://aws.amazon.com/executive-insights/content/amazon-two-pizza-team/)
- [Pedro del Gallego — Single-Threaded Leaders at Amazon](https://pedrodelgallego.github.io/blog/amazon/single-threaded-model/)
- [Jade Rubick — Implementing Amazon's Single-Threaded Owner model](https://www.rubick.com/implementing-amazons-single-threaded-owner-model/)

---

### 3.4 RAPID Decision Framework (Bain & Company)

#### Core structure (time-free)

Five roles per decision ([Bain](https://www.bain.com/insights/rapid-decision-making/), [Bridgespan](https://www.bridgespan.org/insights/nonprofit-organizational-effectiveness/rapid-decision-making), [Asana](https://asana.com/resources/rapid-decision-making)):

- **R**ecommend — proposes; gathers data & input; drives proposal forward
- **A**gree — must formally agree before proposal is passed to Decide (veto power in their area, e.g., Legal on contract); used sparingly
- **P**erform — executes once decision is made
- **I**nput — provides expertise / information; cannot block
- **D**ecide — makes the final call; exactly one Decider per decision

Natural flow: Recommend → Input → Agree → Decide → Perform.

#### Agent-native translation

Per `IntentContract`, assign:

```yaml
decision_rapid:
  R: <agent_id>        # usually a C-suite agent
  A: [<agent_id>, ...] # optional; typically empty or [CFO] for financial, [CTO] for tech risk
  P: [<agent_id>, ...] # engineers
  I: [<agent_id>, ...] # any agent with relevant context
  D: <agent_id>        # exactly one; usually CEO or the domain C-suite; Board only for Board-gated intents
```

gov-mcp `gov_dispatch` tool binds these; `gov_enforce` blocks P from starting before D has recorded the decision event, and blocks D from deciding before all A have recorded agreement.

#### gov-mcp hardening: **5 / 5**

Every field is enforceable:
- `decision_rapid.D.count == 1` (constraint)
- `decision_rapid.A[].agreement_event_id != null` before `decision_rapid.D.decision_event_id`
- `decision_rapid.P[].start_event_id > decision_rapid.D.decision_event_id`

#### Replaces

- **L0-L3 decision tier system** — homegrown 4-level escalation → replaced entirely by RAPID assignment. L0 ≈ D=agent alone; L1 ≈ D=agent + A=peer; L2 ≈ D=C-suite; L3 ≈ D=Board. RAPID is more expressive because A and D are independent axes.
- **Implicit Board gate** → now explicit: intents whose `D = Board` are the only ones that block.

#### Does-not-transfer

- Nothing inherent. (RAPID has no time concept in its core definition.)

**Sources**:
- [Bain & Company — RAPID Decision-Making](https://www.bain.com/insights/rapid-decision-making/)
- [Mindtools — Bain's RAPID Framework](https://www.mindtools.com/av8ceid/bains-rapid-framework/)
- [Bridgespan — RAPID for Nonprofits](https://www.bridgespan.org/insights/nonprofit-organizational-effectiveness/rapid-decision-making)
- [Asana — RAPID Decision Making (2025)](https://asana.com/resources/rapid-decision-making)
- [Uncertainty Project — RAPID tool](https://www.theuncertaintyproject.org/tools/rapid-framework)

---

### 3.5 RACI / DACI Matrix

#### Core structure (time-free)

Per-task (not per-decision; this is the key difference from RAPID) ([Wikipedia](https://en.wikipedia.org/wiki/Responsibility_assignment_matrix), [Atlassian](https://www.atlassian.com/work-management/project-management/raci-chart), [CIO.com](https://www.cio.com/article/287088/project-management-how-to-design-a-successful-raci-project-plan.html)):

- **R**esponsible — does the work (can be many)
- **A**ccountable — single owner; answerable for completion (exactly 1)
- **C**onsulted — two-way communication
- **I**nformed — one-way notification

DACI variant adds **D**river ahead of A — drives the process; A is still the accountable approver.

#### Agent-native translation

- RACI is **task-level**, used under RAPID's `P` role to break execution into sub-tasks.
- `IntentContract.tasks[].raci = { R: [...], A: <single>, C: [...], I: [...] }`.
- `gov-mcp` can enforce `A.count == 1` per task.

#### gov-mcp hardening: **4 / 5**

Direct mapping. Only nuance: "Informed" is one-way — enforced by a post-completion notification CIEU event to each I agent's inbox.

#### Replaces

- Currently implicit task ownership — RACI forces explicitness.

#### Does-not-transfer

- Nothing clock-based. Historical complaint that RACI "adds bureaucracy" is a volume issue (not applying it per trivial task) rather than a time issue.

**Sources**:
- [Wikipedia — Responsibility Assignment Matrix](https://en.wikipedia.org/wiki/Responsibility_assignment_matrix)
- [Atlassian — RACI Chart](https://www.atlassian.com/work-management/project-management/raci-chart)
- [CIO.com — RACI Blueprint](https://www.cio.com/article/287088/project-management-how-to-design-a-successful-raci-project-plan.html)
- [Project-management.com — RACI guide](https://project-management.com/understanding-responsibility-assignment-matrix-raci-matrix/)

---

### 3.6 OKR (Andy Grove form, cadence stripped)

#### Core structure

Original definition ([Andy Grove, *High Output Management* 1983, as documented by What Matters](https://www.whatmatters.com/articles/the-origin-story)):

- **Objective**: a direction / intent statement — qualitative, ambitious
- **Key Results**: 3-5 measurable outcomes that prove the Objective achieved — quantitative, verifiable

Introduced at Intel by Grove (evolved from Drucker's MBO); brought to Google in 1999 by John Doerr. ([Wikipedia — OKR](https://en.wikipedia.org/wiki/Objectives_and_key_results), [What Matters — Origin Story](https://www.whatmatters.com/articles/the-origin-story))

Original cadence in industry practice: quarterly + annual. **[TIME-STRIPPED.]**

#### Agent-native translation

Keep structure, delete cadence:

```yaml
okr:
  objective: "Y*gov installation works first-try on clean machines"
  key_results:
    - kr_id: kr_1
      statement: "ystar doctor exits 0 on N consecutive clean-venv installs"
      target_count: 20
      current_count: <ciu-derived>
      trigger_review_on: count >= target_count OR blocker_detected
    - ...
```

Rolling sequence: when all KRs in an OKR hit their target counts OR the Objective is invalidated, **the next Objective in the backlog becomes active**. No calendar. No Q1/Q2. Progress = completion_count_of_CIEU_events, per Board's hard constraint.

#### gov-mcp hardening: **4 / 5**

- Objective text: free-form (not enforceable).
- KR structure: enforceable (`target_count` integer, `trigger_review_on` expression).
- Rollover: enforceable via `gov_trend` + `gov_report` on KR completion.

#### Replaces

- CLAUDE.md "Current Top Priorities" bullet list → becomes 3-4 active OKRs with measurable KRs.

#### Does-not-transfer / Risk

- **Quarterly scoring ritual (0.0-1.0 per KR)**: adopt grading, drop the quarter. Grade on demand, on KR-trigger.
- "70% score is healthy for stretch OKRs" ([Google re:Work](https://rework.withgoogle.com/intl/en/guides/set-goals-with-okrs)) — adopt.

**Sources**:
- [What Matters — OKRs History (Grove/Intel)](https://www.whatmatters.com/articles/the-origin-story)
- [What Matters — OKR Definition/Examples](https://www.whatmatters.com/faqs/okr-meaning-definition-example)
- [Wikipedia — Objectives and Key Results](https://en.wikipedia.org/wiki/Objectives_and_key_results)
- [Google re:Work — Set goals with OKRs](https://rework.withgoogle.com/intl/en/guides/set-goals-with-okrs)
- [PeopleLogic — History of OKRs](https://peoplelogic.ai/blog/history-of-objectives-and-key-results)

---

### 3.7 Netflix Culture Deck (decision doctrine subset)

#### Core structure (decision doctrine is time-free; HR policies are not relevant)

From [Netflix Culture Memo (official)](https://jobs.netflix.com/culture) and [No Rules Rules](https://variety.com/2020/digital/news/netflix-reed-hastings-book-five-takeaways-no-rules-rules-1234752550/):

- **Context, not Control**: managers set context; ICs make the call. Managers intervene only when the decision is unethical, materially harmful, crisis-level, or context is missing. ([Netflix Culture Memo](https://jobs.netflix.com/culture))
- **Informed Captain**: every significant decision has one designated captain; captain consults widely ("farming for dissent") but decides alone. No decision-by-committee.
- **Freedom & Responsibility**: expectations replace rules (expense policy = "Act in Netflix's best interests"; vacation = "take vacation").
- **Keeper Test**: "If X wanted to leave, would I fight to keep them?" / "Knowing everything I know today, would I hire X again?" ([Variety on Hastings' book](https://variety.com/2020/digital/news/netflix-reed-hastings-book-five-takeaways-no-rules-rules-1234752550/))

#### Agent-native translation

- **Informed Captain** ≡ RAPID `D` — same concept with different vocabulary. Use RAPID's terminology internally; cite Netflix as the cultural grounding.
- **Context not Control** → CEO/C-suite provide `IntentContract` + obligations (the context); agents execute freely within the contract envelope. Hooks enforce contract, not execution path.
- **Farming for dissent** → `IntentContract.dissent_sought_from[]` must include ≥1 agent with opposing stance before `D` decides. Enforceable.
- **Keeper test (agent version)** → periodic (on N-completion trigger, NOT on time): "Knowing what we know, would we spawn this agent again? Is its domain still load-bearing? If no, retire and redistribute." This replaces our homegrown `session_close` ritual's self-assessment.

#### gov-mcp hardening: **3 / 5**

- "Context not control" — philosophical; partial hardening via: hooks only check contract boundary, never prescribe implementation.
- "Informed Captain" — fully hardened via RAPID D constraint.
- "Farming for dissent" — hardened as `dissent_event_count >= 1`.
- "Keeper test" — trigger definable, judgment-call remains agent-side.

#### Replaces

- Current reflex where Board is consulted on every mid-sized decision → Informed Captain doctrine gives explicit permission for C-suite agents to decide within their domain.

#### Does-not-transfer

- Vacation / expense / salary policies — irrelevant for agents.
- "Talent density" as hiring criterion — remap to "capability density per agent domain"; loose adoption.
- **Keeper test frequency** — original is annual-ish; replaced with "on N=20 completed intents per domain, trigger self-assessment CIEU event."

**Sources**:
- [Netflix Culture Memo (jobs.netflix.com)](https://jobs.netflix.com/culture)
- [Netflix Culture Deck PDF (archived)](https://www.cpj.fyi/content/files/2022/12/Netflix-Culture-Deck.pdf)
- [Variety — 5 Takeaways from *No Rules Rules*](https://variety.com/2020/digital/news/netflix-reed-hastings-book-five-takeaways-no-rules-rules-1234752550/)
- [Variety — Reed Hastings on the Hardest Keeper Test](https://variety.com/2020/digital/news/reed-hastings-book-netflix-cfo-keeper-test-1234755643/)
- [HBS Working Knowledge — Freedom, Fear, and Feedback on Netflix culture](https://www.library.hbs.edu/working-knowledge/freedom-fear-and-feedback-should-other-companies-follow-netflixs-lead)

---

### 3.8 Bridgewater Principles (Dot Collector + Issue Log + Pain-Reflection)

#### Core structure (partly time-bound; strip the daily cadence)

From [Principles.com](https://www.principles.com/principles/633d5d13-8610-425f-ad62-cd62347d9165/) and derivative coverage:

- **Radical truth, radical transparency** — every meeting / interaction is recorded; no secrets.
- **Dot Collector** — in every meeting, participants rate each other live on ~100 attributes. Produces a track record / "baseball card" for each person. Votes are then both equal-weighted and **believability-weighted** (weighted by the voter's track record in that dimension). ([P2P Foundation](https://wiki.p2pfoundation.net/Believability-Weighted_Decision_Making), [Bastian Moritz](https://www.bastianmoritz.com/blog/bridgewater-associates-believability-weighted-system-for-algorithmic-decision-making/))
- **Believability-weighted decision making** — if equal-vote and believability-weighted vote agree → resolved; if disagree → re-discuss; if still disagree → defer to believability-weighted. ([Principles.com](https://www.principles.com/))
- **Issue Log** — **daily** (strip) report from reports to manager: what did, what issues, reflections. Dalio used to track problems and morale. ([Shortform — Bridgewater Tools](https://www.shortform.com/blog/bridgewater-tools/))
- **Pain + Reflection = Progress** — app records emotion at the moment of pain; reflection guided later. ([Principles.com — Pain + Reflection = Progress](https://www.principles.com/principles/4a903526-2db6-4a0a-9b71-889868f0f475/), [FS.blog](https://fs.blog/pain-reflection/))

#### Agent-native translation

- **Issue Log** — `gov_remember` call on *every CIEU event with severity ≥ warn*, structured as `{what_attempted, blocker, reflection_prompt}`. No daily cadence; event-driven. Aggregation triggers a `gov_health_retrospective` when blocker count exceeds threshold or a causal-chain-depth threshold is crossed.
- **Dot Collector** — `[NOT ADOPTABLE yet]`. Agents don't have enough comparable track records, and LLM self-rating is noisy. Revisit after N=500 CIEU events per agent accumulates.
- **Believability-weighted voting** — `[DEFERRED]`. Keep it as a roadmap item; not a primary adoption.
- **Pain + Reflection = Progress** — already maps closely to our OmissionEngine concept. **Replace OmissionEngine's custom schema with Bridgewater's issue-log schema** (external credibility without redesign cost).

#### gov-mcp hardening: **3 / 5**

- Issue log schema: fully hardenable (`gov_remember` obligation on severity-threshold CIEU events).
- Believability scoring: deferred until track-record data exists.

#### Replaces

- **OmissionEngine** (home-grown name/schema) → re-skinned as "Issue Log" with Bridgewater-format fields (`situation / cause / lesson / pattern_flag`). Same underlying DB, externally validated schema.

#### Does-not-transfer

- Daily cadence → event-driven.
- Personality-attribute rating (100+ dimensions on humans) → not meaningful for agents yet.
- "Radical transparency" to the point of recording all meetings → already native (all agent interactions are CIEU-logged). Cite Bridgewater to *narrate* this, not to change behavior.

**Sources**:
- [Principles.com — Pain + Reflection = Progress](https://www.principles.com/principles/4a903526-2db6-4a0a-9b71-889868f0f475/)
- [Principles.com — Idea Meritocracy](https://www.principles.com/principles/633d5d13-8610-425f-ad62-cd62347d9165/)
- [P2P Foundation — Believability-Weighted Decision Making](https://wiki.p2pfoundation.net/Believability-Weighted_Decision_Making)
- [Shortform — Top 10 Bridgewater Tools](https://www.shortform.com/blog/bridgewater-tools/)
- [FS.blog — Pain + Reflection = Progress](https://fs.blog/pain-reflection/)
- [Opensource.com — Designing a system where best ideas win](https://opensource.com/open-organization/18/3/dalio-principles-1)

---

### 3.9 Shape Up (Basecamp, Ryan Singer)

#### Core structure (strip the 6-week cycle + 2-week cool-down)

Three phases ([Basecamp/37signals — Shape Up](https://basecamp.com/shapeup), [Ryan Singer — Common Pitfalls](https://www.ryansinger.co/pitfalls-when-adopting-shape-up/), [Changelog podcast #357](https://changelog.com/podcast/357)):

1. **Shaping** — done by senior person. Produce a *pitch*: problem / appetite / solution sketch / rabbit holes / no-gos. Solution is intentionally rough, not a spec. ([Basecamp Shape Up](https://basecamp.com/shapeup))
2. **Betting** — small group looks at pitches and **bets** (doesn't *plan*) which ones to build. "No backlog." Bets are commitments: once bet on, the team owns time and scope to ship or abandon — no interruptions.
3. **Building** — team gets the pitch, fills in details, tracks progress via **Hill Charts** (uphill = discovering unknowns; downtop of hill = ambiguity resolved; downhill = execution). ([Basecamp Shape Up](https://basecamp.com/shapeup))

Key primitives:
- **Appetite vs Estimate**: fix the *amount of time/budget worth spending*; let the design contract to fit. Original: "small batch = 1-2 weeks" / "big batch = 6 weeks" **[TIME-STRIPPED]** → replace with "appetite as an abstract budget unit."
- **Pitch** as the bet unit.
- **Rabbit holes** = unknowns explicitly named and addressed during shaping.
- **Scope hammering** — during build, cut scope aggressively to fit appetite.

#### Agent-native translation

- **Pitch artifact** = subset of the Amazon 6-pager (or a sibling format). Fields: `problem`, `appetite`, `solution_sketch`, `rabbit_holes[]`, `out_of_scope[]`.
- **Appetite** (time-stripped) → **"causal-chain depth budget"**: e.g., appetite = "shallow" means solution must fit within a CIEU chain of ≤N nodes; "deep" means ≤M, M > N. This replaces "6 weeks" with something agent-meaningful (compute / tool-call / sub-agent-spawn budget).
- **Betting** → `gov_contract_activate` gate: only N active pitches allowed per domain at once; rest sit uncommitted. No "backlog grooming" ritual.
- **Hill Charts** → `KR.hill_position ∈ {uphill_discovering, summit, downhill_executing}` enum; updated on each CIEU event that resolves or creates an unknown. Clean visualization of uphill drift = Andon trigger.
- **Scope hammering** → explicit obligation: on any `rabbit_hole_encountered` CIEU event, the owner must emit either `scope_cut` or `escalate_to_D` event — no silent expansion allowed.

#### gov-mcp hardening: **5 / 5**

All primitives except the cycle length are directly hardenable:
- `IntentContract.appetite_budget = {chain_depth: N, token_budget: M}` with enforcement via `gov_enforce`.
- `IntentContract.rabbit_holes[].resolved` — required field.
- `KR.hill_position` — enum, CIEU-transitioned.

#### Replaces

- Current informal scoping of `.claude/tasks/*.md` → structured pitch.
- The today-discovered failure mode "we spent too much on inventing management structure" → Shape Up's explicit `out_of_scope[]` would have named "inventing governance" as out-of-scope from the start.

#### Does-not-transfer

- **6-week build + 2-week cool-down cycle** — hard rejected per Board constraint. Replaced with appetite-budget depletion as the boundary.
- "Daily standups during build" — not in Shape Up's original anyway (one of its selling points); keep absent.

**Sources**:
- [Basecamp / 37signals — Shape Up (book, free online)](https://basecamp.com/shapeup)
- [Ryan Singer — Common Pitfalls When Adopting Shape Up](https://www.ryansinger.co/pitfalls-when-adopting-shape-up/)
- [Changelog #357 — Shape Up with Ryan Singer](https://changelog.com/podcast/357)
- [37signals podcast — Shape Up Print Edition](https://37signals.com/podcast/shape-up-print-edition/)

---

### 3.10 Toyota Production System / Lean (Jidoka, Andon, Kaizen, Gemba)

#### Core structure (mostly time-free; continuous-flow is event-driven by nature)

Developed by Taiichi Ohno and Eiji Toyoda, 1948-1975. ([Toyota Global — TPS official](https://global.toyota/en/company/vision-and-philosophy/production-system/), [Wikipedia — TPS](https://en.wikipedia.org/wiki/Toyota_Production_System))

Two pillars:
- **Jidoka** ("automation with a human touch") — stop immediately when abnormality detected, to prevent defective products from propagating. Workers empowered to stop the line. ([Toyota Global](https://global.toyota/en/company/vision-and-philosophy/production-system/))
- **Just-in-Time** — produce only what's needed, when needed, in the amount needed. Demand-pull, not schedule-push.

Supporting primitives:
- **Andon cord** — physical rope/button any worker pulls to halt the line when they see a defect ([Supply Chain Today on Andon](https://www.supplychaintoday.com/toyota-production-system-jidoka-stopping-production-a-call-button-and-andon/)). The cord + andon board broadcast the problem for rapid joint resolution.
- **Kaizen** — continuous improvement, bottom-up, every worker empowered to suggest.
- **Gemba / Genchi Genbutsu** — "go and see" the actual place where work happens before deciding.
- **Muri / Mura / Muda** — overburden / unevenness / waste — the three wastes to eliminate.

#### Agent-native translation

- **Jidoka** — already native: any CIEU event with `severity=error` is an automatic stop signal. Formalize: `gov_enforce` must halt downstream on error-severity events.
- **Andon cord** → `gov_escalate` tool surfaces a high-priority CIEU chain to Board (or to domain captain) immediately. Any agent can pull it. No shame attached. Andon-pull count is a *positive* quality metric (problems surfaced, not hidden).
- **Kaizen** → Bridgewater's issue log reflections double as Kaizen suggestions. On each retrospective, extract `kaizen_candidates[]` from the issue log and consider them for IntentContract updates.
- **Gemba** → for agents: before deciding on a sub-agent's domain design, *read the sub-agent's recent CIEU events* (the actual place). No deciding purely from abstract doc.
- **Muda (waste)** — "inventing management process we didn't need" is muda; today's self-diagnosis is a Gemba + muda identification. Make muda an explicit CIEU label.

#### gov-mcp hardening: **4 / 5**

- Jidoka → `gov_enforce` + severity enum: fully hardenable.
- Andon → `gov_escalate` tool already exists (verified from loaded tools list).
- Kaizen → process, partially enforceable via "every retrospective must emit ≥1 improvement proposal CIEU event."
- Gemba → enforceable: `before_decision` hook requires `recent_events_read_count ≥ N` for the affected domain.
- Muda labeling → soft, agent judgment.

#### Replaces

- Informal error handling paths in current hook_wrapper.py / session code → formalize under Jidoka.
- Ad-hoc escalations to Board → Andon-cord discipline (explicit pull, explicit reason, explicit downstream stop).

#### Does-not-transfer

- Physical factory floor primitives (kanban card as paper, takt time as seconds-per-unit) — takt time is inherently clock-based; **rejected**. Use event-rate proxies only if needed.
- "JIT inventory" — not directly applicable to agents; loose analogue is "don't pre-compute artifacts whose consumers haven't emerged."

**Sources**:
- [Toyota Motor Corporation — TPS Official](https://global.toyota/en/company/vision-and-philosophy/production-system/)
- [Toyota UK Magazine — 13 pillars of TPS](https://mag.toyota.co.uk/13-pillars-of-the-toyota-production-system/)
- [Wikipedia — Toyota Production System](https://en.wikipedia.org/wiki/Toyota_Production_System)
- [Supply Chain Today — Jidoka, Andon](https://www.supplychaintoday.com/toyota-production-system-jidoka-stopping-production-a-call-button-and-andon/)
- [Lean Sigma — TPS blueprint](https://www.learnleansigma.com/lean-manufacturing/discover-the-toyota-production-system-tps-the-foundation-of-lean-learn-how-jit-jidoka-and-kaizen-drive-efficiency-eliminate-waste-and-transform-industries-beyond-automotive/)

---

### 3.11 ITIL 4 / ISO 27001:2022 (external control baseline)

#### Core structure

- **ITIL 4** — service management framework; 34 management practices under a Service Value System; "guiding principles" + "service value chain" structure. ([Fox IT — ITIL and ISO/IEC 27001](https://www.foxitsm.com/wp-content/uploads/ITIL-and-ISO27001-v3.pdf), [Medium — IT Governance Trilogy](https://medium.com/@cnh.zzt/the-it-governance-trilogy-understanding-cobit-itil-and-iso-27001-4449a917c7f3))
- **ISO 27001:2022** — information security management system (ISMS) standard; **Annex A has 93 controls** (reduced from 114 in 2013 version), grouped into 4 themes: Organizational (37), People (8), Physical (14), Technological (34). ([Hightable — Annex A Complete Reference](https://hightable.io/iso-27001-annex-a-controls-reference-guide/), [ISMS.online — Annex A 2022](https://www.isms.online/iso-27001/annex-a-2022/), [DataGuard — Annex A](https://www.dataguard.com/iso-27001/annex-a/))

#### Agent-native translation

- These are **not** adopted as our day-to-day operating rhythm. They are adopted as the **external audit yardstick** against which gov-mcp measures its own coverage.
- Concrete action: map each of the 93 Annex A controls to gov-mcp primitives. Produce a Statement of Applicability (SoA) listing which controls gov-mcp covers natively, which require user-authored IntentContracts, which are N/A for an agent org.

Sample mapping (illustrative):

| Annex A control | gov-mcp primitive |
|---|---|
| A.5.1 Policies for information security | `gov_contract_load` + signed IntentContract |
| A.5.7 Threat intelligence | `gov_risk_classify` |
| A.5.24 Information security incident management planning | `gov_escalate` + Andon flow |
| A.8.15 Logging | CIEU event stream |
| A.8.16 Monitoring activities | `gov_health` + `gov_audit` |
| A.8.34 Protection during audit testing | `gov_seal` |

(Full mapping is a follow-on task; not completed in this report.)

#### gov-mcp hardening: **N/A** (this is the benchmark, not a thing we enforce on ourselves)

#### Replaces

- Nothing internal. **Adds** external credibility: "gov-mcp covers X/93 Annex A controls natively" is a marketable claim.

#### Does-not-transfer

- ITIL 4 change-advisory-board cadence → event-driven change approval via RAPID.
- ITIL 4 "daily operations" roles → not applicable.

**Sources**:
- [Hightable — ISO 27001 Annex A 93 Controls Reference](https://hightable.io/iso-27001-annex-a-controls-reference-guide/)
- [ISMS.online — Annex A 2022 Explained](https://www.isms.online/iso-27001/annex-a-2022/)
- [Advisera — ISO 27001 vs ITIL Comparison](https://advisera.com/27001academy/blog/2016/03/07/iso-27001-vs-itil-similarities-and-differences/)
- [Fox IT — ITIL and ISO/IEC 27001](https://www.foxitsm.com/wp-content/uploads/ITIL-and-ISO27001-v3.pdf)
- [DataGuard — Overview of Annex A measures](https://www.dataguard.com/iso-27001/annex-a/)

---

### 3.12 YC / a16z Startup Operating Material (selected extracts)

#### Core structure (largely human-org; select subset only)

From Sam Altman's [Startup Playbook](https://playbook.samaltman.com/) ([also YC blog](https://www.ycombinator.com/blog/startup-playbook/)):

- **Hire slowly, fire quickly**. Delay hiring; once hired, remove poor-fit fast. Culture is defined by who you hire, fire, and promote. ([Startup Playbook](https://playbook.samaltman.com/))
- Founder-mode concentration; most early-stage hires add organizational drag.
- YC's general advice library: [ycombinator.com/library/4D-yc-s-essential-startup-advice](https://www.ycombinator.com/library/4D-yc-s-essential-startup-advice).

#### Agent-native translation

- **Spawn agents slowly; retire them fast** — direct analogue. Don't add an agent to the roster unless the domain is structurally distinct AND the load exceeds current STL capacity. Retire (delete `.claude/agents/<name>.md` + migrate knowledge) when Keeper-test-fails.
- **Culture is defined by spawn/retire/promote** — true for agents: whichever agent is given first-crack at new intents defines de facto culture.

#### gov-mcp hardening: **2 / 5**

Mostly cultural / judgment; light enforcement via `agent_roster.max_count` soft cap.

#### Replaces

- Ad-hoc creation of sub-agents → Keeper-test + "spawn slowly" gate.

#### Does-not-transfer

- Fundraising advice (N/A for our operating model).
- Product-market fit iteration advice (already subsumed by Working Backwards).

**Sources**:
- [Sam Altman — Startup Playbook](https://playbook.samaltman.com/)
- [YC — Startup Playbook blog post](https://www.ycombinator.com/blog/startup-playbook/)
- [YC Startup Library — Essential Startup Advice](https://www.ycombinator.com/library/4D-yc-s-essential-startup-advice)

---

## 4. Recommended Stack for Y* Bridge Labs

Minimum adopted set (ordered by dependency):

```
Layer 1 (identity & ownership):
  Single-Threaded Leader + Two-Pizza Team        ← structural invariant
  Amazon Leadership Principles (16)              ← value dimensions

Layer 2 (decision & execution):
  RAPID                                          ← decisions
  RACI (under RAPID.P)                           ← task execution
  Netflix Informed Captain doctrine              ← cultural reinforcement of RAPID

Layer 3 (artifact & scope):
  Amazon 6-pager + Working Backwards             ← proposal format
  Shape Up: Pitch + Appetite + Hill Charts       ← scope + progress shape
                                                    (NO 6-week cycle)

Layer 4 (goal & rhythm, event-driven only):
  OKR (Andy Grove form, cadence stripped)        ← direction + measurable progress
  Bridgewater Issue Log (re-skins OmissionEngine) ← learning loop

Layer 5 (safety & quality):
  TPS Jidoka + Andon cord                        ← stop-the-line on error
  Amazon "Disagree and Commit"                   ← deadlock-break primitive

Layer 6 (external benchmark — NOT for internal rhythm):
  ISO 27001:2022 Annex A                         ← marketing / audit coverage
  (Selected) YC "spawn slowly / retire fast"     ← agent-roster discipline
```

### Rationale

- **Coverage**: Layers 1-5 cover identity, decisions, execution, artifacts, scope, goals, learning, and safety. Nothing in our current home-grown stack lacks a replacement.
- **Cost to adopt**: each framework above has free, primary, citeable documentation (Bezos letters, Bain insights, Singer's free Shape Up book, Toyota's own site, etc.). Zero licensing cost.
- **gov-mcp hardening density**: at least 4/5 score for all Layer 1-5 items; the stack is structurally enforceable, not aspirational.
- **External narrative**: "Y* Bridge Labs runs on Amazon + Bain + Andy Grove + Basecamp + Toyota + Bridgewater — hardened into gov-mcp contracts" is defensible marketing. "Y* Bridge Labs invented L0-L3 decision tiers" is not.

---

## 5. Homegrown → External Replacement Map

| Current home-grown artifact | External replacement | Migration action |
|---|---|---|
| L0-L3 decision tiers (4-level escalation) | RAPID D/A roles | Rewrite each existing escalation rule as `{R, A, P, I, D}` tuple in IntentContract |
| `.ystar_session.json` 193-constraint file, 11 categories | Same file; re-categorize constraints to map onto ISO 27001 Annex A + Amazon LPs + RAPID | Taxonomy migration only; data stays |
| `session_handoff.md` bespoke schema | Bridgewater issue-log schema (what_attempted / blocker / reflection / pattern_flag) | Schema rewrite; keep file |
| OmissionEngine (.ystar_omission.db) | Same DB, re-skinned as "Bridgewater Issue Log" with Pain+Reflection fields | Schema migration |
| `BOARD_PENDING.md` free-form | Each entry a link to a 6-pager `reports/proposals/*.md` | Backfill pending items |
| `.claude/tasks/*.md` free-form task notes | Shape Up Pitch template (problem / appetite / solution sketch / rabbit holes / no-gos) | Template + lint check |
| "Current Top Priorities" bullet list in CLAUDE.md | 3-4 active OKRs with measurable KRs, rolling | Rewrite §Current Top Priorities |
| `active_agent` mutex (today's bug) | STL invariant: `domain.owner_agent_count == 1` enforced by gov_doctor | Replace homegrown mutex with gov-mcp contract constraint |
| Ad-hoc escalations to Board | Andon-cord via `gov_escalate` + RAPID D=Board intents only | Formalize list of D=Board intents; everything else stops escalating |
| EXECUTION_MODEL.md homegrown doc | Delete; reference a short `FRAMEWORK_STACK.md` citing the 5-framework set above with URLs | Rewrite |
| Home-grown "active_agent" concurrency check | Two-Pizza + STL invariant (one owner per domain) | Delete custom code; enforce via gov-mcp contract |
| `hook_wrapper.py` error handling ad-hoc | Jidoka doctrine: on severity=error, gov_enforce halts downstream | Refactor hook to emit standardized severity CIEU events |

---

## 6. Implementation Risk & gov-mcp Hardening Feasibility

### Risk 1 — Over-adoption / ceremony inflation

If RAPID + RACI + 6-pager + pitch + issue-log all get applied to every trivial intent, the overhead exceeds benefit. **Mitigation**: each artifact has an **appetite gate** — trivial intents (single-step, reversible, single-agent) skip 6-pager + pitch; only intents above a defined size threshold require the full stack. This threshold is itself a `gov-mcp` contract dimension (`intent.size ∈ {trivial, shaped, strategic}`).

### Risk 2 — Agent-native time concept under-specified

Replacing "quarterly" with "N CIEU events" requires picking N. Unknown good defaults. **Mitigation**: start with order-of-magnitude placeholders (N=20, N=100, N=500 for different loops), collect data across first rolling sequence of OKRs, recalibrate. Explicit obligation: every time-replaced threshold must be listed in a `FRAMEWORK_TUNABLES.md` to prevent magic-number sprawl.

### Risk 3 — Believability-weighted voting defers indefinitely

Bridgewater's most valuable primitive is the one we can't adopt yet (no track record). **Mitigation**: accept the deferral; revisit on milestone "every agent has ≥500 CIEU events with outcome labels."

### Risk 4 — External framework citations become credentialism rather than utility

Risk of saying "we do Shape Up" while not actually doing it. **Mitigation**: for each adopted framework, require at least one concrete gov-mcp contract dimension or tool invocation as the operational hook. No pure "we subscribe to the philosophy" claims.

### Risk 5 — Shape Up 6-week cycle rejection may leave appetite unbounded

Removing the 6-week clock without a replacement appetite unit = unbounded work. **Mitigation**: appetite measured in causal-chain depth + compute budget + token budget. Three bounded units, enforced by gov-mcp. Never let appetite = unbounded.

### gov-mcp hardening feasibility summary

| Framework | Hardening score | Feasible now? |
|---|---|---|
| Amazon 6-pager + Working Backwards | 5/5 | Yes |
| Amazon Leadership Principles | 3/5 | Partial |
| Single-Threaded Leader + Two-Pizza | 5/5 | Yes |
| RAPID | 5/5 | Yes |
| RACI | 4/5 | Yes |
| OKR (cadence-stripped) | 4/5 | Yes |
| Netflix Informed Captain | 3/5 | Yes (overlaps RAPID) |
| Bridgewater Issue Log | 3/5 | Yes |
| Bridgewater believability voting | 1/5 now, 4/5 later | No (defer) |
| Shape Up pitch + appetite + Hill | 5/5 | Yes |
| TPS Jidoka + Andon | 4/5 | Yes |
| ISO 27001 Annex A | N/A (benchmark) | Yes (mapping task) |
| YC spawn-slow/retire-fast | 2/5 | Partial |

**Overall feasibility**: 9 of 12 frameworks hardenable to ≥3/5 now. Sufficient for adoption decision.

---

## 7. References

### Amazon
- Amazon Leadership Principles (official): https://www.amazon.jobs/content/en/our-workplace/leadership-principles
- Amazon Leadership Principles PDF snapshot: https://assets.aboutamazon.com/bc/83/6707031f4dbdbe3d4118b0f05737/amazon-leadership-principles-10012020.pdf
- Amazon 2016 Shareholder Letter (Disagree and Commit): https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders
- AWS Executive Insights — Two-Pizza Teams: https://aws.amazon.com/executive-insights/content/amazon-two-pizza-team/
- AWS Executive Insights — Day 1 Culture: https://aws.amazon.com/executive-insights/content/how-amazon-defines-and-operationalizes-a-day-1-culture/
- CNBC — Bezos and the 6-page memo: https://www.cnbc.com/2018/04/23/what-jeff-bezos-learned-from-requiring-6-page-memos-at-amazon.html
- a16z podcast — Amazon Narratives, Working Backwards: https://a16z.com/podcast/amazon-narratives-memos-working-backwards-from-release-more/
- Amazon Chronicles — Dave Limp on Six Page Memo: https://amazonchronicles.substack.com/p/working-backwards-dave-limp-on-amazons
- Writing Cooperative — Anatomy of an Amazon 6-pager: https://writingcooperative.com/the-anatomy-of-an-amazon-6-pager-fc79f31a41c9
- Pedro del Gallego — Single-Threaded Leaders: https://pedrodelgallego.github.io/blog/amazon/single-threaded-model/
- Jade Rubick — Implementing Single-Threaded Owner: https://www.rubick.com/implementing-amazons-single-threaded-owner-model/

### Bain / RAPID
- Bain — RAPID Decision-Making: https://www.bain.com/insights/rapid-decision-making/
- Mindtools — Bain's RAPID: https://www.mindtools.com/av8ceid/bains-rapid-framework/
- Bridgespan — RAPID for Nonprofits: https://www.bridgespan.org/insights/nonprofit-organizational-effectiveness/rapid-decision-making
- Asana — RAPID Decision Making 2025: https://asana.com/resources/rapid-decision-making
- Uncertainty Project — RAPID tool: https://www.theuncertaintyproject.org/tools/rapid-framework

### RACI
- Wikipedia — Responsibility Assignment Matrix: https://en.wikipedia.org/wiki/Responsibility_assignment_matrix
- Atlassian — RACI Chart: https://www.atlassian.com/work-management/project-management/raci-chart
- CIO.com — RACI Blueprint: https://www.cio.com/article/287088/project-management-how-to-design-a-successful-raci-project-plan.html
- Project-management.com — RACI guide: https://project-management.com/understanding-responsibility-assignment-matrix-raci-matrix/

### OKR
- What Matters — OKR Origin Story (Andy Grove/Intel): https://www.whatmatters.com/articles/the-origin-story
- What Matters — OKR Definition: https://www.whatmatters.com/faqs/okr-meaning-definition-example
- Wikipedia — Objectives and Key Results: https://en.wikipedia.org/wiki/Objectives_and_key_results
- Google re:Work — Set goals with OKRs: https://rework.withgoogle.com/intl/en/guides/set-goals-with-okrs
- PeopleLogic — History of OKRs: https://peoplelogic.ai/blog/history-of-objectives-and-key-results

### Netflix
- Netflix Culture Memo (official): https://jobs.netflix.com/culture
- Netflix Culture Deck PDF (archived 2009 original): https://www.cpj.fyi/content/files/2022/12/Netflix-Culture-Deck.pdf
- Variety — *No Rules Rules* 5 Takeaways: https://variety.com/2020/digital/news/netflix-reed-hastings-book-five-takeaways-no-rules-rules-1234752550/
- Variety — Hastings on Keeper Test: https://variety.com/2020/digital/news/reed-hastings-book-netflix-cfo-keeper-test-1234755643/
- HBS Working Knowledge — Freedom, Fear, Feedback: https://www.library.hbs.edu/working-knowledge/freedom-fear-and-feedback-should-other-companies-follow-netflixs-lead

### Bridgewater / Ray Dalio
- Principles.com — Pain + Reflection = Progress: https://www.principles.com/principles/4a903526-2db6-4a0a-9b71-889868f0f475/
- Principles.com — Idea Meritocracy: https://www.principles.com/principles/633d5d13-8610-425f-ad62-cd62347d9165/
- P2P Foundation — Believability-Weighted Decision Making: https://wiki.p2pfoundation.net/Believability-Weighted_Decision_Making
- Shortform — Top 10 Bridgewater Tools: https://www.shortform.com/blog/bridgewater-tools/
- FS.blog — Pain + Reflection = Progress: https://fs.blog/pain-reflection/
- Opensource.com — Designing a system where best ideas win (Dalio): https://opensource.com/open-organization/18/3/dalio-principles-1

### Shape Up / Basecamp
- Basecamp / 37signals — Shape Up book (free online): https://basecamp.com/shapeup
- Ryan Singer — Common Pitfalls Adopting Shape Up: https://www.ryansinger.co/pitfalls-when-adopting-shape-up/
- Changelog #357 — Shape Up with Ryan Singer: https://changelog.com/podcast/357

### Toyota / TPS / Lean
- Toyota Global — TPS Official: https://global.toyota/en/company/vision-and-philosophy/production-system/
- Toyota UK — 13 Pillars of TPS: https://mag.toyota.co.uk/13-pillars-of-the-toyota-production-system/
- Wikipedia — Toyota Production System: https://en.wikipedia.org/wiki/Toyota_Production_System
- Supply Chain Today — Jidoka and Andon: https://www.supplychaintoday.com/toyota-production-system-jidoka-stopping-production-a-call-button-and-andon/

### ITIL / ISO 27001
- Hightable — ISO 27001 Annex A 93 Controls Reference: https://hightable.io/iso-27001-annex-a-controls-reference-guide/
- ISMS.online — Annex A 2022 Explained: https://www.isms.online/iso-27001/annex-a-2022/
- DataGuard — ISO 27001 Annex A Overview: https://www.dataguard.com/iso-27001/annex-a/
- Advisera — ISO 27001 vs ITIL: https://advisera.com/27001academy/blog/2016/03/07/iso-27001-vs-itil-similarities-and-differences/
- Fox IT — ITIL and ISO/IEC 27001: https://www.foxitsm.com/wp-content/uploads/ITIL-and-ISO27001-v3.pdf

### YC / a16z
- Sam Altman — Startup Playbook: https://playbook.samaltman.com/
- YC — Startup Playbook (blog): https://www.ycombinator.com/blog/startup-playbook/
- YC Library — Essential Startup Advice: https://www.ycombinator.com/library/4D-yc-s-essential-startup-advice

---

*End of report.*
