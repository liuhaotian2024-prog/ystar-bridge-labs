# AMENDMENT-004 — Single-Machine Operating Reality (DRAFT, pending Board approval)

> **Level 3 修宪提案** · 起草人：Samantha Lin (Secretary)
> **起草日期**：2026-04-12
> **触发背景**：CEO Aiden 于 2026-04-12 session 中发现 CLAUDE.md 「双机分工原则」与「Y\*gov Source Repository」「新窗口启动指令」三段已与运行现实脱节；CEO 已踩过"派活给 MAC 执行"的空操作坑，裁决进入 L3 流程修正。
> **授权路径**：本文件起草 → Board 审阅 → Board 批准 → Secretary 按"影响评估"逐项执行 → 补入 `governance/BOARD_CHARTER_AMENDMENTS.md` 作为 AMENDMENT-004 正式条目。
> **Level 判定依据**：`governance/INTERNAL_GOVERNANCE.md` 第 120 行——修改 CLAUDE.md 属于"宪法伴随文档"层级；因为 CLAUDE.md 是 session boot 的顶层 context，变更会同时波及多个 agent 行为语义，按 Level 3 标准「架构变更影响两个及以上岗位的核心职责」处理。

---

## 1. 一行摘要

把 CLAUDE.md 里"Windows 本机 / MAC mini 双机分工"的过期叙事，替换为"全团队运行于单台 Mac 的 OpenClaw workspace（`/Users/haotianliu/.openclaw/workspace/ystar-company`），岗位分工通过 Agent/MCP delegation 而非跨机派发"。

---

## 2. 事实对照（为什么必须改）

| 维度 | CLAUDE.md 当前叙事 | 运行现实（2026-04-12 验证） |
|---|---|---|
| 操作系统 | Windows（本机）+ MAC mini（远端） | 单台 Mac（`Platform = darwin`） |
| 工作目录 | `C:\Users\liuha\OneDrive\桌面\ystar-company` | `/Users/haotianliu/.openclaw/workspace/ystar-company` |
| Y\*gov 源码 | `C:\Users\liuha\OneDrive\桌面\Y-star-gov\` | 同一台 Mac 的对应 macOS 路径（需 CTO 确认新实际路径后 Secretary 补录） |
| 工程任务派发 | Windows 写 `.claude/tasks/` → Board 转发 → MAC 执行 | 同一台 Mac 上通过 sub-agent / MCP delegation 派发给 CTO + 4 工程师 |
| "派给 MAC mini" 的语义 | 跨机 RPC | **空操作**——本来就在同一台机上 |
| Gemma endpoint `192.168.1.228:11434` | 远端 MAC mini 服务 | 需 CTO/Platform 确认：是否仍为独立 MAC mini，或已折叠到本机 localhost（本提案**不改**此条，仅标注待验证） |

**直接后果**：CEO 在 2026-04-12 session 中按旧叙事说"派给 MAC 执行"，实际是在同一台 Mac 上派给自身 sub-agent，语义错位导致 Board 裁决。

---

## 3. 修改前 / 修改后 Diff

### 3.1 CLAUDE.md 第 145–148 行（"Y\*gov Source Repository"小节）

**修改前：**
```markdown
## Y*gov Source Repository

The Y*gov source code is located at:
C:\Users\liuha\OneDrive\桌面\Y-star-gov\
```

**修改后：**
```markdown
## Y*gov Source Repository

The Y*gov source code is located at the macOS sibling workspace of this company repo.
Canonical path (pending CTO confirmation at AMENDMENT-004 execution time):
`/Users/haotianliu/.openclaw/workspace/Y-star-gov/` (or the path reported by `ystar --version --verbose`).

Legacy Windows path `C:\Users\liuha\OneDrive\桌面\Y-star-gov\` is DEPRECATED as of AMENDMENT-004 (2026-04-12) — the company no longer operates in a dual-machine Windows+Mac configuration.
```

---

### 3.2 CLAUDE.md 第 156–167 行（"双机分工原则"整节）

**修改前：**
```markdown
## 双机分工原则（Y* Bridge Labs专用）

Windows（本机）Aiden负责：
- 读文件、分析状态、写文档、生成报告
- 向Board汇报、等待指令、协调任务分配
- 收到代码任务时：写入.claude/tasks/，通知Board转发MAC执行

MAC mini（192.168.1.228）工程团队负责：
- 所有写代码的任务
- 所有测试运行
- 所有git操作
- GOV MCP server常驻运行
```

**修改后：**
```markdown
## 单机运行原则（Y* Bridge Labs专用，AMENDMENT-004, 2026-04-12 起）

**物理现实**：整个 Y* Bridge Labs 运行在一台 Mac 上，workspace 位于
`/Users/haotianliu/.openclaw/workspace/ystar-company`。所有岗位（CEO / CTO / CMO / CSO / CFO / Secretary / 4 工程师）都是同一 Claude Code 实例里的 agent/sub-agent，通过 Agent 工具与 MCP delegation 协作，不存在跨机 RPC。

**岗位协作方式**：
- **CEO (Aiden)**：协调、分工、汇报、与 Board 对话。不直接写代码。收到代码任务时，通过 Agent 工具调起 CTO (Ethan) 或相应工程师 sub-agent，或把任务卡写入 `.claude/tasks/` 由对应岗位认领。
- **CTO (Ethan) + 4 工程师 (Leo / Maya / Ryan / Jordan)**：承担所有写代码、跑测试、git 操作、Y\*gov 源码维护。作为 sub-agent 在同一 Claude Code 会话中运行。
- **GOV MCP server**：本机长驻进程（`localhost:7922` SSE 或对应端口，以 `.ystar_session.json` 与 gov-mcp 启动参数为准）。

**历史**：2026-04 之前曾存在 Windows 主机 + MAC mini (192.168.1.228) 的双机分工配置，所有 code/test/git 跨机派给 MAC mini 执行。该配置随 OpenClaw workspace 统一到单台 Mac 后作废。任何 agent 指令中出现"派给 MAC 执行"字样一律视为**空操作冗余**，必须改述为"调起 {角色} sub-agent 执行"。

**关于 `192.168.1.228` 的遗留引用**：
- `.ystar_session.json` 中的 Gemma endpoint `http://192.168.1.228:11434` 与 `scripts/local_learn.py` 中的同一 URL，属于**本地模型服务**层，其归属机器（本机 localhost 还是独立局域网 MAC mini）需 Platform 工程师在 AMENDMENT-004 执行阶段确认，本条 amendment **不修改**这些字段，仅要求 CTO 在批准后 72h 内给出验证报告。
```

---

### 3.3 CLAUDE.md 第 58–61 行（"新窗口启动指令"代码块）

**修改前：**
```markdown
**新窗口启动指令（固化）：** 如果老大开了新终端窗口，必须先进入公司目录再启动：
```
cd "C:\Users\liuha\OneDrive\桌面\ystar-company"
claude
```
然后输入"重启"触发boot协议。**不在ystar-company目录下启动的Claude Code不会加载本文件，团队记忆不会恢复。**
```

**修改后：**
```markdown
**新窗口启动指令（固化）：** 如果老大开了新终端窗口，必须先进入公司目录再启动：
```
cd /Users/haotianliu/.openclaw/workspace/ystar-company
claude
```
然后输入"重启"触发boot协议。**不在ystar-company目录下启动的Claude Code不会加载本文件，团队记忆不会恢复。**
```

---

## 4. 修改理由

1. **事实对齐**：CLAUDE.md 作为 session boot 的顶层 context，其描述的物理拓扑必须与 `env.cwd` / `Platform` 一致。当前不一致已经造成至少一次 CEO 误操作。
2. **消除空操作语义**："派给 MAC mini 执行"在单机配置下是零语义动作，却让 Board 与 agent 都在该词面上浪费推理步骤。
3. **OpenClaw workspace 统一**：公司已迁入 `~/.openclaw/workspace/`，这是平台级约定，应在宪法伴随文档层固化。
4. **保留历史**：本次修改不是删除历史，而是把"双机分工"降级为"曾经的配置"，保留给未来审计可读的来龙去脉。

---

## 5. 影响评估（Board 批准后 Secretary 按此清单执行）

### 5.1 必须同步修改（高优先）

| 文件 | 位置 | 动作 |
|---|---|---|
| `CLAUDE.md` | 第 58–61 行 | 替换 Windows 路径为 Mac 绝对路径（见 §3.3） |
| `CLAUDE.md` | 第 145–148 行 | 重写 Y\*gov Source Repository 小节（见 §3.1） |
| `CLAUDE.md` | 第 156–167 行 | 重写"双机分工原则"→"单机运行原则"（见 §3.2） |
| `governance/BOARD_CHARTER_AMENDMENTS.md` | 文件末尾 | 追加 AMENDMENT-004 正式条目（含 commit hash 与执行日期） |
| `memory/session_handoff.md` | 开头的 "MAC mini" 标签 | 改为 "Single-Mac OpenClaw workspace" |

### 5.2 需审阅并按情况更新（中优先，Secretary 逐个确认）

| 文件 | 涉及问题 |
|---|---|
| `AGENTS.md` | 如含双机分工 regex 或路径常量，需同步（**注意：AGENTS.md 本身是 Y\*gov immutable path，修改走独立 amendment 条目**，见 AMENDMENT-003 历史教训；本提案不触碰 AGENTS.md，只标出若存在相关文本则需要独立 amendment） |
| `governance/WORKING_STYLE.md` | grep 显示含相关字样，需人工确认是否为实质规则 |
| `agents/Secretary.md` | 第 439 行 "192.168.1.228: ?" 需更新为确切归属（本机 localhost 还是独立 MAC mini） |
| `agents/CFO.md` | 第 27 行 "MAC mini电费估算" — 如已折叠到本机则删除此成本条目 |
| `.claude/agents/{ceo,cto,cmo,cso,cfo,eng-domains,eng-governance,eng-kernel,eng-platform}.md` | 逐份 grep 双机分工描述 |
| `docs/mac-cto-workstation-setup.md` | 明确标注为 DEPRECATED 或移入 `archive/` |
| `docs/session-lifecycle-cieu-events-and-deny-upgrade.md` | 第 4 行 "MAC mini engineering team" 描述需更新为 "sub-agent engineering team" |
| `docs/JINJIN_INTEGRATION.md` | 第 23 行 Mac mini (192.168.1.228) 架构图需重画或标注历史 |
| `DISPATCH.md` | 第 255 行 "MAC mini CTO session" 描述 |
| `scripts/migrate_handoff_to_yml.py` | 第 95 行 "MAC mini: Primary" 硬编码字符串 |
| `scripts/deploy_mac_cto*.py` / `scripts/mac_deploy_agents.py` / `scripts/mac_command.py` / `scripts/setup_ssh_access.md` | 全部判定为 legacy；Board 批准后 Secretary 与 CTO 协商是否 move 到 `archive/deprecated/` |
| `drafts/FRONTEND_PROMOTION_PLAN.md` / `drafts/README_REWRITE.md` | 草稿层，等正稿时顺带更新 |
| `reports/pretrain_verification_2026-04-05.md` / `reports/autonomous/2026-04-01-platform-mac-deployment.md` / `reports/governance_layer_on_openclaw.md` | 历史报告，**不修改**，但在 AMENDMENT-004 条目里交叉引用，声明其物理前提已失效 |
| `reports/cto/daemon_governance_architecture_proposal.md` | 如提案尚在生效期，需 CTO 重新提交；否则归档 |

### 5.3 **不修改**（明确保留）

| 文件 | 保留理由 |
|---|---|
| `.ystar_session.json` Gemma endpoint | 模型服务拓扑是 Platform 级决定，独立议题；本 amendment 不触碰 |
| `scripts/local_learn.py` `192.168.1.228:11434` | 同上 |
| `archive/deprecated/daemon_failed_experiment_2026_04_04/*` | 历史实验档案，按 archive 原则不回写 |
| 所有 social cookies / linkedin profiles | 与本议题无关 |

### 5.4 验证步骤（Secretary 执行后）

1. `grep -rn "双机分工" .` → 期望 0 条命中（除 `BOARD_CHARTER_AMENDMENTS.md` 历史记录外）
2. `grep -rn "C:\\\\Users\\\\liuha" CLAUDE.md` → 期望 0 条命中
3. `grep -rn "Windows（本机）" .` → 期望 0 条命中
4. 新开一个 Claude Code session 跑 boot 协议，确认 `ALL SYSTEMS GO` 输出未引入 regression
5. CTO 72h 内提交 `192.168.1.228` 归属验证报告

---

## 6. 风险与回退

- **风险 A**：CLAUDE.md 修改可能被 Y\*gov immutable-path hook 拦截（参照 AMENDMENT-003 经验）。
  - **缓解**：CLAUDE.md 不在 Y\*gov 当前 immutable 列表中（仅 `AGENTS.md` 是硬禁）；Secretary Edit 工具调用应能通过。如被拦，按 AMENDMENT-003 方案 (Y) 由 Board 手动编辑。
- **风险 B**：CTO 在 72h 内未能确认 `192.168.1.228` 归属。
  - **缓解**：AMENDMENT-004 主体条款不依赖此验证；Gemma endpoint 验证作为独立 follow-up 子任务。
- **回退路径**：如批准后实测发现单机假设破裂（例如 Gemma 实际仍在独立 MAC mini），Secretary 起草 AMENDMENT-005 微调"单机"表述为"主机 + 模型推理侧车"。

---

## 7. Board 需批准的具体点（签字位）

请 Board 在以下三项上分别给出"批准 / 否决 / 修改"裁决：

- [ ] **点 1**：同意将 CLAUDE.md §156–167 "双机分工原则"替换为"单机运行原则"（§3.2 diff）。
- [ ] **点 2**：同意将 CLAUDE.md §145–148 与 §58–61 中的 Windows 硬路径替换为 Mac OpenClaw 路径（§3.1 + §3.3 diff）。
- [ ] **点 3**：授权 Secretary 按 §5.1 + §5.2 的清单在 commit 窗口内逐项同步更新，并在 `BOARD_CHARTER_AMENDMENTS.md` 追加 AMENDMENT-004 正式条目。

| 字段 | 内容 |
|---|---|
| Board 裁决 | ⬜ 批准 / ⬜ 否决 / ⬜ 修改后批准 |
| Board 签字时间 | __________________________ |
| Board 备注 | __________________________ |
| 执行人 | Samantha Lin (Secretary) |
| 执行 commit hash | （待填） |
| 执行完成时间 | （待填） |

---

*— End of AMENDMENT-004 draft —*
