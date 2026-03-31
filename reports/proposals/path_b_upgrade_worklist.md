# Path B升级 + Experience Bridge 工作清单
# Date: 2026-03-31
# Source: ChatGPT三段评估 + 团队共识
# Purpose: 增强Y*gov能力（与论文无关）

---

## P0 — 必须立刻做

### 1. Experience Bridge（Path B → Path A 数据桥）
**文件**: `ystar/governance/experience_bridge.py`（新建）
**输入**: Path B的CIEU事件 + compliance结果 + budget轨迹
**处理**: 聚合模式 → 归因内部缺口 → 生成增强observation
**输出**: GovernanceLoop可用的3个外部治理指标
  - `external_constraint_effectiveness_rate`
  - `external_budget_exhaustion_rate`
  - `external_disconnect_pressure`
**集成**: GovernanceLoop.tighten()吸收这些指标
**关键**: Path A不直接听Path B → Path A只听GovernanceLoop → GovernanceLoop现在包含外部经验

### 2. Path B Constitution（宪法绑定）
**文件**: `ystar/module_graph/PATH_B_AGENTS.md`（新建，类似PATH_A_AGENTS.md）
**内容**: Path B的权限边界、禁止项、义务、目标约束
**绑定**: hash写入Path B生成的每条CIEU记录的contract_hash
**代码改动**: `path_b_agent.py` — 加载constitution + hash检查（同Path A模式）

---

## P1 — 本周完成

### 3. Path B Obligation/Inconclusive/Human Gate
**文件**: `ystar/module_graph/path_b_agent.py`
**增加**:
  - 外部治理obligation创建（对外部agent施加约束后 → 创建"验证合规"义务）
  - INCONCLUSIVE状态（约束施加了但效果不确定）
  - 连续3次INCONCLUSIVE → human review required
  - HARD_OVERDUE → 自动disconnect（不是可选）
**参考**: Path A的inconclusive_count + human_review_required逻辑

### 4. Authority Boundary（从budget刹车→边界定义）
**文件**: `ystar/module_graph/path_b_agent.py`
**改动**:
  - ConstraintBudget增加`allowed_dimensions`（Path B只能约束哪些维度）
  - 允许约束的维度由observation派生，不由Path B自定
  - 类似Path A的`only_paths`约束——Path B的约束范围也必须是被授权的
**公式**: `Path B可约束的范围 ⊆ 观测到的违规范围`

---

## P2 — 下周完成

### 5. 外部治理语义内核化
**文件**: `ystar/kernel/engine.py` + `ystar/kernel/dimensions.py`
**增加**:
  - `external_agent_scope` 概念进入IntentContract
  - `tenant_id` / `domain_boundary` 作为check()的一等公民
  - 类似`module:`前缀，加`external:`前缀让kernel原生理解外部约束

### 6. 真实Disconnect执行
**文件**: `ystar/module_graph/path_b_agent.py` + `ystar/adapters/`
**改动**:
  - disconnect不只是清内存——要真正断开adapter连接
  - 定义统一的disconnect协议：降级contract → 冻结session → 关闭tool route → CIEU记录
  - disconnect_external_agent()调用adapter层的真实断开方法

---

## Experience Bridge 详细设计

### 数据结构
```python
@dataclass
class ExternalGovernancePattern:
    pattern_id: str
    pattern_type: str  # repeated_violation / ineffective_constraint / budget_exhaustion
    count: int
    severity_mean: float
    affected_agents: list
    evidence_refs: list
    confidence: float

@dataclass
class InternalGovernanceGap:
    gap_id: str
    inferred_module_targets: list
    inferred_gap_type: str
    supporting_patterns: list
    confidence: float
    rationale: str
```

### 三段流水线
1. **经验聚合**: CIEU事件 → ExternalGovernancePattern（模式识别）
2. **模式归因**: Pattern → InternalGovernanceGap（外部症状→内部缺口）
3. **指标生成**: Gap → GovernanceLoop增强observation（3个外部指标）

### 架构原则
- ExperienceBridge是GovernanceLoop的扩展观测器，不是独立的suggestion engine
- Path A只听GovernanceLoop，不直接听Path B
- 桥接层不能绕开GovernanceLoop直接给Path A下命令

---

## 联动闭环（最终目标）

```
Path B (外部治理)
  → CIEU + compliance + causal + budget
  → ExperienceBridge (聚合 → 归因 → 指标)
  → GovernanceLoop (吸收外部经验 → 产出suggestion)
  → Path A (suggestion_to_contract → check → execute → CIEU)
  → 更强的Y*gov内核
  → Path B用更强内核对外治理
  → 循环
```
