"""
Module 6: Auto Updater
Vérification et mise à jour automatique des dépendances
"""

import subprocess
import sys
import pkg_resources
import importlib
from typing import List, Dict, Tuple
import requests
import json
from datetime import datetime, timedelta

class AutoUpdater:
    def __init__(self, requirements_file: str = "requirements.txt"):
        """
        Initialise le système de mise à jour
        
        Args:
            requirements_file: Fichier des dépendances
        """
        self.requirements_file = requirements_file
        self.last_check_file = "data/last_update_check.json"
        self.check_interval = timedelta(days=1)  # Vérifier une fois par jour
        
        # Créer le dossier data
        import os
        os.makedirs(os.path.dirname(self.last_check_file), exist_ok=True)
    
    def check_dependencies(self) -> Dict[str, Dict]:
        """
        Vérifie l'état des dépendances
        
        Returns:
            État de chaque dépendance
        """
        dependencies = {}
        
        try:
            # Lire le fichier requirements
            with open(self.requirements_file, 'r') as f:
                requirements = f.readlines()
            
            for line in requirements:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parser le format package==version
                    if '==' in line:
                        package, required_version = line.split('==')
                    elif '>=' in line:
                        package, required_version = line.split('>=')
                        required_version = f">={required_version}"
                    elif '<=' in line:
                        package, required_version = line.split('<=')
                        required_version = f"<={required_version}"
                    else:
                        package = line
                        required_version = "latest"
                    
                    package = package.strip()
                    required_version = required_version.strip()
                    
                    # Vérifier si installé
                    try:
                        installed_version = pkg_resources.get_distribution(package).version
                        is_installed = True
                    except pkg_resources.DistributionNotFound:
                        installed_version = "Non installé"
                        is_installed = False
                    
                    # Vérifier les mises à jour disponibles
                    update_available = False
                    latest_version = None
                    
                    if is_installed:
                        try:
                            latest_version = self._get_latest_version(package)
                            if latest_version and latest_version != installed_version:
                                # Comparaison simple (pour version exacte)
                                if required_version == "latest":
                                    update_available = True
                                elif required_version.startswith(">="):
                                    min_version = required_version[2:]
                                    if self._compare_versions(installed_version, min_version) < 0:
                                        update_available = True
                                elif '==' in required_version:
                                    if installed_version != required_version.split('==')[1]:
                                        update_available = installed_version < required_version.split('==')[1]
                        except:
                            latest_version = "Inconnu"
                    
                    dependencies[package] = {
                        'required': required_version,
                        'installed': installed_version,
                        'latest': latest_version,
                        'installed_bool': is_installed,
                        'update_available': update_available,
                        'status': self._get_status(is_installed, update_available)
                    }
            
        except FileNotFoundError:
            print(f"✗ Fichier {self.requirements_file} non trouvé")
        except Exception as e:
            print(f"✗ Erreur vérification dépendances: {e}")
        
        return dependencies
    
    def _get_latest_version(self, package: str) -> str:
        """
        Récupère la dernière version d'un package
        
        Args:
            package: Nom du package
        
        Returns:
            Dernière version ou chaîne vide
        """
        try:
            # Utiliser pip index pour récupérer les infos
            result = subprocess.run(
                [sys.executable, "-m", "pip", "index", "versions", package],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Available versions:' in line:
                        versions = line.split('Available versions:')[1].strip()
                        # Prendre la première version (la plus récente)
                        latest = versions.split(',')[0].strip()
                        return latest
        
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  Timeout pour {package}")
        except Exception as e:
            print(f"  ✗ Erreur version {package}: {e}")
        
        # Fallback: utiliser PyPI API
        try:
            response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data['info']['version']
        except:
            pass
        
        return ""
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare deux versions
        
        Args:
            v1: Version 1
            v2: Version 2
        
        Returns:
            -1 si v1 < v2, 0 si égales, 1 si v1 > v2
        """
        try:
            from pkg_resources import parse_version
            pv1 = parse_version(v1)
            pv2 = parse_version(v2)
            
            if pv1 < pv2:
                return -1
            elif pv1 > pv2:
                return 1
            else:
                return 0
        except:
            # Comparaison simple
            return -1 if v1 < v2 else (1 if v1 > v2 else 0)
    
    def _get_status(self, installed: bool, update_available: bool) -> str:
        """Détermine le statut d'une dépendance"""
        if not installed:
            return "missing"
        elif update_available:
            return "outdated"
        else:
            return "ok"
    
    def install_dependencies(self, packages: List[str] = None) -> Dict[str, bool]:
        """
        Installe ou met à jour des packages
        
        Args:
            packages: Liste des packages (None pour tous)
        
        Returns:
            Résultat pour chaque package
        """
        results = {}
        
        if packages is None:
            # Installer tous les packages manquants
            dependencies = self.check_dependencies()
            packages_to_install = [
                pkg for pkg, info in dependencies.items()
                if not info['installed_bool']
            ]
        else:
            packages_to_install = packages
        
        if not packages_to_install:
            print("✓ Toutes les dépendances sont déjà installées")
            return {}
        
        print(f"📦 Installation de {len(packages_to_install)} packages...")
        
        for package in packages_to_install:
            try:
                print(f"  Installing {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                success = result.returncode == 0
                results[package] = success
                
                if success:
                    print(f"    ✓ {package} installé")
                else:
                    print(f"    ✗ {package} échec: {result.stderr[:100]}")
                    
            except subprocess.TimeoutExpired:
                print(f"    ✗ {package} timeout")
                results[package] = False
            except Exception as e:
                print(f"    ✗ {package} erreur: {e}")
                results[package] = False
        
        return results
    
    def update_dependencies(self, packages: List[str] = None) -> Dict[str, bool]:
        """
        Met à jour des packages
        
        Args:
            packages: Liste des packages (None pour tous obsolètes)
        
        Returns:
            Résultat pour chaque package
        """
        results = {}
        
        # Vérifier quels packages ont besoin d'être mis à jour
        dependencies = self.check_dependencies()
        
        if packages is None:
            packages_to_update = [
                pkg for pkg, info in dependencies.items()
                if info['update_available']
            ]
        else:
            packages_to_update = packages
        
        if not packages_to_update:
            print("✓ Tous les packages sont à jour")
            return {}
        
        print(f"🔄 Mise à jour de {len(packages_to_update)} packages...")
        
        for package in packages_to_update:
            try:
                print(f"  Updating {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", package],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                success = result.returncode == 0
                results[package] = success
                
                if success:
                    print(f"    ✓ {package} mis à jour")
                else:
                    print(f"    ✗ {package} échec: {result.stderr[:100]}")
                    
            except subprocess.TimeoutExpired:
                print(f"    ✗ {package} timeout")
                results[package] = False
            except Exception as e:
                print(f"    ✗ {package} erreur: {e}")
                results[package] = False
        
        return results
    
    def check_for_updates(self, force: bool = False) -> Dict:
        """
        Vérifie les mises à jour disponibles
        
        Args:
            force: Forcer la vérification même si récente
        
        Returns:
            Informations sur les mises à jour
        """
        # Vérifier quand a eu lieu la dernière vérification
        if not force:
            last_check = self._load_last_check()
            if last_check and (datetime.now() - last_check) < self.check_interval:
                print("✓ Dernière vérification récente, ignorée")
                return {"skipped": True}
        
        print("🔍 Vérification des mises à jour...")
        
        # Vérifier les dépendances
        dependencies = self.check_dependencies()
        
        # Compter les différents statuts
        stats = {
            'total': len(dependencies),
            'missing': sum(1 for info in dependencies.values() if info['status'] == 'missing'),
            'outdated': sum(1 for info in dependencies.values() if info['status'] == 'outdated'),
            'ok': sum(1 for info in dependencies.values() if info['status'] == 'ok')
        }
        
        # Sauvegarder la date de vérification
        self._save_last_check()
        
        return {
            'dependencies': dependencies,
            'stats': stats,
            'timestamp': datetime.now().isoformat(),
            'needs_action': stats['missing'] > 0 or stats['outdated'] > 0
        }
    
    def _load_last_check(self) -> Optional[datetime]:
        """Charge la date de la dernière vérification"""
        try:
            with open(self.last_check_file, 'r') as f:
                data = json.load(f)
                return datetime.fromisoformat(data['last_check'])
        except:
            return None
    
    def _save_last_check(self):
        """Sauvegarde la date de vérification"""
        try:
            data = {
                'last_check': datetime.now().isoformat(),
                'version': '1.0'
            }
            with open(self.last_check_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"✗ Erreur sauvegarde vérification: {e}")
    
    def fix_all(self) -> Dict[str, Dict]:
        """
        Répare toutes les dépendances (installe manquantes, met à jour obsolètes)
        
        Returns:
            Résultats des opérations
        """
        print("🔧 Réparation des dépendances...")
        
        results = {
            'installed': {},
            'updated': {}
        }
        
        # 1. Installer les manquantes
        dependencies = self.check_dependencies()
        missing = [pkg for pkg, info in dependencies.items() if info['status'] == 'missing']
        
        if missing:
            print(f"📦 Installation des {len(missing)} packages manquants...")
            results['installed'] = self.install_dependencies(missing)
        
        # 2. Mettre à jour les obsolètes
        dependencies = self.check_dependencies()  # Re-vérifier après installation
        outdated = [pkg for pkg, info in dependencies.items() if info['status'] == 'outdated']
        
        if outdated:
            print(f"🔄 Mise à jour des {len(outdated)} packages obsolètes...")
            results['updated'] = self.update_dependencies(outdated)
        
        # 3. Vérifier le résultat final
        final_check = self.check_dependencies()
        all_ok = all(info['status'] == 'ok' for info in final_check.values())
        
        results['final_status'] = {
            'all_ok': all_ok,
            'dependencies': final_check
        }
        
        if all_ok:
            print("✓ Toutes les dépendances sont OK !")
        else:
            print("⚠️  Certaines dépendances nécessitent une attention manuelle")
        
        return results
    
    def generate_report(self) -> str:
        """
        Génère un rapport des dépendances
        
        Returns:
            Rapport formaté
        """
        dependencies = self.check_dependencies()
        
        report = "📦 **Rapport des Dépendances**\n\n"
        
        for package, info in dependencies.items():
            emoji = {
                'missing': '❌',
                'outdated': '🔄',
                'ok': '✅'
            }.get(info['status'], '❓')
            
            report += f"{emoji} **{package}**\n"
            report += f"   Requis: {info['required']}\n"
            report += f"   Installé: {info['installed']}\n"
            
            if info['latest'] and info['latest'] != info['installed']:
                report += f"   Dernière: {info['latest']}\n"
            
            report += "\n"
        
        # Statistiques
        stats = {
            'missing': sum(1 for info in dependencies.values() if info['status'] == 'missing'),
            'outdated': sum(1 for info in dependencies.values() if info['status'] == 'outdated'),
            'ok': sum(1 for info in dependencies.values() if info['status'] == 'ok')
        }
        
        report += f"📊 **Statistiques:**\n"
        report += f"   Total: {len(dependencies)}\n"
        report += f"   ✅ OK: {stats['ok']}\n"
        report += f"   🔄 Obsolètes: {stats['outdated']}\n"
        report += f"   ❌ Manquants: {stats['missing']}\n"
        
        return report

# Test du module
if __name__ == "__main__":
    updater = AutoUpdater()
    
    print("🔧 Test Auto Updater\n")
    
    # Vérifier les dépendances
    print("1. Vérification des dépendances:")
    dependencies = updater.check_dependencies()
    
    for package, info in list(dependencies.items())[:3]:  # Afficher 3 seulement
        status_emoji = {
            'missing': '❌',
            'outdated': '🔄',
            'ok': '✅'
        }.get(info['status'], '❓')
        
        print(f"   {status_emoji} {package}: {info['installed']} "
              f"(requis: {info['required']})")
    
    print(f"\n   Total: {len(dependencies)} packages")
    
    # Vérifier les mises à jour
    print("\n2. Vérification des mises à jour:")
    update_info = updater.check_for_updates(force=True)
    
    if 'stats' in update_info:
        stats = update_info['stats']
        print(f"   ✅ OK: {stats['ok']}")
        print(f"   🔄 Obsolètes: {stats['outdated']}")
        print(f"   ❌ Manquants: {stats['missing']}")
    
    # Générer un rapport
    print("\n3. Rapport complet:")
    report = updater.generate_report()
    print(report)
    
    # Note: Ne pas installer/mettre à jour automatiquement pendant le test
    print("\n⚠️  Note: Les installations/mises à jour sont désactivées en mode test")
    print("   Pour installer: updater.fix_all()")