"""
Fenêtre principale de Zodiac OS avec navigation par onglets
Auteur: tvcraft01
"""
import customtkinter as ctk
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les onglets avec gestion des erreurs
try:
    from ui.tabs.assistant_tab import AssistantTab
    print("✅ AssistantTab importé")
except ImportError as e:
    print(f"⚠️ AssistantTab non importé: {e}")
    
    class AssistantTab(ctk.CTkFrame):
        def __init__(self, parent):
            super().__init__(parent, fg_color="#0A0A0F")
            label = ctk.CTkLabel(self, text="ASSISTANT - Erreur d'import", 
                                font=("Segoe UI", 24), text_color="#FF6B6B")
            label.pack(expand=True)

try:
    from ui.tabs.vault_tab import VaultTab
    print("✅ VaultTab importé")
except ImportError:
    print("⚠️ VaultTab non trouvé, création d'un placeholder...")
    
    class VaultTab(ctk.CTkFrame):
        def __init__(self, parent):
            super().__init__(parent, fg_color="#0A0A0F")
            label = ctk.CTkLabel(self, text="VAULT - En développement", 
                                font=("Segoe UI", 24), text_color="#6C63FF")
            label.pack(expand=True)

try:
    from ui.tabs.dashboard_tab import DashboardTab
    print("✅ DashboardTab importé")
except ImportError:
    print("⚠️ DashboardTab non trouvé, création d'un placeholder...")
    
    class DashboardTab(ctk.CTkFrame):
        def __init__(self, parent):
            super().__init__(parent, fg_color="#0A0A0F")
            label = ctk.CTkLabel(self, text="DASHBOARD - En développement", 
                                font=("Segoe UI", 24), text_color="#00D4AA")
            label.pack(expand=True)

class MainWindow:
    def __init__(self):
        """Initialise la fenêtre principale avec navigation"""
        print("🔧 Initialisation de MainWindow...")
        self.root = ctk.CTk()
        self.setup_window()
        self.setup_theme()
        self.create_widgets()
        self.setup_navigation()
        print("✅ MainWindow initialisé")
        
    def setup_window(self):
        """Configure la fenêtre principale"""
        self.root.title("Zodiac OS - Assistant Vocal Intelligent")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Centrer la fenêtre
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Icône de la fenêtre
        try:
            icon_path = os.path.join("assets", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
    def setup_theme(self):
        """Définit le thème cyberpunk"""
        # Palette de couleurs
        self.bg_color = "#0A0A0F"
        self.sidebar_color = "#1A1A2E"
        self.primary_color = "#6C63FF"
        self.accent_color = "#00D4AA"
        self.text_color = "#FFFFFF"
        self.secondary_text = "#B0B0B0"
        self.hover_color = "#2A2A3E"
        
        # Configurer CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
    def create_widgets(self):
        """Crée les widgets principaux"""
        # Configuration de la grille
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # --- SIDEBAR (Navigation) ---
        self.sidebar = ctk.CTkFrame(
            self.root,
            width=80,
            corner_radius=0,
            fg_color=self.sidebar_color
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo en haut
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="Z",
            font=("Segoe UI", 32, "bold"),
            text_color=self.primary_color
        )
        self.logo_label.pack(pady=(30, 40))
        
        # Frame pour les boutons de navigation
        self.nav_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            corner_radius=0
        )
        self.nav_frame.pack(fill="x", expand=False, padx=10)
        
        # --- ZONE PRINCIPALE (Contenu des onglets) ---
        self.main_container = ctk.CTkFrame(
            self.root,
            corner_radius=0,
            fg_color=self.bg_color
        )
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Frame pour le contenu (les onglets seront affichés ici)
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=self.bg_color,
            corner_radius=0
        )
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
    def setup_navigation(self):
        """Configure la navigation entre les onglets"""
        # Dictionnaire pour stocker les onglets
        self.tabs = {}
        self.current_tab = None
        
        # Créer les boutons de navigation
        self.create_nav_buttons()
        
        # Initialiser les onglets
        self.init_tabs()
        
        # Afficher l'onglet Assistant par défaut
        self.switch_tab("assistant")
        
    def create_nav_buttons(self):
        """Crée les boutons de navigation dans la sidebar"""
        self.nav_buttons = {}
        
        # Définir les onglets
        nav_items = [
            ("assistant", "Assistant", "🎙️"),
            ("vault", "Vault", "📁"),
            ("dashboard", "Dashboard", "📊")
        ]
        
        for tab_id, label, icon in nav_items:
            # Créer un bouton de navigation
            btn = ctk.CTkButton(
                self.nav_frame,
                text=f"{icon}\n{label}",
                font=("Segoe UI", 12),
                fg_color="transparent",
                hover_color=self.hover_color,
                text_color=self.secondary_text,
                height=80,
                width=70,
                corner_radius=10,
                compound="top",
                anchor="center",
                command=lambda tid=tab_id: self.switch_tab(tid)
            )
            btn.pack(pady=5, fill="x")
            
            # Stocker le bouton pour mise à jour ultérieure
            self.nav_buttons[tab_id] = btn
            
    def init_tabs(self):
        """Initialise tous les onglets (mais ne les affiche pas encore)"""
        print("🔧 Initialisation des onglets...")
        
        # Onglet Assistant
        try:
            self.tabs["assistant"] = AssistantTab(self.content_frame)
            print("✅ AssistantTab créé")
        except Exception as e:
            print(f"❌ Erreur création AssistantTab: {e}")
            self.tabs["assistant"] = ctk.CTkFrame(self.content_frame, fg_color="#0A0A0F")
            label = ctk.CTkLabel(self.tabs["assistant"], text="Erreur Assistant", 
                                font=("Segoe UI", 20), text_color="#FF6B6B")
            label.pack(expand=True)
        
        # Onglet Vault
        try:
            self.tabs["vault"] = VaultTab(self.content_frame)
            print("✅ VaultTab créé")
        except Exception as e:
            print(f"❌ Erreur création VaultTab: {e}")
            self.tabs["vault"] = ctk.CTkFrame(self.content_frame, fg_color="#0A0A0F")
            label = ctk.CTkLabel(self.tabs["vault"], text="Erreur Vault", 
                                font=("Segoe UI", 20), text_color="#FF6B6B")
            label.pack(expand=True)
        
        # Onglet Dashboard
        try:
            self.tabs["dashboard"] = DashboardTab(self.content_frame)
            print("✅ DashboardTab créé")
        except Exception as e:
            print(f"❌ Erreur création DashboardTab: {e}")
            self.tabs["dashboard"] = ctk.CTkFrame(self.content_frame, fg_color="#0A0A0F")
            label = ctk.CTkLabel(self.tabs["dashboard"], text="Erreur Dashboard", 
                                font=("Segoe UI", 20), text_color="#FF6B6B")
            label.pack(expand=True)
        
        # Tous les onglets sont créés mais pas affichés
        for tab in self.tabs.values():
            tab.grid_forget()
            
    def switch_tab(self, tab_id):
        """Bascule vers l'onglet spécifié"""
        print(f"🔄 Changement vers l'onglet: {tab_id}")
        
        # Cacher l'onglet actuel
        if self.current_tab:
            self.tabs[self.current_tab].grid_forget()
            # Réinitialiser le style du bouton précédent
            prev_btn = self.nav_buttons[self.current_tab]
            prev_btn.configure(
                fg_color="transparent",
                text_color=self.secondary_text
            )
        
        # Afficher le nouvel onglet
        if tab_id in self.tabs:
            self.tabs[tab_id].grid(row=0, column=0, sticky="nsew")
        else:
            print(f"❌ Onglet {tab_id} non trouvé")
            return
            
        # Mettre à jour le style du bouton actif
        active_btn = self.nav_buttons[tab_id]
        active_btn.configure(
            fg_color=self.primary_color,
            text_color=self.text_color
        )
        
        # Mettre à jour l'onglet courant
        self.current_tab = tab_id
        
        # Mettre à jour le titre de la fenêtre
        tab_names = {
            "assistant": "Assistant",
            "vault": "Vault",
            "dashboard": "Dashboard"
        }
        self.root.title(f"Zodiac OS - {tab_names.get(tab_id, tab_id)}")
        
    def run(self):
        """Lance la fenêtre principale"""
        print("🚀 Lancement de la boucle principale...")
        self.root.mainloop()
        
    def shutdown(self):
        """Ferme proprement la fenêtre"""
        print("🛑 Arrêt de l'application...")
        self.root.quit()
        self.root.destroy()

# Point d'entrée pour tester directement ce fichier
if __name__ == "__main__":
    print("🧪 Test direct de main_window.py")
    app = MainWindow()
    app.run()