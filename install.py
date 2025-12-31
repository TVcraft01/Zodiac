"""
Script d'installation pour Zodiac v10.0
"""

import subprocess
import sys
import os
from pathlib import Path

def print_banner():
    """Affiche la bannière"""
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║            🚀 INSTALLATION ZODIAC v10.0           ║
    ╚═══════════════════════════════════════════════════╝
    """)

def check_python():
    """Vérifie la version de Python"""
    print("🔍 Vérification de Python...")
    
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ requis (vous avez {sys.version})")
        print("📥 Téléchargez Python: https://www.python.org/downloads/")
        return False
    
    print(f"✅ Python {sys.version}")
    return True

def install_dependencies():
    """Installe les dépendances"""
    print("\n📦 Installation des dépendances...")
    
    # Liste des packages
    packages = [
        'psutil',
        'Pillow',
        'pyautogui',
        'pyperclip',
        'python-dateutil',
    ]
    
    # Packages optionnels
    optional = [
        'requests',
        'beautifulsoup4',
        'feedparser',
        'googletrans',
        'customtkinter',
    ]
    
    all_success = True
    
    # Installer les packages principaux
    for package in packages:
        print(f"  • {package}...", end=" ")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("✅")
        except:
            print("❌")
            all_success = False
    
    # Installer les optionnels
    print("\n📦 Packages optionnels:")
    for package in optional:
        print(f"  • {package}...", end=" ")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("✅")
        except:
            print("⚠️ (optionnel)")
    
    return all_success

def create_folders():
    """Crée la structure des dossiers"""
    print("\n📁 Création de la structure...")
    
    folders = [
        'ai',
        'core',
        'ui',
        'tools',
        'modules',
        'media',
        'data',
        'data/notes',
        'data/logs',
        'screenshots',
        'assets',
        'assets/icons',
        'assets/themes',
        'config'
    ]
    
    for folder in folders:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  📂 {folder}/")
    
    # Créer des fichiers __init__.py
    for init_folder in ['ai', 'core', 'ui', 'tools', 'media']:
        init_file = Path(init_folder) / "__init__.py"
        init_file.write_text('"""Package {} pour Zodiac v10.0"""\n'.format(init_folder))
        print(f"  📄 {init_folder}/__init__.py")

def create_config_files():
    """Crée les fichiers de configuration"""
    print("\n⚙️ Création des fichiers de configuration...")
    
    # zodiac_config.json
    config = {
        "version": "10.0",
        "theme": "dark",
        "language": "fr",
        "auto_start": False,
        "notifications": True,
        "ai_enabled": True,
        "vault_scanned": False,
        "first_run": True
    }
    
    import json
    with open('zodiac_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    print("  📄 zodiac_config.json")
    
    # requirements.txt si non existant
    if not Path('requirements.txt').exists():
        req_content = """# Zodiac v10.0 - Dépendances
psutil>=5.9.0
Pillow>=10.0.0
pyautogui>=0.9.54
pyperclip>=1.8.2
python-dateutil>=2.8.2

# Optionnel
requests>=2.31.0
beautifulsoup4>=4.12.2
customtkinter>=5.2.0"""
        
        Path('requirements.txt').write_text(req_content)
        print("  📄 requirements.txt")
    
    # README.md
    readme = """# 🚀 ZODIAC v10.0 - Assistant Personnel IA

Assistant intelligent avec interface moderne et fonctionnalités complètes.

## 🎯 Fonctionnalités

- **🤖 Assistant IA** - Chat intelligent
- **📁 Vault Scanner** - Gestionnaire d'applications
- **⚡ Surveillance système** - Monitoring temps réel
- **🛠️ Outils** - Utilitaires de productivité
- **🌐 Recherche web** - Intégration web
- **🎵 Multimédia** - Contrôle musique/volume
- **⚙️ Interface moderne** - Thème personnalisable

## 🚀 Démarrage rapide

```bash
# 1. Installez les dépendances
pip install -r requirements.txt

# 2. Lancez Zodiac
python main.py