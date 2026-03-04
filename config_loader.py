"""Config Loader - YAML configuration with Pydantic validation."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    model_config = {"populate_by_name": True}

    # LiteLLM model string with provider prefix, e.g. "gemini/gemini-2.5-flash"
    model: str = "gemini/gemini-2.5-flash"
    api_key: str | None = None
    api_base: str | None = None  # For Ollama or custom endpoints
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    streaming: bool = True
    warmup: bool = True           # Pre-warm model before first turn
    prompt_caching: bool = False  # Enable prompt caching (cache_control on system prompt)
    reasoning_effort: str | None = None  # "none", "low", "medium", "high"
    extra_params: dict | None = None  # Extra provider-specific params


class ToolsConfig(BaseModel):
    """Tools configuration."""

    scripts_dir: str = "./scripts"
    system_prompt: str | None = None
    enabled: list[str] = Field(default_factory=list)


# ── Pipeline presets: maps pipeline name → (stages file, data file, start stage) ──
# This avoids hardcoding paths — just set `pipeline: procurement` in config.yaml.
PIPELINE_PRESETS = {
    "recovery": {
        "stages": "./stages.yaml",
        "customer_data": "./customer_data.yaml",
        "start_stage": "intro",
    },
    "procurement": {
        "stages": "./procurement_stages.yaml",
        "customer_data": "./supplier_data.yaml",
        "start_stage": "discovery",
    },
}


class OrchestratorConfig(BaseModel):
    """Orchestrator configuration for chained stage mode.

    The `pipeline` field selects which preset to use (recovery or procurement).
    Individual fields (stages, customer_data, start_stage) can still be
    overridden explicitly in config.yaml if needed.
    """

    enabled: bool = False
    pipeline: str = "recovery"  # "recovery" or "procurement" — selects preset defaults
    customer_data: str | None = None  # Override preset if needed
    stages: str | None = None         # Override preset if needed
    start_stage: str | None = None    # Override preset if needed


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


class Config(BaseModel):
    """Root configuration."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    orchestrator: OrchestratorConfig = Field(default_factory=OrchestratorConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(path: str | Path = "config.yaml") -> Config:
    """Load configuration from YAML file."""
    path = Path(path)
    if not path.exists():
        # Return default config if file doesn't exist
        return Config()

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return Config(**data)


def load_system_prompt(config: Config) -> str | None:
    """Load the system prompt from file if configured."""
    if not config.tools.system_prompt:
        return None

    prompt_path = Path(config.tools.scripts_dir) / config.tools.system_prompt
    if not prompt_path.exists():
        return None

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def _resolve_preset(config: Config) -> dict:
    """Resolve pipeline preset defaults, allowing explicit overrides.

    If config.yaml specifies `pipeline: procurement`, the preset provides
    default values for stages, customer_data, and start_stage. Any
    explicitly set field in config.yaml takes precedence over the preset.
    """
    orch = config.orchestrator
    preset = PIPELINE_PRESETS.get(orch.pipeline, PIPELINE_PRESETS["recovery"])
    return {
        "stages": orch.stages or preset["stages"],
        "customer_data": orch.customer_data or preset["customer_data"],
        "start_stage": orch.start_stage or preset["start_stage"],
    }


def load_customer_data(config: Config) -> dict:
    """Load customer/supplier data from YAML file and flatten into a single dict.

    Nested sections (customer, loan, supplier, contract, etc.) are flattened
    so that {customer_name}, {supplier_name}, {annual_spend} etc. work directly
    as template placeholders.

    The file path is resolved from the pipeline preset (recovery → customer_data.yaml,
    procurement → supplier_data.yaml) unless explicitly overridden in config.yaml.
    """
    resolved = _resolve_preset(config)
    path = Path(resolved["customer_data"])
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    # Flatten nested sections into a single dict
    flat = {}
    for section_key, section_val in raw.items():
        if isinstance(section_val, dict):
            flat.update(section_val)
        else:
            flat[section_key] = section_val

    return flat


def load_stages_config(config: Config) -> dict:
    """Load stages pipeline from YAML file.

    The file path is resolved from the pipeline preset (recovery → stages.yaml,
    procurement → procurement_stages.yaml) unless explicitly overridden.

    Returns a dict keyed by stage name, e.g.:
    {
        "discovery": {"prompt": "Intro_stage_prompt.md", "tools": [...], "transitions": {...}},
        ...
    }
    """
    resolved = _resolve_preset(config)
    path = Path(resolved["stages"])
    if not path.exists():
        raise FileNotFoundError(f"Stages config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    pipeline = raw.get("pipeline", [])
    stages = {}
    for stage in pipeline:
        name = stage["name"]
        stages[name] = {
            "prompt": stage["prompt"],
            "modules": stage.get("modules"),
            "tools": stage.get("tools", []),
            "transitions": stage.get("transitions") or {},
        }

    return stages
