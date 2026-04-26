# CZL Runtime Contract

This file converts the existing CZL definition into runtime-facing contract language. It does not change CZL.

Canonical reference: `/Users/haotianliu/.openclaw/workspace/ystar-company/CZL.md`

## Contract

Every runtime task should expose:

- `Y*`: the human-defined target or completion standard.
- `Xt`: the measured current state before action.
- `U`: the action or action sequence taken.
- `Yt+1`: the measured state after action.
- `Rt+1`: the residual distance between `Yt+1` and `Y*`.

## Closure

- `Rt+1 = 0`: the loop is closed.
- `Rt+1 != 0`: the residual remains open.

## Residual-open handling

When residual remains open, the runtime-facing options are:

- retry with a revised `U`;
- delegate to the correct agent/function;
- escalate to the correct authority;
- revise the target if `Y*` was invalid or underspecified;
- record the gap as evidence for future learning.

Amendment 014 extends this into ResidualLoopEngine design: CIEU should not merely record residuals; residuals can drive the next action loop. Current live implementation status is not asserted here.
