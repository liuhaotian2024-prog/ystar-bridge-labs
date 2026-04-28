# Stop And Abort Policy

The recurring loop must stop or abort whenever a tick violates source, governance, execution, persistence, or size boundaries.

Stop/abort handling is conservative: fail closed, emit a generated finding if safe, and require operator review before any future enablement.

