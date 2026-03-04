"""End Call Tool."""

import os
from datetime import datetime
import yaml

from tool_registry import Tool

REGISTERS_DIR = "registers"
CALLS_FILE = os.path.join(REGISTERS_DIR, "calls.yaml")

def _load_yaml(path: str) -> list | dict:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data or []

def _dump_yaml(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


class EndCallTool(Tool):
    """Tool to end the call and log the outcome."""

    @property
    def name(self) -> str:
        return "end_call"

    @property
    def description(self) -> str:
        return (
            "End the call and log the outcome. "
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
                        "PAYMENT_IMMEDIATE",
                        "FOLLOW_UP_SCHEDULED",
                        "SUPERVISOR_ESCALATION",
                    ],
                    "description": "The exit path being taken.",
                },
                "payment_amount": {
                    "type": "number",
                    "description": "Amount being paid (required for PAYMENT_IMMEDIATE).",
                },
                "payment_confirmed": {
                    "type": "boolean",
                    "description": "Whether payment was confirmed (required for PAYMENT_IMMEDIATE).",
                },
                "follow_up_slot": {
                    "type": "string",
                    "description": "Confirmed follow-up datetime (required for FOLLOW_UP_SCHEDULED).",
                },
                "follow_up_reason": {
                    "type": "string",
                    "description": "Reason for follow-up (required for FOLLOW_UP_SCHEDULED).",
                },
                "escalation_reason": {
                    "type": "string",
                    "description": "Reason for supervisor escalation (required for SUPERVISOR_ESCALATION).",
                },
                "call_outcome": {
                    "type": "string",
                    "enum": [
                        "PAYMENT_RECEIVED",
                        "FOLLOW_UP_BOOKED",
                        "ESCALATED",
                    ],
                    "description": "Final call outcome.",
                },
                "commitment_summary": {
                    "type": "object",
                    "description": "Summary of customer commitment (amount, date, source).",
                },
            },
            "required": ["exit_path", "call_outcome"],
        }

    def execute(self, arguments: dict) -> str:
        exit_path = arguments.get("exit_path", "")
        payment_amount = arguments.get("payment_amount")
        payment_confirmed = arguments.get("payment_confirmed")
        follow_up_slot = arguments.get("follow_up_slot")
        follow_up_reason = arguments.get("follow_up_reason")
        escalation_reason = arguments.get("escalation_reason")
        call_outcome = arguments.get("call_outcome", "")
        commitment_summary = arguments.get("commitment_summary", {})

        # Validate exit_path
        valid_paths = ["PAYMENT_IMMEDIATE", "FOLLOW_UP_SCHEDULED", "SUPERVISOR_ESCALATION"]
        if exit_path not in valid_paths:
            return (
                f"REJECTED: Invalid exit_path '{exit_path}'. "
                f"Must be one of: {valid_paths}"
            )

        # Validate call_outcome
        valid_outcomes = ["PAYMENT_RECEIVED", "FOLLOW_UP_BOOKED", "ESCALATED"]
        if call_outcome not in valid_outcomes:
            return (
                f"REJECTED: Invalid call_outcome '{call_outcome}'. "
                f"Must be one of: {valid_outcomes}"
            )

        # Validate path-specific requirements
        if exit_path == "PAYMENT_IMMEDIATE":
            if payment_amount is None:
                return "REJECTED: payment_amount is required for PAYMENT_IMMEDIATE path."
            if payment_confirmed is None:
                return "REJECTED: payment_confirmed is required for PAYMENT_IMMEDIATE path."
            if not payment_confirmed:
                return "REJECTED: payment_confirmed must be TRUE to end call for PAYMENT_IMMEDIATE."
            if call_outcome != "PAYMENT_RECEIVED":
                return "REJECTED: call_outcome must be PAYMENT_RECEIVED for PAYMENT_IMMEDIATE path."

        elif exit_path == "FOLLOW_UP_SCHEDULED":
            if not follow_up_slot:
                return "REJECTED: follow_up_slot is required for FOLLOW_UP_SCHEDULED path."
            if not follow_up_reason:
                return "REJECTED: follow_up_reason is required for FOLLOW_UP_SCHEDULED path."
            if call_outcome != "FOLLOW_UP_BOOKED":
                return "REJECTED: call_outcome must be FOLLOW_UP_BOOKED for FOLLOW_UP_SCHEDULED path."

        elif exit_path == "SUPERVISOR_ESCALATION":
            if not escalation_reason:
                return "REJECTED: escalation_reason is required for SUPERVISOR_ESCALATION path."
            if call_outcome != "ESCALATED":
                return "REJECTED: call_outcome must be ESCALATED for SUPERVISOR_ESCALATION path."

        # Build call log
        call_log = {
            "exit_path": exit_path,
            "call_outcome": call_outcome,
            "payment": {
                "amount": payment_amount,
                "confirmed": payment_confirmed,
            } if exit_path == "PAYMENT_IMMEDIATE" else None,
            "follow_up": {
                "slot": follow_up_slot,
                "reason": follow_up_reason,
            } if exit_path == "FOLLOW_UP_SCHEDULED" else None,
            "escalation": {
                "reason": escalation_reason,
            } if exit_path == "SUPERVISOR_ESCALATION" else None,
            "commitment_summary": commitment_summary,
            "logged_at": datetime.now().isoformat(timespec="seconds"),
        }

        # Persist to YAML register
        try:
            existing = _load_yaml(CALLS_FILE)
            if isinstance(existing, list):
                existing.append(call_log)
                _dump_yaml(CALLS_FILE, existing)
            else:
                _dump_yaml(CALLS_FILE, [call_log])
        except Exception:
            # Best-effort logging; continue even if file write fails
            pass

        # Log the outcome
        outcome_messages = {
            "PAYMENT_RECEIVED": f"Payment of ₹{payment_amount} confirmed",
            "FOLLOW_UP_BOOKED": f"Follow-up scheduled for {follow_up_slot}",
            "ESCALATED": f"Escalated to supervisor: {escalation_reason}",
        }

        return (
            f"CALL_ENDED - {outcome_messages.get(call_outcome, call_outcome)}. "
            f"Exit path: {exit_path}. "
            f"Call logged successfully."
        )
