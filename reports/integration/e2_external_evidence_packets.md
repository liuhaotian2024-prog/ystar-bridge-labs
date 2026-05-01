# E2 External Evidence Packets

## Live external evidence not available
- packet_id: external_not_available
- category: external_capability
- live_market_evidence: False
- fixture_or_demo: False
- private_or_secret_content_included: False
- summary: No live read-only research was executed. Current recommendation remains internal-evidence preliminary.
- blocked_reason: BLOCKED_BY_MISSING_LIVE_RESEARCH_CONFIG
- enablement_packet_ref: reports/integration/e2_live_read_only_enablement_packet.md

## Fixture/demo research evidence availability
- packet_id: external_fixture_demo_available
- category: fixture_demo
- live_market_evidence: False
- fixture_or_demo: True
- private_or_secret_content_included: False
- summary: ystar-company has fixture-backed research demo plumbing, but fixture evidence is not live market evidence and is not counted for E2 market validation.

Safety: evidence packets exclude secrets, private DB/WAL/SHM/log content, and active-agent marker contents.
