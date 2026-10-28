"""Base Agent class for all specialized agents in the system."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from anthropic import Anthropic

from src.utils.logger import get_logger

logger = get_logger(__name__)


class Tool:
    """Tool definition for Claude function calling."""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: callable,
    ):
        """
        Initialize a tool definition.

        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON schema for tool inputs
            handler: Function to handle tool calls
        """
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler

    def to_claude_format(self) -> Dict[str, Any]:
        """Convert tool to Claude API format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.input_schema.get("properties", {}),
                "required": self.input_schema.get("required", []),
            },
        }


class BaseAgent(ABC):
    """Base class for all specialized agents."""

    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        tools: Optional[List[Tool]] = None,
    ):
        """
        Initialize base agent.

        Args:
            agent_name: Name of the agent
            system_prompt: System prompt for Claude
            tools: List of Tool objects available to agent
        """
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.client = Anthropic()
        self.logger = get_logger(f"agents.{agent_name}")

    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the agent."""
        self.tools.append(tool)
        self.logger.debug(f"Tool registered: {tool.name}")

    def _build_tools_for_claude(self) -> List[Dict[str, Any]]:
        """Build tools in Claude API format."""
        return [tool.to_claude_format() for tool in self.tools]

    def _process_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        Process a tool call from Claude.

        Args:
            tool_name: Name of the tool to call
            tool_input: Input arguments for the tool

        Returns:
            Tool execution result
        """
        for tool in self.tools:
            if tool.name == tool_name:
                self.logger.debug(f"Executing tool: {tool_name} with input: {tool_input}")
                try:
                    result = tool.handler(**tool_input)
                    self.logger.debug(f"Tool {tool_name} result: {result}")
                    return result
                except Exception as e:
                    self.logger.error(f"Tool {tool_name} failed: {e}", exc_info=True)
                    return {"error": str(e)}

        self.logger.error(f"Tool {tool_name} not found")
        return {"error": f"Tool {tool_name} not found"}

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with given input data.

        This method implements agentic loop with Claude:
        1. Send user message with available tools
        2. Claude responds with potential tool calls
        3. Execute tool calls and return results
        4. Continue until Claude returns final message

        Args:
            input_data: Input data for agent processing

        Returns:
            Agent output/result
        """
        self.logger.info(f"Agent {self.agent_name} starting execution")

        messages = [
            {
                "role": "user",
                "content": self._format_input_for_claude(input_data),
            }
        ]

        # Agentic loop
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            self.logger.debug(f"Agent loop iteration {iteration}")

            # Call Claude
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=self.system_prompt,
                tools=self._build_tools_for_claude() if self.tools else None,
                messages=messages,
            )

            # Check stop reason
            if response.stop_reason == "end_turn":
                self.logger.debug(f"Agent {self.agent_name} completed after {iteration} iterations")
                return self._extract_final_response(response, messages, input_data)

            if response.stop_reason == "tool_use":
                # Process tool calls
                tool_results = []
                assistant_message = {"role": "assistant", "content": response.content}
                messages.append(assistant_message)

                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_result = self._process_tool_call(
                            content_block.name,
                            content_block.input,
                        )
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": content_block.id,
                                "content": str(tool_result),
                            }
                        )

                # Add tool results to messages
                messages.append({"role": "user", "content": tool_results})
                continue

            # Other stop reasons
            self.logger.warning(f"Unexpected stop reason: {response.stop_reason}")
            break

        self.logger.error(f"Agent {self.agent_name} exceeded max iterations ({max_iterations})")
        return {"error": "Max iterations exceeded"}

    def _format_input_for_claude(self, input_data: Dict[str, Any]) -> str:
        """
        Format input data into a prompt for Claude.

        Override this method in subclasses for custom formatting.

        Args:
            input_data: Raw input data

        Returns:
            Formatted prompt string
        """
        return f"Process the following data:\n{input_data}"

    def _extract_final_response(
        self,
        response: Any,
        messages: List[Dict[str, Any]],
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract final response from Claude.

        Override this method in subclasses for custom response extraction.

        Args:
            response: Claude API response
            messages: Conversation history
            input_data: Original input data

        Returns:
            Extracted result
        """
        text_content = ""
        for content_block in response.content:
            if hasattr(content_block, "text"):
                text_content += content_block.text

        return {
            "success": True,
            "response": text_content,
            "iterations": len(messages) // 2,
        }

    @abstractmethod
    def validate_output(self, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate agent output format and content.

        Must be implemented by subclasses.

        Args:
            output: Agent output to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass
