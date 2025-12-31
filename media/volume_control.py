"""
Module 27: Volume Master
Contrôle du volume système
"""
import os

class VolumeControl:
    def set_volume(self, percent):
        if os.name == 'nt':
            os.system(f'nircmd.exe setsysvolume {percent*655}')