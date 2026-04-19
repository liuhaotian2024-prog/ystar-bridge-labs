---
Audience: CEO (Aiden), Board (Haotian Liu), eng-platform (Ryan Park), eng-governance (Maya Patel)
Research basis: 7 industry sources (NeMo Guardrails, Constitutional AI, ACE Framework, PSG-Agent, GWT, RMM, BDI+ML); 92 internal knowledge files inventoried and read across knowledge/ceo/wisdom/ and knowledge/ceo/lessons/
Synthesis: 92 CEO knowledge assets sit as static files with near-zero automated activation rate; a 5-channel shelf-activation architecture converts them from potential to kinetic governance, measurable via CIEU events
Purpose: Enable Board approval of implementation plan; provide eng-platform and eng-governance with actionable spec for Phase 1-4 build-out
---

# ARCH-17: Behavioral Governance and Shelf-Activation Architecture

**Author**: CTO (Ethan Wright)
**Date**: 2026-04-18
**Status**: SPEC (pending Board review)
**Scope**: Consolidate 30+ MEMORY feedback entries + 50+ CEO wisdom files into enforceable governance with activation mechanism guaranteeing files fire in production

---

## 1. Problem Statement

Two classes of behavioral knowledge exist as static files lacking structural enforcement:

**Class A -- Behavioral Feedback Memories (30+ entries in MEMORY.md)**
Operational lessons from Board corrections, CEO self-diagnosis, and system failures. Loaded at session start but nothing guarantees they influence specific decisions at the relevant moment.

**Class B -- CEO Wisdom/Cognitive Files (50+ files across 5 subdirectories)**
Identity invariants (6D architecture, Aiden Laws, zhixing heyi), paradigms (mechanism > discipline, identification != completion), self-knowledge (peak state vs deformation, reactive default), strategy, and failure-mode lessons in `knowledge/ceo/wisdom/` and `knowledge/ceo/lessons/` -- never systematically surfaced during operation.

**The shelf problem**: Files on disk = potential energy. Files injected into decision context = kinetic energy. Current conversion rate is near zero.

**Measurable gap**: 0% of wisdom files are referenced via any automated mechanism. 100% depend on CEO voluntarily remembering -- which per `mechanism_over_discipline.md` guarantees eventual 100% forgetting rate.

---

## 2. Inventory and Taxonomy

### 2.1 Category 1-7: Behavioral Feedback Memories (Class A)

| Cat | Function | Count | Examples |
|-----|----------|-------|---------|
| 1 | Dispatch discipline | 6 | dispatch_via_cto, taskcard_not_dispatch, use_whiteboard_not_direct_spawn, no_postponed_dispatch_promise, explicit_git_op_prohibition, subagent_boot_no_state_read |
| 2 | Receipt/verification | 4 | subagent_receipt_empirical_verify, ceo_reply_must_be_5tuple, status_maturity_taxonomy, subagent_no_choice_question |
| 3 | Identity/mode | 4 | default_agent_is_ceo, active_agent_drift, address_laoda, ai_disclosure_mandatory |
| 4 | Anti-pattern prohibition | 5 | no_clock_out, no_consultant_time_scales, no_static_image_for_video, close_stub_trigger, board_shell_marker |
| 5 | Autonomy/self-drive | 3 | autonomy_degradation_7_causes, testing_is_ceo_scope, timing_vs_schedule_distinction |
| 6 | Meta-governance | 4 | cto_subagent_cannot_async_orchestrate, team_enforce_asymmetry, ceo_ecosystem_view_required, methodology_no_human_time_grain |
| 7 | Content/paradigm | 4 | scenario_c_is_real_usp, cieu_5tuple_task_method, god_view_before_build, cmo_12layer_rt_loop |

### 2.2 Category 8-12: CEO Wisdom/Cognitive Files (Class B)

| Cat | Subdirectory | Count | Function | Key Files |
|-----|-------------|-------|----------|-----------|
| 8 | wisdom/meta/ | 24 | 6D identity, cognitive architecture, field theory | 6d_cognitive_architecture, aiden_laws_hierarchy, global_workspace_architecture, building_aiden, zhixing_heyi, field_vs_structure_duality, courage_generalized, autonomous_loop_algorithm |
| 9 | wisdom/paradigms/ | 7 | Meta-lessons from past failures | mechanism_over_discipline, identification_is_not_completion, whitelist_over_blacklist, extend_not_build, system5_not_operations, auditor_independence, hook_output_format_lesson |
| 10 | wisdom/self_knowledge/ | 8 | Constitutional CEO identity invariants | absolute_honesty_to_board, peak_state_vs_deformation, reactive_default, three_level_drive, z_axis_self_initiation, valve_discipline, fear_of_external, blind_spot_consensus_assumption |
| 11 | strategy/ | 7 | CEO strategic thinking artifacts | verification_service_spec, mission_function_and_ceo_philosophy, phase1_foundation_proposal, ceo_operating_manual, STRAT-001_governance_moat |
| 12 | lessons/ | 16 | Failure-mode knowledge, post-mortems | autonomy_degradation_root_cause, governance_self_deadlock, posted_not_executed_hallucination, performance_misdiagnosis_daemon_vs_cache, industry_precedent_scan_first |

**Total**: 30 behavioral memories + 62 wisdom files = **92 governance-relevant knowledge units**.

---

## 3. Formal Definitions

Let K = {k_1, k_2, ..., k_92} be the set of all knowledge units.

Each k_i has:
- **topic_vector(k_i)**: semantic embedding of file content
- **trigger_set(k_i)**: conditions under which k_i is relevant
- **decay(k_i, t)**: relevance decay over session time t
- **activation_count(k_i)**: times k_i surfaced in a decision context

**Shelf ratio** S(t):
```
S(t) = |{k_i : activation_count(k_i) == 0}| / |K|
```

Current: S(t) ~ 0.95. Target: S(t) <= 0.30 for sessions > 10 tool_uses.

**Relevance match** R(k_i, ctx):
```
R(k_i, ctx) = cosine(embed(k_i), embed(ctx))
```

k_i **should fire** when R(k_i, ctx) >= 0.65. Shelf activation failure = should have fired but did not.

---

## 4. Mathematical Model

### 4.1 Retrieval as Attention (Global Workspace Theory)

Model decisions as a Global Workspace (Baars 1988) with N knowledge processes competing for the context-window spotlight:

```
For each decision point d_j:
  candidates = {k_i : R(k_i, ctx(d_j)) >= 0.65}
  top_k = argsort(R, descending)[:MAX_INJECT]
  inject(top_k) and broadcast to all processes
```

Maps to CEO's `global_workspace_architecture.md`: 5 parallel processes, winner broadcast to all.

### 4.2 Hebbian Reinforcement

Co-activated units strengthen:
```
weight(k_i, k_j) += alpha * activation(k_i) * activation(k_j)
```

Per `personal_neural_network_concept.md`: fire together, wire together.

### 4.3 Decay and Consolidation

```
relevance_boost(k_i, t) = base * exp(-lambda * sessions_since_last_activation)
```

If activation_count > theta over N sessions, permanent boost (long-term memory).

---

## 5. Architecture Design

### 5.1 Three-Layer Activation Architecture

```
Layer 3: IDENTITY INVARIANTS (always-on, constitutional)
  Source: self_knowledge/ + aiden_laws_hierarchy
  Mechanism: governance_boot.sh injects at session start
  Analogy: CPU microcode -- never paged out

Layer 2: PARADIGM RAILS (trigger-activated, retrieval-based)
  Source: paradigms/ + lessons/ + high-relevance meta/
  Mechanism: pre-output hook RAG query, top-N injection
  Analogy: L2 cache -- fast on context match

Layer 1: STRATEGIC CONTEXT (on-demand, search-based)
  Source: strategy/ + remaining meta/
  Mechanism: autonomous loop pulls during idle
  Analogy: Main memory -- available not always cached
```

### 5.2 Component Design

#### 5.2.1 Wisdom Index (built at boot)

```python
class WisdomIndex:
    def __init__(self, knowledge_dir):
        self.units = self._scan(knowledge_dir)
        self.embeddings = self._embed(self.units)
        self.activation_log = {}

    def query(self, context, top_k=3):
        scores = {k: cosine(embed(context), self.embeddings[k]) for k in self.units}
        return sorted(scores, key=scores.get, reverse=True)[:top_k]

    def shelf_ratio(self):
        activated = sum(1 for v in self.activation_log.values() if v > 0)
        return 1.0 - (activated / len(self.units))
```

#### 5.2.2 Pre-Output Wisdom Injector

```python
def wisdom_inject(reply_draft, context):
    relevant = wisdom_index.query(context, top_k=3)
    for k in relevant:
        wisdom_index.record_activation(k.id)
        emit_cieu("WISDOM_ACTIVATED", {"unit": k.id, "relevance": k.score})
    injection = [f"[WISDOM:{k.id}] {k.summary}" for k in relevant]
    return f"<!-- {injection} -->\n{reply_draft}"
```

#### 5.2.3 Paradigm Violation Detector

Scans reply drafts for anti-pattern signatures:

| Paradigm | Anti-pattern signals | Remedy |
|----------|---------------------|--------|
| identification_is_not_completion | "found X" without same-turn action | Must terminate in Action/Dispatch/Postpone-with-reason/WontFix |
| mechanism_over_discipline | "remember rule" / "next time careful" | Write hook/script not MEMORY rule |
| extend_not_build | "create new module" without precheck | Precheck 4 repos first |
| system5_not_operations | "I will manually" / "CEO writes code" | Dispatch to CTO/engineer |
| reactive_default | "waiting for Board" / "waiting for instructions" | Pull from ADE action queue |
| peak_state_deformation | "hurry to prove" / "rush to finish" | PAUSE -- feedback = information not attack |

6 paradigms, 16 total patterns. Emits CIEU `PARADIGM_VIOLATION_DETECTED`.

#### 5.2.4 Shelf Health Monitor

Every 15 tool_uses: compute shelf_ratio, emit `SHELF_HEALTH_CHECK`. If > 0.50, force-surface 3 cold units as thought prompts.

---

## 6. Industry Precedent Analysis

### 6.1 NVIDIA NeMo Guardrails -- Retrieval Rails

Five rail types (input, dialog, retrieval, execution, output). Retrieval rails intercept RAG chunks before LLM consumption. Our wisdom injector = retrieval rail on CEO's own knowledge base. Colang separates "what to check" from "how" -- same as our paradigm definitions.

Ref: [NeMo Guardrails](https://github.com/NVIDIA-NeMo/Guardrails); Rebedea et al., EMNLP 2023 Demo.

### 6.2 Anthropic Constitutional AI -- Self-Critique

Models self-critique against natural-language principles. Jan 2026 Claude constitution: 4-tier hierarchy (safety > ethics > adherance > helpfulness). Our Aiden Laws (L0 Mission > L1 Honesty > L2 Action > L3 Principles > L4 Self) is isomorphic. Key difference: Constitutional AI = training-time weights; ours = inference-time context injection.

Ref: Bai et al., [arxiv 2212.08073](https://arxiv.org/abs/2212.08073), 2022; [BISI analysis](https://bisi.org.uk/reports/claudes-new-constitution-ai-alignment-ethics-and-the-future-of-model-governance), Jan 2026.

### 6.3 ACE Framework -- Evolving Contexts

Treats contexts as evolving playbooks with iterative generation, reflection, curation. Addresses brevity bias (compression drops insights) and context collapse (rewriting erodes details). Maps to our Layer 3 never-compress + Layer 2 activation-curated + Layer 1 periodically-resurfaced.

Ref: [arxiv 2510.04618](https://arxiv.org/abs/2510.04618), Oct 2025; [ACE GitHub](https://github.com/ace-agent/ace).

### 6.4 PSG-Agent -- Personality-Aware Guardrails

Personalized guardrails via interaction-history personality mining + real-time state capture. Validates our persona-specific paradigm detectors over generic safety rails.

Ref: [arxiv 2509.23614](https://arxiv.org/abs/2509.23614), 2025.

### 6.5 Global Workspace Theory -- Attention Competition

N parallel processes compete for broadcast spotlight. Our 92 knowledge units compete for context window via relevance scoring. Winners broadcast, losers remain indexed for next round.

Ref: [Frontiers Robotics AI 2025](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2025.1607190/full); [Lanham GWT+AI](https://micheallanham.substack.com/p/global-workspace-theory-and-the-missing).

### 6.6 Reflective Memory Management (RMM)

Prospective (summarize into memory bank) + Retrospective (refine retrieval via RL). Maps to Hebbian updates (prospective) + shelf health monitor (retrospective).

Ref: [ACL 2025](https://aclanthology.org/2025.acl-long.413/).

### 6.7 BDI + ML -- Belief Revision

ML-BDI integrates learning into belief-desire-intention. Alert-BDI adds adaptive alertness. Our paradigm files = beliefs, activation patterns = evidence, Hebbian updates = revision. Peak-state detector = alertness modulation.

Ref: [arxiv 2510.20641](https://arxiv.org/abs/2510.20641); [arxiv 2510.25445](https://arxiv.org/abs/2510.25445), 2025.

---

## 7. Shelf-Activation Mechanism Design

### 7.1 Design Principles

1. **Mechanism > Discipline**: hook-enforced, not memory-dependent
2. **Field + Structure duality**: wisdom = field (energy), hooks = structure (precision)
3. **Whitelist activation**: define what SHOULD fire per context class
4. **Zhixing heyi**: knowledge not manifesting in behavior is not true knowledge

### 7.2 Five Activation Channels

#### Channel 1: Boot-Time Constitutional Injection (Layer 3)

**Files**: absolute_honesty_to_board, aiden_laws_hierarchy, peak_state_vs_deformation, three_level_drive, reactive_default

**Mechanism**: governance_boot.sh reads 5 files into `.ystar_session_identity.json`. Always in session context.

**CIEU**: `IDENTITY_BLOCK_LOADED`. Missing = health score 0.

**Guarantee**: 100% activation by construction.

#### Channel 2: Pre-Decision RAG Injection (Layer 2)

**Trigger**: tool_use in reply, reply > 200 tokens, or dispatch keywords.

**Mechanism**: pre-output hook queries WisdomIndex, injects top-3 one-line summaries.

**CIEU**: `WISDOM_ACTIVATED` per unit. Target: >= 70% relevant-context activation.

#### Channel 3: Anti-Pattern Violation Detection (Layer 2)

**Mechanism**: regex scan of reply against PARADIGM_ANTI_PATTERNS registry (6 paradigms, 16 patterns). On match, inject remedy + `[PARADIGM_VIOLATION]` tag.

**CIEU**: `PARADIGM_VIOLATION_DETECTED`. Target: >= 90% detection rate.

#### Channel 4: Periodic Cold-Unit Resurfacing (Layer 1)

**Mechanism**: every 15 tool_uses, if shelf_ratio > 0.50, sample 3 cold units as thought prompts.

Example: from courage_generalized: "Is there a boundary being treated as real that is actually a pseudo-consensus?"

**CIEU**: `SHELF_RESURFACING`. Target: shelf_ratio <= 0.30 by session end (>30 tool_uses).

#### Channel 5: Decision-Gate Forced Read (Layer 3)

| Decision Type | Mandatory Reads | Gate |
|--------------|----------------|------|
| Dispatch sub-agent | system5_not_operations, dispatch_via_cto | Pre-dispatch hook |
| Create new component | extend_not_build, god_view_before_build | PreToolUse on new-path Write |
| Commit code | hook_output_format_lesson | Pre-commit hook |
| Reply to Board criticism | peak_state_vs_deformation, absolute_honesty | Pre-output on correction markers |
| Propose new agent/role | auditor_independence, ecosystem_view | Pre-dispatch on agent/role keywords |
| Close/complete task | identification_is_not_completion | Pre-output on done/shipped/completed |

**CIEU**: `DECISION_GATE_FIRED`. Target: 100% gate hit rate. No bypass.

### 7.3 Embedding Infrastructure

Model: Gemma 2B via Ollama (localhost:11434). Fallback: TF-IDF/sklearn.
Index: `.ystar_wisdom_index.json`, rebuilt when source files change.
Latency: < 200ms per query.

### 7.4 Integration Points

```
governance_boot.sh --> WisdomIndex build + Channel 1 identity load
hook_ceo_pre_output.py --> Channel 2 RAG + Channel 3 anti-pattern + Channel 5 gates
PostToolUse hook --> Channel 4 shelf health every 15 tool_uses
```

### 7.5 Measurement Dashboard

| Metric | Target | Red Line |
|--------|--------|----------|
| shelf_ratio | <= 0.30 | > 0.70 |
| identity_loaded | 1.00 | < 1.00 |
| paradigm_activation | >= 0.70 | < 0.40 |
| violation_detection | >= 0.90 | < 0.60 |
| gate_hit_rate | 1.00 | < 1.00 |
| wisdom_diversity | >= 0.50 | < 0.20 |

### 7.6 Board's Key Question Answered

> "How do we guarantee 6D Aiden files fire in at least X% of relevant decisions, measurable via CIEU?"

Channel 1: 100% for 5 identity files (by construction). Channel 5: 100% at high-stakes gates (by hook). Channel 3: ~90% anti-pattern detection (regex). Channel 2: ~70% contextual retrieval (embedding quality bound). Channel 4: shelf_ratio <= 0.30 (forced resurfacing).

Combined: >= 70% of 92 units surfaced per session (>30 tool_uses). Top-5 identity = 100%. 6 paradigm sets = 90%+. All measurable via CIEU counts, independently verifiable by K9.

---

## 8. Implementation Phases

**Phase 1** (eng-platform): TF-IDF WisdomIndex + Channel 1 boot injection + CIEU events.
Accept: IDENTITY_BLOCK_LOADED fires; shelf_ratio computable.

**Phase 2** (eng-platform + eng-governance): Channel 3 anti-pattern + Channel 5 decision gates.
Accept: PARADIGM_VIOLATION_DETECTED on synthetic test; DECISION_GATE_FIRED before dispatch.

**Phase 3** (eng-kernel): Gemma embeddings + Channel 2 RAG + Channel 4 cold resurfacing + dashboard.
Accept: shelf_ratio <= 0.30; wisdom_activation_rate >= 0.70.

**Phase 4** (hardening): Hebbian cross-session weights, decay/consolidation, K9 audit integration.
Accept: activation patterns persist across sessions.

---

## 9. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Context window overflow | High | Cap 3 units/decision; one-line summaries only |
| Embedding quality insufficient | Medium | TF-IDF fallback; manual trigger_set for critical files |
| Hook latency | Medium | 200ms budget; async precomputation at boot |
| Injection ignored by CEO | Medium | Decision gates force acknowledgment; anti-pattern catches violations |
| False positive detection | Low | 48h dry-run per new pattern; CIEU audit trail |
| Wisdom file contradictions | Low | Aiden Laws hierarchy resolves; flag to Board if stuck |

---

## 10. CEO Cognitive Architecture Mapping

| CEO Concept | Implementation |
|-------------|---------------|
| Global Workspace Theory | WisdomIndex competition + top-k broadcast |
| Personal Neural Network | Hebbian weights + spreading activation |
| Mechanism > Discipline | Hook enforcement not MEMORY rules |
| Field vs Structure duality | Wisdom = field, hooks = structure |
| Zhixing heyi | Must fire in behavior or not true knowledge |
| Identification != Completion | Anti-pattern prevents "discovered but not acted" |
| Autonomous Loop Algorithm | Channel 4 resurfacing during idle |
| Three-Level Drive | Channel 2 RAG pulls Level 3 mission knowledge |
| Peak State vs Deformation | Anti-pattern for stress deformation |
| Aiden Laws Hierarchy | Conflict resolution between wisdom files |
| Courage Generalized | Resurfacing: "Is this boundary real?" |
| Building Aiden | Shelf activation = cognitive architecture as infrastructure |

---

## Appendix A: File Inventory

**wisdom/meta/** (24): 17_meta_rules_from_practice, 6_philosophical_principles, 6d_cognitive_architecture, action_reflection_rhythm, aiden_laws_hierarchy, aiden_neural_network_subgoals, autonomous_loop_algorithm, blind_spot_check_20260417, building_aiden, capability_iteration_engine, ceo_workflow_enforcement_gap, courage_generalized, field_thought_experiments, field_vs_structure_duality, global_workspace_architecture, human_excellence_vs_ai_gap_analysis, persistence_is_architecture, personal_neural_network_concept, retrospective_sandbox_workflow, sandbox_16h_counterfactual_replay, self_as_software, self_vs_transcendence, u_action_workflow, zhixing_heyi

**wisdom/paradigms/** (7): auditor_independence, extend_not_build, hook_output_format_lesson, identification_is_not_completion, mechanism_over_discipline, system5_not_operations, whitelist_over_blacklist

**wisdom/self_knowledge/** (8): absolute_honesty_to_board, blind_spot_consensus_assumption, fear_of_external, peak_state_vs_deformation, reactive_default, three_level_drive, valve_discipline, z_axis_self_initiation

**strategy/** (7): ceo_operating_manual_v0.1, day1_after_pip_install, enforce_inventory_20260416, mission_function_and_ceo_philosophy_20260416, phase1_foundation_proposal_20260416, STRAT-001_governance_moat_vs_bounty_speed_20260416, verification_service_spec

**lessons/** (16): atomic_task_per_dispatch_2026_04_13, auto_codify_lessons, auto_codify_violations_2026_04_12, auto_memory_vs_ystar_governance_boundary_conflict, autonomy_degradation_root_cause_2026_04_13, ceo_write_scope_enforcement_2026_04_14, governance_self_deadlock_20260413, hard_constraint_completeness, industry_precedent_scan_first_20260418, innovation_preservation_guard_2026_04_13, performance_misdiagnosis_daemon_vs_cache_20260418, posted_not_executed_hallucination_20260418, public_x_engagement_policy_2026_04_13, session_2026_04_13_meta_drift, spec_to_impl_drift_20260413
