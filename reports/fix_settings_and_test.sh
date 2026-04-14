#!/bin/bash
# 修settings.json BOM + merge SessionStart + E2E测试
cd /Users/haotianliu/.openclaw/workspace/ystar-company

python3 << 'PYEOF'
import json, pathlib
p = pathlib.Path(".claude/settings.json")
s = json.loads(p.read_text(encoding="utf-8-sig"))
s.setdefault("hooks", {})
s["hooks"]["SessionStart"] = [{
    "matcher": "startup|resume|clear|compact",
    "hooks": [{
        "type": "command",
        "command": "python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_session_start.py",
        "timeout": 5000
    }]
}]
p.write_text(json.dumps(s, indent=2))
print("[OK] SessionStart hook registered, BOM stripped")
PYEOF

echo ""
echo "=== E2E Test ==="
bash scripts/test_session_handoff.sh
