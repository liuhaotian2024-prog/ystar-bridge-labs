# SIM-001 Product Gaps → Phase 2 Requirements
# Created: 2026-04-05
# Source: SIM-001 five-industry user journey simulation

---

## Phase 1 (PyPI Release) — Fixed ✅

| # | Gap | Fix | Status |
|---|---|---|---|
| 1 | String amounts bypass value_range | _normalize_amount() strips $,¥,€,£, commas, ISO 4217 codes | ✅ Fixed |
| 2 | No per-event Merkle hash | _compute_event_hash() in governance envelope, chained SHA-256 | ✅ Fixed |
| 3 | No confidence_score field | Added to governance envelope (1.0/0.95/0.7 by decision type) | ✅ Fixed |
| 4 | No human_approved field | Added via DelegationChain principal lookup | ✅ Fixed |

---

## Phase 2 Enterprise (Post-Launch Roadmap)

### Financial Services (FINRA/SOX)

| # | Gap | Priority | Effort | Description |
|---|---|---|---|---|
| 5 | COSO report template | P2 | 2 days | SOX Section 404 five-element internal control report generator |
| 6 | FINRA CRD mapping | P2 | 1 day | Map agent_id to FINRA Central Registration Depository number |

### Healthcare (EU AI Act)

| # | Gap | Priority | Effort | Description |
|---|---|---|---|---|
| 7 | Automatic rollback | P2 | 3 days | Undo mechanism for incorrect AI outputs with CIEU audit |
| 8 | ISO 13485 QMS template | P2 | 2 days | Quality Management System report template for medical devices |

### Legal Tech

| # | Gap | Priority | Effort | Description |
|---|---|---|---|---|
| 9 | Per-client encryption keys | P1 | 5 days | Separate encryption per client matter for attorney-client privilege |
| 10 | Privilege field | P2 | 1 day | Attorney-client privilege marker on CIEU records |
| 11 | Config validation | P2 | 2 days | Warn if only_paths isolation has potential gaps |

### Manufacturing / Supply Chain

| # | Gap | Priority | Effort | Description |
|---|---|---|---|---|
| 12 | Multi-currency support | P2 | 2 days | Currency-aware value_range with exchange rate context |
| 13 | Non-MCP ERP adapter | P2 | 5 days | REST/BAPI bridge for SAP/Oracle without MCP support |

### Cross-Industry

| # | Gap | Priority | Effort | Description |
|---|---|---|---|---|
| 14 | Country-specific modules | P2 | 10 days | EU GDPR, China CAC, Japan METI, Singapore PDPA compliance templates |

---

## Priority Summary

| Priority | Count | When |
|---|---|---|
| P1 (Fixed) | 4 | ✅ Done — included in v0.1.0 |
| P1 (Remaining) | 1 | Phase 2 early (#9 per-client encryption) |
| P2 | 9 | Phase 2 enterprise features |
| Total | 14 | |

---

## Decision Points for Board

1. Per-client encryption (#9) is P1 for legal vertical — invest before or after first legal customer?
2. Country modules (#14) — which country first? EU (largest regulatory pressure) or US (largest market)?
3. Non-MCP ERP adapter (#13) — build or partner?
