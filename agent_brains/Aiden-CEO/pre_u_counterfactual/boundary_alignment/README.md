# Pre-U Counterfactual Boundary Alignment

This directory aligns Aiden's Pre-U Counterfactual Packet with labs,
Y-star-gov, hook, CIEU, and brain responsibilities.

It is documentation/reference only. It does not implement validation, hook
behavior, CIEU events, DB writes, or runtime brain learning.

The alignment exists to prevent architectural drift:

- Labs should not become the judge.
- Y-star-gov should not become a subjective brain.
- Hook should not become a reasoning engine.
- CIEU should not remain passive audit only.
- Brain should learn from evidence-backed deltas, not unaudited fantasy.

Core principle:

- Labs thinks.
- Y-star-gov judges.
- Hook enforces.
- CIEU records and teaches.
- Brain learns.

This layer prepares a later implementation path where Aiden generates a
structured Pre-U packet, Y-star-gov validates it, hook gates risky action, CIEU
records predicted-vs-actual outcome, and Aiden's brain learns from the resulting
delta.
