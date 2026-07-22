import threading
import time
import json
from pathlib import Path
from enum import Enum
import sys

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
STATE_LOG_PATH = BASE_DIR / "agent" / "state_log.json"

class AgentState(Enum):
    IDLE = "idle"
    ROUTING = "routing"
    PLANNING = "planning"
    EXECUTING = "executing"
    SPEAKING = "speaking"
    ERROR = "error"

class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StateManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.agent_state = AgentState.IDLE
        self.current_task_id = None
        self.tasks = {}
        self.active_workers = {}
        self.on_state_change = None
        self._load_state_log()

    def _load_state_log(self):
        try:
            if STATE_LOG_PATH.exists():
                with open(STATE_LOG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.tasks = data.get("tasks", {})
        except Exception:
            pass

    def _save_state_log(self):
        try:
            STATE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(STATE_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump({"tasks": self.tasks}, f, indent=2)
        except Exception:
            pass

    def set_agent_state(self, state: AgentState):
        with self._lock:
            self.agent_state = state
            print(f"[StateManager] Agent state changed to: {state.value.upper()}")
            if self.on_state_change:
                try:
                    self.on_state_change(state.value.upper())
                except Exception:
                    pass

    def get_agent_state(self) -> AgentState:
        with self._lock:
            return self.agent_state

    def register_task(self, task_id: str, goal: str):
        with self._lock:
            self.tasks[task_id] = {
                "task_id": task_id,
                "goal": goal,
                "status": TaskState.PENDING.value,
                "start_time": time.time(),
                "end_time": None,
                "steps": [],
                "workers": []
            }
            self.current_task_id = task_id
            self._save_state_log()
            print(f"[StateManager] Task {task_id} registered: '{goal[:50]}...'")

    def update_task_status(self, task_id: str, status: TaskState, error_msg: str = ""):
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = status.value
                if status in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
                    self.tasks[task_id]["end_time"] = time.time()
                if error_msg:
                    self.tasks[task_id]["error"] = error_msg
                self._save_state_log()
                print(f"[StateManager] Task {task_id} status updated to: {status.value.upper()}")

    def add_task_step(self, task_id: str, step_num: int, tool: str, description: str):
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id]["steps"].append({
                    "step": step_num,
                    "tool": tool,
                    "description": description,
                    "status": "running",
                    "start_time": time.time(),
                    "end_time": None
                })
                self._save_state_log()

    def update_task_step_status(self, task_id: str, step_num: int, status: str, result: str = ""):
        with self._lock:
            if task_id in self.tasks:
                for step in self.tasks[task_id]["steps"]:
                    if step["step"] == step_num:
                        step["status"] = status
                        step["end_time"] = time.time()
                        if result:
                            step["result"] = result[:200]
                        self._save_state_log()
                        break

    def register_worker(self, worker_id: str, task_id: str, role: str):
        with self._lock:
            self.active_workers[worker_id] = {
                "worker_id": worker_id,
                "task_id": task_id,
                "role": role,
                "status": "active",
                "start_time": time.time()
            }
            if task_id in self.tasks:
                self.tasks[task_id]["workers"].append(worker_id)
                self._save_state_log()
            print(f"[StateManager] Worker {worker_id} ({role}) spawned for task {task_id}")

    def unregister_worker(self, worker_id: str, status: str = "completed"):
        with self._lock:
            if worker_id in self.active_workers:
                self.active_workers[worker_id]["status"] = status
                self.active_workers[worker_id]["end_time"] = time.time()
                del self.active_workers[worker_id]
                print(f"[StateManager] Worker {worker_id} terminated with status: {status}")

    def get_task_details(self, task_id: str) -> dict:
        with self._lock:
            return self.tasks.get(task_id, {})

    def get_all_active_workers(self) -> dict:
        with self._lock:
            return dict(self.active_workers)

state_manager = StateManager()
