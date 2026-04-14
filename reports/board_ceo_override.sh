#!/bin/bash
# Board → CEO 权限临时升级 / 回收
# Usage:
#   bash reports/board_ceo_override.sh grant  [minutes]   # 默认 60 min
#   bash reports/board_ceo_override.sh revoke
#   bash reports/board_ceo_override.sh status
#
# 作用（grant）：
#   1. 把 Y-star-gov/ 和 gov-mcp/ 加入 CEO 写路径
#   2. 从 ceo_deny_paths 移除 Y-star-gov/ystar/
#   3. 翻 agent_behavior_rules.ceo.must_dispatch_via_cto = false（允许 CEO 直派工程师）
#   4. 记录 expires_at；CEO 用完自己 revoke
#
# 每次 grant 会写 backup 到 .ystar_session.json.pre_override.<ts>

set -e
WORKSPACE="/Users/haotianliu/.openclaw/workspace/ystar-company"
SESSION_JSON="$WORKSPACE/.ystar_session.json"
cd "$WORKSPACE"

MODE="${1:-status}"
MINUTES="${2:-60}"

case "$MODE" in
  grant)
    TS=$(date +%s)
    BACKUP="$SESSION_JSON.pre_override.$TS"
    cp "$SESSION_JSON" "$BACKUP"
    python3 - <<PY
import json, time
p = "$SESSION_JSON"
d = json.load(open(p))

wp = d.setdefault("agent_write_paths", {}).setdefault("ceo", [])
for extra in [
    "/Users/haotianliu/.openclaw/workspace/Y-star-gov/",
    "/Users/haotianliu/.openclaw/workspace/gov-mcp/",
]:
    if extra not in wp:
        wp.append(extra)

deny = d.get("ceo_deny_paths", [])
d["ceo_deny_paths"] = [x for x in deny if "Y-star-gov/ystar/" not in x]

rules = d.setdefault("agent_behavior_rules", {}).setdefault("ceo", {})
rules["must_dispatch_via_cto"] = False

d["_ceo_board_override"] = {
    "granted_at": int(time.time()),
    "expires_at": int(time.time()) + $MINUTES * 60,
    "backup": "$BACKUP",
    "granter": "Board (Haotian)",
}

json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
print("[grant] write_paths += Y-star-gov, gov-mcp")
print("[grant] deny_paths -= Y-star-gov/ystar/")
print("[grant] must_dispatch_via_cto = False")
print(f"[grant] expires in $MINUTES min")
print(f"[grant] backup: $BACKUP")
PY
    echo ""
    echo "✅ CEO override GRANTED ($MINUTES min)."
    echo "回收：bash reports/board_ceo_override.sh revoke"
    ;;

  revoke)
    BACKUP=$(ls -t "$SESSION_JSON".pre_override.* 2>/dev/null | head -1)
    if [ -z "$BACKUP" ]; then
      echo "❌ 无 backup 可回滚"
      exit 1
    fi
    cp "$BACKUP" "$SESSION_JSON"
    echo "✅ 回滚自: $BACKUP"
    python3 -c "import json; print('    must_dispatch_via_cto:', json.load(open('$SESSION_JSON'))['agent_behavior_rules']['ceo'].get('must_dispatch_via_cto'))"
    ;;

  status)
    python3 - <<PY
import json, time
d = json.load(open("$SESSION_JSON"))
ov = d.get("_ceo_board_override")
if not ov:
    print("状态：无 override（标准约束）")
else:
    remain = ov["expires_at"] - int(time.time())
    if remain > 0:
        print(f"状态：GRANTED — 剩余 {remain//60}m {remain%60}s")
    else:
        print(f"状态：GRANTED 但已过期 {(-remain)//60}m（仍生效到 revoke）")
    print(f"  backup: {ov['backup']}")
    print(f"  must_dispatch_via_cto: {d['agent_behavior_rules']['ceo'].get('must_dispatch_via_cto')}")
PY
    ;;

  *)
    echo "Usage: $0 {grant [minutes] | revoke | status}"
    exit 1
    ;;
esac
