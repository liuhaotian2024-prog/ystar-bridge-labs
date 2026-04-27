# Labs-Gov Alignment Bridge

This bridge is the first dry-run alignment layer between ystar-company labs
read models and the independent Y-star-gov governance endpoint.

The bridge converts a curated labs sample task into a Y-star-gov-compatible
hook-like envelope, calls the Y-star-gov hook contract dry-run CLI, and records
the returned decision as a labs-side snapshot.

It is intentionally narrow:

- no real hook integration
- no action execution
- no CIEU write
- no brain or memory mutation
- no dirty runtime artifact reads
- no candidate approval or semantic truth scoring

Generated bridge outputs are read-model artifacts only. They are safe for the
team console to display as dry-run governance alignment status.

`pre_u_generator/` generalizes the sample bridge into multi-role Pre-U packet
generation for Aiden-CEO, Ethan-CTO, and Samantha-Secretary. It creates dry-run
packets, converts them to hook envelopes, calls the same Y-star-gov dry-run CLI,
and records decision snapshots without executing actions.

`labs_runtime_acceptance/` is the labs-side acceptance pack that proves the
current quarantine, safe-mining, review, disposition, evidence, Pre-U, bridge,
console, and local-check stack in dry-run mode only.

`cross_repo_alignment/` pairs the labs acceptance result with Y-star-gov
endpoint acceptance and records a deterministic dry-run compatibility manifest.

`labs_live_readiness/` turns the current dry-run bridge, acceptance, and
alignment artifacts into a live-readiness report. That report is intentionally
blocking: it identifies the smallest future live-loop path without enabling
execution, CIEU writes, memory ingestion, or brain writeback.
