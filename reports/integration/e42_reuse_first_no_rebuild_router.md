# E42 Reuse-First No-Rebuild Router

- Added a gate that chooses reuse, extension, thin adapter, cross-repo proposal, or block.
- Blocks wrong-layer work such as Labs-owned MCP execution or duplicate Y-star-gov governance semantics.
- Designed to be called before creating new modules or artifacts.

## Gate decisions

- reuse_existing
- extend_existing
- thin_adapter_allowed
- new_build_allowed
- cross_repo_proposal_required
- blocked_duplicate
- blocked_wrong_layer
- blocked_report_pile

## Fixture summary

- Continue frontier capability import: reuse_existing
- Prepare public read-only evidence sprint: reuse_existing
- Plan external execution/tool use: blocked_wrong_layer
- Update CEO memory after milestone: reuse_existing
- Create owner decision packet for next commercial route: reuse_existing
- Fix delivery bridge/status issue: reuse_existing
