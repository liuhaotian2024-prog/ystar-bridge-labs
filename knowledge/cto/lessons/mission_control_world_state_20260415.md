# Lesson: Mission Control WORLD_STATE Pattern (2026-04-15)

## Context
Board 指出 CEO tunnel-view 错误（propose 全新 v3 Guardian，90% 已存在）。Board 建议创建 Mission Control 单文件整合层，避免 CEO 每次 boot 读 5+ 文件。

## Pattern: Single Wakeup Context File

### Problem
- CEO boot 时需读 `priority_brief.md` + `active_task.json` × 10 + `.czl_subgoals.json` + `wire_integrity` + CIEU DB + `BOARD_PENDING.md` = 15+ file reads
- Context window 浪费 → 重要信号淹没

### Solution
- `memory/WORLD_STATE.md` — 单文件自动整合 7 段（公司战略 / 各条线状态 / Campaign 进度 / 系统健康 / 外部信号 / Board pending / reserved）
- `scripts/generate_world_state.py` — crontab 每 30min 自动更新
- `hook_session_start.py` PRIORITY 0 注入 — 所有 agent boot 时第一个读到的 context

### Implementation (60b1fbd0)
- `generate_world_state.py`: 150 lines, 7-section aggregator
- Crontab: `*/30 * * * * cd repo && python3 scripts/generate_world_state.py`
- Hook injection: `_append_world_state()` prepend before C7 Conversation Replay

### Rt+1 (Honest Gaps)
1. Wire integrity check 未输出 total_issues 到 stdout → 脚本无法解析
2. CIEU 24h query 失败（table name mismatch: `cieu_events` vs actual schema）
3. Board Pending 输出完整 237 lines → 应截取前 20 + count
4. E2E boot 验证待下 session（hook 注入未真实测试）

### Generalization
**Vogels "Single Pane of Glass" Principle** — operational dashboards 必须单一入口，否则 on-call 工程师夜里醒来需拼 5 个监控页面才能判断事故等级 = 系统设计失败。

**Application to AI agents**: Session boot = on-call wakeup. 单文件 context > 多文件拼图。

### Next Steps
1. 修 3 个 Rt+1 gaps（10 min）
2. 下 session 验证 hook E2E
3. 推广到其他 C-suite agents（CMO/CSO/CFO 各有自己 WORLD_STATE 视角）

---
**Author**: CTO (Ethan Wright)  
**Source commit**: 60b1fbd0  
**Related**: reports/cto/hiagent_czl_integration_design_20260415.md (HiAgent working memory 压缩 — 相同思路)
