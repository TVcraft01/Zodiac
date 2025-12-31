"""
Module 4: Task Killer
Gestion des processus et fermeture d'applications
"""

import psutil
import os
import signal
import platform
from typing import List, Optional, Dict

class TaskKiller:
    def __init__(self):
        """Initialise le gestionnaire de tâches"""
        self.system = platform.system().lower()
    
    def kill_process(self, process_name: str, force: bool = False) -> bool:
        """
        Tue un processus par son nom
        
        Args:
            process_name: Nom du processus
            force: Force la fermeture
        
        Returns:
            True si succès
        """
        try:
            process_name = process_name.lower()
            killed = False
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # Vérifier par nom
                    if proc.info['name'] and process_name in proc.info['name'].lower():
                        self._terminate_process(proc, force)
                        print(f"✓ Processus terminé: {proc.info['name']} (PID: {proc.info['pid']})")
                        killed = True
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return killed
            
        except Exception as e:
            print(f"✗ Erreur kill_process: {e}")
            return False
    
    def kill_pid(self, pid: int, force: bool = False) -> bool:
        """
        Tue un processus par son PID
        
        Args:
            pid: ID du processus
            force: Force la fermeture
        
        Returns:
            True si succès
        """
        try:
            proc = psutil.Process(pid)
            self._terminate_process(proc, force)
            print(f"✓ Processus terminé: {proc.name()} (PID: {pid})")
            return True
            
        except psutil.NoSuchProcess:
            print(f"✗ Processus {pid} non trouvé")
            return False
        except psutil.AccessDenied:
            print(f"✗ Accès refusé pour le processus {pid}")
            return False
        except Exception as e:
            print(f"✗ Erreur kill_pid: {e}")
            return False
    
    def _terminate_process(self, proc: psutil.Process, force: bool = False):
        """
        Termine un processus
        
        Args:
            proc: Processus à terminer
            force: Force la fermeture
        """
        try:
            if force:
                proc.kill()
            else:
                proc.terminate()
        except:
            try:
                proc.kill()
            except:
                pass
    
    def kill_by_window_title(self, window_title: str, force: bool = False) -> bool:
        """
        Tue un processus par le titre de sa fenêtre
        
        Args:
            window_title: Titre de la fenêtre
            force: Force la fermeture
        
        Returns:
            True si succès
        """
        try:
            import pygetwindow as gw
            
            windows = gw.getWindowsWithTitle(window_title)
            
            if not windows:
                print(f"✗ Aucune fenêtre trouvée avec: {window_title}")
                return False
            
            killed_count = 0
            
            for window in windows:
                try:
                    # Récupérer le PID depuis le handle de fenêtre
                    pid = window._hWnd  # Note: Ceci est spécifique à Windows
                    
                    # Sur Windows, nous pouvons utiliser taskkill
                    if self.system == "windows":
                        os.system(f"taskkill /PID {pid} {'/F' if force else ''}")
                        killed_count += 1
                        print(f"✓ Fenêtre fermée: {window.title}")
                    
                except Exception as e:
                    print(f"✗ Erreur fermeture fenêtre: {e}")
            
            return killed_count > 0
            
        except ImportError:
            print("✗ pygetwindow non disponible pour cette fonctionnalité")
            return False
        except Exception as e:
            print(f"✗ Erreur kill_by_window_title: {e}")
            return False
    
    def kill_all_except(self, allowed_processes: List[str]) -> int:
        """
        Tue tous les processus sauf ceux autorisés
        
        Args:
            allowed_processes: Liste des processus autorisés
        
        Returns:
            Nombre de processus terminés
        """
        try:
            allowed_lower = [p.lower() for p in allowed_processes]
            killed_count = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name']
                    
                    if proc_name:
                        proc_name_lower = proc_name.lower()
                        
                        # Vérifier si le processus est autorisé
                        is_allowed = False
                        for allowed in allowed_lower:
                            if allowed in proc_name_lower:
                                is_allowed = True
                                break
                        
                        # Tuer si non autorisé
                        if not is_allowed and proc.info['pid'] != os.getpid():
                            self._terminate_process(proc)
                            killed_count += 1
                            print(f"  Terminé: {proc_name}")
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print(f"✓ {killed_count} processus terminés")
            return killed_count
            
        except Exception as e:
            print(f"✗ Erreur kill_all_except: {e}")
            return 0
    
    def get_process_info(self, pid: int) -> Optional[Dict]:
        """
        Récupère les informations détaillées d'un processus
        
        Args:
            pid: ID du processus
        
        Returns:
            Informations du processus ou None
        """
        try:
            proc = psutil.Process(pid)
            
            with proc.oneshot():
                info = {
                    'pid': pid,
                    'name': proc.name(),
                    'exe': proc.exe(),
                    'cmdline': proc.cmdline(),
                    'status': proc.status(),
                    'cpu_percent': proc.cpu_percent(),
                    'memory_percent': proc.memory_percent(),
                    'memory_info': proc.memory_info()._asdict(),
                    'create_time': proc.create_time(),
                    'num_threads': proc.num_threads(),
                    'username': proc.username(),
                    'ppid': proc.ppid()  # Parent PID
                }
            
            return info
            
        except psutil.NoSuchProcess:
            return None
        except Exception as e:
            print(f"✗ Erreur get_process_info: {e}")
            return None
    
    def list_processes(self, filter_term: str = "") -> List[Dict]:
        """
        Liste tous les processus
        
        Args:
            filter_term: Filtrer par nom
        
        Returns:
            Liste des processus
        """
        processes = []
        filter_term = filter_term.lower()
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'] or ""
                    
                    # Filtrer si nécessaire
                    if filter_term and filter_term not in proc_name.lower():
                        continue
                    
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_name,
                        'cpu': proc_info['cpu_percent'],
                        'memory': round(proc_info['memory_percent'], 1),
                        'status': proc_info['status']
                    })
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Trier par utilisation mémoire (décroissant)
            processes.sort(key=lambda x: x['memory'], reverse=True)
            
        except Exception as e:
            print(f"✗ Erreur list_processes: {e}")
        
        return processes
    
    def cleanup_zombie_processes(self) -> int:
        """
        Nettoie les processus zombies
        
        Returns:
            Nombre de zombies nettoyés
        """
        cleaned = 0
        
        try:
            for proc in psutil.process_iter():
                try:
                    if proc.status() == psutil.STATUS_ZOMBIE:
                        print(f"  Zombie trouvé: {proc.name()} (PID: {proc.pid})")
                        self._terminate_process(proc, force=True)
                        cleaned += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if cleaned > 0:
                print(f"✓ {cleaned} processus zombies nettoyés")
            
        except Exception as e:
            print(f"✗ Erreur cleanup_zombie: {e}")
        
        return cleaned

# Test du module
if __name__ == "__main__":
    killer = TaskKiller()
    
    print("⚡ Test Task Killer\n")
    
    # Lister les processus
    print("1. Liste des processus (top 5 par mémoire):")
    processes = killer.list_processes()
    
    for i, proc in enumerate(processes[:5], 1):
        print(f"   {i}. {proc['name'][:30]:30} PID:{proc['pid']:6} "
              f"CPU:{proc['cpu']:5.1f}% MEM:{proc['memory']:5.1f}%")
    
    # Informations sur le processus courant
    print(f"\n2. Processus courant (PID: {os.getpid()}):")
    info = killer.get_process_info(os.getpid())
    
    if info:
        print(f"   Nom: {info['name']}")
        print(f"   Exe: {info['exe']}")
        print(f"   Utilisateur: {info['username']}")
        print(f"   Threads: {info['num_threads']}")
    
    # Nettoyer les zombies (simulation)
    print(f"\n3. Nettoyage zombies:")
    zombies_cleaned = killer.cleanup_zombie_processes()
    print(f"   Zombies nettoyés: {zombies_cleaned}")
    
    # Warning: Ne pas tuer de vrais processus dans le test
    print("\n⚠️  Note: Les fonctions de kill sont désactivées en mode test")
    print("   Pour tester: killer.kill_process('notepad', force=False)")