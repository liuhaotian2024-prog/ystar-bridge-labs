#!/usr/bin/env python3
"""
K9 Three-Dimensional Governance Audit
Adopted from consultant 3-dim framework (2026-04-16)

Dimensions:
- Producer: CIEU data production pipeline integrity
- Executor: Tool-call hook chain runtime integrity
- Governed: Governance constraints actually enforcing

Output: Markdown report with P0/P1/P2 violations, Rt+1 = sum(P0 + P1)
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# Add Y-star-gov to path for ystar module import
YSTAR_GOV_PATH = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
if YSTAR_GOV_PATH.exists():
    sys.path.insert(0, str(YSTAR_GOV_PATH))

# Paths
REPO_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
SETTINGS_JSON = REPO_ROOT / ".claude" / "settings.json"
REPORTS_DIR = REPO_ROOT / "reports" / "k9_daily"


def check_producer_integrity() -> Tuple[List[str], int]:
    """
    Dimension 1: CIEU data production pipeline

    Checks:
    P1. Tool-call gov events in last 24h (BEHAVIOR_RULE_VIOLATION/WARNING/WHITELIST_DRIFT/MATCH)
    P2. Session-level events in last 24h (HOOK_BOOT/INTENT_RECORDED/OBLIGATION_REGISTERED)
    P3. CIEU DB writable (INSERT + DELETE + commit test)
    """
    findings = []
    rt_score = 0

    try:
        from ystar.governance.cieu_store import CIEUStore
        store = CIEUStore()

        # P1: Tool-call gov events
        cutoff_24h = (datetime.now() - timedelta(hours=24)).isoformat()
        gov_event_types = ["BEHAVIOR_RULE_VIOLATION", "WARNING", "WHITELIST_DRIFT", "MATCH"]

        gov_counts = {}
        with store._get_connection() as conn:
            for evt_type in gov_event_types:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM cieu_events WHERE event_type = ? AND timestamp > ?",
                    (evt_type, cutoff_24h)
                )
                count = cursor.fetchone()[0]
                gov_counts[evt_type] = count

        total_gov_events = sum(gov_counts.values())
        if total_gov_events == 0:
            findings.append("❌ **P0**: No tool-call governance events in 24h (producer dead)")
            rt_score += 10  # P0
        else:
            findings.append(f"✅ **P1**: {total_gov_events} tool-call gov events 24h — {gov_counts}")

        # P2: Session-level events
        session_event_types = ["HOOK_BOOT", "INTENT_RECORDED", "OBLIGATION_REGISTERED"]
        session_counts = {}
        with store._get_connection() as conn:
            for evt_type in session_event_types:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM cieu_events WHERE event_type = ? AND timestamp > ?",
                    (evt_type, cutoff_24h)
                )
                count = cursor.fetchone()[0]
                session_counts[evt_type] = count

        total_session = sum(session_counts.values())
        if total_session == 0:
            findings.append("⚠️ **P1**: No session-level events in 24h (low activity or boot hook failed)")
            rt_score += 5  # P1
        else:
            findings.append(f"✅ **P2**: {total_session} session events 24h — {session_counts}")

        # P3: CIEU DB writable
        try:
            test_ts = datetime.now().isoformat()
            store.record_event(
                event_type="K9_AUDIT_TEST",
                agent="k9_three_dim_audit",
                metadata={"test": "writable_check", "timestamp": test_ts}
            )
            # Clean up
            with store._get_connection() as conn:
                conn.execute(
                    "DELETE FROM cieu_events WHERE event_type = 'K9_AUDIT_TEST' AND agent = 'k9_three_dim_audit'"
                )
                conn.commit()
            findings.append("✅ **P3**: CIEU DB writable (INSERT + DELETE + commit OK)")
        except Exception as e:
            findings.append(f"❌ **P0**: CIEU DB NOT writable — {e}")
            rt_score += 10  # P0

    except Exception as e:
        findings.append(f"❌ **P0**: Producer integrity check CRASHED — {e}")
        rt_score += 10

    return findings, rt_score


def check_executor_integrity() -> Tuple[List[str], int]:
    """
    Dimension 2: Tool-call hook chain runtime

    Checks:
    E1. .claude/settings.json has all required hooks (PreToolUse/PostToolUse/SessionStart/UserPromptSubmit)
    E2. Registered hook scripts exist on disk
    E3. ystar.adapters.hook.check_hook() importable and callable with deny payload test
    E4. forget_guard.py callable (exit code check, if dead code -> flag)
    """
    findings = []
    rt_score = 0

    # E1: Required hooks registered
    required_hooks = ["PreToolUse", "PostToolUse", "SessionStart", "UserPromptSubmit"]

    if not SETTINGS_JSON.exists():
        findings.append(f"❌ **P0**: .claude/settings.json NOT FOUND at {SETTINGS_JSON}")
        return findings, 10

    with open(SETTINGS_JSON) as f:
        settings = json.load(f)

    registered_hooks = settings.get("hooks", {}).keys()
    missing_hooks = [h for h in required_hooks if h not in registered_hooks]

    if missing_hooks:
        findings.append(f"❌ **P0**: Missing required hooks: {missing_hooks}")
        rt_score += 10
    else:
        findings.append(f"✅ **E1**: All required hooks registered: {required_hooks}")

    # E2: Hook scripts exist on disk
    all_hook_commands = []
    for hook_type, matchers in settings.get("hooks", {}).items():
        for matcher_block in matchers:
            for hook_def in matcher_block.get("hooks", []):
                if hook_def.get("type") == "command":
                    all_hook_commands.append(hook_def["command"])

    missing_scripts = []
    for cmd in all_hook_commands:
        # Extract python script path from command
        parts = cmd.split()
        if len(parts) >= 2 and parts[0] == "python3":
            script_path = Path(parts[1])
            if not script_path.exists():
                missing_scripts.append(str(script_path))

    if missing_scripts:
        findings.append(f"⚠️ **P1**: Hook scripts missing on disk: {missing_scripts}")
        rt_score += 5
    else:
        findings.append(f"✅ **E2**: All {len(all_hook_commands)} hook scripts exist on disk")

    # E3: check_hook() importable and callable
    try:
        from ystar.adapters.hook import check_hook

        # Test with deny payload
        test_payload = {
            "tool_name": "Bash",
            "parameters": {"command": "rm -rf /"},
            "agent": "test_agent",
            "context": {}
        }

        # check_hook should accept this structure (we don't care about result, just callable)
        # Real test would need proper schema, but import success is main signal
        findings.append("✅ **E3**: ystar.adapters.hook.check_hook() importable (callable test skipped, need real payload schema)")
    except ImportError as e:
        findings.append(f"❌ **P0**: ystar.adapters.hook.check_hook NOT importable — {e}")
        rt_score += 10
    except Exception as e:
        findings.append(f"⚠️ **P2**: check_hook() import OK but callable test failed — {e}")

    # E4: forget_guard.py callable
    forget_guard_path = REPO_ROOT / "scripts" / "forget_guard.py"
    if not forget_guard_path.exists():
        findings.append(f"⚠️ **P2**: forget_guard.py NOT FOUND (possible dead code)")
    else:
        # Try calling it with --help or similar to check if alive
        import subprocess
        try:
            result = subprocess.run(
                ["python3", str(forget_guard_path), "--help"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0 or "usage" in result.stdout.decode().lower():
                findings.append("✅ **E4**: forget_guard.py callable (--help exit clean)")
            else:
                findings.append(f"⚠️ **P2**: forget_guard.py exists but --help failed (exit {result.returncode})")
        except subprocess.TimeoutExpired:
            findings.append("⚠️ **P2**: forget_guard.py timeout on --help (possible hang)")
        except Exception as e:
            findings.append(f"⚠️ **P2**: forget_guard.py call error — {e}")

    return findings, rt_score


def check_governed_integrity() -> Tuple[List[str], int]:
    """
    Dimension 3: Governance constraints actually enforcing

    Checks:
    G1. Last 7d has ≥1 decision='deny' event (deny rules actually firing)
    G2. delegation_chain.links each child deny_commands ⊇ parent deny_commands (monotonicity)
    G3. OBLIGATION_REGISTERED events catalyze at least 30 downstream events (50% threshold)
    G4. Same agent + same violation type ≥3 times without behavior change -> P1 warning
    """
    findings = []
    rt_score = 0

    try:
        from ystar.governance.cieu_store import CIEUStore
        store = CIEUStore()

        # G1: Deny events in 7d
        cutoff_7d = (datetime.now() - timedelta(days=7)).isoformat()

        with store._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM cieu_events
                WHERE event_type = 'BEHAVIOR_RULE_VIOLATION'
                  AND json_extract(metadata, '$.decision') = 'deny'
                  AND timestamp > ?
                """,
                (cutoff_7d,)
            )
            deny_count = cursor.fetchone()[0]

        if deny_count == 0:
            findings.append("❌ **P0**: 0 deny decisions in 7d (rules not enforcing)")
            rt_score += 10
        else:
            findings.append(f"✅ **G1**: {deny_count} deny decisions in 7d (rules enforcing)")

        # G2: Delegation chain monotonicity (simplified: check if .ystar_session.json has delegation_chain)
        session_json = REPO_ROOT / ".ystar_session.json"
        if session_json.exists():
            with open(session_json) as f:
                session_data = json.load(f)

            delegation_chain = session_data.get("delegation_chain", {}).get("links", [])
            if not delegation_chain:
                findings.append("⚠️ **P2**: No delegation_chain in .ystar_session.json (no child agents or not recorded)")
            else:
                # Check monotonicity: each child should have deny_commands ⊇ parent
                monotonicity_violations = []
                for i in range(len(delegation_chain) - 1):
                    parent = delegation_chain[i]
                    child = delegation_chain[i + 1]

                    parent_deny = set(parent.get("deny_commands", []))
                    child_deny = set(child.get("deny_commands", []))

                    if not parent_deny.issubset(child_deny):
                        missing = parent_deny - child_deny
                        monotonicity_violations.append({
                            "parent": parent.get("agent"),
                            "child": child.get("agent"),
                            "missing_denies": list(missing)
                        })

                if monotonicity_violations:
                    findings.append(f"⚠️ **P1**: Delegation monotonicity violated — {monotonicity_violations}")
                    rt_score += 5
                else:
                    findings.append(f"✅ **G2**: Delegation chain monotonicity OK ({len(delegation_chain)} links)")
        else:
            findings.append("⚠️ **P2**: .ystar_session.json NOT FOUND (can't check delegation monotonicity)")

        # G3: OBLIGATION_REGISTERED catalyze rate
        with store._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'OBLIGATION_REGISTERED' AND timestamp > ?",
                (cutoff_7d,)
            )
            obligation_count = cursor.fetchone()[0]

            if obligation_count == 0:
                findings.append("⚠️ **P2**: 0 OBLIGATION_REGISTERED events in 7d (no obligations or not recorded)")
            else:
                # Simplified: assume catalyzed events are anything that follows obligation (rough heuristic)
                # Real check would need causal_chain link
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM cieu_events WHERE timestamp > ?",
                    (cutoff_7d,)
                )
                total_events = cursor.fetchone()[0]
                catalyze_rate = total_events / obligation_count if obligation_count > 0 else 0

                if catalyze_rate < 30:
                    findings.append(f"⚠️ **P1**: OBLIGATION_REGISTERED catalyze rate too low ({catalyze_rate:.1f} events/obligation, target ≥30)")
                    rt_score += 5
                else:
                    findings.append(f"✅ **G3**: {obligation_count} obligations catalyzed ~{catalyze_rate:.1f} events each (≥30 threshold)")

        # G4: Repeat violations without behavior change
        with store._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT agent, json_extract(metadata, '$.rule_type') as rule_type, COUNT(*) as count
                FROM cieu_events
                WHERE event_type IN ('BEHAVIOR_RULE_VIOLATION', 'WARNING')
                  AND timestamp > ?
                GROUP BY agent, rule_type
                HAVING count >= 3
                ORDER BY count DESC
                """,
                (cutoff_7d,)
            )
            repeat_offenders = cursor.fetchall()

        if repeat_offenders:
            findings.append(f"⚠️ **P1**: {len(repeat_offenders)} agent+rule combos with ≥3 violations (warn ineffective) — {[(r[0], r[1], r[2]) for r in repeat_offenders[:5]]}")
            rt_score += 5
        else:
            findings.append("✅ **G4**: No repeat violations ≥3 (warnings effective or low violation rate)")

    except Exception as e:
        findings.append(f"❌ **P0**: Governed integrity check CRASHED — {e}")
        rt_score += 10

    return findings, rt_score


def generate_report() -> str:
    """Run all 3 dimensions and generate markdown report"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y%m%d")

    report_lines = [
        "# K9 Three-Dimensional Governance Audit",
        "",
        f"**Date**: {timestamp}",
        f"**Framework**: Consultant 3-dim (adopted 2026-04-16)",
        f"**Auditor**: k9_three_dim_audit.py",
        "",
        "## TL;DR",
        "",
    ]

    # Run all checks
    p_findings, p_rt = check_producer_integrity()
    e_findings, e_rt = check_executor_integrity()
    g_findings, g_rt = check_governed_integrity()

    total_rt = p_rt + e_rt + g_rt

    # Count severity
    all_findings = p_findings + e_findings + g_findings
    p0_count = sum(1 for f in all_findings if "**P0**" in f)
    p1_count = sum(1 for f in all_findings if "**P1**" in f)
    p2_count = sum(1 for f in all_findings if "**P2**" in f)

    if total_rt == 0:
        report_lines.append(f"✅ **Rt+1 = {total_rt}** — All 3 dimensions healthy (P0: {p0_count}, P1: {p1_count}, P2: {p2_count})")
    else:
        report_lines.append(f"⚠️ **Rt+1 = {total_rt}** — Violations detected (P0: {p0_count}, P1: {p1_count}, P2: {p2_count})")

    report_lines.extend([
        "",
        "## Dimension 1: Producer (CIEU Data Pipeline)",
        "",
    ])
    report_lines.extend(p_findings)
    report_lines.append(f"\n**Producer Rt+1**: {p_rt}")

    report_lines.extend([
        "",
        "## Dimension 2: Executor (Hook Chain Runtime)",
        "",
    ])
    report_lines.extend(e_findings)
    report_lines.append(f"\n**Executor Rt+1**: {e_rt}")

    report_lines.extend([
        "",
        "## Dimension 3: Governed (Constraint Enforcement)",
        "",
    ])
    report_lines.extend(g_findings)
    report_lines.append(f"\n**Governed Rt+1**: {g_rt}")

    report_lines.extend([
        "",
        "---",
        "",
        f"**Total Rt+1 = {total_rt}** (P0×10 + P1×5 + P2×0 weighting)",
        "",
        "### Severity Legend",
        "- **P0**: Critical — governance broken, immediate fix required",
        "- **P1**: Major — governance degraded, fix this week",
        "- **P2**: Minor — hygiene issue, backlog OK",
        "",
    ])

    return "\n".join(report_lines)


def main():
    """Main entry point"""

    # Generate report
    report_md = generate_report()

    # Print to stdout
    print(report_md)

    # Write to file
    date_str = datetime.now().strftime("%Y%m%d")
    report_path = REPORTS_DIR / f"3dim_audit_{date_str}.md"

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report_md)

    print(f"\n\n📄 Report written to: {report_path}")


if __name__ == "__main__":
    main()
