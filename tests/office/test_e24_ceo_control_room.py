import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(rel): return json.loads((ROOT/rel).read_text(encoding="utf-8"))
def load_jsonl(rel): return [json.loads(line) for line in (ROOT/rel).read_text(encoding="utf-8").splitlines() if line.strip()]
def test_e24_ecosystem_archaeology_scans_all_repos_and_finds_ceo_assets():
    d=load("operations/external_validation/e24_whole_ecosystem_observation.json"); assert d["repos_scanned_count"]==4; assert d["local_legacy_ceo_brain_found"] is True; assert "reports/boot_packages/ceo.json" in d["local_legacy_ceo_brain_candidates"]; assert d["external_action_executed"] is False
def test_e24_existing_wheel_inventory_reuses_existing_wheels():
    d=load("operations/external_validation/e24_existing_wheel_inventory.json"); assert d["wheel_count"]>=30; assert d["reused_wheel_count"]>=25; assert any(w["repo"]=="gov-mcp" for w in d["wheels"])
def test_e24_duplicate_overlap_map_documents_without_destructive_refactor():
    d=load("operations/external_validation/e24_duplicate_overlap_map.json"); assert d["overlap_cluster_count"]>=5; assert d["destructive_refactor_performed"] is False
def test_e24_legacy_ceo_brain_archaeology_marks_items_noncanonical():
    d=load("operations/external_validation/e24_legacy_ceo_brain_archaeology.json"); assert d["local_legacy_ceo_brain_found"] is True; assert d["items_count"]>=5; assert all(i["promotion_status"]!="promoted_to_canonical" for i in d["extracted_items"])
def test_e24_legacy_ceo_brain_adapter_routes_candidates_to_kg():
    d=load("operations/external_validation/e24_legacy_ceo_brain_adapter.json"); assert d["candidate_node_count"]==d["candidate_edge_count"]; assert d["direct_canonical_write_performed"] is False
def test_e24_missing_wheel_analysis_implements_core_runtime_now():
    d=load("operations/external_validation/e24_missing_wheel_analysis.json"); assert d["missing_wheels_identified"]>=12; assert d["implemented_now_count"]>=10
def test_e24_mature_pattern_borrowing_is_marked_non_fresh_when_no_external_research():
    d=load("operations/external_validation/e24_mature_pattern_borrowing_matrix.json"); assert d["fresh_external_research_performed"] is False; assert d["pattern_count"]>=12
def test_e24_ceo_knowledge_graph_builder_creates_required_node_and_edge_types():
    nodes=load_jsonl("operations/knowledge_graph/e24_ceo_kg_nodes.jsonl"); edges=load_jsonl("operations/knowledge_graph/e24_ceo_kg_edges.jsonl"); assert {"Repo","Capability","Offer","RevenuePath","InnovationHypothesis","Blocker","Decision"} <= {n["type"] for n in nodes}; assert {"supports","requires","blocked_by","routes_to","governed_by"} <= {e["relationship"] for e in edges}
def test_e24_ceo_kg_entity_resolution_has_core_clusters():
    d=load("operations/knowledge_graph/e24_ceo_kg_entity_resolution.json"); assert d["cluster_count"]>=4; assert d["unresolved_entity_count"]==0
def test_e24_ceo_kg_evidence_binder_counts_legacy_and_hypothesis_nodes():
    d=load("operations/knowledge_graph/e24_ceo_kg_evidence_index.json"); assert d["evidence_bound_node_count"]>=15; assert d["legacy_derived_node_count"]>=5; assert d["generated_hypothesis_node_count"]>=10
def test_e24_ceo_kg_read_model_answers_business_questions():
    d=load("operations/knowledge_graph/e24_ceo_kg_read_model.json"); assert "48h" in d["question_answers"]["current_shortest_cash_path"]; assert d["question_answers"]["closest_sellable_offer"]=="48h AI Agent Implementation Readiness Review"; assert d["node_count"]>=35; assert d["edge_count"]>=25
def test_e24_ceo_brain_state_is_working_shadow_not_canonical():
    d=load("operations/external_validation/e24_ceo_brain_state.json"); assert d["state_type"]=="working_shadow_not_canonical_truth"; assert "live provider" in d["current_strategic_bottleneck"]; assert d["external_action_executed"] is False
def test_e24_field_functional_opportunity_map_ranks_opportunities():
    d=load("operations/external_validation/e24_field_functional_opportunity_map.json"); assert d["opportunity_nodes_count"]>=7; assert d["ranked_opportunities"][0]["rank"]==1; assert "score" in d["ranked_opportunities"][0]
def test_e24_commercial_imagination_engine_generates_hypotheses_not_facts():
    d=load("operations/external_validation/e24_commercial_imagination_paths.json"); assert d["path_count"]>=7; assert d["all_paths_are_hypotheses"] is True; assert all("money_reason" in p for p in d["paths"])
def test_e24_innovation_hypothesis_generator_links_capabilities():
    d=load("operations/external_validation/e24_innovation_hypotheses.json"); assert d["innovation_hypotheses_count"]>=8; assert all(h["source_capabilities"] for h in d["hypotheses"]); assert d["generated_hypothesis_not_fact"] is True
def test_e24_revenue_path_portfolio_selector_selects_shortest_cash_path():
    d=load("operations/external_validation/e24_revenue_path_portfolio_selection.json"); assert d["top_selected_path"]["id"]=="rev_path_readiness_review_ai_consultancies"; assert d["backup_paths"]; assert d["blocked_paths"]
def test_e24_ceo_execution_router_keeps_owner_manual_send_out_of_default():
    d=load("operations/external_validation/e24_ceo_execution_router.json"); assert d["owner_manual_send_is_default"] is False; assert len(d["autonomous_actions_recommended"])>=3; assert len(d["owner_approval_actions_required_by_risk"])==0; assert "real external send" in d["blocked_no_go_actions"]
def test_e24_strategic_memory_promotion_gate_blocks_canonical_truth_promotion():
    d=load("operations/external_validation/e24_strategic_memory_promotion_gate.json"); assert d["canonical_truth_promoted"] is False; assert "working_hypothesis" in d["allowed_states"]
def test_e24_ecosystem_route_registry_prevents_duplicate_wheels():
    d=load("operations/external_validation/e24_ecosystem_route_registry.json"); assert d["route_count"]>=8; assert "duplicate" in d["duplicate_wheel_prevention"]
def test_e24_ceo_control_room_unifies_kg_strategy_and_execution():
    d=load("operations/external_validation/e24_ceo_control_room.json"); assert d["whole_system_observation_summary"]["repos_scanned"]==4; assert d["kg_summary"]["node_count"]>=35; assert d["selected_path"]["id"]=="rev_path_readiness_review_ai_consultancies"; assert d["external_action_executed"] is False
def test_e24_ecosystem_alignment_gate_documents_read_only_repos():
    d=load("operations/external_validation/e24_ecosystem_alignment_gate.json"); assert set(d["repos_checked"])=={"ystar-bridge-labs","gov-mcp","Y-star-gov","ystar-company"}; assert d["gov_mcp_modified"] is False; assert d["closure_status"]=="ecosystem_aligned_with_documented_followups"
def test_e24_future_ceo_agent_policy_requires_kg_and_no_fake_evidence():
    d=load("operations/external_validation/e24_future_ceo_agent_policy.json"); assert "CEO KG update" in d["future_commercial_milestone_requirements"]; assert "explicit no-fake-evidence statement" in d["future_commercial_milestone_requirements"]; assert d["owner_manual_send_default_allowed"] is False
def test_e24_czl_closure_proves_no_external_action_and_shadow_state():
    d=load("operations/external_validation/e24_czl_closure.json"); assert d["whole_ecosystem_inspected"] is True; assert d["no_real_external_action_occurred"] is True; assert d["no_provider_api_called"] is True; assert d["no_message_sent"] is True; assert d["ceo_brain_state_type"]=="working_shadow_not_canonical_truth"
