import subprocess

def cmd_control(parameters: dict, player=None, speak=None) -> str:
    """
    Executes a shell command based on the task description.
    """
    task = parameters.get("task")
    command = parameters.get("command")
    
    cmd_to_run = command or task
    
    if not cmd_to_run:
        return "Error: No command or task provided."
        
    if player:
        player.write_log(f"CMD: Executing: {cmd_to_run}")

    try:
        # We run via powershell to allow more complex commands
        result = subprocess.run(
            ["powershell", "-Command", cmd_to_run],
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
