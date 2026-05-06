from pathlib import Path
from office.mission_command.e52_no_overclaim_validator import validate_no_overclaim


def test_e52_no_overclaim_validator_passes_packet_and_fails_forbidden(tmp_path):
    good = validate_no_overclaim()
    assert good['passed'] is True
    bad_dir = tmp_path / 'packet'
    bad_dir.mkdir()
    (bad_dir / 'bad.md').write_text('This is production ready and customer validated.', encoding='utf-8')
    result = validate_no_overclaim(bad_dir)
    assert result['passed'] is False
    assert result['violations']
