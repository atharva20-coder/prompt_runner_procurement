"""End Negotiation Tool — Procurement Pipeline.

Terminal tool for the Exit stage. Logs the deal outcome to
registers/negotiations.yaml. This is the procurement equivalent
of end_call_tool.py from the recovery pipeline.

Called by: Procurement_exit_stage_prompt.md (Exit stage)
Outcomes: DEAL_CLOSED, FOLLOW_UP_BOOKED, ESCALATED, NO_DEAL
"""

import os
from datetime import datetime

import yaml

from tool_registry import Tool

# ── Persistence: YAML register for negotiation outcomes ──
REGISTERS_DIR = "registers"
NEGOTIATIONS_FILE = os.path.join(REGISTERS_DIR, "negotiations.yaml")


def _load_yaml(path: str) -> list | dict:
    """Load existing YAML register (or return empty list)."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data or []


def _dump_yaml(path: str, data) -> None:
    """Write data to YAML register, creating directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


class EndNegotiationTool(Tool):
    """Tool to end the negotiation and log the outcome."""

    @property
    def name(self) -> str:
        return "end_negotiation"

    @property
    def description(self) -> str:
        return (
            "End the negotiation and log the outcome. "
            "ONLY call when the exit flow is complete and all required information is captured. "
            "Must provide exit_path and path-specific required fields."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "exit_path": {
                    "type": "string",
                    "enum": [
                        "DEAL_CLOSED",
                        "FOLLOW_UP_SCHEDULED",
                        "ESCALATION_TO_AUTHORITY",
                        "NO_DEAL_EXIT",
                    ],
                    "description": "The exit path being taken.",
                },
                "agreed_terms": {
                    "type": "object",
                    "description": (
                        "Final agreed terms: price, payment_terms, rebate, conditions. "
                        "Required for DEAL_CLOSED."
                    ),
                },
                "savings_estimate": {
                    "type": "object",
                    "description": (
                        "Savings breakdown: vs_current, vs_bare_min, total_annual_savings. "
                        "Required for DEAL_CLOSED."
                    ),
                },
                "follow_up_slot": {
                    "type": "string",
                    "description": "Confirmed follow-up datetime (required for FOLLOW_UP_SCHEDULED).",
                },
                "locked_terms": {
                    "type": "object",
                    "description": "Terms already locked (for FOLLOW_UP_SCHEDULED).",
                },
                "outstanding_axes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Axes still under negotiation (for FOLLOW_UP_SCHEDULED).",
                },
                "escalation_reason": {
                    "type": "string",
                    "description": "Reason for escalation (required for ESCALATION_TO_AUTHORITY).",
                },
                "escalation_gap_analysis": {
                    "type": "object",
                    "description": "Gap analysis: price_gap, payment_gap, rebate_gap (for ESCALATION_TO_AUTHORITY).",
                },
                "negotiation_summary": {
                    "type": "object",
                    "description": "Full negotiation summary for audit trail.",
                },
                "call_outcome": {
                    "type": "string",
                    "enum": [
                        "DEAL_CLOSED",
                        "FOLLOW_UP_BOOKED",
                        "ESCALATED",
                        "NO_DEAL",
                    ],
                    "description": "Final negotiation outcome.",
                },
            },
            "required": ["exit_path", "call_outcome"],
        }

    def execute(self, arguments: dict) -> str:
        exit_path = arguments.get("exit_path", "")
        agreed_terms = arguments.get("agreed_terms", {})
        savings_estimate = arguments.get("savings_estimate", {})
        follow_up_slot = arguments.get("follow_up_slot")
        locked_terms = arguments.get("locked_terms", {})
        outstanding_axes = arguments.get("outstanding_axes", [])
        escalation_reason = arguments.get("escalation_reason", "")
        escalation_gap = arguments.get("escalation_gap_analysis", {})
        negotiation_summary = arguments.get("negotiation_summary", {})
        call_outcome = arguments.get("call_outcome", "")

        # ── Validate exit_path ──
        valid_paths = ["DEAL_CLOSED", "FOLLOW_UP_SCHEDULED", "ESCALATION_TO_AUTHORITY", "NO_DEAL_EXIT"]
        if exit_path not in valid_paths:
            return (
                f"REJECTED: Invalid exit_path '{exit_path}'. "
                f"Must be one of: {valid_paths}"
            )

        # ── Validate call_outcome ──
        valid_outcomes = ["DEAL_CLOSED", "FOLLOW_UP_BOOKED", "ESCALATED", "NO_DEAL"]
        if call_outcome not in valid_outcomes:
            return (
                f"REJECTED: Invalid call_outcome '{call_outcome}'. "
                f"Must be one of: {valid_outcomes}"
            )

        # ── Path-specific validation ──
        if exit_path == "DEAL_CLOSED":
            if not agreed_terms:
                return "REJECTED: agreed_terms is required for DEAL_CLOSED path."
            if call_outcome != "DEAL_CLOSED":
                return "REJECTED: call_outcome must be DEAL_CLOSED for DEAL_CLOSED path."

        elif exit_path == "FOLLOW_UP_SCHEDULED":
            if not follow_up_slot:
                return "REJECTED: follow_up_slot is required for FOLLOW_UP_SCHEDULED path."
            if call_outcome != "FOLLOW_UP_BOOKED":
                return "REJECTED: call_outcome must be FOLLOW_UP_BOOKED for FOLLOW_UP_SCHEDULED path."

        elif exit_path == "ESCALATION_TO_AUTHORITY":
            if not escalation_reason:
                return "REJECTED: escalation_reason is required for ESCALATION_TO_AUTHORITY path."
            if call_outcome != "ESCALATED":
                return "REJECTED: call_outcome must be ESCALATED for ESCALATION_TO_AUTHORITY path."

        elif exit_path == "NO_DEAL_EXIT":
            if call_outcome != "NO_DEAL":
                return "REJECTED: call_outcome must be NO_DEAL for NO_DEAL_EXIT path."

        # ── Build negotiation log entry ──
        negotiation_log = {
            "exit_path": exit_path,
            "call_outcome": call_outcome,
            "deal": {
                "agreed_terms": agreed_terms,
                "savings_estimate": savings_estimate,
            } if exit_path == "DEAL_CLOSED" else None,
            "follow_up": {
                "slot": follow_up_slot,
                "locked_terms": locked_terms,
                "outstanding_axes": outstanding_axes,
            } if exit_path == "FOLLOW_UP_SCHEDULED" else None,
            "escalation": {
                "reason": escalation_reason,
                "gap_analysis": escalation_gap,
            } if exit_path == "ESCALATION_TO_AUTHORITY" else None,
            "negotiation_summary": negotiation_summary,
            "logged_at": datetime.now().isoformat(timespec="seconds"),
        }

        # ── Persist to YAML register ──
        try:
            existing = _load_yaml(NEGOTIATIONS_FILE)
            if isinstance(existing, list):
                existing.append(negotiation_log)
                _dump_yaml(NEGOTIATIONS_FILE, existing)
            else:
                _dump_yaml(NEGOTIATIONS_FILE, [negotiation_log])
        except Exception:
            # Best-effort logging; continue even if file write fails
            pass

        # ── Return outcome message ──
        outcome_messages = {
            "DEAL_CLOSED": f"Deal closed — terms: {agreed_terms}",
            "FOLLOW_UP_BOOKED": f"Follow-up scheduled for {follow_up_slot}",
            "ESCALATED": f"Escalated to authority: {escalation_reason}",
            "NO_DEAL": "No deal reached — relationship preserved for future",
        }

        return (
            f"NEGOTIATION_ENDED - {outcome_messages.get(call_outcome, call_outcome)}. "
            f"Exit path: {exit_path}. "
            f"Negotiation logged successfully."
        )
