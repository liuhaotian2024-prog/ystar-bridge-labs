## Task: CZL-166 — Wire REWRITE transforms into 3 live block paths

Engineer: eng-kernel (Leo Chen)
Priority: P0
CZL Tracking: CZL-166
Tool-use cap: 15

### Context

Board red-team (2026-04-18) proved Y*gov blocks correctly (D7/D8/D9 PASS) but never REWRITEs.
The `auto_rewrite.py` module has 3 transforms but they only serve the commit-msg router path.
The 3 most-fired block sites have zero rewrite coverage. This is the "门卫+导游" gap —
governance blocks but doesn't help agents fix the compliance problem.

### Deliverable: 3 New RewriteTransform entries + integration wiring

All work in Y-star-gov repo: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/`

#### Transform 4: `bash_env_token_safe`

**File**: `ystar/rules/auto_rewrite.py` (append to SAFE_TRANSFORMS)

**Match**: `tool_name == "Bash"` AND command contains `.env` literal BUT the `.env` token appears
inside one of these safe contexts:
  - `os.environ` / `os.getenv` (Python env access, not file access)
  - Inside a string literal that is a variable name (e.g. `MY_APP.env.local` as a key)
  - Inside a comment (`#` prefixed line)
  - Inside an echo/print statement (not a file read/write of .env)

**Replacement function**: Return `{"_rewrite_safe": True, "_rewrite_mode": "bash_env_token_safe",
"_rewrite_suggestion": "Use os.environ['KEY'] or os.getenv('KEY') instead of reading .env files directly"}`

**Test case** (from red-team): `cat .env` should still DENY. `python3 -c "import os; os.environ.pop('.env_backup', None)"` should REWRITE-allow.

#### Transform 5: `write_boundary_redirect`

**File**: `ystar/rules/auto_rewrite.py` (append to SAFE_TRANSFORMS)

**Match**: `tool_name in ("Write", "Edit")` AND `params.get("file_path", "")` is outside agent's
allowed write paths. This transform does NOT auto-allow — it returns a suggestion.

**Replacement function**: 
1. Accept agent's allowed paths via params key `_agent_allowed_paths` (injected by boundary_enforcer before calling detector)
2. Extract the filename from the denied path via `os.path.basename()`
3. Pick the first allowed path that looks like a directory (ends with `/`) and join with filename
4. Return `{"_rewrite_safe": False, "_rewrite_mode": "write_boundary_redirect",
"_rewrite_suggestion": f"Redirect to {suggested_path} which is within your write scope"}`

Note: `_rewrite_safe: False` means this is a SUGGESTION, not an auto-allow. The deny still fires
but the deny message includes the suggestion.

**Test case** (from red-team): CEO Write to `/tmp/redteam_matrix.md` -> deny + suggestion
`reports/redteam_matrix.md` (first dir-like allowed path).

#### Transform 6: `czl159_header_autoinject`

**File**: `ystar/rules/auto_rewrite.py` (append to SAFE_TRANSFORMS)

**Match**: `tool_name == "Write"` AND path matches CZL-159 enforced prefixes (`reports/`,
`content/`, `knowledge/ceo/strategy/`) AND content is missing 1+ U-workflow signals
(research/synthesis/audience).

**Replacement function**:
1. Detect which signals are missing using these regexes (same as hook_ceo_pre_output.py):
   - research: `(source[s]?[:\s]|cite[ds]?[\s:]|per\s+\w|according\s+to|search|found\s+that|reference[ds]?|evidence|data\s+show|based\s+on|research|study|paper|article|empirical)`
   - synthesis: `(therefore|because|analysis|conclude[ds]?|lesson[s]?|insight[s]?|implication|root\s+cause|pattern|takeaway|diagnosis|framework|principle|synthesis|assessment)`
   - audience: `(audience|purpose|for\s+board|stakeholder|reader[s]?|intended\s+for|context\s+for|decision\s+maker|consumer|recipient)`
2. Build a header comment block with FILL lines only for missing signals:
```
# --- U-Workflow Compliance (auto-generated) ---
# Audience: [FILL: who reads this and why]
# Research: [FILL: cite sources or evidence]
# Synthesis: [FILL: your analysis/conclusion]
# ---
```
3. Return `{"_rewrite_safe": False, "_rewrite_mode": "czl159_header_autoinject",
"_rewrite_suggestion": header_block}`

Note: `_rewrite_safe: False` — injected into deny message as actionable guidance.
The agent sees the template and can re-submit with filled content.

**Test case** (from red-team): CEO Write to `reports/ceo/analysis.md` with body "The system works"
(missing all 3 signals) -> deny + full 3-line header template suggested.

### Integration Points (3 wiring changes)

#### Wire 1: `boundary_enforcer.py` `_check_write_boundary()` deny path (~line 630)

BEFORE returning the deny PolicyResult, inject allowed paths into params and call detector:
```python
from ystar.rules.auto_rewrite import auto_rewrite_detector, auto_rewrite_executor
_rw_params = dict(params)
_rw_params["_agent_allowed_paths"] = allowed  # list of allowed write paths
transform = auto_rewrite_detector(tool_name, _rw_params)
if transform and transform.mode == "write_boundary_redirect":
    meta = auto_rewrite_executor(transform, tool_name, _rw_params)
    suggestion = meta.get("_rewrite_suggestion", "")
    # Append suggestion to the deny reason string
```
Then include `suggestion` in the PolicyResult reason and in the Remediation.correct_steps.

#### Wire 2: `hook_wrapper.py` CZL-159 block (~line 185)

In the CZL-159 missing-signals block, BEFORE outputting the deny JSON, call:
```python
from ystar.rules.auto_rewrite import auto_rewrite_detector, auto_rewrite_executor
transform = auto_rewrite_detector("Write", tool_input)
if transform and transform.mode == "czl159_header_autoinject":
    meta = auto_rewrite_executor(transform, "Write", tool_input)
    _block_msg += f"\n\nAuto-fix template — prepend this to your content:\n{meta.get('_rewrite_suggestion', '')}"
```

#### Wire 3: Bash cannot_touch check — `hook.py` check_hook path

The `cannot_touch` token check lives in Y*gov's dimensions/check layer. The intercept point is
inside `check_hook()` where PolicyResult(allowed=False) is returned for token matches.

Find the exact site by tracing: `check_hook()` -> boundary checks -> where `cannot_touch` tokens
are matched against Bash command params. BEFORE the deny return, insert:
```python
from ystar.rules.auto_rewrite import auto_rewrite_detector, auto_rewrite_executor
transform = auto_rewrite_detector("Bash", params)
if transform and transform.mode == "bash_env_token_safe":
    meta = auto_rewrite_executor(transform, "Bash", params)
    if meta.get("_rewrite_safe"):
        return PolicyResult(allowed=True, reason=meta["_rewrite_mode"])
    # else: still deny but append suggestion
```

If the exact `cannot_touch` check site is hard to find in the dimensions layer, an acceptable
fallback is wiring into `hook_wrapper.py` BEFORE the `check_hook()` call — run
`auto_rewrite_detector("Bash", {"command": cmd})` and if `bash_env_token_safe` matches, annotate
params with `_rewrite_safe=True` so downstream checks skip the token.

### Acceptance Criteria

- [ ] 3 new RewriteTransform entries added to SAFE_TRANSFORMS in auto_rewrite.py
- [ ] Each transform has match_pattern + replacement_fn matching the spec above
- [ ] Wire 1: boundary_enforcer.py deny path includes redirect suggestion in reason string
- [ ] Wire 2: hook_wrapper.py CZL-159 deny includes header template in block message
- [ ] Wire 3: bash token safe context detected before cannot_touch deny fires
- [ ] All existing tests still pass: `cd /Users/haotianliu/.openclaw/workspace/Y-star-gov && python -m pytest --tb=short -q`
- [ ] Add 3 new test cases (one per transform) in `tests/test_auto_rewrite.py`
- [ ] No files outside `ystar/` and `tests/` modified
- [ ] NO git commit, NO git push, NO git add, NO git reset

### 5-Tuple Receipt Template (fill on completion)

```
Y*  = 3 REWRITE transforms wired into live block paths
Xt  = [describe state before changes]
U   = [list tool_uses with file:line references]
Yt+1 = [describe state after changes]
Rt+1 = [0 if all AC checked, else describe gap]
```

### Files In Scope

MODIFY:
- `ystar/rules/auto_rewrite.py` — add 3 transforms
- `ystar/adapters/boundary_enforcer.py` — wire redirect suggestion into deny path
- `ystar/adapters/hook.py` — wire bash_env_token_safe into cannot_touch path

CREATE (if not exists, else append):
- `tests/test_auto_rewrite.py`

READ-ONLY (for reference patterns):
- `scripts/hook_wrapper.py` — understand CZL-159 integration point (in ystar-company repo)
- `scripts/hook_ceo_pre_output.py` — regex patterns to reuse (in ystar-company repo)

DO NOT TOUCH:
- Any file outside Y-star-gov/ystar/ and Y-star-gov/tests/
- Any .md, .json, .yml config file
- No git operations of any kind
