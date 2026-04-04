# Y*gov 0.49.0 Implementation Plan

**Status:** Ready for Board Review  
**Created:** 2026-04-03 (Autonomous Session 5)  
**Target Start:** Week 2 post-0.48.0 launch  
**Target Release:** Q2 2026 (6-8 weeks)  
**Total Estimated Effort:** 180-220 hours (4.5-5.5 weeks full-time CTO)

---

## Executive Summary

This plan translates the 0.49.0 roadmap into executable tasks with:
- **7 major features** across P0/P1/P2 priorities
- **180-220 hours** of CTO effort (phased over 6-8 weeks)
- **Dynamic prioritization** based on 0.48.0 launch feedback
- **40+ new tests**, performance benchmarks, Windows CI
- **3 milestones** with Board checkpoints

**Key Decision Points:**
1. **Week 2 post-launch:** Prioritize based on user feedback (git-free API vs Windows vs dashboard?)
2. **Milestone 1 (Week 4):** Board approval to continue P1 features or ship 0.49.0 with P0 only
3. **Milestone 2 (Week 6):** Board decision on P2 scope (templates/adapters) or defer to 0.50.0

---

## Phase Structure

### Phase 0: Launch Feedback Collection (Week 1 post-launch)
**Duration:** 5-7 days  
**Owner:** CEO + CMO + CSO  
**CTO involvement:** 2 hours (feedback triage with team)

**Activities:**
1. Monitor HN/Twitter/GitHub for pain points
2. Categorize feedback: Installation, Performance, Windows, Git dependency, Features
3. Score each feedback category by frequency + severity
4. CEO presents prioritization recommendation to Board

**Outputs:**
- `reports/launch_feedback_analysis.md` (CMO)
- Priority ordering for 0.49.0 features (CEO → Board)

**Decision Gate:** Board approves adjusted feature priority for 0.49.0

---

### Phase 1: P0 Features (Week 2-4 post-launch)
**Duration:** 15-18 business days  
**CTO Effort:** 100-120 hours  
**Parallel work:** CSO enterprise outreach, CMO content production

#### Feature 1.1: Direct Python API (No Git Required)
**Priority:** P0 (unless launch feedback says otherwise)  
**Estimated Effort:** 50-60 hours  
**Timeline:** 10-12 days

**Tasks:**
1. **Design API surface** (4h)
   - Sketch `Governance`, `CIEURecorder`, `Contract` classes
   - Define `.from_file()`, `.from_string()`, `.from_dict()` loaders
   - API design review with CEO (1h meeting)

2. **Extract enforcement engine from hook layer** (16h)
   - Refactor `ystar/hook.py` → `ystar/engine.py` (core logic)
   - Remove git assumptions from engine
   - Maintain backward compatibility with hooks

3. **Implement `Governance` class** (12h)
   - Constructor, loaders (file/string/dict)
   - `.check(tool, params)` method
   - Unit tests (20+ tests)

4. **Implement `CIEURecorder` (git-optional)** (10h)
   - SQLite writes without git context (fallback to manual session_id)
   - API: `.record(decision, tool, params, context)`
   - Unit tests (15+ tests)

5. **Integration tests** (8h)
   - Jupyter notebook usage (`.ipynb` tests)
   - AWS Lambda mock (no git repo)
   - Docker scratch image test

6. **Documentation** (4h)
   - Update README with Python API examples
   - Create `docs/python_api.md`
   - Add to `ystar doctor` checks (verify API loadable)

**Success Metrics:**
- ✅ 40+ new tests passing
- ✅ Jupyter notebook example works (no git)
- ✅ `ystar doctor` passes in non-git directory

**Risks:**
- Breaking change if hook layer refactor introduces regressions
- Mitigation: Full hook E2E test suite must pass (559 tests)

---

#### Feature 1.2: Windows Native Support (No Git Bash)
**Priority:** P0 (Windows = 30% of Python developers)  
**Estimated Effort:** 30-35 hours  
**Timeline:** 6-7 days

**Tasks:**
1. **Environment detection** (4h)
   - Detect PowerShell, CMD, Git Bash, WSL
   - Auto-select hook installation strategy
   - Unit tests (10+ tests)

2. **Python-based hook runner** (12h)
   - Rewrite `ystar/hook.py` → use Python subprocess (not bash)
   - Git hook becomes: `#!/usr/bin/env python\nfrom ystar.hook_runner import main; main()`
   - Ensure Unix/Windows compatibility

3. **Windows CI pipeline** (8h)
   - Add GitHub Actions workflow: `windows-latest`
   - Run full test suite on Windows
   - Fix path separators, env var issues

4. **Hook install on Windows** (6h)
   - `ystar hook-install` works in PowerShell/CMD
   - No bash requirement
   - Install tests on Windows CI

5. **Documentation** (3h)
   - Update install guide for Windows
   - Troubleshooting section for Windows-specific issues

**Success Metrics:**
- ✅ CI passes on `windows-latest`
- ✅ `ystar hook-install` works in PowerShell (no Git Bash)
- ✅ All 559+ tests pass on Windows

**Risks:**
- Path separator issues (\\ vs /)
- Mitigation: Use `pathlib.Path` consistently

---

**Phase 1 Milestone (Week 4):**
- Board review: P0 features complete, 90+ new tests
- Decision: Ship 0.49.0 now (fast iteration) or continue to P1?
- If ship now: 0.49.0 RC → 1 week QA → PyPI release
- If continue: Proceed to Phase 2

---

### Phase 2: P1 Features (Week 5-7 post-launch)
**Duration:** 15-18 business days  
**CTO Effort:** 60-80 hours  
**Conditional on:** Board approval at Milestone 1

#### Feature 2.1: Delegation Chain Visualization (`ystar tree`)
**Priority:** P1 (nice to have, high enterprise value)  
**Estimated Effort:** 20-25 hours  
**Timeline:** 4-5 days

**Tasks:**
1. **Tree construction algorithm** (8h)
   - Query CIEU for delegation events
   - Build tree from `parent_context`
   - Detect cycles, orphaned nodes

2. **ASCII rendering** (6h)
   - Format tree with `├─`, `└─` characters
   - Color-code violations (ANSI colors)

3. **Export formats** (6h)
   - JSON export
   - Graphviz DOT export
   - Mermaid diagram export

4. **Tests** (4h)
   - 15+ tests for tree construction, cycle detection

**Success Metrics:**
- ✅ `ystar tree` shows delegation hierarchy
- ✅ Detects permission violations (child ⊄ parent)

---

#### Feature 2.2: Performance Optimization (<0.03ms)
**Priority:** P1 (competitive advantage)  
**Estimated Effort:** 18-22 hours  
**Timeline:** 4-5 days

**Tasks:**
1. **Profiling** (4h)
   - Identify hot paths with `cProfile`
   - Benchmark current performance (baseline)

2. **Regex caching** (3h)
   - Pre-compile all patterns at load time
   - LRU cache for compiled regexes

3. **Path normalization caching** (3h)
   - Cache `os.path.abspath()` results
   - LRU cache (max 1000 entries)

4. **AST parsing improvements** (5h)
   - Skip unnecessary traversals
   - Lazy contract loading (only parse needed rules)

5. **Performance regression suite** (5h)
   - Automated benchmarks on every commit
   - Fail if `check()` > 0.03ms (95th percentile)

**Success Metrics:**
- ✅ `check()` avg: 30μs (down from 42μs)
- ✅ 95th percentile: 45μs (down from 68μs)
- ✅ Performance regression suite integrated in CI

**Risks:**
- Optimizations may introduce bugs
- Mitigation: Full test suite must pass (no regressions)

---

#### Feature 2.3: Real-Time Dashboard (Web UI)
**Priority:** P1 (enterprise feature, high wow factor)  
**Estimated Effort:** 24-30 hours  
**Timeline:** 5-6 days

**Tasks:**
1. **Backend API** (10h)
   - FastAPI server with `/api/events`, `/api/agents`, `/api/metrics`
   - WebSocket endpoint for live tail (`/ws/live`)
   - SQLite query layer

2. **Frontend** (10h)
   - Single HTML page with Chart.js
   - Live event timeline (WebSocket updates)
   - Filters: agent, tool, decision (ALLOW/DENY)

3. **Deployment** (4h)
   - `ystar dashboard` command (starts server + opens browser)
   - Auto-detect available port (8080, 8081, ...)

4. **Tests** (4h)
   - E2E tests for endpoints
   - WebSocket streaming tests

**Success Metrics:**
- ✅ `ystar dashboard` opens browser with live dashboard
- ✅ Real-time updates when new CIEU events occur
- ✅ Shareable read-only links work

**Risks:**
- Scope creep (users want more features)
- Mitigation: Strict MVP scope, defer advanced features to 0.50.0

---

**Phase 2 Milestone (Week 7):**
- Board review: P1 features complete, 50+ new tests
- Decision: Ship 0.49.0 now or add P2 features?
- If ship now: 0.49.0 RC → QA → PyPI
- If continue: Proceed to Phase 3 (P2)

---

### Phase 3: P2 Features (Optional, Week 8-9)
**Duration:** 10-12 days  
**CTO Effort:** 40-50 hours  
**Conditional on:** Board approval at Milestone 2

#### Feature 3.1: Policy Templates
**Priority:** P2 (lowers activation energy for new users)  
**Estimated Effort:** 20-25 hours  

**Tasks:**
1. **Template design** (8h)
   - Draft `basic`, `hipaa`, `soc2`, `finra`, `development` templates
   - Validate against compliance requirements (CMO helps with HIPAA/SOC2 research)

2. **`ystar init --template`** (8h)
   - Command implementation
   - Template selection logic

3. **Tests** (6h)
   - Validate each template loads correctly
   - Compliance spot-checks (does HIPAA template block PII in logs?)

**Success Metrics:**
- ✅ 5 templates available
- ✅ `ystar init --template hipaa` creates valid AGENTS.md

---

#### Feature 3.2: Integration Adapters
**Priority:** P2 (ecosystem growth)  
**Estimated Effort:** 18-22 hours  

**Tasks:**
1. **LangChain adapter** (8h)
   - Wrap LangChain tools with Y*gov checks
   - Example: Governance-wrapped `PythonREPLTool`

2. **CrewAI adapter** (6h)
   - Similar to LangChain

3. **Documentation** (4h)
   - Integration guides for each framework

4. **Tests** (4h)
   - Integration tests with real LangChain/CrewAI code

**Success Metrics:**
- ✅ LangChain + CrewAI adapters published
- ✅ Example code in docs

---

**Phase 3 Milestone (Week 9):**
- Board decision: Ship 0.49.0 with P2 or defer P2 to 0.50.0
- If ship: 0.49.0 RC → QA → PyPI
- If defer: Ship 0.49.0 with P0+P1, move P2 to 0.50.0 backlog

---

## Resource Allocation

### CTO Time Budget
| Phase | Effort | Calendar Time | Parallel Work |
|-------|--------|---------------|---------------|
| Phase 0 (Feedback) | 2h | Week 1 | CMO/CSO active, CTO observes |
| Phase 1 (P0) | 100-120h | Week 2-4 (15-18 days) | CSO enterprise outreach |
| Phase 2 (P1) | 60-80h | Week 5-7 (15-18 days) | CMO content, CSO POCs |
| Phase 3 (P2) | 40-50h | Week 8-9 (10-12 days) | Optional |

**Total:** 180-220 hours over 6-8 weeks

**Assumptions:**
- CTO works 6-8h/day on 0.49.0 (not full-time, leaves buffer for P0 bugs, customer support)
- P0 bugs from 0.48.0 launch have priority interrupt (CTO may pause 0.49.0 work)
- Parallel work by other agents doesn't block CTO

---

## Dynamic Prioritization Logic

**Scenario 1: "Git dependency is killing us"**
- Feedback: Many users in non-git environments (Jupyter, Lambda)
- Action: Prioritize Feature 1.1 (Direct Python API) → ship 0.49.0 with P0 only (fast iteration)

**Scenario 2: "Windows install is broken"**
- Feedback: Windows users struggling with Git Bash requirement
- Action: Prioritize Feature 1.2 (Windows Native) → may skip dashboard (P1) to ship faster

**Scenario 3: "Performance is fine, we want visibility"**
- Feedback: Dashboard requests >> performance complaints
- Action: Prioritize Feature 2.3 (Dashboard) over Feature 2.2 (Performance)

**Scenario 4: "We need HIPAA compliance templates"**
- Feedback: Enterprise customers asking for policy templates
- Action: Elevate Feature 3.1 (Templates) from P2 → P1

**Board reviews feedback at Week 1 and adjusts priorities accordingly.**

---

## Testing Strategy

### New Tests by Phase
| Phase | Unit Tests | Integration Tests | E2E Tests | Performance Tests | Total |
|-------|-----------|-------------------|-----------|-------------------|-------|
| Phase 1 (P0) | 60+ | 15+ | 8+ | 5+ | 90+ |
| Phase 2 (P1) | 30+ | 10+ | 5+ | 10+ | 55+ |
| Phase 3 (P2) | 20+ | 8+ | 0 | 0 | 28+ |

**Grand Total:** 170+ new tests (559 → 730+ tests)

### CI Enhancements
- Windows CI pipeline (GitHub Actions `windows-latest`)
- Performance regression suite (auto-fail if `check()` > 0.03ms)
- Integration tests for Jupyter, Lambda, Docker

---

## Risk Management

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **P0 bugs from 0.48.0 launch interrupt 0.49.0 work** | HIGH | MEDIUM | Budget 20% CTO time for support/fixes |
| **Scope creep on dashboard feature** | MEDIUM | HIGH | Strict MVP scope, defer advanced features |
| **Windows CI flakiness** | MEDIUM | MEDIUM | Retry logic, fix path separator issues early |
| **Performance optimization introduces bugs** | LOW | HIGH | Full test suite must pass, no regressions |
| **Enterprise customers request features not in plan** | MEDIUM | LOW | Capture in 0.50.0 backlog, stay disciplined |

---

## Success Metrics (0.49.0 Release)

### Technical Metrics
- ✅ 730+ tests passing (170+ new tests)
- ✅ CI passes on Linux + macOS + Windows
- ✅ `check()` performance: <0.03ms (95th percentile)
- ✅ Direct Python API works in Jupyter (no git)
- ✅ `ystar hook-install` works in PowerShell (no Git Bash)
- ✅ Dashboard accessible at `localhost:8080`

### User Metrics (90 days post-0.49.0)
- 📈 30% increase in PyPI downloads (git-free API unlocks new use cases)
- 📈 50% reduction in Windows-related GitHub issues
- 📈 10+ enterprise POCs using dashboard for compliance audits
- 📈 5+ blog posts/tweets mentioning Y*gov performance (<0.03ms)

### Business Metrics
- 💰 2+ paid pilot agreements (dashboard feature is selling point)
- 💰 1+ enterprise LOI (policy templates reduce activation energy)
- 📊 20+ GitHub stars (down from 50+, more modest expectation)

---

## Board Decision Points

**Decision 1 (Week 1 post-launch):**
- Question: Adjust feature priority based on launch feedback?
- Options: Keep plan as-is / Swap P0↔P1 / Defer features

**Decision 2 (Week 4, Milestone 1):**
- Question: Ship 0.49.0 with P0 only (fast iteration) or continue to P1?
- Options: Ship now / Continue to P1 / Pause for enterprise POC feedback

**Decision 3 (Week 7, Milestone 2):**
- Question: Add P2 features (templates/adapters) or defer to 0.50.0?
- Options: Ship with P2 / Ship without P2 / Pause for customer validation

---

## Appendix: Dependency Graph

```
Phase 0 (Feedback)
    ↓
Phase 1.1 (Direct Python API) ─┐
Phase 1.2 (Windows Native)      ├─→ Milestone 1 Decision
    ↓                           │
Phase 2.1 (Delegation Tree)    ─┤
Phase 2.2 (Performance)        ─┤
Phase 2.3 (Dashboard)          ─┘
    ↓
Milestone 2 Decision
    ↓
Phase 3.1 (Templates)          ─┐
Phase 3.2 (Adapters)           ─┴→ Ship 0.49.0
```

**No blocking dependencies between P0 features** (can parallelize if CTO has help)  
**P1 features independent** (can pick subset based on feedback)  
**P2 features optional** (nice-to-have, not blockers)

---

**Plan Author:** CEO (Aiden)  
**Date:** 2026-04-03 (Autonomous Session 5)  
**Status:** Ready for Board review and approval  
**Next Step:** Await 0.48.0 launch feedback, then execute Phase 0
