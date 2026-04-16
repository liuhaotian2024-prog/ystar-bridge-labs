---
name: eng-domains 误改 governance/ 路径触发 write_boundary_violation
type: lesson / incident
created: 2026-04-12
severity: medium
trigger_incident: Jordan (eng-domains) 在实装 omission_engine 时尝试修改 ystar/governance/omission_engine.py，被 hook DENY
lesson_id: 25a41f85-99dd-4c0c-9f7a-498d3c02d210
---

# 规则
每个 engineer 只能修改自己负责的 `ystar/` 子目录。跨域修改必须走 CTO delegation。

# Why
2026-04-12 Jordan (eng-domains) 实装 OmissionEngine 集成时，发现需要修改 `ystar/governance/omission_engine.py` 添加新 API。Jordan 尝试直接 Edit 该文件 → hook DENY `write_boundary_violation`。

错误推理链：
1. "OmissionEngine 是我负责集成的" ✅ (集成层确实 Jordan 负责)
2. "所以 omission_engine.py 我可以改" ❌ (文件路径在 governance/，归 Maya)
3. 直接 Edit → DENY

正确路径：
1. Jordan 发现需要 `governance/omission_engine.py` 新增 API
2. 写需求到 `.claude/tasks/eng-governance-omission-api.md` 或调 CTO
3. CTO 派 Maya (eng-governance) 实装
4. Maya 改完后 Jordan 调用新 API（Jordan 只改 `domains/` 里的调用代码）

Board 点评："文件路径归属 > 功能逻辑归属。omission 逻辑归你，但 governance/ 路径归 Maya。"

# 工程师写作域划分

| Engineer | 可写路径 | 禁止路径 |
|---|---|---|
| **Leo (eng-kernel)** | `ystar/kernel/` | 其他所有 ystar/ 子目录 |
| **Ryan (eng-platform)** | `ystar/adapters/`, `ystar/_*.py`, `ystar/cli/` | `ystar/kernel/`, `ystar/governance/`, `ystar/domains/` |
| **Maya (eng-governance)** | `ystar/governance/` | `ystar/kernel/`, `ystar/adapters/`, `ystar/domains/` |
| **Jordan (eng-domains)** | `ystar/domains/`, `ystar/patterns/`, `ystar/templates/`, `ystar/products/` | `ystar/kernel/`, `ystar/governance/`, `ystar/adapters/` |

所有人共享可写：
- `ystar-company/reports/proposals/` (RFC 草稿)
- `ystar-company/knowledge/{own_role}/` (各自知识库)
- `Y-star-gov/tests/test_{own_scope}.py` (各自测试文件)

# How to apply
每次 Write/Edit Y-star-gov/ystar/ 任何文件前：
1. 检查文件路径是否在自己写作域
2. 如果不在 → 停下
3. 写需求到 `.claude/tasks/{responsible_engineer}-xxx.md` 或调 CTO
4. 不要绕过 delegation 直接改

# 系统改进
- AMENDMENT-012 为 `write_boundary_violation` 补 remediation（包含 4 个工程师写作域列表）
- `knowledge/eng-domains/skills/eng_domains_scope.md` 立项（Jordan 自己写自己的 scope 文档）
- Hook 实装后 deny 消息包含"应该 delegate 给谁"

# 关联
- `.ystar_session.json` → `restricted_write_paths` (每个 path pattern 有 allowed_roles)
- `AGENTS.md` — 4 个工程师职责划分
- `knowledge/cto/role_definition/task_type_map.md`
- `knowledge/eng-domains/skills/eng_domains_scope.md`

# 验证
下次 Jordan 需要跨域改动时：
- [ ] 检查文件路径归属
- [ ] 跨域需求写 task 卡或调 CTO
- [ ] CIEU 无 `write_boundary_violation` DENY
- [ ] 只改 `ystar/domains|patterns|templates|products/` 路径
