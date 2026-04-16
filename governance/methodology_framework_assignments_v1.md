# Methodology Framework Assignments v1.0

**Constitutional, Board 2026-04-16, fixes self-invented-methodology problem**

## Purpose

This specification catalogs **external established methodologies** from authoritative sources and assigns each role at Y* Bridge Labs the mandate to **self-build** their own methodology by customizing frameworks relevant to their scope.

**Root cause addressed:**
- Agents (CEO/CTO/engineers) have been inventing frameworks on the fly ("first-principles CZL 5-tuple", "Ethan#74 ecosystem rules", "atomic dispatch") without grounding them in established theory.
- This causes:
  - Reinventing the wheel (e.g., CZL 5-tuple ≈ OODA Loop, atomic dispatch ≈ Theory of Constraints)
  - Knowledge fragmentation (each agent has implicit heuristics, no shared vocabulary)
  - Lack of external validation (Board cannot cross-check agent reasoning against known frameworks)

**Solution:**
- **Part 1:** Catalog ≥10 established frameworks per role scope (CEO/CTO/engineers/C-suite/Secretary)
- **Part 2:** Map today's observed patterns to external frameworks (validate existing work retroactively)
- **Part 3:** Self-build mandate — each role writes their own `knowledge/{role}/methodology/{role}_methodology_v1.md` (≥800 words, custom mix from external + own observations)
- **Part 4:** Ecosystem Dependency Map (per Ethan#74 spec) — link methodology to agent boot, trust scoring, ForgetGuard enforcement
- **Part 5:** Inline task cards (≥5 dispatches for immediate execution)

---

## Part 1 — External Methodology Catalog (≥10 frameworks per scope)

### CEO Scope (Operating Discipline + Strategic Coordination)

| Framework | Author(s) | Key Concepts | Applicability to CEO Role |
|-----------|-----------|--------------|---------------------------|
| **OODA Loop** | John Boyd (USAF strategist) | Observe → Orient → Decide → Act cycle, tempo advantage, decision superiority | **Core CEO loop:** Every session = observe (read continuations/reports) → orient (assess gaps) → decide (assign tasks) → act (dispatch sub-agents). Maps directly to CZL 5-tuple: Xt=Observe, Y*=Orient, U=Decide, Yt+1=Act, Rt+1=feedback loop. |
| **Cynefin Framework** | Dave Snowden (IBM, Cognitive Edge) | 5 domains: Clear/Complicated/Complex/Chaotic/Confused; context-based decision-making | **Task routing:** P0 crises = Chaotic (act-sense-respond), engineering bugs = Complicated (sense-analyze-respond), new product features = Complex (probe-sense-respond). CEO must identify domain before dispatching. |
| **Theory of Constraints (TOC)** | Eliyahu Goldratt (The Goal) | Identify bottleneck, exploit it, subordinate everything else, elevate it, repeat | **CTO bottleneck (observed 2026-04-13):** CTO is system constraint. CEO must: exploit (give CTO only architectural decisions), subordinate (move code tasks to engineers), elevate (teach engineers to self-architect). |
| **Toyota Production System (TPS)** | Taiichi Ohno (Toyota) | Just-in-time, Jidoka (automation with human touch), Kaizen (continuous improvement), Andon (stop-the-line) | **K9 routing ≈ Andon:** When K9 detects violation, pull the Andon cord (halt session, emit CIEU). CEO kaizen = session_close retrospective + twin_evolution extract. |
| **Double-Loop Learning** | Chris Argyris (Harvard) | Single-loop = fix symptom, double-loop = fix underlying assumption | **Reactive-patch problem (observed):** Fixing bugs without updating ForgetGuard rules = single-loop. Writing new governance rules after each failure = double-loop. CEO must ensure every fix includes rule/test update. |
| **Systems Thinking** | Peter Senge (The Fifth Discipline), Donella Meadows (Thinking in Systems) | Feedback loops, leverage points, system archetypes (Fixes That Fail, Shifting the Burden) | **Governance recursion trap:** More governance → more self-servicing → less product work = Fixes That Fail archetype. CEO must find leverage points (e.g., auto-validate instead of manual reviews). |
| **First Principles Thinking** | Aristotle (ancient), Elon Musk (modern popularizer) | Break problem to fundamental truths, reason up from axioms | **Used for:** When existing frameworks don't apply (e.g., designing Y*gov governance itself — no prior art for self-governing agent companies). |
| **Requisite Variety (Law of)** | W. Ross Ashby (Cybernetics) | Regulator must have ≥ variety of system being regulated | **Trust + diversify principle:** CEO cannot micromanage 4 engineers + 4 C-suite. Must delegate variety (each agent has own methodology) to match system complexity. |
| **OKR (Objectives & Key Results)** | Andy Grove (Intel), popularized by John Doerr (Google) | Set ambitious objectives, measure via 3-5 key results, quarterly review | **Used for:** Board-CEO alignment on quarterly goals (e.g., Q2 2026: ship Y*gov v0.5, 10 pilot customers, $50K ARR). Not micro-task level. |
| **GTD (Getting Things Done)** | David Allen | Capture, clarify, organize, reflect, engage; weekly review | **Session protocol:** Capture = read continuations, clarify = parse to 5-tuple, organize = task cards, reflect = session_close, engage = dispatch. CEO uses GTD at session timescale. |
| **Wardley Mapping** | Simon Wardley (Bits or pieces?) | Value chain mapping, evolution axis (genesis → custom → product → commodity), strategic gameplay | **Product strategy:** Map Y*gov components (e.g., CIEU DB = commodity, ForgetGuard rules = custom, governance philosophy = genesis). Decide build vs buy per evolution stage. |
| **Decision Trees & Expected Value** | Decision Theory (von Neumann, Morgenstern) | Probabilistic decision-making, maximize expected utility | **Used for:** High-uncertainty choices (e.g., invest 2 weeks in Scenario C demo vs pivot to enterprise sales). Calculate EV = P(success) × payoff. |

---

### CTO Scope (Engineering Discipline + Architecture)

| Framework | Author(s) | Key Concepts | Applicability to CTO Role |
|-----------|-----------|--------------|---------------------------|
| **Domain-Driven Design (DDD)** | Eric Evans (Blue Book) | Ubiquitous language, bounded contexts, aggregates, entities/value objects | **Y*gov architecture:** `kernel/` = core domain (CIEU, RT), `governance/` = supporting domain (ForgetGuard, OmissionEngine), `adapters/` = anti-corruption layer (Claude Code hooks). CTO must enforce bounded context boundaries. |
| **Conway's Law** | Melvin Conway (1967) | Organizations design systems that mirror their communication structure | **4-engineer team structure → 4 bounded contexts:** Leo (kernel), Maya (governance), Ryan (platform), Jordan (domains). CTO must align module ownership to team structure. |
| **Clean Architecture** | Robert C. Martin (Uncle Bob) | Dependency inversion, entities/use-cases/adapters layers, independence from frameworks/UI/DB | **Y*gov layers:** Core (RT measurement, CIEU schema) → Use Cases (ForgetGuard, OmissionEngine) → Adapters (Claude Code hooks, GOV MCP). CTO enforces: Core has zero dependencies on adapters. |
| **SOLID Principles** | Robert C. Martin | Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion | **Enforced via:** Code review (CTO checks SRP violations), mypy (LSP violations), ForgetGuard (ISP — rules have minimal interfaces). |
| **YAGNI (You Aren't Gonna Need It)** | Extreme Programming (Kent Beck) | Don't build features until needed | **CTO discipline:** Reject speculative abstractions. Example: Don't build generic "Policy Engine" until we have ≥3 concrete policies. |
| **DRY (Don't Repeat Yourself)** | Andy Hunt, Dave Thomas (Pragmatic Programmer) | Every piece of knowledge has single authoritative representation | **Violation detector:** If same logic appears in ≥2 files, refactor to shared module. CTO audits for DRY violations in code review. |
| **KISS (Keep It Simple, Stupid)** | Kelly Johnson (Lockheed) | Simplicity is virtue, avoid over-engineering | **Applied to:** Governance layer (current violation: too many recursive self-checks). CTO must simplify before adding features. |
| **Microservices Patterns** | Chris Richardson, Sam Newman | Service decomposition, API gateway, saga pattern, event sourcing | **Future state (not current):** If Y*gov scales, decompose to: CIEU service, ForgetGuard service, Hook service. CTO plans migration path. |
| **Hexagonal Architecture (Ports & Adapters)** | Alistair Cockburn | Core business logic independent of I/O adapters, ports define interfaces | **Y*gov structure:** Core = `kernel/` + `governance/`, Adapters = `adapters/claudecode/`, `adapters/openai/` (future). Ports = `emit_cieu()` interface. |
| **Event Storming** | Alberto Brandolini | Collaborative modeling via domain events, identify aggregates/commands/policies | **Used for:** When adding new Y*gov features (e.g., Scenario D — omission detection), CTO runs event storm with engineers to map: Event = OMISSION_DETECTED, Command = trigger audit, Policy = escalate to CEO. |
| **Technical Debt Quadrant** | Martin Fowler | Reckless/Prudent × Deliberate/Inadvertent | **Debt tracking:** `reports/tech_debt.md` categorizes each item. CTO allows Prudent-Deliberate (ship fast, plan payback), rejects Reckless-Inadvertent. |
| **Stability Patterns** | Michael Nygard (Release It!) | Circuit breaker, bulkhead, timeout, retry with exponential backoff | **Applied to:** GOV MCP daemon (current bug: no circuit breaker on CIEU DB lock). CTO must add bulkheads between kernel/governance/platform. |

---

### Engineer Scope (Craft + Execution Discipline)

#### Common to All Engineers

| Framework | Author(s) | Key Concepts | Applicability |
|-----------|-----------|--------------|---------------|
| **TDD (Test-Driven Development)** | Kent Beck (XP), popularized by Uncle Bob | Red → Green → Refactor cycle, write test before code | **Enforced:** All new Y*gov features require test file first. Commit rejected if `test_*.py` not included. |
| **Continuous Delivery** | Jez Humble, Dave Farley | Automated pipeline, trunk-based dev, feature flags, blue/green deploy | **Y*gov CI:** Every commit → pytest + mypy + integration tests. CTO enforces: main branch always releasable. |
| **Pareto Principle (80/20)** | Vilfredo Pareto (economics), applied to engineering by Joseph Juran | 80% of effects from 20% of causes | **Applied to:** Bug triage (fix 20% of bugs that cause 80% of user pain first), test coverage (cover 20% of code paths that handle 80% of edge cases). |
| **Postmortem Culture** | Google SRE Book | Blameless postmortems, focus on system failures not human errors, action items | **Y*gov incidents:** When session crashes or hallucination detected, engineer writes postmortem to `reports/postmortems/{date}_{incident}.md`, CTO reviews for ForgetGuard rule additions. |
| **Code Smells** | Martin Fowler (Refactoring) | Long method, large class, feature envy, shotgun surgery, divergent change | **Code review checklist:** CTO/senior engineer flags smells, assigns refactor task. Examples: `emit_cieu()` callsites scattered = shotgun surgery → centralize. |
| **Refactoring Patterns** | Martin Fowler | Extract method, move field, replace conditional with polymorphism, introduce parameter object | **Used for:** Legacy code cleanup. Example: `rt_measurement.py` has 5 dict params → introduce RTMeasurementConfig dataclass. |

#### Specialist Frameworks (New Engineer Domains)

##### eng-data (Data Engineering / Analytics)

| Framework | Author(s) | Key Concepts | Applicability |
|-----------|-----------|--------------|---------------|
| **Kimball Dimensional Modeling** | Ralph Kimball | Star schema, fact tables, dimension tables, slowly changing dimensions | **CIEU DB schema design:** Fact table = cieu_events (measurable: timestamp, rt_value), Dimensions = agents, tasks, roles. eng-data designs analytics layer. |
| **Lambda Architecture** | Nathan Marz (Big Data) | Batch layer + speed layer + serving layer | **Future CIEU analytics:** Batch (nightly aggregates), Speed (real-time Rt>0 alerts), Serving (query API). eng-data owns this. |
| **Kappa Architecture** | Jay Kreps (LinkedIn) | Stream-only (simplifies Lambda), event sourcing, replay capability | **Alternative to Lambda:** If CIEU DB stays small (<10M events), use Kappa (single stream processing). eng-data decides. |
| **Event Sourcing** | Greg Young, Martin Fowler | Store events not state, replay to rebuild state, audit trail | **CIEU is event-sourced by design.** eng-data ensures: events immutable, state derived via queries, replay possible for debugging. |

##### eng-security (Security / Compliance)

| Framework | Author(s) | Key Concepts | Applicability |
|-----------|-----------|--------------|---------------|
| **STRIDE Threat Modeling** | Microsoft (Loren Kohnfelder, Praerit Garg) | Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege | **Y*gov threat model:** eng-security runs STRIDE on each module. Example: CIEU DB → Tampering (malicious agent deletes events) → mitigation: append-only log. |
| **Defense-in-Depth** | NSA, cybersecurity industry | Multiple layers of security controls | **Applied to:** Governance enforcement = layer 1 (ForgetGuard rules), layer 2 (Stop hooks), layer 3 (CIEU audit log), layer 4 (human review). eng-security ensures no single point of failure. |
| **Zero Trust** | John Kindervag (Forrester), NIST SP 800-207 | Never trust, always verify; micro-segmentation | **Agent permissions:** No agent trusted by default. Each tool call → permission check → CIEU log. eng-security enforces: no implicit trust between CEO/CTO/engineers. |
| **OWASP Top 10** | OWASP Foundation | Top web app vulnerabilities (injection, broken auth, XSS, etc.) | **Not directly applicable (Y*gov is not web app), but:** eng-security checks for injection in Agent tool prompts (e.g., malicious Board input → code injection via bash). |

##### eng-ml (Machine Learning / AI Safety)

| Framework | Author(s) | Key Concepts | Applicability |
|-----------|-----------|--------------|---------------|
| **MLOps Principles** | D. Sculley et al. (Google) | Hidden technical debt in ML systems, monitoring, reproducibility | **Applied to:** Gemma local model (`scripts/local_learn.py`). eng-ml ensures: training data versioned, model checkpoints reproducible, inference monitoring. |
| **Bias-Variance Tradeoff** | Statistics (Geman et al.) | High bias = underfitting, high variance = overfitting, balance via regularization/cross-validation | **Agent behavior tuning:** If CEO always delegates (high bias), train to take more actions. If CEO micromanages (high variance), add regularization (ForgetGuard rules limit). |
| **Cross-Validation** | Statistics (Stone, Geisser) | K-fold CV, hold-out set, avoid overfitting to training data | **Used for:** If Y*gov trains custom agent behavior models, eng-ml ensures: test set never seen during training, metrics validated on fresh sessions. |
| **A/B Testing Rigor** | Statistics, Ron Kohavi (Microsoft) | Randomized controlled trials, statistical significance, multiple testing correction | **Governance experiments:** If testing new ForgetGuard rule, eng-ml runs: 50% sessions with rule ON, 50% OFF, compare Rt+1 metrics, check p-value before rollout. |

##### eng-perf (Performance / Reliability)

| Framework | Author(s) | Key Concepts | Applicability |
|-----------|-----------|--------------|---------------|
| **USE Method (Utilization/Saturation/Errors)** | Brendan Gregg (Netflix, Intel) | For every resource, check: utilization %, saturation (queue depth), error count | **GOV MCP daemon debugging:** eng-perf checks: CPU util (should be <10%), CIEU DB lock saturation (current bug: high), error count in logs. |
| **Latency Budget** | Google SRE | Allocate acceptable latency per layer, monitor budget spend | **Y*gov latency:** Target <100ms per `emit_cieu()` call. eng-perf allocates: 20ms DB write, 30ms hook execution, 50ms buffer. Monitor violations. |
| **Amdahl's Law** | Gene Amdahl (IBM) | Speedup limited by serial fraction of work | **Parallelization limits:** If 20% of Y*gov work is serial (e.g., CEO coordination), max speedup from parallelizing engineers = 5x. eng-perf calculates ROI before adding engineers. |
| **Little's Law** | John Little (MIT) | L = λW (queue length = arrival rate × wait time) | **Task queue modeling:** If CEO dispatches 10 tasks/day (λ=10), engineers finish in 2 days avg (W=2), queue length L=20 tasks. eng-perf monitors to prevent overload. |

##### eng-compliance (Governance / Risk / Compliance)

| Framework | Author(s) | Key Concepts | Applicability |
|-----------|-----------|--------------|---------------|
| **NIST Cybersecurity Framework (CSF)** | NIST | Identify, Protect, Detect, Respond, Recover | **Y*gov compliance:** Identify = asset inventory (CIEU DB, agent credentials), Protect = ForgetGuard rules, Detect = K9 audit, Respond = Andon escalation, Recover = session restart. |
| **GRC (Governance, Risk, Compliance)** | Industry standard | Policy → control → audit → remediation cycle | **Y*gov meta-governance:** eng-compliance ensures: governance rules documented, risk register maintained (`reports/tech_debt.md`), CIEU audit trail complete. |
| **SOC 2 (Service Organization Control)** | AICPA | Trust principles: security, availability, confidentiality, processing integrity, privacy | **If Y*gov sells to enterprises:** eng-compliance maps Y*gov controls to SOC 2 criteria. Example: CIEU audit log → processing integrity evidence. |
| **GDPR Article 25 (Privacy by Design)** | EU GDPR | Data minimization, pseudonymization, privacy as default | **Agent data handling:** eng-compliance ensures: CIEU logs don't store PII by default, agent credentials encrypted at rest, deletion workflows exist. |

---

### CMO/CSO/CFO Scope (Go-to-Market + Finance)

| Framework | Author(s) | Key Concepts | Applicability |
|-----------|-----------|--------------|---------------|
| **Jobs-to-be-Done (JTBD)** | Clayton Christensen (Harvard) | Customers "hire" products to do a job, not for features | **CMO positioning:** Y*gov's job = "catch AI agent mistakes before they reach production". Not "governance framework" (feature-speak). |
| **SPIN Selling** | Neil Rackham (Huthwaite) | Situation, Problem, Implication, Need-Payoff questions | **CSO sales calls:** Situation (how do you deploy agents today?), Problem (what breaks?), Implication (what's the cost?), Need-Payoff (if Y*gov caught 80% of errors, what's the value?). |
| **MEDDIC** | Jack Napoli (PTC), popularized by David Priemer | Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion | **CSO enterprise sales:** Qualify every lead via MEDDIC. Example: Metrics = "5 production incidents/month from agent errors", Economic Buyer = CTO, Champion = DevOps lead. |
| **Unit Economics** | Finance/SaaS industry | CAC (customer acquisition cost), LTV (lifetime value), LTV/CAC ratio, payback period | **CFO pricing model:** If CAC = $5K (sales effort), LTV must be ≥$15K (3x ratio). CFO calculates break-even point per pricing tier. |
| **Lean Startup** | Eric Ries | Build-Measure-Learn loop, MVP, validated learning, pivot or persevere | **CMO product launches:** Don't write 50-page whitepaper upfront. Ship blog post (MVP), measure engagement, learn what resonates, iterate. |
| **Lifetime Value (LTV) Calculation** | SaaS finance (David Skok) | LTV = ARPU × Gross Margin % / Churn Rate | **CFO financial model:** If ARPU = $500/mo, margin = 80%, churn = 5%/mo, LTV = $500 × 0.8 / 0.05 = $8K. Drives pricing strategy. |
| **Positioning (Category Design)** | April Dunford, Al Ries & Jack Trout | Own a category in customer's mind, differentiate vs alternatives | **CMO strategy:** Position Y*gov as "Runtime Governance for AI Agents" (new category), not "Testing Tool" (crowded category). |
| **Content Marketing Flywheel** | HubSpot (Dharmesh Shah) | Attract (SEO blog) → Engage (email nurture) → Delight (customer success) → repeat | **CMO growth engine:** Blog posts → newsletter signup → product trial → case study → referrals. |

---

### Secretary Scope (Knowledge Management + Institutional Memory)

| Framework | Author(s) | Key Concepts | Applicability |
|-----------|-----------|--------------|---------------|
| **Zettelkasten** | Niklas Luhmann (sociologist) | Atomic notes, unique IDs, bidirectional links, emergent structure | **Applied to:** `knowledge/` directory. Each `.md` file = atomic concept, links to related concepts, no rigid hierarchy. Secretary ensures: no orphan notes, links valid. |
| **PARA Method** | Tiago Forte (Building a Second Brain) | Projects, Areas, Resources, Archives | **Directory structure:** Projects = `.claude/tasks/` (active), Areas = `knowledge/{role}/` (ongoing), Resources = `governance/` (reference), Archives = `reports/archive/` (completed). |
| **Building a Second Brain** | Tiago Forte | Capture, Organize, Distill, Express (CODE framework) | **Secretary workflow:** Capture = session_close notes, Organize = PARA folders, Distill = weekly summaries, Express = knowledge articles. |
| **Systems of Records vs Systems of Engagement** | Geoffrey Moore (Crossing the Chasm) | SoR = canonical data (slow-changing), SoE = interaction layer (fast-changing) | **Y* Bridge Labs:** SoR = `knowledge/`, `governance/` (Board-approved, version-controlled), SoE = `.ystar_session.json`, `memory/continuation.json` (session-ephemeral). Secretary guards SoR integrity. |

---

## Part 2 — Mapping to Today's Observed Patterns (Retroactive Validation)

This section maps existing Y* Bridge Labs practices to external frameworks, validating that our "invented" methods are actually rediscoveries of established theory.

| Observed Pattern (Y* Bridge Labs) | Maps to External Framework | Validation / Insight |
|-----------------------------------|----------------------------|---------------------|
| **CZL 5-tuple (Y\*, Xt, U, Yt+1, Rt+1)** | **OODA Loop** (Boyd) | CZL is OODA at atomic task level. Xt=Observe, Y\*=Orient (ideal state), U=Decide (actions), Yt+1=Act (execute), Rt+1=feedback. CZL adds verifiability (Rt+1=0 closure criterion). **Validates CZL as sound decision framework.** |
| **Tier-routing (Board/CEO/CTO/engineers)** | **Cynefin Framework** (Snowden) | P0 crises = Chaotic domain (CEO acts immediately), bugs = Complicated (CTO analyzes), new features = Complex (engineers probe). Current routing aligns with Cynefin. **Validates hierarchical dispatch.** |
| **CTO bottleneck (observed 2026-04-13)** | **Theory of Constraints** (Goldratt) | CTO is system constraint. Solution per TOC: exploit (architectural decisions only), subordinate (delegate code to engineers), elevate (train engineers). **Validates delegation strategy.** |
| **K9 routing (halt on violation)** | **Toyota Andon Cord** (Ohno) | When K9 detects governance violation, pull Andon → halt session, emit CIEU, escalate. Same principle as Toyota production line. **Validates stop-on-error design.** |
| **Reactive-patch problem (fix bugs without updating rules)** | **Single-Loop vs Double-Loop Learning** (Argyris) | Fixing bugs = single-loop. Updating ForgetGuard rules after each failure = double-loop. CEO must enforce double-loop. **Identifies process gap: need mandatory rule update per fix.** |
| **Governance recursion trap (too much self-servicing)** | **Systems Thinking: Fixes That Fail** (Senge, Meadows) | Adding more governance to fix governance failures → recursive overhead → less product work. Classic "Fixes That Fail" archetype. **Suggests leverage point: auto-validate instead of manual reviews.** |
| **Ecosystem-view rule (Ethan#74)** | **Systems Thinking: Interconnectedness** (Meadows) | All components affect each other (daemon ↔ CIEU DB ↔ ForgetGuard ↔ hooks). Must map dependencies before changes. **Validates Ecosystem Dependency Map requirement.** |
| **Trust + diversify (delegate to sub-agents)** | **Requisite Variety** (Ashby) | CEO cannot micromanage 9 agents (4 engineers + 4 C-suite + Secretary). Must delegate variety to match system complexity. **Validates sub-agent autonomy design.** |
| **Sub-agent atomic dispatch (1 deliverable per dispatch)** | **Theory of Constraints + Kanban WIP limits** | Multi-task dispatch → truncation → all work lost. Limiting WIP to 1 prevents overload. **Validates atomic dispatch doctrine.** |
| **Session health score (auto-restart at <40)** | **USE Method** (Gregg) + **Error Budgets** (Google SRE) | Health score = composite metric (Utilization, Saturation, Errors). <40 = exhausted error budget → restart. **Validates health monitoring approach.** |
| **CIEU audit trail (immutable event log)** | **Event Sourcing** (Fowler, Young) | All governance decisions stored as immutable events, state derived via queries. **Validates CIEU DB design.** |
| **ForgetGuard rules (deny choice questions, multi-task dispatch)** | **Poka-Yoke (mistake-proofing)** (Shingo, Toyota) | ForgetGuard = automated mistake-proofing. Prevents errors before they happen, not just detects after. **Validates proactive governance approach.** |
| **First-principles CZL design** | **First Principles Thinking** (Aristotle, Musk) | Used correctly: when no prior art exists (self-governing agent companies = new domain). **But:** Should default to external frameworks first, first-principles only when necessary. |

**Key Insight from Mapping:**
- ~70% of our "invented" frameworks are rediscoveries of established theory (OODA, TOC, Cynefin, Andon, Event Sourcing, Poka-Yoke).
- This validates our reasoning is sound, but shows we lack **shared vocabulary** with external world (marketing/sales handicap).
- Going forward: **Always search for external framework before inventing.** Faster + better grounded + easier to explain to customers.

---

## Part 3 — Self-Build Mandate (Per Role)

Each agent at Y* Bridge Labs must write their own `knowledge/{role}/methodology/{role}_methodology_v1.md` file (≥800 words) by:
1. Reading ≥2 assigned frameworks from Part 1 catalog (relevant to their scope)
2. Observing their own work patterns over ≥3 sessions
3. Writing custom methodology that mixes external frameworks + own heuristics
4. Submitting to CTO for review (not rigid spec enforcement, coaching feedback only)

**Why self-build instead of top-down mandate:**
- **Requisite Variety:** Each role has unique context (CEO coordination ≠ eng-kernel code craft). No single methodology fits all.
- **Ownership:** Writing own methodology → deeper internalization than reading imposed rules.
- **Double-Loop Learning:** Reflection on own patterns → identifies improvement opportunities.
- **Trust Scoring:** Completing methodology = +5pt one-time trust boost (signals self-awareness).

**Template Structure (suggested, not mandatory):**

```markdown
# {Role} Methodology v1.0

## Role Scope
[What decisions/tasks I own]

## External Frameworks I Use
[≥2 frameworks from Part 1, with brief explanation of how I apply them]

## My Core Heuristics (Observed Patterns)
[≥3 rules-of-thumb I follow, with examples from past work]

## Decision Trees
[For common scenarios, what framework do I apply? E.g., "If task is urgent P0 → OODA, if complex → Cynefin probe-sense-respond"]

## Failure Modes I Watch For
[≥2 anti-patterns I avoid, with past mistakes as examples]

## Continuous Improvement Plan
[How I update this methodology — e.g., "After every 10 tasks, review Rt+1 gaps and add new heuristic"]

## References
[Links to external framework sources, past session reports, knowledge articles]
```

**Minimum Acceptance Criteria:**
- ≥800 words (enforces depth, not superficial list)
- ≥2 external frameworks cited with author + source
- ≥3 concrete examples from own past work (not hypothetical)
- ≥1 failure mode documented (shows honest reflection)
- AI re-grain (2026-04-16): Submitted within N idle observation periods after role assignment (N=30 default, ForgetGuard rule: `engineer_no_methodology_after_N_idle_periods` warns at N, escalates at N+15). No hardcoded calendar days.

**Review Process:**
- CTO reads each methodology within 7 days of submission
- Feedback focuses on: missing frameworks (if obvious gap), vague heuristics (need examples), no failure modes (need honesty)
- CTO does NOT enforce rigid template or specific frameworks — this is coaching, not compliance
- After CTO approval, methodology linked in `.claude/agents/{role}.md` "Methodology" section
- Methodology versioned (v1.0 → v1.1 → v2.0) as agent learns and updates

---

## Part 4 — Ecosystem Dependency Map (Integration Spec per Ethan#74)

**Purpose:** Ensure methodology framework is not a dead document, but actively integrated into Y*gov runtime, boot protocol, trust scoring, and ForgetGuard enforcement.

### 4.1 Charter Files (Agent Definitions)

**Location:** `.claude/agents/{role}.md`

**New Section (add to all agent definitions):**
```markdown
## Methodology

**Framework File:** `knowledge/{role}/methodology/{role}_methodology_v1.md`

**Core Frameworks:**
- [Framework 1 name] (Author) — [1 sentence: how I use it]
- [Framework 2 name] (Author) — [1 sentence: how I use it]

**Last Updated:** YYYY-MM-DD

**Completion Status:** ✅ Shipped / 🚧 In Progress / ❌ Not Started
```

**Example (CEO):**
```markdown
## Methodology

**Framework File:** `knowledge/ceo/methodology/ceo_methodology_v1.md`

**Core Frameworks:**
- OODA Loop (Boyd) — Every session = observe continuations → orient priorities → decide dispatch → act via sub-agents
- Theory of Constraints (Goldratt) — Identify bottleneck (currently CTO), subordinate all other work to exploit it
- Double-Loop Learning (Argyris) — Every fix must update ForgetGuard rule (double-loop), not just patch symptom (single-loop)

**Last Updated:** 2026-04-16

**Completion Status:** 🚧 In Progress (due 2026-04-20)
```

### 4.2 Boot Injection (Session Start Context)

**Modify:** `scripts/governance_boot.sh` and `governance/sub_agent_boot_prompt_template.md`

**Add to boot context (after identity restoration, before task briefing):**
```
=== METHODOLOGY CONTEXT ===

Your methodology file: knowledge/{role}/methodology/{role}_methodology_v1.md
Status: {completion_status}

{if completed:}
Summary of your core frameworks:
- {framework_1}: {one_line_summary}
- {framework_2}: {one_line_summary}

Your documented failure modes to avoid:
- {failure_mode_1}
- {failure_mode_2}

{if not completed:}
⚠️ You have not written your methodology yet. This is required within 30 days of role assignment.
Refer to governance/methodology_framework_assignments_v1.md for guidance.
```

**Why:** Every session, agent is reminded of their own documented decision-making patterns. Reduces "forgetting" between sessions.

### 4.3 Trust Scoring Integration

**Modify:** Trust scoring system (currently informal, to be formalized by eng-governance)

**New Trust Events:**
- `METHODOLOGY_COMPLETED`: +5pt one-time (signals self-awareness, planning capability)
- `METHODOLOGY_UPDATED`: +1pt per update (signals continuous improvement)
- `METHODOLOGY_CITED_IN_DECISION`: +0.5pt per citation (signals active use, not dead doc)
- `METHODOLOGY_OVERDUE`: -2pt at 30 days, -5pt at 45 days (signals lack of planning)

**Trust Score Display:**
```
Agent: eng-kernel (Leo Chen)
Trust Score: 68/100
Recent Events:
  +5pt (2026-04-18): METHODOLOGY_COMPLETED
  +0.5pt (2026-04-19): METHODOLOGY_CITED_IN_DECISION (used TDD framework for W22.2)
```

### 4.4 ForgetGuard Enforcement

**New Rule (to be implemented by Maya Patel, eng-governance):**

**File:** `ystar/governance/forgetguard_rules/methodology_enforcement.py`

**Rule 1: `engineer_no_methodology_after_N_idle_periods`**
- **AI re-grain (2026-04-16)**: Trigger based on observation periods, not hardcoded days.
- **Trigger:** Agent role assigned AND N idle observation periods elapsed (N=30 default) AND `knowledge/{role}/methodology/{role}_methodology_v1.md` does not exist
- **Action:** 
  - N periods: WARN (emit CIEU `METHODOLOGY_OVERDUE_WARNING`, send reminder to agent)
  - N+15 periods: ESCALATE (emit CIEU `METHODOLOGY_OVERDUE_CRITICAL`, notify CEO, recommend: re-assign role or fire agent)
- **Rationale:** Methodology is not optional. If agent hasn't reflected on own patterns after N idle periods, they lack self-awareness for autonomous operation. No hardcoded calendar time-grain.

**Rule 2: `methodology_cited_in_major_decision`**
- **Trigger:** Sub-agent receipt for P0 or P1 task (identified via task metadata) AND receipt text does NOT contain any framework name from Part 1 catalog
- **Action:** WARN (emit CIEU `DECISION_NOT_GROUNDED`, suggest: "Consider citing external framework to ground your reasoning")
- **Rationale:** Major decisions should reference established theory, not just gut instinct. This is coaching, not enforcement (WARN not DENY).

**Rule 3: `methodology_stale`**
- **AI re-grain (2026-04-16)**: Trigger based on consecutive task completions without methodology update, not hardcoded days.
- **Trigger:** Agent has completed N consecutive tasks (N=50 default) since last `knowledge/{role}/methodology/{role}_methodology_v1.md` modification
- **Action:** REMIND (emit CIEU `METHODOLOGY_STALE`, suggest: "Review your methodology and update based on recent learnings")
- **Rationale:** Methodologies should evolve as agent learns. After N task completions, methodology should incorporate new patterns. No hardcoded calendar time-grain.

### 4.5 Cross-Cutting: Methodology in CIEU Events

**Modify:** `ystar/kernel/rt_measurement.py` schema

**Add Optional Field to RT_MEASUREMENT:**
```python
class RTMeasurement(TypedDict):
    # ... existing fields ...
    framework_applied: str | None  # e.g., "OODA Loop", "TDD", "Cynefin Complex domain"
```

**Usage:**
- When sub-agent emits RT_MEASUREMENT event, optionally tag which framework they applied.
- CEO/CTO can query: "Which frameworks correlate with lowest Rt+1 gaps?" → data-driven methodology refinement.

**Example:**
```python
emit_rt_measurement(
    y_star="Parser lib ships with 6/6 tests",
    x_t="No parser exists",
    u=["Read spec", "Write code", "Write tests", "Run pytest"],
    y_t_plus_1="Parser exists, tests pass",
    rt_value=0.0,
    framework_applied="TDD (Kent Beck) — Red/Green/Refactor cycle"
)
```

**Analytics Query (future, by eng-data):**
```sql
SELECT framework_applied, AVG(rt_value) AS avg_gap
FROM cieu_events
WHERE event_type = 'RT_MEASUREMENT'
GROUP BY framework_applied
ORDER BY avg_gap ASC;
```

**Insight:** "TDD tasks have avg Rt+1=0.1, non-TDD tasks have avg Rt+1=0.8" → encourage TDD adoption.

---

## Part 5 — Inline Task Cards (Immediate Dispatch, ≥5 Cards)

### Task Card 1 — Ryan Park (eng-platform): Methodology Boot Injection

**Task ID:** `METH-1_eng-platform_boot_inject`  
**Priority:** P1  
**Depends on:** This spec landed

**CIEU 5-tuple:**

**Y\*:** File `scripts/governance_boot.sh` updated to inject methodology summary (per §4.2 spec) into agent boot context. All 9 agents (CEO/CTO/4 engineers/CMO/CSO/CFO/Secretary) receive methodology reminder on session start. Verified by: grep "METHODOLOGY CONTEXT" in governance_boot.sh output.

**Xt:** Current `governance_boot.sh` (commit dedf11d7, 247 lines) loads identity + session state + continuation, but does NOT inject methodology context. Verified via: `grep -i methodology scripts/governance_boot.sh` → 0 matches.

**U (≤15 tool_uses):**
1. Read `governance/methodology_framework_assignments_v1.md` §4.2 (this spec, boot injection section)
2. Read `scripts/governance_boot.sh` current implementation (lines 120-180: boot context assembly)
3. Write bash function `inject_methodology_context()` that:
   - Checks if `knowledge/{role}/methodology/{role}_methodology_v1.md` exists
   - If exists: extracts "Core Frameworks" + "Failure Modes" sections (grep + awk)
   - If not exists: emits warning "⚠️ You have not written your methodology yet"
   - Returns formatted string per §4.2 template
4. Insert call to `inject_methodology_context()` in `governance_boot.sh` after identity restoration (line ~150)
5. Test boot for 3 agents: `bash scripts/governance_boot.sh ceo`, `bash scripts/governance_boot.sh eng-kernel`, `bash scripts/governance_boot.sh cmo`
6. Paste boot output showing "=== METHODOLOGY CONTEXT ===" section
7. Commit: `git commit -m "feat(platform): inject methodology context into governance_boot.sh [METH-1]"`

**Yt+1:** Boot script updated, 3/3 test boots show methodology injection, receipt contains bash output paste.

**Rt+1 target:** 0.0

**Role tags:** `{"producer": "cto", "executor": "eng-platform", "governed": "eng-platform"}`

---

### Task Card 2 — Maya Patel (eng-governance): ForgetGuard Methodology Rules

**Task ID:** `METH-2_eng-governance_forgetguard_rules`  
**Priority:** P1  
**Depends on:** This spec landed

**CIEU 5-tuple:**

**Y\*:** File `ystar/governance/forgetguard_rules/methodology_enforcement.py` exists with 3 rules (per §4.4 spec):
1. `engineer_no_methodology_after_N_idle_periods` (WARN at N periods, ESCALATE at N+15 periods, AI re-grain 2026-04-16)
2. `methodology_cited_in_major_decision` (WARN if P0/P1 task receipt lacks framework citation)
3. `methodology_stale` (REMIND if methodology file >90 days old)

Rules registered in ForgetGuard engine. Tests pass: `pytest ystar/tests/governance/test_methodology_forgetguard.py -q` 5/5 green.

**Xt:** No methodology-specific ForgetGuard rules exist. Current rules in `ystar/governance/forgetguard_rules/*.py`: choice_question_to_board, multi_task_dispatch_disguise, boot_state_reads (3 files, 87 lines total). Verified via: `ls -la ystar/governance/forgetguard_rules/` → 3 files.

**U (≤15 tool_uses):**
1. Read `governance/methodology_framework_assignments_v1.md` §4.4 (this spec, ForgetGuard section)
2. Read `ystar/governance/forgetguard_rules/choice_question_to_board.py` as pattern reference (rule structure, emit_cieu integration)
3. Write `ystar/governance/forgetguard_rules/methodology_enforcement.py` with 3 rules (per §4.4 pseudocode)
4. Write `ystar/tests/governance/test_methodology_forgetguard.py` with:
   - `test_engineer_no_methodology_N_periods_warn()` — agent assigned N idle periods ago, no methodology → WARN
   - `test_engineer_no_methodology_45d_escalate()` — 45d → ESCALATE
   - `test_major_decision_no_framework_warn()` — P0 task receipt, no framework cited → WARN
   - `test_major_decision_with_framework_pass()` — P0 task receipt, framework cited → PASS
   - `test_methodology_stale_N_tasks_remind()` — methodology file unchanged after N task completions → REMIND
5. Register rules in `ystar/governance/forgetguard_engine.py` (add to rule loader list)
6. Run `pytest ystar/tests/governance/test_methodology_forgetguard.py -q`, paste output
7. Commit: `git commit -m "feat(governance): ForgetGuard methodology enforcement rules [METH-2]"`

**Yt+1:** File exists, rules registered, 5/5 tests pass, receipt contains pytest output.

**Rt+1 target:** 0.0

**Role tags:** `{"producer": "cto", "executor": "eng-governance", "governed": "eng-governance"}`

---

### Task Card 3 — Leo Chen (eng-kernel): RT_MEASUREMENT Framework Tag

**Task ID:** `METH-3_eng-kernel_rt_framework_tag`  
**Priority:** P2  
**Depends on:** This spec landed

**CIEU 5-tuple:**

**Y\*:** File `ystar/kernel/rt_measurement.py` updated to add optional `framework_applied: str | None` field to RT_MEASUREMENT schema (per §4.5 spec). All existing `emit_rt_measurement()` callsites still work (backward compatible). New callsites can optionally tag framework. Tests pass: `pytest ystar/tests/kernel/test_rt_measurement.py -q` 8/8 green (2 new tests added).

**Xt:** Current `rt_measurement.py` (commit d89f2a1c, 117 lines) has RT_MEASUREMENT schema with 7 fields (y_star, x_t, u, y_t_plus_1, rt_value, timestamp, task_id). No `framework_applied` field. Verified via: `grep framework_applied ystar/kernel/rt_measurement.py` → 0 matches.

**U (≤15 tool_uses):**
1. Read `governance/methodology_framework_assignments_v1.md` §4.5 (this spec, CIEU framework tagging)
2. Read `ystar/kernel/rt_measurement.py` current schema (lines 15-40)
3. Add `framework_applied: str | None = None` field to `RTMeasurement` TypedDict
4. Update `emit_rt_measurement()` function signature to accept optional `framework_applied` param
5. Update CIEU DB schema (if needed) to store new field (or verify it's stored in JSON blob)
6. Write 2 new tests in `ystar/tests/kernel/test_rt_measurement.py`:
   - `test_rt_measurement_with_framework()` — emit with framework tag, verify DB stores it
   - `test_rt_measurement_without_framework()` — emit without tag (backward compat), verify no error
7. Run `pytest ystar/tests/kernel/test_rt_measurement.py -q`, paste output
8. Update 1 existing callsite (in `ystar/kernel/`) to use new field (as example for engineers)
9. Commit: `git commit -m "feat(kernel): add framework_applied tag to RT_MEASUREMENT [METH-3]"`

**Yt+1:** Schema updated, 8/8 tests pass (6 old + 2 new), receipt contains pytest output.

**Rt+1 target:** 0.0

**Role tags:** `{"producer": "cto", "executor": "eng-kernel", "governed": "eng-kernel"}`

---

### Task Card 4 — Jordan Lee (eng-domains): CEO Methodology (Self-Build Example)

**Task ID:** `METH-4_ceo_methodology_v1`  
**Priority:** P1  
**Depends on:** This spec landed

**CIEU 5-tuple:**

**Y\*:** File `knowledge/ceo/methodology/ceo_methodology_v1.md` exists (≥800 words) following template in §3, citing ≥2 frameworks from CEO catalog (OODA Loop, Theory of Constraints, Double-Loop Learning recommended). File includes ≥3 concrete examples from past CEO work (e.g., session_close retrospectives, sub-agent dispatch decisions, bottleneck identification). CTO reviews and approves. File linked in `.claude/agents/ceo.md` "Methodology" section.

**Xt:** No CEO methodology file exists. CEO has implicit heuristics (observed via session reports) but no documented decision framework. Verified via: `ls -la knowledge/ceo/methodology/` → directory does not exist.

**U (≤15 tool_uses):**
1. Read `governance/methodology_framework_assignments_v1.md` §1 (CEO catalog) + §3 (template)
2. Read past 5 CEO session reports in `reports/ceo/` (identify patterns: how CEO routes tasks, handles bottlenecks, escalates to Board)
3. Create directory: `mkdir -p knowledge/ceo/methodology/`
4. Write `knowledge/ceo/methodology/ceo_methodology_v1.md` (≥800 words):
   - Role Scope: "Coordinate 9 agents, route tasks per Cynefin domain, identify constraints, escalate to Board only when blocked"
   - External Frameworks: OODA Loop (session cycle), Theory of Constraints (CTO bottleneck analysis), Double-Loop Learning (post-fix rule updates)
   - Core Heuristics: ≥3 rules (e.g., "P0 tasks bypass CTO, go direct to engineers", "Never dispatch multi-task to sub-agent")
   - Failure Modes: ≥1 documented mistake (e.g., "2026-04-13: dispatched 6 tasks to Ethan in 1 prompt → truncation → all lost")
   - Continuous Improvement: "After every 10 dispatches, review Rt+1 gaps, add heuristic if pattern found"
5. Run `wc -w knowledge/ceo/methodology/ceo_methodology_v1.md`, verify ≥800 words
6. Update `.claude/agents/ceo.md` to add "Methodology" section (per §4.1 charter template)
7. Commit: `git commit -m "docs(ceo): CEO methodology v1.0 — OODA + TOC + Double-Loop [METH-4]"`
8. Notify CTO for review (emit CIEU `METHODOLOGY_SUBMITTED`)

**Yt+1:** File exists (≥800 words), charter updated, receipt contains wc output, CTO review requested.

**Rt+1 target:** 0.0 (for delivery; CTO review is separate async task)

**Role tags:** `{"producer": "cto", "executor": "eng-domains", "governed": "ceo"}` ← Note: Jordan writes on behalf of CEO (ghostwriting), but methodology governs CEO.

**Special Note:** This is a bootstrapping task. Normally CEO would write own methodology, but CEO is currently handling this dispatch. Jordan ghostwrites, CEO reviews and claims ownership.

---

### Task Card 5 — Samantha Kim (Secretary): Knowledge Directory Audit

**Task ID:** `METH-5_secretary_knowledge_audit`  
**Priority:** P2  
**Depends on:** This spec landed

**CIEU 5-tuple:**

**Y\*:** Report file `reports/secretary/knowledge_directory_audit_20260416.md` exists, documenting:
1. Current state of `knowledge/` directory structure (which roles have methodology files, which don't)
2. Orphan notes (`.md` files not linked from any other file)
3. Missing backlinks (A links to B, but B doesn't link back to A)
4. Recommendations: which roles should prioritize methodology writing (based on trust score, workload, tenure)

Report ≤500 words (concise, actionable). Delivered to CEO for review.

**Xt:** No knowledge audit exists. Current `knowledge/` structure unknown (per Zettelkasten, Secretary should maintain graph integrity). Verified via: `ls -R knowledge/` output unknown to CEO/CTO.

**U (≤15 tool_uses):**
1. Read `governance/methodology_framework_assignments_v1.md` §3 (self-build mandate) + §4.1 (charter integration)
2. Run: `find knowledge/ -name "*.md" | wc -l` → count total knowledge files
3. Run: `find knowledge/ -path "*/methodology/*.md" | wc -l` → count existing methodology files
4. Run: `grep -r "knowledge/" knowledge/ --include="*.md" | wc -l` → count total internal links
5. Identify orphan notes: `find knowledge/ -name "*.md"` + manually check which have 0 inbound links (script or manual audit, ≤10 files expected)
6. Identify missing backlinks: for each link A→B, check if B→A exists (manual audit, ≤10 link pairs expected)
7. Write report: `reports/secretary/knowledge_directory_audit_20260416.md` with findings + recommendations
8. Run `wc -w reports/secretary/knowledge_directory_audit_20260416.md`, verify ≤500 words
9. Commit: `git commit -m "docs(secretary): knowledge directory audit [METH-5]"`
10. Notify CEO (emit CIEU `KNOWLEDGE_AUDIT_COMPLETED`)

**Yt+1:** Report exists (≤500 words), contains file counts + orphan list + recommendations, receipt contains wc output.

**Rt+1 target:** 0.0

**Role tags:** `{"producer": "cto", "executor": "secretary", "governed": "knowledge/"}` ← Governed entity is knowledge directory itself.

---

## Part 6 — Adoption Dependency-Sequence & Success Metrics

**AI re-grain note (2026-04-16)**: Timeline replaced with phase-by-dependency triggered sequence per Board mandate — no hardcoded weekly/daily calendar.

**Phase A (Immediate — depends on: this spec lands):**
- Trigger: This spec committed to governance/
- Task cards METH-1 to METH-5 dispatched to engineers.
- Dependencies: None (parallel dispatch)

**Phase B (Depends on: Phase A task completions):**
- Trigger: After Ryan ships boot injection (METH-1) AND Maya ships ForgetGuard rules (METH-2) AND Leo ships RT framework tag (METH-3)
- Jordan completes CEO methodology (METH-4), Samantha completes knowledge audit (METH-5).
- CTO reviews CEO methodology, provides feedback. CEO updates based on feedback.
- **Phase B Completion Metric:** 3/9 agents have completed methodologies (CEO + 2 engineers who volunteer early).

**Phase C (Depends on: Phase B completion):**
- Trigger: After CEO methodology approved by CTO
- All 9 agents write methodologies (CEO done, 8 remaining: CTO/CMO/CSO/CFO/Secretary + 4 engineers).
- CTO reviews each after submission (no hardcoded 7-day SLA, reviews triggered by submission event), provides coaching feedback.
- Agents update methodologies based on feedback.
- **Phase C Completion Metric:** 9/9 agents have CTO-approved methodologies, all linked in charter files.

**Phase D (Depends on: Phase C completion, ongoing maintenance):**
- Trigger: After all 9 methodologies approved
- Methodologies in active use: sub-agents cite frameworks in receipts (tracked via `methodology_cited_in_major_decision` ForgetGuard rule).
- Data collection: Which frameworks correlate with lowest Rt+1 gaps? (Analytics query per §4.5).
- Ongoing methodology updates: Each agent reviews own methodology after N consecutive task completions (N=50 default, per `methodology_stale` ForgetGuard rule). No hardcoded quarterly calendar cycle.

**Success Metrics (Quantitative):**

**AI re-grain note (2026-04-16)**: Milestone targets replaced with phase-completion triggers, not hardcoded Week N / Q2 calendar dates.

| Metric | Baseline (2026-04-16) | Target (Phase C Complete) | Target (Phase D Steady-State) |
|--------|----------------------|---------------------------|-------------------------------|
| **Agents with completed methodology** | 0/9 (0%) | 9/9 (100%) | 9/9 (100%) |
| **Sub-agent receipts citing frameworks** | Unknown (not tracked) | ≥30% of P0/P1 tasks | ≥60% of P0/P1 tasks |
| **Avg Rt+1 gap (all tasks)** | Unknown (no baseline measurement) | <0.5 | <0.3 |
| **Methodology staleness** | N/A (no files exist) | 0 files with >50 task-completions since last update | ≤1 file with >50 task-completions since last update (acceptable lag for stable roles) |
| **Trust score delta from methodology** | N/A | Avg +5pt per agent (completion bonus) | Avg +8pt per agent (completion + citation bonuses) |

**Success Metrics (Qualitative):**

1. **Shared Vocabulary:** Board/CEO/CTO can discuss decisions using external framework names ("Let's apply TOC here", "This is a Cynefin Complex domain problem") instead of inventing jargon.
2. **Faster Onboarding:** New engineers read existing methodologies → understand team decision-making culture in <1 day (vs current: learn by osmosis over weeks).
3. **External Credibility:** When explaining Y*gov to customers/investors, can cite "We use OODA Loop for decision-making" (sounds professional) vs "We invented CZL 5-tuple" (sounds unproven).
4. **Self-Awareness:** Agents proactively update methodologies when they discover new frameworks or observe own failure patterns (evidence of double-loop learning).

---

## Part 7 — References & Further Reading

**Authoritative Sources for Frameworks:**

### CEO Scope
- Boyd, John. "A Discourse on Winning and Losing" (OODA Loop). U.S. Air Force, 1987.
- Snowden, Dave, and Mary Boone. "A Leader's Framework for Decision Making" (Cynefin). Harvard Business Review, 2007.
- Goldratt, Eliyahu. *The Goal: A Process of Ongoing Improvement*. North River Press, 1984. (Theory of Constraints)
- Ohno, Taiichi. *Toyota Production System: Beyond Large-Scale Production*. Productivity Press, 1988.
- Argyris, Chris. "Double Loop Learning in Organizations" (Harvard Business Review, 1977).
- Senge, Peter. *The Fifth Discipline: The Art & Practice of The Learning Organization*. Doubleday, 1990.
- Meadows, Donella. *Thinking in Systems: A Primer*. Chelsea Green Publishing, 2008.
- Ashby, W. Ross. *An Introduction to Cybernetics*. Chapman & Hall, 1956. (Requisite Variety)
- Doerr, John. *Measure What Matters: How Google, Bono, and the Gates Foundation Rock the World with OKRs*. Portfolio, 2018.
- Allen, David. *Getting Things Done: The Art of Stress-Free Productivity*. Penguin, 2001.
- Wardley, Simon. "Wardley Maps" (online book, https://medium.com/wardleymaps).

### CTO Scope
- Evans, Eric. *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley, 2003.
- Conway, Melvin. "How Do Committees Invent?" Datamation, 1968. (Conway's Law)
- Martin, Robert C. *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall, 2017.
- Martin, Robert C. *Clean Code: A Handbook of Agile Software Craftsmanship*. Prentice Hall, 2008. (SOLID)
- Beck, Kent. *Extreme Programming Explained: Embrace Change*. Addison-Wesley, 1999. (YAGNI)
- Hunt, Andrew, and David Thomas. *The Pragmatic Programmer: Your Journey to Mastery*. Addison-Wesley, 1999. (DRY)
- Richardson, Chris. *Microservices Patterns*. Manning, 2018.
- Cockburn, Alistair. "Hexagonal Architecture" (2005, online article).
- Brandolini, Alberto. *Introducing EventStorming*. Leanpub, 2021.
- Fowler, Martin. "Technical Debt Quadrant" (blog post, https://martinfowler.com/bliki/TechnicalDebtQuadrant.html).
- Nygard, Michael. *Release It! Design and Deploy Production-Ready Software*. Pragmatic Bookshelf, 2007.

### Engineer Scope
- Beck, Kent. *Test-Driven Development: By Example*. Addison-Wesley, 2002.
- Humble, Jez, and David Farley. *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation*. Addison-Wesley, 2010.
- Fowler, Martin. *Refactoring: Improving the Design of Existing Code*. Addison-Wesley, 1999.
- Beyer, Betsy, et al. *Site Reliability Engineering: How Google Runs Production Systems* (Google SRE Book). O'Reilly, 2016. Free online: https://sre.google/books/
- Kimball, Ralph, and Margy Ross. *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*. Wiley, 2013.
- Marz, Nathan, and James Warren. *Big Data: Principles and Best Practices of Scalable Real-Time Data Systems*. Manning, 2015. (Lambda Architecture)
- Kreps, Jay. "Questioning the Lambda Architecture" (blog post, 2014, O'Reilly).
- Young, Greg. "CQRS and Event Sourcing" (talks and articles, https://cqrs.wordpress.com/).
- Shostack, Adam. *Threat Modeling: Designing for Security*. Wiley, 2014. (STRIDE)
- Rose, Scott, et al. *Zero Trust Architecture* (NIST SP 800-207). NIST, 2020.
- Sculley, D., et al. "Hidden Technical Debt in Machine Learning Systems" (NIPS 2015).
- Gregg, Brendan. *Systems Performance: Enterprise and the Cloud*. Prentice Hall, 2013. (USE Method)
- NIST. *Cybersecurity Framework* (https://www.nist.gov/cyberframework).

### CMO/CSO/CFO Scope
- Christensen, Clayton, et al. "Know Your Customers' Jobs to Be Done" (Harvard Business Review, 2016).
- Rackham, Neil. *SPIN Selling*. McGraw-Hill, 1988.
- Priemer, David. "MEDDIC Sales Methodology" (various articles/talks).
- Skok, David. "SaaS Metrics 2.0" (blog series, https://www.forentrepreneurs.com/saas-metrics-2/).
- Ries, Eric. *The Lean Startup: How Today's Entrepreneurs Use Continuous Innovation to Create Radically Successful Businesses*. Crown Business, 2011.
- Dunford, April. *Obviously Awesome: How to Nail Product Positioning*. Ambient Press, 2019.
- Dharmesh Shah (HubSpot). "Inbound Marketing & Sales" (HubSpot Academy resources).

### Secretary Scope
- Ahrens, Sönke. *How to Take Smart Notes: One Simple Technique to Boost Writing, Learning and Thinking*. Sönke Ahrens, 2017. (Zettelkasten)
- Forte, Tiago. *Building a Second Brain: A Proven Method to Organize Your Digital Life and Unlock Your Creative Potential*. Atria Books, 2022. (PARA, CODE)
- Moore, Geoffrey. *Crossing the Chasm*. HarperBusiness, 1991. (Systems of Record vs Engagement)

---

**Related Y* Bridge Labs Documents:**
- `governance/sub_agent_atomic_dispatch.md` — Atomic dispatch doctrine (maps to Theory of Constraints)
- `governance/czl_unified_communication_protocol_v1.md` — CZL 5-tuple spec (maps to OODA Loop)
- `knowledge/shared/unified_work_protocol_20260415.md` — CIEU 5-tuple definition, Rt+1=0 closure criteria
- `AGENTS.md` — Y*gov governance contract (maps to Clean Architecture boundaries)
- `knowledge/ceo/lessons/autonomy_degradation_root_cause_2026_04_13.md` — Self-driving 7 causes diagnosis (maps to Double-Loop Learning)

---

**Version History:**
- v1.0 (2026-04-16): Initial specification. Catalogs ≥10 frameworks per scope, maps to observed patterns, defines self-build mandate, integrates with Ecosystem Dependency Map (Ethan#74), includes 5 inline task cards for immediate dispatch.

---

**END OF SPECIFICATION**

Co-Authored-By: Ethan Wright (CTO) + Board (Haotian Liu) directive 2026-04-16

