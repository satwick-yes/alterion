import logging
from core.inference_wrapper import inference_client
from memory.memory_manager import format_chat_history_for_prompt

logger = logging.getLogger("llm_brains")

def run_llm_brain(provider: str, task: str, player=None) -> str:
    """Generic executor for the specialized LLM brains."""
    try:
        chat_hist = format_chat_history_for_prompt(limit=10)
        sys_prompt = f"You are the {provider.upper()} specialized sub-brain of Vani. Solve the following task precisely.\n\n{chat_hist}"
        response = inference_client.generate_text(
            prompt=task,
            system_instruction=sys_prompt,
            provider=provider
        )
        output = f"[{provider.upper()} Brain Output]\n{response}"
        if player:
            player.write_log(f"🧠 {provider.upper()} Brain Output:\n{response}")
        return output
    except Exception as e:
        logger.error(f"Error in {provider} brain: {e}")
        return f"Error: {provider} brain failed to complete the task. Details: {e}"

def run_gemini_brain(parameters: dict, player=None) -> str:
    return run_llm_brain("gemini", parameters.get("task", ""), player=player)

def run_openrouter_brain(parameters: dict, player=None) -> str:
    return run_llm_brain("openrouter", parameters.get("task", ""), player=player)

def run_nvidia_brain(parameters: dict, player=None) -> str:
    return run_llm_brain("nvidia", parameters.get("task", ""), player=player)

def run_openai_brain(parameters: dict, player=None) -> str:
    return run_llm_brain("openai", parameters.get("task", ""), player=player)

def run_groq_brain(parameters: dict, player=None) -> str:
    return run_llm_brain("groq", parameters.get("task", ""), player=player)

def run_deepseek_brain(parameters: dict, player=None) -> str:
    return run_llm_brain("deepseek", parameters.get("task", ""), player=player)

def run_cerebras_brain(parameters: dict, player=None) -> str:
    return run_llm_brain("cerebras", parameters.get("task", ""), player=player)

def run_mistral_brain(parameters: dict, player=None) -> str:
    return run_llm_brain("mistral", parameters.get("task", ""), player=player)

def run_sambanova_brain(parameters: dict, player=None) -> str:
    return run_llm_brain("sambanova", parameters.get("task", ""), player=player)
