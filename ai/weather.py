"""
Module 18: Weather Module
Récupération de la météo via différentes APIs
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
import os

class WeatherModule:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le module météo
        
        Args:
            api_key: Clé API OpenWeatherMap (optionnelle)
        """
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY', '')
        self.cache = {}
        self.cache_timeout = 1800  # 30 minutes en secondes
        
        # Fournisseurs disponibles
        self.providers = {
            'openweather': self.get_openweather,
            'wttr': self.get_wttr,
            'weatherstack': self.get_weatherstack
        }
    
    def get_weather(self, location: str, provider: str = 'openweather') -> Optional[Dict]:
        """
        Récupère la météo pour un lieu
        
        Args:
            location: Ville ou coordonnées
            provider: Fournisseur ('openweather', 'wttr', 'weatherstack')
        
        Returns:
            Données météo ou None
        """
        # Vérifier le cache
        cache_key = f"{location}_{provider}"
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_timeout:
                print("✓ Météo chargée depuis le cache")
                return cached_data
        
        if provider not in self.providers:
            provider = 'openweather' if self.api_key else 'wttr'
        
        try:
            data = self.providers[provider](location)
            if data:
                self.cache[cache_key] = (datetime.now(), data)
            return data
        except Exception as e:
            print(f"✗ Erreur météo ({provider}): {e}")
            return None
    
    def get_openweather(self, location: str) -> Optional[Dict]:
        """Utilise l'API OpenWeatherMap"""
        if not self.api_key:
            return None
        
        try:
            # D'abord géocodage
            geo_url = "http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {
                'q': location,
                'limit': 1,
                'appid': self.api_key
            }
            
            geo_response = requests.get(geo_url, params=geo_params, timeout=10)
            geo_data = geo_response.json()
            
            if not geo_data:
                return None
            
            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']
            city = geo_data[0]['name']
            country = geo_data[0].get('country', '')
            
            # Récupérer la météo
            weather_url = "https://api.openweathermap.org/data/2.5/weather"
            weather_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'fr'
            }
            
            response = requests.get(weather_url, params=weather_params, timeout=10)
            data = response.json()
            
            # Formater les données
            weather_data = {
                'location': f"{city}, {country}",
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # m/s to km/h
                'wind_deg': data['wind'].get('deg', 0),
                'clouds': data['clouds']['all'],
                'visibility': data.get('visibility', 0),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                'provider': 'OpenWeatherMap'
            }
            
            return weather_data
            
        except Exception as e:
            print(f"✗ Erreur OpenWeather: {e}")
            return None
    
    def get_wttr(self, location: str) -> Optional[Dict]:
        """Utilise wttr.in (gratuit, sans API)"""
        try:
            url = f"https://wttr.in/{requests.utils.quote(location)}?format=j1&lang=fr"
            response = requests.get(url, headers={'User-Agent': 'curl'}, timeout=10)
            data = response.json()
            
            current = data['current_condition'][0]
            area = data['nearest_area'][0]
            
            weather_data = {
                'location': f"{area['areaName'][0]['value']}, {area['country'][0]['value']}",
                'temperature': int(current['temp_C']),
                'feels_like': int(current['FeelsLikeC']),
                'humidity': int(current['humidity']),
                'pressure': int(current['pressure']),
                'description': current['weatherDesc'][0]['value'],
                'icon': self.map_wttr_icon(current['weatherCode']),
                'wind_speed': int(current['windspeedKmph']),
                'wind_deg': int(current['winddirDegree']),
                'clouds': int(current['cloudcover']),
                'visibility': int(current['visibility']),
                'precipitation': float(current['precipMM']),
                'uv_index': int(current['uvIndex']),
                'provider': 'wttr.in'
            }
            
            # Ajouter les prévisions si disponibles
            if 'weather' in data and len(data['weather']) > 0:
                tomorrow = data['weather'][1]
                weather_data['forecast'] = {
                    'date': tomorrow['date'],
                    'max_temp': int(tomorrow['maxtempC']),
                    'min_temp': int(tomorrow['mintempC']),
                    'condition': tomorrow['hourly'][4]['weatherDesc'][0]['value']
                }
            
            return weather_data
            
        except Exception as e:
            print(f"✗ Erreur wttr.in: {e}")
            return None
    
    def get_weatherstack(self, location: str) -> Optional[Dict]:
        """Utilise Weatherstack (nécessite API key)"""
        # Cette méthode nécessite une clé API payante
        # Implémentation basique
        return None
    
    def map_wttr_icon(self, weather_code: str) -> str:
        """Mappe les codes wttr vers des icônes"""
        icon_map = {
            '113': '☀️',   # Ensoleillé
            '116': '⛅',   # Partiellement nuageux
            '119': '☁️',   # Nuageux
            '122': '☁️',   # Très nuageux
            '143': '🌫️',   # Brume
            '176': '🌦️',   # Averses
            '179': '🌨️',   # Averses de neige
            '182': '🌧️',   # Pluie verglaçante
            '185': '🌧️',   # Bruine verglaçante
            '200': '⛈️',   # Orage
            '227': '🌨️',   # Chutes de neige
            '230': '❄️',   # Tempête de neige
            '248': '🌫️',   # Brouillard
            '260': '🌫️',   # Brouillard givrant
            '263': '🌦️',   # Légères averses
            '266': '🌧️',   # Légère pluie
            '281': '🌧️',   # Pluie verglaçante
            '284': '🌧️',   # Légère pluie verglaçante
            '293': '🌦️',   # Averses éparses
            '296': '🌧️',   # Pluie
            '299': '🌧️',   # Fortes averses
            '302': '🌧️',   # Forte pluie
            '305': '🌧️',   # Averses fortes
            '308': '🌧️',   # Pluie torrentielle
            '311': '🌧️',   # Pluie verglaçante légère
            '314': '🌧️',   # Pluie et neige mêlées
            '317': '🌨️',   # Légère neige
            '320': '🌨️',   # Légères chutes de neige
            '323': '🌨️',   # Neige éparse
            '326': '🌨️',   # Légère neige
            '329': '❄️',   # Neige modérée
            '332': '❄️',   # Forte neige
            '335': '❄️',   # Tempête de neige
            '338': '❄️',   # Neige abondante
            '350': '🌧️',   # Grésil
            '353': '🌦️',   # Légères averses
            '356': '🌧️',   # Averses modérées
            '359': '🌧️',   # Fortes averses
            '362': '🌧️',   # Averses de grésil
            '365': '🌧️',   # Légères averses de grésil
            '368': '🌨️',   # Légères chutes de neige
            '371': '❄️',   # Fortes chutes de neige
            '374': '🌧️',   # Légères averses de grésil
            '377': '🌧️',   # Averses modérées de grésil
            '386': '⛈️',   # Orage avec averses
            '389': '⛈️',   # Orage violent
            '392': '⛈️',   # Orage avec neige
            '395': '❄️',   # Fortes chutes de neige avec orage
        }
        
        return icon_map.get(weather_code, '🌡️')
    
    def format_weather(self, data: Dict) -> str:
        """
        Formate les données météo pour l'affichage
        
        Args:
            data: Données météo
        
        Returns:
            Chaîne formatée
        """
        if not data:
            return "❌ Impossible de récupérer la météo."
        
        emoji = data.get('icon', '🌡️')
        formatted = f"{emoji} **Météo à {data['location']}**\n\n"
        formatted += f"🌡️ **Température:** {data['temperature']}°C "
        formatted += f"(ressentie: {data['feels_like']}°C)\n"
        formatted += f"📝 **Condition:** {data['description']}\n"
        formatted += f"💧 **Humidité:** {data['humidity']}%\n"
        formatted += f"🌬️ **Vent:** {data['wind_speed']} km/h\n"
        
        if 'pressure' in data and data['pressure']:
            formatted += f"📊 **Pression:** {data['pressure']} hPa\n"
        
        if 'clouds' in data and data['clouds']:
            formatted += f"☁️ **Nuages:** {data['clouds']}%\n"
        
        if 'sunrise' in data and 'sunset' in data:
            formatted += f"🌅 **Lever:** {data['sunrise']} | 🌇 **Coucher:** {data['sunset']}\n"
        
        if 'forecast' in data:
            forecast = data['forecast']
            formatted += f"\n📅 **Demain:** {forecast['condition']}\n"
            formatted += f"   Min: {forecast['min_temp']}°C | Max: {forecast['max_temp']}°C\n"
        
        formatted += f"\n_({data.get('provider', 'Source inconnue')})_"
        
        return formatted
    
    def get_weather_alert(self, location: str) -> Optional[str]:
        """
        Vérifie les alertes météo
        
        Args:
            location: Lieu à vérifier
        
        Returns:
            Message d'alerte ou None
        """
        # Cette fonction nécessiterait une API spécifique
        # Pour l'instant, simulation basique
        data = self.get_weather(location)
        
        if not data:
            return None
        
        alerts = []
        
        # Vérifier les conditions extrêmes
        if data['temperature'] > 35:
            alerts.append("⚠️ **Alerte canicule**: Température très élevée")
        elif data['temperature'] < -5:
            alerts.append("⚠️ **Alerte grand froid**: Température très basse")
        
        if data['wind_speed'] > 60:
            alerts.append("⚠️ **Alerte vent violent**: Rafales dangereuses")
        
        if 'precipitation' in data and data['precipitation'] > 20:
            alerts.append("⚠️ **Alerte pluies intenses**: Risque d'inondation")
        
        if alerts:
            return "\n".join(alerts)
        
        return None

# Test du module
if __name__ == "__main__":
    # Tester avec ou sans clé API
    weather = WeatherModule()
    
    print("🌤️ Test du module météo\n")
    
    # Tester plusieurs villes
    test_locations = ["Paris", "Londres", "New York"]
    
    for location in test_locations:
        print(f"\n📍 {location}:")
        
        # Essayer d'abord OpenWeather (si clé API disponible)
        data = weather.get_weather(location, provider='openweather')
        
        if not data:
            # Fallback sur wttr.in
            data = weather.get_weather(location, provider='wttr')
        
        if data:
            print(weather.format_weather(data))
            
            # Vérifier les alertes
            alert = weather.get_weather_alert(location)
            if alert:
                print(f"\n{alert}")
        else:
            print("❌ Données météo non disponibles")