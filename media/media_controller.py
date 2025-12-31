"""
Module 26: Media Controller
Contrôle des lecteurs multimédias
"""
import pyautogui

class MediaController:
    def play_pause(self):
        pyautogui.press('playpause')
    
    def next_track(self):
        pyautogui.press('nexttrack')
    
    def previous_track(self):
        pyautogui.press('prevtrack')