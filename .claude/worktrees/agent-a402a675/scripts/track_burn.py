#!/usr/bin/env python3
"""
Token Cost Tracking Script for Y* Bridge Labs
Parses Claude Code session summaries and logs costs to daily_burn.md
"""

import argparse
import re
from datetime import datetime
import os


# Pricing model (blended input/output rates)
PRICING = {
    'sonnet': 0.0054,  # $3 input + $15 output (80/20 blend) per 1K tokens
    'opus': 0.027,     # $15 input + $75 output (80/20 blend) per 1K tokens
    'haiku': 0.0018,   # $1 input + $5 output (80/20 blend) per 1K tokens
}


def parse_summary(summary):
    """
    Parse Claude Code summary string.
    Expected format: "Done (N tool uses · Xk tokens · Ym Zs)" or "Done (N tool uses · Xk tokens · Zs)"
    Returns: (tool_uses, tokens, duration)
    """
    # Pattern: Done (28 tool uses · 45k tokens · 4m 20s)
    pattern = r'Done \((\d+) tool uses? · (\d+)k tokens · (.+?)\)'
    match = re.search(pattern, summary)

    if not match:
        raise ValueError(f"Could not parse summary string: {summary}")

    tool_uses = int(match.group(1))
    tokens = int(match.group(2)) * 1000  # Convert "45k" to 45000
    duration = match.group(3).strip()

    return tool_uses, tokens, duration


def calculate_cost(tokens, model):
    """Calculate estimated cost based on token count and model."""
    if model not in PRICING:
        raise ValueError(f"Unknown model: {model}. Must be one of {list(PRICING.keys())}")

    cost_per_1k = PRICING[model]
    cost = (tokens / 1000) * cost_per_1k
    return round(cost, 4)


def format_table_row(date, agent, tool_uses, tokens, duration, cost):
    """Format a row for the session log table."""
    return f"| {date} | {agent} | {tool_uses} | {tokens:,} | {duration} | ${cost:.4f} |"


def ensure_session_log_exists(filepath):
    """Ensure the daily_burn.md file has a Session Log section with table header."""
    if not os.path.exists(filepath):
        # Create new file with session log
        content = """# Daily Burn Rate Log

**Last Updated:** {date}
**Purpose:** Track daily operational costs for CEO reporting

---

## Session Log

| Date | Agent | Tool Uses | Tokens | Duration | Est. Cost |
|------|-------|-----------|--------|----------|-----------|
""".format(date=datetime.now().strftime('%Y-%m-%d'))
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return

    # Check if Session Log section exists
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if '## Session Log' not in content:
        # Append session log section
        header = """
---

## Session Log

| Date | Agent | Tool Uses | Tokens | Duration | Est. Cost |
|------|-------|-----------|--------|----------|-----------|
"""
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(header)


def append_session(filepath, date, agent, tool_uses, tokens, duration, cost, dry_run=False):
    """Append a session row to the daily_burn.md file."""
    ensure_session_log_exists(filepath)

    row = format_table_row(date, agent, tool_uses, tokens, duration, cost)

    if dry_run:
        print(f"[DRY RUN] Would append to {filepath}:")
        print(row)
        return

    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(row + '\n')

    print(f"Logged session to {filepath}")
    print(row)


def main():
    parser = argparse.ArgumentParser(
        description='Track Claude Code session token costs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python track_burn.py --agent cto --model sonnet --summary "Done (28 tool uses · 45k tokens · 4m 20s)"
  python track_burn.py --agent ceo --model opus --summary "Done (17 tool uses · 12k tokens · 37s)" --dry-run
  python track_burn.py --agent cmo --summary "Done (2 tool uses · 9k tokens · 19s)" --date 2026-03-25
        """
    )

    parser.add_argument('--agent', required=True,
                       choices=['cto', 'cmo', 'cso', 'cfo', 'ceo', 'main'],
                       help='Which agent ran the session')
    parser.add_argument('--model', default='sonnet',
                       choices=['opus', 'sonnet', 'haiku'],
                       help='Which model was used (default: sonnet)')
    parser.add_argument('--summary', required=True,
                       help='Claude Code summary string (e.g., "Done (28 tool uses · 45k tokens · 4m 20s)")')
    parser.add_argument('--date', default=None,
                       help='Session date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Print what would be written without modifying the file')

    args = parser.parse_args()

    # Parse summary
    try:
        tool_uses, tokens, duration = parse_summary(args.summary)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Calculate cost
    cost = calculate_cost(tokens, args.model)

    # Determine date
    date = args.date if args.date else datetime.now().strftime('%Y-%m-%d')

    # Validate date format if provided
    if args.date:
        try:
            datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD")
            return 1

    # File path
    burn_file = r'C:\Users\liuha\OneDrive\桌面\ystar-company\finance\daily_burn.md'

    # Append session
    append_session(burn_file, date, args.agent, tool_uses, tokens, duration, cost, args.dry_run)

    return 0


if __name__ == '__main__':
    exit(main())
