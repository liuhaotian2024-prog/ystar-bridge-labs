# Article 11: Seven-Layer Cognitive Construction for Autonomous Missions

## When to Use This

**Trigger**: You are about to declare an autonomous mission, autonomous campaign, or symbol-aligned task.

**Mandatory for**:
- Any work that will take multiple sessions without Board supervision
- Strategic initiatives with >1 week timeline
- Tasks requiring coordination across multiple agents
- Any symbol alignment declaration ("I commit to achieving X")

**NOT required for**:
- Board-directed tasks with explicit instructions
- Routine operations within existing workflows
- Single-session tactical fixes

---

## Core Pattern

Article 11 requires **7 layers of cognitive construction** BEFORE autonomous execution begins:

### Layer 1: Problem Reality Check
- What EXACT problem am I solving? (not symptom, but root cause)
- Who confirmed this is actually a problem? (Board? CIEU audit? User report?)
- What evidence validates this problem exists right now?

### Layer 2: Solution Landscape Scan
- What solutions already exist? (internal tools, external frameworks, prior art)
- Why can't I use existing solutions? (specific blockers, not vague inadequacy)
- What 3 alternatives did I consider and reject? (with reasons)

### Layer 3: Success Criteria Definition
- How will Board VERIFY this mission succeeded? (concrete metrics, not vibes)
- What does "done" look like? (deliverables, passing tests, user feedback)
- What is the failure condition? (when should I abort and report?)

### Layer 4: Resource Inventory
- What tools/agents/data do I have access to?
- What dependencies do I need? (MCP servers, API keys, Board approval for X)
- What is my time budget? (Board expectation: hours? days? weeks?)

### Layer 5: Risk Mitigation
- What can go wrong? (technical debt, scope creep, breaking changes)
- How do I detect early warnings? (metrics, logs, canary tests)
- What is my rollback plan? (can I undo if Board says stop?)

### Layer 6: Coordination Protocol
- Who else needs to know? (which agents will be affected?)
- How do I avoid stepping on others' work? (check DISPATCH.md, active_task.json)
- When do I escalate to Board? (daily report? only on blockers?)

### Layer 7: Reflection Loop
- How will I capture learnings? (write to knowledge/{role}/lessons/?)
- What new patterns should become skills? (distill to Hermes format)
- How do I update organizational DNA? (session_close_yml.py captures this)

**Output**: Write all 7 layers to `reports/autonomous/{mission_name}_7layer_brief.md` BEFORE starting execution.

---

## Common Mistakes

1. **Skipping Layer 1 (Problem)**: jumping to solution without validating the problem exists.
   - Fix: Always ask "who reported this problem?" and "what evidence confirms it?"

2. **Vague Layer 3 (Success)**: "make it better" is not a success criterion.
   - Fix: Define measurable outcomes. Board must be able to verify with one command.

3. **Ignoring Layer 5 (Risk)**: assuming nothing will go wrong.
   - Fix: Every autonomous mission has risks. Document them or you'll be blindsided.

4. **No Layer 6 (Coordination)**: solo cowboy mode breaks team coherence.
   - Fix: Check DISPATCH.md, ping affected agents, write handoff notes.

5. **Forgetting Layer 7 (Reflection)**: treating each mission as one-off instead of building capability.
   - Fix: Every mission should produce 1+ new lesson files. Knowledge compounds.

---

## Example

**Mission**: "Build video content strategy for Y*gov launch" (CMO Sofia, 2026-04-12)

**Layer 1 (Problem)**: Y*gov has no visual content for Show HN launch. Purely technical docs won't attract non-engineer audience. Board confirmed: "we need explainer videos, not just text."

**Layer 2 (Alternatives)**: 
- Hire external videographer → rejected (budget + turnaround time)
- Use stock footage + voiceover → rejected (not authentic, doesn't show actual product)
- Wait for user-generated content → rejected (chicken-egg: need users first)
- **Chosen**: AI-generated persona videos (Hedra, Suno) + screen recordings of live demos

**Layer 3 (Success)**: 
- 5 videos published (CEO intro, product demo, use case walkthrough, technical deep-dive, community CTA)
- Each <3min, hosted on docs site + LinkedIn + Twitter
- Board verification: `ls docs/*.mp4 | wc -l` returns 5

**Layer 4 (Resources)**:
- Hedra API access (Board confirmed)
- Suno for background music
- Screen recording tools (native macOS)
- Claude Code for script generation

**Layer 5 (Risks)**:
- AI-generated faces may look uncanny → mitigation: test 3 samples, get Board approval before batch
- Video file size too large for GitHub → mitigation: host on external CDN, link from docs
- Script may be too technical → mitigation: write for "smart PM who isn't an engineer" persona

**Layer 6 (Coordination)**:
- Notify CSO (videos will be sales assets)
- Check with CTO (product demo needs stable Y*gov install)
- Update DISPATCH.md: "CMO owns video strategy, don't duplicate"

**Layer 7 (Reflection)**:
- New lesson: AI persona videos are faster than hiring, but need human review for tone
- New skill: "content_production_workflow.md" (script → Hedra → edit → publish pipeline)
- Knowledge capture: `session_close_yml.py` will extract Board feedback on video quality

**Output file**: `reports/autonomous/cmo_video_strategy_7layer_brief.md` (written before execution started)

---

**Board Reminder**: Article 11 isn't bureaucracy. It's the difference between "agent did stuff" and "agent built lasting organizational capability."

Every layer you skip = a lesson you'll learn the hard way later.
