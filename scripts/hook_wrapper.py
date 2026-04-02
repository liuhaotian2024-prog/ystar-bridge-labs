"""
Y*gov hook wrapper — captures ALL errors to a log file.
This replaces the inline -c command to diagnose silent failures.

Performance optimization v0.49:
- Cache Policy and session config (60s TTL)
- Skip debug CIEU count checks in production
- Remove monkey-patch instrumentation
"""
import json
import sys
import os
import traceback
import time
import hashlib

LOG = os.path.join(os.path.dirname(__file__), "hook_debug.log")
_CACHE_FILE = os.path.join(os.path.dirname(__file__), ".hook_cache.json")
_CACHE_TTL = 60  # 60 seconds cache TTL

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

def _get_file_hash(path):
    """Fast hash of file modification time + size."""
    try:
        stat = os.stat(path)
        return hashlib.md5(f"{stat.st_mtime}:{stat.st_size}".encode()).hexdigest()
    except Exception:
        return ""

def _load_cache():
    """Load policy cache if valid."""
    try:
        if not os.path.exists(_CACHE_FILE):
            return None
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)

        # Check TTL
        if time.time() - cache.get("timestamp", 0) > _CACHE_TTL:
            log("Cache expired")
            return None

        # Check if AGENTS.md changed
        agents_path = os.path.join(os.getcwd(), "AGENTS.md")
        current_hash = _get_file_hash(agents_path)
        if current_hash != cache.get("agents_hash", ""):
            log("AGENTS.md changed, cache invalid")
            return None

        log(f"Cache hit (age: {int(time.time() - cache.get('timestamp', 0))}s)")
        return cache
    except Exception as e:
        log(f"Cache load failed: {e}")
        return None

def _save_cache(agents_hash, session_cfg):
    """Save policy cache."""
    try:
        cache = {
            "timestamp": time.time(),
            "agents_hash": agents_hash,
            "session_cfg": session_cfg,
        }
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f)
        log("Cache saved")
    except Exception as e:
        log(f"Cache save failed: {e}")

try:
    # ── Session Boot Check ──────────────────────────────────────────────
    # Detects if CEO has completed the mandatory boot protocol.
    # Boot flag is written by the first successful handoff read.
    # If missing after 5+ tool calls in this session, inject a reminder.
    session_id_env = os.environ.get("CLAUDE_SESSION_ID", "")
    boot_flag = os.path.join(os.path.dirname(__file__), ".session_booted")
    call_counter = os.path.join(os.path.dirname(__file__), ".session_call_count")

    # Increment call counter for this session
    try:
        count = int(open(call_counter, "r").read().strip()) if os.path.exists(call_counter) else 0
    except Exception:
        count = 0
    count += 1
    with open(call_counter, "w") as f:
        f.write(str(count))

    log(f"Hook invoked. CWD={os.getcwd()} call={count} booted={os.path.exists(boot_flag)}")

    # Read stdin
    raw = sys.stdin.read()
    log(f"Stdin: {raw[:200]}")

    payload = json.loads(raw)
    tool_name = payload.get('tool_name', '?')
    log(f"Parsed tool: {tool_name}")

    # ── FAST PATH: Read-only operations skip full governance check ──────
    # Read/Grep/Glob are low-risk and high-frequency. Running full check_hook()
    # on every Read adds 2-4 seconds of latency with zero governance value.
    # Full check only runs for Write/Edit/Bash (mutation operations).
    if tool_name in ("Read", "Grep", "Glob", "Ls", "LS"):
        log(f"FAST PATH: {tool_name} → allow (read-only)")
        sys.stdout.write("{}")
        sys.exit(0)

    # Check AGENTS.md
    agents_path = os.path.join(os.getcwd(), "AGENTS.md")
    agents_exists = os.path.exists(agents_path)

    # Import ystar (only for mutation operations)
    from ystar import Policy
    from ystar.adapters.hook import check_hook
    log("ystar imported OK")

    # ── P0 Performance: Cache Policy and session config ─────────────────
    cache = _load_cache()
    if cache:
        # Use cached session config (Policy is rebuilt each time as it's cheap)
        # The expensive part is loading+parsing session config from disk
        session_cfg_cached = cache.get("session_cfg")
        if session_cfg_cached:
            # Inject cached session config into identity_detector module
            import ystar.adapters.identity_detector as id_module
            id_module._SESSION_CONFIG_CACHE = session_cfg_cached
            log("Session config loaded from cache")

    # Build policy (always rebuild — it's fast, just dict operations)
    if agents_exists:
        policy = Policy.from_agents_md_multi(agents_path)
    else:
        policy = Policy({})
    log(f"Policy built: {policy}")

    # Save cache if needed
    if not cache:
        from ystar.adapters.identity_detector import _load_session_config
        session_cfg = _load_session_config()
        agents_hash = _get_file_hash(agents_path)
        _save_cache(agents_hash, session_cfg)

    # ── REMOVED: Debug instrumentation (monkey-patch, CIEU count checks) ──
    # These were for debugging during development, not needed in production.
    # Removed to reduce per-call overhead.

    # ── CEO Code-Write Prohibition (Constitutional) ────────────────────
    # CEO must not write to Y*gov source code. This is a governance boundary.
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    if tool in ("Write", "Edit", "NotebookEdit"):
        file_path = tool_input.get("file_path", "")
        ceo_deny = ["Y-star-gov/ystar/", "Y-star-gov\\ystar\\", "/src/ystar/"]
        for deny_pattern in ceo_deny:
            if deny_pattern in file_path:
                result = {
                    "action": "block",
                    "message": f"[Y*gov CONSTITUTIONAL] CEO禁止直接写代码。文件 {file_path} 属于CTO管辖范围。请派工程师执行。"
                }
                log(f"CEO CODE-WRITE BLOCK: {file_path}")
                sys.stdout.write(json.dumps(result))
                sys.exit(0)

    # Run check
    result = check_hook(payload, policy)
    log(f"Result: {result}")

    # ── Session Boot Enforcement (HARD BLOCK) ──────────────────────────────
    # If 5+ tool calls and boot protocol not completed, BLOCK all non-Read operations
    if count >= 5 and not os.path.exists(boot_flag):
        tool = payload.get("tool_name", "")
        # Allow Read/Grep/Glob (needed to execute boot protocol itself)
        if tool not in ("Read", "Grep", "Glob"):
            result = {
                "action": "block",
                "message": "[Y*gov CONSTITUTIONAL] SESSION BOOT NOT COMPLETED. 所有非读取操作被阻断。请立即执行boot协议：读取memory/session_handoff.md → memory/team_dna.md → 验证CIEU → 向老大汇报 → echo BOOTED > scripts/.session_booted"
            }
            log(f"BOOT HARD BLOCK at call {count}, tool={tool}")

    # Output ONLY valid JSON to stdout
    sys.stdout.write(json.dumps(result))

except Exception as e:
    log(f"FATAL ERROR: {e}")
    log(traceback.format_exc())
    # Output empty JSON so Claude Code doesn't crash
    sys.stdout.write("{}")
