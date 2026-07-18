import json
import os
from pathlib import Path

def setup_api_keys():
    print("Welcome to Jarvis Setup!")
    print("This script will help you configure your API keys.\n")

    base_dir = Path(__file__).resolve().parent.parent
    config_dir = base_dir / "config"
    api_key_file = config_dir / "api_keys.json"
    
    # Ensure the config directory exists
    config_dir.mkdir(exist_ok=True, parents=True)

    # Load existing config or create a new one
    keys = {}
    if api_key_file.exists():
        try:
            with open(api_key_file, "r", encoding="utf-8") as f:
                keys = json.load(f)
        except json.JSONDecodeError:
            print("Warning: existing api_keys.json is corrupted. Starting fresh.")
    
    # Prompt for Gemini API Key
    print(f"Current Gemini API Key: {keys.get('gemini_api_key', 'Not set')}")
    gemini_key = input("Enter your new Gemini API Key (leave blank to keep current): ").strip()
    if gemini_key:
        keys["gemini_api_key"] = gemini_key

    # Prompt for OpenRouter API Key
    print(f"\nCurrent OpenRouter API Key: {keys.get('openrouter_api_key', 'Not set')}")
    openrouter_key = input("Enter your new OpenRouter API Key (leave blank to keep current): ").strip()
    if openrouter_key:
        keys["openrouter_api_key"] = openrouter_key
        
    # Keep placeholders for others if they don't exist
    if "nvidia_api_key" not in keys:
        keys["nvidia_api_key"] = ""
    if "os_system" not in keys:
        keys["os_system"] = "Windows" # Assuming default Windows

    # Save to file
    with open(api_key_file, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=4)
        
    print(f"\n✅ API keys successfully saved to {api_key_file.relative_to(base_dir)}")
    print("You can now start Jarvis!")

if __name__ == "__main__":
    setup_api_keys()
