"""
Module 2: App Launcher
Exécution sécurisée des applications
"""

import os
import subprocess
import platform
from typing import Optional, Dict
import psutil

class AppLauncher:
    def __init__(self):
        """Initialise le lanceur d'applications"""
        self.system = platform.system().lower()
    
    def launch_app(self, app_info: Dict) -> bool:
        """
        Lance une application
        
        Args:
            app_info: Informations de l'application
        
        Returns:
            True si succès
        """
        try:
            app_path = app_info.get('path')
            
            if not app_path or not os.path.exists(app_path):
                print(f"✗ Fichier non trouvé: {app_path}")
                return False
            
            print(f"🚀 Lancement: {app_info.get('name', 'Inconnu')}")
            
            if self.system == "windows":
                return self._launch_windows(app_path, app_info)
            elif self.system == "darwin":  # macOS
                return self._launch_macos(app_path, app_info)
            else:  # Linux/Unix
                return self._launch_linux(app_path, app_info)
                
        except Exception as e:
            print(f"✗ Erreur lancement: {e}")
            return False
    
    def _launch_windows(self, app_path: str, app_info: Dict) -> bool:
        """Lance une application sur Windows"""
        try:
            # Pour les .exe
            if app_path.lower().endswith('.exe'):
                subprocess.Popen([app_path], 
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                return True
            
            # Pour les .lnk
            elif app_path.lower().endswith('.lnk'):
                import pythoncom
                from win32com.client import Dispatch
                
                pythoncom.CoInitialize()
                shell = Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(app_path)
                target = shortcut.Targetpath
                args = shortcut.Arguments
                working_dir = shortcut.WorkingDirectory
                
                if args:
                    subprocess.Popen([target, args], 
                                   cwd=working_dir,
                                   shell=True,
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                else:
                    subprocess.Popen([target], 
                                   cwd=working_dir,
                                   shell=True,
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                return True
            
            # Autres fichiers
            else:
                os.startfile(app_path)
                return True
                
        except Exception as e:
            print(f"✗ Erreur Windows: {e}")
            return False
    
    def _launch_macos(self, app_path: str, app_info: Dict) -> bool:
        """Lance une application sur macOS"""
        try:
            # Pour les .app
            if app_path.endswith('.app'):
                subprocess.Popen(['open', '-a', app_path])
                return True
            
            # Pour les scripts/exécutables
            elif os.access(app_path, os.X_OK):
                subprocess.Popen([app_path])
                return True
            
            # Ouvrir avec l'application par défaut
            else:
                subprocess.Popen(['open', app_path])
                return True
                
        except Exception as e:
            print(f"✗ Erreur macOS: {e}")
            return False
    
    def _launch_linux(self, app_path: str, app_info: Dict) -> bool:
        """Lance une application sur Linux"""
        try:
            # Vérifier si exécutable
            if os.access(app_path, os.X_OK):
                subprocess.Popen([app_path])
                return True
            
            # Essayer avec xdg-open (ouverture par défaut)
            else:
                subprocess.Popen(['xdg-open', app_path])
                return True
                
        except Exception as e:
            print(f"✗ Erreur Linux: {e}")
            return False
    
    def launch_with_args(self, app_path: str, arguments: list) -> bool:
        """
        Lance une application avec des arguments
        
        Args:
            app_path: Chemin de l'application
            arguments: Liste des arguments
        
        Returns:
            True si succès
        """
        try:
            cmd = [app_path] + arguments
            subprocess.Popen(cmd, shell=(self.system == "windows"))
            return True
        except Exception as e:
            print(f"✗ Erreur lancement avec args: {e}")
            return False
    
    def launch_url(self, url: str) -> bool:
        """
        Ouvre une URL dans le navigateur par défaut
        
        Args:
            url: URL à ouvrir
        
        Returns:
            True si succès
        """
        try:
            if self.system == "windows":
                os.startfile(url)
            elif self.system == "darwin":
                subprocess.Popen(['open', url])
            else:
                subprocess.Popen(['xdg-open', url])
            return True
        except Exception as e:
            print(f"✗ Erreur ouverture URL: {e}")
            return False
    
    def is_app_running(self, app_name: str) -> bool:
        """
        Vérifie si une application est en cours d'exécution
        
        Args:
            app_name: Nom du processus
        
        Returns:
            True si l'application tourne
        """
        try:
            app_name_lower = app_name.lower()
            
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    # Vérifier par nom
                    if proc.info['name'] and app_name_lower in proc.info['name'].lower():
                        return True
                    
                    # Vérifier par chemin
                    if proc.info['exe'] and app_name_lower in proc.info['exe'].lower():
                        return True
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return False
            
        except Exception as e:
            print(f"✗ Erreur vérification processus: {e}")
            return False
    
    def get_running_apps(self) -> list:
        """
        Liste les applications en cours d'exécution
        
        Returns:
            Liste des processus
        """
        running_apps = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    
                    # Filtrer les processus système
                    if info['name'] and info['exe']:
                        app_info = {
                            'pid': info['pid'],
                            'name': info['name'],
                            'path': info['exe'],
                            'cpu': info['cpu_percent'],
                            'memory': info['memory_percent']
                        }
                        running_apps.append(app_info)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
        except Exception as e:
            print(f"✗ Erreur liste processus: {e}")
        
        return running_apps

# Test du module
if __name__ == "__main__":
    launcher = AppLauncher()
    
    print("🚀 Test App Launcher")
    print(f"Système: {platform.system()}")
    
    # Tester l'ouverture d'URL
    print("\n1. Test ouverture URL:")
    success = launcher.launch_url("https://github.com")
    print(f"   Résultat: {'✓ Succès' if success else '✗ Échec'}")
    
    # Vérifier les applications en cours
    print("\n2. Applications en cours:")
    running = launcher.get_running_apps()
    for app in running[:5]:  # Afficher seulement 5
        print(f"   • {app['name']} (PID: {app['pid']})")
    
    print(f"\n   Total: {len(running)} processus")
    
    # Vérifier si Chrome tourne
    print("\n3. Chrome en cours?")
    chrome_running = launcher.is_app_running("chrome")
    print(f"   Chrome running: {chrome_running}")