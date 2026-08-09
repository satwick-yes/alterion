Set objShell = CreateObject("WScript.Shell")
' Get the directory of this script
strPath = Wscript.ScriptFullName
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objFile = objFSO.GetFile(strPath)
strFolder = objFSO.GetParentFolderName(objFile)
' Run the python script hidden (0)
objShell.Run "python """ & strFolder & "\wake_word_listener.py""", 0, False
