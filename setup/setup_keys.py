import json
import os
from pathlib import Path
import platform

def setup_api_keys():
    print("Welcome to Vani Setup!")
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

    # Prompt for OpenAI API Key
    print(f"\nCurrent OpenAI API Key: {keys.get('openai_api_key', 'Not set')}")
    openai_key = input("Enter your new OpenAI API Key (leave blank to keep current): ").strip()
    if openai_key:
        keys["openai_api_key"] = openai_key
        
    # Prompt for Nvidia API Key
    print(f"\nCurrent Nvidia API Key: {keys.get('nvidia_api_key', 'Not set')}")
    nvidia_key = input("Enter your new Nvidia API Key (leave blank to keep current): ").strip()
    if nvidia_key:
        keys["nvidia_api_key"] = nvidia_key
        
    # Prompt for Groq API Key
    print(f"\nCurrent Groq API Key: {keys.get('groq_api_key', 'Not set')}")
    groq_key = input("Enter your new Groq API Key (leave blank to keep current): ").strip()
    if groq_key:
        keys["groq_api_key"] = groq_key

    # Prompt for DeepSeek API Key
    print(f"\nCurrent DeepSeek API Key: {keys.get('deepseek_api_key', 'Not set')}")
    deepseek_key = input("Enter your new DeepSeek API Key (leave blank to keep current): ").strip()
    if deepseek_key:
        keys["deepseek_api_key"] = deepseek_key

    # Prompt for Cerebras API Key
    print(f"\nCurrent Cerebras API Key: {keys.get('cerebras_api_key', 'Not set')}")
    cerebras_key = input("Enter your new Cerebras API Key (leave blank to keep current): ").strip()
    if cerebras_key:
        keys["cerebras_api_key"] = cerebras_key

    # Prompt for Mistral AI API Key
    print(f"\nCurrent Mistral AI API Key: {keys.get('mistral_api_key', 'Not set')}")
    mistral_key = input("Enter your new Mistral AI API Key (leave blank to keep current): ").strip()
    if mistral_key:
        keys["mistral_api_key"] = mistral_key

    # Prompt for Cohere API Key
    print(f"\nCurrent Cohere API Key: {keys.get('cohere_api_key', 'Not set')}")
    cohere_key = input("Enter your new Cohere API Key (leave blank to keep current): ").strip()
    if cohere_key:
        keys["cohere_api_key"] = cohere_key

    # Prompt for Eden AI API Key
    print(f"\nCurrent Eden AI API Key: {keys.get('eden_api_key', 'Not set')}")
    eden_key = input("Enter your new Eden AI API Key (leave blank to keep current): ").strip()
    if eden_key:
        keys["eden_api_key"] = eden_key

    # Prompt for Hugging Face API Key
    print(f"\nCurrent Hugging Face API Key: {keys.get('huggingface_api_key', 'Not set')}")
    huggingface_key = input("Enter your new Hugging Face API Key (leave blank to keep current): ").strip()
    if huggingface_key:
        keys["huggingface_api_key"] = huggingface_key

    # Prompt for SambaNova API Key
    print(f"\nCurrent SambaNova API Key: {keys.get('sambanova_api_key', 'Not set')}")
    sambanova_key = input("Enter your new SambaNova API Key (leave blank to keep current): ").strip()
    if sambanova_key:
        keys["sambanova_api_key"] = sambanova_key

    # Prompt for Cloudflare API Key
    print(f"\nCurrent Cloudflare API Key: {keys.get('cloudflare_api_key', 'Not set')}")
    cloudflare_key = input("Enter your new Cloudflare API Key (leave blank to keep current): ").strip()
    if cloudflare_key:
        keys["cloudflare_api_key"] = cloudflare_key

    # Prompt for Github API Key
    print(f"\nCurrent Github API Key: {keys.get('github_api_key', 'Not set')}")
    github_key = input("Enter your new Github API Key (leave blank to keep current): ").strip()
    if github_key:
        keys["github_api_key"] = github_key

    # Prompt for Tripo AI API Key
    print(f"\nCurrent Tripo AI API Key: {keys.get('tripo_api_key', 'Not set')}")
    tripo_key = input("Enter your new Tripo AI API Key (leave blank to keep current): ").strip()
    if tripo_key:
        keys["tripo_api_key"] = tripo_key

    # Prompt for Composio API Key
    print(f"\nCurrent Composio API Key: {keys.get('composio_api_key', 'Not set')}")
    composio_key = input("Enter your new Composio API Key (leave blank to keep current): ").strip()
    if composio_key:
        keys["composio_api_key"] = composio_key

    # Keep placeholders for others if they don't exist
    if "os_system" not in keys:
        keys["os_system"] = platform.system()

    # Save to file
    with open(api_key_file, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=4)
        
    # Sync with .env
    env_file = base_dir / ".env"
    existing_env = {}
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    existing_env[k.strip()] = v.strip().strip('"').strip("'")
                    
    # Map json keys to env format
    for k, v in keys.items():
        if isinstance(v, str) and v:
            # e.g., github_api_key -> GITHUB_API_KEY
            # For standard tools, map specific names
            env_key = k.upper()
            if k == "github_api_key":
                env_key = "GITHUB_TOKEN"
            elif k == "cloudflare_api_key":
                env_key = "CLOUDFLARE_API_TOKEN"
            
            existing_env[env_key] = v

    with open(env_file, "w", encoding="utf-8") as f:
        f.write("# V.A.N.I. Environment Variables (Auto-Synced)\n\n")
        for k, v in existing_env.items():
            f.write(f'{k}="{v}"\n')

    print(f"\n✅ API keys successfully saved to {api_key_file.relative_to(base_dir)}")
    print(f"✅ Environment variables automatically synced to {env_file.relative_to(base_dir)}")
    print("You can now start Vani!")

if __name__ == "__main__":
    setup_api_keys()
