# Repository Delivery Bridge Jobs

This directory documents the host-local repository delivery bridge contract. Runtime jobs live under `/tmp/ystar_delivery_bridge/`:

- `/tmp/ystar_delivery_bridge/pending/`
- `/tmp/ystar_delivery_bridge/running/`
- `/tmp/ystar_delivery_bridge/completed/`
- `/tmp/ystar_delivery_bridge/failed/`
- `/tmp/ystar_delivery_bridge/logs/`

Codex submits structured, allowlisted jobs with `scripts/repository_delivery_bridge_submit.py`. The host-local worker validates the job, installs the payload, runs tests, commits only allowed files, pushes, and confirms the remote SHA.

This replaces per-milestone owner bootstrap commands. The owner may need a one-time installation command to register the LaunchAgent, but future milestone delivery should submit bridge jobs instead of asking the owner to run another delivery script.

