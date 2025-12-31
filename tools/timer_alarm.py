"""
Module 22: Timer/Alarm
Gestion des minuteurs et alarmes
"""
import threading
import time
from datetime import datetime

class TimerManager:
    def __init__(self):
        self.timers = {}
    
    def set_timer(self, seconds, callback):
        timer_id = datetime.now().strftime('%Y%m%d%H%M%S')
        timer = threading.Timer(seconds, callback)
        self.timers[timer_id] = timer
        timer.start()
        return timer_id