# AMENDMENT-026 — CTO-Centralized Dispatch Architecture (CDP (CTO Dispatch Protocol — Y*gov Path B 是产品术语，本文 CDP 是流程术语，2026-04-13 rename 避免冲突) 选定)

> **2026-04-13 Board 重写指示**: 原本提议"per-role write + cross-role help"是 both-and 复杂方案。Board 二选一选 **CDP (CTO Dispatch Protocol — Y*gov Path B 是产品术语，本文 CDP 是流程术语，2026-04-13 rename 避免冲突) (CTO 派单写)** — 理由："自己写自己岗位的容易乱"。下面是修正版。

---

| 字段 | 内容 |
|---|---|
| Level | 3 (Constitutional addition: 写入权限治理底层重构) |
| 起草日 | 2026-04-13 |
| 起草人 | CEO Aiden (per Board 直接指出"之前的技术债") |
| 强依赖 | A007 (CEO OS) + A009 (escape hatch) + A017 (capability envelope) + A023 (CROBA) |

## §0 TL;DR

**Board 原话第一轮**: "CMO 写 content/ 越 cto boundary，这就是之前的技术债"
**Board 原话第二轮 (corrective)**: "不是 both 关系，是二选一。要么定好 [per-role] 或者 CTO 派单写。自己写自己岗位的容易乱"

**选定 CDP (CTO Dispatch Protocol — Y*gov Path B 是产品术语，本文 CDP 是流程术语，2026-04-13 rename 避免冲突)**: CTO-Centralized Dispatch (单点 orchestration)

修复 = 1 件事 + 1 个固化：
1. **激活 `must_dispatch_via_cto` rule** (当前 NOT_ENFORCING per session boot output) — CEO/Board 不直派 engineer/specialist subagent，必经 CTO
2. **每岗位仍 own 自己业务 allowed_write_paths** (domain expert 实际写)，但 spawn 入口收拢到 CTO 一处

---

## §1 现状审计 (deep tech debt)

`.ystar_session.json` 当前结构 (sample):
```json
{
  "agent_write_paths": {
    "ceo": ["./reports/", "knowledge/ceo/", ...],
    "cto": ["./scripts/", "./tests/", "./products/", "./docs/", "Y-star-gov/", "CLAUDE.md"]
  },
  "restricted_write_paths": {
    ".ystar_active_agent": ["secretary"],
    "AGENTS.md": ["secretary"],
    ...
  }
}
```

**真问题：**
1. `agent_write_paths` 主要列了 CEO + CTO，**CMO/CSO/CFO/Secretary/Engineers 几乎都没显式列**
2. 当 CMO subagent 写 `content/offended_ai/` 时 — 它 hit cto boundary 因 active_agent=cto (顶岗) 或 因 cmo 没显式 allow content/
3. 跨岗位帮写 (CMO 让 CTO 帮 ship 视频生成 pipeline 进 scripts/) 没有 formal 通道

**今晚实证：** CMO顶岗 v5 第一次 spawn 时 active_agent=cto → 写 content/ deny → 报 blocker → CEO 用 pkill window 切 active_agent=cmo → 重 spawn 才能写。这是手动 workaround，应该是协议。

---

## §2 提议

### Part A: Per-Role Write Boundary Matrix

`.ystar_session.json` `agent_write_paths` 字段全员显式：

```json
{
  "ceo":         ["./reports/", "./knowledge/ceo/", "./BOARD_PENDING.md", "./DISPATCH.md", "./OKR.md", "./DIRECTIVE_TRACKER.md", "./OPERATIONS.md", "./WEEKLY_CYCLE.md", "memory/", ".claude/agents/"],
  "cto":         ["./scripts/", "./tests/", "./products/", "./docs/", "Y-star-gov/", "gov-mcp/", "./CHANGELOG.md", "./CLAUDE.md", "./.github/", ".claude/tasks/"],
  "cmo":         ["./content/", "./marketing/", "./knowledge/cmo/", "./reports/cmo*"],
  "cso":         ["./sales/", "./knowledge/cso/", "./reports/cso*"],
  "cfo":         ["./finance/", "./knowledge/cfo/", "./reports/cfo*"],
  "secretary":   ["./governance/BOARD_CHARTER_AMENDMENTS.md", "./governance/DNA_LOG.md", "./knowledge/", "./memory/boot_packages/", "ARCHIVE_INDEX.md", ".ystar_active_agent"],
  "eng-kernel":     ["Y-star-gov/ystar/kernel/", "Y-star-gov/tests/", "knowledge/eng-kernel/"],
  "eng-governance": ["Y-star-gov/ystar/governance/", "Y-star-gov/tests/", "knowledge/eng-governance/"],
  "eng-platform":   ["./scripts/", "./tests/", "Y-star-gov/ystar/adapters/", "knowledge/eng-platform/"],
  "eng-domains":    ["Y-star-gov/ystar/adapters/", "Y-star-gov/tests/", "knowledge/eng-domains/"]
}
```

每岗位**默认 own 业务路径** + 可显式 deny / restrict 子路径

### Part B: 单点 Spawn 入口 — `must_dispatch_via_cto` 激活

**核心规则** (现 NOT_ENFORCING → 改 ENFORCING):
- CEO/Board 不可直接 spawn CMO/CSO/CFO/Secretary/任何 engineer subagent
- 唯一允许 CEO/Board 直 spawn: **Ethan-CTO** subagent
- 其他角色 spawn 必经 CTO: `CEO → CTO → CMO/CSO/.../engineer`

**实现:**
1. `governance/forget_guard_rules.yaml` 加 rule `ceo_direct_engineer_dispatch` (Maya 上次 Gap 2 已规划但没 ship 因 hook bug)
2. ForgetGuard trigger: `tool=Agent + active_agent=ceo + subagent_type in [CMO/CSO/CFO/Secretary/engineer*] + 不在 break_glass + 缺 "via CTO override" justification`
3. action: **deny** (不 warn — 这是硬约束) + recipe "Use Agent(subagent_type=Ethan-CTO, ...) and have CTO dispatch downstream"

**ForgetGuard rule 例外 (whitelist)**:
- general-purpose subagent (顶岗 protocol) 仍允许 CEO 直 spawn — 因为顶岗是 emergency 不是常规
- break_glass mode 期间 CEO 直 spawn 任何 — 紧急逃生

### Part C: 移除 (Cross-Role Help Protocol DROPPED)

原 Part C "X 帮 Y 写"复杂协议**全部废弃**——Board 选了 CDP (CTO Dispatch Protocol — Y*gov Path B 是产品术语，本文 CDP 是流程术语，2026-04-13 rename 避免冲突) 后，cross-role 写法只一种：让 CTO 派对应 domain expert subagent。  
没有 self-help。没有 grant transfer。没有 顶岗 except emergency。简化。

### Part C: 顶岗 Protocol (when subagent unavailable)

当 Y subagent 不在 registry (e.g. Sofia-CMO BOM bug 修了但本 session 不重读)：

1. **Active_agent flip**: CEO/Secretary 用 pkill window 设 `.ystar_active_agent = Y`
2. **Spawn general-purpose** with prompt "你顶岗 Y, daemon 会按 Y boundary enforce" 
3. 顶岗 sub-agent 写 within Y domain 全 OK
4. 顶岗 退出后 CEO self-heal active_agent 回 ceo

需 codify 进 `knowledge/ceo/skills/ding_gang_protocol.md` (新 skill)

---

## §3 验收

- (a) `.ystar_session.json` `agent_write_paths` 含全 10 角色显式 list
- (b) `gov_delegate` 增 `additional_paths` 参数 + Y consent 流程
- (c) 写 `knowledge/ceo/skills/ding_gang_protocol.md`
- (d) e2e: spawn CMO subagent → 直接写 content/ pass; CTO 用 gov_delegate 临时拿 1 个 sales/ 文件 write 权; 顶岗 protocol pkill window flip → 顶岗 spawn → ship → CEO 自 restore，全 0 Board intervention

---

## §4 RAPID

| Role | Action |
|---|---|
| **R**ecommend | CEO Aiden (本提案) |
| **A**gree | CTO Ethan + Maya-Governance + Secretary Samantha |
| **P**erform | Ethan-CTO 统筹 → Ryan-Platform (session.json edit) + Leo-Kernel (gov_delegate 扩展) + Secretary (顶岗 protocol skill 写) |
| **I**nput | 4 engineers (验各自 boundary) |
| **D**ecide | Board L3 |

---

## §5 风险

| 风险 | mitigation |
|---|---|
| 全员开新 boundary → 安全降级 | 严守 default-deny + 每条 path 走 review |
| Cross-role delegation 滥用 | gov_delegate `additional_paths` 默认 max 3 文件 + 1h expire |
| 顶岗 protocol 被滥用 | pkill window 已有 CIEU audit；secretary auto-enforce 周扫顶岗时长 |

---

## §6 与其他 amendment 关系

- **A007 CEO OS**: CEO 现 allowed_write 已含 reports/+memory/ — 无变更
- **A009 escape hatch**: pkill window self-heal 为顶岗 protocol Step 1
- **A017 capability envelope**: A026 是 A017 specific 实例 (write 是其中一种 capability)
- **A018 whitelist**: 跨域 write delegation 应进 whitelist sync
- **A023 CROBA**: 任何 cross-role write 前必先 read 目标 path 现有内容

---

## §7 Board 决策点

CEO 已批方向 (本 amendment 起草授权)。Board L3 批 = 触发 Ryan/Leo/Secretary 实施（48h 内 ship Part A+B+C）。

无选择题。

---

## 附录 A: 即时手动 patch (Board 批前可先用)

CEO 用 break_glass + Edit 给 .ystar_session.json `agent_write_paths` 加 cmo/cso/cfo/secretary 显式 list — 不 wait Ryan 实施。今晚就解 CMO content/ 写阻塞类问题。
