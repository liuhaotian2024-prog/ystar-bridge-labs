#!/usr/bin/env python3
"""
K9 Rescue Daemon — Physically isolated emergency rescue service.

Runs under launchd (com.ystar.k9rescue), completely independent of the
Y*gov governance layer. Listens on a FIFO pipe for rescue action requests
from agents that may be trapped in governance lock-death.

Design principles (Board INC-2026-04-23):
1. Physical isolation: launchd independent service
2. Zero governance dependency: NO import from ystar.*
3. Whitelist-driven: only hardcoded action IDs accepted (R-001..R-007)
4. FIFO single-direction: agent writes to FIFO, daemon reads
5. Auditable: independent Merkle audit chain log

Protocol:
  Agent writes to /tmp/ystar_rescue_fifo:
    ACTION_ID [ARG]\n
  e.g.:
    R-001\n
    R-007 12345\n

  Daemon reads, validates against whitelist, executes, logs to Merkle chain.
"""

import os
import sys
import json
import time
import hashlib
import signal
import errno

# ---- ZERO ystar.* imports ---- #
# Import only from the co-located actions module (same directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k9_rescue_actions import execute_action, ACTION_REGISTRY

FIFO_PATH = "/tmp/ystar_rescue_fifo"
AUDIT_LOG = "/tmp/ystar_k9_rescue_audit.jsonl"
PID_FILE = "/tmp/ystar_k9_rescue.pid"

# Merkle chain state
_prev_hash = "0" * 64  # Genesis block


def _merkle_hash(prev, record_json):
    """Compute SHA-256 hash chaining previous hash with current record."""
    data = f"{prev}|{record_json}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _audit_log(record):
    """Append record to audit log with Merkle chain hash."""
    global _prev_hash
    record["prev_hash"] = _prev_hash
    record_json = json.dumps(record, sort_keys=True)
    record["hash"] = _merkle_hash(_prev_hash, record_json)
    _prev_hash = record["hash"]
    try:
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        sys.stderr.write(f"[K9-RESCUE] Audit log write failed: {e}\n")


def _load_chain_state():
    """Load the last hash from existing audit log to resume the chain."""
    global _prev_hash
    if not os.path.exists(AUDIT_LOG):
        return
    try:
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            last_line = None
            for line in f:
                line = line.strip()
                if line:
                    last_line = line
            if last_line:
                entry = json.loads(last_line)
                _prev_hash = entry.get("hash", _prev_hash)
    except Exception:
        pass  # Fresh chain on any error


def _ensure_fifo():
    """Create FIFO pipe if it doesn't exist."""
    if os.path.exists(FIFO_PATH):
        if not _is_fifo(FIFO_PATH):
            # Not a FIFO — remove and recreate
            os.remove(FIFO_PATH)
        else:
            return
    os.mkfifo(FIFO_PATH, mode=0o622)


def _is_fifo(path):
    """Check if path is a FIFO."""
    import stat
    try:
        return stat.S_ISFIFO(os.stat(path).st_mode)
    except OSError:
        return False


def _write_pid():
    """Write PID file for daemon management."""
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


def _cleanup(signum=None, frame=None):
    """Clean shutdown: remove PID file, log shutdown."""
    _audit_log({
        "ts": time.time(),
        "event": "DAEMON_SHUTDOWN",
        "signal": signum,
        "pid": os.getpid(),
    })
    try:
        os.remove(PID_FILE)
    except FileNotFoundError:
        pass
    sys.exit(0)


def _parse_request(line):
    """
    Parse a rescue request line.
    Format: ACTION_ID [ARG]
    Returns (action_id, arg_or_none).
    """
    parts = line.strip().split(None, 1)
    if not parts:
        return None, None
    action_id = parts[0].upper()
    arg = parts[1].strip() if len(parts) > 1 else None
    return action_id, arg


def run_daemon():
    """Main daemon loop: listen on FIFO, process rescue requests."""
    _load_chain_state()
    _ensure_fifo()
    _write_pid()

    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGTERM, _cleanup)
    signal.signal(signal.SIGINT, _cleanup)

    _audit_log({
        "ts": time.time(),
        "event": "DAEMON_START",
        "pid": os.getpid(),
        "fifo": FIFO_PATH,
        "whitelist": list(ACTION_REGISTRY.keys()),
    })

    sys.stderr.write(f"[K9-RESCUE] Daemon started (pid={os.getpid()}, fifo={FIFO_PATH})\n")

    while True:
        try:
            # Open FIFO for reading (blocks until a writer connects)
            with open(FIFO_PATH, "r") as fifo:
                for line in fifo:
                    line = line.strip()
                    if not line:
                        continue

                    ts = time.time()
                    action_id, arg = _parse_request(line)

                    if action_id is None:
                        _audit_log({
                            "ts": ts,
                            "event": "INVALID_REQUEST",
                            "raw": line[:200],
                        })
                        continue

                    # Execute the whitelisted action
                    result = execute_action(action_id, arg)

                    # Audit log with Merkle chain
                    _audit_log({
                        "ts": ts,
                        "event": "ACTION_EXECUTED",
                        "action_id": action_id,
                        "arg": arg,
                        "result": result,
                    })

                    sys.stderr.write(
                        f"[K9-RESCUE] {action_id} ok={result.get('ok')} "
                        f"ts={time.strftime('%H:%M:%S', time.localtime(ts))}\n"
                    )

        except IOError as e:
            if e.errno == errno.EINTR:
                continue  # Interrupted by signal, retry
            sys.stderr.write(f"[K9-RESCUE] FIFO read error: {e}\n")
            time.sleep(1)
        except Exception as e:
            sys.stderr.write(f"[K9-RESCUE] Unexpected error: {e}\n")
            _audit_log({
                "ts": time.time(),
                "event": "ERROR",
                "error": str(e),
            })
            time.sleep(1)


def send_rescue(action_id, arg=None):
    """
    Convenience function: send a rescue request to the daemon via FIFO.
    Can be called from any agent context (including locked-out agents).
    """
    msg = action_id
    if arg is not None:
        msg = f"{action_id} {arg}"
    msg += "\n"

    if not os.path.exists(FIFO_PATH):
        return {"ok": False, "error": f"FIFO {FIFO_PATH} does not exist. Is k9_rescue_daemon running?"}

    try:
        fd = os.open(FIFO_PATH, os.O_WRONLY | os.O_NONBLOCK)
        os.write(fd, msg.encode("utf-8"))
        os.close(fd)
        return {"ok": True, "sent": msg.strip()}
    except OSError as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "send":
        # CLI mode: send a rescue request
        if len(sys.argv) < 3:
            print("Usage: k9_rescue_daemon.py send ACTION_ID [ARG]")
            sys.exit(1)
        aid = sys.argv[2]
        a = sys.argv[3] if len(sys.argv) > 3 else None
        result = send_rescue(aid, a)
        print(json.dumps(result))
    else:
        run_daemon()
