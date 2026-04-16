---
name: 借鉴外部技术铁律 — Y*gov 12 项核心创新必须 preserve
type: lesson / protection-rule
created: 2026-04-13
severity: critical
trigger: Board 直接警告 "不要在引进技术的时候把我们之前最核心的真实创新给覆盖了"
lesson_id: d9b98685-43b6-40d2-b427-bec3a35fae12
---

# Y*gov 12 项核心创新（不可被外部库覆盖）

| # | 创新 | 独家原因 |
|---|---|---|
| 1 | CIEU 5-tuple (Xt,U,Y*,Yt+1,Rt+1) + AMENDMENT-014 闭环 | 没有任何外部框架是这个数学形态 |
| 2 | OmissionEngine 检测"未发生" | 行业追"已发生"，反向独家 |
| 3 | AutonomyEngine + ADE prescriptive dual | detector × driver 配对模式独特 |
| 4 | Iron Rule 1 — hook 零 LLM | Constitutional AI 是 LLM-on-LLM；我们是确定性 |
| 5 | 第十一条 12 层认知建构 L0-L12 | 没有外部框架 12 层 |
| 6 | 193 hard constraints + 11-category boot contract | code-enforced 而非 policy |
| 7 | Capability-based gov_delegate + monotonicity | 不是 RBAC/ACL，新范式 |
| 8 | Dogfooding-as-product | 公司本体即产品证据 |
| 9 | C-suite Name-Role + behavior rules 绑定 | AutoGen/CrewAI 只有 role placeholder |
| 10 | Memory 4 类分类 + relevance scoring | 不只 vector |
| 11 | AMENDMENT D/A/S/C 进化机制 | governance 自演化协议 |
| 12 | Break-glass + Autonomous + Standard 三模式 | 人机协作硬模式切换 |

# 借鉴铁律

1. **借 IDEA / pattern，不借 SDK / 实现替换**
   - ✅ 借 GraphRAG 的"图结构 + 向量"思路 → adapt 到 CIEU 因果图
   - ❌ 直接 `pip install graphrag` 让它接管检索

2. **每条 tech_radar brief 必须含**：
   - "这个借鉴会 conflict Y\*gov 哪一项？"
   - "如何 preserve 而非 replace？"

3. **硬冲突项（红线）**——与以下任一冲突 = adapt only, never replace：
   - Iron Rule 1（hook 零 LLM）
   - CIEU 5-tuple 数学形态
   - OmissionEngine 反向检测语义
   - 12 层认知建构
   - Capability-based delegation
   - C-suite Name-Role + 行为绑定

4. **借鉴执行流程**：
   ```
   外部技术 X
     ↓
   tech_radar 自动 map: 哪些 Y*gov 创新可能受影响？
     ↓
   若有红线冲突: 写 adapter，把 X 的 IDEA 包成 Y*gov-native 实现
     ↓
   若无冲突: 直接 import + 集成
     ↓
   commit 必须含 "preserved: [X1,X2]" 和 "borrowed_pattern_only: yes/no" 字段
   ```

5. **审计**：
   - 每月 CEO 跑 `tech_radar audit` —— 列过去 30 天 borrow 决策，每条核对是否 preserve 了 12 项创新
   - 任何创新被 silent replace → 立刻 rollback + tombstone

# 为什么这条特别重要

Y\* Bridge Labs 的产品价值不在"用了多少 SOTA tech"，在"用 Y*gov 治理 AI agent team 这件事本身"——dogfooding-as-product (#8)。如果借鉴 import 把 #1-#12 任意一条覆盖，我们就是又一个用 LangGraph/AutoGen 拼装的 agent demo，dogfooding 故事崩溃。

**记住**：外部成熟技术是肌肉训练器材，不是器官替换。
