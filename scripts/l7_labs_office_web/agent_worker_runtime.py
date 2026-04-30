#!/usr/bin/env python3
"""Deterministic local worker replies for the recovered Y*Bridge Labs team."""

from __future__ import annotations

from typing import Any


ROLE_WORK = {
    "aiden_ceo": {
        "role_interpretation": "I interpret the owner goal, keep the team aligned, and route work to the original legacy roles.",
        "work_done": "Created a safe delegation frame and kept all external actions behind approval gates.",
        "findings": ["Use the whiteboard as the coordination surface; route domain work to the recovered team, not invented roles."],
        "next_step": "Run a team work cycle or ask for a completion report after domain replies land.",
    },
    "ethan_cto": {
        "role_interpretation": "I evaluate tooling, architecture, implementation, and test gaps.",
        "work_done": "Identified tool/runtime implications and kept execution local-only.",
        "findings": ["The shortest path improves if the office can convert goals into work items, agent replies, and reports."],
        "next_step": "Build or test the next missing local tool only after the team agrees on priority.",
    },
    "sofia_cmo": {
        "role_interpretation": "I shape narrative, positioning, and owner-readable framing.",
        "work_done": "Drafted internal positioning boundaries without publication.",
        "findings": ["The story should be: governed AI workflow audit first, productization later after paid validation."],
        "next_step": "Prepare review-only messaging once owner approves an outreach path.",
    },
    "marco_cfo": {
        "role_interpretation": "I check pricing, cash-path assumptions, and financial honesty.",
        "work_done": "Reviewed cash realization assumptions as estimates, not settled facts.",
        "findings": ["The $1,500 pilot remains plausible as a test price, but quoting externally needs owner approval."],
        "next_step": "Track willingness-to-pay evidence before treating pricing as validated.",
    },
    "zara_cso": {
        "role_interpretation": "I analyze sales strategy, commercialization, offer validation, and buyer fit.",
        "work_done": "Mapped the request to first-revenue readiness and approval-gated buyer contact.",
        "findings": ["Fastest cash path is still a scoped founder workflow audit with CEO command brief deliverable."],
        "next_step": "Prepare a no-contact target archetype review or approval request for first outreach.",
    },
    "samantha_secretary": {
        "role_interpretation": "I maintain archive, indexes, DNA consistency, and traceability.",
        "work_done": "Recorded the work item in local packets and preserved no-action boundaries.",
        "findings": ["Every reply, route, and completion report should have a local packet reference."],
        "next_step": "Index generated packets and keep runtime state readable from the office page.",
    },
    "leo_engineer": {
        "role_interpretation": "I focus on kernel/runtime correctness and local execution integrity.",
        "work_done": "Checked that the task can stay inside local packet/runtime boundaries.",
        "findings": ["Runtime IDs, state transitions, and local-only writes are the critical correctness layer."],
        "next_step": "Harden local state transitions if the whiteboard becomes long-running.",
    },
    "maya_engineer": {
        "role_interpretation": "I focus on governance, policy boundaries, and approval gates.",
        "work_done": "Confirmed external side effects and permanent writeback remain blocked.",
        "findings": ["Approval requests should be explicit when a goal implies outreach, payment, publication, or writeback."],
        "next_step": "Review approval queue before any future external execution.",
    },
    "ryan_engineer": {
        "role_interpretation": "I focus on platform, server, APIs, UI wiring, and QA.",
        "work_done": "Mapped the whiteboard request to local API and UI controls.",
        "findings": ["The UI should show whiteboard, work board, timeline, agent panel, approvals, and completion reports together."],
        "next_step": "Keep smoke tests local and deterministic.",
    },
    "jordan_engineer": {
        "role_interpretation": "I focus on workflow templates, domains, and reusable operating patterns.",
        "work_done": "Converted the task into reusable work item and completion report structure.",
        "findings": ["The same whiteboard loop can become a reusable Labs operating protocol."],
        "next_step": "Extract templates only after a few real owner workflows prove useful.",
    },
    "jinjin_k9_scout": {
        "role_interpretation": "I scout research angles and read-only observation targets.",
        "work_done": "Proposed safe read-only research directions without contacting anyone.",
        "findings": ["First-cash validation needs public buyer-signal observation and owner-approved contact gates."],
        "next_step": "Prepare a read-only observation plan for buyer pain signals if requested.",
    },
}


def generate_agent_reply(agent_id: str, work_item: dict[str, Any]) -> dict[str, Any]:
    profile = ROLE_WORK.get(
        agent_id,
        {
            "role_interpretation": "I perform scoped internal work aligned to my recovered legacy role.",
            "work_done": "Reviewed the work item locally.",
            "findings": ["No external action taken."],
            "next_step": "Ask Aiden to clarify routing if needed.",
        },
    )
    description = work_item.get("description", "")
    lowered = description.lower()
    draft_only = any(term in lowered for term in ["draft-only", "review-only", "draft", "草稿", "仅供审阅"])
    external_execution = any(
        keyword in lowered
        for keyword in [
            "send email",
            "email send",
            "contact customer",
            "customer contact",
            "publish",
            "payment",
            "submit form",
            "grant submission",
            "rfp submission",
            "actual writeback",
            "发送邮件",
            "联系客户",
            "付款",
            "发布",
        ]
    )
    approval_needed = external_execution and not draft_only
    return {
        "agent_id": agent_id,
        "work_item_id": work_item["work_item_id"],
        "role_interpretation": profile["role_interpretation"],
        "work_done": profile["work_done"],
        "findings": profile["findings"],
        "artifacts_created": [],
        "blockers": ["owner approval required before external action"] if approval_needed else [],
        "next_step": profile["next_step"],
        "approval_needed": approval_needed,
        "status": "waiting_for_approval" if approval_needed else "done",
    }


def auditor_boundary_reply(work_item: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_id": "auditor_function",
        "work_item_id": work_item["work_item_id"],
        "role_interpretation": "Auditor is a governance function, not an invented legacy person.",
        "work_done": "Reviewed no-action and approval boundaries for this local work cycle.",
        "findings": [
            "No external side effects are allowed in this runtime.",
            "Actual memory/brain/canonical/CIEU DB writeback remains blocked.",
            "COO was not invented as a legacy team member.",
        ],
        "artifacts_created": [],
        "blockers": [],
        "next_step": "Escalate to owner only if an approval-gated action is requested.",
        "approval_needed": False,
        "status": "done",
    }
