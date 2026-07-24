import os
import platform
import time
import shutil

try:
    import psutil
except ImportError:
    psutil = None

def get_system_stats() -> str:
    """
    Returns a comprehensive diagnostic report of system performance, CPU, RAM, Disk, and Battery stats.
    """
    lines = ["=== JARVIS System Diagnostics ==="]
    lines.append(f"OS: {platform.system()} {platform.release()} ({platform.architecture()[0]})")
    lines.append(f"Hostname: {platform.node()}")

    if psutil:
        try:
            # CPU
            cpu_pct = psutil.cpu_percent(interval=0.5)
            cpu_count = psutil.cpu_count(logical=True)
            lines.append(f"CPU Usage: {cpu_pct}% ({cpu_count} Logical Cores)")

            # Memory
            mem = psutil.virtual_memory()
            lines.append(f"RAM Usage: {mem.percent}% ({mem.used / (1024**3):.2f} GB / {mem.total / (1024**3):.2f} GB)")

            # Disk
            disk = psutil.disk_usage('/')
            lines.append(f"Main Disk Usage: {disk.percent}% ({disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB free: {disk.free / (1024**3):.2f} GB)")

            # Battery
            battery = psutil.sensors_battery()
            if battery:
                plugged = "Plugged In" if battery.power_plugged else "On Battery"
                lines.append(f"Battery: {battery.percent}% ({plugged})")
            else:
                lines.append("Battery: Desktop / AC Powered")

            # System Uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = uptime_seconds / 3600
            lines.append(f"Uptime: {uptime_hours:.1f} hours")
        except Exception as e:
            lines.append(f"Error gathering detailed psutil metrics: {e}")
    else:
        # Fallback using shutil / os
        try:
            total, used, free = shutil.disk_usage("/")
            lines.append(f"Main Disk Usage: {used / (1024**3):.2f} GB / {total / (1024**3):.2f} GB (Free: {free / (1024**3):.2f} GB)")
        except Exception:
            pass
        lines.append("Note: Install 'psutil' package for extended CPU/RAM/Battery metrics.")

    return "\n".join(lines)
