Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\satwi\Downloads\jarvis ai"
WshShell.Run """C:\Users\satwi\AppData\Local\Programs\Python\Python312\python.exe"" voice_activation\daemon.py", 0
Set WshShell = Nothing
