#!/usr/bin/env python3
"""Wisdom-to-YAML Proposer — G3 Pipeline Last-Mile Wire

Reads memory/feedback_*.md (or memory/claude_code_memory_mirror/feedback_*.md)
and session_wisdom_extractor_v2.py output (wisdom_package_*.md), producing
candidate ForgetGuard YAML entries in governance/proposed_rules/.

Each candidate entry follows the forget_guard_rules.yaml schema:
  - id, enabled, description, trigger, action, recipe, cieu_event, severity

Output status is always 'proposed' (CTO must review before activation).

Heuristics (regex + NL parsing, no LLM calls):
  - ENFORCED feedback -> action: deny/warn (behavioral constraint)
  - Diagnostic/lesson feedback -> action: info (advisory only)
  - Board-originated -> severity: high
  - Agent-originated -> severity: medium

Author: Maya Patel (Governance Engineer)
Date: 2026-04-22
Task: CZL-CEO-RULES-REGISTRY-V3-MAYA G3
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import yaml


# ============================================================================
# Feedback File Parser
# ============================================================================

def parse_feedback_md(filepath: Path) -> Dict:
    """Parse a feedback .md file into structured fields.

    Expected format (YAML frontmatter + body):
    ---
    name: ...
    description: ...
    type: feedback
    ---
    Body text with Why/How sections.

    Returns dict with keys: name, description, type, body, why, how_to_apply,
                            keywords, is_diagnostic, is_board_originated
    """
    text = filepath.read_text(errors="replace")
    result = {
        "filename": filepath.stem,
        "name": filepath.stem.replace("feedback_", "").replace("_", " ").title(),
        "description": "",
        "type": "feedback",
        "body": "",
        "why": "",
        "how_to_apply": "",
        "keywords": [],
        "is_diagnostic": False,
        "is_board_originated": False,
    }

    # Parse YAML frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1))
            if isinstance(fm, dict):
                result["name"] = fm.get("name", result["name"])
                result["description"] = fm.get("description", "")
                result["type"] = fm.get("type", "feedback")
        except yaml.YAMLError:
            pass
        body_start = fm_match.end()
    else:
        body_start = 0

    body = text[body_start:].strip()
    result["body"] = body

    # Extract Why section
    why_match = re.search(r"\*\*Why[:\s]*\*\*(.*?)(?=\*\*How|\*\*Ref|\Z)", body, re.DOTALL | re.IGNORECASE)
    if why_match:
        result["why"] = why_match.group(1).strip()[:500]

    # Extract How to apply section
    how_match = re.search(r"\*\*How to apply[:\s]*\*\*(.*?)(?=\*\*Why|\*\*Ref|\Z)", body, re.DOTALL | re.IGNORECASE)
    if how_match:
        result["how_to_apply"] = how_match.group(1).strip()[:500]

    # Detect Board origin
    board_indicators = ["board", "老大", "haotian", "2026-04"]
    if any(ind in result["why"].lower() or ind in result["description"].lower() for ind in board_indicators):
        result["is_board_originated"] = True

    # Detect diagnostic/lesson (not actionable as deny/warn)
    diagnostic_indicators = [
        "diagnostic", "memo", "workaround", "investigation", "lesson",
        "architecture", "technical modeling", "scope clarification",
        "positioning", "recovery pattern", "boot config",
        "硬重启", "临时方案", "pattern",
    ]
    # Check name, description, AND body for diagnostic markers
    combined_text = (
        result["name"] + " " + result["description"] + " " + result["body"][:500]
    ).lower()
    if any(ind in combined_text for ind in diagnostic_indicators):
        result["is_diagnostic"] = True

    # Extract keywords from How to apply (behavioral trigger words)
    keywords = set()
    # Look for example patterns (✅ / ❌ examples)
    for m in re.finditer(r"[❌✅]\s*(.+)", body):
        example_text = m.group(1).strip()
        # Extract quoted strings
        for q in re.findall(r'"([^"]+)"', example_text):
            keywords.add(q)
        for q in re.findall(r"'([^']+)'", example_text):
            keywords.add(q)
        # Extract key phrases
        words = [w for w in example_text.split() if len(w) > 2 and w not in {"the", "and", "for", "not", "with"}]
        keywords.update(words[:3])

    # Extract ForgetGuard suggestion if present
    for m in re.finditer(r"ForgetGuard.*?(?:rule|加).*?[`']([a-z_]+)[`']", body, re.IGNORECASE):
        keywords.add(m.group(1))

    result["keywords"] = list(keywords)[:10]

    return result


# ============================================================================
# YAML Entry Generator
# ============================================================================

def generate_yaml_entry(parsed: Dict) -> Dict:
    """Convert parsed feedback into a candidate ForgetGuard YAML entry.

    Returns a dict matching forget_guard_rules.yaml schema.
    """
    filename = parsed["filename"]
    # Derive rule ID from filename
    rule_id = filename.replace("feedback_", "proposed_")
    if not rule_id.startswith("proposed_"):
        rule_id = f"proposed_{rule_id}"

    # Determine action based on feedback type
    if parsed["is_diagnostic"]:
        action = "info"
        severity = "low"
    elif parsed["is_board_originated"]:
        action = "warn"
        severity = "high"
    else:
        action = "warn"
        severity = "medium"

    # Build trigger keywords from parsed content
    trigger_keywords = []
    if parsed["keywords"]:
        trigger_keywords = [kw for kw in parsed["keywords"] if len(kw) > 2][:6]

    # If no keywords extracted, use name words
    if not trigger_keywords:
        name_words = parsed["name"].lower().split()
        trigger_keywords = [w for w in name_words if len(w) > 3][:4]

    # Build description
    desc = parsed["description"] or f"Auto-proposed from {filename}"
    if len(desc) > 120:
        desc = desc[:117] + "..."

    # Build recipe
    recipe_parts = [desc]
    if parsed["how_to_apply"]:
        recipe_parts.append(f"\nHow to apply:\n{parsed['how_to_apply'][:300]}")
    if parsed["why"]:
        recipe_parts.append(f"\nWhy:\n{parsed['why'][:200]}")
    recipe_parts.append(f"\nSource: memory/claude_code_memory_mirror/{filename}.md")
    recipe = "\n".join(recipe_parts)

    entry = {
        "id": rule_id,
        "enabled": False,  # proposed, not active
        "status": "proposed",
        "description": desc,
        "proposed_date": time.strftime("%Y-%m-%d"),
        "source": f"{filename}.md",
        "trigger": {
            "tool": ["Edit", "Write", "Bash"],
            "conditions": [
                {
                    "type": "content_contains",
                    "keywords": trigger_keywords,
                }
            ],
        },
        "action": action,
        "recipe": recipe,
        "cieu_event": f"PROPOSED_{rule_id.upper()}",
        "severity": severity,
    }

    return entry


# ============================================================================
# Wisdom Package Parser (for extractor v2 output)
# ============================================================================

def parse_wisdom_package(filepath: Path) -> List[Dict]:
    """Parse a wisdom_package_*.md file and extract actionable items
    that could become ForgetGuard rules.

    Returns list of dicts with keys: content, section, score
    """
    text = filepath.read_text(errors="replace")
    items = []

    current_section = ""
    for line in text.splitlines():
        # Track section headers
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue

        # Skip non-content lines
        if not line.strip() or line.startswith("---") or line.startswith("#"):
            continue

        # Extract numbered items with scores
        m = re.match(r"\d+\.\s+(.+?)(?:\[score:\s*([\d.]+)\])?$", line.strip())
        if m:
            content = m.group(1).strip()
            score = float(m.group(2)) if m.group(2) else 0.0
            items.append({
                "content": content,
                "section": current_section,
                "score": score,
            })

        # Extract bullet items
        elif line.strip().startswith("- "):
            content = line.strip()[2:]
            items.append({
                "content": content,
                "section": current_section,
                "score": 0.0,
            })

    return items


def wisdom_item_to_yaml_entry(item: Dict, index: int) -> Optional[Dict]:
    """Convert a wisdom package item to a candidate yaml entry.

    Only items with behavioral/rule content get converted.
    Diagnostic/informational items are skipped (return None).
    """
    content = item["content"]

    # Skip informational-only items
    skip_patterns = [
        r"^No\s+",
        r"^\(No\s+",
        r"^\*\*Campaign\*\*",
        r"^\*\*Team State\*\*",
        r"^\*\*Target\*\*",
    ]
    for pat in skip_patterns:
        if re.match(pat, content, re.IGNORECASE):
            return None

    # Check if content contains actionable governance indicators
    governance_indicators = [
        "must", "required", "forbidden", "禁止", "必须", "不许",
        "violation", "enforce", "deny", "warn", "block",
        "obligation", "constraint", "rule", "policy",
    ]
    content_lower = content.lower()
    is_governance = any(ind in content_lower for ind in governance_indicators)

    if not is_governance and item["score"] < 5.0:
        return None

    rule_id = f"wisdom_proposed_{index:03d}"
    severity = "high" if item["score"] > 8.0 else ("medium" if item["score"] > 3.0 else "low")

    # Extract keywords (first 4 meaningful words)
    words = re.findall(r"[a-zA-Z一-鿿]{3,}", content)
    keywords = words[:5]

    if not keywords:
        return None

    entry = {
        "id": rule_id,
        "enabled": False,
        "status": "proposed",
        "description": content[:120],
        "proposed_date": time.strftime("%Y-%m-%d"),
        "source": f"wisdom_package (section: {item['section']}, score: {item['score']:.2f})",
        "trigger": {
            "tool": ["Edit", "Write", "Bash"],
            "conditions": [
                {
                    "type": "content_contains",
                    "keywords": keywords,
                }
            ],
        },
        "action": "warn",
        "recipe": f"Auto-proposed from wisdom extraction:\n{content[:300]}\n\nReview before activation.",
        "cieu_event": f"WISDOM_{rule_id.upper()}",
        "severity": severity,
    }

    return entry


# ============================================================================
# Main Pipeline
# ============================================================================

def process_feedback_file(filepath: Path, output_dir: Path) -> Optional[Path]:
    """Process a single feedback file and write proposed yaml.

    Returns output path if successful, None if skipped.
    """
    parsed = parse_feedback_md(filepath)
    entry = generate_yaml_entry(parsed)

    output_filename = f"{parsed['filename']}_proposed.yaml"
    output_path = output_dir / output_filename

    yaml_content = {
        "schema_version": "1.1",
        "status": "proposed",
        "source_file": str(filepath),
        "proposed_date": time.strftime("%Y-%m-%d"),
        "rules": [entry],
    }

    with open(output_path, "w") as f:
        yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)

    return output_path


def process_wisdom_package(filepath: Path, output_dir: Path) -> Optional[Path]:
    """Process a wisdom package file and write proposed yaml entries.

    Returns output path if successful.
    """
    items = parse_wisdom_package(filepath)

    entries = []
    for i, item in enumerate(items):
        entry = wisdom_item_to_yaml_entry(item, i)
        if entry:
            entries.append(entry)

    if not entries:
        return None

    output_filename = f"{filepath.stem}_proposed.yaml"
    output_path = output_dir / output_filename

    yaml_content = {
        "schema_version": "1.1",
        "status": "proposed",
        "source_file": str(filepath),
        "proposed_date": time.strftime("%Y-%m-%d"),
        "rules": entries,
    }

    with open(output_path, "w") as f:
        yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Wisdom-to-YAML Proposer: Convert feedback files and wisdom packages to ForgetGuard YAML candidates"
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to a feedback_*.md file, wisdom_package_*.md file, or directory to scan",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: governance/proposed_rules/)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process all feedback_*.md files in the input directory",
    )
    args = parser.parse_args()

    # Determine output directory
    company_root = Path(__file__).parent.parent
    output_dir = args.output_dir or (company_root / "governance" / "proposed_rules")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    if args.batch or args.input_path.is_dir():
        # Batch mode: scan directory for feedback_*.md
        scan_dir = args.input_path if args.input_path.is_dir() else args.input_path.parent

        feedback_files = sorted(scan_dir.glob("feedback_*.md"))
        wisdom_files = sorted(scan_dir.glob("wisdom_package_*.md"))

        print(f"Scanning {scan_dir}:")
        print(f"  Found {len(feedback_files)} feedback files")
        print(f"  Found {len(wisdom_files)} wisdom package files")
        print()

        for fp in feedback_files:
            try:
                out = process_feedback_file(fp, output_dir)
                if out:
                    results.append(("feedback", fp.name, str(out)))
                    print(f"  [OK] {fp.name} -> {out.name}")
            except Exception as e:
                print(f"  [ERR] {fp.name}: {e}", file=sys.stderr)

        for wp in wisdom_files:
            try:
                out = process_wisdom_package(wp, output_dir)
                if out:
                    results.append(("wisdom", wp.name, str(out)))
                    print(f"  [OK] {wp.name} -> {out.name}")
            except Exception as e:
                print(f"  [ERR] {wp.name}: {e}", file=sys.stderr)

    elif args.input_path.name.startswith("feedback_"):
        # Single feedback file
        out = process_feedback_file(args.input_path, output_dir)
        if out:
            results.append(("feedback", args.input_path.name, str(out)))
            print(f"[OK] {args.input_path.name} -> {out.name}")

    elif "wisdom_package" in args.input_path.name:
        # Single wisdom package
        out = process_wisdom_package(args.input_path, output_dir)
        if out:
            results.append(("wisdom", args.input_path.name, str(out)))
            print(f"[OK] {args.input_path.name} -> {out.name}")

    else:
        # Try as generic feedback file
        out = process_feedback_file(args.input_path, output_dir)
        if out:
            results.append(("generic", args.input_path.name, str(out)))
            print(f"[OK] {args.input_path.name} -> {out.name}")

    print(f"\nTotal: {len(results)} proposed YAML entries written to {output_dir}/")
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
