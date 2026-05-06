# E50A gov-mcp Tool Registration Inspection

- `gov_check`, `gov_demo`, `gov_doctor`, and `gov_enforce` are nested FastMCP registrations inside `create_server(...)`.
- Direct `gov_mcp.server` import without fake MCP fails on missing module `mcp`.
- Fake FastMCP registration capture: `True`.
- Captured tool count: `70`.
- Minimum safe path: `inject fake mcp.server.fastmcp.FastMCP -> import gov_mcp.server -> create_server(session_config_path=scratch) -> call captured gov_check/gov_demo functions`.

No external action occurred.
