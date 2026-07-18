import subprocess
import sys

print("Installing requirements...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

print("Installing Playwright browsers...")
subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)

print("Setting up automatic voice activation on Windows startup...")
import platform
import os
from pathlib import Path
if platform.system() == "Windows":
    try:
        jarvis_dir = Path(__file__).resolve().parent.parent
        pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
        vbs_code = f"""Set WshShell = CreateObject("WScript.Shell")\nWshShell.CurrentDirectory = "{jarvis_dir}"\nWshShell.Run "{pythonw_path} voice_activation\\listener.py", 0\nSet WshShell = Nothing\n"""
        
        startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if startup_dir.exists():
            vbs_path = startup_dir / "jarvis_background_listener.vbs"
            with open(vbs_path, "w", encoding="utf-8") as f:
                f.write(vbs_code)
            print(f"[OK] Voice listener added to Startup folder: {vbs_path}")
            
            old_lnk = startup_dir / "Jarvis.lnk"
            if old_lnk.exists():
                try: old_lnk.unlink()
                except: pass
    except Exception as e:
        print(f"Failed to setup startup script: {e}")

print("\n[SUCCESS] Setup complete! Run 'python main.py' to start Jarvis.")