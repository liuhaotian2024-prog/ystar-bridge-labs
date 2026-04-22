"""
Audience: Board-shell runner to fix meeting room left/right column rendering
Research basis: Board 2026-04-20 late-night reported "两侧 member 不显示"; suspected 1fr rows collapsing below min-content
Synthesis: grid-template-rows change from 1fr to minmax(70px, 1fr) + explicit member-window min-height prevents collapse
Purpose: one-shot CSS patch, Board runs `python3 scripts/fix_meeting_room_css.py` then Cmd+R browser
"""
import pathlib

p = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/meeting_room/index.html")
src = p.read_text()

patches = [
    ("grid-template-rows: auto repeat(5, 1fr) auto;",
     "grid-template-rows: auto repeat(5, minmax(75px, 1fr)) auto;"),
    (".member-window {\n            background: #161b22; border: 1px solid #30363d;",
     ".member-window {\n            background: #161b22; border: 1px solid #30363d;\n            min-height: 75px;"),
]

changed = 0
for old, new in patches:
    if old in src and new not in src:
        src = src.replace(old, new)
        changed += 1

p.write_text(src)
print(f"PATCHED OK — {changed} patches applied")
print("Refresh browser (Cmd+R) at http://localhost:8080 to see fix")
