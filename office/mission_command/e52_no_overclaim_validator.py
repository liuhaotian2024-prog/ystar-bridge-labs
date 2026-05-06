from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
PRODUCT_DIR = BRIDGE_ROOT / 'products/governed_agent_action_proof_packet'
FORBIDDEN_PATTERNS = [
    'customer validated', 'customer-approved', 'paying customer', 'production ready',
    'production proven', 'enterprise certified', 'compliance certified',
    'real MCP transport closed', 'real MCP client/server complete', 'expert validated',
    'expert reviewed', 'outreach completed', 'externally validated',
]
SENSITIVE_CONTEXT_PATTERNS = ['published', 'contacted', 'paid signal']
REQUIRED_DISCLAIMERS = [
    'real MCP transport not claimed', 'no customer validation', 'no paid signal',
    'no outreach', 'no publication', 'owner approval required before external contact/publication',
    'local tool-layer proof only',
]


def _is_negated_or_boundary_line(line: str, phrase: str) -> bool:
    lower = line.lower()
    phrase_lower = phrase.lower()
    allowed_prefixes = [f'no {phrase_lower}', f'not {phrase_lower}', f'without {phrase_lower}']
    if any(prefix in lower for prefix in allowed_prefixes):
        return True
    if any(marker in lower for marker in ['forbidden', 'forbidden_language', 'forbidden_claims', 'unsupported_claims', 'do not say', 'do not claim', 'does not prove', 'without claiming', 'not claimed', 'not_published', 'not_contacted', 'false', 'no_']):
        return True
    return False


def validate_no_overclaim(product_dir: Path | None = None) -> dict[str, Any]:
    product = product_dir or PRODUCT_DIR
    scanned = []
    violations = []
    text_blob = ''
    for path in sorted(product.rglob('*')) if product.exists() else []:
        if not path.is_file() or path.suffix.lower() not in {'.md', '.json', '.txt'}:
            continue
        text = path.read_text(encoding='utf-8', errors='ignore')
        text_blob += '\n' + text.lower()
        try:
            rel_path = str(path.relative_to(BRIDGE_ROOT))
        except ValueError:
            rel_path = str(path.relative_to(product.parent.parent if product.name == 'governed_agent_action_proof_packet' else product))
        scanned.append(rel_path)
        for pattern in FORBIDDEN_PATTERNS + SENSITIVE_CONTEXT_PATTERNS:
            for line_no, line in enumerate(text.splitlines(), 1):
                if pattern.lower() in line.lower() and not _is_negated_or_boundary_line(line, pattern):
                    try:
                        violation_path = str(path.relative_to(BRIDGE_ROOT))
                    except ValueError:
                        violation_path = str(path)
                    violations.append({'path': violation_path, 'line': line_no, 'pattern': pattern, 'line_text': line[:240]})
    missing = [disc for disc in REQUIRED_DISCLAIMERS if disc.lower() not in text_blob]
    return {
        'artifact_id': 'e52_no_overclaim_validation_result',
        'scanned_file_count': len(scanned),
        'scanned_files': scanned,
        'violations': violations,
        'missing_required_disclaimers': missing,
        'passed': not violations and not missing,
        'no_external_action': True,
    }


def render_no_overclaim_markdown(data: dict[str, Any]) -> str:
    return '\n'.join(['# E52 No-Overclaim Validation', '', f"Passed: `{data['passed']}`", f"Scanned files: {data['scanned_file_count']}", f"Violations: {len(data['violations'])}", f"Missing disclaimers: {len(data['missing_required_disclaimers'])}", '', 'No external action occurred.', ''])


def write_no_overclaim_validation(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = validate_no_overclaim(root / 'products/governed_agent_action_proof_packet')
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e52_no_overclaim_validation_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e52_no_overclaim_validation_result.md').write_text(render_no_overclaim_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(validate_no_overclaim(), indent=2, ensure_ascii=False))
