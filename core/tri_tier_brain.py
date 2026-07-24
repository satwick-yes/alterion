import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from core.local_engine import local_engine
from core.inference_wrapper import inference_client

logger = logging.getLogger("tri_tier_brain")

class TriTierBrain:
    """
    Orchestrates the Tri-Tier Hybrid Brain Architecture:
    - Tier 1: Local Engine (Ollama / On-device - 0 Cost, Offline)
    - Tier 2: Real-time Conversational Stream Engine (Groq / Gemini Live - <300ms Speech)
    - Tier 3: Cloud Master Brain (Claude / Gemini Pro - High Reasoning & Vision)
    """

    def __init__(self):
        self.config_path = Path(__file__).resolve().parent.parent / "config" / "brain_config.json"
        self._load_config()

    def _load_config(self):
        self.config = {}
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load brain_config.json: {e}")

    def route_text_query(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        prefer_local: bool = False,
        requires_high_reasoning: bool = False
    ) -> str:
        """
        Dynamically routes a text request to the appropriate tier:
        - If requires_high_reasoning: Routes to Tier 3 (Cloud Master Brain).
        - If prefer_local or local tasks: Attempts Tier 1 (Local Engine), falling back to Cloud.
        - Default: Routes via InferenceWrapper smart fallback.
        """
        # Tier 3: High reasoning / vision tasks
        if requires_high_reasoning:
            logger.info("TriTierBrain: Routing to Tier 3 (Cloud Master Brain)")
            return inference_client.generate_text(
                prompt=prompt,
                system_instruction=system_instruction,
                provider="gemini"
            )

        # Tier 1: Local engine execution check
        if (prefer_local or self._is_local_task(prompt)) and local_engine.is_available():
            try:
                logger.info(f"TriTierBrain: Routing to Tier 1 Local Engine ({local_engine.active_model})")
                return local_engine.generate_text(
                    prompt=prompt,
                    system_instruction=system_instruction
                )
            except Exception as e:
                logger.warning(f"Tier 1 Local Engine execution failed: {e}. Falling back to Cloud Tier.")

        # Default fallback to Cloud Provider (Groq/Gemini)
        logger.info("TriTierBrain: Routing to Cloud Provider")
        return inference_client.generate_text(
            prompt=prompt,
            system_instruction=system_instruction
        )

    def _is_local_task(self, prompt: str) -> bool:
        """Determines if a task is a candidate for Tier 1 local processing."""
        p = prompt.lower()
        local_keywords = [
            "system stats", "wifi", "organize folder", "ip address", 
            "speed test", "local", "volume", "file", "disk", "hardware"
        ]
        return any(kw in p for kw in local_keywords)

    def get_status() -> Dict[str, Any]:
        """Returns the current status of all 3 Tiers."""
        local_online = local_engine.is_available()
        return {
            "tier_1_local": {
                "status": "ONLINE" if local_online else "OFFLINE (Cloud Fallback Active)",
                "engine": "Ollama",
                "active_model": local_engine.active_model if local_online else "N/A",
                "available_models": local_engine.available_models
            },
            "tier_2_realtime": {
                "status": "ONLINE",
                "engine": "Gemini Live / Groq Realtime Audio"
            },
            "tier_3_master": {
                "status": "ONLINE",
                "engine": "Gemini 3.1 Flash / Claude 3.7 Master Orchestration"
            }
        }

# Singleton instance
tri_tier_brain = TriTierBrain()
