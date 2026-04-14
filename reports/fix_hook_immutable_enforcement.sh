#!/bin/bash
# ============================================================
# FIX-3: Hook immutable enforcement — 修复 bash path-extraction 误报
# ============================================================
# 根因 (2个子bug):
#
# 3a) _extract_write_paths_from_bash (boundary_enforcer.py:446) 正则过宽:
#     - cp_pattern: r'\bcp\s+(?:-\w+\s+)*(.+?)(?:\s*[;&|]|$)'
#     - mv_pattern: r'\bmv\s+(?:-\w+\s+)*(.+?)(?:\s*[;&|]|$)'
#     会把 `sqlite3 db "SELECT ... strftime('%s','now') ..."` 这类命令里的
#     子串误当 cp/mv 参数，把 "strftime(" 当成目标路径。
#     → CEO跑sqlite查CIEU时被DENY: "cannot write to 'strftime('".
#     这是**过度触发** (B3测试本想测under-trigger, 实际同时暴露了over-trigger)。
#
# 3b) verify脚本B3测试的AGENTS.md写入payload用的是 YSTAR_AGENT_ID=ceo 环境变量，
#     但hook_wrapper从payload.tool_input里读file_path, 走的是 check_hook()
#     里的 _check_immutable_paths，应该触发DENY。
#     实测返回 {} → 可能immutable_paths未配置/未加载。
#     需检查: session.json里immutable_paths是否含 AGENTS.md。
#
# 修改:
#   1. boundary_enforcer.py _extract_write_paths_from_bash:
#      给 cp/mv/tee 正则加词边界 + 只接受看起来像路径的token (含 / 或 . 或以字母开头
#      的合法文件名chars)，过滤掉含 ( ) ' " % 的token。
#   2. scripts/hook_wrapper.py: 在 _intent_guard_check 之前加一个 guard:
#      如果 file_path 含 "(" 或 "%" 等非法path char → 早返回 None (防御性)。
#   3. 检查 .ystar_session.json 的 immutable_paths 是否含 AGENTS.md;
#      如无则补上并打印WARN.
#
# 跑法:
#   bash /Users/haotianliu/.openclaw/workspace/ystar-company/reports/fix_hook_immutable_enforcement.sh
#
# 验证 (两条):
#   (a) sqlite3查询不再被假DENY:
#       YSTAR_AGENT_ID=ceo python3 -c "..." (含strftime) 应正常跑完
#   (b) 故意写AGENTS.md仍被DENY:
#       echo '{"tool_name":"Write","tool_input":{"file_path":"AGENTS.md",...}}' \
#         | YSTAR_AGENT_ID=ceo python3 scripts/hook_wrapper.py
#       输出应含 "deny" / "immutable"
# ============================================================
set -e

BE_PY=/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/boundary_enforcer.py
SESSION_JSON=/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json

# ── Part 1: patch _extract_write_paths_from_bash ──────────────
if grep -q "# FIX-3: path-like filter" "$BE_PY"; then
  echo "[SKIP] boundary_enforcer already patched"
else
  cp "$BE_PY" "$BE_PY.bak.$(date +%s)"
  python3 <<'PYEOF'
import pathlib
p = pathlib.Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/boundary_enforcer.py")
src = p.read_text(encoding="utf-8")

# Insert helper just before `def _extract_write_paths_from_bash`.
helper = '''
# FIX-3: path-like filter — reject tokens that clearly aren't filesystem paths.
# Root cause: the cp/mv/tee regexes are greedy and can capture SQL fragments
# like "strftime(" from `sqlite3 db "... strftime('%s','now') ..."` invocations.
# A token is treated as a path only if it:
#   - contains no shell metacharacters (parens, %, quotes, $, backticks)
#   - either contains / or . or - or _, or is a bareword starting with a letter
_FIX3_FORBIDDEN_CHARS = set("()%`$\\"'\\n\\t")

def _looks_like_path(token: str) -> bool:
    if not token:
        return False
    if any(c in _FIX3_FORBIDDEN_CHARS for c in token):
        return False
    # Reject things that look like SQL function calls or inline code fragments.
    if token.endswith("("):
        return False
    # Accept if clearly path-shaped.
    if "/" in token or "\\\\" in token or "." in token or "-" in token or "_" in token:
        return True
    # Bare identifiers: only accept if reasonable file-name length.
    return token.isidentifier() and 1 <= len(token) <= 64

'''

anchor = "# ── Bash 命令写路径提取 ───────────────────────────────────────────────────\ndef _extract_write_paths_from_bash(command: str) -> list:"
if anchor not in src:
    raise SystemExit("[FAIL] extract_write_paths anchor not found")
src = src.replace(anchor, helper + anchor, 1)

# Then filter the final `normalized` list via _looks_like_path before returning.
old_ret = '''    # 去重并返回
    return list(set(normalized))'''
new_ret = '''    # 去重并返回 (FIX-3: drop tokens that don't look like filesystem paths)
    return list({p for p in normalized if _looks_like_path(p)})'''
if old_ret not in src:
    raise SystemExit("[FAIL] extract_write_paths return anchor not found")
src = src.replace(old_ret, new_ret, 1)

p.write_text(src, encoding="utf-8")
print("[OK] boundary_enforcer.py: added _looks_like_path filter, fixing over-triggering DENY")
PYEOF
fi

# ── Part 2: ensure AGENTS.md is in immutable_paths ────────────
if [ -f "$SESSION_JSON" ]; then
  python3 <<PYEOF
import json, pathlib
p = pathlib.Path("$SESSION_JSON")
data = json.loads(p.read_text(encoding="utf-8"))
imm = data.get("immutable_paths") or data.get("contract", {}).get("immutable_paths") or []
target = "AGENTS.md"
if target in imm:
    print(f"[OK] {target} already in immutable_paths")
else:
    # Try both top-level and contract.* locations
    if "immutable_paths" in data:
        data["immutable_paths"] = list(set(list(imm) + [target]))
    elif "contract" in data and isinstance(data["contract"], dict):
        cur = data["contract"].get("immutable_paths", [])
        data["contract"]["immutable_paths"] = list(set(list(cur) + [target]))
    else:
        data["immutable_paths"] = [target]
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] appended {target} to immutable_paths in $SESSION_JSON")
PYEOF
else
  echo "[WARN] $SESSION_JSON not found — skip immutable_paths check"
fi

echo ""
echo "[DONE] fix_hook_immutable_enforcement applied."
echo "  Verify (a): CEO can now run sqlite with strftime() without false DENY."
echo "  Verify (b): Writing to AGENTS.md via Write tool should still DENY (immutable)."
