"""Intro Next Stage Tool."""

from tool_registry import Tool


class IntroNextStageTool(Tool):
    """Tool to signal transition from introduction to investigation/dispute/recovery stage."""

    @property
    def name(self) -> str:
        return "intro_next_stage"

    @property
    def description(self) -> str:
        return (
            "Transition from the INTRODUCTION stage. "
            "ONLY call when exit_criteria_matched is TRUE in your INTRO_STAGE_INFO. "
            "You must pass the complete INTRO_STAGE_INFO as proof. "
            "Routes to INVESTIGATION (if delay reason captured), "
            "DISPUTE_HANDLER (if dispute detected), or RECOVERY (if 3+ avoidances)."
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
                        "DO NOT call this tool. Continue the conversation."
                    ),
                },
                "delay_reason_captured": {
                    "type": "boolean",
                    "description": "Whether the customer's delay reason was captured.",
                },
                "raw_statement": {
                    "type": "string",
                    "description": "The customer's exact words explaining their delay reason.",
                },
                "category": {
                    "type": "string",
                    "enum": [
                        "MEDICAL",
                        "ACCIDENT",
                        "JOB_LOSS",
                        "SALARY_DELAY",
                        "REDUCED_SALARY",
                        "BUSINESS_SLOWDOWN",
                        "CUSTOMER_PAYMENT_DELAY",
                        "OVER_LEVERAGE",
                        "OTHER",
                    ],
                    "description": "The classified reason category.",
                },
                "dispute_detected": {
                    "type": "boolean",
                    "description": "Whether a dispute was raised by the customer.",
                },
                "dispute_type": {
                    "type": "string",
                    "enum": [
                        "WRONG_PERSON",
                        "WRONG_LOAN",
                        "CUSTOMER_DEATH",
                        "WRONG_EMI",
                        "EMI_ALREADY_PAID",
                        "WRONG_CHARGES",
                        "PAST_CALL_EXPERIENCE",
                        "MULTIPLE_CALLS",
                        "OTHER_DISPUTE",
                    ],
                    "description": "The type of dispute if detected.",
                },
                "avoidance_count": {
                    "type": "integer",
                    "description": "Number of times customer avoided answering.",
                },
                "commitment": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "string"},
                        "date": {"type": "string"}
                    },
                    "description": "Captured commitment details (amount, date) if any.",
                },
                "next_stage": {
                    "type": "string",
                    "enum": ["INVESTIGATION", "DISPUTE_HANDLER", "RECOVERY"],
                    "description": (
                        "The next stage to route to: "
                        "INVESTIGATION (delay reason captured), "
                        "DISPUTE_HANDLER (dispute detected), "
                        "or RECOVERY (3+ avoidances)."
                    ),
                },
                "reason": {
                    "type": "string",
                    "description": "Brief explanation of why exit criteria is met.",
                },
            },
            "required": ["exit_criteria_matched", "next_stage", "reason"],
        }

    def execute(self, arguments: dict) -> str:
        exit_matched = arguments.get("exit_criteria_matched", False)
        delay_reason_captured = arguments.get("delay_reason_captured", False)
        raw_statement = arguments.get("raw_statement", "")
        category = arguments.get("category", "")
        dispute_detected = arguments.get("dispute_detected", False)
        dispute_type = arguments.get("dispute_type", "")
        avoidance_count = arguments.get("avoidance_count", 0)
        commitment = arguments.get("commitment", None)
        next_stage = arguments.get("next_stage", "")
        reason = arguments.get("reason", "")

        # Reject if exit_criteria_matched is not True
        if not exit_matched:
            return (
                "REJECTED: exit_criteria_matched must be TRUE to transition. "
                "Continue the conversation until exit criteria is met."
            )

        # Validate next_stage
        valid_stages = ["INVESTIGATION", "DISPUTE_HANDLER", "RECOVERY"]
        if next_stage not in valid_stages:
            return (
                f"REJECTED: Invalid next_stage '{next_stage}'. "
                f"Must be one of: {valid_stages}"
            )

        # Validate based on next_stage
        if next_stage == "INVESTIGATION":
            if not delay_reason_captured:
                return (
                    "REJECTED: Cannot route to INVESTIGATION without capturing delay reason. "
                    "delay_reason_captured must be TRUE."
                )
            if not raw_statement:
                return (
                    "REJECTED: raw_statement is required when routing to INVESTIGATION. "
                    "Capture the customer's exact words."
                )
            if not category:
                return (
                    "REJECTED: category is required when routing to INVESTIGATION. "
                    "Classify the delay reason into a category."
                )

        elif next_stage == "DISPUTE_HANDLER":
            if not dispute_detected:
                return (
                    "REJECTED: Cannot route to DISPUTE_HANDLER without detecting dispute. "
                    "dispute_detected must be TRUE."
                )
            if not dispute_type:
                return (
                    "REJECTED: dispute_type is required when routing to DISPUTE_HANDLER. "
                    "Classify the dispute type."
                )

        elif next_stage == "RECOVERY":
            if avoidance_count < 3:
                return (
                    f"REJECTED: Cannot route to RECOVERY with avoidance_count={avoidance_count}. "
                    "Need at least 3 avoidances to skip to RECOVERY."
                )

        # Build handoff data
        handoff = {
            "from_stage": "INTRODUCTION",
            "delay_reason": {
                "captured": delay_reason_captured,
                "raw_statement": raw_statement,
                "category": category,
            },
            "dispute": {
                "detected": dispute_detected,
                "type": dispute_type,
            },
            "avoidance_count": avoidance_count,
            "commitment": commitment,
            "reason": reason,
        }
        
        # Strip internal fields before passing to next stage
        if "exit_criteria_matched" in handoff:
            del handoff["exit_criteria_matched"]

        # Signal stage transition
        from orchestrator import StageTransitionSignal

        raise StageTransitionSignal(
            from_stage="INTRODUCTION",
            next_stage=next_stage,
            handoff_data=handoff,
        )
