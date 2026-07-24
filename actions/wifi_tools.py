import subprocess
import re
import platform

def get_wifi_passwords() -> str:
    """
    Retrieves stored Wi-Fi profiles and their passwords on Windows using netsh.
    Returns a formatted string of network SSIDs and passwords.
    """
    if platform.system().lower() != "windows":
        return "Wi-Fi password extraction is currently only supported on Windows OS."

    try:
        # Get profiles list
        output = subprocess.check_output(["netsh", "wlan", "show", "profiles"], encoding="utf-8", errors="ignore")
        profiles = re.findall(r"All User Profile\s*:\s*(.*)", output)

        if not profiles:
            return "No Wi-Fi profiles found on this system."

        results = []
        for profile in profiles:
            ssid = profile.strip().strip("\r").strip("\n")
            if not ssid:
                continue
            try:
                profile_info = subprocess.check_output(
                    ["netsh", "wlan", "show", "profile", f"name={ssid}", "key=clear"],
                    encoding="utf-8",
                    errors="ignore"
                )
                password_match = re.search(r"Key Content\s*:\s*(.*)", profile_info)
                password = password_match.group(1).strip() if password_match else "None / Open Network"
                results.append(f"- SSID: {ssid} | Password: {password}")
            except Exception:
                results.append(f"- SSID: {ssid} | Password: Could not retrieve")

        return "Stored Wi-Fi Profiles & Passwords:\n" + "\n".join(results)
    except Exception as e:
        return f"Error retrieving Wi-Fi passwords: {str(e)}"

def get_wifi_status() -> str:
    """Retrieves current active Wi-Fi connection details."""
    if platform.system().lower() != "windows":
        return "Wi-Fi status check is currently only supported on Windows OS."
    try:
        output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], encoding="utf-8", errors="ignore")
        return f"Active Wi-Fi Interface Details:\n{output.strip()}"
    except Exception as e:
        return f"Error retrieving Wi-Fi status: {str(e)}"
