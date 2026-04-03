# Engineering Culture Framework

## Code Review Best Practices

**Definition**: Systematic examination of code changes before merge.
- Purpose: catch bugs, share knowledge, ensure consistency, mentor juniors
- Not about gatekeeping or ego

### When to Apply
- Every production code change (no exceptions)
- Configuration changes affecting prod (IaC, feature flags)
- Skip for: docs-only changes, emergency hotfixes (but review after)

### Review Process Steps
1. Author: Write PR description (what, why, testing done)
2. Author: Self-review diff first (catch obvious issues)
3. Reviewer: Understand context before reading code
4. Reviewer: Check automated tests pass, code runs locally if complex
5. Reviewer: Comment on correctness, clarity, edge cases
6. Author: Address feedback or explain why not needed
7. Approve and merge

### Review Checklist
- [ ] Does it solve the stated problem?
- [ ] Are edge cases handled (null, empty, very large input)?
- [ ] Are errors logged with enough context?
- [ ] Are new functions tested?
- [ ] Is it readable by someone unfamiliar with the code?
- [ ] Does it follow existing patterns (or justify deviation)?

### Common Mistakes
- Reviewing for style instead of correctness (automate style checks)
- Requesting changes without explaining why (teach, don't dictate)
- Approving without reading (LGTM on blind trust)
- PRs over 400 lines (split into smaller changes)
- Waiting days to review (blocks progress, creates merge conflicts)

## Testing Philosophy

**Test Pyramid**: Unit tests (70%) > integration tests (20%) > E2E tests (10%)
- Unit: Fast, isolated, test single function
- Integration: Test component interactions (DB, API)
- E2E: Test full user flow, slow and brittle

### When to Mock
Mock when:
- Testing logic independent of external state
- External service is slow (DB, API)
- Testing error handling (hard to trigger real errors)

Don't mock when:
- Testing integration points (defeats purpose)
- Mock is more complex than real implementation
- Testing data structures (lists, dicts)

### Testing Steps
1. Identify: What behavior needs verification?
2. Arrange: Set up test data and mocks
3. Act: Call function under test
4. Assert: Verify output and side effects
5. Cleanup: Reset state (or use fixtures)

### Test Quality Checklist
- [ ] Tests fail when code is broken (not flaky)
- [ ] Test names describe behavior ("test_withdrawl_fails_when_insufficient_funds")
- [ ] Each test verifies one behavior
- [ ] Tests run in <10s (unit), <2min (integration), <10min (E2E)
- [ ] Coverage >80% for critical paths, not 100% everywhere

### Common Mistakes
- Testing implementation instead of behavior (breaks on refactor)
- High coverage, low value (testing getters/setters)
- No tests for error paths (only happy path)
- Shared state between tests (tests pass individually, fail in suite)
- Mocking everything (integration bugs slip through)

## Documentation Standards

**Definition**: Written explanations of code purpose, architecture, and usage.

### What to Document
- README: Setup, running, testing
- API: Endpoints, parameters, examples
- Architecture: System diagram, data flow, key decisions
- Runbooks: How to deploy, rollback, debug common issues
- Code comments: Why (not what), non-obvious behavior

### When to Write
- README: Before first external user
- API docs: Before API is used by another service
- Architecture: After design is approved, before implementation
- Runbooks: After second incident of same type
- Code comments: When you're tempted to add "TODO: refactor"

### Documentation Checklist
- [ ] Can a new engineer run the project in <30min?
- [ ] Are all environment variables documented?
- [ ] Is there a troubleshooting section for common errors?
- [ ] Are examples copy-pasteable and tested?
- [ ] Is it clear who to ask for help?

### Common Mistakes
- Writing docs that duplicate code (auto-generate instead)
- No examples (users cargo-cult from elsewhere)
- Outdated docs (worse than no docs)
- Over-documenting obvious code (clutter)
- Documentation not versioned with code (drift)

## Technical Debt Management

**Definition**: Code quality shortcuts that slow future development.
- Not all debt is bad (strategic debt accelerates learning)

### Technical Debt Quadrants (Martin Fowler)
1. Reckless + Deliberate: "We don't have time for design" (avoid)
2. Reckless + Inadvertent: "What's layering?" (junior mistakes, mentor)
3. Prudent + Deliberate: "Ship now, fix later" (acceptable if tracked)
4. Prudent + Inadvertent: "Now we know how we should have done it" (learning)

### When to Take on Debt
- To validate uncertain hypothesis (MVP, prototype)
- To meet critical deadline (fundraising, contract)
- When cost of delay > cost of debt

Never for: performance-critical code, security, data integrity

### Debt Management Steps
1. Identify: Create ticket immediately when taking debt
2. Tag: Label as "tech-debt", estimate repayment cost
3. Prioritize: Review debt backlog monthly
4. Allocate: Spend 20% of sprint on debt reduction
5. Measure: Track debt ticket count and age

### Common Mistakes
- Not documenting why debt was taken (looks like sloppiness)
- Deferring all debt (system becomes unmaintainable)
- Rewriting working code (repay debt that hurts, not annoys)
- No budget for repayment (debt grows unbounded)

## The Joel Test (Adapted for Y*gov)

**Definition**: 12-question test of engineering quality.

1. Do you use source control? (Yes - Git)
2. Can you make a build in one step? (Target: `pip install ystar`)
3. Do you make daily builds? (CI on every commit)
4. Do you have a bug database? (GitHub Issues)
5. Do you fix bugs before writing new code? (SEV1/2 always, SEV3 in sprints)
6. Do you have an up-to-date schedule? (Roadmap in README)
7. Do you have a spec? (Design docs for major features)
8. Do programmers have quiet working conditions? (N/A for AI agents)
9. Do you use the best tools money can buy? (Claude Opus, GitHub Copilot)
10. Do you have testers? (86 automated tests, CEO manual testing)
11. Do new candidates write code during interview? (N/A)
12. Do you do hallway usability testing? (Dogfooding Y*gov to run Y* Bridge Labs)

Score: 10/12 → Target 12/12

### Steps to Improve Score
- Score < 8: Fix infrastructure (CI, build process)
- Score 8-10: Fix process (specs, schedules)
- Score 10+: Optimize (tooling, culture)

Review quarterly, track score over time.

### Common Mistakes
- Treating as absolute (context matters)
- Scoring yes when partially true (be honest)
- Not acting on low scores (awareness without action)
