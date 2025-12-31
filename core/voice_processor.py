"""
Moteur vocal pour Zodiac OS - Basé sur old_main.py
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
import webbrowser
import os
import subprocess
from datetime import datetime

class VoiceEngine:
    def __init__(self, callback_function=None):
        """Initialise le moteur vocal avec callback pour l'interface"""
        self.callback = callback_function
        self.is_listening = False
        
        # Initialisation avec gestion d'erreurs
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            print("✅ Microphone initialisé")
        except Exception as e:
            print(f"❌ Erreur microphone: {e}")
        
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            print("✅ Synthèse vocale initialisée")
        except Exception as e:
            print(f"❌ Erreur synthèse vocale: {e}")
    
    def start_listening(self):
        """Démarre l'écoute continue"""
        if not self.recognizer:
            if self.callback:
                self.callback("error", "Microphone non disponible")
            return False
        
        self.is_listening = True
        self.listener_thread = threading.Thread(target=self._listener_loop, daemon=True)
        self.listener_thread.start()
        
        if self.callback:
            self.callback("status", "Écoute activée")
        
        return True
    
    def stop_listening(self):
        """Arrête l'écoute"""
        self.is_listening = False
        if self.callback:
            self.callback("status", "Écoute désactivée")
    
    def _listener_loop(self):
        """Boucle d'écoute principale"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    try:
                        text = self.recognizer.recognize_google(audio, language='fr-FR')
                        text = text.lower()
                        
                        if self.callback:
                            self.callback("voice_command", text)
                        
                        # Détection du mot-clé "zodiac"
                        if 'zodiac' in text:
                            command = text.replace('zodiac', '').strip()
                            if command and self.callback:
                                self.callback("zodiac_command", command)
                        elif len(text.split()) <= 4:
                            # Commande courte
                            if self.callback:
                                self.callback("quick_command", text)
                                
                    except sr.UnknownValueError:
                        if self.callback:
                            self.callback("error", "Audio non compris")
                    except sr.RequestError as e:
                        if self.callback:
                            self.callback("error", f"Erreur API: {e}")
                            
            except Exception as e:
                time.sleep(0.1)
    
    def speak(self, text):
        """Parle un texte (synthèse vocale)"""
        if not self.tts_engine:
            print(f"(Voix): {text}")
            return
        
        def _speak():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Erreur synthèse vocale: {e}")
        
        threading.Thread(target=_speak, daemon=True).start()
    
    def process_command(self, command):
        """Traite une commande - Logique de votre ancien code"""
        command_lower = command.lower()
        
        # --- COMMANDES SYSTÈME ---
        if any(word in command_lower for word in ['arrête', 'stop', 'quitte', 'exit']):
            return "Arrêt de Zodiac"
        
        elif any(word in command_lower for word in ['aide', 'help', 'commandes']):
            return "Commandes: ouvre [app], musique, météo, système, recherche, heure"
        
        elif any(word in command_lower for word in ['test', 'teste']):
            return "Test réussi ! Zodiac fonctionne correctement."
        
        # --- APPLICATIONS ---
        elif any(word in command_lower for word in ['ouvre', 'lance', 'start', 'run']):
            return self._launch_application(command_lower)
        
        # --- MÉDIA ---
        elif any(word in command_lower for word in ['musique', 'chanson', 'son']):
            return self._control_media(command_lower)
        
        elif 'volume' in command_lower:
            return self._control_volume(command_lower)
        
        # --- SYSTÈME ---
        elif any(word in command_lower for word in ['cpu', 'mémoire', 'ram', 'système']):
            return self._system_info(command_lower)
        
        elif any(word in command_lower for word in ['heure', 'date']):
            return self._show_time(command_lower)
        
        # --- WEB ---
        elif any(word in command_lower for word in ['recherche', 'cherche', 'google']):
            return self._web_search(command_lower)
        
        # --- INTELLIGENCE ---
        else:
            return self._intelligent_response(command)
    
    def _launch_application(self, command):
        """Lance une application"""
        app_name = command
        for word in ['ouvre ', 'lance ', 'start ', 'run ', 'ouvrir ', 'lancer ']:
            app_name = app_name.replace(word, '')
        
        app_name = app_name.strip()
        
        if not app_name:
            return "Quelle application voulez-vous ouvrir ?"
        
        # Mapping des applications
        app_map = {
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'spotify': 'Spotify.exe',
            'discord': 'Discord.exe',
            'vscode': 'Code.exe',
            'notepad': 'notepad.exe',
            'calc': 'calc.exe',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe'
        }
        
        for key, exe in app_map.items():
            if key in app_name:
                try:
                    os.startfile(exe)
                    return f"Je lance {key}"
                except:
                    try:
                        subprocess.Popen([exe], shell=True)
                        return f"Je lance {key}"
                    except Exception as e:
                        return f"Erreur avec {key}: {e}"
        
        # Tentative générique
        try:
            os.system(f'start {app_name}')
            return f"Tentative de lancement de {app_name}"
        except:
            return f"Je n'ai pas pu lancer {app_name}"
    
    def _control_media(self, command):
        """Contrôle multimédia"""
        try:
            import pyautogui
            if 'suivant' in command or 'next' in command:
                pyautogui.press('nexttrack')
                return "Musique suivante"
            elif 'précédent' in command or 'previous' in command:
                pyautogui.press('prevtrack')
                return "Musique précédente"
            elif 'pause' in command or 'stop' in command:
                pyautogui.press('playpause')
                return "Musique en pause"
            elif 'play' in command or 'joue' in command:
                pyautogui.press('playpause')
                return "Lecture musique"
            else:
                return "Commande média non reconnue"
        except:
            return "Contrôle média non disponible"
    
    def _control_volume(self, command):
        """Contrôle du volume"""
        try:
            import pyautogui
            if 'plus' in command or 'augmente' in command:
                pyautogui.press('volumeup')
                return "Volume augmenté"
            elif 'moins' in command or 'baisse' in command:
                pyautogui.press('volumedown')
                return "Volume baissé"
            elif 'mute' in command or 'silence' in command:
                pyautogui.press('volumemute')
                return "Volume coupé"
            else:
                return "Commande volume non reconnue"
        except:
            return "Contrôle volume non disponible"
    
    def _system_info(self, command):
        """Affiche les infos système"""
        try:
            import psutil
            if 'cpu' in command:
                cpu = psutil.cpu_percent()
                return f"Le processeur est utilisé à {cpu:.0f}%"
            elif 'mémoire' in command or 'ram' in command:
                mem = psutil.virtual_memory()
                return f"La mémoire est utilisée à {mem.percent:.0f}%"
            else:
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory()
                return f"Système: CPU {cpu:.0f}%, RAM {mem.percent:.0f}%"
        except:
            return "Informations système non disponibles"
    
    def _show_time(self, command):
        """Affiche l'heure ou la date"""
        now = datetime.now()
        
        if 'heure' in command:
            return f"Il est {now.hour} heures {now.minute:02d}"
        elif 'date' in command:
            months_fr = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
            return f"Nous sommes le {now.day} {months_fr[now.month-1]} {now.year}"
    
    def _web_search(self, command):
        """Recherche web"""
        query = command
        for word in ['recherche ', 'cherche ', 'google ']:
            query = query.replace(word, '')
        
        if query:
            webbrowser.open(f'https://www.google.com/search?q={query}')
            return f"Recherche pour {query}"
        else:
            return "Que voulez-vous rechercher ?"
    
    def _intelligent_response(self, text):
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
        import random
        responses = [
            "Je comprends. Que voulez-vous faire ?",
            "D'accord. Comment puis-je vous aider ?",
            "Je vois. Avez-vous une demande spécifique ?"
        ]
        
        return random.choice(responses)