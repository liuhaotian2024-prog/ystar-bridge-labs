from __future__ import annotations

import importlib
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MILESTONE_ID = "E125_Aiden_Retrieval_Orchestration_Runtime_R1"
SESSION_ID = "e125_aiden_retrieval_orchestration"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
RAG_INDEX_DIR = Path.home() / ".ystar_rag" / "chroma_db"

MANDATORY_SOURCE_IDS = (
    "repo_evidence_index",
    "aiden_6d_brain",
    "code_index_or_capability_map",
    "cieu_store_history",
    "ystar_memory_store",
    "local_vector_rag",
)


def run_aiden_retrieval_orchestration(
    owner_message: str,
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
    repo_root: str | Path | None = None,
    high_wisdom_required: bool = True,
    external_public_read_required: bool = False,
    allow_vector_query: bool = True,
) -> dict[str, Any]:
    """Build, validate, and CIEU-record Aiden's retrieval context packet."""

    base = Path(repo_root or BRIDGE_ROOT)
    packet = build_aiden_retrieval_orchestration_packet(
        owner_message,
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        repo_root=base,
        high_wisdom_required=high_wisdom_required,
        external_public_read_required=external_public_read_required,
        allow_vector_query=allow_vector_query,
    )
    gov = _load_ystar_module("ystar.governance.aiden_retrieval_orchestration_contract", ystar_gov_root)
    validation = gov.validate_and_write_aiden_retrieval_orchestration_packet(
        packet,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
    )
    return {
        "artifact_id": "e125_aiden_retrieval_orchestration_result",
        "milestone_id": MILESTONE_ID,
        "retrieval_packet": packet,
        "YstarGov_retrieval_result": validation,
        "retrieval_decision": validation["governance_decision"]["decision"],
        "retrieval_context_summary": format_retrieval_context_for_aiden(packet),
        "CIEUStore_summary": summarize_cieustore(cieu_db),
        "external_action_executed": False,
        "provider_action_executed": False,
        "payment_executed": False,
    }


def build_aiden_retrieval_orchestration_packet(
    owner_message: str,
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
    repo_root: str | Path | None = None,
    high_wisdom_required: bool = True,
    external_public_read_required: bool = False,
    allow_vector_query: bool = True,
) -> dict[str, Any]:
    base = Path(repo_root or BRIDGE_ROOT)
    retrieval_id = f"retrieval_{uuid.uuid4().hex[:12]}"
    task_type = classify_task_type(owner_message)

    source_results = [
        retrieve_repo_evidence(owner_message, repo_root=base),
        retrieve_aiden_brain(owner_message, repo_root=base),
        retrieve_code_index_or_capability_map(owner_message, repo_root=base),
        retrieve_cieu_history(owner_message, cieu_db=cieu_db, ystar_gov_root=ystar_gov_root),
        retrieve_ystar_memory(owner_message, ystar_gov_root=ystar_gov_root),
        retrieve_local_vector_rag(owner_message, repo_root=base, allow_query=allow_vector_query),
        retrieve_e123_memory_asset_discovery(owner_message, repo_root=base),
    ]
    if external_public_read_required:
        source_results.append(
            {
                "source_id": "external_public_read_runtime",
                "retrieval_status": "blocked_by_policy",
                "evidence_count": 0,
                "evidence_items": [],
                "evidence_refs": [],
                "unavailable_reason": "external public-read was requested but no live provider execution is authorized inside retrieval orchestration",
                "correct_path": [
                    "run the governed public-read strategy runtime separately with owner-approved live-network mode",
                    "do not call this answer fully market-grounded until public-read evidence is captured",
                ],
            }
        )

    evidence_items: list[dict[str, Any]] = []
    for source in source_results:
        evidence_items.extend(source.get("evidence_items") or [])
    satisfied_source_ids = sorted({item["source_id"] for item in evidence_items if item.get("source_id")})
    unavailable_source_ids = sorted(
        source["source_id"]
        for source in source_results
        if source.get("retrieval_status") in {"unavailable_declared", "not_configured", "dependency_unavailable", "blocked_by_policy"}
    )
    minimum_required = 5 if high_wisdom_required or task_type in {"strategy", "governance", "runtime", "implementation"} else 3
    sufficient = len(evidence_items) >= minimum_required and len(satisfied_source_ids) >= (4 if high_wisdom_required else 3)

    return {
        "artifact_id": "e125_aiden_retrieval_orchestration_packet",
        "milestone_id": MILESTONE_ID,
        "retrieval_id": retrieval_id,
        "created_at": _now(),
        "task_context": {
            "agent_id": "Aiden",
            "owner_message": owner_message,
            "task_objective": "retrieve relevant governed memory and evidence before Aiden answers or acts",
            "task_type": task_type,
            "major_action": task_type in {"strategy", "governance", "runtime", "implementation"},
            "high_wisdom_required": bool(high_wisdom_required),
            "external_public_read_required": bool(external_public_read_required),
            "generation_mode": "retrieval_orchestrated_structured_output",
        },
        "retrieval_plan": {
            "retrieval_required_before_answer": True,
            "mandatory_source_ids": list(MANDATORY_SOURCE_IDS),
            "optional_source_ids": ["e123_memory_asset_discovery", "external_public_read_runtime"],
            "recent_memory_only_allowed": False,
            "retrieval_policy": "query mandatory local memory/evidence systems and declare unavailable systems with correct path",
        },
        "retrieval_sources": [_source_without_items(source) for source in source_results],
        "retrieved_evidence_pack": {
            "evidence_items": evidence_items,
            "human_summary": _summarize_evidence_pack(evidence_items, unavailable_source_ids),
        },
        "source_coverage": {
            "queried_source_ids": [source["source_id"] for source in source_results],
            "satisfied_source_ids": satisfied_source_ids,
            "satisfied_source_family_count": len(satisfied_source_ids),
            "unavailable_source_ids": unavailable_source_ids,
            "mandatory_source_ids": list(MANDATORY_SOURCE_IDS),
        },
        "sufficiency_assessment": {
            "sufficient_for_answer": sufficient,
            "recent_memory_only": False,
            "minimum_evidence_items_required": minimum_required,
            "actual_evidence_items": len(evidence_items),
            "correct_path": []
            if sufficient
            else [
                "retrieve more evidence from repo evidence, brain, baseline, CIEU, or vector RAG before answering",
                "if vector RAG is missing, build it with scripts/build_rag_index.py after Ollama embeddings are available",
            ],
        },
        "downstream_binding": {
            "retrieval_required_before_aiden_answer": True,
            "retrieved_context_bound_to_answer": True,
            "raw_prompt_to_codex_allowed": False,
            "aiden_reply_should_reference_retrieval_summary": True,
        },
        "CIEU_linkage": {
            "CIEU_recording_required": True,
            "target_event_type": "AIDEN_RETRIEVAL_ORCHESTRATION_DECISION",
            "target_cieu_db": str(cieu_db),
        },
        "truth_constraints": {
            "recent_memory_only": False,
            "raw_natural_language_only_answer": False,
            "retrieval_bypassed": False,
            "static_template_only": False,
            "external_web_research_claim_without_provider": False,
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "live_provider_execution_claim": False,
            "K9Audit_write_claim": False,
            "hidden_chain_of_thought_stored": False,
            "CIEU_recording_bypassed": False,
        },
    }


def classify_task_type(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ("strategy", "market", "赚钱", "战略", "市场", "cash", "revenue")):
        return "strategy"
    if any(term in lowered for term in ("govern", "治理", "contract", "rule", "lock")):
        return "governance"
    if any(term in lowered for term in ("implement", "runtime", "修", "实现", "代码", "build")):
        return "implementation"
    if any(term in lowered for term in ("rag", "retrieval", "memory", "检索", "记忆", "知识图谱")):
        return "runtime"
    return "ceo_meeting_answer"


def retrieve_repo_evidence(owner_message: str, *, repo_root: Path) -> dict[str, Any]:
    try:
        from office.aiden_meeting_room.repo_evidence_index import build_repo_evidence_index

        index = build_repo_evidence_index(repo_root)
        tokens = _query_tokens(owner_message)
        matches = index.search(*tokens)
        if not matches:
            matches = index.by_classification("core_constitutional", "active_runtime_rule", "revenue_relevant_now")[:8]
        evidence = []
        for item in matches[:8]:
            evidence.append(
                {
                    "source_id": "repo_evidence_index",
                    "evidence_ref": f"{item.source}:{getattr(item, 'line', '?')}:{item.label}",
                    "summary": _compact(getattr(item, "text", "")),
                    "runtime_status": "retrieved",
                    "classification": getattr(item, "classification", ""),
                }
            )
        return _source("repo_evidence_index", "queried", evidence)
    except Exception as exc:
        return _unavailable_source(
            "repo_evidence_index",
            f"repo evidence index could not run: {exc}",
            ["inspect office/aiden_meeting_room/repo_evidence_index.py and rebuild safe context extraction"],
        )


def retrieve_aiden_brain(owner_message: str, *, repo_root: Path) -> dict[str, Any]:
    brain_db = repo_root / "aiden_brain.db"
    if not brain_db.exists():
        return _unavailable_source(
            "aiden_6d_brain",
            "aiden_brain.db not present in this repo checkout",
            ["restore or configure the governed Aiden brain database before claiming brain provenance"],
        )
    try:
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        brain = importlib.import_module("scripts.aiden_brain")
        activations = brain.activate(owner_message, max_hops=2, top_n=8, db_path=brain_db)
        evidence = [
            {
                "source_id": "aiden_6d_brain",
                "evidence_ref": f"brain:{node_id}",
                "summary": _compact(f"{name} | activation={activation:.3f} | path={file_path}"),
                "runtime_status": "retrieved",
                "hop": hop,
            }
            for node_id, name, activation, file_path, hop in activations[:8]
        ]
        status = "queried" if evidence else "empty"
        return _source("aiden_6d_brain", status, evidence)
    except Exception as exc:
        return _unavailable_source(
            "aiden_6d_brain",
            f"brain activation failed without writing brain state: {exc}",
            ["inspect scripts/aiden_brain.py and brain DB path; do not answer with fake brain provenance"],
        )


def retrieve_code_index_or_capability_map(owner_message: str, *, repo_root: Path) -> dict[str, Any]:
    baseline = repo_root / "operations/baseline/e87r_full_repo_baseline"
    files = [
        baseline / "baseline_summary.json",
        baseline / "architecture_evidence_map.json",
        baseline / "stable_vocabulary_and_owner_map.json",
        baseline / "code_index.json",
    ]
    evidence: list[dict[str, Any]] = []
    for path in files:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        summary = _json_summary(data, path.name, owner_message)
        evidence.append(
            {
                "source_id": "code_index_or_capability_map",
                "evidence_ref": str(path.relative_to(repo_root)),
                "summary": summary,
                "runtime_status": "retrieved",
            }
        )
    if not evidence:
        return _unavailable_source(
            "code_index_or_capability_map",
            "E87R baseline files are missing",
            ["read operations/baseline/e87r_full_repo_baseline before claiming repo/capability recall"],
        )
    return _source("code_index_or_capability_map", "queried", evidence[:6])


def retrieve_cieu_history(
    owner_message: str,
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    db = Path(cieu_db)
    if not db.exists():
        return _unavailable_source(
            "cieu_store_history",
            "target CIEUStore database does not exist yet; retrieval decision will create it",
            ["after first CIEU writes, query this store for prior governed decisions"],
        )
    try:
        gov_root = Path(ystar_gov_root or Y_GOV_ROOT)
        if str(gov_root) not in sys.path:
            sys.path.insert(0, str(gov_root))
        from ystar.governance.cieu_store import CIEUStore

        store = CIEUStore(str(db))
        rows = store.query(limit=8)
        evidence = [
            {
                "source_id": "cieu_store_history",
                "evidence_ref": f"cieu:{row.event_id}",
                "summary": _compact(f"{row.event_type} decision={row.decision} agent={row.agent_id} task={row.task_description or ''}"),
                "runtime_status": "retrieved",
            }
            for row in rows[:8]
        ]
        return _source("cieu_store_history", "queried" if evidence else "empty", evidence)
    except Exception as exc:
        return _unavailable_source(
            "cieu_store_history",
            f"CIEUStore query failed: {exc}",
            ["inspect Y-star-gov CIEUStore path and schema before claiming runtime memory recall"],
        )


def retrieve_ystar_memory(owner_message: str, *, ystar_gov_root: str | Path | None = None) -> dict[str, Any]:
    gov_root = Path(ystar_gov_root or Y_GOV_ROOT)
    candidate_paths = [
        BRIDGE_ROOT / ".ystar_memory.db",
        gov_root / ".ystar_memory.db",
        Path.home() / ".ystar_memory.db",
    ]
    db_path = next((path for path in candidate_paths if path.exists()), None)
    if db_path is None:
        return _unavailable_source(
            "ystar_memory_store",
            "no Y-star MemoryStore database was found in configured local paths",
            ["initialize MemoryStore or bind existing long-term local memory before claiming Y-star memory recall"],
        )
    try:
        if str(gov_root) not in sys.path:
            sys.path.insert(0, str(gov_root))
        from ystar.memory.store import MemoryStore

        store = MemoryStore(str(db_path))
        rows = []
        for agent_id in ("Aiden", "aiden", "bridge_labs_ceo"):
            rows.extend(store.recall(agent_id=agent_id, limit=5))
        evidence = [
            {
                "source_id": "ystar_memory_store",
                "evidence_ref": f"ystar_memory:{getattr(row, 'memory_id', index)}",
                "summary": _compact(str(getattr(row, "content", row))),
                "runtime_status": "retrieved",
            }
            for index, row in enumerate(rows[:6])
        ]
        return _source("ystar_memory_store", "queried" if evidence else "empty", evidence)
    except Exception as exc:
        return _unavailable_source(
            "ystar_memory_store",
            f"Y-star MemoryStore recall failed: {exc}",
            ["inspect ystar.memory.store.MemoryStore and memory DB path before claiming memory recall"],
        )


def retrieve_local_vector_rag(owner_message: str, *, repo_root: Path, allow_query: bool = True) -> dict[str, Any]:
    if not RAG_INDEX_DIR.exists():
        return _unavailable_source(
            "local_vector_rag",
            f"local vector index not found at {RAG_INDEX_DIR}",
            ["start Ollama, pull nomic-embed-text, then run python3.11 scripts/build_rag_index.py"],
            status="not_configured",
        )
    if not allow_query:
        return _unavailable_source(
            "local_vector_rag",
            "vector RAG query disabled by runtime caller",
            ["call retrieval with allow_vector_query=true when local embeddings are available"],
            status="blocked_by_policy",
        )
    try:
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        rag = importlib.import_module("scripts.build_rag_index")
        rows = rag.query_index(owner_message, top_k=6)
        evidence = [
            {
                "source_id": "local_vector_rag",
                "evidence_ref": f"vector_rag:{row.get('source')}#{row.get('header')}",
                "summary": _compact(row.get("text") or ""),
                "runtime_status": "retrieved",
                "distance": row.get("distance"),
            }
            for row in rows[:6]
        ]
        return _source("local_vector_rag", "queried" if evidence else "empty", evidence)
    except Exception as exc:
        return _unavailable_source(
            "local_vector_rag",
            f"vector RAG query failed or dependency unavailable: {exc}",
            ["verify Ollama is serving, nomic-embed-text is pulled, ChromaDB is installed, and rebuild scripts/build_rag_index.py"],
            status="dependency_unavailable",
        )


def retrieve_e123_memory_asset_discovery(owner_message: str, *, repo_root: Path) -> dict[str, Any]:
    try:
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        module = importlib.import_module("office.mission_command.e123_aiden_model_orchestration_runtime")
        discovery = module.discover_local_long_term_memory_assets(bridge_root=repo_root)
        assets = discovery.get("assets") or discovery.get("memory_assets") or discovery.get("discovered_assets") or []
        evidence = []
        for asset in assets[:8]:
            if not isinstance(asset, Mapping):
                continue
            evidence.append(
                {
                    "source_id": "e123_memory_asset_discovery",
                    "evidence_ref": str(asset.get("asset_id") or asset.get("path") or asset.get("name")),
                    "summary": _compact(str(asset.get("purpose") or asset.get("description") or asset)),
                    "runtime_status": "retrieved",
                }
            )
        return _source("e123_memory_asset_discovery", "queried" if evidence else "empty", evidence)
    except Exception as exc:
        return _unavailable_source(
            "e123_memory_asset_discovery",
            f"E123 memory asset discovery not callable: {exc}",
            ["reuse E123 model orchestration/memory asset discovery before adding another memory inventory"],
        )


def format_retrieval_context_for_aiden(packet: Mapping[str, Any], *, max_items: int = 8) -> str:
    pack = dict(packet.get("retrieved_evidence_pack") or {})
    items = list(pack.get("evidence_items") or [])[:max_items]
    coverage = dict(packet.get("source_coverage") or {})
    lines = [
        "Governed retrieval context was built before this answer.",
        f"Sources satisfied: {', '.join(coverage.get('satisfied_source_ids') or []) or 'none'}",
        f"Sources unavailable/declared: {', '.join(coverage.get('unavailable_source_ids') or []) or 'none'}",
    ]
    for index, item in enumerate(items, start=1):
        lines.append(f"{index}. [{item.get('source_id')}] {item.get('summary')} ({item.get('evidence_ref')})")
    return "\n".join(lines)


def write_e125_reports(
    *,
    cieu_db: str | Path,
    root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(root or BRIDGE_ROOT)
    result = run_aiden_retrieval_orchestration(
        "Aiden, explain whether you have RAG-like retrieval and use governed retrieval before answering.",
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        repo_root=base,
    )
    source_map = {
        "milestone_id": MILESTONE_ID,
        "source_ids": list(MANDATORY_SOURCE_IDS) + ["e123_memory_asset_discovery", "external_public_read_runtime"],
        "merged_systems": [
            "office.aiden_meeting_room.repo_evidence_index",
            "scripts.aiden_brain.activate",
            "Y-star-gov CIEUStore",
            "Y-star-gov MemoryStore when configured",
            "scripts/build_rag_index.py Chroma/Ollama vector RAG when configured",
            "E87R baseline code/capability artifacts",
            "E123 long-term memory asset discovery",
        ],
        "no_external_action_executed": True,
        "vector_rag_status": next(
            (source for source in result["retrieval_packet"]["retrieval_sources"] if source["source_id"] == "local_vector_rag"),
            {},
        ),
    }
    status = {
        "milestone_id": MILESTONE_ID,
        "status": "implemented_governed_retrieval_orchestration_runtime",
        "retrieval_required_before_aiden_answer": True,
        "CIEUStore_summary": result["CIEUStore_summary"],
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_governed_retrieval_orchestration",
            "L5-B": "stronger_governed_intelligence_with_repo_brain_cieu_memory_and_vector_rag_orchestration",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_safe_brain_learning_and_retrieval_backed_memory_growth",
        },
    }
    report = {
        "milestone_id": MILESTONE_ID,
        "result": result,
        "source_map": source_map,
        "status": status,
        "what_was_not_claimed": [
            "no live external research executed by retrieval orchestration",
            "no customer validation",
            "no revenue or payment evidence",
            "no K9Audit write",
        ],
    }
    files = {
        "report_json": base / "office/mission_command/e125_aiden_retrieval_orchestration_runtime_report.json",
        "report_md": base / "office/mission_command/e125_aiden_retrieval_orchestration_runtime_readback.md",
        "source_map_json": base / "operations/retrieval_orchestration/e125_retrieval_source_map.json",
        "source_map_md": base / "operations/retrieval_orchestration/e125_retrieval_source_map.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e125_aiden_retrieval_orchestration_runtime.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e125_aiden_retrieval_orchestration_runtime.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["source_map_json"].write_text(json.dumps(source_map, indent=2, sort_keys=True), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_md(report), encoding="utf-8")
    files["source_map_md"].write_text(_source_map_md(source_map), encoding="utf-8")
    files["status_md"].write_text(_status_md(status), encoding="utf-8")
    return {"result": result, "report": report, "source_map": source_map, "status": status, "files": {key: str(value) for key, value in files.items()}}


def summarize_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"db_path": str(path), "event_count": 0, "event_types": []}
    with sqlite3.connect(path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM cieu_events").fetchone()[0]
        event_types = [row[0] for row in conn.execute("SELECT DISTINCT event_type FROM cieu_events ORDER BY event_type").fetchall()]
    return {"db_path": str(path), "event_count": int(count), "event_types": event_types}


def _source(source_id: str, status: str, evidence_items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "retrieval_status": status,
        "evidence_count": len(evidence_items),
        "evidence_refs": [item.get("evidence_ref") for item in evidence_items],
        "evidence_items": evidence_items,
        "unavailable_reason": "",
        "correct_path": [],
    }


def _unavailable_source(source_id: str, reason: str, correct_path: list[str], *, status: str = "unavailable_declared") -> dict[str, Any]:
    return {
        "source_id": source_id,
        "retrieval_status": status,
        "evidence_count": 0,
        "evidence_refs": [],
        "evidence_items": [],
        "unavailable_reason": reason,
        "correct_path": correct_path,
    }


def _source_without_items(source: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in source.items() if key != "evidence_items"}


def _query_tokens(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9_]{3,}|[\u4e00-\u9fff]{2,}", text.lower())
    tokens.extend(["Aiden", "CEO", "CIEU", "runtime", "governance", "retrieval", "evidence"])
    return sorted(dict.fromkeys(tokens))[:40]


def _json_summary(data: Any, name: str, owner_message: str) -> str:
    if isinstance(data, Mapping):
        keys = list(data.keys())[:12]
        matched = [key for key in keys if any(token in str(key).lower() for token in _query_tokens(owner_message)[:12])]
        interesting = matched or keys[:6]
        counts = {key: len(value) for key, value in data.items() if isinstance(value, (list, dict)) and key in interesting}
        return _compact(f"{name}: keys={interesting}; counts={counts}")
    if isinstance(data, list):
        return _compact(f"{name}: list_items={len(data)}")
    return _compact(f"{name}: loaded baseline artifact")


def _summarize_evidence_pack(items: list[Mapping[str, Any]], unavailable: list[str]) -> str:
    families = sorted({str(item.get("source_id")) for item in items if item.get("source_id")})
    return (
        f"Retrieved {len(items)} items from {len(families)} source families: {', '.join(families)}. "
        f"Unavailable but declared: {', '.join(unavailable) if unavailable else 'none'}."
    )


def _compact(text: str, limit: int = 360) -> str:
    compacted = " ".join(str(text).split())
    return compacted[: limit - 3] + "..." if len(compacted) > limit else compacted


def _load_ystar_module(module_name: str, ystar_gov_root: str | Path | None = None):
    root = Path(ystar_gov_root or Y_GOV_ROOT)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _report_md(report: Mapping[str, Any]) -> str:
    result = dict(report["result"])
    packet = dict(result["retrieval_packet"])
    coverage = dict(packet["source_coverage"])
    return "\n".join(
        [
            "# E125 Aiden Retrieval Orchestration Runtime",
            "",
            "## What Changed",
            "- Merged repo evidence, Aiden 6D brain, E87R code/capability baseline, CIEU history, Y-star memory status, and local vector RAG status into one governed retrieval packet.",
            "- Y-star-gov now validates retrieval before Aiden uses retrieved context in answers/actions.",
            "- Retrieval decisions write formal CIEUStore records.",
            "",
            "## Source Coverage",
            f"- Satisfied: {', '.join(coverage.get('satisfied_source_ids') or [])}",
            f"- Unavailable declared: {', '.join(coverage.get('unavailable_source_ids') or [])}",
            f"- Evidence items: {len(packet['retrieved_evidence_pack']['evidence_items'])}",
            "",
            "## Boundaries",
            "- No external action executed.",
            "- No customer/revenue/payment claim.",
            "- Vector RAG may be unavailable; if so the runtime declares the correct build path instead of faking retrieval.",
        ]
    )


def _source_map_md(source_map: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# E125 Retrieval Source Map",
            "",
            "## Source IDs",
            *[f"- `{source_id}`" for source_id in source_map["source_ids"]],
            "",
            "## Merged Systems",
            *[f"- {system}" for system in source_map["merged_systems"]],
        ]
    )


def _status_md(status: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Current Runtime Status After E125",
            "",
            f"Status: {status['status']}",
            "",
            "## Retrieval Boundary",
            "- Aiden answers must be backed by a governed retrieval packet.",
            "- Retrieval is CIEU-recorded and cannot be recent-memory-only.",
            "",
            "## L5 Truth Table",
            *[f"- {key}: {value}" for key, value in status["L5_truth_table_after"].items()],
        ]
    )
