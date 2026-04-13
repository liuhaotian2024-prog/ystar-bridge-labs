#!/usr/bin/env python3
"""
Goal Progress Dashboard — CEO Aiden's Self-Driving Capability #2
Track completion % of priority_brief.md targets using CIEU event flow.

Usage:
    python3 scripts/goal_progress.py [--target_id TARGET_ID] [--output PATH]

Output: reports/goal_progress.md with progress bars for today/week/month targets
"""

import argparse
import re
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

WORKSPACE = Path(__file__).parent.parent
PRIORITY_BRIEF = WORKSPACE / "reports" / "priority_brief.md"
CIEU_DB = WORKSPACE / ".ystar_cieu.db"
OUTPUT_PATH = WORKSPACE / "reports" / "goal_progress.md"


def extract_yaml_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        print(f"YAML parse error: {e}", file=sys.stderr)
        return {}


def extract_verify_markers(verify_str: str) -> List[str]:
    """
    Extract verification markers from verify string.
    Examples:
        "Maya commit + RLE on_cieu_event" → ["Maya", "commit", "RLE", "on_cieu_event"]
        "17 base + 10 新 tests 全绿" → ["17", "base", "10", "tests"]
        "pytest pass" → ["pytest", "pass"]
    """
    # Remove common filler words
    stop_words = {'在', '的', '了', '和', '与', '或', '触发', '跑完', '全', '个'}
    # Extract alphanumeric + underscore tokens
    tokens = re.findall(r'[\w]+', verify_str)
    markers = [t for t in tokens if t not in stop_words and len(t) > 1]
    return markers


def query_cieu_markers(markers: List[str], lookback_hours: int = 48) -> Dict[str, int]:
    """
    Query CIEU database for each marker and count matches.
    Returns dict: {marker: match_count}
    """
    if not CIEU_DB.exists():
        return {m: 0 for m in markers}

    conn = sqlite3.connect(str(CIEU_DB))
    cutoff_ts = time.time() - (lookback_hours * 3600)

    results = {}
    for marker in markers:
        # Search in decision, event_type, file_path, command, task_description
        query = """
        SELECT COUNT(*) FROM cieu_events
        WHERE created_at > ?
        AND (
            decision LIKE ? OR
            event_type LIKE ? OR
            file_path LIKE ? OR
            command LIKE ? OR
            task_description LIKE ? OR
            agent_id LIKE ?
        )
        """
        pattern = f'%{marker}%'
        cursor = conn.execute(query, (cutoff_ts, pattern, pattern, pattern, pattern, pattern, pattern))
        count = cursor.fetchone()[0]
        results[marker] = count

    conn.close()
    return results


def calculate_completion(verify: str, lookback_hours: int = 48) -> Tuple[int, Dict[str, int]]:
    """
    Calculate completion % for a target based on its verify string.
    Returns: (completion_percent, marker_hits_dict)
    """
    markers = extract_verify_markers(verify)
    if not markers:
        return 0, {}

    marker_hits = query_cieu_markers(markers, lookback_hours)

    # Count how many markers have at least 1 hit
    hit_count = sum(1 for count in marker_hits.values() if count > 0)
    total_markers = len(markers)

    completion = int((hit_count / total_markers) * 100) if total_markers > 0 else 0
    return completion, marker_hits


def render_progress_bar(percent: int, width: int = 10) -> str:
    """Render ASCII progress bar."""
    filled = int((percent / 100) * width)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}]"


def format_target_line(target: dict, completion: int, marker_hits: Dict[str, int]) -> str:
    """Format a single target line with progress bar and details."""
    bar = render_progress_bar(completion)
    target_text = target.get('target', 'Unknown target')
    owner = target.get('owner', 'unknown')

    # Show top 3 markers that hit (for debugging/transparency)
    top_hits = sorted(marker_hits.items(), key=lambda x: x[1], reverse=True)[:3]
    hit_summary = ", ".join([f"{k}:{v}" for k, v in top_hits if v > 0])
    hit_info = f" ({hit_summary})" if hit_summary else ""

    return f"- {bar} {completion:3}% {target_text} (owner: {owner}){hit_info}"


def generate_dashboard(target_id: str = None) -> str:
    """Generate the goal progress dashboard markdown."""
    if not PRIORITY_BRIEF.exists():
        return "ERROR: reports/priority_brief.md not found"

    content = PRIORITY_BRIEF.read_text()
    meta = extract_yaml_frontmatter(content)

    today_targets = meta.get('today_targets', [])
    week_targets = meta.get('this_week_targets', [])
    month_targets = meta.get('this_month_targets', [])

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    version = meta.get('version', 'unknown')
    last_updated = meta.get('last_updated', 'unknown')

    lines = [
        "# Goal Progress Dashboard",
        f"**Generated**: {now}",
        f"**Source**: priority_brief.md v{version} (last_updated: {last_updated})",
        f"**Method**: CIEU event flow keyword matching (lookback: 48h)",
        "",
        "---",
        ""
    ]

    # Today targets
    lines.append(f"## Today (EOD {last_updated}): {len(today_targets)} active")
    lines.append("")
    for target in today_targets:
        verify = target.get('verify', '')
        completion, marker_hits = calculate_completion(verify, lookback_hours=48)
        lines.append(format_target_line(target, completion, marker_hits))
    lines.append("")

    # Week targets
    deadline_week = week_targets[0].get('deadline', 'unknown') if week_targets else 'unknown'
    lines.append(f"## This Week ({deadline_week}): {len(week_targets)} active")
    lines.append("")
    for target in week_targets:
        verify = target.get('verify', '')
        completion, marker_hits = calculate_completion(verify, lookback_hours=7*24)
        lines.append(format_target_line(target, completion, marker_hits))
    lines.append("")

    # Month targets
    deadline_month = month_targets[0].get('deadline', 'unknown') if month_targets else 'unknown'
    lines.append(f"## This Month ({deadline_month}): {len(month_targets)} active")
    lines.append("")
    for target in month_targets:
        verify = target.get('verify', '')
        completion, marker_hits = calculate_completion(verify, lookback_hours=30*24)
        lines.append(format_target_line(target, completion, marker_hits))
    lines.append("")

    # Overall summary
    all_targets = today_targets + week_targets + month_targets
    if all_targets:
        all_completions = [calculate_completion(t.get('verify', ''), lookback_hours=48)[0] for t in all_targets]
        avg_completion = sum(all_completions) // len(all_completions)
        lines.append("---")
        lines.append(f"**Overall Progress**: {avg_completion}% (avg across {len(all_targets)} active targets)")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("*Auto-generated by scripts/goal_progress.py — DO NOT manually edit*")
    lines.append(f"*CIEU events: {get_cieu_event_count()}*")

    return "\n".join(lines)


def get_cieu_event_count() -> int:
    """Get total CIEU event count."""
    if not CIEU_DB.exists():
        return 0
    conn = sqlite3.connect(str(CIEU_DB))
    count = conn.execute("SELECT COUNT(*) FROM cieu_events").fetchone()[0]
    conn.close()
    return count


def main():
    parser = argparse.ArgumentParser(description="Generate goal progress dashboard")
    parser.add_argument('--target_id', help="Filter to specific target ID")
    parser.add_argument('--output', default=str(OUTPUT_PATH), help="Output path")
    args = parser.parse_args()

    dashboard = generate_dashboard(target_id=args.target_id)

    output = Path(args.output)
    output.write_text(dashboard)
    print(f"✓ Dashboard written to {output}")
    print(f"✓ CIEU events analyzed: {get_cieu_event_count()}")

    # Also print to stdout for CLI usage
    print("\n" + dashboard)


if __name__ == '__main__':
    main()
