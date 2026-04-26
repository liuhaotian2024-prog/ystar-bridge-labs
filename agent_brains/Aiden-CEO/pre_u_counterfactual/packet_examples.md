# Packet Examples

These examples are illustrative only. They are not executable runtime packets and
do not include commands that mutate DBs, logs, scripts, hooks, or governance code.

## Example A: Low-Risk Documentation / Index Update

**Y***: Aiden's reference capsule clearly points future readers to the correct
memory and governance references without changing runtime behavior.

**Xt**: A documentation index is incomplete or missing a reference to an
already-existing artifact.

**Candidate U options**

- `U-A1`: Add a small reference-only index entry.
- `U-A2`: Rewrite the whole documentation section.
- `U-A3`: Do nothing and leave the gap for a later pass.

**Predicted Yt+1**

- `U-A1`: Future readers have the missing pointer with minimal churn.
- `U-A2`: Future readers may get more context, but unrelated text changes could
  blur evidence boundaries.
- `U-A3`: The missing pointer remains open.

**Predicted Rt+1**

- `U-A1`: Low residual because the specific gap is closed with little risk.
- `U-A2`: Medium residual because the change may introduce review noise.
- `U-A3`: High residual because the known gap remains.

**Selected U**: `U-A1`.

**Why selected**: It is the closest path to `Rt+1 = 0` while preserving the
reference-only boundary.

**Expected hook / Y-star-gov review**: Likely low-risk documentation review.
Future validators may check role scope, path locality, and whether the packet
exists for the action.

**CIEU comparison later**: Compare predicted outcome "gap closed with minimal
churn" against actual review result, residual comments, and any follow-up fixes.

## Example B: High-Risk Runtime / Script / DB-Adjacent Action

**Y***: Improve Aiden brain writeback reliability without corrupting runtime
state or bypassing governance.

**Xt**: A live wiring gap is suspected around L2 writeback, but DB contents and
runtime scripts have not been inspected in this reference pass.

**Candidate U options**

- `U-B1`: Create a read-only design packet describing the validation needed.
- `U-B2`: Directly run a writeback or scheduler script to observe behavior.
- `U-B3`: Edit a hook or runtime script to force writeback.

**Predicted Yt+1**

- `U-B1`: The next implementation pass has a safe validation plan and explicit
  unknowns.
- `U-B2`: Runtime behavior may be observed, but DB/log/runtime mutation risk is
  introduced.
- `U-B3`: Live semantics may change before the architecture is validated.

**Predicted Rt+1**

- `U-B1`: Lowest residual for an architecture-planning milestone because it
  advances clarity without crossing the runtime boundary.
- `U-B2`: High residual because the action may create unreviewed runtime state.
- `U-B3`: Very high residual because it changes enforcement/writeback behavior
  without prior validation.

**Selected U**: `U-B1`.

**Why selected**: It minimizes residual while respecting the boundary that labs
thinks, Y-star-gov judges, hooks enforce, and CIEU teaches.

**Expected hook / Y-star-gov review**: Future hook policy should require packet
validation for DB-adjacent or runtime-script actions. Y-star-gov should validate
schema, Y*, m_functor grounding, role scope, and residual logic before allowing
execution.

**CIEU comparison later**: After a future validated run, CIEU should compare the
predicted safety outcome against actual events, residuals, and any error or
intervention signals, then feed that delta into brain learning/writeback.
