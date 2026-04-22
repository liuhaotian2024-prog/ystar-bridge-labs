"""
Audience: Board-shell runner to fix idle_pulse crash
Research basis: Ryan diagnostic + live crash reproduced by Board (ValueError ISO timestamp)
Synthesis: line 50 float(last_ts) fails on ISO string; wrap try/except fallback datetime.fromisoformat
Purpose: one-command fix, Board runs `python3 reports/ceo/ops/fix_idle_pulse.py` then verify

One-shot patch for scripts/idle_pulse.py line 50 ISO timestamp crash.
"""
import pathlib

p = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/idle_pulse.py")
src = p.read_text()

old_line = "        last_age = int(time.time() - float(last_ts)) if last_ts else -1"

new_block = """        try:
            last_age = int(time.time() - float(last_ts)) if last_ts else -1
        except (ValueError, TypeError):
            from datetime import datetime as _dt
            last_age = int(time.time() - _dt.fromisoformat(str(last_ts)).timestamp()) if last_ts else -1"""

if old_line in src:
    src = src.replace(old_line, new_block)
    p.write_text(src)
    print("PATCHED OK - line 50 now handles ISO + float timestamps")
elif "except (ValueError, TypeError):" in src:
    print("ALREADY PATCHED - skipping")
else:
    print(f"PATTERN NOT FOUND - inspect {p} manually")
