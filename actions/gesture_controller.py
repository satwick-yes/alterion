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
    def mouseMoveAbsolute(self, norm_x: float, norm_y: float):
        """Moves the mouse precisely to the normalized coordinates without scaling."""
        target_x = int(norm_x * self.screen_w)
        target_y = int(norm_y * self.screen_h)

        # Clamp to screen
        target_x = max(0, min(self.screen_w - 1, target_x))
        target_y = max(0, min(self.screen_h - 1, target_y))
        
        pyautogui.FAILSAFE = False
        try:
            pyautogui.moveTo(target_x, target_y)
        except pyautogui.FailSafeException:
            pass
            
        self.last_mouse_x = target_x
        self.last_mouse_y = target_y

    @pyqtSlot()
    def mouseClickLeft(self):
        pyautogui.click(button='left')

    @pyqtSlot()
    def mouseDown(self):
        pyautogui.mouseDown(button='left')

    @pyqtSlot()
    def mouseUp(self):
        pyautogui.mouseUp(button='left')

    @pyqtSlot(int)
    def scroll(self, delta: int):
        pyautogui.scroll(delta)

