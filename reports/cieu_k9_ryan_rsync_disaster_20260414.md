# K9 Causal Chain — Ryan-Platform rsync --delete 灾难 (2026-04-14)
Severity P0 系统级. Author CEO Aiden. Trigger Board 2026-04-14 "K9 audit 追溯工程师灾难根因".
## K9 因果链: Ryan 写 rsync_sync(Y_GOV, Y_COMPANY, --delete) 反向同步, 删 2640 files, session.json 1339→81. 2 次派单同事故.
## 系统级根因 (Y*gov/gov-mcp bug)
1. engine.py contract.deny 只 path-level 字面量, 无 destructive command 层校验
2. sub-agent 写破坏命令无 dry-run 强制阶段
3. 镜像方向 schema 缺 (canonical vs mirror)
4. session.json 无 JSON schema 守护
5. hook 无 WIP auto-commit 安全网
## 防御 Patch (待 Maya/Leo 落)
Patch 1 engine.py destructive cmd pre-check (rsync --delete / rm -rf / git reset --hard 必 dry-run + Board approval)
Patch 2 session.json schema (missing immutable_paths/override_roles/contract BLOCK)
Patch 3 mirror_contract 方向 JSON
Patch 4 hook WIP auto-commit
## Ryan agent-level
.claude/agents/eng-platform.md 缺 destructive-cmd 指引; task card 需方向强标.
