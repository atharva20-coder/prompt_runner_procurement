"""Agent - Multi-turn conversation orchestrator with tool support."""

import json
import logging
from typing import Any

from chat_logger import ChatLogger
from litellm_provider import LiteLLMProvider
from tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

# ANSI color codes
PINK = "\033[95m"
BLUE = "\033[94m"
GREY = "\033[90m"
RESET = "\033[0m"


class Agent:
    """Multi-turn conversation agent with tool calling support."""

    def __init__(
        self,
        provider: LiteLLMProvider,
        tool_registry: ToolRegistry,
        system_prompt: str | None = None,
        max_turns: int = 10,
        streaming: bool = True,
        prompt_caching: bool = False,
        stage_name: str | None = None,
        chat_logger: ChatLogger | None = None,
    ):
        self.provider = provider
        self.tool_registry = tool_registry
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self.streaming = streaming
        self.prompt_caching = prompt_caching
        self.stage_name = stage_name
        self.chat_logger = chat_logger
        self.messages: list[dict[str, Any]] = []

        # Initialize with system prompt
        if system_prompt:
            self.messages.append(self._build_system_message(system_prompt))

    def _build_system_message(self, prompt: str) -> dict[str, Any]:
        """Build system message, optionally with cache_control."""
        if self.prompt_caching:
            return {"role": "system", "content": [
                {
                    "type": "text",
                    "text": prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ]}
        return {"role": "system", "content": prompt}

    def _get_tools(self) -> list[dict[str, Any]] | None:
        """Get tools for LLM if any are registered."""
        tools = self.tool_registry.get_tools_for_llm()
        return tools if tools else None

    def _process_tool_calls(self, tool_calls) -> list[dict[str, Any]]:
        """Execute tool calls and return tool response messages.

        Note: StageTransitionSignal from next-stage tools is allowed to
        propagate up — the orchestrator (or main.py) catches it.
        """
        if not tool_calls:
            return []

        tool_messages = []
        for tool_call in tool_calls:
            func = tool_call.function
            name = func.name
            # Parse arguments - may be string or dict
            args = func.arguments
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}

            # Print tool call with arguments (pink)
            print(f"\n{PINK}[Tool Call: {name}]")
            print(f"  Arguments: {args}")
            logger.info(f"Executing tool: {name}")
            result = self.tool_registry.execute_tool(name, args)
            # Print tool output (truncated)
            truncated = result[:100] + "..." if len(result) > 100 else result
            print(f"  Result: {truncated}{RESET}")
            logger.debug(f"Tool result: {result}")

            tool_messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id,
                "name": name,
            })

        return tool_messages

    def _add_assistant_message(self, response) -> None:
        """Add assistant response to message history."""
        # For streaming, we build the message manually
        if isinstance(response, dict):
            self.messages.append(response)
            return

        # For non-streaming, extract from ModelResponse
        message = response.choices[0].message
        msg: dict[str, Any] = {
            "role": "assistant",
            "content": message.content or "",
        }
        if message.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]
        self.messages.append(msg)

    @staticmethod
    def _parse_and_print_response(content: str, ttft_ms: int | None = None, cached_token_count: int | None = None) -> None:
        """Parse structured JSON response and print state (grey) + agent (blue)."""
        prefix = ""
        if ttft_ms is not None:
            prefix = f"(TTFT: {ttft_ms}ms) "
        suffix = ""
        if cached_token_count:
            suffix = f" {PINK}(cached: {cached_token_count} tokens){RESET}"

        try:
            # Strip markdown code fences if LLM wrapped the JSON
            clean = content.strip()
            if clean.startswith("```"):
                # Remove opening fence (```json or ```)
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
                # Remove closing fence
                if clean.rstrip().endswith("```"):
                    clean = clean.rstrip()[:-3].rstrip()
            data = json.loads(clean)
            state = data.get("state")
            agent_text = data.get("agent", "")

            if state is not None:
                state_json = json.dumps(state, indent=2, ensure_ascii=False)
                print(f"{prefix}{GREY}{state_json}{RESET}")
                print(f"{BLUE}{agent_text}{RESET}{suffix}")
            else:
                # Valid JSON but no 'state' key — print raw
                print(f"{prefix}{BLUE}{content}{RESET}{suffix}")
        except (json.JSONDecodeError, TypeError):
            # Not JSON — fallback to raw output
            print(f"{prefix}{BLUE}{content}{RESET}{suffix}")

    def _prepare_messages(self) -> list[dict[str, Any]]:
        """Filter conversation history for LLM.
        
        Send full content (with state) only for the last assistant message.
        For older assistant messages, send only the 'agent' text to keep
        the context window lean and minimize uncached input tokens (TTFT).
        """
        prepared = []
        
        # Find the index of the last assistant message only
        last_assistant_idx = -1
        for i in range(len(self.messages) - 1, -1, -1):
            if self.messages[i].get("role") == "assistant":
                last_assistant_idx = i
                break
                
        for i, msg in enumerate(self.messages):
            if msg.get("role") == "assistant" and i != last_assistant_idx:
                content = msg.get("content", "")
                if content:
                    try:
                        clean = content.strip()
                        if clean.startswith("```"):
                            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
                            if clean.rstrip().endswith("```"):
                                clean = clean.rstrip()[:-3].rstrip()
                        data = json.loads(clean)
                        if isinstance(data, dict) and "agent" in data:
                            new_msg = dict(msg)
                            new_msg["content"] = data["agent"]
                            prepared.append(new_msg)
                            continue
                    except (json.JSONDecodeError, TypeError):
                        pass
            prepared.append(msg)
            
        return prepared

    def _run_turn(self, print_stream: bool = True):
        """Run a single conversation turn."""
        import time

        tools = self._get_tools()
        messages_to_send = self._prepare_messages()

        if self.streaming:
            # Stream response — accumulate silently, then parse and display
            full_content = ""
            tool_calls_list = []
            first_token_time = None
            cached_token_count = None
            start_time = time.perf_counter()
            ttft_ms = None

            for chunk in self.provider.chat_stream(messages_to_send, tools):
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                        ttft_ms = int((first_token_time - start_time) * 1000)
                    full_content += delta.content

                # Accumulate tool calls from deltas
                if delta and delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index if hasattr(tc_delta, 'index') and tc_delta.index is not None else 0
                        # Extend list if needed
                        while len(tool_calls_list) <= idx:
                            tool_calls_list.append({
                                "id": "",
                                "type": "function",
                                "function": {"name": "", "arguments": ""},
                            })
                        if tc_delta.id:
                            tool_calls_list[idx]["id"] = tc_delta.id
                        if tc_delta.function:
                            if tc_delta.function.name:
                                tool_calls_list[idx]["function"]["name"] += tc_delta.function.name
                            if tc_delta.function.arguments:
                                tool_calls_list[idx]["function"]["arguments"] += tc_delta.function.arguments

                # Extract cache info from usage in the last chunk
                if hasattr(chunk, "usage") and chunk.usage:
                    usage = chunk.usage
                    if hasattr(usage, "prompt_tokens_details") and usage.prompt_tokens_details:
                        cached_token_count = getattr(usage.prompt_tokens_details, "cached_tokens", None)

            if print_stream and full_content:
                self._parse_and_print_response(full_content, ttft_ms, cached_token_count)

            # Build the assistant message dict for history
            assistant_msg: dict[str, Any] = {
                "role": "assistant",
                "content": full_content if full_content else "",
            }

            # Convert accumulated tool calls to proper format
            parsed_tool_calls = None
            if tool_calls_list and any(tc["function"]["name"] for tc in tool_calls_list):
                assistant_msg["tool_calls"] = tool_calls_list
                # Parse into objects for _process_tool_calls
                from types import SimpleNamespace
                parsed_tool_calls = []
                for tc in tool_calls_list:
                    parsed_tool_calls.append(SimpleNamespace(
                        id=tc["id"],
                        function=SimpleNamespace(
                            name=tc["function"]["name"],
                            arguments=tc["function"]["arguments"],
                        ),
                    ))

            return assistant_msg, parsed_tool_calls, cached_token_count
        else:
            # Blocking response
            start_time = time.perf_counter()
            response = self.provider.chat(messages_to_send, tools)
            ttft_ms = int((time.perf_counter() - start_time) * 1000)

            message = response.choices[0].message
            content = message.content or ""
            cached_token_count = None
            if hasattr(response, "usage") and response.usage:
                if hasattr(response.usage, "prompt_tokens_details") and response.usage.prompt_tokens_details:
                    cached_token_count = getattr(response.usage.prompt_tokens_details, "cached_tokens", None)

            if content and print_stream:
                self._parse_and_print_response(content, ttft_ms, cached_token_count)

            tool_calls = message.tool_calls if message.tool_calls else None
            assistant_msg: dict[str, Any] = {
                "role": "assistant",
                "content": content,
            }
            if tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ]

            return assistant_msg, tool_calls, cached_token_count

    def run(self, prompt: str) -> str:
        """Run a single prompt through the agent.

        Returns the final assistant response.
        """
        self.messages.append({"role": "user", "content": prompt})

        json_nudge_sent = False  # Guard: only nudge once per user turn

        for turn in range(self.max_turns):
            logger.debug(f"Turn {turn + 1}/{self.max_turns}")

            assistant_msg, tool_calls, _ = self._run_turn()
            self.messages.append(assistant_msg)

            # Check for tool calls
            if tool_calls:
                tool_messages = self._process_tool_calls(tool_calls)
                self.messages.extend(tool_messages)
                # Continue loop to get LLM response to tool results
                continue

            # Safety net: Gemini sometimes outputs exit_criteria_matched: true
            # without making the tool call, despite prompt instructions.
            # Detect this and give the model one more turn to call the tool.
            content = assistant_msg.get("content", "")
            if '"exit_criteria_matched": true' in content or '"exit_criteria_matched":true' in content:
                logger.warning("exit_criteria_matched is true but no tool call — nudging LLM")
                self.messages.append({
                    "role": "user",
                    "content": (
                        "[SYSTEM] You set exit_criteria_matched to true but did not call the transition tool. "
                        "You MUST call the stage transition tool NOW with the complete stage info."
                    ),
                })
                continue

            # Safety net: If recovery stage produces plain text without JSON state,
            # nudge the model ONCE to re-respond with proper format.
            if self.stage_name == "recovery" and content and not json_nudge_sent:
                clean = content.strip()
                if clean.startswith("```"):
                    clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
                    if clean.rstrip().endswith("```"):
                        clean = clean.rstrip()[:-3].rstrip()
                try:
                    parsed = json.loads(clean)
                    has_state = isinstance(parsed, dict) and "state" in parsed
                except (json.JSONDecodeError, TypeError):
                    has_state = False

                if not has_state:
                    logger.warning("Recovery response missing JSON state — nudging LLM (once)")
                    json_nudge_sent = True
                    self.messages.append({
                        "role": "user",
                        "content": (
                            "[SYSTEM] Your response was missing the required JSON format. "
                            'You MUST respond with: {"state": <full CONVERSATION_CONTEXT_REGISTER>, "agent": "your words"}. '
                            "Restate your last response in this exact JSON format NOW. Include ALL register fields."
                        ),
                    })
                    continue

            # No tool calls - return the response
            return content

        logger.warning("Max turns reached")
        last = self.messages[-1] if self.messages else {}
        return last.get("content", "")

    def run_interactive(self) -> None:
        """Run an interactive REPL session."""
        import select
        import sys

        print("Starting interactive session. Type 'quit' or 'exit' to end.")
        print('For multi-line input, start with """ and end with """')
        print("-" * 50)

        while True:
            try:
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit"):
                    print("Goodbye!")
                    break

                # Multi-line input mode
                if user_input.startswith('"""'):
                    lines = [user_input[3:]]  # Content after opening """
                    print('(paste your content, end with """ on a new line)')
                    
                    while True:
                        # Check if there's already input waiting (pasted content)
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            line = sys.stdin.readline().rstrip('\n')
                        else:
                            line = input("... ")
                        
                        if line.strip() == '"""':
                            break
                        lines.append(line)
                    
                    user_input = "\n".join(lines).strip()

                # Log user input
                if self.chat_logger:
                    self.chat_logger.log_user(user_input)

                print("\nAssistant: ", end="")
                response = self.run(user_input)

                # Log bot response
                if self.chat_logger and response:
                    self.chat_logger.log_bot(response)

            except KeyboardInterrupt:
                print("\nInterrupted. Goodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break

        # Save chat log on session exit
        if self.chat_logger:
            path = self.chat_logger.save()
            if path:
                print(f"\n\033[92m[Chat log saved to {path}]\033[0m")

    def reset(self) -> None:
        """Reset conversation history."""
        self.messages = []
        if self.system_prompt:
            self.messages.append(self._build_system_message(self.system_prompt))
