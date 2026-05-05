from __future__ import annotations

from typing import Any

from .e44a_capability_archaeology import build_full_ceo_capability_archaeology

def diagnose_capability_breakage(archaeology: dict[str, Any] | None = None) -> dict[str, Any]:
    archaeology = archaeology or build_full_ceo_capability_archaeology()
    resources = archaeology["resources"]
    def sample(predicate):
        return [r["path"] for r in resources if predicate(r)][:8]
    definitions = [
        ("artifact_accessor_only", sample(lambda r: r["resource_type"] == "artifact_accessor"), "Capability-named modules often only load JSON artifacts."),
        ("static_artifact_not_runtime", sample(lambda r: r["resource_type"] == "static_artifact" and r["milestone"] in {"E35", "E36", "E39", "E41"}), "Valuable reasoning exists but is not invoked during tasks."),
        ("missing_first_class_tags", ["office/mission_command/e42_task_capability_matcher.py"], "E42 lacks first-class imagination/innovation/six-dimensional/opportunity tags."),
        ("missing_synonyms", ["office/mission_command/e42_task_capability_matcher.py"], "Strategic/customer/commercial terms do not route to E35/E36 capabilities."),
        ("workflow_coverage", ["office/mission_command/e42_ceo_task_preflight_packet.py", "office/mission_command/e43_first_value_loop_runner.py"], "Router-first workflow covered over cognition-first workflow."),
        ("test_blind_spot", sample(lambda r: r["resource_type"] == "test_only" and r["milestone"] in {"E35", "E36", "E42", "E43"}), "Tests checked existence/boundaries more than invocation."),
        ("no_task_time_cascade", ["no pre-E44A cascade runtime found"], "No required cascade invokes cognition, customer, commercial, evidence, execution, and reuse together."),
        ("no_activation_registry", ["no pre-E44A activation registry found"], "No durable callable activation map existed."),
        ("overconservative_boundary_drift", ["E40/E42/E43 boundary artifacts"], "Valid external-action boundaries narrowed strategic cognition."),
        ("hardcoded_or_local_only_paths", [r["path"] for r in resources if r["repo"] == "ystar-bridge-labs" and "host-local" in r["path"]][:8], "Host-local assumptions exist in delivery/runtime layers."),
    ]
    return {
        "artifact_id": "e44a_capability_breakage_root_cause",
        "root_causes": [{
            "root_cause": name,
            "evidence_paths": paths,
            "evidence_structure": evidence,
            "impact_on_CEO_task_quality": "CEO behaves like a resource router/safety secretary when this is uncorrected.",
            "fix_implemented_in_E44A": "activation registry, cognition overlay, cascade runtime, E43 replay, and preflight v2",
            "residual_risk": "Future serious company tasks must use preflight v2 rather than router-only flow.",
        } for name, paths, evidence in definitions],
        "no_external_action": True,
    }
