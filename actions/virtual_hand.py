import sys
import json
import threading
import math
import platform
import time
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor

# Force DPI awareness for the subprocess so the UI overlay maps 1:1 with the screen
if platform.system() == "Windows":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception as e:
        print(f"DPI setting failed: {e}")

import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from gesture_controller import GestureController

class VirtualHandWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(50, 50, 200, 200)
        
        self.norm_x = 0.5
        self.norm_y = 0.5
        self.is_pinching = False
        
        self.gesture_ctrl = GestureController()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_from_queue)
        self.timer.start(30)
        
        self.command_queue = []
        
        self.reader_thread = threading.Thread(target=self.read_stdin, daemon=True)
        self.reader_thread.start()

    def read_stdin(self):
        for line in sys.stdin:
            try:
                cmd = json.loads(line)
                self.command_queue.append(cmd)
            except Exception:
                pass

    def update_from_queue(self):
        updated = False
        while self.command_queue:
            cmd = self.command_queue.pop(0)
            if "norm_x" in cmd and "norm_y" in cmd:
                self.norm_x = cmd["norm_x"]
                self.norm_y = cmd["norm_y"]
                self.gesture_ctrl.mouseMoveAbsolute(self.norm_x, self.norm_y)
                updated = True
            
            if "click" in cmd and cmd["click"]:
                self.is_pinching = True
                
                # Check if the AI or system requested a double click for desktop items
                if cmd["click"] == "double" or cmd.get("double_click"):
                    self.gesture_ctrl.mouseClickLeft()
                    time.sleep(0.08) # Standard OS double-click interval
                    self.gesture_ctrl.mouseClickLeft()
                else:
                    self.gesture_ctrl.mouseClickLeft()
                    
                QTimer.singleShot(200, self.release_pinch)
                updated = True
                
            if "action" in cmd and cmd["action"] == "close":
                QApplication.quit()
                
        if updated:
            self.update()

    def release_pinch(self):
        self.is_pinching = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background bubble
        painter.setBrush(QColor(0, 0, 0, 150))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        
        # Wireframe logic
        center_x = self.width() / 2 + (self.norm_x - 0.5) * 50
        center_y = self.height() / 2 + (self.norm_y - 0.5) * 50
        
        pen = QPen(QColor(0, 255, 255))
        pen.setWidth(3)
        painter.setPen(pen)
        
        wrist = QPointF(center_x, center_y + 50)
        palm = QPointF(center_x, center_y)
        
        for i, angle in enumerate([-40, -15, 10, 35, 60]):
            rad = angle * 3.14159 / 180
            length = 60 if i == 2 else (50 if i in (1, 3) else 40)
            
            if self.is_pinching and i in (0, 1): # Thumb and index pinch
                tip_x = center_x - 15
                tip_y = center_y - 25
            else:
                tip_x = center_x + math.sin(rad) * length
                tip_y = center_y - math.cos(rad) * length
                
            tip = QPointF(tip_x, tip_y)
            painter.drawLine(palm, tip)
            
            painter.setBrush(QColor(255, 0, 255))
            painter.drawEllipse(tip, 4, 4)
            
        painter.drawLine(wrist, palm)
        painter.setBrush(QColor(255, 255, 0))
        painter.drawEllipse(palm, 6, 6)
        painter.drawEllipse(wrist, 6, 6)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VirtualHandWindow()
    window.show()
    sys.exit(app.exec())
