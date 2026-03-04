"""Qualification Next Stage Tool — Procurement Pipeline.

Signals transition from Qualification → Negotiation stage.
Passes all captured qualification fields as handoff data so the
negotiation engine has full context about the supplier's business
characteristics.

Called by: Procurement_qualification_stage_prompt.md (Qualification stage)
Routes to: NEGOTIATION
"""

from tool_registry import Tool


class QualificationNextStageTool(Tool):
    """Tool to signal transition from qualification to negotiation stage."""

    @property
    def name(self) -> str:
        return "qualification_next_stage"

    @property
    def description(self) -> str:
        return (
            "Transition from the QUALIFICATION stage to NEGOTIATION. "
            "ONLY call when exit_criteria_matched is TRUE in your state. "
            "You must pass all captured qualification fields as proof."
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
                        "DO NOT call this tool. Continue asking qualification questions."
                    ),
                },
                "qualification_fields": {
                    "type": "object",
                    "description": (
                        "All captured qualification fields from the category script. "
                        "These are category-specific (e.g., license_model for SaaS, "
                        "pricing_basis for Raw Material). Include ALL non-null fields."
                    ),
                },
                "avoidance_count": {
                    "type": "integer",
                    "description": "Number of times supplier avoided answering.",
                },
                "next_stage": {
                    "type": "string",
                    "enum": ["NEGOTIATION"],
                    "description": "Must be NEGOTIATION.",
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
        qualification_fields = arguments.get("qualification_fields", {})
        avoidance_count = arguments.get("avoidance_count", 0)
        next_stage = arguments.get("next_stage", "")
        reason = arguments.get("reason", "")

        # ── Gate: exit_criteria_matched must be True ──
        if not exit_matched:
            return (
                "REJECTED: exit_criteria_matched must be TRUE to transition. "
                "Continue asking qualification questions or skip remaining fields."
            )

        # ── Gate: next_stage must be NEGOTIATION ──
        if next_stage != "NEGOTIATION":
            return (
                f"REJECTED: Invalid next_stage '{next_stage}'. "
                "Must be 'NEGOTIATION'."
            )

        # ── Build handoff data for negotiation stage ──
        handoff = {
            "from_stage": "QUALIFICATION",
            "qualification_fields": qualification_fields,
            "avoidance_count": avoidance_count,
            "reason": reason,
        }

        # ── Signal stage transition ──
        from orchestrator import StageTransitionSignal

        raise StageTransitionSignal(
            from_stage="QUALIFICATION",
            next_stage=next_stage,
            handoff_data=handoff,
        )
