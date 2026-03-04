"""Orchestrator - Stage chaining engine for multi-stage conversations."""

import json
import logging

from agent import Agent
from chat_logger import ChatLogger
from config_loader import Config, load_customer_data, load_stages_config
from litellm_provider import LiteLLMProvider
from prompt_composer import PromptComposer
from tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


class StageTransitionSignal(Exception):
    """Raised by next-stage tools to signal a stage transition.

    In orchestrator mode, the orchestrator catches this to chain stages.
    In single-stage mode, main.py catches this and prints the handoff data.
    """

    def __init__(self, from_stage: str, next_stage: str, handoff_data: dict):
        self.from_stage = from_stage
        self.next_stage = next_stage
        self.handoff_data = handoff_data
        super().__init__(
            f"Stage transition: {from_stage} → {next_stage}"
        )


# Tool name to class mapping (same as main.py)
TOOL_CLASSES = {
    "get_delay_script": "DelayScriptTool",
    "investigation_next_stage": "InvestigationNextStageTool",
    "log_payment_commitment": "LogPaymentCommitmentTool",
    "recovery_next_stage": "RecoveryNextStageTool",
    "intro_next_stage": "IntroNextStageTool",
    "end_call": "EndCallTool",
}


class Orchestrator:
    """Chains stages together — Intro → Investigation → Recovery → Exit.

    Each stage gets a fresh Agent with its own system prompt, tools,
    and no conversation history from previous stages. Only the structured
    handoff_data passes between stages.
    """

    def __init__(self, config: Config, provider: LiteLLMProvider, chat_logger: ChatLogger | None = None):
        self.config = config
        self.provider = provider
        self.chat_logger = chat_logger
        self.stages = load_stages_config(config)
        self.customer_data = load_customer_data(config)
        self.composer = PromptComposer(
            config.tools.scripts_dir, self.customer_data
        )
        self.current_stage_name = config.orchestrator.start_stage

        # Pre-build tool registries for all stages
        self._registries: dict[str, ToolRegistry] = {}
        for name, stage_config in self.stages.items():
            self._registries[name] = self._build_registry(stage_config["tools"])

        # Pre-build agents with base prompts and warmup all stages
        self._agents: dict[str, Agent] = {}
        print(f"\n{GREEN}Preloading all stages...{RESET}")
        for name, stage_config in self.stages.items():
            base_prompt = self.composer.compose(
                stage_config["prompt"],
                modules=stage_config.get("modules"),
            )
            registry = self._registries[name]
            agent = Agent(
                provider=self.provider,
                tool_registry=registry,
                system_prompt=base_prompt,
                streaming=self.config.llm.streaming,
                prompt_caching=self.config.llm.prompt_caching,
                stage_name=name,
                chat_logger=self.chat_logger,
            )
            self._agents[name] = agent
            if self.config.llm.warmup:
                print(f"  Warming up {name}...", end=" ", flush=True)
                tools = registry.get_tools_for_llm()
                self.provider.warmup(base_prompt, tools=tools if tools else None, prompt_caching=self.config.llm.prompt_caching)
                print("done")
        if self.config.llm.warmup:
            print(f"{GREEN}All stages preloaded.{RESET}")

    def _build_registry(self, tool_names: list[str]) -> ToolRegistry:
        """Build a ToolRegistry with only the specified tools."""
        import tools as tools_module

        registry = ToolRegistry()
        for tool_name in tool_names:
            class_name = TOOL_CLASSES.get(tool_name)
            if not class_name:
                logger.warning(f"Unknown tool: {tool_name}")
                continue

            tool_class = getattr(tools_module, class_name, None)
            if tool_class:
                registry.register(tool_class())
                logger.debug(f"Registered tool: {tool_name}")
            else:
                logger.warning(f"Tool class not found: {class_name}")

        return registry

    def run(self):
        """Main orchestration loop.

        Reuses pre-built, warmed-up agents for each stage. Handoff data
        from the previous stage is sent as the first user message,
        preserving the cached system prompt.
        """
        handoff_data = None

        while self.current_stage_name:
            stage_config = self.stages.get(self.current_stage_name)
            if not stage_config:
                print(f"{RED}[ERROR] Stage '{self.current_stage_name}' not found in pipeline{RESET}")
                break

            # Reuse pre-built, warmed-up agent
            agent = self._agents[self.current_stage_name]
            agent.reset()

            print(f"\n{GREEN}{'=' * 50}")
            print(f"  STAGE: {self.current_stage_name.upper()}")
            print(f"  Tools: {stage_config['tools']}")
            print(f"{'=' * 50}{RESET}\n")

            try:
                # Handoff data IS the first message — no "Hello" or "Begin"
                print("\nAssistant: ", end="")
                if handoff_data:
                    context = json.dumps(handoff_data, indent=2)
                else:
                    # First stage: minimal trigger context
                    context = json.dumps({"stage": self.current_stage_name, "action": "begin"})
                agent.run(context)

                agent.run_interactive()
                # Normal exit — user typed 'quit'/'exit' or end_call tool ran
                print(f"\n{GREEN}[Session ended]{RESET}")
                break

            except StageTransitionSignal as signal:
                logger.info(
                    f"Stage transition: {signal.from_stage} → {signal.next_stage}"
                )

                # Dispute → print message and end session
                if signal.next_stage == "DISPUTE_HANDLER":
                    print(
                        f"\n{YELLOW}[DISPUTE DETECTED] "
                        f"Type: {signal.handoff_data.get('dispute', {}).get('type', 'Unknown')}. "
                        f"Session ending. Escalation required.{RESET}"
                    )
                    break

                # Look up the next stage name from transitions
                next_name = stage_config["transitions"].get(signal.next_stage)
                if not next_name:
                    print(
                        f"\n{RED}[ERROR] No transition defined for "
                        f"'{signal.next_stage}' from stage "
                        f"'{self.current_stage_name}'{RESET}"
                    )
                    break

                print(f"\n{YELLOW}{'=' * 50}")
                print(f"  TRANSITION: {signal.from_stage} → {next_name.upper()}")
                print(f"  Handoff: {signal.handoff_data}")
                print(f"{'=' * 50}{RESET}")

                handoff_data = signal.handoff_data
                self.current_stage_name = next_name

                # Log stage transition
                if self.chat_logger:
                    self.chat_logger.log_stage_transition(signal.from_stage, next_name)

            except KeyboardInterrupt:
                print(f"\n{YELLOW}[Interrupted]{RESET}")
                break

        # Save chat log at end of session
        if self.chat_logger:
            path = self.chat_logger.save()
            if path:
                print(f"\n\033[92m[Chat log saved to {path}]\033[0m")
