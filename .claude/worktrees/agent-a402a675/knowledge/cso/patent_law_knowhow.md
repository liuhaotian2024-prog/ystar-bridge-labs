# Patent Law Knowledge for Y*gov Provisional Patent Application

## Document Purpose
This file contains CSO research on US provisional patent law, conducted March 26, 2026, for Y*gov's y*_t invention patent application.

---

## 1. US Provisional Patent Requirements (USPTO 2026)

### Essential Components
- **Written Description**: Complete technical description clear enough for someone skilled in the field to understand and replicate
- **Drawings**: Any diagrams needed to explain the invention
- **Cover Sheet**: USPTO Form SB/16 identifying this as a provisional application
- **Filing Fee**: $60 (micro), $120 (small), $300 (large entity)

### What's NOT Required (vs Non-Provisional)
- No formal patent claims required
- No oath or declaration needed
- Simpler format, faster filing

### Filing Method
- Electronic via Patent Center (preferred): PDF format, real-time processing
- 12-month pendency (non-extendable) — must file non-provisional within 12 months

### Provisional Structure
1. Background of the invention
2. Summary of the invention
3. Drawings describing the invention
4. Detailed description of the invention

---

## 2. Alice Corp v. CLS Bank (2014) — Software Patent Eligibility

### The Holding
Alice Corp. v. CLS Bank International, 573 U.S. 208 (2014): Patents on abstract ideas implemented on generic computers are INVALID.

### Two-Step Test
1. Is the claim directed to an abstract idea?
2. Does the claim contain an "inventive concept" — something MORE than just implementing the abstract idea on a computer?

### What This Means for Software Patents
- Simply putting an abstract idea "on a computer" is NOT enough
- Must show concrete technical implementation details
- Must demonstrate how the invention improves computer functionality itself
- Must distinguish from prior art with specific technical mechanisms

### Post-Alice Impact
- Massive increase in software patent invalidations
- Patent office rejections under 35 U.S.C. § 101 increased dramatically
- Survival strategy: Show technical improvement, not just automation

---

## 3. Patent Claims Drafting Best Practices

### Independent Claims
- Define the **broadest scope** of protection
- Establish primary elements without relying on other claims
- Should capture the core innovation
- Maximize protection scope while maintaining clarity

### Dependent Claims
- Refine independent claims with specific implementation details
- Add limitations that narrow scope but increase defensibility
- Cover specific embodiments

### Language Precision
- Define specialized terminology clearly
- Use "a" or "an" at first mention
- Use "said" or "the" for subsequent references
- Avoid ambiguity — critical for enforceability

### Software-Specific Considerations
- Structure claims so a single entity performs all steps (avoid divided infringement)
- Showcase practical applications demonstrating utility
- Provide real-world scenarios solving specific problems
- Focus on technical effects, not business outcomes

---

## 4. Differentiating from Prior Art

### Novelty Test
- Invention must not be identical to any single prior art reference
- Must be more than trivial variation

### Non-Obviousness Test
- Must not be derivable by person of ordinary skill in the art (POSITA)
- Cannot be obvious combination of existing elements
- Must show unexpected results or advantages

### Differentiation Strategy
1. Conduct thorough prior art search
2. Emphasize structural AND functional differences
3. Highlight unique features explicitly
4. Describe the problem solved differently than prior art
5. Show technical improvements over existing solutions

### For Software Patents
- Detail how software operates uniquely
- Explain problems solved that prior art cannot solve
- Show how it interacts with systems in novel ways
- Balance claim breadth (too broad = overlap risk; too narrow = weak protection)

---

## 5. Prior Art in AI Agent Governance (2026 Landscape)

### Identified Prior Art Systems

#### A. Microsoft Agent-Governance-Toolkit
**Source**: github.com/microsoft/agent-governance-toolkit (MIT license, community preview as of March 2026)

**What It Does**:
- Runtime policy enforcement for AI agents
- Deterministic policy engine (OPA/Rego, Cedar, YAML)
- Cryptographic identity (Ed25519, SPIFFE/SVID)
- Execution sandboxing with 4-tier privilege rings
- Append-only audit logs

**Key Technical Approach**:
- Decision gate: Evaluates actions BEFORE execution
- Returns `allowed` boolean based on policy
- Logs events (tool calls, resource access, inter-agent communication)
- Behavioral anomaly detection for rogue agents
- Saga orchestration for multi-step workflows
- Sub-millisecond latency (<0.1 ms)

**CRITICAL LIMITATION** (for patent differentiation):
- **NO "ideal contract" field** written to audit records before execution
- Logs decisions and events but does NOT write "what should happen" as separate audit field
- Omission detection relies on circuit breakers and SLO violations (reactive, not proactive)
- Policy exists separately from audit records

#### B. Proofpoint Agent Integrity Framework (2026)
**Source**: Announced March 17, 2026; white paper available at proofpoint.com

**What It Does**:
- Intent-Based Access Control (IBAC)
- Five pillars: Intent Alignment, Identity and Attribution, Behavioral Consistency, Auditability, Operational Transparency
- Addresses "semantic privilege escalation"
- Emphasizes that "permissions alone can't ensure proper alignment or accountability"

**Key Technical Approach** (limited detail available):
- Intent verification at runtime
- Multi-surface control points
- Five-phase maturity model
- Continuous verification of agent behavior

**CRITICAL LIMITATION** (for patent differentiation):
- Detailed technical specs unavailable from public sources (white paper download required)
- Appears focused on intent verification, but unclear if "ideal contract" is written to audit records
- No clear description of proactive omission detection mechanism

#### C. LangSmith / Langfuse / LLM Observability Tools
**What They Do**:
- Post-hoc logging and observability
- Trace agent actions after execution
- Debugging and monitoring dashboards

**CRITICAL LIMITATION**:
- **Pure observability, no enforcement**
- Log what happened, not what should have happened
- No governance, no ideal contract, no omission detection

---

## 6. How Y*gov's y*_t Differs from Prior Art

### Core Invention: y*_t as Pre-Execution Ideal Contract Field

**What Y*gov Does Differently**:
1. **y*_t field written to CIEU BEFORE tool execution** — by the enforcement engine, not by the agent
2. **y*_t is machine-verifiable predicate** — not a policy decision boolean, but a complete contract hash
3. **Absence of y*_t field is itself evidence** of ungoverned action
4. **Agent cannot modify y*_t** — written by kernel, sealed with Merkle proof

**Prior Art Gap**:
- Microsoft: Logs policy decisions but does NOT write ideal contract to audit record
- Proofpoint: Intent-based but no clear "ideal contract field" in audit structure
- LangSmith/Langfuse: No governance, pure post-hoc logs

### Invention 2: OmissionEngine Passive Non-Compliance Detection

**What Y*gov Does Differently**:
- **Agent's own next action triggers scan()** — not polling, not monitoring
- **Obligations created at task assignment time** — not inferred from logs
- **SOFT → HARD state machine** — explicit lifecycle for overdue obligations
- **Deterministic, zero-latency** — no external monitoring required

**Prior Art Gap**:
- Microsoft: Circuit breakers and SLO violations (reactive, requires threshold breach)
- Proofpoint: Unclear mechanism from public documentation
- Others: No passive violation detection

### Invention 3: NL-to-Deterministic-Contract Translation with Human-in-Loop

**What Y*gov Does Differently**:
- **Non-technical users write rules in plain English**
- **LLM translates to IntentContract (Python AST)**
- **Deterministic validator checks contract correctness**
- **Human confirms translation once**
- **LLM exits enforcement path entirely** — no LLM at runtime

**Prior Art Gap**:
- All prior systems require technical policy languages (OPA/Rego, Cedar)
- No "translate once, enforce forever" pattern found
- No explicit human confirmation step before deterministic enforcement

---

## 7. Alice Corp Compliance Strategy for Y*gov Patent

### Challenge
Software patents must show "something more" than abstract idea on a computer.

### Y*gov's "Something More"
1. **Specific data structure invention**: y*_t as audit field with cryptographic sealing
2. **Novel state machine**: SOFT/HARD obligation lifecycle
3. **Architectural innovation**: LLM out of enforcement path (translation layer only)
4. **Technical problem solved**: Agent fabrication prevention (cryptographic, not behavioral)
5. **Computer functionality improvement**: Deterministic audit records vs post-hoc logs

### Patent Claim Strategy
- Focus on **how** y*_t is written to audit records (kernel-enforced, pre-execution, agent-immutable)
- Focus on **how** obligations are scanned (action-triggered, not polled)
- Focus on **how** NL rules become deterministic (translation pipeline, human confirmation gate)
- Cite specific code: engine.py, omission_engine.py, nl_to_contract.py line numbers

---

## Sources

### USPTO Documentation
- [Provisional Application for Patent | USPTO](https://www.uspto.gov/patents/basics/apply/provisional-application)
- [Filing a provisional application](https://www.uspto.gov/sites/default/files/documents/Basics%20of%20a%20Provisional%20Application.pdf)
- [Drafting a Provisional Application](https://www.uspto.gov/sites/default/files/documents/provisional-applications-6-2023.pdf)

### Alice Corp Decision
- [Alice Corp. v. CLS Bank International - Wikipedia](https://en.wikipedia.org/wiki/Alice_Corp._v._CLS_Bank_International)
- [Alice Corp. v. CLS Bank Int'l | 573 U.S. 208 (2014) | Justia](https://supreme.justia.com/cases/federal/us/573/208/)
- [Patenting Software and Beyond: A Guide to Understanding Alice](https://henry.law/blog/understanding-alice/)

### Claims Drafting
- [Patent Claims: Drafting Software and Computerized Method Claims](https://www.lexisnexis.com/community/insights/legal/b/practical-guidance/posts/patent-claims-drafting-software-and-computerized-method-claims)
- [How to Write a Strong Patent Claim: Best Practices | PatentPC](https://patentpc.com/blog/how-to-write-a-strong-patent-claim-best-practices)
- [Best practices for drafting strong patent claims](https://patentlawyermagazine.com/best-practices-for-drafting-strong-patent-claims/)

### Prior Art Research
- [GitHub - microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit)
- [Proofpoint Agent Integrity Framework – 2026 Edition](https://www.proofpoint.com/us/resources/white-papers/agent-integrity-framework)
- [Proofpoint Unveils Industry's Newest Intent-Based AI Security Solution](https://www.proofpoint.com/us/newsroom/press-releases/proofpoint-unveils-industrys-newest-intent-based-ai-security-solution)

---

**Document Status**: Research complete, ready for patent drafting
**Next Step**: Read Y*gov source code and experimental evidence
