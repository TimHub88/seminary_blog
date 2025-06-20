#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Handler - Gestion des images via Unsplash API
Seminary Blog System - Système de Blog Automatisé SEO-First

Ce module gère la recherche, téléchargement et optimisation d'images
libres de droit via l'API Unsplash, avec système de fallback robuste.
"""

import os
import re
import logging
import requests
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import json
from pathlib import Path
import hashlib
import time

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageHandler:
    """Gestionnaire d'images pour le système Seminary Blog."""
    
    def __init__(self, unsplash_access_key: Optional[str] = None):
        """
        Initialise le gestionnaire d'images.
        
        Args:
            unsplash_access_key: Clé d'accès Unsplash API
        """
        self.unsplash_access_key = unsplash_access_key
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
            'vosges mountains', 'france mountains business'
        ]
        
        # Cache des recherches pour éviter les appels répétitifs
        self.search_cache_file = self.cache_dir / "unsplash_cache.json"
        self.search_cache = self._load_search_cache()
    
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
        Recherche des images sur Unsplash.
        
        Args:
            query: Terme de recherche
            count: Nombre d'images à retourner (max 30)
            orientation: 'landscape', 'portrait', ou 'squarish'
            
        Returns:
            Liste d'informations sur les images trouvées
        """
        if not self.unsplash_access_key:
            logger.warning("Clé API Unsplash manquante")
            return self._get_fallback_images(query, count)
        
        # Vérifier le cache d'abord
        cache_key = self._generate_cache_key(query, orientation)
        if cache_key in self.search_cache:
            cached_result = self.search_cache[cache_key]
            if time.time() - cached_result['timestamp'] < 3600:  # Cache valide 1h
                logger.info(f"Utilisation du cache pour la recherche: {query}")
                return cached_result['images'][:count]
        
        try:
            # Préparer la requête à l'API Unsplash
            headers = {
                'Authorization': f'Client-ID {self.unsplash_access_key}',
                'Accept-Version': 'v1'
            }
            
            params = {
                'query': query,
                'page': 1,
                'per_page': min(count, 30),  # Max 30 par requête
                'orientation': orientation,
                'content_filter': 'high',  # Contenu approprié
                'order_by': 'relevant'
            }
            
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
                image_info = {
                    'id': photo['id'],
                    'description': photo.get('description') or photo.get('alt_description', ''),
                    'url_regular': photo['urls']['regular'],
                    'url_small': photo['urls']['small'],
                    'url_thumb': photo['urls']['thumb'],
                    'width': photo['width'],
                    'height': photo['height'],
                    'photographer': photo['user']['name'],
                    'photographer_url': photo['user']['links']['html'],
                    'download_url': photo['links']['download_location'],
                    'unsplash_url': photo['links']['html']
                }
                images.append(image_info)
            
            # Mettre en cache le résultat
            self.search_cache[cache_key] = {
                'timestamp': time.time(),
                'query': query,
                'images': images
            }
            self._save_search_cache()
            
            logger.info(f"Trouvé {len(images)} images pour '{query}'")
            return images
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API Unsplash pour '{query}': {e}")
            return self._get_fallback_images(query, count)
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'images: {e}")
            return self._get_fallback_images(query, count)
    
    def _get_fallback_images(self, query: str, count: int) -> List[Dict]:
        """
        Retourne des images de fallback quand l'API Unsplash n'est pas disponible.
        
        Args:
            query: Terme de recherche original
            count: Nombre d'images demandées
            
        Returns:
            Liste d'images de fallback
        """
        # Images de fallback avec Picsum (placeholder)
        fallback_images = []
        
        for i in range(min(count, 5)):  # Max 5 images de fallback
            image_id = 1000 + i * 50  # IDs espacés pour éviter les doublons
            
            fallback_image = {
                'id': f'fallback_{image_id}',
                'description': f'Image professionnelle pour séminaire - {query}',
                'url_regular': f'https://picsum.photos/id/{image_id}/1200/800',
                'url_small': f'https://picsum.photos/id/{image_id}/600/400',
                'url_thumb': f'https://picsum.photos/id/{image_id}/300/200',
                'width': 1200,
                'height': 800,
                'photographer': 'Picsum Photos',
                'photographer_url': 'https://picsum.photos',
                'download_url': f'https://picsum.photos/id/{image_id}/1200/800',
                'unsplash_url': 'https://picsum.photos',
                'is_fallback': True
            }
            fallback_images.append(fallback_image)
        
        logger.info(f"Utilisation de {len(fallback_images)} images de fallback")
        return fallback_images
    
    def download_image(self, image_info: Dict, filename: Optional[str] = None) -> Optional[str]:
        """
        Télécharge une image et la sauvegarde localement.
        
        Args:
            image_info: Informations de l'image (depuis search_images)
            filename: Nom de fichier personnalisé (optionnel)
            
        Returns:
            Chemin local de l'image téléchargée ou None si échec
        """
        try:
            # Générer le nom de fichier
            if not filename:
                # Utiliser l'ID de l'image et nettoyer la description
                clean_desc = re.sub(r'[^\w\s-]', '', image_info.get('description', ''))
                clean_desc = re.sub(r'\s+', '-', clean_desc.strip())[:50]
                filename = f"{image_info['id']}_{clean_desc}.jpg"
            
            # Assurer l'extension .jpg
            if not filename.lower().endswith(('.jpg', '.jpeg')):
                filename += '.jpg'
            
            file_path = self.images_dir / filename
            
            # Vérifier si l'image existe déjà
            if file_path.exists():
                logger.info(f"Image déjà présente: {filename}")
                return str(file_path)
            
            # Télécharger l'image
            download_url = image_info.get('url_regular', image_info.get('download_url'))
            
            # Pour Unsplash, déclencher le download tracking
            if not image_info.get('is_fallback', False) and 'download_url' in image_info:
                try:
                    headers = {'Authorization': f'Client-ID {self.unsplash_access_key}'}
                    requests.get(image_info['download_url'], headers=headers, timeout=10)
                except Exception:
                    pass  # Le tracking n'est pas critique
            
            # Télécharger l'image
            response = requests.get(download_url, timeout=self.image_config['timeout'])
            response.raise_for_status()
            
            # Vérifier la taille du fichier
            if len(response.content) > self.image_config['max_file_size']:
                logger.warning(f"Image trop volumineuse: {len(response.content)} bytes")
                # Essayer avec l'URL small
                small_url = image_info.get('url_small')
                if small_url:
                    response = requests.get(small_url, timeout=self.image_config['timeout'])
                    response.raise_for_status()
            
            # Sauvegarder l'image
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Image téléchargée: {filename} ({len(response.content)} bytes)")
            return str(file_path)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors du téléchargement: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'image: {e}")
            return None
    
    def suggest_images_for_article(self, article_content: str, title: str) -> List[Dict]:
        """
        Suggère des images appropriées pour un article.
        
        Args:
            article_content: Contenu de l'article
            title: Titre de l'article
            
        Returns:
            Liste d'images suggérées avec scores de pertinence
        """
        # Analyser le contenu pour identifier les mots-clés pertinents
        content_keywords = self._extract_keywords_from_content(article_content, title)
        
        # Préparer les requêtes de recherche
        search_queries = self._generate_search_queries(content_keywords)
        
        all_suggestions = []
        
        for query in search_queries[:3]:  # Limiter à 3 requêtes pour éviter les quotas
            images = self.search_images(query, count=5)
            
            for image in images:
                # Calculer un score de pertinence
                relevance_score = self._calculate_relevance_score(
                    image, content_keywords, query
                )
                
                suggestion = {
                    **image,
                    'search_query': query,
                    'relevance_score': relevance_score,
                    'suggested_alt_text': self._generate_alt_text(image, content_keywords),
                    'suggested_title': self._generate_image_title(image, content_keywords)
                }
                
                all_suggestions.append(suggestion)
        
        # Trier par score de pertinence
        all_suggestions.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Supprimer les doublons basés sur l'ID
        seen_ids = set()
        unique_suggestions = []
        for suggestion in all_suggestions:
            if suggestion['id'] not in seen_ids:
                seen_ids.add(suggestion['id'])
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:5]  # Retourner les 5 meilleures suggestions
    
    def _extract_keywords_from_content(self, content: str, title: str) -> List[str]:
        """Extrait les mots-clés pertinents du contenu."""
        # Combiner titre et contenu
        full_text = f"{title} {content}".lower()
        
        # Mots-clés spécifiques aux séminaires
        seminary_terms = [
            'séminaire', 'équipe', 'team building', 'formation',
            'entreprise', 'professionnel', 'meeting', 'réunion',
            'montagne', 'nature', 'forêt', 'outdoor', 'vosges'
        ]
        
        # Mots-clés trouvés dans le contenu
        found_keywords = []
        for term in seminary_terms:
            if term in full_text:
                found_keywords.append(term)
        
        # Ajouter des mots-clés génériques si aucun trouvé
        if not found_keywords:
            found_keywords = ['corporate', 'business', 'meeting', 'professional']
        
        return found_keywords
    
    def _generate_search_queries(self, keywords: List[str]) -> List[str]:
        """Génère des requêtes de recherche optimisées."""
        queries = []
        
        # Requête basée sur les mots-clés trouvés
        if keywords:
            primary_query = ' '.join(keywords[:3])  # Max 3 mots-clés
            queries.append(f"{primary_query} business")
        
        # Requêtes Seminary spécifiques
        queries.extend([
            "corporate retreat mountain",
            "business seminar nature",
            "team meeting outdoor"
        ])
        
        # Ajouter des requêtes de fallback
        queries.extend(self.seminary_keywords[:2])
        
        return queries[:5]  # Max 5 requêtes
    
    def _calculate_relevance_score(self, image: Dict, keywords: List[str], query: str) -> float:
        """Calcule un score de pertinence pour une image."""
        score = 0.0
        
        # Score basé sur la description de l'image
        description = (image.get('description', '') + ' ' + 
                      image.get('alt_description', '')).lower()
        
        for keyword in keywords:
            if keyword.lower() in description:
                score += 2.0
        
        # Score basé sur la requête
        query_words = query.lower().split()
        for word in query_words:
            if word in description:
                score += 1.0
        
        # Bonus pour les images avec de bonnes dimensions
        width = image.get('width', 0)
        height = image.get('height', 0)
        if width >= 1200 and height >= 600:
            score += 1.0
        
        # Malus pour les images de fallback
        if image.get('is_fallback', False):
            score *= 0.5
        
        return score
    
    def _generate_alt_text(self, image: Dict, keywords: List[str]) -> str:
        """Génère un texte alt optimisé pour l'image."""
        base_description = image.get('description', '')
        
        if base_description:
            # Nettoyer et adapter la description
            alt_text = re.sub(r'[^\w\s-]', '', base_description)
            alt_text = alt_text.strip()[:100]  # Limiter à 100 caractères
        else:
            # Générer une description basée sur les mots-clés
            alt_text = f"Séminaire professionnel en {' '.join(keywords[:2])}"
        
        return alt_text
    
    def _generate_image_title(self, image: Dict, keywords: List[str]) -> str:
        """Génère un titre optimisé pour l'image."""
        photographer = image.get('photographer', 'Photographe')
        
        if keywords:
            title = f"Séminaire {keywords[0]} - Photo par {photographer}"
        else:
            title = f"Séminaire d'entreprise - Photo par {photographer}"
        
        return title[:150]  # Limiter la longueur
    
    def cleanup_old_images(self, days_old: int = 30) -> int:
        """
        Nettoie les anciennes images non utilisées.
        
        Args:
            days_old: Âge en jours des images à supprimer
            
        Returns:
            Nombre d'images supprimées
        """
        if not self.images_dir.exists():
            return 0
        
        import time
        from datetime import datetime, timedelta
        
        cutoff_time = time.time() - (days_old * 24 * 3600)
        deleted_count = 0
        
        for image_file in self.images_dir.glob('*.jpg'):
            try:
                file_stat = image_file.stat()
                if file_stat.st_mtime < cutoff_time:
                    image_file.unlink()
                    deleted_count += 1
                    logger.info(f"Image supprimée: {image_file.name}")
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de {image_file}: {e}")
        
        logger.info(f"Nettoyage terminé: {deleted_count} images supprimées")
        return deleted_count


def main():
    """Point d'entrée pour les tests CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Image Handler - Seminary Blog")
    parser.add_argument('--search', help='Rechercher des images')
    parser.add_argument('--api-key', help='Clé API Unsplash')
    parser.add_argument('--download', help='ID image à télécharger')
    parser.add_argument('--cleanup', type=int, help='Nettoyer images plus anciennes que X jours')
    
    args = parser.parse_args()
    
    handler = ImageHandler(args.api_key)
    
    if args.search:
        images = handler.search_images(args.search, count=5)
        print(f"=== RECHERCHE: {args.search} ===")
        for i, img in enumerate(images, 1):
            print(f"{i}. {img['id']} - {img['description'][:50]}...")
            print(f"   {img['width']}x{img['height']} - {img['photographer']}")
    
    if args.download and args.search:
        images = handler.search_images(args.search, count=1)
        if images:
            path = handler.download_image(images[0])
            if path:
                print(f"Image téléchargée: {path}")
            else:
                print("Échec du téléchargement")
    
    if args.cleanup:
        deleted = handler.cleanup_old_images(args.cleanup)
        print(f"Images supprimées: {deleted}")


if __name__ == "__main__":
    main() 