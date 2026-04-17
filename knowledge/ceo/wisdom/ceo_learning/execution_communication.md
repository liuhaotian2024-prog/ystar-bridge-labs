---
name: CEO Execution & Communication — 4DX + OKR + Board Communication (学习笔记 Round 6)
type: ceo_learning
discovered: 2026-04-17
source: 4 Disciplines of Execution / OKR / CEO Board communication
depth: deep
---

## 4DX (4 Disciplines of Execution) + Y* Labs 适用

### Discipline 1: Focus on WIG (Wildly Important Goal)
- 1-2 个最重要目标，不贪多
- **Y* Labs WIG**: M(t) = "证明 AI agent 能运营真公司" → 当前 sub-WIG = "基础建设稳到 9/10"
- **CEO 问题**: 我今天同时推了 20+ 方向 (K9 + AC + 行动模型 + 终极版 + 使命函数 + wisdom + ...) = 违反 WIG 原则
- **修正**: 每 session 只设 1 WIG，其他全排队

### Discipline 2: Act on Lead Measures (not Lag)
- Lag measure = 结果 (已发生，无法改变): "客户数 = 0"
- Lead measure = 驱动行为 (可预测+可影响): "每 session 完成 enforce smoke test 数量"
- **Y* Labs Lead vs Lag**:
  | Lag (结果) | Lead (驱动) |
  |---|---|
  | 客户数 | 每 session commit 的 evidence artifacts 数 |
  | 收入 | 产品 install 成功率 |
  | 团队能力 | 每 session gauntlet PASS + wisdom entries 数 |
  | 治理得分 | enforce fire-verified 比率 |
- **洞察**: 我一直在看 lag (客户 0! 收入 0!)，但应该看 lead (今天 evidence 增了多少?)

### Discipline 3: Compelling Scoreboard (可见记分牌)
- 团队能随时看到进度 → 投入感
- **Y* Labs scoreboard = statusline HP:NN AC:NN** → 已有! 但只有 CEO 看
- **改进**: 让 statusline 对所有 sub-agent 可见 (BOOT context 含 HP/AC)

### Discipline 4: Cadence of Accountability (问责节奏)
- 每周 accountability 会议 → 上周承诺做了吗? 下周承诺什么?
- **Y* Labs 版本**: 每 session boot → 读 session_handoff → 检查上次承诺 → 本次新承诺 → 记录
- **注意**: per no-human-time-grain 规则，"weekly" → "every session boot"

## OKR vs 4DX 对比 + 我们用哪个

| 维度 | OKR | 4DX | Y* Labs 选择 |
|---|---|---|---|
| 目标数 | 3-5 O + 3 KR each | 1-2 WIG only | **4DX WIG** (聚焦) |
| 度量 | Key Results (lag) | Lead + Lag | **4DX Lead** (可影响) |
| 节奏 | Quarterly | Weekly | **Every session boot** |
| 灵活性 | 高 (OKR 可改) | 低 (WIG 固定) | **混合**: WIG 固定 + OKR 灵活 sub-goals |

**我的选择**: 4DX 的 WIG + Lead measures 作为主框架，OKR 的灵活性作为补充。

## CEO ↔ Board 沟通方法论

从今天 session 提炼 Board 沟通最佳实践:

1. **5-tuple reply** — Board 是 dispatch sender, CEO reply = receipt (已 enforce)
2. **人话优先** — Board 不是工程师，governance jargon = 沟通 fail
3. **表格 + 数字** — Board 看一眼就懂 (不读段落)
4. **诚实 push back** — Board 要 CEO 反驳不只执行 (System 5 not relay)
5. **提案 not 选择题** — CEO 给 1 recommendation + execute, 不给 3 options

## CEO 执行方法论 v0.1

```python
def execute_session():
    # 1. WIG check (4DX Discipline 1)
    wig = read_session_handoff().current_wig
    assert count_active_goals() <= 2, "too many goals, focus on WIG"
    
    # 2. Lead measures (4DX Discipline 2)
    lead_measures = [
        "enforce_fire_verified_count",
        "wisdom_entries_added",
        "evidence_artifacts_committed",
        "cto_autonomous_actions"
    ]
    for m in lead_measures:
        track(m)  # 每 session 结束时报 lead measure delta
    
    # 3. Scoreboard (4DX Discipline 3)
    # HP:NN AC:NN in statusline = live scoreboard ✓
    
    # 4. Accountability (4DX Discipline 4)
    last_session_commitments = read_session_handoff().commitments
    for c in last_session_commitments:
        verify(c)  # 上次说的做了吗?
    this_session_commitments = derive_from_wig()
    save_to_handoff(this_session_commitments)  # 这次说的下次验
```
