import uuid
from typing import Dict, Optional, AsyncIterator
from datetime import datetime

from app.models import (
    SimulationConfig,
    SimulationState,
    SimulationStatus,
    Message,
    MessageRole,
    VerificationResult
)
from app.services import LLMService
from app.agents.agent import Agent, AgentRole
from app.verification import Verifier


class SimulationOrchestrator:
    """
    Orchestrates the multi-turn agent simulation.
    Manages turn-taking, message passing, and verification.
    """

    def __init__(self):
        self.llm_service = LLMService()
        self.verifier = Verifier(self.llm_service)
        self.active_simulations: Dict[str, SimulationState] = {}

    def create_simulation(self, config: SimulationConfig) -> str:
        """
        Create a new simulation.
        Returns: simulation_id
        """
        simulation_id = str(uuid.uuid4())

        state = SimulationState(
            simulation_id=simulation_id,
            config=config,
            status=SimulationStatus.IDLE,
            messages=[],
            current_turn=0
        )

        self.active_simulations[simulation_id] = state
        return simulation_id

    def get_simulation(self, simulation_id: str) -> Optional[SimulationState]:
        """Get simulation state by ID"""
        return self.active_simulations.get(simulation_id)

    async def run_simulation(self, simulation_id: str) -> AsyncIterator[Dict]:
        """
        Run a simulation turn-by-turn.
        Yields state updates as they happen.
        """
        state = self.active_simulations.get(simulation_id)
        if not state:
            raise ValueError(f"Simulation {simulation_id} not found")

        if state.status == SimulationStatus.RUNNING:
            raise ValueError(f"Simulation {simulation_id} is already running")

        # Update status
        state.status = SimulationStatus.RUNNING
        state.updated_at = datetime.now()
        yield {"type": "status", "status": "running"}

        # Create agents
        candidate_agent = Agent(
            role=AgentRole.CANDIDATE,
            config=state.config.candidate_config,
            llm_service=self.llm_service
        )

        sim_agent = Agent(
            role=AgentRole.SIM,
            config=state.config.sim_config,
            llm_service=self.llm_service
        )

        # Determine who goes first
        current_speaker = (
            AgentRole.CANDIDATE
            if state.config.first_speaker == MessageRole.CANDIDATE
            else AgentRole.SIM
        )

        last_message = None
        should_verify = False

        # Run turns
        while state.current_turn < state.config.max_turns and not should_verify:
            state.current_turn += 1
            turn_number = state.current_turn

            # Get the current agent
            if current_speaker == AgentRole.CANDIDATE:
                agent = candidate_agent
                role = MessageRole.CANDIDATE
            else:
                agent = sim_agent
                role = MessageRole.SIM

            yield {
                "type": "turn_start",
                "turn": turn_number,
                "speaker": current_speaker.value
            }

            # Generate response (streaming)
            content = ""
            reasoning = ""

            async for chunk in agent.generate_response_stream(last_message):
                if chunk["type"] == "content":
                    content += chunk["delta"]
                    yield {
                        "type": "content_delta",
                        "speaker": role.value,
                        "delta": chunk["delta"],
                        "turn": turn_number
                    }
                elif chunk["type"] == "reasoning":
                    reasoning += chunk["delta"]
                    yield {
                        "type": "reasoning_delta",
                        "speaker": role.value,
                        "delta": chunk["delta"],
                        "turn": turn_number
                    }

                if chunk.get("should_verify"):
                    should_verify = True

            # Create message record
            message = Message(
                role=role,
                content=content,
                reasoning=reasoning if reasoning else None,
                turn_number=turn_number
            )
            state.messages.append(message)

            yield {
                "type": "message_complete",
                "message": message.model_dump(mode='json'),
                "turn": turn_number
            }

            # Update for next turn
            last_message = content

            # Switch speaker
            current_speaker = (
                AgentRole.SIM if current_speaker == AgentRole.CANDIDATE
                else AgentRole.CANDIDATE
            )

            # Check if verification was requested
            if should_verify:
                yield {"type": "verification_requested"}
                break

        # Run verification if requested or max turns reached
        yield {"type": "verification_start"}

        verification_result = await self.verifier.verify(
            candidate_objective=state.config.candidate_config.objective,
            verification_prompt=state.config.verification_prompt,
            conversation_history=state.messages
        )

        state.verification_result = verification_result
        state.status = SimulationStatus.COMPLETED
        state.updated_at = datetime.now()

        yield {
            "type": "verification_complete",
            "result": verification_result.model_dump(mode='json')
        }

        yield {"type": "simulation_complete"}

    async def run_single_turn(
        self,
        simulation_id: str,
        speaker: MessageRole,
        message_content: Optional[str] = None
    ) -> Message:
        """
        Run a single turn manually (for editing/rerunning).
        Returns the generated message.
        """
        state = self.active_simulations.get(simulation_id)
        if not state:
            raise ValueError(f"Simulation {simulation_id} not found")

        # Create agents and restore their state from messages
        candidate_agent = Agent(
            role=AgentRole.CANDIDATE,
            config=state.config.candidate_config,
            llm_service=self.llm_service
        )

        sim_agent = Agent(
            role=AgentRole.SIM,
            config=state.config.sim_config,
            llm_service=self.llm_service
        )

        # Restore conversation history for both agents
        for msg in state.messages:
            if msg.role == MessageRole.CANDIDATE:
                candidate_agent.add_message_to_history("assistant", msg.content)
                if msg.reasoning:
                    candidate_agent.add_reasoning_trace(msg.reasoning)
                # Add to sim as incoming
                sim_agent.add_message_to_history("user", msg.content)
            elif msg.role == MessageRole.SIM:
                sim_agent.add_message_to_history("assistant", msg.content)
                if msg.reasoning:
                    sim_agent.add_reasoning_trace(msg.reasoning)
                # Add to candidate as incoming
                candidate_agent.add_message_to_history("user", msg.content)

        # Get the agent for this turn
        if speaker == MessageRole.CANDIDATE:
            agent = candidate_agent
        else:
            agent = sim_agent

        # Generate response
        content, reasoning, should_verify = await agent.generate_response(message_content)

        # Create message
        turn_number = len(state.messages) + 1
        message = Message(
            role=speaker,
            content=content,
            reasoning=reasoning,
            turn_number=turn_number
        )

        return message

    def update_message(
        self,
        simulation_id: str,
        turn_number: int,
        new_content: str,
        new_reasoning: Optional[str] = None
    ):
        """Update a message in place (for editing)"""
        state = self.active_simulations.get(simulation_id)
        if not state:
            raise ValueError(f"Simulation {simulation_id} not found")

        # Find and update the message
        for message in state.messages:
            if message.turn_number == turn_number:
                message.content = new_content
                if new_reasoning is not None:
                    message.reasoning = new_reasoning
                state.updated_at = datetime.now()
                return

        raise ValueError(f"Message with turn {turn_number} not found")

    def delete_messages_from(self, simulation_id: str, turn_number: int):
        """Delete all messages from a specific turn onwards (for rerunning)"""
        state = self.active_simulations.get(simulation_id)
        if not state:
            raise ValueError(f"Simulation {simulation_id} not found")

        state.messages = [
            msg for msg in state.messages
            if msg.turn_number < turn_number
        ]
        state.current_turn = turn_number - 1
        state.updated_at = datetime.now()
