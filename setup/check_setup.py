import sys
import importlib.util
from pathlib import Path

def check_requirements():
    req_file = Path("requirements.txt")
    if not req_file.exists():
        return False, "requirements.txt missing"
        
    missing = []
    with open(req_file, "r") as f:
        for line in f:
            pkg = line.strip()
            if not pkg or pkg.startswith("#"): continue
            
            # map pip names to import names for common ones
            import_name = pkg
            if pkg == "pillow" or pkg == "Pillow": import_name = "PIL"
            if pkg == "beautifulsoup4": import_name = "bs4"
            if pkg == "opencv-python": import_name = "cv2"
            if pkg == "python-docx": import_name = "docx"
            if pkg == "python-pptx": import_name = "pptx"
            if pkg == "PyPDF2": import_name = "PyPDF2"
            if pkg == "google-genai": import_name = "google.genai"
            if pkg == "google-generativeai": import_name = "google.generativeai"
            if pkg == "duckduckgo-search": import_name = "duckduckgo_search"
            if pkg == "youtube-transcript-api": import_name = "youtube_transcript_api"
            
            try:
                # Just check if we can import it
                if importlib.util.find_spec(import_name.split('.')[0]) is None:
                    missing.append(pkg)
            except Exception:
                missing.append(pkg)
                
    if missing:
        return False, f"Missing packages: {', '.join(missing)}"
    return True, "All dependencies are installed properly."

def check_startup_script():
    import os
    startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    vbs_path = startup_dir / "jarvis_background_listener.vbs"
    if vbs_path.exists():
        return True, f"Startup script is correctly placed at {vbs_path}"
    return False, "Startup script missing."

if __name__ == "__main__":
    print("=== JARVIS SETUP CHECKER ===")
    
    status, msg = check_requirements()
    print(f"[{'PASS' if status else 'FAIL'}] {msg}")
    
    status, msg = check_startup_script()
    print(f"[{'PASS' if status else 'FAIL'}] {msg}")
    
    print("\nSetup verification complete.")
