#!/usr/bin/env sh
set -eu

echo "L6.13 controlled observation environment check"
echo "Policy: staged controlled observation access (policy/action_capability_registry.json)"
echo "Search backend mode: ${YSTAR_CONTROLLED_SEARCH_BACKEND:-disabled}"
echo "Page-read backend mode: ${YSTAR_CONTROLLED_PAGE_READ_BACKEND:-disabled}"
echo "Search network allow flag set: $([ "${YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK:-0}" = "1" ] && echo yes || echo no)"
echo "Page-read network allow flag set: $([ "${YSTAR_CONTROLLED_PAGE_READ_ALLOW_NETWORK:-0}" = "1" ] && echo yes || echo no)"

if [ -n "${BRAVE_SEARCH_API_KEY:-}" ]; then
  echo "BRAVE_SEARCH_API_KEY present: yes"
else
  echo "BRAVE_SEARCH_API_KEY present: no"
fi

if [ -n "${TAVILY_API_KEY:-}" ]; then
  echo "TAVILY_API_KEY present: yes"
else
  echo "TAVILY_API_KEY present: no"
fi

if [ -n "${SERPAPI_API_KEY:-}" ]; then
  echo "SERPAPI_API_KEY present: yes"
else
  echo "SERPAPI_API_KEY present: no"
fi

echo "Secret values printed: no"
echo "Manual URL request required: no"
echo "Owner setup path: auto_detect_available; blocked_pending_config only when backend/key/allow flag is missing"
echo "Human-supervised setup available: yes"
