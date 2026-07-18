import os
import sys

class _DummyIO:
    def __init__(self):
        pass
    def write(self, msg, *args, **kwargs):
        pass
    def flush(self):
        pass

if getattr(sys, 'stdout', None) is None:
    sys.stdout = _DummyIO()
if getattr(sys, 'stderr', None) is None:
    sys.stderr = _DummyIO()

import json
import time
import subprocess
import threading
from pathlib import Path
import psutil
import speech_recognition as sr

# Ensure correct base dir
def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
VA_DIR = BASE_DIR / "voice_activation"
LOG_PATH = VA_DIR / "activation.log"

def log_msg(msg: str):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except:
        pass

def clear_log():
    try:
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("=== Background Voice Activation Log Started ===\n")
    except:
        pass

def is_jarvis_running():
    try:
        pid_file = BASE_DIR / "jarvis.pid"
        if pid_file.exists():
            pid = int(pid_file.read_text().strip())
            if psutil.pid_exists(pid):
                p = psutil.Process(pid)
                if 'py' in p.name().lower() and any('main.py' in str(c) for c in p.cmdline()):
                    return True
    except Exception:
        pass

    for p in psutil.process_iter(['name', 'cmdline']):
        try:
            name = p.info.get('name', '')
            if name and ('python' in name.lower() or 'py' in name.lower()):
                cmd = p.info.get('cmdline')
                if cmd and any('main.py' in str(c) for c in cmd):
                    return True
        except Exception:
            pass
    return False

def launch_jarvis():
    if is_jarvis_running():
        return
    log_msg("Launching Jarvis UI (no console)...")
    
    try:
        python_path = sys.executable.replace("pythonw.exe", "python.exe")
        subprocess.Popen(
            [python_path, "main.py"], 
            cwd=str(BASE_DIR), 
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        log_msg("Jarvis spawned.")
    except Exception as e:
        log_msg(f"Failed to launch Jarvis: {e}")

def main():
    clear_log()
    log_msg("Initializing background listener...")
    
    recognizer = sr.Recognizer()
    
    # Increase base sensitivity (lower threshold means more sensitive)
    recognizer.energy_threshold = 150
    # Disable dynamic threshold so it doesn't automatically increase the required volume
    recognizer.dynamic_energy_threshold = False
    
    try:
        microphone = sr.Microphone()
        with microphone as source:
            log_msg("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Ensure the threshold isn't set too high by the ambient noise adjustment
            if recognizer.energy_threshold > 300:
                recognizer.energy_threshold = 300
                
            log_msg(f"Energy threshold set to: {recognizer.energy_threshold}")
    except Exception as e:
        log_msg(f"Microphone initialization failed: {e}")
        time.sleep(5)
        return
    
    log_msg("Waiting for wake word 'jarvis' in background...")
    
    while True:
        if is_jarvis_running():
            time.sleep(2)
            continue
            
        try:
            with microphone as source:
                # listen for up to 5 seconds before checking if jarvis is running again
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            try:
                # Use Google Speech Recognition
                text = recognizer.recognize_google(audio).lower()
                log_msg(f"Recognized: {text}")
                
                if "jarvis" in text:
                    log_msg(f"Wake word matched: {text}")
                    launch_jarvis()
                    # Wait for Jarvis to start before listening again
                    time.sleep(2)
            except sr.UnknownValueError:
                # Speech was unintelligible
                pass
            except sr.RequestError as e:
                log_msg(f"Could not request results; {e}")
                
        except sr.WaitTimeoutError:
            # timeout reached, loop restarts and checks is_jarvis_running()
            pass
        except Exception as e:
            log_msg(f"Listener stream error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        with open(str(VA_DIR / "listener_error.log"), "a") as f:
            f.write(traceback.format_exc() + "\n")
