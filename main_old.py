"""
🚀 ZODIAC - Assistant Vocal Intelligent
Version complète avec reconnaissance vocale, gestion d'erreurs et intelligence
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import queue
import json
import os
import sys
import time
from datetime import datetime

# --- GESTION DES IMPORTS AVEC ERREURS ---
def safe_import(module_name, install_name=None):
    """Importe un module en gérant les erreurs"""
    try:
        if module_name == 'speech_recognition':
            import speech_recognition as sr
            return sr
        elif module_name == 'pyttsx3':
            import pyttsx3
            return pyttsx3
        elif module_name == 'psutil':
            import psutil
            return psutil
        elif module_name == 'pyautogui':
            import pyautogui
            return pyautogui
        else:
            return __import__(module_name)
    except ImportError as e:
        print(f"❌ Module manquant: {module_name}")
        print(f"   Installez-le: pip install {install_name or module_name}")
        return None

# Importations sécurisées
sr = safe_import('speech_recognition', 'SpeechRecognition')
tts = safe_import('pyttsx3', 'pyttsx3')
psutil_module = safe_import('psutil', 'psutil')
pyautogui_module = safe_import('pyautogui', 'pyautogui')

class ZodiacVoiceAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 ZODIAC - Assistant Vocal")
        self.root.geometry("800x600")
        self.root.configure(bg='#0f172a')
        
        # Files
        self.config_file = "zodiac_config.json"
        self.permissions_file = "permissions.json"
        self.error_log_file = "error_log.txt"
        
        # State
        self.is_listening = False
        self.is_processing = False
        self.voice_enabled = False
        self.command_queue = queue.Queue()
        
        # Services
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        
        # Setup
        self.setup_directories()
        self.load_config()
        self.setup_services()
        self.setup_ui()
        self.setup_voice_thread()
        
        # Welcome
        self.add_to_log("🤖", "Zodiac démarré. Dites 'Zodiac' pour activer.")
        self.speak("Zodiac prêt. Dites Zodiac pour commencer.")
        
    def setup_directories(self):
        """Crée les dossiers nécessaires"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
    def load_config(self):
        """Charge ou crée la configuration"""
        default_config = {
            "first_run": True,
            "voice_enabled": True,
            "auto_listen": False,
            "language": "fr-FR",
            "theme": "dark"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = default_config
        else:
            self.config = default_config
            
    def save_config(self):
        """Sauvegarde la configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def setup_services(self):
        """Initialise les services avec gestion d'erreurs"""
        # Reconnaissance vocale
        if sr:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self.add_to_log("✅", "Microphone détecté")
            except Exception as e:
                self.add_to_log("❌", f"Erreur microphone: {e}")
        else:
            self.add_to_log("⚠️", "SpeechRecognition non installé")
            
        # Synthèse vocale
        if tts:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.voice_enabled = True
                self.add_to_log("✅", "Synthèse vocale activée")
            except Exception as e:
                self.add_to_log("❌", f"Erreur synthèse vocale: {e}")
        else:
            self.add_to_log("⚠️", "pyttsx3 non installé")
            
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Zone de log
        self.log_text = scrolledtext.ScrolledText(
            self.root,
            bg='#1e293b',
            fg='white',
            font=('Consolas', 10),
            height=20
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_frame = tk.Frame(self.root, bg='#334155', height=40)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="🔴 En attente...",
            bg='#334155',
            fg='white',
            font=('Arial', 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Boutons de contrôle
        control_frame = tk.Frame(self.root, bg='#0f172a')
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Bouton microphone
        self.mic_button = tk.Button(
            control_frame,
            text="🎤 DÉMARRER L'ÉCOUTE",
            bg='#ef4444',
            fg='white',
            font=('Arial', 11, 'bold'),
            command=self.toggle_listening
        )
        self.mic_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton parler
        tk.Button(
            control_frame,
            text="🔊 TESTER LA VOIX",
            bg='#3b82f6',
            fg='white',
            font=('Arial', 11),
            command=lambda: self.speak("Test de la voix Zodiac")
        ).pack(side=tk.LEFT, padx=5)
        
        # Bouton commandes
        tk.Button(
            control_frame,
            text="📋 COMMANDES",
            bg='#10b981',
            fg='white',
            font=('Arial', 11),
            command=self.show_commands
        ).pack(side=tk.LEFT, padx=5)
        
        # Zone de commande texte
        self.text_input = tk.Entry(
            control_frame,
            bg='#475569',
            fg='white',
            font=('Arial', 12),
            width=30
        )
        self.text_input.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.text_input.bind('<Return>', self.process_text_command)
        
        # Indicateur vocal
        self.voice_indicator = tk.Label(
            self.status_frame,
            text="",
            bg='#334155',
            fg='#fbbf24',
            font=('Arial', 20)
        )
        self.voice_indicator.pack(side=tk.RIGHT, padx=10)
        
    def setup_voice_thread(self):
        """Démarre le thread d'écoute vocale"""
        self.voice_thread = threading.Thread(target=self.voice_listener, daemon=True)
        self.voice_thread.start()
        
    def add_to_log(self, icon, message, color="white"):
        """Ajoute un message au log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"{timestamp} {icon} {message}\n")
        
        # Colorisation
        if color == "green":
            self.log_text.tag_add("green", f"end-2l linestart", f"end-2l lineend")
            self.log_text.tag_config("green", foreground="#10b981")
        elif color == "red":
            self.log_text.tag_add("red", f"end-2l linestart", f"end-2l lineend")
            self.log_text.tag_config("red", foreground="#ef4444")
        elif color == "yellow":
            self.log_text.tag_add("yellow", f"end-2l linestart", f"end-2l lineend")
            self.log_text.tag_config("yellow", foreground="#f59e0b")
        elif color == "blue":
            self.log_text.tag_add("blue", f"end-2l linestart", f"end-2l lineend")
            self.log_text.tag_config("blue", foreground="#3b82f6")
            
        self.log_text.see(tk.END)
        
    def log_error(self, error_message):
        """Log une erreur"""
        self.add_to_log("❌", error_message, "red")
        
        # Sauvegarder dans le fichier d'erreurs
        with open(self.error_log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {error_message}\n")
            
    def update_status(self, message, color="white"):
        """Met à jour la barre de statut"""
        self.status_label.config(text=message, fg=color)
        
    def toggle_listening(self):
        """Active/désactive l'écoute"""
        if not self.recognizer:
            self.log_error("Microphone non disponible")
            return
            
        self.is_listening = not self.is_listening
        
        if self.is_listening:
            self.mic_button.config(text="⏸️ ARRÊTER L'ÉCOUTE", bg='#10b981')
            self.update_status("🎤 Écoute active - Dites 'Zodiac'", "#10b981")
            self.voice_indicator.config(text="🔊")
            self.speak("Écoute activée")
        else:
            self.mic_button.config(text="🎤 DÉMARRER L'ÉCOUTE", bg='#ef4444')
            self.update_status("🔴 Écoute arrêtée", "#ef4444")
            self.voice_indicator.config(text="")
            self.speak("Écoute désactivée")
            
    def voice_listener(self):
        """Écoute continue de la voix"""
        while True:
            if self.is_listening and self.recognizer and self.microphone:
                try:
                    with self.microphone as source:
                        # Ajustement du bruit ambiant
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        
                        # Écoute avec timeout
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        
                        # Reconnaissance
                        try:
                            text = self.recognizer.recognize_google(audio, language='fr-FR')
                            text = text.lower()
                            
                            # Animation indicateur
                            self.root.after(0, self.voice_indicator.config, {"text": "🎤"})
                            
                            # Traitement
                            self.root.after(0, self.process_voice_command, text)
                            
                            # Réinitialiser l'indicateur après 1s
                            self.root.after(1000, self.voice_indicator.config, {"text": "🔊"})
                            
                        except sr.UnknownValueError:
                            self.root.after(0, self.add_to_log, "🔇", "Audio non compris", "yellow")
                        except sr.RequestError as e:
                            self.root.after(0, self.log_error, f"Erreur API: {e}")
                            
                except sr.WaitTimeoutError:
                    pass
                except Exception as e:
                    self.root.after(0, self.log_error, f"Erreur écoute: {e}")
                    
            time.sleep(0.1)
            
    def process_voice_command(self, text):
        """Traite une commande vocale"""
        self.add_to_log("🎤", f"Reçu: {text}", "blue")
        
        # Détection du mot-clé "zodiac"
        if 'zodiac' in text:
            command = text.replace('zodiac', '').strip()
            if command:
                self.execute_command(command)
                return
                
        # Si court, probablement une commande directe
        if len(text.split()) <= 4:
            self.execute_command(text)
            
    def process_text_command(self, event=None):
        """Traite une commande texte"""
        text = self.text_input.get().strip()
        if not text:
            return
            
        self.text_input.delete(0, tk.END)
        self.add_to_log("⌨️", f"Commande: {text}", "blue")
        self.execute_command(text)
        
    def execute_command(self, command):
        """Exécute une commande"""
        if self.is_processing:
            self.add_to_log("⚠️", "Déjà en traitement...", "yellow")
            return
            
        self.is_processing = True
        
        try:
            # Conversion en minuscules pour la comparaison
            cmd_lower = command.lower()
            
            # --- COMMANDES SYSTÈME ---
            if any(word in cmd_lower for word in ['arrête', 'stop', 'quitte', 'exit']):
                self.speak("Arrêt de Zodiac")
                self.root.after(2000, self.root.quit)
                
            elif any(word in cmd_lower for word in ['aide', 'help', 'commandes']):
                self.show_commands()
                
            elif any(word in cmd_lower for word in ['test', 'teste']):
                self.speak("Test réussi ! Zodiac fonctionne correctement.")
                self.add_to_log("✅", "Test réussi", "green")
                
            # --- APPLICATIONS ---
            elif any(word in cmd_lower for word in ['ouvre', 'lance', 'start', 'run']):
                self.launch_application(cmd_lower)
                
            # --- MÉDIA ---
            elif any(word in cmd_lower for word in ['musique', 'chanson', 'son']):
                self.control_media(cmd_lower)
                
            elif 'volume' in cmd_lower:
                self.control_volume(cmd_lower)
                
            # --- SYSTÈME ---
            elif any(word in cmd_lower for word in ['cpu', 'mémoire', 'ram', 'système']):
                self.system_info(cmd_lower)
                
            elif any(word in cmd_lower for word in ['heure', 'date']):
                self.show_time(cmd_lower)
                
            # --- WEB ---
            elif any(word in cmd_lower for word in ['recherche', 'cherche', 'google']):
                self.web_search(cmd_lower)
                
            # --- DÉFAUT ---
            else:
                response = self.intelligent_response(command)
                self.speak(response)
                
        except Exception as e:
            error_msg = f"Erreur commande: {str(e)}"
            self.log_error(error_msg)
            self.speak("Désolé, une erreur est survenue.")
            
        finally:
            self.is_processing = False
            
    def launch_application(self, command):
        """Lance une application"""
        # Extraction du nom d'app
        app_name = command
        for word in ['ouvre ', 'lance ', 'start ', 'run ', 'ouvrir ', 'lancer ']:
            app_name = app_name.replace(word, '')
            
        app_name = app_name.strip()
        
        if not app_name:
            self.speak("Quelle application voulez-vous ouvrir ?")
            return
            
        self.add_to_log("🔍", f"Recherche: {app_name}", "blue")
        
        # Mapping des applications courantes
        app_map = {
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'deezer': 'Deezer.exe',
            'spotify': 'Spotify.exe',
            'discord': 'Discord.exe',
            'vscode': 'Code.exe',
            'notepad': 'notepad.exe',
            'calc': 'calc.exe',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe'
        }
        
        # Chercher l'application
        found = False
        for key, exe in app_map.items():
            if key in app_name:
                try:
                    import os
                    import subprocess
                    
                    # Essayer plusieurs méthodes
                    try:
                        os.startfile(exe)
                    except:
                        subprocess.Popen([exe], shell=True)
                        
                    self.speak(f"Je lance {key}")
                    self.add_to_log("✅", f"Application lancée: {key}", "green")
                    found = True
                    break
                    
                except Exception as e:
                    self.log_error(f"Erreur lancement {key}: {e}")
                    continue
                    
        if not found:
            # Essayer avec le nom directement
            try:
                import os
                os.system(f'start {app_name}')
                self.speak(f"Tentative de lancement de {app_name}")
                self.add_to_log("⚠️", f"Tentative: {app_name}", "yellow")
            except Exception as e:
                self.speak(f"Je n'ai pas pu lancer {app_name}")
                self.log_error(f"Échec lancement: {app_name}")
                
    def control_media(self, command):
        """Contrôle multimédia"""
        if not pyautogui_module:
            self.speak("Contrôle média non disponible")
            return
            
        try:
            if 'suivant' in command or 'next' in command:
                pyautogui_module.press('nexttrack')
                self.speak("Musique suivante")
            elif 'précédent' in command or 'previous' in command:
                pyautogui_module.press('prevtrack')
                self.speak("Musique précédente")
            elif 'pause' in command or 'stop' in command:
                pyautogui_module.press('playpause')
                self.speak("Musique en pause")
            elif 'play' in command or 'joue' in command:
                pyautogui_module.press('playpause')
                self.speak("Lecture musique")
            else:
                self.speak("Commande média non reconnue")
                
        except Exception as e:
            self.log_error(f"Erreur contrôle média: {e}")
            self.speak("Impossible de contrôler le média")
            
    def control_volume(self, command):
        """Contrôle du volume"""
        if not pyautogui_module:
            self.speak("Contrôle volume non disponible")
            return
            
        try:
            if 'plus' in command or 'augmente' in command:
                pyautogui_module.press('volumeup')
                self.speak("Volume augmenté")
            elif 'moins' in command or 'baisse' in command:
                pyautogui_module.press('volumedown')
                self.speak("Volume baissé")
            elif 'mute' in command or 'silence' in command:
                pyautogui_module.press('volumemute')
                self.speak("Volume coupé")
            else:
                self.speak("Commande volume non reconnue")
                
        except Exception as e:
            self.log_error(f"Erreur contrôle volume: {e}")
            
    def system_info(self, command):
        """Affiche les infos système"""
        if not psutil_module:
            self.speak("Informations système non disponibles")
            return
            
        try:
            if 'cpu' in command:
                cpu = psutil_module.cpu_percent()
                self.speak(f"Le processeur est utilisé à {cpu:.0f} pourcent")
            elif 'mémoire' in command or 'ram' in command:
                mem = psutil_module.virtual_memory()
                self.speak(f"La mémoire est utilisée à {mem.percent:.0f} pourcent")
            else:
                cpu = psutil_module.cpu_percent()
                mem = psutil_module.virtual_memory()
                self.speak(f"Système: processeur {cpu:.0f} pourcent, mémoire {mem.percent:.0f} pourcent")
                
        except Exception as e:
            self.log_error(f"Erreur système: {e}")
            self.speak("Impossible de récupérer les informations")
            
    def show_time(self, command):
        """Affiche l'heure ou la date"""
        now = datetime.now()
        
        if 'heure' in command:
            self.speak(f"Il est {now.hour} heures {now.minute}")
            self.add_to_log("🕐", f"Heure: {now.hour}:{now.minute:02d}")
        elif 'date' in command:
            from datetime import datetime
            months_fr = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
            self.speak(f"Nous sommes le {now.day} {months_fr[now.month-1]} {now.year}")
            
    def web_search(self, command):
        """Recherche web"""
        query = command
        for word in ['recherche ', 'cherche ', 'google ']:
            query = query.replace(word, '')
            
        if query:
            import webbrowser
            webbrowser.open(f'https://www.google.com/search?q={query}')
            self.speak(f"Recherche pour {query}")
        else:
            self.speak("Que voulez-vous rechercher ?")
            
    def intelligent_response(self, text):
        """Réponse intelligente par défaut"""
        text_lower = text.lower()
        
        # Salutations
        if any(word in text_lower for word in ['bonjour', 'salut', 'hello', 'coucou']):
            return "Bonjour ! Comment puis-je vous aider ?"
            
        # Ça va ?
        if any(word in text_lower for word in ['ça va', 'vas bien', 'comment ça va']):
            return "Je vais très bien, merci ! Et vous ?"
            
        # Merci
        if any(word in text_lower for word in ['merci', 'thanks']):
            return "Avec plaisir !"
            
        # Questions
        if '?' in text:
            if 'qui' in text_lower:
                return "Je suis Zodiac, votre assistant vocal !"
            elif 'quoi' in text_lower:
                return "Je suis ici pour vous aider !"
            elif 'pourquoi' in text_lower:
                return "Pour rendre votre vie plus simple !"
                
        # Réponses par défaut
        responses = [
            "Je comprends. Que voulez-vous faire ?",
            "D'accord. Comment puis-je vous aider ?",
            "Je vois. Avez-vous une demande spécifique ?"
        ]
        
        import random
        return random.choice(responses)
        
    def speak(self, text):
        """Parle le texte"""
        if not self.tts_engine:
            self.add_to_log("🔇", f"(Voix): {text}", "yellow")
            return
            
        def speak_thread():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                self.log_error(f"Erreur synthèse vocale: {e}")
                
        threading.Thread(target=speak_thread, daemon=True).start()
        self.add_to_log("🔊", text, "green")
        
    def show_commands(self):
        """Affiche les commandes disponibles"""
        commands = """
🎯 **COMMANDES VOCALES:**

**BASIQUE:**
• "Zodiac arrête" - Quitter
• "Zodiac aide" - Afficher l'aide
• "Zodiac test" - Tester le système

**APPLICATIONS:**
• "Zodiac ouvre chrome/firefox/deezer"
• "Zodiac lance spotify/vscode"

**MUSIQUE:**
• "Zodiac musique suivante/précédente"
• "Zodiac pause musique"
• "Zodiac volume plus/moins"

**SYSTÈME:**
• "Zodiac état du système"
• "Zodiac cpu/mémoire"
• "Zodiac quelle heure"

**WEB:**
• "Zodiac recherche [terme]"

**TEXTE:**
• Tapez directement dans la zone de saisie
        """
        
        # Afficher dans une fenêtre séparée
        help_window = tk.Toplevel(self.root)
        help_window.title("Commandes Zodiac")
        help_window.geometry("500x600")
        help_window.configure(bg='#0f172a')
        
        text_widget = scrolledtext.ScrolledText(
            help_window,
            bg='#1e293b',
            fg='white',
            font=('Consolas', 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, commands)
        text_widget.config(state=tk.DISABLED)
        
        self.speak("Voici les commandes disponibles")
        
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

# --- LANCEMENT ---
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════╗
    ║      🎤 ZODIAC - Assistant Vocal     ║
    ╚══════════════════════════════════════╝
    """)
    
    print("🔧 Vérification des modules...")
    
    # Vérifier les modules
    modules = [
        ('speech_recognition', 'SpeechRecognition'),
        ('pyttsx3', 'pyttsx3'),
        ('psutil', 'psutil'),
        ('pyautogui', 'pyautogui')
    ]
    
    missing = []
    for module, install in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except:
            print(f"❌ {module}")
            missing.append(install)
    
    if missing:
        print(f"\n⚠️ Modules manquants: {', '.join(missing)}")
        print(f"📦 Installez-les: pip install {' '.join(missing)}")
    
    print("\n🚀 Lancement de Zodiac...")
    
    # Lancer l'application
    app = ZodiacVoiceAssistant()
    app.run()