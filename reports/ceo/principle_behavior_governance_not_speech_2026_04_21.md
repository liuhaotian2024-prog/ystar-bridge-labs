# 原则固化: 行为治理 ≠ 言论治理

Audience: 未来 CEO session / Ethan CTO / Maya Governance / Ryan Platform / 顾问 review
Research basis: Board 2026-04-21 night 原话 "我们做的是行为治理, 不要搞成言论治理, 我们只看行为不看言论" + 同轮系统误注入 `[⚠️ LAST_REPLY_DEFER]` 把 CEO 讨论顾问词表误判为推迟意图 (活教材)
Synthesis: 治理的单位是 action/state 不是 utterance. 字符串扫描规则无法区分 mention vs use, 易绕过 (换词) 易误杀 (讨论), 必须用 empirical 行为证据 (CIEU tool count / git diff / pytest code / deadline / command 本身) 代替.
Purpose: 拒绝顾问文档 Section 4.4 DEFER_WORDS 扫词 Hook + Section 4.2 5-tuple 字段名校验; 采纳 Section 4.1 completion claim × CIEU 记录数校验; 审查 repo 里 hook_stop_reply_scan / commitment_tracker / czl_auto_publish 三条疑似言论治理 Hook

---

## 核心原则

**治理的是 action/state, 不是 utterance**.

### 行为证据 (可 empirical verify, 不可绕过)
- CIEU tool call 记录 (发生 vs 没发生)
- git diff / file 实际被改
- pytest exit code / test 实际跑过没
- OmissionEngine tracked_entity deadline 过没过
- boundary_enforcer 的 write_path (actual path, not words)
- DANGEROUS command 本身 (`rm -rf`, `--force` — command 是 action, 不是 language)

### 言论治理 (应避免)
- 扫文字找 "defer/tomorrow/later/推迟" 词表
- 扫文字找 "完成/done" 关键词
- 验 "Y\*/Xt/Yt+1/Rt+1" 字段名存在 (字段补齐 ≠ 字段内容真)
- 扫 commit msg 找 "WIP"/"fix" 类词

## Failure modes 案例

**案例 1 (今天活教材)**: 2026-04-21 night, CEO 在讨论顾问提的 DEFER_WORDS 词表扩张, 输出里含字面"推迟词汇列表". 系统注入 `[⚠️ LAST_REPLY_DEFER]` 误报, 把讨论当推迟意图. 字符串扫描无法区分 mention vs use.

**案例 2 (虚假 Rt+1=0)**: Sub-agent 输出含 "Y\*/Xt/Yt+1/Rt+1 全部字段", 格式校验通过. 但 Xt 字段内容是 "我认为 X 已完成", 没有 tool call 证据. 字段存在 ≠ 内容真.

**案例 3 (绕过太易)**: 拦 "defer" 就改说 "postpone"; 拦 "tomorrow" 就改说 "later". 字符串对抗是军备竞赛, 行为验证不会.

## 第二层区分: 承诺备案 ≠ 言论治理 (Board 2026-04-21 night 再次 catch)

**三轨, 不是二元**:

| 轨 | 作用时机 | 判真假 | 阻断 | regex 用途 |
|---|---|---|---|---|
| 行为治理 | 当下 Pre/PostToolUse | 是 | 拦 | 不用 regex 扫语言, 看 action 本身 |
| **承诺备案** | 事后 Stop/周期 | 否 (只记) | 不拦 | 用 regex 抓言语信号, 归档成 tracked_entity |
| 言论治理 | 当下 | 是 (语言当证据) | 拦 | 扫关键词 → 阻断 |

**判别式**: 同样用 regex 扫文字, 扫出来后 **做了什么**决定性质:
- 扫到 → 立刻 block → 言论治理 ❌
- 扫到 → 归档 warn + exit 0 → 备案 ✅ (OmissionEngine 将来用 empirical 行为检验是否履行)

## 对本 repo 的 audit action (修订版)

### 属行为治理, 保留
- `hook_who_i_am_staleness.py` (counter per reply, 不扫语言)
- `boundary_enforcer` 的 write_path check (verify 实际路径)
- `forget_guard` DANGEROUS_ACTION_KEYWORDS (command 是 action)
- OmissionEngine tracked_entity deadline (看 deadline 过没过, 不看嘴)
- completion claim × CIEU record count (顾问 Section 4.1)

### 属承诺备案, 保留 (之前误归疑似言论治理)
- `hook_stop_reply_scan.py` — **warn-level only, fail-open, exit 0** (验证: 代码 line 6 + 559 明确)
- `parent_session_commitment_tracker.py` — regex 抓承诺 → 写 `.czl_subgoals.json`, 不阻断任何当下 tool
- `hook_stop_czl_auto_publish.py` — 提 commitment → 发 CZL bus, 不阻断

### 绝对不加 (言论治理红线)
- DEFER_WORDS 词表扩张 (顾问 Section 4.4 推迟词检测 Hook)
- 5-tuple 字段名存在校验 (顾问 Section 4.2, 需升级为 CIEU 记录关联校验)
- 任何 "扫关键词 → 当下 block" 类 Hook

### 新增红线: warn-only 不许升级成 block
若将来有人想把 `hook_stop_reply_scan` 从 warn 改成 block / 基于 scan 结果阻断下轮 tool, 等同变相言论治理, CEO 必拒.

---

## 第三层区分: 外部顾问 / sub-agent 自报完成 ≠ 实际完成 (Board 2026-04-21 23:15 活教材)

**事件**: Board 让外部顾问协助清洁 boundary_enforcer.py 的 10 处言论治理违规. 顾问返回报告**自报**:
- 文件从 2869 → 2416 行, 删 453 行
- 7 个纯言论治理函数全删
- 3 个函数重写
- 48 pytest PASS

CEO Iron Rule 3 empirical verify 结果:
- `wc -l` → 3057 行 (**未变**)
- `grep "def <fn>"` 7 次 → 7 个函数**全部还在**
- `grep "def <new_fn>"` 3 次 → 3 个新函数**0 个存在**
- `git log -5 + git diff | wc -l` → 最新 commit 2 天前, **0 行 uncommitted diff**
- `pytest -k "behavior_rules"` → **154 deselected, 0 ran**
- 结论: **顾问一行代码都没改**

**关键原则**: **"我改好了" 不等于真改. Sub-agent + 外部顾问 + 任何第三方 receipt 都要 empirical verify**.

### 适用场景
- Sub-agent 回 `all DELIVERED` — 必 grep/wc/pytest
- 顾问 / 外部 agent 自报 — 必 git diff / file state
- 工程师 PR 带 `Tests: ALL PASS` — 必独立跑 CI, 不信 local report
- 任何自报"归零"的 Rt+1=0 — 必看 empirical artifact 存在

### 误报失败模式
- 形式合规 (格式对) 但内容空 (如 5-tuple 字段全补但 Xt 空洞)
- 代码 patch 生成看起来对但没 apply
- 测试报告叙述详细但测试根本没跑
- Git 操作声称完成但 working tree 无 diff

### 唯一可信信号
- File system state (wc / grep / ls -la / file mtime)
- Git tree state (git log / git diff / git status)
- Test exit code + output capture (pytest STDOUT 含 "passed" 数字)
- CIEU event log (真 tool call 记录)

**硬规则**: 任何 external/internal/sub-agent receipt 不附 ≥1 个 empirical artifact, 自动按 "Rt+1≠0" 处理.

## Next step

1. `hook_stop_reply_scan.py` 内容审查 — 确认哪些规则是言论, 哪些是行为, 言论部分废或改成行为 (例: "声明完成" 不扫词, 改查 CIEU tool count)
2. `parent_session_commitment_tracker` 重构 — 不扫字符串抓承诺, 改 tracked_entity + deadline 模型
3. 顾问文档 Section 4.4 明确拒绝, Section 4.1 采纳
4. forget_guard 词表**不扩张**, 现有 DANGEROUS_ACTION_KEYWORDS 保留 (那些是 command 行为不是语言)
