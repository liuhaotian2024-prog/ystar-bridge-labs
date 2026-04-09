# Daemon Governance Architecture — 反事实推理提案

**作者**: Ethan Wright (CTO)
**日期**: 2026-04-09
**优先级**: P1
**权限层级**: **Level 3**(架构变更影响 daemon + agent + 治理基础设施三层)
**状态**: 提案,待 Board 决策
**触发**: Board GOV-005 framework first real architecture decision
**提案格式**: 严格遵守 `governance/WORKING_STYLE.md` 第七条反事实推理格式

---

## 问题

**`scripts/agent_daemon.py` 用 `subprocess.Popen` 启动的 Claude Code 子进程不继承父 session 的 MCP servers 和 hooks,导致 daemon 内的所有 agent 工作完全旁路 Y\*gov 治理层。** 2026-04-04 这个旁路问题已经爆发过一次: 违规速率 173→386→466/小时加速,CEO 紧急停机至今,daemon 已 frozen 5 天。

---

## 当前状态 Xt

### Xt-1: daemon 的实际行为(代码读取证据)

`scripts/agent_daemon.py` line 371-377 + line 439-445:

```python
cmd = [
    "cmd.exe", "/c", CLAUDE_CMD,           # ← Windows shell 硬编码
    "--agent", name,
    "-p", agent["prompt"],
    "--max-turns", str(MAX_TURNS),
    "--no-session-persistence",            # ← 关键问题: 不继承父 session
]
result = subprocess.run(cmd, ...)
```

`CLAUDE_CMD = r"C:\Users\liuha\AppData\Roaming\npm\claude.cmd"`(line 35)
`WORK_DIR = Path(r"C:\Users\liuha\OneDrive\桌面\ystar-company")`(line 31)

**这个 daemon 从未在 Mac mini 上运行过——所有路径、所有 shell 调用、所有进程检测全是 Windows-only。**

### Xt-2: `--no-session-persistence` 的真实含义

这个 flag 让 Claude Code 启动一个**全新会话**,不读取 `~/.claude/settings.json`,不连接父 session 的 MCP servers,不加载任何 hooks。后果:

- ❌ 不连接 gov-mcp(本机 SSE 端口 7922)
- ❌ 不触发 PreToolUse hook(`_hook_client.sh`,即拦截 AGENTS.md 编辑的那个 hook)
- ❌ 不写 CIEU records 到 `.ystar_cieu.db`
- ❌ 不受 `deny_commands` 保护(包括 GOV-005 Part 3 刚加的 `ystar setup --yes` 禁令)
- ❌ 不受 `restricted_write_paths` 保护
- ❌ 不查 obligation_agent_scope 也不更新 OmissionEngine

子进程 Claude Code 在 daemon 模式下**完全不受治理**,可以任意读写、任意执行命令、任意修改 AGENTS.md。

### Xt-3: 2026-04-04 emergency stop 的真相

`scripts/.daemon_emergency_stop`:

```json
{
  "stopped_by": "CEO",
  "reason": "Option D failed - violations accelerating (173→386→466/hour)",
  "timestamp": "2026-04-04T12:30:00",
  "decision": "Emergency stop pending Board review"
}
```

违规速率每两小时翻倍,daemon 在 6 小时内累积 1000+ 违规,人类来不及审计。"Option D" 是当时尝试的某个 patch 性修复,失败。从此 daemon frozen,company 在过去 5 天靠 Board-initiated session 完成了 GOV-001 + GOV-004 + GOV-005 所有治理升级,**没有 daemon 也活得好好的**。

### Xt-4: daemon 当前的设计意图(代码注释 + 配置)

- `CYCLE_INTERVAL = 14400`(4 小时一轮,line 38。注释明确写"CEO决策2026-04-04:降低violations压力"——降时间间隔是 Option D 的一部分,失败了)
- `PARALLEL_GROUPS`(line 416-425): 4 组并行(eng-kernel/governance, eng-platform/domains, cto+cmo+cso+cfo, 单 ceo)
- 7 agent + 4 工程师 + 1 ceo 一轮共 12 spawned subprocess
- 每个 prompt 50-80 行,要求 agent "立刻产出代码 / commit / push / 写报告"
- `--max-turns 25`,每 agent 最多 25 个 LLM round-trip
- 静默时段 23:00-07:00 不运行

### Xt-5: gov-mcp 的实际能力(README + tool list 证据)

- **38 个治理工具** 全部 production,EXP-008 验证: -45.1% output tokens, -61.5% wall time, 39000+ checks/sec, 50 并发 agent 零死锁
- 核心入口: **`gov_check(agent_id, tool_name, params)`**——单一 entry point,返回 ALLOW/DENY,deterministic 命令(`ls`, `git status`, `cat`)直接 inline 执行返回 stdout
- 设计模式: gov-mcp 是 **MCP server**(SSE 端口 7922),不是 agent runner。它**不 spawn agent**,只**拦截 agent 的 tool call**。
- **`gov_exec` 已经 DEPRECATED**(README 明文标注),redirect 到 `gov_check` 并显示迁移指南
- 连接方式: 任何 MCP client 加一段 config 即可:
  ```json
  {"mcpServers":{"gov-mcp":{"url":"http://127.0.0.1:7922/sse","transport":"sse"}}}
  ```
- 本 session(我现在跑的这个 Claude Code)就是通过这个 config 连上 gov-mcp 的,所以我的 deferred tools 列表里有 `mcp__gov-mcp__*` 系列。

---

## 目标 Y*

Daemon 内每个 spawned agent 的每个 tool call **必须**:

1. 经过 gov-mcp 的 `gov_check` 拦截层(ALLOW/DENY 决定)
2. 写入 `.ystar_cieu.db`(CIEU 审计记录)
3. 触发 OmissionEngine(义务追踪)
4. 受 `deny_commands` / `restricted_write_paths` / immutable charter 保护
5. 在 ystar doctor 8/8 健康状态下运行

并且 daemon 本身必须能在 Mac mini 上跑(去 Windows 化)。

**Rt = 0 的可观测条件:**

- daemon 跑一轮后,`.ystar_cieu.db` records 数量增加 ≥ N(其中 N = spawned agent 数 × tool calls 数)
- daemon 跑一轮后,OmissionEngine 状态 report 显示 daemon 期间触发的义务
- 任何 spawned agent 试图执行 `ystar setup --yes` 被 gov-mcp 拦截
- doctor 8/8 全绿,违规速率 < 10/小时

---

## 反事实分析

### 方案 A: 让 spawned Claude Code 通过 MCP config 连接 gov-mcp

**做法**: daemon 的 spawn 命令改成传一个 MCP config 文件,文件里包含 gov-mcp 连接信息。spawned Claude Code 启动后自动连上 gov-mcp,所有后续 tool call 都经过 `gov_check`。

具体修改:

1. 写一个 `scripts/daemon_mcp_config.json`:
   ```json
   {"mcpServers":{"gov-mcp":{"url":"http://127.0.0.1:7922/sse","transport":"sse"}}}
   ```
2. daemon 的 spawn 命令改成:
   ```python
   cmd = [
     "claude",                                # macOS native (/opt/homebrew/bin/claude)
     "--mcp-config", str(MCP_CONFIG_PATH),    # 显式加载 gov-mcp config
     "--agent", name,
     "-p", agent["prompt"],
     "--max-turns", str(MAX_TURNS),
     # 删除 --no-session-persistence (它阻止 MCP servers 加载)
   ]
   ```
3. 去 Windows 化:
   - `WORK_DIR` 改为 `/Users/haotianliu/.openclaw/workspace/ystar-company`
   - `CLAUDE_CMD` 改为 `claude`(直接走 PATH)
   - 删除 `cmd.exe /c` 包装
   - `is_board_active()` 用 `pgrep -f claude` 替代 `Get-Process claude`(PowerShell)
4. 7 个 agent 的 prompt 里 Y-star-gov 路径(`C:\Users\liuha\OneDrive\桌面\Y-star-gov\`)改为 `/Users/haotianliu/.openclaw/workspace/Y-star-gov/`
5. 验证 gov-mcp 在 Mac mini 上以 SSE 模式启动(`gov-mcp install` 或检查 port 7922)

**Yt 预测**:
- 修改量约 **70 行** in agent_daemon.py(10 行 paths/shell + 8 行 spawn cmd + 50 行 prompts 路径替换)
- 新增 1 个 5 行 JSON config 文件
- gov-mcp 已经 production,无需新代码
- 验证: spawn 一个 daemon agent → 让它执行 `ystar setup --yes` → gov-mcp 拦截 → CIEU 库 +1 deny record
- **依然要解决的根问题**: 即使 governance 接通了, daemon 自主工作的 quality 问题(2026-04-04 教训)是否改善?**这不是接 gov-mcp 能解决的——是 prompt design 和 oversight cadence 问题**。

**Rt(与 Y* 的差距)**:
- ✅ tool call 拦截 → DONE
- ✅ CIEU 审计 → DONE
- ✅ OmissionEngine → DONE
- ✅ deny_commands → DONE
- ✅ Mac mini 可运行 → DONE
- ⚠️ 违规速率 < 10/小时 → **不确定**, 因为这取决于 agent prompt 质量, gov-mcp 只能拦不能教

**Rt 评分**: 治理层 = 0,质量层 = 中等不确定

### 方案 B: daemon 内嵌 Y*gov enforcement 层(MITM proxy)

**做法**: daemon 解析 spawned Claude Code 的 stdout/stderr 流,识别 tool call 边界,在每个 tool call 出去之前调 `gov_check`,在结果返回之前注入 deny 信息。本质上是在 Python 里手写一份 hook 客户端,绕过 Claude Code 自己的 MCP 协议。

**Yt 预测**:
- 修改量 **>500 行 新代码** + 重大测试投入
- 需要解决的子问题:
  - 解析 Claude Code 的 tool call 输出格式(可能跨多行 / 含 ANSI 控制符 / 含 JSON 嵌套)
  - 注入 deny 反馈到 spawned 进程的 stdin(stdin 可能是非交互式)
  - 处理 race condition(daemon 还没拦下来,Claude Code 已经 commit 到 LLM 了)
  - 处理 partial output(stream 还没完整就要拦)
  - 维护一个 inflight tool call state machine
- gov-mcp 现有代码完全用不上,等于重写一个简陋版的 MCP client/proxy
- 测试投入估计 5-10 天

**Rt(与 Y* 的差距)**:
- ✅ tool call 拦截(理论上)
- ⚠️ CIEU 审计可以做但要自己写写入逻辑
- ❌ 违反 DRY: Y\*gov + gov-mcp 已经做了所有这些事,daemon 再写一遍是反模式
- ❌ 违反 Iron Rule 3(Ecosystem Neutrality): hardcode 解析 Claude Code 输出格式 = ecosystem-bound,Y\*gov 卖点之一是 host-agnostic
- ❌ 维护成本: Claude Code 输出格式一变, daemon 就坏

**Rt 评分**: 治理层 = 0(理论上),工程债 = 极高,违反 Iron Rule 3 → **直接出局**

### 方案 C: 退役 daemon,不修不迁

**做法**: 删除 `scripts/agent_daemon.py` + 相关 state 文件 + 配套 reports 移入归档。所有"自主工作"改为 Board-initiated session(包括定时调度的 cron-like 触发——但触发点是人,不是无监督进程)。

**理由(基于 5 天的真实数据)**:
- daemon 自 2026-04-04 emergency stop 后 frozen 至今(已 5 天)
- 这 5 天里 Board-initiated session 完成了:
  - GOV-001 (8 步): CIEU 修复 + 义务追踪基础设施
  - GOV-004 Part 1: 宪法修改授权机制
  - GOV-005 (5 parts): 反事实推理 + 三级权限 + agent_id 统一 + AMENDMENT-001 + 文档归并易部分
  - YGVCC framework validity test
  - 6 个 agents/*.md DNA 蒸馏
  - RuleRegistry P1 提案
- **没有 daemon 的情况下,治理基础设施反而完成度更高**——因为每一步都有人在
- daemon 的设计假设是"AI 自己工作 24/7 = throughput 最大化",但 Y\*gov 自身的产品定位是"无监督 agent 是危险的"。**daemon 和 Y\*gov 哲学相矛盾**

**Yt 预测**:
- `git rm scripts/agent_daemon.py scripts/agent_daemon.log scripts/agent_daemon.nohup.log scripts/.agent_daemon_state.json scripts/.daemon_emergency_stop scripts/agent_daemon_task.xml`
- `mv reports/autonomous/daemon_*.md reports/archive/daemon_failed_experiment_2026_04_04/`
- 在 `governance/DNA_LOG.md` 写一条蒸馏: "DNA #N: 不监督的 agent 自主工作创造的治理债 > 创造的工作产出, 此公司选择 Board-supervised cadence"
- 修改量: 0 行新代码,~10 个文件删除/移动
- 时间投入: 30 分钟

**Rt(与 Y* 的差距)**:
- ✅ 治理违规 = 0(因为没有不受治理的 spawned process)
- ✅ Mac mini 不需要去 Windows 化
- ✅ 不需要修 gov-mcp 集成
- ✅ doctor 8/8 全绿
- ⚠️ 失去"24/7 自主工作"的能力(但过去 5 天的数据表明这个能力的真实价值 ≤ 0)
- ⚠️ daemon 的代码学习价值损失(可以保留一份 archive 备查)

**Rt 评分**: **0**(并且无新增技术债)

---

## 最优解 = **方案 C(退役 daemon)**

**理由(一句话)**: 过去 5 天的真实数据证明 daemon 的实际价值 ≤ 0(GOV-001/004/005 全部 Board-initiated 完成),修复成本(70 行 + 测试 + Mac mini 验证)不如 0 行(直接退役)。Y\*gov 自身的产品哲学是"无监督 agent 危险",daemon 的存在自相矛盾。

## 次优解 = **方案 A(MCP config 接通 gov-mcp)**

**为什么不是最优**: 即使治理层完美接通,daemon 自主工作的质量问题(2026-04-04 教训)是 prompt design + oversight cadence 问题,不是 governance 拦截能解决的。修了 daemon 等于花 70 行代码 + 半天测试,**仍然不能保证它不再产生违规**——只能保证违规会被记录。"违规会被记录"和"不违规"是两件事。但如果 Board 出于**情感原因或路线图原因**坚持保留 daemon 概念(例如未来想做 24/7 公司演示),A 是唯一合理的技术路径。

## 直接出局 = **方案 B(MITM proxy)**

> 500 行新代码 + 违反 Iron Rule 3 (ecosystem-bound) + 重新发明 gov-mcp 已经做的事 + Claude Code 输出格式一变就坏。**不在候选范围内**。

---

## Board 提的 3 个具体问题的回答

### Q1: agent_daemon.py 现在怎么调用 Claude Code?

**用 Windows shell 子进程,完全旁路治理。** 具体:

```python
# scripts/agent_daemon.py line 371-387
cmd = ["cmd.exe", "/c", CLAUDE_CMD,
       "--agent", name, "-p", agent["prompt"],
       "--max-turns", str(MAX_TURNS),
       "--no-session-persistence"]
subprocess.run(cmd, cwd=str(WORK_DIR), ...)
```

`--no-session-persistence` 让 spawned Claude Code 不加载 `~/.claude/settings.json`,所以**没有 MCP servers,没有 hooks,没有 gov-mcp 连接,没有 Y\*gov 治理**。

### Q2: gov-mcp 的接口能不能覆盖 daemon 当前所有的使用场景?

**能,但需要理解 gov-mcp 的角色定位。** gov-mcp 不是"agent runner"——它**不 spawn agent**,而是**拦截 agent 的 tool call**。它是一个 MCP server(SSE port 7922,38 个 tool),agent 作为 MCP client 连上去,然后每次 tool call 走 `gov_check` 决定 ALLOW/DENY。

所以"通过 gov-mcp 运行 agent" 的真实含义是: **让 spawned Claude Code 把 gov-mcp 注册为它的 MCP server**。daemon 还是用 subprocess,但 spawned Claude Code 通过 `--mcp-config` flag 加载 gov-mcp 连接。这样 daemon 内的 agent 和 Board-initiated session 走的是**同一条治理路径**——本 session(你正在看的这个)就是通过这条路径连上 gov-mcp 的,deferred tools 列表里那 12 个 `mcp__gov-mcp__*` 是证据。

**关于覆盖度**:
- ✅ Tool call 拦截: gov_check 完整覆盖 38 个工具
- ✅ CIEU 审计: gov-mcp 自动写 `.ystar_cieu.db`
- ✅ OmissionEngine 触发: gov-mcp 集成
- ✅ deny_commands 保护: 包括 `ystar setup --yes`(GOV-005 Part 3 刚加)
- ✅ delegation chain: gov_delegate
- ✅ 38000+ checks/sec, sub-2ms latency, 50 并发 agent 零死锁(EXP-008)
- ⚠️ "agent 整轮 session 的 task 调度" gov-mcp 不管——daemon 仍然要负责 spawn / 串并行编排 / 超时 / 重试

### Q3: 从 subprocess 切到 gov-mcp 集成需要改多少地方?

**约 70 行 in agent_daemon.py + 1 个 5 行 JSON config 文件。** 拆解:

| 修改项 | 行数估计 |
|---|---|
| `WORK_DIR`、`CLAUDE_CMD` Windows path → Mac path | 2 |
| `cmd.exe /c` 包装去除 + spawn 命令重构 | 8 |
| 添加 `--mcp-config` flag 到 spawn 命令 | 4 |
| 删除 `--no-session-persistence` flag | 2 |
| `is_board_active()` PowerShell → `pgrep` | 12 |
| 7 个 agent 的 prompt 里 Y-star-gov 路径替换(每个 prompt ~7 行 path 引用) | ~50 |
| **新建** `scripts/daemon_mcp_config.json` | 5 |
| **小计** | **~83** |

加上验证测试(spawn 一个 daemon agent → 让它跑测试命令 → 看 CIEU 库 +1 → 让它跑 deny 命令 → 看拦截): 约 **半天工程时间**。

但这是方案 A 的代价——如果 Board 选方案 C,**修改量是 0,删除量是 ~10 个文件**。

---

## 风险评估

### 方案 A 的风险

| 风险 | 严重度 | 缓解 |
|---|---|---|
| spawned Claude Code 在 Mac mini 上 path 解析失败 | 中 | 全部用绝对路径 + cwd 显式传 |
| `--mcp-config` flag 不被 spawned Claude Code 识别 | 低 | claude code CLI 已支持(本 session 就在用) |
| gov-mcp 在 Mac mini 上未启动 | 中 | spawn 前先 `gov-mcp status` 检查 |
| daemon 跑完一轮 又开始 violations 加速 | **高** | **方案 A 不能消除这个风险**——这是 prompt design 问题 |
| daemon 同时 spawn 12 个 Claude Code = 12 个 LLM cost burst | 中 | CYCLE_INTERVAL 已经是 4h |
| `--no-session-persistence` 移除后 spawned session 累积 state 污染 | 中 | 每次 spawn 显式清 `.ystar_active_agent_*` |

### 方案 C 的风险

| 风险 | 严重度 | 缓解 |
|---|---|---|
| 失去 24/7 throughput | 低 | 过去 5 天数据说明 throughput ≤ 0 |
| Board 想未来做"AI 公司 24/7 演示" | 中 | 可以保留 daemon 代码 archive,需要时复活 |
| daemon 的某些独特能力(如 K9 inbox 自动检查)失去 | 低 | 这些可以独立写小脚本,不需要 daemon |

---

## 实施步骤

### 如果 Board 批准方案 C(退役)

```bash
# Step 1: archive daemon experiment
mkdir -p reports/archive/daemon_failed_experiment_2026_04_04
git mv scripts/agent_daemon.py \
       scripts/agent_daemon.log \
       scripts/agent_daemon.nohup.log \
       scripts/.agent_daemon_state.json \
       scripts/.daemon_emergency_stop \
       scripts/agent_daemon_task.xml \
       reports/archive/daemon_failed_experiment_2026_04_04/

# Step 2: archive related crisis reports
git mv reports/autonomous/daemon_*.md \
       reports/archive/daemon_failed_experiment_2026_04_04/

# Step 3: write DNA distillation entry
# (Secretary writes governance/DNA_LOG.md entry — Level 1 自决)

# Step 4: commit
git commit -m "decommission: retire agent_daemon experiment — GOV-005-followup
                Empirical data 2026-04-04 to 2026-04-09: 5 days frozen,
                governance work flow completed without it. Y*gov philosophy
                conflict: unsupervised agents create more debt than value.
                Code preserved in reports/archive/ for future reference."
git push origin main
```

工作量: **30 分钟,1 commit**

### 如果 Board 批准方案 A(修复 + 接通 gov-mcp)

```bash
# Step 1: 验证 gov-mcp 在 Mac mini 上运行
gov-mcp status     # 期望输出: "Server running on port 7922"
# 如果没跑: gov-mcp install

# Step 2: 写 MCP config 文件
cat > scripts/daemon_mcp_config.json << 'EOF'
{"mcpServers":{"gov-mcp":{"url":"http://127.0.0.1:7922/sse","transport":"sse"}}}
EOF

# Step 3: 修 agent_daemon.py(70 行)
# - WORK_DIR / CLAUDE_CMD path
# - is_board_active() PowerShell → pgrep
# - spawn cmd: 加 --mcp-config, 去 --no-session-persistence, 去 cmd.exe
# - 7 prompts: Y-star-gov path 替换

# Step 4: spawn 一个 test agent 验证
python scripts/agent_daemon.py --test-spawn eng-kernel
# 期望: spawned Claude Code 连上 gov-mcp,执行测试命令,CIEU +N records

# Step 5: 验证治理保护
python scripts/agent_daemon.py --test-deny "ystar setup --yes"
# 期望: gov-mcp 拦截,CIEU +1 deny record

# Step 6: ystar doctor 8/8 全绿

# Step 7: commit + push

# Step 8: 决定是否真的启动定时 daemon, 还是只保留代码不启动
```

工作量: **半天工程 + 测试**

---

## Level 3 决策点(Board 必看)

GOV-005 Part 2 定义 Level 3:
> 架构变更影响两个及以上岗位的核心职责

本提案影响:
- **CTO (ethan_wright)**: 工程实施
- **CEO (aiden_liu)**: 自主工作流程的存在与否
- **CMO/CSO/CFO/Secretary**: 自主工作 prompt 直接定义这些岗位的 daemon 行为
- **Y\*gov 治理基础设施**: 是否扩展到 daemon 内

→ **Level 3,Board 拍板**。

---

## Board 决策需要回答

**只需要一句话**: 选 A、C,还是 A 和 C 都不要(让 daemon 继续 frozen)?

- **C**: Ethan 30 分钟内完成退役 commit,1 个 commit。daemon 历史代码在 archive 可查。
- **A**: Ethan 半天工程 + 测试。daemon 修好但 quality 风险仍在。
- **维持现状**: daemon 继续 frozen,什么都不动。这其实和 C 等价,只是文件还在。

---

**附录: 反事实分析的元注解**

按 GOV-005 第七条,本提案是 Y\*Bridge Labs 第一次正式使用反事实推理格式提案。提案给出的不只是"A vs B",而是"A vs B vs C",其中 C 是 Board 没有列出但**反事实推理过程中浮现的更优解**。这正是 GOV-005 设计意图——团队完成全部分析,不让 Board 在 Board 列出的选项里做有限选择。如果未来类似情况,提案方应该总是问自己:"Board 列的选项是否完整?有没有更优解 Board 没有想到?"

CTO 同时承诺: 本提案完成于 2026-04-09 ET 同一 session,**没有动一行代码**,严格遵守 Board 指令"不要直接动代码,这是一个架构决策,不是一个'先做再说'的任务"。

---

**End of proposal.** 等 Board 一句话决策。
