import subprocess
import time
import socket
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = Path(__file__).resolve().parent.parent
ADB_PATH = str(BASE_DIR / "platform-tools" / "adb.exe")
PHONE_IP = "192.168.1.5"

def check_port(port):
    s = socket.socket()
    s.settimeout(0.15)
    try:
        s.connect((PHONE_IP, port))
        s.close()
        return port
    except:
        return None

def main():
    print("=" * 60)
    print("      VANI FAST WIRELESS PAIRING")
    print("=" * 60)
    print("\n1. Make sure your phone screen is ON.")
    print("2. Open: Settings -> Developer Options -> Wireless Debugging.")
    print("3. Tap: 'Pair device with pairing code'.")
    print("=" * 60)
    
    user_input = input("\nEnter the full 'IP address & Port' from the popup (e.g. 192.168.1.5:41157): ").strip()
    if not user_input:
        print("Error: No IP:Port entered.")
        return

    code = input("Enter the 6-digit pairing code: ").strip()
    if not code:
        print("Error: No code entered.")
        return

    # Normalize IP:Port
    target = user_input if ":" in user_input else f"{PHONE_IP}:{user_input}"
    
    print(f"\n[Pairing] Sending handshake to {target} with code {code}...")
    res = subprocess.run([ADB_PATH, "pair", target, code], capture_output=True, text=True)
    out = (res.stdout or "") + (res.stderr or "")
    print(out)

    if "Successfully paired" in out:
        print("\n🎉 PAIRING SUCCESSFUL!")
        print("\nNow looking for active device...")
        time.sleep(1)
        # Check if connected
        d = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True)
        print(d.stdout)
    else:
        print("\nTroubleshooting tip: If pairing gave an error, make sure the popup stayed open on your phone screen while you pressed Enter.")

if __name__ == "__main__":
    main()
