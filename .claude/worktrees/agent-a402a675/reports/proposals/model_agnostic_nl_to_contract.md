# Proposal: Model-Agnostic Natural Language to Contract Translation

**Status:** DRAFT
**Author:** CTO Agent
**Date:** 2026-03-26
**Board Directive:** Formalize model-agnostic input design for nl_to_contract

---

## Executive Summary

Y*gov's core design principle is **INPUT INDEPENDENCE** — the enforcement layer does not care what model generated the input. However, the current `nl_to_contract.py` implementation hardcodes the Anthropic API, creating vendor lock-in and blocking users who:

1. Cannot access Anthropic API (region restrictions, corporate firewalls)
2. Want to use cheaper models (MiniMax, local Llama)
3. Require data privacy (local-only inference)
4. Have existing OpenAI/Azure infrastructure

This proposal establishes a **model-agnostic translation layer** that preserves the existing regex fallback while enabling users to configure any LLM provider via environment variables or config files.

**Core Principle:** Zero config required (regex-only mode always available), but users can opt into LLM translation by setting `YSTAR_LLM_PROVIDER`.

---

## 1. Current Architecture

### Code Path (lines 133-194)

```
_try_llm_translation()
  → hardcoded check: os.environ.get("ANTHROPIC_API_KEY")
  → hardcoded request: "https://api.anthropic.com/v1/messages"
  → hardcoded model: "claude-sonnet-4-20250514"
  → hardcoded headers: "x-api-key", "anthropic-version"
  → return None on any failure
```

### Fallback Chain

```
translate_to_contract(text)
  → _try_llm_translation(text)  [Anthropic API only]
  → if None → _try_regex_translation(text)  [always available]
```

### Current Behavior

- **With ANTHROPIC_API_KEY set:** Uses Claude Sonnet 4, confidence=0.90
- **Without ANTHROPIC_API_KEY:** Falls back to regex, confidence=0.50, prints warning
- **API failure:** Silent fallback to regex (network error, rate limit, etc.)

### Why This Matters

The regex fallback (`ystar.kernel.prefill._extract_constraints_from_text`) has **limited coverage**:
- Paths: Good (deny, only_paths)
- Commands: Basic (deny_commands)
- Domains: Basic (only_domains)
- Invariants: Poor (cannot parse complex logic)
- Obligation timing: None
- Value ranges: None

Users **need** LLM translation for comprehensive governance, but Anthropic API is not always viable.

---

## 2. Proposed Architecture

### Provider Interface

Each provider implements a simple contract:

```python
class LLMProvider(Protocol):
    def translate(self, prompt: str) -> str:
        """
        Send prompt to LLM, return raw text response.
        Raises exception on failure (handled by caller).
        """
        ...
```

### New Translation Flow

```
translate_to_contract(text)
  → provider = _get_configured_provider()  # AnthropicProvider | OpenAIProvider | MiniMaxProvider | LocalProvider | None
  → if provider:
      → try provider.translate(prompt)
      → parse JSON response
      → return result
  → if provider is None OR provider fails:
      → _try_regex_translation(text)  [unchanged fallback]
```

### Provider Selection Logic

```python
def _get_configured_provider() -> Optional[LLMProvider]:
    provider_name = os.environ.get("YSTAR_LLM_PROVIDER", "").lower()

    if not provider_name:
        # Backward compatibility: check for ANTHROPIC_API_KEY
        if os.environ.get("ANTHROPIC_API_KEY"):
            provider_name = "anthropic"
        else:
            return None  # Use regex-only mode

    if provider_name == "anthropic":
        return AnthropicProvider()
    elif provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "minimax":
        return MiniMaxProvider()
    elif provider_name == "local":
        return LocalProvider()
    elif provider_name == "regex":
        return None  # Explicit regex-only mode
    else:
        print(f"  [Y*] Unknown provider '{provider_name}'. Using regex fallback.", file=sys.stderr)
        return None
```

---

## 3. Provider Implementations

### AnthropicProvider (Refactor Existing Code)

**Source:** Lines 149-175 (extract into class)

```python
class AnthropicProvider:
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.model = os.environ.get("YSTAR_LLM_MODEL", "claude-sonnet-4-20250514")
        self.base_url = os.environ.get("YSTAR_LLM_BASE_URL", "https://api.anthropic.com/v1")

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

    def translate(self, prompt: str) -> str:
        # [Existing urllib.request code, unchanged]
        # POST to {base_url}/messages
        # Headers: x-api-key, anthropic-version
        ...
```

**Config:**
```bash
export YSTAR_LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-xxx
export YSTAR_LLM_MODEL=claude-sonnet-4-20250514  # optional
```

### OpenAIProvider (New, Highest Priority)

**Rationale:** OpenAI-compatible API is the de facto standard. Covers:
- OpenAI GPT-4, GPT-3.5
- Azure OpenAI
- Most local model servers (Ollama, llama.cpp, vLLM)
- Most third-party model providers (Groq, Together, etc.)

```python
class OpenAIProvider:
    def __init__(self):
        self.api_key = os.environ.get("YSTAR_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.model = os.environ.get("YSTAR_LLM_MODEL", "gpt-4")
        self.base_url = os.environ.get("YSTAR_LLM_BASE_URL", "https://api.openai.com/v1")

        if not self.api_key:
            raise ValueError("YSTAR_LLM_API_KEY or OPENAI_API_KEY not set")

    def translate(self, prompt: str) -> str:
        # POST to {base_url}/chat/completions
        # Headers: Authorization: Bearer {api_key}
        # Body: {"model": model, "messages": [{"role": "user", "content": prompt}]}
        ...
```

**Config:**
```bash
export YSTAR_LLM_PROVIDER=openai
export YSTAR_LLM_API_KEY=sk-xxx
export YSTAR_LLM_MODEL=gpt-4  # optional
export YSTAR_LLM_BASE_URL=https://api.openai.com/v1  # optional
```

**Azure OpenAI Example:**
```bash
export YSTAR_LLM_PROVIDER=openai
export YSTAR_LLM_API_KEY=<azure-key>
export YSTAR_LLM_BASE_URL=https://<resource>.openai.azure.com/openai/deployments/<deployment-name>
export YSTAR_LLM_MODEL=gpt-4  # ignored by Azure, but kept for consistency
```

### MiniMaxProvider (New, Validated by K9)

**Rationale:** K9 verification (2026-03-28) confirmed MiniMax works for clear rules, extremely low cost.

```python
class MiniMaxProvider:
    def __init__(self):
        self.api_key = os.environ.get("YSTAR_LLM_API_KEY") or os.environ.get("MINIMAX_API_KEY")
        self.group_id = os.environ.get("MINIMAX_GROUP_ID")
        self.model = os.environ.get("YSTAR_LLM_MODEL", "abab6.5s-chat")

        if not self.api_key or not self.group_id:
            raise ValueError("MINIMAX_API_KEY and MINIMAX_GROUP_ID required")

    def translate(self, prompt: str) -> str:
        # POST to https://api.minimax.chat/v1/text/chatcompletion_v2
        # Headers: Authorization: Bearer {api_key}
        # Body: {"model": model, "messages": [...], "tokens_to_generate": 1024}
        ...
```

**Config:**
```bash
export YSTAR_LLM_PROVIDER=minimax
export MINIMAX_API_KEY=xxx
export MINIMAX_GROUP_ID=xxx
export YSTAR_LLM_MODEL=abab6.5s-chat  # optional
```

### LocalProvider (New, Privacy-First)

**Rationale:** Enterprise users with data privacy requirements need fully local inference.

```python
class LocalProvider:
    def __init__(self):
        self.base_url = os.environ.get("YSTAR_LLM_BASE_URL", "http://localhost:11434")
        self.model = os.environ.get("YSTAR_LLM_MODEL", "llama3")

    def translate(self, prompt: str) -> str:
        # POST to {base_url}/api/generate (Ollama format)
        # OR {base_url}/v1/chat/completions (OpenAI-compatible)
        # No API key required for localhost
        ...
```

**Config (Ollama):**
```bash
export YSTAR_LLM_PROVIDER=local
export YSTAR_LLM_BASE_URL=http://localhost:11434
export YSTAR_LLM_MODEL=llama3  # or mistral, codellama, etc.
```

**Config (llama.cpp server):**
```bash
export YSTAR_LLM_PROVIDER=local
export YSTAR_LLM_BASE_URL=http://localhost:8080
export YSTAR_LLM_MODEL=model  # ignored by llama.cpp, but kept for consistency
```

### RegexProvider (Explicit Mode)

Not a real provider, but allows users to explicitly disable LLM translation:

```bash
export YSTAR_LLM_PROVIDER=regex
```

This is useful for testing, debugging, or environments where LLM overhead is unwanted.

---

## 4. Configuration Format

### Environment Variables (Primary Method)

```bash
# Required: Select provider
export YSTAR_LLM_PROVIDER=openai|anthropic|minimax|local|regex

# Provider-specific auth
export YSTAR_LLM_API_KEY=xxx           # For openai, minimax, local (if auth enabled)
export ANTHROPIC_API_KEY=xxx           # For anthropic (backward compatible)
export MINIMAX_GROUP_ID=xxx            # For minimax

# Optional: Override model
export YSTAR_LLM_MODEL=gpt-4           # Default varies by provider

# Optional: Override base URL (for custom endpoints)
export YSTAR_LLM_BASE_URL=https://...
```

### .ystar_session.json (Alternative Method)

```json
{
  "llm_config": {
    "provider": "openai",
    "api_key": "sk-xxx",
    "model": "gpt-4",
    "base_url": "https://api.openai.com/v1"
  },
  "governance_config": {
    "auto_activate_threshold": 0.9
  }
}
```

**Priority:** Environment variables > .ystar_session.json > defaults

---

## 5. Backward Compatibility

### Existing Behavior Preserved

1. **No config:** Falls back to regex (unchanged)
2. **ANTHROPIC_API_KEY set:** Auto-detects `provider=anthropic` (new)
3. **API failure:** Silent fallback to regex (unchanged)
4. **All existing tests pass:** Provider abstraction is transparent to `translate_to_contract()` callers

### Migration Path

**Users with ANTHROPIC_API_KEY:**
- No action required (auto-detection)
- Optional: Set `YSTAR_LLM_PROVIDER=anthropic` for explicitness

**Users without API access:**
- Before: Regex-only, limited coverage
- After: Set `YSTAR_LLM_PROVIDER=openai` or `local`, full coverage

**CI/CD pipelines:**
- Before: Required ANTHROPIC_API_KEY in secrets
- After: Can use any provider, or set `YSTAR_LLM_PROVIDER=regex` to disable LLM

---

## 6. Implementation Plan

### Phase 1: Refactor Core (Week 1)

- Extract provider interface (`ystar/kernel/llm_providers.py`)
- Refactor `_try_llm_translation()` to use `_get_configured_provider()`
- Extract `AnthropicProvider` from existing code
- Add tests for provider selection logic
- **Goal:** All 86 tests pass, no behavior change

### Phase 2: Add OpenAI Support (Week 1-2)

- Implement `OpenAIProvider`
- Add tests with mocked OpenAI API responses
- Document Azure OpenAI usage
- **Goal:** Users can switch to OpenAI with env var

### Phase 3: Add MiniMax and Local Support (Week 2)

- Implement `MiniMaxProvider` (K9-validated)
- Implement `LocalProvider` (Ollama + llama.cpp)
- Add integration tests (requires external setup)
- **Goal:** Full provider ecosystem

### Phase 4: Documentation (Week 3)

- Update README.md with provider examples
- Add troubleshooting guide for each provider
- Document rate limits and error handling
- **Goal:** Users can self-service provider setup

---

## 7. Testing Strategy

### Unit Tests (Required)

```python
def test_provider_selection_openai():
    with env_vars({"YSTAR_LLM_PROVIDER": "openai", "YSTAR_LLM_API_KEY": "sk-test"}):
        provider = _get_configured_provider()
        assert isinstance(provider, OpenAIProvider)

def test_backward_compat_anthropic_auto_detect():
    with env_vars({"ANTHROPIC_API_KEY": "sk-ant-test"}):
        provider = _get_configured_provider()
        assert isinstance(provider, AnthropicProvider)

def test_fallback_to_regex_when_no_provider():
    with env_vars({}):
        provider = _get_configured_provider()
        assert provider is None
```

### Integration Tests (Optional, Gated)

- Test each provider with real API (requires API keys in CI secrets)
- Compare output quality across providers (same input, compare coverage)
- Measure latency and cost per provider

### Regression Tests (Critical)

- All 86 existing tests must pass
- `translate_to_contract()` output format unchanged
- Error handling unchanged (silent fallback to regex)

---

## 8. Risk Assessment

### Low Risk

- **Provider abstraction:** Clean interface, no coupling to enforcement layer
- **Backward compatibility:** Auto-detection prevents breaking changes
- **Fallback safety:** Regex always available, no new single points of failure

### Medium Risk

- **Third-party API reliability:** MiniMax/local providers may be less stable
  - **Mitigation:** Fallback to regex on any provider failure
- **Configuration complexity:** More environment variables to document
  - **Mitigation:** Sensible defaults, clear error messages

### High Risk (None Identified)

---

## 9. Estimated Effort

| Phase | Tasks | Effort | Dependencies |
|-------|-------|--------|--------------|
| Phase 1: Refactor Core | Provider interface, AnthropicProvider extraction, tests | 2 days | None |
| Phase 2: OpenAI Support | OpenAIProvider, Azure docs, tests | 1 day | Phase 1 |
| Phase 3: MiniMax + Local | MiniMaxProvider, LocalProvider, tests | 1 day | Phase 1 |
| Phase 4: Documentation | README, troubleshooting guide, examples | 1 day | All phases |
| **Total** | | **5 days** | |

**Assumptions:**
- CTO has access to OpenAI/MiniMax API keys for testing
- Integration tests can be mocked or gated behind `pytest -m integration`
- Board approval required before merging to main

---

## 10. Success Criteria

1. **Zero regression:** All 86 tests pass after refactor
2. **Backward compatibility:** Existing users with `ANTHROPIC_API_KEY` see no change
3. **Provider parity:** OpenAI, MiniMax, and Local providers produce comparable contract quality
4. **Documentation clarity:** New users can set up any provider in <5 minutes
5. **Board approval:** CEO confirms design aligns with Y*gov's INPUT INDEPENDENCE principle

---

## Appendix: Alternative Considered

### Option A: LangChain Integration

**Pros:** Covers 100+ models, standard abstractions
**Cons:** Adds 50MB+ dependency, overkill for one prompt
**Decision:** Rejected (violates Y*gov's zero-dependency philosophy)

### Option B: Plugin System

**Pros:** Users can add custom providers without modifying Y*gov
**Cons:** Adds complexity, harder to test
**Decision:** Deferred to v0.42 (if user demand exists)

### Option C: LLM-Free Mode (Regex Only)

**Pros:** No API dependencies, fastest
**Cons:** Poor coverage for complex rules
**Decision:** Already exists as fallback, not sufficient for governance use cases

---

**Next Step:** Board approval required before implementation.
