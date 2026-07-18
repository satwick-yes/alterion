import json
import logging
from pathlib import Path
import sys

logger = logging.getLogger("integration_gateway")

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
OAUTH_PATH = BASE_DIR / "config" / "oauth_tokens.json"

class IntegrationGateway:
    def __init__(self):
        self.tokens = {}
        self._load_tokens()
        
        # Hardcoded list of default companion tool permissions to enforce security policies
        self.permissions = {
            "System & Control": [
                "open_app", "close_app", "computer_settings", 
                "computer_control", "desktop_control", "system_shell", 
                "advanced_computer_use", "mobile_control"
            ],
            "Research & Intelligence": [
                "web_search", "weather_report", "flight_finder", 
                "youtube_video", "open_app", "computer_control", "advanced_computer_use"
            ],
            "Developer Core": [
                "code_helper", "dev_agent", "system_shell", "open_app", "computer_control", "advanced_computer_use"
            ],
            "Office & Productivity": [
                "file_controller", "file_processor", "create_presentation", 
                "create_report", "reminder", "open_app", "computer_control", "advanced_computer_use"
            ],
            "Communication": [
                "send_message"
            ]
        }

    def _load_tokens(self):
        try:
            if OAUTH_PATH.exists():
                with open(OAUTH_PATH, "r", encoding="utf-8") as f:
                    self.tokens = json.load(f)
            else:
                # Initialize with mock tokens for demonstration
                self.tokens = {
                    "google_oauth": {
                        "access_token": "ya29.a0AfH6SMD_mock_token_gmail",
                        "refresh_token": "1//0g_mock_refresh",
                        "scope": "https://www.googleapis.com/auth/gmail.send"
                    },
                    "hubspot_oauth": {
                        "access_token": "pat-na1-mock-hubspot-token",
                        "scope": "contacts"
                    }
                }
                self._save_tokens()
        except Exception as e:
            logger.error(f"[IntegrationGateway] Failed to load OAuth tokens: {e}")

    def _save_tokens(self):
        try:
            OAUTH_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(OAUTH_PATH, "w", encoding="utf-8") as f:
                json.dump(self.tokens, f, indent=2)
        except Exception as e:
            logger.error(f"[IntegrationGateway] Failed to save OAuth tokens: {e}")

    def get_oauth_token(self, service: str) -> str:
        service_key = f"{service.lower()}_oauth"
        if service_key in self.tokens:
            return self.tokens[service_key].get("access_token", "")
        # Standard alias mappings
        if service.lower() == "gmail":
            return self.tokens.get("google_oauth", {}).get("access_token", "")
        if service.lower() == "hubspot":
            return self.tokens.get("hubspot_oauth", {}).get("access_token", "")
        return ""

    def verify_tool_permission(self, companion_name: str, tool_name: str) -> bool:
        """
        Verify if the given companion agent has permissions to execute the requested tool.
        """
        # If no companion_name is specified (e.g. running outside orchestrator), allow it
        if not companion_name:
            return True
            
        allowed_tools = self.permissions.get(companion_name, [])
        # Always allow system sleep, memory saving, and general free API queries
        if tool_name in ["go_to_sleep", "save_memory", "shutdown_jarvis", "free_api_query"]:
            return True
            
        is_allowed = tool_name in allowed_tools
        if not is_allowed:
            logger.warning(
                f"[IntegrationGateway] 🚫 PERMISSION DENIED: Companion '{companion_name}' "
                f"is not authorized to use tool '{tool_name}'"
            )
        else:
            logger.info(f"[IntegrationGateway] ✓ PERMISSION VERIFIED: '{companion_name}' -> '{tool_name}'")
        return is_allowed

    def execute_oauth_api_call(self, service: str, endpoint: str, payload: dict) -> dict:
        """
        Interceptors standard REST API requests requiring external OAuth tokens.
        """
        token = self.get_oauth_token(service)
        if not token:
            raise PermissionError(f"OAuth credentials for service '{service}' are missing or expired.")
            
        logger.info(
            f"[IntegrationGateway] Intercepted call to '{service}'. "
            f"Verifying OAuth Token: {token[:12]}..."
        )
        
        # Simulate successful external API response
        logger.info(f"[IntegrationGateway] Executing REST API call to {service} {endpoint}...")
        return {
            "status": "success",
            "message": f"Successfully performed integration action via simulated OAuth for {service}.",
            "data": payload
        }

# Global integration gateway instance
integration_gateway = IntegrationGateway()
