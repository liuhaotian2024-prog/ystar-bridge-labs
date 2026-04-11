# Y* Bridge Labs — Agent Communication Architecture

## Overview

Y* Bridge Labs operates a hybrid multi-agent system with agents running on different platforms and models. This document describes the communication channels and protocols.

## Agent Roster

| Agent | Role | Platform | Model | Location |
|-------|------|----------|-------|----------|
| Aiden (CEO) | Chief Executive | Claude Code | Sonnet 4.5 | Windows/Mac |
| Ethan (CTO) | Engineering Lead | Claude Code | Sonnet 4.5 | Mac |
| Marco (CMO) | Marketing | Claude Code | Sonnet 4.5 | Mac |
| Zara (CSO) | Sales/Strategy | Claude Code | Sonnet 4.5 | Mac |
| Sofia (CFO) | Finance | Claude Code | Sonnet 4.5 | Mac |
| Jinjin (金金) | Research/Ops | OpenClaw Gateway | MiniMax-M2.7 | Mac mini 24/7 |

## Communication Channels

### 1. Direct CLI (Recommended)

**Use case:** Claude Code agents ↔ Jinjin

**Implementation:** `scripts/jinjin_client.py`

**Characteristics:**
- Latency: 5-12s average
- No authentication needed
- Full conversation history support
- JSON response with metadata

**Example:**
```python
from scripts.jinjin_client import ask_jinjin
response = ask_jinjin("检查ystar-gov的测试状态")
```

**When to use:**
- Real-time coordination
- Task delegation
- Status queries
- CIEU log analysis

---

### 2. Shared Workspace Files

**Use case:** Async task handoff, persistent records

**Implementation:** `.claude/tasks/`, `reports/`, `memory/session_handoff.md`

**Characteristics:**
- Latency: Variable (polling-based)
- Persistent across sessions
- Board-visible audit trail
- Supports batch operations

**Example:**
```bash
# Aiden creates task for CTO
echo "Fix installation bugs" > .claude/tasks/cto_urgent.md

# CTO reads and deletes after completion
cat .claude/tasks/cto_urgent.md
rm .claude/tasks/cto_urgent.md
```

**When to use:**
- Cross-session task assignment
- Non-urgent coordination
- Board-approved directives
- Autonomous work planning

---

### 3. Telegram Bot (Legacy, Deprecated)

**Use case:** External human ↔ Jinjin

**Implementation:** `scripts/k9.py` (deprecated, use jinjin_client.py instead)

**Characteristics:**
- Latency: 30-60s
- Session expiry issues
- Requires manual authentication
- Network-dependent

**Status:** Deprecated in favor of jinjin_client.py

---

### 4. HEARTBEAT.md (Legacy, Deprecated)

**Use case:** CEO ↔ Jinjin async communication

**Implementation:** `~/.openclaw/workspace/HEARTBEAT.md`

**Characteristics:**
- Latency: Variable (polling-based)
- One-way communication
- No structured response format
- Manually monitored

**Status:** Replaced by jinjin_client.py for real-time queries

---

### 5. MCP (Gov-MCP Server)

**Use case:** Governance enforcement and audit queries

**Implementation:** `gov_mcp` server on port 7922

**Characteristics:**
- Latency: <1s (local RPC)
- Structured tool interface
- Real-time governance checks
- Available to all agents

**Available tools:**
- `gov_check` - policy compliance check
- `gov_audit` - CIEU log analysis
- `gov_delegate` - delegate task with governance
- `gov_escalate` - escalate violation
- ... (40+ tools)

**Example:**
```python
# Via MCP tool call
result = mcp_gov_check(
    operation="file_write",
    target="ystar/kernel/core.py",
    agent="eng-kernel"
)
```

**When to use:**
- Pre-commit governance checks
- CIEU log queries
- Policy validation
- Delegation with accountability

---

## Communication Patterns

### Pattern 1: Synchronous Request-Response

```
Aiden (CEO) → jinjin_client.py → Jinjin
                              ← Response (5-12s)
```

**Use case:** Quick status queries, real-time coordination

**Example:**
```python
status = ask_jinjin("Mac mini的磁盘空间还有多少？")
```

---

### Pattern 2: Async Task Queue

```
Aiden → .claude/tasks/cto_task.md → (CTO reads on next session boot)
CTO → processes task → deletes task file → reports in reports/autonomous/
```

**Use case:** Non-blocking work assignment, session-independent tasks

---

### Pattern 3: Governance Check (Pre-operation)

```
CTO → gov_check(operation, target) → Gov-MCP
                                  ← ALLOW/DENY + reasoning
CTO → if ALLOW: execute operation
      if DENY: escalate or abort
```

**Use case:** Compliance verification before risky operations

---

### Pattern 4: CIEU Audit (Post-operation)

```
Any agent → executes operation → CIEU log written
Board/CEO → gov_audit(time_range) → Gov-MCP
                                  ← Audit report with violations
```

**Use case:** Retrospective analysis, violation detection

---

### Pattern 5: Cross-Agent Collaboration

```
CEO → jinjin_client.ask("扫描AI治理领域的最新论文（arxiv）")
Jinjin → executes web search → returns TOP 10 papers
CEO → summarizes → writes to reports/research/
CEO → notifies CSO via .claude/tasks/cso_intel.md
```

**Use case:** Research delegation, multi-step workflows

---

## Latency Comparison

| Channel | Avg Latency | Reliability | Auth Required | Structured Output |
|---------|-------------|-------------|---------------|-------------------|
| jinjin_client.py | 5-12s | High | No | Yes (JSON) |
| Gov-MCP | <1s | Very High | No | Yes (JSON) |
| .claude/tasks/ | Variable | High | No | No |
| Telegram k9.py | 30-60s | Medium | Yes | No |
| HEARTBEAT.md | Variable | Low | No | No |

---

## Best Practices

### 1. Choose the Right Channel

- **Urgent + Real-time** → jinjin_client.py or Gov-MCP
- **Non-urgent + Persistent** → .claude/tasks/
- **Governance check** → Gov-MCP (always)
- **Research/web tasks** → Delegate to Jinjin via jinjin_client.py

### 2. Session Management

For multi-turn conversations with Jinjin:
```python
client = JinjinClient()
q1 = client.ask("请列出Y*gov的所有模块")
session_id = q1["session_id"]

q2 = client.ask("哪个模块最复杂？", session_id=session_id)
```

### 3. Error Handling

Always wrap external communication in try-except:
```python
try:
    response = ask_jinjin("task")
except RuntimeError as e:
    # Gateway down or timeout
    # Fallback: write to .claude/tasks/ for manual handling
    Path(".claude/tasks/jinjin_fallback.md").write_text(f"Task: {task}")
```

### 4. Governance First

Before any risky operation:
```python
# 1. Check policy
check_result = mcp_gov_check(operation="git_push", target="main")

# 2. If DENY, escalate
if check_result["decision"] == "DENY":
    mcp_gov_escalate(
        operation="git_push",
        reason=check_result["reasoning"],
        request_override=False
    )
    return

# 3. If ALLOW, proceed
git_push()
```

---

## Migration Checklist

If you're migrating from old communication methods:

- [ ] Replace `k9.py` calls with `jinjin_client.py`
- [ ] Replace manual HEARTBEAT.md polling with real-time `ask_jinjin()`
- [ ] Add Gov-MCP checks before risky operations
- [ ] Use `.claude/tasks/` only for session-independent work
- [ ] Document all cross-agent workflows in this file

---

## Troubleshooting

### "Jinjin not responding"

1. Check gateway: `openclaw daemon status`
2. If down: `openclaw daemon start`
3. Check logs: `tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log`

### "Gov-MCP connection failed"

1. Check MCP server: `ps aux | grep gov_mcp`
2. Expected: process on port 7922
3. If down: start manually or check `.ystar_session.json`

### "High latency with jinjin_client.py"

1. Check Mac mini load: `ask_jinjin("系统负载是多少？top -l 1")`
2. Check workspace size (large context = slow inference)
3. Consider using Gov-MCP for structured queries instead

---

## Related Documentation

- Jinjin integration: `docs/JINJIN_INTEGRATION.md`
- Gov-MCP tools: `gov_mcp --help`
- Task management: `memory/session_handoff.md`
- AGENTS.md: Governance contract

---

## Future Enhancements

1. **WebSocket streaming** — Real-time token streaming from Jinjin
2. **MCP bidirectional** — Jinjin can call gov-mcp proactively
3. **Unified message bus** — All agents publish/subscribe to event stream
4. **CIEU auto-analysis** — Gov-MCP triggers alerts on violations
5. **Agent-to-agent MCP** — Direct MCP calls between Claude Code agents
