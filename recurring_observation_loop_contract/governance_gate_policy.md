# Governance Gate Policy

Every future recurring observation tick must pass a governance gate before any observation step.

For L4.8, the only allowed decision is `allow_manual_local_simulated_tick`. This permits one deterministic local simulation from generated/read-model sources only. It does not permit recurrence, scheduler use, daemon use, live action, external action, persistence, or writeback.

If a tick requests unsafe sources, external access, live action, persistence, or scheduler/daemon activation, it must fail closed and require operator review.

