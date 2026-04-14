"""查CIEU里所有session启动相关事件，了解重启实际发生了什么"""
import sqlite3, json
db = sqlite3.connect('/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db')

# 1. 找所有不同的session_id
print("=== 所有session ===")
sessions = db.execute("""
    SELECT session_id, agent_id, COUNT(*) as event_count,
           MIN(created_at) as start_time, MAX(created_at) as end_time
    FROM cieu_events
    WHERE session_id IS NOT NULL
    GROUP BY session_id
    ORDER BY MIN(created_at) DESC
    LIMIT 10
""").fetchall()
for sid, aid, cnt, st, et in sessions:
    from datetime import datetime
    st_str = datetime.fromtimestamp(st).strftime('%Y-%m-%d %H:%M') if st else '?'
    et_str = datetime.fromtimestamp(et).strftime('%H:%M') if et else '?'
    print(f"  {sid[:8]} | {aid} | {cnt} events | {st_str} → {et_str}")

# 2. 当前session的前10个事件（CEO重启后到底先做了什么）
print("\n=== 当前session（最新）的前10个事件 ===")
latest_session = sessions[0][0] if sessions else None
if latest_session:
    early = db.execute("""
        SELECT created_at, event_type, decision, file_path, command, task_description
        FROM cieu_events
        WHERE session_id = ?
        ORDER BY created_at ASC
        LIMIT 15
    """, (latest_session,)).fetchall()
    for ts, et, dec, fp, cmd, td in early:
        from datetime import datetime
        t = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        target = (fp or cmd or td or '')[:80]
        print(f"  {t} | {et} | {dec} | {target}")

# 3. 今天所有重启相关事件（governance_boot.sh）
print("\n=== 今天所有governance_boot.sh调用 ===")
boots = db.execute("""
    SELECT created_at, session_id, agent_id, command
    FROM cieu_events
    WHERE command LIKE '%governance_boot%'
    ORDER BY created_at DESC
    LIMIT 15
""").fetchall()
for ts, sid, aid, cmd in boots:
    from datetime import datetime
    t = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    print(f"  {t} | {sid[:8]} | {aid} | {cmd[:100] if cmd else ''}")

# 4. 今天session_close调用
print("\n=== 今天session_close调用 ===")
closes = db.execute("""
    SELECT created_at, session_id, agent_id, command
    FROM cieu_events
    WHERE command LIKE '%session_close%'
    ORDER BY created_at DESC
    LIMIT 10
""").fetchall()
for ts, sid, aid, cmd in closes:
    from datetime import datetime
    t = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    print(f"  {t} | {sid[:8]} | {aid} | {cmd[:100] if cmd else ''}")

# 5. 今天continuation相关事件
print("\n=== 今天continuation相关事件 ===")
conts = db.execute("""
    SELECT created_at, session_id, agent_id, file_path, command, task_description
    FROM cieu_events
    WHERE file_path LIKE '%continuation%' OR command LIKE '%continuation%'
       OR task_description LIKE '%continuation%'
    ORDER BY created_at DESC
    LIMIT 10
""").fetchall()
for ts, sid, aid, fp, cmd, td in conts:
    from datetime import datetime
    t = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    target = (fp or cmd or td or '')[:80]
    print(f"  {t} | {sid[:8]} | {aid} | {target}")

# 6. behavior rule违规事件
print("\n=== behavior rule违规事件（最近20条）===")
violations = db.execute("""
    SELECT created_at, agent_id, decision, violations, drift_details
    FROM cieu_events
    WHERE event_type LIKE '%BEHAVIOR%' OR violations != '[]'
    ORDER BY created_at DESC
    LIMIT 20
""").fetchall()
for ts, aid, dec, viol, drift in violations:
    from datetime import datetime
    t = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    info = (viol if viol != '[]' else drift) or ''
    print(f"  {t} | {aid} | {dec} | {info[:100]}")
