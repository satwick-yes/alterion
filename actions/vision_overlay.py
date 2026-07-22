import cv2
import numpy as np
import io
import base64
from PIL import ImageGrab, Image

def generate_marked_screenshot() -> tuple[str, dict, int, int]:
    """
    Takes a screenshot, applies UI element detection (Set-of-Mark),
    and returns a base64 encoded image and a dictionary of string ID -> (orig_x, orig_y) in native resolution.
    """
    screenshot = ImageGrab.grab()
    orig_w, orig_h = screenshot.size
    
    # Scale down for LLM consumption (max width 1280)
    max_w = 1280
    scale = min(1.0, max_w / orig_w)
    
    if scale < 1.0:
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        screenshot_resized = screenshot.resize((new_w, new_h), Image.Resampling.LANCZOS)
    else:
        new_w, new_h = orig_w, orig_h
        screenshot_resized = screenshot.copy()
        
    img = cv2.cvtColor(np.array(screenshot_resized), cv2.COLOR_RGB2BGR)
    
    # UI edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Dilate edges to connect broken parts of a single UI element
    kernel = np.ones((7,7), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    mark_dict = {}
    idx = 1
    
    # Sort contours by y then x so numbering is somewhat logical (top to bottom, left to right)
    bounding_boxes = [cv2.boundingRect(c) for c in contours]
    bounding_boxes.sort(key=lambda b: (b[1], b[0]))
    
    for x, y, w, h in bounding_boxes:
        # Filter too small (noise) or too large (the whole screen)
        if w > 20 and h > 20 and w < (new_w * 0.9) and h < (new_h * 0.9):
            # Calculate center point in original native image scale
            center_x = int((x + w/2) / scale)
            center_y = int((y + h/2) / scale)
            
            mark_dict[str(idx)] = (center_x, center_y)
            
            # Draw box
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
            
            # Calculate text size for background
            text = str(idx)
            (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            
            # Draw text background
            cv2.rectangle(img, (x, max(0, y - text_h - 4)), (x + text_w + 4, y), (0, 0, 0), -1)
            
            # Draw text
            cv2.putText(img, text, (x + 2, max(text_h, y - 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            idx += 1
            
    # Encode as JPEG
    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 60])
    b64 = base64.b64encode(buffer).decode('utf-8')
    
    return b64, mark_dict, new_w, new_h

if __name__ == "__main__":
    # Test script: save the marked image locally to verify
    b64, marks, w, h = generate_marked_screenshot()
    print(f"Detected {len(marks)} elements on {w}x{h} screen.")
    with open("test_overlay.jpg", "wb") as f:
        f.write(base64.b64decode(b64))
