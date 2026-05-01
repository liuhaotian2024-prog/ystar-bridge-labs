from pathlib import Path

from office.aiden_meeting_room.company_context_loader import load_company_context
from office.mission_command.meta_development_method_kernel import (
    build_meta_development_trace,
    design_experiments,
    detect_prompt_overfit_risk,
    infer_deeper_objective,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_infer_deeper_objective_does_not_overfit_budget_phrase():
    objective = infer_deeper_objective("我们是不是应该先找有预算的客户？")
    assert "budget, urgency, and Y*Bridge Labs advantage overlap" in objective
    assert "grant" in objective
    assert "RFP" in objective


def test_prompt_overfit_detection_flags_narrow_budget_or_offer_focus():
    risk = detect_prompt_overfit_risk("先找 budget，然后最快拿第一笔收入")
    joined = " ".join(risk["risks"])
    assert "budget_phrase_overfit" in joined
    assert "first_revenue_overfit" in joined


def test_method_trace_contains_internal_and_external_observe():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    assert "observe_internal" in trace["method_steps"]
    assert "observe_external_status" in trace["method_steps"]
    assert trace["inferred_objective"]


def test_aiden_context_loader_includes_method_kernel_doctrine():
    ctx = load_company_context(REPO_ROOT)
    assert "knowledge/ceo/wisdom/AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md" in ctx.source_texts
    assert "observe/compare/capability/opportunity" in ctx.methodology_summary


def test_method_trace_marks_external_observe_not_run_when_live_research_disabled():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    assert trace["external_world_state"]["status"] in {"ARCHITECTURE_ONLY", "FIXTURE_ONLY", "NOT_READY"}
    assert trace["external_world_state"]["live_research_executed"] is False
    assert trace["evidence_status"]["confidence"] != "evidence_backed_live_read_only"


def test_experiment_design_contains_48h_internal_experiment():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    experiment = design_experiments(trace["top_opportunities"][0])
    assert "48h" in experiment["48h_internal_experiment"]
    assert "Tier 1" in experiment["tier1_read_only_research_experiment"]


def test_experiment_design_contains_kill_condition():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    experiment = design_experiments(trace["top_opportunities"][0])
    assert "kill_condition" in experiment
    assert "No clear pain" in experiment["kill_condition"]


def test_owner_burden_minimization_present():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    assert "manual ops" in trace["owner_burden"]
    assert trace["method_compliance"]["has_owner_burden_statement"] is True


def test_no_coo_invented():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    assert "COO" not in str(trace)
