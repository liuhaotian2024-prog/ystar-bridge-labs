# CZL-ARCH-14 Completion Receipt — REWRITE Decision Type

**Atomic ID**: CZL-ARCH-14
**Claimed by**: eng-kernel (Leo)
**Completed + CEO Verified**: 2026-04-18 (27 tool_uses / 746s / 18/18 tests)

**Audience**: Board (who directly requested this mechanism 2026-04-18: "能不能有个模块把 agent 做的不合规的地方直接修改到合规然后顺利推进"), CTO Ethan (arch integration with ARCH-11 family), future engineers building on REWRITE primitive.

**Research basis**: Industry precedents — auto-formatters (black, prettier, clippy auto-fix), service mesh auto-inject (Istio mTLS, linkerd), SQL input sanitization, Rust rustfmt. Ethan's arch doc Part A spec. Today's empirical triggers: CEO commit messages falsely denied because token "EOF" / "case-insensitive" matched write-path parser; `os.environ` falsely denied because contains ".env" substring; `> /dev/null` falsely denied because redirect treated as write.

**Synthesis**: RewriteTransform dataclass + 3 registered safe transforms (commit_msg_token_safe / os_environ_env_match / dev_null_write_false_positive) + auto_rewrite_detector + auto_rewrite_executor. Hook.py integration at 2 points: `_check_hook_full` (session path) + `check_hook` (light path). When enforce() returns DENY AND a safe transform matches, override to ALLOW + emit REWRITE_APPLIED CIEU event. Board's "门卫+导游" principle extended — now hook also does auto-repair where safely identifiable.

## 5-Tuple
- **Y\***: REWRITE decision type wired end-to-end with 3 safe transforms; CEO no longer workarounds false-positive hook denies
- **Xt**: Hook treated commit msg tokens / os.environ substrings / /dev/null redirects as path writes → blanket deny → CEO trapped in workaround loop
- **U**:
  - `Y-star-gov/ystar/domains/openclaw/adapter.py:100` — `REWRITE = "rewrite"` enum
  - `Y-star-gov/ystar/rules/auto_rewrite.py` — 160 lines with 3 registered transforms
  - `Y-star-gov/ystar/adapters/hook.py:902-912` — 2 wire points + REWRITE_APPLIED CIEU event
  - `Y-star-gov/tests/rules/test_auto_rewrite.py` — 18 tests across 4 test classes
- **Yt+1**: 18/18 tests PASS in 0.06s; CEO empirical verify: grep confirms enum value + wire points + CIEU event name
- **Rt+1**: 0 for ARCH-14 core. Remaining false-positive patterns can be added as RewriteTransform registrations without changing adapter or hook.
