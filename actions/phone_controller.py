import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()

def _run_adb_command(args: list) -> subprocess.CompletedProcess:
    adb_path = str(BASE_DIR / "platform-tools" / "adb.exe")
    try:
        return subprocess.run(
            [adb_path] + args,
            capture_output=True,
            check=True
        )
    except FileNotFoundError:
        raise RuntimeError("adb command not found. Ensure Android Platform Tools are installed and in PATH.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ADB command failed: {e.stderr.decode('utf-8', errors='ignore')}")

def make_phone_call(parameters: dict, player=None, speak: Optional[Callable] = None) -> str:
    goal = parameters.get("goal", "")
    if not goal:
        return "Error: No goal provided."

    goal_lower = goal.lower()
    if "hang up" in goal_lower or "end call" in goal_lower or "stop call" in goal_lower:
        print("[PhoneController] Ending call via ADB...")
        if speak: speak("Ending the call, sir.")
        try:
            _run_adb_command(["shell", "input", "keyevent", "6"]) # KEYCODE_ENDCALL
            return "Call ended successfully."
        except Exception as e:
            return f"Failed to end call: {e}"

    print(f"[PhoneController] Goal: {goal}")
    
    # Try to extract a phone number
    number_match = re.search(r'\+?\d{7,15}', goal.replace(" ", "").replace("-", ""))
    number = ""
    if number_match:
        number = number_match.group(0)
    else:
        # We can ask Gemini to extract the contact name and then use adb to search contacts, 
        # but for now we just pass the raw name if it's not a number.
        return f"Error: Could not find a valid phone number in the request: {goal}. Please provide a 10-digit number."

    if speak:
        speak(f"Initiating call to {number}, sir.")

    try:
        out = _run_adb_command(["shell", "dumpsys", "power"]).stdout.decode("utf-8", errors="ignore")
        if "mWakefulness=Asleep" in out:
            _run_adb_command(["shell", "input", "keyevent", "26"])

        print(f"[PhoneController] Dialing {number} via ADB...")
        _run_adb_command(["shell", "am", "start", "-a", "android.intent.action.CALL", "-d", f"tel:{number}"])
        
        return f"Successfully initiated call to {number}. The call is now active over Bluetooth Hands-Free."
    except Exception as e:
        print(f"[PhoneController] Call failed: {e}")
        return f"Failed to initiate call: {str(e)}"
