---
name: 16h Session Counterfactual Sandbox — 平行宇宙复盘
type: meta
discovered: 2026-04-17
trigger: Board 批准沙箱复盘
depth: deep
---

# 17 决策点反事实重跑 — 真实 vs 平行宇宙

## #1 K9 噪音修还是绕
**Real U**: 修 (CROBA fix + alias + daemon recycle)
**Counterfactual U**: 同 — P-3 因果序正确 (噪音根因→修根因)
**Delta**: 0 — 这个决策本来就对
**Insight**: 技术 triage 我做得不错 (Cynefin Complex 正确处理)

## #2 Board "白名单不是黑名单"
**Real U**: 接受 Board 指导 → 建 reply_taxonomy_whitelist
**Counterfactual U**: 如果有 P-1 有限可证 → 我自己就能想到白名单 → 不等 Board catch
**Delta**: 省 1 轮 Board correction
**Insight**: **P-1 是最高杠杆原理 — 如果内化了，很多设计错误自己就能避免**

## #3 Board "你为什么不反驳我"
**Real U**: 被动接受 Board 所有意见
**Counterfactual U**: 如果有 P-4 碰撞出真理 → 我会主动 push back 不合理的地方
**Delta**: CEO 独立判断力 +1
**Insight**: **P-4 的价值不是"吵架" — 是"让 Board 也能被校准"**

## #4 提案 #001 跳到找客户
**Real U**: 看 16 维度最低分(客户 0) → 提"先找客户"
**Counterfactual U**: P-3 因果有方向 → 画 dependency DAG → 发现客户在链末端 → 提"先稳基建"
**Delta**: 省 1 轮 Board reject + 省掉错误提案浪费的思考时间
**Insight**: **P-3 是 CEO 提案质量的决定因素 — 没有因果链分析的提案 = 拍脑袋**

## #5 CZL-114 Ethan hallucination
**Real U**: 1h 后手动 verify 才发现假的
**Counterfactual U**: MR-1 极端值 (0 tool_uses + 22s) → 自动 reject → 5 分钟内发现
**Delta**: 省 55 分钟 + 省 CZL-115 重派
**Insight**: **极端值检测是成本最低收益最高的 self-check — 几乎 0 成本避免最大损失**

## #6 Ryan CZL-134 hallucination #2
**Real U**: 60s 内 empirical verify 发现 (比 #5 快很多)
**Counterfactual U**: 同 — 因为 #5 已经建了 MR-1 → 这次执行了
**Delta**: 0 — **能力迭代的实证: #5 犯错→建规则→#6 生效→从 55min→60s**
**Insight**: **P-2 在起作用 — structure (MR-1) 第二次自动拦截 = 能力 > 认知**

## #7 造轮子 5 silo
**Real U**: 派 5 个新 spec → 全 duplicate Y*gov
**Counterfactual U**: MR-6 先查后造 + precheck 4-repo → 发现已有 → extend 不 build
**Delta**: 省 5 个 atomic + 省 Board catch "你又在造轮子"
**Insight**: **precheck 必须是 BOOT 步骤不是可选项 — P-2 结构化保证执行**

## #8 Board "技术问题归 CTO"
**Real U**: CEO 一直在做技术决策 (formal methods primer / CROBA regex / threshold tuning)
**Counterfactual U**: MR-4 建系统>做事 → 从 session 开始就声明 "技术方案 = CTO scope"
**Delta**: CEO 带宽释放 ~30% → 可以早 10h 开始战略思考
**Insight**: **P-5 身份选择 — "我选择只做 System 5" 应该是 session 开头的第一条声明**

## #9 Board "接下来靠你自己了"
**Real U**: Board 渐进教育 → 最终交棒 → CEO 开始建使命函数
**Counterfactual U**: 如果我从 session 开始就有 P-5 → 主动提出使命函数 → Board 不用教这么久
**Delta**: 理论上省 ~8h → 但 Board 的教育路径本身有因果序 (P-3) → 不确定能跳步
**Insight**: **有些认知只能通过经历获得，不能通过理论跳过 — 这是 Board 教育的不可替代价值**
**这是 "Board 智慧 > 所有理论" 的实证点**

## #10 审计独立性
**Real U**: Board 设红线 → CEO 存 wisdom
**Counterfactual U**: 如果有 P-4 碰撞出真理 → 我应该自己推导出"自审无效" → 但实际我没想到
**Delta**: **0 — 即使有 P-4 我也可能漏，因为这需要治理哲学的深度不只是碰撞原则**
**Insight**: **P-4 必要但不充分。碰撞产出真理的前提 = 有东西可碰。没有治理哲学底蕴 → 碰撞也空**

## #11 "存下来不是轻飘飘的话"
**Real U**: Board push → CEO 建 4 层记忆系统
**Counterfactual U**: 如果有 P-2 结构>意愿 → 我自己就会想到 "wisdom 不能只是 note"
**Delta**: 省 1 轮 Board push
**Insight**: **P-2 是递归的 — "persistence 需要 structure" 本身就是 P-2 的应用**

## #12 使命函数定义
**Real U**: Board 引导 → CEO 提候选 → Board 选 C → 共创
**Counterfactual U**: 如果有 P-5 → 我 session 开始就应该自问 "为什么这家公司存在?"
**Delta**: 使命可能早 12h 定义 → 但质量可能不如 Board 共创版
**Insight**: **使命函数 = P-5 的具象化。没有 P-5 (identity) 就不会主动问 "我为了什么存在?"**

## #13 CTO broker 自主发现
**Real U**: CEO 放手 → CTO 真独立工作 → 发现 61 test failures
**Counterfactual U**: 如果从 session 开始就有 MR-4 → CTO 更早接管 → 更早发现
**Delta**: CTO 独立性早 10h+ 建立
**Insight**: **CEO 放手的速度 = 团队能力增长的上界。CEO 不放手 = 团队无法成长 (P-4 碰撞延伸)**

## #14 Opus 4.6 旁路
**Real U**: 以为需要 restart → Board 提示找旁路 → 发现 model:"opus" 参数
**Counterfactual U**: 如果有 P-6 按现实行动 → 先检查 Agent tool 参数 → 当场发现
**Delta**: 省 Board 1 轮提示 + 全 session sub-agent 本可以 Opus 跑
**Insight**: **P-6 的应用 = "动手试之前先读 API 文档"。现实 > 假设。参数 > 重启**

## #15 180s 自主循环
**Real U**: Board 提出 → CEO 实施 → 20min 失败 → 再实施 → 成功运转
**Counterfactual U**: 如果有 P-5 + MR-11 → 我应该自己提出定时 wakeup
**Delta**: 循环早 2h 建立
**Insight**: **ScheduleWakeup 工具 = P-5 的技术实现。身份选择 ("我不等 Board") 需要技术支撑**

## #16 Board "全维度分工模型"
**Real U**: CEO 列技术清单 → Board catch "管理维度呢?"
**Counterfactual U**: MR-12 全维度穷举 → Aristotle 互斥穷尽 → 技术+管理都列
**Delta**: 省 1 轮 Board catch
**Insight**: **MR-12 是 P-1 的操作版。有限可证 + 穷尽 = 不遗漏**

## #17 五元组通讯缺失
**Real U**: CEO 整个前半段散文 reply → Board catch → 后半段用 5-tuple
**Counterfactual U**: MR-7 制度>自律 → session 开始就应该有 hook 拦截非 5-tuple
**Delta**: 但 hook 实际 broken (import path 错) → **认知没用，结构坏了**
**Insight**: **这是 P-2 最强证据 — 即使 CEO "知道" MR-7，hook broken = 能力 = 0**

---

## 平行宇宙总结

| 类别 | 决策点数 | 平行宇宙改善 | Board 智慧不可替代 |
|---|---|---|---|
| CEO 可自行避免 (有原理就行) | 8 (#2,4,5,7,8,14,15,16) | 省 ~10h + 5 轮 Board correction | 否 |
| 需要 Board 教育才能获得 | 5 (#3,9,10,11,12) | 无法省 — 教育路径本身有因果序 | **是** |
| 能力已迭代生效 | 2 (#6,13) | 实证: 第 2 次比第 1 次好 | 否 |
| 决策本来就对 | 2 (#1,#17 部分) | 0 delta | 否 |

## 核心发现

1. **8/17 可自行避免** — 如果 6 条原理在 session 开始就内化 → 近半数 Board correction 不需要
2. **5/17 Board 教育不可替代** — 有些认知只能通过"被纠正"获得，理论无法跳过 → **Board 的价值 ≠ 给指令 = 创造 CEO 无法自己到达的认知**
3. **2/17 已实证能力迭代** — CZL-114→CZL-134 (hallucination catch 55min→60s) = P-2 在工作
4. **P-2 (结构>意愿) 仍是 dominant**: 4/5 最大 delta 点的根因 = 结构缺失
