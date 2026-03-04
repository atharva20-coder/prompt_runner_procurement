"""Investigation Next Stage Tool."""

from tool_registry import Tool


class InvestigationNextStageTool(Tool):
    """Tool to signal transition from investigation to recovery stage."""

    @property
    def name(self) -> str:
        return "investigation_next_stage"

    @property
    def description(self) -> str:
        return (
            "Transition to the RECOVERY stage. "
            "ONLY call when exit_criteria_matched is TRUE in your INVESTIGATION_STAGE_INFO. "
            "You must pass the complete INVESTIGATION_STAGE_INFO as proof. "
            "If exit is due to all fields answered, all required fields must be non-null. "
            "If exit is due to all fields resolved (answered + SKIPPED), no null fields should remain. "
            "If exit is due to avoidance (Rule 5 Step 3), nulls are allowed."
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
                        "DO NOT call this tool. Continue asking questions."
                    ),
                },
                "investigation_stage_info": {
                    "type": "object",
                    "description": (
                        "The complete INVESTIGATION_STAGE_INFO JSON with all captured field values."
                    ),
                },
                "reason": {
                    "type": "string",
                    "description": "Brief explanation of why exit criteria is met (include 'avoidance' if exiting due to repeated non-responses)",
                },
            },
            "required": ["exit_criteria_matched", "investigation_stage_info", "reason"],
        }

    def execute(self, arguments: dict) -> str:
        exit_matched = arguments.get("exit_criteria_matched", False)
        stage_info = arguments.get("investigation_stage_info", {})
        reason = arguments.get("reason", "")
        
        # Reject if exit_criteria_matched is not True
        if not exit_matched:
            return (
                "REJECTED: exit_criteria_matched must be TRUE to transition. "
                "Continue asking questions until all required fields are captured."
            )
        
        # Check that script was loaded
        if not stage_info.get("script_loaded", False):
            return (
                "REJECTED: Script was not loaded. Call get_delay_script first."
            )
        
        # Count non-null fields (excluding script_loaded and exit_criteria_matched)
        excluded_keys = {"script_loaded", "exit_criteria_matched", "commitment"}
        captured_fields = {
            k: v for k, v in stage_info.items() 
            if k not in excluded_keys and v is not None and v != "SKIPPED"
        }
        skipped_fields = [
            k for k, v in stage_info.items() 
            if k not in excluded_keys and v == "SKIPPED"
        ]
        null_fields = [
            k for k, v in stage_info.items() 
            if k not in excluded_keys and v is None
        ]
        
        # Allow exit if: avoidance-based, OR all fields resolved (answered + SKIPPED, no nulls)
        is_avoidance_exit = "avoidance" in reason.lower()
        all_fields_resolved = len(null_fields) == 0
        
        if not is_avoidance_exit and not all_fields_resolved and len(captured_fields) + len(skipped_fields) < 3:
            return (
                f"REJECTED: Only {len(captured_fields)} field(s) captured: {list(captured_fields.keys())}. "
                f"Fields still null: {null_fields}. "
                "Need at least 3 required fields or resolve all fields. Continue asking questions."
            )
        # Strip internal fields before passing to next stage
        for key in ["exit_criteria_matched", "script_loaded"]:
            if key in stage_info:
                del stage_info[key]

        # Build handoff data
        handoff = {
            "from_stage": "INVESTIGATION",
            "investigation_stage_info": stage_info,
            "captured_fields": captured_fields,
            "null_fields": null_fields,
            "reason": reason,
        }

        # Signal stage transition to RECOVERY
        from orchestrator import StageTransitionSignal

        raise StageTransitionSignal(
            from_stage="INVESTIGATION",
            next_stage="RECOVERY",
            handoff_data=handoff,
        )
