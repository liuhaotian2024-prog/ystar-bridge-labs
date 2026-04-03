## Task: P5 TIER2 Remaining Fixes
Engineer: CTO (assign to eng-platform and eng-governance)
Priority: P1
Created: 2026-04-02

### FIX-6: Bash命令路径检查
Assign to: eng-platform
- 写 _extract_write_paths_from_bash(command) 函数
- 提取 >, >>, tee, cp, mv 的目标路径
- 对提取路径执行 _check_write_boundary + _check_immutable_paths
- 写测试覆盖所有case

### FIX-7: 委托链加载
Assign to: eng-governance
- 在 .ystar_session.json 中增加 delegation_chain 字段
- Board→CEO→CTO/CMO/CSO/CFO 层级
- _check_hook_full 中加载并验证单调性

### Acceptance Criteria
- [ ] 406+ tests pass
- [ ] Bash重定向到AGENTS.md被拦截
- [ ] 委托链验证生效
- [ ] commit+push
