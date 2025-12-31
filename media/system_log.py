"""
Module 31: System Log
Journalisation système
"""
import json
from datetime import datetime

class SystemLogger:
    def __init__(self, log_file="data/system_log.json"):
        self.log_file = log_file
        self.logs = []
    
    def log(self, action, details=""):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details
        }
        self.logs.append(entry)
        self._save()
    
    def _save(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.logs[-100:], f, indent=2)  # Garder 100 dernières entrées