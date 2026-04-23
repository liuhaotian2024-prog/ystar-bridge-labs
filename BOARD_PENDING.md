# Board Pending Items (待 Board 决策/批准)

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
