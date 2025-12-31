"""
Module 3: Fuzzy Matcher
Algorithme de comparaison textuelle pour commandes imprécises
"""

import difflib
import re
from typing import List, Dict, Tuple, Optional
from collections import Counter

class FuzzyMatcher:
    def __init__(self, threshold: float = 0.6):
        """
        Initialise le matcher flou
        
        Args:
            threshold: Seuil de similarité (0.0 à 1.0)
        """
        self.threshold = threshold
        self.synonyms = self._load_synonyms()
    
    def _load_synonyms(self) -> Dict[str, List[str]]:
        """Charge les synonymes courants"""
        return {
            'ouvrir': ['lance', 'démarre', 'start', 'run', 'execute', 'lancer'],
            'fermer': ['stop', 'arrête', 'kill', 'terminate', 'quitte', 'exit'],
            'trouver': ['cherche', 'search', 'find', 'recherche'],
            'météo': ['temps', 'weather', 'climat'],
            'actualités': ['news', 'nouvelles', 'infos'],
            'traduire': ['translate', 'translation'],
            'note': ['memo', 'mémorandum', 'reminder'],
            'calculatrice': ['calc', 'calculator'],
            'navigateur': ['browser', 'chrome', 'firefox', 'edge'],
            'musique': ['spotify', 'player', 'lecteur'],
            'volume': ['son', 'sound', 'audio']
        }
    
    def match_command(self, user_input: str, commands: List[str]) -> Optional[Tuple[str, float]]:
        """
        Trouve la commande la plus proche
        
        Args:
            user_input: Entrée utilisateur
            commands: Liste des commandes disponibles
        
        Returns:
            (commande, score) ou None
        """
        if not user_input or not commands:
            return None
        
        user_input = user_input.lower().strip()
        
        # Essayer d'abord une correspondance exacte
        if user_input in commands:
            return (user_input, 1.0)
        
        # Vérifier les synonymes
        for cmd in commands:
            if self._check_synonyms(user_input, cmd):
                return (cmd, 0.9)
        
        # Recherche floue
        best_match = None
        best_score = 0.0
        
        for command in commands:
            score = self._calculate_similarity(user_input, command)
            
            if score > best_score and score >= self.threshold:
                best_score = score
                best_match = command
        
        if best_match:
            return (best_match, best_score)
        
        return None
    
    def _check_synonyms(self, user_input: str, command: str) -> bool:
        """Vérifie les synonymes"""
        command_lower = command.lower()
        
        # Vérifier les synonymes directs
        for key, synonyms in self.synonyms.items():
            if command_lower == key:
                for synonym in synonyms:
                    if synonym in user_input:
                        return True
        
        # Vérifier si la commande est dans les synonymes
        for synonyms in self.synonyms.values():
            if command_lower in synonyms:
                for synonym in synonyms:
                    if synonym in user_input:
                        return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité entre deux textes
        
        Args:
            text1: Premier texte
            text2: Second texte
        
        Returns:
            Score de similarité (0.0 à 1.0)
        """
        # Normaliser les textes
        text1 = self._normalize_text(text1)
        text2 = self._normalize_text(text2)
        
        # 1. Similarité de séquence (difflib)
        seq_ratio = difflib.SequenceMatcher(None, text1, text2).ratio()
        
        # 2. Similarité de mots
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            word_ratio = 0.0
        else:
            common = words1.intersection(words2)
            word_ratio = len(common) / max(len(words1), len(words2))
        
        # 3. Similarité de début (prefix)
        prefix_len = 0
        min_len = min(len(text1), len(text2))
        
        for i in range(min_len):
            if text1[i] == text2[i]:
                prefix_len += 1
            else:
                break
        
        prefix_ratio = prefix_len / min_len if min_len > 0 else 0
        
        # Score combiné (pondéré)
        total_score = (seq_ratio * 0.5) + (word_ratio * 0.3) + (prefix_ratio * 0.2)
        
        return total_score
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalise le texte pour la comparaison
        
        Args:
            text: Texte à normaliser
        
        Returns:
            Texte normalisé
        """
        # Convertir en minuscules
        text = text.lower()
        
        # Supprimer la ponctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Supprimer les articles courants
        articles = ['le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'à']
        words = text.split()
        words = [w for w in words if w not in articles]
        
        return ' '.join(words)
    
    def extract_parameters(self, user_input: str, command: str) -> Dict[str, str]:
        """
        Extrait les paramètres de la commande
        
        Args:
            user_input: Entrée utilisateur
            command: Commande reconnue
        
        Returns:
            Paramètres extraits
        """
        params = {}
        
        # Normaliser les textes
        user_norm = self._normalize_text(user_input)
        cmd_norm = self._normalize_text(command)
        
        # Séparer les mots
        user_words = user_norm.split()
        cmd_words = cmd_norm.split()
        
        # Trouver les mots supplémentaires dans l'entrée utilisateur
        param_words = [w for w in user_words if w not in cmd_words]
        
        if param_words:
            params['query'] = ' '.join(param_words)
        
        # Extraire les nombres
        numbers = re.findall(r'\d+', user_input)
        if numbers:
            params['numbers'] = numbers
        
        # Extraire les URLs
        urls = re.findall(r'https?://\S+', user_input)
        if urls:
            params['urls'] = urls
        
        # Extraire les noms de fichiers avec extension
        files = re.findall(r'\b\w+\.(?:exe|lnk|txt|pdf|docx?|xlsx?|jpg|png|mp3|mp4)\b', user_input, re.IGNORECASE)
        if files:
            params['files'] = files
        
        return params
    
    def suggest_corrections(self, user_input: str, commands: List[str], max_suggestions: int = 3) -> List[str]:
        """
        Suggère des corrections pour l'entrée utilisateur
        
        Args:
            user_input: Entrée utilisateur
            commands: Commandes disponibles
            max_suggestions: Nombre maximum de suggestions
        
        Returns:
            Liste des suggestions
        """
        suggestions = []
        
        for command in commands:
            score = self._calculate_similarity(user_input, command)
            
            if score >= self.threshold * 0.8:  # Seuil plus bas pour suggestions
                suggestions.append((command, score))
        
        # Trier par score décroissant
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        # Retourner seulement les commandes
        return [s[0] for s in suggestions[:max_suggestions]]
    
    def learn_from_correction(self, user_input: str, correct_command: str):
        """
        Apprend d'une correction (pour améliorer les synonymes)
        
        Args:
            user_input: Entrée originale erronée
            correct_command: Commande correcte
        """
        # Extraire les mots clés de l'entrée utilisateur
        user_words = set(self._normalize_text(user_input).split())
        cmd_words = set(self._normalize_text(correct_command).split())
        
        # Ajouter les mots uniques de l'utilisateur comme synonymes potentiels
        unique_words = user_words - cmd_words
        
        if unique_words and cmd_words:
            for word in unique_words:
                if len(word) > 2:  # Ignorer les mots trop courts
                    cmd = next(iter(cmd_words))  # Prendre le premier mot de la commande
                    if cmd in self.synonyms:
                        if word not in self.synonyms[cmd]:
                            self.synonyms[cmd].append(word)
                    else:
                        self.synonyms[cmd] = [word]

# Test du module
if __name__ == "__main__":
    matcher = FuzzyMatcher(threshold=0.5)
    
    # Commandes disponibles
    commands = [
        "ouvrir chrome",
        "fermer application",
        "météo paris",
        "actualités technologie",
        "traduire français anglais",
        "créer note",
        "calculatrice",
        "volume augmenter",
        "musique play"
    ]
    
    # Tests
    test_cases = [
        ("ouvre chrome", "ouvrir chrome"),
        ("stop app", "fermer application"),
        ("température paris", "météo paris"),
        ("news tech", "actualités technologie"),
        ("translate french to english", "traduire français anglais"),
        ("nouvelle note", "créer note"),
        ("calc", "calculatrice"),
        ("augmente son", "volume augmenter"),
        ("jouer musique", "musique play")
    ]
    
    print("🔍 Test Fuzzy Matcher\n")
    
    for user_input, expected in test_cases:
        result = matcher.match_command(user_input, commands)
        
        if result:
            matched, score = result
            status = "✓" if matched == expected else "✗"
            print(f"{status} '{user_input}' → '{matched}' (score: {score:.2f})")
            
            # Extraire les paramètres
            params = matcher.extract_parameters(user_input, matched)
            if params:
                print(f"   Paramètres: {params}")
        else:
            print(f"✗ '{user_input}' → Aucune correspondance")
    
    # Test suggestions
    print("\n💡 Suggestions pour 'ouvre chrom':")
    suggestions = matcher.suggest_corrections("ouvre chrom", commands)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")