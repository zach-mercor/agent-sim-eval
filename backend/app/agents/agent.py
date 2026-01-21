from enum import Enum
from typing import List, Dict, Optional, AsyncIterator
from datetime import datetime

from app.models import AgentConfig, Message, MessageRole
from app.services import LLMService
from app.mcp import MCPProtocol, MCPMessage


class AgentRole(str, Enum):
    CANDIDATE = "candidate"
    SIM = "sim"


class Agent:
    """
    Represents a single agent (either candidate or sim) in the simulation.
    Maintains its own conversation history, reasoning traces, and can communicate via MCP.
    """

    def __init__(
        self,
        role: AgentRole,
        config: AgentConfig,
        llm_service: LLMService
    ):
        self.role = role
        self.config = config
        self.llm_service = llm_service

        # Conversation history (visible to this agent)
        self.conversation_history: List[Dict[str, str]] = []

        # Reasoning traces (internal to this agent)
        self.reasoning_traces: List[str] = []

        # MCP protocol handler
        self.mcp = MCPProtocol()

    def _build_system_prompt(self) -> str:
        """Build the complete system prompt including MCP instructions"""
        base_prompt = f"""{self.config.system_prompt}

YOUR OBJECTIVE:
{self.config.objective}

COMMUNICATION PROTOCOL:
You are communicating with another agent via the Model Context Protocol (MCP).
Your messages will be delivered to the other agent, and their messages will be delivered to you.
"""

        if self.role == AgentRole.CANDIDATE:
            base_prompt += """
VERIFICATION:
When you believe you have completed your objective and gathered the necessary information,
you can signal that you're ready for verification by including the phrase:
"REQUEST_VERIFICATION" in your response, followed by your final answer/conclusion.
"""

        return base_prompt

    def add_message_to_history(self, role: str, content: str):
        """Add a message to this agent's conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def add_reasoning_trace(self, reasoning: str):
        """Add a reasoning trace (internal thinking)"""
        if reasoning:
            self.reasoning_traces.append(reasoning)

    async def generate_response(self, incoming_message: Optional[str] = None) -> tuple[str, Optional[str], bool]:
        """
        Generate a response from this agent.

        Args:
            incoming_message: Message from the other agent (if any)

        Returns:
            (content, reasoning, should_verify) tuple
            - content: The agent's response
            - reasoning: Internal reasoning/thinking
            - should_verify: Whether the candidate agent wants to verify (candidate only)
        """
        # Add incoming message to history if present
        if incoming_message:
            # Format as MCP message for context
            mcp_msg = self.mcp.create_request(incoming_message)
            formatted_msg = self.mcp.format_for_llm(mcp_msg)
            self.add_message_to_history("user", formatted_msg)
        elif len(self.conversation_history) == 0:
            # First turn with no incoming message - add a start prompt
            self.add_message_to_history("user", "Begin working on your objective. You may start the conversation.")

        # Generate response from LLM
        system_prompt = self._build_system_prompt()
        content, reasoning = await self.llm_service.generate_response(
            model=self.config.model,
            system_prompt=system_prompt,
            messages=self.conversation_history,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Add response to history
        self.add_message_to_history("assistant", content)

        # Add reasoning trace
        if reasoning:
            self.add_reasoning_trace(reasoning)

        # Check if candidate wants verification
        should_verify = False
        if self.role == AgentRole.CANDIDATE and "REQUEST_VERIFICATION" in content:
            should_verify = True

        return content, reasoning, should_verify

    async def generate_response_stream(
        self,
        incoming_message: Optional[str] = None
    ) -> AsyncIterator[Dict[str, any]]:
        """
        Generate a streaming response from this agent.

        Yields:
            {"type": "content"|"reasoning", "delta": str, "should_verify": bool}
        """
        # Add incoming message to history if present
        if incoming_message:
            mcp_msg = self.mcp.create_request(incoming_message)
            formatted_msg = self.mcp.format_for_llm(mcp_msg)
            self.add_message_to_history("user", formatted_msg)
        elif len(self.conversation_history) == 0:
            # First turn with no incoming message - add a start prompt
            self.add_message_to_history("user", "Begin working on your objective. You may start the conversation.")

        # Generate streaming response from LLM
        system_prompt = self._build_system_prompt()

        content_buffer = ""
        reasoning_buffer = ""

        async for chunk in self.llm_service.generate_response_stream(
            model=self.config.model,
            system_prompt=system_prompt,
            messages=self.conversation_history,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        ):
            chunk_type = chunk["type"]
            delta = chunk["delta"]

            if chunk_type == "content":
                content_buffer += delta
            elif chunk_type == "reasoning":
                reasoning_buffer += delta

            # Check for verification request in real-time
            should_verify = False
            if self.role == AgentRole.CANDIDATE and "REQUEST_VERIFICATION" in content_buffer:
                should_verify = True

            yield {
                "type": chunk_type,
                "delta": delta,
                "should_verify": should_verify
            }

        # Add complete response to history
        self.add_message_to_history("assistant", content_buffer)
        if reasoning_buffer:
            self.add_reasoning_trace(reasoning_buffer)

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get this agent's conversation history"""
        return self.conversation_history.copy()

    def get_reasoning_traces(self) -> List[str]:
        """Get this agent's reasoning traces"""
        return self.reasoning_traces.copy()

    def reset(self):
        """Reset agent state"""
        self.conversation_history.clear()
        self.reasoning_traces.clear()
