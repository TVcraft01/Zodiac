"""
Journal des actions effectuées par Zodiac
"""

import json
from datetime import datetime
from pathlib import Path

class ActionLogger:
    def __init__(self):
        self.log_file = Path('data/actions.json')
        self.log_file.parent.mkdir(exist_ok=True)
        self.actions = self._load_actions()
        
    def _load_actions(self):
        """Charge les actions existantes"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
        
    def log_action(self, command, result, success=True):
        """Log une action"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'result': result,
            'success': success,
            'type': self._detect_type(command)
        }
        
        self.actions.append(action)
        
        # Garder seulement les 100 dernières actions
        if len(self.actions) > 100:
            self.actions = self.actions[-100:]
            
        self._save_actions()
        
    def _detect_type(self, command):
        """Détecte le type d'action"""
        cmd_lower = command.lower()
        
        if any(word in cmd_lower for word in ['ouvre', 'lance', 'start']):
            return 'application'
        elif any(word in cmd_lower for word in ['musique', 'volume', 'play', 'pause']):
            return 'media'
        elif any(word in cmd_lower for word in ['recherche', 'cherche', 'google']):
            return 'web'
        elif any(word in cmd_lower for word in ['cpu', 'mémoire', 'système']):
            return 'system'
        elif any(word in cmd_lower for word in ['fichier', 'dossier', 'document']):
            return 'files'
        else:
            return 'other'
            
    def _save_actions(self):
        """Sauvegarde les actions"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.actions, f, indent=2, ensure_ascii=False)
        except:
            pass
            
    def get_recent_actions(self, limit=10):
        """Récupère les actions récentes"""
        return self.actions[-limit:]
        
    def get_stats(self):
        """Récupère les statistiques"""
        if not self.actions:
            return {}
            
        total = len(self.actions)
        successful = sum(1 for a in self.actions if a.get('success', False))
        
        # Comptage par type
        types = {}
        for action in self.actions:
            t = action.get('type', 'other')
            types[t] = types.get(t, 0) + 1
            
        return {
            'total_actions': total,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'by_type': types,
            'last_action': self.actions[-1] if self.actions else None
        }