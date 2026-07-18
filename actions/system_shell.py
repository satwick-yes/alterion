import subprocess

def run_system_shell(parameters: dict, player=None) -> str:
    """
    Executes a shell command (PowerShell by default on Windows) and returns the output.
    """
    command = parameters.get("command")
    if not command:
        return "Error: No command provided."
        
    if player:
        player.write_log(f"SYS: Executing shell command: {command}")

    try:
        # We run via powershell to allow more complex commands
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        res_str = ""
        if output:
            res_str += f"Output:\n{output}\n"
        if error:
            res_str += f"Errors:\n{error}\n"
            
        if not res_str:
            res_str = "Command executed successfully with no output."
            
        return res_str
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 120 seconds."
    except Exception as e:
        return f"Error executing command: {e}"
