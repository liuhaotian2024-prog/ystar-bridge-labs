# gov-order: Board 自然语言 → CIEU obligation 自动执行管道

**作者**: Ethan Wright (CTO)
**日期**: 2026-04-09
**优先级**: P0(GOV-008 directive)
**权限层级**: **Level 3**(新治理工具 + 引入 LLM 依赖到 contract authoring 路径 + 跨 6 岗位影响 + 与 GOV-006 紧耦合)
**状态**: Step 1 research only,等 Board 确认才动 Step 2 代码
**触发**: Board GOV-008 directive (2026-04-09)
**前置文档**:
- `reports/cto/nl_to_contract_pipeline_feasibility.md`(commit `dbf4d8f`,GOV-007 Step 2 expanded scope 的可行性研究——Board 否决了那个版本的 human-in-loop 设计,选了 zero-friction 方向)
- `reports/cto/intent_verification_proposal.md`(GOV-006 提案,Board 已批 C 方案,task #57 等下次 session 实施)
- `governance/INTERNAL_GOVERNANCE.md` 三级权限层级(GOV-005 Part 2)

---

## 1. 关键 tensions Ethan 必须先 flag(诚实先行)

### Tension 1: "无需 Board 确认" vs 我之前的 human-in-loop 推荐

之前 commit `dbf4d8f` 的 NL pipeline 可行性研究,我推荐 "LLM 翻译 → diff review → Board 说确认 → write contract"。Board 现在 GOV-008 显式 override:**全程零摩擦,无需 Board 确认**。

**Board 的决策更激进,但有 internal logic**:

- **Board 是 source of authority**——Board 自己的话不需要"再被 Board 确认"。GOV-006 (task #57) intent_verification 是为 **agent 侧** 的 intent 设计的(agent → Board confirm),不是为 Board 侧的 intent。Board 自己说的话进入 audit chain 不需要再过 Board 一遍 gate。
- **diff review 是 friction**——如果每次 Board 说一句话都要 Board 看 diff 然后说"确认",Board 就成了系统的 bottleneck。GOV-008 的设计哲学是"Board 输入即 truth",由 deterministic 复核层 (`translate_to_contract`) 抓 LLM 错误,而不是由 Board 抓。
- **接受 LLM 翻译误差,换零摩擦**——LLM 偶尔会翻译错(我可行性研究里 estimate 是 70-80% 准确)。Board 认为这是可接受的成本,因为(a)deterministic 复核可以挡掉明显的错误,(b)`save-to-pending` 兜底所有不可靠翻译,(c)真错误可以 rollback(单独 task)。

**Ethan 的观点**: Board 的判断比我之前的更激进,但**也更符合 Board 自己作为 authority 的角色**。我之前的 human-in-loop 是 over-engineering——它把 Board 当成"另一个需要被审批的 agent",而 Board 实际上是审批者本身。Board 的话进入系统不需要"被审批",只需要"被忠实翻译"。**采纳 Board 的 zero-friction 方向**。

### Tension 2: "前置条件 GOV-006 必须先实施" vs gov-006 task #57 仍 pending

Board 说 "gov-order 依赖 INTENT_RECORDED 机制",意味着 gov-006 必须先有 record_intent.py + INTENT_RECORDED CIEU 事件 schema,gov-008 才能 reuse。

**当前状态**: GOV-006 task #57 是 pending,Board 已批 C 方案但还没实施。

**排期含义**: gov-008 Step 2 实施 **必须发生在 GOV-006 实施之后**。Step 1 (本研究) 可以现在写,但 Step 2 启动前 Board 必须先批准 GOV-006 实施 + 让我做完。

**两种处理路径**:
- **A**: GOV-006 task #57 先实施 → 然后 gov-008 Step 2 实施。安全,顺序清晰。
- **B**: gov-008 Step 2 自己**临时定义** INTENT_RECORDED schema(基于 GOV-006 提案的 C 方案设计),GOV-006 后续实施时 reuse 同一 schema。快但有协调风险(gov-008 定的 schema 可能和 GOV-006 实施时想用的不完全一致)。

**Ethan 的推荐**: A。GOV-006 半天工程,先做完再做 gov-008,顺序自然,避免 schema 双定义。

### Tension 3: "用户当前环境的 LLM 配置" + "不硬编码任何厂商" + "降级优雅"

这是 portability 要求。需要检测多种 LLM provider 配置,优雅 fallback,无 LLM 时 gracefully 降级到手动模式。这是设计上的约束,不是 tension。下面 §5 详细设计。

---

## 2. 当前状态 Xt

- **Board 想说的话进 CIEU 的现有路径**: 没有自动化路径
  - Board 在 chat 里说一句话
  - Aiden 或 Ethan 手动理解,手动调用 `scripts/register_obligation.py` 或手动写 `BOARD_CHARTER_AMENDMENTS.md`
  - 多步 + 易遗漏(GOV-001 Step 4-7 等历史已经多次出现"Board 说过的话被忘记")
- **现有可复用组件**:
  - `scripts/register_obligation.py`(GOV-001 Step 5 commit `ca0910e`):接受 CLI 参数,写 OBLIGATION_REGISTERED CIEU 事件
  - `scripts/check_obligations.py`(同上):查询 / mark fulfilled
  - `ystar.kernel.nl_to_contract.translate_to_contract(text, api_call_fn)`:Y*gov 已有的翻译函数,默认 regex,可注入 LLM
  - `ystar.governance.cieu_store.CIEUStore`:写 CIEU 记录的标准接口
  - `gov-mcp` 现在(post GOV-007 Step 2,commit `69a9b7c`)读 `.ystar_session.json`——任何对 .ystar_session.json 的更新都会被 gov-mcp 在重启或 SIGHUP 后看到(GOV-008 不需要每次更新都重启 gov-mcp,因为 gov-008 写的是 CIEU obligation 而不是 .ystar_session.json contract;contract 不变,enforcement 不变)
- **关键差异**: GOV-008 写的是 **runtime obligations**(进 CIEU),不是 **persistent contract rules**(进 .ystar_session.json)。这是范围澄清——
  - 下令 "ethan 今晚 22:00 前完成 X" → obligation,gov-008 处理
  - 下令 "从今往后任何 agent 不许动 production database" → contract rule,**未来另一个 directive**(GOV-009?),不在 GOV-008 范围

### 范围边界(必须明确,否则 GOV-008 会蔓延)

| 输入类型 | 例子 | 是 GOV-008 范围? | 实际处理 |
|---|---|---|---|
| 一次性 task | "ethan 明天前把 X 修好" | ✅ YES | gov-order → register_obligation (CIEU) |
| 重复 task | "secretary 每周一发周报" | ✅ YES (注册 recurring obligation) | gov-order → register_obligation with recurrence flag |
| 永久 deny rule | "从今往后任何 agent 不许 X" | ❌ NO | 走 BOARD_CHARTER_AMENDMENTS 流程,改 .ystar_session.json contract |
| 价值观陈述 | "我希望团队朝 X 方向努力" | ❌ NO | 归 AGENTS.md prose,Secretary 手动整理 |
| 询问/讨论 | "你觉得 X 怎么样?" | ❌ NO | 普通对话,无需进 CIEU |

**gov-order 必须先判断输入类型**,只对前两种生效,后三种 refuse 或转给其它路径。

---

## 3. 目标 Y*

- Board 在 chat 里说一句 task-shaped 的话 → 在 N 秒内(N ≤ 30)出现一条 CIEU OBLIGATION_REGISTERED 记录
- 全程无需 Board 输入第二句话(zero friction)
- LLM 翻译失败 → save-to-pending,Board 收到一行明确提示"翻译失败,已存入 pending,需手动 review"
- 没装 LLM API 的环境 → 降级为输出 `register_obligation.py` 的等效命令行,Board 看到后可手动复制粘贴
- INTENT_RECORDED 审计事件写入 CIEU,记录原始 NL + LLM 输出 + 验证状态 + 后续 obligation_id(链接)
- 如果 Board 输入是非 task-shaped(deny rule / 价值观 / 询问),refuse with clear message,不强行 register

**Rt = 0 的可观测条件**:

```bash
$ python3.11 scripts/gov_order.py "ethan 明早 9 点前把 GOV-008 实施完"
[gov-order] Detected LLM provider: anthropic
[gov-order] Translating: "ethan 明早 9 点前把 GOV-008 实施完"
[gov-order] LLM proposed obligation:
  owner: cto (Ethan Wright)
  entity_id: BOARD-2026-04-09-001
  due_secs: 39600 (about 11 hours)
  rule_id: gov_008_implementation_cto
  severity: high
[gov-order] Deterministic verification: PASS
[gov-order] INTENT_RECORDED CIEU event: int_a3b1c2...
[gov-order] OBLIGATION_REGISTERED CIEU event: ob_d4e5f6...
[gov-order] Done. obligation_id: d4e5f6...
[gov-order]   Run check_obligations.py --actor cto to see it.
```

---

## 4. 完整链路(GOV-008 directive 给的图,我精化版本)

```
Board 在 chat 说一句话
  │
  ▼
scripts/gov_order.py "<sentence>"     ← 入口 (CLI 或 Python import)
  │
  ▼
[1] LLM provider detection             ← portable, env-driven, no hardcode
  │   detect: ANTHROPIC_API_KEY / OPENAI_API_KEY / OLLAMA_HOST / LM_STUDIO_HOST / ...
  │   no provider → manual fallback (echo register_obligation.py command)
  │
  ▼
[2] LLM 翻译                           ← prompt 设计 § 5
  │   input: NL sentence + structured prompt
  │   output: JSON {owner, entity_id, rule_id, rule_name, description, due_secs, severity, required_event}
  │
  ▼
[3] Deterministic 复核 (translate_to_contract pass)
  │   - JSON schema validation
  │   - Field type / range / enum 检查
  │   - 跟 .ystar_session.json 现有 contract 的一致性 (e.g. owner ∈ agent_display_names keys)
  │   - 复核失败 → 跳到 [save-to-pending]
  │
  ▼
[4] INTENT_RECORDED CIEU 事件 (依赖 GOV-006 record_intent.py)
  │   原始 NL + LLM 输出 + provider name + 复核 status
  │   返回 intent_id,作为后续 obligation 的 trigger_event_id
  │
  ▼
[5] register_obligation.py 程序化调用 (Python import,不是 subprocess)
  │   把 [3] 验证过的 dict 直接 pass 给 register_obligation 函数
  │   写 OBLIGATION_REGISTERED CIEU 事件
  │
  ▼
[6] 输出 success message + obligation_id 给 Board
  │
  └─→ agent 下次 session 启动时调用 check_obligations.py --actor <self>,
      看到这条 obligation,执行,完成后 mark fulfilled
```

**Failure path**:

```
LLM 翻译失败 / 复核失败
  ↓
[save-to-pending]
  写 reports/board_proposed_changes/pending/YYYY-MM-DD-HHMMSS-rejected.json
  内容: {nl, llm_output, validation_errors, timestamp, suggested_manual_command}
  ↓
打印提示给 Board: "翻译失败已存 pending,请 manual review。
建议命令: python3.11 scripts/register_obligation.py --owner ... --entity-id ..."
  ↓
exit 0 (不报错,优雅降级)
```

---

## 5. LLM 翻译层设计

### 5.1 Prompt 设计

```text
You are translating a Y*Bridge Labs Board directive into a structured
obligation record. Output exactly one JSON object, nothing else.

Schema:
{
  "owner": one of [ceo, cto, cmo, cso, cfo, secretary],
  "entity_id": format BOARD-YYYY-MM-DD-NNN, or reuse if Board mentions
               an existing directive ID (GOV-001, AMENDMENT-001, etc.)
  "rule_id": short snake_case identifier, e.g. "gov_008_impl_cto"
  "rule_name": human-readable obligation name
  "description": one-paragraph description of what the agent must do
  "due_secs": deadline in seconds from now
              ("today" = 28800, "tonight" = 14400, "this week" = 604800,
               "tomorrow morning 9am" = approximate seconds-to-tomorrow-9am,
               specific datetime → seconds from now to that datetime)
  "severity": one of [low, medium, high, critical]
  "required_event": one of [acknowledgement_event, completion_event,
                            result_publication_event, status_update_event]
}

Rules:
1. If Board's sentence is NOT a task (it's a deny rule, value statement,
   or question), output {"_input_type": "non_task", "reason": "..."}.
   gov-order will refuse to register and tell Board.
2. If you cannot determine a field with high confidence, use null. The
   deterministic verifier will reject null fields and route to pending.
3. owner must be a single agent role (not "all"). If Board says "all
   agents", default to "ceo" (Aiden) who will dispatch.
4. Do not invent fields not in the schema.

Input: {board_sentence}

Output JSON:
```

**Why this prompt is honest about its own limits**:

- "If you cannot determine a field with high confidence, use null" — 让 LLM 主动报告不确定,而不是 hallucinate
- "The deterministic verifier will reject null fields" — LLM 知道 null 会被拒,所以会尽量不留 null
- "non_task" 输出类别 — 让 LLM 主动 surface 范围外的输入,gov-order 不会强行 register 一句"我希望我们朝 X 方向努力"

### 5.2 LLM provider detection + abstraction

**Detection chain**(优先级从高到低):

```python
# scripts/gov_order_llm.py (or inline in gov_order.py)

def detect_llm_provider() -> Optional[Tuple[str, str, Callable]]:
    """Returns (provider_name, model, call_fn) or None if no provider available.

    Detection chain (priority order):
      1. Anthropic — ANTHROPIC_API_KEY env var
      2. OpenAI    — OPENAI_API_KEY env var
      3. Ollama    — OLLAMA_HOST env var or `ollama` binary in PATH
      4. LM Studio — LM_STUDIO_HOST env var
      5. None      — graceful degradation, manual mode

    The detection is non-destructive: probes env vars and `which` for
    binary, no API calls. Returns the first match.
    """
    import os, shutil

    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic  # noqa
            return ("anthropic", "claude-sonnet-4-5", _anthropic_call)
        except ImportError:
            pass  # SDK not installed, try next

    if os.environ.get("OPENAI_API_KEY"):
        try:
            import openai  # noqa
            return ("openai", "gpt-4o", _openai_call)
        except ImportError:
            pass

    if os.environ.get("OLLAMA_HOST") or shutil.which("ollama"):
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        model = os.environ.get("OLLAMA_MODEL", "llama3")
        return ("ollama", model, lambda p: _ollama_call(host, model, p))

    if os.environ.get("LM_STUDIO_HOST"):
        host = os.environ["LM_STUDIO_HOST"]
        model = os.environ.get("LM_STUDIO_MODEL", "default")
        return ("lm_studio", model, lambda p: _lm_studio_call(host, model, p))

    return None  # no provider, manual fallback
```

**Provider call functions** are simple wrappers — anthropic.messages.create, openai.chat.completions.create, requests.post(ollama_host + "/api/generate"), etc.

**Why this design**:

- **Env-var driven**: 用户改环境变量切 provider,不需要改代码。无 hardcode。
- **Lazy import**: anthropic / openai SDK 只在 detected 时才 import,避免给没装 SDK 的用户 ImportError。
- **Probe-only detection**: 只看 env var + binary 存在性,不发实际 API 调用,启动快、无 cost。
- **Manual fallback**: 没 provider 时返回 None,gov_order.py 输出 etc effective register_obligation.py 命令,用户手动复制粘贴执行。

### 5.3 LLM 调用失败处理

| 失败类型 | 处理 |
|---|---|
| API key 无效(401) | print 错误 + save-to-pending |
| API 限流(429) | exponential backoff retry 3 次,仍失败 → save-to-pending |
| API 超时 | 30s timeout, 失败 → save-to-pending |
| 输出不是 JSON | 尝试用 regex 抠 JSON 块,失败 → save-to-pending |
| JSON 但不符合 schema | save-to-pending |
| LLM 输出 `_input_type: non_task` | refuse,告知 Board "this looks like a non-task sentence,not registering" |

**所有失败都不报错给 Board**(per directive: "降级优雅,给出明确提示")。

---

## 6. translate_to_contract() 作为 deterministic 复核层

**Board directive 原文**: "translate_to_contract() 如何作为确定性复核层验证 LLM 的输出?"

**重要 clarification**: `translate_to_contract()` 的设计意图是 **AGENTS.md prose → IntentContract dict**。它不是 obligation 字段验证器。LLM 输出的是 **obligation params**(owner, due_secs, ...),不是 IntentContract。两者是不同 schema。

**因此 deterministic 复核层不能直接用 `translate_to_contract()`**——需要写**新的 deterministic validator**,专门验证 obligation params。

**复核 validator 设计**:

```python
def validate_obligation_dict(d: Dict[str, Any]) -> List[str]:
    """Returns list of validation errors, empty list = valid."""
    errors = []

    # Required fields
    REQUIRED = {"owner", "entity_id", "rule_id", "rule_name",
                "description", "due_secs", "severity", "required_event"}
    missing = REQUIRED - set(d.keys())
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")

    # Owner must be in known agent roles
    KNOWN_OWNERS = {"ceo", "cto", "cmo", "cso", "cfo", "secretary"}
    if d.get("owner") not in KNOWN_OWNERS:
        errors.append(f"owner '{d.get('owner')}' not in {sorted(KNOWN_OWNERS)}")

    # Severity enum
    if d.get("severity") not in {"low", "medium", "high", "critical"}:
        errors.append(f"severity '{d.get('severity')}' invalid")

    # required_event enum
    KNOWN_EVENTS = {"acknowledgement_event", "completion_event",
                    "result_publication_event", "status_update_event"}
    if d.get("required_event") not in KNOWN_EVENTS:
        errors.append(f"required_event '{d.get('required_event')}' invalid")

    # due_secs must be positive number
    due = d.get("due_secs")
    if not isinstance(due, (int, float)) or due <= 0:
        errors.append(f"due_secs '{due}' must be positive number")

    # description non-empty
    desc = d.get("description", "")
    if not isinstance(desc, str) or len(desc.strip()) < 10:
        errors.append(f"description too short or empty")

    # rule_id format (snake_case, no spaces)
    rule_id = d.get("rule_id", "")
    if not rule_id or " " in rule_id or not rule_id.replace("_", "").isalnum():
        errors.append(f"rule_id '{rule_id}' must be snake_case alphanumeric")

    # entity_id format
    entity_id = d.get("entity_id", "")
    if not entity_id or len(entity_id) > 80:
        errors.append(f"entity_id '{entity_id}' invalid")

    # cross-check: owner agent_id must exist in .ystar_session.json
    # (this is the consistency-with-current-contract check)
    try:
        import json
        with open(".ystar_session.json") as f:
            session = json.load(f)
        display_names = session.get("agent_display_names", {})
        if d.get("owner") not in display_names:
            errors.append(
                f"owner '{d.get('owner')}' not in .ystar_session.json "
                f"agent_display_names; available: {sorted(display_names.keys())}"
            )
    except (OSError, json.JSONDecodeError):
        pass  # session file unreadable, skip this check

    return errors
```

**Why this is deterministic**:
- Pure Python,no LLM
- Pure schema validation,no fuzzy matching
- Reads `.ystar_session.json` for cross-reference (consistent with the source of truth)
- Returns explicit error list,easy to log to save-to-pending

**This is the "deterministic complement" Board asked for**——LLM 翻译可能错,但**所有 LLM 输出都必须通过这个 validator** 才能进 CIEU。LLM 是 best-effort translator,validator 是 hard gate。

---

## 7. register_obligation.py 程序化调用

**Board 原文**: "register_obligation.py 如何被程序化调用而不是人工敲命令行?"

**两个选项**:

| 方案 | 做法 | 优 | 劣 |
|---|---|---|---|
| **A. subprocess** | `subprocess.run(["python3.11", "scripts/register_obligation.py", "--owner", ...])` | 不需要改 register_obligation.py | 慢(subprocess 启动 ~200ms);brittle(参数解析二次发生);Y\*gov hook 检查每次 |
| **B. Python import + 函数调用** | refactor register_obligation.py 暴露 `register_obligation_programmatic(owner=..., ...)` 函数,gov_order.py 直接 import 调用 | 快(0 subprocess 开销);干净(单次解析);可测试(unit test 能 import 同一函数) | 需要小幅 refactor register_obligation.py(把 main() 内的逻辑提到一个独立函数) |

**推荐: B**。

**Refactor 范围**: `scripts/register_obligation.py` 已经是 175 行,把 `main()` 内的核心逻辑(build engine + register entity + ingest event + write CIEU)提到一个独立函数 `register_obligation_programmatic(...)`,`main()` 改成 thin wrapper(parse argparse + 调函数)。这样:
- CLI 用法不变(向后兼容)
- gov_order.py `from register_obligation import register_obligation_programmatic`
- Unit test 可以直接调函数,不需要 subprocess

**Refactor 工作量**: ~30 分钟。Step 2 实施时一并做。

---

## 8. INTENT_RECORDED 集成 (与 GOV-006 关系)

**Board 原文**: "前置条件: GOV-006 必须先实施"

**INTENT_RECORDED 在 gov-order 上下文的语义**:

- **GOV-006 task #57 原意**: agent 收到 Level 2/3 directive → 写 INTENT_RECORDED → Board 看 → Board 写 INTENT_CONFIRMED → agent 执行
- **GOV-008 gov-order 复用**: gov-order 把 Board 的 NL + LLM translation + validation 状态写 INTENT_RECORDED,**没有 INTENT_CONFIRMED 步骤**(Board 本身就是 source of truth,不需要再 confirm 自己)

**字段 schema(gov-order 用法)**:

```python
intent_record = {
    "event_id": str(uuid.uuid4()),
    "session_id": entity_id,         # e.g. "BOARD-2026-04-09-001"
    "agent_id": "board",              # 谁说的话
    "event_type": "INTENT_RECORDED",
    "decision": "info",
    "evidence_grade": "intent",
    "params": {
        "source": "gov_order",        # 区分 GOV-006 (agent intent) 和 GOV-008 (board intent)
        "input_nl": board_sentence,
        "llm_provider": provider_name,
        "llm_model": model,
        "llm_output": llm_dict,       # raw LLM JSON
        "validation_status": "pass" | "fail" | "non_task",
        "validation_errors": [...] if validation_status == "fail" else [],
        "subsequent_obligation_id": obligation_id if validation_status == "pass" else None,
        "registered_at": time.time(),
    },
    ...
}
```

**Why this integrates with GOV-006 cleanly**:

- 同一 `event_type = "INTENT_RECORDED"`,同一 CIEU schema → check_obligations.py 等查询工具不需要分叉
- `params.source` 字段区分 origin (gov_order vs agent_self)→ 用查询 filter
- `params.subsequent_obligation_id` 链接到 OBLIGATION_REGISTERED 事件 → 完整因果链(NL → intent → obligation → execution → fulfillment)

**依赖关系澄清**: gov-order 不依赖 GOV-006 的 record_intent.py CLI 工具——它依赖 INTENT_RECORDED **CIEU schema**。gov-008 实施时直接写 schema,如果 GOV-006 已实施 then reuse,如果未实施 then gov-008 是 first mover 且 GOV-006 后续 reuse。

**推荐排期**: GOV-006 task #57 先实施(半天)→ gov-008 Step 2 实施(半天 + 测试)。这是 Tension 2 的 A 方案。

---

## 9. save-to-pending 设计

**Board 原文**: "翻译失败时(LLM 输出不符合 schema)选 save-to-pending"

**Pending 文件 schema**:

```json
{
  "version": "1.0",
  "timestamp": "2026-04-09T22:00:00Z",
  "input_nl": "ethan 明天前把 X 修好",
  "llm_provider": "anthropic",
  "llm_model": "claude-sonnet-4-5",
  "llm_raw_output": "...",
  "llm_parsed_dict": { ... },
  "validation_errors": [
    "owner 'engineering' not in [ceo, cto, cmo, cso, cfo, secretary]",
    "due_secs '0' must be positive number"
  ],
  "suggested_manual_command": "python3.11 scripts/register_obligation.py \\\n  --owner cto \\\n  --entity-id BOARD-2026-04-09-001 \\\n  --rule-id ...\\\n  --due-secs 28800 \\\n  --severity high",
  "review_status": "pending"
}
```

**Pending 目录**: `reports/board_proposed_changes/pending/`(GOV-008 创建,如果不存在)

**文件命名**: `YYYY-MM-DD-HHMMSS-rejected-{rule_id_or_unknown}.json`

**Secretary 职责** (写进 agents/Secretary.md GOV-008 段落):
- 每周一审计 `pending/` 目录
- 对每条 pending 决定: (a) 修正后手动 register,(b) 标记为 "intentionally dropped",(c) 反馈给 Board "你说的 X 我没解析出来"
- 审计完后移到 `reports/board_proposed_changes/reviewed/YYYY-MM-DD/`

**Output 给 Board 的提示**(降级优雅):

```text
[gov-order] LLM 翻译失败(see validation_errors below)
[gov-order] 已存到 pending: reports/board_proposed_changes/pending/2026-04-09-220000-rejected-unknown.json
[gov-order] 错误:
  - owner 'engineering' not in [ceo, cto, cmo, cso, cfo, secretary]
  - due_secs '0' must be positive number
[gov-order] 你可以手动注册:
  python3.11 scripts/register_obligation.py \\
      --owner cto \\
      --entity-id BOARD-2026-04-09-001 \\
      --rule-id ... \\
      --due-secs 28800 \\
      --severity high \\
      --rule-name "..." \\
      --description "..."
[gov-order] 或者重新说一遍,描述更具体一些。
```

**No exception raised**, exit code 0, Board 看到提示后决定下一步。

---

## 10. 完整实施代码骨架(供 Step 2 实施时参考)

```python
#!/usr/bin/env python3.11
"""
gov_order.py — Board NL → CIEU obligation auto-pipeline (GOV-008)

Usage:
    python3.11 scripts/gov_order.py "ethan 明早 9 点前把 GOV-008 实施完"
    python3.11 scripts/gov_order.py --db .ystar_cieu.db "..."
"""
import argparse, json, os, sys, time, uuid

from typing import Optional, Tuple, Callable, Dict, Any

# Will be implemented in Step 2 — placeholder structure

def main():
    p = argparse.ArgumentParser()
    p.add_argument("nl", help="Board's natural-language directive")
    p.add_argument("--db", default=".ystar_cieu.db")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    print(f"[gov-order] Input: {args.nl!r}")

    # ── 1. LLM provider detection ────────────────────────────────
    provider = detect_llm_provider()
    if provider is None:
        print("[gov-order] No LLM provider detected. Manual fallback:")
        print(_manual_fallback_message(args.nl))
        sys.exit(0)
    name, model, call_fn = provider
    print(f"[gov-order] Using {name}/{model}")

    # ── 2. LLM translation ────────────────────────────────────────
    try:
        llm_output = call_fn(_build_prompt(args.nl))
    except Exception as e:
        _save_pending(args.nl, name, model, None, [f"LLM call failed: {e}"])
        print(f"[gov-order] LLM call failed: {e}")
        sys.exit(0)

    # Parse JSON
    try:
        llm_dict = _extract_json(llm_output)
    except ValueError as e:
        _save_pending(args.nl, name, model, llm_output, [f"JSON parse: {e}"])
        print(f"[gov-order] LLM output not valid JSON: {e}")
        sys.exit(0)

    # ── 3. Non-task detection ────────────────────────────────────
    if llm_dict.get("_input_type") == "non_task":
        print(f"[gov-order] Input classified as non-task: {llm_dict.get('reason')}")
        print(f"[gov-order] Not registering. If this is a contract rule, use BOARD_CHARTER_AMENDMENTS.")
        sys.exit(0)

    # ── 4. Deterministic verification ────────────────────────────
    errors = validate_obligation_dict(llm_dict)
    if errors:
        _save_pending(args.nl, name, model, llm_dict, errors)
        print("[gov-order] LLM output failed validation:")
        for e in errors:
            print(f"  - {e}")
        print(f"[gov-order] Saved to pending. Run manual:")
        print(_manual_fallback_message(args.nl, partial=llm_dict))
        sys.exit(0)

    # ── 5. INTENT_RECORDED CIEU event ────────────────────────────
    intent_id = _write_intent_record(args.db, args.nl, name, model, llm_dict)
    print(f"[gov-order] INTENT_RECORDED: {intent_id}")

    if args.dry_run:
        print("[gov-order] DRY RUN — would register obligation, exiting")
        sys.exit(0)

    # ── 6. Programmatic register_obligation.py call ──────────────
    from register_obligation import register_obligation_programmatic
    obligation_id = register_obligation_programmatic(
        db_path=args.db,
        entity_id=llm_dict["entity_id"],
        owner=llm_dict["owner"],
        rule_id=llm_dict["rule_id"],
        rule_name=llm_dict["rule_name"],
        description=llm_dict["description"],
        due_secs=llm_dict["due_secs"],
        severity=llm_dict["severity"],
        required_event=llm_dict["required_event"],
        initiator="board",
        directive_ref=llm_dict["entity_id"],
        trigger_event_id=intent_id,  # link CIEU events
    )

    # ── 7. Update INTENT_RECORDED with subsequent_obligation_id ──
    # (or write a separate CIEU event linking the two)

    # ── 8. Output success ────────────────────────────────────────
    print(f"[gov-order] OBLIGATION_REGISTERED: {obligation_id}")
    print(f"[gov-order] Owner: {llm_dict['owner']}, due in {llm_dict['due_secs']}s")
    print(f"[gov-order] Run check_obligations.py --actor {llm_dict['owner']} to verify")


# Helper functions (LLM detect, prompt build, validate, save-pending, etc.)
# Bodies omitted in skeleton; full implementation in Step 2.

if __name__ == "__main__":
    main()
```

**预估行数**: ~400 行 (包含 helpers + LLM provider adapters + manual fallback message generator)

---

## 11. 风险评估

| 风险 | 严重度 | Mitigation |
|---|---|---|
| LLM 翻译错误产生错的 obligation,Board 没注意到 | **高** | (a) 强 deterministic validator,(b) gov-order 输出明确显示 LLM proposed fields,(c) 任何 obligation 都进 CIEU 可追溯,(d) 加 `gov_order_undo.py` 工具(GOV-008 sub-task 或单独 directive) |
| LLM provider API 成本累积 | 中 | 每次 gov-order 一次 LLM 调用 ~1-3k tokens (~$0.01-0.05),Board 自然限频 |
| 没装 LLM SDK 的环境 import 失败 | 低 | lazy import + fallback chain,任何一层失败往下走 |
| pending 目录被遗忘审计 | 中 | Secretary 周审计 + 写进 DAILY_SCHEDULE.md weekly check |
| LLM 输出 SQL injection 进 CIEU | 低 | CIEU 用 sqlite3 parametrized query (`?` placeholders),不拼字符串 |
| 同一 NL 重复 register 多次 | 中 | gov-order 检查 entity_id 是否已存在的 OBLIGATION_REGISTERED 记录,有则 refuse + 提示 |
| 跨语言(中英混合输入) | 中 | LLM provider 默认能处理多语言,prompt 不限定语言 |
| Board 输入隐含 deny rule(不是 task) | **高** | LLM `_input_type: non_task` 检测 + 显式 refuse + 提示走 BOARD_CHARTER_AMENDMENTS 流程。**关键边界,不能漏** |
| GOV-006 未实施时 INTENT_RECORDED schema 不存在 | 中 | gov-008 自己定义 schema,当 first mover,GOV-006 后续 reuse(B 路径)。或先做 GOV-006(A 路径,推荐) |
| 跨 repo 一致性 (`register_obligation_programmatic` 不存在) | 中 | Step 2 包含 register_obligation.py 的 refactor |

---

## 12. 实施步骤(Step 2,等 Board 确认本提案后启动)

| Step | 工作 | 时间估算 |
|---|---|---|
| 0 | (前置) 实施 GOV-006 task #57 — record_intent.py + INTENT_RECORDED schema | 4-5 小时 |
| 2a | Refactor `scripts/register_obligation.py` — 提取 `register_obligation_programmatic()` 函数,`main()` 变 thin wrapper | 30 分钟 |
| 2b | 写 `scripts/gov_order.py` — main flow,detect_llm_provider,_build_prompt,_extract_json,validate_obligation_dict,_save_pending,_manual_fallback_message | 3 小时 |
| 2c | LLM provider adapters — _anthropic_call, _openai_call, _ollama_call, _lm_studio_call(每个 ~30 行) | 2 小时 |
| 2d | INTENT_RECORDED CIEU event 写入 — 复用 GOV-006 的 schema | 30 分钟 |
| 2e | 写 `tests/test_gov_order.py` — unit tests for validate_obligation_dict,detect_llm_provider,_extract_json,_save_pending | 2 小时 |
| 2f | 端到端测试: real LLM call (Anthropic),verify CIEU 出现 OBLIGATION_REGISTERED 记录,verify check_obligations.py 能查到 | 1 小时 |
| 2g | 创建 `reports/board_proposed_changes/pending/` 目录 + README + Secretary 周审计文档 | 30 分钟 |
| 2h | 更新 agents/*.md GOV-008 段落 — 让所有 agent 知道 Board 现在有 gov-order 通道,他们应该轮询 check_obligations 看新 obligation | 1 小时 |

**总工程量(不含 GOV-006 前置)**: ~10-12 小时,约 1.5 天工程

**含 GOV-006 前置**: ~14-17 小时,约 2 天工程

---

## 13. Acceptance criteria 映射到 Step 2

| Board acceptance criterion | Step 2 工作 | 验证方法 |
|---|---|---|
| Board 输入自然语言 → CIEU 有 obligation 记录 | Step 2b + 2d + 2f | `check_obligations.py --directive BOARD-...` 看到记录 |
| agent 自动执行 | (依赖现有 check_obligations.py + agent boot 协议) | spawned claude -p 启子 session,看 agent 是否自动 query own obligations |
| 全程无需 Board 确认 | Step 2b 流程图: detect → translate → validate → register,**无 Board input 第二步** | 端到端测试 1 句话出 obligation |
| 无 API 接入时降级优雅,给出明确提示 | Step 2b: detect_llm_provider 返回 None 时输出 manual fallback message | 端到端测试: unset 所有 API key,跑 gov-order,看 fallback message |
| 翻译失败 save-to-pending(不 refuse,不静默丢) | Step 2b: _save_pending + exit 0 + clear print | 端到端测试: 输入故意模糊的 NL,看是否进 pending |

---

## 14. Open questions for Board(等回答才启动 Step 2)

**Q1**: Board 是否同意 GOV-006 task #57 必须先实施?(Tension 2 的 A 路径)

**Q2**: gov-order 输入的范围边界(§ 2 表格)Board 是否同意?具体: "永久 deny rule" 应该 **refuse + 提示走 BOARD_CHARTER_AMENDMENTS**,而不是自动转写 .ystar_session.json contract。这是 GOV-008 vs 未来 GOV-009 的范围划分。

**Q3**: pending 文件的 Secretary 审计 cadence —— Board 想 weekly 还是更频繁?(影响 DAILY_SCHEDULE.md 写法)

**Q4**: LLM 翻译错误的 rollback 机制 —— 是写一个 `gov_order_undo.py` 工具(GOV-008 的 sub-task),还是用更通用的 obligation cancel 机制(单独的 GOV-009 directive)?

**Q5**: gov-order 是否应该有 quota 限制(防止 Board 误用脚本说很多话产生 obligation 风暴)?或者完全信任 Board 自然限频?

---

## 15. 严守 GOV-006 协议(尽管它还没实施)

**0 行代码改动**。**0 个 ystar-company file modify**(除新建本 research 文档)。**0 个 gov-mcp file modify**。**0 个 K9Audit file modify**。**`scripts/gov_order.py` 没创建**。**`scripts/register_obligation.py` 没 refactor**。

deliverable = 1 个 markdown research 文档 (~700 行)。

**这是 Y\*Bridge Labs 第 3 次实践 GOV-006 intent_verification 协议精神**(commit `e80b24e` GOV-007 Step 1 + commit `dbf4d8f` NL pipeline feasibility + 本次 GOV-008 Step 1)。Board 在 directive 字面要求 "发 Board 确认后才动代码" —— 这就是 record_intent 阶段。我现在交付 intent 内容 + reasoning + risk + 5 questions,等 Board 的 confirm 信号。

---

## 16. 推荐执行顺序(给 Board 决策的清晰路径)

**如果 Board 批准本提案,推荐顺序**:

1. **Board 回答 5 个 open questions**(本 turn 之后)
2. **Board 启动 GOV-006 task #57 实施**(先决条件,~5 小时)
3. **Board 启动 gov-008 Step 2 实施**(~10-12 小时)
4. **Step 3 验证: Board 在 chat 说一句话,看 CIEU 是否出现 obligation,agent 是否在下次 session 自动 query 到**
5. **DIRECTIVE_TRACKER GOV-008 标 EXECUTED**

---

**End of design doc.** 等 Board 5 个 open questions 的回答,以及对本研究的整体批准。
