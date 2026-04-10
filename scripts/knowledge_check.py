#!/usr/bin/env python3.11
"""
knowledge_check.py — Path C: Gemma-driven pairwise contradiction detection.

After an agent writes a new knowledge file (theory, case, SOP), this
script compares it against existing files in the same directory to detect
contradictions. Contradictions are written to CIEU as GAP_IDENTIFIED
events for human resolution — no auto-merge (4B model not reliable
enough for automatic consolidation).

Design (borrowed from CrewAI Cognitive Memory's consolidation concept,
implemented without CrewAI dependency):
  - Pairwise comparison: new file vs each existing file in same dir
  - Gemma generates a judgment: consistent / contradictory / complementary
  - Contradictions → GAP_IDENTIFIED CIEU event + console warning
  - Fail-open: Gemma unreachable → skip check, log warning

Usage:
  # Check a specific new file against its directory:
  python3.11 scripts/knowledge_check.py \\
      --file knowledge/cto/theory/system_architecture.md \\
      --actor cto

  # Check all files in a role's theory dir (batch mode):
  python3.11 scripts/knowledge_check.py --role cto --dir theory

Called automatically by active_task.py complete (if the output path
is inside knowledge/).
"""
import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSION_PATH = REPO_ROOT / ".ystar_session.json"
ROLES = {"ceo", "cto", "cmo", "cso", "cfo", "secretary"}

PROMPT_TEMPLATE = """\
You are comparing two knowledge files from the same domain to detect contradictions.

FILE A (existing):
{file_a_content}

FILE B (new):
{file_b_content}

Analyze the relationship between these two files. Output EXACTLY one JSON object:

{{
  "relationship": "consistent" | "contradictory" | "complementary",
  "explanation": "one sentence explaining the relationship",
  "contradiction_details": "if contradictory, what specifically contradicts what; otherwise null"
}}

Rules:
- "consistent": they agree on the same points
- "contradictory": they make opposing claims about the same topic
- "complementary": they cover different aspects of the same topic without conflict
- If unsure, default to "complementary" (fail-safe: don't raise false alarms)
"""


def load_config():
    try:
        with open(SESSION_PATH) as f:
            data = json.load(f)
        endpoints = data.get("gemma_endpoints", ["http://localhost:11434"])
        model = data.get("gemma_default_model", "gemma3:4b")
        cieu_db = data.get("cieu_db", str(REPO_ROOT / ".ystar_cieu.db"))
        return endpoints, model, cieu_db
    except (OSError, json.JSONDecodeError):
        return ["http://localhost:11434"], "gemma3:4b", str(REPO_ROOT / ".ystar_cieu.db")


def call_gemma(endpoints, model, prompt, timeout=60):
    import urllib.request
    for ep in endpoints:
        try:
            payload = json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1},
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{ep.rstrip('/')}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = json.loads(r.read().decode("utf-8"))
            return body.get("response", ""), ep
        except Exception:
            continue
    return None, None


def extract_json(text):
    import re
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


def write_gap_event(cieu_db, actor, new_file, existing_file, details):
    from ystar.governance.cieu_store import CIEUStore
    cieu = CIEUStore(db_path=cieu_db)
    record = {
        "event_id": str(uuid.uuid4()),
        "session_id": "knowledge_check",
        "agent_id": actor,
        "event_type": "GAP_IDENTIFIED",
        "decision": "info",
        "evidence_grade": "ops",
        "created_at": time.time(),
        "seq_global": time.time_ns() // 1000,
        "params": {
            "type": "contradiction",
            "new_file": str(new_file),
            "existing_file": str(existing_file),
            "details": details,
            "detected_at": time.time(),
            "source": "knowledge_check.py",
        },
        "violations": ["knowledge_contradiction"],
        "drift_detected": True,
        "human_initiator": actor,
    }
    cieu.write_dict(record)


def check_file(target_path, actor, endpoints, model, cieu_db, verbose=True):
    target = Path(target_path)
    if not target.exists() or not target.suffix == ".md":
        return []

    target_content = target.read_text()[:3000]  # truncate for prompt size
    if len(target_content.strip()) < 20:
        return []

    # Compare against all other .md files in the same directory
    siblings = [f for f in target.parent.iterdir()
                if f.suffix == ".md" and f != target and f.name != "README.md"]

    contradictions = []
    for sib in siblings:
        sib_content = sib.read_text()[:3000]
        if len(sib_content.strip()) < 20:
            continue

        prompt = PROMPT_TEMPLATE.format(
            file_a_content=sib_content[:2000],
            file_b_content=target_content[:2000],
        )

        response, ep = call_gemma(endpoints, model, prompt)
        if response is None:
            if verbose:
                print(f"  WARN: Gemma unreachable, skipping {sib.name}")
            continue

        result = extract_json(response)
        if result is None:
            if verbose:
                print(f"  WARN: could not parse Gemma output for {sib.name}")
            continue

        rel = result.get("relationship", "complementary")
        if verbose:
            icon = {"consistent": "✓", "complementary": "~", "contradictory": "✗"}
            print(f"  {icon.get(rel, '?')} {target.name} vs {sib.name}: {rel}")

        if rel == "contradictory":
            details = result.get("contradiction_details") or result.get("explanation", "")
            write_gap_event(cieu_db, actor, target, sib, details)
            contradictions.append({
                "new_file": str(target),
                "existing_file": str(sib),
                "details": details,
            })
            if verbose:
                print(f"    ⚠ CONTRADICTION: {details[:100]}")

    return contradictions


def main():
    p = argparse.ArgumentParser(
        description="Gemma-driven knowledge contradiction detection (Path C)",
    )
    p.add_argument("--file", help="Specific file to check against its directory")
    p.add_argument("--role", help="Role to check (batch mode)")
    p.add_argument("--dir", default="theory", help="Subdirectory within role (default: theory)")
    p.add_argument("--actor", help="Actor for CIEU events (defaults to role)")
    args = p.parse_args()

    if not args.file and not args.role:
        p.print_help()
        return 2

    endpoints, model, cieu_db = load_config()

    if args.file:
        actor = args.actor or "cto"
        target = Path(args.file)
        print(f"Checking {target.name} against {target.parent}/")
        contradictions = check_file(target, actor, endpoints, model, cieu_db)
        if contradictions:
            print(f"\n{len(contradictions)} contradiction(s) found → GAP_IDENTIFIED in CIEU")
        else:
            print(f"\nNo contradictions found")
        return 0

    if args.role:
        actor = args.actor or args.role
        role_dir = REPO_ROOT / "knowledge" / args.role / args.dir
        if not role_dir.exists():
            print(f"ERROR: {role_dir} does not exist", file=sys.stderr)
            return 1
        files = [f for f in role_dir.iterdir() if f.suffix == ".md" and f.name != "README.md"]
        if not files:
            print(f"No .md files in {role_dir}")
            return 0
        total_contradictions = 0
        for f in files:
            print(f"\nChecking {f.name}...")
            c = check_file(f, actor, endpoints, model, cieu_db)
            total_contradictions += len(c)
        print(f"\nTotal: {total_contradictions} contradiction(s) across {len(files)} files")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
