
from __future__ import annotations

import json
import os
from pathlib import Path

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
PRODUCT_DIR = BRIDGE_ROOT / 'products/governed_agent_action_proof_packet'


def build_non_sent_review_request_template() -> dict:
    return {
        'template_id': 'e53_non_sent_review_request_template',
        'status': 'template_only_not_sent',
        'short_intro': 'I am preparing a local proof packet for governed agent actions and would like feedback only if the owner approves a future review step.',
        'why_review_is_requested': 'to test clarity, credibility, proof gaps, and language risk',
        'what_the_packet_is': 'a local tool-layer proof packet with evidence and no-overclaim boundaries',
        'what_the_packet_is_not': ['not customer validated', 'no paid signal', 'real MCP transport not claimed', 'not production readiness evidence'],
        'review_questions': ['Is the packet understandable?', 'Which proof is missing?', 'Which language feels too strong?', 'What local demo would help?'],
        'explicit_no_overclaim_language': 'This is a local proof packet, not a customer-validated product, with no sales ask and no paid ask.',
        'request_type': 'feedback only',
        'sales_ask': False,
        'paid_ask': False,
        'sent': False,
        'contact_identified': False,
        'contact_info_collected': False,
        'owner_approval_required_before_send': True,
        'no_external_action': True,
    }


def render_template_md(template: dict) -> str:
    return '\n'.join([
        '# E53 Non-Sent Review Request Template', '',
        '**Status:** template only, not sent.', '',
        template['short_intro'], '',
        'I am asking for feedback only. This is a local proof packet, not a customer-validated product, with no sales ask and no paid ask.', '',
        '## What it is', template['what_the_packet_is'], '',
        '## What it is not', *[f"- {x}" for x in template['what_the_packet_is_not']], '',
        '## Review questions', *[f"- {x}" for x in template['review_questions']], '',
        'Owner approval is required before any send, publication, real reviewer identification, or contact information collection.', ''
    ])


def write_non_sent_review_request_template(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    product = root / 'products/governed_agent_action_proof_packet'
    product.mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    template = build_non_sent_review_request_template()
    product.joinpath('e53_non_sent_review_request_template.json').write_text(json.dumps(template, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    product.joinpath('e53_non_sent_review_request_template.md').write_text(render_template_md(template), encoding='utf-8')
    result = {'artifact_id': 'e53_non_sent_review_request_template_result', 'sent': False, 'contact_identified': False, 'contact_info_collected': False, 'owner_approval_required_before_send': True, 'no_external_action': True}
    (root / 'operations/external_validation/e53_non_sent_review_request_template_result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    print(json.dumps(build_non_sent_review_request_template(), indent=2, ensure_ascii=False))
