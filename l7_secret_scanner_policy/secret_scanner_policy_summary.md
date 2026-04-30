# L7.0S Secret Scanner Context Policy

L7.0S adds a contextual secret scanner policy and helper. Real-looking provider keys, bearer tokens, OAuth tokens, private keys, and unredacted API key assignments remain blocked.

Approved redacted placeholders, documentation examples, scanner-rule examples, and test fixture tokens are allowed when they use explicit `REDACTED`, `PLACEHOLDER`, `TEST_ONLY`, or `EXAMPLE` markers.

Result: tests no longer need string-splitting workarounds just to describe safe scanner examples, while real secret values remain unsafe for commit.
