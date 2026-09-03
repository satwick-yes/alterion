import subprocess
import time
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ADB_PATH = str(BASE_DIR / "platform-tools" / "adb.exe")

def run_adb(args):
    try:
        return subprocess.run([ADB_PATH] + args, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        return e

def main():
    print("=" * 60)
    print("      VANI WIRELESS PHONE PAIRING HELPER")
    print("=" * 60)
    print("\n[STEP 1] On your Android phone:")
    print("  1. Open Settings -> Developer Options -> Wireless Debugging.")
    print("  2. Turn Wireless Debugging ON.")
    print("  3. Tap 'Pair device with pairing code'.")
    print("  ⚠️ KEEP THIS POPUP OPEN ON YOUR PHONE SCREEN (DO NOT CLOSE IT)!\n")
    
    ip_port = input("Enter the 'IP address & Port' shown INSIDE the popup (e.g. 192.168.1.5:40045): ").strip()
    if not ip_port:
        print("Error: No IP:Port entered.")
        return
        
    code = input("Enter the 6-digit Wi-Fi pairing code (e.g. 123456): ").strip()
    if not code:
        print("Error: No code entered.")
        return

    print("\n[STEP 2] Pairing with your phone...")
    res = subprocess.run([ADB_PATH, "pair", ip_port, code], capture_output=True, text=True)
    print(res.stdout or res.stderr)
    
    if "Successfully paired" in (res.stdout or ""):
        print("\n✅ PAIRING SUCCESSFUL!")
        print("\n[STEP 3] Now close that popup on your phone.")
        print("Look at the main 'Wireless Debugging' screen for the current 'IP address & Port'.")
        conn_ip_port = input("Enter the main IP address & Port (e.g. 192.168.1.5:38427): ").strip()
        if conn_ip_port:
            print(f"Connecting to {conn_ip_port}...")
            c_res = subprocess.run([ADB_PATH, "connect", conn_ip_port], capture_output=True, text=True)
            print(c_res.stdout or c_res.stderr)
            
            # Verify devices
            d_res = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True)
            print("\nConnected devices:")
            print(d_res.stdout)
            print("🎉 Setup complete! Vani can now control your phone completely wirelessly.")
    else:
        print("\n❌ Pairing failed. Common causes:")
        print("1. The popup on your phone closed or the screen turned off before the command finished.")
        print("2. You entered the main port instead of the specific pairing port shown inside the popup.")
        print("3. Try restarting Wireless Debugging and run this script again.")

if __name__ == "__main__":
    main()
