# Scheduler Disabled Policy

The manual tick runner must never start or enable a scheduler, daemon, recurrence loop, or auto-run process.

If a request asks for recurrence, scheduler use, daemon use, auto-run, live action, external action, persistence, or writeback, the runner must fail closed before observation.

