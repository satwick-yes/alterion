# actions/send_message.py
# Universal messaging — WhatsApp & Instagram
# Uses visual element detection (pyautogui + screen search) instead of
# hardcoded tab/click sequences — works on any screen resolution.

import time
import pyautogui
from pathlib import Path

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.08

def _open_app(app_name: str) -> bool:
    """Opens an app via Windows search."""
    try:
        pyautogui.press("win")
        time.sleep(0.4)
        pyautogui.write(app_name, interval=0.04)
        time.sleep(0.5)
        pyautogui.press("enter")
        time.sleep(2.0)  
        return True
    except Exception as e:
        print(f"[SendMessage] Could not open {app_name}: {e}")
        return False


def _search_contact(contact: str, platform: str):
    """
    Searches for a contact inside the messaging app.
    Uses Ctrl+F (universal search shortcut) then types contact name.
    """
    time.sleep(0.5)
    pyautogui.hotkey("ctrl", "f")
    time.sleep(0.4)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.write(contact, interval=0.04)
    time.sleep(0.8)
    pyautogui.press("enter")
    time.sleep(0.6)


def _type_and_send(message: str):
    """Types message and sends it."""
    pyautogui.press("tab")
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.write(message, interval=0.03)
    time.sleep(0.2)
    pyautogui.press("enter")
    time.sleep(0.3)


def _send_whatsapp(receiver: str, message: str) -> str:
    """
    Sends a WhatsApp message via the Windows desktop app.
    Steps: Open WhatsApp → Search contact → Click → Type → Send
    """
    try:
        if not _open_app("WhatsApp"):
            return "Could not open WhatsApp."

        time.sleep(1.5)

        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        pyautogui.write(receiver, interval=0.04)
        time.sleep(2.0)  # Wait longer for search results

        pyautogui.press("enter")
        time.sleep(1.5)  # Wait longer for chat to open and focus

        pyautogui.write(message, interval=0.03)
        time.sleep(0.5)
        pyautogui.press("enter")

        return f"Message sent to {receiver} via WhatsApp."

    except Exception as e:
        return f"WhatsApp error: {e}"


def _send_instagram(receiver: str, message: str, browser_param: str = "") -> str:
    """
    Sends an Instagram DM via browser (instagram.com).
    Steps: Open Browser → Go to instagram.com/direct/new/ → Search contact → Send
    """
    try:
        import webbrowser
        import os
        
        browser_obj = webbrowser
        if browser_param == "brave":
            paths = [
                os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe")
            ]
            for p in paths:
                if os.path.exists(p):
                    try:
                        webbrowser.register('brave', None, webbrowser.BackgroundBrowser(p))
                        browser_obj = webbrowser.get('brave')
                    except Exception:
                        pass
                    break
        elif browser_param == "chrome":
            paths = [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
            ]
            for p in paths:
                if os.path.exists(p):
                    try:
                        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(p))
                        browser_obj = webbrowser.get('chrome')
                    except Exception:
                        pass
                    break

        browser_obj.open("https://www.instagram.com/direct/new/")
        time.sleep(3.5)

        is_top_chat = receiver.lower() in ["top chat", "recent chat", "first chat", "latest chat"]
        
        if not is_top_chat:
            pyautogui.write(receiver, interval=0.05)
            time.sleep(2.0)

        # Tab to the first user in the list (search result or top suggested)
        pyautogui.press("tab")
        time.sleep(0.3)
        pyautogui.press("space")
        time.sleep(0.5)

        # Navigate backwards to the "Next"/"Chat" button in the header
        # Shift+Tab 1: Back to Search Input
        pyautogui.hotkey("shift", "tab")
        time.sleep(0.3)
        # Shift+Tab 2: Back to Next/Chat Button
        pyautogui.hotkey("shift", "tab")
        time.sleep(0.3)
        
        # Press enter to open the chat
        pyautogui.press("enter")
        time.sleep(2.5)

        # Type and send the message
        pyautogui.write(message, interval=0.04)
        time.sleep(0.2)
        pyautogui.press("enter")

        return f"Message sent to {receiver} via Instagram."

    except Exception as e:
        return f"Instagram error: {e}"

def _send_telegram(receiver: str, message: str) -> str:
    """Sends a Telegram message via Windows desktop app."""
    try:
        if not _open_app("Telegram"):
            return "Could not open Telegram."

        time.sleep(1.5)

        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.4)
        pyautogui.write(receiver, interval=0.04)
        time.sleep(1.0)
        pyautogui.press("enter")
        time.sleep(0.8)

        pyautogui.write(message, interval=0.03)
        time.sleep(0.2)
        pyautogui.press("enter")

        return f"Message sent to {receiver} via Telegram."

    except Exception as e:
        return f"Telegram error: {e}"



def _send_generic(platform: str, receiver: str, message: str) -> str:
    """
    For any other platform not explicitly supported.
    Opens the app, searches for contact, types and sends.
    Works for: Messenger, Discord, Signal, etc.
    """
    try:
        if not _open_app(platform):
            return f"Could not open {platform}."

        time.sleep(1.5)
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.4)
        pyautogui.write(receiver, interval=0.04)
        time.sleep(1.0)
        pyautogui.press("enter")
        time.sleep(0.8)
        pyautogui.write(message, interval=0.03)
        time.sleep(0.2)
        pyautogui.press("enter")

        return f"Message sent to {receiver} via {platform}."

    except Exception as e:
        return f"{platform} error: {e}"

def send_message(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None
) -> str:
    """
    Called from main.py.

    parameters:
        receiver     : Contact name to send to
        message_text : The message content
        platform     : whatsapp | instagram | telegram | <any app name>
                       Default: whatsapp
    """
    params       = parameters or {}
    receiver     = params.get("receiver", "").strip()
    message_text = params.get("message_text", "").strip()
    
    import re
    # Clean up quotes and common LLM phrasing mistakes
    receiver = receiver.strip(' "\'')
    message_text = message_text.strip(' "\'')
    receiver = re.sub(r'(?i)\s+(on|via)\s+(whatsapp|telegram|instagram|discord|messenger|skype|signal).*$', '', receiver).strip()
    receiver = re.sub(r'(?i)^(to|for|message|contact)\s+', '', receiver).strip()
    platform     = params.get("platform", "whatsapp").strip().lower()

    browser_param = params.get("browser", "").lower().strip()
    if not browser_param and session_memory:
        try:
            mem_str = str(session_memory).lower()
            if "default browser is brave" in mem_str or "browser: brave" in mem_str:
                browser_param = "brave"
            elif "default browser is chrome" in mem_str or "browser: chrome" in mem_str:
                browser_param = "chrome"
            elif "default browser is firefox" in mem_str or "browser: firefox" in mem_str:
                browser_param = "firefox"
        except:
            pass

    if not receiver:
        return "Please specify who to send the message to, sir."
    if not message_text:
        return "Please specify what message to send, sir."

    print(f"[SendMessage] 📨 {platform} → {receiver}: {message_text[:40]}")
    if player:
        player.write_log(f"[msg] Sending to {receiver} via {platform}...")

    if "whatsapp" in platform or "wp" in platform or "wapp" in platform:
        result = _send_whatsapp(receiver, message_text)

    elif "instagram" in platform or "ig" in platform or "insta" in platform:
        result = _send_instagram(receiver, message_text, browser_param)

    elif "telegram" in platform or "tg" in platform:
        result = _send_telegram(receiver, message_text)

    else:
        result = _send_generic(platform, receiver, message_text)

    print(f"[SendMessage] ✅ {result}")
    if player:
        player.write_log(f"[msg] {result}")

    return result
