# setup.py
import subprocess
import sys
import os

def install_dependencies():
    """Installe les dépendances nécessaires"""
    
    print("🔧 Installation des dépendances Zodiac v10.0\n")
    
    # Dépendances essentielles
    essential = [
        'psutil>=5.9.0',
        'Pillow>=10.0.0',
        'pyperclip>=1.8.0',
    ]
    
    # Dépendances recommandées
    recommended = [
        'requests>=2.31.0',
        'pyautogui>=0.9.0',
        'python-dateutil>=2.8.0',
    ]
    
    # Dépendances optionnelles (AI)
    optional = [
        'beautifulsoup4>=4.12.0',
        'feedparser>=6.0.0',
        'googletrans>=4.0.0',
        'duckduckgo-search>=3.9.0',
    ]
    
    print("📦 Installation des dépendances ESSENTIELLES:")
    for package in essential:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"  ✅ {package}")
        except:
            print(f"  ❌ {package}")
    
    print("\n📦 Installation des dépendances RECOMMANDÉES:")
    for package in recommended:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"  ✅ {package}")
        except:
            print(f"  ⚠️  {package} (optionnel)")
    
    print("\n📦 Installation des dépendances OPTIONNELLES (AI):")
    for package in optional:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"  ✅ {package}")
        except:
            print(f"  ⚠️  {package} (facultatif)")
    
    # Créer la structure de dossiers
    print("\n📁 Création de la structure de dossiers...")
    folders = [
        'ai',
        'core', 
        'tools',
        'media',
        'data',
        'data/notes',
        'data/logs',
        'screenshots',
        'modules'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"  📂 {folder}/")
    
    print("\n" + "="*50)
    print("✅ Installation terminée avec succès!")
    print("\n🎯 Pour démarrer Zodiac:")
    print("   python main.py")
    print("\n🔧 Pour tester l'installation:")
    print("   python test_installation.py")

def test_installation():
    """Teste l'installation"""
    print("🧪 Test de l'installation...")
    
    tests = [
        ('tkinter', 'Interface graphique'),
        ('psutil', 'Surveillance système'),
        ('PIL', 'Manipulation images'),
        ('pyperclip', 'Presse-papiers'),
    ]
    
    all_ok = True
    for module, description in tests:
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'PIL':
                from PIL import Image
            else:
                __import__(module)
            print(f"  ✅ {description} ({module})")
        except ImportError:
            print(f"  ❌ {description} ({module})")
            all_ok = False
    
    if all_ok:
        print("\n✅ Tous les tests passés avec succès!")
    else:
        print("\n⚠️  Certains tests ont échoué")
        print("   Ré-exécutez setup.py ou installez manuellement les modules manquants")

if __name__ == "__main__":
    print("ZODIAC v10.0 - Assistant Personnel AI")
    print("="*50)
    
    action = input("\nChoisissez une action:\n1. Installer les dépendances\n2. Tester l'installation\n3. Quitter\n\nVotre choix: ")
    
    if action == '1':
        install_dependencies()
    elif action == '2':
        test_installation()
    else:
        print("Au revoir!")