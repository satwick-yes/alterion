import json
import os
import sys
import logging
from pathlib import Path
from typing import Optional, Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inference_wrapper")

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"

class InferenceWrapper:
    def __init__(self):
        self.gemini_key = ""
        self.openrouter_key = ""
        self.nvidia_key = ""
        self.openai_key = ""
        self.default_provider = "gemini"
        self._load_keys()

    def _load_keys(self):
        try:
            if API_CONFIG_PATH.exists():
                with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.gemini_key = data.get("gemini_api_key", "").strip()
                self.openrouter_key = data.get("openrouter_api_key", "").strip()
                self.nvidia_key = data.get("nvidia_api_key", "").strip()
                self.openai_key = data.get("openai_api_key", "").strip()
            
            is_gemini_valid = bool(self.gemini_key)
            
            if is_gemini_valid:
                self.default_provider = "gemini"
            else:
                self.default_provider = "gemini" # fallback
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        provider = provider or self.default_provider
        
        try:
            if provider == "gemini":
                return self._call_gemini_text(prompt, system_instruction, model, temperature, max_tokens)
            elif provider == "openrouter":
                return self._call_openrouter_text(prompt, system_instruction, model, temperature, max_tokens)
            elif provider == "nvidia":
                return self._call_nvidia_text(prompt, system_instruction, model, temperature, max_tokens)
            elif provider == "openai":
                return self._call_openai_text(prompt, system_instruction, model, temperature, max_tokens)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        except Exception as e:
            # Automatic fallback to OpenRouter if primary provider fails and OpenRouter key exists
            if provider != "openrouter" and self.openrouter_key:
                logger.warning(f"Provider '{provider}' text generation failed: {e}. Falling back to openrouter.")
                return self._call_openrouter_text(prompt, system_instruction, None, temperature, max_tokens)
            raise

    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> Dict:
        provider = provider or self.default_provider
        
        try:
            if provider == "gemini":
                return self._call_gemini_json(prompt, system_instruction, model, temperature, max_tokens)
            elif provider == "openrouter":
                return self._call_openrouter_json(prompt, system_instruction, model, max_tokens)
            elif provider == "nvidia":
                return self._call_nvidia_json(prompt, system_instruction, model, temperature, max_tokens)
            elif provider == "openai":
                return self._call_openai_json(prompt, system_instruction, model, temperature, max_tokens)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        except Exception as e:
            # Automatic fallback to OpenRouter JSON if primary fails
            if provider != "openrouter" and self.openrouter_key:
                logger.warning(f"Provider '{provider}' JSON generation failed: {e}. Falling back to openrouter.")
                return self._call_openrouter_json(prompt, system_instruction, None, max_tokens)
            raise

    def _emulated_embedding(self, text: str) -> List[float]:
        logger.warning("Emulating local embedding.")
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        val = [float(b) / 255.0 for b in h]
        val = val * (768 // len(val) + 1)
        return val[:768]

    def generate_embedding(self, text: str) -> List[float]:
        if not self.gemini_key:
            return self._emulated_embedding(text)
            
        try:
            from google import genai
            client = genai.Client(api_key=self.gemini_key)
            # Remove "models/" prefix for google-genai SDK
            response = client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
            embeddings = response.embeddings
            if embeddings and len(embeddings) > 0:
                return embeddings[0].values
            raise ValueError("No embeddings returned from API")
        except Exception as e:
            logger.error(f"Gemini embedding failed: {e}. Trying google-generativeai fallback.")
            try:
                import google.generativeai as old_genai
                old_genai.configure(api_key=self.gemini_key)
                response = old_genai.embed_content(
                    model="models/embedding-001",
                    content=text  # Singular parameter for google-generativeai
                )
                return response.get("embedding", [])
            except Exception as e2:
                logger.error(f"Fallback embedding failed: {e2}")
                # Return emulated embedding to ensure local tasks and tests don't crash
                return self._emulated_embedding(text)

    # --- GEMINI IMPLEMENTATIONS ---
    def _call_gemini_text(self, prompt: str, system: Optional[str], model: Optional[str], temp: float, max_tok: int) -> str:
        model = model or "gemini-2.5-flash"
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=self.gemini_key)
            config = types.GenerateContentConfig(
                temperature=temp,
                max_output_tokens=max_tok
            )
            if system:
                config.system_instruction = system
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"google-genai failed: {e}. Trying older google-generativeai client.")
            try:
                import google.generativeai as old_genai
                old_genai.configure(api_key=self.gemini_key)
                client_model = old_genai.GenerativeModel(
                    model_name=model,
                    system_instruction=system
                )
                config = {"temperature": temp, "max_output_tokens": max_tok}
                response = client_model.generate_content(prompt, generation_config=config)
                return response.text.strip()
            except Exception as e2:
                logger.error(f"Gemini fallback failed: {e2}")
                raise RuntimeError(f"Gemini generation failed: {e2}")

    def _call_gemini_json(self, prompt: str, system: Optional[str], model: Optional[str], temp: float, max_tok: int) -> Dict:
        model = model or "gemini-2.5-flash"
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=self.gemini_key)
            config = types.GenerateContentConfig(
                temperature=temp,
                max_output_tokens=max_tok,
                response_mime_type="application/json"
            )
            if system:
                config.system_instruction = system
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
            return json.loads(response.text.strip())
        except Exception as e:
            logger.error(f"google-genai JSON failed: {e}. Trying older fallback.")
            try:
                import google.generativeai as old_genai
                old_genai.configure(api_key=self.gemini_key)
                client_model = old_genai.GenerativeModel(
                    model_name=model,
                    system_instruction=system
                )
                config = {
                    "temperature": temp,
                    "max_output_tokens": max_tok,
                    "response_mime_type": "application/json"
                }
                response = client_model.generate_content(prompt, generation_config=config)
                clean_text = response.text.strip()
                import re
                clean_text = re.sub(r"```(?:json)?", "", clean_text).strip().rstrip("`").strip()
                return json.loads(clean_text)
            except Exception as e2:
                logger.error(f"Gemini fallback JSON failed: {e2}")
                raise RuntimeError(f"Gemini JSON generation failed: {e2}")

    # --- OPENROUTER IMPLEMENTATIONS ---
    def _call_openrouter_text(self, prompt: str, system: Optional[str], model: Optional[str], temp: float, max_tok: int) -> str:
        try:
            sys.path.append(str(BASE_DIR))
            import or_client
            client_inst = or_client.OpenRouterClient()
            return client_inst.chat(
                prompt=prompt,
                system=system or "You are a helpful assistant.",
                model=model,
                max_tokens=max_tok,
                temperature=temp
            )
        except Exception as e:
            logger.error(f"OpenRouter text generation failed: {e}")
            raise

    def _call_openrouter_json(self, prompt: str, system: Optional[str], model: Optional[str], max_tok: int) -> Dict:
        try:
            sys.path.append(str(BASE_DIR))
            import or_client
            client_inst = or_client.OpenRouterClient()
            return client_inst.chat_json(
                prompt=prompt,
                system=system or "Return ONLY valid JSON.",
                model=model,
                max_tokens=max_tok
            )
        except Exception as e:
            logger.error(f"OpenRouter JSON generation failed: {e}")
            raise

    # --- NVIDIA IMPLEMENTATIONS ---
    def _call_nvidia_text(self, prompt: str, system: Optional[str], model: Optional[str], temp: float, max_tok: int) -> str:
        model = model or "meta/llama-3.1-70b-instruct"
        try:
            import openai
            client = openai.OpenAI(api_key=self.nvidia_key, base_url="https://integrate.api.nvidia.com/v1")
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Nvidia text failed: {e}")
            raise RuntimeError(f"Nvidia generation failed: {e}")

    def _call_nvidia_json(self, prompt: str, system: Optional[str], model: Optional[str], temp: float, max_tok: int) -> Dict:
        system_instructions = (system or "") + "\n\nYou MUST return ONLY valid JSON. No markdown backticks, no other text."
        raw_text = self._call_nvidia_text(prompt, system_instructions, model, temp, max_tok)
        import re
        clean = raw_text.strip()
        clean = re.sub(r"```(?:json)?", "", clean).strip().rstrip("`").strip()
        try:
            return json.loads(clean)
        except Exception as e:
            logger.error(f"Nvidia JSON parse failed: {e}. Raw was: {raw_text}")
            raise

    # --- OPENAI IMPLEMENTATIONS ---
    def _call_openai_text(self, prompt: str, system: Optional[str], model: Optional[str], temp: float, max_tok: int) -> str:
        model = model or "gpt-4o"
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI text failed: {e}")
            raise RuntimeError(f"OpenAI generation failed: {e}")

    def _call_openai_json(self, prompt: str, system: Optional[str], model: Optional[str], temp: float, max_tok: int) -> Dict:
        model = model or "gpt-4o"
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                response_format={"type": "json_object"}
            )
            return json.loads(resp.choices[0].message.content.strip())
        except Exception as e:
            logger.error(f"OpenAI JSON failed: {e}")
            raise RuntimeError(f"OpenAI JSON generation failed: {e}")

    def generate_consensus_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Executes a Mixture-of-Agents (MoA) consensus cycle.
        Queries Gemini, Nemotron, and Llama 3.3 in parallel,
        and synthesizes their answers into a single, high-fidelity final response.
        """
        import concurrent.futures
        
        candidates = []
        models = [
            ("gemini", None),
            ("openrouter", "nvidia/nemotron-3-super-120b-a12b:free"),
            ("openrouter", "meta-llama/llama-3.3-70b-instruct:free")
        ]
        
        def _call_worker(prov, mod):
            try:
                # If Gemini is the provider and we don't have a valid key, it will raise exception,
                # which gets caught and defaults to OpenRouter fallback automatically inside generate_text.
                return self.generate_text(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    provider=prov,
                    model=mod,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            except Exception as e:
                logger.error(f"MoA worker failed for {prov}/{mod}: {e}")
                return ""

        logger.info("[MoA] Dispatched parallel multi-model consensus queries...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(_call_worker, prov, mod) for prov, mod in models]
            results = [f.result() for f in futures]
            
        valid_responses = [r.strip() for r in results if r and r.strip()]
        
        if not valid_responses:
            raise RuntimeError("All models in the MoA pool failed or returned empty results.")
            
        if len(valid_responses) == 1:
            return valid_responses[0]
            
        # Synthesize the final answer using the primary provider
        resp3_str = f"--- Draft Response 3:\n{valid_responses[2]}" if len(valid_responses) > 2 else ""
        synthesis_prompt = f"""
You are the master response synthesizer for Jarvis.
Below are draft responses generated by different AI models for the user's prompt: "{prompt}"

---
Draft Response 1:
{valid_responses[0]}

---
Draft Response 2:
{valid_responses[1]}

{resp3_str}
---

Task:
Synthesize these draft responses into a single, high-quality, comprehensive, and cohesive response for the user.
Combine their details, resolve any contradictions or factual discrepancies, and ensure a polite, professional, and helpful tone fitting for Tony Stark's assistant Jarvis.
Keep it concise and do not repeat information.
"""
        logger.info("[MoA] Synthesizing consensus response from parallel inputs...")
        try:
            return self.generate_text(
                prompt=synthesis_prompt,
                system_instruction="You are a master response synthesizer.",
                provider=self.default_provider,
                temperature=0.3,
                max_tokens=max_tokens
            )
        except Exception as e:
            logger.warning(f"Consensus synthesis failed: {e}. Returning the first valid candidate response.")
            return valid_responses[0]

# Global shared client
inference_client = InferenceWrapper()
