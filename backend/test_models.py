import asyncio
import os
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()

async def test_model(client, model_name):
    try:
        response = await client.messages.create(
            model=model_name,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"✓ {model_name} - WORKS")
        return True
    except Exception as e:
        print(f"✗ {model_name} - FAILED: {str(e)[:100]}")
        return False

async def main():
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    models_to_test = [
        "claude-sonnet-4-5-20250929",
        "claude-opus-4-5-20251101",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]

    print("Testing Anthropic models...\n")
    working_models = []

    for model in models_to_test:
        if await test_model(client, model):
            working_models.append(model)

    print(f"\nWorking models: {working_models}")

if __name__ == "__main__":
    asyncio.run(main())
