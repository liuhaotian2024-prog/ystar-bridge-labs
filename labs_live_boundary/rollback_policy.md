# Rollback And Abort Policy

Status: defined disabled.

Any future minimal live loop must define:

- an abort path before action execution,
- rollback expectations before filesystem mutation,
- failure reporting before CIEU event recording,
- operator-visible stop conditions,
- evidence needed before any later learning or writeback.

This policy does not execute rollback logic. It only defines the missing gate.
