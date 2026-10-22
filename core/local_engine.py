import json
import urllib.request
import urllib.parse
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Generator

logger = logging.getLogger("local_engine")

class LocalEngine:
    """
    Tier 1 Local Engine connecting to an on-device Ollama server.
    Provides zero-latency, 100% offline, zero-api-cost inference for local tasks.
    Optimized for NVIDIA RTX 4050 (6GB VRAM) and AMD Ryzen 7 7735HS.
    """
    PREFERRED_MODELS = [
        "qwen2.5:7b",
        "qwen2.5:latest",
        "qwen2.5-coder:7b",
        "qwen2.5-coder:latest",
        "llama3.1:8b",
        "llama3.1:latest",
        "mistral:7b",
        "gemma2:9b",
        "phi3.5:latest",
        "phi3:latest",
        "llama3.2:3b"
    ]
    
    PREFERRED_VISION_MODELS = [
        "moondream",
        "llava:7b",
        "llava:latest",
        "minicpm-v",
        "bakllava"
    ]

    def __init__(self, ollama_url: str = "http://localhost:11434", timeout: int = 5):
        self.ollama_url = ollama_url.rstrip("/")
        self.timeout = timeout
        self.available_models: List[str] = []
        self.active_model: Optional[str] = None
        self.active_vision_model: Optional[str] = None
        self._check_health()

    def _check_health(self) -> bool:
        """Checks if local Ollama server is running and fetches installed models."""
        try:
            url = f"{self.ollama_url}/api/tags"
            req = urllib.request.Request(url, headers={"User-Agent": "Vani-Local/1.0"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = data.get("models", [])
                self.available_models = [m.get("name") for m in models if m.get("name")]
                
                if self.available_models:
                    # Select best primary text model
                    for pref in self.PREFERRED_MODELS:
                        for installed in self.available_models:
                            if pref in installed:
                                self.active_model = installed
                                break
                        if self.active_model:
                            break
                    if not self.active_model:
                        self.active_model = self.available_models[0]

                    # Select best vision model
                    for vpref in self.PREFERRED_VISION_MODELS:
                        for installed in self.available_models:
                            if vpref in installed:
                                self.active_vision_model = installed
                                break
                        if self.active_vision_model:
                            break

                    logger.info(f"Local Ollama online. Active Model: {self.active_model}, Vision Model: {self.active_vision_model}")
                    return True
        except Exception as e:
            logger.debug(f"Local Ollama health check: offline ({e})")
            self.available_models = []
            self.active_model = None
            self.active_vision_model = None
        return False

    def is_available(self) -> bool:
        return self._check_health()

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        images: Optional[List[str]] = None
    ) -> str:
        """Generates text response using local Ollama model (with optional vision images)."""
        if not self._check_health():
            raise RuntimeError("Local Ollama engine is offline or unreachable at " + self.ollama_url)

        # Pick appropriate model (switch to vision model if images are provided)
        if images:
            target_model = model or self.active_vision_model or self.active_model or "moondream"
        else:
            target_model = model or self.active_model or "qwen2.5:7b"

        url = f"{self.ollama_url}/api/generate"
        payload: Dict[str, Any] = {
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
        if images:
            payload["images"] = images

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"Local Ollama generation failed ({target_model}): {e}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Chat completion using Ollama /api/chat with full conversational history."""
        if not self._check_health():
            raise RuntimeError("Local Ollama engine is offline or unreachable at " + self.ollama_url)

        target_model = model or self.active_model or "qwen2.5:7b"
        url = f"{self.ollama_url}/api/chat"

        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                message = result.get("message", {})
                return message.get("content", "").strip()
        except Exception as e:
            raise RuntimeError(f"Local Ollama chat failed ({target_model}): {e}")

    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """Generates structured JSON output using local Ollama model."""
        enhanced_instruction = (system_instruction or "") + "\nCRITICAL: Respond ONLY with a valid, parseable JSON object. Do not include markdown codeblocks or preamble."
        raw_text = self.generate_text(
            prompt=prompt,
            system_instruction=enhanced_instruction,
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
            logger.warning(f"Local JSON parsing failed: {e}. Raw output: {raw_text[:120]}")
            return {"raw_response": raw_text}

# Singleton instance
local_engine = LocalEngine()

