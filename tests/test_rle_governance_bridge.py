"""
test_rle_governance_bridge.py  —  RLE→GovernanceLoop escalation bridge unit test
===================================================================================

AMENDMENT-014 bridge verification: ResidualLoopEngine emits suggestions to
GovernanceLoop when task does not converge.

Test scenario:
  1. Mock RLE with non-converging task (Rt+1 stays high)
  2. Trigger escalation (max_iterations exceeded)
  3. Verify GovernanceLoop.receive_rle_suggestion() called
  4. Verify _rle_suggestions list populated
"""
import pytest
from unittest.mock import Mock, MagicMock
from ystar.governance.residual_loop_engine import ResidualLoopEngine
from ystar.governance.governance_loop import GovernanceLoop
from ystar.governance.reporting import ReportEngine
from ystar.governance.omission_engine import OmissionStore
from ystar.governance.cieu_store import CIEUStore


def test_rle_escalates_to_governance_loop_on_max_iterations():
    """
    Verify RLE calls governance_suggestion_callback when max_iterations exceeded.
    """
    # Setup
    cieu_store = CIEUStore()
    mock_autonomy_engine = Mock()
    mock_autonomy_engine.pull_next_action = Mock(return_value=Mock(description="mock_action"))

    received_suggestions = []

    def suggestion_callback(suggestion_dict):
        """Capture suggestions for verification."""
        received_suggestions.append(suggestion_dict)

    rle = ResidualLoopEngine(
        autonomy_engine=mock_autonomy_engine,
        cieu_store=cieu_store,
        target_provider=lambda event: event.get("params", {}).get("target_y_star"),
        max_iterations=3,
        convergence_epsilon=0.01,
        damping_gamma=0.9,
        governance_suggestion_callback=suggestion_callback,
    )

    # Simulate non-converging task (high residual, multiple iterations)
    session_id = "test_session_001"
    agent_id = "test_agent"
    for i in range(5):  # Exceeds max_iterations=3
        event = {
            "session_id": session_id,
            "agent_id": agent_id,
            "event_type": "TASK_STEP",
            "params": {
                "target_y_star": "complete_task",
                "y_actual": f"incomplete_step_{i}",
            },
        }
        rle.on_cieu_event(event)

    # Verify callback was triggered
    assert len(received_suggestions) >= 1, "Expected at least 1 escalation suggestion"
    last_suggestion = received_suggestions[-1]
    assert last_suggestion["source"] == "residual_loop_engine"
    assert last_suggestion["trigger"] == "max_iterations_exceeded"
    assert last_suggestion["session_id"] == session_id
    assert "non-convergent" in last_suggestion["rationale"].lower()


def test_governance_loop_receives_rle_suggestion():
    """
    Verify GovernanceLoop.receive_rle_suggestion() stores RLE escalations.
    """
    # Setup GovernanceLoop
    omission_store = OmissionStore()
    report_engine = ReportEngine(omission_store=omission_store)
    loop = GovernanceLoop(report_engine=report_engine)

    # Simulate RLE suggestion
    suggestion_dict = {
        "source": "residual_loop_engine",
        "trigger": "oscillation_detected",
        "session_id": "test_session_002",
        "agent_id": "test_agent",
        "residual_rt_plus_1": 0.35,
        "residual_history": [0.4, 0.3, 0.38, 0.32, 0.35],
        "rationale": "Task oscillating with Rt+1=0.35. Path A should inspect causal chain.",
        "suggested_action": "inspect_causal_chain",
    }

    loop.receive_rle_suggestion(suggestion_dict)

    # Verify suggestion stored
    assert len(loop._rle_suggestions) == 1
    stored_suggestion = loop._rle_suggestions[0]
    assert stored_suggestion.suggestion_type == "rle_escalation"
    assert stored_suggestion.target_rule_id == "inspect_causal_chain"
    assert stored_suggestion.current_value == 0.35
    assert stored_suggestion.suggested_value == 0.0  # Target: converge to zero
    assert stored_suggestion.confidence == 0.8
    assert "oscillating" in stored_suggestion.rationale.lower()


def test_rle_oscillation_triggers_callback():
    """
    Verify RLE detects oscillation and calls governance_suggestion_callback.
    """
    cieu_store = CIEUStore()
    mock_autonomy_engine = Mock()
    mock_autonomy_engine.pull_next_action = Mock(return_value=Mock(description="mock_action"))

    received_suggestions = []

    def suggestion_callback(suggestion_dict):
        received_suggestions.append(suggestion_dict)

    rle = ResidualLoopEngine(
        autonomy_engine=mock_autonomy_engine,
        cieu_store=cieu_store,
        target_provider=lambda event: event.get("params", {}).get("target_y_star"),
        max_iterations=20,  # High limit to test oscillation path
        convergence_epsilon=0.01,
        damping_gamma=0.9,
        governance_suggestion_callback=suggestion_callback,
    )

    # Simulate oscillating residuals (±振荡模式)
    session_id = "test_session_003"
    agent_id = "test_agent"
    oscillating_residuals = [0.5, 0.3, 0.48, 0.32, 0.51, 0.29, 0.49]  # Oscillates around 0.4
    for i, expected_rt in enumerate(oscillating_residuals):
        event = {
            "session_id": session_id,
            "agent_id": agent_id,
            "event_type": "TASK_STEP",
            "params": {
                "target_y_star": 1.0,  # Numeric target for easy distance computation
                "y_actual": 1.0 - expected_rt,  # y_actual chosen to produce expected residual
            },
        }
        rle.on_cieu_event(event)

    # Verify oscillation callback triggered
    assert len(received_suggestions) >= 1, "Expected oscillation to trigger suggestion"
    last_suggestion = received_suggestions[-1]
    assert last_suggestion["source"] == "residual_loop_engine"
    assert last_suggestion["trigger"] == "oscillation_detected"
    assert "oscillating" in last_suggestion["rationale"].lower()


def test_rle_convergence_does_not_trigger_callback():
    """
    Verify RLE does NOT call governance_suggestion_callback when task converges.
    """
    cieu_store = CIEUStore()
    mock_autonomy_engine = Mock()

    received_suggestions = []

    def suggestion_callback(suggestion_dict):
        received_suggestions.append(suggestion_dict)

    rle = ResidualLoopEngine(
        autonomy_engine=mock_autonomy_engine,
        cieu_store=cieu_store,
        target_provider=lambda event: event.get("params", {}).get("target_y_star"),
        max_iterations=10,
        convergence_epsilon=0.05,
        damping_gamma=0.9,
        governance_suggestion_callback=suggestion_callback,
    )

    # Simulate converging task
    session_id = "test_session_004"
    agent_id = "test_agent"
    event = {
        "session_id": session_id,
        "agent_id": agent_id,
        "event_type": "TASK_STEP",
        "params": {
            "target_y_star": "complete_task",
            "y_actual": "complete_task",  # Perfect match → Rt+1 = 0
        },
    }
    rle.on_cieu_event(event)

    # Verify no callback triggered (converged, no escalation needed)
    assert len(received_suggestions) == 0, "Expected no suggestion when task converges"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
