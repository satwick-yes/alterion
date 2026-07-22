import io
import json
import re
import sys
import time
import subprocess
import base64
from pathlib import Path
from typing import Callable, Optional

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()

APP_PACKAGES = {
    "instagram": "com.instagram.android",
    "whatsapp": "com.whatsapp",
    "youtube": "com.google.android.youtube",
    "chrome": "com.android.chrome",
    "maps": "com.google.android.apps.maps",
    "gmail": "com.google.android.gm",
    "spotify": "com.spotify.music",
    "tiktok": "com.zhiliaoapp.musically",
    "twitter": "com.twitter.android",
    "x": "com.twitter.android",
    "facebook": "com.facebook.katana",
    "snapchat": "com.snapchat.android",
    "discord": "com.discord",
    "telegram": "org.telegram.messenger",
    "netflix": "com.netflix.mediaclient",
    "settings": "com.android.settings",
}

def _load_keys() -> dict:
    try:
        with open(BASE_DIR / "config" / "api_keys.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

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

def _check_device_connected():
    result = _run_adb_command(["devices"])
    output = result.stdout.decode("utf-8")
    lines = output.strip().split("\n")
    devices = [line for line in lines[1:] if "device" in line and "offline" not in line]
    if devices:
        return

    print("[MobileControl] No device connected, attempting mDNS auto-connect...")
    try:
        mdns_result = _run_adb_command(["mdns", "services"])
        mdns_output = mdns_result.stdout.decode("utf-8")
        for line in mdns_output.strip().split("\n"):
            if "_adb-tls-connect._tcp" in line:
                parts = line.split()
                if len(parts) >= 3:
                    ip_port = parts[2]
                    print(f"[MobileControl] Found mDNS device at {ip_port}. Attempting connection...")
                    _run_adb_command(["connect", ip_port])
                    check_result = _run_adb_command(["devices"])
                    check_out = check_result.stdout.decode("utf-8")
                    check_lines = check_out.strip().split("\n")
                    if any("device" in l and "offline" not in l for l in check_lines[1:]):
                        print("[MobileControl] Successfully auto-connected to mDNS device.")
                        return
    except Exception as e:
        print(f"[MobileControl] Auto-connect failed: {e}")

    raise RuntimeError(
        "No active Android device found. Since you want to use wireless ADB, "
        "please ensure your phone is connected to the same Wi-Fi network and run: "
        "`platform-tools\\adb.exe connect <YOUR_PHONE_IP>:5555` in your terminal. "
        "If using Android 11+ Wireless Debugging, use the specific port shown in Developer Options."
    )

def _take_screenshot() -> tuple[str, int, int]:
    result = _run_adb_command(["exec-out", "screencap", "-p"])
    img_data = result.stdout
    if not img_data:
        raise RuntimeError("Failed to capture screenshot.")
    
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(img_data))
        width, height = img.size
        
        # Optionally resize if it's too large to save token usage
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return b64, width, height
    except Exception as e:
        # Fallback if PIL fails
        b64 = base64.b64encode(img_data).decode('utf-8')
        return b64, 1080, 2400

def _extract_json_action(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except Exception:
        return {}

def _vision_step(goal: str, b64_image: str, width: int, height: int, history: str) -> dict:
    keys = _load_keys()
    gemini_key = keys.get("gemini_api_key", "").strip()
    if not gemini_key:
        return {"action": "error", "message": "Gemini API key not found"}

    prompt = (
        f'You are an AI agent controlling an Android mobile phone via ADB.\n'
        f'The user wants to achieve this goal: "{goal}".\n'
        f'The screenshot is {width}x{height} pixels.\n'
        f'Previous Actions History:\n{history}\n\n'
        'Analyze the screen and determine the NEXT action to get closer to the goal.\n'
        'Return ONLY a JSON object representing the action to take. Allowed actions:\n'
        '1. {"action": "tap", "x": <int>, "y": <int>} - Tap at coordinates.\n'
        '2. {"action": "swipe", "x1": <int>, "y1": <int>, "x2": <int>, "y2": <int>} - Swipe from (x1, y1) to (x2, y2).\n'
        '3. {"action": "type", "text": "<string>"} - Type text (assuming a text field is focused).\n'
        '4. {"action": "keyevent", "code": <int>} - Press hardware key (e.g., 26=power, 82=unlock, 3=home, 4=back, 66=enter).\n'
        '5. {"action": "done", "message": "<string>"} - The goal has been achieved.\n'
        '6. {"action": "error", "message": "<string>"} - Cannot proceed (explain why).\n'
    )

    print("[MobileControl] Asking Gemini Vision for next action...")
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                types.Part.from_bytes(data=base64.b64decode(b64_image), mime_type="image/jpeg"),
                types.Part.from_text(text=prompt)
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=300
            )
        )
        return _extract_json_action(response.text.strip())
    except Exception as e:
        print(f"[MobileControl] Gemini Vision failed: {e}")
        return {"action": "error", "message": str(e)}

def mobile_control(parameters: dict, player=None, speak: Optional[Callable] = None) -> str:
    goal = parameters.get("goal", "")
    if not goal:
        return "Error: No goal provided."

    print(f"[MobileControl] Goal: {goal}")
    if speak:
        speak("Connecting to your mobile device, sir.")

    try:
        _check_device_connected()
    except RuntimeError as e:
        with open("adb_error.log", "w") as f:
            f.write(str(e))
        if speak:
            speak("I cannot connect to your mobile phone. Please ensure it is connected to the same Wi-Fi and Wireless Debugging is authorized.")
        return str(e)

    history = ""
    max_steps = 10
    
    # Wake up screen as first step if screen is off
    try:
        out = _run_adb_command(["shell", "dumpsys", "power"]).stdout.decode("utf-8", errors="ignore")
        if "mWakefulness=Asleep" in out:
            print("[MobileControl] Screen is off. Pressing power button to wake up.")
            _run_adb_command(["shell", "input", "keyevent", "26"])
            time.sleep(1)
    except Exception:
        pass

    # Fast path: intent to open an app
    goal_lower = goal.lower()
    
    if "unlock" in goal_lower:
        pin_match = re.search(r'\b(\d{4,8})\b', goal_lower)
        if pin_match:
            pin = pin_match.group(1)
            print(f"[MobileControl] Fast-path: unlocking phone with PIN {pin}")
            try:
                _run_adb_command(["shell", "input", "keyevent", "224"]) # WAKEUP
                time.sleep(0.5)
                _run_adb_command(["shell", "input", "swipe", "500", "1000", "500", "200", "300"])
                time.sleep(2)
                
                for digit in pin:
                    keycode = str(int(digit) + 7) # '0'->7, '1'->8, etc.
                    _run_adb_command(["shell", "input", "keyevent", keycode])
                    time.sleep(0.3)
                    
                _run_adb_command(["shell", "input", "keyevent", "66"])
                time.sleep(2.0)
                
                # Check if user also wanted to open something
                if "open" not in goal_lower:
                    return "Successfully unlocked the phone."
            except Exception as e:
                print(f"[MobileControl] Fast-path unlock failed: {e}")

    if "open " in goal_lower:
        app_name = goal_lower.replace("open ", "").replace("on my phone", "").strip()
        for known_app, pkg in APP_PACKAGES.items():
            if known_app in app_name:
                print(f"[MobileControl] Fast-path: launching {pkg} directly via adb.")
                try:
                    _run_adb_command(["shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"])
                    print(f"Successfully opened {known_app} on the mobile device. Continuing to vision loop...")
                    time.sleep(3.0)
                    break
                except Exception as e:
                    print(f"[MobileControl] Fast-path launch failed: {e}")
                    pass

    for step in range(max_steps):
        print(f"\n[MobileControl] Step {step+1}/{max_steps}")
        try:
            b64_image, width, height = _take_screenshot()
        except Exception as e:
            msg = f"Failed to take screenshot: {e}"
            print(msg)
            return msg
        
        action_obj = _vision_step(goal, b64_image, width, height, history)
        act_type = action_obj.get("action")
        
        print(f"[MobileControl] Action decided: {action_obj}")
        
        if act_type == "done":
            msg = action_obj.get("message", "Goal achieved successfully.")
            if speak:
                speak("Mobile task completed, sir.")
            return msg
            
        elif act_type == "error":
            msg = action_obj.get("message", "Unknown error encountered.")
            return f"Failed to complete goal: {msg}"
            
        elif act_type == "tap":
            x, y = action_obj.get("x", 0), action_obj.get("y", 0)
            _run_adb_command(["shell", "input", "tap", str(x), str(y)])
            history += f"- Step {step+1}: Tapped at ({x}, {y})\n"
            
        elif act_type == "swipe":
            x1, y1 = action_obj.get("x1", 0), action_obj.get("y1", 0)
            x2, y2 = action_obj.get("x2", 0), action_obj.get("y2", 0)
            _run_adb_command(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), "300"])
            history += f"- Step {step+1}: Swiped from ({x1}, {y1}) to ({x2}, {y2})\n"
            
        elif act_type == "type":
            text = action_obj.get("text", "")
            # Escape spaces for adb shell input text
            text_escaped = text.replace(" ", "%s")
            _run_adb_command(["shell", "input", "text", text_escaped])
            history += f"- Step {step+1}: Typed text '{text}'\n"
            
        elif act_type == "keyevent":
            code = action_obj.get("code", 0)
            _run_adb_command(["shell", "input", "keyevent", str(code)])
            history += f"- Step {step+1}: Pressed hardware key {code}\n"
            
        else:
            print(f"[MobileControl] Unknown action type: {act_type}")
            history += f"- Step {step+1}: Unknown action {act_type}\n"
            
        # Wait a moment for UI to respond before next step
        time.sleep(2.0)
        
    return "Failed to complete the goal within the maximum number of steps."

if __name__ == "__main__":
    print(mobile_control({"goal": "unlock phone and open settings"}))
