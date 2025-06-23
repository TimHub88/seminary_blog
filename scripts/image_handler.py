#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Handler - Gestion des images et illustrations visuelles
Seminary Blog System - Système de Blog Automatisé SEO-First

Ce module gère :
1. Recherche et téléchargement d'images via Unsplash API
2. Génération d'illustrations CSS/SVG pour améliorer le SEO
3. Création de graphiques intégrés et infographies
4. Système de fallback robuste multi-niveaux
"""

import os
import re
import logging
import requests
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
import json
from pathlib import Path
import hashlib
import time
import base64
import random
from dataclasses import dataclass

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UnsplashConfig:
    """Configuration pour l'API Unsplash."""
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    app_name: str = "Seminary Blog"
    utm_source: str = "seminary_blog"
    demo_mode: bool = True
    rate_limit_per_hour: int = 50  # 50 en demo, 5000 en production

class ImageHandler:
    """Gestionnaire d'images et illustrations pour le système Seminary Blog."""
    
    def __init__(self, unsplash_access_key: Optional[str] = None, unsplash_secret_key: Optional[str] = None):
        """
        Initialise le gestionnaire d'images et illustrations.
        
        Args:
            unsplash_access_key: Clé d'accès Unsplash API
            unsplash_secret_key: Clé secrète Unsplash API (pour production)
        """
        # Configuration Unsplash améliorée
        self.unsplash_config = UnsplashConfig(
            access_key=unsplash_access_key,
            secret_key=unsplash_secret_key,
            demo_mode=not bool(unsplash_secret_key)  # Production si secret key fournie
        )
        
        if not self.unsplash_config.demo_mode:
            self.unsplash_config.rate_limit_per_hour = 5000
        
        self.unsplash_base_url = "https://api.unsplash.com"
        self.images_dir = Path("images")
        self.cache_dir = Path("data/image_cache")
        
        # Créer les répertoires nécessaires
        self.images_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration des images
        self.image_config = {
            'default_width': 1200,
            'default_height': 800,
            'quality': 85,
            'formats': ['jpg', 'jpeg', 'webp'],
            'max_file_size': 2 * 1024 * 1024,  # 2MB
            'timeout': 30
        }
        
        # Mots-clés Seminary pour recherche d'images
        self.seminary_keywords = [
            'mountain meeting', 'corporate retreat', 'team building nature',
            'business seminar mountains', 'professional workshop forest',
            'corporate event outdoor', 'meeting room nature',
            'teamwork outdoors', 'business conference mountain',
            'vosges mountains', 'france mountains business',
            'leadership training', 'corporate wellness', 'professional development'
        ]
        
        # Cache des recherches pour éviter les appels répétitifs
        self.search_cache_file = self.cache_dir / "unsplash_cache.json"
        self.search_cache = self._load_search_cache()
        
        # Système de tracking des requêtes pour respecter les limites
        self.request_tracker = {
            'count': 0,
            'last_reset': time.time(),
            'limit_reached': False
        }
    
    def _check_rate_limit(self) -> bool:
        """Vérifie si on peut faire une requête API selon les limites."""
        current_time = time.time()
        
        # Reset du compteur toutes les heures
        if current_time - self.request_tracker['last_reset'] >= 3600:
            self.request_tracker = {
                'count': 0,
                'last_reset': current_time,
                'limit_reached': False
            }
        
        # Vérifier la limite
        if self.request_tracker['count'] >= self.unsplash_config.rate_limit_per_hour:
            self.request_tracker['limit_reached'] = True
            logger.warning(f"Limite de requêtes Unsplash atteinte: {self.unsplash_config.rate_limit_per_hour}/h")
            return False
        
        return True
    
    def _increment_request_count(self):
        """Incrémente le compteur de requêtes."""
        self.request_tracker['count'] += 1
    
    def _load_search_cache(self) -> Dict:
        """Charge le cache des recherches Unsplash."""
        try:
            if self.search_cache_file.exists():
                with open(self.search_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du cache: {e}")
        
        return {}
    
    def _save_search_cache(self) -> None:
        """Sauvegarde le cache des recherches."""
        try:
            with open(self.search_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du cache: {e}")
    
    def _generate_cache_key(self, query: str, orientation: str = 'landscape') -> str:
        """Génère une clé de cache unique pour une recherche."""
        cache_string = f"{query.lower().strip()}_{orientation}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def search_images(self, query: str, count: int = 10, orientation: str = 'landscape') -> List[Dict]:
        """
        Recherche des images sur Unsplash avec configuration améliorée.
        
        Args:
            query: Terme de recherche
            count: Nombre d'images à retourner (max 30)
            orientation: 'landscape', 'portrait', ou 'squarish'
            
        Returns:
            Liste d'informations sur les images trouvées
        """
        if not self.unsplash_config.access_key:
            logger.warning("Clé API Unsplash manquante - utilisation du fallback")
            return self._get_fallback_images(query, count)
        
        if not self._check_rate_limit():
            logger.warning("Limite de requêtes atteinte - utilisation du cache/fallback")
            return self._get_fallback_images(query, count)
        
        # Vérifier le cache d'abord
        cache_key = self._generate_cache_key(query, orientation)
        if cache_key in self.search_cache:
            cached_result = self.search_cache[cache_key]
            if time.time() - cached_result['timestamp'] < 3600:  # Cache valide 1h
                logger.info(f"Utilisation du cache pour la recherche: {query}")
                return cached_result['images'][:count]
        
        try:
            # Headers avec configuration complète selon la documentation Unsplash
            headers = {
                'Authorization': f'Client-ID {self.unsplash_config.access_key}',
                'Accept-Version': 'v1',
                'User-Agent': f'{self.unsplash_config.app_name}/1.0'
            }
            
            # Paramètres optimisés selon la documentation
            params = {
                'query': query,
                'page': 1,
                'per_page': min(count, 30),  # Max 30 par requête selon l'API
                'orientation': orientation,
                'content_filter': 'high',  # Contenu approprié professionnel
                'order_by': 'relevant',
                'color': None,  # Pas de filtre couleur pour plus de résultats
                'utm_source': self.unsplash_config.utm_source,
                'utm_medium': 'referral'
            }
            
            self._increment_request_count()
            
            response = requests.get(
                f"{self.unsplash_base_url}/search/photos",
                headers=headers,
                params=params,
                timeout=self.image_config['timeout']
            )
            
            response.raise_for_status()
            search_data = response.json()
            
            images = []
            for photo in search_data.get('results', []):
                # Construction des URLs avec utm_source selon les guidelines
                unsplash_url = f"{photo['links']['html']}?utm_source={self.unsplash_config.utm_source}&utm_medium=referral"
                
                image_info = {
                    'id': photo['id'],
                    'description': photo.get('description') or photo.get('alt_description', ''),
                    'url_regular': photo['urls']['regular'],
                    'url_small': photo['urls']['small'],
                    'url_thumb': photo['urls']['thumb'],
                    'url_raw': photo['urls']['raw'],
                    'width': photo['width'],
                    'height': photo['height'],
                    'photographer': photo['user']['name'],
                    'photographer_url': f"{photo['user']['links']['html']}?utm_source={self.unsplash_config.utm_source}&utm_medium=referral",
                    'download_url': photo['links']['download_location'],
                    'unsplash_url': unsplash_url,
                    'color': photo.get('color', '#000000'),
                    'blur_hash': photo.get('blur_hash'),
                    'likes': photo.get('likes', 0),
                    'tags': [tag['title'] for tag in photo.get('tags', [])]
                }
                images.append(image_info)
            
            # Mettre en cache le résultat
            self.search_cache[cache_key] = {
                'timestamp': time.time(),
                'query': query,
                'images': images
            }
            self._save_search_cache()
            
            logger.info(f"Trouvé {len(images)} images Unsplash pour '{query}' (requêtes: {self.request_tracker['count']}/{self.unsplash_config.rate_limit_per_hour})")
            return images
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API Unsplash pour '{query}': {e}")
            return self._get_fallback_images(query, count)
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'images: {e}")
            return self._get_fallback_images(query, count)
    
    def generate_css_illustration(self, illustration_type: str, theme: str, **kwargs) -> str:
        """
        Génère des illustrations CSS/SVG pour améliorer le SEO et l'engagement.
        
        Args:
            illustration_type: Type d'illustration ('chart', 'infographic', 'icon', 'diagram')
            theme: Thème Seminary ('team-building', 'nature', 'professional', 'statistics')
            **kwargs: Paramètres spécifiques selon le type
            
        Returns:
            Code HTML/CSS/SVG de l'illustration
        """
        if illustration_type == 'chart':
            return self._generate_chart_css(theme, **kwargs)
        elif illustration_type == 'infographic':
            return self._generate_infographic_css(theme, **kwargs)
        elif illustration_type == 'icon':
            return self._generate_icon_illustration(theme, **kwargs)
        elif illustration_type == 'diagram':
            return self._generate_diagram_css(theme, **kwargs)
        else:
            return self._generate_default_illustration(theme)
    
    def _generate_chart_css(self, theme: str, data: Optional[Dict] = None, chart_type: str = 'bar', **kwargs) -> str:
        """Génère un graphique CSS animé."""
        if not data:
            # Données par défaut pour les séminaires
            data = {
                'Cohésion équipe': 85,
                'Productivité': 78,
                'Communication': 92,
                'Motivation': 88,
                'Innovation': 76
            }
        
        if chart_type == 'bar':
            return self._generate_bar_chart(data, theme)
        elif chart_type == 'progress':
            return self._generate_progress_chart(data, theme)
        else:
            return self._generate_bar_chart(data, theme)
    
    def _generate_bar_chart(self, data: Dict, theme: str) -> str:
        """Génère un graphique en barres CSS animé."""
        chart_html = """
<div class="seminary-chart-container" style="margin: 2rem 0; padding: 2rem; background: linear-gradient(135deg, #f8f9ff 0%, #e8edff 100%); border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h3 style="text-align: center; color: #7E22CE; margin-bottom: 2rem; font-weight: 600;">Impact des séminaires Seminary sur les équipes</h3>
    <div class="chart-bars" style="display: flex; align-items: end; justify-content: space-between; height: 200px; margin-bottom: 1rem;">
"""
        
        max_value = max(data.values())
        colors = ['#7E22CE', '#A94BE0', '#6B1B9A', '#8B5A9F', '#9F4BBD']
        
        for i, (label, value) in enumerate(data.items()):
            height_percent = (value / max_value) * 100
            color = colors[i % len(colors)]
            
            chart_html += f"""
        <div class="chart-bar" style="
            width: {100 / len(data) - 2}%;
            height: {height_percent}%;
            background: linear-gradient(to top, {color}, {color}AA);
            border-radius: 4px 4px 0 0;
            position: relative;
            animation: seminary-bar-grow 1.5s ease-out {i * 0.2}s both;
            margin: 0 1%;
        ">
            <div style="
                position: absolute;
                top: -30px;
                left: 50%;
                transform: translateX(-50%);
                font-weight: 600;
                color: #333;
                font-size: 0.9rem;
            ">{value}%</div>
            <div style="
                position: absolute;
                bottom: -40px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 0.8rem;
                color: #666;
                text-align: center;
                width: 120%;
            ">{label}</div>
        </div>"""
        
        chart_html += """
    </div>
    <p style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 2rem;">
        📊 Amélioration moyenne constatée 3 mois après un séminaire Seminary dans les Vosges
    </p>
</div>

<style>
@keyframes seminary-bar-grow {
    from {
        height: 0%;
    }
    to {
        height: var(--final-height);
    }
}

.seminary-chart-container:hover .chart-bar {
    transform: scale(1.05);
    transition: transform 0.3s ease;
}
</style>
"""
        return chart_html
    
    def _generate_progress_chart(self, data: Dict, theme: str) -> str:
        """Génère un graphique de progression circulaire."""
        if len(data) > 1:
            # Prendre la première valeur pour le cercle principal
            main_value = list(data.values())[0]
            main_label = list(data.keys())[0]
        else:
            main_value = 85
            main_label = "Satisfaction globale"
        
        # Calculer le stroke-dasharray pour l'animation
        circumference = 2 * 3.14159 * 45  # rayon de 45
        stroke_offset = circumference - (main_value / 100) * circumference
        
        chart_html = f"""
<div class="seminary-progress-chart" style="
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    margin: 2rem 0;
    background: linear-gradient(135deg, #7E22CE10, #A94BE020);
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(126, 34, 206, 0.1);
">
    <div style="position: relative; width: 200px; height: 200px;">
        <svg width="200" height="200" style="transform: rotate(-90deg);">
            <!-- Cercle de fond -->
            <circle
                cx="100"
                cy="100"
                r="45"
                fill="none"
                stroke="#e5e7eb"
                stroke-width="8"
            />
            <!-- Cercle de progression -->
            <circle
                cx="100"
                cy="100"
                r="45"
                fill="none"
                stroke="url(#seminary-gradient)"
                stroke-width="8"
                stroke-linecap="round"
                stroke-dasharray="{circumference}"
                stroke-dashoffset="{stroke_offset}"
                style="
                    animation: seminary-progress-draw 2s ease-out forwards;
                "
            />
            <defs>
                <linearGradient id="seminary-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#7E22CE"/>
                    <stop offset="100%" stop-color="#A94BE0"/>
                </linearGradient>
            </defs>
        </svg>
        
        <!-- Texte central -->
        <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        ">
            <div style="
                font-size: 2.5rem;
                font-weight: 700;
                color: #7E22CE;
                line-height: 1;
            ">{main_value}%</div>
            <div style="
                font-size: 0.9rem;
                color: #666;
                margin-top: 0.5rem;
                font-weight: 500;
            ">{main_label}</div>
        </div>
    </div>
</div>

<style>
@keyframes seminary-progress-draw {{
    from {{
        stroke-dashoffset: {circumference};
    }}
    to {{
        stroke-dashoffset: {stroke_offset};
    }}
}}
</style>
"""
        return chart_html
    
    def _generate_infographic_css(self, theme: str, **kwargs) -> str:
        """Génère une infographie CSS sur les séminaires."""
        steps = kwargs.get('steps', [
            {'title': 'Diagnostic', 'desc': 'Analyse des besoins équipe', 'icon': '🔍'},
            {'title': 'Planification', 'desc': 'Choix du lieu et activités', 'icon': '📋'},
            {'title': 'Animation', 'desc': 'Séminaire dans les Vosges', 'icon': '🏔️'},
            {'title': 'Suivi', 'desc': 'Mesure des impacts', 'icon': '📈'}
        ])
        
        infographic_html = """
<div class="seminary-infographic" style="
    margin: 2rem 0;
    padding: 2rem;
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 25px rgba(126, 34, 206, 0.1);
">
    <h3 style="
        text-align: center;
        color: #7E22CE;
        margin-bottom: 3rem;
        font-weight: 600;
        font-size: 1.8rem;
    ">Processus Seminary en 4 étapes</h3>
    
    <div style="
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 2rem;
        position: relative;
    ">
"""
        
        for i, step in enumerate(steps):
            infographic_html += f"""
        <div class="infographic-step" style="
            text-align: center;
            position: relative;
            animation: seminary-step-appear 0.6s ease-out {i * 0.3}s both;
        ">
            <div style="
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #7E22CE, #A94BE0);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem;
                font-size: 2rem;
                color: white;
                box-shadow: 0 4px 15px rgba(126, 34, 206, 0.3);
            ">{step['icon']}</div>
            
            <h4 style="
                color: #333;
                margin-bottom: 0.5rem;
                font-weight: 600;
            ">{step['title']}</h4>
            
            <p style="
                color: #666;
                font-size: 0.9rem;
                line-height: 1.5;
            ">{step['desc']}</p>
            
            <div style="
                position: absolute;
                top: 40px;
                right: -1rem;
                width: 2rem;
                height: 2px;
                background: linear-gradient(to right, #7E22CE, transparent);
                display: {'' if i < len(steps) - 1 else 'none'};
            "></div>
        </div>"""
        
        infographic_html += """
    </div>
</div>

<style>
@keyframes seminary-step-appear {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.infographic-step:hover {
    transform: translateY(-5px);
    transition: transform 0.3s ease;
}
</style>
"""
        return infographic_html