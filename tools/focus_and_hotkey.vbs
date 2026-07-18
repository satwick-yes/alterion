' focus_and_hotkey.vbs
' Called by Jarvis computer_control.py to focus a window and send a hotkey.
' wscript.exe runs outside Python sandbox with full desktop access.
'
' Usage: wscript //Nologo focus_and_hotkey.vbs "Discord" "^+v"
'   Arg 0: window title substring (case-insensitive)
'   Arg 1: keys in WScript.Shell SendKeys format
'          ^ = Ctrl,  + = Shift,  % = Alt

Dim titleMatch, keys, shell, activated

titleMatch = WScript.Arguments(0)
keys       = WScript.Arguments(1)

Set shell = CreateObject("WScript.Shell")

' First attempt: AppActivate with the title substring
activated = shell.AppActivate(titleMatch)

If Not activated Then
    ' Wait 200ms and try again (window may be loading)
    WScript.Sleep 200
    activated = shell.AppActivate(titleMatch)
End If

If Not activated Then
    WScript.Echo "NOT_FOUND"
    WScript.Quit 1
End If

' Window is now focused - wait for it to fully come to front
WScript.Sleep 600

' Send the keystrokes
shell.SendKeys keys

WScript.Echo "OK"
WScript.Quit 0
