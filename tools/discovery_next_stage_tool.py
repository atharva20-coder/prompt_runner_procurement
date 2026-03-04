"""Discovery Next Stage Tool — Procurement Pipeline.

Signals transition from Discovery → Qualification stage.
Validates that required supplier context fields were captured before
allowing NARA to advance. Modeled on intro_next_stage_tool.py from
the recovery pipeline.

Called by: Intro_stage_prompt.md (Discovery stage)
Routes to: QUALIFICATION (or NEGOTIATION for eager suppliers)
"""

from tool_registry import Tool


class DiscoveryNextStageTool(Tool):
    """Tool to signal transition from discovery to qualification stage."""

    @property
    def name(self) -> str:
        return "discovery_next_stage"

    @property
    def description(self) -> str:
        return (
            "Transition from the DISCOVERY stage to the next stage. "
            "ONLY call when exit_criteria_matched is TRUE in your state. "
            "You must pass the complete discovery context as proof. "
            "Routes to QUALIFICATION (normal flow) or NEGOTIATION (if supplier wants to skip)."
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
                        "DO NOT call this tool. Continue the discovery conversation."
                    ),
                },
                "category_confirmed": {
                    "type": "string",
                    "description": "The validated supplier category (e.g., SAAS_SOFTWARE, RAW_MATERIAL).",
                },
                "relationship_context": {
                    "type": "string",
                    "description": "Supplier's perspective on the partnership — pain points, satisfaction, etc.",
                },
                "supplier_opening_position": {
                    "type": "string",
                    "enum": [
                        "PRICE_INCREASE_REQUESTED",
                        "STATUS_QUO",
                        "OPEN_TO_NEGOTIATE",
                        "DEFENSIVE",
                        "EAGER_TO_NEGOTIATE",
                    ],
                    "description": "The supplier's initial stance on renewal terms.",
                },
                "supplier_sentiment": {
                    "type": "string",
                    "enum": ["COLLABORATIVE", "TRANSACTIONAL", "DEFENSIVE", "FRUSTRATED"],
                    "description": "The supplier's emotional baseline going into negotiation.",
                },
                "next_stage": {
                    "type": "string",
                    "enum": ["QUALIFICATION", "NEGOTIATION"],
                    "description": (
                        "QUALIFICATION for normal flow. "
                        "NEGOTIATION only if supplier explicitly wants to jump to numbers."
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
        category_confirmed = arguments.get("category_confirmed", "")
        relationship_context = arguments.get("relationship_context", "")
        supplier_opening_position = arguments.get("supplier_opening_position", "")
        supplier_sentiment = arguments.get("supplier_sentiment", "")
        next_stage = arguments.get("next_stage", "")
        reason = arguments.get("reason", "")

        # ── Gate: exit_criteria_matched must be True ──
        if not exit_matched:
            return (
                "REJECTED: exit_criteria_matched must be TRUE to transition. "
                "Continue the discovery conversation until exit criteria is met."
            )

        # ── Gate: next_stage must be valid ──
        valid_stages = ["QUALIFICATION", "NEGOTIATION"]
        if next_stage not in valid_stages:
            return (
                f"REJECTED: Invalid next_stage '{next_stage}'. "
                f"Must be one of: {valid_stages}"
            )

        # ── Build handoff data for the next stage ──
        handoff = {
            "from_stage": "DISCOVERY",
            "category_confirmed": category_confirmed,
            "relationship_context": relationship_context,
            "supplier_opening_position": supplier_opening_position,
            "supplier_sentiment": supplier_sentiment,
            "reason": reason,
        }

        # ── Signal stage transition ──
        from orchestrator import StageTransitionSignal

        raise StageTransitionSignal(
            from_stage="DISCOVERY",
            next_stage=next_stage,
            handoff_data=handoff,
        )
