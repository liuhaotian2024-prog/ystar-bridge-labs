from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping


MILESTONE_ID = "E149_Governed_Real_Model_Invocation_Binding_R1"
PROTOCOL = "AidenGovernedRealModelInvocationV1"
SESSION_ID = "e149_governed_real_model_invocation"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
OLLAMA_ENDPOINT = os.environ.get("AIDEN_OLLAMA_ENDPOINT", "http://127.0.0.1:11434").rstrip("/")

ModelInvoker = Callable[[str, str, Mapping[str, Any]], Mapping[str, Any]]


def run_governed_real_model_invocation(
    *,
    owner_text: str,
    cieu_db: str | Path,
    retrieval_context_summary: str = "",
    ystar_gov_root: str | Path | None = None,
    repo_root: str | Path | None = None,
    real_model_invoker: ModelInvoker | None = None,
    owner_approved_external_model_use: bool = False,
) -> dict[str, Any]:
    """Select a model through E123, then require a real model invocation proof.

    This runtime intentionally does not fall back to the deterministic behavior
    center. If the selected model cannot be called, Aiden must say so plainly.
    """

    from office.mission_command.e123_aiden_model_orchestration_runtime import run_aiden_model_orchestration_session

    orchestration = run_aiden_model_orchestration_session(
        owner_intent=owner_text,
        cieu_db=cieu_db,
        task_id=f"e149_owner_reply_{uuid.uuid4().hex[:8]}",
        ystar_gov_root=ystar_gov_root,
        owner_approved_external_model_use=owner_approved_external_model_use,
    )
    decision = orchestration["YstarGov_model_orchestration_result"]["governance_decision"]
    selected = orchestration["model_orchestration_packet"]["selected_model"]
    selected_model_id = str(selected.get("model_id") or "")

    if decision.get("decision") != "ALLOW":
        proof = _build_proof(
            selected_model_id=selected_model_id or "not_selected",
            status="not_executed",
            reason=f"model orchestration returned {decision.get('decision')}: {decision.get('reason')}",
            external_provider_called=False,
            deterministic_template_substitute_used=False,
        )
        _write_invocation_record(cieu_db, owner_text, orchestration, proof, "")
        return _result(
            owner_text=owner_text,
            orchestration=orchestration,
            proof=proof,
            reply_text=_model_unavailable_text(selected_model_id or "not_selected", proof["reason"]),
            backend="governed_real_model_invocation_blocked",
        )

    prompt = build_aiden_owner_reply_prompt(
        owner_text=owner_text,
        retrieval_context_summary=retrieval_context_summary,
        selected_model_id=selected_model_id,
        repo_root=repo_root or BRIDGE_ROOT,
    )

    if selected_model_id in {"local_gemma4_e4b", "local_ystar_gemma"}:
        model_name = _ollama_model_name_for(selected_model_id)
        invoker = real_model_invoker or _call_local_ollama
        raw = dict(invoker(model_name, prompt, {"selected_model_id": selected_model_id}))
        text = str(raw.get("text") or "").strip()
        ok = raw.get("error") in {None, ""} and bool(text)
        proof = _build_proof(
            selected_model_id=selected_model_id,
            status="executed" if ok else "not_executed",
            reason="local model generated owner reply" if ok else str(raw.get("error") or "local model returned empty response"),
            provider=str(raw.get("provider") or model_name),
            model_name=model_name,
            latency_ms=raw.get("latency_ms"),
            output_chars=len(text),
            external_provider_called=False,
            deterministic_template_substitute_used=False,
            raw_result={k: v for k, v in raw.items() if k != "text"},
        )
        _write_invocation_record(cieu_db, owner_text, orchestration, proof, text)
        if ok:
            return _result(
                owner_text=owner_text,
                orchestration=orchestration,
                proof=proof,
                reply_text=text,
                backend="governed_real_local_model_invocation",
            )
        return _result(
            owner_text=owner_text,
            orchestration=orchestration,
            proof=proof,
            reply_text=_model_unavailable_text(selected_model_id, proof["reason"]),
            backend="governed_real_model_unavailable_notice",
        )

    proof = _build_proof(
        selected_model_id=selected_model_id,
        status="not_executed",
        reason=f"selected model {selected_model_id} is not executable in the local owner-facing messenger path",
        external_provider_called=False,
        deterministic_template_substitute_used=False,
    )
    _write_invocation_record(cieu_db, owner_text, orchestration, proof, "")
    return _result(
        owner_text=owner_text,
        orchestration=orchestration,
        proof=proof,
        reply_text=_model_unavailable_text(selected_model_id, proof["reason"]),
        backend="governed_real_model_unavailable_notice",
    )


def build_aiden_owner_reply_prompt(
    *,
    owner_text: str,
    retrieval_context_summary: str,
    selected_model_id: str,
    repo_root: str | Path,
) -> str:
    return (
        "你是 Aiden，Y* Bridge Labs 的 CEO principal agent。你不是模板解释器。\n"
        "你必须用流利、清晰、有判断力的中文回答 owner。\n"
        "不要展示隐藏推理链；只输出结构化结论、判断依据、取舍、下一步行动和边界。\n"
        "如果 owner 要推进上一轮任务，你要直接推进 no-send 内部行动包，而不是只说“建议下一步”。\n"
        "禁止声称已经外发、付款、联系客户、获得收入、完成 K9Audit 或写入 production brain。\n\n"
        f"选定模型: {selected_model_id}\n"
        f"repo_root: {repo_root}\n\n"
        "本地检索/治理上下文摘要：\n"
        f"{_compact(retrieval_context_summary, 5000)}\n\n"
        "owner 当前输入：\n"
        f"{_compact(owner_text, 12000)}\n\n"
        "请输出 owner-readable 的 CEO 回复。"
    )


def _call_local_ollama(model_name: str, prompt: str, context: Mapping[str, Any]) -> dict[str, Any]:
    _ensure_ollama_started_if_allowed()
    start = time.perf_counter()
    payload = json.dumps(
        {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.4, "num_predict": int(os.environ.get("AIDEN_OLLAMA_NUM_PREDICT", "1600"))},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_ENDPOINT}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=float(os.environ.get("AIDEN_OLLAMA_TIMEOUT_SECONDS", "120"))) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {
            "provider": "Ollama_local",
            "model": model_name,
            "text": data.get("response", ""),
            "eval_count": data.get("eval_count", 0),
            "latency_ms": int((time.perf_counter() - start) * 1000),
            "error": None,
        }
    except Exception as exc:
        return {
            "provider": "Ollama_local",
            "model": model_name,
            "text": "",
            "latency_ms": int((time.perf_counter() - start) * 1000),
            "error": f"{exc.__class__.__name__}: {exc}",
        }


def _ensure_ollama_started_if_allowed() -> None:
    if os.environ.get("AIDEN_AUTO_START_OLLAMA", "1").lower() not in {"1", "true", "yes", "on"}:
        return
    try:
        req = urllib.request.Request(f"{OLLAMA_ENDPOINT}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2):
            return
    except Exception:
        pass
    try:
        log_dir = Path(os.environ.get("AIDEN_OLLAMA_LOG_DIR", "/tmp/ystar_agent_native_messenger/logs"))
        log_dir.mkdir(parents=True, exist_ok=True)
        stdout = (log_dir / "ollama_serve.stdout.log").open("ab")
        stderr = (log_dir / "ollama_serve.stderr.log").open("ab")
        subprocess.Popen(["ollama", "serve"], stdout=stdout, stderr=stderr, start_new_session=True)
        time.sleep(2)
    except Exception:
        return


def _ollama_model_name_for(selected_model_id: str) -> str:
    if selected_model_id == "local_ystar_gemma":
        return os.environ.get("AIDEN_YSTAR_GEMMA_MODEL", "ystar-gemma:latest")
    return os.environ.get("AIDEN_GEMMA4_MODEL", "gemma4")


def _build_proof(
    *,
    selected_model_id: str,
    status: str,
    reason: str,
    provider: str = "",
    model_name: str = "",
    latency_ms: Any = None,
    output_chars: int = 0,
    external_provider_called: bool,
    deterministic_template_substitute_used: bool,
    raw_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "proof_id": f"e149_invocation_{uuid.uuid4().hex[:12]}",
        "selected_model_id": selected_model_id,
        "provider": provider,
        "model_name": model_name,
        "actual_generation_executed": status == "executed",
        "invocation_status": status,
        "reason": reason,
        "latency_ms": latency_ms,
        "output_chars": output_chars,
        "external_provider_called": external_provider_called,
        "deterministic_template_substitute_used": deterministic_template_substitute_used,
        "no_external_business_side_effect": True,
        "customer_contact_executed": False,
        "payment_executed": False,
        "raw_result_metadata": dict(raw_result or {}),
    }


def _write_invocation_record(
    cieu_db: str | Path,
    owner_text: str,
    orchestration: Mapping[str, Any],
    proof: Mapping[str, Any],
    model_text: str,
) -> None:
    root = Path(Y_GOV_ROOT)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from ystar.governance.cieu_store import CIEUStore

    record = {
        "event_id": str(uuid.uuid4()),
        "seq_global": int(time.time() * 1_000_000),
        "created_at": time.time(),
        "session_id": SESSION_ID,
        "agent_id": "Aiden",
        "event_type": "AIDEN_REAL_MODEL_INVOCATION_DECISION",
        "decision": "ALLOW" if proof.get("actual_generation_executed") else "DENY",
        "passed": bool(proof.get("actual_generation_executed")),
        "violations": [] if proof.get("actual_generation_executed") else [str(proof.get("reason"))],
        "drift_detected": not bool(proof.get("actual_generation_executed")),
        "drift_details": None if proof.get("actual_generation_executed") else str(proof.get("reason")),
        "task_description": "Aiden governed real model invocation for owner-facing reply",
        "contract_hash": "e149-governed-real-model-invocation-v1",
        "params": {
            "owner_text_preview": owner_text[:500],
            "selected_model_id": proof.get("selected_model_id"),
            "orchestration_decision": orchestration.get("YstarGov_model_orchestration_result", {})
            .get("governance_decision", {})
            .get("decision"),
        },
        "result": {
            "actual_model_invocation_proof": dict(proof),
            "model_text_preview": model_text[:1000],
        },
        "human_initiator": "owner",
        "lineage_path": ["bridge-labs", "E123-model-orchestration", "E149-real-model-invocation", "CIEUStore"],
        "evidence_grade": "runtime_proof",
        "m_functor": "M-2b",
        "m_weight": 1.0,
        "y_star_validator_pass": True,
    }
    CIEUStore(str(cieu_db)).write_dict(record)


def _result(
    *,
    owner_text: str,
    orchestration: Mapping[str, Any],
    proof: Mapping[str, Any],
    reply_text: str,
    backend: str,
) -> dict[str, Any]:
    return {
        "artifact_id": "e149_governed_real_model_invocation_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "owner_text_preview": owner_text[:300],
        "reply_text": reply_text,
        "reply_backend": backend,
        "reply_protocol": PROTOCOL,
        "runtime_fallback_used": not bool(proof.get("actual_generation_executed")),
        "model_orchestration_result": orchestration,
        "actual_model_invocation_proof": dict(proof),
        "truth_constraints": {
            "deterministic_template_substitute_used": proof.get("deterministic_template_substitute_used") is True,
            "external_provider_called": proof.get("external_provider_called") is True,
            "external_business_action_executed": False,
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "K9Audit_write_claim": False,
        },
    }


def _model_unavailable_text(selected_model_id: str, reason: str) -> str:
    return (
        "我不能把这轮回答伪装成 CEO 的真实思考。\n\n"
        f"治理已经选择了模型 `{selected_model_id}`，但真实模型调用没有成功：{reason}\n\n"
        "因此我不会再用 deterministic 模板继续冒充 Aiden 的判断。正确路径是：启动本地 Ollama/Gemma，"
        "或由 owner 明确批准经过脱敏的外部 GPT/Claude 路径；然后重新运行这条消息。"
    )


def _compact(text: str, limit: int) -> str:
    normalized = str(text or "").strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip() + "\n...（已截断给本地模型；完整原文仍保留在 messenger/CIEU 记录中。）"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


__all__ = [
    "MILESTONE_ID",
    "PROTOCOL",
    "build_aiden_owner_reply_prompt",
    "run_governed_real_model_invocation",
]
