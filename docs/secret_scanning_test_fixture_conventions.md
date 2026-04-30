# Secret Scanning Test Fixture Conventions

L7.0S adds contextual secret scanning so tests can use clear fixture tokens without hiding them behind string concatenation.

Rules:

- Never put real secrets in tests, docs, generated JSON, Markdown, scripts, or committed fixtures.
- Do not use real-looking provider key values, even if the value is fake.
- Use approved placeholder tokens such as `TAVILY_API_KEY_PLACEHOLDER`, `TAVILY_API_KEY_REDACTED`, `SECRET_EXAMPLE_TAVILY_API_KEY`, `TVLY_TEST_PREFIX_EXAMPLE`, `REDACTED_API_KEY_VALUE`, `<REDACTED>`, or `<TEST_SECRET_PLACEHOLDER>`.
- Use `REDACTED`, `PLACEHOLDER`, `TEST_ONLY`, or `EXAMPLE` markers when documenting environment variables.
- Do not rely on string concatenation hacks to hide scanner-rule examples.
- Scanner-rule examples may describe symbolic patterns, but must not include real-looking concrete secret values.
- Context matters: tests and docs may contain approved fixtures; unsafe contexts such as env files, logs, DB/WAL/SHM surfaces, and active-agent markers remain blocked.

The scanner should be strict against actual leakage and calm around approved fixtures. That is the whole trick.
