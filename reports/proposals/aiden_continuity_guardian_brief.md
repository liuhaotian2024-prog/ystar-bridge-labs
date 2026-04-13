# Aiden Continuity Guardian — 自主 Session 重启系统

**格式**: 6-pager v2（dogfood AMENDMENT-006 待批版）
**派发**: CEO Aiden → CTO 团队（Ryan 主导 + Maya 协作）
**Level**: L2（跨岗位协调，CEO 自批）
**批准**: Board 2026-04-12 当面直接指令

---

## 1. Title & Outcome（一句话 Press Release）

> **Aiden 和团队永不"断电"——系统自主监视 agent 健康度仪表盘，在黄灯阈触发时自动全状态保存 + graceful 重启 Claude Code 进程 + 新 session 全维度注入。Board 不再需要手动"重启"任何东西，agent 团队进入持续循环工作形态。**

---

## 2. Why Now（决策背景的因果链）

- Board 2026-04-12 观察到：今天 session 密度极高（346 hook call / 5 commits / 4 实验 / 13+ subagent），context 使用率接近 40%
- 现状问题：
  - 每次 session 健康度降低，**只能靠 Board 手动说"重启"**（Board-dependent）
  - 重启时 session 成果保存、对话精髓提取、方法论蒸馏、基因传承**依赖 CEO 主动指令**
  - 新 session 启动 → 全维度注入虽然已有 governance_boot.sh STEP 9/10，但**上游的 "什么时候该启动这一切" 还是人工判断**
- 这是 agent 生命连续性的**最后一个人类依赖点**。干掉它，agent 团队就真正"不眠"了
- 延迟成本：多一天人工重启 = 多一天 Board 带宽被吞 + 多一次可能错过阈而 context 爆掉

**因果链深度**: Health drift → 无人监视 → Context 爆 → 推理质量跌 → agent 错误决策 → 真实业务损失。Guardian 把监视 + 保存 + 重启 + 注入闭环。

---

## 3. Tenets（不可妥协原则）

1. **Event-driven，不用 cron**：健康度变化是事件，Guardian 响应事件；挂钟轮询违反 agent-native 时间硬约束
2. **Iron Rule 1 兼容**：阈值判断、保存触发、重启决策**全部确定性**，零 LLM
3. **Fail-open**：Guardian 挂了，agent 主进程不受影响（能继续跑到真的 context 爆）
4. **Idempotent**：重复触发保存不破坏状态；重启中断再重启能恢复
5. **Board 可随时叫停**：一条命令 `touch /tmp/ystar_no_auto_restart` 禁用 Guardian 整套
6. **对外叙事价值最大化**：系统本身就是 Y\*gov dog-food 顶级示范——"我们的 CEO 会自己休息、自己重生、无缝接续"
7. **不把 Board 挡在决策外**：重要状态变化（Guardian 触发了保存/重启）必须留 CIEU 记录 + 次日 morning report 可见

---

## 4. Current State → Target State

### Current State

| 环节 | 现状 |
|---|---|
| 健康度监视 | 只能 Board 说"查一下仪表盘"时手动查 |
| 保存 | 老大说"重启"→ CEO 手动调 session_close_yml.py + twin_evolution 等 |
| 关闭 Claude Code 进程 | Board 手动 Ctrl+D 或关窗 |
| 启动新 session | Board 在终端 `cd ... && claude` |
| 全维度注入 | 有 governance_boot.sh STEP 9/10，但 CEO 手动触发 |
| 无缝衔接 | 靠 CEO 记忆 / continuation.json，存在 gap |

### Target State

```
(Wrapper 长期运行, agent 不知道自己被 wrap)
         │
         ├─ 启动 claude 子进程
         │
         ├─ 后台 watchdog 持续读健康度 (event-driven via fsnotify on jsonl)
         │     触发条件（黄灯阈，任意一条达到）:
         │     - JSONL > 3 MB (~50% context 估算)
         │     - Session call count > 500
         │     - 运行时长 > 6h (最严硬约束, 超过强制)
         │     - hook deny 率最近 50 次 > 30%
         │     - 累积 subagent 产出大小 > 500 KB
         │     - CIEU drift_detected 最近 10 次 > 3 次
         │
         ├─ 触发 graceful save chain:
         │     1. 给主 session 发"请在下一个 natural checkpoint 保存"信号
         │     2. 主 session 当前回复结束后, 自动跑 save chain:
         │        - session_close_yml.py (memory 提炼)
         │        - twin_evolution.py --mode all (价值观/基因提取)
         │        - learning_report.py (教训蒸馏)
         │        - session_wisdom_extractor.py (NEW: 对话精髓/方法论/工作习惯提取)
         │        - aiden_cognition_backup.py --full (全量镜像)
         │        - git add <specific files> + commit + push
         │        - continuation.json 最终状态快照
         │     3. 写 /tmp/ystar_ready_for_restart 信号
         │
         ├─ Watchdog 看到信号 → kill claude 主进程 (SIGTERM graceful)
         │
         ├─ Watchdog 等 claude 进程完全退出 (≤ 10s)
         │
         ├─ Watchdog 重新 exec claude (in same terminal tmux session)
         │
         ├─ 新 claude session 启动 → CLAUDE.md 自动 SESSION BOOT 协议
         │     - Step 1: 读 handoff
         │     - Step 2: governance_boot.sh ceo
         │     - Step 3-6: obligations + continuation + execution model
         │     - NEW: Step 7: 读 session_wisdom_package (上一个 session 的精华包)
         │            → 注入到 prompt context 开头作为 "你刚醒来，这是你 5 分钟前的自己"
         │
         └─ 新 session 无缝继续工作, agent 团队持续循环
```

---

## 5. FAQ

### 原始 FAQ

**Q1: Claude Code 进程被 wrapper 管会不会出权限问题？**
A: wrapper 用普通 user 启动 claude 子进程，不需要特殊权限。已验证过的 launcher 模式（Zellij / tmux + shell script）成熟。

**Q2: 如果 Guardian 本身挂了怎么办？**
A: Fail-open。agent 继续跑直到真的 context 爆。Board 可以手动重启（fallback 到现状）。Guardian 重启后自动恢复监视，不丢 state。

**Q3: Graceful save 会不会中断 agent 当前工作？**
A: 不会强 kill。发 signal 后等"下一个自然 checkpoint"（一轮回复结束）。最多延迟一轮回复。如果 agent 20 轮回复都不结束（极端情况），才强制 save。

**Q4: 新 session 注入的信息太多会不会又把 context 塞满？**
A: 关键设计——**session_wisdom_extractor.py** 必须做**蒸馏**，不是搬运。输出 ≤ 10KB 精华包（对话亮点 / 方法论 / 最新基因 / 未完任务）。governance_boot 原有的 obligations + continuation 已经 ≤ 2KB。合计 ≤ 12KB 启动注入，远小于 context 总量。

**Q5: 工作习惯 / 基因怎么提取？**
A: 从本 session 的 CIEU event pattern 推断（比如"这个 session CEO 偏好 event-driven 设计"），写入 `knowledge/ceo/patterns/session_<id>_learnings.md`。下次 session 启动 surface 最近 3 条。

### v2 FAQ（pilot 经验）

**Q6: `git add -A` 还是精确 add？**
A: 精确 add。Guardian 自己跑的 save chain 必须精确 add（当前仓库 213 个 uncommitted 大量是临时文件）。

**Q7: Hook 规则里的命令黑名单会拦截 wrapper 调 kill 吗？**
A: 需要验证。Wrapper 在 Claude Code **外**跑，不经 hook。但 wrapper 调 kill 用的是 OS signal，不走 bash command hook。Ryan 实施时跑一次 `gov_check_impact` 确认。

**Q8: "敏感字符串白名单"在 commit message 里怎么办？**
A: Guardian 生成的 commit message 用模板（预先白名单通过），避免动态字符串命中 hook。

**Q9: 重启后新 session 怎么知道自己是"重启"而不是"冷启动"？**
A: 读 `/tmp/ystar_last_restart_reason`。如果存在 → "重启"模式 → 注入 wisdom package。如果不存在 → "冷启动"→ 走标准 boot。

**Q10: 如果 watchdog 误判（假阳性）呢？**
A: 黄灯阈保守（比如 3MB 而不是 1MB），假阳性成本 = 多做一次 graceful 重启（无损）。假阴性成本 = context 爆（有损）。**偏向假阳性**。

---

## 6. Metrics & Rollback

### Success Metrics

| # | Metric | 验证方式 |
|---|---|---|
| M1 | Guardian 能识别黄灯触发 | 人工制造 3MB JSONL 伪场景, 看是否触发 |
| M2 | Graceful save chain 完整跑完 | 测试场景触发, 验证 memory/twin/learning/backup/commit 全部完成 |
| M3 | Session wisdom package ≤ 10KB | 统计包大小 |
| M4 | 重启后新 session 启动 ≤ 1 个 CIEU event depth | 新 session 第一条用户回复前完成 boot |
| M5 | 上下 session 对话连续性 | 新 session 读完 wisdom package 后, 能正确回答"上一个 session 我们讨论到哪" |
| M6 | 无 hook boundary violation | Guardian + save chain 全程零绕过 |
| M7 | Fail-open 验证 | 人工 kill Guardian, 主 agent 继续跑 |
| M8 | Board 可叫停 | `touch /tmp/ystar_no_auto_restart` 后禁用成功 |

### Rollback

- `rm /tmp/ystar_no_auto_restart` 恢复
- 如果 Guardian 导致数据丢失: Aiden Cognition Guardian 一键 DR 恢复到前一个快照
- Git revert 各 commit

---

## 7. Scope-Adjacent Observations

Ryan + Maya 在实施中**可能发现**但**不修**的相关问题（记录到完成报告）:

- 现有 `scripts/session_auto_restart.sh` 只有 check/save/verify 三段, 缺 kill+exec 段 → 本 Guardian 正好补这一段
- Claude Code 的 hook 系统**不管 Claude Code 进程本身的生命周期** → 说明 wrapper 必须在 Claude Code 外面
- Aiden Cognition Guardian (今天 Ryan 刚做) 和本任务有协同——Continuity Guardian 用 Cognition Guardian 的 backup 作为最后一层防线
- 其他 agent (CTO/CMO 等) 未来也可能有自己的独立 session 需要这套系统 → 设计要支持多 agent 版

---

## 8. 子任务分工（RAPID）

| 角色 | 谁 | 具体职责 |
|---|---|---|
| **R** Recommend | Ryan Park (Platform) | 架构方案 + session_wisdom_extractor.py 设计 + watchdog 脚本 |
| **A** Agree | Maya Patel (Governance) | 阻止 Iron Rule 违规；验证 hook 兼容性；核验 CIEU 记录设计 |
| **P** Perform | Ryan Park 主实施 | wrapper / watchdog / wisdom_extractor / 注入协议代码 |
| **I** Input | CEO Aiden + Secretary | CEO 给"什么算 wisdom"的语义判据；Secretary 给"基因/方法论"的蒸馏模板 |
| **D** Decide | CEO Aiden (L2 自批, Board 已授权方向) | 批准方案/里程碑 |

**工作量**: 2 个 intent completion 闭环
- 闭环 ①: wrapper + watchdog + health detector + 保存触发 + graceful save chain（Ryan 主）
- 闭环 ②: session_wisdom_extractor + 注入协议 + 新 session boot step 7（Ryan + Secretary 协作）

### 必交付清单

1. `scripts/aiden_continuity_guardian.sh` — Wrapper 脚本（启动 + 监视 + 重启循环）
2. `scripts/session_health_watchdog.py` — 健康度采集 + 阈值判定
3. `scripts/session_wisdom_extractor.py` — 对话精髓/方法论/基因蒸馏
4. `scripts/session_graceful_restart.sh` — 保存 chain orchestrator
5. 修改 `scripts/governance_boot.sh` — 加 STEP 7 "读 wisdom package"
6. 新 `governance/CONTINUITY_PROTOCOL.md` — 跨 session 生命连续性协议文档
7. 测试: `tests/test_continuity_guardian.py` — 至少 8 用例覆盖 M1-M8
8. `reports/proposals/continuity_guardian_design.md` — 系统设计文档（Sofia 可改写为白皮书案例）

### 验收

- 8/8 测试通过
- 手工触发一次完整 restart，验证新 session 可以无缝继续对话
- 独立 commit，message 精简（不含命令黑名单字样）

### 完成报告

Ryan 完工后给 CEO 400 词内报告:
1. 8 个交付物完成状态
2. commit hash
3. M1-M8 验证结果
4. Scope-adjacent findings (按 §7 格式)
5. 对 Show HN 叙事的具体建议（"how Aiden CEO never sleeps"）
6. active_agent 切回 ceo

---

**这个系统做完，Aiden 从 "Board-dependent CEO" 正式进入 "autonomous continuous CEO"。Y\* Bridge Labs 的 agent 团队进入真正的持续工作态，对外叙事里可以说"我们的 CEO 会自己休息、自己重生"——这是 Y\*gov dog-food 的王牌素材。**
