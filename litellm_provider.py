"""LiteLLM Provider - Unified LLM provider using LiteLLM."""

import logging
from typing import Any, Generator

import litellm
from litellm import ModelResponse

logger = logging.getLogger(__name__)


class LiteLLMProvider:
    """Unified LLM provider using LiteLLM.

    Replaces the custom GeminiProvider and OllamaProvider with a single
    provider that routes to any LLM via LiteLLM's model prefix convention
    (e.g. "gemini/gemini-2.5-flash", "ollama/llama3.1").
    """

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        api_base: str | None = None,
        temperature: float = 0.2,
        reasoning_effort: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.temperature = temperature
        self.reasoning_effort = reasoning_effort
        self.extra_params = extra_params or {}

        # Suppress litellm's verbose logging
        litellm.suppress_debug_info = True

    def _build_kwargs(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Build kwargs for litellm.completion()."""
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": stream,
        }

        if stream:
            kwargs["stream_options"] = {"include_usage": True}

        if self.api_key:
            kwargs["api_key"] = self.api_key
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if tools:
            kwargs["tools"] = tools
        if self.model.startswith("ollama"):
            # Always disable thinking tokens for Ollama models (e.g. Qwen3)
            kwargs["extra_body"] = {"think": False}
        if self.reasoning_effort:
            kwargs["reasoning_effort"] = self.reasoning_effort

        # Merge any extra provider-specific params
        kwargs.update(self.extra_params)

        return kwargs

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ModelResponse:
        """Send messages and get a response (blocking)."""
        kwargs = self._build_kwargs(messages, tools, stream=False)
        return litellm.completion(**kwargs)

    def chat_stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Generator:
        """Send messages and stream responses."""
        kwargs = self._build_kwargs(messages, tools, stream=True)
        return litellm.completion(**kwargs)

    def warmup(
        self,
        system_prompt: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        prompt_caching: bool = False,
    ) -> None:
        """Pre-load model and/or trigger cache creation.

        For Gemini: if prompt_caching is True, system_prompt gets cache_control.
        For Ollama: loads the model into memory.
        """
        if not system_prompt:
            return

        if prompt_caching:
            system_content: Any = [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ]
        else:
            system_content = system_prompt

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": "Hello"},
        ]

        try:
            kwargs = self._build_kwargs(messages, tools, stream=False)
            # Set max_tokens low to minimize cost/latency for warmup
            kwargs["max_tokens"] = 5
            litellm.completion(**kwargs)
        except Exception as e:
            logger.warning(f"Warmup failed (non-fatal): {e}")

    def cleanup(self) -> None:
        """Clean up resources. LiteLLM uses TTL-based cache expiration."""
        pass
