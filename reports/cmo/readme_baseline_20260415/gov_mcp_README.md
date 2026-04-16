# Baseline: gov-mcp README.md (2026-04-15)

**Captured from:** `/Users/haotianliu/.openclaw/workspace/gov-mcp/README.md`

---

[Full content archived - see Read tool result in CIEU audit trail]

## Structure Analysis
- **Opening statement**: "Governed execution for any AI agent framework. Install in 30 seconds."
- **Install snippet**: 2 commands at the top (`pip install gov-mcp && gov-mcp install`)
- **Why**: Single paragraph pain point (prompt injection → rm -rf / .env leak / privilege escalation)
- **Performance (EXP-008)**: 4-metric table (output tokens -45.1%, wall time -61.5%, throughput, concurrent agents)
- **Security**: SIM-001 tested (50 agents, 1000 checks, zero leaks)
- **Compliance**: FINRA / EU AI Act Article 14 compatibility
- **Limitations (Honest Assessment)**: 6 items with "Implemented" / "Not yet available" / "Roadmap"
- **Quick Start**: 5 steps (install → write contract → `gov-mcp install` → management commands → manual setup alternative)
- **Tools (38)**: 7 category tables (Core Enforcement, Delegation, Contract Management, Audit, Governance Analysis, UX, Domain)
- **How It Works**: ASCII flow diagram with inline execution branches
- **Auto-Execution**: Explanation of deterministic command inline execution (saves 22% tokens)
- **Governance Extension Layer**: JSON envelope schema + 5-field table
- **A2A Integration (Coming Soon)**: 3-phase roadmap (GOV MCP → GOV A2A → Gov Pipeline)
- **License**: MIT

## Key Patterns
- **Install-first**: 2-command snippet at line 6-7 (before "Why" section)
- **Honest limitations**: "Limitations (Honest Assessment)" section lists what's NOT ready
- **Performance quantified**: EXP-008 table with negative deltas (% improvement)
- **Tool catalog**: 38 tools in 7 categories with one-line descriptions
- **Auto-execution USP**: 22% token savings, 66.7% of Bash commands auto-executed
- **Governance extension**: Backward-compatible audit envelope riding on MCP protocol
- **Management commands**: `status / restart / uninstall` for lifecycle
- **A2A roadmap**: 3-phase timeline with Q3/Q4 dates
- **No "Getting Started" narrative**: Jumps straight to CLI commands
