import os
import json
import re
import requests
from pathlib import Path
from typing import Optional


def get_base_dir() -> Path:
    import sys
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"
DESKTOP = os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Desktop')


def _load_keys() -> dict:
    try:
        with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _safe_filename(prompt: str, prefix: str) -> str:
    safe = re.sub(r'[\\/\*\?:\"<>|]', "", prompt[:25]).strip()
    return f"{prefix}_{safe.replace(' ', '_')}.png"


def _generate_with_dalle3(prompt: str, save_path: str) -> Optional[str]:
    """Use DALL-E 3 for photorealistic image generation."""
    keys = _load_keys()
    openai_key = keys.get("openai_api_key", "").strip()
    if not openai_key:
        return None
    try:
        import openai
        print(f"[ImageGenerator] Trying DALL-E 3...")
        client = openai.OpenAI(api_key=openai_key)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1,
        )
        image_url = response.data[0].url
        img_data = requests.get(image_url, timeout=30).content
        with open(save_path, "wb") as f:
            f.write(img_data)
        return save_path
    except Exception as e:
        print(f"[ImageGenerator] DALL-E 3 failed: {e}")
        return None


def _generate_with_imagen4(prompt: str, save_path: str) -> Optional[str]:
    """Use Google Imagen 4 as fallback."""
    keys = _load_keys()
    gemini_key = keys.get("gemini_api_key", "").strip()
    if not gemini_key:
        return None
    try:
        from google import genai
        from google.genai import types
        print(f"[ImageGenerator] Trying Imagen 4 (fallback)...")
        client = genai.Client(api_key=gemini_key)
        result = client.models.generate_images(
            model='imagen-4.0-generate',
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="1:1")
        )
        for generated_image in result.generated_images:
            with open(save_path, "wb") as f:
                f.write(generated_image.image.image_bytes)
        return save_path
    except Exception as e:
        print(f"[ImageGenerator] Imagen 4 failed: {e}")
        return None


def generate_image(parameters: dict, player=None) -> str:
    """
    Generates an image. Tries DALL-E 3 first, then Imagen 4 as fallback.
    Parameters:
      - prompt: str — the image description
    """
    prompt = (parameters or {}).get("prompt", "").strip()
    if not prompt:
        return "Error: No prompt provided for image generation."

    if player:
        player.write_log(f"SYS: Generating image: '{prompt[:50]}'...")

    dalle_path = os.path.join(DESKTOP, _safe_filename(prompt, "dalle3"))
    imagen_path = os.path.join(DESKTOP, _safe_filename(prompt, "imagen4"))

    # Try DALL-E 3 first (primary)
    result = _generate_with_dalle3(prompt, dalle_path)
    if result:
        if player:
            player.write_log(f"SYS: Image saved to {result}")
        os.startfile(result)
        return f"Image successfully generated with DALL-E 3 and saved to {result}."

    # Fall back to Imagen 4
    result = _generate_with_imagen4(prompt, imagen_path)
    if result:
        if player:
            player.write_log(f"SYS: Image saved to {result}")
        os.startfile(result)
        return f"Image successfully generated with Imagen 4 and saved to {result}."

    return "Error: All image generation providers (DALL-E 3, Imagen 4) failed."
