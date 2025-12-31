"""
Module 17: Quick Wiki
Récupération rapide de résumés depuis Wikipédia
"""

import requests
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict
import urllib.parse

class WikiParser:
    def __init__(self, lang: str = "fr"):
        """
        Initialise le parser Wikipédia
        
        Args:
            lang: Langue (fr, en, es, etc.)
        """
        self.lang = lang
        self.base_url = f"https://{lang}.wikipedia.org"
        self.headers = {
            'User-Agent': 'ZodiacAI/1.0 (https://github.com/zodiac-ai)'
        }
    
    def get_summary(self, query: str, sentences: int = 3) -> Optional[Dict]:
        """
        Récupère un résumé Wikipédia
        
        Args:
            query: Terme à rechercher
            sentences: Nombre de phrases dans le résumé
        
        Returns:
            Dictionnaire avec les informations ou None
        """
        try:
            # 1. Rechercher la page
            search_url = f"{self.base_url}/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'utf8': 1
            }
            
            response = requests.get(search_url, params=params, 
                                  headers=self.headers, timeout=10)
            data = response.json()
            
            if not data.get('query', {}).get('search'):
                return None
            
            # Prendre le premier résultat
            first_result = data['query']['search'][0]
            page_title = first_result['title']
            
            # 2. Récupérer le contenu
            content_url = f"{self.base_url}/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': page_title,
                'prop': 'extracts|info',
                'exsentences': sentences,
                'exintro': 1,
                'explaintext': 1,
                'inprop': 'url'
            }
            
            response = requests.get(content_url, params=params,
                                  headers=self.headers, timeout=10)
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            if not pages:
                return None
            
            page_id = list(pages.keys())[0]
            page_data = pages[page_id]
            
            if 'missing' in page_data:
                return None
            
            # Extraire le résumé
            extract = page_data.get('extract', '')
            if not extract:
                return None
            
            # Nettoyer le texte
            extract = self.clean_text(extract)
            
            # Formater la réponse
            result = {
                'title': page_data.get('title', ''),
                'summary': extract,
                'url': page_data.get('fullurl', ''),
                'pageid': page_id,
                'length': len(extract),
                'sentences': sentences
            }
            
            return result
            
        except Exception as e:
            print(f"✗ Erreur Wikipédia: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """
        Nettoie le texte des balises et caractères spéciaux
        
        Args:
            text: Texte à nettoyer
        
        Returns:
            Texte nettoyé
        """
        # Supprimer les références [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        # Supprimer les sauts de ligne multiples
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Nettoyer le début (supprimer "Pour les articles homonymes", etc.)
        unwanted_patterns = [
            r'Pour les articles homonymes.*?\n',
            r'Pour l\'article homonyme.*?\n',
            r'Pour les autres significations.*?\n',
            r'\(homonymie\).*?\n'
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def search_multiple(self, queries: list, sentences: int = 2) -> Dict:
        """
        Recherche plusieurs termes
        
        Args:
            queries: Liste des termes à rechercher
            sentences: Nombre de phrases par résumé
        
        Returns:
            Dictionnaire des résultats
        """
        results = {}
        
        for query in queries:
            summary = self.get_summary(query, sentences)
            if summary:
                results[query] = summary
            else:
                results[query] = {"error": "Non trouvé"}
        
        return results
    
    def get_random_article(self) -> Optional[Dict]:
        """
        Récupère un article aléatoire
        
        Returns:
            Article aléatoire ou None
        """
        try:
            url = f"{self.base_url}/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'random',
                'rnnamespace': 0,  # Articles principaux seulement
                'rnlimit': 1
            }
            
            response = requests.get(url, params=params, 
                                  headers=self.headers, timeout=10)
            data = response.json()
            
            random_article = data['query']['random'][0]
            title = random_article['title']
            
            # Récupérer le résumé
            return self.get_summary(title, sentences=2)
            
        except Exception as e:
            print(f"✗ Erreur article aléatoire: {e}")
            return None
    
    def format_summary(self, data: Dict) -> str:
        """
        Formate le résumé pour l'affichage
        
        Args:
            data: Données du résumé
        
        Returns:
            Chaîne formatée
        """
        if not data or 'error' in data:
            return "❌ Aucune information trouvée sur Wikipédia."
        
        formatted = f"📚 **{data['title']}**\n\n"
        formatted += f"{data['summary']}\n\n"
        formatted += f"🔗 Source: {data['url']}\n"
        formatted += f"📏 Longueur: {data['length']} caractères"
        
        return formatted

# Test du module
if __name__ == "__main__":
    wiki = WikiParser(lang="fr")
    
    # Test de résumé
    print("🔍 Test Wikipedia Parser\n")
    
    # Recherche simple
    query = "Intelligence artificielle"
    result = wiki.get_summary(query, sentences=4)
    
    if result:
        print(wiki.format_summary(result))
    else:
        print(f"✗ Aucun résultat pour '{query}'")
    
    # Test article aléatoire
    print("\n🎲 Article aléatoire:")
    random_article = wiki.get_random_article()
    if random_article:
        print(f"  Titre: {random_article['title']}")
        print(f"  Résumé: {random_article['summary'][:100]}...")