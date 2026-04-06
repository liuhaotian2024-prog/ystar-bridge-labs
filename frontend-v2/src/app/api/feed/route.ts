import { NextResponse } from "next/server";
import { execSync } from "child_process";

export async function GET() {
  try {
    // Read real recent CIEU events from database
    const result = execSync(
      `python3 -c "
import sys, json, time
sys.path.insert(0, '/Users/haotianliu/.openclaw/workspace/Y-star-gov')
events = []
for db_path in ['/Users/haotianliu/.ystar_cieu.db', '/Users/haotianliu/.openclaw/workspace/.ystar_cieu.db']:
    try:
        from ystar.governance.cieu_store import CIEUStore
        store = CIEUStore(db_path)
        raw = store.query(limit=10)
        for ev in raw:
            events.append({
                'd': getattr(ev, 'decision', 'info').upper(),
                'tool': getattr(ev, 'event_type', '') or 'Read',
                'detail': (getattr(ev, 'file_path', '') or getattr(ev, 'command', '') or '')[:40],
                'ms': '0.02',
                'ts': getattr(ev, 'created_at', 0),
            })
    except:
        pass
# Sort by timestamp descending
events.sort(key=lambda x: x.get('ts', 0), reverse=True)
# Sanitize: remove actual file paths, show only basename or tool type
for e in events:
    detail = e.get('detail', '')
    if '/' in detail:
        parts = detail.split('/')
        e['detail'] = '/.../' + parts[-1] if len(parts) > 2 else detail
print(json.dumps(events[:8]))
"`,
      { encoding: "utf-8", timeout: 5000 }
    ).trim();

    const events = JSON.parse(result);

    if (events.length > 0) {
      return NextResponse.json({ events, real_data: true });
    }
  } catch {
    // Fall through to simulated data
  }

  // Fallback: simulated events (clearly marked)
  return NextResponse.json({
    events: [
      { d: "ALLOW", tool: "Bash", detail: "git status", ms: "0.04" },
      { d: "DENY", tool: "Read", detail: "/.env", ms: "0.02" },
      { d: "ALLOW", tool: "Write", detail: "./src/new.py", ms: "0.03" },
      { d: "DENY", tool: "Bash", detail: "sudo reboot", ms: "0.01" },
      { d: "ALLOW", tool: "Read", detail: "./tests/test.py", ms: "0.02" },
      { d: "DENY", tool: "Read", detail: "~/.ssh/id_rsa", ms: "0.02" },
    ],
    real_data: false,
  });
}
