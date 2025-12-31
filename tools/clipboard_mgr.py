"""
Module 25: Clipboard Manager
Gestion du presse-papiers
"""
import pyperclip

class ClipboardManager:
    def __init__(self, history_size=10):
        self.history = []
        self.history_size = history_size
    
    def copy(self, text):
        pyperclip.copy(text)
        self.history.insert(0, text)
        if len(self.history) > self.history_size:
            self.history.pop()
    
    def paste(self):
        return pyperclip.paste()