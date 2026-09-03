import os
import shutil
import subprocess
from pathlib import Path

def world_monitor(parameters: dict, player=None, speak=None) -> str:
    target_dir = Path(r"c:\Users\satwi\Documents\alterion\tools d\worldmonitor-main\worldmonitor-main")

    if player:
        player.write_log("SYS: Setting up and starting World Monitor dashboard.")
    
    if speak:
        speak("I am starting the World Monitor dashboard. I will prepare the environment and open it in your browser shortly.")

    # 1. Setup .env if it doesn't exist
    env_path = target_dir / ".env.local"
    env_example_path = target_dir / ".env.example"
    if not env_path.exists() and env_example_path.exists():
        shutil.copy(env_example_path, env_path)
        if speak:
            speak("I have created a new configuration file in the World Monitor directory for you.")
            
    # 2. Check dependencies and install if missing
    node_modules_path = target_dir / "node_modules"
    if not node_modules_path.exists():
        if speak:
            speak("Installing necessary Node packages for the dashboard. This might take a few moments.")
        try:
            subprocess.run("npm install", cwd=str(target_dir), shell=True, check=True)
        except subprocess.CalledProcessError as e:
            return f"Failed to install dependencies: {e}"

    # 3. Start the dev server in the background
    try:
        # Running via shell to keep it alive
        subprocess.Popen(
            "npm run dev", 
            cwd=str(target_dir), 
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        return f"Failed to start the server: {e}"
        
    # 4. Open the browser
    # Give it a second to start the server
    import time
    time.sleep(3)
    subprocess.Popen(["explorer", "http://localhost:3000"])
    
    if speak:
        speak("World Monitor is now running in your browser!")
        
    return "Successfully started World Monitor and opened http://localhost:3000 in the browser."
