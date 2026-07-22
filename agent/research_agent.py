import logging
from typing import Dict, Any

logger = logging.getLogger("research_agent")

class ResearchAgent:
    """
    Role: Web & Data gathering.
    Tools: web_search, flight_finder, weather_report, youtube_video, free_api_query
    """
    def __init__(self):
        self.allowed_tools = [
            "web_search", "flight_finder", "weather_report", 
            "youtube_video", "free_api_query"
        ]
        
    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        logger.info(f"ResearchAgent executing {tool_name} with args {args}")
        return f"ResearchAgent executed {tool_name}"
