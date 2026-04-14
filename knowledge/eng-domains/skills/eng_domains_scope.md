# Skill: eng-domains 写作域边界

**类型**: Hermes 可加载 skill（4 段格式）
**适用 agent**: eng-domains (Jordan Lee)
**立约**: 2026-04-13 (AMENDMENT-012 remediation)
**依据**: `.ystar_session.json` restricted_write_paths — 每个 engineer 只能改自己负责的 ystar/ 子目录

---

## 1. Trigger (适用场景)

下列任一条件触发加载本 skill：
- Jordan (eng-domains) 准备 Write / Edit Y-star-gov/ystar/ 任何文件
- Hook DENY `write_boundary_violation` 并提示 "not in your scope"
- CTO 分派任务但不确定是否在 Jordan 职责范围
- 需要跨域协作（Jordan 需要 kernel 改动配合）

## 2. Procedure (程序——逐步执行)

### Step 1: 检查文件路径是否在 Jordan 写作域

**Jordan (eng-domains) 可写路径**:
```
Y-star-gov/ystar/domains/           # Domain packs (openclaw / ystar_dev / omission_domain_packs.py)
Y-star-gov/ystar/patterns/          # Policy patterns
Y-star-gov/ystar/pretrain/          # Pretrain data
Y-star-gov/ystar/products/          # Product-specific templates
Y-star-gov/ystar/templates/         # Policy templates
Y-star-gov/ystar/template.py        # Template engine
Y-star-gov/tests/test_openclaw.py   # OpenClaw adapter 测试
Y-star-gov/tests/test_openclaw_extended.py
Y-star-gov/tests/test_v041_features.py
ystar-company/ystar/domains/        # (if exists, 公司侧 domain 文档)
ystar-company/knowledge/eng-domains/ # Jordan 知识库
ystar-company/reports/proposals/    # (RFC / proposal 草稿，全员可写)
```

**Jordan 禁止写路径**:
```
Y-star-gov/ystar/kernel/            # → eng-kernel (Leo) 负责
Y-star-gov/ystar/governance/        # → eng-governance (Maya) 负责
Y-star-gov/ystar/adapters/          # → eng-platform (Ryan) 负责
Y-star-gov/ystar/_hook_*.py         # → eng-platform (Ryan) 负责
Y-star-gov/ystar/_cli.py            # → eng-platform (Ryan) 负责
Y-star-gov/ystar/session.py         # → eng-kernel (Leo) or CTO
ystar-company/ystar/kernel/         # (if exists, 禁止)
ystar-company/ystar/governance/     # (if exists, 禁止)
```

### Step 2: 如果在写作域内 → 直接执行

```python
Edit(file_path="/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/domains/openclaw/policy_constraints.py",
     old_string="...",
     new_string="...")
```

### Step 3: 如果不在写作域 → Delegate to CTO

**方法 A: 调 CTO agent**
```python
invoke("Agent", 
       agent="cto",
       task="""
       需要修改 ystar/kernel/engine.py（Leo 负责）
       原因：[说明为什么需要这个改动]
       改动内容：[具体代码]
       验收：[测试覆盖]
       """)
```

**方法 B: 写跨域协作任务卡**
```bash
Write(file_path=".claude/tasks/eng-kernel-engine-extension.md",
      content="""
      # Task: Kernel Engine Extension for Domain Pack Feature
      Priority: P1
      Assigned: eng-kernel (Leo Chen)
      Requested by: eng-domains (Jordan Lee)
      Created: 2026-04-13
      
      ## Context
      Jordan 在开发新 domain pack 时需要 engine.py 支持新约束类型...
      
      ## Required Change
      ystar/kernel/engine.py: add constraint_type="domain_specific"
      
      ## Acceptance
      - tests/test_kernel.py 覆盖新 constraint_type
      - domain pack 可调用新接口
      """)
```

### Step 4: Escalate to Board (如需 immutable override)

某些路径（AGENTS.md / governance/BOARD_CHARTER_AMENDMENTS.md）连 CTO 也不能改，需 Board shell override:

```bash
# Jordan 不执行这个，报告给 CEO → CEO 报告 Board
echo "需要 Board shell 解锁 immutable path: <path>"
```

---

## 3. Pitfalls (容易踩的坑)

### 坑 A: "只改一行" 觉得不用走 delegation
**症状**: 看到 `ystar/adapters/hook.py` 只改 1 行 → 直接 Edit
**规避**: 任何不在写作域的文件，哪怕 1 字符都要走 CTO delegation

### 坑 B: CTO 口头说"你改吧" → 直接改 kernel/
**症状**: CTO 在对话里说"Jordan 你改 engine.py" → Jordan 直接 Edit
**规避**: 即使 CTO 批准，仍需 CTO 正式 delegate（调 eng-kernel agent 或写任务卡）留 CIEU 记录

### 坑 C: 测试文件混淆（test_behavior_rules.py 不在 Jordan scope）
**症状**: 想改 `tests/test_behavior_rules.py` → hook DENY
**规避**: Jordan 只能改 `test_openclaw*.py` / `test_v041_features.py`。其他测试归对应 engineer

### 坑 D: ystar-company/ 和 Y-star-gov/ 路径混淆
**症状**: 想改 `ystar-company/ystar/kernel/` （不存在这个路径）
**规避**: Y*gov 源码在 `Y-star-gov/ystar/`（Mac workspace sibling）。`ystar-company/` 是公司运营 repo

### 坑 E: Hook DENY 后钻牛角尖研究 boundary_enforcer 源码
**症状**: 撞 `write_boundary_violation` → 花 20min 读 `boundary_enforcer.py` 试图绕过
**规避**: Hook DENY = 停下 + 读本 skill + 走正确路径（delegation）。不要 debug governance 层（那是 Maya 职责）

---

## 4. Verification Steps (验证执行成功)

- [ ] 所有 Write/Edit 路径在 Jordan 写作域内
- [ ] 跨域需求通过 CTO delegation (Agent call / task 卡 / RAPID)
- [ ] CIEU 无 `write_boundary_violation` DENY 记录
- [ ] Immutable path 需求 escalate to Board (不自己硬闯)
- [ ] 测试文件只改 `test_openclaw*.py` / `test_v041_features.py`

---

## 5. 关联 skill / doc

- `.ystar_session.json` → `restricted_write_paths` (每个 path pattern 有 allowed_roles 列表)
- `AGENTS.md` — 4 个工程师职责划分
- `knowledge/cto/role_definition/task_type_map.md` (CTO 如何分派工程师)
- `knowledge/eng-domains/lessons/scope_violation_2026_04_12.md` (历史事故：Jordan 误改 governance/)

---

## 6. 版本
v0.1 — 2026-04-13 Jordan (eng-domains) 为 AMENDMENT-012 remediation 编写（自己给自己写 scope 文档）
