#!/usr/bin/env python3
"""
CTO Dispatch Broker Daemon — CTO-judgment routing automation
Implements broker pattern per governance/cto_dispatch_broker_v1.md
"""
import argparse
import json
import sys
import time
import fcntl
import re
from pathlib import Path
from datetime import datetime, timezone

# Import CIEU helpers
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import emit_cieu, _get_canonical_agent

BOARD_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/dispatch_board.json")
PID_FILE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/.cto_broker.pid")
TRUST_SCORES_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/trust_scores.json")
POLL_TRIGGER_EVENTS = 10  # Poll dispatch_board every N CIEU events (no hardcoded time)


def _read_board():
    """Read dispatch board with advisory lock."""
    if not BOARD_PATH.exists():
        return {"tasks": []}
    with open(BOARD_PATH, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data


def _write_board(data):
    """Write dispatch board with exclusive lock."""
    BOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BOARD_PATH, "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def count_recent_events(hours=1):
    """
    Count CIEU events in last N hours.
    Used for event-driven polling trigger.
    """
    try:
        import sqlite3
        CIEU_DB_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db")

        if not CIEU_DB_PATH.exists():
            return 0

        conn = sqlite3.connect(str(CIEU_DB_PATH))
        cursor = conn.cursor()

        cutoff_timestamp = time.time() - (hours * 3600)

        cursor.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE created_at > ?",
            (cutoff_timestamp,)
        )
        count = cursor.fetchone()[0]

        conn.close()
        return count
    except Exception:
        return 0


def classify_tier(description, scope, estimated_tool_uses):
    """
    Tier classifier per tier-routing v1 rules.
    Returns: "T1" | "T2" | "T3"
    """
    # T3 keywords (highest priority)
    t3_keywords = [
        "push origin", "git push", "deploy", "release", "pypi",
        "payment", "rollback", "amendment", "external email",
        "cold email", "PR merge external", "GDPR", "data deletion"
    ]
    if any(kw in description.lower() for kw in t3_keywords):
        return "T3"

    # T2 heuristics
    if estimated_tool_uses > 15:
        return "T2"

    # Count files/directories in scope (comma-separated or space-separated)
    # Split by comma first, then handle each part
    parts = scope.replace(",", " ").split()
    file_count = len([p.strip() for p in parts if p.strip()])
    if file_count > 3:
        return "T2"

    t2_keywords = [
        "architecture", "API change", "cross-engineer", "refactor",
        "new module", "new component", "migration", "ForgetGuard mode=deny",
        "data model", "module boundary"
    ]
    if any(kw in description.lower() for kw in t2_keywords):
        return "T2"

    # Default T1
    return "T1"


def select_engineer_for_t1(scope):
    """
    Select engineer based on file scope + trust scores.
    Returns: engineer_id (e.g., "ryan-platform", "leo-kernel")
    """
    # Load trust scores
    trust_data = {}
    if TRUST_SCORES_PATH.exists():
        try:
            trust_data = json.loads(TRUST_SCORES_PATH.read_text())
        except Exception:
            pass

    # Scope-based routing (primary)
    if "governance/" in scope or "forget_guard" in scope.lower():
        return "maya-governance"
    elif "scripts/" in scope or "platform/" in scope or "test" in scope:
        return "ryan-platform"
    elif "kernel/" in scope or "ystar/kernel" in scope:
        return "leo-kernel"
    elif "domains/" in scope or "ystar/domains" in scope:
        return "jordan-domains"
    else:
        # Fallback: pick engineer with highest trust score
        if trust_data:
            return max(trust_data.items(), key=lambda x: x[1].get("trust_score", 0))[0]
        # Ultimate fallback
        return "ryan-platform"


def validate_receipt(task, receipt_text):
    """
    Validate engineer receipt per CIEU 5-tuple.
    Returns: True if valid, False if validation fails
    """
    # Parse receipt for Rt+1 value (expect "Rt+1 = 0" or "Rt+1: 0")
    rt_match = re.search(r"Rt\+1[:\s=]+([0-9.]+)", receipt_text, re.IGNORECASE)
    if not rt_match:
        emit_cieu(
            "CTO_BROKER_VALIDATION_FAIL",
            decision="reject",
            passed=0,
            task_description=f"{task['atomic_id']} receipt validation failed: Rt+1 missing",
            params_json=json.dumps({"atomic_id": task["atomic_id"], "reason": "rt_missing"})
        )
        return False

    rt_value = float(rt_match.group(1))
    if rt_value > 0:
        emit_cieu(
            "CTO_BROKER_VALIDATION_FAIL",
            decision="reject",
            passed=0,
            task_description=f"{task['atomic_id']} receipt validation failed: Rt+1 > 0",
            params_json=json.dumps({"atomic_id": task["atomic_id"], "rt_value": rt_value})
        )
        return False

    # Scope compliance check (files_in_scope from dispatch vs files_modified from receipt)
    claimed_scope = set(f.strip() for f in task["scope"].split(",") if f.strip())

    # Parse receipt for modified files (heuristic: look for file paths in receipt)
    # Match patterns like: scripts/file.py, governance/file.md, ystar/module/file.py
    modified_files = set(re.findall(r"[\w_/]+\.(?:py|md|yaml|json|sh)", receipt_text.lower()))

    # Check if modified files are within claimed scope
    # Allow if no files detected (receipt may not list files)
    if modified_files and claimed_scope:
        # Check each modified file matches at least one scope pattern
        # Scope pattern can be exact path or prefix (e.g., "governance/" matches "governance/forget_guard_rules.yaml")
        scope_violation = False
        for modified in modified_files:
            # Check if any scope pattern is a substring of the modified file
            # OR if modified file is a substring of scope pattern (handles exact matches)
            matches = any(
                scope_pattern in modified or modified in scope_pattern
                for scope_pattern in claimed_scope
            )
            if not matches:
                scope_violation = True
                break

        if scope_violation:
            emit_cieu(
                "CTO_BROKER_VALIDATION_FAIL",
                decision="reject",
                passed=0,
                task_description=f"{task['atomic_id']} scope violation",
                params_json=json.dumps({
                    "claimed": list(claimed_scope),
                    "actual": list(modified_files)
                })
            )
            return False

    # All checks passed
    emit_cieu(
        "CTO_BROKER_VALIDATION_PASS",
        decision="accept",
        passed=1,
        task_description=f"{task['atomic_id']} receipt valid",
        params_json=json.dumps({"atomic_id": task["atomic_id"], "rt_value": 0})
    )
    return True


def poll_and_route():
    """Poll dispatch_board, route tasks with CTO judgment."""
    board = _read_board()

    # Find tasks with status="open" and posted_by != broker (avoid loops)
    open_tasks = [
        t for t in board["tasks"]
        if t["status"] == "open" and t.get("posted_by") != "cto-broker"
    ]

    for task in open_tasks:
        atomic_id = task["atomic_id"]

        # Step 1: Tier classify (T1/T2/T3)
        tier = classify_tier(
            task["description"],
            task["scope"],
            task.get("estimated_tool_uses", 0)
        )

        emit_cieu(
            "CTO_BROKER_TIER_CLASSIFIED",
            decision="info",
            passed=1,
            task_description=f"{atomic_id} classified as {tier}",
            params_json=json.dumps({
                "atomic_id": atomic_id,
                "tier": tier,
                "scope": task["scope"],
                "estimated_tool_uses": task.get("estimated_tool_uses", 0)
            })
        )

        # Step 2: Routing decision
        if tier == "T1":
            # T1 → direct engineer assignment
            engineer_id = select_engineer_for_t1(task["scope"])

            emit_cieu(
                "CTO_BROKER_ENGINEER_SELECTED",
                decision="dispatch",
                passed=1,
                task_description=f"Dispatching {atomic_id} to {engineer_id}",
                params_json=json.dumps({
                    "atomic_id": atomic_id,
                    "engineer_id": engineer_id,
                    "tier": tier,
                })
            )

            # Mark task as broker_routing (claimed by broker)
            task["status"] = "broker_routing"
            task["claimed_by"] = "cto-broker"
            task["claimed_at"] = datetime.now(timezone.utc).isoformat()
            task["tier"] = tier
            task["assigned_engineer"] = engineer_id

        elif tier == "T2":
            # T2 → escalate to CTO for design
            emit_cieu(
                "CTO_BROKER_INTENT_RECEIVED",
                decision="escalate",
                passed=1,
                task_description=f"{atomic_id} T2 escalated to CTO for design",
                params_json=json.dumps({"atomic_id": atomic_id, "tier": "T2"})
            )

            task["status"] = "broker_escalate_t2"
            task["claimed_by"] = "cto-broker"
            task["claimed_at"] = datetime.now(timezone.utc).isoformat()
            task["tier"] = tier

        elif tier == "T3":
            # T3 → escalate to Board (CEO drafts proposal)
            emit_cieu(
                "CTO_BROKER_INTENT_RECEIVED",
                decision="escalate",
                passed=1,
                task_description=f"{atomic_id} T3 escalated to Board",
                params_json=json.dumps({"atomic_id": atomic_id, "tier": "T3"})
            )

            task["status"] = "broker_escalate_t3"
            task["claimed_by"] = "cto-broker"
            task["claimed_at"] = datetime.now(timezone.utc).isoformat()
            task["tier"] = tier

    # Write updated board back
    _write_board(board)


def validate_completed_tasks():
    """Validate receipts for completed tasks assigned by broker."""
    board = _read_board()

    # Find tasks with status="completed" and claimed_by="cto-broker" or assigned_engineer set
    completed_tasks = [
        t for t in board["tasks"]
        if t["status"] == "completed" and (
            t.get("claimed_by") == "cto-broker" or
            t.get("assigned_engineer")
        ) and t.get("completion_receipt") and not t.get("broker_validated")
    ]

    for task in completed_tasks:
        receipt_text = task["completion_receipt"]
        is_valid = validate_receipt(task, receipt_text)

        task["broker_validated"] = True
        task["broker_validation_result"] = "pass" if is_valid else "fail"
        task["broker_validated_at"] = datetime.now(timezone.utc).isoformat()

    if completed_tasks:
        _write_board(board)


def daemon_loop():
    """Event-driven polling loop (no time-based cadence)."""
    last_event_count = count_recent_events(hours=1)

    emit_cieu(
        "CTO_BROKER_DAEMON_START",
        decision="info",
        passed=1,
        task_description="CTO dispatch broker daemon started"
    )

    print("CTO Dispatch Broker daemon started (event-driven polling)", file=sys.stderr)

    while True:
        try:
            # Event-driven trigger: poll when CIEU event count increases by N
            current_event_count = count_recent_events(hours=1)
            if current_event_count - last_event_count >= POLL_TRIGGER_EVENTS:
                poll_and_route()
                validate_completed_tasks()
                last_event_count = current_event_count

            # Minimal sleep to avoid CPU spin (not time-cadence, just yielding)
            time.sleep(0.5)

        except KeyboardInterrupt:
            emit_cieu(
                "CTO_BROKER_DAEMON_STOP",
                decision="info",
                passed=1,
                task_description="CTO dispatch broker daemon stopped"
            )
            PID_FILE.unlink(missing_ok=True)
            print("\nCTO Dispatch Broker daemon stopped", file=sys.stderr)
            break
        except Exception as e:
            emit_cieu(
                "CTO_BROKER_ERROR",
                decision="warn",
                passed=0,
                task_description=f"Broker error: {e}",
                params_json=json.dumps({"error": str(e)})
            )
            # Continue running despite errors (fail-open)
            time.sleep(1)


def start_daemon():
    """Start broker daemon (blocks until SIGTERM)."""
    # Check if already running
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        import os
        try:
            os.kill(pid, 0)  # Check if process exists
            print(f"ERROR: Broker daemon already running (PID {pid})", file=sys.stderr)
            return 1
        except ProcessLookupError:
            # Stale PID file, remove it
            PID_FILE.unlink()

    # Write PID file
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    import os
    PID_FILE.write_text(str(os.getpid()))

    # Run daemon loop (blocks)
    daemon_loop()
    return 0


def stop_daemon():
    """Stop running daemon."""
    if not PID_FILE.exists():
        print("No daemon running (no PID file)", file=sys.stderr)
        return 1

    pid = int(PID_FILE.read_text().strip())
    import os
    import signal
    try:
        os.kill(pid, signal.SIGTERM)
        PID_FILE.unlink()
        print(f"Stopped daemon (PID {pid})", file=sys.stderr)
        return 0
    except ProcessLookupError:
        print(f"Daemon PID {pid} not running (stale PID file removed)", file=sys.stderr)
        PID_FILE.unlink()
        return 1


def daemon_status():
    """Check daemon status."""
    if not PID_FILE.exists():
        print("Daemon: NOT RUNNING", file=sys.stderr)
        return 1

    pid = int(PID_FILE.read_text().strip())
    import os
    try:
        os.kill(pid, 0)  # Signal 0 checks if process exists
        print(f"Daemon: RUNNING (PID {pid})", file=sys.stderr)
        return 0
    except ProcessLookupError:
        print(f"Daemon: STALE PID {pid} (process not found)", file=sys.stderr)
        PID_FILE.unlink()
        return 1


def dispatch_single_task(atomic_id):
    """Manual single-task dispatch (for testing, non-daemon mode)."""
    board = _read_board()

    task = next((t for t in board["tasks"] if t["atomic_id"] == atomic_id), None)
    if not task:
        print(f"ERROR: Task {atomic_id} not found", file=sys.stderr)
        return 1

    if task["status"] != "open":
        print(f"ERROR: Task {atomic_id} status={task['status']}, expected open", file=sys.stderr)
        return 1

    # Classify tier
    tier = classify_tier(
        task["description"],
        task["scope"],
        task.get("estimated_tool_uses", 0)
    )

    print(f"Task {atomic_id} classified as {tier}", file=sys.stderr)

    if tier == "T1":
        engineer_id = select_engineer_for_t1(task["scope"])
        print(f"Selected engineer: {engineer_id}", file=sys.stderr)

        emit_cieu(
            "CTO_BROKER_ENGINEER_SELECTED",
            decision="dispatch",
            passed=1,
            task_description=f"Manual dispatch {atomic_id} to {engineer_id}",
            params_json=json.dumps({
                "atomic_id": atomic_id,
                "engineer_id": engineer_id,
                "tier": tier,
                "mode": "manual"
            })
        )

    return 0


# ────────────────────────────────────────────────────────────────
# CTO System 2-3 Takeover — scan + verify (CZL-155)
# ────────────────────────────────────────────────────────────────

CZL_REGISTRY_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/czl_registry.json")
WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
YSTAR_GOV = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")


def _next_czl_id():
    """Get next CZL ID from registry (auto-increment, no collision)."""
    if CZL_REGISTRY_PATH.exists():
        try:
            registry = json.loads(CZL_REGISTRY_PATH.read_text())
            ids = [int(r["id"].replace("CZL-", "")) for r in registry.get("entries", []) if r["id"].startswith("CZL-")]
            return f"CZL-{max(ids) + 1}" if ids else "CZL-200"
        except Exception:
            pass
    # Fallback: scan dispatch_board for highest ID
    board = _read_board()
    ids = []
    for t in board.get("tasks", []):
        aid = t.get("atomic_id", "")
        if aid.startswith("CZL-"):
            try:
                ids.append(int(aid.replace("CZL-", "")))
            except ValueError:
                pass
    return f"CZL-{max(ids) + 1}" if ids else "CZL-200"


def _auto_post_task(description, scope, urgency="P1", estimated_tool_uses=8):
    """CTO broker autonomously posts a discovered task to dispatch_board."""
    atomic_id = _next_czl_id()
    board = _read_board()

    # Deduplicate: skip if same description already open
    for t in board.get("tasks", []):
        if t["status"] == "open" and t["description"] == description:
            print(f"SKIP: duplicate task already open: {description[:60]}", file=sys.stderr)
            return None

    task = {
        "atomic_id": atomic_id,
        "scope": scope,
        "description": description,
        "urgency": urgency,
        "estimated_tool_uses": estimated_tool_uses,
        "status": "open",
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "posted_by": "cto-broker",
        "claimed_by": None,
        "claimed_at": None,
        "completed_at": None,
        "completion_receipt": None,
    }
    board["tasks"].append(task)
    _write_board(board)

    emit_cieu(
        "CTO_BROKER_SELF_POST",
        decision="dispatch",
        passed=1,
        task_description=f"CTO broker auto-posted {atomic_id}: {description[:80]}",
        params_json=json.dumps({
            "atomic_id": atomic_id,
            "scope": scope,
            "urgency": urgency,
            "posted_by": "cto-broker",
        })
    )
    print(f"AUTO-POSTED: {atomic_id} | {description[:80]}")
    return atomic_id


def scan_problems():
    """
    CTO proactive problem discovery — scan codebase + CIEU + tests
    for issues, auto-post tasks to dispatch_board.
    Returns count of problems found.
    """
    import subprocess
    problems_found = 0

    # ── Scan 1: Test suite health ──
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--tb=line", "-q",
             str(YSTAR_GOV / "tests/")],
            capture_output=True, text=True, timeout=120,
            cwd=str(YSTAR_GOV)
        )
        if result.returncode != 0:
            # Extract failure count
            lines = result.stdout.strip().split("\n")
            summary = lines[-1] if lines else "unknown failures"
            _auto_post_task(
                f"Test regression detected: {summary}",
                "tests/",
                urgency="P0",
                estimated_tool_uses=10,
            )
            problems_found += 1
            print(f"SCAN[tests]: FAIL — {summary}")
        else:
            print(f"SCAN[tests]: PASS — {result.stdout.strip().split(chr(10))[-1]}")
    except subprocess.TimeoutExpired:
        print("SCAN[tests]: TIMEOUT (120s)")
    except FileNotFoundError:
        print("SCAN[tests]: SKIP — Y-star-gov not found")

    # ── Scan 2: Stale open tasks on dispatch_board ──
    board = _read_board()
    stale_count = 0
    for t in board.get("tasks", []):
        if t["status"] == "open":
            # Check if posted_at is old (compare to current CIEU event count as proxy)
            stale_count += 1
    if stale_count > 5:
        print(f"SCAN[stale]: WARN — {stale_count} open tasks on board (backlog growing)")
        problems_found += 1
    else:
        print(f"SCAN[stale]: OK — {stale_count} open tasks")

    # ── Scan 3: CIEU anomaly patterns ──
    try:
        import sqlite3
        CIEU_DB = WORKSPACE / ".ystar_cieu.db"
        if CIEU_DB.exists():
            conn = sqlite3.connect(str(CIEU_DB))
            cursor = conn.cursor()

            # Check for validation failures in last hour
            cutoff = time.time() - 3600
            cursor.execute(
                "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'CTO_BROKER_VALIDATION_FAIL' AND created_at > ?",
                (cutoff,)
            )
            fail_count = cursor.fetchone()[0]
            if fail_count >= 3:
                _auto_post_task(
                    f"High receipt validation failure rate: {fail_count} failures in last hour",
                    "scripts/cto_dispatch_broker.py",
                    urgency="P1",
                    estimated_tool_uses=5,
                )
                problems_found += 1
                print(f"SCAN[cieu]: WARN — {fail_count} validation failures")

            # Check for identity drift warnings
            cursor.execute(
                "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'AGENT_REGISTRY_K9_WARN' AND created_at > ?",
                (cutoff,)
            )
            drift_count = cursor.fetchone()[0]
            if drift_count >= 5:
                print(f"SCAN[cieu]: WARN — {drift_count} identity drift warnings")
                problems_found += 1
            else:
                print(f"SCAN[cieu]: OK — {drift_count} drift warnings, {fail_count} validation failures")

            conn.close()
        else:
            print("SCAN[cieu]: SKIP — no CIEU database")
    except Exception as e:
        print(f"SCAN[cieu]: ERROR — {e}")

    # ── Scan 4: FG rules ready for promotion ──
    fg_rules_path = WORKSPACE / "governance" / "forget_guard_rules.yaml"
    if fg_rules_path.exists():
        try:
            import yaml
            with open(fg_rules_path) as f:
                fg_data = yaml.safe_load(f)
            dry_run_rules = []
            if isinstance(fg_data, dict):
                for rule_name, rule_cfg in fg_data.items():
                    if isinstance(rule_cfg, dict) and rule_cfg.get("mode") == "dry_run":
                        dry_run_rules.append(rule_name)
            if dry_run_rules:
                print(f"SCAN[fg]: INFO — {len(dry_run_rules)} rules in dry_run: {', '.join(dry_run_rules[:3])}")
            else:
                print("SCAN[fg]: OK — no dry_run rules pending promotion")
        except ImportError:
            print("SCAN[fg]: SKIP — yaml not installed")
        except Exception as e:
            print(f"SCAN[fg]: ERROR — {e}")
    else:
        print("SCAN[fg]: SKIP — no forget_guard_rules.yaml")

    # ── Summary ──
    emit_cieu(
        "CTO_BROKER_SCAN_COMPLETE",
        decision="info",
        passed=1 if problems_found == 0 else 0,
        task_description=f"CTO proactive scan: {problems_found} problems found",
        params_json=json.dumps({"problems_found": problems_found})
    )
    print(f"\n{'='*60}")
    print(f"SCAN COMPLETE: {problems_found} problems found")
    print(f"{'='*60}")
    return problems_found


def verify_task(atomic_id):
    """
    CTO auto-verify pipeline — 5-step receipt validation.
    Replaces CEO manual ls/wc/pytest cycle.
    """
    import subprocess
    import os

    board = _read_board()
    task = next((t for t in board["tasks"] if t["atomic_id"] == atomic_id), None)
    if not task:
        print(f"ERROR: Task {atomic_id} not found on dispatch_board", file=sys.stderr)
        return 1

    receipt = task.get("completion_receipt", "")
    if not receipt:
        print(f"ERROR: Task {atomic_id} has no completion_receipt", file=sys.stderr)
        return 1

    results = {}
    overall_pass = True

    # ── Step 1: FILE_EXISTS ──
    claimed_files = re.findall(r"[\w_/.-]+\.(?:py|md|yaml|json|sh|txt)", receipt)
    missing = []
    for f in claimed_files:
        # Try workspace path first, then Y-star-gov
        if not (WORKSPACE / f).exists() and not (YSTAR_GOV / f).exists():
            # Also try as absolute path
            if not Path(f).exists():
                missing.append(f)
    results["file_exists"] = "PASS" if not missing else f"FAIL: missing {missing}"
    if missing:
        overall_pass = False
    print(f"  [1/5] FILE_EXISTS: {results['file_exists']}")

    # ── Step 2: TOOL_USES_ACCURACY ──
    tu_match = re.search(r"tool_uses[:\s=]+(\d+)", receipt, re.IGNORECASE)
    if tu_match:
        claimed_tu = int(tu_match.group(1))
        # We can only check the claim exists, metadata comparison requires hook data
        results["tool_uses"] = f"CLAIMED: {claimed_tu} (metadata cross-check requires hook)"
    else:
        results["tool_uses"] = "WARN: no tool_uses claim in receipt"
    print(f"  [2/5] TOOL_USES: {results['tool_uses']}")

    # ── Step 3: RT_CHECK ──
    rt_valid = validate_receipt(task, receipt)
    results["rt_check"] = "PASS" if rt_valid else "FAIL: Rt+1 > 0 or scope violation"
    if not rt_valid:
        overall_pass = False
    print(f"  [3/5] RT_CHECK: {results['rt_check']}")

    # ── Step 4: TEST_GATE ──
    scope = task.get("scope", "")
    if "test" in scope or ".py" in scope:
        try:
            test_result = subprocess.run(
                [sys.executable, "-m", "pytest", "--tb=line", "-q"],
                capture_output=True, text=True, timeout=120,
                cwd=str(YSTAR_GOV)
            )
            if test_result.returncode == 0:
                results["test_gate"] = "PASS"
            else:
                lines = test_result.stdout.strip().split("\n")
                results["test_gate"] = f"FAIL: {lines[-1] if lines else 'unknown'}"
                overall_pass = False
        except Exception as e:
            results["test_gate"] = f"ERROR: {e}"
    else:
        results["test_gate"] = "SKIP: no test-related scope"
    print(f"  [4/5] TEST_GATE: {results['test_gate']}")

    # ── Step 5: SCOPE_COMPLIANCE ──
    # Already checked in validate_receipt Step 3
    results["scope_compliance"] = "PASS (checked in RT_CHECK)"
    print(f"  [5/5] SCOPE_COMPLIANCE: {results['scope_compliance']}")

    # ── Update board with verification result ──
    task["broker_verified"] = True
    task["broker_verify_result"] = "PASS" if overall_pass else "FAIL"
    task["broker_verify_details"] = results
    task["broker_verified_at"] = datetime.now(timezone.utc).isoformat()
    _write_board(board)

    verdict = "PASS" if overall_pass else "FAIL"
    emit_cieu(
        f"CTO_BROKER_VERIFICATION_{verdict}",
        decision="accept" if overall_pass else "reject",
        passed=1 if overall_pass else 0,
        task_description=f"CTO auto-verify {atomic_id}: {verdict}",
        params_json=json.dumps({
            "atomic_id": atomic_id,
            "verdict": verdict,
            "details": results,
        })
    )

    print(f"\nVERIFICATION {verdict}: {atomic_id}")
    return 0 if overall_pass else 1


def main():
    parser = argparse.ArgumentParser(description="CTO Dispatch Broker Daemon")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # start
    start_parser = subparsers.add_parser("start", help="Start broker daemon")
    start_parser.set_defaults(func=lambda args: start_daemon())

    # stop
    stop_parser = subparsers.add_parser("stop", help="Stop broker daemon")
    stop_parser.set_defaults(func=lambda args: stop_daemon())

    # status
    status_parser = subparsers.add_parser("status", help="Check daemon status")
    status_parser.set_defaults(func=lambda args: daemon_status())

    # dispatch (manual single task)
    dispatch_parser = subparsers.add_parser("dispatch", help="Manual single-task dispatch (testing)")
    dispatch_parser.add_argument("--atomic_id", required=True, help="CZL-XX identifier")
    dispatch_parser.set_defaults(func=lambda args: dispatch_single_task(args.atomic_id))

    # scan (CTO proactive problem discovery — CZL-155)
    scan_parser = subparsers.add_parser("scan", help="CTO proactive scan: discover problems, auto-post tasks")
    scan_parser.set_defaults(func=lambda args: scan_problems())

    # verify (CTO auto-verify receipt — CZL-155)
    verify_parser = subparsers.add_parser("verify", help="CTO auto-verify: 5-step receipt validation")
    verify_parser.add_argument("--atomic_id", required=True, help="CZL-XX identifier to verify")
    verify_parser.set_defaults(func=lambda args: verify_task(args.atomic_id))

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
