# Runtime Contract

This is a future contract, not executable code.

## Stage 0: Task Received

- Purpose: Capture the task and determine whether a Pre-U packet is required.
- Inputs: User instruction, agent identity, risk tier.
- Outputs: Task identifier and initial packet draft.
- Owning layer: future runtime.
- Not implemented yet: automatic task-risk classification.

## Stage 1: Read Aiden Brain Capsule References

- Purpose: Load reference pointers for Aiden identity, memory, field, CZL, CIEU, and governance.
- Inputs: `agent_brains/Aiden-CEO/` and `agent_brain_capsule/`.
- Outputs: Reference context for packet generation.
- Owning layer: labs.
- Not implemented yet: executable capsule reader.

## Stage 2: Derive / Confirm Y*

- Purpose: Make the intended target explicit before proposing action.
- Inputs: Task, Aiden ontology, memory refs, field refs.
- Outputs: `y_star` packet field.
- Owning layer: labs.
- Not implemented yet: deterministic Y* derivation.

## Stage 3: Derive m_functor / Mission Field Grounding

- Purpose: Ground the action in the Y* Field rather than local convenience.
- Inputs: Y* Field references, task, current state.
- Outputs: `m_functor` packet field.
- Owning layer: labs, later validated by Y-star-gov.
- Not implemented yet: live m_functor generator or validator.

## Stage 4: Summarize Xt

- Purpose: Establish the current state baseline before imagining action.
- Inputs: memory refs, task context, evidence refs.
- Outputs: `x_t_summary`.
- Owning layer: labs.
- Not implemented yet: evidence-bound current-state summarizer.

## Stage 5: Generate Candidate U Actions

- Purpose: Produce bounded candidate actions, not free-form fantasy.
- Inputs: Y*, m_functor, Xt, Aiden cognitive policy.
- Outputs: `candidate_actions`.
- Owning layer: labs.
- Not implemented yet: candidate generator.

## Stage 6: Predict Yt+1 and Rt+1

- Purpose: Estimate likely next state and residual for each candidate.
- Inputs: candidate actions, CZL contract, field alignment, assumptions.
- Outputs: `predicted_y_t1` and `predicted_r_t1` for each candidate.
- Owning layer: labs.
- Not implemented yet: calibrated residual predictor.

## Stage 7: Select Candidate Closest to Rt+1 = 0

- Purpose: Choose the action path expected to close the residual most cleanly.
- Inputs: candidate residual estimates, risks, assumptions, confidence.
- Outputs: `selected_action` and `residual_minimization_rationale`.
- Owning layer: labs.
- Not implemented yet: deterministic selection policy.

## Stage 8: Produce ready_for_validation Packet

- Purpose: Freeze a structured packet for future validation.
- Inputs: completed packet fields.
- Outputs: `packet_status = ready_for_validation`.
- Owning layer: labs.
- Not implemented yet: packet writer/storage path.

## Stage 9: Hook / Y-star-gov Validation

- Purpose: Validate schema, Y*, m_functor grounding, role scope, and residual logic.
- Inputs: packet, action request, governance validators.
- Outputs: allow, deny, warning, or review requirement.
- Owning layer: hook and Y-star-gov.
- Not implemented yet: packet validator and hook integration.

## Stage 10: Action Execution if Allowed

- Purpose: Execute only after governance permits the selected path.
- Inputs: validation result and selected action.
- Outputs: actual execution event.
- Owning layer: hook / future runtime.
- Not implemented yet: enforcement wiring.

## Stage 11: CIEU Post-Action Comparison

- Purpose: Compare predicted Yt+1/Rt+1 against actual outcome and residual.
- Inputs: packet, execution evidence, CIEU event.
- Outputs: prediction-error / residual-delta record.
- Owning layer: CIEU.
- Not implemented yet: actual-vs-predicted delta metric.

## Stage 12: Brain Writeback / Dream / Learning

- Purpose: Nourish Aiden's brain with validated deltas and replay-worthy lessons.
- Inputs: CIEU comparison, learning policy, dream/writeback guardrails.
- Outputs: future writeback/dream candidate.
- Owning layer: CIEU and future runtime.
- Not implemented yet: validated live wiring for this packet type.
