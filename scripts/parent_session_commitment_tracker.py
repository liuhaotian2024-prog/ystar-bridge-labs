#!/usr/bin/env python3
"""
Parent Session Commitment Tracker (POC).

Milestone 8c (2026-04-21): close the "omission engine sleep" gap Board caught
at session 20:15 — CEO reply 里承诺 (e.g., "Milestone N 下 reply 开",
"Pilot 成功再 scale 到 8 agent") 从未被 OmissionEngine track, 所以 CEO 走到
下 cycle 不做后续就 silent. 本 tracker 扫 reply text 提取 commitment 模式,
落 pending_commitments.jsonl + CIEU event PARENT_SESSION_COMMITMENT_REGISTERED.

当前 POC scope:
- extract_commitments(reply_text) → [(statement, commitment_type, deadline_hint)]
- register_commitment(ces) → write .pending_commitments.jsonl + CIEU
- check_overdue() → report commitments past deadline not delivered

TODO (Ryan wire P0 CZL-PARENT-SESSION-REGISTER-AS-ENTITY):
- Stop hook call register_commitment per reply
- UserPromptSubmit hook call check_overdue, surface to CEO as context
- Integrate with OmissionEngine TrackedEntity model (omission_models.py)

M-tag: M-2b 防不作为 (structural 防 CEO 自欺), M-2a 防虚假 done claims.
"""
import json
import re
import sys
import time
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
COMMITMENTS_FILE = WORKSPACE / "scripts/.pending_commitments.jsonl"


# Patterns that indicate CEO commitments in reply text.
# Each pattern: (regex, commitment_type, default_deadline_sec_from_now)
COMMITMENT_PATTERNS = [
    # "下 reply 开 Milestone X", "下轮 reply 立刻开 Y", "下一步 ... 下 reply 做 ..."
    (re.compile(r"(下(?:[一回轮次]+|\s)?reply\s*(?:立刻|立即|马上)?\s*(?:开|启动|做|实施)[^\n。]{0,80})", re.IGNORECASE),
     "next_reply_commitment",
     600),

    # "Milestone N = X" / "Milestone N: X" / "Milestone N — X" / "Milestone N self-pick"
    (re.compile(r"(Milestone\s*\d+\s*(?:[=:—\-]|self-pick|scope)\s*[^\n。]{3,120})", re.IGNORECASE),
     "milestone_scope_declaration",
     1800),

    # "Pilot 成功再 X", "成功再 template scale"
    (re.compile(r"(Pilot\s*成功再\s*[^\n。]{5,80}|成功[后再]\s*template\s*scale\s*[^\n。]{0,80})"),
     "pilot_then_scale",
     1800),

    # "立刻做 X", "I am doing X right now"
    (re.compile(r"(立刻[做开始动手][^\n。]{3,80}|I\s+am\s+doing\s+[^\n。]{3,80})"),
     "immediate_action",
     300),

    # "Rt\+1=0" after N — progress committed
    (re.compile(r"(Rt\+?1\s*=\s*0\s*(?:收敛|达成|PASS)?[^\n]{0,50})"),
     "convergence_claim",
     60),  # near-term verify
]


def extract_commitments(reply_text: str) -> list:
    """Scan reply text for CEO commitment patterns. Return list of dicts."""
    now = time.time()
    out = []
    for pattern, ctype, deadline_sec in COMMITMENT_PATTERNS:
        for m in pattern.finditer(reply_text):
            statement = m.group(1).strip()[:200]
            out.append({
                "statement": statement,
                "commitment_type": ctype,
                "created_at": now,
                "deadline": now + deadline_sec,
                "deadline_hint_sec": deadline_sec,
            })
    return out


def register_commitment(commitment: dict,
                        session_id: str = "unknown",
                        reply_id: str = "unknown",
                        commitments_file: Path = None) -> str:
    """Append commitment to pending_commitments.jsonl. Return commitment_id."""
    f = commitments_file or COMMITMENTS_FILE
    f.parent.mkdir(parents=True, exist_ok=True)
    commitment_id = f"commit_{int(time.time() * 1_000_000)}_{hash(commitment['statement']) & 0xffff:04x}"
    record = dict(commitment)
    record["commitment_id"] = commitment_id
    record["session_id"] = session_id
    record["reply_id"] = reply_id
    record["status"] = "PENDING"
    with open(f, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return commitment_id


def check_overdue(commitments_file: Path = None, now: float = None) -> list:
    """Return commitments whose deadline passed and still PENDING."""
    f = commitments_file or COMMITMENTS_FILE
    if not f.exists():
        return []
    now = now or time.time()
    overdue = []
    with open(f, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("status") != "PENDING":
                continue
            deadline = rec.get("deadline", 0)
            if now > deadline:
                rec["overdue_sec"] = now - deadline
                overdue.append(rec)
    return overdue


def mark_delivered(commitment_id: str,
                   commitments_file: Path = None) -> bool:
    """Mark a commitment DELIVERED (not overdue anymore)."""
    f = commitments_file or COMMITMENTS_FILE
    if not f.exists():
        return False
    lines = []
    found = False
    with open(f, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                lines.append(line)
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                lines.append(line)
                continue
            if rec.get("commitment_id") == commitment_id:
                rec["status"] = "DELIVERED"
                rec["delivered_at"] = time.time()
                found = True
                lines.append(json.dumps(rec, ensure_ascii=False))
            else:
                lines.append(line)
    if found:
        with open(f, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    return found


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true",
                    help="read reply text from stdin, extract commitments, print JSON")
    ap.add_argument("--check-overdue", action="store_true",
                    help="list overdue pending commitments")
    args = ap.parse_args()

    if args.scan:
        text = sys.stdin.read()
        commitments = extract_commitments(text)
        for c in commitments:
            print(json.dumps(c, ensure_ascii=False))
        return 0

    if args.check_overdue:
        over = check_overdue()
        if not over:
            print("[tracker] no overdue commitments")
            return 0
        print(f"[tracker] {len(over)} OVERDUE commitments:")
        for r in over[:10]:
            print(f"  - '{r['statement'][:80]}' overdue {r['overdue_sec']:.0f}s type={r['commitment_type']}")
        return 1

    print("Usage: --scan (stdin) | --check-overdue")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
