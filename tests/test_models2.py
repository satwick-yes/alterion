import main
import asyncio
from google import genai

async def test_model(model_name):
    client = genai.Client(api_key=main._get_api_key(), http_options={'api_version': 'v1alpha'})
    print(f"Testing {model_name}...")
    try:
        async with client.aio.live.connect(model=model_name) as session:
            print(f"SUCCESS: {model_name}")
            return True
    except Exception as e:
        print(f"FAILED: {model_name} - {str(e)}")
        return False

async def main_test():
    models_to_test = [
        "gemini-3-flash-live",
        "gemini-3-flash-live-preview",
        "gemini-3.1-flash-live-preview",
        "gemini-2.5-flash-native-audio-latest"
    ]
    for model in models_to_test:
        await test_model(model)

if __name__ == "__main__":
    asyncio.run(main_test())
