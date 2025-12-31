#!/usr/bin/env python3
"""
Point d'entrée principal de Zodiac OS - Version 2.0.0
Interface Zodiac OS avec 3 onglets modernes
"""

import sys
import os

# Ajoute le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Vérifie les dépendances nécessaires"""
    print("🔧 Vérification des modules...")
    
    required_modules = [
        ('customtkinter', 'customtkinter'),
        ('PIL', 'pillow'),
        ('psutil', 'psutil'),
    ]
    
    missing = []
    for module, install_name in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing.append(install_name)
    
    if missing:
        print(f"\n⚠️ Modules manquants: {', '.join(missing)}")
        print(f"📦 Installez-les: pip install {' '.join(missing)}")
        
        # Demander l'installation
        response = input("\nVoulez-vous installer les modules manquants ? (o/n): ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
                print("✅ Modules installés avec succès !")
            except Exception as e:
                print(f"❌ Erreur lors de l'installation: {e}")
                return False
        else:
            print("❌ Impossible de démarrer sans les modules nécessaires.")
            return False
    
    print("✅ Toutes les dépendances sont satisfaites !")
    return True

def launch_interface():
    """
    Lance l'interface principale
    """
    try:
        # Importer après vérification des dépendances
        from ui.main_window import MainWindow
        
        print("\n" + "="*60)
        print("🚀 LANCEMENT DE ZODIAC OS v2.0.0")
        print("="*60)
        print("📱 Interface: 3 onglets modernes")
        print("🎨 Style: Thème cyberpunk/neutre")
        print("🎯 Fonctionnalités: Assistant, Vault, Dashboard")
        print("="*60)
        
        # Créer et lancer la fenêtre principale
        print("\n🔧 Initialisation de la fenêtre principale...")
        app = MainWindow()
        
        print("✅ Interface principale chargée !")
        print("👉 Navigation disponible: Assistant | Vault | Dashboard")
        print("💡 Astuce: Utilisez la sidebar à gauche pour changer d'onglet")
        print("🎤 Testez le bouton microphone dans l'onglet Assistant\n")
        
        # Lancer l'application
        app.run()
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        print("\n🔍 Détails de l'erreur:")
        import traceback
        traceback.print_exc()
        
        # Essayer de lancer l'ancienne interface en backup
        print("\n🔄 Tentative de lancement de l'interface de secours...")
        try:
            from backup_interface import launch_backup
            launch_backup()
        except:
            print("❌ Impossible de lancer aucune interface.")
            input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)

def main():
    """Fonction principale"""
    # En-tête ASCII
    print(r"""
    ╔═══════════════════════════════════════════════════════╗
    ║        ███████╗ ██████╗ ██████╗ ██╗ █████╗  ██████╗  ║
    ║        ╚══███╔╝██╔═══██╗██╔══██╗██║██╔══██╗██╔════╝  ║
    ║          ███╔╝ ██║   ██║██║  ██║██║███████║██║  ███╗ ║
    ║         ███╔╝  ██║   ██║██║  ██║██║██╔══██║██║   ██║ ║
    ║        ███████╗╚██████╔╝██████╔╝██║██║  ██║╚██████╔╝ ║
    ║        ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═╝ ╚═════╝  ║
    ║                   VERSION 2.0.0                        ║
    ║             Assistant Vocal Intelligent                ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("\n❌ Arrêt du programme.")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    print("\n✅ Prêt à démarrer !")
    print("📊 Système: Python", sys.version.split()[0])
    print("📁 Répertoire:", os.getcwd())
    print("\n" + "="*60)
    
    # Demander à l'utilisateur s'il veut le splash screen
    print("\n🎨 OPTIONS DE DÉMARRAGE:")
    print("1. Interface complète avec splash screen (Recommandé)")
    print("2. Interface principale directement")
    print("3. Mode texte (dépannage)")
    
    try:
        choice = input("\nVotre choix (1-3, défaut=1): ").strip()
        
        if choice == "2":
            # Lancer directement l'interface principale
            print("\n🚀 Lancement direct de l'interface...")
            launch_interface()
            
        elif choice == "3":
            # Mode texte
            print("\n📟 Mode texte activé")
            print("Cette fonctionnalité est en développement...")
            input("\nAppuyez sur Entrée pour quitter...")
            
        else:
            # Option 1 par défaut: avec splash screen
            print("\n✨ Démarrage avec interface animée...")
            
            # Importer le splash screen
            from ui.splash_screen import SplashScreen
            
            # Créer et lancer le splash screen
            splash = SplashScreen(launch_interface)
            splash.run()
            
    except KeyboardInterrupt:
        print("\n\n❌ Arrêt demandé par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    # Créer les dossiers nécessaires
    os.makedirs("ui/tabs", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Lancer l'application
    main()