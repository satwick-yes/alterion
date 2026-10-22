import subprocess
import sys
import os

def run_command(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("========================================================")
    print("                VANI CLEAN SETUP")
    print("========================================================\n")

    print("[1/3] Installing Python Backend Dependencies...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run_command([sys.executable, "-m", "pip", "install", "torch", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu"])
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("\n[2/3] Installing Playwright Browsers...")
    try:
        run_command([sys.executable, "-m", "playwright", "install"])
    except Exception as e:
        print(f"Warning: Playwright install failed: {e}")

    print("\n[3/3] Configuring API Keys...")
    run_command([sys.executable, os.path.join("setup", "setup_keys.py")])

    print("\n========================================================")
    print("  Setup Complete! You can now run Start_Vani.bat")
    print("========================================================")

if __name__ == "__main__":
    main()
