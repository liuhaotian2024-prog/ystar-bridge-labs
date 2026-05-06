# E48 Real-Code Interface Discovery

- Selected strategy: `in_process_ystar_kernel_proof_with_server_transport_blocker`
- Reason: Y-star-gov kernel demo works and gov-mcp exposes gov_check/gov_demo, but the local gov-mcp server import is blocked by missing mcp dependency or client path; no internet install is allowed.
- gov-mcp CLI commands: install, uninstall, status, restart
- Proof tools present: {"gov_check": true, "gov_demo": true, "gov_doctor": true, "gov_enforce": true}
- Install side effects: {"detects_local_mcp_ecosystems": true, "may_bind_localhost_port": true, "may_call_claude_mcp_add": true, "starts_background_server": true, "writes_pid_log_port_agents_state": false}
- Server import return code: 1
- Y-star demo return code: 0

E48 does not run `gov-mcp install` because current code may start a server and mutate real client config.
