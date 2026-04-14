#!/bin/bash
# ============================================================
# FIX-2: Delegation store schema — 创建 delegations 视图/表对齐verify脚本
# ============================================================
# 根因:
#   gov-mcp 实际表名: delegation_links (server.py:349)
#     columns: principal, actor, contract_json, grant_id
#   verify_full_handoff.sh B4 查询的是: SELECT COUNT(*) FROM delegations
#     → sqlite报 "no such table: delegations" (FAIL)
#
#   这是verify脚本和server实现之间的schema契约不齐。两条fix路线:
#     A) 改verify脚本查 delegation_links (最小改动，契约不变)
#     B) 在 .gov_mcp_state.db 建 VIEW delegations AS SELECT * FROM delegation_links
#        (生态兼容，未来gov_self_test MCP工具查delegations更语义化)
#   我们两条都做: 建VIEW + 修verify脚本 (防御式)。
#
# 修改:
#   1. .gov_mcp_state.db: CREATE VIEW delegations AS SELECT principal, actor,
#                         contract_json, grant_id FROM delegation_links
#   2. reports/verify_full_handoff.sh B4 段: 容错查 delegations 或 delegation_links
#   3. gov-mcp/gov_mcp/server.py persist_to_db(): 建表时同时建 VIEW (确保新部署也有)
#
# 跑法:
#   bash /Users/haotianliu/.openclaw/workspace/ystar-company/reports/fix_delegation_schema.sh
#
# 验证:
#   sqlite3 .gov_mcp_state.db "SELECT COUNT(*) FROM delegations;"  # no error
#   bash reports/verify_full_handoff.sh  # B4 应 PASS
# ============================================================
set -e

STATE_DB=/Users/haotianliu/.openclaw/workspace/ystar-company/.gov_mcp_state.db
SERVER_PY=/Users/haotianliu/.openclaw/workspace/gov-mcp/gov_mcp/server.py
VERIFY_SH=/Users/haotianliu/.openclaw/workspace/ystar-company/reports/verify_full_handoff.sh

# ── Part 1: 在现有 state DB 建 VIEW ─────────────────────────
if [ -f "$STATE_DB" ]; then
  sqlite3 "$STATE_DB" <<'SQL'
-- 幂等: 已存在则先删
DROP VIEW IF EXISTS delegations;
CREATE VIEW delegations AS
  SELECT principal, actor, contract_json, grant_id
  FROM delegation_links;
SQL
  echo "[OK] VIEW delegations created in $STATE_DB"
else
  echo "[WARN] $STATE_DB not present — VIEW will be created on next gov-mcp boot via server patch"
fi

# ── Part 2: server.py persist_to_db() 加 CREATE VIEW IF NOT EXISTS ─────
if grep -q "# FIX-2: delegations view" "$SERVER_PY"; then
  echo "[SKIP] server.py already patched"
else
  cp "$SERVER_PY" "$SERVER_PY.bak.delegations.$(date +%s)"
  python3 <<'PYEOF'
import pathlib
p = pathlib.Path("/Users/haotianliu/.openclaw/workspace/gov-mcp/gov_mcp/server.py")
src = p.read_text(encoding="utf-8")
old = '''            c.execute("""CREATE TABLE IF NOT EXISTS counters (
                key TEXT PRIMARY KEY, value TEXT)""")'''
new = '''            c.execute("""CREATE TABLE IF NOT EXISTS counters (
                key TEXT PRIMARY KEY, value TEXT)""")

            # FIX-2: delegations view — semantic alias over delegation_links
            # Lets external tools (gov_self_test, verify scripts) query
            # the canonical name `delegations` without schema drift.
            c.execute("""CREATE VIEW IF NOT EXISTS delegations AS
                SELECT principal, actor, contract_json, grant_id
                FROM delegation_links""")'''
    # (indentation: keep 4 leading spaces consistent)
if old not in src:
    raise SystemExit("[FAIL] anchor for persist_to_db not found")
p.write_text(src.replace(old, new, 1), encoding="utf-8")
print("[OK] server.py persist_to_db() now also creates `delegations` VIEW")
PYEOF
fi

# ── Part 3: verify_full_handoff.sh B4 容错查询 ─────────────
if [ -f "$VERIFY_SH" ] && ! grep -q "# FIX-2: delegations tolerant" "$VERIFY_SH"; then
  cp "$VERIFY_SH" "$VERIFY_SH.bak.$(date +%s)"
  python3 <<'PYEOF'
import pathlib
p = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/reports/verify_full_handoff.sh")
src = p.read_text(encoding="utf-8")
old = '''    cur = c.execute('SELECT COUNT(*) FROM delegations')
    print(f'  delegations: {cur.fetchone()[0]} grants in store')'''
new = '''    # FIX-2: delegations tolerant — prefer view, fall back to base table
    try:
        cur = c.execute('SELECT COUNT(*) FROM delegations')
    except Exception:
        cur = c.execute('SELECT COUNT(*) FROM delegation_links')
    print(f'  delegations: {cur.fetchone()[0]} grants in store')'''
if old not in src:
    raise SystemExit("[FAIL] anchor for verify_full_handoff.sh B4 not found")
p.write_text(src.replace(old, new, 1), encoding="utf-8")
print("[OK] verify_full_handoff.sh B4 now tolerates missing view")
PYEOF
fi

echo ""
echo "[DONE] fix_delegation_schema applied."
echo "      Verify: sqlite3 $STATE_DB 'SELECT COUNT(*) FROM delegations;'"
