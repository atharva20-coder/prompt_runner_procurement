"""Recovery Next Stage Tool."""

from tool_registry import Tool


class RecoveryNextStageTool(Tool):
    """Tool to signal transition from recovery to exit stage."""

    @property
    def name(self) -> str:
        return "recovery_next_stage"

    @property
    def description(self) -> str:
        return (
            "Transition to the EXIT stage. "
            "ONLY call when exit_criteria_matched is TRUE in your CONVERSATION_CONTEXT_REGISTER. "
            "You must pass the complete recovery context and exit handoff data as proof. "
            "If exit validation checklist is not complete, DO NOT call this tool."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "exit_criteria_matched": {
                    "type": "boolean",
                    "description": (
                        "Must be TRUE. If this is false or if you're unsure, "
                        "DO NOT call this tool. Continue the negotiation."
                    ),
                },
                "exit_path": {
                    "type": "string",
                    "enum": [
                        "PAYMENT_IMMEDIATE",
                        "FOLLOW_UP_SCHEDULED",
                        "SUPERVISOR_ESCALATION",
                        "IMMEDIATE_EXIT",
                        "INVESTIGATION_EXIT",
                    ],
                    "description": "The exit path being taken.",
                },
                "commitment": {
                    "type": "object",
                    "description": (
                        "The commitment details: amount, date, is_split, "
                        "remainder_amount (if split), remainder_date (if split)."
                    ),
                },
                "recovery_summary": {
                    "type": "object",
                    "description": (
                        "Summary of the recovery stage including stage traversed, "
                        "tactics used, and final outcome."
                    ),
                },
                "reason": {
                    "type": "string",
                    "description": "Brief explanation of why exit criteria is met",
                },
                "emi_amount": {
                    "type": "number",
                    "description": "EMI amount used to derive floor for validation (optional but recommended).",
                },
                "min_floor_amount": {
                    "type": "number",
                    "description": "Minimum acceptable amount for exit (e.g., emi × 0.2). Required for PAYMENT_IMMEDIATE/FOLLOW_UP_SCHEDULED validation if enforcing floor.",
                },
                "max_timeline_days": {
                    "type": "integer",
                    "description": "Maximum allowed days for the commitment date (e.g., 2 for B/C, 5 for D).",
                },
                "days_until_commitment": {
                    "type": "integer",
                    "description": "Numeric days from today until the commitment date. Used to validate against max_timeline_days.",
                },
            },
            "required": ["exit_criteria_matched", "exit_path", "commitment", "reason"],
        }

    def execute(self, arguments: dict) -> str:
        exit_matched = arguments.get("exit_criteria_matched", False)
        exit_path = arguments.get("exit_path", "")
        commitment = arguments.get("commitment", {})
        recovery_summary = arguments.get("recovery_summary", {})
        reason = arguments.get("reason", "")
        emi_amount = arguments.get("emi_amount")
        min_floor_amount = arguments.get("min_floor_amount")
        max_timeline_days = arguments.get("max_timeline_days")
        days_until_commitment = arguments.get("days_until_commitment")

        # Reject if exit_criteria_matched is not True
        if not exit_matched:
            return (
                "REJECTED: exit_criteria_matched must be TRUE to transition. "
                "Continue the negotiation until exit conditions are met."
            )

        # Validate exit path
        valid_paths = [
            "PAYMENT_IMMEDIATE",
            "FOLLOW_UP_SCHEDULED",
            "SUPERVISOR_ESCALATION",
            "IMMEDIATE_EXIT",
            "INVESTIGATION_EXIT",
        ]
        if exit_path not in valid_paths:
            return (
                f"REJECTED: Invalid exit_path '{exit_path}'. "
                f"Must be one of: {valid_paths}"
            )

        # Validate commitment has required fields
        required_commitment_fields = ["amount", "date"]
        missing_fields = [
            f for f in required_commitment_fields if f not in commitment or commitment[f] is None
        ]

        # Allow missing commitment ONLY for these paths
        paths_allowing_null_commitment = ["IMMEDIATE_EXIT", "INVESTIGATION_EXIT", "SUPERVISOR_ESCALATION"]
        if missing_fields and exit_path not in paths_allowing_null_commitment:
            return (
                f"REJECTED: Missing required commitment fields: {missing_fields}. "
                "Ensure amount and date are captured before exiting."
            )

        # Enforce floor for applicable paths if provided
        if exit_path in ["PAYMENT_IMMEDIATE", "FOLLOW_UP_SCHEDULED"]:
            amt = commitment.get("amount")
            if amt is None:
                return (
                    "REJECTED: commitment.amount is required for this exit_path."
                )
            if min_floor_amount is not None and amt < float(min_floor_amount):
                return (
                    f"REJECTED: commitment.amount ₹{amt} is below floor ₹{min_floor_amount}. "
                    "Escalate or enforce FE; do not exit with below-floor amount."
                )
            if max_timeline_days is not None and days_until_commitment is not None:
                if int(days_until_commitment) > int(max_timeline_days):
                    return (
                        f"REJECTED: commitment date is beyond the allowed limit ({days_until_commitment} > {max_timeline_days} days). "
                        "Apply Timeline Enforcement and re-confirm within the allowed window."
                    )

        # Build exit handoff
        exit_handoff = {
            "from_stage": "RECOVERY",
            "exit_path": exit_path,
            "commitment": commitment,
            "recovery_summary": recovery_summary,
            "reason": reason,
            "validation": {
                "emi_amount": emi_amount,
                "min_floor_amount": min_floor_amount,
            },
        }
        
        # Strip internal fields before passing to next stage
        if "exit_criteria_matched" in exit_handoff:
            del exit_handoff["exit_criteria_matched"]

        # Signal stage transition to EXIT
        from orchestrator import StageTransitionSignal

        raise StageTransitionSignal(
            from_stage="RECOVERY",
            next_stage="EXIT",
            handoff_data=exit_handoff,
        )
