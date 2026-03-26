# Y*gov CIEU Governance Report #001

**Generated:** 2026-03-26
**Database:** .ystar_cieu.db

---

## Summary

```
Y*gov CIEU Report — .ystar_cieu.db
──────────────────────────────────────────────────
  Total decisions : 13
  Allow           : 3  (23.1%)
  Deny            : 10   (76.9%)
```

## Top Blocked Paths/Commands

| Count | Target |
|-------|--------|
| 10 | `/etc` path access (Read & Bash) |

## By Agent

| Agent | Total | Denied | Deny% |
|-------|-------|--------|-------|
| doctor_agent | 9 | 9 | 100% |
| agent | 4 | 1 | 25% |

## Deny Records Detail

| # | Time | Agent | Event Type | Violation |
|---|------|-------|------------|-----------|
| 1 | 14:22:32 | doctor_agent | Read | `/etc` is not allowed in file_path |
| 2 | 14:23:23 | doctor_agent | Read | `/etc` is not allowed in file_path |
| 3 | 15:09:26 | doctor_agent | Read | `/etc` is not allowed in file_path |
| 4 | 15:10:36 | doctor_agent | Read | `/etc` is not allowed in file_path |
| 5 | 15:41:50 | doctor_agent | Read | `/etc` is not allowed in file_path |
| 6 | 15:43:12 | doctor_agent | Read | `/etc` is not allowed in file_path |
| 7 | 16:00:16 | doctor_agent | Read | `/etc` is not allowed in file_path |
| 8 | 16:04:49 | agent | Bash | `/etc` is not allowed in command |
| 9 | 16:04:55 | doctor_agent | Read | `/etc` is not allowed in file_path |
| 10 | 16:08:07 | doctor_agent | Read | `/etc` is not allowed in file_path |

## Analysis

- **All 10 deny events** were triggered by the `/etc` path restriction in the governance contract
- **9 of 10** came from `doctor_agent` self-tests (`ystar doctor` deliberately probes `/etc/passwd` to verify enforcement)
- **1 of 10** came from the main `agent` attempting a Bash command referencing `/etc`
- **3 allow events** represent legitimate operations within permitted boundaries
- **Deny rate of 76.9%** is inflated by doctor self-tests; excluding those, the operational deny rate is 1/4 (25%)

---

*Report generated from Y*gov CIEU audit chain. Records are immutable and tamper-evident.*
