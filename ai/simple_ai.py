"""
Module AI simple pour Zodiac - Version basique mais fonctionnelle
"""

import random
from datetime import datetime

class SimpleAI:
    def __init__(self):
        self.commands = self._load_commands()
        self.conversation_history = []
    
    def _load_commands(self):
        """Charge les commandes et réponses"""
        return {
            # Salutations
            'bonjour': [
                "Bonjour ! Je suis Zodiac, votre assistant personnel. 😊",
                "Salut ! Prêt à booster votre productivité ?",
                "Hello ! Comment puis-je vous aider aujourd'hui ?"
            ],
            'salut': [
                "Salut ! Que puis-je faire pour vous ?",
                "Bonjour ! En quoi puis-je vous assister ?"
            ],
            'hello': [
                "Hello ! I'm Zodiac, your personal assistant. How can I help?",
                "Hi there! Ready to get things done?"
            ],
            
            # Ça va ?
            'ça va': [
                "Je vais très bien, merci ! Et vous ?",
                "Tout va bien de mon côté ! Prêt à vous aider."
            ],
            'comment ça va': [
                "Je fonctionne parfaitement ! Merci de demander. 😊"
            ],
            
            # Parle anglais ?
            'anglais': [
                "Oui, je parle anglais ! Yes, I speak English! 🇬🇧",
                "Bien sûr ! I can speak English fluently."
            ],
            'english': [
                "Yes, I speak English! How can I assist you today?"
            ],
            
            # Remerciements
            'merci': [
                "Avec plaisir ! 😊",
                "Je suis là pour ça !",
                "De rien ! N'hésitez pas si besoin."
            ],
            'thanks': [
                "You're welcome!",
                "My pleasure!"
            ],
            
            # Au revoir
            'au revoir': [
                "Au revoir ! À bientôt ! 👋",
                "Bye ! N'hésitez pas à revenir."
            ],
            'bye': [
                "Goodbye! See you soon!",
                "Bye! Take care!"
            ]
        }
    
    def process(self, user_input):
        """Traite l'entrée utilisateur et retourne une réponse"""
        user_input_lower = user_input.lower()
        self.conversation_history.append({
            'user': user_input,
            'time': datetime.now().isoformat()
        })
        
        # Limiter l'historique à 10 messages
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)
        
        # 1. Commandes de lancement
        if any(word in user_input_lower for word in ['ouvre', 'lance', 'start', 'run']):
            return self._handle_open_command(user_input_lower)
        
        # 2. Informations système
        elif any(word in user_input_lower for word in ['cpu', 'mémoire', 'ram', 'système']):
            return "💻 **Informations système:**\nJe vais vérifier l'état du système..."
        
        # 3. Météo
        elif 'météo' in user_input_lower or 'weather' in user_input_lower:
            return self._handle_weather(user_input_lower)
        
        # 4. Recherche
        elif any(word in user_input_lower for word in ['recherche', 'cherche', 'search']):
            return self._handle_search(user_input_lower)
        
        # 5. Aide
        elif 'aide' in user_input_lower or 'help' in user_input_lower:
            return self._get_help()
        
        # 6. Commandes prédéfinies
        for keyword, responses in self.commands.items():
            if keyword in user_input_lower:
                return random.choice(responses)
        
        # 7. Questions
        if '?' in user_input:
            return self._answer_question(user_input_lower)
        
        # 8. Réponse intelligente par défaut
        return self._get_smart_response(user_input_lower)
    
    def _handle_open_command(self, text):
        """Gère les commandes d'ouverture"""
        app_name = text
        for word in ['ouvre ', 'lance ', 'start ', 'run ', 'ouvrir ', 'lancer ']:
            app_name = app_name.replace(word, "")
        
        if app_name:
            return f"🚀 Je lance l'application '{app_name.strip()}'..."
        return "Quelle application voulez-vous ouvrir ?"
    
    def _handle_weather(self, text):
        """Gère les demandes météo"""
        city = "Paris"
        if 'météo' in text:
            parts = text.split('météo')
            if len(parts) > 1 and parts[1].strip():
                city = parts[1].strip()
        elif 'weather' in text:
            parts = text.split('weather')
            if len(parts) > 1 and parts[1].strip():
                city = parts[1].strip()
        
        return f"🌤️ Je cherche la météo pour {city}..."
    
    def _handle_search(self, text):
        """Gère les recherches"""
        query = text
        for word in ['recherche ', 'cherche ', 'search ']:
            query = query.replace(word, "")
        
        if query and len(query) > 2:
            return f"🔍 Je recherche '{query.strip()}' sur le web..."
        return "Que souhaitez-vous rechercher ?"
    
    def _get_help(self):
        """Retourne le texte d'aide"""
        return """🛠️ **Commandes disponibles:**

**Applications:**
• 'ouvre chrome' - Lance Chrome
• 'lance spotify' - Lance Spotify
• 'ouvre deezer' - Lance Deezer

**Système:**
• 'cpu' - Informations processeur
• 'mémoire' - Utilisation mémoire
• 'système' - État général

**Web & Info:**
• 'météo paris' - Météo d'une ville
• 'recherche python' - Recherche web
• 'actualités' - Dernières nouvelles

**Divers:**
• 'aide' - Affiche cette aide
• 'notes' - Gestionnaire de notes
• 'minuteur 60' - Minuteur 60 secondes"""
    
    def _answer_question(self, text):
        """Répond aux questions"""
        if 'qui' in text:
            return "Je suis Zodiac, votre assistant personnel IA ! 🤖"
        elif 'quoi' in text:
            return "Je suis ici pour vous aider avec diverses tâches !"
        elif 'pourquoi' in text:
            return "Pour rendre votre vie numérique plus simple et productive !"
        elif 'comment' in text:
            return "Je fonctionne grâce à des algorithmes d'intelligence artificielle !"
        
        return "Bonne question ! Pouvez-vous préciser ?"
    
    def _get_smart_response(self, text):
        """Retourne une réponse intelligente par défaut"""
        if len(text) < 3:
            return "Pouvez-vous développer un peu plus ?"
        
        responses = [
            "Je comprends. Comment puis-je vous aider ?",
            "Intéressant ! Avez-vous besoin d'aide spécifique ?",
            "D'accord. Que souhaitez-vous accomplir ?",
            "Merci pour cette information. Comment puis-je vous assister ?",
            f"Je note que vous dites '{text[:50]}...'. Que voulez-vous faire ensuite ?"
        ]
        
        return random.choice(responses)
    
    def get_history(self):
        """Retourne l'historique de conversation"""
        return self.conversation_history

# Test
if __name__ == "__main__":
    ai = SimpleAI()
    
    test_inputs = [
        "bonjour",
        "ouvre chrome",
        "ça va ?",
        "parle anglais ?",
        "météo paris",
        "aide",
        "merci",
        "au revoir"
    ]
    
    for test in test_inputs:
        print(f"👤: {test}")
        print(f"🤖: {ai.process(test)}\n")