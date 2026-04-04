# Y*gov 0.49.0 Roadmap (DRAFT)

**Status:** Planning (waiting for 0.48.0 launch feedback)  
**Target Release:** Q2 2026 (4-6 weeks post-0.48.0)  
**Last Updated:** 2026-04-03

---

## Strategic Goals for 0.49.0

1. **Remove Git Dependency** — Enable Y*gov in non-git environments (Jupyter notebooks, serverless, Docker containers)
2. **Improve Windows UX** — Eliminate Git Bash requirement, make Windows a first-class platform
3. **Increase Observability** — Make CIEU audit data easier to visualize and analyze
4. **Performance Optimization** — Reduce `check()` latency from 0.042ms → <0.03ms
5. **Enterprise Readiness** — Add features requested by SOC 2 / HIPAA compliance teams

---

## Proposed Features (Priority TBD After Launch Feedback)

### P0 — Must-Have (Blocking Pain Points)

#### 1. Direct Python API (No Git Required)
**Problem:** Many users want Y*gov in non-git environments (Jupyter, AWS Lambda, Docker scratch images)

**Solution:**
```python
from ystar import Governance, CIEURecorder

# Load governance contract
gov = Governance.from_file("AGENTS.md")  # or from_string(), from_dict()

# Explicit check
result = gov.check(tool="bash", params={"command": "rm -rf /"})
if result.decision == "DENY":
    raise PermissionError(result.reason)

# Optional CIEU recording (even without git)
recorder = CIEURecorder(db_path=".ystar_cieu.db")
recorder.write(result)
```

**Impact:**
- Unlocks: Jupyter notebooks, AWS Lambda, Google Cloud Functions, Docker
- Reduces friction for non-git users (data science teams, rapid prototyping)

**Implementation:**
- Extract enforcement engine from hook layer
- Create standalone `Governance` class (no git dependency)
- CIEU recorder works with or without git
- Hooks become one integration path (not the only path)

**Tests:** 40+ new tests for direct API usage

---

#### 2. Windows Native Support (No Git Bash)
**Problem:** Windows users must install Git Bash just to run hook installation (friction, confusion)

**Solution:**
- Detect Windows PowerShell/CMD and install hooks using native Windows tools
- Use Python `subprocess` hooks instead of bash scripts
- `ystar hook-install` works in PowerShell, CMD, Git Bash (auto-detect)

**Implementation:**
- Hook scripts in Python (not bash) — cross-platform by default
- Git hooks call `python -m ystar.hook_runner`
- Deprecate bash-specific hooks

**Tests:** Windows CI pipeline (GitHub Actions with windows-latest)

---

### P1 — High Value (Significant Improvements)

#### 3. Delegation Chain Visualization
**Problem:** Users want to see the full permission inheritance tree (parent → child agents)

**Solution:**
```bash
ystar tree

# Output:
CEO (full permissions)
├─ CTO (read/write src/, tests/)
│  ├─ test_agent (read tests/, write test_reports/)
│  └─ build_agent (read src/, write dist/)
└─ CMO (read/write content/, marketing/)
   └─ blog_agent (write content/blog/ only)
```

**Features:**
- ASCII tree visualization
- Highlight permission violations (child has permissions ⊄ parent)
- Export to JSON, Graphviz, Mermaid

**Implementation:**
- Query CIEU records for delegation events
- Build tree from `parent_context` relationships
- Detect inheritance violations

**Tests:** 15+ tests for tree construction, cycle detection, permission subset validation

---

#### 4. Performance: `check()` < 0.03ms
**Problem:** 0.042ms is fast, but every microsecond matters for high-volume agents (1M+ tool calls/day)

**Target:** Reduce to <0.03ms (30 microseconds) — 40% improvement

**Optimizations:**
1. **Compiled regex caching** — Pre-compile all patterns at load time
2. **Path normalization caching** — LRU cache for `os.path.abspath()` results
3. **AST parsing improvements** — Skip unnecessary traversals
4. **Lazy contract loading** — Only parse rules needed for current tool
5. **C extension (optional)** — Compile hot path in Cython (opt-in for performance-critical users)

**Benchmark:**
- Current: 42μs avg, 95th percentile: 68μs
- Target: 30μs avg, 95th percentile: 45μs

**Tests:** Performance regression suite (run on every commit)

---

#### 5. Real-Time Dashboard (Web UI)
**Problem:** CIEU records are SQLite → CLI only. Enterprises want web dashboards.

**Solution:**
```bash
ystar dashboard --port 8080

# Opens browser to http://localhost:8080
# Live-updating dashboard showing:
# - Recent violations (DENY events)
# - Agent activity timeline
# - Delegation chain graph
# - Performance metrics (check() latency distribution)
```

**Features:**
- Real-time tail of CIEU records (WebSocket updates)
- Filter by agent, tool, decision (ALLOW/DENY)
- Export filtered records to JSON/CSV
- Shareable read-only links (for compliance audits)

**Tech Stack:**
- Backend: Python (FastAPI or Flask)
- Frontend: Simple HTML + Chart.js (no React/Vue — keep it lightweight)
- Deployment: Single `ystar dashboard` command (no separate install)

**Tests:** E2E tests for dashboard endpoints, WebSocket streaming

---

### P2 — Nice to Have (Enhancements)

#### 6. Policy Templates (Pre-Built Governance Contracts)
**Problem:** Users don't know where to start with governance rules

**Solution:**
```bash
ystar init --template hipaa
# Creates AGENTS.md with HIPAA-specific rules:
# - No PII in logs
# - Encryption for patient data
# - Audit all access to protected health information

ystar init --template soc2
# SOC 2 controls:
# - MFA for production access
# - Change management (test before deploy)
# - Access control matrices

ystar init --template basic
# Starter rules:
# - No /etc, /var, /usr access
# - No rm -rf
# - No production credentials
```

**Templates:**
- `basic` — General safety (file protection, dangerous commands)
- `hipaa` — HIPAA compliance (PII, PHI, encryption)
- `soc2` — SOC 2 controls (access, change management)
- `finra` — Financial services (trading, audit, retention)
- `development` — Safe defaults for dev teams (no force push to main, etc.)

**Tests:** Validate each template against known compliance requirements

---

#### 7. Integration Adapters
**Problem:** Users want plug-and-play integration with popular frameworks

**Solution:**
Pre-built adapters in `ystar.integrations`:

```python
# LangChain
from ystar.integrations.langchain import YGovCallback
agent = initialize_agent(..., callbacks=[YGovCallback()])

# AutoGPT
from ystar.integrations.autogpt import YGovPlugin
# Automatically enforces governance on all AutoGPT actions

# CrewAI
from ystar.integrations.crewai import YGovEnforcer
crew = Crew(agents=[...], enforcer=YGovEnforcer())
```

**Integrations to build:**
- LangChain (callback handler)
- AutoGPT (plugin)
- CrewAI (enforcer)
- Haystack (custom component)
- Semantic Kernel (filter)

**Tests:** Integration test suite with each framework

---

#### 8. CIEU Archive & Retention Policies
**Problem:** CIEU database grows large (100MB+), but users need to keep records for compliance

**Solution:**
```bash
# Archive records older than 90 days
ystar archive --older-than 90d --output cieu_archive_2026Q1.db

# Verify archived records (hash chain still intact)
ystar verify --db cieu_archive_2026Q1.db

# Set automatic retention policy
ystar config set retention.days 90
ystar config set retention.auto-archive true
```

**Features:**
- Automatic archiving based on age or size
- Compressed archives (gzip SQLite files)
- Tamper-evident verification works across archives
- S3/GCS upload for archived records

**Tests:** Archiving, compression, hash chain validation across split databases

---

### P3 — Future / Experimental

#### 9. Multi-Agent Causal Tracing
**Problem:** Violation happens in Agent C, but root cause was Agent A's faulty delegation

**Solution:**
```bash
ystar trace --violation seq=1774555489773712

# Output:
Violation: Agent C tried to read /etc/passwd
← Delegated from: Agent B (seq=1774555489773710)
← Delegated from: Agent A (seq=1774555489773705)
Root cause: Agent A delegated overly broad permissions (/etc included)
```

**Features:**
- Trace violations back through delegation chain
- Identify root cause agent
- Suggest governance rule fixes

**Implementation:**
- Causal chain analysis (inspiration: K9Audit's CausalChainAnalyzer)
- Graph traversal of delegation events
- LLM-assisted root cause analysis (optional)

**Tests:** Multi-agent scenarios with nested violations

---

#### 10. Kubernetes Sidecar Enforcement
**Problem:** Agents running in Kubernetes pods need governance without git hooks

**Solution:**
Deploy Y*gov as a sidecar container:
```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: agent
    image: myagent:latest
  - name: ygov-enforcer
    image: ystarlabs/ygov-sidecar:0.49.0
    env:
    - name: GOVERNANCE_CONTRACT_URL
      value: "https://config-server/AGENTS.md"
```

**Features:**
- All tool calls proxied through sidecar
- Centralized CIEU records (streamed to compliance database)
- Dynamic governance updates (reload contract without pod restart)

**Tests:** Kubernetes integration tests (kind cluster)

---

## Decision Framework (Post-Launch)

**After 0.48.0 launches, prioritize based on:**

1. **User feedback volume** (which features are requested most?)
2. **Installation blockers** (if Windows users can't install → P0 fix)
3. **Enterprise sales traction** (if SOC 2 templates unlock deals → prioritize)
4. **Competitive pressure** (if competitor ships similar feature → accelerate)

**Feedback collection channels:**
- GitHub issues (feature requests)
- Show HN comments
- Direct emails (enterprise inquiries)
- Analytics (which `ystar` commands are used most?)

---

## Estimated Timeline (Tentative)

| Feature | Priority | Est. Effort | Target |
|---------|----------|-------------|--------|
| Direct Python API | P0 | 2 weeks | v0.49.0 |
| Windows Native Support | P0 | 1 week | v0.49.0 |
| Delegation Chain Viz | P1 | 1 week | v0.49.0 |
| Performance < 0.03ms | P1 | 1 week | v0.49.0 |
| Real-Time Dashboard | P1 | 2 weeks | v0.50.0 (too large) |
| Policy Templates | P2 | 1 week | v0.49.0 or v0.50.0 |
| Integration Adapters | P2 | 2 weeks | v0.50.0 |
| CIEU Archive | P2 | 1 week | v0.49.0 |
| Causal Tracing | P3 | 3 weeks | v0.51.0+ |
| K8s Sidecar | P3 | 3 weeks | v0.52.0+ |

**v0.49.0 MVP:** Direct API + Windows support + delegation viz + performance (5 weeks total)

---

## Success Metrics for 0.49.0

**Adoption:**
- 500+ PyPI downloads in first week (10x growth from 0.48.0)
- 50+ GitHub stars
- 5+ external contributors

**Quality:**
- Zero P0 bugs in first 2 weeks
- <5% installation failure rate (down from ~15% in 0.48.0)
- All 559 existing tests pass + 100 new tests

**Performance:**
- `check()` latency: <0.03ms (40% improvement)
- CIEU write latency: <0.5ms (no regression)

**Enterprise traction:**
- 3+ enterprise evaluation conversations
- 1+ enterprise pilot deployment

---

## Open Questions (To Resolve Before Implementation)

1. **API Design:** Should `Governance.from_file()` use YAML, TOML, or keep Markdown?
2. **Windows Hooks:** Python-based hooks vs. native .exe shim?
3. **Dashboard:** Self-hosted only, or offer cloud-hosted version?
4. **Templates:** Ship as code or fetch from remote registry?
5. **Pricing:** Keep 0.49.0 fully MIT, or introduce "Pro" tier for dashboard?

**Resolution:** Board decision after 0.48.0 user feedback analysis.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking changes for existing users | Low | High | Maintain backward compatibility, deprecation warnings |
| Windows support increases test complexity | High | Medium | Automate Windows CI, comprehensive testing |
| Dashboard becomes scope creep | Medium | High | Ship minimal viable dashboard, iterate based on feedback |
| Performance optimization regresses accuracy | Low | Critical | Extensive regression testing, benchmark suite |
| User feedback contradicts roadmap | Medium | Medium | Flexible prioritization, weekly re-evaluation |

---

## Communication Plan

**When to share this roadmap:**
- After 0.48.0 launches (don't distract from current release)
- After first week of user feedback (validate priorities)
- As GitHub issue: "Roadmap 0.49.0 — Request for Comments"

**Where to share:**
- GitHub Discussions (pin to top)
- Show HN follow-up comment (if 0.48.0 post gets traction)
- Email to early enterprise users

**Feedback loop:**
- Weekly roadmap review (CEO + CTO)
- Adjust priorities based on GitHub issue votes
- Monthly public roadmap update

---

**Next Steps:**
1. Launch 0.48.0
2. Monitor feedback for 1 week
3. Lock 0.49.0 priorities
4. Begin implementation (CTO + community contributors)

---

**Draft prepared by:** CEO (Aiden)  
**Review needed from:** CTO (技术可行性), CMO (市场定位), CSO (企业需求)  
**Board approval required:** Yes (before public communication)
