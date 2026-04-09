# Spawned Claude Code Session — Y*gov Governance Connection
# 创建日期：2026-04-09 · GOV-005 daemon architecture decision (Board: 退役c, 安装a)

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

## 使用方法

任何 subprocess 启动 Claude Code 时,加上 `--mcp-config` flag 指向本配置文件:

```python
import subprocess

subprocess.run([
    "claude",                                                    # macOS native, /opt/homebrew/bin/claude
    "--mcp-config", "scripts/spawned_mcp_config.json",           # ← 关键
    "--agent", "cto",                                            # 选择 agent
    "-p", "你的 prompt 内容",
    "--max-turns", "25",
    # 不要加 --no-session-persistence! 它会 disable MCP servers loading
], cwd="/Users/haotianliu/.openclaw/workspace/ystar-company")
```

**绝对不要加** `--no-session-persistence` flag——这是 daemon 失败的根因,它让 spawned Claude Code 不加载 settings.json,因此不连任何 MCP server,因此完全旁路治理。

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
