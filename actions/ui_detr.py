"""
ui_detr.py — V.A.N.I. Screen State Generator

Converts a raw desktop screenshot into a structured JSON list of detected
UI elements using Gemini Vision (primary) or OpenRouter vision (fallback).

This is the perception layer of the V.A.N.I. autonomous GUI agent loop.
The output "Screen State" is fed to the reasoning LLM each turn so it can
ground its actions to real pixel coordinates instead of hallucinating them.
"""

import base64
import io
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# ── PIL / mss for screenshotting ──────────────────────────────────────────────
try:
    from PIL import Image, ImageGrab
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

try:
    import mss
    import mss.tools
    _MSS_OK = True
except ImportError:
    _MSS_OK = False


# ── Base dir helpers ──────────────────────────────────────────────────────────
def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()


def _load_keys() -> dict:
    try:
        with open(BASE_DIR / "config" / "api_keys.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ── Vision Prompt (UI-DETR) ───────────────────────────────────────────────────
_UI_DETR_PROMPT = """You are an advanced Computer Vision UI Parser operating as a visual element detection engine.

### MISSION
Analyze the provided screenshot and identify all interactive and contextual UI elements currently visible on the screen.

### ELEMENT TYPES TO IDENTIFY
- button: Clickable buttons, icons acting as buttons, and submit/action triggers.
- text_input: Text fields, search bars, text areas, and password inputs.
- link: Hyperlinks or navigational text.
- icon: Actionable symbols (settings gear, close 'X', minimize, search magnifying glass, etc.).
- checkbox / radio: Selectable toggle controls.
- dropdown: Select boxes or expandable menus.
- static_text: Key labels, titles, or messages providing essential context.

### EXTRACTION RULES
1. Precise Center Coordinates: For every element, compute the exact [x, y] center coordinate based on the native pixel resolution of the image.
2. Label & Text Extraction: Extract the exact visible text inside or directly adjacent to the element. If an icon has no text, describe its visual meaning in parentheses (e.g., "(close)", "(settings)", "(search)").
3. Visibility & Occlusion: Only include elements that are clearly visible and clickable. Do not hallucinate elements that might be scrolled out of view.
4. Output Constraints: Output ONLY a valid JSON array of objects. Do not include markdown commentary, explanations, or conversational text.

### OUTPUT JSON SCHEMA
[
  {
    "id": 1,
    "type": "text_input",
    "text": "Search Google or type a URL",
    "center_coords": [640, 420]
  },
  {
    "id": 2,
    "type": "button",
    "text": "Google Search",
    "center_coords": [580, 480]
  }
]"""


# ── Screenshot capture ────────────────────────────────────────────────────────
def _capture_screenshot(max_width: int = 1280, jpeg_quality: int = 70):
    """
    Capture the primary monitor and return:
      (jpeg_bytes, scaled_w, scaled_h, scale_x, scale_y)

    scale_x / scale_y convert scaled pixel coords back to native screen coords.
    """
    orig_w = orig_h = 0

    # Prefer mss (faster, handles HiDPI) then PIL ImageGrab
    if _MSS_OK:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            shot = sct.grab(monitor)
            png_bytes = mss.tools.to_png(shot.rgb, shot.size)
            orig_w, orig_h = shot.width, shot.height
        if _PIL_OK:
            img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
        else:
            raise RuntimeError("PIL is required to compress the screenshot.")
    elif _PIL_OK:
        img = ImageGrab.grab()
        orig_w, orig_h = img.size
    else:
        raise RuntimeError("Neither mss nor PIL is available — cannot take screenshot.")

    # Downscale so the vision model gets a fast, clear image
    scale = min(1.0, max_width / orig_w)
    if scale < 1.0:
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    else:
        new_w, new_h = orig_w, orig_h

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=jpeg_quality)
    jpeg_bytes = buf.getvalue()

    # Scale factors so the model's coords can be mapped back to native pixels
    scale_x = orig_w / new_w if new_w else 1.0
    scale_y = orig_h / new_h if new_h else 1.0

    return jpeg_bytes, new_w, new_h, scale_x, scale_y


# ── Vision backends ───────────────────────────────────────────────────────────
def _parse_element_list(raw: str) -> List[Dict[str, Any]]:
    """Strip markdown fences and parse the JSON array from the model response."""
    raw = raw.strip()
    # Strip ```json ... ``` fences if present
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:]) if lines[0].startswith("```") else raw
        if raw.endswith("```"):
            raw = raw[: raw.rfind("```")]
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    return []


def _call_gemini(b64_image: str, width: int, height: int) -> Optional[str]:
    """Call Gemini Vision and return raw model text, or None on failure."""
    keys = _load_keys()
    api_key = keys.get("gemini_api_key", "").strip()
    if not api_key:
        return None
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt_with_dims = (
            f"{_UI_DETR_PROMPT}\n\n"
            f"### IMAGE METADATA\n"
            f"- Scaled resolution fed to you: {width}x{height} px\n"
            f"- Your coordinates must match this resolution exactly.\n"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=base64.b64decode(b64_image),
                    mime_type="image/jpeg",
                ),
                types.Part.from_text(text=prompt_with_dims),
            ],
            config=types.GenerateContentConfig(
                max_output_tokens=4096,
                temperature=0.0,
            ),
        )
        print("[UI-DETR] Gemini Vision responded.")
        return response.text
    except Exception as e:
        print(f"[UI-DETR] Gemini Vision failed: {e}")
        return None


def _call_openrouter(b64_image: str, width: int, height: int) -> Optional[str]:
    """Call OpenRouter vision (fallback) and return raw model text, or None on failure."""
    try:
        from core.or_client import OpenRouterClient

        client = OpenRouterClient()
        prompt_with_dims = (
            f"{_UI_DETR_PROMPT}\n\n"
            f"### IMAGE METADATA\n"
            f"- Scaled resolution fed to you: {width}x{height} px\n"
            f"- Your coordinates must match this resolution exactly.\n"
        )
        text = client.vision(
            prompt=prompt_with_dims,
            image_b64=b64_image,
            mime="image/jpeg",
            system="Output ONLY a valid JSON array. No commentary or markdown.",
        )
        print("[UI-DETR] OpenRouter Vision responded.")
        return text
    except Exception as e:
        print(f"[UI-DETR] OpenRouter Vision failed: {e}")
        return None


# ── Coordinate remapping ──────────────────────────────────────────────────────
def _remap_coords(
    elements: List[Dict[str, Any]],
    scale_x: float,
    scale_y: float,
) -> List[Dict[str, Any]]:
    """
    The vision model outputs coords relative to the *scaled* image.
    Convert them back to native screen pixel coordinates.
    """
    remapped = []
    for el in elements:
        el = dict(el)
        coords = el.get("center_coords")
        if isinstance(coords, (list, tuple)) and len(coords) == 2:
            el["center_coords"] = [
                int(coords[0] * scale_x),
                int(coords[1] * scale_y),
            ]
        remapped.append(el)
    return remapped


# ── Public API ────────────────────────────────────────────────────────────────
def generate_screen_state() -> List[Dict[str, Any]]:
    """
    Capture a screenshot and parse it into a structured Screen State.

    Returns a list of dicts, each with keys:
      - id            (int)
      - type          (str: button | text_input | link | icon | ...)
      - text          (str)
      - center_coords ([x, y] in native screen pixels)

    Returns an empty list on failure.
    """
    print("[UI-DETR] Capturing screenshot...")
    try:
        jpeg_bytes, scaled_w, scaled_h, scale_x, scale_y = _capture_screenshot()
    except Exception as e:
        print(f"[UI-DETR] Screenshot failed: {e}")
        return []

    b64 = base64.b64encode(jpeg_bytes).decode("utf-8")
    print(f"[UI-DETR] Sending {scaled_w}x{scaled_h} image to Vision model...")

    # Try Gemini first, then OpenRouter
    raw_text = _call_gemini(b64, scaled_w, scaled_h)
    if not raw_text:
        raw_text = _call_openrouter(b64, scaled_w, scaled_h)

    if not raw_text:
        print("[UI-DETR] All vision backends failed. Returning empty state.")
        return []

    elements = _parse_element_list(raw_text)
    if not elements:
        print(f"[UI-DETR] Could not parse element list from model response:\n{raw_text[:300]}")
        return []

    # Remap scaled -> native pixel coordinates
    elements = _remap_coords(elements, scale_x, scale_y)

    print(f"[UI-DETR] Detected {len(elements)} UI elements.")
    return elements


def screen_state_to_text(elements: List[Dict[str, Any]]) -> str:
    """
    Serialise the screen state list to a compact, readable JSON string
    for injection into the reasoning prompt.
    """
    return json.dumps(elements, indent=2, ensure_ascii=False)


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== UI-DETR Screen State Test ===")
    t0 = time.perf_counter()
    state = generate_screen_state()
    elapsed = time.perf_counter() - t0

    print(f"\n  {elapsed:.2f}s | {len(state)} elements detected\n")
    print(screen_state_to_text(state))
