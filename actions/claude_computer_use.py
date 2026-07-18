# This module now delegates directly to vision_computer_use.
# Claude/Anthropic has been removed. All computer use now uses vision (OpenRouter/Gemini).
from actions.vision_computer_use import advanced_computer_use  # noqa: F401
