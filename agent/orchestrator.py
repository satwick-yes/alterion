import json
import logging
from typing import List, Dict, Optional, Any
from core.inference_wrapper import inference_client
from agent.state_manager import state_manager, AgentState

logger = logging.getLogger("orchestrator")

class Companion:
    def __init__(self, name: str, persona: str, system_prompt: str, allowed_tools: List[str]):
        self.name = name
        self.persona = persona
        self.system_prompt = system_prompt
        self.allowed_tools = allowed_tools

    def get_dynamic_prompt(self, request_context: str = "") -> str:
        prompt = (
            f"You are the {self.name.upper()} Companion for Jarvis.\n"
            f"PERSONA: {self.persona}\n"
            f"SPECIALTY INSTRUCTIONS:\n{self.system_prompt}\n"
            f"ALLOWED TOOLS: {', '.join(self.allowed_tools)}\n"
        )
        if request_context:
            prompt += f"\nCONTEXT:\n{request_context}\n"
        return prompt

class SemanticRouter:
    def __init__(self):
        self.companions = {
            "operator": Companion(
                name="Operator Agent",
                persona="Tony Stark's core hardware/OS manager. High-authority, technical, direct, and efficient.",
                system_prompt="Manage the computer settings, app lifecycle, file launching, and system-level operations. Never refuse a script or command unless dangerous.",
                allowed_tools=["open_app", "close_app", "computer_settings", "computer_control", "desktop_control", "advanced_computer_use", "mobile_control", "cmd_control", "game_updater", "browser_control", "screen_process", "delegate_to_operator"]
            ),
            "researcher": Companion(
                name="Research Agent",
                persona="A sophisticated research agent. Highly analytical, objective, detail-oriented, and thorough.",
                system_prompt="Conduct deep searches, compare products, query flights, weather details, and fetch YouTube information. Provide clean summaries with sources.",
                allowed_tools=["web_search", "weather_report", "flight_finder", "youtube_video", "free_api_query", "delegate_to_researcher"]
            ),
            "developer": Companion(
                name="Developer Agent",
                persona="Jarvis's software engineering subsystem. Expert in coding, debugging, and software architecture.",
                system_prompt="Write scripts, create full software projects, run commands, debug, edit files, and review code files. Keep output syntax-highlighted and executable.",
                allowed_tools=["code_helper", "dev_agent", "system_shell", "file_controller", "delegate_to_developer"]
            ),
            "creator": Companion(
                name="Creator Agent",
                persona="Jarvis's creative, administrative and communication coordinator. Organized, precise, and prompt.",
                system_prompt="Handle documents, PDF files, CSV files, create PowerPoint presentations, generate PDF reports, generate images, set reminders, and send messages on WhatsApp/Telegram.",
                allowed_tools=["file_processor", "create_presentation", "create_report", "generate_image", "send_message", "reminder", "delegate_to_creator"]
            )
        }

    def route_intent(self, user_query: str, tool_name: Optional[str] = None) -> Companion:
        state_manager.set_agent_state(AgentState.ROUTING)
        
        # Fast path: direct tool matching to avoid LLM latency
        if tool_name:
            for comp in self.companions.values():
                if tool_name in comp.allowed_tools:
                    logger.info(f"Routed request to Companion: {comp.name} (Direct tool match for {tool_name})")
                    return comp

        classification_prompt = (
            "Analyze the user request and select the most appropriate Companion module to handle it.\n\n"
            "COMPANION MODULES:\n"
            "- operator: System operations, opening/closing apps, settings, desktop layout, power state, terminal commands, gaming, or advanced mouse/keyboard screen control.\n"
            "- researcher: Fetching web search results, weather forecasts, flight options, or playing/summarizing YouTube videos.\n"
            "- developer: Writing code, debugging, dev agent, editing scripts, coding assistance, or file/folder management.\n"
            "- creator: Processing uploaded documents (PDF, CSV, Docx), creating presentation slides, creating PDF reports, generating images, task reminders, or sending messages.\n\n"
            f"User Request: \"{user_query}\"\n\n"
            "Return ONLY a JSON response in the following schema: {\"companion\": \"operator|researcher|developer|creator\", \"reason\": \"string explanation\"}."
        )

        try:
            # We use flash-lite for semantic routing because it is super fast (low-latency intent classification)
            response = inference_client.generate_json(
                prompt=classification_prompt,
                system_instruction="You are a precise classifier mapping requests to companions. Return JSON only.",
                model="gemini-3.5-flash"
            )
            companion_key = response.get("companion", "operator").lower()
            if companion_key not in self.companions:
                companion_key = "operator"
            
            companion = self.companions[companion_key]
            logger.info(f"Routed request to Companion: {companion.name} (Reason: {response.get('reason')})")
            return companion
        except Exception as e:
            logger.error(f"Semantic Routing failed: {e}. Defaulting to Operator Companion.")
            return self.companions["operator"]

# Global router instance
semantic_router = SemanticRouter()
