#!/bin/bash
# K9-RT Sentinel Cron Wrapper
# Invokes ystar.governance.k9_rt_sentinel from Y-star-gov repo
# Outputs to /tmp/ystar_k9_rt.log for monitoring
# Exit code 0 on success (warnings emitted or not), non-zero on crash

YSTAR_GOV_PATH="/Users/haotianliu/.openclaw/workspace/Y-star-gov"
YSTAR_COMPANY_PATH="/Users/haotianliu/.openclaw/workspace/ystar-company"

cd "$YSTAR_COMPANY_PATH" || exit 1

/usr/bin/python3 -c "
import sys
sys.path.insert(0, '$YSTAR_GOV_PATH')
from ystar.governance.k9_rt_sentinel import scan_and_emit_warnings
count = scan_and_emit_warnings()
print(f'[K9-RT Sentinel] Emitted {count} warnings', flush=True)
sys.exit(0)
"
