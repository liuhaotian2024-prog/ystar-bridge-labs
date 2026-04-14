#!/bin/bash
# ============================================================
# FIX-1: CIEU persistence — gov-mcp state._cieu_store 启动时挂SQLite
# ============================================================
# 根因:
#   gov-mcp/gov_mcp/server.py 的 _State.__init__ line 74:
#     self._cieu_store: Optional[Any] = None
#   只有在 gov_report/gov_verify 调用时才lazy-init CIEUStore。
#   gov_doctor L1.02 因此恒报 "in_memory_only"，warn 泄露到CI。
#   对比: ystar.adapters.hook._write_cieu 走独立code path，
#   通过 cieu_db=.ystar_cieu.db 直接落盘 (已验证13:32最新写入,5.8MB)。
#
#   风险: 两个writer不一致 — 对外"every CIEU record is sales evidence"
#   承诺在 gov_doctor 输出里变成 warn，看起来像造假。
#
# 修改:
#   gov-mcp/gov_mcp/server.py line ~74 附近:
#   插入启动时挂载持久CIEUStore的代码。
#
# 跑法:
#   bash /Users/haotianliu/.openclaw/workspace/ystar-company/reports/fix_cieu_persistence.sh
#
# 验证:
#   启动gov-mcp后 `mcp__gov-mcp__gov_doctor` → L1_02_cieu.status 应为 "active"
#   并看到 total_events > 0 (hook已累计写入)
# ============================================================
set -e

SERVER_PY=/Users/haotianliu/.openclaw/workspace/gov-mcp/gov_mcp/server.py

if [ ! -f "$SERVER_PY" ]; then
  echo "[FAIL] server.py not found: $SERVER_PY"
  exit 1
fi

# 幂等检查: 已patch过则跳过
if grep -q "# FIX-1: persistent CIEU store on boot" "$SERVER_PY"; then
  echo "[SKIP] fix_cieu_persistence already applied"
  exit 0
fi

# 备份
cp "$SERVER_PY" "$SERVER_PY.bak.$(date +%s)"

python3 <<'PYEOF'
import re, pathlib
p = pathlib.Path("/Users/haotianliu/.openclaw/workspace/gov-mcp/gov_mcp/server.py")
src = p.read_text(encoding="utf-8")

old = "        # CIEU store (None until a db path is provided via gov_report/gov_verify)\n        self._cieu_store: Optional[Any] = None"
new = '''        # CIEU store — FIX-1: persistent CIEU store on boot (was lazy-init → in_memory_only warn)
        # Attach CIEUStore backed by .ystar_cieu.db at config_dir so gov_doctor L1.02
        # reports "active" instead of in_memory_only, and so gov_report/verify see the
        # same events that hook_wrapper writes via ystar.adapters.hook._write_cieu.
        self._cieu_store: Optional[Any] = None
        try:
            from ystar.governance.cieu_store import CIEUStore
            cieu_db_path = config_dir / ".ystar_cieu.db"
            self._cieu_store = CIEUStore(db_path=str(cieu_db_path))
            self.db_path = cieu_db_path
        except Exception as _cieu_boot_exc:
            # Fail-open: if import/open fails we stay in the legacy None state.
            # gov_doctor will still warn, but server remains up.
            import logging
            logging.getLogger(__name__).warning(
                "CIEU persistent store init failed (%s); falling back to lazy init",
                _cieu_boot_exc,
            )'''

if old not in src:
    raise SystemExit("[FAIL] anchor line not found — server.py may have changed; aborting patch")

src = src.replace(old, new, 1)
p.write_text(src, encoding="utf-8")
print("[OK] patched server.py _State.__init__ to attach persistent CIEUStore on boot")
PYEOF

echo ""
echo "[DONE] fix_cieu_persistence applied."
echo "      Backup saved next to server.py (*.bak.<ts>)."
echo "      Restart gov-mcp process; then call gov_doctor and check L1_02_cieu.status == 'active'."
