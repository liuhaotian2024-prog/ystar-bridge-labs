# Runtime Layers

These layers are a runtime-facing view of existing artifacts.

## DNA Layer

- Purpose: preserve identity, Board relationship, first principles, and team DNA.
- Input: ontology docs, team memory, boot references.
- Output: stable identity context for boot and decision framing.
- Canonical references: `AIDEN_ONTOLOGY.md`; adjacent reference `team_dna.md`.
- Not responsible for: live governance enforcement, DB mutation, or task completion scoring.

## Cognitive Substrate Layer

- Purpose: provide the 6D brain coordinate space and node/edge activation substrate.
- Input: CIEU rows, memory/report/knowledge nodes, event projections.
- Output: activations, nearest-node context, Hebbian co-firing edges.
- Canonical references: `cieu_brain_bridge.py`.
- Not responsible for: deciding whether mission alignment is valid or whether residual is closed.

## Thinking / Cognitive Policy Layer

- Purpose: connect Aiden’s counterfactual operating style with the L1/L2/L3 brain loop.
- Input: Board prompts, current context, brain top-k, prior ontology.
- Output: cognitive context for action and learning signals after action.
- Canonical references: `AIDEN_ONTOLOGY.md`, `brain_3loop_consolidated_v2.md`, `CZL-BRAIN-3LOOP-FINAL-ruling.md`.
- Not responsible for: inventing new goals or overriding CZL.

## Mission Field Layer

- Purpose: make local `Y*` traceable to mission axes through `m_functor`.
- Input: task description, `Y*`, `m_functor`, mission axis vocabulary.
- Output: deterministic validation result and field-state references.
- Canonical references: `Y_STAR_FIELD_THEORY_SPEC.md`, `y_star_field_validator.py`.
- Not responsible for: judging content quality with LLMs or replacing operations.

## CZL Runtime Contract Layer

- Purpose: require every task to expose target, current state, action, observed result, and residual.
- Input: task target and execution evidence.
- Output: closed residual (`Rt+1 = 0`) or open residual requiring action.
- Canonical references: `CZL.md`, `charter_amendment_014_closed_loop_cieu_residual_engine.md`.
- Not responsible for: creating the mission field or modifying brain DBs.

## CIEU Nutrition Layer

- Purpose: turn CIEU from evidence into brain nutrition without losing audit meaning.
- Input: CIEU log events, decisions, outcomes, violations, residuals.
- Output: event projections, activations, learning batches, dream replay inputs.
- Canonical references: `CZL-BRAIN-BIPARTITE-ruling.md`, `CZL-BRAIN-BIPARTITE-P2-ALGO-ruling.md`, `cieu_brain_streamer.py`, `cieu_brain_learning.py`.
- Not responsible for: raw DB migration in this capsule.

## Brain Lifecycle Layer

- Purpose: define how brain state is read, written back, and consolidated over time.
- Input: boot memory, prompts, tool events, post-action outcomes, activation history.
- Output: L1 pre-query context, L2 writeback, L3 dream proposals, guardrail decisions.
- Canonical references: `CZL-BRAIN-3LOOP-FINAL-ruling.md`, `brain_auto_ingest.py`, `brain_dream_scheduler.py`, `CZL-BRAIN-L3-GUARD-RAILS-ruling.md`.
- Not responsible for: silently applying dream changes without review/guardrails.

## Governance Boundary Layer

- Purpose: keep deterministic governance separate from cognitive/operational achievement.
- Input: structured action, role identity, session state, `m_functor`, rules.
- Output: allow/warn/deny/recipe/evidence events.
- Canonical references: `GOVERNANCE-DUAL-ASPECT-AND-INSIGHT-RULE-PIPELINE-20260420.md`, `Y_STAR_FIELD_THEORY_SPEC.md` Section 11, Y-star-gov boundary/runtime modules.
- Not responsible for: LLM-judged semantic quality or replacing agent cognition.
