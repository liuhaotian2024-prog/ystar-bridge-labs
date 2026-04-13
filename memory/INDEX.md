# Memory Directory Index
# Y* Bridge Labs · Memory Files Catalog
# 创建日期：2026-04-09 · GOV-005 Part 5

---

## 用途

`memory/` 目录存放跨 session 持久的运营状态文件——session handoff、Board 当前关注点、未完成任务清单等。**所有 session 启动协议都会读取这些文件以恢复上下文**，因此每个文件都必须有明确的用途说明和维护责任人。

**任何新增 memory 文件必须同步更新本索引。**

---

## 当前 memory 文件

| 文件 | 用途 | 维护责任人 | 更新频率 | 受 Y\*gov restricted_write_paths 保护 |
|---|---|---|---|---|
| `memory_sync/` | OpenClaw → Claude Code 记忆同步缓存 | CEO (`ceo`) | 每次 session 结束 + cron 每15分钟自动同步 | ✅ 是（`session_handoff.md` 同步目标） |
| `memory/continuation.md` | 下一个 session 的执行上下文（含活跃任务、阻塞点、团队状态） | CEO (`ceo`) | 每次 session 结束 | ✅ 是（`ceo` 写入） |

---

## 维护规则

1. **新增文件必须更新本索引**——文件名 + 用途 + 维护人 + 更新频率,缺一不可。
2. **删除文件必须征得 Board 批准**——`memory/` 是治理基础设施,不是临时文件夹。
3. **写入权限受 `.ystar_session.json` 的 `restricted_write_paths` 保护**——例如 `session_handoff.md` 只允许 `ceo` 写。其它岗位需要写 memory 时,必须先经 CEO 批准并更新 restricted_write_paths(Level 2 决策)。
4. **本索引文件本身**(`memory/INDEX.md`)**由 Secretary 维护**(DNA 蒸馏权限内,Level 1 自决)。

---

## 来源

Board GOV-005 Part 5 directive (2026-04-09)。Secretary 在 GOV-005 Part 5 易部分执行中创建,作为 memory 目录的导航索引。
