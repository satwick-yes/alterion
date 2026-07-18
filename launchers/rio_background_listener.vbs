Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\satwi\Downloads\jarvis ai"
WshShell.Run "pythonw.exe voice_activation\daemon.py", 0
Set WshShell = Nothing
