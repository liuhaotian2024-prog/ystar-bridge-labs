# Host-Local Delivery Bridge Install

- status: pending_one_time_install
- one_time_setup_required: true
- future_owner_delivery_commands_required: true
- repository_delivery_rt1: 1
- bridge_root: `/tmp/ystar_delivery_bridge`
- launch_agent_label: `com.ystar.repository-delivery-bridge`
- credentials_printed: false

This remains pending until the one-time installer completes self-delivery, push, remote SHA confirmation, and LaunchAgent activation. Once installed, Codex can submit structured allowlisted delivery jobs to the bridge root and the host-local worker performs validation, tests, commit, push, and remote SHA confirmation.
