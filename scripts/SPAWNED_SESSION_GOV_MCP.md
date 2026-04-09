# Spawned Claude Code Session — Y*gov Governance Connection
# 创建日期：2026-04-09 · GOV-005 daemon architecture decision (Board: 退役c, 安装a)
# 验证日期：2026-04-09 · End-to-end smoke test passed (commit will reference)

---

## ⚠️ Schema 易错点(2026-04-09 验证发现)

`scripts/spawned_mcp_config.json` 用的是 **Claude Code 的 mcpServers config 格式**,字段是 **`type`**,**不是** gov-mcp README 里 MCP 协议 wire format 用的 `transport`。两者是不同 layer:

- **gov-mcp README**(MCP 协议 wire format):`{"transport": "sse", "url": "..."}`
- **Claude Code mcpServers config**(本文件):`{"type": "sse", "url": "..."}`

这两个 schema 看起来几乎一样,但 Claude Code 加载时如果用 `transport` 会报 `Does not adhere to MCP server configuration schema` 然后拒绝加载。**首次提交本文件 (commit 90af9ed) 用的是错的 `transport` 字段,直到 GOV-005 followup verification (Board "/mcp 验证" task) 才被发现并修复。**

唯一正确的真相源是 `~/.claude.json` 里 Claude Code 自己的 mcpServers config 块——以那里为准。

---

## 用途

`scripts/spawned_mcp_config.json` 是一个 MCP config 文件,让任何**用 subprocess 启动的 Claude Code 子进程**自动连接到本机运行的 gov-mcp 服务器(SSE 端口 7922),从而继承全套 Y\*gov 治理保护:

- ✅ 每个 tool call 经过 `gov_check` 拦截(ALLOW/DENY)
- ✅ 写入 CIEU 库(`.ystar_cieu.db`)
- ✅ 触发 OmissionEngine 义务追踪
- ✅ 受 `deny_commands` 保护(包括 `ystar setup --yes`)
- ✅ 受 `restricted_write_paths` 保护
- ✅ AGENTS.md immutable charter hook 物理拦截

---

## 历史背景

GOV-005 daemon architecture decision(2026-04-09)Board 选择 **C+A 组合方案**:

- **C**: 退役 `agent_daemon.py`(失败实验,2026-04-04 emergency stop 后 frozen 5 天,文件已归档到 `reports/archive/daemon_failed_experiment_2026_04_04/`)
- **A**: 保留 gov-mcp 接通基础设施,让未来任何 spawned Claude Code session 都能直接复用,不重蹈 daemon "subprocess 旁路治理" 的覆辙

完整提案见 `reports/cto/daemon_governance_architecture_proposal.md`。

---

## 前置条件

**Mac mini 必须有 gov-mcp server 在跑,监听 SSE port 7922**。验证命令:

```bash
lsof -i :7922 | grep LISTEN
# 期望输出: Python ... TCP *:7922 (LISTEN)

pgrep -fl gov_mcp
# 期望输出: ... python -m gov_mcp --transport sse --port 7922
```

如果没跑(installed 但未启动):

```bash
python3.11 -m gov_mcp \
    --agents-md /Users/haotianliu/.openclaw/workspace/Y-star-gov/AGENTS.md \
    --transport sse \
    --host 0.0.0.0 \
    --port 7922 &
```

注意: 当前 Mac mini 上 `gov-mcp` CLI 命令未在 PATH 里,只能用 `python -m gov_mcp` 调用 module。这是 GOV-005 后续发现的小问题,留 P3 任务跟进。

---

## 使用方法(已验证 2026-04-09)

### Bash invocation pattern(已端到端测试通过)

```bash
claude -p \
       --max-budget-usd 2.00 \
       --mcp-config scripts/spawned_mcp_config.json -- \
       "Use the mcp__gov-mcp__gov_doctor tool with empty arguments..." \
       < /dev/null
```

**3 个易错点**(都在 2026-04-09 verification 时被发现):

1. **`--mcp-config <configs...>` 是 variadic flag**——它接受空格分隔的多个 config 文件路径。**必须用 `--` 分隔符**告诉 Claude Code 后面是 prompt 不是另一个 config 文件,否则 prompt 字符串会被当成 config 文件路径,报 `MCP config file not found: <prompt 内容>`。

2. **`< /dev/null` 跳过 stdin wait**——`claude -p` 默认等 stdin 3 秒,如果不重定向会有 warning + 延迟。

3. **`--max-budget-usd` 必须 ≥ 1.00**——即使 "say only OK" 这种最小 prompt 也会消耗 ~$0.10+ 的 input tokens。$0.10 budget 立刻 exceed。

### Python subprocess invocation pattern

```python
import subprocess

result = subprocess.run([
    "claude", "-p",
    "--max-budget-usd", "2.00",
    "--mcp-config", "scripts/spawned_mcp_config.json",
    "--",  # ← 关键: 终止 flag parsing
    "你的 prompt 内容",
],
cwd="/Users/haotianliu/.openclaw/workspace/ystar-company",
stdin=subprocess.DEVNULL,  # ← 关键: 跳过 3s stdin wait
capture_output=True, text=True)
print(result.stdout)
```

### 不要做

- ❌ **不要加 `--no-session-persistence` 而不带 `--mcp-config`**——这是 daemon (`agent_daemon.py` line 374) 失败的根因。这个 flag 让 spawned Claude Code 不加载 settings.json,如果同时没有 `--mcp-config` 显式指定,就完全没有 MCP servers,因此完全旁路治理。**和 `--mcp-config` 一起用是 OK 的**(因为 `--mcp-config` 显式提供 servers)。
- ❌ **不要省略 `--` 分隔符**——你的 prompt 会被吃成 config 文件路径,报错。
- ❌ **不要忘了 `< /dev/null`**——会有 stdin warning。

### 验证调用是否真的接通了 gov-mcp(端到端 smoke test)

```bash
claude -p --max-budget-usd 2.00 --mcp-config scripts/spawned_mcp_config.json -- \
"Use the mcp__gov-mcp__gov_doctor tool with empty arguments {}. Return ONLY the raw JSON response from the tool. No analysis. No prose. Just the JSON. If the tool is not available, output exactly: TOOL_NOT_AVAILABLE" \
< /dev/null
```

**期望输出**: 一个 JSON 字符串,包含 `health`, `checks`, `delegation_chain`, `omission_engine`, `cieu`, `exec_whitelist` 字段。任意正常返回的 JSON 都证明 MCP round-trip 通。

**失败模式**:
- `Error: Invalid MCP configuration: ... Does not adhere to MCP server configuration schema` → 检查 spawned_mcp_config.json 字段名,必须是 `type` 不是 `transport`
- `Error: MCP config file not found: <你的 prompt 内容>` → 缺 `--` 分隔符
- `TOOL_NOT_AVAILABLE` → gov-mcp server 没跑,或 `--mcp-config` 没加载成功
- `Exceeded USD budget` → 提高 `--max-budget-usd`

**端到端测试历史**: 2026-04-09 GOV-005 followup ("/mcp 验证" task) 第一次真实验证通过,13 秒返回完整 gov_doctor JSON。在此之前(commit 90af9ed → 验证之前),本 config 文件用的是错的 `transport` 字段,**实际上无法被 Claude Code 加载**——但这一事实从未被 verified,直到 Board 强制要求验证才暴露。这是 reports/cto/intent_verification_proposal.md 的第 4 个 real intent-drift 例子。

---

## 验证 spawned session 真的连上了 gov-mcp

启动测试 spawned session 后,检查:

```bash
# 1. CIEU 库 record 数量在 spawned session 期间应该增加
python3.11 -c "from ystar.governance.cieu_store import CIEUStore; \
               print(CIEUStore('.ystar_cieu.db').count())"

# 2. 让 spawned session 试一个被 deny 的命令(应该被拦)
# 例如让它跑 `ystar setup --yes` → 期望被 deny_commands 拦截

# 3. 检查 obligation status
python3.11 scripts/check_obligations.py --db .ystar_cieu.db
```

---

## 与现有治理基础设施的关系

| 治理层 | 现状 |
|---|---|
| `.ystar_session.json` `deny_commands` | ✅ 包含 `ystar setup --yes`(GOV-005 Part 3 加入) |
| `.ystar_session.json` `obligation_agent_scope` | ✅ 已用 role-based ID(GOV-005 Part 4) |
| `agents/*.md` GOV-001 义务追踪条款 | ✅ 6 个岗位都有(GOV-001 Step 6) |
| `governance/INTERNAL_GOVERNANCE.md` 三级权限 | ✅ Level 1/2/3 已定义(GOV-005 Part 2) |
| `governance/WORKING_STYLE.md` 第七条 | ✅ 反事实推理提案规范(GOV-005 Part 1) |
| `scripts/register_obligation.py` / `check_obligations.py` | ✅ Production 就绪(GOV-001 Step 5) |
| **`scripts/spawned_mcp_config.json` (本文件)** | ✅ **新增,GOV-005 daemon architecture** |

---

## 来源

Board GOV-005 daemon architecture decision (2026-04-09)。CTO Ethan 的反事实推理提案(`reports/cto/daemon_governance_architecture_proposal.md`)推荐 C 为最优、A 为次优,Board 决定**两个都要**:C 退役失败实验 + A 保留架构教训作为可复用基础设施。
