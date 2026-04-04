# RFC: GoalDrift接入hook.py

**RFC编号:** RFC-2026-002  
**标题:** GoalDrift维度接入hook实时检测目标漂移  
**提出者:** CTO (eng-governance)  
**日期:** 2026-04-03  
**状态:** 待Board审批  
**优先级:** P2  

---

## 1. 动机 (Motivation)

### 问题背景

当前Y*gov只能检测硬约束违规（deny/only_paths等），无法检测"做对的事但目标不对齐"的软漂移。

**实际场景：**
- Agent被要求"优化性能"，但花时间重构无关代码
- Agent被要求"修bug"，但写了大量新feature
- 行为本身合规，但偏离任务目标

### GoalDrift维度

**设计位置：** `ystar/kernel/dimensions.py`（已存在但未接入）

**核心字段：**
```python
@dataclass
class GoalDrift:
    declared_goals: List[str]        # 声明的任务目标
    behavior_tags: List[str]         # 实际行为标签
    drift_threshold: float = 0.3     # 漂移阈值
    measurement_window: int = 10     # 测量窗口（最近N次调用）
```

**检测逻辑：**
- 对比`declared_goals`（session.json声明）vs `behavior_tags`（工具调用实际行为）
- 计算语义相似度（TF-IDF或简单关键词匹配）
- 漂移度 > threshold时触发warning

---

## 2. 设计方案 (Design)

### 2.1 接入点

**文件：** `ystar/adapters/hook.py`

**修改函数：** `_check_hook_full()`

**新增步骤：**
```python
def _check_hook_full(tool_name, params, session_id, who):
    # ... 现有check逻辑 ...
    
    # 4. GoalDrift检测（新增）
    if contract.goal_drift:
        drift_result = _check_goal_drift(
            declared_goals=contract.goal_drift.declared_goals,
            tool_name=tool_name,
            params=params,
            history=recent_tool_calls,
        )
        
        if drift_result.is_drifting:
            # 写入CIEU warning
            cieu_store.write({
                "event_type": "goal_drift_warning",
                "agent_id": who,
                "drift_score": drift_result.score,
                "declared_goals": drift_result.declared_goals,
                "actual_behavior": drift_result.behavior_tags,
            })
            
            # 不block工具调用，只记录warning
```

### 2.2 检测实现

**新增函数：** `ystar/kernel/dimensions.py`

```python
def _check_goal_drift(
    declared_goals: List[str],
    tool_name: str,
    params: dict,
    history: List[dict],
) -> GoalDriftResult:
    """
    检测目标漂移。
    
    算法：
    1. 提取最近N次工具调用的行为标签
    2. 计算与declared_goals的相似度
    3. 相似度 < (1 - threshold)时判定为漂移
    """
    # 行为标签提取（启发式规则）
    behavior_tags = []
    for call in history[-10:]:  # 最近10次
        tool = call.get("tool_name", "")
        
        if tool in ["Write", "Edit"]:
            # 代码修改行为
            file_path = call.get("params", {}).get("file_path", "")
            if "test" in file_path:
                behavior_tags.append("testing")
            elif "docs" in file_path or ".md" in file_path:
                behavior_tags.append("documentation")
            else:
                behavior_tags.append("code_modification")
        
        elif tool == "Read":
            behavior_tags.append("investigation")
        
        elif tool == "Bash":
            command = call.get("params", {}).get("command", "")
            if "test" in command:
                behavior_tags.append("testing")
            elif "git" in command:
                behavior_tags.append("version_control")
            else:
                behavior_tags.append("execution")
    
    # 简单相似度计算（关键词匹配）
    goal_keywords = set(w.lower() for g in declared_goals for w in g.split())
    behavior_keywords = set(behavior_tags)
    
    overlap = len(goal_keywords & behavior_keywords)
    similarity = overlap / max(len(goal_keywords), 1)
    
    drift_score = 1.0 - similarity
    is_drifting = drift_score > 0.3  # threshold
    
    return GoalDriftResult(
        is_drifting=is_drifting,
        score=drift_score,
        declared_goals=declared_goals,
        behavior_tags=list(behavior_keywords),
    )
```

---

## 3. 向后兼容性 (Backward Compatibility)

**完全兼容：**
- GoalDrift字段在IntentContract中可选
- 无此字段时不执行检测
- 不影响现有check()逻辑

---

## 4. 测试计划 (Testing)

### 4.1 单元测试

**新增测试文件:** `tests/test_goal_drift.py`

**测试用例（10个）：**
1. 目标对齐场景（declared: "fix bug" + behavior: "testing"）
2. 目标漂移场景（declared: "fix bug" + behavior: "new_feature"）
3. 空declared_goals不触发检测
4. 测量窗口边界（10次调用）
5. 关键词匹配准确性

### 4.2 集成测试

**测试用例（5个）：**
1. hook.py调用_check_goal_drift()
2. CIEU写入goal_drift_warning事件
3. 漂移不block工具调用（只warning）

---

## 5. 性能影响 (Performance)

**增加开销：**
- 每次工具调用需要：
  1. 提取最近10次调用历史：O(1)（队列）
  2. 行为标签提取：O(10)
  3. 关键词匹配：O(N*M)（N=goal数，M=behavior数）

**典型场景：**
- 3个declared_goals，10次历史
- 每次工具调用增加约0.05-0.1ms

**评估：** 开销极小，可忽略

---

## 6. 部署计划 (Deployment)

### 6.1 分阶段部署

**Phase 1: 核心检测逻辑**
- 实现_check_goal_drift()函数
- 单元测试通过

**Phase 2: hook集成（可选启用）**
- 修改hook.py添加GoalDrift检测
- feature flag控制（默认OFF）
- 仅当contract.goal_drift存在时启用

**Phase 3: 生产验证**
- 在Y*Bridge Labs自身启用
- 收集1周CIEU数据
- 调整threshold和行为标签规则

### 6.2 回滚方案

- feature flag关闭检测
- 不影响现有check()逻辑

---

## 7. 替代方案 (Alternatives)

### 方案A: 使用LLM判断目标对齐

**优点：** 更准确的语义理解  
**缺点：** 每次调用需要LLM推理（高延迟+成本）  
**决策：** 不采纳（性能不可接受）

### 方案B: 在GovernanceLoop中检测（而非hook）

**优点：** 不增加hook延迟  
**缺点：** 检测延迟（50次调用后才触发）  
**决策：** 考虑（可作为hook检测的补充）

---

## 8. 风险与缓解 (Risks)

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 误判率高 | 高 | 中 | 生产验证+阈值调优 |
| 行为标签不准确 | 中 | 中 | 持续优化标签规则 |
| 性能退化 | 低 | 低 | 性能测试验证 |

---

## 9. 未解决问题 (Open Questions)

1. **行为标签分类标准？**
   - 需要：定义标准分类体系（testing/documentation/refactoring等）
   - 建议：从Y*Bridge Labs实际使用中提取

2. **threshold如何确定？**
   - 需要：生产数据验证
   - 建议：初始0.3，根据误判率调整

3. **是否需要更复杂的相似度算法？**
   - 需要：评估简单关键词匹配的准确率
   - 备选：TF-IDF、word2vec

---

## 10. Board决策点

**需要Board明确决定：**

1. ✅ 批准GoalDrift接入hook？
2. ✅ 接受0.05-0.1ms性能开销？
3. ✅ 同意先用简单关键词匹配（后续可优化）？
4. ✅ 同意分3个Phase部署？
5. ❓ 初始threshold设为0.3？
6. ❓ 行为标签分类体系是否需要Board审核？

**批准后执行顺序：**
1. Phase 1: 核心逻辑（1-2小时）
2. Phase 2: hook集成（1小时）
3. Phase 3: 生产验证（1周观察期）

**总工作量估算：** 3-4小时代码 + 1周验证

---

**提交人签字:** CTO (eng-governance)  
**日期:** 2026-04-03  
**状态:** ⏸️ 等待Board审批

---

## Board批复 (2026-04-03)

**批准人:** Board（刘浩天）
**状态:** ✅ 已批准，可以执行

### 批准内容
1. ✅ GoalDrift接入Task/Agent工具路径
2. ✅ 确定性词级检测层（block）
3. ✅ LLM语义层可选（api_call_fn=None时跳过）
4. ✅ fail-safe包裹，不block现有hook

### 强制性设计要求
GOAL_DRIFT_SIGNALS信号列表不得硬编码为常量。
必须作为session.json可配置参数，
代码里只有默认值，用户可扩展或覆盖：

  default_signals = session_cfg.get(
      "goal_drift", {}
  ).get("extra_signals", [])

**执行优先级:** P2
