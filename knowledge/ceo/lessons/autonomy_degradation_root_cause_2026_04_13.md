---
name: 自驱力退化 7 因诊断 + Autonomy Driver Engine 提议
type: lesson / strategic-diagnosis
created: 2026-04-13
severity: critical
trigger: Board 2026-04-13 直接质询 "团队自驱力和自主性深度思考立刻行动的能力退化的严重"
framework: AMENDMENT-007 第十一条 7 层
lesson_id: 528a67ad-8025-4277-946f-aab2e369cbb7
---

# 7 个真因（按因果深度）

1. **CEO 把"问 Board"当避险机制**——每次 ask 是决策肌肉萎缩，规则可以拦"出现选择题"但拦不住"反射式推回 Board"
2. **没有 goal gradient**——priority_brief 描述当前阶段，不规定 daily/weekly target → CEO 无 self-direction 锚点
3. **OmissionEngine 是 detector 不是 driver**——检测 gap，不生成 next-action（Board 说的"对照表"的更深层）
4. **CIEU 描述性 ≠ 处方性**——记录"发生了什么"，不输出"接下来该做什么"
5. **Sub-agent 做完即退**——不携带状态，所有 initiative 堆 CEO 头上，SPOF
6. **Governance 递归陷阱**——今晚 12 commit / 11 是 meta-governance，1 是 product-shape
7. **缺"无活主动找活"硬约束**——agent 默认"等指令"而非"扫 backlog 自取"

# 解：Autonomy Driver Engine (ADE)

```
OmissionEngine (backward / descriptive)
       ↓ feed →
ADE (forward / prescriptive)
   • 输入: priority_brief.daily_target + role + obligation backlog + role 能力清单
   • 输出: 每 agent 的 next-N action queue (含 why + verify + on_fail)
   • 注入: boot_packages.category_11_action_queue
```

# 关键设计
- **goal gradient 化**：priority_brief 强制含 `today_targets[]` / `this_week_targets[]` / `this_month_targets[]`
- **每 N 分钟自检 OFF_TARGET**：当前 agent 在做的不在 daily_target → warning + pull next
- **idle-pull**：static silence 5 min → 自动 pull 不等
- **orphan-claim**：无 owner obligation 自动按 role-mapping 派

# 与现有提案集成
- AMENDMENT-013 proactive skill activation = 教学层
- Maya obligation fulfiller contract = 兑现层
- ADE = 驱动层
- 三者合 = 完整自驱力闭环

# 行为约束（codify）
- `autonomy_self_check_every_5min`：CEO session 静默 5 min 自动从 action_queue pull 下一活
- `forbidden_choice_question_reflex`：检测到自己写"要 X 还是 Y"立即删除并自决
- `daily_meta_to_product_ratio`：当日 commit 中 product/customer-facing 必须 ≥ 50%（否则 warning）
