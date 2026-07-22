import cv2
import numpy as np
import base64
from PIL import ImageGrab, Image

def generate_grid_screenshot(cell_size=50) -> tuple[str, float, int]:
    """
    Takes a screenshot, applies a grid overlay with X and Y axis labels,
    and returns a base64 encoded image, the scale factor, and the cell size used.
    """
    screenshot = ImageGrab.grab()
    orig_w, orig_h = screenshot.size
    
    # We will not scale down heavily for grid to avoid squishing the 50x50 cell.
    # We use a max width of 1920 (which is standard 1080p).
    max_w = 1920
    scale = min(1.0, max_w / orig_w)
    
    if scale < 1.0:
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        screenshot_resized = screenshot.resize((new_w, new_h), Image.Resampling.LANCZOS)
    else:
        new_w, new_h = orig_w, orig_h
        screenshot_resized = screenshot.copy()
        
    img = cv2.cvtColor(np.array(screenshot_resized), cv2.COLOR_RGB2BGR)
    
    overlay = img.copy()
    
    # Draw horizontal lines and Y labels (Row indices)
    for y in range(0, new_h, cell_size):
        cv2.line(overlay, (0, y), (new_w, y), (0, 0, 0), 1)
        row_idx = y // cell_size
        cv2.putText(overlay, str(row_idx), (2, min(y + 15, new_h - 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        cv2.putText(overlay, str(row_idx), (new_w - 25, min(y + 15, new_h - 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
    # Draw vertical lines and X labels (Col indices)
    for x in range(0, new_w, cell_size):
        cv2.line(overlay, (x, 0), (x, new_h), (0, 0, 0), 1)
        col_idx = x // cell_size
        cv2.putText(overlay, str(col_idx), (x + 2, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        cv2.putText(overlay, str(col_idx), (x + 2, new_h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
    # Blend overlay with original image to make grid semi-transparent
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
    
    # Encode as JPEG
    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 75])
    b64 = base64.b64encode(buffer).decode('utf-8')
    
    return b64, scale, cell_size
