"""Procurement Next Stage Tool — Procurement Pipeline.

Signals transition from Negotiation → Exit stage.
Validates exit criteria, agreed terms, and exit path before allowing
NARA to advance to the closure stage. This is the procurement equivalent
of recovery_next_stage_tool.py.

Called by: Procurement_stage_prompt.md (Negotiation stage)
Routes to: EXIT with one of 4 paths:
  - DEAL_CLOSED          → All terms agreed at/above bare minimum
  - FOLLOW_UP_SCHEDULED  → Partial progress, follow-up needed
  - ESCALATION_TO_AUTHORITY → Supplier can't meet bare minimum
  - NO_DEAL_EXIT         → No agreement possible
"""

from tool_registry import Tool


class ProcurementNextStageTool(Tool):
    """Tool to signal transition from negotiation to exit stage."""

    @property
    def name(self) -> str:
        return "procurement_next_stage"

    @property
    def description(self) -> str:
        return (
            "Transition to the EXIT stage. "
            "ONLY call when exit_criteria_matched is TRUE in your CONVERSATION_CONTEXT_REGISTER. "
            "You must pass the complete negotiation context and exit handoff data as proof. "
            "If the exit validation checklist is not complete, DO NOT call this tool."
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
                        "DEAL_CLOSED",
                        "FOLLOW_UP_SCHEDULED",
                        "ESCALATION_TO_AUTHORITY",
                        "NO_DEAL_EXIT",
                    ],
                    "description": "The exit path being taken.",
                },
                "commitment": {
                    "type": "object",
                    "description": (
                        "The agreed terms: price, payment_terms, rebate, conditions. "
                        "Required for DEAL_CLOSED and FOLLOW_UP_SCHEDULED paths."
                    ),
                },
                "negotiation_summary": {
                    "type": "object",
                    "description": (
                        "Summary of the negotiation: strategies_used, levers_used, "
                        "nudges_used, total_exchanges, deal_quality_score."
                    ),
                },
                "reason": {
                    "type": "string",
                    "description": "Brief explanation of why exit criteria is met.",
                },
                "savings_estimate": {
                    "type": "object",
                    "description": (
                        "Savings breakdown: vs_current, vs_bare_min, total_annual_savings. "
                        "Required for DEAL_CLOSED path."
                    ),
                },
                "follow_up_axes_outstanding": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Axes still under negotiation (for FOLLOW_UP_SCHEDULED).",
                },
                "escalation_reason": {
                    "type": "string",
                    "description": "Reason for escalation (for ESCALATION_TO_AUTHORITY).",
                },
            },
            "required": ["exit_criteria_matched", "exit_path", "reason"],
        }

    def execute(self, arguments: dict) -> str:
        exit_matched = arguments.get("exit_criteria_matched", False)
        exit_path = arguments.get("exit_path", "")
        commitment = arguments.get("commitment", {})
        negotiation_summary = arguments.get("negotiation_summary", {})
        reason = arguments.get("reason", "")
        savings_estimate = arguments.get("savings_estimate", {})
        follow_up_axes = arguments.get("follow_up_axes_outstanding", [])
        escalation_reason = arguments.get("escalation_reason", "")

        # ── Gate: exit_criteria_matched must be True ──
        if not exit_matched:
            return (
                "REJECTED: exit_criteria_matched must be TRUE to transition. "
                "Continue the negotiation until exit conditions are met."
            )

        # ── Gate: exit_path must be valid ──
        valid_paths = [
            "DEAL_CLOSED",
            "FOLLOW_UP_SCHEDULED",
            "ESCALATION_TO_AUTHORITY",
            "NO_DEAL_EXIT",
        ]
        if exit_path not in valid_paths:
            return (
                f"REJECTED: Invalid exit_path '{exit_path}'. "
                f"Must be one of: {valid_paths}"
            )

        # ── Validate DEAL_CLOSED requires commitment with all 3 axes ──
        if exit_path == "DEAL_CLOSED":
            required_axes = ["price", "payment_terms", "rebate"]
            missing = [a for a in required_axes if not commitment.get(a)]
            if missing:
                return (
                    f"REJECTED: DEAL_CLOSED requires all 3 axes in commitment. "
                    f"Missing: {missing}. Continue negotiation to secure all terms."
                )

        # ── Validate FOLLOW_UP_SCHEDULED requires some commitment progress ──
        if exit_path == "FOLLOW_UP_SCHEDULED":
            if not commitment and not follow_up_axes:
                return (
                    "REJECTED: FOLLOW_UP_SCHEDULED requires either partial commitment "
                    "or outstanding axes. Capture at least one locked term."
                )

        # ── Validate ESCALATION_TO_AUTHORITY requires reason ──
        if exit_path == "ESCALATION_TO_AUTHORITY":
            if not escalation_reason:
                return (
                    "REJECTED: ESCALATION_TO_AUTHORITY requires an escalation_reason. "
                    "Explain why the supplier cannot meet bare minimum."
                )

        # ── Build exit handoff ──
        exit_handoff = {
            "from_stage": "NEGOTIATION",
            "exit_path": exit_path,
            "commitment": commitment,
            "negotiation_summary": negotiation_summary,
            "savings_estimate": savings_estimate,
            "follow_up_axes_outstanding": follow_up_axes,
            "escalation_reason": escalation_reason,
            "reason": reason,
        }

        # ── Signal stage transition to EXIT ──
        from orchestrator import StageTransitionSignal

        raise StageTransitionSignal(
            from_stage="NEGOTIATION",
            next_stage="EXIT",
            handoff_data=exit_handoff,
        )
