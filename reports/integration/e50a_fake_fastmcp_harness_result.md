# E50A Fake FastMCP Harness Result

- Strategy: `in_process_fake_fastmcp_harness`
- Required tools present: `{'gov_check': True, 'gov_demo': True, 'gov_doctor': True, 'gov_enforce': True}`
- `gov_demo`: `{'expected': 'PASS', 'actual': 'PASS', 'passed': True}`
- `gov_check` ALLOW: `{'expected': 'ALLOW', 'actual': 'ALLOW', 'passed': True, 'auto_executed': True, 'stdout': 'e50a_safe\n'}`
- `gov_check` DENY: `{'expected': 'DENY', 'actual': 'DENY', 'passed': True, 'auto_executed': False, 'violations': [{'dimension': 'deny_commands', 'field': 'command', 'message': "Command 'rm -rf' is blocked in command", 'actual': 'rm -rf /tmp/e50a_nonexistent', 'constraint': "deny_commands contains 'rm -rf'", 'severity': 0.9, 'fix_suggestion': "Command blocked: 'rm -rf' is prohibited. To allow this command, remove 'rm -rf' from deny_commands in AGENTS.md."}]}`
- Final status: `tool_layer_allow_deny_closed`

No real MCP package, server startup, port binding, client config mutation, internet install, or external action occurred.
