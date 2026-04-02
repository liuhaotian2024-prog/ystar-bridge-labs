"""
Y*gov hook wrapper — OBSERVE-ONLY mode.
Records CIEU events in the same format as the full hook, but NEVER denies.
Used as the A-group control in A/B experiments.

Difference from hook_wrapper.py:
  - Runs check_hook() to compute the real decision
  - Writes CIEU record (with the real decision: allow OR deny)
  - But ALWAYS returns {} to Claude Code (= always allow)
  - Tags CIEU records with observe_only=true for later filtering
"""
import json
import sys
import os
import traceback

LOG = os.path.join(os.path.dirname(__file__), "hook_observe.log")

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        import time
        f.write(f"{time.strftime('%H:%M:%S')} [OBSERVE] {msg}\n")

try:
    raw = sys.stdin.read()
    payload = json.loads(raw)
    tool_name = payload.get('tool_name', '?')
    log(f"Tool: {tool_name}")

    agents_path = os.path.join(os.getcwd(), "AGENTS.md")

    from ystar import Policy
    from ystar.adapters.hook import check_hook

    if os.path.exists(agents_path):
        policy = Policy.from_agents_md_multi(agents_path)
    else:
        policy = Policy({})

    # Run the REAL check — this writes CIEU records internally
    result = check_hook(payload, policy)

    # Log what WOULD have happened under full governance
    if result.get("action") == "block":
        log(f"WOULD_DENY: {tool_name} — {result.get('message', '')[:100]}")
    else:
        log(f"ALLOW: {tool_name}")

    # ALWAYS return {} (allow) — this is the observe-only guarantee
    sys.stdout.write("{}")

except Exception as e:
    log(f"ERROR: {e}")
    sys.stdout.write("{}")
