from office.mission_command.e9_pattern_translation import translate_patterns_to_architecture
from office.mission_command.external_pattern_mining import extract_patterns_from_sources, load_or_run_external_pattern_research


def test_pattern_translation_maps_external_patterns_to_internal_modules():
    research = load_or_run_external_pattern_research()
    translations = translate_patterns_to_architecture(extract_patterns_from_sources(research["sources"]))
    assert any(item.target_module.endswith("e9_scope_minimization.py") for item in translations)
    assert any("method" in item.ybridge_equivalent.lower() for item in translations)


def test_pattern_translation_marks_already_present_partial_missing():
    research = load_or_run_external_pattern_research()
    statuses = {item.current_implementation_status for item in translate_patterns_to_architecture(extract_patterns_from_sources(research["sources"]))}
    assert {"partial", "missing"}.issubset(statuses)
