from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json


class MCPMessageType(str, Enum):
    """Types of MCP messages"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MCPMessage(BaseModel):
    """
    Model Context Protocol message format.
    This defines the structure for agent-to-agent communication.
    """
    type: MCPMessageType
    content: str
    metadata: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None  # For matching requests to responses

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
            "request_id": self.request_id
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPMessage":
        """Create from dictionary"""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "MCPMessage":
        """Create from JSON string"""
        return cls.from_dict(json.loads(json_str))


class MCPProtocol:
    """
    Handler for MCP protocol operations.
    Manages the communication protocol between agents.
    """

    @staticmethod
    def create_request(content: str, metadata: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None) -> MCPMessage:
        """Create a request message"""
        return MCPMessage(
            type=MCPMessageType.REQUEST,
            content=content,
            metadata=metadata,
            request_id=request_id
        )

    @staticmethod
    def create_response(content: str, request_id: str, metadata: Optional[Dict[str, Any]] = None) -> MCPMessage:
        """Create a response message"""
        return MCPMessage(
            type=MCPMessageType.RESPONSE,
            content=content,
            metadata=metadata,
            request_id=request_id
        )

    @staticmethod
    def create_notification(content: str, metadata: Optional[Dict[str, Any]] = None) -> MCPMessage:
        """Create a notification message (doesn't expect response)"""
        return MCPMessage(
            type=MCPMessageType.NOTIFICATION,
            content=content,
            metadata=metadata
        )

    @staticmethod
    def create_error(content: str, request_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> MCPMessage:
        """Create an error message"""
        return MCPMessage(
            type=MCPMessageType.ERROR,
            content=content,
            metadata=metadata,
            request_id=request_id
        )

    @staticmethod
    def format_for_llm(message: MCPMessage) -> str:
        """
        Format an MCP message for inclusion in LLM context.
        This presents the message in a structured way that the LLM can understand.
        """
        formatted = f"[MCP {message.type.value.upper()}]"
        if message.request_id:
            formatted += f" (ID: {message.request_id})"
        formatted += f"\n{message.content}"
        if message.metadata:
            formatted += f"\n[Metadata: {json.dumps(message.metadata)}]"
        return formatted

    @staticmethod
    def parse_from_llm_output(output: str) -> Optional[MCPMessage]:
        """
        Parse an MCP message from LLM output.
        Looks for structured MCP message format in the text.
        """
        # Simple parser - can be made more sophisticated
        # For now, treat any output as a REQUEST unless specified otherwise
        try:
            # Check if output contains explicit MCP formatting
            if "[MCP" in output:
                # Extract the structured message
                # This is a simplified parser - production would be more robust
                lines = output.split("\n")
                header = lines[0]
                content = "\n".join(lines[1:])

                if "REQUEST" in header:
                    msg_type = MCPMessageType.REQUEST
                elif "RESPONSE" in header:
                    msg_type = MCPMessageType.RESPONSE
                elif "NOTIFICATION" in header:
                    msg_type = MCPMessageType.NOTIFICATION
                else:
                    msg_type = MCPMessageType.REQUEST

                return MCPMessage(type=msg_type, content=content)
            else:
                # Default: treat as a request message
                return MCPMessage(type=MCPMessageType.REQUEST, content=output)
        except Exception:
            return None
