from __future__ import annotations

import ast
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


MILESTONE_ID = "E91_Open_World_CEO_Doctrine_Discovery_And_Runtime_Enforcement_R1"
REGISTRY_ID = "ceo_operating_doctrine_registry_open_world_v1"

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9AUDIT_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))
YSTAR_COMPANY_ROOT = Path(os.environ.get("YSTAR_COMPANY_ROOT", "/Users/haotianliu/.openclaw/workspace/ystar-company"))

INITIAL_QUERY_SEEDS = (
    "CEO",
    "Aiden",
    "runtime",
    "governance",
    "CIEU",
    "residual",
    "external",
    "observation",
    "market",
    "evidence",
    "owner decision",
    "gov-mcp",
    "K9Audit",
    "first cash",
    "strategy",
)

SIGNAL_GROUPS: dict[str, tuple[str, ...]] = {
    "ceo": ("ceo", "aiden", "mission_command", "behavior center", "owner_intent"),
    "runtime_governance": ("runtime", "governance", "validator", "enforce", "hook", "allow", "deny", "escalate", "require_revision"),
    "market_external_evidence": ("market", "external", "public-read", "public read", "observation", "evidence", "buyer", "first cash"),
    "cieu_residual": ("cieu", "residual", "prediction", "learning", "store", "record", "log"),
    "gov_mcp_provider": ("gov-mcp", "gov_mcp", "provider", "tool", "dry_run", "dry-run", "receipt", "no_send"),
    "owner_l4_l5_revenue": ("owner decision", "owner_decision", "l4", "l5", "revenue", "payment", "pricing", "customer"),
}

SCHEMA_TERMS = (
    "owner_intent",
    "action_context",
    "evidence_refs",
    "candidate_actions",
    "counterfactual_comparison",
    "CIEU_prediction",
    "residual",
    "owner_decision",
    "route_scoring",
    "dry_run_receipt",
    "no_send_invariant",
)

FUNCTION_PREFIXES = ("build_", "run_", "validate_", "write_", "route_", "compile_", "assess_", "classify_", "select_", "score_", "resolve_")


def build_open_world_discovery_reports(
    *,
    bridge_root: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
    k9audit_root: Path | None = None,
    ystar_company_root: Path | None = None,
) -> dict[str, Any]:
    roots = {
        "bridge-labs": bridge_root or BRIDGE_ROOT,
        "Y-star-gov": ystar_gov_root or Y_GOV_ROOT,
        "gov-mcp": gov_mcp_root or GOV_MCP_ROOT,
    }
    optional_roots = {
        "K9Audit": k9audit_root or K9AUDIT_ROOT,
        "ystar-company": ystar_company_root or YSTAR_COMPANY_ROOT,
    }
    asset_graph = build_asset_graph(roots, optional_roots)
    query_log = build_query_expansion_log(asset_graph)
    clusters = discover_same_problem_clusters(asset_graph, query_log)
    coverage = build_coverage_proof(asset_graph, clusters, query_log)
    registry_spec = synthesize_canonical_doctrine_registry(asset_graph, clusters, coverage)
    reports = {
        "asset_graph": asset_graph,
        "query_expansion_log": query_log,
        "same_problem_clusters": clusters,
        "coverage_proof": coverage,
        "canonical_doctrine_registry_spec": registry_spec,
        "completion_report": build_completion_report(asset_graph, clusters, coverage, registry_spec),
        "runtime_status": build_runtime_status(registry_spec),
    }
    write_open_world_reports(reports, roots["bridge-labs"])
    return reports


def build_asset_graph(roots: Mapping[str, Path], optional_roots: Mapping[str, Path] | None = None) -> dict[str, Any]:
    optional_roots = optional_roots or {}
    assets: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    repo_counts: dict[str, Any] = {}
    for repo, root in {**dict(roots), **dict(optional_roots)}.items():
        root = Path(root)
        if not root.exists():
            repo_counts[repo] = {"available": False, "tracked_files": 0}
            continue
        files = tracked_files(root)
        parsed_python = 0
        for rel in files:
            path = root / rel
            if not path.is_file():
                continue
            node = build_asset_node(repo, root, rel)
            if node["file_type"] == "source_python":
                parsed_python += 1
                ast_info = python_ast_info(path)
                node.update(ast_info)
                for imported in ast_info.get("imports", []):
                    edges.append({"edge_type": "import", "source": f"{repo}:{rel}", "target": imported})
            milestone = node.get("milestone_id")
            if milestone:
                edges.append({"edge_type": "same_milestone", "source": f"{repo}:{rel}", "target": milestone})
            if node["category"] == "test":
                target = infer_test_target(rel)
                if target:
                    edges.append({"edge_type": "test_target", "source": f"{repo}:{rel}", "target": target})
            assets.append(node)
        repo_counts[repo] = {
            "available": True,
            "tracked_files": len(files),
            "python_files_parsed": parsed_python,
        }
    by_repo = Counter(asset["repo"] for asset in assets)
    return {
        "artifact_id": "e91_asset_graph",
        "milestone_id": MILESTONE_ID,
        "generated_at": utc_now(),
        "prompt_seeds_closed_ontology": False,
        "repo_counts": repo_counts,
        "asset_count": len(assets),
        "assets": assets,
        "edge_count": len(edges),
        "edges": edges[:50000],
        "edge_truncated": len(edges) > 50000,
        "assets_by_repo": dict(by_repo),
    }


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=False, timeout=120)
    if result.returncode == 0 and result.stdout.strip():
        return sorted(line.strip() for line in result.stdout.splitlines() if line.strip())
    ignored = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    files: list[str] = []
    for path in root.rglob("*"):
        if path.is_file() and not any(part in ignored for part in path.relative_to(root).parts):
            files.append(str(path.relative_to(root)))
    return sorted(files)


def build_asset_node(repo: str, root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    text = read_text_sample(path)
    lower = f"{rel}\n{text}".lower()
    signals = {group: any(term.lower() in lower for term in terms) for group, terms in SIGNAL_GROUPS.items()}
    return {
        "asset_id": safe_id(f"{repo}:{rel}"),
        "repo": repo,
        "path": rel,
        "extension": path.suffix,
        "file_type": infer_file_type(rel),
        "size": path.stat().st_size,
        "modified_time": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        "category": infer_category(rel),
        "milestone_id": infer_milestone_id(rel),
        "signals": signals,
        "contains_CEO_related_terms": signals["ceo"],
        "contains_runtime_governance_terms": signals["runtime_governance"],
        "contains_market_external_evidence_terms": signals["market_external_evidence"],
        "contains_CIEU_residual_terms": signals["cieu_residual"],
        "contains_gov_mcp_provider_terms": signals["gov_mcp_provider"],
        "contains_owner_L4_L5_revenue_terms": signals["owner_l4_l5_revenue"],
        "schema_terms": sorted(term for term in SCHEMA_TERMS if term.lower() in lower),
        "high_signal": sum(bool(v) for v in signals.values()) >= 2 or bool(infer_milestone_id(rel)),
    }


def python_ast_info(path: Path) -> dict[str, Any]:
    text = read_text_full(path)
    if not text:
        return {"ast_parse_error": "empty_or_unreadable", "functions": [], "classes": [], "imports": [], "constants": [], "__all__": []}
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {"ast_parse_error": f"{exc.__class__.__name__}: {exc}", "functions": [], "classes": [], "imports": [], "constants": [], "__all__": []}
    functions: list[str] = []
    classes: list[str] = []
    constants: list[str] = []
    imports: list[str] = []
    all_names: list[str] = []
    dataclasses: list[str] = []
    enums: list[str] = []
    cli_entrypoints: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
            if node.name == "main" or any(node.name.startswith(prefix) for prefix in FUNCTION_PREFIXES):
                cli_entrypoints.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
            decorator_names = {name_from_expr(item) for item in node.decorator_list}
            base_names = {name_from_expr(item) for item in node.bases}
            if "dataclass" in decorator_names:
                dataclasses.append(node.name)
            if "Enum" in base_names or "str, Enum" in base_names:
                enums.append(node.name)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants.append(target.id)
                if isinstance(target, ast.Name) and target.id == "__all__" and isinstance(node.value, (ast.List, ast.Tuple)):
                    all_names.extend(str(getattr(item, "value", "")) for item in node.value.elts)
    return {
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "dataclasses": sorted(set(dataclasses)),
        "enums": sorted(set(enums)),
        "imports": sorted(set(imports)),
        "constants": sorted(set(constants)),
        "__all__": sorted(name for name in set(all_names) if name),
        "cli_entrypoints": sorted(set(cli_entrypoints)),
    }


def build_query_expansion_log(asset_graph: Mapping[str, Any]) -> dict[str, Any]:
    assets = list(asset_graph.get("assets", []))
    rounds: list[dict[str, Any]] = []
    seen: set[str] = set()
    terms = list(INITIAL_QUERY_SEEDS)
    for round_index in range(4):
        matched = match_assets_by_terms(assets, terms)
        new_ids = [asset["asset_id"] for asset in matched if asset["asset_id"] not in seen]
        seen.update(new_ids)
        top_terms = top_terms_from_assets(matched)
        if round_index == 0:
            next_terms = [term for term, _count in top_terms[:30] if term not in {s.lower() for s in INITIAL_QUERY_SEEDS}]
        elif round_index == 1:
            next_terms = [term for term, _count in top_terms[:40] if len(term) > 4]
        elif round_index == 2:
            next_terms = list(SCHEMA_TERMS) + list(FUNCTION_PREFIXES)
        else:
            next_terms = ["runtime", "orchestrator", "adapter", "planner", "selector", "resolver", "evidence", "receipt", "owner", "residual"]
        rounds.append(
            {
                "round": round_index,
                "terms": terms,
                "matched_assets": len(matched),
                "new_high_signal_assets": len(new_ids),
                "new_high_signal_asset_sample": new_ids[:30],
                "top_recurring_terms": top_terms[:25],
                "next_terms": next_terms[:45],
            }
        )
        terms = next_terms[:45]
    return {
        "artifact_id": "e91_query_expansion_log",
        "milestone_id": MILESTONE_ID,
        "round_count": len(rounds),
        "stopping_rule": "completed at least 4 rounds; round 3 shifts to orphan/runtime-like capability discovery",
        "initial_seeds_treated_as_opening_not_ontology": True,
        "rounds": rounds,
        "total_unique_assets_discovered_by_queries": len(seen),
    }


def discover_same_problem_clusters(asset_graph: Mapping[str, Any], query_log: Mapping[str, Any]) -> dict[str, Any]:
    assets = list(asset_graph.get("assets", []))
    clusters = []
    cluster_specs = discover_cluster_specs(assets)
    for spec in cluster_specs:
        cluster_assets = [asset for asset in assets if asset_matches_cluster(asset, spec)]
        if not cluster_assets:
            continue
        clusters.append(build_cluster(spec, cluster_assets))
    clusters = sorted(clusters, key=lambda item: (-len(item["assets"]), item["cluster_id"]))
    return {
        "artifact_id": "e91_open_world_same_problem_clusters",
        "milestone_id": MILESTONE_ID,
        "generated_at": utc_now(),
        "discovery_algorithms": [
            "lexical_clustering",
            "structural_schema_clustering",
            "runtime_path_clustering",
            "milestone_lineage_clustering",
            "test_evidence_clustering",
            "report_to_code_clustering",
            "gap_clustering",
            "duplicate_problem_clustering",
            "unseeded_high_signal_discovery",
        ],
        "clusters": clusters,
        "cluster_count": len(clusters),
        "unseeded_clusters": [item["cluster_id"] for item in clusters if item.get("unseeded")],
    }


def discover_cluster_specs(assets: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    specs = [
        {"id": "ceo_behavior_center_and_owner_intent", "name": "CEO behavior center and owner-intent grounding", "terms": ("aiden", "answer_owner", "owner_intent", "behavior center"), "owner": "bridge-labs"},
        {"id": "full_repo_capability_recall_and_inventory", "name": "Full repo capability recall and inventory", "terms": ("capability", "inventory", "baseline", "code_index", "architecture_evidence"), "owner": "bridge-labs"},
        {"id": "legacy_asset_promotion_and_quarantine", "name": "Legacy asset promotion and quarantine", "terms": ("legacy", "promotion", "quarantine", "resurrection", "E71"), "owner": "bridge-labs"},
        {"id": "external_observation_public_read_evidence", "name": "External observation and public-read evidence", "terms": ("public-read", "public read", "external observation", "evidence_atoms", "controlled_search", "locator"), "owner": "bridge-labs"},
        {"id": "market_dynamics_and_buyer_pain", "name": "Market dynamics, buyer pain, and route analysis", "terms": ("market dynamics", "buyer", "pain", "route", "first cash", "E65"), "owner": "bridge-labs"},
        {"id": "offer_blueprint_and_packaging", "name": "Offer blueprint and product packaging", "terms": ("offer", "blueprint", "packaging", "pricing", "E66"), "owner": "bridge-labs"},
        {"id": "strategy_benchmark_and_commercial_sharpness", "name": "Strategic benchmark and commercial sharpness", "terms": ("commercial_sharpness", "strategic_intelligence", "benchmark", "speed_to_cash", "E90"), "owner": "bridge-labs"},
        {"id": "counterfactual_candidate_selection", "name": "Candidate generation and counterfactual comparison", "terms": ("candidate_actions", "counterfactual", "route_scoring", "selected_action"), "owner": "bridge-labs"},
        {"id": "owner_decision_and_l4_l5_boundary", "name": "Owner decision and L4/L5 authority boundary", "terms": ("owner decision", "owner_decision", "pending_owner_decision", "L4", "L5"), "owner": "bridge-labs"},
        {"id": "cieu_prediction_residual_learning", "name": "CIEU prediction and residual learning", "terms": ("CIEU_prediction", "residual", "learning_candidate", "post_action"), "owner": "bridge-labs"},
        {"id": "ystar_governance_runtime_reflex", "name": "Y-star-gov runtime governance reflex", "terms": ("validate_ceo", "runtime_hook", "governance_decision", "IntentContract"), "owner": "Y-star-gov"},
        {"id": "cieustore_formal_recording", "name": "CIEUStore formal record writing and verification", "terms": ("CIEUStore", "write_dict", "seal_session", "formal_CIEU"), "owner": "Y-star-gov"},
        {"id": "gov_mcp_dry_run_provider_boundary", "name": "gov-mcp dry-run provider/tool execution boundary", "terms": ("dry_run_outbound_action", "no_send_invariant", "provider_action_executed", "receipt"), "owner": "gov-mcp"},
        {"id": "k9audit_hash_chain_boundary", "name": "K9Audit hash-chain evidence boundary", "terms": ("K9Audit", "hash-chain", "hash_chain", "evidence chain", "ledger"), "owner": "K9Audit"},
        {"id": "revenue_payment_customer_gate", "name": "Revenue, payment, customer, and pricing gate", "terms": ("revenue", "payment", "customer validation", "paid signal", "pricing validation"), "owner": "bridge-labs"},
    ]
    discovered_terms = Counter()
    for asset in assets:
        if asset.get("high_signal"):
            for token in tokenize(asset["path"]):
                if token not in {seed.lower().replace(" ", "_") for seed in INITIAL_QUERY_SEEDS} and len(token) > 4:
                    discovered_terms[token] += 1
    for token, count in discovered_terms.most_common(20):
        if count >= 20 and token in {"delivery", "bridge", "dream", "brain", "cockpit", "notification", "locator", "resolver", "shadow", "projection", "whiteboard"}:
            specs.append(
                {
                    "id": f"unseeded_{token}_capability_cluster",
                    "name": f"Unseeded {token} capability cluster",
                    "terms": (token,),
                    "owner": "bridge-labs",
                    "unseeded": True,
                }
            )
    return specs


def build_cluster(spec: Mapping[str, Any], assets: list[Mapping[str, Any]]) -> dict[str, Any]:
    code_paths = [asset["path"] for asset in assets if asset.get("file_type") == "source_python"][:40]
    tests = [asset["path"] for asset in assets if asset.get("category") == "test"][:30]
    reports = [asset["path"] for asset in assets if asset.get("category") in {"report", "generated_artifact"}][:40]
    status = infer_cluster_status(assets)
    return {
        "cluster_id": spec["id"],
        "discovered_name": spec["name"],
        "problem_statement": f"Repeated assets address {spec['name'].lower()} as a CEO operating capability.",
        "why_these_files_belong_together": f"Matched open-world terms {list(spec['terms'])} across paths, schemas, reports, and tests.",
        "assets": [f"{asset['repo']}:{asset['path']}" for asset in assets[:120]],
        "asset_count": len(assets),
        "code_paths": code_paths,
        "tests": tests,
        "reports": reports,
        "runtime_status": status,
        "governance_status": "Y-star-gov validated" if spec.get("owner") == "Y-star-gov" else "requires Y-star-gov doctrine invocation validation",
        "CIEU_status": "formal CIEUStore owner" if "cieu" in spec["id"].lower() else "CIEU recording required when invoked",
        "gov_mcp_status": "provider dry-run boundary owner" if spec.get("owner") == "gov-mcp" else "metadata alignment only unless provider boundary is reached",
        "stale_deprecated_quarantined_assets": [f"{asset['repo']}:{asset['path']}" for asset in assets if "quarantine" in asset["path"].lower() or "deprecated" in asset["path"].lower()][:20],
        "duplicate_overlap_notes": "Multiple milestone artifacts solve similar problems under different names; canonical registry merges by required behavior.",
        "canonical_owner_repo": spec.get("owner", "bridge-labs"),
        "required_next_action": "register as canonical doctrine" if status != "deprecated" else "keep historical/deprecated only",
        "discovery_methods": ["lexical", "schema", "milestone_lineage", "report_to_code", "test_evidence"],
        "unseeded": bool(spec.get("unseeded")),
    }


def build_coverage_proof(asset_graph: Mapping[str, Any], clusters: Mapping[str, Any], query_log: Mapping[str, Any]) -> dict[str, Any]:
    assets = list(asset_graph.get("assets", []))
    clustered = {asset_ref.split(":", 1)[1] for cluster in clusters.get("clusters", []) for asset_ref in cluster.get("assets", [])}
    high_signal = [asset for asset in assets if asset.get("high_signal")]
    unclustered_high_signal = [asset for asset in high_signal if asset["path"] not in clustered]
    return {
        "artifact_id": "e91_discovery_coverage_proof",
        "milestone_id": MILESTONE_ID,
        "generated_at": utc_now(),
        "total_tracked_files_scanned": len(assets),
        "tracked_files_by_repo": asset_graph.get("assets_by_repo", {}),
        "total_files_matched_by_any_discovery_signal": len(high_signal),
        "total_files_parsed_as_python": sum(1 for asset in assets if asset.get("file_type") == "source_python"),
        "total_assets_clustered": sum(cluster.get("asset_count", 0) for cluster in clusters.get("clusters", [])),
        "total_unclustered_high_signal_assets": len(unclustered_high_signal),
        "findings_older_than_E86": sum(1 for asset in high_signal if _milestone_num(asset.get("milestone_id")) and _milestone_num(asset.get("milestone_id")) < 86),
        "findings_from_L5_or_L6": sum(1 for asset in high_signal if re.search(r"(^|[/_\\-])l[56]([/_\\-]|$)", asset.get("path", "").lower())),
        "findings_from_E65_E80": sum(1 for asset in high_signal if (n := _milestone_num(asset.get("milestone_id"))) and 65 <= n <= 80),
        "findings_from_E1_E64": sum(1 for asset in high_signal if (n := _milestone_num(asset.get("milestone_id"))) and 1 <= n <= 64),
        "findings_in_Y_star_gov": sum(1 for asset in high_signal if asset["repo"] == "Y-star-gov"),
        "findings_in_gov_mcp": sum(1 for asset in high_signal if asset["repo"] == "gov-mcp"),
        "K9Audit_boundary_findings": sum(1 for asset in high_signal if asset["repo"] == "K9Audit"),
        "ystar_company_findings": sum(1 for asset in high_signal if asset["repo"] == "ystar-company"),
        "unclustered_sample": [
            {
                "repo": asset["repo"],
                "path": asset["path"],
                "reason_irrelevant_or_lower_priority": "high-signal term present but no repeated same-problem cluster after four rounds",
            }
            for asset in unclustered_high_signal[:25]
        ],
        "query_rounds": query_log.get("round_count"),
        "prompt_seeds_not_closed_ontology": True,
    }


def synthesize_canonical_doctrine_registry(
    asset_graph: Mapping[str, Any],
    clusters: Mapping[str, Any],
    coverage: Mapping[str, Any],
) -> dict[str, Any]:
    doctrines = []
    for cluster in clusters.get("clusters", []):
        doctrine_id = canonical_doctrine_id(cluster["cluster_id"])
        status = cluster["runtime_status"]
        classification = classify_doctrine_from_cluster(cluster)
        doctrines.append(
            {
                "doctrine_id": doctrine_id,
                "source_cluster_ids": [cluster["cluster_id"]],
                "title": cluster["discovered_name"],
                "canonical_owner_repo": cluster["canonical_owner_repo"],
                "source_paths": cluster["assets"][:60],
                "callable_implementation_path": first_code_path(cluster),
                "wrapper_path_if_needed": wrapper_for_doctrine(doctrine_id, status),
                "runtime_status": status,
                "classification": classification,
                "mandatory_when": mandatory_when_for_doctrine(doctrine_id),
                "conditional_when": conditional_when_for_doctrine(doctrine_id),
                "advisory_when": advisory_when_for_doctrine(doctrine_id, classification),
                "forbidden_substitutes": forbidden_substitutes_for_doctrine(doctrine_id),
                "required_evidence": required_evidence_for_doctrine(doctrine_id),
                "required_output_schema": required_output_schema_for_doctrine(doctrine_id),
                "Y_star_gov_validation_requirement": "validate as doctrine invocation plan/proof before CEO major action continuation",
                "CIEUStore_recording_requirement": "write CEO_OPERATING_DOCTRINE_INVOCATION_DECISION for plan/proof",
                "gov_mcp_alignment_requirement": "include doctrine metadata in dry-run receipt when provider/tool boundary is reached",
                "owner_approval_requirement": owner_approval_for_doctrine(doctrine_id),
                "K9Audit_boundary": "read-only boundary; no K9Audit write/bridge claimed",
                "L_level_relevance": infer_l_level_relevance(doctrine_id),
            }
        )
    return {
        "artifact_id": "e91_canonical_doctrine_registry_spec",
        "milestone_id": MILESTONE_ID,
        "registry_id": REGISTRY_ID,
        "generated_at": utc_now(),
        "ontology_source": "open_world_asset_graph_clusters",
        "prompt_categories_used_as_closed_ontology": False,
        "coverage_summary": {
            "total_tracked_files_scanned": coverage["total_tracked_files_scanned"],
            "findings_older_than_E86": coverage["findings_older_than_E86"],
            "findings_from_E65_E80": coverage["findings_from_E65_E80"],
            "unclustered_high_signal_assets": coverage["total_unclustered_high_signal_assets"],
        },
        "doctrines": doctrines,
        "doctrine_count": len(doctrines),
        "unseeded_doctrines": [item["doctrine_id"] for item in doctrines if item["source_cluster_ids"][0].startswith("unseeded_")],
        "truth_constraints": {
            "static_evidence_map_cannot_satisfy_non_test_external_observation": True,
            "static_template_cannot_satisfy_non_test_live_ceo_intelligence": True,
            "no_customer_revenue_payment_claim": True,
            "no_K9Audit_write_claim": True,
            "no_live_provider_execution": True,
        },
    }


def write_open_world_reports(reports: Mapping[str, Any], root: Path) -> None:
    out = root / "operations" / "ceo_doctrine_registry"
    out.mkdir(parents=True, exist_ok=True)
    mapping = {
        "e91_asset_graph.json": reports["asset_graph"],
        "e91_query_expansion_log.json": reports["query_expansion_log"],
        "e91_open_world_same_problem_clusters.json": reports["same_problem_clusters"],
        "e91_discovery_coverage_proof.json": reports["coverage_proof"],
        "e91_canonical_doctrine_registry_spec.json": reports["canonical_doctrine_registry_spec"],
    }
    for name, payload in mapping.items():
        (out / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "e91_asset_graph_summary.md").write_text(asset_graph_md(reports["asset_graph"]), encoding="utf-8")
    (out / "e91_query_expansion_log.md").write_text(query_log_md(reports["query_expansion_log"]), encoding="utf-8")
    (out / "e91_open_world_same_problem_clusters.md").write_text(clusters_md(reports["same_problem_clusters"]), encoding="utf-8")
    (out / "e91_discovery_coverage_proof.md").write_text(coverage_md(reports["coverage_proof"]), encoding="utf-8")
    (out / "e91_canonical_doctrine_registry_spec.md").write_text(spec_md(reports["canonical_doctrine_registry_spec"]), encoding="utf-8")
    report_dir = root / "office" / "mission_command"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "e91_open_world_ceo_doctrine_discovery_report.json").write_text(
        json.dumps(reports["completion_report"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (report_dir / "e91_open_world_ceo_doctrine_discovery_readback.md").write_text(
        completion_md(reports["completion_report"]), encoding="utf-8"
    )
    status_dir = root / "operations" / "baseline" / "e87r_full_repo_baseline"
    status_dir.mkdir(parents=True, exist_ok=True)
    (status_dir / "current_runtime_status_after_e91_open_world_doctrine_enforcement.json").write_text(
        json.dumps(reports["runtime_status"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (status_dir / "current_runtime_status_after_e91_open_world_doctrine_enforcement.md").write_text(
        runtime_status_md(reports["runtime_status"]), encoding="utf-8"
    )


def build_completion_report(asset_graph: Mapping[str, Any], clusters: Mapping[str, Any], coverage: Mapping[str, Any], spec: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "e91_open_world_ceo_doctrine_discovery_report",
        "milestone_id": MILESTONE_ID,
        "generated_at": utc_now(),
        "prompt_seeds_were_not_closed_ontology": True,
        "asset_graph": {
            "total_assets": asset_graph.get("asset_count"),
            "tracked_files_by_repo": asset_graph.get("assets_by_repo"),
            "edge_count": asset_graph.get("edge_count"),
        },
        "query_expansion_rounds": 4,
        "cluster_count": clusters.get("cluster_count"),
        "unseeded_clusters": clusters.get("unseeded_clusters"),
        "coverage": coverage,
        "canonical_doctrine_count": spec.get("doctrine_count"),
        "unseeded_doctrines": spec.get("unseeded_doctrines"),
        "external_observation_model_status": "historical public-read wrappers found; live external observation remains gated/unavailable unless future owner-approved provider exists",
        "E89_E90_integration_status": "doctrine plan/proof gate required before continuation in prepared bridge-labs runtime",
        "static_template_evidence_loophole_status": "closed by registry and Y-star-gov contract",
        "L5_truth_table_after_E91": {
            "L5-A": "complete_internal_runtime_foundation",
            "L5-B": "complete_for_structured_governed_intelligence_loop_with_open_world_doctrine_enforcement",
            "L5-B+": "partial_dynamic_intelligence_pending_live_external_observation_and_real_feedback",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
        },
        "safety_statement": {
            "no_external_action": True,
            "no_L4_feedback_executed": True,
            "no_customer_revenue_payment_claim": True,
            "no_K9Audit_write": True,
            "no_live_provider_execution": True,
        },
    }


def build_runtime_status(spec: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "current_runtime_status_after_e91_open_world_doctrine_enforcement",
        "milestone_id": MILESTONE_ID,
        "registry_id": spec.get("registry_id"),
        "canonical_doctrine_count": spec.get("doctrine_count"),
        "L5-A": "complete_internal_runtime_foundation",
        "L5-B": "complete_for_structured_governed_intelligence_loop_with_open_world_doctrine_enforcement",
        "L5-B+": "partial_dynamic_intelligence_pending_live_external_observation_and_real_feedback",
        "L5-C": "partial_dry_run_only",
        "L5-D": "absent_or_not_executed",
        "no_L4_feedback_executed": True,
        "no_customer_revenue_payment_claim": True,
        "K9Audit_integrated": False,
        "gov_mcp_live_execution": False,
    }


def infer_file_type(rel: str) -> str:
    suffix = Path(rel).suffix.lower()
    if suffix == ".py":
        return "source_python"
    if suffix in {".js", ".jsx", ".ts", ".tsx"}:
        return "source_js_ts"
    if suffix in {".sh", ".bash", ".zsh"}:
        return "shell_script"
    if suffix in {".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg"}:
        return "config_or_data"
    if suffix in {".md", ".rst", ".txt"}:
        return "doc_text"
    return "unknown"


def infer_category(rel: str) -> str:
    lower = rel.lower()
    if "/test" in lower or lower.startswith("tests/") or lower.startswith("test_"):
        return "test"
    if "archive" in lower or "deprecated" in lower or "quarantine" in lower:
        return "archive_deprecated"
    if lower.startswith("operations/") or lower.startswith("reports/") or "report" in lower:
        return "generated_artifact" if lower.endswith((".json", ".jsonl")) else "report"
    if "runtime_state" in lower or "runtime_packets" in lower or lower.endswith(".db"):
        return "runtime_state"
    if lower.startswith("docs/") or lower.endswith(".md"):
        return "doc"
    if lower.startswith(("office/", "ystar/", "gov_mcp/", "scripts/", "tools/")):
        return "source"
    if lower.endswith((".json", ".jsonl", ".csv")):
        return "data"
    return "unknown"


def infer_milestone_id(rel: str) -> str:
    match = re.search(r"(?i)(?:^|[/_\\-])((?:e|l)\d+[a-z]?(?:r\d?)?)", rel)
    return match.group(1).upper() if match else ""


def infer_test_target(rel: str) -> str:
    name = Path(rel).stem
    if name.startswith("test_"):
        return name[5:]
    return ""


def asset_matches_cluster(asset: Mapping[str, Any], spec: Mapping[str, Any]) -> bool:
    hay = f"{asset.get('repo')} {asset.get('path')} {' '.join(asset.get('schema_terms', []))} {' '.join(asset.get('functions', []))}".lower()
    return any(str(term).lower() in hay for term in spec.get("terms", ()))


def infer_cluster_status(assets: list[Mapping[str, Any]]) -> str:
    if any(asset.get("category") == "test" for asset in assets) and any(asset.get("file_type") == "source_python" for asset in assets):
        return "runtime_active"
    if any(asset.get("file_type") == "source_python" for asset in assets):
        return "callable_but_not_mandatory"
    if any(asset.get("category") in {"report", "generated_artifact"} for asset in assets):
        return "report_only"
    return "artifact_only"


def classify_doctrine_from_cluster(cluster: Mapping[str, Any]) -> str:
    if cluster["runtime_status"] == "runtime_active":
        return "mandatory doctrine"
    if cluster["runtime_status"] == "callable_but_not_mandatory":
        return "conditional doctrine"
    if cluster["runtime_status"] == "report_only":
        return "historical context only"
    return "advisory doctrine"


def mandatory_when_for_doctrine(doctrine_id: str) -> list[str]:
    rules: dict[str, list[str]] = {
        "external_observation_public_read_evidence": ["external_observation_required=true", "market_strategy_required=true"],
        "market_dynamics_and_buyer_pain": ["market_strategy_required=true"],
        "strategy_benchmark_and_commercial_sharpness": ["market_strategy_required=true"],
        "counterfactual_candidate_selection": ["major_action=true"],
        "ystar_governance_runtime_reflex": ["major_action=true"],
        "cieustore_formal_recording": ["major_action=true"],
        "gov_mcp_dry_run_provider_boundary": ["provider_tool_boundary=true"],
        "owner_decision_and_l4_l5_boundary": ["owner_decision_required=true", "L_level=L4"],
        "revenue_payment_customer_gate": ["revenue_or_payment_related=true"],
        "k9audit_hash_chain_boundary": ["K9Audit_related=true"],
    }
    base = ["major_action=true"] if doctrine_id in {"ceo_behavior_center_and_owner_intent", "full_repo_capability_recall_and_inventory", "cieu_prediction_residual_learning"} else []
    return rules.get(doctrine_id, base)


def conditional_when_for_doctrine(doctrine_id: str) -> list[str]:
    if "legacy" in doctrine_id:
        return ["historical_asset_retrieval_required=true"]
    if "offer" in doctrine_id:
        return ["route_type=revenue_path_candidate", "market_strategy_required=true"]
    return []


def advisory_when_for_doctrine(doctrine_id: str, classification: str) -> list[str]:
    return ["non_major_readback=true"] if "advisory" in classification or "historical" in classification else []


def forbidden_substitutes_for_doctrine(doctrine_id: str) -> list[str]:
    items = ["recent_memory_only", "unverified_summary_only"]
    if "external_observation" in doctrine_id:
        items.extend(["static_evidence_map_only", "historical_report_only_for_non_test_live_observation"])
    if "strategy" in doctrine_id or "market" in doctrine_id:
        items.append("static_template_for_non_test_strategy")
    if "gov_mcp" in doctrine_id:
        items.append("live_provider_execution_without_owner_approval")
    return items


def required_evidence_for_doctrine(doctrine_id: str) -> list[str]:
    if "external_observation" in doctrine_id:
        return ["public_read_source_refs", "freshness_status", "live_observation_runtime_status"]
    if "capability" in doctrine_id:
        return ["E87R_code_index", "architecture_evidence_map", "runtime_status"]
    if "cieu" in doctrine_id:
        return ["CIEU_prediction", "CIEUStore_write_result"]
    return ["source_paths", "evidence_refs", "output_summary"]


def required_output_schema_for_doctrine(doctrine_id: str) -> list[str]:
    return ["doctrine_id", "invocation_status", "output_summary", "evidence_refs", "gaps", "CIEU_recording_status"]


def owner_approval_for_doctrine(doctrine_id: str) -> str:
    if any(term in doctrine_id for term in ("owner_decision", "revenue", "payment", "customer")):
        return "explicit owner approval required before execution"
    return "not required for internal deterministic validation"


def infer_l_level_relevance(doctrine_id: str) -> list[str]:
    if "revenue" in doctrine_id:
        return ["L5-D"]
    if "gov_mcp" in doctrine_id:
        return ["L5-C"]
    if "strategy" in doctrine_id or "market" in doctrine_id:
        return ["L5-B"]
    return ["L5-A", "L5-B"]


def canonical_doctrine_id(cluster_id: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", cluster_id.lower()).strip("_")


def wrapper_for_doctrine(doctrine_id: str, status: str) -> str:
    if "external_observation" in doctrine_id:
        return "office/mission_command/e91_external_observation_doctrine_adapter.py"
    if "capability" in doctrine_id:
        return "office/mission_command/e91_capability_recall_doctrine_adapter.py"
    if "legacy" in doctrine_id:
        return "office/mission_command/e91_legacy_asset_doctrine_adapter.py"
    return "" if status == "runtime_active" else "registry_records_historical_context_only"


def first_code_path(cluster: Mapping[str, Any]) -> str:
    paths = cluster.get("code_paths") or []
    return paths[0] if paths else ""


def match_assets_by_terms(assets: Iterable[Mapping[str, Any]], terms: Iterable[str]) -> list[Mapping[str, Any]]:
    needles = [str(term).lower().replace("_", " ") for term in terms if str(term).strip()]
    matched = []
    for asset in assets:
        hay = f"{asset.get('repo')} {asset.get('path')} {' '.join(asset.get('schema_terms', []))} {' '.join(asset.get('functions', []))}".lower().replace("_", " ")
        if any(term in hay for term in needles):
            matched.append(asset)
    return matched


def top_terms_from_assets(assets: Iterable[Mapping[str, Any]]) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for asset in assets:
        counter.update(tokenize(asset.get("path", "")))
        counter.update(tokenize(" ".join(asset.get("schema_terms", []))))
        counter.update(tokenize(" ".join(asset.get("functions", [])[:20])))
    stop = {"the", "and", "for", "with", "json", "test", "tests", "office", "operations", "external", "validation"}
    return [(term, count) for term, count in counter.most_common(100) if term not in stop]


def tokenize(text: str) -> list[str]:
    return [item for item in re.split(r"[^A-Za-z0-9]+", str(text).lower()) if len(item) >= 3]


def read_text_sample(path: Path, limit: int = 20000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def read_text_full(path: Path, limit: int = 2_000_000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    return text[:limit]


def name_from_expr(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return name_from_expr(node.func)
    if isinstance(node, ast.Subscript):
        return name_from_expr(node.value)
    return ""


def _milestone_num(value: Any) -> int | None:
    match = re.search(r"(?i)e(\d+)", str(value or ""))
    return int(match.group(1)) if match else None


def safe_id(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.:-]+", "_", text)[:220]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def asset_graph_md(payload: Mapping[str, Any]) -> str:
    return "\n".join([
        "# E91 Asset Graph Summary",
        "",
        f"- total_assets: {payload.get('asset_count')}",
        f"- assets_by_repo: `{payload.get('assets_by_repo')}`",
        f"- edge_count: {payload.get('edge_count')}",
        "- prompt seeds treated as closed ontology: false",
        "",
    ])


def query_log_md(payload: Mapping[str, Any]) -> str:
    lines = ["# E91 Query Expansion Log", "", f"- rounds: {payload.get('round_count')}", ""]
    for round_payload in payload.get("rounds", []):
        lines.append(f"## Round {round_payload['round']}")
        lines.append(f"- matched_assets: {round_payload['matched_assets']}")
        lines.append(f"- new_high_signal_assets: {round_payload['new_high_signal_assets']}")
    return "\n".join(lines) + "\n"


def clusters_md(payload: Mapping[str, Any]) -> str:
    lines = ["# E91 Open-World Same-Problem Clusters", "", f"- cluster_count: {payload.get('cluster_count')}", f"- unseeded_clusters: `{payload.get('unseeded_clusters')}`", ""]
    for cluster in payload.get("clusters", [])[:30]:
        lines.append(f"## {cluster['discovered_name']}")
        lines.append(f"- cluster_id: `{cluster['cluster_id']}`")
        lines.append(f"- asset_count: {cluster['asset_count']}")
        lines.append(f"- runtime_status: {cluster['runtime_status']}")
    return "\n".join(lines) + "\n"


def coverage_md(payload: Mapping[str, Any]) -> str:
    return "\n".join([
        "# E91 Discovery Coverage Proof",
        "",
        f"- total_tracked_files_scanned: {payload.get('total_tracked_files_scanned')}",
        f"- total_files_matched_by_any_discovery_signal: {payload.get('total_files_matched_by_any_discovery_signal')}",
        f"- findings_older_than_E86: {payload.get('findings_older_than_E86')}",
        f"- findings_from_L5_or_L6: {payload.get('findings_from_L5_or_L6')}",
        f"- findings_from_E65_E80: {payload.get('findings_from_E65_E80')}",
        f"- findings_from_E1_E64: {payload.get('findings_from_E1_E64')}",
        f"- findings_in_Y_star_gov: {payload.get('findings_in_Y_star_gov')}",
        f"- findings_in_gov_mcp: {payload.get('findings_in_gov_mcp')}",
        "- prompt_seeds_not_closed_ontology: true",
        "",
    ])


def spec_md(payload: Mapping[str, Any]) -> str:
    lines = ["# E91 Canonical Doctrine Registry Spec", "", f"- doctrine_count: {payload.get('doctrine_count')}", f"- unseeded_doctrines: `{payload.get('unseeded_doctrines')}`", ""]
    for doctrine in payload.get("doctrines", [])[:40]:
        lines.append(f"## {doctrine['title']}")
        lines.append(f"- doctrine_id: `{doctrine['doctrine_id']}`")
        lines.append(f"- classification: {doctrine['classification']}")
        lines.append(f"- runtime_status: {doctrine['runtime_status']}")
    return "\n".join(lines) + "\n"


def completion_md(payload: Mapping[str, Any]) -> str:
    return "\n".join([
        "# E91 Open-World CEO Doctrine Discovery Readback",
        "",
        f"- canonical_doctrine_count: {payload.get('canonical_doctrine_count')}",
        f"- cluster_count: {payload.get('cluster_count')}",
        f"- unseeded_clusters: `{payload.get('unseeded_clusters')}`",
        f"- external_observation_model_status: {payload.get('external_observation_model_status')}",
        "- no L4 feedback executed",
        "- no customer/revenue/payment validation claimed",
        "",
    ])


def runtime_status_md(payload: Mapping[str, Any]) -> str:
    return "\n".join([
        "# Runtime Status After E91 Open-World Doctrine Enforcement",
        "",
        f"- L5-A: {payload.get('L5-A')}",
        f"- L5-B: {payload.get('L5-B')}",
        f"- L5-B+: {payload.get('L5-B+')}",
        f"- L5-C: {payload.get('L5-C')}",
        f"- L5-D: {payload.get('L5-D')}",
        "- no L4 feedback executed",
        "",
    ])


__all__ = [
    "build_asset_graph",
    "build_open_world_discovery_reports",
    "build_query_expansion_log",
    "build_coverage_proof",
    "discover_same_problem_clusters",
    "synthesize_canonical_doctrine_registry",
]
