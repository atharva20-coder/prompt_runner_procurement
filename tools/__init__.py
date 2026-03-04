"""Tools package - Custom tool implementations.

Exports both recovery pipeline tools and procurement pipeline tools.
The orchestrator and main.py use TOOL_CLASSES to map tool names to classes.
"""

# ── Recovery Pipeline Tools ──
from tools.delay_script_tool import DelayScriptTool
from tools.end_call_tool import EndCallTool
from tools.intro_next_stage_tool import IntroNextStageTool
from tools.investigation_next_stage_tool import InvestigationNextStageTool
from tools.recovery_next_stage_tool import RecoveryNextStageTool
from tools.log_payment_commitment_tool import LogPaymentCommitmentTool

# ── Procurement Pipeline Tools ──
# These tools power the Discovery → Qualification → Negotiation → Exit pipeline.
from tools.discovery_next_stage_tool import DiscoveryNextStageTool
from tools.category_script_tool import CategoryScriptTool
from tools.qualification_next_stage_tool import QualificationNextStageTool
from tools.procurement_next_stage_tool import ProcurementNextStageTool
from tools.end_negotiation_tool import EndNegotiationTool

__all__ = [
    # Recovery
    "DelayScriptTool",
    "EndCallTool",
    "IntroNextStageTool",
    "InvestigationNextStageTool",
    "RecoveryNextStageTool",
    "LogPaymentCommitmentTool",
    # Procurement
    "DiscoveryNextStageTool",
    "CategoryScriptTool",
    "QualificationNextStageTool",
    "ProcurementNextStageTool",
    "EndNegotiationTool",
]
