# Responsibility Matrix

| Layer | Owns | Must not own | Input | Output | Future implementation location |
| --- | --- | --- | --- | --- | --- |
| ystar-company / labs | Packet generation, candidate-action imagination, residual-minimization rationale, Aiden-side cognitive context. | Deterministic governance judgment, hook enforcement, DB mutation by packet docs. | Task, Aiden capsule refs, memory refs, field refs, CZL refs. | Draft or ready-for-validation Pre-U packet. | `ystar-company` future labs runtime. |
| Aiden Brain Capsule | Aiden-specific ontology, DNA, memory refs, field refs, CZL refs, CIEU nutrition refs, lifecycle refs. | Runtime enforcement, kernel validation, DB content migration. | Existing indexes and referenced artifacts. | Per-agent read model for Aiden. | `agent_brains/Aiden-CEO/`. |
| Pre-U Counterfactual Packet | Structured action imagination before U: candidate U options, predicted Yt+1, predicted Rt+1, selected path. | Free-form fantasy, post-action truth claims, direct execution. | Aiden capsule context, task Y*, Xt, m_functor grounding. | Packet for future validation. | `agent_brains/Aiden-CEO/pre_u_counterfactual/`. |
| Y-star-gov | Deterministic validation, governance law, schema checks, role scope, CZL/CIEU semantics, m_functor validation. | Subjective brain cognition or candidate-action imagination. | Packet, requested action, governance rules, kernel validators. | Validation decision or revision/escalation signal. | Future Y-star-gov validator; external to this repo. |
| hook layer | Thin pre-action gate, packet existence check for risk-tiered actions, call to Y-star-gov validator, allow/deny/escalate. | Complex reasoning, counterfactual generation, DB content inspection. | Action request, risk tier, packet ref, validator result. | Gate decision and pre-action CIEU link. | Future hook integration, likely kernel/adapter side. |
| CIEU | Post-action evidence, actual Yt+1/Rt+1 recording, predicted-vs-actual comparison, learning signal. | Unaudited speculation as fact, brain update without outcome evidence. | Packet id, selected prediction, actual event/outcome evidence. | Residual delta and prediction-error evidence. | Future CIEU event/store integration. |
| Brain writeback / dream | Learn from packet plus actual outcome plus CIEU delta; replay patterns and failures. | Learning directly from speculative packet alone. | CIEU deltas, writeback policy, dream guardrails. | Brain nutrition/writeback candidates. | Future L2/L3 brain lifecycle wiring. |
| Console read model | Display packet status, boundary status, residual deltas, and learning readiness. | Raw DB/log mutation or runtime enforcement. | Capsule indexes, packet metadata, CIEU summaries. | Human-readable operational view. | Future `console_read_model/` or app layer. |

Minimum boundary rule: labs generates the packet, Y-star-gov validates it, hook
gates action, CIEU records outcome, and brain learns only from evidence-backed
deltas.
