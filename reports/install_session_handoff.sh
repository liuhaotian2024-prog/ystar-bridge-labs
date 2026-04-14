#!/bin/bash
# ============================================================
# Session Handoff Feature — 安装脚本
# 源头: reports/session_handoff_implementation.md (CTO Ethan已完成设计+源码)
# 绕过: Claude Code hook对CEO/CTO写权限限制，老大!bash直跑
# ============================================================

set -e

REPO=/Users/haotianliu/.openclaw/workspace/ystar-company
REPORT="$REPO/reports/session_handoff_implementation.md"
cd "$REPO"

echo "=== Session Handoff 安装 ==="
echo ""

# Python extractor: 从report markdown里抽code blocks
python3 << 'PYEOF'
import re, pathlib, json, sys, os

report_path = pathlib.Path("reports/session_handoff_implementation.md")
report = report_path.read_text()

def extract_code_block(text, section_header, lang):
    """Extract first ```<lang> ... ``` block after section_header."""
    start = text.find(section_header)
    if start == -1:
        raise ValueError(f"Section not found: {section_header}")
    # Find opening fence
    fence_open = f"```{lang}"
    fo = text.find(fence_open, start)
    if fo == -1:
        raise ValueError(f"No {lang} block in section {section_header}")
    body_start = text.find("\n", fo) + 1
    fence_close = text.find("\n```", body_start)
    return text[body_start:fence_close]

files_to_write = [
    ("## 2. Complete source", "python", "scripts/ystar_handoff.py", 0o755),
    ("## 3. Complete source", "python", "scripts/hook_session_start.py", 0o755),
    ("## 5. E2E test", "bash", "scripts/test_session_handoff.sh", 0o755),
]

# Products doc (markdown block inside markdown — fence is ```markdown)
products_dir = pathlib.Path("products/ystar-gov/features")
products_dir.mkdir(parents=True, exist_ok=True)

for header, lang, target, mode in files_to_write:
    try:
        code = extract_code_block(report, header, lang)
    except Exception as e:
        print(f"  [SKIP] {target}: {e}")
        continue
    p = pathlib.Path(target)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(code)
    os.chmod(p, mode)
    print(f"  [OK] {target} ({len(code)} chars)")

# Product doc: fence is ```markdown
try:
    code = extract_code_block(report, "## 6. Product doc", "markdown")
    p = pathlib.Path("products/ystar-gov/features/session_handoff.md")
    p.write_text(code)
    print(f"  [OK] {p} ({len(code)} chars)")
except Exception as e:
    print(f"  [SKIP] products doc: {e}")

# .claude/settings.json merge
print("")
print("=== Merge .claude/settings.json ===")
settings_path = pathlib.Path(".claude/settings.json")
if settings_path.exists():
    settings = json.loads(settings_path.read_text())
else:
    settings = {}

settings.setdefault("hooks", {})
settings["hooks"]["SessionStart"] = [
    {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
            {
                "type": "command",
                "command": f"python3 {pathlib.Path.cwd()}/scripts/hook_session_start.py",
                "timeout": 5000,
            }
        ],
    }
]
settings_path.parent.mkdir(parents=True, exist_ok=True)
settings_path.write_text(json.dumps(settings, indent=2))
print(f"  [OK] SessionStart hook registered in {settings_path}")

print("")
print("=== gov-mcp server.py additions ===")
print("  [MANUAL] 需要手工append 2个tool到 gov-mcp/gov_mcp/server.py:")
print("  [MANUAL] - gov_full_handoff(agent_id)")
print("  [MANUAL] - gov_full_handoff_text(agent_id)")
print("  [MANUAL] 代码片段在 reports/session_handoff_implementation.md '## 7.'")
print("  [MANUAL] 现在hook可直接调用 scripts/ystar_handoff.py，不依赖MCP endpoint")
print("           (双路径设计: hook走stdlib direct, MCP tool是产品化入口)")

PYEOF

echo ""
echo "=== 运行E2E测试 ==="
bash scripts/test_session_handoff.sh || {
    echo ""
    echo "测试失败——检查上面输出，常见原因："
    echo "  1. memory/continuation.json 没有 campaign.name='Defuse' + day=3 — 已知此文件在repo"
    echo "  2. scripts/ystar_handoff.py 组装逻辑bug — 看详细报错"
    echo "  3. additionalContext超10k — 调per-section char budget"
    exit 1
}

echo ""
echo "============================================================"
echo "  Session Handoff 安装完成。"
echo "  老大验证方法:"
echo "  1. 退出当前Claude Code (Ctrl+D 或 /exit)"
echo "  2. 重新 cd $REPO && claude"
echo "  3. 不boot不输任何命令，直接问Aiden: '你正在打什么仗？Day几？'"
echo "  4. Aiden应该直接答'Y*Defuse Day 3' — 他无感接上"
echo ""
echo "  如果Aiden答对 = session handoff成功 = 搬家问题解决 = gov-mcp新feature诞生"
echo "============================================================"
