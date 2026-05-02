from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict


class LearningSource(str, Enum):
    REPORT_ONLY_LEARNING = "report_only_learning"
    METHOD_KERNEL_CANDIDATE = "method_kernel_candidate"
    DREAM_DIFF_PROPOSAL = "dream_diff_proposal"
    BRAIN_GRAPH_CANDIDATE = "brain_graph_candidate"
    CIEU_PREDICTION_DELTA = "cieu_prediction_delta"


class LearningDestination(str, Enum):
    REPORT = "report"
    METHOD_KERNEL = "method_kernel"
    BRAIN_GRAPH = "brain_graph"
    CIEU = "cieu"
    CORE_MEMORY = "core_memory"


@dataclass(frozen=True)
class LearningWritebackDecision:
    source: LearningSource
    destination: LearningDestination
    allowed: bool
    requires_cieu_delta: bool
    requires_explicit_gate: bool
    blocked_reason: str
    next_step: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["source"] = self.source.value
        data["destination"] = self.destination.value
        return data


def route_learning_writeback(
    source: LearningSource | str,
    destination: LearningDestination | str,
    *,
    has_cieu_delta: bool = False,
    explicit_gate: bool = False,
    durable_principle: bool = False,
) -> LearningWritebackDecision:
    src = LearningSource(source)
    dst = LearningDestination(destination)
    if dst == LearningDestination.REPORT:
        return LearningWritebackDecision(src, dst, True, False, False, "", "render_report_only_learning")
    if dst == LearningDestination.METHOD_KERNEL:
        allowed = durable_principle and explicit_gate and src in {LearningSource.METHOD_KERNEL_CANDIDATE, LearningSource.CIEU_PREDICTION_DELTA}
        return LearningWritebackDecision(
            src,
            dst,
            allowed,
            False,
            True,
            "" if allowed else "method_kernel_update_requires_durable_principle_and_explicit_gate",
            "owner_or_test_review_method_kernel_candidate",
        )
    if dst in {LearningDestination.BRAIN_GRAPH, LearningDestination.CORE_MEMORY, LearningDestination.CIEU}:
        allowed = has_cieu_delta and explicit_gate and src == LearningSource.CIEU_PREDICTION_DELTA
        return LearningWritebackDecision(
            src,
            dst,
            allowed,
            True,
            True,
            "" if allowed else "persistent_learning_requires_CIEU_prediction_delta_and_explicit_writeback_gate",
            "create_CIEU_prediction_delta_for_review",
        )
    return LearningWritebackDecision(src, dst, False, True, True, "unknown_learning_destination", "owner_review")


def report_direct_brain_writeback_is_blocked() -> bool:
    return not route_learning_writeback(LearningSource.REPORT_ONLY_LEARNING, LearningDestination.BRAIN_GRAPH).allowed

