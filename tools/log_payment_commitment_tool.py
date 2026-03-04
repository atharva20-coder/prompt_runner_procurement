"""Log Payment Commitment Tool."""

import os
from datetime import datetime
from typing import Any

import yaml

from tool_registry import Tool


REGISTERS_DIR = "registers"
COMMITMENTS_FILE = os.path.join(REGISTERS_DIR, "commitments.yaml")


def _load_yaml(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data or {}


def _dump_yaml(path: str, data: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


class LogPaymentCommitmentTool(Tool):
    """Tool to log a customer's stated payment commitment to a YAML register."""

    @property
    def name(self) -> str:
        return "log_payment_commitment"

    @property
    def description(self) -> str:
        return (
            "Record a customer's payment commitment (amount, date, optional source) "
            "into a YAML register keyed by loan_number. "
            "Use immediately when the customer states a specific amount AND date."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "loan_number": {
                    "type": "string",
                    "description": "Customer's loan identifier used to group commitments.",
                },
                "amount": {
                    "type": "number",
                    "description": "Committed amount in INR.",
                },
                "date": {
                    "type": "string",
                    "description": "Committed date (ISO or human-readable).",
                },
                "source": {
                    "type": "string",
                    "description": "Optional source of funds (salary, family, savings, etc.).",
                },
                "notes": {
                    "type": "string",
                    "description": "Optional freeform notes for this commitment.",
                },
            },
            "required": ["loan_number", "amount", "date"],
        }

    def execute(self, arguments: dict) -> str:
        loan_number = str(arguments.get("loan_number", "")).strip()
        amount = arguments.get("amount")
        date_str = str(arguments.get("date", "")).strip()
        source = arguments.get("source")
        notes = arguments.get("notes")

        if not loan_number:
            return "REJECTED: loan_number is required."
        if amount is None:
            return "REJECTED: amount is required."
        if not date_str:
            return "REJECTED: date is required."

        now_iso = datetime.now().isoformat(timespec="seconds")
        entry = {
            "amount": float(amount),
            "date": date_str,
            "source": source or None,
            "notes": notes or None,
            "logged_at": now_iso,
        }

        data = _load_yaml(COMMITMENTS_FILE)
        account = data.get(loan_number) or {}

        history = account.get("commitment_history") or []
        history.append(entry)

        # Maintain convenience aggregates
        account["last_commitment"] = entry
        account["commitment_history"] = history
        account["quoted_amounts"] = [h.get("amount") for h in history if "amount" in h]
        account["max_quoted_amount"] = max(account["quoted_amounts"]) if account["quoted_amounts"] else None

        data[loan_number] = account
        _dump_yaml(COMMITMENTS_FILE, data)

        return (
            f"COMMITMENT_LOGGED: ₹{amount} on {date_str} "
            f"for loan {loan_number}. History count: {len(history)}."
        )

