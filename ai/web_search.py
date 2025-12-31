"""
Module 16: Web Search Agent
Recherche web via DuckDuckGo et autres moteurs
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
from typing import List, Dict, Optional
import time

class WebSearchAgent:
    def __init__(self, max_results: int = 5):
        """
        Initialise l'agent de recherche web
        
        Args:
            max_results: Nombre maximum de résultats
        """
        self.max_results = max_results
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Moteurs de recherche disponibles
        self.search_engines = {
            'duckduckgo': self.search_duckduckgo,
            'google': self.search_google,
            'bing': self.search_bing
        }
    
    def search(self, query: str, engine: str = 'duckduckgo') -> List[Dict]:
        """
        Effectue une recherche web
        
        Args:
            query: Termes de recherche
            engine: Moteur de recherche ('duckduckgo', 'google', 'bing')
        
        Returns:
            Liste des résultats
        """
        if engine not in self.search_engines:
            engine = 'duckduckgo'
        
        print(f"🔍 Recherche: '{query}' sur {engine}")
        
        try:
            results = self.search_engines[engine](query)
            return results[:self.max_results]
        except Exception as e:
            print(f"✗ Erreur recherche {engine}: {e}")
            return self.search_fallback(query)
    
    def search_duckduckgo(self, query: str) -> List[Dict]:
        """Recherche via DuckDuckGo (sans API)"""
        results = []
        
        try:
            # Encoder la requête
            encoded_query = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            # Récupérer la page
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parser les résultats
            result_elements = soup.find_all('a', class_='result__url')
            
            for i, element in enumerate(result_elements[:self.max_results]):
                title_element = element.find_next('a', class_='result__title')
                snippet_element = element.find_next('a', class_='result__snippet')
                
                if title_element and snippet_element:
                    result = {
                        'title': title_element.text.strip(),
                        'url': element.text.strip(),
                        'snippet': snippet_element.text.strip()[:200],
                        'rank': i + 1
                    }
                    results.append(result)
            
        except Exception as e:
            print(f"✗ Erreur DuckDuckGo: {e}")
        
        return results
    
    def search_google(self, query: str) -> List[Dict]:
        """Recherche via Google (scraping simple)"""
        results = []
        
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Chercher les résultats (structure Google)
            for g in soup.find_all('div', class_='g'):
                title_element = g.find('h3')
                link_element = g.find('a')
                snippet_element = g.find('div', class_='VwiC3b')
                
                if title_element and link_element:
                    result = {
                        'title': title_element.text,
                        'url': link_element.get('href', ''),
                        'snippet': snippet_element.text[:200] if snippet_element else '',
                        'rank': len(results) + 1
                    }
                    
                    if result['url'].startswith('/url?q='):
                        result['url'] = result['url'].split('/url?q=')[1].split('&')[0]
                    
                    results.append(result)
                    
                    if len(results) >= self.max_results:
                        break
        
        except Exception as e:
            print(f"✗ Erreur Google: {e}")
        
        return results
    
    def search_bing(self, query: str) -> List[Dict]:
        """Recherche via Bing"""
        results = []
        
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.bing.com/search?q={encoded_query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parser les résultats Bing
            for li in soup.find_all('li', class_='b_algo'):
                title_element = li.find('h2')
                link_element = li.find('a')
                snippet_element = li.find('p')
                
                if title_element and link_element:
                    result = {
                        'title': title_element.text,
                        'url': link_element.get('href', ''),
                        'snippet': snippet_element.text[:200] if snippet_element else '',
                        'rank': len(results) + 1
                    }
                    results.append(result)
                    
                    if len(results) >= self.max_results:
                        break
        
        except Exception as e:
            print(f"✗ Erreur Bing: {e}")
        
        return results
    
    def search_fallback(self, query: str) -> List[Dict]:
        """Méthode de fallback si tout échoue"""
        return [
            {
                'title': 'Recherche web indisponible',
                'url': '',
                'snippet': f'Essayez une autre méthode pour "{query}"',
                'rank': 1
            }
        ]
    
    def get_quick_answer(self, query: str) -> Optional[str]:
        """
        Tente d'obtenir une réponse rapide (feature DuckDuckGo)
        
        Args:
            query: Question posée
        
        Returns:
            Réponse rapide ou None
        """
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get('AbstractText'):
                return data['AbstractText']
            elif data.get('Answer'):
                return data['Answer']
            elif data.get('Definition'):
                return data['Definition']
        
        except Exception as e:
            print(f"✗ Erreur réponse rapide: {e}")
        
        return None
    
    def format_results(self, results: List[Dict]) -> str:
        """
        Formate les résultats pour l'affichage
        
        Args:
            results: Liste des résultats
        
        Returns:
            Chaîne formatée
        """
        if not results:
            return "❌ Aucun résultat trouvé."
        
        formatted = "🔍 **Résultats de recherche:**\n\n"
        
        for result in results:
            formatted += f"**{result['rank']}. {result['title']}**\n"
            formatted += f"   📎 {result['url']}\n"
            formatted += f"   📝 {result['snippet']}\n\n"
        
        return formatted

# Test du module
if __name__ == "__main__":
    searcher = WebSearchAgent()
    
    # Test de recherche
    query = "intelligence artificielle 2024"
    results = searcher.search(query, engine='duckduckgo')
    
    print(f"Recherche: '{query}'")
    print(f"Nombre de résultats: {len(results)}")
    
    for result in results:
        print(f"\n{result['rank']}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Extrait: {result['snippet'][:100]}...")
    
    # Test réponse rapide
    quick_answer = searcher.get_quick_answer("Qui est Elon Musk ?")
    if quick_answer:
        print(f"\n💡 Réponse rapide: {quick_answer}")