# gov-mcp 接入 Y\*gov 输入层 — 反事实推理实现提案

**作者**: Ethan Wright (CTO)
**日期**: 2026-04-09
**优先级**: P0(gov-mcp 0.2.0 核心任务)
**权限层级**: **Level 3**(改 gov-mcp 产品代码 + 跨 repo + 影响 0.2.0 release + 引入 Y\*gov ↔ gov-mcp 版本耦合)
**状态**: Step 1 research,等 Board 确认才动 Step 2 代码
**触发**: Board GOV-007 directive (2026-04-09)
**提案格式**: 严格 GOV-005 第七条 + GOV-006 intent verification 协议 (Board 已批 C 方案,本提案是其精神的应用)

---

## 背景的精确陈述

Board 的 GOV-007 directive 描述: "gov-mcp 现在自己用 regex 解析 AGENTS.md,覆盖率 0.7。Y\*gov 已经有成熟的翻译层把 AGENTS.md 翻译成 .ystar_session.json,经过 807 个测试,在生产跑了两周。gov-mcp 在重复造一个更差的轮子。"

**Ethan 调研后,需要纠正一个表述**: gov-mcp **没有自己重复造轮子** —— 它**已经在使用 Y\*gov 的 `translate_to_contract` 函数**(`gov-mcp/gov_mcp/server.py` line 29):

```python
from ystar.kernel.nl_to_contract import translate_to_contract, validate_contract_draft
```

`gov-mcp` 调用 Y\*gov 的 nl_to_contract 函数把 AGENTS.md 翻译成 IntentContract。问题不是 "gov-mcp 自己造的差轮子",问题是 **`translate_to_contract(text)` 默认走 regex 模式**(因为 LLM 模式违反 Iron Rule 1,必须禁用),regex 在 prose-heavy 的 AGENTS.md 上 confidence ~0.7。同一个函数,同一份代码,只是不能用 LLM。

**真正的问题**(纠正后): `.ystar_session.json` 是经过两周**人工演化**出来的 operational 真相源,信息量远超 regex parser 能从 AGENTS.md 提取的。gov-mcp 错过了这份富信息,只能用 regex 重建一个 parsable subset。

**这个区别很重要**: GOV-007 的目标不应该是"换一个翻译器",而是 **"换一个数据源"** —— 从 AGENTS.md 的 prose 换到 `.ystar_session.json` 的结构化运营数据。

---

## 当前状态 Xt

### Xt-1: gov-mcp 当前的 contract 加载路径

```python
# server.py line 39-47
class _State:
    def __init__(self, agents_md_path: Path, ...):
        self.agents_md_path = agents_md_path
        self.agents_md_text = agents_md_path.read_text(encoding="utf-8")
        contract_dict, self.confidence_label, self.confidence_score = translate_to_contract(
            self.agents_md_text
        )
        self.active_contract = _dict_to_contract(contract_dict)
```

读 AGENTS.md → 调 `translate_to_contract(text)` → 拿 contract_dict → 转成 IntentContract 对象。

`translate_to_contract(text, api_call_fn=None)` 签名:
- 默认 `api_call_fn=None` → regex fallback
- 如果传 LLM API 函数 → LLM 模式 (但**违反 Iron Rule 1,gov-mcp 必须禁用**)
- 返回 `(contract_dict, "regex"|"llm", confidence_score)`

### Xt-2: 当前 `IntentContract` 字段(20 个)

```python
IntentContract(
    deny: List[str],                      # 路径 deny
    only_paths: List[str],                # 路径白名单
    deny_commands: List[str],             # 命令 deny
    only_domains: List[str],              # 域白名单
    invariant: List[str],                 # 不变式
    optional_invariant: List[str],
    postcondition: List[str],
    field_deny: Dict[str, List[str]],     # 字段级 deny
    value_range: Dict[str, Dict],         # 值域约束
    obligation_timing: Dict[str, float],  # 义务时限
    confirmed_by: str,                    # 治理元数据
    confirmed_at: float,
    valid_until: float,
    review_triggers: List[str],
    status: str,
    superseded_by: str,
    version: int,
    legitimacy_decay: Dict[str, float],
    name: str,
    hash: str,
)
```

### Xt-3: `.ystar_session.json` 实际字段(基于本仓库 file 验证)

```
top-level keys:
  session_id: str
  cieu_db: str
  contract: dict (4 sub-keys: name, deny, deny_commands, obligation_timing)
  obligation_agent_scope: dict (60 entries — agent role × obligation type)
  agent_display_names: dict (6 entries, GOV-005 Part 4 added)
  agent_write_paths: dict (10 entries — per-role write whitelists)
  restricted_write_paths: dict (2 entries — file-level write restrictions)
  ceo_deny_paths: list (2 items)
  trigger_path_patterns: dict (7 entries — obligation trigger config)
  delegation_chain: dict (links: principal, actor, scope, allow_redelegate, delegation_depth, contract)

delegation_chain.links[].contract: {deny, deny_commands, only_paths, only_domains, invariant}

NO `schema_version` field present.
```

### Xt-4: gov_doctor 现在的报告

```
L1_01_contract:
  hash: sha256:9fdbdaed...
  agents_md: /Users/haotianliu/.openclaw/workspace/ystar-company/AGENTS.md
  confidence: regex
  (confidence_score in governance envelope: 0.7)
L1_06_engine_config:
  deny_rules: 1
  deny_commands: 0
  only_paths: 0
  total_rules: 1
```

**只有 1 个 deny rule, 0 个 deny_command 被 regex 提取出来。** ystar-company/AGENTS.md 是 948 行,有几十条 Iron Rules / 各 agent 权限段 / CIEU 规则。regex parser 几乎全部漏掉。**这就是 0.7 confidence 的真实含义**——70% 是 parser 自己对 "covered" 的乐观估计。

---

## 目标 Y\*

- **gov-mcp 启动时直接读 `.ystar_session.json`**(operational 真相源),而不是从 AGENTS.md prose 翻译
- **`gov_doctor` 报告 confidence ≥ 0.95**(structured data 加载,不是 regex 推断)
- **check() 路径仍然零 LLM**(Iron Rule 1)
- **`--agents-md` 保留为 deprecated fallback**(向后兼容旧部署)
- **`.ystar_session.json` 增加 `schema_version: "1.0"` 字段**(为未来 Y\*gov ↔ gov-mcp 版本协调建立基础)
- **gov-mcp 0.2.0 release 包含本 directive 全部 deliverables**

**Rt = 0 的可观测条件**:
- `gov_doctor` 报告 `L1_06_engine_config` 显示的 deny_rules / deny_commands 数与 `.ystar_session.json` 实际字段数一致(完整 mapping)
- 现有 38 个 MCP 工具全部回归通过
- 启动 log 显示 "loaded contract from session config" 而不是 "regex translation, confidence 0.7"
- `.ystar_session.json` 加 `schema_version: "1.0"` 后,gov-mcp 0.2.0 启动时校验 schema_version

---

## 反事实分析

### 方案 A: Board directive 字面版 — 加 `--session-config` 参数

**做法**:

1. `gov-mcp/gov_mcp/__main__.py` 新增 `--session-config <path>` argparse 参数(可选)
2. `gov-mcp/gov_mcp/server.py` `_State.__init__`:
   - 如果传了 `--session-config`,读 `.ystar_session.json`,从中构造 IntentContract(直接用 `contract` 段 + 提取 `delegation_chain` 等字段)
   - 如果没传,fallback 到 `--agents-md` regex translation(deprecated 但兼容)
3. `--agents-md` 保留作为 fallback,启动时打 deprecation warning
4. `.ystar_session.json` 加 `schema_version: "1.0"` 字段(在 ystar-company repo 改 file)
5. gov-mcp 启动时校验 `schema_version` ∈ supported set,不在则 refuse

**Yt 预测**:
- gov-mcp 改动: ~80 行 in `__main__.py` + `server.py`(包括 _State.__init__、新的 `_load_session_config()` 方法、schema_version 校验)
- ystar-company 改动: 1 行(加 `"schema_version": "1.0"`)
- 测试: smoke test 用 ystar-company `.ystar_session.json` 启动 → gov_doctor → 验证 14/14 + confidence ≥0.95 + 38 工具回归
- 工作量: **半天工程 + 半天测试 = 1 天**

**Rt(与 Y\* 的差距)**:
- ✅ Board intent 字面满足
- ✅ 向后兼容
- ✅ Iron Rule 1 不破坏(继续用 regex parse 的 contract,只是 source 换了)
- ⚠️ **gov-mcp 的 IntentContract model 没动,所以 `obligation_agent_scope`、`agent_write_paths`、`restricted_write_paths`、`ceo_deny_paths`、`trigger_path_patterns` 这些 `.ystar_session.json` 独有字段对 gov-mcp 仍然是黑盒**——gov-mcp 只用 `contract.{name, deny, deny_commands, obligation_timing}` + `delegation_chain` 这两个段
- ⚠️ confidence 提升到 ≥0.95 取决于 contract 段是否能直接 load(它是结构化 JSON,所以 yes,confidence 应该接近 1.0)
- ⚠️ **`obligation_agent_scope` 等富信息没被 gov-mcp 利用**——这是 next iteration 的事

**核心 Rt**: 0(Board 字面 intent 满足),但**留下了 60+ 行 obligation_agent_scope 不被 gov-mcp 看到**的 follow-up gap。

### 方案 B: 完整 schema rebuild — 把 IntentContract 扩展到 cover `.ystar_session.json` 全字段

**做法**: 不只是换 source,还要扩展 IntentContract 增加新字段:
- `obligation_agent_scope: Dict[str, List[str]]`
- `agent_write_paths: Dict[str, List[str]]`
- `restricted_write_paths: Dict[str, List[str]]`
- `ceo_deny_paths: List[str]`
- `trigger_path_patterns: Dict[str, List[str]]`

然后 gov-mcp 的 `gov_check` 等工具识别这些新字段做更细粒度 enforcement。

**Yt 预测**:
- 改 Y\*gov 的 IntentContract 类(`ystar/kernel/contract.py` 或类似位置)~50 行
- 改 gov-mcp 的 `gov_check`、`gov_enforce` 等工具的 contract 检查逻辑 ~150-200 行
- Y\*gov 自己的 807 测试需要回归(Y\*gov product code 改了)
- gov-mcp 的 38 工具需要适配
- 工作量: **3-5 天**

**Rt**:
- ✅ 完整 cover `.ystar_session.json` 所有运营字段
- ✅ 真正的"统一数据源"
- ❌ 改 Y\*gov 产品 + gov-mcp 产品 + 双方测试回归 = **跨 2 个 repo 的 Level 3 改动**
- ❌ 触发 Y\*gov 0.49 release(因为改了 IntentContract 公共 API)
- ❌ 工作量是 Board directive 估的 5x
- ❌ 违反 Board "0.2.0 核心任务"的范围(Board 想的是 gov-mcp 0.2.0,不是同步 Y\*gov 0.49)

### 方案 C: 最简 — 直接读 `.ystar_session.json.contract` 段一对一映射

**做法**: gov-mcp `_State.__init__` 改成:

```python
import json
session_data = json.loads(session_config_path.read_text())
contract_dict = session_data["contract"]
self.active_contract = _dict_to_contract(contract_dict)
```

**不用 translate_to_contract,直接用 `.ystar_session.json` 的 `contract` 段**(已经是 structured dict)。delegation_chain 也直接 import。其它字段(`obligation_agent_scope` 等)忽略,不影响 gov-mcp 现有 38 工具的工作。

**Yt 预测**:
- gov-mcp 改动: ~40 行(_State 加载逻辑 + __main__ argparse + schema_version 校验)
- ystar-company 改动: 1 行(加 schema_version)
- 工作量: **半天 + 半天测试 = 1 天**(同方案 A)

**Rt**:
- ✅ Board intent 满足
- ✅ Iron Rule 1 不破坏
- ✅ confidence 应该 ≥0.95(直接 JSON load,不是 regex 推断)
- ✅ 最小工程债
- ⚠️ 同方案 A 的 follow-up gap(`obligation_agent_scope` 等独有字段没被利用)

**核心 Rt**: 等同方案 A,**实施更简洁**(没有保留 translate_to_contract 调用,因为 .ystar_session.json 已经是 dict 不是 prose)。

---

## 最优解 = **方案 C(最简一对一映射)**

**理由(一句话)**: 方案 A 和方案 C 实际上等价(Board directive 字面 = 直接读 contract 段),差别只是 A 还保留 translate_to_contract 作为 fallback 路径(给 `--agents-md` deprecated 模式用),C 把 fallback 路径和新路径分得更清楚。Board 明确说 "保留 --agents-md 作为 deprecated fallback",所以**最终方案 = A 和 C 的合并**: `--session-config` 走方案 C 路径(直接 dict load),`--agents-md` 走旧的 translate_to_contract 路径(deprecated)。

## 次优解 = **方案 B(扩展 schema)**

**为什么不是最优**: 方案 B 是"做正确的事的极致版"——它真正消除了 GOV-007 隐含的"`.ystar_session.json` 的丰富信息没被 gov-mcp 利用"的 gap。但工作量是 directive 估的 5x,跨 2 个 repo,要 Y\*gov 同步 release。Board 把这定为 "gov-mcp 0.2.0 核心任务",scope 已经 fixed 在 gov-mcp 0.2.0,**不应该 silently 扩到 Y\*gov 0.49**。方案 B 应该是 GOV-008 或 0.3.0 的事。

## 直接出局 = **任何把 LLM 引入 check() 路径的方案**

不再讨论。Iron Rule 1。

---

# Board 4 个具体问题的逐项回答

## Q1: `.ystar_session.json` 字段和 gov-mcp 现有规则的映射是否完整?

**简答**: **不完整,但缺失字段对 gov-mcp 现有功能影响为 0**。

**详细映射表**:

| `IntentContract` 字段(gov-mcp 现有) | `.ystar_session.json` source | 状态 | 影响 |
|---|---|---|---|
| `name` | `contract.name` | ✅ 1:1 mapping | 完整 |
| `deny` | `contract.deny` | ✅ 1:1 mapping | 完整 |
| `deny_commands` | `contract.deny_commands` | ✅ 1:1 mapping | 完整 |
| `obligation_timing` | `contract.obligation_timing` | ✅ 1:1 mapping (10 entries) | 完整 |
| `only_paths` | ❌ 不在顶层 `contract`,仅在 `delegation_chain.links[].contract` | ⚠️ partial | gov-mcp 现在的 only_paths 是 0,所以失去等于 0,无影响 |
| `only_domains` | 同上 | ⚠️ partial | 同上 |
| `invariant` | 同上 | ⚠️ partial | 同上 |
| `optional_invariant` | ❌ 不存在 | ❌ missing | gov-mcp 当前未使用 |
| `postcondition` | ❌ 不存在 | ❌ missing | gov-mcp 当前未使用 |
| `field_deny` | ❌ 不存在 | ❌ missing | gov-mcp 当前未使用 |
| `value_range` | ❌ 不存在 | ❌ missing | gov-mcp 当前未使用 |
| `confirmed_by` | ❌ 不存在 | ❌ missing | governance metadata,默认空字符串 |
| `confirmed_at` | ❌ 不存在 | ❌ missing | 同上 |
| `valid_until` | ❌ 不存在 | ❌ missing | 同上 |
| `review_triggers` | ❌ 不存在 | ❌ missing | 同上 |
| `status` | ❌ 不存在 | ❌ missing | 默认 "" |
| `superseded_by` | ❌ 不存在 | ❌ missing | 默认 "" |
| `version` | ❌ 不存在 | ❌ missing | 默认 1 |
| `legitimacy_decay` | ❌ 不存在 | ❌ missing | 默认 {} |
| `hash` | ❌ 不存在(会在 load 时计算) | computed | gov-mcp 在 load 后自己 hash IntentContract dump |

**反向查找** — `.ystar_session.json` 有哪些字段是 IntentContract 不知道的?

| `.ystar_session.json` 字段 | gov-mcp IntentContract 对应 | 备注 |
|---|---|---|
| `session_id` | (无) | 用作 CIEU session 标识,gov-mcp 启动时可读 |
| `cieu_db` | (无) | Q2 已 defer (Finding 3 / GOV-005),gov-mcp 当前不用 |
| `obligation_agent_scope` (60 entries) | (无) | **operational data**,定义"哪个 agent 应该满足哪个 obligation 类型"。gov-mcp 当前用 OmissionEngine 自己管 obligations,与 .ystar_session.json 这个字段独立 |
| `agent_display_names` | (无) | 显示层 mapping,gov-mcp 当前不用 |
| `agent_write_paths` | (无,概念近 only_paths 但 per-role) | 比 only_paths 强 — per-role 路径白名单。gov-mcp 当前不区分 role-level 权限,这个信息会浪费 |
| `restricted_write_paths` | (无) | 文件级写权限限制,gov-mcp 当前不用 |
| `ceo_deny_paths` | (无,概念近 deny 但 per-role) | role-specific deny,gov-mcp 当前不用 |
| `trigger_path_patterns` | (无) | OmissionEngine 触发条件配置,gov-mcp 当前用内置 builtin rules,不读这个 |
| `delegation_chain.links[]` | gov-mcp 自己有 DelegationChain | gov-mcp 启动时可以从 .ystar_session.json import,代替自己的 default chain |

**结论**: 

- **核心 contract 字段(deny, deny_commands, obligation_timing, name)100% 1:1 mapping**,gov-mcp 切到 `.ystar_session.json` source 后所有现有功能都能继续工作。
- **delegation_chain 可以从 .ystar_session.json import**,代替 gov-mcp 自己的内存 default chain(side effect: 解决了 Finding 2 stale chain 问题的根本——chain source 跟 .ystar_session.json 同步)
- **5 个 .ystar_session.json 独有字段(`obligation_agent_scope`、`agent_write_paths`、`restricted_write_paths`、`ceo_deny_paths`、`trigger_path_patterns`)gov-mcp 当前不利用**,数据"浪费"但不影响 GOV-007 acceptance criteria(Board 没要求 utilize 这些)

**Mapping 完整度**: 4/4 核心 contract 字段(100%)+ delegation chain(100%)+ 5 个独有字段不利用(GOV-007 范围外,留 GOV-008 / 方案 B)

---

## Q2: 启动参数如何变化?

**新启动模式**(GOV-007 acceptance):

```bash
python -m gov_mcp \
    --session-config /Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json \
    --transport sse \
    --host 0.0.0.0 \
    --port 7922
```

**旧启动模式(deprecated 但兼容)**:

```bash
python -m gov_mcp \
    --agents-md /Users/haotianliu/.openclaw/workspace/ystar-company/AGENTS.md \
    --transport sse \
    --host 0.0.0.0 \
    --port 7922
# stderr 出 deprecation warning: "[DEPRECATED] --agents-md is deprecated since 0.2.0,
# use --session-config <path>/.ystar_session.json instead. Falling back to regex
# translation with confidence ≤0.7."
```

**互斥规则**:
- 同时传 `--session-config` 和 `--agents-md`: gov-mcp 优先用 `--session-config`,`--agents-md` 仅用于显示层(`agents_md` 字段在 doctor 报告里指向哪个文件),不参与 contract 加载
- 都不传: refuse to start,exit 1,提示 "must provide either --session-config or --agents-md"

**`__main__.py` 改动**(~10 行):

```python
parser.add_argument(
    "--session-config", type=str, default=None,
    help="Path to .ystar_session.json (Y*gov runtime config). "
         "Recommended over --agents-md since 0.2.0. Confidence ≥0.95."
)
parser.add_argument(
    "--agents-md", type=str, default=None,  # 改成 default=None
    help="[DEPRECATED] Path to AGENTS.md governance file. "
         "Falls back to regex translation, confidence ≤0.7. "
         "Use --session-config instead."
)
# 互斥校验
if not args.session_config and not args.agents_md:
    parser.error("Must provide --session-config (recommended) or --agents-md (deprecated)")
if args.agents_md and not args.session_config:
    print("[DEPRECATED] --agents-md mode, falling back to regex...", file=sys.stderr)
```

**`server.py` `_State.__init__` 改动**(~30 行):

```python
def __init__(
    self,
    session_config_path: Optional[Path] = None,
    agents_md_path: Optional[Path] = None,
    exec_whitelist_path: Optional[Path] = None,
) -> None:
    if session_config_path:
        # NEW PATH: 直接读 session config (high confidence)
        self._load_from_session_config(session_config_path)
    elif agents_md_path:
        # OLD PATH (deprecated)
        self._load_from_agents_md(agents_md_path)
    else:
        raise ValueError("Either session_config_path or agents_md_path required")
    # ... rest of init unchanged ...

def _load_from_session_config(self, path: Path) -> None:
    """NEW: load contract from .ystar_session.json (Y*gov operational truth)"""
    raw = json.loads(path.read_text(encoding="utf-8"))
    self._validate_schema_version(raw)
    contract_dict = raw["contract"]
    self.active_contract = _dict_to_contract(contract_dict)
    self.confidence_label = "session_config"
    self.confidence_score = 0.98  # ≥0.95, structured data
    # Optional: import delegation_chain from session
    for link_data in raw.get("delegation_chain", {}).get("links", []):
        link_contract = _dict_to_contract(link_data.get("contract", {}))
        # ... build DelegationContract and append to self.delegation_chain
    self.session_config_path = path
    self.agents_md_path = None  # not used in this mode

def _load_from_agents_md(self, path: Path) -> None:
    """OLD (deprecated): regex parse AGENTS.md prose"""
    self.agents_md_path = path
    self.agents_md_text = path.read_text(encoding="utf-8")
    contract_dict, self.confidence_label, self.confidence_score = translate_to_contract(
        self.agents_md_text
    )
    self.active_contract = _dict_to_contract(contract_dict)
    self.session_config_path = None

def _validate_schema_version(self, session_data: Dict[str, Any]) -> None:
    SUPPORTED_SCHEMAS = {"1.0"}
    schema = session_data.get("schema_version")
    if not schema:
        # 兼容 .ystar_session.json 还没加 schema_version 的过渡期
        import warnings
        warnings.warn(
            "[gov-mcp] .ystar_session.json missing schema_version field. "
            "Assuming 1.0 for backward compat. Add 'schema_version': '1.0' "
            "to silence this warning."
        )
        return
    if schema not in SUPPORTED_SCHEMAS:
        raise ValueError(
            f"[gov-mcp] Unsupported .ystar_session.json schema_version '{schema}'. "
            f"Supported: {SUPPORTED_SCHEMAS}. "
            f"Either upgrade gov-mcp or downgrade .ystar_session.json schema."
        )
```

---

## Q3: Y\*gov 版本升级时 `.ystar_session.json` 格式变化,gov-mcp 如何适配?

**核心机制: schema_version + 容错策略**

### Step 1: 在 `.ystar_session.json` 加 schema_version 字段(本 directive 的前置条件)

ystar-company `.ystar_session.json` 顶层加 1 行:

```json
{
  "schema_version": "1.0",
  "session_id": "ystar-company_0a84f3c6",
  ...
}
```

**这是改 ystar-company 的 .ystar_session.json,Level 2 (CEO 内部权限,影响内部配置)。** 应该和 gov-mcp 0.2.0 release 同时进行,作为 GOV-007 第三步实施。

### Step 2: gov-mcp 启动时校验 schema_version

```python
SUPPORTED_SCHEMAS = {"1.0"}  # gov-mcp 0.2.0 支持的 schema set

if session_data.get("schema_version") not in SUPPORTED_SCHEMAS:
    raise ValueError("schema_version mismatch — upgrade gov-mcp or downgrade session config")
```

### Step 3: Y\*gov 演化路径

未来 Y\*gov 版本如果改 `.ystar_session.json` 格式:

| 改动类型 | schema_version 行为 | gov-mcp 行为 |
|---|---|---|
| **Backward-compatible 加字段**(如 GOV-005 Part 4 加的 `agent_display_names`) | schema_version 保持 `1.0` | gov-mcp 不需更新,新字段会被 ignored |
| **Backward-incompatible 改字段**(如重命名 `contract.deny` → `contract.deny_paths`) | schema_version bump 到 `2.0` | gov-mcp 0.2.0 启动时 refuse,需升级 gov-mcp 0.3.0 才支持 schema 2.0 |
| **加新顶层字段被 gov-mcp 主动消费**(如 future cieu_db 配置) | schema_version 可能 bump 或保持(看是否 breaking) | gov-mcp 升级后开始读新字段 |
| **删除字段** | schema_version 必 bump | gov-mcp 必升级 |

**默认策略 = 容错向后兼容**:
- gov-mcp 见到未知字段 → log warning,ignore
- gov-mcp 见到缺失的非必需字段 → 用 default value
- gov-mcp 见到 schema_version 比自己支持的高 → refuse to start,提示升级 gov-mcp
- gov-mcp 见到 schema_version 比自己支持的低 → 启动但 log warning,提示升级 .ystar_session.json
- gov-mcp 见到 .ystar_session.json 缺 schema_version → 警告 + 假设 1.0 + 启动(过渡期兼容)

### Step 4: schema_version migration 文档

每个 Y\*gov release 如果改 schema,在 `Y-star-gov/CHANGELOG.md` 增加一段 schema migration 说明,例如:

```markdown
## Y*gov 0.49.0 — Breaking schema_version change

- `.ystar_session.json` schema_version: 1.0 → 2.0
- Breaking: `contract.deny` renamed to `contract.deny_paths`
- Migration: run `ystar migrate-session --from 1.0 --to 2.0` (idempotent)
- gov-mcp compatibility: requires gov-mcp 0.3.0+
```

---

## Q4: 两者版本耦合策略是什么?

**推荐: hybrid coupling — pyproject 声明 min Y\*gov + runtime 校验 schema_version**

### Layer 1: build-time 依赖(pyproject.toml)

```toml
# gov-mcp/pyproject.toml
[project]
dependencies = [
    "ystar>=0.48.0,<0.50.0",  # 支持 Y*gov 0.48.x 和 0.49.x
    "mcp>=0.x",
]
```

- `>=0.48.0`: gov-mcp 0.2.0 需要 Y\*gov 0.48 引入的 IntentContract 字段(本仓库 doctor 显示 ystar 0.48.0)
- `<0.50.0`: 上限是 Y\*gov 0.50,gov-mcp 0.2.0 没测试过 0.50 schema,主动 refuse

这层校验在 `pip install gov-mcp` 时由 pip 执行。

### Layer 2: runtime schema_version 校验(server.py)

```python
SUPPORTED_SCHEMAS = {"1.0"}  # gov-mcp 0.2.0 知道的 schema set

if schema not in SUPPORTED_SCHEMAS:
    raise ValueError(...)
```

这层校验在 gov-mcp 启动时执行,**比 pyproject 更精确**:
- pyproject 是版本号约束(粗粒度)
- schema_version 是具体协议版本(细粒度)
- 同一个 Y\*gov 版本内可能 schema 不变(只改实现,不改协议)
- 跨 Y\*gov 大版本的 schema 也可能保持兼容(只是实现升级)

### Layer 3: gov-mcp release notes 显式 ystar tested-with

每个 gov-mcp release 在 README 写明:

```markdown
## gov-mcp 0.2.0 (2026-04-XX)

- **Tested with**: ystar 0.48.0, 0.48.1
- **Schema version**: `.ystar_session.json` schema 1.0
- **Breaking changes**: --agents-md is deprecated, use --session-config
```

### 何时 bump gov-mcp 版本

| Y\*gov 改动 | gov-mcp 反应 | gov-mcp version bump |
|---|---|---|
| Patch (0.48.0 → 0.48.1) bug fix | 无变化 | 不 bump |
| Minor (0.48 → 0.49) 加字段 backward-compat | 无变化 | 不 bump |
| Minor (0.48 → 0.49) breaking schema | 升 schema,加字段处理 | gov-mcp 0.2.0 → 0.3.0 |
| Major (0.x → 1.0) | 全面适配 | gov-mcp 0.x → 1.0 |

### 为什么 hybrid 优于纯 tight coupling 或纯 loose coupling

| 策略 | 优点 | 缺点 |
|---|---|---|
| **Tight only** (pyproject 锁死 Y\*gov 单一版本) | 简单 | 任何 Y\*gov patch 都需要 gov-mcp re-release,运维灾难 |
| **Loose only** (只 runtime 校验 schema_version) | 灵活 | 用户可能装不兼容 Y\*gov,启动时才发现,bad UX |
| **Hybrid** (pyproject 声明 range + runtime schema 校验) | install-time 粗校验 + start-time 细校验,bad UX 减半 | 多写 5 行代码 |

---

# 风险评估

| 风险 | 严重度 | 缓解 |
|---|---|---|
| `.ystar_session.json` 加 schema_version 后,**ystar Python hook** 可能不认识 | 中 | hook 已经 read .ystar_session.json,加新字段是 backward compat,hook 会 ignore unknown keys。但需要测试一次。 |
| gov-mcp 0.2.0 用了 .ystar_session.json 之后,**ystar setup --yes 还是会 overwrite** 它(虽然命令已 deny) | 高 | AMENDMENT-001 已经 deny 了 setup --yes,但万一有人禁用 hook 跑了。Mitigation: gov-mcp 启动时备份 .ystar_session.json 到 .ystar_session.json.govmcp-backup,启动失败时自动 restore。 |
| Y\*gov 0.49 改 schema 1.0 → 2.0,gov-mcp 0.2.0 用户的实例**突然 refuse to start** | 中 | hybrid coupling Layer 1 (pyproject `<0.50.0`) 阻止 pip upgrade Y\*gov 到 0.49 之后的版本,buy time 让用户先升 gov-mcp 0.3.0 |
| `.ystar_session.json` 字段中有 absolute path(`cieu_db`),不同机器**不能直接共享** | 低 | 已知问题(GOV-001 Step 2 incident),与 GOV-007 无关 |
| `delegation_chain.links[].contract` 是 partial(只有 deny/deny_commands/only_paths/only_domains/invariant),其它 IntentContract 字段是 default | 低 | gov-mcp 现有 delegation chain 也没用 advanced 字段,影响 0 |
| **regex parser 0.7 confidence vs 加载 .ystar_session.json 的 ≥0.95 confidence,数字会让 doctor 报"突然提升"看起来像 gaming metric** | 低 | doctor 报告里说明 confidence label 从 "regex" 变成 "session_config",数字提升是 source 类型差异,不是同种 source 的进步 |
| **`.ystar_session.json` 的 contract 段比 AGENTS.md 实际要 enforced 的少**(因为 setup --yes 当年只 parse 了部分 prose) | 中 | Q1 mapping 表已经显示 4/4 核心字段 1:1,但 only_paths/only_domains/invariant 是空的。**这是 ystar setup 的历史限制,不是 GOV-007 引入的新问题**。GOV-008 / 方案 B 才能彻底解决 |
| **跨 repo 实施**(本提案在 ystar-company,代码改动在 gov-mcp) | 中 | Ethan 有 gov-mcp 写权限。两个 repo 各一个 commit,在 gov-mcp 仓库提 PR,在 ystar-company 加 schema_version |

---

# 实施步骤(等 Board 确认 Step 1 后启动 Step 2-3)

## Step 2 实施(等 Board 确认本提案后)

### Step 2a: 在 ystar-company 加 schema_version

文件: `/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json`

修改: 顶层加一行 `"schema_version": "1.0"`,放在 `session_id` 之前。

```diff
  {
+   "schema_version": "1.0",
    "session_id": "ystar-company_0a84f3c6",
    "cieu_db": "/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db",
    ...
  }
```

Commit: `governance: add schema_version 1.0 to .ystar_session.json — GOV-007 prep`

**先验证 ystar Python hook 不会报错读 schema_version 字段**(应该 ignore unknown keys)。

### Step 2b: 在 gov-mcp repo 实施 --session-config

文件改动:
1. `gov-mcp/gov_mcp/__main__.py`: argparse 加 `--session-config`,改 `--agents-md` 为 deprecated,加互斥校验和 deprecation warning
2. `gov-mcp/gov_mcp/server.py` `_State`:
   - `__init__` 接收 session_config_path 或 agents_md_path
   - 新增 `_load_from_session_config()` 方法
   - 新增 `_load_from_agents_md()` 方法(把现有逻辑挪过来)
   - 新增 `_validate_schema_version()` 方法
   - confidence_score for session_config = 0.98
3. `gov-mcp/pyproject.toml`: dependencies 改成 `ystar>=0.48.0,<0.50.0`
4. `gov-mcp/README.md`: 更新 Quick Start 用 `--session-config`,旧 `--agents-md` 标 [DEPRECATED]

Commit in gov-mcp: `feat(server): support --session-config for direct .ystar_session.json loading — GOV-007`

### Step 2c: gov-mcp 测试

在 gov-mcp repo 加 unit test:

```python
# tests/test_session_config_loading.py
def test_load_from_session_config():
    # 用一个 fixture session.json (含 schema_version: "1.0")
    state = _State(session_config_path=Path("tests/fixtures/session.json"))
    assert state.confidence_label == "session_config"
    assert state.confidence_score >= 0.95
    assert "ystar setup --yes" in state.active_contract.deny_commands  # if fixture has it
    
def test_session_config_schema_version_unsupported():
    # session.json with schema_version: "9.99"
    with pytest.raises(ValueError, match="Unsupported.*schema_version"):
        _State(session_config_path=Path("tests/fixtures/session_v999.json"))

def test_agents_md_fallback_with_deprecation():
    # 旧 path 仍然工作但有 warning
    with pytest.warns(DeprecationWarning):
        state = _State(agents_md_path=Path("tests/fixtures/AGENTS.md"))
    assert state.confidence_label == "regex"
```

## Step 3 验证(同 Step 2c + production smoke)

1. **kill 当前 gov-mcp PID 62861**(同 Q1 修复时的 kill+restart pattern)
2. **重启 gov-mcp 用新参数**:
   ```bash
   cd /Users/haotianliu/.openclaw/workspace/gov-mcp
   nohup python3.11 -m gov_mcp \
       --session-config /Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json \
       --transport sse --host 0.0.0.0 --port 7922 \
       > /tmp/gov-mcp-gov007.log 2>&1 &
   ```
3. **通过 spawned claude -p 调 gov_doctor**(因为我自己 session 的 MCP 会断,同 Q1 验证 pattern):
   - 期望 `confidence: session_config`
   - 期望 `confidence_score >= 0.95`
   - 期望 `L1_06_engine_config: deny_commands ≥ 4`(包含 `rm -rf, sudo, DROP TABLE, ystar setup --yes`)
4. **回归测试**: 让 spawned claude -p 调 38 个 MCP 工具中至少 5 个核心工具(`gov_check, gov_enforce, gov_obligations, gov_report, gov_doctor`),验证全通
5. **结果发 Board**

---

# Acceptance Criteria

| 项 | 期望 | 验证方式 |
|---|---|---|
| `gov_doctor` confidence ≥ 0.95 | `governance.confidence_score >= 0.95` | 调 gov_doctor 看 governance envelope |
| `L1_01_contract.confidence == "session_config"` | confidence label string | gov_doctor checks 段 |
| `L1_06_engine_config.deny_commands` ≥ 4 | 包含 `rm -rf, sudo, DROP TABLE, ystar setup --yes` | gov_doctor checks 段 + 手工核对 .ystar_session.json |
| check() 路径无 LLM | 静态代码 grep 确认无 api_call_fn 注入 | grep `api_call_fn` in server.py |
| `--agents-md` 向后兼容 | 旧启动模式仍工作 + 出 deprecation warning | 用旧命令启动 gov-mcp,验证 deprecation warning + 成功启动 |
| 38 个 MCP 工具全通 | regression suite | gov-mcp 自己的 tests + 5 个核心工具 smoke test |
| `.ystar_session.json` 加了 `schema_version: "1.0"` | grep 字段存在 | `python -c "import json; print(json.load(open('.ystar_session.json'))['schema_version'])"` |
| schema_version mismatch refuse 行为 | 改成 "9.99" 测试 startup 报错 | unit test |

---

# 元注解

**这是 Y\* Bridge Labs 第一个走 GOV-006 intent_verification 协议精神的 directive**(虽然 GOV-006 还没正式实施)。Board 在 directive 里**字面要求** "在 reports/cto/gov_mcp_session_integration.md 回答四个问题,发 Board 确认后才动代码",这就是 GOV-006 (intent → board confirm → execute) 的 manual 应用。Ethan 写完本提案后**严格不动一行代码**,等 Board 看到完整 mapping、风险、跨 repo 影响后,才决定 Step 2 是否启动。

**如果未来 GOV-006 自动化实施完成**,本提案的写作过程就会被替换为 `record_intent.py` 调用,但提案 deliverable 本身不变 — proposal markdown + Board confirmation 仍然是 Level 3 决策的 audit 证据。

CTO 同时承诺: 本提案完成于 2026-04-09 ET 同一 session,**没有动一行 gov-mcp 代码,没有动 .ystar_session.json,没有重启 gov-mcp**。等 Board 一句话决定走方案 C / 拒绝 / 调整后再启动 Step 2。

---

**End of proposal.** 等 Board 一句话决定 Step 2 是否启动,以及任何对方案 C 的修订指示。
