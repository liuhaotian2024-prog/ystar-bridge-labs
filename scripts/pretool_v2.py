#!/usr/bin/env python3
"""Y*gov Claude Code hook — thin v2 adapter (ARCH-6).

All governance logic lives in the ystar package.
This file is ONLY protocol translation: stdin -> handle_hook_event -> stdout.
Feature-flagged: activate via YSTAR_HOOK_V2=1 in hook_wrapper.py.
"""
import json, os, sys

from ystar.adapters.hook import handle_hook_event

raw = sys.stdin.buffer.read().decode("utf-8-sig").lstrip("\ufeff")
payload = json.loads(raw)
rules_dir = os.environ.get("YSTAR_RULES_DIR", "")
result = handle_hook_event(payload, rules_dir=rules_dir or None)
sys.stdout.write(json.dumps(result))
