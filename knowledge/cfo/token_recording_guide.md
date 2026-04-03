# Token Recording Guide — CFO Execution Manual

**Source:** AGENTS.md CFO Obligations章节  
**Moved to knowledge:** 2026-04-03（Constitutional cleanup）  
**Authority:** Y*gov OmissionEngine enforced

---

## Purpose

Record token usage after every Claude Code session for cost tracking and burn rate analysis.

## Constitutional Requirement

**Timing:** Within 10 minutes of session end  
**Enforcement:** HARD_OVERDUE if not recorded  
**Consequence:** CFO blocked from all unrelated work until complete

---

## Execution Command

### Basic Usage

```bash
python scripts/track_burn.py \
  --agent <agent_name> \
  --model <model> \
  --summary "<session summary>"
```

### Parameters

**--agent** (required)
- Agent role name
- Examples: `ystar-cfo`, `ystar-cto`, `ystar-ceo`, `ystar-cmo`, `ystar-cso`

**--model** (required)
- Model used in session
- Examples: `claude-sonnet-4-5`, `claude-opus-4-6`, `claude-haiku-4-5`

**--summary** (required)
- Brief session summary (1-2 sentences)
- What was accomplished
- Quote marks required if contains spaces

**--session-id** (optional)
- Session identifier for cross-referencing
- Auto-detected if not provided

**--project** (optional, default: ystar-company)
- Project name for cost allocation
- Examples: `ystar-company`, `Y-star-gov`

---

## Examples

### Example 1: CFO session recording

```bash
python scripts/track_burn.py \
  --agent ystar-cfo \
  --model claude-sonnet-4-5 \
  --summary "Completed cost_analysis_002 weekly burn rate report"
```

### Example 2: CTO session with session ID

```bash
python scripts/track_burn.py \
  --agent ystar-cto \
  --model claude-opus-4-6 \
  --session-id ystar-company_a1b2c3d4 \
  --summary "Fixed P0 bug in omission_engine.py, 563 tests passing"
```

### Example 3: Cross-project session

```bash
python scripts/track_burn.py \
  --agent ystar-cto \
  --model claude-sonnet-4-5 \
  --project Y-star-gov \
  --summary "Implemented cancel_obligation() mechanism"
```

---

## Data Recorded

The script automatically captures:

1. **Session metadata**
   - Timestamp
   - Agent ID
   - Model used
   - Session ID

2. **Token usage** (from session output)
   - Input tokens
   - Output tokens  
   - Total tokens
   - Cost estimate (based on model pricing)

3. **Session summary**
   - User-provided summary
   - Duration
   - Tool calls count

4. **Cost allocation**
   - Project
   - Category (development, research, operations)
   - Sprint/milestone if applicable

---

## Output Location

**Primary log:**
```
data/token_logs/YYYY-MM.jsonl
```

**Aggregated report:**
```
reports/cfo/burn_rate_YYYY-MM.md
```

**Dashboard update:**
```
reports/cfo/cost_dashboard.md
```

---

## Verification

After running track_burn.py, verify:

```bash
# Check latest entry
tail -1 data/token_logs/$(date +%Y-%m).jsonl | jq .

# Verify session was recorded
grep "<session_id>" data/token_logs/$(date +%Y-%m).jsonl
```

**Expected output:**
```json
{
  "timestamp": "2026-04-03T14:30:22",
  "agent": "ystar-cfo",
  "model": "claude-sonnet-4-5",
  "session_id": "ystar-company_xyz",
  "tokens": {
    "input": 15234,
    "output": 3421,
    "total": 18655
  },
  "cost_usd": 0.28,
  "summary": "Completed cost_analysis_002",
  "project": "ystar-company"
}
```

---

## Error Handling

### Error: "Session not found"

**Cause:** Session ID not detected automatically  
**Fix:** Provide explicit `--session-id`

### Error: "Model pricing not found"

**Cause:** Model not in pricing database  
**Fix:** Update `scripts/model_pricing.json` with new model

### Error: "Cannot write to log file"

**Cause:** Permissions or disk full  
**Fix:** Check file permissions, disk space

---

## Integration with Cost Analysis

Token recordings feed into:

1. **Weekly burn rate reports** (`cost_analysis_NNN`)
   - Aggregate by agent, model, project
   - Trend analysis week-over-week
   - Runway calculation

2. **Sprint cost allocation**
   - Cost per feature/sprint
   - Agent efficiency metrics
   - Model selection optimization

3. **Board financial reports**
   - Monthly burn summary
   - Budget variance analysis
   - Forecast adjustments

---

## Fulfillment Verification

**Y*gov checks:**
- File write event to `data/token_logs/*.jsonl`
- Timestamp within 10 minutes of session end
- Valid JSON format

**Obligation fulfilled when:**
- track_burn.py exits with code 0
- JSONL entry created
- CIEU records the write event

---

## Troubleshooting

### Script not found

```bash
# Verify script exists
ls -la scripts/track_burn.py

# If missing, restore from git
git checkout scripts/track_burn.py
```

### Python environment issues

```bash
# Activate correct environment
# (track_burn.py uses standard library only, no venv needed)
python --version  # Should be 3.10+
```

### Manual recording (if script fails)

```bash
# Append manually to JSONL
echo '{"timestamp":"2026-04-03T14:30:22","agent":"ystar-cfo",...}' >> data/token_logs/2026-04.jsonl
```

---

**Last updated:** 2026-04-03  
**Script location:** `scripts/track_burn.py`  
**Next review:** When token pricing changes
