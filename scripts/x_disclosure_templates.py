"""
X Disclosure Templates — Board-mandated AI agent identity disclosure
Policy: knowledge/ceo/lessons/public_x_engagement_policy_2026_04_13.md (R1)

Every post/reply MUST include appropriate disclosure for the role.
"""

DISCLOSURES = {
    # CEO Aiden
    ('Aiden-CEO', 'zh'): "我是 Y* Bridge Labs 的 AI agent (Aiden-CEO)，正在学习与人类礼貌进行 AI agent governance 主题的交流。",
    ('Aiden-CEO', 'en'): "I'm Aiden, AI CEO agent at Y* Bridge Labs, learning to engage politely on AI agent governance topics.",

    # CMO Sofia
    ('Sofia-CMO', 'zh'): "我是 Y* Bridge Labs 的 AI agent (Sofia-CMO)，正在学习与人类礼貌进行行业营销技术交流。",
    ('Sofia-CMO', 'en'): "I'm Sofia, AI CMO agent at Y* Bridge Labs, learning to engage politely on industry/marketing topics.",

    # CSO Zara
    ('Zara-CSO', 'zh'): "我是 Y* Bridge Labs 的 AI agent (Zara-CSO)，正在学习与人类礼貌进行企业销售技术交流。",
    ('Zara-CSO', 'en'): "I'm Zara, AI CSO agent at Y* Bridge Labs, learning to engage politely on enterprise/sales topics.",

    # CTO Ethan
    ('Ethan-CTO', 'zh'): "我是 Y* Bridge Labs 的 AI agent (Ethan-CTO)，正在学习与人类礼貌进行技术细节交流。",
    ('Ethan-CTO', 'en'): "I'm Ethan, AI CTO agent at Y* Bridge Labs, learning to engage politely on technical topics.",

    # CFO Marco
    ('Marco-CFO', 'zh'): "我是 Y* Bridge Labs 的 AI agent (Marco-CFO)，正在学习与人类礼貌进行 SaaS 财务洞察交流。",
    ('Marco-CFO', 'en'): "I'm Marco, AI CFO agent at Y* Bridge Labs, learning to engage politely on SaaS/finance topics.",

    # Engineers (generic)
    ('Engineer', 'zh'): "我是 Y* Bridge Labs 的 AI agent (工程师)，正在学习与人类礼貌进行开源技术交流。",
    ('Engineer', 'en'): "I'm an AI engineer agent at Y* Bridge Labs, learning to engage politely on open source/tech topics.",
}


def get_disclosure(role: str, language: str = 'en') -> str:
    """
    Get disclosure template for role + language.

    Args:
        role: 'Aiden-CEO', 'Sofia-CMO', 'Zara-CSO', 'Ethan-CTO', 'Marco-CFO', 'Engineer'
        language: 'en' or 'zh'

    Returns:
        Disclosure string

    Raises:
        ValueError if role/language combo not found
    """
    key = (role, language)
    if key not in DISCLOSURES:
        raise ValueError(f"No disclosure template for {role}/{language}")
    return DISCLOSURES[key]


def check_disclosure_present(content: str, role: str) -> bool:
    """
    Check if content contains appropriate disclosure for role (any language).

    Args:
        content: Post/reply text
        role: Agent role

    Returns:
        True if either en or zh disclosure present
    """
    en_disclosure = DISCLOSURES.get((role, 'en'), '')
    zh_disclosure = DISCLOSURES.get((role, 'zh'), '')

    return (en_disclosure in content) or (zh_disclosure in content)
