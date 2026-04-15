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
