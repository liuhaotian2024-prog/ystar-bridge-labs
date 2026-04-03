import sqlite3
from datetime import datetime
conn = sqlite3.connect('.ystar_cieu.db')
conn.row_factory = sqlite3.Row
rows = conn.execute('''
    SELECT seq_global, created_at, agent_id, event_type, decision, violations, command, file_path
    FROM cieu_events ORDER BY seq_global
''').fetchall()
for r in rows:
    ts = datetime.fromtimestamp(r['created_at']).strftime('%H:%M:%S')
    detail = r['violations'] or r['command'] or r['file_path'] or ''
    print(f"{ts} | {r['agent_id']:20s} | {r['decision']:5s} | {r['event_type']:10s} | {detail}")
conn.close()
