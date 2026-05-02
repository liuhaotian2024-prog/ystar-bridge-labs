from office.mission_command.e9_draft_binding import E9DraftBinding, validate_e9_draft_binding


def test_e9_draft_hash_mismatch_blocks():
    binding = E9DraftBinding("d1", "h1", "path", "email", True, True, False, ["manifest_draft_hash_mismatch"])
    assert "manifest_draft_hash_mismatch" in validate_e9_draft_binding(binding)


def test_e9_draft_requires_ai_disclosure():
    binding = E9DraftBinding("d1", "h1", "path", "email", False, True, False, [])
    assert "draft_requires_ai_disclosure" in validate_e9_draft_binding(binding)


def test_e9_draft_requires_opt_out_language():
    binding = E9DraftBinding("d1", "h1", "path", "email", True, False, False, [])
    assert "draft_requires_opt_out" in validate_e9_draft_binding(binding)
