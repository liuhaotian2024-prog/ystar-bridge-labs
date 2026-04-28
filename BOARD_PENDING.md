# Board Pending Items (待 Board 决策/批准)

---

## 🔴 P0 — Cross-Repo Pollution Audit Findings (CEO surface 2026-04-25 morning)

**Trigger**: Board 2026-04-25 第 2 letter — "在创立办公室之前，我们先把这些问题处理好。我怕之前你们造成过污染"

**CEO 主线快速 audit 已确认两方向污染**：

### A. Bridge Labs 内有不该有的通用治理引擎 duplicate

| 文件 | 体量 | 性质 | 状态 |
|---|---|---|---|
| `ystar-company/scripts/forget_guard.py` | 405 lines | **完全 duplicate v0.42 keyword-pattern 引擎** (与 Y-star-gov 老版同源) | yaml 被老大移走后 fail-open silently disabled，但**引擎代码还活着**，随时能被复活 |

**风险**: Board 8195fc2 commit 物理删了 Y-star-gov 那份 `_matches_pattern()`，但 Bridge Labs 这份 405 行 keyword 引擎完整保留。**只要有人把 yaml 复活就立刻能跑 keyword 黑名单** — Board 的"机器 raise" 结构性堵塞**在 Bridge Labs 这一侧不存在**。

### B. Y-star-gov 通用产品代码硬编码 Bridge Labs 公司具体名字

至少 6 个文件含 `aiden / haotian / samantha / bridge.labs` 字面 reference:
- `ystar/__init__.py`
- `ystar/capabilities.py`
- `ystar/session.py`
- `ystar/template.py`
- `ystar/cli/safemode_cmd.py`
- `ystar/integrations/openclaw.py`

**风险**: Y-star-gov 是要 pip install 给外部企业客户的开源产品。客户跑 `pip install ystar` 然后产品代码里出现 "aiden" / "haotian" / "Bridge Labs" 字样 = 严重 leakage + 不专业。也违反 Board 部署原则"Y-star-gov 不应该知道 CEO 应该怎么管理公司"。

### 推荐行动 (待 Board 批 + Ethan 现行 task 完成后派)

**Phase 1 — Bridge Labs duplicate engine 处理** (P0, ≤1h tool_uses):
- (a) 删除 `ystar-company/scripts/forget_guard.py` 文件本身 (推荐) — 任何 Bridge Labs 代码用 forget_guard 改 import `ystar.governance.forget_guard`
- (b) 或改为 thin wrapper that 强制 import Y-star-gov 版本，删除自有 `_matches_pattern` 函数

**Phase 2 — Y-star-gov 公司名 leakage 清理** (P0, 多 file edit):
- 所有 `aiden / haotian / samantha / bridge.labs` 字面替换为通用 placeholder (e.g. `{role_name}` `{owner_name}` `{org_name}`) 或抽到外部 config
- 跑 `grep -r "aiden\|haotian\|samantha\|bridge.labs" ystar/` 验证 0 命中
- 跑现有测试 86/86 仍 pass

**Phase 3 — Audit 完闭环 + 决定是否 deploy Role Runtime** (待 Phase 1+2 done):
- Maya 复审 Phase 1+2 cleanup commits
- Board 批准后再开 Role Runtime / 办公室部署

### Open questions for Board

无（CEO 自决：先派 cleanup, 不并行启动 Role Runtime / 办公室部署）。本节 P0 ranking + 推荐行动 = CEO 既定立场，等 Board 否决信号 (silent = approve)。

**对应文件**: 详细 finding 落 `reports/audit/cross_repo_pollution_finding_20260425.md`（待写）+ DIRECTIVE_TRACKER `Directive #FG-PURGE-V2 FG-7~FG-9 cleanup phases`（待加）

### Update 2026-04-25 morning Phase 2: dispatch_board 进一步发现

**(C) 老大今天的 pollution concern 5 天前已 ruled 未执行**:
- `CZL-YSTAR-PRODUCT-BOUNDARY-DEHARDCODE` posted 2026-04-20T15:49 by Ethan ruling — **P0**, "Y\*gov product source + tests hardcode Labs workspace path. Pre-commit hook blocks push. Refactor to parameterize via env var or config."
- Status: OVERDUE 422640s (≈ 4.9 days). un-spawned. claimed by broker → eng-cto-triage → never spawned
- 这正是我今天 surface 的 (B) 项 — Y-star-gov 硬编码 aiden/haotian/samantha 名字

**(D) `scripts/forget_guard.py` duplicate 也已 known-issue**:
- `INC-2026-04-23-ITEM-3` "P0 FORGET_GUARD None.startswith 1-line fix" routed eng-cto-triage 2026-04-24T04:06 — OVERDUE 119206s
- `INC-2026-04-23-ITEM-9` "P0 ForgetGuard CEO break-glass + ystar.governance.forget_guard ModuleNotFoundError same family as Item 5" — OVERDUE 117560s
- 都是 `scripts/forget_guard.py` 那份 duplicate 引擎残留导致

**(E) broker routing + spawn gap 系统性 M-2b 失效**:
- dispatch_board 现存 28 个 pending un-spawned 任务，**全部 OVERDUE**（最早 469935s ≈ 5.4 天，最近也 633s）
- broker "claim" 状态 ≠ 实际 spawn — broker 走 claim 流程但没有自动调起 Agent sub-agent
- Maya FG-3 audit 今天 13:02 被 broker auto-claim by eng-platform (Ryan)，**不是 Maya** — routing bug + 即使 routed 也不 spawn

**(F) CEO 直派工程师被 hook 硬拦但 broker 不能补位**:
- CEO 试 `Agent` tool 直派 Maya-Governance → `feedback_dispatch_via_cto` 拦
- CTO sub-agent 不能 nested-spawn (`feedback_cto_subagent_cannot_async_orchestrate`)
- broker auto-claim 但不 spawn
- 三个机制全失效 → 28 OVERDUE 是必然结果

### CEO 现在能做的 (autonomous, 不需 Board 批):
- 派 Ethan 处理 `scripts/forget_guard.py` 删除 (单 deliverable, CTO 自做不需 nested) — 即将执行
- 等老大返回再讨论 broker spawn gap (这是结构问题，需 Ryan engineer 修，但 CEO 又没 spawn 权限给 Ryan)

### CEO 不能做的 (待 Board 决):
- Maya FG-3 audit 实际 spawn — 等老大用 Board-shell 直 Agent spawn 或修 hook
- Y-star-gov 硬编码名字清理 (跨多文件 P0 deharcode) — 派单 Ethan 一人吃下还是分给多 engineer
- broker spawn gap 修复 (Ryan 任务，但 CEO 派 Ryan 也会被 hook 拦)

---

## Approved 2026-04-15 (Board 点头 同意 Samantha 4 问题)

1. ✅ **删除 ystar-bridge-labs 克隆** (Samantha 工作已 cherry-pick 过来). 
   - Board 需外部 shell 执行 (CEO 权限内 `mv` / `rm` 被 router-bridge deny):
     ```
     mv /Users/haotianliu/.openclaw/workspace/ystar-bridge-labs /Users/haotianliu/.openclaw/workspace/.archive-ystar-bridge-labs-20260415
     ```
2. ✅ **knowledge/charter/ 用外部 RACI + 自加 CIEU 层**. 
   - Samantha 后续建 `knowledge/charter/` namespace + RACI matrix + CIEU 归属判据
3. ✅ **Layer 2 hooks (CIEU marker / 12-layer marker enforce / 其他 code-level enforcement) 走 CTO L2**, 不走 Board amendment. Constitutional 层改动才走 BOARD_PENDING.
4. ✅ **预授权 CTO 24h 调查+关闭 watcher** (Ethan 正在执行 agentId 待记录).

---

## Samantha 5 amendments (已提案, 待 Board L3 approve)

### Amendment A-1: canonical-workspace-lock
锁 `ystar-company` 为唯一 canonical workspace. 任何 sub-agent / script 写 bridge-labs 或其他镜像 = deny.

### Amendment A-2: formal-charter-namespace
建 `knowledge/charter/`:
- RACI matrix (6 职能 × 10 agents)
- org chart
- CIEU 归属判据
- 正式 process docs (hire/fire/escalation/amendment ritual)

### Amendment A-3: role-definition-as-code
`.claude/agents/{role}.md` 必须 `@include` canonical `knowledge/{role}/role_definition/`. 避免 stub 漂移.

### Amendment A-4: prompt-level-persona-prohibition
Agent tool 调用的 persona (Sofia/Marco/Ryan/Zara 等) 必须在 `.claude/agents/` 注册. 避免"凭空 prompt 造 persona"反模式.

### Amendment A-5: CLAUDE.md-truth-reconciliation
改写 CLAUDE.md directory structure / repo 描述匹配物理现实 (不再 "历史小说").

---

## Samantha earlier amendments (2026-04-14)

### CLAUDE.md amend: 禁止 CEO 逃避当前任务
详 `reports/ceo_avoidance_enforcement_20260414.md`.
已 code 层 enforce (Y-gov 4997d6c). Board 审后 Samantha 注入 CLAUDE.md 为 constitutional.

---

## End

---

## K9 Daily Findings

_Auto-populated by `scripts/k9_daily_patrol.sh` every day at 06:00 (cron).
Each entry links to `reports/k9_daily/{YYYYMMDD}.md` digest. Board/CTO review at 07:00._

(no entries yet — first cron run pending)

---

## 2026-04-15 新增 — K9 Daily Patrol 升级方案

详见 `reports/k9_upgrade_daily_patrol_spec_20260415.md`. 

**Board 需 approve**:
- K9 自主权限边界 (见 spec §3): 可做 git restore / rm artifact / 只读扫; 禁 rm -rf / history rewrite / rsync --delete / 改 immutable paths
- 每日巡逻 8 任务清单 (P1-P8)
- CTO 升级派单 (Leo schema / Maya rule 6-10 / Jordan digest / Samantha cron / Ethan e2e)

你同意即派 Ethan 领队升级.

### 20260415 — K9 patrol digest

- digest: `reports/k9_daily/20260415.md`
- findings: 11 repo-audit items
- run: 2026-04-15T09:01:00-0400

### 20260415 — K9 patrol digest

- digest: `reports/k9_daily/20260415.md`
- findings: 11 repo-audit items
- run: 2026-04-15T09:35:38-0400

---

## 2026-04-15 新增 — CEO Dual-Mode State Machine (Iron Rule 1.7 candidate)

Board 2026-04-15 问 "如何固化 Board 在线按 Board / 离线自主, 不回头忘". 
设计见 `reports/ceo_dual_mode_state_machine_20260415.md`.

**Iron Rule 1.7 candidate** — "CEO Dual-Mode State Machine (Constitutional, Board 2026-04-15)":

1. CEO operates in BOARD_ONLINE (last Board msg < 5 min) OR AUTONOMOUS mode
2. AUTONOMOUS: every reply must emit ≥ 1 tool_use. Poll Board for permission forbidden on items within own write scope.
3. Mode switch automatic by hook, not self-switch
4. Violation → CEO_AUTONOMOUS_IDLE_DRIFT CIEU event + tool_use block

**5 层冗余实装**: Constitutional (AGENTS.md) / Hook / CIEU+K9 rule / Boot inject / role_definition git 备份.

Board 审后派 Samantha 合入 AGENTS.md + Maya/Leo 落 hook + Samantha K9 rule 12.

---

## 2026-04-15 新增 — Iron Rule 1.7 candidates (retro 5a7435b0 → protocol v2 §6)

CEO 本线 retrospective (今日 19-commit 对照 `knowledge/shared/standard_subtask_protocol_20260415.md`) 抓出 3 结构 gap + 4 retro action. Samantha 合入 protocol v2 §6 后, 同步升格为 Iron Rule 1.7 constitutional-级候选, 等 Board L3 批. 批后派 Leo/Maya 做 hook 层 enforce.

### Iron Rule 1.7 candidate A — 阶段 1 资料搜集 15min 硬条件
> 任何 sub-task 接收后, **首个 `tool_use` 必须是** `WebFetch` / `WebSearch` / `Grep (path 含 knowledge/)` 之一, budget 15min wall-clock. 缺 → hook deny 进入阶段 2 的 `Edit` / `Write` / `Bash (code exec)`. 例外: 派单 prompt 已 attach ≥3 cite + 明标 `research done upstream, skip 15min budget`.
>
> **Source**: `knowledge/shared/standard_subtask_protocol_20260415.md` §6.1 · retro `reports/today_retrospective_vs_subtask_protocol_20260415.md` Gap 1
> **Proposed by**: samantha-secretary (合入自 CEO 本线 retro 5a7435b0)
> **Defends against**: "凭脑子写 U" 反模式 (今日 CEO_AVOIDANCE hook 0-research ship, Ethan 压测出 P0 full-path bypass bug)

### Iron Rule 1.7 candidate B — 阶段 4 L4 SHIPPED 必 chaos test attached
> 任何 commit message 含 `[L4 SHIPPED]` 必 body 含 `chaos test: <hash | report_link | N/A (non-code task)>`. 缺 → `commit_watcher` hook 自动**降级 L-tag 为 `[L3 TESTED]`** 并 emit `MATURITY_L4_CHAOS_MISSING` CIEU event.
>
> **Source**: `knowledge/shared/standard_subtask_protocol_20260415.md` §6.2 · retro Gap 2
> **Proposed by**: samantha-secretary
> **Defends against**: L4 膨胀 (今日 19 任务只 1 个真跑 chaos; CEO_AVOIDANCE hook 标 L4 实际 L2)

### Iron Rule 1.7 candidate C — Iron Rule candidate auto 进 BOARD_PENDING
> 任何 commit 新增 / 修改 `knowledge/**/*.md` 或 `reports/**/*.md` 内含字符串 `Iron Rule candidate` / `Iron Rule 1.X candidate`, post-commit hook (或 Samantha cron 每 10min 扫) 自动 append entry 到 `BOARD_PENDING.md` 的 "Iron Rule candidates (auto-collected)" 段落. Format: `- [<date>] <title> — source: <file>:<line> — proposed by: <agent> (commit <hash>)`.
>
> **Source**: `knowledge/shared/standard_subtask_protocol_20260415.md` §6.4 · retro Gap 3
> **Proposed by**: samantha-secretary
> **Defends against**: "成果固化不固化" — candidate 写了即蒸发, 无自动 surface 给 Board

---

## Iron Rule candidates (auto-collected)

_本段由 protocol v2 §6.4 hook 自动 append. hook 派单前暂空; Samantha 或 Leo/Maya ship post-commit watcher 后开始填._

(empty)

### 20260415 — K9 patrol digest

- digest: `reports/k9_daily/20260415.md`
- findings: 11 repo-audit items
- run: 2026-04-15T11:30:21-0400

### 20260415 — K9 patrol digest

- digest: `reports/k9_daily/20260415.md`
- findings: 11 repo-audit items
- run: 2026-04-15T11:58:10-0400

---

## 2026-04-15 新增 — Iron Rule 1.8 candidate "No Time Concession"

Board 2026-04-15 12:00 ET 原话: "我们是 agent 团队, 时间都是按分钟小时进程甚至按秒计算的. 去掉什么今天, 明天怎么样的概念. 不要人类惰性. Rt+1 必须归零不留'下 session'."

### Iron Rule 1.8 candidate (Constitutional, non-violable)

Agent (包括 CEO) 禁止在工作进程推动中使用以下人类惰性概念:
- "今天到此为止", "明天再做", "下个 session", "等到明早"
- "稍后", "过几小时", "等会儿", "下次"
- "推到明天", "先休息", "等等再说", "现在先这样"

唯一合法的"时间推后"表述: **具体 minutes/hours delay 带明确 unblock 条件**, 如:
- "等 sub-agent X 回传 (预计 90 sec)"
- "等 cron 跑一轮 (下次 05:10 UTC 是 2 小时后)"

遇 blocker → 立即 atomic 拆到可执行的 minute-scale subtask 推, 不 park.
违反 → CIEU event `CEO_TIME_CONCESSION_DRIFT` + tool_use block (extend 14 ban phrase list).

### Extend hook 14 ban phrase to 20+ phrase
加入 ban list:
- "明早", "明天", "今天先", "下 session", "等到明"
- "先到这里", "先停", "再说", "等会儿"

待 Maya Edit hook.py AVOIDANCE_PHRASES list (9cd8014 + 4997d6c 同处 append).

### 20260416 — K9 patrol digest

- digest: `reports/k9_daily/20260416.md`
- findings: 11 repo-audit items
- run: 2026-04-16T06:00:00-0400
- [ ] TS3L paper: ready for external publish review
- [ ] Case study draft: AI CEO 2-session case study for Medium/GitHub publish review

### 20260422 — K9 patrol digest

- digest: `reports/k9_daily/20260422.md`
- findings: 11 repo-audit items
- run: 2026-04-22T06:00:00-0400

### 20260423 — K9 patrol digest

- digest: `reports/k9_daily/20260423.md`
- findings: 11 repo-audit items
- run: 2026-04-23T06:00:01-0400

### 20260427 — K9 patrol digest

- digest: `reports/k9_daily/20260427.md`
- findings: 11 repo-audit items
- run: 2026-04-27T06:08:18-0400

### 20260428 — K9 patrol digest

- digest: `reports/k9_daily/20260428.md`
- findings: 11 repo-audit items
- run: 2026-04-28T06:13:43-0400
