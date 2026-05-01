from pathlib import Path

from office.mission_command.evidence_gated_money_plan import build_evidence_gated_money_plan
from office.mission_command.mission_summary import build_mission_summary


REPO_ROOT = Path(__file__).resolve().parents[2]
MISSION = (
    "Aiden，带团队制定未来 7 天最可能产生第一笔真实收入或强付费信号的行动方案。"
    "要求不要锁死 Founder AI Workflow Audit，必须比较当前 top money paths，给出默认推荐、团队分工、可自主执行事项、需要我审批的事项。"
)


def test_mission_command_outputs_method_trace():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "Meta-Development Method Trace" in text
    assert "observe_internal" in text
    assert "compare_resources" in text
    assert "design_experiments" in text


def test_mission_command_outputs_next_executable_U():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "Next Executable U" in text
    assert "Within 48h" in text


def test_mission_command_outputs_resource_and_behavior_matrices():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "Resource Comparison" in text
    assert "Behavior Capability Matrix" in text
    assert "customer contact" in text
    assert "core writeback" in text


def test_mission_command_outputs_opportunity_space_and_default():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "Opportunity Space" in text
    assert "Top Opportunities" in text
    assert "Founder AI Workflow Audit" in text
    assert "Agent Workflow Bottleneck Diagnosis" in text


def test_evidence_gated_money_plan_contains_method_sections():
    plan = build_evidence_gated_money_plan(REPO_ROOT)
    assert plan["aiden_inferred_owner_objective"]
    assert plan["anti_prompt_overfit_check"]["risks"]
    assert plan["meta_development_method_trace"]
    assert plan["behavior_capability_matrix"]
    assert plan["opportunity_synthesis_by_lens"]
    assert plan["experiment_design"]
    assert plan["residual_plan"]


def test_no_external_side_effects():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "no external sending" in text


def test_no_coo_invented():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "COO" not in text
