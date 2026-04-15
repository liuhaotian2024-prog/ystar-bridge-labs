# Tool-Use Recovery via OpenClaw Subagent JSONL (2026-04-14)

## 发现 (Board 2026-04-14 hint: 去 OpenClaw 看是否能找到丢失的)

OpenClaw 每个 sub-agent 的 JSONL transcript 完整保存 tool_use input, 含 Write/Edit/MultiEdit 的 file_path + content + old_string + new_string.

路径: `/Users/haotianliu/.claude/projects/-Users-haotianliu--openclaw-workspace-ystar-company/<session-uuid>/subagents/agent-<agentId>.jsonl`

关键字段: `message.content[].type == "tool_use"` + `name == Write|Edit|MultiEdit` + `input.{file_path, content, old_string, new_string}`

## Recovery 优先顺序

1. OpenClaw subagent JSONL (完整, 无截断)
2. CIEU DB `cieu_events.params_json` (8KB 截断, 按 file_path grep)
3. Main session JSONL (同路径, 无 agentId subdir)
4. git reflog + mirror/backup (如 `~/.openclaw/mirror/ystar-company-backup`)

## 2026-04-14 实战
- Ryan a53b6c8e: 救 `content/video_registry.yml` + `reports/video_storage_migration_20260414.md`
- Maya a8fbc8ac + a21bc2860: 救 `scripts/hook_wrapper.py` fail-closed Edit 序列, 保存为 `reports/recovery/maya_hook_wrapper_edits_20260414.json`

## CEO 自省 lesson

之前声称"Ryan 2 文件不可逆丢失"= prose-only defeatism, 没查 OpenClaw 就 claim unrecoverable. Board 一句"去 OpenClaw 看看"全救回. **遇 '丢失' 必查 3 层 (subagent JSONL + CIEU DB + git reflog) 穷尽后才 claim unrecoverable**.
