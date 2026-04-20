#!/usr/bin/env python3
"""
Audience: Board (executes). CEO-authored patch; Board-invoked because CEO cross-boundary writes blocked.
Research basis: Ryan#5 receipt + v1 audit — _check_must_dispatch_via_cto uses blacklist (prefix tuple from alias keys), catches Ethan-/Samantha-/all-C-suite-via-alias wrongly. Board 2026-04-19 architectural correction: rule intent is "block CEO→engineer direct spawn", whitelist form = "canonical resolves to eng-* → DENY; otherwise allow".
Synthesis: Swap prefix-blacklist for canonical-whitelist. Same intent, smaller attack surface, no keyword drift.
Purpose: restore CEO ability to spawn Ethan-CTO (canonical=cto) + Samantha-Secretary (canonical=secretary); keep eng-* (canonical=eng-*) correctly blocked.
"""

import pathlib

hook = pathlib.Path('/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/boundary_enforcer.py')
text = hook.read_text()

# Target block: current blacklist prefix-match
old_block = '''    if tool_name == "Agent":
        target_agent = params.get("subagent_type") or params.get("agent", "")
        # LABS_ALIAS: name-based prefixes loaded from session config at runtime
        from ystar.adapters.identity_detector import _load_alias_map
        _alias_map = _load_alias_map()
        _name_prefixes = tuple(f"{k.split('-')[0]}-" for k in _alias_map if "-" in k)
        _eng_prefixes = ("eng-",) + _name_prefixes
        if target_agent.startswith(_eng_prefixes):'''

# Whitelist replacement: resolve to canonical first, then check canonical
new_block = '''    if tool_name == "Agent":
        target_agent = params.get("subagent_type") or params.get("agent", "")
        # CZL-DISPATCH-WHITELIST-FIX (Board 2026-04-19 architectural correction):
        # Resolve target through alias map to CANONICAL value, then check if
        # canonical starts with "eng-". This is whitelist form — CEO→CTO and
        # CEO→Secretary are canonically legal paths (cto/secretary canonicals
        # are NOT engineering), previous prefix-blacklist caught them wrongly.
        from ystar.adapters.identity_detector import _load_alias_map
        _alias_map = _load_alias_map()
        target_canonical = _alias_map.get(target_agent, target_agent)
        if target_canonical.startswith("eng-"):'''

if old_block in text:
    new_text = text.replace(old_block, new_block)
    hook.write_text(new_text)
    print('[PATCH] boundary_enforcer.py _check_must_dispatch_via_cto: swapped to canonical-whitelist form')
    print('        target_canonical = _alias_map.get(target_agent, target_agent)')
    print('        if target_canonical.startswith("eng-"):')
elif 'target_canonical = _alias_map.get(target_agent, target_agent)' in text:
    print('[PATCH] Already applied (skip)')
else:
    print('[PATCH] WARNING — neither old nor new pattern matched; manual inspection needed')
    print("        Expected old marker: _name_prefixes = tuple(f..split..)")

# Smoke test via live import
import sys
sys.path.insert(0, '/Users/haotianliu/.openclaw/workspace/Y-star-gov')
try:
    import importlib
    # Clear cache so patch is picked up
    for mod in list(sys.modules.keys()):
        if 'boundary_enforcer' in mod or 'ystar.adapters' in mod:
            del sys.modules[mod]
    from ystar.adapters import boundary_enforcer
    print('[SMOKE] import OK, _check_must_dispatch_via_cto callable:', callable(boundary_enforcer._check_must_dispatch_via_cto))
except Exception as e:
    print(f'[SMOKE] import failed: {e}')
