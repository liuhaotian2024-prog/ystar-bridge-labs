# Y* Bridge Labs · `archive/deprecated/` Directory
# Standard long-term deprecation area
# 创建日期：2026-04-09 · GOV-005 daemon architecture decision

---

## 用途

`archive/deprecated/` 是 Y\* Bridge Labs 仓库的**标准长期废弃区**。任何被正式退役但需要保留学习价值的代码、文档、配置、实验产物都进入这里(不删除,不藏在 git history 里)。

每个 deprecated 物件应该:

- 占据自己的子目录(便于隔离 + 寻找)
- 子目录命名格式: `{物件名}_{失败/退役日期}` 或 `{物件名}_{原因简称}`
- 子目录顶层有一个 README.md(或本类型的总说明文件)解释退役原因 + cross-ref 相关 commit/proposal/DNA

**当前住户(本目录第一个 occupant)**: `daemon_failed_experiment_2026_04_04/`

---

## AMENDMENT-002 · agent_daemon.py 退役

### 退役决策

- **决策来源**: Board GOV-005 daemon architecture directive (2026-04-09)
- **决策格式**: GOV-005 反事实推理提案 → Board 选 "C+A 组合方案" (退役失败实现 + 安装可复用架构)
- **决策权限层级**: Level 3 (架构变更影响 daemon + agent + 治理基础设施 + 5 个岗位 prompts)
- **执行人**: Ethan Wright (CTO)
- **完整提案**: `reports/cto/daemon_governance_architecture_proposal.md`

### 退役理由 (5 条客观证据,不带情感)

**1. 治理旁路是设计缺陷,不是 bug:**
`scripts/agent_daemon.py` line 374 的 `--no-session-persistence` flag 让 spawned Claude Code 不加载 `~/.claude/settings.json`,因此**不连接任何 MCP server,不触发任何 hook,完全旁路 Y\*gov 治理**。这不是可以"打补丁修复"的 bug——它是 daemon 设计的根本路径选择。要修就要重写 spawn 逻辑。

**2. 2026-04-04 emergency stop 的客观数据:**
违规速率 173 → 386 → 466 / 小时(每 2 小时翻倍),CEO 紧急停机。"Option D" 补丁尝试失败。`.daemon_emergency_stop` 文件是 CEO 当时手写的决策证据。

**3. 5 天 frozen 期的对照实验:**
2026-04-04 12:30 → 2026-04-09 18:00, daemon frozen 5 天 5 小时。这期间 Board-initiated session 完成了:
- GOV-001 (8 步 治理基础设施 + 义务追踪)
- GOV-004 Part 1 (宪法修改授权机制)
- GOV-005 (5 parts 反事实推理 + 三级权限 + agent_id 统一 + AMENDMENT-001 + 文档归并)
- AMENDMENT-001 / 002 (deny_commands + daemon 退役)
- 6 个 agents/*.md GOV-001 + GOV-005 双重 DNA 蒸馏
- RuleRegistry P1 提案
- YGVCC framework validity test

**没有 daemon,治理工作完成度反而更高**。这是反事实推理意义上的硬证据: daemon 的实际价值 ≤ 0。

**4. 哲学冲突:**
Y\*gov 自己的产品定位卖点是"无监督 agent 是危险的"。daemon 的存在(让 agent 24/7 自主跑) **直接和这个定位矛盾**。Board 不可能既卖"危险性"产品又自己运行"危险性"系统。这不是工程问题,是 alignment 问题。

**5. Windows 设计 + Mac mini 迁移成本:**
daemon 是 Windows hardcode (`r"C:\Users\liuha\..."` paths, `cmd.exe /c`, `Get-Process` PowerShell),从未在 Mac mini 真实运行过。即使要保留,也需要 70+ 行重构 + 半天测试。这是修复成本叠加在已经验证为低价值的功能上,不划算。

### 替代方案 (Board 选项 A,已安装,不属于退役范围)

`scripts/spawned_mcp_config.json` + `scripts/SPAWNED_SESSION_GOV_MCP.md` 是 daemon 退役的**架构教训蒸馏物**:
任何未来用 subprocess 启动的 Claude Code session **必须**通过 `--mcp-config` 加载 gov-mcp 接通。这一条规则现在是公司 Level 3 宪法的一部分(写入 `governance/DNA_LOG.md` DNA #006)。

### 归档清单 (12 个文件 + 本 README)

代码 + 状态:
- `agent_daemon.py` (652 行, Windows 设计)
- `agent_daemon.log`
- `agent_daemon.nohup.log`
- `.agent_daemon_state.json`
- `.daemon_emergency_stop` (CEO 紧急停机决策证据,JSON)
- `agent_daemon_task.xml`

Crisis postmortems (从 reports/autonomous/ 归档):
- `daemon_bug_fix_20260404.md`
- `daemon_crisis_session11_20260404.md`
- `daemon_emergency_stop_20260404.md`
- `daemon_escalation_option_a_20260404.md`
- `daemon_fix_failure_20260404.md`
- `daemon_governance_crisis_20260403.md`

### 不复活的条件

未来如果要复活类似 daemon 概念,**必须先满足以下 3 条**(任一缺失则不得部署):

1. **走 gov-mcp 治理路径**: 使用 `scripts/spawned_mcp_config.json` 或同等机制,subprocess 启动的 Claude Code 必须能 verify 连上 gov-mcp(`gov_check` 拦截链路通)
2. **有人在场的 cadence**: 自主工作时段必须和 Board/CEO 的活跃 session 部分 overlap, 不能纯无监督 24/7
3. **过 GOV-005 反事实推理 + Board Level 3 批准**: 走完整的 governance/WORKING_STYLE.md 第七条提案流程,Board 在 RT 评分基础上批准

不满足任一条件者退回提案。

---

## 相关 commits / 文件 cross-reference

| Artifact | 路径 / Hash |
|---|---|
| 反事实推理提案 | `reports/cto/daemon_governance_architecture_proposal.md` (commit `626030e`) |
| 退役 commit (option C) | `57d8aec` |
| 安装基础设施 commit (option A) | `90af9ed` |
| 重定位到 archive/deprecated/ commit | (本 commit) |
| DNA 蒸馏 | `governance/DNA_LOG.md` DNA #006 |
| MCP 接通 config | `scripts/spawned_mcp_config.json` |
| 接通操作文档 | `scripts/SPAWNED_SESSION_GOV_MCP.md` |
| 治理执行层禁令 | `.ystar_session.json` `deny_commands` 含 `ystar setup --yes` (AMENDMENT-001) |

---

## AMENDMENT 编号约定

本目录的退役事件以 `AMENDMENT-NNN` 编号(和 `governance/BOARD_CHARTER_AMENDMENTS.md` 共用编号空间但目的不同):

- AMENDMENT-001: `ystar setup --yes` 加入 deny_commands (执行层修复, GOV-005 Part 3)
- **AMENDMENT-002: agent_daemon.py 退役** (GOV-005 daemon architecture, 本文件)

未来 AMENDMENT-003+ 会出现在 `governance/BOARD_CHARTER_AMENDMENTS.md` 或本目录,取决于性质(宪法修改 vs 物件退役)。
