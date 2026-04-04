# 孤立模块调查报告：Top 2最大文件

**调查时间：** 2026-04-03  
**调查人：** CTO (eng-platform)  
**调查范围：** governance/ml/objectives.py (53KB) + governance/experience_bridge.py (23KB)  
**调查目的：** 确认是历史沉积还是功能断裂，决定系统健康度评分（B- vs C）

---

## 调查结果摘要

| 文件 | 大小 | 状态 | 结论 | 影响健康度 |
|------|------|------|------|------------|
| **ml/objectives.py** | 53KB (1277行) | 🟡 代码重复 | 历史沉积（拆分未完成） | 不影响功能 |
| **experience_bridge.py** | 23KB | 🔴 功能断裂 | 设计上应该调用但断裂 | **降级到C** |

**Board问题答案：**
- ❌ 不是"都是历史沉积准备删除"
- ✅ **experience_bridge.py是设计上应该被调用但目前断裂**
- ✅ **ml/objectives.py是历史沉积（代码重复）**

**系统健康度判定：C级**
- 原因：experience_bridge.py功能断裂，Path B -> Path A反馈通道缺失

---

## 详细调查：governance/ml/objectives.py (53KB)

### 文件元信息
```python
"""
ystar.governance.ml.objectives
NormativeObjective, ContractQuality, AdaptiveCoefficients, RefinementFeedback
v0.41: 从 metalearning.py 拆分，原始行 290-1552。
"""
```

### 定义的类
- `NormativeObjective` (第15行)
- `ContractQuality` (第53行)
- `AdaptiveCoefficients`
- `RefinementFeedback`

### 代码重复证据

**metalearning.py同样定义了这些类：**
```bash
$ grep -n "^class NormativeObjective" ystar/governance/metalearning.py ystar/governance/ml/objectives.py
ystar/governance/metalearning.py:294:class NormativeObjective:
ystar/governance/ml/objectives.py:15:class NormativeObjective:

$ grep -n "^class ContractQuality" ystar/governance/metalearning.py ystar/governance/ml/objectives.py
ystar/governance/metalearning.py:332:class ContractQuality:
ystar/governance/ml/objectives.py:53:class ContractQuality:
```

**文件行数：**
- metalearning.py: 2720行
- ml/objectives.py: 1277行

### 使用情况

**metalearning.py内部使用：** 40+处引用
```python
# metalearning.py:238
objective:          Optional[NormativeObjective] = None
quality:            Optional[ContractQuality] = None

# metalearning.py:777
def derive_objective(history: List["CallRecord"]) -> NormativeObjective:
    从CIEU历史确定性推导 NormativeObjective（v0.8.0核心函数）。

# metalearning.py:1095
quality = ContractQuality.evaluate(additions, history)
```

**ml/__init__.py导入策略：**
```python
# 从 metalearning 重新导出（向后兼容）
from ystar.governance.metalearning import (
    NormativeObjective, ContractQuality,
    ...
)
```

**外部引用检测：**
```bash
$ grep -r "from ystar.governance.ml.objectives import" ystar/
# 无结果
```

### 结论：历史沉积（代码重复）

**根因：** v0.41尝试将2720行的metalearning.py拆分，但：
1. 拆分出了ml/objectives.py（1277行）
2. 但metalearning.py中未删除原实现
3. ml/__init__.py从metalearning导入（不是从objectives导入）
4. 导致objectives.py成为孤立的重复代码

**修复方案：**
- Option A：删除objectives.py，完全使用metalearning.py的实现
- Option B：完成拆分，删除metalearning.py中的重复定义，修改ml/__init__.py从objectives导入
- Option C：保持现状，标记objectives.py为"拆分未完成的历史副本"

**对系统功能影响：** 零（所有代码使用metalearning.py的实现）

---

## 详细调查：governance/experience_bridge.py (23KB)

### 文件元信息
```python
"""
ystar.governance.experience_bridge — Path B Experience Bridge

Bridge between Path B's external governance experience and Path A's GovernanceLoop.

Design:
    Path B observes external agents and produces CIEU records.
    This bridge aggregates those records into governance-relevant metrics
    that feed into GovernanceLoop via GovernanceObservation.raw_kpis.

Pipeline:
    1. ingest_path_b_cieu(records)     — raw CIEU records from Path B
    2. aggregate_patterns()            — events -> ExternalGovernancePatterns
    3. attribute_gaps()                — patterns -> InternalGovernanceGaps
    4. generate_observation_metrics()  — gaps -> Dict[str, float] (3 KPIs)
    5. feed_governance_loop(gloop)     — inject metrics into GovernanceLoop

This is the formal feedback channel from external governance back to
internal governance. Without it, Path A has no visibility into what
Path B is learning about the outside world.
"""
```

### 设计角色

**功能：** Path B -> Path A的正式反馈通道

**Pipeline：**
```
Path B CIEU records
    → ExperienceBridge.ingest_path_b_cieu()
    → aggregate_patterns() → ExternalGovernancePattern
    → attribute_gaps() → InternalGovernanceGap
    → generate_observation_metrics() → Dict[str, float] (3 KPIs)
    → 注入GovernanceLoop.raw_kpis
```

**关键设计声明：**
> "This is the formal feedback channel from external governance back to internal governance. **Without it, Path A has no visibility into what Path B is learning about the outside world.**"

### 集成点验证

**governance_loop.py集成（✅ 完整）：**
```python
# 第236行：接受experience_bridge参数
def __init__(
    self,
    report_engine,
    experience_bridge: Optional[Any] = None,   # P1-4: ExperienceBridge（可选）
):
    self._experience_bridge = experience_bridge

# 第462行：使用bridge metrics
if self._experience_bridge is not None:
    bridge_metrics = self._experience_bridge.generate_observation_metrics()
    observation.raw_kpis.update(bridge_metrics)

# 第671行：使用bridge suggestions
if self._experience_bridge is not None:
    bridge_output = self._experience_bridge.generate_output()
    # Merge bridge suggestion candidates into governance suggestions
```

**orchestrator.py集成（❌ 缺失）：**
```bash
$ grep -n "ExperienceBridge\|experience_bridge" ystar/adapters/orchestrator.py
# 无结果
```

**orchestrator未初始化ExperienceBridge，GovernanceLoop初始化时未传入bridge参数。**

### 测试覆盖验证

**test_experience_bridge_integration.py (9个测试)：**
```bash
$ python -m pytest tests/test_experience_bridge_integration.py -v
tests/test_experience_bridge_integration.py::test_governance_loop_with_bridge PASSED
tests/test_experience_bridge_integration.py::test_governance_loop_without_bridge PASSED
tests/test_experience_bridge_integration.py::test_bridge_feeds_governance_loop PASSED
tests/test_experience_bridge_integration.py::test_governance_loop_without_bridge_unchanged PASSED
tests/test_experience_bridge_integration.py::test_bridge_suggestions_merged_into_tighten PASSED
tests/test_experience_bridge_integration.py::test_bridge_failure_does_not_block_observation PASSED
tests/test_experience_bridge_integration.py::test_bridge_failure_does_not_block_tighten PASSED
tests/test_experience_bridge_integration.py::test_bridge_suggestion_candidate_conversion PASSED
tests/test_experience_bridge_integration.py::test_bridge_ingest_multiple_sources PASSED

============================== 9 passed in 0.42s ==============================
```

**结论：** 集成测试全部通过，证明设计正确。

### 断裂点分析

**设计链路：**
```
Path B (path_b_agent.py)
    → CIEU records (external_observation事件)
    → ExperienceBridge.ingest_path_b_cieu()
    → ExperienceBridge.generate_observation_metrics()
    → GovernanceLoop (experience_bridge参数)
    → GovernanceLoop.observe() 合并metrics
```

**实际链路：**
```
Path B (path_b_agent.py)
    → CIEU records (external_observation事件) ✅
    → [断裂] ExperienceBridge未被orchestrator初始化 ❌
    → [断裂] GovernanceLoop未接收experience_bridge参数 ❌
```

**断裂位置：** orchestrator.py

**orchestrator应该做但没做的：**
```python
# orchestrator.py应该有（但实际没有）：
from ystar.governance.experience_bridge import ExperienceBridge

def __init__(self, ...):
    self._experience_bridge = ExperienceBridge()
    
    # 初始化GovernanceLoop时传入
    self._governance_loop = GovernanceLoop(
        report_engine=self._report_engine,
        experience_bridge=self._experience_bridge,  # ← 缺失
    )
```

### 结论：功能断裂（设计上应该调用）

**根因：** orchestrator.py未实现ExperienceBridge集成

**影响：**
- Path B观察外部agent，写入CIEU ✅
- 但这些观察**无法反馈到Path A** ❌
- GovernanceLoop无法基于Path B学到的经验改进自身策略
- **Path B功能不完整**（只有观察，没有反馈闭环）

**与今日Path B激活的关系：**
- 今天激活了：path_b_agent.observe() → CIEU ✅
- 今天未激活：ExperienceBridge → GovernanceLoop ❌
- **今天的Path B激活只完成了一半**

**修复方案：**
1. 在orchestrator.__init__()中初始化ExperienceBridge
2. 将experience_bridge传给GovernanceLoop
3. 定期调用experience_bridge.ingest_path_b_cieu()喂入Path B的CIEU记录
4. 工作量：2-3小时

**对系统功能影响：** 🔴 高
- Path B -> Path A反馈通道完全缺失
- 今日交付的Path B完整激活实际上不完整

---

## 对系统健康度的影响

### 原评分：B-
- 基于"9个P1模块孤立，但核心功能正常"

### 新发现后重新评估

**ml/objectives.py (53KB):**
- 性质：历史沉积（代码重复）
- 影响：零（无人使用）
- 评分影响：不降级

**experience_bridge.py (23KB):**
- 性质：功能断裂
- 影响：高（Path B不完整）
- 评分影响：**降级到C**

### 最终评分：C级

**C级定义：** 有问题需要修复才能投产

**降级理由：**
1. **今日交付的Path B完整激活实际上不完整**
   - 有observe()写入CIEU ✅
   - 但无反馈闭环到Path A ❌

2. **设计文档明确声明这是必需功能**
   - "This is the formal feedback channel..."
   - "Without it, Path A has no visibility..."

3. **有完整测试验证设计正确**
   - 9个集成测试全部通过
   - 证明不是实验性功能，是设计就绪但未接入

4. **orchestrator有能力接入但未接入**
   - 不是架构限制
   - 是实现未完成

---

## Board决策建议

### 立即行动（明天P0任务追加）

**4. 修复experience_bridge断裂**（P0，2-3小时）
- 在orchestrator中初始化ExperienceBridge
- 传给GovernanceLoop
- 定期喂入Path B CIEU记录
- 验证反馈闭环工作

### 近期修复（P1）

**11. 清理ml/objectives.py代码重复**（P1，1小时）
- 删除objectives.py或完成拆分
- 统一代码路径

### 健康度恢复

修复experience_bridge断裂后：
- C级 → B级（恢复到"有小问题但不阻塞"）

---

## 结论

**回答Board问题：**

❌ **不是都是历史沉积准备删除**

✅ **ml/objectives.py是历史沉积（代码重复），experience_bridge.py是功能断裂**

✅ **系统健康度应该是C级，不是B-**

**关键发现：**
今日交付的"Path B完整激活"实际上只完成了一半：
- ✅ Path B observe() → CIEU
- ❌ CIEU → ExperienceBridge → GovernanceLoop（反馈闭环缺失）

**建议：**
明天P0任务追加第4项，修复experience_bridge断裂后再投产。

---

**CTO签字：** eng-platform (执行)  
**Board审核：** Haotian Liu  
**调查时间：** 2026-04-03 22:45  
**报告版本：** Final
