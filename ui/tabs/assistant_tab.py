"""
Onglet Assistant pour Zodiac OS
Auteur: tvcraft01
"""
import customtkinter as ctk
import threading
import time
from datetime import datetime
from PIL import Image, ImageDraw
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class AssistantTab(ctk.CTkFrame):
    def __init__(self, parent):
        """Initialise l'onglet Assistant"""
        super().__init__(parent, corner_radius=0, fg_color="#0A0A0F")
        
        # Configuration des couleurs
        self.bg_color = "#0A0A0F"
        self.chat_bg = "#1A1A2E"
        self.user_bubble = "#6C63FF"
        self.assistant_bubble = "#2A2A3E"
        self.accent_color = "#00D4AA"
        self.text_color = "#FFFFFF"
        self.secondary_text = "#B0B0B0"
        
        # État du microphone
        self.is_listening = False
        self.voice_engine = None  # Sera connecté plus tard
        
        # Historique du chat
        self.chat_history = []
        
        # Configuration de la grille
        self.grid_rowconfigure(0, weight=1)  # Zone du chat
        self.grid_rowconfigure(1, weight=0)  # Zone de saisie
        self.grid_columnconfigure(0, weight=1)
        
        # Créer l'interface
        self.setup_ui()
        
        # Ajouter un message de bienvenue
        self.add_message("assistant", "Bonjour ! Je suis Zodiac, votre assistant vocal intelligent. Comment puis-je vous aider ?")
        
    def setup_ui(self):
        """Configure l'interface de l'onglet Assistant"""
        # --- ZONE DU CHAT ---
        self.chat_frame = ctk.CTkFrame(
            self,
            fg_color=self.chat_bg,
            corner_radius=15
        )
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas pour le chat avec scrollbar
        self.chat_canvas = ctk.CTkCanvas(
            self.chat_frame,
            bg=self.chat_bg,
            highlightthickness=0
        )
        
        # Scrollbar
        self.scrollbar = ctk.CTkScrollbar(
            self.chat_frame,
            command=self.chat_canvas.yview
        )
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Frame interne pour les messages
        self.messages_frame = ctk.CTkFrame(
            self.chat_canvas,
            fg_color=self.chat_bg,
            corner_radius=0
        )
        
        # Fenêtre dans le canvas
        self.canvas_window = self.chat_canvas.create_window(
            (0, 0),
            window=self.messages_frame,
            anchor="nw",
            width=self.chat_canvas.winfo_reqwidth()
        )
        
        # Placement des widgets
        self.chat_canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configuration de la grille du chat
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        
        # --- WIDGETS D'ACTIONS RAPIDES ---
        self.quick_actions_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=60
        )
        self.quick_actions_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.quick_actions_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Boutons d'actions rapides
        quick_actions = [
            ("🌤️ Météo", self.quick_weather),
            ("🎵 Musique", self.quick_music),
            ("📅 Agenda", self.quick_calendar),
            ("🔍 Recherche", self.quick_search)
        ]
        
        for i, (text, command) in enumerate(quick_actions):
            btn = ctk.CTkButton(
                self.quick_actions_frame,
                text=text,
                font=("Segoe UI", 13),
                fg_color="#2A2A3E",
                hover_color="#3A3A4E",
                text_color=self.text_color,
                height=40,
                corner_radius=20,
                command=command
            )
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        
        # --- ZONE DE SAISIE ---
        self.input_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=80
        )
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=0)
        self.input_frame.grid_columnconfigure(2, weight=0)
        
        # Champ de saisie
        self.input_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Tapez ou parlez à Zodiac...",
            font=("Segoe UI", 14),
            height=50,
            corner_radius=25,
            fg_color="#2A2A3E",
            border_color="#6C63FF",
            text_color=self.text_color
        )
        self.input_entry.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        self.input_entry.bind("<Return>", lambda e: self.send_message())
        
        # Bouton microphone avec état
        self.mic_button = ctk.CTkButton(
            self.input_frame,
            text="🎤",
            font=("Segoe UI", 20),
            width=50,
            height=50,
            corner_radius=25,
            fg_color="#6C63FF",
            hover_color="#7C73FF",
            command=self.toggle_listening
        )
        self.mic_button.grid(row=0, column=1, padx=(0, 10), pady=5)
        
        # Bouton d'envoi
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="➤",
            font=("Segoe UI", 20),
            width=50,
            height=50,
            corner_radius=25,
            fg_color=self.accent_color,
            hover_color="#10E4BA",
            command=self.send_message
        )
        self.send_button.grid(row=0, column=2, pady=5)
        
        # Indicateur d'état vocal
        self.voice_indicator = ctk.CTkLabel(
            self.input_frame,
            text="",
            font=("Segoe UI", 12),
            text_color=self.accent_color
        )
        self.voice_indicator.grid(row=1, column=0, columnspan=3, pady=(5, 0))
        
        # --- ANIMATION DU MICROPHONE ---
        self.mic_animation_id = None
        self.mic_animation_running = False
        
        # Gestion du redimensionnement
        self.bind("<Configure>", self.on_resize)
        self.messages_frame.bind("<Configure>", self.update_scrollregion)
        
    def add_message(self, sender, text):
        """Ajoute un message au chat"""
        # Stocker dans l'historique
        self.chat_history.append({
            "sender": sender,
            "text": text,
            "time": datetime.now().strftime("%H:%M")
        })
        
        # Créer un frame pour le message
        message_frame = ctk.CTkFrame(
            self.messages_frame,
            fg_color="transparent",
            corner_radius=0
        )
        
        # Configuration de la bulle
        if sender == "user":
            bubble_color = self.user_bubble
            align = "right"
            sender_text = "Vous"
        else:
            bubble_color = self.assistant_bubble
            align = "left"
            sender_text = "Zodiac"
        
        # Frame de la bulle
        bubble_frame = ctk.CTkFrame(
            message_frame,
            fg_color=bubble_color,
            corner_radius=15
        )
        
        # Texte du message
        message_label = ctk.CTkLabel(
            bubble_frame,
            text=text,
            font=("Segoe UI", 13),
            text_color=self.text_color,
            wraplength=500,
            justify="left"
        )
        message_label.pack(padx=15, pady=10, anchor="w")
        
        # Infos (expéditeur + heure)
        info_label = ctk.CTkLabel(
            bubble_frame,
            text=f"{sender_text} • {self.chat_history[-1]['time']}",
            font=("Segoe UI", 10),
            text_color=self.secondary_text
        )
        info_label.pack(padx=15, pady=(0, 5), anchor="e")
        
        # Placement de la bulle
        if align == "right":
            bubble_frame.pack(anchor="e", padx=10, pady=5)
            message_frame.grid_columnconfigure(0, weight=1)
        else:
            bubble_frame.pack(anchor="w", padx=10, pady=5)
        
        # Ajouter au frame des messages
        message_frame.pack(fill="x", padx=5, pady=2)
        
        # Mettre à jour le scroll
        self.update_scrollregion()
        
        # Scroll vers le bas
        self.chat_canvas.after(100, self.scroll_to_bottom)
        
    def send_message(self):
        """Envoie le message du champ de saisie"""
        text = self.input_entry.get().strip()
        if text:
            # Ajouter le message utilisateur
            self.add_message("user", text)
            
            # Effacer le champ
            self.input_entry.delete(0, "end")
            
            # Simuler une réponse (à remplacer par l'appel réel à l'assistant)
            self.simulate_assistant_response(text)
            
    def simulate_assistant_response(self, user_input):
        """Simule une réponse de l'assistant (temporaire)"""
        # Démarrer un thread pour ne pas bloquer l'interface
        thread = threading.Thread(target=self._process_response, args=(user_input,))
        thread.daemon = True
        thread.start()
        
    def _process_response(self, user_input):
        """Traite la réponse de l'assistant"""
        # Simuler un délai de traitement
        time.sleep(0.5)
        
        # Réponses simulées (à remplacer par l'IA réelle)
        responses = {
            "météo": "Actuellement, il fait 22°C avec un temps partiellement nuageux à Paris.",
            "bonjour": "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
            "heure": f"Il est actuellement {datetime.now().strftime('%H:%M')}.",
            "musique": "Je lance Spotify pour vous. Quelle musique souhaitez-vous écouter ?"
        }
        
        # Chercher une réponse correspondante
        response = "J'ai bien reçu votre message. Pour une réponse complète, connectez-moi à votre assistant IA."
        user_input_lower = user_input.lower()
        
        for key in responses:
            if key in user_input_lower:
                response = responses[key]
                break
        
        # Ajouter la réponse dans l'interface (dans le thread principal)
        self.after(0, self.add_message, "assistant", response)
        
    def toggle_listening(self):
        """Active/désactive l'écoute vocale"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
            
    def start_listening(self):
        """Démarre l'écoute vocale"""
        self.is_listening = True
        self.mic_button.configure(fg_color="#FF6B6B")  # Rouge quand en écoute
        self.voice_indicator.configure(text="🎤 Écoute active... Parlez maintenant")
        
        # Démarrer l'animation du microphone
        self.start_mic_animation()
        
        # TODO: Connecter au VoiceEngine réel
        print("Démarrage de l'écoute vocale...")
        
    def stop_listening(self):
        """Arrête l'écoute vocale"""
        self.is_listening = False
        self.mic_button.configure(fg_color="#6C63FF")  # Retour à la couleur normale
        self.voice_indicator.configure(text="")
        
        # Arrêter l'animation
        self.stop_mic_animation()
        
        # TODO: Arrêter le VoiceEngine réel
        print("Arrêt de l'écoute vocale...")
        
    def start_mic_animation(self):
        """Démarre l'animation du microphone (VU-mètre)"""
        if self.mic_animation_running:
            return
            
        self.mic_animation_running = True
        self.animate_mic_level()
        
    def animate_mic_level(self):
        """Anime le niveau du microphone (simulation)"""
        if not self.mic_animation_running:
            return
            
        # Simuler un niveau aléatoire
        import random
        level = random.randint(1, 5)
        dots = "•" * level
        
        self.mic_button.configure(text=f"🎤{dots}")
        
        # Planifier la prochaine animation
        self.mic_animation_id = self.after(200, self.animate_mic_level)
        
    def stop_mic_animation(self):
        """Arrête l'animation du microphone"""
        self.mic_animation_running = False
        if self.mic_animation_id:
            self.after_cancel(self.mic_animation_id)
        self.mic_button.configure(text="🎤")
        
    def quick_weather(self):
        """Action rapide: Météo"""
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, "Quel temps fait-il aujourd'hui ?")
        self.send_message()
        
    def quick_music(self):
        """Action rapide: Musique"""
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, "Lance de la musique")
        self.send_message()
        
    def quick_calendar(self):
        """Action rapide: Agenda"""
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, "Qu'ai-je prévu aujourd'hui ?")
        self.send_message()
        
    def quick_search(self):
        """Action rapide: Recherche"""
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, "Recherche sur internet")
        self.send_message()
        
    def update_scrollregion(self, event=None):
        """Met à jour la région de scroll du canvas"""
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        
    def scroll_to_bottom(self):
        """Scroll vers le bas du chat"""
        self.chat_canvas.yview_moveto(1.0)
        
    def on_resize(self, event=None):
        """Gère le redimensionnement de la fenêtre"""
        # Ajuster la largeur du frame des messages
        if event and event.widget == self:
            new_width = event.width - 40  # Marges
            self.chat_canvas.itemconfig(self.canvas_window, width=new_width)
            
        # Mettre à jour le scroll
        self.update_scrollregion()
        
    def connect_voice_engine(self, voice_engine):
        """Connecte le moteur vocal à l'interface"""
        self.voice_engine = voice_engine
        # TODO: Implémenter la connexion réelle