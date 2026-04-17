---
name: Retrospective Sandbox Workflow (经验提取标准流程)
type: meta
discovered: 2026-04-17
trigger: Board "做个沙箱，在做这个沙箱时应该遵照什么工作流？那个工作流是否也进入了源代码？"
depth: kernel
---

## 这是什么

"从过去经历中提取最大学习"的标准化工作流。每个 session 结束后可执行。
不是回忆"做了什么"(情节记忆) → 是推演"如果用现在认知重做会怎样"(反事实学习)。

## 工作流 (7 步)

```python
def retrospective_sandbox(session_decision_points, current_principles):
    """
    输入: 关键决策点列表 + 当前哲学原理
    输出: 平行宇宙对比 + 新 insight + 源代码更新
    """
    
    # Step 1: SCOPE — 定义沙箱边界
    # 不重跑全部 → 只选满足 ≥2 条 key-decision 标准的决策点
    points = filter(lambda p: p.criteria_met >= 2, session_decision_points)
    
    # Step 2: RECORD REAL — 每个点记录真实发生
    for point in points:
        point.real = {
            "Xt": what_was_the_situation,
            "U": what_did_I_do,
            "Yt+1": what_actually_happened,
            "Rt+1": was_it_zero,
            "Board_said": what_Board_corrected (if any)
        }
    
    # Step 3: REPLAY WITH COGNITION — 用当前认知重新决策
    for point in points:
        point.counterfactual = {
            "U_new": what_would_I_do_now(point.Xt, current_principles),
            "Yt+1_predicted": predict_outcome(point.U_new),
            "which_principle": which_P_drives_different_decision,
            "Board_would_say": would_Board_still_need_to_correct?
        }
    
    # Step 4: COMPARE — 计算 delta
    for point in points:
        point.delta = {
            "outcome_improvement": point.counterfactual.Yt+1 - point.real.Yt+1,
            "time_saved": rounds_of_correction_avoided,
            "Board_correction_avoided": yes_or_no,
            "root_principle": which_P_made_the_difference
        }
    
    # Step 5: PATTERN — 跨决策点找模式
    patterns = {
        "most_impactful_principle": mode(p.delta.root_principle for p in points),
        "biggest_delta_point": max(points, key=lambda p: p.delta.outcome_improvement),
        "still_would_fail": [p for p in points if p.counterfactual.still_wrong],
        "Board_unique_insight": [p for p in points if p.delta.Board_correction_avoided == False]
    }
    # Board_unique_insight = 即使有当前认知也做不对的 → Board 智慧 > 所有理论
    
    # Step 6: SYNTHESIZE — 产出新认知
    new_insights = []
    for pattern in patterns:
        if pattern.is_novel():  # 不重复已有 wisdom
            new_insights.append(create_wisdom_entry(pattern))
    
    # Step 7: CODIFY — 写入源代码
    for insight in new_insights:
        save_to_wisdom(insight)
        if insight.can_become_selfcheck():
            update_capability_iteration_engine(insight)
    
    return SandboxReport(points, patterns, new_insights)
```

## 度量标准

沙箱复盘成功 (Rt+1=0) 条件:
- [ ] 所有 key decision points 都对比完
- [ ] 每个点有 real vs counterfactual 明确 delta
- [ ] 找到跨点模式 (不只是逐点分析)
- [ ] 识别出 "Board 智慧不可替代" 的点 (= 认知的天花板)
- [ ] 至少 1 条新 insight 不在已有 wisdom 中
- [ ] 新 insight 写入源代码

## 何时使用

- 每个长 session (>4h) 结束后
- Board 明确要求复盘时
- CEO 发现重复犯同类错误时 (= 说明上次复盘没到位)
