---
name: Subagent 注册表 boot-only
description: Claude Code 在 session boot 时读 .claude/agents/，mid-session 改文件不会让新 subagent 出现；要么重启要么顶岗
type: feedback
originSessionId: b8aed99a-55f2-4073-a223-d41630cec4f4
---
`.claude/agents/{name}.md` 改了 (新增/修复 frontmatter)，本 session 内 subagent 注册表**不会重读**。新 subagent 只在下次 session boot 时才注册到可调用列表。这是 Claude Code 平台行为，无法在 hook 层绕过。

**Why:** 2026-04-13 session：Sofia-CMO 文件因 BOM 字节 frontmatter 解析失败，CEO 修了 BOM (`aa2ecd5`) 但 Sofia-CMO 在本 session 仍不在可派列表，需要 general-purpose 顶岗。Board 困惑"为什么还顶岗"。根因 = 平台限制不是疏忽。

**How to apply:**
- 修 `.claude/agents/*.md` 后**立刻告知 Board**：本 session 仍顶岗，下次 session boot 才真注册
- 不要假装新 agent 已可用
- 如果 mission 紧急且必须真 agent，告知 Board 唯一解 = 重启 (用 `bash scripts/aiden_continuity_guardian.sh ceo`)
- 顶岗 general-purpose 需在 prompt 内显式说 "你扮演 X，subagent 没注册"，让顶岗 agent 知道自己是临时
- **预防**：所有新写 agent file 必跑 BOM 检查 (`xxd -l 3 file.md | head -c 8 | grep -c efbbbf` 应 =0)
- **codify 进 wire_integrity_check.py**：扫所有 .claude/agents/*.md frontmatter 是否能 yaml.safe_load，含 BOM/语法错的报 `WIRE_AGENT_REGISTRATION_BROKEN`

**永久解（待派工程）**: Claude Code 应该提供 `claude --reload-agents` 或 SIGHUP 信号热重载 subagent registry。提 issue 给 Anthropic Claude Code team。
