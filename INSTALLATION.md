# Jarvis AI - Installation Guide

Welcome to the Jarvis AI setup! Follow these steps to install and start Jarvis on your Windows machine.

## Prerequisites
1. **Python 3.12 or newer**: Make sure you have Python installed. When installing Python, ensure you check the box that says **"Add Python to PATH"**.
2. **Git** (optional but recommended): To clone the repository.

## Step 1: Install Dependencies & Setup
You can run the entire installation and API key configuration in one go by using the `entire_setup.bat` script:
1. Double-click the `setup\entire_setup.bat` file.
2. Wait for the installer to finish downloading all the required packages from `requirements.txt`.
3. It will then automatically prompt you to enter your API keys.

Alternatively, you can run them manually:
- To just install dependencies: run `setup\install_dependencies.bat`
- To just configure keys: run `python setup\setup_keys.py`

## Step 2: Configure API Keys
Jarvis requires API keys (such as Google Gemini and OpenRouter) to function.

1. Open your terminal or command prompt in the Jarvis folder.
2. Run the following command:
   ```cmd
   python setup\setup_keys.py
   ```
3. Follow the on-screen prompts to enter your API keys. This will securely save them to `config\api_keys.json`.

## Step 3: Starting Jarvis
You have a few options for starting Jarvis, depending on your needs:

- **Background Mode (Recommended)**: Double-click `launchers\start_jarvis.bat`. Jarvis will run silently in the background without keeping a console window open.
- **Console Mode (For Debugging)**: Double-click `launchers\jarvis_console.bat`. This will open a visible command prompt so you can see the logs and actions as Jarvis performs them.
- **Always-On Voice Listener**: Double-click `Start_Always_On_Listener.bat`. This runs the offline `vosk` voice model listener in a console window, waiting for you to say the wake word "Jarvis".

## Troubleshooting
- If you encounter issues during `install_dependencies.bat`, ensure you have the latest `pip` installed by running `python -m pip install --upgrade pip` in your command prompt.
- Make sure you are running the setup scripts from the main `jarvis ai` folder.
- If voice activation is not working, ensure your microphone is properly connected and set as the default input device in Windows settings.
