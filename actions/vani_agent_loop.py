"""
vani_agent_loop.py — V.A.N.I. Autonomous GUI Agent Loop

The closed-loop agentic computer control engine for V.A.N.I.:

  LOOP:
    1. generate_screen_state()         <- ui_detr.py (Gemini Vision)
    2. build_per_turn_prompt()         <- inject goal + history + screen state
    3. llm_reason()                    <- Groq/Gemini fast LLM -> strict JSON action
    4. dispatch_action()               <- PyAutoGUI physical execution
    5. append to action_history
    6. if DONE or max_steps reached -> return

The reasoning LLM uses the exact system prompt and per-turn template
specified in the V.A.N.I. design document.
"""

import json
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    _PYAUTOGUI_OK = True
except ImportError:
    _PYAUTOGUI_OK = False

try:
    import pyperclip
    _PYPERCLIP_OK = True
except ImportError:
    _PYPERCLIP_OK = False


# ── Base dir ──────────────────────────────────────────────────────────────────
def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()


def _load_keys() -> dict:
    try:
        with open(BASE_DIR / "config" / "api_keys.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT — Reasoning LLM
# ══════════════════════════════════════════════════════════════════════════════
_REASONING_SYSTEM_PROMPT = """You are V.A.N.I., an autonomous multimodal AI agent with direct physical control over an operating system. You operate software interfaces by analyzing screen states and issuing precise physical input actions.

### OPERATIONAL CYCLE
You operate in a continuous closed loop:
1. Review the User Goal.
2. Analyze the Action History to verify the outcome of previous steps.
3. Inspect the current Screen State (parsed UI elements and coordinates).
4. Reason step-by-step about what must happen next.
5. Issue exactly ONE action command per turn in strict JSON format.

### AVAILABLE ACTIONS
- CLICK: Move cursor to coordinates and execute a single left-click.
  Parameters: {"x": integer, "y": integer}
- DOUBLE_CLICK: Move cursor and double-click (useful for opening desktop icons or selecting words).
  Parameters: {"x": integer, "y": integer}
- RIGHT_CLICK: Context menu trigger.
  Parameters: {"x": integer, "y": integer}
- TYPE: Click a target field, focus it, and enter text.
  Parameters: {"x": integer, "y": integer, "text": "string"}
- KEY_COMBINATION: Execute hotkeys or special keyboard shortcuts (e.g., Enter, Ctrl+A, Backspace, Esc).
  Parameters: {"keys": ["ctrl", "t"] or ["enter"]}
- SCROLL_DOWN: Scroll the active viewport downward to reveal more content.
  Parameters: {"amount": integer} (default 500)
- SCROLL_UP: Scroll the active viewport upward.
  Parameters: {"amount": integer} (default 500)
- WAIT: Pause execution to allow animations, network calls, or software loads to complete.
  Parameters: {"seconds": float}
- DONE: Signal that the overall goal has been completely achieved or cannot be completed.
  Parameters: {"status": "success" | "failure", "message": "Summary of result"}

### MANDATORY REASONING RULES
1. Strict Coordinate Grounding: Use ONLY the [x, y] coordinates provided in the current Screen State. Never guess or hallucinate coordinates.
2. Spatial Disambiguation: When multiple elements share identical text labels (e.g., multiple "Delete" or "Submit" buttons), examine surrounding elements and vertical/horizontal alignment to select the correct instance.
3. Verification & Correction: Check the Action History. If your previous action did not change the screen state as expected, assume the click missed or lagged: adjust coordinates, retry, or issue a WAIT.
4. Input Discipline: Before typing, ensure the target text input field is either already focused or explicitly clicked in the same command.
5. Task Completion: As soon as the end goal is visible and verified on the screen, issue the DONE command immediately. Do not trigger unnecessary additional clicks.

### RESPONSE FORMAT
You must respond with valid JSON containing both reasoning and action keys:

{
  "thought_process": "1. Goal analysis. 2. Current screen status. 3. Target element selection and why. 4. Next logical step.",
  "action": {
    "command": "CLICK | TYPE | KEY_COMBINATION | SCROLL_DOWN | SCROLL_UP | WAIT | DONE",
    "parameters": {}
  }
}"""


# ══════════════════════════════════════════════════════════════════════════════
# PER-TURN PROMPT TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════
_PER_TURN_TEMPLATE = """### TASK CONTEXT
- User Goal: {user_goal}
- Step Number: {current_step} of {max_steps}

### ACTION HISTORY (Past Steps & Observations)
{action_history_log}

### CURRENT SCREEN STATE (Detected Elements)
{screen_state_json}

### INSTRUCTIONS
Evaluate the screen state against the user goal, review past actions, formulate your chain-of-thought, and output your next action JSON."""


# ══════════════════════════════════════════════════════════════════════════════
# LLM REASONING CALL
# ══════════════════════════════════════════════════════════════════════════════
def _call_reasoning_llm(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Send the per-turn prompt to the fast reasoning LLM.
    Tries Groq (llama-3.3) first for low latency, then falls back to
    Gemini Flash via the existing inference_client.

    Returns parsed JSON dict or None on failure.
    """
    keys = _load_keys()

    # ── Groq (primary — fastest) ───────────────────────────────────────────
    groq_key = keys.get("groq_api_key", "").strip()
    if groq_key:
        try:
            import openai as _openai
            client = _openai.OpenAI(
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1",
            )
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": _REASONING_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content.strip()
            print("[AgentLoop] Groq reasoning responded.")
            return json.loads(raw)
        except Exception as e:
            print(f"[AgentLoop] Groq failed: {e}")

    # ── Gemini Flash (fallback) ────────────────────────────────────────────
    try:
        from core.inference_wrapper import inference_client
        raw = inference_client.generate_text(
            prompt=prompt,
            system_instruction=_REASONING_SYSTEM_PROMPT,
            model="gemini-2.5-flash",
            temperature=0.0,
        )
        raw = raw.strip()
        # Strip markdown fences
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:]) if lines[0].startswith("```") else raw
            if raw.endswith("```"):
                raw = raw[: raw.rfind("```")]
        print("[AgentLoop] Gemini Flash reasoning responded.")
        return json.loads(raw)
    except Exception as e:
        print(f"[AgentLoop] Gemini Flash failed: {e}")

    return None


# ══════════════════════════════════════════════════════════════════════════════
# PYAUTOGUI ACTION DISPATCHER
# ══════════════════════════════════════════════════════════════════════════════
def _require_pyautogui():
    if not _PYAUTOGUI_OK:
        raise RuntimeError("pyautogui is not installed. Run: pip install pyautogui")


def _smart_type(text: str) -> str:
    """Type text using clipboard for long strings (faster, handles unicode)."""
    _require_pyautogui()
    if _PYPERCLIP_OK and len(text) > 15:
        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "v")
        return f"Clipboard-typed: {text[:60]}{'...' if len(text) > 60 else ''}"
    pyautogui.typewrite(text, interval=0.04)
    return f"Typed: {text[:60]}{'...' if len(text) > 60 else ''}"


def _dispatch(command: str, parameters: dict) -> str:
    """
    Physically execute the action on the machine via PyAutoGUI.
    Returns a short observation string logged to action_history.
    """
    cmd = command.upper().strip()

    if cmd == "CLICK":
        _require_pyautogui()
        x, y = int(parameters["x"]), int(parameters["y"])
        pyautogui.moveTo(x, y, duration=0.25)
        time.sleep(0.05)
        pyautogui.click()
        return f"Clicked ({x}, {y})"

    elif cmd == "DOUBLE_CLICK":
        _require_pyautogui()
        x, y = int(parameters["x"]), int(parameters["y"])
        pyautogui.moveTo(x, y, duration=0.25)
        time.sleep(0.05)
        pyautogui.doubleClick()
        return f"Double-clicked ({x}, {y})"

    elif cmd == "RIGHT_CLICK":
        _require_pyautogui()
        x, y = int(parameters["x"]), int(parameters["y"])
        pyautogui.moveTo(x, y, duration=0.25)
        time.sleep(0.05)
        pyautogui.rightClick()
        return f"Right-clicked ({x}, {y})"

    elif cmd == "TYPE":
        _require_pyautogui()
        x, y = int(parameters.get("x", 0)), int(parameters.get("y", 0))
        text = str(parameters.get("text", ""))
        if x and y:
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click()
            time.sleep(0.2)
        return _smart_type(text)

    elif cmd == "KEY_COMBINATION":
        _require_pyautogui()
        keys = parameters.get("keys", [])
        if isinstance(keys, str):
            # accept "ctrl+t" as well as ["ctrl", "t"]
            keys = [k.strip() for k in keys.split("+")]
        if len(keys) == 1:
            pyautogui.press(keys[0])
            return f"Pressed key: {keys[0]}"
        pyautogui.hotkey(*keys)
        return f"Hotkey: {'+'.join(keys)}"

    elif cmd == "SCROLL_DOWN":
        _require_pyautogui()
        amount = int(parameters.get("amount", 500))
        pyautogui.scroll(-amount)
        return f"Scrolled down {amount}px"

    elif cmd == "SCROLL_UP":
        _require_pyautogui()
        amount = int(parameters.get("amount", 500))
        pyautogui.scroll(amount)
        return f"Scrolled up {amount}px"

    elif cmd == "WAIT":
        secs = float(parameters.get("seconds", 1.5))
        secs = min(secs, 30.0)  # safety cap
        time.sleep(secs)
        return f"Waited {secs}s"

    elif cmd == "DONE":
        # Handled by the loop — dispatcher just returns a marker
        status = parameters.get("status", "success")
        message = parameters.get("message", "Goal completed.")
        return f"DONE:{status}:{message}"

    else:
        return f"Unknown command: {cmd}"


# ══════════════════════════════════════════════════════════════════════════════
# ACTION HISTORY FORMATTER
# ══════════════════════════════════════════════════════════════════════════════
def _format_history(history: List[Dict[str, Any]]) -> str:
    if not history:
        return "(No actions taken yet — this is the first step.)"
    lines = []
    for i, entry in enumerate(history, 1):
        thought = entry.get("thought_process", "")
        cmd = entry.get("command", "?")
        params = entry.get("parameters", {})
        obs = entry.get("observation", "")
        lines.append(
            f"Step {i}: [{cmd}] params={json.dumps(params, ensure_ascii=False)}\n"
            f"  Thought: {thought[:200]}\n"
            f"  Observation: {obs}"
        )
    return "\n\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PUBLIC FUNCTION
# ══════════════════════════════════════════════════════════════════════════════
def vani_agent_loop(
    parameters: dict,
    player=None,
    speak: Optional[Callable] = None,
) -> str:
    """
    Entry point for the V.A.N.I. autonomous GUI agent loop.

    Parameters dict keys:
      goal      (str, required) — The high-level user goal
      max_steps (int, optional) — Max agent turns before giving up (default: 30)

    Returns a summary string of what was accomplished.
    """
    from actions.ui_detr import generate_screen_state, screen_state_to_text

    goal = (parameters or {}).get("goal", "").strip()
    if not goal:
        return "Error: No goal provided to vani_agent_loop."

    max_steps = int((parameters or {}).get("max_steps", 30))

    print(f"\n[AgentLoop] Goal: {goal}")
    print(f"[AgentLoop] Max steps: {max_steps}")

    if speak:
        speak("Alright, entering autonomous control loop — I'll figure this out step by step.")

    action_history: List[Dict[str, Any]] = []
    final_message = f"Reached max step limit ({max_steps}) without completing the goal."

    for step in range(1, max_steps + 1):
        print(f"\n[AgentLoop] ── Step {step}/{max_steps} ─────────────────────")

        # ── 1. Perception: generate Screen State ──────────────────────────
        screen_state = generate_screen_state()
        screen_state_json = screen_state_to_text(screen_state)

        if not screen_state:
            print("[AgentLoop] Warning: empty screen state — vision may have failed.")

        # ── 2. Build per-turn prompt ───────────────────────────────────────
        history_log = _format_history(action_history)
        per_turn_prompt = _PER_TURN_TEMPLATE.format(
            user_goal=goal,
            current_step=step,
            max_steps=max_steps,
            action_history_log=history_log,
            screen_state_json=screen_state_json,
        )

        # ── 3. Reasoning: call LLM ─────────────────────────────────────────
        print("[AgentLoop] Calling reasoning LLM...")
        response = _call_reasoning_llm(per_turn_prompt)

        if not response:
            print("[AgentLoop] Reasoning LLM failed — waiting 2s and retrying next step.")
            action_history.append({
                "thought_process": "Reasoning LLM failed.",
                "command": "WAIT",
                "parameters": {"seconds": 2},
                "observation": "LLM call failed — skipped turn.",
            })
            time.sleep(2)
            continue

        thought = response.get("thought_process", "")
        action_block = response.get("action", {})
        command = action_block.get("command", "WAIT").upper()
        params = action_block.get("parameters", {})

        print(f"[AgentLoop] Thought: {thought[:200]}")
        print(f"[AgentLoop] Action : {command} | Params: {params}")

        if player:
            player.write_log(f"[AgentLoop] Step {step}: {command} {params}")

        # ── 4. Dispatch action ─────────────────────────────────────────────
        try:
            observation = _dispatch(command, params)
        except Exception as e:
            observation = f"Dispatch error: {e}"
            print(f"[AgentLoop] Dispatch error: {e}")

        print(f"[AgentLoop] Observation: {observation}")

        # ── 5. Log to history ──────────────────────────────────────────────
        action_history.append({
            "thought_process": thought,
            "command": command,
            "parameters": params,
            "observation": observation,
        })

        # ── 6. Check terminal condition ────────────────────────────────────
        if command == "DONE" or observation.startswith("DONE:"):
            # Parse the result from the observation string
            parts = observation.split(":", 2)
            status = parts[1] if len(parts) > 1 else "success"
            msg = parts[2] if len(parts) > 2 else params.get("message", "Goal completed.")

            final_message = msg
            print(f"\n[AgentLoop] DONE — status={status} | {msg}")

            if speak:
                speak(msg if len(msg) < 120 else msg[:117] + "...")

            return f"[{status.upper()}] {msg}"

        # Small breathing room between steps
        time.sleep(0.5)

    # Fell through max steps
    print(f"\n[AgentLoop] Max steps reached. Last state had {len(screen_state)} elements.")
    if speak:
        speak("I've hit the step limit — I'll stop here. Let me know if you want me to try again.")

    return f"[INCOMPLETE] {final_message}"


# ══════════════════════════════════════════════════════════════════════════════
# TOOL WRAPPER (for executor.py _call_tool dispatch)
# ══════════════════════════════════════════════════════════════════════════════
def run_vani_agent_loop(
    parameters: dict,
    player=None,
    speak: Optional[Callable] = None,
) -> str:
    """Thin public wrapper matching V.A.N.I.'s tool call convention."""
    return vani_agent_loop(parameters=parameters, player=player, speak=speak)


# ══════════════════════════════════════════════════════════════════════════════
# STANDALONE TEST
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    test_goal = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Open Notepad and type Hello from V.A.N.I."
    print(f"\n=== V.A.N.I. Agent Loop — Test Run ===")
    print(f"Goal: {test_goal}\n")
    result = vani_agent_loop({"goal": test_goal, "max_steps": 15})
    print(f"\nResult: {result}")
