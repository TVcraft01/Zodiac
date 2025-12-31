"""
Scanner simple d'applications
"""

import os

class VaultScanner:
    def scan_basic(self):
        """Scan basique des applications courantes"""
        apps = {
            "chrome": {
                "name": "Google Chrome",
                "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "type": "navigateur"
            },
            "firefox": {
                "name": "Mozilla Firefox", 
                "path": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                "type": "navigateur"
            },
            "deezer": {
                "name": "Deezer",
                "path": os.path.expandvars("%LOCALAPPDATA%\\Programs\\Deezer\\Deezer.exe"),
                "type": "musique"
            },
            "spotify": {
                "name": "Spotify",
                "path": os.path.expandvars("%APPDATA%\\Spotify\\Spotify.exe"),
                "type": "musique"
            },
            "vscode": {
                "name": "Visual Studio Code",
                "path": os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe"),
                "type": "dev"
            },
            "discord": {
                "name": "Discord",
                "path": os.path.expandvars("%LOCALAPPDATA%\\Discord\\app-*\\Discord.exe"),
                "type": "communication"
            }
        }
        return apps