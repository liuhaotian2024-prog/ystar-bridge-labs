# E11 Global Environment Inventory

## ystar_bridge_labs
- root: /private/tmp/ystar-bridge-labs-e11-20260502083633
- available: True
- branch: backflow/aiden-ceo-meeting-room
- head: 98fdfd7e08e7dc86dd7eed16edb69f6a2dd7e2e7
- blocker: none

## y_star_gov
- root: /Users/haotianliu/.openclaw/workspace/Y-star-gov
- available: True
- branch: backflow/company-runtime-domain-pack
- head: 5f031f4be151b81ef1a1b1908a5c83c5420e8ce1
- blocker: none

## gov_mcp
- root: /Users/haotianliu/.openclaw/workspace/gov-mcp
- available: True
- branch: backflow/company-runtime-tools
- head: f06aef334923d395202283766869e688129411d3
- blocker: none

## ystar_company
- root: /Users/haotianliu/.openclaw/workspace/ystar-company
- available: True
- branch: main
- head: dd9cb6b247a9cf06d953d9319ba1ebd5c38dcbf6
- blocker: none

## Coverage

- gov_mcp: 48 files inventoried
- y_star_gov: 482 files inventoried
- ystar_bridge_labs: 1016 files inventoried
- ystar_company: 386 files inventoried

## Artifact Types
- json: 335
- markdown: 553
- python: 1044

## Sensitive Boundary
- DB/WAL/SHM files, private logs, env files, and active-agent markers were not read.
- ystar-company was inventoried as incubation source/docs/templates/code; dirty runtime private artifacts were not read.
- `reports/integration/post_push_quality_audit.md` remains intentionally untracked in the original primary workspace.
