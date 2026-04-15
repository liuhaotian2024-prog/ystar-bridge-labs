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
