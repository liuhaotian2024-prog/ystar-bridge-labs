# AMENDMENT-012 — Deny-as-Teaching (Governance Transforms from Police to Coach)

| 字段 | 内容 |
|---|---|
| Level | 2 (Infrastructure-level enhancement to existing governance enforcement) |
| 起草人 | eng-domains (Jordan Lee) |
| 起草日期 | 2026-04-13 |
| RAPID | R=Jordan / A=Maya(governance impact)+Ryan(Platform infra) / P=Jordan(implementation) / I=CTO / **D=Board** |
| 前置依赖 | AMENDMENT-009 (priority_brief + article11 hook) / AMENDMENT-010 (11-category boot + behavior_rules codification) |
| 源驱动 | Board 2026-04-13 direct delegation: "denial = teaching moment — agent 撞一次学不会是浪费碰撞。每次 deny 返回结构化正确步骤 + skill ref + incident ref，让 deny 成为 in-context 教学" |

---

## §0. TL;DR (一句话)

**Gov-mcp / hook 的 deny 消息从 "reason 字符串" 改造为 "结构化补救指令包"（wrong_action + correct_steps + skill_ref + lesson_ref + rule_context），让每次治理拦截成为 agent 上下文内学习机会。**

---

## §1. Problem Statement (问题实证)

### 1.1 当前 deny 消息格式（无教学价值）

2026-04-13 前，所有 behavior_rules / boundary_enforcer 拦截返回格式：
```
PolicyResult(allowed=False, reason="CEO must dispatch engineering tasks via CTO, not directly to eng-kernel")
```

Agent 收到后只知道"被拦"，不知道：
- 我刚才做了什么（wrong code）
- 正确做法是什么（correct steps）
- 哪里有完整参考（skill document）
- 为什么有这条规则（历史事故）

结果：CEO 在 2026-04-13 session **连撞 4 次** `must_dispatch_via_cto` 同一 rule（每次都是尝试直接调 eng-* agent），每次 deny 后仅 revert 本次动作，下次同类场景又犯。**治理成了卡点，不是成长杠杆。**

### 1.2 根因：治理范式是"警察"不是"教练"

- 拦截后无上下文复用
- Skill document / lesson 存在但 deny 消息不引用 → agent 不知道去哪读
- Board 原则："把每个问题转成系统增量" — 当前 deny 只消耗碰撞机会，未形成复用

Board 指示："Governance 从 cop → coach。Deny = 教学设计机会。" 当前架构缺教学层，必须补全。

---

## §2. Proposal (提议)

### 2.1 核心数据结构：`Remediation` (补救指令包)

新增 `ystar/adapters/boundary_enforcer.py` 数据类：

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Remediation:
    """
    Structured remediation payload for DENY responses.
    
    Transform governance from "you can't" to "here's how you should".
    """
    wrong_action: str           # Agent 刚才做了什么（code/command 原样）
    correct_steps: list[str]    # 正确步骤序列（可执行代码/MCP 调用）
    skill_ref: str | None       # knowledge/{role}/skills/*.md 路径（完整参考）
    lesson_ref: str | None      # knowledge/{role}/lessons/*.md 或 CIEU incident_id
    rule_name: str              # Behavior rule 名称（可查 .ystar_session.json）
    rule_context: str | None    # 为什么有这条规则（1 句话背景）
```

### 2.2 PolicyResult 扩展

`ystar/session.py` 中 `PolicyResult` 加字段：

```python
@dataclass
class PolicyResult:
    allowed:    bool
    reason:     str
    who:        str
    what:       str
    violations: List[Any] = field(default_factory=list)
    remediation: Optional[Remediation] = None  # ← NEW (AMENDMENT-012)
```

### 2.3 Deny 消息生成格式（hook wrapper 统一格式化）

所有 hook / gov-mcp 返回 deny 时格式化为：

```
[Y*] DENY: {agent_id} → {attempted_action} (rule: {rule_name})

❌ You did:
  {wrong_action_code}

✅ Correct sequence:
  Step 1: {correct_step_1}
  Step 2: {correct_step_2}
  ...

📖 Skill reference: {path/to/skill.md}
📊 Why this rule exists: {rule_context or lesson_ref}
```

Example for `must_dispatch_via_cto`:
```
[Y*] DENY: ceo → Agent(agent="eng-kernel") (rule: must_dispatch_via_cto)

❌ You did:
  invoke("Agent", agent="eng-kernel", ...)

✅ Correct sequence:
  Step 1: invoke("Agent", agent="cto", task="...")
  Step 2: CTO will spawn appropriate engineer (eng-kernel/platform/governance/domains)

📖 Skill reference: knowledge/ceo/skills/ceo_delegation_chain.md
📊 Why this rule exists: CEO is strategic coordinator, not technical dispatcher. 
    CTO owns all engineering work allocation. (Ref: AMENDMENT-009 §2, AGENTS.md Article 2)
```

### 2.4 初始覆盖范围（10 条核心 rule）

立项时至少为以下 10 条 behavior_rules 写 Remediation：

1. `must_dispatch_via_cto` (CEO → eng-* blocked)
2. `write_boundary_violation` (agent write path 越权)
3. `immutable_paths` (AGENTS.md / governance/ 写拦截)
4. `ceo_deny_paths` (CEO 不能写 ystar/kernel/)
5. `pre_commit_requires_test` (git commit 前必须 pytest)
6. `source_first_fixes` (修 bug 先改 Y-star-gov/ 再 build whl)
7. `autonomous_mission_requires_article_11` (自主任务前跑第十一条)
8. `counterfactual_before_major_decision` (重大决策前反事实)
9. `root_cause_fix_required` (发现问题后系统级修复)
10. `document_requires_execution_plan` (写 doc 前先执行 plan)

每条 Remediation 必须：
- `wrong_action`: 实际被拦的 tool call 原样
- `correct_steps`: 可执行代码示例（不是抽象描述）
- `skill_ref`: 引用 `knowledge/{role}/skills/` 现有文件；若不存在 → 写草稿到 `knowledge/{role}/skills/_draft_/`
- `lesson_ref`: 引用 `knowledge/{role}/lessons/` 相关 incident
- `rule_context`: 1 句话说明规则意图

---

## §3. 验收标准（Acceptance Criteria）

实装完成需满足：

1. ✅ `ystar/session.py` 中 `PolicyResult` 有 `remediation: Optional[Remediation]` 字段
2. ✅ `ystar/adapters/boundary_enforcer.py` 定义 `Remediation` dataclass
3. ✅ 10 条核心 rule 函数（`_check_must_dispatch_via_cto` 等）全部返回带 `Remediation` 的 `PolicyResult`
4. ✅ `_hook_daemon.py` / `scripts/hook_wrapper.py` 格式化 deny 消息时读取 `result.remediation`，输出 §2.3 格式
5. ✅ CIEU 记录新增字段 `remediation_payload` (JSON blob 或单独字段)，`_record_behavior_rule_cieu` 写入
6. ✅ 测试：`tests/test_deny_as_teaching.py` 至少 15 个 test case，覆盖：
   - 撞 `must_dispatch_via_cto` → 返回结构化 remediation（含 gov_delegate / Agent(agent="cto") 代码示例）
   - 撞 `write_boundary_violation` → 返回合法路径建议 + `board_ceo_override.sh` escape hatch
   - 撞 `pre_commit_requires_test` → 返回 `pytest --tb=short -q` 步骤
   - Remediation schema 完整性验证（所有字段非空 + skill_ref 文件存在）
   - CIEU 记录包含完整 remediation JSON
7. ✅ 所有引用的 skill 文件**真实存在**（或补草稿到 `_draft_/`），不准造假路径
8. ✅ 86 existing tests 保持 PASS（不破坏现有 enforcement）
9. ✅ 实装报告 `reports/amendment_012_impl_20260413.md` 包含：
   - 10 条 rule 的 Remediation 清单
   - 新增 skill 草稿清单
   - 测试覆盖报告（15+ cases）
   - CIEU schema 改动

---

## §4. 派给 (RAPID Ownership)

- **R (Research)**: Jordan (eng-domains) — 收集 10 条 rule 的历史 lesson / skill / 正确步骤
- **A (Author)**: Jordan — 写 Remediation 数据 + skill 草稿 + 测试
- **P (Perform)**: Jordan — 代码实装 + hook wrapper 集成
- **I (Inform)**: CTO (Ethan) / Maya (eng-governance，CIEU schema 改动需 review)
- **D (Decide)**: Board

---

## §5. 风险与缓解

| 风险 | 检测 | 缓解 |
|---|---|---|
| Skill 引用路径不存在 → agent 读 404 | 测试扫 skill_ref 字段 verify file exists | Jordan 补全 `_draft_/` 草稿（Hermes 4 段格式），标 `[DRAFT v0.1]` |
| Remediation 长度爆炸（单次 deny 返回 2KB 文本） | 测试 assert `len(formatted_message) < 800` | `correct_steps` 限 ≤ 5 步；`rule_context` ≤ 100 字；skill 详细内容放文件 |
| 与 Ryan dual-mode 实装冲突（他改 mode 切换） | Jordan 只改 `PolicyResult` + `Remediation`；Ryan 改 `_get_current_mode` | 两人改的文件不重叠（Jordan boundary_enforcer rule 函数 / Ryan mode manager） |
| CIEU schema 改动需 Maya review | Jordan 改完发 PR 前 ping Maya | Maya 24h 内 review CIEU 字段 |
| Agent 学习过度依赖 deny 消息，不主动读 skill | 监控 skill 文件 read 频率 vs deny 触发频率 | 如 `deny_count / skill_read_count > 5` → Board escalate（治理依赖症） |

---

## §6. Board 批示

- [ ] 通过 / 通过需修订 / 驳回
- [ ] 优先级：P0（立即启动）/ P1（24h 内）/ P2

Board D 后，Jordan 自主推进（eng-domains scope 内），完成或卡住 ping CEO。

---

## §7. 与其他 Amendment 关系

- **AMENDMENT-009**: 引入 article11 pre-response hook → AMENDMENT-012 为 article11 拦截补 remediation
- **AMENDMENT-010**: 11-category boot + behavior_rules 代码实装 → AMENDMENT-012 扩展 behavior_rules 返回结构
- **AMENDMENT-011** (Ryan): Dual-mode enforcement → 本 amendment 为两种 mode 的 deny 统一加教学层

三者独立可并行（Jordan 改 Remediation / Ryan 改 mode / Maya 观察 CIEU 记录）。

---

## Appendix A: 初始 Remediation 数据示例（10 条之 3）

### A.1 `must_dispatch_via_cto`

```python
Remediation(
    wrong_action='invoke("Agent", agent="eng-kernel", task="...")',
    correct_steps=[
        'invoke("Agent", agent="cto", task="...")',
        'CTO will delegate to appropriate engineer (eng-kernel/platform/governance/domains)',
        '(Alternative: use mcp__gov-mcp__gov_delegate for cross-role task assignment)'
    ],
    skill_ref="knowledge/ceo/skills/ceo_delegation_chain.md",
    lesson_ref="knowledge/ceo/lessons/ceo_越权派工_2026_04_13.md",
    rule_name="must_dispatch_via_cto",
    rule_context="CEO is strategic coordinator, not technical dispatcher. CTO owns engineering work allocation."
)
```

### A.2 `pre_commit_requires_test`

```python
Remediation(
    wrong_action='bash("git commit -m \'...\'")',
    correct_steps=[
        'bash("python -m pytest --tb=short -q")',
        'Verify all tests pass (exit code 0)',
        'bash("git add <files>") # only add specific files',
        'bash("git commit -m \'...\\n\\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\'")',
    ],
    skill_ref="knowledge/eng-platform/skills/pre_commit_workflow.md",
    lesson_ref="CIEU incident_id=test_skip_regression_2026_04_10",
    rule_name="pre_commit_requires_test",
    rule_context="Prevent regressions — all code changes must pass existing tests before commit."
)
```

### A.3 `write_boundary_violation`

```python
Remediation(
    wrong_action='Write(file_path="ystar/kernel/engine.py", ...)',
    correct_steps=[
        '# eng-domains write scope: ystar/domains/, ystar/patterns/, ystar/templates/, ystar/products/',
        '# For kernel changes: delegate to eng-kernel (Leo Chen)',
        'invoke("Agent", agent="cto", task="kernel engine.py needs X change")',
        '# Or escalate to Board if requires immutable path override',
    ],
    skill_ref="knowledge/eng-domains/skills/eng_domains_scope.md",
    lesson_ref="knowledge/eng-domains/lessons/scope_violation_2026_04_12.md",
    rule_name="write_boundary_violation",
    rule_context="Each engineer owns specific ystar/ subdirectories. Cross-boundary edits go via CTO delegation."
)
```

(剩余 7 条 Jordan 实装时补全)

---

**END OF CHARTER**
