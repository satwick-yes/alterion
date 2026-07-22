import json
import subprocess
import os
import sys

_hand_process = None

def virtual_hand_control(parameters: dict, player=None, session_memory=None) -> str:
    global _hand_process
    
    action = parameters.get("action", "move").lower().strip()
    
    if _hand_process is None or _hand_process.poll() is not None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, "virtual_hand.py")
        _hand_process = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True
        )
        
    if action == "close":
        if _hand_process:
            try:
                _hand_process.stdin.write(json.dumps({"action": "close"}) + "\n")
                _hand_process.stdin.flush()
            except Exception:
                pass
            _hand_process = None
        return "Virtual hand window closed."
        
    element = parameters.get("element_description", "")
    click = bool(parameters.get("click", False))
    
    if element:
        try:
            import pyautogui
            from actions.vision_computer_use import _find_button_coordinates_grid
            coords = _find_button_coordinates_grid(f"Click on {element}")
            if coords:
                px, py = coords
                screen_w, screen_h = pyautogui.size()
                norm_x = px / screen_w
                norm_y = py / screen_h
            else:
                return f"Could not visually find the element: {element}"
        except Exception as e:
            return f"Error running vision search: {e}"
    else:
        norm_x = float(parameters.get("norm_x", 0.5))
        norm_y = float(parameters.get("norm_y", 0.5))
        
    
    cmd = {
        "action": "move",
        "norm_x": norm_x,
        "norm_y": norm_y,
        "click": click
    }
    
    try:
        _hand_process.stdin.write(json.dumps(cmd) + "\n")
        _hand_process.stdin.flush()
        return f"Virtual 3D hand moved to ({norm_x}, {norm_y}) {'and performed pinch click' if click else ''}."
    except Exception as e:
        return f"Error controlling virtual hand: {e}"
