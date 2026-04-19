#!/bin/bash
# Audience: Board (Haotian) to source in shell rc (e.g. ~/.zshrc) or run once
# in the current terminal before launching Claude Code so YSTAR_HOOK_V2 is
# inherited by every hook subprocess.
#
# Research basis: Board directive 2026-04-18 "默认 on" for YSTAR_HOOK_V2.
# Claude Code tool hooks run as subprocess of the terminal-launched Claude
# Code process, so env set in parent shell inherits down.
#
# Synthesis: single export line. Adding to ~/.zshrc makes it default across
# all future sessions; running in current terminal scopes to that terminal.
#
# Default OFF rationale (prior state): safer rollback; router rules inert
# when flag off; exists as progressive enablement option.
# Default ON rationale (Board directive today): once 5-component anti-drift
# net shipped, router rules (next_action inject, break_glass, per_rule)
# SHOULD fire on live traffic to actually benefit the team — leaving flag
# off means ARCH-8/ARCH-11 series are dead code in runtime.

export YSTAR_HOOK_V2=1

echo "YSTAR_HOOK_V2 is now set to 1 (router rules active in live traffic)."
echo ""
echo "To make this permanent across terminals, append this line to ~/.zshrc:"
echo "  export YSTAR_HOOK_V2=1"
echo ""
echo "Current env:"
echo "  YSTAR_HOOK_V2=$YSTAR_HOOK_V2"
