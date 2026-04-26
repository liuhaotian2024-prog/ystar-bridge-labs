# Future Validation Contract

This file defines what a future Y-star-gov packet validator should check. It is
not validator code.

| Category | Validation question | Check type | Y-star-gov responsibility | Labs responsibility | Hook responsibility | Failure action |
| --- | --- | --- | --- | --- | --- | --- |
| Schema validity | Does the packet conform to `packet_schema.json`? | Deterministic | Validate JSON shape and required fields. | Produce conforming packet. | Call validator before action when required. | deny |
| agent_id validity | Is `agent_id` valid and scoped to `Aiden-CEO` for this capsule? | Deterministic | Validate agent identity against registry/scope. | Use correct agent id. | Deny if validator rejects identity. | deny |
| task_id presence | Is `task_id` present and non-empty? | Deterministic | Require traceable task id. | Provide task id. | Deny or require revision if missing. | require_revision |
| Y* presence and grounding | Is Y* declared and grounded in evidence or task context? | Future semantic check | Validate presence and grounding rules. | Derive/confirm Y*. | Enforce validator result. | require_revision |
| m_functor presence and grounding | Is m_functor declared and tied to field refs? | Future semantic check | Validate field grounding and deterministic constraints. | Provide m_functor notes and refs. | Enforce validator result. | require_revision |
| Xt summary presence | Is current state summarized without claiming unknown facts? | Future semantic check | Check required presence and evidence discipline. | Summarize current state. | Enforce validator result. | warn |
| candidate_actions presence | Are candidate actions present and bounded? | Deterministic plus future semantic check | Ensure array and minimum count. | Generate bounded candidates. | Deny high-risk action if absent. | deny |
| selected_action reference | Does selected action reference an existing candidate id? | Deterministic | Validate referential integrity. | Select from candidates only. | Deny invalid packet. | deny |
| predicted Rt+1 per candidate | Does every candidate include predicted residual? | Deterministic | Validate required residual field. | Estimate predicted residual for each candidate. | Deny high-risk action if missing. | deny |
| residual minimization rationale | Does rationale explain why selected path is closest to Rt+1 = 0? | Future semantic check | Validate required rationale and residual logic. | Explain selection. | Require revision if insufficient. | require_revision |
| risk/high-risk review fields | Are governance expectation fields present? | Deterministic | Validate risk/review fields. | Set expectations honestly. | Escalate based on risk tier. | escalate |
| packet_status validity | Is packet status one of the allowed states? | Deterministic | Validate enum. | Mark status accurately. | Only act on acceptable status. | deny |
| no actual result before action | Does packet avoid claiming actual post-action outcome before action? | Future semantic check | Reject future-tense prediction masquerading as fact. | Keep prediction distinct from evidence. | Deny or require revision. | require_revision |
| no embedded DB/log/runtime mutation | Does packet avoid embedding mutation of DB/log/runtime state? | Future semantic check | Detect forbidden embedded mutation intent. | Keep packet descriptive. | Deny Tier 4 unsafe action unless explicitly authorized. | deny |
| no unbounded fantasy | Are predictions structured and evidence-linked rather than free-form fantasy? | Future semantic check | Enforce structured prediction discipline. | Provide evidence refs, assumptions, confidence. | Require revision if too vague. | require_revision |

Future validator output should be explicit enough for hook to decide:
`allow_with_note`, `warn`, `require_revision`, `escalate`, or `deny`.
