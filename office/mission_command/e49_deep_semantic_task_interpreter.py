from __future__ import annotations

from typing import Any

from .e49_semantic_object_model import build_semantic_task, validate_semantic_object

TASK_FIXTURES = [
    'Make the deep semantic layer fully mature.',
    'How do we make money fastest?',
    'Prepare a first external user attempt.',
    'Fix gov-mcp server/client demo.',
    'Use our previous imagination and innovation modules.',
    'Reconnect CEO brain and field projection.',
]


def _contains(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def interpret_owner_task_semantically(task_text: str) -> dict[str, Any]:
    lower = task_text.lower()
    families: list[str] = []
    reqs: list[str] = []
    shallow: list[str] = []
    output_type = 'semantic_runtime_packet'
    if _contains(lower, ['semantic', 'meaning', 'understand']):
        families.extend(['semantic_object_model', 'semantic_graph', 'route_scorer', 'runtime_validation'])
        reqs.extend(['typed semantic objects', 'graph edges', 'validation', 'runtime integration'])
        shallow.append('keyword/tag matching without typed object validation')
    if _contains(lower, ['money', 'revenue', 'paid', 'cash']):
        families.extend(['commercial_route', 'value_object', 'evidence_burden', 'execution_blocker'])
        reqs.extend(['commercial assets', 'buyer pain', 'proof readiness', 'paid-signal boundary'])
        output_type = 'money_route_decision'
    if _contains(lower, ['external user', 'first user', 'outreach']):
        families.extend(['owner_approval_gate', 'no_contact_boundary', 'first_user_packet'])
        reqs.extend(['owner approval required', 'no real human identification', 'no contact info'])
        shallow.append('message draft or target list before approval')
    if _contains(lower, ['gov-mcp', 'server', 'client', 'demo']):
        families.extend(['gov_mcp_execution_boundary', 'minimal_mcp_client_path', 'local_cleanup'])
        reqs.extend(['server/client code inspection', 'sandbox', 'process/port cleanup'])
    if _contains(lower, ['imagination', 'innovation', 'creative', 'opportunity']):
        families.extend(['E34_strategic_imagination', 'E35_six_dimensional_cognition', 'E36_opportunity_evidence_ladder'])
        reqs.extend(['E34/E35/E36 cognition assets', 'high-imagination preservation'])
    if _contains(lower, ['ceo brain', 'memory', 'field projection', 'projection']):
        families.extend(['field_functional_projection', 'ceo_brain_context', 'wisdom_memory_kg'])
        reqs.extend(['field projection adapter', 'CEO brain adapter', 'KG/read-model context'])
    if not families:
        families.extend(['E42_resource_router', 'canonical_runtime_v2', 'side_effect_guard'])
        reqs.extend(['task routing', 'runtime decision', 'closure packet'])
    semantic_task = build_semantic_task(
        task_id='task_' + str(abs(hash(task_text)))[:8],
        owner_request=task_text,
        implicit_goal='produce value-oriented CEO action without shallow artifact churn',
    )
    return {
        'artifact_id': 'e49_deep_semantic_task_interpretation',
        'task_text': task_text,
        'semantic_task': semantic_task,
        'semantic_task_validation': validate_semantic_object(semantic_task),
        'explicit_request': task_text.strip(),
        'implicit_strategic_intent': semantic_task['implicit_goal'],
        'capability_families_required': sorted(set(families)),
        'value_production_relation': 'direct' if any(f in families for f in ['commercial_route', 'value_object', 'first_user_packet']) else 'enabling_runtime',
        'field_projection_requirement': 'required' if any(f in families for f in ['field_functional_projection', 'commercial_route', 'semantic_object_model']) else 'contextual',
        'ceo_brain_requirement': 'required' if any(f in families for f in ['ceo_brain_context', 'commercial_route', 'E34_strategic_imagination']) else 'contextual',
        'commercial_evidence_execution_audit_requirements': sorted(set(reqs + ['no-overclaim boundary', 'side-effect guard', 'CIEU/CZL closure'])),
        'forbidden_shortcuts': sorted(set(shallow + ['external action without owner approval', 'paid-signal claim without payment', 'customer validation claim without customer use'])),
        'what_would_count_as_shallow_answer': sorted(set(shallow + ['report-only output with no runtime object validation'])),
        'required_output_type': output_type,
        'no_external_action': True,
    }


def build_fixture_interpretations() -> dict[str, Any]:
    results = {task: interpret_owner_task_semantically(task) for task in TASK_FIXTURES}
    return {'artifact_id': 'e49_deep_semantic_task_interpreter_results', 'fixture_count': len(results), 'results': results, 'no_external_action': True}
