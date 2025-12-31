"""
Onglet Vault - Explorateur d'Applications Complet
Auteur: tvcraft01
"""
import customtkinter as ctk
import os
import sys
import subprocess
import threading
import time
from PIL import Image, ImageTk
import json
from datetime import datetime

class VaultTab(ctk.CTkFrame):
    def __init__(self, parent):
        """Initialise l'onglet Vault complet"""
        super().__init__(parent, corner_radius=0, fg_color="#0A0A0F")
        
        # Configuration des couleurs
        self.bg_color = "#0A0A0F"
        self.card_bg = "#1A1A2E"
        self.primary_color = "#6C63FF"
        self.accent_color = "#00D4AA"
        self.text_color = "#FFFFFF"
        self.secondary_text = "#B0B0B0"
        
        # Données des applications
        self.applications = []
        self.favorites = []
        self.filtered_apps = []
        
        # État du scanner
        self.is_scanning = False
        
        # Fichier de configuration
        self.config_file = "data/vault_config.json"
        
        # Configuration de la grille
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Charger les favoris
        self.load_favorites()
        
        # Créer l'interface
        self.setup_ui()
        
        # Scanner automatiquement au démarrage
        self.after(500, self.scan_applications)
        
    def setup_ui(self):
        """Configure l'interface complète du Vault"""
        # Frame principal
        main_frame = ctk.CTkFrame(
            self,
            fg_color=self.bg_color,
            corner_radius=0
        )
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_rowconfigure(1, weight=1)  # Zone de contenu
        main_frame.grid_columnconfigure(0, weight=1)
        
        # --- EN-TÊTE ---
        header_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent",
            height=80
        )
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Titre
        title_label = ctk.CTkLabel(
            header_frame,
            text="📁 VAULT - Explorateur d'Applications",
            font=("Segoe UI", 24, "bold"),
            text_color=self.text_color
        )
        title_label.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        # Barre de recherche
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_applications)
        
        self.search_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="Rechercher une application...",
            font=("Segoe UI", 14),
            height=40,
            width=300,
            corner_radius=20,
            fg_color="#2A2A3E",
            border_color=self.primary_color,
            text_color=self.text_color,
            textvariable=self.search_var
        )
        self.search_entry.grid(row=0, column=1, padx=10, sticky="ew")
        
        # Bouton scanner
        self.scan_button = ctk.CTkButton(
            header_frame,
            text="🔍 Scanner à nouveau",
            font=("Segoe UI", 13, "bold"),
            fg_color=self.primary_color,
            hover_color="#7C73FF",
            text_color=self.text_color,
            height=40,
            width=180,
            corner_radius=20,
            command=self.scan_applications
        )
        self.scan_button.grid(row=0, column=2, sticky="e")
        
        # --- SECTION FAVORIS ---
        self.favorites_frame = ctk.CTkFrame(
            main_frame,
            fg_color=self.card_bg,
            corner_radius=15,
            height=120
        )
        self.favorites_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        self.favorites_frame.grid_propagate(False)
        self.favorites_frame.grid_columnconfigure(0, weight=1)
        
        # Titre favoris
        fav_title = ctk.CTkLabel(
            self.favorites_frame,
            text="⭐ Applications Favorites",
            font=("Segoe UI", 16, "bold"),
            text_color=self.accent_color
        )
        fav_title.pack(pady=(15, 10))
        
        # Frame pour les icônes de favoris
        self.fav_icons_frame = ctk.CTkFrame(
            self.favorites_frame,
            fg_color="transparent"
        )
        self.fav_icons_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Message par défaut
        self.fav_message = ctk.CTkLabel(
            self.fav_icons_frame,
            text="Aucun favori. Cliquez sur ☆ dans une app pour l'ajouter.",
            font=("Segoe UI", 12),
            text_color=self.secondary_text
        )
        self.fav_message.pack()
        
        # --- SECTION APPLICATIONS ---
        apps_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        apps_frame.grid(row=2, column=0, sticky="nsew")
        apps_frame.grid_rowconfigure(0, weight=1)
        apps_frame.grid_columnconfigure(0, weight=1)
        
        # Titre avec compteur
        self.apps_title_frame = ctk.CTkFrame(
            apps_frame,
            fg_color="transparent"
        )
        self.apps_title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.apps_title_frame.grid_columnconfigure(0, weight=1)
        
        self.apps_title = ctk.CTkLabel(
            self.apps_title_frame,
            text="Toutes les Applications (0)",
            font=("Segoe UI", 18, "bold"),
            text_color=self.text_color
        )
        self.apps_title.grid(row=0, column=0, sticky="w")
        
        # Canvas avec scrollbar pour les applications
        self.apps_canvas = ctk.CTkCanvas(
            apps_frame,
            bg=self.bg_color,
            highlightthickness=0
        )
        
        self.scrollbar = ctk.CTkScrollbar(
            apps_frame,
            orientation="vertical",
            command=self.apps_canvas.yview
        )
        
        self.apps_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Frame pour la grille d'applications
        self.apps_grid_frame = ctk.CTkFrame(
            self.apps_canvas,
            fg_color=self.bg_color,
            corner_radius=0
        )
        
        self.canvas_window = self.apps_canvas.create_window(
            (0, 0),
            window=self.apps_grid_frame,
            anchor="nw",
            width=self.apps_canvas.winfo_reqwidth()
        )
        
        # Placement
        self.apps_canvas.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Configurer la grille pour les apps
        self.apps_grid_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="col")
        
        # Gestion du redimensionnement
        self.bind("<Configure>", self.on_resize)
        self.apps_grid_frame.bind("<Configure>", self.update_scrollregion)
        
        # --- STATUT EN BAS ---
        self.status_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent",
            height=40
        )
        self.status_frame.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Prêt",
            font=("Segoe UI", 12),
            text_color=self.secondary_text
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.app_count_label = ctk.CTkLabel(
            self.status_frame,
            text="0 applications",
            font=("Segoe UI", 12),
            text_color=self.accent_color
        )
        self.app_count_label.grid(row=0, column=1, sticky="e")
        
    def load_favorites(self):
        """Charge les applications favorites depuis le fichier"""
        try:
            os.makedirs("data", exist_ok=True)
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.favorites = config.get("favorites", [])
        except Exception as e:
            print(f"Erreur chargement favoris: {e}")
            self.favorites = []
            
    def save_favorites(self):
        """Sauvegarde les favoris dans le fichier"""
        try:
            config = {"favorites": self.favorites}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Erreur sauvegarde favoris: {e}")
            
    def scan_applications(self):
        """Scanne les applications sur le système"""
        if self.is_scanning:
            return
            
        self.is_scanning = True
        self.scan_button.configure(state="disabled", text="⏳ Scanning...")
        self.status_label.configure(text="Scan en cours...")
        
        # Démarrer le scan dans un thread séparé
        thread = threading.Thread(target=self._scan_applications_thread, daemon=True)
        thread.start()
        
    def _scan_applications_thread(self):
        """Thread de scan des applications"""
        # Simuler un scan (à remplacer par le vrai scanner)
        time.sleep(2)  # Simulation du temps de scan
        
        # Applications système Windows courantes
        windows_apps = [
            {"name": "Chrome", "path": "chrome.exe", "category": "Navigateur"},
            {"name": "Firefox", "path": "firefox.exe", "category": "Navigateur"},
            {"name": "Edge", "path": "msedge.exe", "category": "Navigateur"},
            {"name": "VSCode", "path": "code.exe", "category": "Développement"},
            {"name": "Discord", "path": "Discord.exe", "category": "Communication"},
            {"name": "Spotify", "path": "Spotify.exe", "category": "Musique"},
            {"name": "Deezer", "path": "Deezer.exe", "category": "Musique"},
            {"name": "Notepad", "path": "notepad.exe", "category": "Utilitaires"},
            {"name": "Calculator", "path": "calc.exe", "category": "Utilitaires"},
            {"name": "Word", "path": "winword.exe", "category": "Bureau"},
            {"name": "Excel", "path": "excel.exe", "category": "Bureau"},
            {"name": "PowerPoint", "path": "powerpnt.exe", "category": "Bureau"},
            {"name": "Paint", "path": "mspaint.exe", "category": "Graphisme"},
            {"name": "Photos", "path": "ms-photos.exe", "category": "Graphisme"},
            {"name": "Command Prompt", "path": "cmd.exe", "category": "Système"},
            {"name": "PowerShell", "path": "powershell.exe", "category": "Système"},
            {"name": "Task Manager", "path": "taskmgr.exe", "category": "Système"},
            {"name": "File Explorer", "path": "explorer.exe", "category": "Système"},
            {"name": "Settings", "path": "SystemSettings.exe", "category": "Système"},
            {"name": "Calendar", "path": "outlookcalendar.exe", "category": "Bureau"},
        ]
        
        # Ajouter des apps génériques pour démonstration
        demo_apps = [
            {"name": "Adobe Reader", "path": "AcroRd32.exe", "category": "Documents"},
            {"name": "WinRAR", "path": "WinRAR.exe", "category": "Utilitaires"},
            {"name": "VLC", "path": "vlc.exe", "category": "Multimédia"},
            {"name": "Zoom", "path": "Zoom.exe", "category": "Communication"},
            {"name": "Teams", "path": "ms-teams.exe", "category": "Communication"},
            {"name": "Steam", "path": "steam.exe", "category": "Jeux"},
            {"name": "Epic Games", "path": "EpicGamesLauncher.exe", "category": "Jeux"},
            {"name": "Photoshop", "path": "photoshop.exe", "category": "Graphisme"},
            {"name": "Illustrator", "path": "illustrator.exe", "category": "Graphisme"},
            {"name": "Blender", "path": "blender.exe", "category": "3D"},
        ]
        
        # Combiner les apps
        self.applications = windows_apps + demo_apps
        
        # Mettre à jour dans le thread principal
        self.after(0, self._update_applications_ui)
        
    def _update_applications_ui(self):
        """Met à jour l'interface après le scan"""
        # Filtrer les applications (par défaut, toutes)
        self.filtered_apps = self.applications.copy()
        
        # Mettre à jour le titre
        self.apps_title.configure(text=f"Toutes les Applications ({len(self.filtered_apps)})")
        self.app_count_label.configure(text=f"{len(self.filtered_apps)} applications")
        
        # Effacer la grille actuelle
        for widget in self.apps_grid_frame.winfo_children():
            widget.destroy()
        
        # Afficher les applications
        self.display_applications()
        
        # Mettre à jour les favoris
        self.update_favorites_display()
        
        # Réactiver le bouton
        self.is_scanning = False
        self.scan_button.configure(state="normal", text="🔍 Scanner à nouveau")
        self.status_label.configure(text=f"Scan terminé - {len(self.applications)} apps trouvées")
        
    def display_applications(self):
        """Affiche les applications dans la grille"""
        if not self.filtered_apps:
            # Message si aucune application
            empty_label = ctk.CTkLabel(
                self.apps_grid_frame,
                text="Aucune application trouvée\nCliquez sur 'Scanner à nouveau'",
                font=("Segoe UI", 14),
                text_color=self.secondary_text,
                justify="center"
            )
            empty_label.grid(row=0, column=0, columnspan=5, pady=50)
            return
        
        # Afficher les apps dans une grille 5 colonnes
        for i, app in enumerate(self.filtered_apps):
            row = i // 5
            col = i % 5
            
            self.create_app_card(app, row, col)
            
    def create_app_card(self, app, row, col):
        """Crée une carte d'application"""
        card = ctk.CTkFrame(
            self.apps_grid_frame,
            fg_color=self.card_bg,
            corner_radius=12,
            width=180,
            height=180
        )
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        card.grid_propagate(False)
        
        # Icône de l'app (simulée)
        icon_label = ctk.CTkLabel(
            card,
            text=self.get_app_icon(app["name"]),
            font=("Segoe UI", 32),
            text_color=self.primary_color
        )
        icon_label.pack(pady=(20, 10))
        
        # Nom de l'app (tronqué si trop long)
        app_name = app["name"]
        if len(app_name) > 15:
            app_name = app_name[:12] + "..."
        
        name_label = ctk.CTkLabel(
            card,
            text=app_name,
            font=("Segoe UI", 13, "bold"),
            text_color=self.text_color
        )
        name_label.pack(pady=(0, 5))
        
        # Catégorie
        cat_label = ctk.CTkLabel(
            card,
            text=app["category"],
            font=("Segoe UI", 10),
            text_color=self.secondary_text
        )
        cat_label.pack(pady=(0, 10))
        
        # Bouton étoile (favori)
        is_favorite = app["name"] in self.favorites
        star_text = "★" if is_favorite else "☆"
        star_color = self.accent_color if is_favorite else self.secondary_text
        
        star_btn = ctk.CTkButton(
            card,
            text=star_text,
            font=("Segoe UI", 16),
            fg_color="transparent",
            hover_color="#2A2A3E",
            text_color=star_color,
            width=30,
            height=30,
            corner_radius=15,
            command=lambda a=app: self.toggle_favorite(a)
        )
        star_btn.place(x=10, y=10)
        
        # Bouton lancer (au survol)
        launch_btn = ctk.CTkButton(
            card,
            text="▶ Lancer",
            font=("Segoe UI", 11),
            fg_color=self.primary_color,
            hover_color="#7C73FF",
            text_color=self.text_color,
            height=30,
            corner_radius=8,
            command=lambda a=app: self.launch_application(a)
        )
        launch_btn.pack(side="bottom", pady=(0, 15))
        
        # Effet de survol
        def on_enter(e):
            card.configure(fg_color="#2A2A3E")
            
        def on_leave(e):
            card.configure(fg_color=self.card_bg)
            
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
    def get_app_icon(self, app_name):
        """Retourne une icône basée sur le nom de l'app"""
        icons = {
            "Chrome": "🌐", "Firefox": "🦊", "Edge": "🔷",
            "VSCode": "📝", "Discord": "🎮", "Spotify": "🎵",
            "Deezer": "🎶", "Notepad": "📄", "Calculator": "🧮",
            "Word": "📘", "Excel": "📗", "PowerPoint": "📙",
            "Paint": "🎨", "Photos": "🖼️", "Command Prompt": "💻",
            "PowerShell": "⚡", "Task Manager": "📊", "File Explorer": "📁",
            "Settings": "⚙️", "Calendar": "📅", "Adobe Reader": "📚",
            "WinRAR": "📦", "VLC": "🎬", "Zoom": "📹",
            "Teams": "👥", "Steam": "🎮", "Epic Games": "🕹️",
            "Photoshop": "🎨", "Illustrator": "✏️", "Blender": "🎨"
        }
        
        return icons.get(app_name, "📱")
        
    def toggle_favorite(self, app):
        """Ajoute/retire une app des favoris"""
        app_name = app["name"]
        
        if app_name in self.favorites:
            self.favorites.remove(app_name)
        else:
            self.favorites.append(app_name)
            
        # Sauvegarder
        self.save_favorites()
        
        # Mettre à jour l'affichage
        self.update_favorites_display()
        
        # Re-créer les cartes pour mettre à jour les étoiles
        self.display_applications()
        
    def update_favorites_display(self):
        """Met à jour l'affichage des favoris"""
        # Effacer les anciens favoris
        for widget in self.fav_icons_frame.winfo_children():
            widget.destroy()
        
        if not self.favorites:
            # Message par défaut
            self.fav_message = ctk.CTkLabel(
                self.fav_icons_frame,
                text="Aucun favori. Cliquez sur ☆ dans une app pour l'ajouter.",
                font=("Segoe UI", 12),
                text_color=self.secondary_text
            )
            self.fav_message.pack()
            return
        
        # Afficher les favoris
        fav_row = ctk.CTkFrame(self.fav_icons_frame, fg_color="transparent")
        fav_row.pack(fill="x")
        
        for i, fav_name in enumerate(self.favorites[:10]):  # Max 10 favoris
            # Trouver l'app correspondante
            app = next((a for a in self.applications if a["name"] == fav_name), None)
            if not app:
                continue
                
            # Créer un bouton favori
            fav_btn = ctk.CTkButton(
                fav_row,
                text=f"{self.get_app_icon(app['name'])} {app['name']}",
                font=("Segoe UI", 11),
                fg_color="transparent",
                hover_color="#2A2A3E",
                text_color=self.accent_color,
                height=40,
                corner_radius=20,
                anchor="w",
                command=lambda a=app: self.launch_application(a)
            )
            fav_btn.pack(side="left", padx=5)
            
    def filter_applications(self, *args):
        """Filtre les applications selon la recherche"""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            self.filtered_apps = self.applications.copy()
        else:
            self.filtered_apps = [
                app for app in self.applications 
                if search_text in app["name"].lower() 
                or search_text in app["category"].lower()
            ]
        
        # Mettre à jour le titre
        self.apps_title.configure(text=f"Applications ({len(self.filtered_apps)})")
        
        # Effacer et réafficher
        for widget in self.apps_grid_frame.winfo_children():
            widget.destroy()
            
        self.display_applications()
        
    def launch_application(self, app):
        """Lance une application"""
        self.status_label.configure(text=f"Lancement de {app['name']}...")
        
        try:
            # Essayer de lancer l'app (simulation pour le moment)
            # Dans la version finale, utiliser subprocess ou os.startfile
            print(f"🚀 Tentative de lancement: {app['name']} ({app['path']})")
            
            # Simuler un délai de lancement
            self.after(1000, lambda: self.status_label.configure(
                text=f"{app['name']} lancé avec succès"
            ))
            
        except Exception as e:
            self.status_label.configure(text=f"Erreur: {str(e)[:50]}...")
            print(f"❌ Erreur lancement: {e}")
            
    def on_resize(self, event=None):
        """Gère le redimensionnement"""
        if event and event.widget == self:
            new_width = event.width - 60  # Marges
            self.apps_canvas.itemconfig(self.canvas_window, width=new_width)
            
    def update_scrollregion(self, event=None):
        """Met à jour la région de scroll"""
        self.apps_canvas.configure(scrollregion=self.apps_canvas.bbox("all"))