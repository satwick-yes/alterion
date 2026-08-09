# agent/actions/audio_transcriber.py
# Transcribes audio files using Eden AI (primary) with OpenAI Whisper as fallback.
import json, sys, os
from pathlib import Path

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"

def _load_keys() -> dict:
    try:
        with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _transcribe_with_edenai(file_path: str, language: str = "en") -> str:
    keys = _load_keys()
    eden_key = keys.get("eden_api_key", "").strip()
    if not eden_key:
        raise ValueError("Eden AI API key not configured.")
    import requests
    print(f"[AudioTranscriber] Transcribing with Eden AI: {file_path}")
    with open(file_path, "rb") as audio_file:
        resp = requests.post(
            "https://api.edenai.run/v2/audio/speech_to_text_async/",
            headers={"Authorization": f"Bearer {eden_key}"},
            files={"file": audio_file},
            data={"providers": "openai,google", "language": language, "response_as_dict": "true", "show_original_response": "false"},
            timeout=60,
        )
    data = resp.json()
    for provider in ["openai", "google"]:
        text = data.get(provider, {}).get("text", "").strip()
        if text:
            print(f"[AudioTranscriber] Eden AI ({provider}) OK.")
            return text
    raise ValueError(f"Eden AI returned no transcription. Response: {data}")

def _transcribe_with_whisper(file_path: str) -> str:
    keys = _load_keys()
    openai_key = keys.get("openai_api_key", "").strip()
    if not openai_key:
        raise ValueError("OpenAI API key not configured for Whisper.")
    import openai
    print(f"[AudioTranscriber] Transcribing with OpenAI Whisper: {file_path}")
    client = openai.OpenAI(api_key=openai_key)
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    print("[AudioTranscriber] Whisper OK.")
    return transcript.text.strip()

def transcribe_audio(parameters: dict, player=None) -> str:
    """Transcribes an audio file. Parameters: file_path, quality (standard|high), language."""
    file_path = (parameters or {}).get("file_path", "").strip()
    quality = (parameters or {}).get("quality", "standard").lower()
    language = (parameters or {}).get("language", "en").strip()
    if not file_path:
        return "Error: No file_path provided for audio transcription."
    if not os.path.exists(file_path):
        return f"Error: File not found at path: {file_path}"
    if player:
        player.write_log(f"[Transcriber] Transcribing: {file_path} (quality={quality})")
    if quality == "high":
        try:
            return _transcribe_with_whisper(file_path)
        except Exception as e:
            print(f"[AudioTranscriber] Whisper failed: {e}. Falling back to Eden AI.")
    try:
        return _transcribe_with_edenai(file_path, language)
    except Exception as e1:
        print(f"[AudioTranscriber] Eden AI failed: {e1}. Falling back to Whisper.")
        try:
            return _transcribe_with_whisper(file_path)
        except Exception as e2:
            return f"Error: All transcription providers failed. Eden AI: {e1}. Whisper: {e2}"
