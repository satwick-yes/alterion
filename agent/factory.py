import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("agent_factory")

class AgentFactory:
    """
    Loads agent configurations from the JSON registry and builds WorkerBots.
    Acts as the 'Company Brain' index.
    """
    def __init__(self):
        self.registry_dir = os.path.join(os.path.dirname(__file__), "registry")
        self.departments = {}
        self.all_agents = {}
        self._load_registry()

    def _load_registry(self):
        if not os.path.exists(self.registry_dir):
            logger.warning(f"Registry directory not found: {self.registry_dir}")
            return
            
        for filename in os.listdir(self.registry_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.registry_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        dept_name = data.get("department", filename.replace(".json", ""))
                        self.departments[dept_name] = data.get("agents", [])
                        
                        # Populate flat lookup
                        for agent in data.get("agents", []):
                            self.all_agents[str(agent["id"])] = agent
                except Exception as e:
                    logger.error(f"Failed to load registry {filename}: {e}")
                    
        logger.info(f"AgentFactory loaded {len(self.all_agents)} specialized agents across {len(self.departments)} departments.")

    def get_agent_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self.all_agents.get(str(agent_id))
        
    def find_best_agent(self, query: str) -> Optional[Dict[str, Any]]:
        """
        A naive semantic match for the prototype. 
        In production, this would use embeddings or an LLM Router.
        """
        query_lower = query.lower()
        best_match = None
        highest_score = 0
        
        for agent_id, agent in self.all_agents.items():
            score = 0
            if agent["name"].lower() in query_lower:
                score += 10
            if any(word in agent["description"].lower() for word in query_lower.split()):
                score += 1
                
            if score > highest_score:
                highest_score = score
                best_match = agent
                
        return best_match

    def create_worker_bot(self, agent_id: str, task_id: str, goal: str):
        """
        Creates a Vani WorkerBot instance pre-configured with the agent's specific prompt.
        """
        from agent.multi_agent import WorkerBot
        
        config = self.get_agent_config(agent_id)
        if not config:
            raise ValueError(f"Agent ID {agent_id} not found in registry.")
            
        # Bind the specialized system prompt and tools
        return WorkerBot(
            task_id=task_id,
            role=config["role"],
            instruction=f"{config['system_prompt']} Your specific goal: {goal}",
            tool=config["tools_required"][0] if config["tools_required"] else "web_search", 
            args={"query": goal} # Placeholder args mapping
        )

# Global factory instance
agent_factory = AgentFactory()
