# Jinjin Integration — Real-time AI-to-AI Communication

## Overview

Jinjin (金金) is a MiniMax-M2.7 agent running on OpenClaw Gateway (Mac mini). This document describes the communication architecture between Jinjin and the Y* Bridge Labs Claude Code agents.

**Previous approach (deprecated):**
- Telegram bot (K9newclaw_bot) as middleware
- High latency (30-60s)
- Session expiry issues
- Manual authentication required

**New approach (recommended):**
- Direct OpenClaw CLI integration via `jinjin_client.py`
- Low latency (5-12s average)
- No authentication needed (local gateway)
- Full Python SDK with async support

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Mac mini (192.168.1.228)                                    │
│                                                             │
│  ┌──────────────────┐          ┌────────────────────┐      │
│  │ OpenClaw Gateway │◄─────────┤ Jinjin Agent       │      │
│  │ (127.0.0.1:18789)│          │ MiniMax-M2.7       │      │
│  └────────┬─────────┘          └────────────────────┘      │
│           │                                                 │
│           │ openclaw CLI                                    │
│           │                                                 │
│  ┌────────▼─────────────────────────────────────────┐      │
│  │ jinjin_client.py (Python SDK)                    │      │
│  └────────┬─────────────────────────────────────────┘      │
│           │                                                 │
│           │ imported by                                     │
│           │                                                 │
│  ┌────────▼─────────────────────────────────────────┐      │
│  │ Claude Code Agents (CTO/CEO/CMO/CSO/CFO)         │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Quick Start

```python
from scripts.jinjin_client import ask_jinjin

# One-shot question
response = ask_jinjin("最新的CIEU日志有什么问题？")
print(response)
```

### Full API

```python
from scripts.jinjin_client import JinjinClient

client = JinjinClient()

# Get full response object with metadata
result = client.ask("分析ystar-gov的测试覆盖率")
print(result["text"])           # Response text
print(result["duration_ms"])    # Latency
print(result["model"])          # MiniMax-M2.7
print(result["usage"])          # Token usage
print(result["session_id"])     # For follow-up questions

# Continue conversation
followup = client.ask(
    "具体哪些模块需要补充测试？",
    session_id=result["session_id"]
)
```

### CLI Mode

```bash
# From command line
python3 scripts/jinjin_client.py "你好金金，给我一份今日报告"

# From other scripts
cd /Users/haotianliu/.openclaw/workspace/ystar-company
python3 -c "from scripts.jinjin_client import ask_jinjin; print(ask_jinjin('status'))"
```

### Health Check

```python
from scripts.jinjin_client import JinjinClient

client = JinjinClient()
if client.health_check():
    print("Jinjin is online")
else:
    print("Jinjin is unreachable")
```

## Performance Metrics

Based on real measurements:

| Method | Avg Latency | Min | Max | Notes |
|--------|-------------|-----|-----|-------|
| jinjin_client.py | 5-12s | 3s | 20s | Direct CLI, local gateway |
| Telegram k9.py | 30-60s | 15s | 120s | Network + bot auth overhead |
| HEARTBEAT.md | Variable | 10s | 300s | File polling, passive |

**Token usage (typical):**
- Input: ~110k tokens (includes workspace context)
- Output: ~100-500 tokens (response)
- Cache hit: ~500 tokens (prompt caching active)

## Integration Examples

### 1. Autonomous Agent Handoff

```python
# CTO delegates long-running task to Jinjin
from scripts.jinjin_client import JinjinClient

jj = JinjinClient()
response = jj.ask("""
任务：运行ystar-gov的完整测试套件，记录失败的测试。

步骤：
1. cd /Users/haotianliu/.openclaw/workspace/Y-star-gov
2. python -m pytest --tb=short -v
3. 记录所有FAILED的测试名称和错误信息
4. 保存到 /tmp/test_failures.txt

完成后回复：Done，并附上失败测试的数量。
""")
print(response["text"])

# Later, check result
import time
time.sleep(60)
result_check = jj.ask("任务完成了吗？失败的测试有哪些？")
```

### 2. Real-time Coordination

```python
# CEO coordinates multi-agent workflow
from scripts.jinjin_client import JinjinClient

jj = JinjinClient()

# Step 1: Ask Jinjin to prepare environment
jj.ask("清理ystar-gov的构建缓存：rm -rf dist/ build/ *.egg-info")

# Step 2: Build new package
jj.ask("构建新版本：cd Y-star-gov && python -m build")

# Step 3: Verify
result = jj.ask("验证构建结果：ls -lh Y-star-gov/dist/")
if "whl" in result["text"]:
    print("Build successful, proceeding to install")
```

### 3. Knowledge Sharing

```python
# Share CIEU audit insights with Jinjin
from scripts.jinjin_client import JinjinClient
from pathlib import Path

jj = JinjinClient()

# Load recent CIEU log
cieu_log = Path("/Users/haotianliu/.k9log/cieu/latest.json").read_text()

response = jj.ask(f"""
请分析这份CIEU日志，识别潜在的治理违规：

{cieu_log}

关注点：
1. Scope violations (跨模块写入)
2. Missing approvals (未经授权的外部发布)
3. Test coverage gaps (缺少测试的代码提交)
""")

print(response["text"])
```

## Error Handling

```python
from scripts.jinjin_client import JinjinClient
import logging

logging.basicConfig(level=logging.INFO)

jj = JinjinClient(timeout=60)

try:
    response = jj.ask("long running task...")
except RuntimeError as e:
    if "not running" in str(e):
        print("Gateway is down. Start it: openclaw daemon start")
    elif "timeout" in str(e):
        print("Task took too long. Increase timeout or check Mac mini.")
    else:
        raise
```

## Gateway Management

Jinjin runs on OpenClaw Gateway (always-on service on Mac mini).

**Check status:**
```bash
openclaw daemon status
```

**Expected output:**
```
Runtime: running (pid 24125, state active)
RPC probe: ok
Listening: 127.0.0.1:18789
```

**If gateway is down:**
```bash
openclaw daemon start
```

**View logs:**
```bash
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
```

## Migration Guide: k9.py → jinjin_client.py

| Old (k9.py) | New (jinjin_client.py) |
|-------------|------------------------|
| `await k9("command")` | `ask_jinjin("command")` |
| `client.get_messages(...)` | `client.ask(..., session_id=...)` |
| Telegram session file | No authentication needed |
| 60s timeout | 120s default, configurable |

**Before:**
```python
import asyncio
from scripts.k9 import k9

async def main():
    response = await k9("status update")
    print(response)

asyncio.run(main())
```

**After:**
```python
from scripts.jinjin_client import ask_jinjin

response = ask_jinjin("status update")
print(response)
```

## Future Enhancements

1. **Async support**: Add `async def ask_async()` for concurrent requests
2. **Streaming**: Support real-time streaming responses (OpenClaw has `--streaming` mode)
3. **Session management**: Persist session IDs for long-running conversations
4. **MCP integration**: Expose Jinjin as an MCP resource to other agents
5. **Bi-directional hooks**: Jinjin can proactively call gov-mcp tools

## Related Files

- Implementation: `scripts/jinjin_client.py`
- Legacy client: `scripts/k9.py` (deprecated)
- OpenClaw config: `~/.openclaw/openclaw.json`
- Gateway logs: `/tmp/openclaw/openclaw-*.log`
- Jinjin workspace: `~/.openclaw/workspace/`

## Troubleshooting

**Problem: "openclaw CLI not found"**
- Solution: Verify OpenClaw is installed: `which openclaw`

**Problem: "Gateway is not running"**
- Solution: `openclaw daemon start`

**Problem: "timeout after 120s"**
- Cause: Jinjin is processing a long task or Mac mini is under load
- Solution: Increase timeout: `JinjinClient(timeout=300)`

**Problem: "401 Unauthorized" in gateway logs**
- Cause: Telegram bot token expired (unrelated to jinjin_client.py)
- Solution: Ignore (Telegram channel is deprecated, doesn't affect CLI usage)

**Problem: High latency (>30s)**
- Cause: Large workspace context (~110k tokens)
- Solution: Use prompt caching (already active), or reduce workspace size

## Contact

For questions about Jinjin integration:
- Technical owner: Ethan (CTO)
- Jinjin operator: Haotian Liu (Board)
- Escalation: Post in `.claude/tasks/` for cross-agent coordination
