import os
import win32com.client
from pathlib import Path

startup_folder = Path(os.environ['APPDATA']) / r"Microsoft\Windows\Start Menu\Programs\Startup"
shortcut_path = startup_folder / "Jarvis_Listener.lnk"

shell = win32com.client.Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(str(shortcut_path))
shortcut.Targetpath = "pythonw.exe"
shortcut.Arguments = "voice_activation\listener.py"
shortcut.WorkingDirectory = r"C:\Users\satwi\Downloads\jarvis ai"
# WindowStyle 7 = Minimized, but pythonw doesn't have a window anyway.
# Let's use python.exe with Minimized (7) so it definitely gets mic access.
shortcut.Targetpath = "python.exe"
shortcut.WindowStyle = 7
shortcut.Save()
print('Shortcut created!')
