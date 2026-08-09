import time
import urllib.request
import json
import subprocess
import platform

def get_ip_info() -> str:
    """Fetches public IP address, location, ISP, and country info."""
    try:
        req = urllib.request.Request("http://ip-api.com/json/", headers={"User-Agent": "Vani/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("status") == "success":
                return (
                    f"Public IP: {data.get('query')}\n"
                    f"Country: {data.get('country')} ({data.get('countryCode')})\n"
                    f"Region/City: {data.get('regionName')}, {data.get('city')}\n"
                    f"ISP: {data.get('isp')}\n"
                    f"ZIP: {data.get('zip')}\n"
                    f"Timezone: {data.get('timezone')}"
                )
    except Exception as e:
        return f"Error fetching IP info: {e}"
    return "Could not retrieve IP information."

def run_speed_test() -> str:
    """Performs a lightweight network speed and latency test."""
    results = ["=== VANI Network Speed Diagnostic ==="]
    
    # Ping test
    host = "8.8.8.8"
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        t0 = time.time()
        res = subprocess.run(["ping", param, "3", host], capture_output=True, text=True, timeout=10)
        latency = (time.time() - t0) / 3.0 * 1000.0
        results.append(f"Ping Host: {host}")
        results.append(f"Average Latency: {latency:.1f} ms")
        if res.returncode == 0:
            results.append("Connectivity: ONLINE (Stable)")
        else:
            results.append("Connectivity: DEGRADED / Packet Loss")
    except Exception as e:
        results.append(f"Ping test error: {e}")

    # Lightweight Download Speed Test (fetching 5MB test file)
    test_url = "https://speed.cloudflare.com/__down?bytes=5000000"
    try:
        t0 = time.time()
        req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            elapsed = time.time() - t0
            size_mb = len(content) / (1024 * 1024)
            speed_mbps = (size_mb * 8) / elapsed
            results.append(f"Download Test: Transferred {size_mb:.2f} MB in {elapsed:.2f}s")
            results.append(f"Estimated Download Speed: {speed_mbps:.2f} Mbps")
    except Exception as e:
        results.append(f"Download speed test skipped/failed: {e}")

    return "\n".join(results)

def scan_local_network() -> str:
    """Scans local ARP table to discover connected network devices."""
    try:
        cmd = ["arp", "-a"]
        output = subprocess.check_output(cmd, encoding="utf-8", errors="ignore")
        lines = [line.strip() for line in output.splitlines() if line.strip() and not line.startswith("Interface")]
        return "Discovered Local Network Devices (ARP Table):\n" + "\n".join(lines[:25])
    except Exception as e:
        return f"Error scanning local network: {e}"
