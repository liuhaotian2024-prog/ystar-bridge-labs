from pathlib import Path

from office.mission_command.counterfactual_router import CounterfactualRoute, route_counterfactual


ROOT = Path(__file__).resolve().parents[2]


def test_counterfactual_router_uses_method_kernel_protocol_if_router_implemented():
    decision = route_counterfactual(ROOT, CounterfactualRoute.REVENUE)
    assert decision.allowed is True
    assert "AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md" in decision.method_kernel_source
    assert "what_would_invalidate" in decision.required_fields

