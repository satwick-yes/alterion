import json
import os
import subprocess
from google import genai
from google.genai import types

API_CONFIG_PATH = os.path.join("legacy_code", "config", "api_keys.json")

def get_api_key():
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]

class JarvisAgent:
    def __init__(self):
        self.client = genai.Client(api_key=get_api_key())
        self.model_name = "gemini-3.5-flash"
        
        # Define a simple tool for PC control
        self.run_command_tool = types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="run_command",
                    description="Run a terminal command on the user's Windows PC.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "command": types.Schema(type=types.Type.STRING, description="The Windows terminal command to run.")
                        },
                        required=["command"]
                    )
                )
            ]
        )

    def execute_command(self, command: str) -> str:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return str(e)

    def handle_request(self, user_intent: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_intent,
            config=types.GenerateContentConfig(
                tools=[self.run_command_tool],
                temperature=0.0
            )
        )
        
        if response.function_calls:
            for function_call in response.function_calls:
                if function_call.name == "run_command":
                    cmd = function_call.args["command"]
                    print(f"[Agent] Executing: {cmd}")
                    output = self.execute_command(cmd)
                    
                    # Return the tool output back to the model for a final summary
                    final_response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=[
                            types.Content(role="user", parts=[types.Part.from_text(text=user_intent)]),
                            types.Content(role="model", parts=[types.Part.from_function_call(name=function_call.name, args=function_call.args)]),
                            types.Content(role="user", parts=[types.Part.from_function_response(name=function_call.name, response={"output": output})])
                        ]
                    )
                    return final_response.text
                    
        return response.text
