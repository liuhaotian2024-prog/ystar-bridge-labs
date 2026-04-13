# L2 派活 → CTO Ethan Wright：Memory闭环三件套

**派发**: CEO Aiden → CTO Ethan Wright
**Level**: L2（跨岗位协调，CEO自批）
**日期**: 2026-04-12
**Board授权**: 2026-04-12对话当面批准三件全部实现
**优先级**: P0（每多拖一天就多丢一段session中段认知）

## 背景

当前 agent 记忆架构存在三个致命 gap，使我们停留在"重启不丢历史"而无法升到"agent生命周期连续记忆"。详细分析见上一条 CEO ↔ Board 对话摘要。

## 必交付（三件套）

### 闭环1: CIEU → memory.db 实时 ingest（事件桥）

**目标**: 把 cron-pull 模式改为 event-push 模式

**实现要求**:
- 每条写入 `.ystar_cieu.db` 的 CIEU 事件触发判断 hook
- 判断"这是否值得记忆化" → 触发条件至少包含：
  - decision=deny 且 violation severity ≥ 0.7
  - drift_detected=1
  - event_type ∈ {insight, decision, lesson, environment_change}
  - human_initiator 非空（Board 直接干预）
- 命中触发条件 → 立即写入 `.ystar_memory.db` 对应 memory_type
- 不命中 → 不写，避免噪音

**约束**:
- 不能阻塞 CIEU 主路径（异步队列或后台线程）
- 不能在 check() 路径上引入 LLM（Iron Rule 1）
- 失败 fail-open（memory 写入失败不阻止业务）

### 闭环2: boot 时 memory_consistency_check

**目标**: 旧记忆与现实冲突时主动告警，强制 agent 确认或废除

**实现要求**:
- 在 `governance_boot.sh` 加入 STEP 11
- 扫描 `.ystar_memory.db` 中 memory_type='environment_assumption' 类型记录
- 与当前真实环境对比维度至少包含：
  - platform (uname/sys.platform)
  - cwd
  - git remote / branch
  - Python version
  - 关键路径的存在性（CLAUDE.md 里硬编码的所有路径）
- 任意维度不一致 → 输出 "MEMORY_DRIFT_DETECTED: ..." 并 FAILURES+1
- 强制 agent 在第一条用户回复前明确响应（确认废除/更新/保留）

**约束**:
- 不能因为冲突就自动改记忆（agent 必须显式决策）
- 必须可绕过（Board 在场时手动 override）

### 闭环3: continuation.json 流式更新

**目标**: 每完成一个 action_queue 项立即更新文件，session 进程被 kill 也不丢

**实现要求**:
- 在 `scripts/active_task.py` 的 complete 路径加 hook
- 每次 INTENT_COMPLETED 事件触发 → 重写 `memory/continuation.json`
- 字段同步更新：action_queue 项标 done、obligations 增减、team_state 推进
- 加 atomic write（temp file + rename），防止半写损坏
- 增加 `last_updated_ts` 字段

**约束**:
- 写入失败不阻止 active_task 主流程
- 必须 idempotent（重复 trigger 不破坏数据）

## 子任务分配建议

| 闭环 | 主负责 | 副负责 | 估时 |
|---|---|---|---|
| 1 CIEU→memory ingest | Maya (治理) | Ryan (平台) | 1 天 |
| 2 boot consistency check | Ryan (平台) | Maya (治理) | 0.5 天 |
| 3 continuation 流式 | Ryan (平台) | Leo (内核, 如有 active_task 改动) | 0.5 天 |

总工期：2 天（如串行），1 天（如并行）

## 验收标准

- [ ] 三件全部 commit + push
- [ ] 每件配 unit test + integration test，全部通过
- [ ] 在 Y* Bridge Labs 自身运行 24 小时验证：
  - CIEU 触发的 memory 写入 ≥ 5 条（自动）
  - 至少模拟一次 environment drift（改 cwd 假数据）→ boot 检测到
  - continuation.json 在 session 中段被更新 ≥ 3 次（非 session_close 触发）
- [ ] CIEU 证据归档到 `reports/cto/memory_loop_closure_evidence.md`

## 完成后汇报

CTO 完成后向 CEO 提交完成报告，CEO 24h 内向 Board 汇报结果（L2 流程）。
