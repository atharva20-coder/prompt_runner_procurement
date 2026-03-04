"""Unified Delay Script Tool."""

import os
from tool_registry import Tool


SCRIPT_MAP = {
    "JOB_LOSS": "job_loss_script.md",
    "MEDICAL": "medical_script.md",
    "ACCIDENT": "accident_script.md",
    "BUSINESS_SLOWDOWN": "business_slowdown_script.md",
    "CUSTOMER_PAYMENT_DELAY": "customer_payment_delay_script.md",
    "OVER_LEVERAGE": "over_leverage_script.md",
    "REDUCED_SALARY": "reduced_salary_script.md",
    "SALARY_DELAY": "salary_delay_script.md",
    "OTHER": "other_script.md",
}

VALID_REASONS = list(SCRIPT_MAP.keys())


class DelayScriptTool(Tool):
    """Unified tool to retrieve delay-reason-specific scripts."""

    @property
    def name(self) -> str:
        return "get_delay_script"

    @property
    def description(self) -> str:
        return (
            "Load the investigation script for a specific delay reason. "
            "Call this ONCE when the delay reason is confirmed. "
            f"Valid delay_reason values: {', '.join(VALID_REASONS)}"
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "delay_reason": {
                    "type": "string",
                    "enum": VALID_REASONS,
                    "description": "The categorized delay reason for the customer's payment issue.",
                }
            },
            "required": ["delay_reason"],
        }

    def execute(self, arguments: dict) -> str:
        delay_reason = arguments.get("delay_reason", "").upper()
        
        if delay_reason not in SCRIPT_MAP:
            return f"Error: Invalid delay_reason '{delay_reason}'. Valid options: {', '.join(VALID_REASONS)}"
        
        script_file = SCRIPT_MAP[delay_reason]
        script_path = os.path.join("scripts", script_file)
        
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: Script file not found at {script_path}"
        except Exception as e:
            return f"Error reading script: {str(e)}"
