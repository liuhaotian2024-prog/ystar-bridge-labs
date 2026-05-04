from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_schema import redact_text


def test_redacts_common_github_tokens_and_https_credentials() -> None:
    text = "https://ghp_abcdef123456@github.com/x/y github_pat_ABC123 sk-testsecret123456"
    redacted = redact_text(text)
    assert "ghp_" not in redacted
    assert "github_pat_" not in redacted
    assert "sk-testsecret" not in redacted
    assert "[REDACTED" in redacted

