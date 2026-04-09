# Y*gov RuleRegistry API 改进提案

**作者**: Ethan Wright (CTO)
**日期**: 2026-04-09
**优先级**: P1
**状态**: 提案,待 Board 决策
**目标版本**: Y*gov 0.49.0
**触发**: GOV-001 Step 5 实现 `register_obligation.py` 时的现场踩坑

---

## 1. 问题陈述

GOV-001 Step 5 实现 Y*Bridge Labs 的 `register_obligation.py` 时,我需要建立一个**只触发我自己定义的 rule** 的 `OmissionEngine`。直觉上的写法:

```python
from ystar import OmissionEngine, OmissionRule, InMemoryOmissionStore
from ystar.governance.omission_engine import RuleRegistry

registry = RuleRegistry()           # 期望: 空 registry
registry.register(my_rule)          # 期望: registry 里只有 my_rule
engine = OmissionEngine(store=InMemoryOmissionStore(), registry=registry)
engine.ingest_event(...)            # 期望: 只触发 my_rule
```

**实际结果**: 每次 `ingest_event` 产生 **2** 条 obligation,不是 1 条。一条是我的,另一条来自一个我从未注册的 `rule_a_delegation` rule,触发 `required_delegation_omission`。

排查后定位到 `RuleRegistry.__init__` 源码:

```python
# /opt/homebrew/lib/python3.11/site-packages/ystar/governance/omission_engine.py
def __init__(self) -> None:
    import copy
    self._rules: Dict[str, OmissionRule] = {}
    for r in BUILTIN_RULES:                    # ← 强制 deep-copy 7 条 builtin
        self._rules[r.rule_id] = copy.deepcopy(r)
```

**`RuleRegistry()` 构造器永远不是空的**——它强制把 `BUILTIN_RULES` 中的 7 条规则(`rule_a_delegation`、`rule_b_acknowledgement`、`rule_c_status_update`、`rule_d_result_publication`、`rule_e_upstream_notification`、`rule_f_escalation`、`rule_g_closure`)deep-copy 进 `_rules`,无任何参数控制此行为。

要绕开这个隐性加载,Y*Bridge Labs 的脚本必须额外手动 unregister 一遍:

```python
from ystar import BUILTIN_RULES
registry = RuleRegistry()
for builtin in BUILTIN_RULES:
    registry.unregister(builtin.rule_id)
registry.register(my_rule)
```

这一步**没有任何文档提示**。任何外部用户(企业客户、开源开发者、Y\*gov 教程跟读者)都会踩这个坑,而且很难自我诊断:
1. CIEU 库里多出来的"幽灵 obligation"会让用户怀疑自己的 rule 配置错了
2. `result.new_obligations` 长度大于预期,但没有 warning 或 hint
3. `RuleRegistry()` 这个 API 名字本身**反直觉**——任何受过基本编程训练的人都会预期"new Registry() = 空 registry"

GOV-001 Step 5 的端到端测试**第一次跑就因这个 bug 失败**,直到 Ethan 读源码才定位根因。这是 Y\*gov 0.41.x → 0.48.x 期间未修复的 P1 级 API 设计问题。

---

## 2. 三个改进方案

### 方案 A: 构造器加 `load_builtins=True` 参数

```python
class RuleRegistry:
    def __init__(self, load_builtins: bool = True) -> None:
        import copy
        self._rules: Dict[str, OmissionRule] = {}
        if load_builtins:
            for r in BUILTIN_RULES:
                self._rules[r.rule_id] = copy.deepcopy(r)
```

**用法**:
```python
registry = RuleRegistry(load_builtins=False)   # 真空 registry
registry.register(my_rule)
```

**优点**:
- 100% 向后兼容(默认 `True`,所有现有代码不变)
- 显式: 调用方一眼就能看到自己启不启用 builtin
- 标准 Python 模式(类似 `dict.__init__(default=None)`)

**缺点**:
- API 多了一个布尔参数,长期可能膨胀
- 仍然需要用户**知道这个参数存在**——如果不读 docstring,默认行为还是隐式加载,新用户依然会困惑

### 方案 B: 提供 `RuleRegistry.empty()` 工厂方法

```python
class RuleRegistry:
    def __init__(self) -> None:
        # 保持原有行为不变
        import copy
        self._rules: Dict[str, OmissionRule] = {}
        for r in BUILTIN_RULES:
            self._rules[r.rule_id] = copy.deepcopy(r)

    @classmethod
    def empty(cls) -> "RuleRegistry":
        """Create a RuleRegistry with NO builtin rules pre-loaded."""
        instance = cls.__new__(cls)
        instance._rules = {}
        return instance
```

**用法**:
```python
registry = RuleRegistry.empty()              # 真空 registry
registry.register(my_rule)
```

**优点**:
- 100% 向后兼容
- 工厂方法名 `empty()` 自我说明,无需读 docstring
- 符合 Python 命名传统(`dict.fromkeys()`、`pathlib.Path.cwd()`)
- 长期看比布尔参数更可扩展(将来可以加 `RuleRegistry.from_pack(pack_name)`、`RuleRegistry.from_dict({...})`)

**缺点**:
- 需要用户**发现**这个工厂方法的存在——如果只看 `__init__`,依然会踩同样的坑
- 实际上没有解决"`RuleRegistry()` 反直觉"的问题,只是给了一个 escape hatch

### 方案 C: 文档 + docstring 警告,不改代码

```python
class RuleRegistry:
    """
    Registry for OmissionRule objects.

    ⚠️ IMPORTANT: RuleRegistry() pre-loads 7 builtin rules
    (rule_a_delegation through rule_g_closure) on construction.
    To create a registry with NO builtin rules, you must explicitly
    unregister each one:

        from ystar import BUILTIN_RULES
        registry = RuleRegistry()
        for r in BUILTIN_RULES:
            registry.unregister(r.rule_id)
        registry.register(your_rule)
    """
    def __init__(self) -> None:
        # ... unchanged ...
```

**优点**:
- 零代码改动,零风险
- 100% 向后兼容
- 教育用户理解 Y*gov 的设计意图(默认 builtin 是 feature 不是 bug)

**缺点**:
- **治标不治本**——反直觉的 API 还是反直觉的 API,文档只能减轻不能消除
- 假定用户会读 docstring(经验告诉我们 80% 的用户不读)
- 留下永久的"必须手动循环 unregister"的样板代码,代码味道

---

## 3. 推荐: **方案 B (`RuleRegistry.empty()`)**,以及为什么不选 A 或 C

### 为什么不是 A

方案 A 的核心问题是: **它在已经反直觉的 API 上加了一个开关**。新用户读到 `RuleRegistry(load_builtins=False)` 时的反应不是"原来如此",而是**"为什么这个参数默认是 True?"**——这暴露了一个本应该是默认行为的设计选择。布尔参数适合"两种用法都常见"的场景,但 builtin pre-load 是 99% 用户不需要的行为。

更深一层: 如果将来要加 `load_builtins=False, only_builtins=['rule_a','rule_b']`,API 会一路膨胀。布尔参数是**短期止血,长期债务**。

### 为什么不是 C

方案 C 把责任完全甩给用户。但 GOV-001 Step 5 的真实数据告诉我们: **Ethan 读了 Y*gov 主类的多份 docstring,仍然没看到这个隐性行为,只能靠读源码定位**。这意味着 docstring 警告的发现率甚至不到 50%。文档是**最后防线,不是第一防线**。

更重要的: Y\*gov 的市场卖点之一是"开发者友好的治理框架"。一个会让人踩坑的隐性 API 行为,直接破坏这个卖点。Y\*gov 0.49.0 应该传达的信息是"我们重视 API 设计",而不是"自己读源码吧"。

### 为什么是 B

1. **`RuleRegistry.empty()` 自我说明**——任何受过 Python 基本训练的人,看到这个方法名,立刻知道它是干什么的。零文档依赖。
2. **100% 向后兼容**——现有代码一行不动。`RuleRegistry()` 仍然 pre-load builtins,这是 Y\*gov 设计意图的一部分(强制用户理解"治理义务必须有默认 baseline")。
3. **可扩展**——`empty()` 是工厂方法范式的开始,将来可以无痛加入 `RuleRegistry.from_pack(...)`、`RuleRegistry.from_yaml(...)`、`RuleRegistry.from_jsonl(...)` 等,API 形状统一。
4. **符合 Python 文化**——`dict.fromkeys`、`pathlib.Path.cwd`、`datetime.datetime.now` 都是同一个模式: 工厂方法做"非默认构造",不污染主构造器。
5. **同时也应该补 docstring**——B 不排除 C,B + C 一起做最理想。

---

## 4. 实现细节(方案 B)

**改动文件**: `ystar/governance/omission_engine.py`

**新增方法**(估计 ~10 行):

```python
@classmethod
def empty(cls) -> "RuleRegistry":
    """Create a RuleRegistry with no builtin rules pre-loaded.

    Use this when you want a registry that contains ONLY rules you
    explicitly register, with no Y*gov default obligation behavior.
    Common use cases:
      - Project-specific governance with custom obligation semantics
      - Testing individual rules in isolation
      - Building lightweight registries for unit tests

    For the default behavior (7 Y*gov builtin rules pre-loaded), use
    the regular constructor: `RuleRegistry()`.
    """
    instance = cls.__new__(cls)
    instance._rules = {}
    return instance
```

**配套补丁**:

1. 在 `RuleRegistry.__init__` 的 docstring 顶部加 4 行说明,提到 builtin pre-load 行为 + 引导到 `empty()`
2. 在 `ystar` 顶层 `__init__.py` 把 `RuleRegistry` 加到 `__all__`(目前从 `ystar.governance.omission_engine` 导,顶层没暴露)
3. 在 `tests/governance/test_omission_engine.py` 加 1 个 unit test:
   ```python
   def test_rule_registry_empty():
       r = RuleRegistry.empty()
       assert len(r._rules) == 0
       assert r.rules_for_trigger("entity_created") == []
   ```
4. 在 `CHANGELOG.md` 0.49.0 段落加一行: `- Add RuleRegistry.empty() factory for creating registries without builtin rules pre-loaded.`

**总改动**: 1 个新方法,~10 行代码 + 4 行 docstring + 1 个 test + 1 行 changelog。**一次 PR,半小时工作量**。

---

## 5. 向后兼容性分析

| 兼容性维度 | 风险 | 评估 |
|---|---|---|
| 现有 `RuleRegistry()` 调用 | **零** | 主构造器行为完全不变 |
| 现有 `register()`、`unregister()`、`enable()`、`disable()` API | **零** | 全部不动 |
| 现有 builtin rule ID(`rule_a_delegation` 等) | **零** | 不动 |
| 现有 OmissionEngine 内部对 `RuleRegistry` 的使用 | **零** | 内部使用 `RuleRegistry()`,行为不变 |
| 现有用户的 cieu_store / 持久化 | **零** | 与 RuleRegistry 无关 |
| **新用户首次接触 API** | **正向改善** | 多一条工厂方法路径,反直觉感降低 |
| **Y\*gov 教程 / 文档** | **需更新** | 加 1 段 `empty()` 用法示例 |

**结论**: **零破坏,纯增量**。可以直接进 0.49.0,无需 deprecation cycle。

---

## 6. 决策建议

**Board 批准方案 B**,Ethan 在 Y-star-gov 仓库开 PR:

- 修改文件: `ystar/governance/omission_engine.py`、`ystar/__init__.py`、`tests/governance/test_omission_engine.py`、`CHANGELOG.md`
- PR 标题: `feat(governance): add RuleRegistry.empty() factory method`
- PR 描述引用本提案 + GOV-001 Step 5 incident
- 工作量: 半小时编码 + 半小时测试 + 半小时 PR review
- 目标版本: **Y\*gov 0.49.0**

如果 Board 倾向 A 或 C,请明示。本提案不包含 Y\*gov 0.50.0+ 的更深度 API 改造(如 OmissionEngine 的 `cieu_store` 自动持久化语义),那是单独的 P2 任务。

---

**附录**: GOV-001 Step 5 实现里的 workaround 已经在 `scripts/register_obligation.py` 的 `build_engine_and_rule()` 函数中,代码注释明确解释了为什么需要 unregister 循环。如果方案 B 进 0.49.0,这段 workaround 可以替换成 `registry = RuleRegistry.empty()` 一行。
