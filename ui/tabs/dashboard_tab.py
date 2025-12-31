"""
Onglet Dashboard - Surveillance Système Complet
Auteur: tvcraft01
"""
import customtkinter as ctk
import threading
import time
import psutil
from datetime import datetime
import json
import os

class DashboardTab(ctk.CTkFrame):
    def __init__(self, parent):
        """Initialise l'onglet Dashboard complet"""
        super().__init__(parent, corner_radius=0, fg_color="#0A0A0F")
        
        # Configuration des couleurs
        self.bg_color = "#0A0A0F"
        self.card_bg = "#1A1A2E"
        self.primary_color = "#6C63FF"
        self.accent_color = "#00D4AA"
        self.text_color = "#FFFFFF"
        self.secondary_text = "#B0B0B0"
        
        # Données
        self.command_history = []
        self.system_logs = []
        self.privacy_logs = []
        
        # Fichiers
        self.history_file = "data/command_history.json"
        self.logs_file = "data/system_logs.json"
        
        # Charger les données
        self.load_data()
        
        # Configuration de la grille
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Créer l'interface
        self.setup_ui()
        
        # Démarrer la mise à jour en temps réel
        self.start_realtime_updates()
        
    def load_data(self):
        """Charge l'historique et les logs"""
        try:
            os.makedirs("data", exist_ok=True)
            
            # Historique des commandes
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.command_history = json.load(f)
            else:
                # Données de démonstration
                self.command_history = [
                    {"time": "14:30", "command": "Test du microphone", "type": "voice"},
                    {"time": "14:28", "command": "Quel temps fait-il ?", "type": "voice"},
                    {"time": "14:25", "command": "Ouvre Chrome", "type": "voice"},
                    {"time": "14:20", "command": "Musique suivante", "type": "voice"},
                    {"time": "14:15", "command": "Volume plus", "type": "voice"},
                    {"time": "14:10", "command": "État du système", "type": "text"},
                    {"time": "14:05", "command": "Recherche Python", "type": "text"},
                ]
                
            # Logs système
            if os.path.exists(self.logs_file):
                with open(self.logs_file, 'r') as f:
                    self.system_logs = json.load(f)
            else:
                self.system_logs = [
                    {"time": "14:35", "message": "Interface Zodiac OS chargée", "level": "info"},
                    {"time": "14:34", "message": "Module vocal initialisé", "level": "info"},
                    {"time": "14:33", "message": "Scan Vault terminé", "level": "info"},
                    {"time": "14:32", "message": "Connexion services IA", "level": "warning"},
                    {"time": "14:30", "message": "Démarrage de Zodiac OS", "level": "info"},
                ]
                
        except Exception as e:
            print(f"Erreur chargement données: {e}")
            
    def setup_ui(self):
        """Configure l'interface complète"""
        # Frame principal avec scroll
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.bg_color,
            corner_radius=0,
            scrollbar_button_color=self.primary_color
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # --- EN-TÊTE ---
        header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 DASHBOARD - Surveillance Système",
            font=("Segoe UI", 24, "bold"),
            text_color=self.text_color
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Surveillance en temps réel et historique d'activité",
            font=("Segoe UI", 14),
            text_color=self.secondary_text
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # --- WIDGETS SYSTÈME ---
        system_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        system_frame.grid(row=1, column=0, sticky="ew", pady=(0, 30))
        system_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="col")
        
        # Widget CPU
        self.cpu_card = self.create_system_widget("⚡ CPU", "cpu", system_frame, 0)
        
        # Widget Mémoire
        self.memory_card = self.create_system_widget("🧠 Mémoire", "memory", system_frame, 1)
        
        # Widget Disque
        self.disk_card = self.create_system_widget("💾 Disque", "disk", system_frame, 2)
        
        # Widget Réseau
        self.network_card = self.create_system_widget("🌐 Réseau", "network", system_frame, 3)
        
        # --- ROW 2: HISTORIQUE & LOGS ---
        row2_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        row2_frame.grid(row=2, column=0, sticky="ew", pady=(0, 30))
        row2_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")
        
        # Historique des commandes
        self.history_frame = self.create_log_widget(
            "📋 Historique des Commandes", 
            self.command_history,
            row2_frame, 
            0
        )
        
        # Logs système
        self.logs_frame = self.create_log_widget(
            "📝 Logs Système", 
            self.system_logs,
            row2_frame, 
            1
        )
        
        # --- ROW 3: PRIVACY & CONTROLES ---
        row3_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        row3_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        row3_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")
        
        # Privacy Dashboard
        privacy_frame = self.create_privacy_widget(row3_frame, 0)
        
        # Contrôles rapides
        controls_frame = self.create_controls_widget(row3_frame, 1)
        
    def create_system_widget(self, title, data_type, parent, column):
        """Crée un widget système"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.card_bg,
            corner_radius=15,
            height=180
        )
        card.grid(row=0, column=column, padx=8, pady=8, sticky="nsew")
        card.grid_propagate(False)
        
        # Titre
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 16, "bold"),
            text_color=self.text_color
        )
        title_label.pack(pady=(20, 10))
        
        # Valeur
        value_label = ctk.CTkLabel(
            card,
            text="0%",
            font=("Segoe UI", 32, "bold"),
            text_color=self.accent_color
        )
        value_label.pack(pady=(5, 10))
        
        # Barre de progression
        progress = ctk.CTkProgressBar(
            card,
            width=200,
            height=8,
            progress_color=self.primary_color,
            fg_color="#2A2A3E"
        )
        progress.pack(pady=(0, 15))
        progress.set(0)
        
        # Détails
        details_label = ctk.CTkLabel(
            card,
            text=self.get_system_details(data_type),
            font=("Segoe UI", 11),
            text_color=self.secondary_text
        )
        details_label.pack(pady=(0, 20))
        
        # Stocker les références
        widget_data = {
            "value_label": value_label,
            "progress": progress,
            "details_label": details_label,
            "type": data_type
        }
        
        # Stocker dans l'attribut approprié
        if not hasattr(self, 'system_widgets'):
            self.system_widgets = {}
        self.system_widgets[data_type] = widget_data
        
        return card
        
    def get_system_details(self, data_type):
        """Retourne les détails système"""
        try:
            if data_type == "cpu":
                cpu_freq = psutil.cpu_freq()
                return f"Cœurs: {psutil.cpu_count()}\nFréq: {cpu_freq.current:.0f} MHz"
                
            elif data_type == "memory":
                mem = psutil.virtual_memory()
                total_gb = mem.total / (1024**3)
                return f"Total: {total_gb:.1f} GB\nDisponible: {mem.available/(1024**3):.1f} GB"
                
            elif data_type == "disk":
                disk = psutil.disk_usage('/')
                total_gb = disk.total / (1024**3)
                free_gb = disk.free / (1024**3)
                return f"Total: {total_gb:.1f} GB\nLibre: {free_gb:.1f} GB"
                
            elif data_type == "network":
                net = psutil.net_io_counters()
                sent_mb = net.bytes_sent / (1024**2)
                recv_mb = net.bytes_recv / (1024**2)
                return f"Envoyé: {sent_mb:.1f} MB\nReçu: {recv_mb:.1f} MB"
                
        except Exception as e:
            print(f"Erreur détails système: {e}")
            
        return "Données non disponibles"
        
    def create_log_widget(self, title, data, parent, column):
        """Crée un widget d'historique/logs"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.card_bg,
            corner_radius=15
        )
        frame.grid(row=0, column=column, padx=8, pady=8, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Titre
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=("Segoe UI", 16, "bold"),
            text_color=self.text_color
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        # Zone de texte avec scroll
        text_widget = ctk.CTkTextbox(
            frame,
            fg_color="#2A2A3E",
            text_color=self.text_color,
            border_width=0,
            font=("Consolas", 11),
            height=180
        )
        text_widget.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 15))
        
        # Ajouter les données
        for item in data[-10:]:  # 10 derniers items
            if "time" in item and "command" in item:
                # Historique de commandes
                icon = "🎤" if item.get("type") == "voice" else "⌨️"
                text_widget.insert("end", f"[{item['time']}] {icon} {item['command']}\n")
            elif "time" in item and "message" in item:
                # Logs système
                level_icon = {
                    "info": "ℹ️",
                    "warning": "⚠️",
                    "error": "❌",
                    "success": "✅"
                }.get(item.get("level", "info"), "ℹ️")
                text_widget.insert("end", f"[{item['time']}] {level_icon} {item['message']}\n")
        
        text_widget.configure(state="disabled")
        
        return frame
        
    def create_privacy_widget(self, parent, column):
        """Crée le widget Privacy Dashboard"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.card_bg,
            corner_radius=15
        )
        frame.grid(row=0, column=column, padx=8, pady=8, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Titre avec icône
        title_frame = ctk.CTkFrame(frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="🔒 Privacy Dashboard",
            font=("Segoe UI", 16, "bold"),
            text_color=self.text_color
        ).pack(side="left")
        
        # Bouton clear
        ctk.CTkButton(
            title_frame,
            text="Effacer",
            font=("Segoe UI", 11),
            fg_color="transparent",
            hover_color="#2A2A3E",
            text_color=self.secondary_text,
            width=60,
            height=30,
            command=self.clear_privacy_logs
        ).pack(side="right")
        
        # Liste des accès
        self.privacy_list = ctk.CTkTextbox(
            frame,
            fg_color="#2A2A3E",
            text_color=self.text_color,
            border_width=0,
            font=("Segoe UI", 11),
            height=180
        )
        self.privacy_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 15))
        
        # Données de démonstration
        demo_logs = [
            {"time": "14:35", "access": "Microphone", "app": "Zodiac Assistant", "allowed": True},
            {"time": "14:34", "access": "Fichiers", "app": "Vault Scanner", "allowed": True},
            {"time": "14:30", "access": "Réseau", "app": "IA Services", "allowed": True},
            {"time": "14:25", "access": "Caméra", "app": "Test Module", "allowed": False},
            {"time": "14:20", "access": "Position", "app": "Weather Service", "allowed": False},
        ]
        
        for log in demo_logs:
            icon = "✅" if log["allowed"] else "❌"
            color = self.accent_color if log["allowed"] else "#FF6B6B"
            self.privacy_list.insert("end", 
                f"[{log['time']}] {icon} {log['access']}\n   par {log['app']}\n\n")
            
        self.privacy_list.configure(state="disabled")
        
        return frame
        
    def create_controls_widget(self, parent, column):
        """Crée le widget de contrôles rapides"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.card_bg,
            corner_radius=15
        )
        frame.grid(row=0, column=column, padx=8, pady=8, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Titre
        title_label = ctk.CTkLabel(
            frame,
            text="⚙️ Contrôles Rapides",
            font=("Segoe UI", 16, "bold"),
            text_color=self.text_color
        )
        title_label.pack(pady=(20, 15))
        
        # Frame pour les boutons
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        buttons_frame.grid_rowconfigure((0, 1, 2), weight=1)
        
        # Boutons de contrôle
        controls = [
            ("👨‍👩‍👧 Family Mode", 0, 0, False),
            ("🔄 Overlay Mode", 0, 1, False),
            ("🔇 Mode Silencieux", 1, 0, False),
            ("🌙 Dark Mode", 1, 1, True),
            ("📊 Logs Détaillés", 2, 0, False),
            ("🚀 Performance", 2, 1, True),
        ]
        
        self.control_switches = {}
        
        for text, row, col, state in controls:
            switch_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
            switch_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            ctk.CTkLabel(
                switch_frame,
                text=text,
                font=("Segoe UI", 12),
                text_color=self.text_color
            ).pack(side="left", padx=(0, 10))
            
            switch = ctk.CTkSwitch(
                switch_frame,
                text="",
                width=40,
                command=lambda t=text: self.toggle_control(t)
            )
            switch.pack(side="right")
            
            if state:
                switch.select()
                
            self.control_switches[text] = switch
        
        return frame
        
    def start_realtime_updates(self):
        """Démarre les mises à jour en temps réel"""
        self.update_system_stats()
        
    def update_system_stats(self):
        """Met à jour les statistiques système"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if hasattr(self, 'system_widgets') and 'cpu' in self.system_widgets:
                self.system_widgets['cpu']['value_label'].configure(text=f"{cpu_percent:.0f}%")
                self.system_widgets['cpu']['progress'].set(cpu_percent / 100)
                self.system_widgets['cpu']['details_label'].configure(
                    text=self.get_system_details('cpu')
                )
            
            # Mémoire
            mem = psutil.virtual_memory()
            if hasattr(self, 'system_widgets') and 'memory' in self.system_widgets:
                self.system_widgets['memory']['value_label'].configure(text=f"{mem.percent:.0f}%")
                self.system_widgets['memory']['progress'].set(mem.percent / 100)
                self.system_widgets['memory']['details_label'].configure(
                    text=self.get_system_details('memory')
                )
            
            # Disque
            disk = psutil.disk_usage('/')
            if hasattr(self, 'system_widgets') and 'disk' in self.system_widgets:
                self.system_widgets['disk']['value_label'].configure(text=f"{disk.percent:.0f}%")
                self.system_widgets['disk']['progress'].set(disk.percent / 100)
                self.system_widgets['disk']['details_label'].configure(
                    text=self.get_system_details('disk')
                )
            
            # Réseau (simplifié)
            if hasattr(self, 'system_widgets') and 'network' in self.system_widgets:
                net = psutil.net_io_counters()
                # Calcul du débit en MB par minute
                speed_mb = (net.bytes_sent + net.bytes_recv) / (1024**2) / 60  # MB par minute
                self.system_widgets['network']['value_label'].configure(text=f"{speed_mb:.1f} MB/m")
                self.system_widgets['network']['details_label'].configure(
                    text=self.get_system_details('network')
                )
                
        except Exception as e:
            print(f"Erreur mise à jour stats: {e}")
            
        # Planifier la prochaine mise à jour
        self.after(2000, self.update_system_stats)
        
    def toggle_control(self, control_name):
        """Bascule un contrôle"""
        switch = self.control_switches.get(control_name)
        if switch:
            state = "activé" if switch.get() else "désactivé"
            print(f"Contrôle '{control_name}' {state}")
            
            # Ajouter au log
            self.add_to_logs(f"Contrôle {control_name} {state}")
            
    def add_to_logs(self, message):
        """Ajoute un message aux logs"""
        log_entry = {
            "time": datetime.now().strftime("%H:%M"),
            "message": message,
            "level": "info"
        }
        self.system_logs.append(log_entry)
        
        # Sauvegarder
        try:
            with open(self.logs_file, 'w') as f:
                # Garder seulement les 50 derniers logs
                recent_logs = self.system_logs[-50:] if len(self.system_logs) > 50 else self.system_logs
                json.dump(recent_logs, f, indent=2)
        except Exception as e:
            print(f"Erreur sauvegarde logs: {e}")
            
    def clear_privacy_logs(self):
        """Efface les logs de privacy"""
        self.privacy_list.configure(state="normal")
        self.privacy_list.delete("1.0", "end")
        self.privacy_list.configure(state="disabled")
        
        self.add_to_logs("Logs de privacy effacés")