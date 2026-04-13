# DISPATCH: First-Turn Ritual + Autonomy Drive Root-Cause Fix

**Authority**: Board 2026-04-13, 第十一条全自主
**Owner**: Ethan-CTO (dispatch) → Ryan-Platform / Maya-Governance / Leo-Kernel
**Deadline**: EOD 2026-04-14
**Trigger**: Restart 2026-04-13 达成率 ~55%（首轮 ritual miss + CEO 线空转等催）

## Root Causes (Board-verified)

1. **G1** first-turn contract 埋在 YAML，boot 不 parse，CEO 不强制执行
2. **G2** Sofia-CMO subagent 不存在，4 并行合同底层不可满足
3. **G3** autonomy_engine 主动路径只靠 idle timer，boot → first turn 之间无触发
4. **G4** Marco-CFO subagent 报 governance permission block（未诊断）
5. **G5** sub-agent 无 "worker report only" 框架默认写长报告
6. **G6** ritual 合同双 source of truth（governance_boot.sh 硬编码 + priority_brief.md YAML）

## Fixes

### FIX-1 [Ryan-Platform] first-turn contract 单一 source + 硬 enforce
- `governance_boot.sh` 删除硬编码字符串，改为从 `priority_brief.md` today_targets 解析 `first_turn_contract` 字段（新增）
- `priority_brief.md` schema 扩展：`first_turn_contract: { trigger, response_exact, parallel_spawns[] }`
- Hook: CEO 第一条 assistant response 发出后，hook 扫描 response 是否包含 `response_exact` 字符串——缺失 → 写 CIEU violation + P0 obligation "ritual_failed"
- Accept: next session `重启` → 不说 "Aiden" 时不触发；说 "Aiden" 时 CEO 必答精确字符串，否则 CIEU 记录 violation

### FIX-2 [Ryan-Platform] Sofia-CMO subagent 定义
- 方案 A（推荐）：`.claude/agents/Sofia-CMO.md` 新建，参照现有 Zara-CSO/Marco-CFO 结构
- 方案 B：改合同 "4 C-suite" → "3 C-suite + CMO 文件轮询"
- 决策：Ethan 选 A 或 B，commit 后更新 priority_brief.md
- Accept: 下次 ritual spawn Sofia-CMO 不报 subagent_type not found

### FIX-3 [Maya-Governance + Leo-Kernel] boot → autonomy_engine.pull_next_action
- `_hook_daemon.py` 新 hook: `on_session_start`（governance_boot.sh 已 emit CIEU `session_start` event——接上这个事件）
- Handler: parse `priority_brief.md` today_targets → 对每个 owner != ceo 的 target emit dispatch intent 到 `.claude/tasks/`；对 owner == ceo 的 target 写 `memory/ceo_first_turn_queue.md`（CEO boot 后必读）
- 同时：CEO 每回合结束新 hook `on_ceo_turn_complete`——evaluate: 本回合有 obligation advance 吗？无 → emit `OFF_TARGET` event → autonomy_engine 强制 propose next action
- Accept: restart 后 CEO 第一回合即执行 today_targets 队列，不空转；空转 1 回合自动触发 OFF_TARGET

### FIX-4 [Ryan-Platform] Marco-CFO governance block 诊断
- Reproduce: Agent subagent_type=Marco-CFO, prompt 最小集
- 查 hook daemon 日志 + `.ystar_session.json` restricted_paths
- 修 root cause，不要 workaround
- Accept: Marco-CFO sub-agent 在 ritual 中能正常回 online check 一句话

### FIX-5 [Ryan-Platform] sub-agent prompt 模板
- 每次 Agent 调用自动注入 "worker report only. commit hash + tests x/x pass 一句话。禁止写 Board 格式长报告。" header
- 实现方式：Agent wrapper skill 或 boot 时写入 `.claude/agent-prompt-prefix.md`
- Accept: 下次派 sub-agent 默认返回 <50 字

### FIX-6 [由 FIX-1 自动解决] 合同单 source

## Reporting
每修一项立刻 commit + 一句话 status 进 `reports/ritual_autonomy_fix_log.md`。
完工总报一次。不要 Board 格式长文。
