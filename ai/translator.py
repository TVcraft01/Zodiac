"""
Module 20: Translation Engine
Traduction de texte via différents services
"""

import requests
import json
from typing import Optional, Dict, List
import os
from googletrans import Translator as GoogleTranslator

class TranslationEngine:
    def __init__(self, cache_dir: str = "data/translations"):
        """
        Initialise le moteur de traduction
        
        Args:
            cache_dir: Répertoire de cache
        """
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "translation_cache.json")
        
        # Services disponibles
        self.services = {
            'google': self.translate_google,
            'libre': self.translate_libre,
            'mymemory': self.translate_mymemory,
            'deepl': self.translate_deepl
        }
        
        # Langues supportées
        self.languages = {
            'fr': 'Français',
            'en': 'Anglais',
            'es': 'Espagnol',
            'de': 'Allemand',
            'it': 'Italien',
            'pt': 'Portugais',
            'ru': 'Russe',
            'zh': 'Chinois',
            'ja': 'Japonais',
            'ko': 'Coréen',
            'ar': 'Arabe',
            'nl': 'Néerlandais',
            'pl': 'Polonais'
        }
        
        # Créer le dossier de cache
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialiser le cache
        self.cache = self.load_cache()
    
    def translate(self, text: str, target_lang: str = 'en', 
                 source_lang: str = 'auto', service: str = 'google') -> Optional[Dict]:
        """
        Traduit un texte
        
        Args:
            text: Texte à traduire
            target_lang: Langue cible (code à 2 lettres)
            source_lang: Langue source ('auto' pour détection)
            service: Service à utiliser
        
        Returns:
            Dictionnaire avec la traduction ou None
        """
        if not text or not text.strip():
            return None
        
        # Vérifier le cache
        cache_key = f"{text[:100]}_{source_lang}_{target_lang}_{service}"
        if cache_key in self.cache:
            print("✓ Traduction chargée depuis le cache")
            return self.cache[cache_key]
        
        # Valider la langue cible
        if target_lang not in self.languages:
            target_lang = 'en'
        
        if service not in self.services:
            service = 'google'
        
        try:
            result = self.services[service](text, target_lang, source_lang)
            
            if result:
                # Mettre en cache
                self.cache[cache_key] = result
                self.save_cache()
            
            return result
            
        except Exception as e:
            print(f"✗ Erreur traduction ({service}): {e}")
            # Essayer avec un autre service
            return self.translate_fallback(text, target_lang, source_lang)
    
    def translate_google(self, text: str, target_lang: str, 
                        source_lang: str = 'auto') -> Optional[Dict]:
        """Utilise l'API Google Translate (googletrans)"""
        try:
            translator = GoogleTranslator()
            
            # Détecter la langue si 'auto'
            if source_lang == 'auto':
                detection = translator.detect(text)
                source_lang = detection.lang
                confidence = detection.confidence
            else:
                confidence = None
            
            # Traduire
            translation = translator.translate(text, dest=target_lang, src=source_lang)
            
            result = {
                'original': text,
                'translated': translation.text,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'source_lang_name': self.languages.get(source_lang, source_lang),
                'target_lang_name': self.languages.get(target_lang, target_lang),
                'pronunciation': translation.pronunciation,
                'confidence': confidence,
                'service': 'Google Translate'
            }
            
            return result
            
        except Exception as e:
            print(f"✗ Erreur Google Translate: {e}")
            return None
    
    def translate_libre(self, text: str, target_lang: str,
                       source_lang: str = 'auto') -> Optional[Dict]:
        """Utilise LibreTranslate (open source)"""
        try:
            # Essayer différents serveurs LibreTranslate
            servers = [
                'https://libretranslate.com',
                'https://translate.argosopentech.com',
                'https://translate.fortavia.eu'
            ]
            
            for server in servers:
                try:
                    url = f"{server}/translate"
                    data = {
                        'q': text,
                        'source': source_lang if source_lang != 'auto' else 'auto',
                        'target': target_lang,
                        'format': 'text'
                    }
                    
                    headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                    
                    response = requests.post(url, json=data, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        result_data = response.json()
                        
                        result = {
                            'original': text,
                            'translated': result_data.get('translatedText', ''),
                            'source_lang': result_data.get('detectedLanguage', {}).get('language', source_lang),
                            'target_lang': target_lang,
                            'confidence': result_data.get('detectedLanguage', {}).get('confidence', None),
                            'service': f'LibreTranslate ({server})'
                        }
                        
                        # Ajouter les noms de langues
                        result['source_lang_name'] = self.languages.get(
                            result['source_lang'], result['source_lang']
                        )
                        result['target_lang_name'] = self.languages.get(
                            target_lang, target_lang
                        )
                        
                        return result
                
                except Exception:
                    continue  # Essayer le serveur suivant
            
            return None
            
        except Exception as e:
            print(f"✗ Erreur LibreTranslate: {e}")
            return None
    
    def translate_mymemory(self, text: str, target_lang: str,
                          source_lang: str = 'auto') -> Optional[Dict]:
        """Utilise MyMemory Translation API"""
        try:
            if source_lang == 'auto':
                # Détection simple basée sur des caractères
                if any(c in text for c in 'àâäéèêëîïôöùûüç'):
                    source_lang = 'fr'
                elif any(c in text for c in 'áéíóúñ'):
                    source_lang = 'es'
                elif any(c in text for c in 'äöüß'):
                    source_lang = 'de'
                else:
                    source_lang = 'en'  # Par défaut
            
            url = "https://api.mymemory.translated.net/get"
            params = {
                'q': text,
                'langpair': f"{source_lang}|{target_lang}"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('responseStatus') == 200:
                result = {
                    'original': text,
                    'translated': data['responseData']['translatedText'],
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'source_lang_name': self.languages.get(source_lang, source_lang),
                    'target_lang_name': self.languages.get(target_lang, target_lang),
                    'match': data['responseData'].get('match', 0),
                    'service': 'MyMemory'
                }
                return result
        
        except Exception as e:
            print(f"✗ Erreur MyMemory: {e}")
        
        return None
    
    def translate_deepl(self, text: str, target_lang: str,
                       source_lang: str = 'auto') -> Optional[Dict]:
        """Utilise DeepL API (nécessite clé API)"""
        api_key = os.getenv('DEEPL_API_KEY', '')
        
        if not api_key:
            return None
        
        try:
            url = "https://api-free.deepl.com/v2/translate"
            data = {
                'text': [text],
                'target_lang': target_lang.upper()
            }
            
            if source_lang != 'auto':
                data['source_lang'] = source_lang.upper()
            
            headers = {
                'Authorization': f'DeepL-Auth-Key {api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            data = response.json()
            
            if 'translations' in data:
                result = {
                    'original': text,
                    'translated': data['translations'][0]['text'],
                    'source_lang': data['translations'][0].get('detected_source_language', source_lang).lower(),
                    'target_lang': target_lang,
                    'source_lang_name': self.languages.get(source_lang, source_lang),
                    'target_lang_name': self.languages.get(target_lang, target_lang),
                    'service': 'DeepL'
                }
                return result
        
        except Exception as e:
            print(f"✗ Erreur DeepL: {e}")
        
        return None
    
    def translate_fallback(self, text: str, target_lang: str,
                          source_lang: str = 'auto') -> Optional[Dict]:
        """Méthode de fallback si tout échoue"""
        # Simple traduction mot à mot (très basique)
        # Ceci est juste un placeholder
        return {
            'original': text,
            'translated': f"[Traduction] {text}",
            'source_lang': source_lang,
            'target_lang': target_lang,
            'service': 'Fallback',
            'note': 'Traduction de base - service temporairement indisponible'
        }
    
    def detect_language(self, text: str) -> Optional[Dict]:
        """
        Détecte la langue d'un texte
        
        Args:
            text: Texte à analyser
        
        Returns:
            Informations sur la langue détectée
        """
        try:
            translator = GoogleTranslator()
            detection = translator.detect(text)
            
            return {
                'language': detection.lang,
                'language_name': self.languages.get(detection.lang, detection.lang),
                'confidence': detection.confidence,
                'text_sample': text[:100]
            }
        except Exception as e:
            print(f"✗ Erreur détection langue: {e}")
            return None
    
    def translate_batch(self, texts: List[str], target_lang: str = 'en',
                       source_lang: str = 'auto') -> List[Optional[Dict]]:
        """
        Traduit plusieurs textes
        
        Args:
            texts: Liste des textes à traduire
            target_lang: Langue cible
            source_lang: Langue source
        
        Returns:
            Liste des traductions
        """
        results = []
        
        for text in texts:
            result = self.translate(text, target_lang, source_lang)
            results.append(result)
        
        return results
    
    def format_translation(self, translation: Dict) -> str:
        """
        Formate la traduction pour l'affichage
        
        Args:
            translation: Données de traduction
        
        Returns:
            Chaîne formatée
        """
        if not translation:
            return "❌ Échec de la traduction."
        
        formatted = f"🌐 **Traduction** ({translation.get('service', 'Inconnu')})\n\n"
        formatted += f"📤 **Source ({translation.get('source_lang_name', '?')}):**\n"
        formatted += f"{translation['original']}\n\n"
        formatted += f"📥 **Cible ({translation.get('target_lang_name', '?')}):**\n"
        formatted += f"{translation['translated']}\n"
        
        if translation.get('pronunciation'):
            formatted += f"🔊 **Prononciation:** {translation['pronunciation']}\n"
        
        if translation.get('confidence'):
            formatted += f"📊 **Confiance:** {translation['confidence']:.1%}\n"
        
        if translation.get('match'):
            formatted += f"🎯 **Correspondance:** {translation['match']}%\n"
        
        return formatted
    
    def get_supported_languages(self) -> Dict:
        """Retourne les langues supportées"""
        return self.languages
    
    def load_cache(self) -> Dict:
        """Charge le cache depuis le fichier"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"✗ Erreur chargement cache: {e}")
        
        return {}
    
    def save_cache(self):
        """Sauvegarde le cache dans le fichier"""
        try:
            # Limiter la taille du cache
            if len(self.cache) > 1000:
                # Garder les 1000 entrées les plus récentes
                items = list(self.cache.items())[-1000:]
                self.cache = dict(items)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"✗ Erreur sauvegarde cache: {e}")

# Test du module
if __name__ == "__main__":
    translator = TranslationEngine()
    
    print("🌐 Test du moteur de traduction\n")
    
    # Test 1: Traduction simple
    print("1. Traduction Français -> Anglais:")
    text_fr = "Bonjour, comment allez-vous aujourd'hui ?"
    result = translator.translate(text_fr, target_lang='en', source_lang='fr')
    
    if result:
        print(translator.format_translation(result))
    else:
        print("❌ Échec de la traduction")
    
    # Test 2: Détection automatique
    print("\n2. Détection automatique:")
    texts = [
        "Hello, how are you?",
        "Hola, ¿cómo estás?",
        "Bonjour, comment ça va ?",
        "Hallo, wie geht's?"
    ]
    
    for text in texts:
        detection = translator.detect_language(text)
        if detection:
            print(f"  '{text[:20]}...' → {detection['language_name']} ({detection['confidence']:.0%})")
    
    # Test 3: Traduction batch
    print("\n3. Traduction multiple:")
    texts_to_translate = [
        "Merci beaucoup",
        "Au revoir",
        "À bientôt"
    ]
    
    results = translator.translate_batch(texts_to_translate, target_lang='es')
    
    for i, (original, result) in enumerate(zip(texts_to_translate, results), 1):
        if result:
            print(f"  {i}. {original} → {result['translated']}")
    
    # Test 4: Langues supportées
    print("\n4. Langues supportées:")
    langs = translator.get_supported_languages()
    for code, name in list(langs.items())[:5]:
        print(f"  {code}: {name}")
    print(f"  ... et {len(langs) - 5} autres")