import json
import urllib.request
import urllib.parse
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger("local_engine")

class LocalEngine:
    """
    Tier 1 Local Engine connecting to an on-device Ollama server.
    Provides zero-latency, 100% offline, zero-api-cost inference for local tasks.
    """
    def __init__(self, ollama_url: str = "http://localhost:11434", timeout: int = 5):
        self.ollama_url = ollama_url.rstrip("/")
        self.timeout = timeout
        self.available_models: List[str] = []
        self.active_model: Optional[str] = None
        self._check_health()

    def _check_health(self) -> bool:
        """Checks if local Ollama server is running and fetches installed models."""
        try:
            url = f"{self.ollama_url}/api/tags"
            req = urllib.request.Request(url, headers={"User-Agent": "Jarvis-Local/1.0"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = data.get("models", [])
                self.available_models = [m.get("name") for m in models if m.get("name")]
                if self.available_models:
                    self.active_model = self.available_models[0]
                    logger.info(f"Local Ollama online. Found {len(self.available_models)} model(s): {self.available_models}")
                    return True
        except Exception as e:
            logger.debug(f"Local Ollama health check: offline ({e})")
            self.available_models = []
            self.active_model = None
        return False

    def is_available(self) -> bool:
        return self._check_health()

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generates text response using local Ollama model."""
        if not self._check_health():
            raise RuntimeError("Local Ollama engine is offline or unreachable.")

        target_model = model or self.active_model or "qwen2.5-coder"
        url = f"{self.ollama_url}/api/generate"

        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if system_instruction:
            payload["system"] = system_instruction

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"Local Ollama generation failed: {e}")

    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """Generates structured JSON output using local Ollama model."""
        raw_text = self.generate_text(
            prompt=prompt + "\nReturn ONLY valid JSON.",
            system_instruction=system_instruction,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        clean = raw_text.strip()
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0].strip()

        try:
            return json.loads(clean)
        except Exception as e:
            logger.warning(f"Local JSON parsing failed: {e}. Raw output: {raw_text[:100]}")
            return {"raw_response": raw_text}

# Singleton instance
local_engine = LocalEngine()
