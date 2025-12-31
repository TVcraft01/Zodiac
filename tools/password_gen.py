"""
Générateur de mots de passe
"""

import random
import string

class PasswordGenerator:
    def __init__(self):
        self.levels = {
            'faible': (8, False),
            'moyen': (12, True),
            'fort': (16, True),
            'très fort': (20, True)
        }
    
    def generate(self, level='moyen'):
        """Génère un mot de passe"""
        if level not in self.levels:
            level = 'moyen'
        
        length, use_symbols = self.levels[level]
        
        chars = string.ascii_letters + string.digits
        if use_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        password = ''.join(random.choice(chars) for _ in range(length))
        
        return {
            'password': password,
            'length': len(password),
            'level': level,
            'has_symbols': use_symbols
        }
    
    def generate_custom(self, length=12, use_uppercase=True, 
                       use_lowercase=True, use_digits=True, 
                       use_symbols=True):
        """Génère un mot de passe personnalisé"""
        chars = ""
        
        if use_lowercase:
            chars += string.ascii_lowercase
        if use_uppercase:
            chars += string.ascii_uppercase
        if use_digits:
            chars += string.digits
        if use_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        if not chars:
            chars = string.ascii_letters + string.digits
        
        password = ''.join(random.choice(chars) for _ in range(length))
        
        return {
            'password': password,
            'length': len(password),
            'uppercase': use_uppercase,
            'lowercase': use_lowercase,
            'digits': use_digits,
            'symbols': use_symbols
        }

# Test
if __name__ == "__main__":
    gen = PasswordGenerator()
    print("Mot de passe moyen:", gen.generate('moyen')['password'])
    print("Mot de passe fort:", gen.generate('fort')['password'])
    print("Personnalisé:", gen.generate_custom(10, True, True, True, False)['password'])