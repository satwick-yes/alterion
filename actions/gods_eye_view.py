import os
import shutil
import subprocess
from pathlib import Path

def gods_eye_view(parameters: dict, player=None, speak=None) -> str:
    target_dir = Path(r"c:\Users\satwi\Documents\alterion\tools d\gods-eye-view-main\gods-eye-view-main")

    if player:
        player.write_log("SYS: Setting up and starting God's Eye View console.")
    
    if speak:
        speak("I am starting the God's Eye View console. I will set up the environment and open it in your browser shortly.")

    # 1. Setup .env if it doesn't exist
    env_path = target_dir / ".env"
    env_example_path = target_dir / ".env.example"
    if not env_path.exists() and env_example_path.exists():
        shutil.copy(env_example_path, env_path)
        if speak:
            speak("I have created a new .env file in the tool's directory. Please remember to add your Google Maps API key later for full 3D rendering.")
            
    # 2. Check dependencies and install if missing
    node_modules_path = target_dir / "node_modules"
    if not node_modules_path.exists():
        if speak:
            speak("Installing necessary packages. This might take a minute.")
        try:
            subprocess.run("npm install", cwd=str(target_dir), shell=True, check=True)
        except subprocess.CalledProcessError as e:
            return f"Failed to install dependencies: {e}"

    # 3. Start the dev server in the background
    try:
        # Running via shell to keep it alive
        subprocess.Popen(
            "npm run dev -- --host localhost --port 4173", 
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
    subprocess.Popen(["explorer", "http://localhost:4173"])
    
    if speak:
        speak("God's Eye View is now running in your browser!")
        
    return "Successfully started God's Eye View and opened http://localhost:4173 in the browser."
