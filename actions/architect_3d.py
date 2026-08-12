import os
import tempfile
import subprocess
import requests
import re
import json
import traceback
import time
from core.inference_wrapper import inference_client
from memory.memory_manager import format_chat_history_for_prompt

def generate_3d_model(parameters: dict, player=None, speak=None) -> str:
    """Generates a 3D model either locally via Blender Python or via fallback Text-to-3D API."""
    task = parameters.get("task", "")
    
    if speak:
        speak("Right away, Sir. Rendering the 3D model now.")
    if player:
        player.write_log("3D_ARCHITECT: Analyzing 3D modeling request...")

    # Determine intent using Gemini
    prompt = (
        f"Analyze the following 3D modeling request: '{task}'.\n"
        "Determine if this should be a 'parametric' model (e.g. gear, box, mechanical part, simple geometric shapes) "
        "or an 'organic' model (e.g. character, animal, textured object, complex organic shapes).\n"
        "Return ONLY a JSON response in the following schema: {\"type\": \"parametric\" | \"organic\", \"reason\": \"string\"}"
    )

    try:
        response = inference_client.generate_json(
            prompt=prompt,
            system_instruction="You are a precise classifier mapping 3D requests to either parametric (geometric) or organic (textured/character). Return JSON only.",
            provider="gemini"
        )
        model_type = response.get("type", "organic").lower()
        reason = response.get("reason", "")
    except Exception as e:
        if player:
            player.write_log(f"3D_ARCHITECT: Intent classification failed, defaulting to organic. Error: {e}")
        model_type = "organic"
        reason = "Fallback to organic due to error."

    if player:
        player.write_log(f"3D_ARCHITECT: Decided type is {model_type}. Reason: {reason}")

    if model_type == "parametric":
        return _generate_parametric(task, player)
    else:
        return _generate_organic(task, player)

def _generate_parametric(task: str, player) -> str:
    if player:
        player.write_log("3D_ARCHITECT: Generating Blender Python script...")

    prompt = (
        f"Write a Python script for Blender (`bpy`) that creates the following 3D model: '{task}'.\n"
        "The script must:\n"
        "1. Delete all existing objects (Cube, Camera, Light).\n"
        "2. Create the requested 3D model.\n"
        "3. Save the file to the current working directory as 'generated_model.blend'.\n"
        "4. Save an export of the model as 'generated_model.glb'.\n"
        "Provide ONLY the raw Python code without any markdown formatting, backticks, or explanations."
    )

    try:
        bpy_script = inference_client.generate_text(
            prompt=prompt,
            system_instruction="You are a Python expert specializing in Blender `bpy` scripting. Output only executable python code.",
            provider="gemini"
        )
        
        bpy_script = re.sub(r'```python\n|```python|```', '', bpy_script).strip()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as temp_script:
            temp_script.write(bpy_script)
            script_path = temp_script.name

        if player:
            player.write_log(f"3D_ARCHITECT: Running Blender with generated script...")

        # Execute blender in background mode
        # Assumes blender is in PATH
        result = subprocess.run(
            ["blender", "--background", "--python", script_path],
            capture_output=True,
            text=True
        )

        try:
            os.remove(script_path)
        except:
            pass

        if result.returncode == 0:
            if player:
                player.write_log(f"3D_ARCHITECT: Parametric model generated successfully (generated_model.blend/glb).")
            return f"Successfully generated the parametric 3D model. The files 'generated_model.blend' and 'generated_model.glb' have been saved in the current directory."
        else:
            if player:
                player.write_log(f"3D_ARCHITECT: Blender execution failed: {result.stderr}")
            return f"Failed to generate parametric 3D model. Blender error: {result.stderr}"

    except Exception as e:
        error_msg = f"Failed in parametric generation: {e}\n{traceback.format_exc()}"
        if player:
            player.write_log(f"3D_ARCHITECT: {error_msg}")
        return error_msg

def _generate_organic(task: str, player) -> str:
    if player:
        player.write_log("3D_ARCHITECT: Triggering Tripo AI Text-to-3D API...")

    import sys
    from pathlib import Path
    
    # Try to load API key from config
    try:
        base_dir = Path(__file__).resolve().parent.parent
        config_path = base_dir / "config" / "api_keys.json"
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).parent
            config_path = base_dir / "config" / "api_keys.json"
            
        with open(config_path, "r", encoding="utf-8") as f:
            api_key = json.load(f).get("tripo_api_key", "")
            
        if not api_key:
            return "Tripo AI API key ('tripo_api_key') is missing from config/api_keys.json."
    except Exception as e:
        return f"Failed to read config/api_keys.json: {e}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "prompt": task,
        "model": "v3.1-20260211"
    }

    try:
        if player:
            player.write_log("3D_ARCHITECT: Initiating task with Tripo AI...")
        
        response = requests.post(
            "https://openapi.tripo3d.ai/v3/generation/text-to-model",
            headers=headers,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        
        # Tripo API returns {"code": 0, "data": {"task_id": "..."}}
        if data.get("code") != 0 or "data" not in data or "task_id" not in data["data"]:
            return f"Tripo AI API Error: Unexpected response format: {data}"
            
        task_id = data["data"]["task_id"]
        
        if player:
            player.write_log(f"3D_ARCHITECT: Task initiated ({task_id}). Polling for completion...")

        max_polls = 30
        poll_interval = 5
        
        for i in range(max_polls):
            time.sleep(poll_interval)
            
            task_resp = requests.get(
                f"https://openapi.tripo3d.ai/v3/tasks/{task_id}",
                headers=headers,
                timeout=10
            )
            task_resp.raise_for_status()
            task_data = task_resp.json()
            
            if task_data.get("code") == 0 and "data" in task_data:
                status = task_data["data"].get("status")
                
                if player:
                    player.write_log(f"3D_ARCHITECT: Polling task status: {status} ({i+1}/{max_polls})")
                
                if status == "SUCCESS":
                    model_url = task_data["data"]["output"].get("model")
                    if model_url:
                        if player:
                            player.write_log("3D_ARCHITECT: Model generated! Downloading...")
                        
                        model_resp = requests.get(model_url, timeout=30)
                        model_resp.raise_for_status()
                        
                        out_file = "generated_model.glb"
                        with open(out_file, "wb") as f:
                            f.write(model_resp.content)
                            
                        if player:
                            player.write_log(f"3D_ARCHITECT: Organic model saved as {out_file}.")
                        return f"Successfully generated the organic 3D model. The file '{out_file}' has been saved in the current directory."
                    else:
                        return f"Task succeeded but no model URL found in output: {task_data}"
                elif status in ["FAILED", "CANCELLED", "TIMEOUT"]:
                    return f"Task failed with status: {status}. Details: {task_data}"
            else:
                if player:
                    player.write_log(f"3D_ARCHITECT: Unexpected task poll response: {task_data}")
                    
        return f"Tripo AI task ({task_id}) timed out after {max_polls * poll_interval} seconds."

    except Exception as e:
        error_msg = f"Failed in organic generation: {e}\n{traceback.format_exc()}"
        if player:
            player.write_log(f"3D_ARCHITECT: {error_msg}")
        return error_msg
