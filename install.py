import subprocess
import sys
import os
import urllib.request

def run_command(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)

def main():
    # Ensure we are in the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("========================================================")
    print("                JARVIS FULL SETUP")
    print("========================================================\n")

    print("[1/5] Installing Microsoft Visual C++ Redistributable (Required for AI)...")
    vc_redist_url = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
    vc_redist_path = "vc_redist.x64.exe"
    
    try:
        print(f"Downloading {vc_redist_url}...")
        urllib.request.urlretrieve(vc_redist_url, vc_redist_path)
        print("Installing VC Redistributable (you may be prompted for Administrator privileges)...")
        # This will prompt for UAC automatically
        subprocess.run([vc_redist_path, "/install", "/passive", "/norestart"], check=True)
        if os.path.exists(vc_redist_path):
            os.remove(vc_redist_path)
    except Exception as e:
        print(f"Warning: Could not install VC Redistributable automatically. You may need to install it manually. Error: {e}")

    print("\n[2/5] Installing Python Backend Dependencies...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run_command([sys.executable, "-m", "pip", "install", "torch", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu"])
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("\n[3/5] Installing Node Frontend Dependencies...")
    if os.path.exists("frontend"):
        # On Windows, npm is a .cmd file
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        try:
            run_command([npm_cmd, "install"], cwd="frontend")
        except FileNotFoundError:
            print("npm not found. Please install Node.js to use the frontend.")
        except subprocess.CalledProcessError as e:
             print(f"npm install failed with error: {e}")
    else:
        print("Frontend folder not found. Skipping Node dependencies.")

    print("\n[4/5] Setting up Playwright Browsers...")
    run_command([sys.executable, "-m", "playwright", "install"])

    print("\n[5/5] Configuring API Keys...")
    run_command([sys.executable, os.path.join("setup", "setup_keys.py")])

    print("\n========================================================")
    print("  Setup Complete! You can now run Start_Jarvis.bat")
    print("========================================================")

if __name__ == "__main__":
    main()
