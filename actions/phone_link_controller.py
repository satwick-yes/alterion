import os
import re

def phone_link_call(parameters, player=None, speak=None):
    """
    Initiates a phone call using Windows Phone Link via the tel: protocol.
    """
    goal = parameters.get("goal", "")
    
    # Extract a phone number from the goal
    phone_numbers = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', goal)
    
    if phone_numbers:
        number = phone_numbers[0].strip()
        # Clean the number for the tel: protocol
        clean_number = re.sub(r'[^\d+]', '', number)
        print(f"[PhoneLinkController] Calling {clean_number} via Windows Phone Link...")
        
        # Open Windows Phone Link using the tel: protocol
        os.system(f"start tel:{clean_number}")
        
        # This exact string must be returned to trigger audio routing in main.py
        return (f"The call is now active over Bluetooth Hands-Free. You have initiated a phone call to {clean_number}. "
                f"INSTRUCTION: YOU ARE NOW ON A LIVE PHONE CALL WITH THE RECIPIENT. You MUST speak directly to them to accomplish the user's goal. "
                f"Act as a human voice agent. Speak clearly and do the requested task. When the conversation is completely finished, you MUST use the end_phone_call tool to hang up.")
    else:
        # Extract contact name using regex from the goal
        contact_name = "Unknown"
        m = re.search(r'(?i)(?:call|dial)\s+([a-zA-Z\s]+)', goal)
        if m:
            contact_name = m.group(1).strip()
        else:
            contact_name = goal
            
        # Strip common action prefixes that might appear before the contact name
        contact_name = re.sub(r'(?i)^(?:make a phone call to|phone call to|call to|contact|phone)\s+', '', contact_name).strip()
        # Strip leading filler words
        contact_name = re.sub(r'(?i)^(?:to|for)\s+', '', contact_name).strip()
        # Stop matching if we hit common filler words
        contact_name = re.split(r'\s+(and|to|if|about|ask|tell|via|using|on|for|through|with)\s+', contact_name)[0].strip()
        
        # If the extracted name is too long or empty, fallback to Unknown
        if not contact_name or len(contact_name.split()) > 4:
            contact_name = "Unknown"
        
        print(f"[PhoneLinkController] No number found, opening Phone Link dialer to search for contact: {contact_name}")
        if speak:
            speak(f"Opening Phone Link to call {contact_name}, sir.")
            
        os.system("start tel:")
        import time
        time.sleep(3.5) # Wait for Phone Link to open
        
        # We will use the vision computer use module to find and click the contact
        try:
            import sys
            from pathlib import Path
            base_dir = Path(__file__).resolve().parent.parent
            if str(base_dir) not in sys.path:
                sys.path.insert(0, str(base_dir))
            
            from actions.vision_computer_use import _find_button_coordinates
            import pyautogui
            pyautogui.FAILSAFE = False
            
            print("[PhoneLinkController] Searching for the 'Search your contacts' box...")
            coords = _find_button_coordinates("Search your contacts box")
            if coords:
                x, y = coords
                pyautogui.moveTo(x, y, duration=0.3)
                pyautogui.click()
                time.sleep(0.5)
                pyautogui.write(contact_name, interval=0.05)
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(2.0)
                
                print(f"[PhoneLinkController] Clicking on contact {contact_name}...")
                coords2 = _find_button_coordinates(f"The contact '{contact_name}' in the search results list below (do NOT click the text in the search bar)")
                if coords2:
                    x2, y2 = coords2
                    pyautogui.moveTo(x2, y2, duration=0.3)
                    pyautogui.click()
                    time.sleep(1.0)
                    
                    print("[PhoneLinkController] Clicking Call button...")
                    coords3 = _find_button_coordinates("Call button icon shaped like a phone")
                    if coords3:
                        x3, y3 = coords3
                        pyautogui.moveTo(x3, y3, duration=0.3)
                        pyautogui.click()
                        time.sleep(1.0)
                        
                        return (f"The call is now active over Bluetooth Hands-Free. You have initiated a phone call to {contact_name}. "
                                f"INSTRUCTION: YOU ARE NOW ON A LIVE PHONE CALL WITH THE RECIPIENT. You MUST speak directly to them to accomplish the user's goal. "
                                f"Act as a human voice agent. Speak clearly and do the requested task. When the conversation is completely finished, you MUST use the end_phone_call tool to hang up.")
        except Exception as e:
            print(f"[PhoneLinkController] UI Automation failed: {e}")
            
        return f"Opened Phone Link dialer but failed to automatically call {contact_name}. Please specify a number next time to auto-dial."

def end_phone_call(parameters, player=None, speak=None):
    """
    Ends the current active phone call mode.
    """
    # We can rely on the user to hang up the actual phone, or the other party to hang up.
    # This tool just signals main.py to revert the audio routing back to normal.
    print("[PhoneLinkController] Ending phone call mode...")
    return "Call ended successfully. Audio routing reverted."

if __name__ == "__main__":
    # Test
    phone_link_call({"goal": "call +1234567890"})
