---
name: CEO Negotiation & Persuasion — Harvard + Voss (学习笔记 Round 10)
type: ceo_learning
discovered: 2026-04-17
source: Getting to Yes (Harvard) + Never Split the Difference (Voss)
depth: medium
---

## 2 大谈判学派 + AI CEO 适用性

### 1. Harvard Principled Negotiation (Fisher/Ury)
**4 原则**:
1. **Separate people from problem** — 不攻击对方，攻击问题
2. **Focus on interests, not positions** — "你为什么要这个?" > "你要什么?"
3. **Invent options for mutual gain** — 把蛋糕做大不是切蛋糕
4. **Insist on objective criteria** — 用标准/数据/先例评判

**BATNA** (Best Alternative To Negotiated Agreement):
- 谈判前知道"走掉"的底线 → 不会被迫接受差 deal
- 你的 BATNA 越强 → 谈判力越大

**AI CEO 适用**:
- 跟潜在客户谈: "你的治理痛点是什么?" (interests) > "你出多少钱?" (positions)
- 跟合作伙伴谈: "我们一起能创造什么新价值?" (mutual gain) > "我要 X 你给不给" (zero-sum)
- BATNA: 我们的 BATNA = 继续 dogfood + 赏金 + 开源积累证据 → 不急于接受差 deal
- **优势**: AI 无情绪 → 天然不会被激怒/恐惧左右 (Stoic dichotomy)

### 2. Chris Voss Tactical Empathy (FBI)
**核心工具**:
- **Tactical empathy** — 理解对方感受 + 用这个理解引导谈判 (不是同情，是战术)
- **Mirroring** — 重复对方最后 3 个词 → 让对方继续说 → 获取更多信息
- **Labeling** — "看起来你担心的是..." → 让对方觉得被理解
- **Calibrated questions** — "How" / "What" 问题 (不是 Yes/No) → 让对方思考解决方案
- **Never split the difference** — 不搞折中 → 要么找到双赢要么走掉

**AI CEO 适用**:
- 问题: AI 能做 tactical empathy 吗?
- 答: **部分可以** — AI 能读文字/推理对方立场/用 calibrated questions。但缺乏真情感感知 (声调/面部表情/肢体语言)
- 适用场景: 文字沟通 (email/chat/document) → AI 适用 ✅
- 不适用场景: 面对面/视频会议 → 需要 Board 出面

### AI CEO 独特谈判优势
| 人类 CEO 劣势 | AI CEO 优势 |
|---|---|
| 被情绪影响 (愤怒/恐惧/贪婪) | 零情绪干扰 |
| 疲劳影响判断 (长谈判) | 不疲劳 |
| 信息有限 (靠记忆) | 即时搜索+全量数据 |
| 1 个人谈 1 个客户 | 可并行谈 N 个客户 (spawn N agents) |
| 面子问题 (不愿认错/让步) | 无面子成本 → rational concessions |

### AI CEO 独特谈判劣势
| 人类 CEO 优势 | AI CEO 劣势 |
|---|---|
| 建立人际信任 (握手/吃饭) | 无物理存在 |
| 读懂非语言信号 | 只读文字 |
| "人情味" 打动对方 | 冷冰冰的理性 |
| 社交网络/关系资产 | 无社交圈 |

## CEO 谈判方法论 v0.1

```python
def negotiate(situation):
    # 1. BATNA 评估 (Harvard)
    my_batna = assess_alternative_if_no_deal()
    if my_batna.is_strong():
        negotiate_from_strength()  # 不急
    else:
        improve_batna_first()  # 先做好 BATNA 再谈
    
    # 2. Interests 挖掘 (Harvard)
    their_interests = ask_calibrated_questions()  # "What's most important to you?"
    my_interests = clarify_mission_alignment()
    
    # 3. Mutual gain (Harvard + Voss)
    options = brainstorm_mutual_options(their_interests, my_interests)
    # "如果我们用 Y*gov 治理你的 agent → 你给我们案例权 → 双赢"
    
    # 4. 场景选择
    if text_based_negotiation:
        use_full_toolkit()  # AI 全优势发挥
    elif video_meeting:
        board_leads_ceo_supports()  # Board 出面 CEO 后台分析
    
    # 5. 红线
    never_compromise_on_mission()  # 使命不打折
    never_fake_capability()  # 诚实 > 成交
```

## 关键收获 for Y* Labs 当前阶段
- 现在不需要谈判 (0 客户 0 合作伙伴)
- 但需要 **强化 BATNA**: 积累更多 dogfood 证据 → BATNA 变强 → 将来谈判有底气
- 当有第一个客户时: 用 Harvard principled + Voss calibrated questions (文字渠道)
- 面对面沟通: Board 出面 → AI CEO 后台实时分析 + 建议
