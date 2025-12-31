"""
Splash screen animé style E-dex UI pour Zodiac OS
Auteur: tvcraft01
"""
import customtkinter as ctk
import threading
import time
import sys
import os
from PIL import Image, ImageTk

class SplashScreen:
    def __init__(self, on_complete_callback):
        """
        Initialise le splash screen
        
        Args:
            on_complete_callback: Fonction à appeler quand le chargement est terminé
        """
        self.on_complete = on_complete_callback
        self.root = ctk.CTk()
        
        # Configuration de la fenêtre
        self.root.title("Zodiac OS")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Centrer la fenêtre
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Supprimer la bordure de la fenêtre
        self.root.overrideredirect(True)
        
        # Palette de couleurs cyberpunk
        self.bg_color = "#0A0A0F"
        self.primary_color = "#6C63FF"
        self.accent_color = "#00D4AA"
        self.text_color = "#FFFFFF"
        self.secondary_text = "#B0B0B0"
        
        # Configurer le thème
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Créer le contenu
        self.setup_ui()
        
        # Démarrer l'animation de chargement
        self.loading_complete = False
        self.start_loading_animation()
        
    def setup_ui(self):
        """Configure l'interface du splash screen"""
        # Frame principal avec fond dégradé
        self.main_frame = ctk.CTkFrame(
            self.root, 
            fg_color=self.bg_color,
            corner_radius=0
        )
        self.main_frame.pack(fill="both", expand=True)
        
        # Logo Zodiac
        self.logo_label = ctk.CTkLabel(
            self.main_frame,
            text="ZODIAC OS",
            font=("Segoe UI", 42, "bold"),
            text_color=self.primary_color
        )
        self.logo_label.pack(pady=(60, 10))
        
        # Sous-titre
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="Assistant Vocal Intelligent",
            font=("Segoe UI", 16),
            text_color=self.secondary_text
        )
        self.subtitle_label.pack(pady=(0, 40))
        
        # Barre de progression
        self.progressbar = ctk.CTkProgressBar(
            self.main_frame,
            width=400,
            height=6,
            progress_color=self.accent_color,
            fg_color="#2A2A3E",
            corner_radius=3
        )
        self.progressbar.pack(pady=(0, 20))
        self.progressbar.set(0)
        
        # Label d'étape de chargement
        self.loading_label = ctk.CTkLabel(
            self.main_frame,
            text="Initialisation du noyau...",
            font=("Segoe UI", 14),
            text_color=self.text_color
        )
        self.loading_label.pack(pady=(0, 10))
        
        # Pourcentage de chargement
        self.percentage_label = ctk.CTkLabel(
            self.main_frame,
            text="0%",
            font=("Segoe UI", 12, "bold"),
            text_color=self.accent_color
        )
        self.percentage_label.pack(pady=(0, 30))
        
        # Copyright
        self.copyright_label = ctk.CTkLabel(
            self.main_frame,
            text="© 2024 tvcraft01 | Version 2.0.0",
            font=("Segoe UI", 10),
            text_color="#666666"
        )
        self.copyright_label.pack(side="bottom", pady=10)
        
    def start_loading_animation(self):
        """Démarre l'animation de chargement simulée"""
        self.loading_steps = [
            ("Initialisation du noyau...", 0.15),
            ("Chargement des modules vocaux...", 0.25),
            ("Connexion aux services IA...", 0.40),
            ("Configuration de l'interface...", 0.60),
            ("Scanner des applications...", 0.75),
            ("Préparation de l'assistant...", 0.90),
            ("Démarrage de Zodiac OS...", 1.0)
        ]
        
        # Démarrer l'animation dans un thread séparé
        thread = threading.Thread(target=self.animate_loading, daemon=True)
        thread.start()
        
    def animate_loading(self):
        """Animation de la barre de progression et des étapes"""
        total_steps = len(self.loading_steps)
        
        for i, (step_text, target_progress) in enumerate(self.loading_steps):
            # Mettre à jour le texte
            self.root.after(0, self.loading_label.configure, {"text": step_text})
            
            # Animer la progression
            current_progress = self.progressbar.get()
            steps = 20  # Nombre d'étapes pour l'animation fluide
            step_increment = (target_progress - current_progress) / steps
            
            for j in range(steps):
                new_progress = current_progress + (step_increment * (j + 1))
                self.root.after(0, self.progressbar.set, new_progress)
                
                # Mettre à jour le pourcentage
                percentage = int(new_progress * 100)
                self.root.after(0, self.percentage_label.configure, {"text": f"{percentage}%"})
                
                time.sleep(0.03)  # Vitesse d'animation
            
            # Petite pause entre les étapes
            if i < total_steps - 1:
                time.sleep(0.3)
        
        # Chargement terminé
        self.loading_complete = True
        
        # Attendre un moment puis fermer
        time.sleep(0.5)
        self.root.after(0, self.close_splash)
        
    def close_splash(self):
        """Ferme le splash screen et appelle le callback"""
        # Animation de fondu
        for i in range(10, -1, -1):
            alpha = i / 10
            self.root.attributes("-alpha", alpha)
            self.root.update()
            time.sleep(0.02)
        
        self.root.destroy()
        self.on_complete()
        
    def run(self):
        """Lance le splash screen"""
        self.root.mainloop()

# Fonction utilitaire pour tester le splash screen seul
if __name__ == "__main__":
    def on_complete():
        print("Chargement terminé !")
        sys.exit(0)
    
    splash = SplashScreen(on_complete)
    splash.run()