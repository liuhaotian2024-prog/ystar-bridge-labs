# CZL-P1-c Completion Receipt — EnforceDecision.REDIRECT Wire

**Atomic ID**: CZL-P1-c
**Claimed by**: eng-kernel (Leo)
**Completed + CEO Verified**: 2026-04-18

**Audience**: Board (核心架构主张 "门卫+导游" 落地证据), Ethan-CTO (架构审查), 未来 agent drift 场景下读这条 receipt 找到自救路径。Purpose: 证明 Board 2026-04-18 "除了 allow deny 以外要有 REDIRECT 中间态" 主张在代码上 landed，不是停留在 docstring TODO。

**Research basis**: Board 原话 "负责 deny 的模块应该有中间区间给出正确规则指引"。先前 `EnforceDecision` 只有 ALLOW/DENY/ESCALATE 三值，REDIRECT 写在 intervention_engine docstring 但从未 wire。hook.py:1017 把 DENY+ESCALATE 合并成同一 deny response，suggested_action 淹没消息末尾。agent drift 后只看到 "denied" 试错放大 → lock-death。

**Synthesis**: 这是整个 enforce-as-router 架构（P2 基础）的关键一步 — REDIRECT 让 enforce 首次能"指路"而非只"拦截"。message 结构化为 `REDIRECT / FIX_COMMAND / THEN_RETRY` 三段让 agent 知道具体跑什么命令可恢复。suggested_action 从泛文改具体 shell 命令是最小可执行单元。后续 Phase 2 INVOKE/INJECT/AUTO_POST 在此 pattern 上延展。

## 5-Tuple
- **Y\***: EnforceDecision 加 REDIRECT + hook.py 3 分支 wire + suggested_action 具体命令
- **Xt**: EnforceDecision={ALLOW,DENY,ESCALATE}, hook.py:1017 DENY+ESCALATE 合并, intervention_engine suggested_action 泛文
- **U**:
  - `Y-star-gov/ystar/domains/openclaw/adapter.py:95` — `REDIRECT = "redirect"` 加入 enum
  - `Y-star-gov/ystar/domains/openclaw/adapter.py:981-1008` — `GateDecision.REDIRECT → EnforceDecision.REDIRECT` wire in `enforce()` + CIEU record
  - `Y-star-gov/ystar/adapters/hook.py:1016-1098` — DENY/ESCALATE/REDIRECT 三独立分支；REDIRECT 返回 `permissionDecision=allow` + 结构化 `[Y*] REDIRECT: / FIX_COMMAND: / THEN_RETRY:` 消息
  - `Y-star-gov/ystar/governance/intervention_engine.py:508` — `suggested_action='echo "ceo" > .../.ystar_active_agent && retry'`（具体命令）
  - `Y-star-gov/tests/adapters/test_redirect_decision.py` — 9 tests
- **Yt+1**: 9 tests PASS + grep 验位置
- **Rt+1**: 0
