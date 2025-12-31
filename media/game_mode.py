"""
Module 30: Game Mode
Optimisation pour jeux
"""
import psutil
import os

class GameMode:
    def __init__(self):
        self.original_processes = []
    
    def enable(self):
        # Sauvegarder les processus actuels
        self.original_processes = [p.info for p in psutil.process_iter(['pid', 'name'])]
        
        # Fermer les applications non essentielles
        non_essential = ['chrome', 'firefox', 'spotify', 'discord']
        for proc in psutil.process_iter(['pid', 'name']):
            if any(app in proc.info['name'].lower() for app in non_essential):
                try:
                    psutil.Process(proc.info['pid']).terminate()
                except:
                    pass
    
    def disable(self):
        # Réactiver les processus (simplifié)
        print("Game Mode désactivé")