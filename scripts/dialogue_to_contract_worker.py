#!/usr/bin/env python3
"""
AMENDMENT-022: Dialogue→Contract Background Worker
Spawned by hook_user_prompt_tracker.py as fire-and-forget subprocess.

Receives user dialogue text, translates to IntentContract, emits CIEU event.
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
YGOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
DIALOGUE_CONTRACT_LOG = WORKSPACE_ROOT / "scripts/.logs/dialogue_contract.log"
CIEU_DB = WORKSPACE_ROOT / ".ystar_cieu.db"

# Add Y*gov to path
sys.path.insert(0, str(YGOV_ROOT))

def emit_cieu_event(event_type: str, details: dict):
    """Emit CIEU event to database using actual schema"""
    try:
        import sqlite3
        import uuid
        import time

        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()

        # Match actual cieu_events schema
        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, task_description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            int(time.time() * 1_000_000),  # microsecond timestamp
            time.time(),
            "dialogue_worker",
            "hook_pipeline",
            event_type,
            "allow",  # Informational event, not enforcement
            1,
            json.dumps(details)
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        with open(DIALOGUE_CONTRACT_LOG, "a") as f:
            f.write(f"{datetime.now().isoformat()} | cieu_emit_error: {e}\n")


def main():
    if len(sys.argv) < 2:
        return

    user_msg = sys.argv[1]
    start_time = datetime.now()

    try:
        # Set LLM provider (matches governance_boot.sh)
        os.environ["YSTAR_LLM_PROVIDER"] = "anthropic"

        from ystar.kernel.nl_to_contract import translate_to_contract

        # Translate dialogue to contract
        contract_dict, method, confidence = translate_to_contract(user_msg)

        # Log result
        with open(DIALOGUE_CONTRACT_LOG, "a") as f:
            f.write(f"{start_time.isoformat()} | method={method} confidence={confidence}\n")
            f.write(f"  msg: {user_msg[:100]}...\n")
            f.write(f"  contract: {json.dumps(contract_dict)}\n")

        # Emit CIEU event
        emit_cieu_event("DIALOGUE_CONTRACT_DRAFT", {
            "user_msg_preview": user_msg[:200],
            "contract": contract_dict,
            "method": method,
            "confidence": confidence,
            "timestamp": start_time.isoformat()
        })

    except Exception as e:
        with open(DIALOGUE_CONTRACT_LOG, "a") as f:
            f.write(f"{start_time.isoformat()} | translation_error: {e}\n")


if __name__ == "__main__":
    main()
