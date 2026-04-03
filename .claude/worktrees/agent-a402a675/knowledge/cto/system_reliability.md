# System Reliability Framework

## SLO/SLI/SLA Definitions

**SLI (Service Level Indicator)**: Quantitative measure of service behavior.
- Examples: Request latency (ms), error rate (%), throughput (req/s), system availability (%)
- Must be measurable from user perspective
- Choose 3-5 indicators max; more creates noise

**SLO (Service Level Objective)**: Target value/range for SLI over time window.
- Format: "99.9% of requests complete in <200ms over 30-day window"
- Set based on user needs, not technical maximums
- Must be achievable with current architecture

**SLA (Service Level Agreement)**: Business contract with consequences.
- Only create SLAs after SLOs are consistently met for 3+ months
- Include financial penalties or service credits
- Always looser than internal SLOs (buffer for unexpected issues)

### When to Use
- SLIs: Every production service, from day one
- SLOs: Once you have 2 weeks of baseline data
- SLAs: Only for paying customers; never promise what you can't consistently deliver

### Setting Process
1. Instrument: Add telemetry to measure candidate SLIs
2. Baseline: Collect 2-4 weeks of real traffic data
3. Analyze: Identify p50, p95, p99 performance
4. Set SLO: Target slightly worse than current p95 (room for growth)
5. Review: Reassess quarterly as product matures

### Common Mistakes
- Setting 99.99% ("four nines") without understanding cost (requires ~52min downtime/year)
- Measuring from load balancer instead of client experience
- Having SLOs without automated alerts
- Setting SLAs equal to SLOs (leaves no error budget)

## Error Budgets

**Definition**: Allowed amount of unreliability = (100% - SLO)
- If SLO is 99.9% uptime, error budget is 0.1% = ~43 minutes/month
- Shared resource between product and engineering teams

### When to Use
- To balance feature velocity with stability
- To make objective decisions about release freezes
- To justify infrastructure investment

### Implementation Steps
1. Calculate: (1 - SLO) × time window = error budget
2. Measure: Track consumption in real-time dashboard
3. Policy: Define actions at 50%, 75%, 100% consumption
4. Enforce: Halt risky deployments when budget exhausted

Example policy:
- 0-50% consumed: Normal velocity, deploy anytime
- 50-75% consumed: Require extra testing, avoid Fridays
- 75-100% consumed: Feature freeze, focus on stability
- >100% consumed: Full freeze until budget resets or SLO revised

### Common Mistakes
- Treating 100% uptime as the goal (leaves no room for innovation)
- Not consuming error budget on purpose (indicates SLO too loose)
- Letting one team spend entire budget (breaks collaboration)
- Resetting budget without postmortem on consumption

## Chaos Engineering

**Definition**: Intentionally injecting failures to verify system resilience.
- Based on Netflix's Simian Army, Chaos Monkey
- Hypothesis: "If X fails, system will Y"

### When to Apply
- After reaching 2 months of SLO compliance
- Before large traffic events (product launches, sales)
- Never in systems without monitoring or rollback capability

### Chaos Experiment Steps
1. Define steady state: Pick SLI that represents normal operation
2. Hypothesize: "Killing service X won't drop success rate below 99%"
3. Inject failure: Terminate instance, add latency, fill disk
4. Measure: Compare SLI during experiment to baseline
5. Automate: Run experiments continuously in production (advanced)

Start small: kill one container, not entire region.

### Common Mistakes
- Running chaos without monitoring (you won't learn anything)
- Only testing in staging (production has unique failure modes)
- Injecting multiple failures simultaneously (can't isolate cause)
- Skipping hypothesis (makes results unactionable)

## Incident Management

**Severity Levels**:
- SEV1 (Critical): Revenue-impacting, all customers affected, <15min response
- SEV2 (High): Major feature broken, subset of customers, <1hr response
- SEV3 (Medium): Minor feature degraded, <4hr response
- SEV4 (Low): Cosmetic issue, next business day

### Incident Response Steps
1. Detect: Automated alert or user report
2. Triage: Assign severity, page on-call if SEV1/2
3. Mitigate: Stop bleeding (rollback, failover), not root cause fix
4. Communicate: Update status page every 30min
5. Resolve: Verify SLIs return to normal
6. Postmortem: Within 48hr for SEV1/2

### Postmortem Template
- Timeline (what happened when)
- Root cause (the why, not the who)
- Impact (users affected, revenue lost, SLO consumption)
- Action items (prevent, detect faster, mitigate faster)
- Owner and due date for each action

### Common Mistakes
- Blaming individuals (creates fear, reduces reporting)
- Skipping postmortems for "small" incidents (patterns emerge from repetition)
- Writing action items without owners (nothing gets done)
- Not tracking action item completion (repeat incidents)

## "Everything Fails" Philosophy (Werner Vogels)

**Core Principle**: Build systems assuming every component will fail.

### Applied to Y*gov
- Agent calls fail: Implement retries with exponential backoff
- LLM providers go down: Support multiple backends (Anthropic, OpenAI, local)
- Governance checks hang: Set timeouts, fail open vs fail closed based on severity
- Disk fills: Monitor CIEU database growth, implement rotation
- Network partitions: Design for eventual consistency

### Design Checklist
- [ ] Every external call has timeout and retry logic
- [ ] Circuit breakers prevent cascading failures
- [ ] Graceful degradation defined (what works when X is down?)
- [ ] Data persisted before acknowledging success
- [ ] Idempotent operations (safe to retry)

### Common Mistakes
- Assuming cloud providers never fail (they do, regularly)
- Retry without backoff (thundering herd)
- No timeout (hang forever)
- Failing closed for non-critical checks (availability over perfection)
