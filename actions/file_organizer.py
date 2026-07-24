import os
import shutil
from pathlib import Path

CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".csv", ".pptx", ".odt", ".epub"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
    "Executables": [".exe", ".msi", ".bat", ".cmd", ".ps1"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".cpp", ".java", ".rs"]
}

def organize_folder(target_folder: str) -> str:
    """
    Scans the target directory and categorizes files into organized subfolders:
    Images, Documents, Videos, Audio, Archives, Executables, Code, and Others.
    """
    path = Path(target_folder).expanduser().resolve()

    if not path.exists() or not path.is_dir():
        return f"Directory does not exist: {target_folder}"

    moved_count = 0
    details = []

    try:
        for item in path.iterdir():
            # Skip directories
            if item.is_dir():
                continue

            file_ext = item.suffix.lower()
            dest_category = "Others"

            for category, exts in CATEGORIES.items():
                if file_ext in exts:
                    dest_category = category
                    break

            cat_dir = path / dest_category
            cat_dir.mkdir(exist_ok=True)

            target_path = cat_dir / item.name
            # If collision, append counter
            if target_path.exists():
                stem = item.stem
                counter = 1
                while target_path.exists():
                    target_path = cat_dir / f"{stem}_{counter}{file_ext}"
                    counter += 1

            shutil.move(str(item), str(target_path))
            moved_count += 1
            details.append(f"- {item.name} -> {dest_category}/")

        if moved_count == 0:
            return f"No unorganized files found in: {path}"

        summary = [f"Successfully organized {moved_count} file(s) in {path}:"]
        summary.extend(details[:15]) # limit preview
        if len(details) > 15:
            summary.append(f"...and {len(details) - 15} more files.")

        return "\n".join(summary)
    except Exception as e:
        return f"Error organizing folder {target_folder}: {e}"
