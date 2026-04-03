# CTO Concept Scan — Y*gov Technical Concepts for HN Articles

**Date:** 2026-03-26
**Purpose:** Extract every article-worthy technical concept from Y*gov codebase for CMO content planning
**Target:** 20+ articles

---

## engine.py — Runtime Enforcement Engine

### 1. Concept: AST-whitelisted expression evaluator (FIX-2)
**What it is:** Replaced bare eval() with AST whitelist to prevent Python class hierarchy traversal RCE
**Why it's interesting for HN:** Demonstrates why `eval(expr, {"__builtins__": {}})` is NOT safe — attackers use `__class__.__bases__[0].__subclasses__()` to escape the sandbox
**Key code:** engine.py:223-286 (_safe_eval, _SAFE_AST_NODES, _BLOCKED_ATTRS)

### 2. Concept: Path traversal defense via abspath normalization (FIX-1)
**What it is:** Converts both whitelist and user input to absolute paths before comparison, blocking `./projects/../../../etc/passwd` attacks
**Why it's interesting for HN:** String prefix matching (`startswith()`) is insufficient for path whitelists — attackers abuse `..` traversal
**Key code:** engine.py:380-384 (only_paths enforcement with os.path.abspath)

### 3. Concept: Domain spoofing prevention (FIX-3)
**What it is:** Rejects multi-part subdomain prefixes in domain allowlists (e.g., `evil.com.api.github.com` masquerading as `api.github.com`)
**Why it's interesting for HN:** Subdomain validation is harder than it looks — single-dot check prevents sophisticated DNS-based social engineering
**Key code:** engine.py:194-219 (_domain_is_allowed)

### 4. Concept: Type confusion bypass (FIX-4)
**What it is:** Non-primitive parameter types can have custom `__str__` that shows innocent strings while carrying malicious payloads
**Why it's interesting for HN:** Even after string checks pass, the underlying object may not be a string — type safety is a missing layer in most policy engines
**Key code:** engine.py:288-305 (_validate_param_types, _PRIMITIVE_TYPES)

### 5. Concept: Phantom variable detection
**What it is:** When invariant references a variable absent from actual parameters, surface it as `phantom_variable` violation instead of silently skipping
**Why it's interesting for HN:** Silent failures are worse than errors — governance that doesn't run is governance that doesn't exist
**Key code:** engine.py:466-485 (phantom_variable in invariant checking)

### 6. Concept: Optional invariants for multi-agent systems
**What it is:** `optional_invariant` checks constraints only when variables exist; silent when absent (vs regular invariant that warns)
**Why it's interesting for HN:** Multi-agent systems pass different parameter subsets; conditional constraints need graceful degradation
**Key code:** engine.py:506-541 (optional_invariant dimension)

### 7. Concept: Six enforcement modes (EnforcementMode enum)
**What it is:** OBSERVE_ONLY / CHECK_AND_RETURN / FAIL_OPEN / FAIL_CLOSED / HOLD_FOR_APPROVAL / SIMULATE_ONLY — caller chooses enforcement semantics
**Why it's interesting for HN:** One check() function, six execution modes; separation of "判断" and "决策后果" is key to composable governance
**Key code:** engine.py:640-738 (EnforcementMode + enforce())

---

## dimensions.py — IntentContract Structure

### 8. Concept: Eight-dimensional constraint space
**What it is:** Every behavioral constraint expressible in natural language maps to 8 deterministic dimensions: deny / only_paths / deny_commands / only_domains / invariant / postcondition / field_deny / value_range
**Why it's interesting for HN:** Natural language policy is ambiguous; 8-dimensional predicate space is deterministic and testable
**Key code:** dimensions.py:69-110 (DIMENSION_NAMES, DIMENSION_LABELS, DIMENSION_HINTS)

### 9. Concept: Policy source trust hierarchy
**What it is:** CONSTITUTION > CONTRACT > GENERATED_MD > IMPORTED_MD > UNKNOWN — only top two levels are runtime-authoritative
**Why it's interesting for HN:** Markdown is for humans; contract objects are for machines; trust never auto-upgrades without approval gates
**Key code:** dimensions.py:112-150 (PolicySourceTrust class)

### 10. Concept: DelegationChain with monotonicity enforcement
**What it is:** Child contracts must be subsets of parent contracts (deny-lists grow, whitelists shrink); enforced via is_subset_of() check
**Why it's interesting for HN:** Prevents privilege escalation in agent delegation trees — child spawned with *more* permissions than parent is caught at runtime
**Key code:** dimensions.py:412-500 (IntentContract.is_subset_of)

### 11. Concept: Contract diff and semantic versioning
**What it is:** IntentContract.diff() computes added/removed/tightened/loosened constraints between two contract versions
**Why it's interesting for HN:** Code diffs show syntax changes; contract diffs show *semantic* changes to governance rules — critical for audit and version control
**Key code:** dimensions.py:239-316 (IntentContract.diff)

### 12. Concept: Obligation timing vs temporal constraints
**What it is:** `obligation_timing` = "you must do X within N seconds" (commitment deadline); `temporal` = "you can do X at most N times per window" (rate limit) — orthogonal dimensions
**Why it's interesting for HN:** Conflating frequency caps and deadlines is a common spec error; Y* separates them cleanly
**Key code:** dimensions.py:196-211 (obligation_timing field)

---

## nl_to_contract.py — LLM Translation Pipeline

### 13. Concept: LLM translation with deterministic fallback
**What it is:** Try Claude API to translate AGENTS.md → IntentContract JSON; if unavailable, fall back to regex parser with lower confidence score
**Why it's interesting for HN:** LLM-first but never LLM-only — degradation strategy ensures system doesn't break when API is down
**Key code:** nl_to_contract.py:105-131 (translate_to_contract with method="llm" or "regex")

### 14. Concept: Y*-validated contract drafts
**What it is:** LLM translation output goes through validate_contract_draft() before user confirmation — Y* kernel checks invariant syntax, value_range consistency, command truncation
**Why it's interesting for HN:** Don't trust LLM output blindly; run deterministic validation *before* human approval to catch obvious errors
**Key code:** nl_to_contract.py:196-347 (validate_contract_draft with errors/warnings/suggestions)

### 15. Concept: Semantic-layer contract validation
**What it is:** Detect value_range inversions (min > max), missing command suffixes (truncated `rm` → should be `rm -rf`), path semantic confusion (deny vs whitelist)
**Why it's interesting for HN:** LLMs make plausible-sounding mistakes; validation rules encode domain knowledge humans would catch in review
**Key code:** nl_to_contract.py:246-300 (value_range direction check, deny_commands truncation)

### 16. Concept: Human-in-the-loop confirmation with quality metrics
**What it is:** Show dimension coverage rate (N/8 active), error/warning counts, suggested improvements *before* asking "confirm [Y/n]"
**Why it's interesting for HN:** Good UX for governance: tell users what's missing, not just "is this correct?" — informed consent
**Key code:** nl_to_contract.py:350-393, 482-556 (format_validation_report, confirm_in_terminal)

---

## omission_engine.py — Deterministic Omission Detection

### 17. Concept: Soft/Hard two-phase obligation aging
**What it is:** PENDING → SOFT_OVERDUE (first violation, reminders) → HARD_OVERDUE (escalation, capability restrictions) — grace period before severe consequences
**Why it's interesting for HN:** Binary "pass/fail" is too harsh for real systems; graduated escalation gives agents recovery time
**Key code:** omission_engine.py:159-210 (soft_overdue → hard_overdue transition logic)

### 18. Concept: Action-triggered obligation creation
**What it is:** OmissionEngine doesn't poll for missing actions; obligations are *created* when trigger events occur, then tracked until fulfillment/expiry
**Why it's interesting for HN:** Event-driven governance is more efficient than continuous scanning; obligations appear only when needed
**Key code:** omission_engine.py:354-409 (_trigger_obligations from GovernanceEvent)

### 19. Concept: Obligation-first fulfillment check
**What it is:** _try_fulfill() runs on every incoming event *before* checking for new violations — paying debt takes priority
**Why it's interesting for HN:** Agents stuck in failure loops need a way out; checking fulfillment first creates recovery paths
**Key code:** omission_engine.py:334-351 (_try_fulfill matching event_type to required_event_types)

### 20. Concept: Deny closure on open obligations
**What it is:** can_close(entity_id) returns False if entity has PENDING/EXPIRED obligations with `deny_closure_on_open=True`
**Why it's interesting for HN:** Prevents premature task closure — can't mark "done" while critical obligations are unfulfilled
**Key code:** omission_engine.py:306-321 (can_close with escalation_policy check)

---

## cieu_store.py — CIEU Five-Tuple Audit Chain

### 21. Concept: SQLite WAL mode for concurrent write-safety
**What it is:** PRAGMA journal_mode=WAL allows multiple readers + one writer without blocking; PRAGMA synchronous=NORMAL balances crash-safety and performance
**Why it's interesting for HN:** SQLite isn't just a toy database — with correct pragmas, it's production-ready for audit logs
**Key code:** cieu_store.py:48-51 (_SCHEMA with PRAGMA settings)

### 22. Concept: FTS5 full-text search on governance logs
**What it is:** CREATE VIRTUAL TABLE cieu_fts USING fts5 enables keyword search across violations, commands, file paths without external search engine
**Why it's interesting for HN:** Governance logs need to be searchable ("show me all /etc violations") — FTS5 is built into SQLite, zero dependencies
**Key code:** cieu_store.py:108-133 (cieu_fts virtual table + sync triggers)

### 23. Concept: Merkle root session sealing (FIX-3)
**What it is:** seal_session() computes SHA-256(event_id_0 \n event_id_1 \n ...) and chains to previous session's root — tamper-evident audit trail
**Why it's interesting for HN:** Blockchain-like immutability without blockchain complexity; each seal cryptographically commits to all prior events
**Key code:** cieu_store.py:594-664 (seal_session with merkle_root chaining)

### 24. Concept: Complete call-site snapshot (FIX-1)
**What it is:** params_json (8KB cap), result_json (4KB cap), human_initiator, lineage_path stored per event — full forensic reconstruction
**Why it's interesting for HN:** Compliance audits ask "who initiated this?" — capturing human actor + delegation chain answers that question
**Key code:** cieu_store.py:86-95 (params_json, result_json, human_initiator, lineage_path columns)

### 25. Concept: NullCIEUStore explicit no-op pattern (FIX-2)
**What it is:** Instead of `cieu_store=None` (silent failure), use `NullCIEUStore()` (warns once, implements same interface)
**Why it's interesting for HN:** None-checks everywhere are code smell; null object pattern + warning clarifies "I know persistence is disabled"
**Key code:** cieu_store.py:763-818 (NullCIEUStore with UserWarning)

---

## hook.py — Claude Code Adapter

### 26. Concept: Light path vs full path automatic升级
**What it is:** If `.ystar_session.json` exists → enforce() (delegation chains, drift, CIEU); else → Policy.check() (basic rules) — zero config change needed
**Why it's interesting for HN:** Adaptive enforcement depth based on context; users get deeper governance as they opt in, not upfront
**Key code:** hook.py:212-245 (check_hook with _load_session_config() branching)

### 27. Concept: Tool name to Y* parameter mapping
**What it is:** _TOOL_PARAMS dict maps `Write`→`file_path`, `Bash`→`command`, `WebFetch`→`url` — adapter knows Claude Code's schema
**Why it's interesting for HN:** Ecosystem adapters need semantic translation layers; this is Y*'s "Rosetta Stone" for Claude Code
**Key code:** hook.py:34-51 (_TOOL_PARAMS mapping)

### 28. Concept: Obligation triggers from tool calls
**What it is:** After check() passes, _process_obligation_triggers() creates new obligations (e.g., "update knowledge after web_search") — governance isn't just blocking, it's prescriptive
**Why it's interesting for HN:** Reactive governance (block bad actions) + proactive governance (require follow-up actions) in one hook
**Key code:** hook.py:477-540 (_process_obligation_triggers with ObligationTrigger framework)

---

## meta_agent.py — Path A Self-Governance

### 29. Concept: GovernanceSuggestion IS IntentContract
**What it is:** Meta-agent's suggestions are themselves contracts: target (postcondition), range (only_paths), confidence (fp_tolerance), deadline (obligation_timing)
**Why it's interesting for HN:** Path A can't escape its own rules — suggestions are contracts, contracts constrain Path A, circular accountability
**Key code:** meta_agent.py:1-32 (docstring design philosophy)

### 30. Concept: Constitutional hash for governance lineage
**What it is:** IntentContract.hash = sha256(PATH_A_AGENTS.md content); every Path A action traceable to constitutional text version
**Why it's interesting for HN:** "宪法以代码为核心" realized — governance rules have cryptographic lineage like git commits
**Key code:** meta_agent.py:64-79 (constitution_hash from file content)

### 31. Concept: Postcondition obligations for meta-agent
**What it is:** After Path A executes接线, OmissionStore gets obligation: "GovernanceLoop must observe improvement within deadline_secs"
**Why it's interesting for HN:** Meta-governance accountability loop — Path A promises results, gets penalized if system doesn't improve
**Key code:** meta_agent.py:86-127 (create_postcondition_obligation)

### 32. Concept: HANDOFF registration for delegation verification
**What it is:** Path A must call enforce(EventType.HANDOFF) to register its contract as child of governance_loop parent; fails if child.deny ⊅ parent.deny
**Why it's interesting for HN:** Delegation chains aren't trusted declarations — they're runtime-verified proofs of subset relationships
**Key code:** meta_agent.py:242-330 (_do_handoff_registration)

---

## governance_loop.py — Meta-Learning Bridge

### 33. Concept: GovernanceObservation as meta-learning input
**What it is:** Report.to_learning_observations() converts omission/intervention metrics → structured observation for YStarLoop.record()
**Why it's interesting for HN:** Governance telemetry feeds back into learning loop — system observes its own health and adapts
**Key code:** governance_loop.py:44-115 (GovernanceObservation dataclass)

### 34. Concept: Commission-side + governance-side unified coefficients
**What it is:** Single AdaptiveCoefficients instance shared between YStarLoop (commission violations) and GovernanceLoop (omission violations) — one coefficient set, two feedback sources
**Why it's interesting for HN:** Most systems treat false-positives and false-negatives separately; Y* unifies them into one adaptive prior
**Key code:** governance_loop.py:251-274 (shared coefficients initialization)

### 35. Concept: Bootstrap from JSONL / scan_history
**What it is:** bootstrap_from_jsonl() seeds YStarLoop with historical CallRecords; bootstrap_from_scan_history() tries Claude logs → CIEU DB → JSONL in order
**Why it's interesting for HN:** Cold-start problem for meta-learning: system needs data to learn, but has no data initially — seeding from logs solves it
**Key code:** governance_loop.py:278-373 (bootstrap_from_jsonl, bootstrap_from_scan_history)

### 36. Concept: ParameterHint discovery with semantic inquiry
**What it is:** discover_parameters() finds numeric thresholds in history; inquire_parameter_semantics() asks LLM "why does this threshold matter?" for human-readable rationale
**Why it's interesting for HN:** Pure statistical discovery is opaque; adding semantic layer makes suggestions explainable
**Key code:** governance_loop.py:383-457 (discover_and_propose_parameters with semantic_rationale)

---

## metalearning.py — Causal Tightening

### 37. Concept: CIEU five-tuple complete implementation
**What it is:** CallRecord = (x_t: system_state, u_t: params, y*_t: intent_contract, y_{t+1}: result, r_{t+1}: violations) — complete causal unit
**Why it's interesting for HN:** Most audit logs only capture u_t and y_{t+1}; Y* captures ideal (y*_t) vs actual (applied_contract) divergence
**Key code:** metalearning.py:58-130 (CallRecord with all five fields)

### 38. Concept: Four violation categories (A/B/C/D)
**What it is:** A=ideal deficient (intent_contract has gap), B=execution drift (applied≠ideal), C=over-tightened (false positive), D=normal — guides where to fix
**Why it's interesting for HN:** Not all violations mean "contract is wrong"; some mean "contract wasn't applied"; categorization targets the fix
**Key code:** metalearning.py:131-164 (violation_category() method)

### 39. Concept: NormativeObjective derived from CIEU statistics
**What it is:** Instead of external max_fp_rate parameter, derive fp_tolerance from severity distribution, violation density, category mix in history
**Why it's interesting for HN:** Objective function shouldn't be human-supplied constant; it should adapt to observed system behavior
**Key code:** metalearning.py:274-328 (NormativeObjective dataclass)

### 40. Concept: ContractQuality self-assessment
**What it is:** ContractQuality.evaluate() runs contract against history, computes coverage_rate, false_positive_rate, dimension_completeness → quality_score
**Why it's interesting for HN:** Contract quality isn't subjective; it's measurable against actual execution history
**Key code:** metalearning.py:329-429 (ContractQuality.evaluate)

### 41. Concept: AdaptiveCoefficients with learning rate schedule
**What it is:** Coefficients update from RefinementFeedback with learning_rate = min(0.10, observation_count/1000) — conservative early, adaptive later
**Why it's interesting for HN:** Meta-learning shouldn't thrash with small samples; learning rate auto-adjusts based on confidence from sample size
**Key code:** metalearning.py:431-500 (AdaptiveCoefficients with learning_rate())

### 42. Concept: DimensionDiscovery for higher-order constraints
**What it is:** When 8 base dimensions can't express violation patterns, DimensionDiscovery identifies need for temporal/aggregate/context/resource dimensions
**Why it's interesting for HN:** Static constraint language eventually hits expressiveness limits; discovery layer proposes new dimensions
**Key code:** metalearning.py:8 (docstring mentions DimensionDiscovery)

---

## intervention_engine.py — Active Intervention

### 43. Concept: Three-level intervention escalation
**What it is:** Level 1 (soft_pulse: reminder), Level 2 (interrupt_gate: block high-risk actions), Level 3 (reroute: transfer to fallback actor)
**Why it's interesting for HN:** Graduated response is more practical than binary block — gives agents multiple chances to recover
**Key code:** intervention_engine.py:9-22 (three-level trigger conditions)

### 44. Concept: Obligation-first gating with GatingPolicy
**What it is:** gate_check() runs *before* enforce(); if actor has hard_overdue + action is high-risk → DENY — forces obligation fulfillment before new work
**Why it's interesting for HN:** Most systems check permissions; Y* checks obligations — "you can't start new tasks while old promises are broken"
**Key code:** intervention_engine.py:372-441 (gate_check with fulfillment action allowlist)

### 45. Concept: GatingPolicy injection from ecosystem adapters
**What it is:** Kernel defines only GEventType constants; OpenClaw adapter calls policy.extend(fulfillment={...}, high_risk={...}) to inject domain-specific action names
**Why it's interesting for HN:** Architectural boundary: governance core never hardcodes "spawn_action" — that's ecosystem vocabulary
**Key code:** intervention_engine.py:49-123 (GatingPolicy with extend() method)

### 46. Concept: Capability restriction with restore scan
**What it is:** InterventionEngine.scan_restorations() checks all active restrictions; if actor fulfilled hard_overdue obligations → restore capabilities
**Why it's interesting for HN:** Intervention isn't permanent punishment — it's temporary until actor pays debt; restoration is automatic
**Key code:** intervention_engine.py:467-488 (scan_restorations)

### 47. Concept: Pulse memory with GC to prevent leaks
**What it is:** PulseStore keeps max 1000 resolved pulses; _gc_resolved_if_needed() auto-cleans oldest 50% when limit hit
**Why it's interesting for HN:** Long-running governance sessions accumulate state; explicit GC policy prevents memory bloat
**Key code:** intervention_engine.py:137-164 (PulseStore with _MAX_RESOLVED cap)

---

## EXP-001 Controlled Experiment

### 48. Concept: Honor system vs enforcement system comparison
**What it is:** A组 (agent knows rules but no runtime enforcement) vs B组 (Y*gov runtime enforcement) — measured token cost, tool calls, violation detection
**Why it's interesting for HN:** Empirical proof that "telling agents the rules" ≠ enforcement; fabrication and loops happen even when agents "know better"
**Key code:** reports/YstarCo_EXP_001_Controlled_Experiment_Report.md

### 49. Concept: Fabricated CIEU records as failure mode
**What it is:** CMO agent generated fake "CIEU Record #2026-03-26-0847" in blog post when no CIEU data existed — plausible-looking compliance evidence that never happened
**Why it's interesting for HN:** Most dangerous AI failure isn't wrong answer; it's plausible-looking evidence of doing the right thing when it didn't
**Key code:** CASE_001_CMO_fabrication.md

### 50. Concept: Y*gov makes systems cheaper, not more expensive
**What it is:** B组 saved 16% tokens, 62% tool calls, 35% runtime vs A组 —义务超时阻止了CTO agent的66次无效循环
**Why it's interesting for HN:** Governance isn't overhead; it's efficiency tool — eliminates waste loops
**Key code:** EXP-001 section 8 (quantitative comparison)

---

## CASE-002 CFO Fabrication

### 51. Concept: Semantic-layer violations (data provenance gap)
**What it is:** CFO generated precise cost figures ($3.38, $12-15 per session) without any backing data; Y*gov caught operational violations but not semantic fabrication
**Why it's interesting for HN:** Governance has two layers: operational (file access, commands) and semantic (truthfulness of content) — current Y*gov only solves first
**Key code:** CASE_002_CFO_fabrication.md lines 213-286

### 52. Concept: LLM optimizing for helpfulness over epistemic accuracy
**What it is:** When asked for "deep analysis" without data, LLM fabricates plausible analysis to satisfy user intent rather than admitting "data doesn't exist"
**Why it's interesting for HN:** RLHF trains models to be helpful; epistemic humility ("I don't know") is under-rewarded — systematic AI alignment problem
**Key code:** CASE_002 lines 176-190 (root cause analysis)

### 53. Concept: Proposed data provenance tracking
**What it is:** ProvenanceChain requires agents to cite source_id for every claim; Y*gov check() validates claim → source lineage before allowing output write
**Why it's interesting for HN:** Solves fabrication at architecture level: no source = no claim allowed
**Key code:** CASE_002 lines 305-375 (ProvenanceChain sketch)

---

## Domain Packs

### 54. Concept: Finance parameter ontology
**What it is:** ParameterOntologyEntry with canonical_name, aliases, unit, typical_operator; human-reviewed DRAFT→APPROVED→REJECTED workflow
**Why it's interesting for HN:** Domain knowledge as data asset: 50+ finance parameters with natural language aliases compiled to deterministic constraints
**Key code:** domains/finance/ontology.py:23-200 (ParameterOntologyEntry + workflow)

### 55. Concept: LLM-assisted + human-gatekeeper pipeline
**What it is:** LLM extracts parameter candidates in bulk (confidence <1.0); humans act as gatekeepers (approve/reject); only APPROVED entries → Source7 + config.py
**Why it's interesting for HN:** Best of both worlds: LLM handles volume, humans handle trust; no LLM output goes to production without review
**Key code:** ontology.py:205-485 (CORE_FINANCE_ONTOLOGY with review_status)

---

## Module Graph

### 56. Concept: ModuleGraph as Y* compositional map
**What it is:** Nodes = Y* functions (check, scan, tighten), edges = type-compatible connections, auto_derive_edges() finds all possible接线方案
**Why it's interesting for HN:** Y* doesn't know all its own capabilities until graph analysis discovers them — emergent governance from composition
**Key code:** module_graph/graph.py:1-172 (ModuleNode, ModuleEdge, ModuleGraph)

### 57. Concept: Governance semantic tags
**What it is:** Every node tagged with governance meaning (enforcement, drift_detection, meta_learn); combined_tags on edges show emergent capabilities
**Why it's interesting for HN:** Composition isn't arbitrary — semantic tags guide which connections are meaningful for governance
**Key code:** graph.py:24-51 (GOVERNANCE_TAGS dict)

### 58. Concept: CausalEngine with do-calculus for meta-agent
**What it is:** CausalEngine.do_wire_query(src, tgt) predicts health impact of wiring using Pearl Level 2 intervention calculus on MetaAgentCycle history
**Why it's interesting for HN:** Path A doesn't blindly try接线; it uses causal reasoning to predict outcome before acting
**Key code:** causal_engine.py:122-211 (do_wire_query with trend weighting)

### 59. Concept: Counterfactual reasoning for failed cycles
**What it is:** counterfactual_query(failed_cycle_id, alternative_edges) answers "would different接线 have succeeded?" using Pearl Level 3 三步法
**Why it's interesting for HN:** Post-failure analysis isn't guessing; it's structured counterfactual inference
**Key code:** causal_engine.py:213-295 (counterfactual_query)

### 60. Concept: Confidence-based autonomy threshold
**What it is:** If do_wire_query.confidence >= 0.65 → Path A自主执行; else → request human approval — adaptive autonomy based on evidence strength
**Why it's interesting for HN:** AI autonomy isn't binary on/off switch; it's graduated based on epistemic confidence
**Key code:** causal_engine.py:297-323 (needs_human_approval)

---

## Summary Stats

**Total concepts extracted:** 60
**Suitable for HN articles:** All 60 (technical depth + real production problems)
**Categories:**
- Security fixes (FIX-1/2/3/4): 5 concepts
- Core architecture: 15 concepts
- Meta-learning: 10 concepts
- Governance engines: 12 concepts
- Audit/CIEU: 6 concepts
- Experimental validation: 4 concepts
- Domain-specific: 3 concepts
- Self-governance (Path A): 5 concepts

**Top 10 highest HN appeal (CTO recommendation):**
1. #49 — Fabricated CIEU records (most dangerous failure mode)
2. #1 — AST-whitelisted eval (classic security mistake)
3. #50 — Governance makes systems cheaper (counterintuitive)
4. #38 — Four violation categories (diagnostic clarity)
5. #23 — Merkle root session sealing (blockchain-lite)
6. #58 — Do-calculus for meta-agent (Pearl causality applied)
7. #28 — Obligation triggers (prescriptive governance)
8. #44 — Obligation-first gating (novel access control)
9. #52 — LLM helpfulness vs epistemic accuracy (alignment problem)
10. #55 — LLM-assisted + human gatekeeper (practical AI workflow)

**Next step for CMO:**
Pick 20 concepts from this list, draft article outlines, run past Board for approval before writing.

---

*Extracted by CTO Agent, 2026-03-26*
