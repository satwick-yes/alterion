import subprocess
import platform
import re

def close_app(parameters: dict, player=None) -> str:
    """
    Closes one or more running applications or processes by name using Task Manager powers (taskkill).
    Supports multiple apps separated by 'and' or commas.
    """
    app_name_input = parameters.get("app_name")
    if not app_name_input:
        return "Error: No app_name provided to close."
        
    # Handle list if the AI happens to pass a list
    if isinstance(app_name_input, list):
        apps_to_close = [str(app).strip() for app in app_name_input if str(app).strip()]
    else:
        # Split by comma or " and "
        cleaned_input = re.sub(r'(?i)\b\s+and\s+\b', ',', str(app_name_input))
        apps_to_close = [app.strip() for app in cleaned_input.split(",") if app.strip()]

    if not apps_to_close:
         return "Error: No valid app names provided to close."

    if player:
        player.write_log(f"SYS: Closing app(s): {', '.join(apps_to_close)}")

    sys_os = platform.system()
    results = []
    
    for app_name in apps_to_close:
        try:
            # Try to normalize the app name using open_app's aliases if available
            try:
                from actions.open_app import _normalize
                normalized_name = _normalize(app_name)
            except ImportError:
                normalized_name = app_name

            if sys_os == "Windows":
                exe_name = normalized_name if normalized_name.lower().endswith(".exe") else f"{normalized_name}.exe"
                
                # Using taskkill with /F (force) and /T (kill child processes) which mimics Task Manager
                cmd_im = f'taskkill /F /T /IM "{exe_name}"'
                
                # Also try without the exact exe name in case it's different, or use window title
                cmd_title = f'taskkill /F /T /FI "WINDOWTITLE eq {app_name}*"'
                
                # Powershell fallback for window titles (very powerful)
                ps_command_title = f"Get-Process | Where-Object {{$_.MainWindowTitle -match '{app_name}'}} | Stop-Process -Force"

                # Execute the commands
                # We ignore errors since taskkill returns an error if the process isn't found
                subprocess.run(cmd_im, shell=True, capture_output=True)
                subprocess.run(cmd_title, shell=True, capture_output=True)
                subprocess.run(["powershell", "-Command", ps_command_title], capture_output=True)
                
                # Sometimes the normalized name might be slightly different than the process name. 
                # Let's ensure we also just try the raw app_name.exe
                raw_exe = app_name if app_name.lower().endswith(".exe") else f"{app_name}.exe"
                if raw_exe.lower() != exe_name.lower():
                    subprocess.run(f'taskkill /F /T /IM "{raw_exe}"', shell=True, capture_output=True)
                    
                results.append(f"Successfully issued task manager close command for '{app_name}'.")
            else:
                # Fallback for Mac/Linux
                cmd = f"pkill -f \"{normalized_name}\""
                subprocess.run(cmd, shell=True, capture_output=True)
                if normalized_name != app_name:
                     subprocess.run(f"pkill -f \"{app_name}\"", shell=True, capture_output=True)
                results.append(f"Successfully issued close command for '{app_name}'.")

        except Exception as e:
            results.append(f"Error closing app '{app_name}': {e}")
            
    return "\n".join(results)
