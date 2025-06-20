#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Manager - Gestion du contexte des 3 derniers articles
Seminary Blog System - Système de Blog Automatisé SEO-First

Ce module gère la mémoire contextuelle du système en maintenant
un résumé des 3 derniers articles publiés pour alimenter l'IA
avec un contexte pertinent lors de la génération de nouveaux contenus.
"""

import json
import os
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextManager:
    """Gestionnaire du contexte des articles pour le système Seminary Blog."""
    
    def __init__(self, data_dir: str = "data", articles_dir: str = "articles"):
        """
        Initialise le gestionnaire de contexte.
        
        Args:
            data_dir: Répertoire contenant le fichier context_window.json
            articles_dir: Répertoire contenant les articles HTML
        """
        self.data_dir = Path(data_dir)
        self.articles_dir = Path(articles_dir)
        self.context_file = self.data_dir / "context_window.json"
        
        # Créer les répertoires s'ils n'existent pas
        self.data_dir.mkdir(exist_ok=True)
        self.articles_dir.mkdir(exist_ok=True)
        
        # Initialiser le fichier de contexte s'il n'existe pas
        if not self.context_file.exists():
            self._initialize_context_file()
    
    def _initialize_context_file(self) -> None:
        """Initialise le fichier context_window.json."""
        initial_context = {
            "last_articles": [],
            "last_updated": None,
            "version": "1.0.0"
        }
        
        with open(self.context_file, 'w', encoding='utf-8') as f:
            json.dump(initial_context, f, indent=4, ensure_ascii=False)
        
        logger.info("Fichier context_window.json initialisé.")
    
    def load_context(self) -> Dict:
        """Charge le contexte actuel depuis le fichier JSON."""
        try:
            with open(self.context_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Erreur lors du chargement du contexte: {e}")
            self._initialize_context_file()
            return self.load_context()
    
    def save_context(self, context: Dict) -> None:
        """Sauvegarde le contexte dans le fichier JSON."""
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=4, ensure_ascii=False)
            logger.info("Contexte sauvegardé avec succès.")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du contexte: {e}")
            raise
    
    def get_latest_articles(self, limit: int = 10) -> List[Path]:
        """
        Récupère les derniers articles HTML triés par date de création.
        
        Args:
            limit: Nombre maximum d'articles à retourner
            
        Returns:
            Liste des chemins des articles, triés du plus récent au plus ancien
        """
        if not self.articles_dir.exists():
            return []
        
        # Récupérer tous les fichiers HTML
        html_files = list(self.articles_dir.glob("*.html"))
        
        # Filtrer les fichiers qui suivent le format YYYY-MM-DD-titre.html
        date_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})-.*\.html$')
        dated_files = []
        
        for file_path in html_files:
            match = date_pattern.match(file_path.name)
            if match:
                date_str = match.group(1)
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    dated_files.append((date_obj, file_path))
                except ValueError:
                    logger.warning(f"Format de date invalide dans le fichier: {file_path.name}")
        
        # Trier par date décroissante (plus récent en premier)
        dated_files.sort(key=lambda x: x[0], reverse=True)
        
        # Retourner seulement les chemins, limités
        return [file_path for _, file_path in dated_files[:limit]]
    
    def extract_article_content(self, article_path: Path) -> Dict[str, str]:
        """
        Extrait le contenu d'un article HTML.
        
        Args:
            article_path: Chemin vers le fichier HTML de l'article
            
        Returns:
            Dictionnaire contenant titre, contenu et métadonnées
        """
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extraire le titre
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "Sans titre"
            
            # Extraire la meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ''
            
            # Extraire le contenu principal
            content_div = soup.find('div', class_='article-content')
            if content_div:
                # Supprimer les balises mais garder le texte
                content_text = content_div.get_text(separator=' ', strip=True)
            else:
                # Fallback: extraire tout le texte du body
                body = soup.find('body')
                content_text = body.get_text(separator=' ', strip=True) if body else ''
            
            # Nettoyer le contenu (supprimer les espaces multiples)
            content_text = re.sub(r'\s+', ' ', content_text).strip()
            
            return {
                'title': title,
                'description': description,
                'content': content_text,
                'filename': article_path.name,
                'date': self._extract_date_from_filename(article_path.name)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du contenu de {article_path}: {e}")
            return {
                'title': f"Erreur - {article_path.name}",
                'description': '',
                'content': '',
                'filename': article_path.name,
                'date': self._extract_date_from_filename(article_path.name)
            }
    
    def _extract_date_from_filename(self, filename: str) -> str:
        """Extrait la date du nom de fichier au format YYYY-MM-DD."""
        match = re.match(r'^(\d{4}-\d{2}-\d{2})', filename)
        return match.group(1) if match else 'Date inconnue'
    
    def generate_summary(self, article_content: str, api_key: str, max_words: int = 100) -> str:
        """
        Génère un résumé de 100 mots via l'API Chutes AI.
        
        Args:
            article_content: Contenu de l'article à résumer
            api_key: Clé API Chutes AI
            max_words: Nombre maximum de mots pour le résumé
            
        Returns:
            Résumé de l'article en 100 mots maximum
        """
        if not article_content.strip():
            return "Contenu vide - impossible de générer un résumé."
        
        # Tronquer le contenu si trop long (limite API)
        content_preview = article_content[:3000] if len(article_content) > 3000 else article_content
        
        prompt = f"""
        Résume cet article de blog sur les séminaires dans les Vosges en exactement {max_words} mots.
        Le résumé doit être informatif, concis et mentionner les points clés.
        
        Article à résumer:
        {content_preview}
        
        Résumé en {max_words} mots:
        """
        
        try:
            # Configuration de l'appel API Chutes AI
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'prompt': prompt,
                'max_tokens': max_words * 2,  # Marge de sécurité
                'temperature': 0.3,  # Résumé précis, peu créatif
                'stop': ['\n\n', 'Article suivant:', 'En conclusion:']
            }
            
            # Note: URL d'API Chutes AI - à adapter selon la documentation
            api_url = "https://api.chutes.ai/v1/generate"  # URL exemple
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            summary = result.get('generated_text', '').strip()
            
            # Nettoyer et valider le résumé
            if summary:
                # Supprimer les préfixes indésirables
                summary = re.sub(r'^(Résumé|Summary):\s*', '', summary, flags=re.IGNORECASE)
                
                # Limiter à max_words mots
                words = summary.split()
                if len(words) > max_words:
                    summary = ' '.join(words[:max_words]) + '...'
                
                return summary
            else:
                logger.warning("Résumé vide reçu de l'API")
                return self._generate_fallback_summary(content_preview, max_words)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API lors de la génération du résumé: {e}")
            return self._generate_fallback_summary(content_preview, max_words)
        except Exception as e:
            logger.error(f"Erreur lors de la génération du résumé: {e}")
            return self._generate_fallback_summary(content_preview, max_words)
    
    def _generate_fallback_summary(self, content: str, max_words: int = 100) -> str:
        """Génère un résumé de fallback simple basé sur les premières phrases."""
        sentences = re.split(r'[.!?]+', content)
        summary_words = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            words = sentence.split()
            if len(summary_words) + len(words) <= max_words:
                summary_words.extend(words)
            else:
                # Ajouter autant de mots que possible
                remaining_words = max_words - len(summary_words)
                if remaining_words > 0:
                    summary_words.extend(words[:remaining_words])
                break
        
        return ' '.join(summary_words) + ('...' if len(summary_words) == max_words else '')
    
    def update_context(self, api_key: str) -> Dict:
        """
        Met à jour le contexte avec les 3 derniers articles.
        
        Args:
            api_key: Clé API Chutes AI pour la génération de résumés
            
        Returns:
            Contexte mis à jour
        """
        logger.info("Mise à jour du contexte des articles...")
        
        # Récupérer les 3 derniers articles
        latest_articles = self.get_latest_articles(limit=3)
        
        if not latest_articles:
            logger.info("Aucun article trouvé.")
            return self.load_context()
        
        # Traiter chaque article
        articles_data = []
        for article_path in latest_articles:
            logger.info(f"Traitement de l'article: {article_path.name}")
            
            # Extraire le contenu
            article_info = self.extract_article_content(article_path)
            
            # Générer le résumé
            summary = self.generate_summary(article_info['content'], api_key)
            
            article_data = {
                'filename': article_info['filename'],
                'title': article_info['title'],
                'date': article_info['date'],
                'summary': summary,
                'description': article_info['description']
            }
            
            articles_data.append(article_data)
            logger.info(f"Résumé généré pour {article_path.name}: {len(summary)} caractères")
        
        # Créer le nouveau contexte
        new_context = {
            'last_articles': articles_data,
            'last_updated': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        # Sauvegarder
        self.save_context(new_context)
        
        logger.info(f"Contexte mis à jour avec {len(articles_data)} articles.")
        return new_context
    
    def get_context_for_ai(self) -> str:
        """
        Retourne le contexte formaté pour l'IA.
        
        Returns:
            String formatée contenant les résumés des 3 derniers articles
        """
        context = self.load_context()
        articles = context.get('last_articles', [])
        
        if not articles:
            return "Aucun article précédent disponible. C'est le premier article du blog."
        
        context_text = "Contexte des derniers articles publiés sur le blog Seminary:\n\n"
        
        for i, article in enumerate(articles, 1):
            context_text += f"{i}. {article['title']} ({article['date']})\n"
            context_text += f"   Résumé: {article['summary']}\n\n"
        
        context_text += "Assure-toi de créer un contenu unique et complémentaire qui n'est pas redondant avec ces articles précédents."
        
        return context_text
    
    def rebuild_context(self, api_key: str) -> Dict:
        """
        Reconstruction complète du contexte (utile pour le debugging).
        
        Args:
            api_key: Clé API Chutes AI
            
        Returns:
            Nouveau contexte reconstruit
        """
        logger.info("Reconstruction complète du contexte...")
        
        # Réinitialiser le fichier de contexte
        self._initialize_context_file()
        
        # Mettre à jour avec les derniers articles
        return self.update_context(api_key)


def main():
    """Point d'entrée principal pour les tests et l'usage CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Context Manager - Seminary Blog")
    parser.add_argument('--rebuild', action='store_true', help='Reconstruire complètement le contexte')
    parser.add_argument('--api-key', required=True, help='Clé API Chutes AI')
    parser.add_argument('--show-context', action='store_true', help='Afficher le contexte actuel')
    
    args = parser.parse_args()
    
    manager = ContextManager()
    
    if args.show_context:
        context_text = manager.get_context_for_ai()
        print("=== CONTEXTE ACTUEL ===")
        print(context_text)
        print("=" * 50)
    
    if args.rebuild:
        context = manager.rebuild_context(args.api_key)
    else:
        context = manager.update_context(args.api_key)
    
    print(f"Contexte mis à jour avec {len(context['last_articles'])} articles.")
    print(f"Dernière mise à jour: {context['last_updated']}")


if __name__ == "__main__":
    main() 