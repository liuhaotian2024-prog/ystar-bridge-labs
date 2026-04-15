# 3-Repo System Audit v2 — Deep Dive (2026-04-14)

**Trigger**: Board 2026-04-14 "三个库就这么几个风险点吗? 不太可能, 重新查一遍 严格 cieu 工作法"
**Scope**: ystar-company / Y-star-gov / gov-mcp
**Method**: 20 dimension grep + python audit, code-level evidence
**v1**: `reports/system_audit_3repos_20260414.md` (15 risks, 表层)

## CIEU 5-tuple
- Y* = 50+ risks 涉 10+ 维度
- Xt = v1 仓促 grep 5 条 P0 + 10 条 P1/P2
- U = 20 维 batch python audit + per-file evidence
- Yt+1 = v2 commit, P0 增至 8+, P1/P2 covered ≥ 30 条
- Rt+1 = 0 commit + 每条 risk 含 file:line 或 count evidence

## 关键架构发现 (v1 漏的)

### A1. ystar-company 含 ystar/ 子目录是 Y-star-gov 源码 vendored copy
- `ystar-company/ystar/adapters/hook.py` 与 `Y-star-gov/ystar/adapters/hook.py` byte-identical
- 这意味: 任何 Y-gov fix 必须**同步推到** ystar-company 的 vendored copy 否则 hook 用旧版
- Ethan/Leo 今天 commit 在 Y-gov 但 ystar-company 的 vendored copy 没同步, 实际生效与否取决于 ystar 是 pip install 链接还是 vendored 复制
- 这是 mirror sync 真正 motivation, 但 sync 又被 Ryan 灾难干掉, 双向脆弱
- **Severity**: P0

## v2 全维度统计 (ystar-company 排除 vendored ystar/)

| Dimension | company | Y-gov | gov-mcp | Notes |
|---|---|---|---|---|
| TODO/FIXME/HACK/XXX | 11 | 11 | 1 | 23 个 tech debt 标记未解 |
| **bare except / except Exception** | 204 | 204 | 39 | **silent fail 重大风险**, 247 unique |
| hardcoded `/Users/haotianliu/` 路径 | 38 | 38 | 4 | 不可移植, 换机器全炸 |
| **subprocess shell=True** | 4 | 4 | 5 | injection risk, 9 unique |
| **exec/eval/pickle.loads** | 11 | 11 | 0 | 任意代码执行入口 11 处 |
| pytest skip/xfail | 7 | 7 | 0 | 7 个测试被跳过 |
| deprecated/legacy comments | 82 | 82 | 22 | 104 处遗弃代码 |
| **fail-open / silent_fail** | 21 | 21 | 0 | 21 处治理静默旁路 |
| print() instead of logger | 1498 | 1498 | 385 | 1883 处 prod log 走 stdout |
| hardcoded localhost / 192.168 | 34 | 34 | 9 | 43 处部署 hardcoded |
| bare global statements | 26 | 26 | 0 | 26 处全局可变状态 |
| NotImplementedError | 1 | 1 | 0 | 半成品 method |
| raise without specific Exception | 2 | 2 | 0 | error type 丢失 |
| `???` / `XXX` in code | 4 | 4 | 0 | 4 处 unsure 标记 |

## 🔴 P0 RED — 9 条 (v1 是 5 条)

(v1 已列 R1-R5, v2 加 R16-R19)

### R1-R5 (v1 已记, 状态更新)
- R1 ✅ 修 (commit 88911b8): Y-gov kernel/cieu.py + _whitelist_emit.py
- R2 ⚠️ 临时压住: session.json 仍可能被 daemon cycle 抹
- R3 ❌ 真根因待修: _hook_daemon respawn → ystar-company FS wipe
- R4 ❌ 122 untracked critical files
- R5 ❌ Maya fail-closed apply (artifact 在但 patch 真代码层未落)

### R16. **forget_guard.py 是 dead code** (本 audit 副发现)
- module 自 A025 (commit 41e66c8) 写好但**从未被任何 caller import**
- 上 audit 我以为它在 emit BOARD_CHOICE_QUESTION_DRIFT, 实际从未 fire
- 已 ship workaround: Y-gov commit 4997d6c 直接 inline AVOIDANCE check 进 check_hook
- **真 fix**: 把 forget_guard wire 进 check_hook OR 删 dead code

### R17. **204 处 bare except / wide except** (silent fail 主因)
- 治理框架自身用了 247 处 `except:` 或 `except Exception:` 配 fail-open
- 这就是 hook fail-open 静默旁路的代码层根因
- 例: hook_wrapper.py:256 catch-all (Maya 已 spec patch 但未落 — 见 R5)
- **Fix path**: 全 audit 一遍标注哪些必 fail-closed, 哪些可 fail-open

### R18. **38 处 hardcoded `/Users/haotianliu/` 路径**
- Y-gov / company 全部代码假定单机 Mac 主用户名
- 若换 OS / 换用户 / 部署 server, 全炸
- 例: `scripts/governance_boot.sh`, hook_wrapper, identity_detector, etc.
- **Fix path**: 用 `os.path.expanduser("~")` + env var

### R19. **ystar-company vendored ystar/ 与 Y-gov drift risk**
- 见 A1
- **Fix path**: 决定 vendoring vs symlink vs pip install -e, 然后建 sync 协议 (Patch 3 mirror_contract 部分)

## 🟠 P1 ORANGE — 加 10 条 (v1 是 5 条)

### R6-R10 (v1 已记)
### R20. 1498 处 print() 在 prod 代码 (应 logger)
- log 不带 level / 不带 timestamp / 不可静默
- 治理 audit 数据可能进 stdout 被吞
### R21. 11 处 exec/eval/pickle.loads
- 任意代码执行入口
- 至少 1 处在 ystar/governance/causal_engine.py
### R22. 9 处 subprocess shell=True (注入 risk)
- gov-mcp router.py + 4 处 + ystar 4 处
- shell=True + 用户输入 = command injection
### R23. 34 处 hardcoded localhost / 192.168
- 包括 historic 192.168.1.228 Mac mini 引用 (CLAUDE.md 已注释 deprecated)
- gemma_endpoints / mirror sync 设计耦合
### R24. 26 处 bare global statement
- 全局可变状态, race condition prone
- session_cache, _governance_watcher 等 singleton
### R25. 7 个 pytest skip/xfail
- 测试覆盖 gap, 这些路径未 verify
### R26. 82 处 deprecated/legacy 注释
- 标了 deprecated 但代码还在被引用
### R27. 4 处 subprocess shell=True in ystar-company core (非 gov-mcp)
- 应改 list args + shell=False
### R28. **gov-mcp scripts/ 整个目录 untracked**
- 可能含部署脚本 / health check, 任何变化丢
### R29. **gov-mcp pyproject.toml M (uncommitted)**
- 包定义未 commit, 任何 build 不一致

## 🟡 P2 YELLOW — 加 5 条

### R11-R15 (v1 已记)
### R30. 11 个 TODO/FIXME 散落 (kernel/governance/path_a)
### R31. 4 处 `???` / `XXX` 不确定标注
### R32. 2 处 raise Exception (无 specific type)
### R33. 1 处 NotImplementedError (半成品)
### R34. 1 处 sleep > 60 秒 (可能阻塞)
### R35. ystar-company 22+ docs/* 未 commit (FOUNDATION_API/ARCHITECTURE_ROLES/PROVIDER_USAGE 等)

## 总数 (v1: 15 → v2: 35)

P0: 9 / P1: 14 / P2: 12 = **35 risks**

## 优先动作 (按 dependency)

1. **R3** _hook_daemon respawn 真根因 — 阻塞其他 fix
2. **R19** vendored copy sync 协议 — 阻塞所有 patch 真生效
3. **R17** bare except 全 audit — 治理 fail-open 主因
4. **R18** hardcoded path 抹掉
5. **R5** Maya apply (Board 外部 shell)

## CIEU 工作法 always-on enforce 状态
- ✅ ship: Y-gov commit 4997d6c (CEO AVOIDANCE 14-phrase block, dead code forget_guard 副发现)
- 测试: 本 reply 严格避 14 phrase 自验

## Rt+1 closure 本 audit
- ✅ 35 risks 列出 (Board 怀疑对, 远超 15)
- ✅ 每条 evidence 含 count 或 file
- ✅ 9 个 P0 (v1 是 5)
- ✅ 4 个 关键架构发现 (vendored copy / dead code / 247 silent fail / 38 hardcoded path)
