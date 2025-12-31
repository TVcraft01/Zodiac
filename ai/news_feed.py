"""
Module 19: News Feed
Récupération des actualités technologiques
"""

import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os

class NewsFeed:
    def __init__(self, cache_dir: str = "data/news"):
        """
        Initialise le flux d'actualités
        
        Args:
            cache_dir: Répertoire de cache
        """
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "news_cache.json")
        self.cache_timeout = 1800  # 30 minutes
        
        # Sources RSS de tech
        self.feeds = {
            "techcrunch": "https://techcrunch.com/feed/",
            "theverge": "https://www.theverge.com/tech/rss/index.xml",
            "wired": "https://www.wired.com/feed/rss",
            "arstechnica": "http://feeds.arstechnica.com/arstechnica/index",
            "hackernews": "https://news.ycombinator.com/rss",
            "github": "https://github.com/trending.atom",
            "python": "https://www.python.org/blogs/rss/",
            "french_tech": "https://www.frenchweb.fr/feed/"
        }
        
        # Créer le dossier de cache
        os.makedirs(cache_dir, exist_ok=True)
    
    def fetch_news(self, source: str = "all", limit: int = 10) -> List[Dict]:
        """
        Récupère les actualités depuis les feeds
        
        Args:
            source: Source spécifique ou 'all'
            limit: Nombre maximum d'articles
        
        Returns:
            Liste des articles
        """
        # Vérifier le cache
        cached_data = self.load_from_cache(source, limit)
        if cached_data:
            return cached_data
        
        articles = []
        
        if source == "all":
            # Récupérer de toutes les sources
            for feed_name, feed_url in self.feeds.items():
                try:
                    feed_articles = self.parse_feed(feed_url, feed_name)
                    articles.extend(feed_articles)
                    
                    if len(articles) >= limit * 2:  # Buffer pour le tri
                        break
                except Exception as e:
                    print(f"✗ Erreur feed {feed_name}: {e}")
        elif source in self.feeds:
            # Source spécifique
            articles = self.parse_feed(self.feeds[source], source)
        else:
            # Recherche de nouvelles via NewsAPI (si clé disponible)
            articles = self.search_news(source)
        
        # Trier par date et limiter
        articles.sort(key=lambda x: x.get('published_parsed', datetime.now()), 
                     reverse=True)
        articles = articles[:limit]
        
        # Mettre en cache
        self.save_to_cache(source, limit, articles)
        
        return articles
    
    def parse_feed(self, feed_url: str, source: str) -> List[Dict]:
        """
        Parse un flux RSS/Atom
        
        Args:
            feed_url: URL du flux
            source: Nom de la source
        
        Returns:
            Liste des articles
        """
        articles = []
        
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:15]:  # Limiter par flux
                article = {
                    'title': entry.get('title', 'Sans titre'),
                    'link': entry.get('link', ''),
                    'summary': self.clean_summary(entry.get('summary', '')),
                    'published': entry.get('published', ''),
                    'published_parsed': entry.get('published_parsed', datetime.now()),
                    'source': source,
                    'author': entry.get('author', ''),
                    'categories': entry.get('tags', [])[:3]
                }
                
                # Nettoyer et formater
                if len(article['summary']) > 300:
                    article['summary'] = article['summary'][:297] + '...'
                
                articles.append(article)
        
        except Exception as e:
            print(f"✗ Erreur parsing {source}: {e}")
        
        return articles
    
    def search_news(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Recherche d'actualités via NewsAPI (nécessite clé API)
        
        Args:
            query: Termes de recherche
            limit: Nombre maximum d'articles
        
        Returns:
            Liste des articles
        """
        articles = []
        api_key = os.getenv('NEWSAPI_KEY', '')
        
        if not api_key:
            # Fallback: utiliser RSS de Google News
            return self.google_news_fallback(query, limit)
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': api_key,
                'pageSize': limit,
                'language': 'fr',
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'ok':
                for item in data['articles'][:limit]:
                    article = {
                        'title': item.get('title', ''),
                        'link': item.get('url', ''),
                        'summary': self.clean_summary(item.get('description', '')),
                        'published': item.get('publishedAt', ''),
                        'source': item.get('source', {}).get('name', ''),
                        'author': item.get('author', ''),
                        'image': item.get('urlToImage', '')
                    }
                    articles.append(article)
        
        except Exception as e:
            print(f"✗ Erreur NewsAPI: {e}")
            return self.google_news_fallback(query, limit)
        
        return articles
    
    def google_news_fallback(self, query: str, limit: int) -> List[Dict]:
        """Fallback via Google News RSS"""
        articles = []
        
        try:
            # Google News RSS (format obsolète mais fonctionnel)
            encoded_query = requests.utils.quote(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=fr&gl=FR&ceid=FR:fr"
            
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:limit]:
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': self.clean_summary(entry.get('summary', '')),
                    'published': entry.get('published', ''),
                    'source': 'Google News',
                    'author': '',
                    'categories': []
                }
                articles.append(article)
        
        except Exception as e:
            print(f"✗ Erreur Google News: {e}")
        
        return articles
    
    def clean_summary(self, summary: str) -> str:
        """
        Nettoie le résumé des balises HTML
        
        Args:
            summary: Résumé à nettoyer
        
        Returns:
            Résumé nettoyé
        """
        if not summary:
            return ""
        
        # Supprimer les balises HTML
        import re
        summary = re.sub(r'<[^>]+>', '', summary)
        
        # Supprimer les caractères de contrôle
        summary = summary.replace('\n', ' ').replace('\r', ' ')
        
        # Supprimer les espaces multiples
        summary = re.sub(r'\s+', ' ', summary).strip()
        
        return summary
    
    def get_trending_tech(self) -> List[Dict]:
        """
        Récupère les tendances tech
        
        Returns:
            Articles tendance
        """
        # Combiner plusieurs sources pour les tendances
        sources = ['hackernews', 'github', 'techcrunch']
        all_articles = []
        
        for source in sources:
            articles = self.fetch_news(source, limit=5)
            all_articles.extend(articles)
        
        # Trier par "popularité" (simulée)
        all_articles.sort(key=lambda x: len(x.get('title', '')), reverse=True)
        
        return all_articles[:10]
    
    def format_articles(self, articles: List[Dict], detailed: bool = False) -> str:
        """
        Formate les articles pour l'affichage
        
        Args:
            articles: Liste des articles
            detailed: Affichage détaillé ou sommaire
        
        Returns:
            Chaîne formatée
        """
        if not articles:
            return "📰 Aucune actualité disponible."
        
        formatted = f"📰 **{len(articles)} actualités**\n\n"
        
        for i, article in enumerate(articles, 1):
            formatted += f"**{i}. {article['title']}**\n"
            
            if detailed:
                formatted += f"   📝 {article['summary'][:200]}...\n"
            
            formatted += f"   📰 Source: {article.get('source', 'Inconnue')}\n"
            formatted += f"   📅 {article.get('published', 'Date inconnue')}\n"
            
            if article.get('link'):
                formatted += f"   🔗 Lien: {article['link']}\n"
            
            formatted += "\n"
        
        return formatted
    
    def load_from_cache(self, source: str, limit: int) -> Optional[List[Dict]]:
        """Charge depuis le cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cache_key = f"{source}_{limit}"
                
                if cache_key in cache_data:
                    timestamp, articles = cache_data[cache_key]
                    cache_time = datetime.fromisoformat(timestamp)
                    
                    if (datetime.now() - cache_time).seconds < self.cache_timeout:
                        print(f"✓ Actualités chargées depuis le cache ({source})")
                        return articles
        
        except Exception as e:
            print(f"✗ Erreur cache: {e}")
        
        return None
    
    def save_to_cache(self, source: str, limit: int, articles: List[Dict]):
        """Sauvegarde dans le cache"""
        try:
            cache_data = {}
            
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
            
            cache_key = f"{source}_{limit}"
            cache_data[cache_key] = (datetime.now().isoformat(), articles)
            
            # Limiter la taille du cache
            if len(cache_data) > 20:
                # Garder les 20 entrées les plus récentes
                cache_data = dict(list(cache_data.items())[-20:])
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"✗ Erreur sauvegarde cache: {e}")

# Test du module
if __name__ == "__main__":
    news = NewsFeed()
    
    print("📰 Test du flux d'actualités\n")
    
    # Test 1: Toutes les sources
    print("1. Toutes les sources (tech):")
    articles = news.fetch_news("all", limit=5)
    
    if articles:
        print(news.format_articles(articles, detailed=True))
    else:
        print("❌ Aucun article trouvé")
    
    # Test 2: Source spécifique
    print("\n2. Source spécifique (techcrunch):")
    articles = news.fetch_news("techcrunch", limit=3)
    
    for article in articles:
        print(f"  • {article['title'][:60]}...")
    
    # Test 3: Tendances
    print("\n3. Tendances tech:")
    trending = news.get_trending_tech()
    
    for i, article in enumerate(trending[:3], 1):
        print(f"  {i}. {article['title'][:50]}...")