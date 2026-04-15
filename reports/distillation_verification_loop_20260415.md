# 蒸馏成果 → Agent 真实记忆 & 行为优化 Verification Loop (2026-04-15)

**Trigger**: Board 2026-04-15 问: "我们如何确定蒸馏出来的东西最后会真正成为 agent 的真实记忆和可以优化行为的能力?"

## 当前蒸馏链 (已 ship)
```
conversation JSONL
  → session_close_yml.py (YAML summary)
  → session_wisdom_extractor.py (提 key decision/lesson/pattern)
  → knowledge/{role}/lessons/*.md (归档)
  → governance/DNA_LOG.md (跨 session 凝练 DNA)
```

## 核心问题 (Board 直指)
蒸馏产出了 (lessons.md 190+ 文件, DNA_LOG 含 #001-#011), **但**:
- 没 closed-loop 验证 agent 真读 lesson?
- 没 feedback "apply 后 Rt+1 真降了吗?"
- 没 "dead knowledge" 识别 — lesson 产了没人用 = 蒸馏白费
- 没"行为优化"量化指标

## 3 层 Verification Loop 设计

### Layer 1: Lesson Usage Tracking (蒸馏 → 真读)
- 每 lesson 加 front-matter `lesson_id` (UUID)
- sub-agent boot 读 knowledge/{role}/lessons/*.md 时 emit `LESSON_READ` CIEU event (lesson_id + agent_id + ts)
- K9 daily patrol (Maya 新 rule 11?) 扫"lesson 存在但 LESSON_READ=0 over 30d" → 标 dead knowledge

### Layer 2: Behavioral Change Detection (真读 → 真改行为)
- 每 lesson 声明它针对的 anti-pattern (例: `anti_pattern: prose_claim_done`)
- CIEU events 统计"此 anti-pattern 发生率 in session" (例 Ethan 首战 prose-claim miss)
- Before vs After lesson 读: anti-pattern 率 下降? 若 N 次读后仍发 → lesson 无效 (或 hook enforce 才管用)

### Layer 3: Outcome Optimization (真改行为 → 真降 Rt+1)
- Lesson 关联"task Y* type" (finance audit / K9 scan / code review)
- 对比 lesson 读前后, 同类 task 的 Rt+1 平均值
- Rt+1 降 = lesson apply 成功; Rt+1 持平 = lesson "知识没用于决策"; Rt+1 涨 = lesson 可能误导

## 数据源
- CIEU DB (.ystar_cieu.db 今天 47064 events)
- knowledge/{role}/lessons/*.md (lesson corpus)
- governance/DNA_LOG.md (凝练的 DNA #001-#011)
- agent task Rt+1 report (每 task closure)

## 实施提案

### Phase 1 (本周): Lesson Usage Tracking
1. Samantha 改 `session_close_yml.py` + boot script 加 LESSON_READ emit
2. K9 daily patrol 加 rule 11 DEAD_KNOWLEDGE (30d 未读 lesson)
3. Telegram 第 3 类汇报: 每日"5 dead lesson + 5 high-use lesson"

### Phase 2 (下周): Behavioral Change
1. Lesson front-matter 加 `anti_pattern_id` (如 "prose_claim_done", "board_choice_question", "fail_open_silent")
2. CIEU query 统计 anti-pattern 发生率 before vs after lesson 读
3. Digest report 每周一份

### Phase 3 (下下周): Outcome Optimization
1. Lesson 关联 task type (与 Rt+1 数据 join)
2. 回归分析: lesson read → Rt+1 delta
3. Deprecate "无效" lesson (丢到 knowledge/{role}/lessons/deprecated/)

## Telegram 第 3 类汇报内容格式
```
🐕 蒸馏状态 2026-04-15
• 本周新 lesson: 3
• 读过 (≥1 LESSON_READ): 2/3 → 67%
• Dead (30d 未读): 12
• Top-3 high-use: ceo_avoidance (47), cieu_5tuple (31), secretary_override (22)
• Anti-pattern 率改善:
  - prose_claim_done: 40% → 8% ✅
  - board_choice_question: 25% → 3% ✅
• Rt+1 平均变化: -15% (task type = audit)
```

## Rt+1=0 条件 (本 design doc)
- commit hash ✓
- 3 phase 清单可 actionable 
- Board approve 后派 Samantha (Phase 1) / Maya (Phase 2 K9 rule 11) / Jordan (Phase 3 分析)

## 与 Gemma 4 API 桥关联 (Leo 同步探索)
若 Gemma 桥起, anti-pattern classifier + lesson summarization 可本地跑 (成本降 + latency 降), Phase 2/3 自动化可行性提升 10x.
