# focus_and_hotkey.ps1
# Called by computer_control.py to focus a window and send a hotkey atomically.
# Usage: powershell -File focus_and_hotkey.ps1 -Title "Discord" -Keys "ctrl+shift+v"

param(
    [string]$Title = "",
    [string]$Keys  = ""
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;

public class WinHelper {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    public delegate bool EnumWindowsCallback(IntPtr hwnd, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsCallback lpEnumFunc, IntPtr lParam);

    public static IntPtr FindWindowByTitle(string titleSubstring) {
        IntPtr found = IntPtr.Zero;
        EnumWindows(delegate(IntPtr hwnd, IntPtr lParam) {
            if (!IsWindowVisible(hwnd)) return true;
            StringBuilder sb = new StringBuilder(512);
            GetWindowText(hwnd, sb, 512);
            if (sb.ToString().ToLower().Contains(titleSubstring.ToLower())) {
                found = hwnd;
                return false;
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }
}
"@

$hwnd = [WinHelper]::FindWindowByTitle($Title)
if ($hwnd -eq [IntPtr]::Zero) {
    Write-Output "NOT_FOUND"
    exit 1
}

# Restore if minimized (SW_RESTORE = 9)
[WinHelper]::ShowWindow($hwnd, 9) | Out-Null
Start-Sleep -Milliseconds 200
[WinHelper]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 600

# Send the hotkey using SendKeys
$wsh = New-Object -ComObject WScript.Shell

# Convert "ctrl+shift+v" -> "^+v" (WScript.Shell SendKeys format)
$keyMap = @{
    "ctrl"  = "^"
    "shift" = "+"
    "alt"   = "%"
    "win"   = "^{ESC}"
}

$parts = $Keys.ToLower() -split '\+'
$sendStr = ""
foreach ($part in $parts) {
    $part = $part.Trim()
    if ($keyMap.ContainsKey($part)) {
        $sendStr += $keyMap[$part]
    } else {
        if ($part.Length -eq 1) {
            $sendStr += $part
        } else {
            $sendStr += "{$part}"
        }
    }
}

$wsh.SendKeys($sendStr)
Write-Output "OK: Sent '$sendStr' to '$Title' (hwnd=$hwnd)"
