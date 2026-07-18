import asyncio
import threading
import uuid
import logging
from typing import List, Dict, Any
from core.inference_wrapper import inference_client
from agent.state_manager import state_manager, TaskState
from agent.orchestrator import Companion

logger = logging.getLogger("multi_agent")

class WorkerBot:
    def __init__(self, task_id: str, role: str, instruction: str, tool: str, args: Dict[str, Any]):
        self.worker_id = str(uuid.uuid4())[:8]
        self.task_id = task_id
        self.role = role
        self.instruction = instruction
        self.tool = tool
        self.args = args
        self.result = ""
        self.status = "pending"

    async def execute(self):
        self.status = "running"
        state_manager.register_worker(self.worker_id, self.task_id, self.role)
        logger.info(f"[WorkerBot {self.worker_id}] Starting task: {self.instruction}")
        
        try:
            # Import call_tool dynamically from executor to avoid circular dependencies
            from agent.executor import _call_tool
            # Run the tool blocking call in a separate thread pool executor so it doesn't block the async loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: _call_tool(self.tool, self.args, None)
            )
            self.result = result
            self.status = "completed"
            state_manager.unregister_worker(self.worker_id, "completed")
            logger.info(f"[WorkerBot {self.worker_id}] Task completed successfully.")
        except Exception as e:
            self.result = f"Error: {e}"
            self.status = "failed"
            state_manager.unregister_worker(self.worker_id, f"failed: {e}")
            logger.error(f"[WorkerBot {self.worker_id}] Task failed: {e}")

class MultiAgentFramework:
    def __init__(self):
        pass

    def check_is_complex(self, goal: str) -> bool:
        """
        Quick check if the goal is complex enough to merit parallel workers.
        """
        # If the goal asks to compare multiple items, do research on multiple topics,
        # or do multi-step operations, it's complex.
        prompt = (
            f"Is the following user task complex and multi-faceted, requiring multiple parallel sub-tasks? "
            f"(e.g., researching multiple competitors, comparing multiple prices, analyzing and writing concurrently)\n"
            f"Task: \"{goal}\"\n\n"
            "Reply with YES or NO."
        )
        try:
            res = inference_client.generate_text(
                prompt=prompt,
                system_instruction="Reply only YES or NO.",
                model="gemini-2.5-flash",
                temperature=0.0
            )
            return "YES" in res.upper()
        except Exception:
            return False

    def decompose_task(self, task_id: str, goal: str, companion: Companion) -> List[WorkerBot]:
        """
        Decomposes a complex task into multiple sub-tasks that can be executed in parallel.
        """
        decomposition_prompt = (
            f"Decompose the following user goal into up to 3 parallel, independent sub-tasks.\n"
            f"Each sub-task must be designed to run as an independent bot worker.\n\n"
            f"Goal: \"{goal}\"\n"
            f"Companion handling this: {companion.name}\n\n"
            "AVAILABLE TOOLS (Choose the correct tool name from this list for each bot):\n"
            "- web_search (query: string)\n"
            "- file_controller (action: 'read'|'write'|'create_file'|'list', path: string, name: string, content: string)\n"
            "- cmd_control (task: string)\n"
            "- code_helper (action: 'write'|'run'|'edit', description: string)\n"
            "- weather_report (city: string)\n"
            "- flight_finder (origin: string, destination: string, date: string)\n"
            "- youtube_video (action: 'play'|'summarize'|'trending', query: string)\n\n"
            "Return ONLY a JSON response in the following schema:\n"
            "{\n"
            "  \"sub_tasks\": [\n"
            "    {\n"
            "      \"role\": \"Role name for the bot (e.g. Competitor X Researcher)\",\n"
            "      \"instruction\": \"Specific objective for this sub-task\",\n"
            "      \"tool\": \"tool_name\",\n"
            "      \"args\": { \"param_name\": \"value\" }\n"
            "    }\n"
            "  ]\n"
            "}"
        )

        try:
            response = inference_client.generate_json(
                prompt=decomposition_prompt,
                system_instruction="You are a decomposition expert. Return only JSON schema.",
                model="gemini-2.5-flash"
            )
            sub_tasks = response.get("sub_tasks", [])
            workers = []
            for st in sub_tasks:
                workers.append(WorkerBot(
                    task_id=task_id,
                    role=st.get("role", "WorkerBot"),
                    instruction=st.get("instruction", ""),
                    tool=st.get("tool", "web_search"),
                    args=st.get("args", {})
                ))
            return workers
        except Exception as e:
            logger.error(f"Task decomposition failed: {e}")
            # Fallback worker
            return [WorkerBot(
                task_id=task_id,
                role="Fallback Searcher",
                instruction=f"Research: {goal}",
                tool="web_search",
                args={"query": goal}
            )]

    async def execute_complex_task(self, task_id: str, goal: str, companion: Companion) -> str:
        """
        Runs the multi-agent task execution loop:
        1. Decomposes the goal into sub-tasks.
        2. Spawns parallel worker bots.
        3. Awaits completion of all workers.
        4. Synthesizes their results.
        """
        workers = self.decompose_task(task_id, goal, companion)
        logger.info(f"Decomposed task into {len(workers)} parallel workers.")
        
        # Execute all workers concurrently
        await asyncio.gather(*(w.execute() for w in workers))
        
        # Synthesize results
        logger.info("Aggregating parallel bot worker outputs.")
        synthesis_prompt = (
            f"You are the supervising companion ({companion.name}) synthesizing the outputs of parallel bot workers.\n"
            f"Original Goal: \"{goal}\"\n\n"
            "BOT WORKER OUTPUTS:\n"
        )
        for i, w in enumerate(workers):
            synthesis_prompt += f"Bot {i+1} ({w.role}):\n- Instruction: {w.instruction}\n- Result:\n{w.result}\n\n"
            
        synthesis_prompt += "Synthesize these results into a highly structured, professional final response for the user. Highlight sources and data clearly. Address the user as 'sir'."

        try:
            final_report = inference_client.generate_text(
                prompt=synthesis_prompt,
                system_instruction=companion.get_dynamic_prompt()
            )
            return final_report
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return f"Sir, I completed the parallel sub-tasks but encountered an error synthesizing the final report: {e}"

# Global multi-agent framework instance
multi_agent_framework = MultiAgentFramework()
