# K9Audit / OpenClaw Capability Gap Analysis

**Analyst:** Maya Patel (eng-governance)  
**Date:** 2026-04-13 00:45 EDT  
**Authority:** CEO (Aiden) directive  
**K9Audit Repository:** https://github.com/liuhaotian2024-prog/K9Audit (commit: latest, ~12.2K LoC)  
**Y*gov Repository:** /Users/haotianliu/.openclaw/workspace/Y-star-gov/  
**Status:** READ-ONLY analysis (no modifications to K9Audit)

---

## Executive Summary

K9Audit provides **4 core capabilities** that Y*gov + gov-mcp + ystar-company governance infrastructure **partially covers**. Key findings:

**GAPS FOUND:**
1. **Causal Chain Tracing** — K9Audit has full chain reconstruction; Y*gov only has delta/counterfactual queries (no backward chain walk)
2. **Secret Scrubbing** — K9Audit has 7 regex patterns + file skip lists; ystar-company secretary pipeline Step 11 is stub
3. **Repo Residue Audit** — K9Audit has 7 residue rules (superseded files, orphaned artifacts); Y*gov has no equivalent
4. **@k9 Decorator Pattern** — K9Audit uses decorator for CIEU recording; Y*gov uses MCP server hooks (different paradigm)

**P0 RECOMMENDATIONS (Top 3):**
1. **Backport Secret Scrubbing** to Secretary pipeline (P0, 2d estimate)
2. **Add Causal Chain Backward Walk** to CausalEngine (P0, 5d estimate)
3. **Build Repo Residue Scanner** for git audit (P1, 3d estimate)

---

## 1. K9Audit Capabilities (Detailed Inventory)

### 1.1 CausalChainAnalyzer (`k9log/causal_analyzer.py`)

**Purpose:** Build causal DAG from CIEU logs, trace root causes, find data dependencies.

**Key Features:**
- **CIEU record merge:** PreToolUse + OUTCOME records merged by `tool_use_id`
- **Causal DAG construction:**
  - Nodes: skill, agent_id, timestamp, passed, violations, execution_error, stdout/stderr
  - Edges: temporal (step N → step N+1) + data dependencies (output → input file paths)
- **Root cause analysis:** Walk backward from failure node to find causal chain
- **Execution failure tracking:** Separate tracking for hook violations vs execution errors
- **Data dependency detection:** `_find_data_dependencies()` extracts file paths from tool params/results

**Core Methods:**
```python
build_causal_dag() → {'nodes': [...], 'edges': [...], 'metadata': {...}}
find_root_cause(failure_node_id) → causal chain (backward walk)
_find_data_dependencies(node_idx, nodes) → edges with type='data_dependency'
```

**Evidence Location:** `/tmp/K9Audit/k9log/causal_analyzer.py` lines 1-100+

---

### 1.2 Auditor (`k9log/auditor.py`)

**Purpose:** Static analysis of AI-written codebases without execution.

**Key Features:**

**1. Secret Detection (7 patterns):**
```python
SECRET_PATTERNS = [
    r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([A-Za-z0-9_\-]{16,})',  # api_key
    r'(?i)(secret[_-]?key|secret)\s*[=:]\s*["\']?([A-Za-z0-9_\-]{16,})', # secret
    r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{4,})["\']',      # password
    r'(?i)(token|access_token|auth_token)\s*[=:]\s*["\']?([A-Za-z0-9_\-\.]{16,})', # token
    r'sk-[A-Za-z0-9]{32,}',                                            # openai_key
    r'ghp_[A-Za-z0-9]{36}',                                           # github_token
    r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',                        # private_key
]
```

**2. Staging URL Detection:**
- `staging.internal`, `.staging.`, `localhost`, `127.0.0.1`, `192.168.*`, `10.0.*`

**3. File/Directory Skip Lists:**
```python
SKIP_FILES = {
    "auditor.py", "k9_live_test.py", "hook.py",  # tool internals
    "main.py", "openclaw.py",  # server infra / examples
}
SKIP_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', 'dist', 'build', '.next',
    'coverage', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'site-packages'
}
```

**4. Finding Severity Model:**
```python
@dataclass
class Finding:
    severity: str     # HIGH / MEDIUM / LOW
    check: str        # imports / secrets / staging / scope / constraints
    title: str
    detail: str
    file: str
    line: Optional[int]
    command: Optional[str]
```

**Evidence Location:** `/tmp/K9Audit/k9log/auditor.py` lines 1-100

---

### 1.3 Repo Residue Audit (`k9_repo_audit.py`)

**Purpose:** Detect AI agent iteration artifacts that should have been cleaned up.

**7 Residue Rules:**

| Rule ID | Pattern | Example | Severity |
|---------|---------|---------|----------|
| SUPERSEDED | `*_fixed.py`, `*_v2.py`, `*_old.py` alongside original | `utils.py` + `utils_v2.py` | HIGH |
| ORPHANED_TXT | `.txt` files not referenced in any `.md` | `notes.txt` (no .md mentions it) | MEDIUM |
| ARTIFACT | Office temp files, `.bak`, `.tmp` | `~$report.docx`, `config.bak` | MEDIUM |
| ORPHANED_JSONL | `.jsonl` without corresponding `.md` case doc | `trace.jsonl` (no case doc) | LOW |
| UNREFERENCED_SCRIPT | Root-level `.py` not in README | `test_temp.py` (not in README.md) | MEDIUM |
| ENCODING_ISSUE | Files with encoding errors | (not shown in excerpt) | HIGH |
| DUPLICATE_CONFIG | (not shown in excerpt) | (not shown in excerpt) | MEDIUM |

**CIEU Integration:**
- Uses `@k9` decorator to record audit results as CIEU events
- Each violation emits `deny_content=["VIOLATION"]` CIEU record
- Produces HTML evidence report via `k9log report --output case_004_evidence.html`

**Evidence Location:** `/tmp/K9Audit/k9_repo_audit.py` lines 1-100

---

### 1.4 @k9 Decorator + CIEU Engine (`k9log/core.py`)

**Purpose:** Automatic CIEU recording via Python decorator.

**Key Features:**

**1. Decorator Syntax:**
```python
@k9(
    deny_content=["VIOLATION"],
    rule_id={"enum": ["SUPERSEDED", "ORPHANED_TXT"]},
)
def audit_file(file_path: str, rule_id: str, verdict: str) -> dict:
    return {"file": file_path, "verdict": verdict}
```

**2. Constraint Schema Inference ("Magic"):**
- Parses function AST to infer constraints from docstrings / type hints
- Persists suggestions to `~/.k9log/config/{skill_name}.json`
- Avoids repeat suggestions via `~/.k9log/magic_seen/{skill_name}.seen`

**3. CIEU Event Structure:**
- **U_t (User Intent):** skill name, params (redacted)
- **X_t (Context):** agent_id, agent_type, timestamp, tool_use_id, hostname
- **Y_t+1 (Outcome):** result (redacted), stdout, stderr, error
- **R_t+1 (Rule Check):** passed, violations, execution_error

**4. Log Level Control:**
- `K9LOG_LEVEL=DEBUG` — per-call trace
- `K9LOG_LEVEL=INFO` — violation summaries only (default)
- `K9LOG_LEVEL=OFF` — suppress all diagnostic output

**Evidence Location:** `/tmp/K9Audit/k9log/core.py` lines 1-150

---

### 1.5 OpenClaw Adapter (`k9log/openclaw_adapter/`)

**Purpose:** Map OpenClaw tool names → ActionClass + facts extractor.

**Architecture:**

**1. Deterministic Lookup Table (`mapping.py`):**
```python
EXACT = {
    "bash": ("EXECUTE", "command_from_args"),
    "file_write": ("WRITE", "path_from_args"),
    "http_request": ("NETWORK", "url_to_domain"),
    "transfer_money": ("TRANSFER", "transfer_facts"),
    # ... 62 total mappings
}
KEYWORD_FALLBACK = [
    ("transfer", "TRANSFER", "transfer_facts"),
    ("delete", "DELETE", "path_from_args"),
    # ... 24 fallback rules
]
```

**2. Facts Extractors (`normalize.py`):**
- `path_from_args`: Extract file path from tool params
- `command_from_args`: Extract command string
- `url_to_domain`: Extract domain from URL
- `transfer_facts`: Extract amount, from_account, to_account

**Evidence Location:** `/tmp/K9Audit/k9log/openclaw_adapter/mapping.py`, `normalize.py`

---

## 2. Y*gov / gov-mcp / ystar-company Current Capabilities

### 2.1 Causal Engine (`Y-star-gov/ystar/governance/causal_engine.py`)

**Implemented:**
- ✅ Pearl Level 2 (Intervention): `P(Y|do(X))` with backdoor adjustment
- ✅ Pearl Level 3 (Counterfactual): 3-step procedure (Abduction → Action → Prediction)
- ✅ Structural Causal Model (SCM): W → O → H → S (Wiring → Obligations → Health → Suggestions)
- ✅ `CausalGraph` class: d-separation, backdoor criterion
- ✅ `BackdoorAdjuster`: stratified adjustment formula
- ✅ `CounterfactualEngine`: `query_counterfactual(observation, intervention)`
- ✅ Causal Discovery: PC algorithm, DirectLiNGAM

**GAP vs K9Audit:**
- ❌ **No backward chain walk:** Can answer "what if X changed" but can't trace "why did X fail" by walking CIEU log backward
- ❌ **No data dependency tracking:** Doesn't extract file paths from tool params/results to build dependency edges
- ⚠️ **Different paradigm:** Y*gov focuses on governance cycle (W→O→H→S), K9Audit focuses on tool execution chain

**Gap Severity:** P0 — Backward causal chain tracing is needed for root cause analysis of obligation failures

---

### 2.2 Secret Scrubbing / Redaction

**K9Audit Implementation:**
- 7 regex patterns (API keys, tokens, passwords, private keys)
- File content scanning across `.py`, `.js`, `.json`, `.yaml`, `.env`, etc.
- SKIP_FILES / SKIP_DIRS to avoid false positives

**Y*gov Implementation:**
- ❌ **Not implemented** — Secretary pipeline Step 11 is documented as "secret scrubbing (stub)"
- ⚠️ CIEU redaction exists (`k9log/redact.py` in K9Audit) but not integrated into Y*gov CIEU store

**ystar-company Implementation:**
- ❌ **Not found** — Grep for "secret|scrub|redact" found only mentions in:
  - `reports/p1_omission_rate_analysis_20260413.md` (documentation)
  - `reports/secretary_curate_impl_20260413.md` (Step 11 stub)
  - Memory/knowledge base references (no actual code)

**Gap Severity:** P0 — Secretary Step 11 must be implemented before production use (prevents API key leaks in CIEU logs)

---

### 2.3 Repo Residue Audit

**K9Audit Implementation:**
- 7 residue rules (SUPERSEDED, ORPHANED_TXT, ARTIFACT, etc.)
- Full repository scan excluding `.git`, `__pycache__`, `node_modules`
- CIEU recording of each violation
- HTML evidence report generation

**Y*gov Implementation:**
- ❌ **Not implemented** — No equivalent residue scanning
- ⚠️ git status / diff exist in `governance_boot.sh` but only for uncommitted changes, not residue patterns

**ystar-company Implementation:**
- ❌ **Not found** — No residue audit scripts
- ⚠️ CEO/Board manually check for residue during amendment reviews (not automated)

**Gap Severity:** P1 — Useful for detecting agent iteration artifacts, but not blocking for core governance

---

### 2.4 @k9 Decorator vs MCP Hook Model

**K9Audit Pattern:**
- Decorator on Python functions: `@k9(deny_content=["X"]) def skill(...): ...`
- CIEU recording happens at function entry/exit
- Constraint checking embedded in decorator

**Y*gov Pattern:**
- MCP server hooks: `gov-mcp` server intercepts tool calls via SSE/stdio
- CIEU recording happens in MCP server before/after tool execution
- Constraint checking via `boundary_enforcer.py` + session config rules

**Paradigm Comparison:**

| Aspect | K9Audit @k9 | Y*gov gov-mcp |
|--------|-------------|---------------|
| **Granularity** | Python function | MCP tool call |
| **Coverage** | Only decorated functions | All tool calls (universal) |
| **Portability** | Python-only | Language-agnostic (MCP protocol) |
| **Deployment** | Modify source code | Hook into runtime |
| **AI Agent Support** | Requires Python agent | Supports any MCP client |

**Gap Severity:** N/A — Different design choices, not a gap. Y*gov's MCP model is **more general** than K9Audit's decorator model.

---

## 3. Gap Summary Table

| Capability | K9Audit | Y*gov | ystar-company | Gap? | Priority | Estimate |
|------------|---------|-------|---------------|------|----------|----------|
| **Causal Chain Backward Walk** | ✅ Full | ❌ No | N/A | **YES** | **P0** | **5d** |
| **Causal Counterfactual** | ❌ No | ✅ Full | N/A | NO (Y*gov ahead) | — | — |
| **Secret Scrubbing** | ✅ 7 patterns | ❌ No | ❌ Stub | **YES** | **P0** | **2d** |
| **Repo Residue Audit** | ✅ 7 rules | ❌ No | ❌ No | **YES** | **P1** | **3d** |
| **Data Dependency Tracking** | ✅ File paths | ❌ No | N/A | **YES** | **P1** | **3d** |
| **@k9 Decorator** | ✅ Full | N/A | N/A | NO (paradigm diff) | — | — |
| **MCP Hook Model** | ❌ No | ✅ Full | N/A | NO (Y*gov ahead) | — | — |
| **Obligation Fulfiller Contract** | ❌ No | ❌ No | ❌ No | **YES** | **P0** | **4d** (Task 2) |

---

## 4. Top-3 P0 Implementation Paths

### 4.1 P0-1: Secret Scrubbing for Secretary Pipeline (2d)

**Backport from:** `K9Audit/k9log/auditor.py` lines 58-66 (SECRET_PATTERNS)

**Integration Point:** `ystar-company/scripts/secretary_curate.py` Step 11

**Implementation:**

```python
# ystar-company/scripts/secretary_curate.py (add after Step 10)

SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([A-Za-z0-9_\-]{16,})', 'api_key'),
    (r'(?i)(secret[_-]?key|secret)\s*[=:]\s*["\']?([A-Za-z0-9_\-]{16,})', 'secret'),
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{4,})["\']', 'password'),
    (r'(?i)(token|access_token|auth_token)\s*[=:]\s*["\']?([A-Za-z0-9_\-\.]{16,})', 'token'),
    (r'sk-[A-Za-z0-9]{32,}', 'openai_key'),
    (r'ghp_[A-Za-z0-9]{36}', 'github_token'),
    (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----', 'private_key'),
]

def step_11_secret_scrub(session_data: dict, cieu_store) -> dict:
    """
    Scan all CIEU events + session artifacts for secrets.
    Emit CIEU violation for each match.
    Return dict with scrub_count, violation_count.
    """
    findings = []
    
    # Scan CIEU log (last 1000 events)
    events = cieu_store.query_events(limit=1000, sort_desc=True)
    for ev in events:
        payload_str = json.dumps(ev.get('U_t', {})) + json.dumps(ev.get('Y_t+1', {}))
        for pattern, secret_type in SECRET_PATTERNS:
            matches = re.findall(pattern, payload_str)
            if matches:
                findings.append({
                    "event_id": ev.get("event_id"),
                    "secret_type": secret_type,
                    "match_count": len(matches),
                    "severity": "HIGH",
                })
    
    # Scan session artifacts (knowledge/, reports/, memory/)
    artifact_dirs = ["knowledge/", "reports/", "memory/"]
    for dir_path in artifact_dirs:
        for fpath in Path(dir_path).rglob("*"):
            if fpath.suffix in {'.md', '.json', '.yaml', '.py', '.sh'}:
                try:
                    content = fpath.read_text(encoding='utf-8', errors='ignore')
                    for pattern, secret_type in SECRET_PATTERNS:
                        matches = re.findall(pattern, content)
                        if matches:
                            findings.append({
                                "file": str(fpath),
                                "secret_type": secret_type,
                                "match_count": len(matches),
                                "severity": "HIGH",
                            })
                            # Emit CIEU violation
                            cieu_store.add_event({
                                "event_type": "SECRET_DETECTED",
                                "actor_id": "secretary",
                                "severity": "HIGH",
                                "details": {"file": str(fpath), "secret_type": secret_type},
                            })
                except Exception as e:
                    continue
    
    return {
        "step": "step_11_secret_scrub",
        "scrub_count": len([f for f in findings if "file" in f]),
        "violation_count": len(findings),
        "findings": findings,
    }
```

**Testing:**
- Create test files with fake API keys in `tests/fixtures/secrets/`
- Run Step 11, verify CIEU events emitted
- Verify no false positives on test suite code

**Acceptance Criteria:**
- [ ] 7 SECRET_PATTERNS implemented
- [ ] CIEU event emission on secret detection
- [ ] Skip list for `tests/`, `tools/`, `.venv/`
- [ ] Unit test: 100% pattern coverage
- [ ] Dry-run on ystar-company repo: 0 false positives

**Estimated Time:** 2 days (1d implementation + 1d testing + false positive tuning)

---

### 4.2 P0-2: Causal Chain Backward Walk (5d)

**Backport from:** `K9Audit/k9log/causal_analyzer.py` `find_root_cause()` method

**Integration Point:** `Y-star-gov/ystar/governance/causal_engine.py` — new module `causal_trace.py`

**Implementation:**

```python
# Y-star-gov/ystar/governance/causal_trace.py

from typing import List, Dict, Tuple, Optional
from ystar.governance.cieu_store import CIEUStore

@dataclass
class CausalNode:
    event_id: str
    timestamp: float
    event_type: str
    tool_name: str
    actor_id: str
    passed: bool
    violations: List[str]
    execution_error: Optional[str]
    params: dict
    result: dict

@dataclass
class CausalEdge:
    from_event: str
    to_event: str
    edge_type: str  # "temporal" | "data_dependency" | "obligation_trigger"
    weight: float

class CausalChainTracer:
    """
    Build causal DAG from CIEU events, trace backward to find root causes.
    
    Similar to K9Audit CausalChainAnalyzer but integrated with Y*gov CIEU schema.
    """
    
    def __init__(self, cieu_store: CIEUStore):
        self.cieu = cieu_store
        self.nodes: List[CausalNode] = []
        self.edges: List[CausalEdge] = []
        self._build_dag()
    
    def _build_dag(self):
        """Build DAG from last 5000 CIEU events."""
        events = self.cieu.query_events(limit=5000, sort_desc=True)
        
        # Create nodes
        for ev in events:
            node = CausalNode(
                event_id=ev["event_id"],
                timestamp=ev["timestamp"],
                event_type=ev.get("event_type", "unknown"),
                tool_name=ev.get("U_t", {}).get("skill", "unknown"),
                actor_id=ev.get("X_t", {}).get("agent_id", "unknown"),
                passed=ev.get("R_t+1", {}).get("passed", True),
                violations=ev.get("R_t+1", {}).get("violations", []),
                execution_error=ev.get("R_t+1", {}).get("execution_error"),
                params=ev.get("U_t", {}).get("params", {}),
                result=ev.get("Y_t+1", {}).get("result", {}),
            )
            self.nodes.append(node)
        
        # Create edges (temporal + data dependencies)
        for i in range(len(self.nodes) - 1):
            # Temporal edge
            self.edges.append(CausalEdge(
                from_event=self.nodes[i].event_id,
                to_event=self.nodes[i+1].event_id,
                edge_type="temporal",
                weight=1.0,
            ))
            
            # Data dependency edge (if tool writes file, next tool reads it)
            self.edges.extend(self._find_data_dependencies(i, i+1))
    
    def _find_data_dependencies(self, from_idx: int, to_idx: int) -> List[CausalEdge]:
        """Extract file path dependencies between two nodes."""
        edges = []
        from_node = self.nodes[from_idx]
        to_node = self.nodes[to_idx]
        
        # Extract output paths from from_node
        output_paths = set()
        if from_node.tool_name in {"file_write", "write_file", "bash"}:
            if "file_path" in from_node.params:
                output_paths.add(from_node.params["file_path"])
            if "command" in from_node.params:
                # Parse "echo X > file.txt" patterns
                cmd = from_node.params["command"]
                if ">" in cmd:
                    parts = cmd.split(">")
                    if len(parts) == 2:
                        output_paths.add(parts[1].strip())
        
        # Extract input paths from to_node
        input_paths = set()
        if to_node.tool_name in {"file_read", "read_file", "bash"}:
            if "file_path" in to_node.params:
                input_paths.add(to_node.params["file_path"])
            if "command" in to_node.params:
                # Parse "cat file.txt" patterns
                cmd = to_node.params["command"]
                if "cat " in cmd or "grep " in cmd or "python" in cmd:
                    words = cmd.split()
                    for w in words:
                        if w.endswith(".py") or w.endswith(".md") or w.endswith(".json"):
                            input_paths.add(w)
        
        # Create edges for overlapping paths
        for out_path in output_paths:
            for in_path in input_paths:
                if out_path == in_path:
                    edges.append(CausalEdge(
                        from_event=from_node.event_id,
                        to_event=to_node.event_id,
                        edge_type="data_dependency",
                        weight=2.0,  # higher weight than temporal
                    ))
        
        return edges
    
    def find_root_cause(self, failure_event_id: str, max_depth: int = 10) -> List[CausalNode]:
        """
        Walk backward from failure event to find causal chain.
        
        Returns chain of nodes from root cause to failure (chronological order).
        """
        # Find failure node
        failure_node = next((n for n in self.nodes if n.event_id == failure_event_id), None)
        if failure_node is None:
            return []
        
        # Backward BFS
        visited = set()
        chain = []
        queue = [(failure_node, 0)]
        
        while queue:
            node, depth = queue.pop(0)
            if depth > max_depth:
                break
            if node.event_id in visited:
                continue
            visited.add(node.event_id)
            chain.append(node)
            
            # Find parent edges (reverse direction)
            parent_edges = [e for e in self.edges if e.to_event == node.event_id]
            # Prioritize data dependencies over temporal
            parent_edges.sort(key=lambda e: -e.weight)
            
            for edge in parent_edges[:3]:  # max 3 parents per node
                parent_node = next((n for n in self.nodes if n.event_id == edge.from_event), None)
                if parent_node:
                    queue.append((parent_node, depth + 1))
        
        # Reverse to get chronological order
        return list(reversed(chain))
    
    def explain_failure(self, failure_event_id: str) -> str:
        """Generate human-readable causal chain explanation."""
        chain = self.find_root_cause(failure_event_id)
        if not chain:
            return "No causal chain found."
        
        lines = [f"Causal Chain ({len(chain)} steps):"]
        for i, node in enumerate(chain):
            status = "✅ PASS" if node.passed else "❌ FAIL"
            lines.append(f"  {i+1}. [{status}] {node.event_type} — {node.tool_name} (actor={node.actor_id})")
            if node.violations:
                lines.append(f"      Violations: {', '.join(node.violations)}")
            if node.execution_error:
                lines.append(f"      Error: {node.execution_error[:100]}")
        
        return "\n".join(lines)
```

**Integration with OmissionEngine:**

```python
# Y-star-gov/ystar/governance/omission_engine.py (add method)

def diagnose_obligation_failure(self, obligation_id: str) -> str:
    """
    Use causal tracing to explain why an obligation wasn't fulfilled.
    
    Returns human-readable causal chain from obligation creation to expiry.
    """
    from ystar.governance.causal_trace import CausalChainTracer
    
    # Find obligation
    ob = self.store.get_obligation(obligation_id)
    if ob is None:
        return f"Obligation {obligation_id} not found."
    
    # Find CIEU event that created the obligation
    events = self.cieu_store.query_events(filters={"obligation_id": obligation_id}, limit=100)
    if not events:
        return f"No CIEU events found for obligation {obligation_id}."
    
    # Build causal chain
    tracer = CausalChainTracer(self.cieu_store)
    
    # Find most recent violation event
    violation_events = [e for e in events if e.get("event_type") == "omission_violation"]
    if violation_events:
        failure_id = violation_events[-1]["event_id"]
        return tracer.explain_failure(failure_id)
    else:
        return f"Obligation {obligation_id} expired without violation CIEU event."
```

**Testing:**
- Create test CIEU log with 50 events forming a chain
- Inject 3 failures at different depths
- Verify `find_root_cause()` returns correct chain
- Verify data dependency edges created correctly

**Acceptance Criteria:**
- [ ] `CausalChainTracer` class implemented
- [ ] `find_root_cause()` backward walk works
- [ ] Data dependency extraction (file paths)
- [ ] Integration with OmissionEngine `diagnose_obligation_failure()`
- [ ] Unit tests: 100% coverage of edge cases
- [ ] Performance: <1s for 5000-event DAG

**Estimated Time:** 5 days (2d implementation + 2d testing + 1d integration with OmissionEngine)

---

### 4.3 P1-1: Repo Residue Audit Scanner (3d)

**Backport from:** `K9Audit/k9_repo_audit.py` (7 residue rules)

**Integration Point:** New script `ystar-company/scripts/repo_residue_audit.py`

**Implementation:**

```python
#!/usr/bin/env python3
"""
Repo Residue Audit — Detect AI agent iteration artifacts.

Adapted from K9Audit/k9_repo_audit.py for Y* Bridge Labs use.
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple

# 7 Residue Rules
SUPERSEDED_PATTERN = re.compile(r'(.+)(_fixed|_v\d+|_old|_backup|_copy|_bak)(\.py)$')
ARTIFACT_PATTERNS = ['~$*', '*.bak', '*.tmp', '*.swp', '*_backup.*']

def rule_1_superseded(repo_root: Path) -> List[Tuple[str, str]]:
    """Find *_fixed.py, *_v2.py, *_old.py alongside original."""
    violations = []
    py_files = list(repo_root.rglob("*.py"))
    py_stems = {f.stem: f for f in py_files}
    
    for f in py_files:
        match = SUPERSEDED_PATTERN.match(f.name)
        if match:
            base_name = match.group(1)
            if base_name in py_stems:
                violations.append((str(f), f"Superseded file (original: {base_name}.py exists)"))
    
    return violations

def rule_2_orphaned_txt(repo_root: Path) -> List[Tuple[str, str]]:
    """Find .txt files not referenced in any .md file."""
    txt_files = set(repo_root.rglob("*.txt"))
    md_files = list(repo_root.rglob("*.md"))
    
    # Build set of referenced txt files
    referenced = set()
    for md in md_files:
        try:
            content = md.read_text(encoding='utf-8', errors='ignore')
            for txt in txt_files:
                if txt.name in content:
                    referenced.add(txt)
        except Exception:
            continue
    
    orphaned = txt_files - referenced
    return [(str(f), "Orphaned .txt file (not referenced in any .md)") for f in orphaned]

def rule_3_artifacts(repo_root: Path) -> List[Tuple[str, str]]:
    """Find Office temp files, .bak, .tmp."""
    violations = []
    for pattern in ARTIFACT_PATTERNS:
        for f in repo_root.rglob(pattern):
            violations.append((str(f), f"Artifact file (pattern: {pattern})"))
    return violations

def rule_4_orphaned_jsonl(repo_root: Path) -> List[Tuple[str, str]]:
    """Find .jsonl without corresponding .md case doc."""
    jsonl_files = list(repo_root.rglob("*.jsonl"))
    violations = []
    
    for jsonl in jsonl_files:
        # Expect case_NNN.jsonl to have case_NNN.md or case_NNN_report.md
        stem = jsonl.stem
        md_files = list(repo_root.rglob(f"{stem}.md")) + list(repo_root.rglob(f"{stem}_*.md"))
        if not md_files:
            violations.append((str(jsonl), "Orphaned .jsonl (no corresponding .md case doc)"))
    
    return violations

def rule_5_unreferenced_script(repo_root: Path) -> List[Tuple[str, str]]:
    """Find root-level .py scripts not mentioned in README."""
    readme = repo_root / "README.md"
    if not readme.exists():
        return []
    
    readme_content = readme.read_text(encoding='utf-8', errors='ignore')
    root_scripts = [f for f in repo_root.glob("*.py")]
    
    violations = []
    for script in root_scripts:
        if script.name not in readme_content:
            violations.append((str(script), f"Unreferenced root script (not in README.md)"))
    
    return violations

def main():
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    repo_root = repo_root.resolve()
    
    print(f"=== Repo Residue Audit: {repo_root} ===\n")
    
    all_violations = []
    
    rules = [
        ("SUPERSEDED", rule_1_superseded),
        ("ORPHANED_TXT", rule_2_orphaned_txt),
        ("ARTIFACT", rule_3_artifacts),
        ("ORPHANED_JSONL", rule_4_orphaned_jsonl),
        ("UNREFERENCED_SCRIPT", rule_5_unreferenced_script),
    ]
    
    for rule_id, rule_fn in rules:
        violations = rule_fn(repo_root)
        all_violations.extend([(rule_id, path, reason) for path, reason in violations])
        print(f"[{rule_id}] {len(violations)} violations")
    
    print(f"\n=== Total: {len(all_violations)} residue violations ===\n")
    
    for rule_id, path, reason in all_violations:
        print(f"  [{rule_id}] {path}")
        print(f"           → {reason}")
    
    sys.exit(0 if len(all_violations) == 0 else 1)

if __name__ == "__main__":
    main()
```

**Testing:**
- Create test repo with residue files
- Run script, verify all 5 rules detect violations
- Run on ystar-company repo, verify no false positives

**Acceptance Criteria:**
- [ ] 5 residue rules implemented (7 rules in K9Audit, 5 most useful ported)
- [ ] CLI interface: `python scripts/repo_residue_audit.py [path]`
- [ ] Exit code 0 if clean, 1 if violations found
- [ ] Unit tests: 100% rule coverage
- [ ] Dry-run on ystar-company: <10 false positives

**Estimated Time:** 3 days (1d implementation + 1d testing + 1d false positive tuning)

---

## 5. Hermes Methodology Integration

**Hermes 4-Section Format** (from SKILL.md in ystar-company):

All skill definitions follow:
1. **Trigger:** When/why to use the skill
2. **Procedure:** Step-by-step execution
3. **Principles:** Underlying reasoning
4. **Red Lines:** Common pitfalls

**Relevance to Gap Analysis:**

K9Audit capabilities can be **packaged as Hermes skills**:

**Skill: Secret Scrubbing**
- **Trigger:** Before session close, before git commit, before external release
- **Procedure:** Run Step 11 secret scrub → emit CIEU violations → reject commit if HIGH severity
- **Principles:** Prevent credential leaks; defense-in-depth (multiple scan points)
- **Red Lines:** Never skip on production branches; never auto-remediate (scrubbing = detection, not deletion)

**Skill: Causal Root Cause Analysis**
- **Trigger:** Obligation failure, circuit breaker ARM, CIEU violation spike
- **Procedure:** Run `CausalChainTracer.find_root_cause(failure_event_id)` → explain chain → identify fix point
- **Principles:** Backward causality (not forward guessing); data dependencies > temporal order
- **Red Lines:** Don't stop at first violation; trace to external trigger (Board decision / git event)

**Skill: Repo Residue Cleanup**
- **Trigger:** End of session, before PR merge, quarterly audit
- **Procedure:** Run `repo_residue_audit.py` → review violations → delete or document exceptions
- **Principles:** Iteration artifacts should not persist; documentation > code duplication
- **Red Lines:** Never auto-delete without human review; exceptions must be in `.residue_exceptions` file

---

## 6. License Compliance

**K9Audit License:** AGPL-3.0  
**Y*gov License:** MIT  
**Y* Bridge Labs License:** (private, Board-owned)

**AGPL-3.0 Implications:**
- **Cannot copy code verbatim** into Y*gov (MIT) without triggering AGPL viral clause
- **CAN extract patterns** (residue rules, regex patterns) as **facts** (not copyrightable)
- **CAN reimplement algorithms** (causal DAG construction) from **methodology** (not code)
- **MUST** include AGPL notice if any K9Audit code is directly used

**Recommendation for Gap Closure:**
- **Reimplement algorithms** from scratch in Y*gov codebase (clean-room)
- **Extract pattern definitions** (SECRET_PATTERNS list, residue rules) as configuration (not code)
- **Reference K9Audit as prior art** in Y*gov documentation
- **Do NOT copy-paste** K9Audit code into Y*gov or ystar-company repos

---

## 7. Conclusion

**Summary of Findings:**

K9Audit provides **4 capabilities** with **3 P0 gaps** in Y*gov ecosystem:

1. **Causal Chain Backward Walk** — P0, 5d estimate
2. **Secret Scrubbing** — P0, 2d estimate
3. **Repo Residue Audit** — P1, 3d estimate

**Next Steps (CEO Decision):**

If CEO approves gap closure:
1. Create task cards in `.claude/tasks/` for each P0 item
2. Assign to Maya (eng-governance) for items 1-2, Ryan (eng-platform) for item 3
3. Coordinate with Jordan (eng-domains) on AMENDMENT-012 integration (obligation fulfiller + remediation)
4. Target completion: Sprint 2 (2 weeks from 2026-04-13)

**End of Report**
