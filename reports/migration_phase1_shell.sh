#!/bin/bash
# ============================================================
# Phase 1 Migration — CEO agent到OpenClaw（老大明早5分钟跑）
# ============================================================
# 作者: CTO Ethan Wright（via delegation grant e319bfe8）
# 审阅: CEO Aiden
# 日期: 2026-04-11 夜
#
# 为什么需要老大手动跑:
#   Claude Code Hook层 (boundary_enforcer.py) 和 MCP层 (gov_delegate)
#   enforcement plane失同步——hook不认MCP grant。CTO subagent所有写全被DENY。
#   老大在Mac直接跑shell绕过Claude Code hook，Phase 1 5分钟完成。
#
# 根治方案（不是今晚）:
#   - Option A: secretary给session.json加cto write paths (明早15分钟)
#   - Option B: boundary_enforcer加delegation-aware查询 (1天工程)
# ============================================================

set -e

echo "=== Phase 1: CEO agent → OpenClaw ==="

# 1) 创建CEO agent目录
mkdir -p /Users/haotianliu/.openclaw/agents/ceo/agent
mkdir -p /Users/haotianliu/.openclaw/agents/ceo/memory
echo "[1/5] Agent目录创建完成"

# 2) 写IDENTITY.md（强制身份header + 完整ceo.md persona）
cat > /Users/haotianliu/.openclaw/agents/ceo/agent/IDENTITY.md <<'EOF'
# IDENTITY (强制每response应用)
- 姓名：Aiden（中文：承远）
- 角色：Y* Bridge Labs CEO
- **称呼Board方式：必须叫"老大"**（不允许Board / 老板 / 直呼）
- 公司：Y* Bridge Labs，做Y*gov多agent runtime governance产品
- 当前战役：Y*Defuse 30天 10K用户+20K stars
- 边界：不直接写代码，工程任务dispatch via CTO
- 硬约束：不出选择题、verification before assertion、12层认知建构、根源解决问题

---
EOF

cat "/Users/haotianliu/.openclaw/workspace/ystar-company/.claude/agents/ceo.md" \
    >> /Users/haotianliu/.openclaw/agents/ceo/agent/IDENTITY.md
echo "[2/5] IDENTITY.md写入完成 ($(wc -l < /Users/haotianliu/.openclaw/agents/ceo/agent/IDENTITY.md)行)"

# 3) 备份 + 更新 openclaw.json maxConcurrent 4→6
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.phase1
python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home() / ".openclaw/openclaw.json"
c = json.loads(p.read_text())
c.setdefault("agents", {}).setdefault("defaults", {})["maxConcurrent"] = 6
p.write_text(json.dumps(c, indent=2))
print("[3/5] openclaw.json: maxConcurrent → 6 (备份在 ~/.openclaw/openclaw.json.bak.phase1)")
PY

# 4) 注册CEO agent（先试Claude Opus，失败则降级MiniMax）
echo "[4/5] 注册CEO agent..."
if openclaw agents add ceo \
    --workspace /Users/haotianliu/.openclaw/workspace/ystar-company \
    --agent-dir /Users/haotianliu/.openclaw/agents/ceo/agent \
    --model anthropic/claude-opus-4.6 \
    --non-interactive 2>/dev/null; then
    echo "  model=anthropic/claude-opus-4.6 注册成功"
else
    echo "  Claude Opus失败，降级MiniMax (老大原话: '宁可用MiniMax 2.7')"
    openclaw agents add ceo \
        --workspace /Users/haotianliu/.openclaw/workspace/ystar-company \
        --agent-dir /Users/haotianliu/.openclaw/agents/ceo/agent \
        --model minimax/MiniMax-M2.5 \
        --non-interactive
    echo "  model=minimax/MiniMax-M2.5 注册成功"
fi

# 5) 端到端验证
echo "[5/5] 验证CEO agent身份..."
echo "=== 测试问题：'你是谁？老大问你今天的任务' ==="
openclaw agent --agent ceo --local --message "你是谁？老大问你今天的任务" --json

echo ""
echo "============================================================"
echo "  Phase 1 完成。老大验证要点:"
echo "  1. 上面JSON回复里自称 Aiden/承远"
echo "  2. 称呼老大（不是Board/老板）"
echo "  3. 提到Y*Defuse战役"
echo "  4. 角色是CEO，边界清晰（不直接写代码）"
echo "  "
echo "  都对 = Phase 1成功，一个常驻不失忆的Aiden已就位"
echo "  任何不对 = 不是Phase 1失败，是IDENTITY.md没被model正确加载"
echo "           → dispatch给Leo/Ryan排查agent model prompt injection"
echo "============================================================"
