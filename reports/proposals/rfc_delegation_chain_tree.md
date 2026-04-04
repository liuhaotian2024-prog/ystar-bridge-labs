# RFC: DelegationChain树形结构改造

**RFC编号:** RFC-2026-001  
**标题:** DelegationChain从单链改为树形结构，支持并行授权分支  
**提出者:** CTO (eng-kernel)  
**日期:** 2026-04-03  
**状态:** 待Board审批  
**优先级:** P1  

---

## 1. 动机 (Motivation)

### 当前问题

DelegationChain当前是`List[DelegationContract]`单链结构，无法表示CEO同时授权给CTO/CMO/CSO的并行分支场景。

**实际场景：**
```
CEO
 ├─ CTO → eng-kernel
 ├─ CMO → content-writer
 └─ CSO → sales-analyst
```

**当前结构只能表示：**
```
CEO → CTO → eng-kernel
```

### 影响范围

**修改文件：**
- `ystar/kernel/dimensions.py` (DelegationContract, DelegationChain类)
- `ystar/adapters/hook.py` (_check_hook_full函数)
- `ystar/cli/setup_cmd.py` (session.json生成逻辑)

**风险级别：** MEDIUM-HIGH
- 修改核心contract传递逻辑
- 影响每次工具调用的权限验证
- 需要完整回归测试

---

## 2. 设计方案 (Design)

### 2.1 数据结构变更

**当前：**
```python
@dataclass
class DelegationContract:
    from_agent: str
    to_agent: str
    delegated_tools: List[str]
    contract: IntentContract

@dataclass
class DelegationChain:
    contracts: List[DelegationContract]  # 单链
```

**改为：**
```python
@dataclass
class DelegationContract:
    from_agent: str
    to_agent: str
    delegated_tools: List[str]
    contract: IntentContract
    children: List['DelegationContract'] = field(default_factory=list)  # 新增

@dataclass
class DelegationChain:
    root: DelegationContract  # 根节点
    all_contracts: Dict[str, DelegationContract] = field(default_factory=dict)  # 索引
```

### 2.2 新增方法

```python
class DelegationChain:
    def find_path(self, agent_id: str) -> List[DelegationContract]:
        """查找从root到指定agent的授权路径"""
        pass
    
    def validate_tree(self) -> Tuple[bool, List[str]]:
        """树形结构验证（单调性、无循环）"""
        pass
    
    def to_dict(self) -> dict:
        """序列化为dict（用于session.json存储）"""
        pass
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DelegationChain':
        """从dict反序列化"""
        pass
```

### 2.3 运行时验证

**在hook.py的_check_hook_full()中：**
1. 读取delegation_chain
2. 调用`chain.find_path(agent_id)`找到授权路径
3. 计算路径上所有contract的交集（最严格约束）
4. 用叠加contract执行check()

**效应：**
- 权限单调性从"session启动时验证一次"变成"每次工具调用都执行"
- 子agent无法使用超出委托链授权范围的权限

---

## 3. 向后兼容性 (Backward Compatibility)

**兼容策略：**

1. **session.json格式**
   - 新增`delegation_chain`字段（可选）
   - 无此字段时使用agent自己的contract（现有行为）
   - 兼容旧版session.json

2. **API兼容**
   - `DelegationContract`保持现有字段
   - 新增`children`字段有默认值`[]`
   - 旧代码读取不受影响

3. **验证逻辑**
   - `validate_tree()`替代`validate()`
   - `validate()`保留但标记为deprecated

---

## 4. 测试计划 (Testing)

### 4.1 单元测试

**新增测试文件:** `tests/test_delegation_chain_tree.py`

**测试用例（15个）：**
1. 树形结构构建和索引
2. find_path()路径查找（正常/不存在）
3. validate_tree()单调性检查
4. validate_tree()循环检测
5. 序列化/反序列化（to_dict/from_dict）
6. 并行分支验证（CEO→CTO+CMO+CSO）
7. 三层链路验证（CEO→CTO→eng-kernel）

### 4.2 集成测试

**新增测试文件:** `tests/test_delegation_chain_runtime.py`

**测试用例（8个）：**
1. hook.py使用有效contract而非agent自己的contract
2. _compute_effective_contract()叠加计算
3. _merge_contracts_strict()交集合并
4. session.json无delegation_chain时的降级行为
5. 权限超出时的deny验证

### 4.3 回归测试

- 现有669测试必须全部通过
- 特别关注：check()相关测试、Policy测试

---

## 5. 性能影响 (Performance)

**增加开销：**
- 每次工具调用需要：
  1. find_path(): O(log N)树遍历
  2. 叠加N个contract: O(N)合并操作

**典型场景：**
- 三层链路（CEO→CTO→eng-kernel）
- 每次工具调用增加约0.1-0.5ms

**优化方案：**
- 缓存路径查找结果（按agent_id索引）
- 叠加contract结果缓存

**评估：** 开销可接受（相比hook总耗时<1%）

---

## 6. 部署计划 (Deployment)

### 6.1 分阶段部署

**Phase 1: 数据结构（无破坏性）**
- 修改DelegationContract/DelegationChain类
- 新增方法，保留旧方法
- 测试通过

**Phase 2: hook集成（可回滚）**
- 修改hook.py添加运行时验证
- 通过feature flag控制（默认OFF）
- 测试通过后启用

**Phase 3: session.json生成（可选）**
- 修改setup_cmd.py生成delegation_chain
- 仅对新用户生效
- 旧用户session.json不受影响

### 6.2 回滚方案

**如果出现问题：**
1. feature flag关闭运行时验证
2. 降级到只使用agent自己的contract
3. session.json保持向后兼容

---

## 7. 替代方案 (Alternatives)

### 方案A: 保持单链，限制授权模式

**优点：** 无需改造，风险低  
**缺点：** 无法支持并行授权  
**决策：** 不采纳（需求明确需要并行）

### 方案B: 引入第三方DAG库

**优点：** 成熟的图结构支持  
**缺点：** 新增依赖，序列化复杂  
**决策：** 不采纳（需求简单，自己实现更可控）

---

## 8. 风险与缓解 (Risks)

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| contract叠加逻辑错误 | 中 | 高 | 45+个单元测试覆盖 |
| 性能退化 | 低 | 中 | 性能测试+缓存优化 |
| 旧session.json不兼容 | 低 | 高 | 向后兼容设计+降级逻辑 |
| hook.py回归问题 | 中 | 高 | 完整回归测试+feature flag |

---

## 9. 未解决问题 (Open Questions)

1. **DelegationChain最大深度限制？**
   - 建议：最多5层（防止过深嵌套）
   - 需要：Board确认

2. **并行分支数量限制？**
   - 建议：每个节点最多10个子节点
   - 需要：Board确认

3. **权限提升机制？**
   - 场景：子agent需要临时更高权限
   - 方案：runtime_relax机制（已有）
   - 需要：确认不需要新机制

---

## 10. Board决策点

**需要Board明确决定：**

1. ✅ 批准树形结构改造？
2. ✅ 同意运行时验证每次工具调用执行？
3. ✅ 接受0.1-0.5ms性能开销？
4. ✅ 批准Phase 1-3分阶段部署计划？
5. ❓ DelegationChain最大深度限制（建议5层）？
6. ❓ 并行分支数量限制（建议10个）？

**批准后执行顺序：**
1. Phase 1: 数据结构改造（2-3小时）
2. 完整测试（45+单元测试 + 8+集成测试）
3. Phase 2: hook集成（1-2小时）
4. 回归测试（669测试全部通过）
5. Phase 3: session.json生成（1小时）
6. 文档更新

**总工作量估算：** 6-8小时（全速执行，忽略估算）

---

**提交人签字:** CTO (eng-kernel)  
**日期:** 2026-04-03  
**状态:** ⏸️ 等待Board审批

---

## Board批复 (2026-04-03)

**批准人:** Board（刘浩天）
**状态:** ✅ 已批准，可以执行

### 批准内容
1. ✅ 树形结构改造
2. ✅ 运行时每次工具调用验证
3. ✅ 0.1-0.5ms性能开销可接受
4. ✅ Phase 1-2-3分阶段部署

### 强制性设计要求（不满足不得执行）
max_depth和max_branches_per_node不得在
Y-star-gov产品代码里硬编码，必须作为
session.json的可配置参数，代码里只有默认值：

  MAX_DEPTH = session_cfg.get(
      "delegation_chain", {}
  ).get("max_depth", 5)

  MAX_BRANCHES = session_cfg.get(
      "delegation_chain", {}
  ).get("max_branches_per_node", 10)

Y*Bridge Labs使用默认值，不需要显式配置。

**执行优先级:** P1
