#!/usr/bin/env python3
"""
K9 Daily Digest — Severity Classifier + Top-5 Actionable Report

Reads:
- reports/k9_repo_audit_YYYYMMDD.txt (repo audit output)
- ~/.k9log/logs/k9log.cieu.jsonl (CIEU events from K9 session)

Produces:
- reports/k9_daily/YYYYMMDD_digest.md

Severity levels:
- P0: immediate session break risk (orphan process / FS wipe / governance disable)
- P1: data integrity (untracked critical / fail-closed broken)
- P2: hygiene (hardcoded path / bare except / deprecated)
- P3: nice-to-have (unused test / unreferenced script)
"""

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


# Severity classification rules
SEVERITY_RULES = {
    # P0: session-breaking risks
    "P0": [
        r"governance.*disable",
        r"orphan.*process",
        r"wipe.*file",
        r"fail.*open",  # Fail-open when should fail-closed
    ],
    # P1: data integrity
    "P1": [
        r"SUPERSEDED.*\.py$",  # Superseded code files
        r"untracked.*critical",
        r"audit.*log.*missing",
    ],
    # P2: code hygiene
    "P2": [
        r"hardcoded.*path",
        r"bare.*except",
        r"deprecated",
        r"ARTIFACT",  # .tmp, .bak files
        r"ORPHANED_JSONL",  # JSONL without .md case
    ],
    # P3: nice-to-have cleanup
    "P3": [
        r"ORPHANED_TXT",
        r"UNREFERENCED_SCRIPT",
        r"duplicate.*config",
        r"encoding.*issue",
    ],
}


def classify_severity(violation_text: str) -> str:
    """Classify violation severity P0/P1/P2/P3."""
    for severity, patterns in SEVERITY_RULES.items():
        for pattern in patterns:
            if re.search(pattern, violation_text, re.IGNORECASE):
                return severity
    return "P3"  # Default to lowest severity


def parse_repo_audit(audit_path: Path) -> List[Dict]:
    """Parse K9 repo audit report into structured violations."""
    violations = []
    current_rule = None

    with open(audit_path, "r") as f:
        for line in f:
            line = line.strip()

            # Detect rule header
            if line.startswith("[Rule"):
                match = re.match(r"\[Rule \d+\] (\w+)", line)
                if match:
                    current_rule = match.group(1)
                continue

            # Detect bonus rule
            if line.startswith("[Bonus]"):
                match = re.match(r"\[Bonus\] (\w+)", line)
                if match:
                    current_rule = match.group(1)
                continue

            # Detect violation
            if line.startswith("❌") or line.startswith("⚠️"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    violation_type = parts[0].strip().lstrip("❌⚠️ ").split(":")[0]
                    file_path = parts[1].strip()

                    severity = classify_severity(f"{current_rule} {violation_type} {file_path}")

                    violations.append({
                        "rule": current_rule or "UNKNOWN",
                        "type": violation_type,
                        "file": file_path,
                        "severity": severity,
                        "raw": line,
                    })

    return violations


def parse_cieu_log(cieu_path: Path) -> List[Dict]:
    """Parse K9 CIEU log for session events."""
    events = []

    if not cieu_path.exists():
        return events

    with open(cieu_path, "r") as f:
        for line in f:
            try:
                event = json.loads(line)
                events.append(event)
            except json.JSONDecodeError:
                continue

    return events


def summarize_top_violations(violations: List[Dict], limit: int = 5) -> List[Tuple[str, List[Dict]]]:
    """Group by severity and return top N actionable items."""
    by_severity = defaultdict(list)

    for v in violations:
        by_severity[v["severity"]].append(v)

    # Sort severity keys P0 > P1 > P2 > P3
    severity_order = ["P0", "P1", "P2", "P3"]
    top_items = []

    for sev in severity_order:
        if sev in by_severity:
            # Limit to top 5 within each severity
            items = by_severity[sev][:limit]
            if items:
                top_items.append((sev, items))

    return top_items


def generate_digest(
    audit_path: Path,
    cieu_path: Path,
    output_path: Path,
    date_str: str,
):
    """Generate daily K9 digest report."""
    violations = parse_repo_audit(audit_path)
    cieu_events = parse_cieu_log(cieu_path)

    # Summary stats
    total_violations = len(violations)
    by_severity = defaultdict(int)
    for v in violations:
        by_severity[v["severity"]] += 1

    # Top actionable items
    top_items = summarize_top_violations(violations, limit=5)

    # CIEU session stats
    cieu_violations = [e for e in cieu_events if e.get("action") == "deny" or "VIOLATION" in str(e)]

    # Write digest
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(f"# K9 Daily Digest — {date_str}\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Total violations**: {total_violations}\n")
        for sev in ["P0", "P1", "P2", "P3"]:
            count = by_severity.get(sev, 0)
            f.write(f"  - **{sev}**: {count}\n")
        f.write(f"- **CIEU events**: {len(cieu_events)}\n")
        f.write(f"  - **Denials/violations**: {len(cieu_violations)}\n\n")

        f.write("## Top 5 Actionable Items (by Severity)\n\n")

        for severity, items in top_items:
            f.write(f"### {severity}\n\n")
            for item in items[:5]:
                f.write(f"- **{item['type']}**: `{item['file']}`\n")
            f.write("\n")

        f.write("## CIEU Session Highlights\n\n")
        if cieu_violations:
            f.write(f"**{len(cieu_violations)} governance violations** recorded during K9 session.\n\n")
            # Show first 3 examples
            for event in cieu_violations[:3]:
                action = event.get("action", "unknown")
                reason = event.get("reason", "")
                f.write(f"- `{action}`: {reason}\n")
        else:
            f.write("No violations recorded.\n")

        f.write("\n---\n")
        f.write(f"**Source**: `{audit_path.name}` + `{cieu_path.name}`\n")

    print(f"✅ Digest written to {output_path}")
    print(f"   Total violations: {total_violations}")
    print(f"   P0={by_severity.get('P0', 0)} P1={by_severity.get('P1', 0)} P2={by_severity.get('P2', 0)} P3={by_severity.get('P3', 0)}")


def main():
    parser = argparse.ArgumentParser(description="Generate K9 daily digest with severity classification")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"), help="Date YYYYMMDD (default: today)")
    parser.add_argument("--audit", help="Path to repo audit report (default: reports/k9_repo_audit_YYYYMMDD.txt)")
    parser.add_argument("--cieu", default=str(Path.home() / ".k9log/logs/k9log.cieu.jsonl"), help="Path to CIEU log")
    parser.add_argument("--output", help="Output digest path (default: reports/k9_daily/YYYYMMDD_digest.md)")

    args = parser.parse_args()

    # Default paths
    workspace = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")

    audit_path = Path(args.audit) if args.audit else workspace / f"reports/k9_repo_audit_{args.date}.txt"
    cieu_path = Path(args.cieu)
    output_path = Path(args.output) if args.output else workspace / f"reports/k9_daily/{args.date}_digest.md"

    if not audit_path.exists():
        print(f"❌ Audit report not found: {audit_path}")
        return 1

    generate_digest(audit_path, cieu_path, output_path, args.date)
    return 0


if __name__ == "__main__":
    exit(main())
