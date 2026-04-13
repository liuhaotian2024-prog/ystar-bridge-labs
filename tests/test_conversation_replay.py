#!/usr/bin/env python3
"""
test_conversation_replay.py - Test suite for C7 Conversation Replay Engine

Tests cover:
1. JSONL loading and parsing
2. Secret masking (≥6 patterns)
3. Token budget enforcement
4. Graceful degradation (missing files, empty JSONL)
5. Lookback window filtering
6. Output format validation

Author: Ryan Park (Platform Engineer) - Y* Bridge Labs
"""
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add scripts to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from conversation_replay import ConversationReplay, ReplayConfig


@pytest.fixture
def temp_projects_dir(tmp_path):
    """Create temporary projects directory."""
    projects_dir = tmp_path / 'projects'
    projects_dir.mkdir()
    return projects_dir


@pytest.fixture
def sample_jsonl_content():
    """Generate sample JSONL conversation entries."""
    now = datetime.now()
    entries = []

    # Permission mode entry (metadata)
    entries.append({
        'type': 'permission-mode',
        'permissionMode': 'default',
        'sessionId': 'test-session-123'
    })

    # User message
    entries.append({
        'type': 'user',
        'timestamp': (now - timedelta(hours=2)).isoformat(),
        'message': {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Hello, please check the API status'}
            ]
        }
    })

    # Assistant message with tool use
    entries.append({
        'type': 'assistant',
        'timestamp': (now - timedelta(hours=2, minutes=-5)).isoformat(),
        'message': {
            'role': 'assistant',
            'model': 'claude-opus-4-6',
            'content': [
                {'type': 'text', 'text': 'I will check the API status for you.'},
                {
                    'type': 'tool_use',
                    'id': 'toolu_123',
                    'name': 'Bash',
                    'input': {'command': 'curl https://api.example.com/status'}
                }
            ]
        }
    })

    # User message with secret (should be masked)
    entries.append({
        'type': 'user',
        'timestamp': (now - timedelta(hours=1)).isoformat(),
        'message': {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'Configure the API with key: sk-1234567890abcdefghijklmnopqrstuvwx'
                }
            ]
        }
    })

    return '\n'.join(json.dumps(e) for e in entries)


def test_find_latest_jsonl(temp_projects_dir, sample_jsonl_content):
    """Test finding latest JSONL file."""
    # Create multiple JSONL files with different mtimes
    old_file = temp_projects_dir / 'old-session.jsonl'
    new_file = temp_projects_dir / 'new-session.jsonl'

    old_file.write_text(sample_jsonl_content)
    new_file.write_text(sample_jsonl_content)

    # Modify mtime
    import time
    time.sleep(0.1)
    new_file.touch()

    config = ReplayConfig(projects_dir=temp_projects_dir)
    replay = ConversationReplay(config)

    latest = replay.find_latest_session_jsonl()
    assert latest is not None
    assert latest.name == 'new-session.jsonl'


def test_load_recent_turns_within_window(temp_projects_dir, sample_jsonl_content):
    """Test loading turns within lookback window."""
    jsonl_file = temp_projects_dir / 'test.jsonl'
    jsonl_file.write_text(sample_jsonl_content)

    config = ReplayConfig(projects_dir=temp_projects_dir, lookback_hours=24)
    replay = ConversationReplay(config)

    turns = replay.load_recent_turns(jsonl_file)

    # Should load user and assistant messages (not permission-mode)
    assert len(turns) >= 2
    assert all(t['type'] in ['user', 'assistant'] for t in turns)


def test_secret_masking_openai_key(temp_projects_dir):
    """Test OpenAI API key masking."""
    content = json.dumps({
        'type': 'user',
        'timestamp': datetime.now().isoformat(),
        'message': {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Use key sk-1234567890abcdefghijKLMNOPQRSTUVWXYZ'}
            ]
        }
    })

    jsonl_file = temp_projects_dir / 'test.jsonl'
    jsonl_file.write_text(content)

    config = ReplayConfig(projects_dir=temp_projects_dir)
    replay = ConversationReplay(config)

    turns = replay.load_recent_turns(jsonl_file)
    assert len(turns) == 1

    masked_content, redactions = replay.mask_secrets(turns[0]['content'])
    assert 'sk-1234567890' not in masked_content
    assert '<REDACTED:OPENAI_KEY>' in masked_content
    assert redactions > 0


def test_secret_masking_github_token(temp_projects_dir):
    """Test GitHub token masking."""
    content = json.dumps({
        'type': 'user',
        'timestamp': datetime.now().isoformat(),
        'message': {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz'}
            ]
        }
    })

    jsonl_file = temp_projects_dir / 'test.jsonl'
    jsonl_file.write_text(content)

    config = ReplayConfig(projects_dir=temp_projects_dir)
    replay = ConversationReplay(config)

    turns = replay.load_recent_turns(jsonl_file)
    masked_content, _ = replay.mask_secrets(turns[0]['content'])

    assert 'ghp_' not in masked_content or '<REDACTED:GITHUB_TOKEN>' in masked_content


def test_secret_masking_aws_key(temp_projects_dir):
    """Test AWS access key masking."""
    content = json.dumps({
        'type': 'user',
        'timestamp': datetime.now().isoformat(),
        'message': {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'AWS key: AKIAIOSFODNN7EXAMPLE'}
            ]
        }
    })

    jsonl_file = temp_projects_dir / 'test.jsonl'
    jsonl_file.write_text(content)

    config = ReplayConfig(projects_dir=temp_projects_dir)
    replay = ConversationReplay(config)

    turns = replay.load_recent_turns(jsonl_file)
    masked_content, _ = replay.mask_secrets(turns[0]['content'])

    assert 'AKIAIOSFODNN7EXAMPLE' not in masked_content
    assert '<REDACTED:AWS_KEY>' in masked_content


def test_secret_masking_jwt(temp_projects_dir):
    """Test JWT token masking."""
    jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U'

    content = json.dumps({
        'type': 'user',
        'timestamp': datetime.now().isoformat(),
        'message': {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': f'JWT: {jwt}'}
            ]
        }
    })

    jsonl_file = temp_projects_dir / 'test.jsonl'
    jsonl_file.write_text(content)

    config = ReplayConfig(projects_dir=temp_projects_dir)
    replay = ConversationReplay(config)

    turns = replay.load_recent_turns(jsonl_file)
    masked_content, _ = replay.mask_secrets(turns[0]['content'])

    assert jwt not in masked_content
    assert '<REDACTED:JWT>' in masked_content


def test_secret_masking_env_variable(temp_projects_dir):
    """Test environment variable secret masking."""
    content = json.dumps({
        'type': 'user',
        'timestamp': datetime.now().isoformat(),
        'message': {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Set API_KEY=super_secret_value_12345'}
            ]
        }
    })

    jsonl_file = temp_projects_dir / 'test.jsonl'
    jsonl_file.write_text(content)

    config = ReplayConfig(projects_dir=temp_projects_dir)
    replay = ConversationReplay(config)

    turns = replay.load_recent_turns(jsonl_file)
    masked_content, _ = replay.mask_secrets(turns[0]['content'])

    assert 'super_secret_value_12345' not in masked_content
    assert '<REDACTED:ENV_SECRET>' in masked_content


def test_secret_masking_google_api_key(temp_projects_dir):
    """Test Google API key masking."""
    content = json.dumps({
        'type': 'user',
        'timestamp': datetime.now().isoformat(),
        'message': {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Google key: AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe'}
            ]
        }
    })

    jsonl_file = temp_projects_dir / 'test.jsonl'
    jsonl_file.write_text(content)

    config = ReplayConfig(projects_dir=temp_projects_dir)
    replay = ConversationReplay(config)

    turns = replay.load_recent_turns(jsonl_file)
    masked_content, _ = replay.mask_secrets(turns[0]['content'])

    assert 'AIzaSyDaGmWKa4JsXZ' not in masked_content
    assert '<REDACTED:GOOGLE_API_KEY>' in masked_content


def test_token_budget_enforcement(temp_projects_dir):
    """Test that replay respects token budget."""
    # Generate large content that exceeds budget
    large_text = 'x' * 100_000  # ~25K tokens
    entries = []

    for i in range(50):  # 50 * 25K = 1.25M tokens (exceeds 800K budget)
        entries.append(json.dumps({
            'type': 'user',
            'timestamp': datetime.now().isoformat(),
            'message': {
                'role': 'user',
                'content': [{'type': 'text', 'text': f'Message {i}: {large_text}'}]
            }
        }))

    jsonl_file = temp_projects_dir / 'test.jsonl'
    jsonl_file.write_text('\n'.join(entries))

    config = ReplayConfig(projects_dir=temp_projects_dir, max_tokens=800_000)
    replay = ConversationReplay(config)

    turns = replay.load_recent_turns(jsonl_file)

    # Should stop before loading all 50 messages
    assert len(turns) < 50

    # Estimate total tokens
    total_chars = sum(len(t['content']) for t in turns)
    estimated_tokens = total_chars / config.char_per_token
    assert estimated_tokens <= config.max_tokens


def test_empty_jsonl_graceful_degradation(temp_projects_dir):
    """Test graceful handling of empty JSONL file."""
    jsonl_file = temp_projects_dir / 'empty.jsonl'
    jsonl_file.write_text('')

    config = ReplayConfig(projects_dir=temp_projects_dir)
    replay = ConversationReplay(config)

    context, metadata = replay.build_replay_context()

    assert context == ''
    assert not metadata['success']
    assert 'No turns' in metadata['error']


def test_missing_projects_dir_graceful_degradation(tmp_path):
    """Test graceful handling of missing projects directory."""
    nonexistent_dir = tmp_path / 'nonexistent'

    config = ReplayConfig(projects_dir=nonexistent_dir)
    replay = ConversationReplay(config)

    context, metadata = replay.build_replay_context()

    assert context == ''
    assert not metadata['success']
    assert 'No JSONL files' in metadata['error']


def test_lookback_zero_returns_empty(temp_projects_dir, sample_jsonl_content):
    """Test that lookback=0 returns no turns."""
    jsonl_file = temp_projects_dir / 'test.jsonl'
    jsonl_file.write_text(sample_jsonl_content)

    config = ReplayConfig(projects_dir=temp_projects_dir, lookback_hours=0)
    replay = ConversationReplay(config)

    turns = replay.load_recent_turns(jsonl_file)

    # With 0-hour lookback, cutoff is now, so no historical turns should load
    assert len(turns) == 0


def test_format_for_prepend_structure(temp_projects_dir, sample_jsonl_content):
    """Test output format structure for prepending."""
    jsonl_file = temp_projects_dir / 'test.jsonl'
    jsonl_file.write_text(sample_jsonl_content)

    config = ReplayConfig(projects_dir=temp_projects_dir)
    replay = ConversationReplay(config)

    turns = replay.load_recent_turns(jsonl_file)
    formatted = replay.format_for_prepend(turns)

    # Verify markdown structure
    assert '# Previous Session Transcript' in formatted
    assert 'C7 Conversation Replay' in formatted
    assert '## USER' in formatted or '## ASSISTANT' in formatted
    assert '---' in formatted


def test_malformed_jsonl_resilience(temp_projects_dir):
    """Test resilience to malformed JSONL entries."""
    malformed_content = '''
    {"type": "user", "timestamp": "invalid-timestamp", "message": null}
    not-valid-json
    {"type": "assistant", "message": {"content": "this is ok"}}
    '''

    jsonl_file = temp_projects_dir / 'malformed.jsonl'
    jsonl_file.write_text(malformed_content)

    config = ReplayConfig(projects_dir=temp_projects_dir)
    replay = ConversationReplay(config)

    # Should not crash, may return empty or partial results
    turns = replay.load_recent_turns(jsonl_file)
    assert isinstance(turns, list)  # At minimum, returns a list


def test_no_mask_flag(temp_projects_dir):
    """Test disabling secret masking."""
    content = json.dumps({
        'type': 'user',
        'timestamp': datetime.now().isoformat(),
        'message': {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Key: sk-1234567890abcdefghijKLMNOPQRSTUVWXYZ'}
            ]
        }
    })

    jsonl_file = temp_projects_dir / 'test.jsonl'
    jsonl_file.write_text(content)

    config = ReplayConfig(projects_dir=temp_projects_dir, mask_secrets=False)
    replay = ConversationReplay(config)

    turns = replay.load_recent_turns(jsonl_file)
    unmasked_content, redactions = replay.mask_secrets(turns[0]['content'])

    # Should not mask when disabled
    assert 'sk-1234567890' in unmasked_content
    assert redactions == 0


def test_subagent_directory_exclusion(temp_projects_dir, sample_jsonl_content):
    """Test that subagents/ directories are excluded."""
    # Create subagents directory
    subagents_dir = temp_projects_dir / 'subagents'
    subagents_dir.mkdir()

    # Create JSONL in subagents (should be ignored)
    subagent_file = subagents_dir / 'subagent-session.jsonl'
    subagent_file.write_text(sample_jsonl_content)

    # Create regular JSONL (should be found)
    main_file = temp_projects_dir / 'main-session.jsonl'
    main_file.write_text(sample_jsonl_content)

    config = ReplayConfig(projects_dir=temp_projects_dir)
    replay = ConversationReplay(config)

    latest = replay.find_latest_session_jsonl()

    assert latest is not None
    assert 'subagents' not in str(latest)
    assert latest.name == 'main-session.jsonl'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
