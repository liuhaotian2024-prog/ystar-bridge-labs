# Next Session Hand-off (2026-04-14, 重启前写)

## Boot 后读这 5 个 commits 从此处继续

```
12c13839 fix(contract): deny rsync --delete + git reset --hard [L4 SHIPPED take2]
2ae0373a feat(handoff): next session handoff [L1 SPEC]
4da6a749 feat(recovery): final 2 artifacts [L3 SPEC]
52883e7b feat(recovery): complete CEO 8-artifact set [L3 SPEC]
f24b04a7 feat(recovery): CEO 4 artifacts [L3 SPEC]
```

## Board 2026-04-14 已定位的精确根因 (下 session 必读)

**Y\*gov 两套危险命令黑名单没打通, 形成 path B 漏洞**:

```
路径A: agent 用 gov_exec 执行命令
  → router.py._WRITE_PATTERNS 检查 rsync → BLOCK ✅

路径B: agent 直接 Bash tool 执行命令  (Ryan 走的就是这条)
  → hook_client_labs.sh → check_hook() 
  → 检查 contract.deny_commands (主 + delegation_chain)
  → "rsync" 不在 deny_commands 里 → ALLOW ❌
```

**Board 诊断清单**:
- `router.py` 有 `_WRITE_PATTERNS` 黑名单, 含 `re.compile(r"\brsync\b")`
- `contract.deny_commands` 主 + 每个 delegation_chain (CEO/CTO/eng-kernel) 全没 rsync
- 两套互相不认识, 没有桥

## 已完成 (Immediate Fix)

commit `12c13839`: `.ystar_session.json` 主 `contract.deny_commands` 加 6 条:
```json
"rsync --delete", "rsync -r --delete", "rsync -a --delete",
"rsync -avz --delete", "rsync -aq --delete", "git reset --hard"
```
**session.json 从 1339 → 1345 行 (完整保留 immutable_paths/override_roles/intent_guard)**

## 待做 (Root Fix, 下 session Ethan-CTO 窄定义 Y\*)

**Task**: 让 `hook_client_labs.sh` 或 `check_hook` 把 `router.py._WRITE_PATTERNS` 作为**补充**黑名单, 不依赖 contract.deny_commands 是否手动写. 两套路径共用一份危险命令知识.

**Ethan Y\* 精确定义** (Board 原话):
> "两个系统之间有一条没有接上的桥"

**U 候选** (Ethan 自选最小 blast):
1. `hook_client_labs.sh` 在 daemon socket call 前 import + 跑 `router._WRITE_PATTERNS` 匹配 incoming command
2. `check_hook()` Python 侧, 在 deny_commands 检查之后再跑一遍 `_WRITE_PATTERNS` 兜底
3. 把 `_WRITE_PATTERNS` 序列化成 JSON, 启动时合并进 contract.deny_commands

**Rt+1 归零判据** (多轮测试):
- fresh session 跑 `rsync -avz --delete src/ dst/` via Bash tool → BLOCK
- 跑 `rsync -avn --dry-run src/ dst/` → ALLOW (dry-run 合法)
- 跑 `git reset --hard HEAD~1` via Bash tool → BLOCK  
- 跑 `git reset --soft HEAD~1` → ALLOW
- 3 独立 session 复现一致

**Ethan 派单硬约束**:
- 顶部 CIEU 5-tuple 必写
- 每 claim 附 tool_result block (参考 reports/cieu_first_battle_rt1_miss_20260414.md 教训)
- Ethan 有 scripts/ + Y-star-gov/ystar/ 写权, 但 session.json 半 immutable 避免再覆盖
- CEO 本线必 grep 实测: `grep -c rsync .ystar_session.json` + hook fire 实测
- 不允许 Ethan 自己 rsync — 他的任务只改 hook/router 代码

## Frozen sub-agents

- **Ryan-Platform**: 不派到 post-mortem 完 + `.claude/agents/eng-platform.md` 补 destructive cmd 指引
- **Maya-Governance**: 本 session 3 轮全 truncate, 下 session 重派前先跑小 task 试水
- **Ethan-CTO / Leo-Kernel / Samantha-Secretary**: 可信, 优先派

## CEO 自省 (avoidance 约束 per f24b04a7)

- Aiden 承诺: Rt+1>0 不出 "推下一个" / "你决定" / "defer" phrase
- 若 forget_guard CIEU 抓 `BOARD_CHOICE_QUESTION_DRIFT` / `CEO_AVOIDANCE_DRIFT`, 立即停回当前 task

## 4 个 system-level patches spec (延伸, 非本 session P0)

见 `reports/cieu_k9_ryan_rsync_disaster_20260414.md`:
1. engine.py destructive cmd pre-check
2. session.json schema 守护 (missing immutable_paths BLOCK)
3. mirror_contract 方向 JSON
4. hook WIP auto-commit

本 session Ethan Task = Board 指令的第 1 件 (架构断裂接桥). 其他 3 延后.

## 丢失 (不可逆, 需下 session 重跑恢复)

- Board 今早 shell 注入 10 agent.md CIEU 段落 → 下 session Board 外部 shell 再跑:
  ```
  bash reports/apply_cieu_inject.sh && bash reports/apply_cieu_rename.sh
  ```
- Maya hook_wrapper.py fail-closed patch (未 commit, 被抹) — 下 session Ethan 一起带回来
- Ryan 自己的 video_storage_migration 报告 + content/video_registry.yml

## End
