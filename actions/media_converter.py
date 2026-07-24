import os
import urllib.request
import urllib.parse
import re
from pathlib import Path

def generate_qr_code(text: str, output_path: str = "qr_code.png") -> str:
    """Generates a QR code image for given text or URL using a clean free API."""
    try:
        encoded_text = urllib.parse.quote(text)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_text}"
        
        save_file = Path(output_path).resolve()
        urllib.request.urlretrieve(qr_url, str(save_file))
        return f"QR code successfully generated and saved to: {save_file}"
    except Exception as e:
        return f"Error generating QR code: {e}"

def fetch_web_page_text(url: str) -> str:
    """Fetches a web page URL and extracts clean readable text content."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
            
            # Clean script/style tags
            clean = re.sub(r"<(script|style).*?>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
            # Remove HTML tags
            text = re.sub(r"<[^>]+>", " ", clean)
            # Normalize whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            extracted = "\n".join(lines[:100]) # First 100 meaningful lines
            return f"--- Content from {url} ---\n{extracted[:3000]}"
    except Exception as e:
        return f"Error fetching web page: {e}"

def image_to_pdf(image_path: str, pdf_output_path: str = "output.pdf") -> str:
    """Converts an image file to PDF."""
    try:
        from PIL import Image
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(pdf_output_path, "PDF")
        return f"Successfully converted image to PDF: {pdf_output_path}"
    except ImportError:
        return "Image to PDF conversion requires PIL/Pillow package."
    except Exception as e:
        return f"Error converting image to PDF: {e}"
