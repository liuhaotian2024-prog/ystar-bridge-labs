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
