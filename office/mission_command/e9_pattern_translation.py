from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from .external_pattern_mining import ExternalPattern


@dataclass(frozen=True)
class PatternTranslation:
    pattern_id: str
    external_pattern: str
    ybridge_equivalent: str
    current_implementation_status: str
    target_module: str
    implementation_action: str
    test_requirement: str
    residual_risk: str
    owner_burden_effect: str
    m3_effect: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


REQUIRED_TRANSLATIONS = {
    "pattern_govern_map_measure_manage": (
        "CZL + Evidence + Action Risk Loop",
        "partial",
        "office/mission_command/strict_czl.py",
        "Use NIST-style govern/map/measure/manage language to frame E9 closure and validation controls.",
    ),
    "pattern_ai_management_system_continuous_improvement": (
        "Method kernel + report lifecycle",
        "partial",
        "knowledge/ceo/wisdom/AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md",
        "Add external pattern mining as a concrete method learning loop.",
    ),
    "pattern_agentic_risk_taxonomy": (
        "E8/E9 action preflight risk labels",
        "partial",
        "office/mission_command/e9_external_action_preflight.py",
        "Add agentic-risk-informed checks for manifest, target, draft, scope, suppression, and feedback provenance.",
    ),
    "pattern_tool_consent_scope_minimization": (
        "Least-privilege target/channel/draft/action scopes",
        "missing",
        "office/mission_command/e9_scope_minimization.py",
        "Require target, channel, draft, count, time, follow-up, data, and feedback scopes before external actions.",
    ),
    "pattern_human_in_loop_approve_edit_reject": (
        "Approval decision model",
        "missing",
        "office/mission_command/e9_approval_decision_model.py",
        "Represent approve, edit, reject, hold, and escalate decisions.",
    ),
    "pattern_opt_out_suppression": (
        "Suppression registry",
        "missing",
        "office/mission_command/e9_suppression_registry.py",
        "Block opted-out, invalid, out-of-scope, or duplicate-over-limit targets.",
    ),
    "pattern_action_trace_ledger": (
        "Action and feedback ledger requirements",
        "partial",
        "office/mission_command/e9_validation_execution.py",
        "Require an action ledger if Aiden ever sends and a feedback ledger for observed responses.",
    ),
    "pattern_progressive_autonomy": (
        "Progressive autonomy ladder",
        "missing",
        "office/mission_command/e9_progressive_autonomy.py",
        "Map L0 internal-only through L5 commercial/production blocked-in-E9.",
    ),
}


def translate_patterns_to_architecture(patterns: List[ExternalPattern]) -> List[PatternTranslation]:
    by_id = {pattern.pattern_id: pattern for pattern in patterns}
    translations: List[PatternTranslation] = []
    for pattern_id, (equivalent, status, module, action) in REQUIRED_TRANSLATIONS.items():
        pattern = by_id.get(pattern_id)
        if not pattern:
            continue
        translations.append(
            PatternTranslation(
                pattern_id=pattern_id,
                external_pattern=pattern.pattern_name,
                ybridge_equivalent=equivalent,
                current_implementation_status=status,
                target_module=module,
                implementation_action=action,
                test_requirement=f"Test that {equivalent} is represented and cannot be bypassed in E9.",
                residual_risk=pattern.residual_risk,
                owner_burden_effect="Lowers owner burden by turning vague review into explicit decisions and scopes.",
                m3_effect="Improves safe external learning velocity for first-revenue validation.",
            )
        )
    return translations


def render_e9_pattern_to_architecture_translation(translations: List[PatternTranslation]) -> str:
    lines = [
        "# E9 Pattern-to-Architecture Translation",
        "",
        f"- translation_count: {len(translations)}",
        "",
    ]
    for item in translations:
        lines.extend(
            [
                f"## {item.pattern_id}",
                f"- external_pattern: {item.external_pattern}",
                f"- Y*Bridge equivalent: {item.ybridge_equivalent}",
                f"- current_implementation_status: {item.current_implementation_status}",
                f"- target_module: {item.target_module}",
                f"- implementation_action: {item.implementation_action}",
                f"- test_requirement: {item.test_requirement}",
                f"- residual_risk: {item.residual_risk}",
                f"- owner_burden_effect: {item.owner_burden_effect}",
                f"- M-3 effect: {item.m3_effect}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()
