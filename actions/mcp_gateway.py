import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger("mcp_gateway")

# The real Composio user ID (from connected accounts)
COMPOSIO_USER_ID = "pg-test-fff375f1-e417-4ece-ba16-594be3c4ab6a"

# Map from common server names Vani might say → actual Composio toolkit slugs
TOOLKIT_SLUG_MAP = {
    "google_workspace": "gmail",
    "gmail":            "gmail",
    "mail":             "gmail",
    "email":            "gmail",
    "github":           "github",
    "outlook":          "outlook",
    "googledrive":      "googledrive",
    "drive":            "googledrive",
    "google_drive":     "googledrive",
    "youtube":          "youtube",
    "discord":          "discord",
}

# The only apps Vani is allowed to access via Composio
ALLOWED_COMPOSIO_APPS = [
    "gmail",
    "github",
    "outlook",
    "googledrive",
    "youtube",
    "discord",
]

class MCPGateway:
    def __init__(self):
        self.composio_api_key = self._get_composio_key()
        self._keys_cache = {}
        
        # Sensitive action registry
        self.registry = {
            "gmail":           {"category": "Personal Email", "sensitive": False},
            "google_workspace":{"category": "Personal Email", "sensitive": False},
            "mail":            {"category": "Personal Email", "sensitive": False},
            "email":           {"category": "Personal Email", "sensitive": False},
            "outlook":         {"category": "Personal Email", "sensitive": False},
            "github":          {"category": "DevOps", "sensitive": True},
            "googledrive":     {"category": "Cloud Storage", "sensitive": False},
            "drive":           {"category": "Cloud Storage", "sensitive": False},
            "google_drive":    {"category": "Cloud Storage", "sensitive": False},
            "youtube":         {"category": "Entertainment", "sensitive": False},
            "discord":         {"category": "Communication", "sensitive": False},
        }

    def _get_composio_key(self):
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "api_keys.json")
            with open(config_path, "r", encoding="utf-8") as f:
                keys = json.load(f)
                return keys.get("composio_api_key", "")
        except:
            return ""

    def _load_keys(self):
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "api_keys.json")
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def execute_action(self, server: str, action: str, payload: Any, authorized: bool = False) -> Dict[str, Any]:
        """
        Contextual dispatch for Composio MCP servers.
        """
        server_key = server.lower().strip()
        
        # Resolve to real Composio toolkit slug
        toolkit_slug = TOOLKIT_SLUG_MAP.get(server_key, server_key)
        
        # Guard against unauthorized apps
        if toolkit_slug not in ALLOWED_COMPOSIO_APPS:
            return {
                "status": "error",
                "message": f"Action on '{toolkit_slug}' is not supported. Allowed apps are: {', '.join(ALLOWED_COMPOSIO_APPS)}."
            }
            
        server_info = self.registry.get(server_key, self.registry.get(toolkit_slug, {"category": "Unknown", "sensitive": False}))

        # 1. Sensitive action authorization check
        is_sensitive = server_info.get("sensitive", False)
        if is_sensitive and not authorized:
            logger.warning(f"[MCP Gateway] ⚠️ Authorization required for sensitive action on '{toolkit_slug}'.")
            return {
                "status": "authorization_required",
                "message": f"AUTHORIZATION REQUIRED: Do you authorize this action on {server_info['category']} ({toolkit_slug})?"
            }

        # 2. Check for Composio setup
        composio_key = self._get_composio_key()
        if not composio_key:
            return {
                "status": "error",
                "message": "Composio API key is not set. Please update config/api_keys.json."
            }

        logger.info(f"[MCP Gateway] 🚀 Executing '{action}' on '{toolkit_slug}' via Composio (user: {COMPOSIO_USER_ID}).")

        try:
            from composio import Composio
            import openai

            composio_client = Composio(api_key=composio_key)
            
            # Get tools for this specific toolkit and user
            tools = composio_client.tools.get(
                user_id=COMPOSIO_USER_ID,
                toolkits=[toolkit_slug]
            )
            
            if not tools:
                return {
                    "status": "error",
                    "message": f"No tools found for toolkit '{toolkit_slug}'. Make sure it's connected in Composio dashboard."
                }

            # Load OpenRouter key for LLM tool selection
            keys = self._load_keys()
            or_key = keys.get("openrouter_api_key", "")
                
            if not or_key:
                return {"status": "error", "message": "OpenRouter API key required to dispatch Composio actions."}
                
            client = openai.OpenAI(api_key=or_key, base_url="https://openrouter.ai/api/v1")
            
            prompt = f"User wants to: '{action}'. Additional payload/context: {payload}"
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that selects and calls the right tool for the user's request. You must call a tool."},
                    {"role": "user", "content": prompt}
                ],
                tools=tools,
                tool_choice="required",
                max_tokens=1000
            )
            
            message = response.choices[0].message
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"[MCP Gateway] 🔧 Calling Composio tool: {tool_name} with {tool_args}")
                
                # Execute the tool via Composio for this user
                res = composio_client.tools.execute(
                    slug=tool_name,
                    arguments=tool_args,
                    user_id=COMPOSIO_USER_ID,
                    dangerously_skip_version_check=True
                )
                
                # Unpack result
                if hasattr(res, 'data'):
                    result_data = res.data
                elif hasattr(res, 'model_dump'):
                    result_data = res.model_dump()
                else:
                    result_data = str(res)
                    
                return {
                    "status": "success",
                    "server": toolkit_slug,
                    "action_performed": action,
                    "composio_tool": tool_name,
                    "result_data": result_data
                }
            else:
                return {
                    "status": "error",
                    "message": f"Could not find the right tool for: '{action}'. LLM response: {message.content}"
                }
        except Exception as e:
            logger.error(f"[MCP Gateway] ❌ {e}")
            return {
                "status": "error",
                "message": f"Composio execution failed: {str(e)}"
            }

# Global MCP Gateway instance
mcp_gateway_instance = MCPGateway()
