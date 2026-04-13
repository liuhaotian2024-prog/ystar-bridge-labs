# EXP-2 Part A — 现有 brief 格式: AMENDMENT-004 残留清理

**日期**: 2026-04-12
**实验**: EXP-2 任务派活格式对比（A 组：现有 brief 格式）
**派活对象**: 未命名 subagent（测试用，不绑定具体 agent）

---

## 任务

清理 AMENDMENT-004 落地后 Secretary 未覆盖的 Windows 路径与 "MAC mini" 残留引用。

## 背景

Secretary Samantha Lin 于 2026-04-12 commit `e6ca1df` 执行 AMENDMENT-004，但以下文件未清理干净：

1. `memory/session_handoff.md:3` — 含 "MAC mini" 标签需改为 "Single-Mac OpenClaw workspace"
2. `.claude/agents/cto.md:109` — Source-First Fixes 段含 Windows 路径 `C:\Users\liuha\OneDrive\桌面\Y-star-gov\`
3. `.claude/agents/eng-governance.md:52` — Working directory 字段含 `C:\Users\liuha\OneDrive\桌面\Y-star-gov\`
4. `sales/cso_patent_report_001.md:4` — File Location 字段含 Windows 路径
5. `sales/cso_patent_report_001.md:212` — knowledge file 引用含 Windows 路径
6. `sales/cso_strategic_intelligence_summary.md:266` — knowledge file 引用含 Windows 路径

## 要求

- 全部替换为对应 Mac OpenClaw 路径：`/Users/haotianliu/.openclaw/workspace/<repo>/...`
- 金金相关的 "Mac mini" 引用（如 `.claude/agents/cmo.md:122`、`.claude/agents/ceo.md:250`）**不改**——那些是金金基础设施语义，不属 AMENDMENT-004 scope
- 每处改动前 Read 确认当前内容，不盲改
- 完成后 grep 验证无残留 `C:\Users\liuha`（archive/ 和 BOARD_CHARTER 除外）

## 权限

本任务需要切 `.ystar_active_agent=secretary`（因为涉及 `.claude/agents/*.md` 和 `memory/session_handoff.md`，都不在 ceo write_paths 内）。

切法：
```
echo secretary > /Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_active_agent
```

完工切回：
```
echo ceo > /Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_active_agent
```

## Commit

```
cd /Users/haotianliu/.openclaw/workspace/ystar-company
git add -A
git commit -m "AMENDMENT-004 follow-up: clean residual Windows paths in agent/memory/sales files"
```

## 完成定义

- [ ] 6 处 Windows 路径全部替换
- [ ] grep 验证无残留
- [ ] git commit
- [ ] 切回 active_agent=ceo
- [ ] 给 CEO 200 词内完成报告

## 注意

- 不绕过 hook，遇 boundary violation 停下报 CEO
- 不 --no-verify
