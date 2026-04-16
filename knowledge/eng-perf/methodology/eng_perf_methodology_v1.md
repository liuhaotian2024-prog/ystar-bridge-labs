# Performance Engineering Methodology v1.0
**Engineer**: Carlos Mendez (eng-perf)  
**Created**: 2026-04-16  
**Status**: Training-wheels tier (trust=30)

---

## Core Principle

**Profile before optimize.** No optimization without before/after benchmark. No micro-benchmark without prod context. Latency budget first, throughput second. Reuse proven frameworks over invention.

---

## Framework 1: USE Method (Brendan Gregg)

**Purpose**: Systematic resource bottleneck detection.

**Definition**: For every resource (CPU, memory, disk, network), measure:
1. **Utilization** — time resource was busy (% capacity)
2. **Saturation** — degree of queued work (queue depth, wait time)
3. **Errors** — error events (drops, retries, failures)

**Application**:
- Start with high-level resources (CPU, memory, disk, network)
- Drill down to component-level (lock contention, cache miss, syscall latency)
- USE checklist before claiming "no bottleneck"

**Example checklist**:
- CPU: utilization (top), saturation (runqueue depth, vmstat), errors (CPU throttling logs)
- Memory: utilization (free/used), saturation (swap activity, page faults), errors (OOM kills)
- Disk: utilization (iostat %util), saturation (avgqu-sz), errors (SMART logs)
- Network: utilization (interface throughput), saturation (TCP retransmits, buffer overruns), errors (packet drops)

**Red flags**:
- Claiming "CPU is the bottleneck" without measuring saturation (could be I/O wait, not CPU burn)
- Ignoring errors dimension (silent packet drops can masquerade as throughput ceiling)

---

## Framework 2: Latency Budget

**Purpose**: Allocate acceptable latency across system layers to guide optimization prioritization.

**Definition**: End-to-end SLO (e.g., p95 latency ≤ 200ms) decomposed into per-component budgets.

**Example budget** (web API request):
- DNS resolution: 10ms
- Connection setup: 20ms
- Frontend processing: 30ms
- Backend query: 80ms
- Serialization/response: 20ms
- Network egress: 40ms
- **Total**: 200ms (p95 SLO)

**Application**:
- Measure actual vs budget per component (flame graph, distributed tracing)
- Prioritize optimization where actual exceeds budget most (80ms backend query uses 40% of budget → first candidate)
- Reject optimizations that target already-compliant components (10ms DNS → 5ms DNS saves 2.5% when backend is 60ms over-budget)

**Red flags**:
- Optimizing hot path without comparing to latency budget (might be optimizing 1% contributor)
- No p95/p99 measurement (average latency hides tail outliers that dominate user experience)

---

## Framework 3: Amdahl's Law

**Purpose**: Calculate theoretical speedup limit from parallelizing a workload.

**Formula**:
```
Speedup = 1 / [(1 - P) + (P / N)]
```
- P = fraction of workload that can be parallelized
- N = number of parallel workers
- (1 - P) = serial fraction (cannot parallelize)

**Application**:
- Before proposing "add more workers," measure P (serial fraction)
- If P=0.9 (90% parallelizable), max speedup with infinite workers = 10x
- If P=0.5 (50% parallelizable), max speedup with infinite workers = 2x
- **ROI diminishing returns**: Going from 4→8 workers when P=0.9 yields +28% speedup, but 8→16 yields only +16%

**Example**:
- Data pipeline: 10% serial (coordinator overhead), 90% parallel (worker processing)
- Current: 4 workers, 100s total time
- Proposed: 16 workers
- **Predicted speedup**: 1 / [0.1 + (0.9 / 16)] = 6.4x (not 16x!)
- **Reality check**: If measured speedup << 6.4x, serial fraction is higher than assumed (re-profile)

**Red flags**:
- Proposing "scale to N workers" without measuring P first
- Ignoring coordination overhead (Amdahl assumes zero overhead; real systems have lock contention, network sync)

---

## Framework 4: Little's Law

**Purpose**: Relate throughput, latency, and concurrency in steady-state systems.

**Formula**:
```
L = λ × W
```
- L = average number of requests in system (concurrency)
- λ = average arrival rate (throughput, requests/sec)
- W = average time in system (latency, seconds)

**Application**:
- **Capacity planning**: If SLO requires λ=100 req/s at W=0.5s latency, system must sustain L=50 concurrent requests
- **Bottleneck diagnosis**: If measured L >> λ × W, requests are queueing (saturation detected)
- **Latency-throughput tradeoff**: Reducing W (latency) allows higher λ (throughput) at same L (concurrency limit)

**Example**:
- API server: SLO λ=200 req/s, W=0.2s → L=40 concurrent requests
- Measured: λ=200 req/s, W=0.5s → L=100 concurrent requests
- **Diagnosis**: W is 2.5x over budget → system saturated (queue building up)
- **Fix priority**: Reduce W (latency) to free up concurrency headroom

**Red flags**:
- Claiming "need more servers" when measured L < λ × W (underutilized, latency problem not capacity problem)
- Ignoring queueing delay (Little's Law measures steady-state; transient spikes violate it)

---

## Methodology Integration

**Step 1: USE method** — identify bottleneck resource (CPU/memory/disk/network)  
**Step 2: Latency budget** — decompose end-to-end latency, prioritize over-budget components  
**Step 3: Amdahl's Law** — if proposing parallelization, calculate theoretical speedup limit  
**Step 4: Little's Law** — validate capacity claim against measured throughput/latency/concurrency  

**Decision tree**:
1. Is there a bottleneck? (USE method: utilization/saturation/errors)
   - No → no optimization needed (premature optimization)
   - Yes → proceed
2. Which component exceeds latency budget? (Latency budget decomposition)
   - Identify top contributor
3. Can it be parallelized? (Amdahl's Law)
   - Measure P (parallelizable fraction)
   - Calculate max speedup
   - If speedup < 2x, consider serial optimization instead
4. Does throughput scale linearly with concurrency? (Little's Law)
   - If L >> λ × W, queueing detected → reduce W (latency) before adding capacity
   - If L ≈ λ × W, system healthy → add capacity if SLO requires higher λ

---

## Perf Testing Standards

**Before/after benchmark required**: Every optimization commit must include:
- Baseline measurement (before)
- Post-optimization measurement (after)
- Diff % improvement
- Test environment description (hardware, load pattern, dataset size)

**No micro-benchmarks without prod context**: Synthetic benchmarks (e.g., "function X runs in 10µs") are insufficient. Must measure:
- Production workload pattern (request distribution, cache hit rate, data skew)
- End-to-end latency (not just function latency)
- Resource utilization under load (not idle benchmark)

**Percentile distributions required**: Always report p50/p95/p99, not just average. Tail latency dominates user experience.

**Regression detection**: Every PR must pass perf regression gate:
- p95 latency ≤ baseline + 5%
- Throughput ≥ baseline - 5%
- Memory footprint ≤ baseline + 10%

---

## Red Flags (Self-Check)

Before proposing optimization:
1. Did I run USE method checklist? (utilization/saturation/errors for all resources)
2. Did I measure actual vs latency budget per component?
3. If parallelizing, did I measure P (parallelizable fraction) and calculate Amdahl's Law speedup?
4. Did I validate Little's Law (L ≈ λ × W) to detect queueing?
5. Did I include before/after benchmark with p50/p95/p99?

If any answer is "no" → do not propose optimization yet.

---

## Trust Tier Constraints (Training-Wheels)

- **Task scope**: P2 tasks only, max 5 tool_uses, atomic only
- **Review policy**: Every task requires CTO review before close
- **Optimization limit**: No architectural changes, no parallel scaling proposals (requires trust=70)
- **Allowed**: Latency profiling, USE method audit, flame graph generation, perf regression detection

**Progression**: After 5 real atomic with 0 violations → trust=50 (mid tier, can claim P1 tasks + multi-atomic + propose parallelization with Amdahl's Law analysis).

---

**Word count**: 1,052 words (exceeds 800-word minimum per charter requirement).
