import pyautogui
import ctypes
import math
import platform
import subprocess
from PyQt6.QtCore import QObject, pyqtSlot

# Adjust these parameters to change mouse speed and smoothing
MOUSE_SPEED_X = 2.5
MOUSE_SPEED_Y = 2.5
SMOOTHING = 0.5

# Fail-safe to avoid getting stuck in a corner
pyautogui.FAILSAFE = False

class GestureController(QObject):
    def __init__(self):
        super().__init__()
        self.screen_w, self.screen_h = pyautogui.size()
        self.last_mouse_x = None
        self.last_mouse_y = None
        
        # We assume volume is managed via pynput or ctypes.
        # Since pycaw can be complex to setup perfectly for all,
        # we will use Windows native virtual key codes for volume.

    @pyqtSlot(float, float)
    def mouseMove(self, norm_x: float, norm_y: float):
        """Moves the mouse based on normalized coordinates from the camera (0 to 1)."""
        target_x = int(norm_x * self.screen_w * MOUSE_SPEED_X - (self.screen_w * (MOUSE_SPEED_X - 1) / 2))
        target_y = int(norm_y * self.screen_h * MOUSE_SPEED_Y - (self.screen_h * (MOUSE_SPEED_Y - 1) / 2))

        # Clamp to screen
        target_x = max(0, min(self.screen_w - 1, target_x))
        target_y = max(0, min(self.screen_h - 1, target_y))

        if self.last_mouse_x is None:
            self.last_mouse_x = target_x
            self.last_mouse_y = target_y

        # Smooth movement
        new_x = int(self.last_mouse_x + (target_x - self.last_mouse_x) * SMOOTHING)
        new_y = int(self.last_mouse_y + (target_y - self.last_mouse_y) * SMOOTHING)
        
        pyautogui.moveTo(new_x, new_y)
        self.last_mouse_x = new_x
        self.last_mouse_y = new_y

    @pyqtSlot(float, float)
    def mouseMoveAbsolute(self, norm_x: float, norm_y: float):
        """Moves the mouse precisely to the normalized coordinates without scaling."""
        target_x = int(norm_x * self.screen_w)
        target_y = int(norm_y * self.screen_h)

        # Clamp to screen
        target_x = max(0, min(self.screen_w - 1, target_x))
        target_y = max(0, min(self.screen_h - 1, target_y))
        
        pyautogui.moveTo(target_x, target_y)
        self.last_mouse_x = target_x
        self.last_mouse_y = target_y

    @pyqtSlot()
    def mouseClickLeft(self):
        pyautogui.click(button='left')

    @pyqtSlot()
    def mouseClickRight(self):
        pyautogui.click(button='right')

    @pyqtSlot()
    def mouseDown(self):
        pyautogui.mouseDown(button='left')

    @pyqtSlot()
    def mouseUp(self):
        pyautogui.mouseUp(button='left')

    @pyqtSlot(int)
    def scroll(self, delta: int):
        pyautogui.scroll(delta)

    @pyqtSlot(str)
    def swipe(self, direction: str):
        """Handles desktop switching and window management."""
        if direction == 'left':
            pyautogui.hotkey('ctrl', 'win', 'right') # Switch to right desktop
        elif direction == 'right':
            pyautogui.hotkey('ctrl', 'win', 'left') # Switch to left desktop
        elif direction == 'up':
            pyautogui.hotkey('win', 'up') # Maximize
        elif direction == 'down':
            pyautogui.hotkey('win', 'down') # Minimize

    @pyqtSlot(int)
    def volumeChange(self, delta: int):
        """Change system volume using virtual keys. Delta is usually positive or negative."""
        VK_VOLUME_UP = 0xAF
        VK_VOLUME_DOWN = 0xAE
        
        if platform.system() == "Windows":
            steps = abs(delta)
            vk = VK_VOLUME_UP if delta > 0 else VK_VOLUME_DOWN
            for _ in range(steps):
                ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
                ctypes.windll.user32.keybd_event(vk, 0, 2, 0) # key up

    @pyqtSlot()
    def volumeMute(self):
        VK_VOLUME_MUTE = 0xAD
        if platform.system() == "Windows":
            ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)

    @pyqtSlot()
    def mediaPlayPause(self):
        VK_MEDIA_PLAY_PAUSE = 0xB3
        if platform.system() == "Windows":
            ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 2, 0)
