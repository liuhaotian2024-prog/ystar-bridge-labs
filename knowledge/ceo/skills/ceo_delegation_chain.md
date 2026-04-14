# Skill: CEO Delegation Chain (Engineering Tasks)

**类型**: Hermes 可加载 skill（4 段格式）
**适用 agent**: CEO (Aiden / 承远)
**立约**: 2026-04-13 (AMENDMENT-012 remediation)
**依据**: `must_dispatch_via_cto` behavior rule — CEO 不直接派工程师，必经 CTO

---

## 1. Trigger (适用场景)

下列任一条件触发加载本 skill：
- CEO 需要工程任务（代码/测试/架构/治理）完成
- 收到 Board 工程需求需要分派
- 尝试直接调 `eng-kernel` / `eng-platform` / `eng-governance` / `eng-domains` 被 hook DENY
- 需要修复 Y*gov 源码 bug

## 2. Procedure (程序——逐步执行)

### Step 1: 判断是否工程任务

工程任务定义：
- 修改 `Y-star-gov/ystar/` 任何代码
- 跑测试 `pytest`
- Build whl package
- Git commit/push 到 Y-star-gov repo
- 架构设计 / 算法实现
- 治理规则代码实装（behavior_rules / hook / gov-mcp tools）

非工程任务（CEO 可直接处理或派其他 C-suite）：
- 写 `reports/` / `content/` / `marketing/` / `sales/`
- 战略决策、OKR、priority_brief
- 对外发布、HN post、arXiv submission
- 财务模型、定价

### Step 2: 走 CTO delegation（正确路径）

**方法 A：Agent 工具调 CTO**
```python
invoke("Agent", 
       agent="cto",
       task="""
       [工程任务描述]
       - 期望产出：...
       - 验收标准：...
       - 优先级：P0/P1/P2
       - 依赖：...
       """)
```

**方法 B：gov_delegate MCP tool（未来实装）**
```python
invoke("mcp__gov-mcp__gov_delegate",
       from_role="ceo",
       to_role="cto",
       task_id="TASK-YYYYMMDD-NNN",
       brief_path="reports/dispatches/cto_task_XXX.md")
```

**方法 C：写任务卡到 `.claude/tasks/`（异步队列）**
```bash
Write(file_path=".claude/tasks/cto-fix-xxx.md",
      content="""
      # Task: [简短标题]
      Priority: P0/P1/P2
      Assigned: CTO (Ethan Wright)
      Created: 2026-04-13
      
      ## Context
      ...
      
      ## Deliverable
      ...
      
      ## Acceptance
      ...
      """)
```

### Step 3: CTO 再分派给工程师（透明给 CEO）

CTO 收到后根据任务类型分派：
- **Kernel 相关** (engine.py / dimensions.py / constraints.py) → eng-kernel (Leo Chen)
- **Platform 相关** (hook / _cli.py / scripts/) → eng-platform (Ryan Park)
- **Governance 相关** (governance/*.py / omission / precheck / health) → eng-governance (Maya Patel)
- **Domains 相关** (domains/ / patterns/ / templates/ / products/) → eng-domains (Jordan Lee)

CEO 不需要记这个映射——CTO 负责。

### Step 4: 验证完成

CTO 或工程师完成后：
- 更新 `knowledge/cto/active_task.json` 状态 = completed
- 回复 CEO 或写 `reports/autonomous/eng_YYYYMMDD.md`
- CEO verify: 读产出 / 跑测试 / check GitHub commit

---

## 3. Pitfalls (容易踩的坑)

### 坑 A: 觉得"小改一行代码"可以直接派工程师
**症状**: 尝试 `invoke("Agent", agent="eng-kernel", task="改 engine.py 第 123 行")`
**规避**: 任何代码改都经 CTO——CTO 判断是否需 code review / 影响其他模块

### 坑 B: Board 说"Jordan 做" CEO 直接调 Jordan
**症状**: Board 指名 Jordan → CEO `invoke("Agent", agent="eng-domains", ...)`
**规避**: Board 指名是建议，CEO 仍需走 CTO delegation（CTO 可直接转 Jordan 但经过 delegation chain 留 CIEU 记录）

### 坑 C: CTO 不在线，CEO 等不及直接派工程师
**症状**: CTO sub-agent 超时 / 报错 → CEO 绕过直接派
**规避**: 
- 写任务卡到 `.claude/tasks/cto-xxx.md`（异步队列）
- 或 escalate to Board："CTO delegation failed, need Board shell override"
- **绝不**直接调工程师（hook 会 DENY）

### 坑 D: 自己写代码（CEO 越权写 ystar/）
**症状**: CEO 直接 `Write(file_path="Y-star-gov/ystar/kernel/engine.py", ...)`
**规避**: CEO 写作域 = `ystar-company/` 且不含 `ystar/kernel|governance|adapters`。任何 Y*gov 源码修改必经 CTO

---

## 4. Verification Steps (验证执行成功)

- [ ] 工程任务通过 CTO delegation（Agent / gov_delegate / task 卡）
- [ ] CIEU 有 `DELEGATION` 事件记录（ceo → cto）
- [ ] 未尝试直接调 `eng-*` agent (hook 无 DENY 记录)
- [ ] 任务完成后 `knowledge/cto/active_task.json` 状态更新
- [ ] CEO 未修改 `Y-star-gov/ystar/` 任何文件

---

## 5. 关联 skill / doc

- `knowledge/ceo/lessons/ceo_越权派工_2026_04_13.md` (本 session 4 次撞 must_dispatch_via_cto)
- `.ystar_session.json` → `agent_behavior_rules.ceo.must_dispatch_via_cto: true`
- `AGENTS.md` Article 2: CEO 职责不含直接技术执行
- `knowledge/cto/role_definition/task_type_map.md` (CTO 如何分派 4 个工程师)

---

## 6. 版本
v0.1 — 2026-04-13 Jordan (eng-domains) 为 AMENDMENT-012 remediation 编写
