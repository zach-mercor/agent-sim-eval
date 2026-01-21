from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import json

from app.models import SimulationConfig, SimulationState, MessageRole
from app.agents import SimulationOrchestrator

router = APIRouter()

# Global orchestrator instance
orchestrator = SimulationOrchestrator()


@router.post("/simulations", response_model=dict)
async def create_simulation(config: SimulationConfig):
    """Create a new simulation"""
    try:
        simulation_id = orchestrator.create_simulation(config)
        return {
            "simulation_id": simulation_id,
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulations/{simulation_id}", response_model=SimulationState)
async def get_simulation(simulation_id: str):
    """Get simulation state"""
    state = orchestrator.get_simulation(simulation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return state


@router.post("/simulations/{simulation_id}/run")
async def run_simulation(simulation_id: str):
    """Run a simulation (streaming response)"""
    try:
        async def event_generator():
            try:
                async for event in orchestrator.run_simulation(simulation_id):
                    # Send as Server-Sent Events
                    yield f"data: {json.dumps(event)}\n\n"
            except Exception as e:
                error_event = {"type": "error", "message": str(e)}
                yield f"data: {json.dumps(error_event)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/simulations/{simulation_id}/messages/{turn_number}")
async def update_message(
    simulation_id: str,
    turn_number: int,
    content: str,
    reasoning: Optional[str] = None
):
    """Update a message in place"""
    try:
        orchestrator.update_message(
            simulation_id,
            turn_number,
            content,
            reasoning
        )
        return {"status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulations/{simulation_id}/rerun/{from_turn}")
async def rerun_from_turn(simulation_id: str, from_turn: int):
    """Delete messages from a turn onwards and prepare for rerun"""
    try:
        orchestrator.delete_messages_from(simulation_id, from_turn)
        return {"status": "ready_for_rerun", "from_turn": from_turn}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """List available models - only for providers with API keys configured"""
    import os

    result = {}

    # Only include Anthropic models if key is set
    if os.getenv("ANTHROPIC_API_KEY"):
        result["anthropic"] = [
            "claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 (latest)
            "claude-opus-4-5-20251101",     # Claude Opus 4.5
            "claude-3-5-haiku-20241022",    # Claude 3.5 Haiku
            "claude-3-haiku-20240307"       # Claude 3 Haiku
        ]

    # Only include OpenAI models if key is set
    if os.getenv("OPENAI_API_KEY"):
        result["openai"] = [
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]

    return result
