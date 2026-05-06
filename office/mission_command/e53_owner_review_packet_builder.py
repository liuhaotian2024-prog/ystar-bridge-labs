
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
PRODUCT_DIR = BRIDGE_ROOT / 'products/governed_agent_action_proof_packet'

PRIORITY_FILES = [
    'products/governed_agent_action_proof_packet/README.md',
    'products/governed_agent_action_proof_packet/proof_packet.json',
    'products/governed_agent_action_proof_packet/executive_brief.md',
    'products/governed_agent_action_proof_packet/limitations_and_no_overclaim.md',
    'products/governed_agent_action_proof_packet/owner_approval_checklist.md',
]


def build_owner_review_packet() -> dict[str, Any]:
    return {
        'review_packet_id': 'e53_owner_review_packet_for_governed_agent_action_proof_packet',
        'packet_id': 'governed_agent_action_proof_packet_e52',
        'language': 'zh-CN',
        'one_sentence': '这是一个本地、证据支持、可给老板审阅的 agent action governance proof packet。',
        'already_proven': [
            '本地 gov-mcp tool-layer allow/deny 证明已经闭合',
            'Y-star-gov/gov-mcp anti-drift validator 已能 ALLOW valid manifest / DENY broken fixture',
            'capability centerline binding gate 已通过',
            'CEO brain readback 已能读到 E52 proof packet 状态',
        ],
        'not_proven': [
            'no customer validation', 'no paid signal', 'real MCP transport not claimed', 'no production readiness claim', 'no enterprise compliance readiness claim', 'no expert feedback claim',
        ],
        'priority_files': PRIORITY_FILES,
        'owner_questions': [
            'packet 是否足够清楚？', '限制是否写得足够诚实？', 'no-overclaim 边界是否足够硬？', '是否可以准备单一受控 first-user review 计划？', '是否必须先补 real MCP transport？'
        ],
        'recommended_decision': '建议批准准备单一受控 first-user review 计划，但不批准发送、不批准发布、不批准识别真人、不批准 claim validation。',
        'if_approved_scope_only': ['prepare_single_controlled_first_user_review_plan', 'prepare_non_sent_outreach_draft', 'prepare_reviewer_category_criteria'],
        'still_forbidden': ['send_outreach', 'publish_packet', 'identify_real_reviewer', 'collect_contact_info', 'claim_customer_validation', 'claim_paid_signal', 'claim_real_mcp_transport_closed'],
        'owner_decision_status': 'pending_owner_decision',
        'external_action_allowed': False,
        'real_reviewer_identified': False,
        'customer_validation_claimed': False,
        'paid_signal_claimed': False,
        'real_mcp_transport_claimed': False,
        'no_external_action': True,
        'next_recommended_milestone': 'E54_owner_decision_or_controlled_first_user_review_plan',
    }


def render_owner_review_packet_md(packet: dict[str, Any]) -> str:
    lines = [
        '# E53 Owner Review Packet', '',
        packet['one_sentence'], '',
        '## 当前已经证明', *[f"- {x}" for x in packet['already_proven']], '',
        '## 当前没有证明', *[f"- {x}" for x in packet['not_proven']], '',
        '## 老板优先阅读的 5 个文件', *[f"- `{x}`" for x in packet['priority_files']], '',
        '## 老板需要判断的问题', *[f"- {x}" for x in packet['owner_questions']], '',
        '## 推荐判断', packet['recommended_decision'], '',
        '## 如果批准，只批准什么', *[f"- {x}" for x in packet['if_approved_scope_only']], '',
        '## 仍然绝对不能做', *[f"- {x}" for x in packet['still_forbidden']], '',
        'Owner decision status: `pending_owner_decision`.',
        'No external action occurred.', ''
    ]
    return '\n'.join(lines)


def write_owner_review_packet(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    packet = build_owner_review_packet()
    product = root / 'products/governed_agent_action_proof_packet'
    product.mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    product.joinpath('e53_owner_review_packet.json').write_text(json.dumps(packet, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    product.joinpath('e53_owner_review_packet.md').write_text(render_owner_review_packet_md(packet), encoding='utf-8')
    (root / 'reports/integration/e53_owner_review_packet_chinese.md').write_text(render_owner_review_packet_md(packet), encoding='utf-8')
    result = {'artifact_id': 'e53_owner_review_packet_result', 'packet_path': 'products/governed_agent_action_proof_packet/e53_owner_review_packet.md', 'json_path': 'products/governed_agent_action_proof_packet/e53_owner_review_packet.json', 'owner_decision_status': 'pending_owner_decision', 'recommended_decision': packet['recommended_decision'], 'external_action_allowed': False, 'no_external_action': True}
    (root / 'operations/external_validation/e53_owner_review_packet_result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    print(json.dumps(build_owner_review_packet(), indent=2, ensure_ascii=False))
