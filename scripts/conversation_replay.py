#!/usr/bin/env python3
"""
conversation_replay.py - C7 Conversation Replay Engine (AMENDMENT-015 v2 LRS)

Load recent Claude Code conversation transcripts (JSONL) and format them for
prepending to new session context, enabling near-seamless continuity.

Key features:
- Loads last N hours of conversation from ~/.claude/projects/.../session.jsonl
- Masks secrets (API keys, tokens, passwords) for privacy
- Token budget management (default 800K for verbatim replay)
- Deterministic (no LLM calls, Iron Rule 1 compliant)

Author: Ryan Park (Platform Engineer) - Y* Bridge Labs
"""
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class ReplayConfig:
    """Configuration for conversation replay."""
    projects_dir: Path
    max_tokens: int = 800_000
    lookback_hours: int = 24
    mask_secrets: bool = True
    char_per_token: float = 4.0  # Simple tiktoken approximation


class ConversationReplay:
    """Build conversation replay context from Claude Code JSONL transcripts."""

    # Secret patterns (regex-based detection)
    SECRET_PATTERNS = [
        (r'sk-[a-zA-Z0-9]{20,}', 'OPENAI_KEY'),
        (r'ghp_[a-zA-Z0-9]{36,}', 'GITHUB_TOKEN'),
        (r'AKIA[A-Z0-9]{16}', 'AWS_KEY'),
        (r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}', 'JWT'),
        (r'AIza[a-zA-Z0-9_-]{35}', 'GOOGLE_API_KEY'),
        (r'[0-9]{4,}:[A-Za-z0-9_-]{35,}', 'BOT_TOKEN'),
    ]

    # Keyword-based context patterns (case-insensitive)
    KEYWORD_PATTERNS = [
        (r'(?i)(TOKEN|API_KEY|SECRET|PASSWORD|PRIVATE_KEY)\s*[:=]\s*["\']?([^\s"\'\n]{8,})', 'ENV_SECRET'),
    ]

    def __init__(self, config: ReplayConfig):
        self.config = config
        self.projects_dir = Path(config.projects_dir).expanduser()

    def find_latest_session_jsonl(self) -> Optional[Path]:
        """Find the most recently modified JSONL file (excluding subagents/)."""
        if not self.projects_dir.exists():
            return None

        candidates = []
        for jsonl_path in self.projects_dir.glob('*.jsonl'):
            # Skip subagent directories
            if 'subagents' in str(jsonl_path):
                continue
            try:
                mtime = jsonl_path.stat().st_mtime
                candidates.append((mtime, jsonl_path))
            except OSError:
                continue

        if not candidates:
            return None

        candidates.sort(reverse=True)
        return candidates[0][1]

    def load_recent_turns(self, jsonl_path: Path) -> List[dict]:
        """
        Load conversation turns from JSONL within lookback window.
        Returns list of {type, content, timestamp} dicts.
        """
        from datetime import timezone
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.config.lookback_hours)
        turns = []
        estimated_tokens = 0

        try:
            with jsonl_path.open('r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line)
                        entry_type = entry.get('type')

                        # Extract message content
                        if entry_type in ['user', 'assistant']:
                            msg = entry.get('message', {})
                            if not isinstance(msg, dict):
                                continue  # Skip if message is not a dict
                            content_blocks = msg.get('content', [])
                            timestamp_str = entry.get('timestamp')

                            # Parse timestamp and filter by age
                            # For lookback_hours=0, we require timestamps and strict filtering
                            should_skip = False
                            if timestamp_str:
                                try:
                                    ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                    # Only filter if we have a valid timezone-aware cutoff
                                    if cutoff.tzinfo and ts < cutoff:
                                        should_skip = True
                                except (ValueError, AttributeError, TypeError):
                                    # If timestamp parse fails and lookback=0, skip
                                    if self.config.lookback_hours == 0:
                                        should_skip = True
                            else:
                                # No timestamp and lookback=0 → skip
                                if self.config.lookback_hours == 0:
                                    should_skip = True

                            if should_skip:
                                continue

                            # Format content
                            formatted = self._format_content_blocks(entry_type, content_blocks)
                            if formatted:
                                char_count = len(formatted)
                                estimated_tokens += int(char_count / self.config.char_per_token)

                                # Enforce token budget
                                if estimated_tokens > self.config.max_tokens:
                                    break

                                turns.append({
                                    'type': entry_type,
                                    'content': formatted,
                                    'timestamp': timestamp_str or 'unknown',
                                })

                    except (json.JSONDecodeError, KeyError, TypeError):
                        continue  # Skip malformed entries

        except OSError:
            return []

        return turns

    def _format_content_blocks(self, role: str, content_blocks: List) -> str:
        """Format message content blocks into readable text."""
        if not content_blocks:
            return ''

        parts = []
        for block in content_blocks:
            if isinstance(block, dict):
                block_type = block.get('type')

                if block_type == 'text':
                    text = block.get('text', '')
                    if text:
                        parts.append(text)

                elif block_type == 'tool_use':
                    name = block.get('name', 'unknown')
                    input_data = block.get('input', {})
                    parts.append(f'[Tool: {name}]')
                    if input_data:
                        parts.append(json.dumps(input_data, indent=2)[:500])  # Truncate long inputs

                elif block_type == 'tool_result':
                    tool_use_id = block.get('tool_use_id', 'unknown')
                    content = block.get('content', '')
                    parts.append(f'[Tool Result: {tool_use_id}]')
                    if isinstance(content, str):
                        parts.append(content[:1000])  # Truncate long results
                    else:
                        parts.append(str(content)[:1000])

            elif isinstance(block, str):
                parts.append(block)

        return '\n'.join(parts)

    def mask_secrets(self, text: str) -> Tuple[str, int]:
        """
        Mask secrets in text using regex patterns.
        Returns (masked_text, num_redactions).
        """
        if not self.config.mask_secrets:
            return text, 0

        masked = text
        redaction_count = 0

        # Apply regex-based patterns
        for pattern, label in self.SECRET_PATTERNS:
            matches = re.findall(pattern, masked)
            if matches:
                redaction_count += len(matches)
                masked = re.sub(pattern, f'<REDACTED:{label}>', masked)

        # Apply keyword-based patterns
        for pattern, label in self.KEYWORD_PATTERNS:
            matches = re.findall(pattern, masked)
            if matches:
                redaction_count += len(matches)
                # Replace only the value part, keep the key
                masked = re.sub(
                    pattern,
                    lambda m: f'{m.group(1)}=<REDACTED:{label}>',
                    masked
                )

        return masked, redaction_count

    def format_for_prepend(self, turns: List[dict]) -> str:
        """Format turns into markdown for prepending to session context."""
        if not turns:
            return ''

        lines = [
            '# Previous Session Transcript (C7 Conversation Replay)',
            '',
            f'Loaded {len(turns)} conversation turns from last {self.config.lookback_hours}h',
            'This verbatim transcript provides continuity from prior session.',
            '',
            '---',
            ''
        ]

        for turn in turns:
            role = turn['type']
            content = turn['content']
            timestamp = turn['timestamp']

            # Apply secret masking
            masked_content, redactions = self.mask_secrets(content)

            # Format as markdown
            lines.append(f'## {role.upper()} [{timestamp}]')
            if redactions > 0:
                lines.append(f'*(Note: {redactions} secret(s) redacted)*')
            lines.append('')
            lines.append(masked_content)
            lines.append('')
            lines.append('---')
            lines.append('')

        return '\n'.join(lines)

    def build_replay_context(self) -> Tuple[str, dict]:
        """
        Build complete replay context.
        Returns (formatted_context, metadata_dict).
        """
        metadata = {
            'success': False,
            'turns_loaded': 0,
            'secrets_redacted': 0,
            'source_file': None,
            'error': None,
        }

        try:
            # Find latest JSONL
            jsonl_path = self.find_latest_session_jsonl()
            if not jsonl_path:
                metadata['error'] = 'No JSONL files found'
                return '', metadata

            metadata['source_file'] = str(jsonl_path)

            # Load recent turns
            turns = self.load_recent_turns(jsonl_path)
            metadata['turns_loaded'] = len(turns)

            if not turns:
                metadata['error'] = 'No turns within lookback window'
                return '', metadata

            # Format for prepend
            formatted = self.format_for_prepend(turns)

            # Count total redactions in final output
            _, total_redactions = self.mask_secrets(formatted)
            metadata['secrets_redacted'] = total_redactions
            metadata['success'] = True

            return formatted, metadata

        except Exception as e:
            metadata['error'] = str(e)
            return '', metadata


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='C7 Conversation Replay Engine - Build verbatim session continuity context'
    )
    parser.add_argument(
        '--projects-dir',
        type=str,
        default='~/.claude/projects/-Users-haotianliu--openclaw-workspace-ystar-company',
        help='Path to Claude Code projects directory'
    )
    parser.add_argument(
        '--lookback-hours',
        type=int,
        default=24,
        help='Hours of conversation history to load (default: 24)'
    )
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=800_000,
        help='Maximum tokens for replay context (default: 800K)'
    )
    parser.add_argument(
        '--no-mask',
        action='store_true',
        help='Disable secret masking (dangerous, for debugging only)'
    )
    parser.add_argument(
        '--metadata',
        action='store_true',
        help='Print metadata JSON to stderr'
    )

    args = parser.parse_args()

    config = ReplayConfig(
        projects_dir=Path(args.projects_dir),
        lookback_hours=args.lookback_hours,
        max_tokens=args.max_tokens,
        mask_secrets=not args.no_mask,
    )

    replay = ConversationReplay(config)
    context, metadata = replay.build_replay_context()

    if args.metadata:
        print(json.dumps(metadata, indent=2), file=sys.stderr)

    if metadata['success']:
        print(context)
        return 0
    else:
        print(f'# C7 Replay unavailable: {metadata["error"]}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
