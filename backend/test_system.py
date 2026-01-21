import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

from app.models import SimulationConfig, AgentConfig, MessageRole
from app.agents import SimulationOrchestrator

async def test_complete_simulation():
    """Test a complete simulation flow"""

    print("=" * 60)
    print("TESTING AGENT SIMULATION PLATFORM")
    print("=" * 60)

    # Create orchestrator
    print("\n[1/5] Creating orchestrator...")
    orchestrator = SimulationOrchestrator()
    print("✓ Orchestrator created")

    # Create simulation config
    print("\n[2/5] Creating simulation configuration...")
    candidate_config = AgentConfig(
        system_prompt="You are trying to find out information.",
        objective="Find out what the other agent's favorite color is.",
        model="claude-sonnet-4-5-20250929",
        temperature=1.0,
        max_tokens=500  # Keep short for testing
    )

    sim_config = AgentConfig(
        system_prompt="You are a helpful agent.",
        objective="Your favorite color is blue. Share it if asked politely.",
        model="claude-sonnet-4-5-20250929",
        temperature=1.0,
        max_tokens=500
    )

    config = SimulationConfig(
        candidate_config=candidate_config,
        sim_config=sim_config,
        verification_prompt="Check if the candidate learned that the favorite color is blue.",
        max_turns=3,  # Keep short for testing
        first_speaker=MessageRole.CANDIDATE
    )
    print("✓ Configuration created")

    # Create simulation
    print("\n[3/5] Creating simulation...")
    simulation_id = orchestrator.create_simulation(config)
    print(f"✓ Simulation created with ID: {simulation_id}")

    # Run simulation
    print("\n[4/5] Running simulation...")
    print("-" * 60)

    events_received = []
    try:
        async for event in orchestrator.run_simulation(simulation_id):
            events_received.append(event['type'])

            if event['type'] == 'turn_start':
                print(f"\n→ Turn {event['turn']}: {event['speaker'].upper()} speaking")

            elif event['type'] == 'content_delta':
                print(event['delta'], end='', flush=True)

            elif event['type'] == 'message_complete':
                print()  # New line after message

            elif event['type'] == 'verification_complete':
                result = event['result']
                status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
                print(f"\n{'-' * 60}")
                print(f"VERIFICATION: {status}")
                print(f"Explanation: {result['explanation']}")

            elif event['type'] == 'simulation_complete':
                print(f"\n{'-' * 60}")
                print("✓ Simulation completed")

            elif event['type'] == 'error':
                print(f"\n✗ ERROR: {event['message']}")
                return False

    except Exception as e:
        print(f"\n✗ EXCEPTION during simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # Verify we got expected events
    print("\n[5/5] Verifying events...")
    expected_events = ['status', 'turn_start', 'message_complete', 'verification_complete', 'simulation_complete']
    for expected in expected_events:
        if expected not in events_received:
            print(f"✗ Missing expected event: {expected}")
            return False
    print(f"✓ All expected events received")

    # Get final state
    final_state = orchestrator.get_simulation(simulation_id)
    print(f"\n✓ Final state retrieved:")
    print(f"  - Messages: {len(final_state.messages)}")
    print(f"  - Status: {final_state.status}")
    print(f"  - Verification: {final_state.verification_result.success if final_state.verification_result else 'N/A'}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = asyncio.run(test_complete_simulation())
    exit(0 if success else 1)
