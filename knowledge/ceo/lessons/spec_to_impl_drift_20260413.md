---
name: Spec→Impl Drift（A018 Phase 1 4 工程师 4 schema）
type: lesson
created: 2026-04-13
severity: medium
trigger: A018 4 工程师并列写 7 YAML，schema 4 个版本互不兼容
---

# 现场

A018 §2 6-pager 定义了 entry schema：
`{id, who, what, when_trigger, when_complete, prerequisites, observable_signal}`

4 工程师并列实施时：
- Ethan 严格遵循（自己写的 spec）
- Maya inter_role_sop 改用 `{flow_id, trigger_condition, required_roles, ...}` (无 who/what)
- Maya rapid_matrix 改用 `{decision_type_id, default_R/A/P/I/D}` (RAPID 专门 schema)
- Ryan role_mandate 加 `task_type, core_verbs` 字段

**结果**：5/7 文件 validator fail。不是疏忽——每人都按"对应 corpus 的合理表达"展开，但偏离 §2 spec。

# 根因（不是 4 个工程师的错）

**Spec→Impl drift 的元根因 = 自然语言 spec 不是可执行 contract**。

A018 §2 用 markdown 表格写 schema，没有：
- machine-readable JSON Schema 文件
- 单元测试样本
- 强制 sub-agent boot 时 load schema 进 prompt

每个 sub-agent 重新解读 spec → 重新展开 → 必然漂移。**这是 AMENDMENT-016 mirror sync 在另一个域的同样问题：spec 是 source，impl 是 mirror，没传播**。

# 教训

1. **任何 multi-agent 并列冲刺前**，先 ship 一个 machine-readable spec（JSON Schema / Python pydantic / proto），不只是 markdown 表格
2. **派工时把 schema 文件路径直接写进 prompt**，让 sub-agent boot 时 import + 用 schema 校验自己输出
3. **schema 必须包含 "core fields + per-domain extensions"**，允许 domain-specific 字段但保证 lookup key 一致

# 处方（应用到 A018 v2）

- spec 变 `governance/whitelist/schema.json` (JSON Schema with `oneOf` for per-corpus variants)
- core fields: `{id, who, what, observable}` 强制
- per-corpus extension: `inter_role_sop` 加 `decision_level, authority`; `rapid_matrix` 加 `R/A/P/I/D`; etc.
- validator 加载 schema.json 自动判 (variant) → 不需 hardcode

# 对其他 amendment 的提示

A005 (RAPID), A013 (proactive activation), A015 (LRS) 都涉及多 sub-agent 协作 schema。**全部应该有 schema.json sibling 而非 markdown only**。
