# Mission Field Runtime

The Mission Field runtime view is derived from `Y_STAR_FIELD_THEORY_SPEC.md` and `y_star_field_validator.py`.

## Existing concepts

- `M_space`: mission space, with axes such as `M-1`, `M-2a`, `M-2b`, and `M-3`.
- `Φ_t`: mission functor mapping mission space into local task `Y*`.
- local `Y*`: task-level target used in CZL.
- `m_functor`: explicit tag linking local `Y*` back to mission axes.
- `ξ`: Y* field assigning local target direction to a state.
- `R_{t+1}`: residual distance between actual outcome and local `Y*`.

## Runtime role

The runtime-facing role of the field is to make mission alignment explicit before or during action:

1. Operations writes or carries `Y*` and `m_functor`.
2. Governance validates formal structure deterministically.
3. CZL measures whether action closes the residual.
4. CIEU records evidence and can later nourish brain updates.

## Deterministic validation

`Y_STAR_FIELD_THEORY_SPEC.md` Section 11 corrects an earlier hybrid-validator idea. The binding recovered principle is:

- Governance should not use an LLM judge to judge LLM behavior.
- Governance validates formal behavior with symbolic/deterministic checks.
- Operations/cognition remains responsible for actually achieving `Y*`.

`y_star_field_validator.py` reflects this direction by checking `m_functor` against a whitelist and deterministic keyword grounding. It also names the Goodhart risk: an agent may tag a perfect-looking `m_functor` while the task content does not support that axis.

## Relation to CZL

CZL closes local task residuals. Mission Field ensures the local `Y*` is not arbitrary: it should be traceable to mission space through `m_functor`.

No new field theory is introduced here.
