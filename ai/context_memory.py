"""
Module 15: Context Memory
Gestion de la mémoire contextuelle pour conversations
"""

import json
import os
from datetime import datetime
from collections import deque
from typing import List, Dict, Optional

class ContextMemory:
    def __init__(self, max_history: int = 5, data_dir: str = "data"):
        """
        Initialise la mémoire contextuelle
        
        Args:
            max_history: Nombre maximum de messages à conserver
            data_dir: Répertoire de stockage des données
        """
        self.max_history = max_history
        self.data_dir = data_dir
        self.conversation_history = deque(maxlen=max_history)
        self.conversation_file = os.path.join(data_dir, "conversations.json")
        
        # Créer le dossier data s'il n'existe pas
        os.makedirs(data_dir, exist_ok=True)
        
        # Charger l'historique précédent
        self.load_history()
    
    def add_message(self, role: str, content: str, timestamp: Optional[str] = None):
        """
        Ajoute un message à l'historique
        
        Args:
            role: 'user' ou 'assistant'
            content: Contenu du message
            timestamp: Horodatage (optionnel)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        
        self.conversation_history.append(message)
        
        # Sauvegarder périodiquement
        if len(self.conversation_history) % 3 == 0:
            self.save_history()
    
    def get_recent_context(self, n: Optional[int] = None) -> List[Dict]:
        """
        Récupère les N derniers messages de contexte
        
        Args:
            n: Nombre de messages (par défaut: tous)
        
        Returns:
            Liste des messages récents
        """
        if n is None or n >= len(self.conversation_history):
            return list(self.conversation_history)
        return list(self.conversation_history)[-n:]
    
    def get_conversation_summary(self) -> str:
        """
        Génère un résumé de la conversation
        
        Returns:
            Résumé textuel
        """
        if not self.conversation_history:
            return "Aucune conversation en cours."
        
        user_messages = [msg for msg in self.conversation_history if msg["role"] == "user"]
        assistant_messages = [msg for msg in self.conversation_history if msg["role"] == "assistant"]
        
        summary = f"Conversation: {len(self.conversation_history)} messages\n"
        summary += f"  • Utilisateur: {len(user_messages)} messages\n"
        summary += f"  • Assistant: {len(assistant_messages)} messages\n"
        
        if user_messages:
            last_user = user_messages[-1]["content"]
            if len(last_user) > 50:
                last_user = last_user[:47] + "..."
            summary += f"Dernière requête: {last_user}"
        
        return summary
    
    def clear_memory(self):
        """Efface la mémoire contextuelle"""
        self.conversation_history.clear()
        print("✓ Mémoire contextuelle effacée")
    
    def save_history(self):
        """Sauvegarde l'historique dans un fichier JSON"""
        try:
            # Charger l'historique existant
            all_conversations = []
            if os.path.exists(self.conversation_file):
                with open(self.conversation_file, 'r', encoding='utf-8') as f:
                    all_conversations = json.load(f)
            
            # Ajouter la conversation actuelle
            session_data = {
                "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "timestamp": datetime.now().isoformat(),
                "messages": list(self.conversation_history)
            }
            
            # Conserver les 10 dernières sessions maximum
            all_conversations.append(session_data)
            if len(all_conversations) > 10:
                all_conversations = all_conversations[-10:]
            
            # Sauvegarder
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                json.dump(all_conversations, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"✗ Erreur sauvegarde historique: {e}")
            return False
    
    def load_history(self):
        """Charge l'historique depuis le fichier JSON"""
        try:
            if os.path.exists(self.conversation_file):
                with open(self.conversation_file, 'r', encoding='utf-8') as f:
                    all_conversations = json.load(f)
                
                if all_conversations:
                    # Charger la dernière session
                    last_session = all_conversations[-1]
                    self.conversation_history.extend(last_session["messages"])
                    print(f"✓ Historique chargé: {len(self.conversation_history)} messages")
                    return True
        except Exception as e:
            print(f"✗ Erreur chargement historique: {e}")
        
        return False
    
    def search_in_memory(self, keyword: str) -> List[Dict]:
        """
        Recherche des messages contenant un mot-clé
        
        Args:
            keyword: Mot-clé à rechercher
        
        Returns:
            Liste des messages correspondants
        """
        results = []
        keyword_lower = keyword.lower()
        
        for msg in self.conversation_history:
            if keyword_lower in msg["content"].lower():
                results.append(msg)
        
        return results

# Test du module
if __name__ == "__main__":
    memory = ContextMemory()
    
    # Test d'ajout de messages
    memory.add_message("user", "Bonjour, quelle est la météo aujourd'hui ?")
    memory.add_message("assistant", "Je vais vérifier la météo pour vous.")
    memory.add_message("user", "Merci, et les actualités ?")
    
    # Afficher le contexte
    print("Contexte récent:")
    for msg in memory.get_recent_context():
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # Afficher le résumé
    print(f"\n{memory.get_conversation_summary()}")