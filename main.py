"""Main - CLI entry point for the prompt runner."""

import argparse
import logging
import sys

from agent import Agent
from chat_logger import ChatLogger
from config_loader import Config, load_config, load_system_prompt
from litellm_provider import LiteLLMProvider
from tool_registry import ToolRegistry

# Tool name → class mapping.
# Both recovery and procurement tools live here so register_tools()
# can build a registry for any stage in either pipeline.
TOOL_CLASSES = {
    # ── Recovery Pipeline Tools ──
    "get_delay_script": "DelayScriptTool",
    "investigation_next_stage": "InvestigationNextStageTool",
    "log_payment_commitment": "LogPaymentCommitmentTool",
    "recovery_next_stage": "RecoveryNextStageTool",
    "intro_next_stage": "IntroNextStageTool",
    "end_call": "EndCallTool",
    # ── Procurement Pipeline Tools ──
    # Discovery → Qualification → Negotiation → Exit
    "discovery_next_stage": "DiscoveryNextStageTool",
    "get_category_script": "CategoryScriptTool",
    "qualification_next_stage": "QualificationNextStageTool",
    "procurement_next_stage": "ProcurementNextStageTool",
    "log_negotiation_position": "LogPaymentCommitmentTool",  # reuse for position tracking
    "end_negotiation": "EndNegotiationTool",
}


def create_provider(config: Config) -> LiteLLMProvider:
    """Create LiteLLM provider based on config."""
    return LiteLLMProvider(
        model=config.llm.model,
        api_key=config.llm.api_key,
        api_base=config.llm.api_base,
        temperature=config.llm.temperature,
        reasoning_effort=config.llm.reasoning_effort,
        extra_params=config.llm.extra_params,
    )


def register_tools(config: Config) -> ToolRegistry:
    """Register enabled tools from config."""
    import tools

    registry = ToolRegistry()

    for tool_name in config.tools.enabled:
        class_name = TOOL_CLASSES.get(tool_name)
        if not class_name:
            logging.warning(f"Unknown tool: {tool_name}")
            continue

        tool_class = getattr(tools, class_name, None)
        if tool_class:
            registry.register(tool_class())
            logging.debug(f"Registered tool: {tool_name}")
        else:
            logging.warning(f"Tool class not found: {class_name}")

    return registry


def setup_logging(config: Config) -> None:
    """Configure logging based on config."""
    level = getattr(logging, config.logging.level, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Suppress httpx INFO logs (from litellm/ollama client)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    # Suppress litellm's own info logs
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)


def run_orchestrator_mode(config: Config, provider: LiteLLMProvider) -> None:
    """Run in orchestrator mode — chained stages."""
    from orchestrator import Orchestrator

    chat_logger = ChatLogger(stage_name="orchestrator")
    orch = Orchestrator(config, provider, chat_logger=chat_logger)
    orch.run()


def run_single_stage_mode(config: Config, provider: LiteLLMProvider) -> None:
    """Run in single-stage testing mode — existing behavior.

    Uses PromptComposer to inject customer data + date/time into the prompt
    if customer_data.yaml exists, otherwise falls back to raw prompt.
    """
    from orchestrator import StageTransitionSignal
    from prompt_composer import PromptComposer

    registry = register_tools(config)

    # Try to compose prompt with customer data (if available)
    system_prompt = None
    if config.tools.system_prompt:
        try:
            from config_loader import load_customer_data
            customer_data = load_customer_data(config)
            composer = PromptComposer(config.tools.scripts_dir, customer_data)
            system_prompt = composer.compose(config.tools.system_prompt)
        except FileNotFoundError:
            # No customer_data.yaml — fall back to raw prompt
            system_prompt = load_system_prompt(config)

    chat_logger = ChatLogger(stage_name=config.tools.system_prompt)

    agent = Agent(
        provider=provider,
        tool_registry=registry,
        system_prompt=system_prompt,
        streaming=config.llm.streaming,
        prompt_caching=config.llm.prompt_caching,
        chat_logger=chat_logger,
    )

    # Warmup: pre-send system prompt to cache it
    if system_prompt and config.llm.warmup:
        print("Warming up model...", end=" ", flush=True)
        tools = registry.get_tools_for_llm()
        provider.warmup(system_prompt, tools=tools if tools else None, prompt_caching=config.llm.prompt_caching)
        print("done")

    try:
        agent.run_interactive()
    except StageTransitionSignal as signal:
        print(f"\n\033[93m[Stage transition signal] → {signal.next_stage}")
        print(f"  From: {signal.from_stage}")
        print(f"  Handoff data: {signal.handoff_data}\033[0m")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Prompt Runner with Tools")
    parser.add_argument(
        "--prompt",
        "-p",
        type=str,
        help="Single prompt to run (non-interactive mode)",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    setup_logging(config)

    # Create provider
    provider = create_provider(config)

    try:
        # Check mode
        if config.orchestrator and config.orchestrator.enabled:
            # Orchestrator mode — chained stages
            if args.prompt:
                print("Error: --prompt flag not supported in orchestrator mode.")
                sys.exit(1)
            run_orchestrator_mode(config, provider)
        else:
            # Single-stage testing mode
            if args.prompt:
                # Single prompt mode
                registry = register_tools(config)
                system_prompt = load_system_prompt(config)
                agent = Agent(
                    provider=provider,
                    tool_registry=registry,
                    system_prompt=system_prompt,
                    streaming=config.llm.streaming,
                    prompt_caching=config.llm.prompt_caching,
                )
                if system_prompt and config.llm.warmup:
                    print("Warming up model...", end=" ", flush=True)
                    tools = registry.get_tools_for_llm()
                    provider.warmup(system_prompt, tools=tools if tools else None, prompt_caching=config.llm.prompt_caching)
                    print("done")
                print("Assistant: ", end="")
                agent.run(args.prompt)
            else:
                run_single_stage_mode(config, provider)
    except KeyboardInterrupt:
        print("\n\033[93mInterrupted. Goodbye!\033[0m")
    except EOFError:
        print("\n\033[93m[Session ended]\033[0m")
    finally:
        provider.cleanup()


if __name__ == "__main__":
    main()
