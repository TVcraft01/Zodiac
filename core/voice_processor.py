"""
Module avancé de traitement vocal
"""

import re
from difflib import SequenceMatcher

class VoiceCommandProcessor:
    def __init__(self):
        self.command_patterns = self._load_patterns()
        self.context = {}
        
    def _load_patterns(self):
        """Charge les patterns de commandes"""
        return {
            # Applications
            r'(ouvre|lance|start|run|execute|démarre)\s+(.+)$': self._parse_app_command,
            
            # Média
            r'(musique|chanson|son)\s+(suivant|précédent|pause|play|stop|continue)$': self._parse_media_command,
            r'(volume)\s+(plus|moins|augmente|baisse|mute|silence)$': self._parse_volume_command,
            
            # Système
            r'(cpu|processeur|mémoire|ram|batterie|système)$': self._parse_system_command,
            r'(éteins|allume)\s+(écran|moniteur)$': self._parse_screen_command,
            
            # Web
            r'(recherche|cherche|google|youtube)\s+(.+)$': self._parse_search_command,
            
            # Fichiers
            r'(ouvre)\s+(explorateur|documents|téléchargements|dossier)$': self._parse_file_command,
            
            # Temps
            r'(quelle|donne).*(heure|date)$': self._parse_time_command,
            
            # Navigation
            r'(page)\s+(précédent|suivant|actualise|stop)$': self._parse_nav_command,
        }
        
    def parse_command(self, text):
        """Parse une commande textuelle"""
        text = text.lower().strip()
        
        # Supprimer "zodiac" si présent
        if text.startswith('zodiac'):
            text = text[6:].strip()
            
        # Chercher un pattern correspondant
        for pattern, parser in self.command_patterns.items():
            match = re.match(pattern, text)
            if match:
                return parser(match)
                
        # Si aucun pattern, essayer la correspondance approximative
        return self._fuzzy_match(text)
        
    def _parse_app_command(self, match):
        """Parse une commande d'application"""
        action, app = match.groups()
        return {
            'type': 'app',
            'action': 'launch',
            'target': app,
            'confidence': 0.9
        }
        
    def _parse_media_command(self, match):
        """Parse une commande média"""
        _, action = match.groups()
        action_map = {
            'suivant': 'next',
            'précédent': 'previous',
            'pause': 'pause',
            'play': 'play',
            'stop': 'stop',
            'continue': 'resume'
        }
        return {
            'type': 'media',
            'action': action_map.get(action, action),
            'confidence': 0.95
        }
        
    def _parse_volume_command(self, match):
        """Parse une commande de volume"""
        _, direction = match.groups()
        action_map = {
            'plus': 'up',
            'augmente': 'up',
            'moins': 'down',
            'baisse': 'down',
            'mute': 'mute',
            'silence': 'mute'
        }
        return {
            'type': 'volume',
            'action': action_map.get(direction, direction),
            'confidence': 0.95
        }
        
    def _fuzzy_match(self, text):
        """Correspondance approximative pour commandes mal reconnues"""
        common_commands = {
            'ouvre chrome': {'type': 'app', 'target': 'chrome', 'action': 'launch'},
            'musique suivante': {'type': 'media', 'action': 'next'},
            'pause musique': {'type': 'media', 'action': 'pause'},
            'volume plus': {'type': 'volume', 'action': 'up'},
            'quelle heure': {'type': 'time', 'action': 'hour'},
            'état système': {'type': 'system', 'action': 'status'},
        }
        
        best_match = None
        best_score = 0
        
        for cmd, result in common_commands.items():
            score = SequenceMatcher(None, text, cmd).ratio()
            if score > best_score and score > 0.6:  # Seuil de 60%
                best_score = score
                best_match = result
                best_match['confidence'] = score
                
        if best_match:
            return best_match
            
        return {
            'type': 'unknown',
            'text': text,
            'confidence': 0.0
        }