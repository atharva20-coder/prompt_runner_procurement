"""Tool Registry - Abstract Tool class and registry for managing tools."""

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Abstract base class for tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description shown to the LLM."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict:
        """JSON Schema for tool parameters."""
        pass

    @abstractmethod
    def execute(self, arguments: dict) -> str:
        """Execute the tool with given arguments."""
        pass


class ToolRegistry:
    """Registry for managing and executing tools."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool by its name."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_tools_for_llm(self) -> list[dict[str, Any]]:
        """Convert registered tools to LLM-compatible format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in self._tools.values()
        ]

    def execute_tool(self, name: str, arguments: dict) -> str:
        """Execute a tool by name with given arguments."""
        from orchestrator import StageTransitionSignal

        tool = self._tools.get(name)
        if tool is None:
            return f"Error: Tool '{name}' not found"
        try:
            return tool.execute(arguments)
        except StageTransitionSignal:
            raise  # Let orchestrator handle stage transitions
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
