"""
Module 28: Screen Capture
Capture d'écran
"""
import pyautogui
from datetime import datetime

class ScreenCapture:
    def capture(self, save_dir="screenshots"):
        import os
        os.makedirs(save_dir, exist_ok=True)
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(save_dir, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        return path