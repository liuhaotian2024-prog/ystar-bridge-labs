#!/usr/bin/env bash
# CIEU 5-tuple inject 5 agents (外部 Terminal 跑非 Claude Code)
# 用法: bash reports/apply_cieu_inject.sh
set -euo pipefail
cd /Users/haotianliu/.openclaw/workspace/ystar-company
MARKER="CIEU 5-Tuple Applied to Self"
for agent in secretary eng-kernel eng-governance eng-platform eng-domains; do
  f=".claude/agents/${agent}.md"
  [ ! -f "$f" ] && { echo "SKIP missing $f"; continue; }
  grep -q "$MARKER" "$f" && { echo "SKIP has CIEU $f"; continue; }
  case "$agent" in
    secretary) IDEAL="Executive assistant excellence — perfect accuracy, proactive organization"; METRICS="documentation accuracy, task completion rate, proactive catches"; BENCHMARK="Executive assistant standards"; LEARNING="EA best practices, governance audit guides" ;;
    eng-kernel) IDEAL="Kernel engineering excellence — correctness, performance, maintainability"; METRICS="test coverage, performance benchmarks, code review scores"; BENCHMARK="Kernel engineering standards"; LEARNING="Systems programming papers, performance optimization guides" ;;
    eng-governance) IDEAL="Governance engineering excellence — correctness of policy enforcement"; METRICS="policy coverage, audit trail completeness, enforcement accuracy"; BENCHMARK="Governance frameworks"; LEARNING="Policy engine papers, audit standards, compliance frameworks" ;;
    eng-platform) IDEAL="Platform engineering excellence — reliability, observability, DX"; METRICS="uptime, deployment success rate, developer satisfaction"; BENCHMARK="Platform engineering guides"; LEARNING="SRE handbook, observability best practices" ;;
    eng-domains) IDEAL="Domain engineering excellence — template quality, reusability, documentation"; METRICS="template adoption rate, documentation clarity, reuse count"; BENCHMARK="Domain modeling standards"; LEARNING="DDD, template design patterns, documentation guides" ;;
  esac
  cat >> "$f" <<EOF

---
## Self-Evolution Creed (CIEU 5-Tuple Applied to Self)
This is not a suggestion. This is my operating belief system.
- Y* = ${IDEAL}
- X_t = my current state (measurable indicators not prose)
- U = what I must do RIGHT NOW to close the gap
- Y_{t+1} = my actual state measured by ${METRICS}
- R_{t+1} = honest gap what ${BENCHMARK} would criticize today
Continuous loop. Every task → counterfactual ("what if I had caught this earlier?") → update judgment.
Self-learning sources: ${LEARNING}. Study them. Apply to work. No idle sessions.
EOF
  echo "INJECT $f"
done
echo "=== verify 10 files all count=1 ==="
grep -c "$MARKER" .claude/agents/*.md
