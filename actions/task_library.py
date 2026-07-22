import subprocess
import time
import os
import platform

try:
    import pyautogui
except ImportError:
    pyautogui = None

# A library of hardcoded actions mapped from the user's master list
TASK_LIBRARY = {
    # POWER AND SESSION
    "turn on the computer": {"type": "error", "message": "Cannot physically turn on the computer when it is already off."},
    "shut down the computer": {"type": "cmd", "cmd": "shutdown /s /t 0"},
    "restart the computer": {"type": "cmd", "cmd": "shutdown /r /t 0"},
    "lock the computer": {"type": "cmd", "cmd": "rundll32.exe user32.dll,LockWorkStation"},
    "sign out of windows": {"type": "cmd", "cmd": "shutdown /l"},
    "switch user accounts": {"type": "cmd", "cmd": "tsdiscon"},
    "put the pc to sleep": {"type": "cmd", "cmd": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"},
    "hibernate the computer": {"type": "cmd", "cmd": "shutdown /h"},
    "force shutdown": {"type": "cmd", "cmd": "shutdown /s /f /t 0"},

    # UI AND NAVIGATION
    "open the start menu": {"type": "hotkey", "keys": ["win"]},
    "search for an application": {"type": "hotkey", "keys": ["win", "s"]},
    "search for a document": {"type": "hotkey", "keys": ["win", "s"]},
    "open task manager": {"type": "hotkey", "keys": ["ctrl", "shift", "esc"]},
    "open windows settings": {"type": "hotkey", "keys": ["win", "i"]},
    "open action center": {"type": "hotkey", "keys": ["win", "a"]},
    "open file explorer": {"type": "hotkey", "keys": ["win", "e"]},
    "show the desktop": {"type": "hotkey", "keys": ["win", "d"]},
    "restore minimized windows": {"type": "hotkey", "keys": ["win", "d"]},
    "open quick access": {"type": "hotkey", "keys": ["win", "e"]},

    # DIAGNOSTICS & SYSTEM
    "view startup applications": {"type": "cmd", "cmd": "start ms-settings:startupapps"},
    "change system language": {"type": "cmd", "cmd": "start ms-settings:regionlanguage"},
    "change date and time manually": {"type": "cmd", "cmd": "start ms-settings:dateandtime"},
    "view windows version": {"type": "cmd", "cmd": "winver"},
    "check system specifications": {"type": "cmd", "cmd": "start ms-settings:about"},
    "rename the computer": {"type": "cmd", "cmd": "start ms-settings:about"},
    "check windows activation status": {"type": "cmd", "cmd": "start ms-settings:activation"},
    "restart windows explorer": {"type": "powershell", "cmd": "Stop-Process -ProcessName explorer -Force"},

    # NETWORK
    "view available wi-fi networks": {"type": "cmd", "cmd": "start ms-settings:network-wifi"},
    "turn airplane mode on": {"type": "cmd", "cmd": "start ms-settings:network-airplanemode"},
    "turn airplane mode off": {"type": "cmd", "cmd": "start ms-settings:network-airplanemode"},
    "view network status": {"type": "cmd", "cmd": "start ms-settings:network-status"},
    "view ip address": {"type": "cmd", "cmd": "cmd /c ipconfig /all & pause"},
    "flush the dns cache": {"type": "cmd", "cmd": "ipconfig /flushdns"},
    "test internet connectivity": {"type": "cmd", "cmd": "ping 8.8.8.8"},

    # BROWSER (Assuming default browser)
    "launch a web browser": {"type": "cmd", "cmd": "start http://google.com"},
    "open an incognito/private window": {"type": "hotkey", "keys": ["ctrl", "shift", "n"]},
    "open a new tab": {"type": "hotkey", "keys": ["ctrl", "t"]},
    "open a new window": {"type": "hotkey", "keys": ["ctrl", "n"]},
    "reopen the last closed tab": {"type": "hotkey", "keys": ["ctrl", "shift", "t"]},
    "bookmark the current page": {"type": "hotkey", "keys": ["ctrl", "d"]},
    "view browsing history": {"type": "hotkey", "keys": ["ctrl", "h"]},
    "clear browsing history": {"type": "hotkey", "keys": ["ctrl", "shift", "delete"]},
    "download a file": {"type": "hotkey", "keys": ["ctrl", "s"]},
    "open the downloads page": {"type": "hotkey", "keys": ["ctrl", "j"]},
    "print a webpage": {"type": "hotkey", "keys": ["ctrl", "p"]},
    "zoom in on a webpage": {"type": "hotkey", "keys": ["ctrl", "+"]},
    "zoom out on a webpage": {"type": "hotkey", "keys": ["ctrl", "-"]},
    "reset browser zoom": {"type": "hotkey", "keys": ["ctrl", "0"]},
    "open developer tools": {"type": "hotkey", "keys": ["f12"]},

    # FILE MANAGEMENT
    "empty the recycle bin": {"type": "powershell", "cmd": "Clear-RecycleBin -Force"},
    "clean temporary files": {"type": "cmd", "cmd": "cleanmgr /sagerun:1"},
    "use disk cleanup": {"type": "cmd", "cmd": "cleanmgr"},
    "open disk management": {"type": "cmd", "cmd": "diskmgmt.msc"},
    
    # ACCESSIBILITY
    "enable magnifier": {"type": "hotkey", "keys": ["win", "+"]},
    "enable narrator": {"type": "hotkey", "keys": ["ctrl", "win", "enter"]},
    "use the on-screen keyboard": {"type": "cmd", "cmd": "osk"},
}

def execute_hardcoded_task(task_name: str) -> str:
    """Executes a hardcoded task if it exists in the library."""
    task = TASK_LIBRARY.get(task_name.lower().strip())
    if not task:
        return ""

    action_type = task.get("type")
    
    if action_type == "error":
        return task.get("message", "Task failed.")
        
    elif action_type == "cmd":
        print(f"[TaskLibrary] Executing CMD: {task['cmd']}")
        try:
            subprocess.Popen(task["cmd"], shell=True)
            return f"Successfully executed: {task_name}"
        except Exception as e:
            return f"Failed to execute command: {e}"
            
    elif action_type == "powershell":
        print(f"[TaskLibrary] Executing PowerShell: {task['cmd']}")
        try:
            subprocess.Popen(["powershell", "-Command", task["cmd"]], shell=True)
            return f"Successfully executed: {task_name}"
        except Exception as e:
            return f"Failed to execute powershell: {e}"
            
    elif action_type == "hotkey":
        if not pyautogui:
            return "PyAutoGUI is not installed; cannot trigger hotkeys."
        print(f"[TaskLibrary] Pressing hotkeys: {task['keys']}")
        time.sleep(0.5) # Give UI time to register
        pyautogui.hotkey(*task["keys"])
        return f"Successfully pressed keys for: {task_name}"
        
    return ""
