import asyncio
import json
from google import genai
from google.genai import types

api_key = json.load(open('config/api_keys.json'))['gemini_api_key']
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})

async def main():
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Charon"
                )
            )
        )
    )

    print("Connecting...")
    async with client.aio.live.connect(model='models/gemini-2.5-flash-native-audio-latest', config=config) as session:
        print('Connected!')
        await session.send_client_content(
            turns={"parts": [{"text": "Hello, please say hello out loud."}]},
            turn_complete=True
        )
        async for response in session.receive():
            for p in response.server_content.model_turn.parts:
                print(f"Received part type: {type(p)}")
                if p.inline_data:
                    print(f"Inline data mime: {p.inline_data.mime_type}")
                elif p.text:
                    print(f"Text: {p.text}")

asyncio.run(main())
