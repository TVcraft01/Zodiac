"""
Vault Scanner - Trouve toutes les applications du système
"""

import os
import glob
import json
import hashlib
from datetime import datetime
import winreg

class VaultScanner:
    def __init__(self):
        self.scan_paths = [
            # Bureau et documents
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Documents"),
            
            # Program Files
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            
            # AppData
            os.path.expandvars("%APPDATA%"),
            os.path.expandvars("%LOCALAPPDATA%"),
            
            # Menu Démarrer
            os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs"),
            os.path.expandvars("%PROGRAMDATA%\\Microsoft\\Windows\\Start Menu\\Programs"),
            
            # Windows
            "C:\\Windows",
            "C:\\Windows\\System32"
        ]
        
    def scan_system(self):
        """Scan complet du système"""
        print("🔍 Début du scan système...")
        
        apps = {}
        
        # 1. Scanner les fichiers
        apps.update(self.scan_files())
        
        # 2. Scanner le registre (applications installées)
        apps.update(self.scan_registry())
        
        # 3. Scanner les raccourcis
        apps.update(self.scan_shortcuts())
        
        print(f"✅ Scan terminé: {len(apps)} applications trouvées")
        return apps
        
    def scan_files(self):
        """Scan les fichiers exécutables"""
        apps = {}
        
        for path in self.scan_paths:
            if os.path.exists(path):
                try:
                    # Chercher .exe
                    for file_path in glob.glob(os.path.join(path, "**/*.exe"), recursive=True):
                        self._add_executable(apps, file_path)
                        
                    # Chercher .msi
                    for file_path in glob.glob(os.path.join(path, "**/*.msi"), recursive=True):
                        self._add_installer(apps, file_path)
                        
                except Exception as e:
                    print(f"⚠️ Erreur scan {path}: {e}")
        
        return apps
        
    def scan_registry(self):
        """Scan le registre Windows pour les applications installées"""
        apps = {}
        
        try:
            # Clés du registre pour les applications installées
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            ]
            
            for hive, path in reg_paths:
                try:
                    key = winreg.OpenKey(hive, path)
                    
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            
                            # Récupérer les infos
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                display_version = winreg.QueryValueEx(subkey, "DisplayVersion")[0] if winreg.QueryValueEx(subkey, "DisplayVersion")[0] else ""
                                
                                # Générer un ID unique
                                app_id = hashlib.md5(f"{display_name}{install_location}".encode()).hexdigest()[:8]
                                
                                apps[app_id] = {
                                    'name': display_name,
                                    'path': install_location,
                                    'version': display_version,
                                    'type': 'installed',
                                    'source': 'registry',
                                    'scanned_at': datetime.now().isoformat()
                                }
                                
                            except:
                                pass
                                
                            winreg.CloseKey(subkey)
                            
                        except:
                            pass
                            
                    winreg.CloseKey(key)
                    
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Erreur scan registre: {e}")
            
        return apps
        
    def scan_shortcuts(self):
        """Scan les raccourcis .lnk"""
        apps = {}
        
        for path in self.scan_paths:
            if os.path.exists(path):
                try:
                    for file_path in glob.glob(os.path.join(path, "**/*.lnk"), recursive=True):
                        self._add_shortcut(apps, file_path)
                except:
                    pass
                    
        return apps
        
    def _add_executable(self, apps, file_path):
        """Ajoute un exécutable"""
        try:
            file_name = os.path.basename(file_path)
            file_name_no_ext = os.path.splitext(file_name)[0]
            
            # Générer un ID unique
            app_id = hashlib.md5(file_path.encode()).hexdigest()[:8]
            
            apps[app_id] = {
                'name': file_name_no_ext,
                'path': file_path,
                'type': 'executable',
                'size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                'source': 'file_system',
                'scanned_at': datetime.now().isoformat()
            }
            
        except:
            pass
            
    def _add_installer(self, apps, file_path):
        """Ajoute un installer"""
        try:
            file_name = os.path.basename(file_path)
            file_name_no_ext = os.path.splitext(file_name)[0]
            
            app_id = hashlib.md5(file_path.encode()).hexdigest()[:8]
            
            apps[app_id] = {
                'name': file_name_no_ext,
                'path': file_path,
                'type': 'installer',
                'source': 'file_system',
                'scanned_at': datetime.now().isoformat()
            }
            
        except:
            pass
            
    def _add_shortcut(self, apps, file_path):
        """Ajoute un raccourci"""
        try:
            file_name = os.path.basename(file_path)
            file_name_no_ext = os.path.splitext(file_name)[0]
            
            app_id = hashlib.md5(file_path.encode()).hexdigest()[:8]
            
            apps[app_id] = {
                'name': file_name_no_ext,
                'path': file_path,
                'type': 'shortcut',
                'source': 'shortcut',
                'scanned_at': datetime.now().isoformat()
            }
            
        except:
            pass