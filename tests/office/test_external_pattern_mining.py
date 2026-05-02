from pathlib import Path

from office.mission_command.external_pattern_mining import (
    SOURCE_FAMILIES,
    extract_patterns_from_sources,
    load_or_run_external_pattern_research,
    build_e9_external_pattern_research_request,
)


ROOT = Path(__file__).resolve().parents[2]


def test_e9_inspection_report_exists():
    assert (ROOT / "reports" / "integration" / "e9_implementation_inspection.md").exists()


def test_external_pattern_request_has_required_source_families():
    request = build_e9_external_pattern_research_request()
    assert set(SOURCE_FAMILIES).issubset(set(request.source_families))
    assert request.required_pattern_count >= 12


def test_external_pattern_library_requires_at_least_12_patterns_when_research_available():
    research = load_or_run_external_pattern_research(ROOT)
    patterns = extract_patterns_from_sources(research["sources"])
    assert research["receipt"]["research_ran"] is True
    assert len(patterns) >= 12


def test_external_pattern_records_source_ids_and_limitations():
    source = load_or_run_external_pattern_research(ROOT)["sources"][0]
    assert source.source_id
    assert source.url_or_identifier.startswith("https://")
    assert source.limitations
