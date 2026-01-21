from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class MessageRole(str, Enum):
    CANDIDATE = "candidate"
    SIM = "sim"
    SYSTEM = "system"


class SimulationStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentConfig(BaseModel):
    """Configuration for a single agent (candidate or sim)"""
    system_prompt: str
    objective: str
    model: str = "claude-sonnet-4-5-20250929"  # Default to latest Anthropic model
    temperature: float = 1.0
    max_tokens: int = 4096


class Message(BaseModel):
    """A single message in the conversation"""
    role: MessageRole
    content: str
    reasoning: Optional[str] = None  # Internal reasoning/thinking
    timestamp: datetime = Field(default_factory=datetime.now)
    turn_number: int

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VerificationResult(BaseModel):
    """Result of the verification check"""
    success: bool
    explanation: str
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SimulationConfig(BaseModel):
    """Full configuration for a simulation"""
    candidate_config: AgentConfig
    sim_config: AgentConfig
    verification_prompt: str  # Prompt for the verifier to check success
    max_turns: int = 10
    first_speaker: MessageRole = MessageRole.CANDIDATE  # Who speaks first


class SimulationState(BaseModel):
    """Current state of a running simulation"""
    simulation_id: str
    config: SimulationConfig
    status: SimulationStatus
    messages: List[Message] = []
    current_turn: int = 0
    verification_result: Optional[VerificationResult] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
