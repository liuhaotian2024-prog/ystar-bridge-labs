# Scheduler Disabled Policy

L4.7 does not install or activate a recurring process.

The refresh loop is intentionally manual and local-only. A future milestone may define a governed recurring observation contract, but this pack only proves that a deterministic refresh can be run safely from generated/read-model evidence.

Required disabled states:

- `scheduler_enabled: false`
- `daemon_enabled: false`
- `recurring_auto_run_enabled: false`
- `manual_local_run_only: true`

