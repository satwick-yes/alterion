import unittest
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication
from ui import HudCanvas

class TestGuiVisualizer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create a single QApplication instance for all tests
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_hud_canvas_initialization(self):
        print("\n--- Running GUI Visualizer Initialization Test ---")
        # Ensure we can instantiate HudCanvas
        canvas = HudCanvas(face_path="", mini_mode=False)
        self.assertIsNotNone(canvas)
        self.assertEqual(canvas.state, "INITIALISING")
        self.assertEqual(canvas.mic_level, 0.0)
        self.assertFalse(canvas.speaking)
        self.assertFalse(canvas.muted)
        print("[PASS] HudCanvas instantiated successfully with default values.")

    def test_hud_canvas_state_updates(self):
        print("\n--- Running GUI Visualizer State Updates Test ---")
        canvas = HudCanvas(face_path="", mini_mode=False)
        
        # Test updating state
        canvas.state = "LISTENING"
        self.assertEqual(canvas.state, "LISTENING")
        
        # Test updating mic level
        canvas.mic_level = 0.85
        self.assertEqual(canvas.mic_level, 0.85)
        
        # Test updating speaking
        canvas.speaking = True
        self.assertTrue(canvas.speaking)
        
        # Test updating muted
        canvas.muted = True
        self.assertTrue(canvas.muted)
        
        print("[PASS] HudCanvas property setters and getters function perfectly.")

if __name__ == "__main__":
    unittest.main()
