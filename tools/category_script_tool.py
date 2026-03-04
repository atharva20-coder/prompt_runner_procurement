"""Category Script Tool — Procurement Pipeline.

Loads supplier-category-specific qualification scripts from the scripts/
directory. This is the procurement equivalent of delay_script_tool.py
from the recovery pipeline.

Called by: Procurement_qualification_stage_prompt.md (Qualification stage)
Returns: The full text of the matching category script for NARA to follow.

Maps 8 supplier categories to their corresponding script files:
  SAAS_SOFTWARE        → saas_software_script.md
  RAW_MATERIAL         → raw_material_script.md
  MANUFACTURING        → manufacturing_script.md
  PROFESSIONAL_SERVICES→ professional_services_script.md
  LOGISTICS_FREIGHT    → logistics_freight_script.md
  MRO_INDIRECT         → mro_indirect_script.md
  IT_HARDWARE          → it_hardware_script.md
  PACKAGING_CONSUMABLES→ packaging_consumables_script.md
"""

import os
from tool_registry import Tool


# ── Category → script file mapping ──
# Each key matches a supplier category enum value used in the qualification prompt.
# Each value is the filename under scripts/ containing the category-specific questions.
CATEGORY_SCRIPT_MAP = {
    "SAAS_SOFTWARE": "saas_software_script.md",
    "RAW_MATERIAL": "raw_material_script.md",
    "MANUFACTURING": "manufacturing_script.md",
    "PROFESSIONAL_SERVICES": "professional_services_script.md",
    "LOGISTICS_FREIGHT": "logistics_freight_script.md",
    "MRO_INDIRECT": "mro_indirect_script.md",
    "IT_HARDWARE": "it_hardware_script.md",
    "PACKAGING_CONSUMABLES": "packaging_consumables_script.md",
    "COST_INFLATION": "cost_inflation_script.md",
    "CAPACITY_CONSTRAINT": "capacity_constraint_script.md",
    "SUPPLY_CHAIN_DISRUPTION": "supply_chain_disruption_script.md",
    "SINGLE_SOURCE_DEPENDENCY": "single_source_dependency_script.md",
    "QUALITY_DEFECT_RESOLUTION": "quality_defect_resolution_script.md",
    "DEMAND_SURGE": "demand_surge_allocation_script.md",
}

VALID_CATEGORIES = list(CATEGORY_SCRIPT_MAP.keys())


class CategoryScriptTool(Tool):
    """Loads the qualification script for a specific supplier category."""

    @property
    def name(self) -> str:
        return "get_category_script"

    @property
    def description(self) -> str:
        return (
            "Load the qualification script for a specific supplier category. "
            "Call this ONCE when entering the Qualification stage to get "
            "category-specific questions. "
            f"Valid supplier_category values: {', '.join(VALID_CATEGORIES)}"
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "supplier_category": {
                    "type": "string",
                    "enum": VALID_CATEGORIES,
                    "description": "The confirmed supplier category or specific negotiation scenario (e.g. COST_INFLATION).",
                }
            },
            "required": ["supplier_category"],
        }

    def execute(self, arguments: dict) -> str:
        category = arguments.get("supplier_category", "").upper()

        # ── Validate category ──
        if category not in CATEGORY_SCRIPT_MAP:
            return (
                f"Error: Invalid supplier_category '{category}'. "
                f"Valid options: {', '.join(VALID_CATEGORIES)}"
            )

        # ── Load and return the script file ──
        script_file = CATEGORY_SCRIPT_MAP[category]
        script_path = os.path.join("scripts", script_file)

        try:
            with open(script_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: Script file not found at {script_path}"
        except Exception as e:
            return f"Error reading script: {str(e)}"
