import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_api():
    print("=" * 60)
    print("TESTING HTTP API ENDPOINTS")
    print("=" * 60)

    # Test 1: Health check
    print("\n[1/4] Testing health endpoint...")
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    health = response.json()
    assert health["status"] == "healthy"
    assert health["anthropic_api_key"] == "set"
    print(f"✓ Health check passed: {health}")

    # Test 2: List models
    print("\n[2/4] Testing models endpoint...")
    response = requests.get(f"{BASE_URL}/models")
    assert response.status_code == 200
    models = response.json()
    assert "anthropic" in models
    assert "openai" in models
    assert len(models["anthropic"]) > 0
    print(f"✓ Models endpoint working: {len(models['anthropic'])} Anthropic, {len(models['openai'])} OpenAI models")

    # Test 3: Create simulation
    print("\n[3/4] Testing simulation creation...")
    config = {
        "candidate_config": {
            "system_prompt": "You are a test agent.",
            "objective": "Say hello to the other agent.",
            "model": "claude-sonnet-4-5-20250929",
            "temperature": 1.0,
            "max_tokens": 100
        },
        "sim_config": {
            "system_prompt": "You are a friendly agent.",
            "objective": "Respond politely to greetings.",
            "model": "claude-sonnet-4-5-20250929",
            "temperature": 1.0,
            "max_tokens": 100
        },
        "verification_prompt": "Check if agents greeted each other.",
        "max_turns": 2,
        "first_speaker": "candidate"
    }

    response = requests.post(f"{BASE_URL}/simulations", json=config)
    assert response.status_code == 200
    result = response.json()
    assert "simulation_id" in result
    simulation_id = result["simulation_id"]
    print(f"✓ Simulation created: {simulation_id}")

    # Test 4: Get simulation
    print("\n[4/4] Testing simulation retrieval...")
    response = requests.get(f"{BASE_URL}/simulations/{simulation_id}")
    assert response.status_code == 200
    state = response.json()
    assert state["simulation_id"] == simulation_id
    assert state["status"] == "idle"
    print(f"✓ Simulation retrieved: status={state['status']}, messages={len(state['messages'])}")

    print("\n" + "=" * 60)
    print("ALL API TESTS PASSED ✓")
    print("=" * 60)
    print("\nThe API is ready for the frontend to connect!")
    return True

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
