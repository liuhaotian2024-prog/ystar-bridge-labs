import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e44a_czl_closure_shape_and_no_external_action():
    artifact = json.loads((ROOT / "operations/external_validation/e44a_czl_closure.json").read_text())
    required = [
        "capability_archaeology_completed",
        "activation_registry_created",
        "ceo_cognition_cascade_created",
        "E43_task_replayed",
        "no_second_CEO_brain",
        "no_second_CEO_KG",
        "no_customer_contact",
        "no_expert_contact",
        "no_send",
        "no_provider_API_or_tool_execution",
        "no_payment",
        "no_secret_use",
        "no_customer_validation_claimed",
        "no_paid_signal_claimed",
    ]
    for key in required:
        assert artifact[key] is True
