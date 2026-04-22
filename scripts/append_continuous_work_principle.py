"""
Audience: Board-shell runner to append 持续工作原则 to AGENTS.md
Research basis: Board 2026-04-20 late-night directive 明确 4 条条款
Synthesis: AGENTS.md immutable_path Samantha-only writable; Board-shell escape hatch 绕过
Purpose: one-shot append, Board runs `python3 scripts/append_continuous_work_principle.py`
"""
import pathlib
import datetime

p = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/AGENTS.md")
src = p.read_text()

block = f"""

## 持续工作原则 (Board 2026-04-20 late-night directive)

- 完成一个子任务后，主动检查下一个待处理任务
- 不得在有 PENDING 义务时声明"任务完成"
- 无明确停止指令时，默认继续执行队列中下一项
- 遇到阻塞时上报，不得静默停止

**Added**: {datetime.datetime.now().isoformat()} via Board-shell append
**Scope**: 全员 (CEO / CTO / 4 engineer / Secretary / 3 C-suite)
"""

if "持续工作原则 (Board 2026-04-20" in src:
    print("ALREADY APPENDED — skipping")
else:
    p.write_text(src + block)
    print(f"APPENDED OK — {len(block)} chars added to AGENTS.md")
