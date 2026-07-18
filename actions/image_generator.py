import os
import json
import re
from pathlib import Path
from google import genai
from google.genai import types

def generate_image(parameters: dict, player=None) -> str:
    """
    Generates an image based on a prompt using Google Imagen 4.
    """
    prompt = parameters.get("prompt")
    if not prompt:
        return "Error: No prompt provided for image generation."

    if player:
        player.write_log(f"SYS: Generating image with Imagen 4: '{prompt}'...")

    try:
        base_dir = Path(__file__).resolve().parent.parent
        api_config = base_dir / "config" / "api_keys.json"
        
        with open(api_config, "r") as f:
            api_key = json.load(f).get("gemini_api_key")
            
        if not api_key:
            return "Error: Gemini API key not found in config."
            
        client = genai.Client(api_key=api_key)
        
        result = client.models.generate_images(
            model='imagen-4.0-generate',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1"
            )
        )
        
        desktop = os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Desktop')
        safe_prompt = re.sub(r'[\\/*?:"<>|]', "", prompt[:20]).strip()
        filename = f"imagen4_{safe_prompt.replace(' ', '_')}.png"
        save_path = os.path.join(desktop, filename)
        
        for generated_image in result.generated_images:
            with open(save_path, "wb") as f:
                f.write(generated_image.image.image_bytes)
                
        if player:
            player.write_log(f"SYS: Image saved to {save_path}")
        
        os.startfile(save_path)
        return f"Image successfully generated using Imagen 4 and saved to {save_path}."
        
    except Exception as e:
        return f"Error generating image with Imagen 4: {e}"
