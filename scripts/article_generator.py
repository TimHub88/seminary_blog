#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Article Generator - Pipeline 4-Pass Principal
Seminary Blog System - Système de Blog Automatisé SEO-First

Ce module orchestre le pipeline complet de génération d'articles :
Pass 1: Génération Créative
Pass 2: Auto-Audit SEO
Pass 3: Auto-Amélioration
Pass 4: Finalisation & Intégration Seminary
"""

import os
import json
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re
from jinja2 import Template
import argparse

# Imports des modules Seminary
from context_manager import ContextManager
from seo_validator import SEOValidator
from image_handler import ImageHandler
from seminary_integrator import SeminaryIntegrator
from fallback_generator import create_fallback_article

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArticleGenerator:
    """Générateur d'articles complet avec pipeline 4-pass."""
    
    def __init__(self, chutes_api_key: str, unsplash_access_key: Optional[str] = None, unsplash_secret_key: Optional[str] = None):
        """
        Initialise le générateur d'articles.
        
        Args:
            chutes_api_key: Clé API Chutes AI
            unsplash_access_key: Clé d'accès Unsplash API
            unsplash_secret_key: Clé secrète Unsplash API (pour production)
        """
        self.chutes_api_key = chutes_api_key
        self.unsplash_access_key = unsplash_access_key
        self.unsplash_secret_key = unsplash_secret_key
        
        # Initialiser les modules
        self.context_manager = ContextManager()
        self.seo_validator = SEOValidator()
        self.image_handler = ImageHandler(unsplash_access_key, unsplash_secret_key)
        self.seminary_integrator = SeminaryIntegrator()
        
        # Configuration de génération - Optimisée pour DeepSeek-R1
        self.generation_config = {
            'max_retries': 3,  # Moins de retries car ils sont longs
            'retry_delay': 20,  # Délai réduit
            'chutes_api_url': 'https://llm.chutes.ai/v1/chat/completions',  # URL officielle Chutes AI
            'chutes_model': 'deepseek-ai/DeepSeek-R1-0528',  # Modèle officiel Chutes AI
            'min_article_words': 600,  # Objectifs plus réalistes
            'max_article_words': 1500,
            'target_word_count': 400,  # Cible réaliste pour l'API
            'seo_score_threshold': 70,  # Seuil plus permissif
            'max_improvement_attempts': 2,  # Moins d'améliorations
            'api_timeout': 180,  # 3 minutes pour DeepSeek-R1
            'max_tokens_per_call': 1500  # Limite pour éviter les timeouts
        }
        
        # Templates de prompts
        self.prompts = {
            'creative_generation': '''
            Écris un article de blog complet de minimum {target_words} mots sur les séminaires d'entreprise dans les Vosges.

            IMPORTANT: 
            - Écris un article substantiel et développé
            - Minimum {target_words} mots requis
            - Ne montre pas ton processus de réflexion

            STRUCTURE REQUISE:
            <h1>Titre principal accrocheur</h1>
            <p>Introduction engageante de 2-3 phrases</p>
            <h2>Les avantages des Vosges pour les séminaires</h2>
            <p>Développe les atouts: nature, accessibilité, équipements...</p>
            <h2>Activités team building incontournables</h2>
            <p>Détaille les activités possibles avec exemples concrets...</p>
            <h2>Organiser son séminaire: conseils pratiques</h2>
            <p>Donne des conseils détaillés pour l'organisation...</p>
            <h2>Pourquoi choisir Seminary pour votre événement</h2>
            <p>Présente les services et expertise de Seminary...</p>

            MOTS-CLÉS À INTÉGRER: séminaire d'entreprise, Vosges, team building, formation, nature, montagne, Seminary

            CONTEXTE EXISTANT: {context}
            
            DÉVELOPPE CHAQUE SECTION EN DÉTAIL POUR ATTEINDRE {target_words} MOTS MINIMUM.
            ''',
            
            'seo_improvement': '''
            Améliore DIRECTEMENT cet article pour le SEO. Ne montre pas ton processus de réflexion.

            ARTICLE À AMÉLIORER:
            {article_content}

            PROBLÈMES À CORRIGER:
            {seo_issues}

            Renvoie UNIQUEMENT l'article HTML amélioré:
            ''',
            
            'content_enrichment': '''
            Enrichis DIRECTEMENT cet article pour atteindre {target_words} mots. Ne montre pas ton processus de réflexion.

            ARTICLE À ENRICHIR:
            {article_content}

            Ajoute: exemples concrets, bénéfices entreprises, descriptions Vosges, conseils pratiques.

            Renvoie UNIQUEMENT l'article HTML enrichi:
            '''
        }
        
        # Charger le template d'article
        self.article_template = self._load_article_template()
    
    def _extract_final_content_from_deepseek(self, raw_content: str) -> str:
        """
        Extrait le contenu final du modèle DeepSeek-R1 qui expose son reasoning.
        Version simplifiée et plus permissive.
        """
        import re
        
        # Cas 1: Contenu avec balises <think>
        if '<think>' in raw_content:
            # Chercher ce qui vient après </think>
            think_pattern = r'<think>.*?</think>\s*(.*)'
            match = re.search(think_pattern, raw_content, re.DOTALL)
            if match:
                final_content = match.group(1).strip()
                if final_content and len(final_content) > 100:
                    logger.info(f"Extraction <think>: {len(final_content)} caractères")
                    return final_content
        
        # Cas 2: Chercher le premier titre <h1> et prendre tout ce qui suit
        h1_pattern = r'(<h1>.*)'
        match = re.search(h1_pattern, raw_content, re.DOTALL | re.IGNORECASE)
        if match:
            html_content = match.group(1).strip()
            if len(html_content) > 200:
                logger.info(f"Extraction <h1>: {len(html_content)} caractères")
                return html_content
        
        # Cas 3: Chercher le premier paragraphe HTML et prendre tout ce qui suit
        p_pattern = r'(<[ph][1-6]?>.*)'
        match = re.search(p_pattern, raw_content, re.DOTALL | re.IGNORECASE)
        if match:
            html_content = match.group(1).strip()
            if len(html_content) > 150:
                logger.info(f"Extraction HTML: {len(html_content)} caractères")
                return html_content
        
        # Cas 4: Filtrer seulement les lignes de reasoning évidentes
        lines = raw_content.split('\n')
        filtered_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # Filtrer SEULEMENT les lignes de reasoning très évidentes
            if any(phrase in line_stripped.lower() for phrase in [
                'je vais créer', 'je dois', 'il me faut', 'mon objectif',
                'je commence par', 'je vais maintenant', 'laissez-moi'
            ]):
                continue
                
            filtered_lines.append(line)
        
        filtered_content = '\n'.join(filtered_lines).strip()
        if len(filtered_content) > 200:
            logger.info(f"Extraction filtrée: {len(filtered_content)} caractères")
            return filtered_content
        
        # Cas 5: Fallback - prendre TOUT le contenu brut
        logger.warning(f"Aucune extraction spécifique, utilisation contenu brut: {len(raw_content)} caractères")
        return raw_content
    
    def _load_article_template(self) -> Template:
        """Charge le template Jinja2 pour les articles."""
        template_path = Path('templates/article_template.html')
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            return Template(template_content)
        except FileNotFoundError:
            logger.error(f"Template non trouvé: {template_path}")
            # Template minimal de fallback
            fallback_template = '''
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{{ title }}</title>
                <meta name="description" content="{{ meta_description }}">
            </head>
            <body>
                {{ content | safe }}
            </body>
            </html>
            '''
            return Template(fallback_template)
    
    def call_chutes_api(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> Optional[str]:
        """
        Appelle l'API Chutes AI avec le format officiel chat/completions.
        
        Args:
            prompt: Prompt à envoyer
            max_tokens: Nombre maximum de tokens
            temperature: Créativité (0.0 à 1.0)
            
        Returns:
            Réponse générée ou None si échec
        """
        # VALIDATION CRITIQUE: Vérifier la clé API
        if not self.chutes_api_key or self.chutes_api_key.strip() == "":
            logger.error("❌ ERREUR CRITIQUE: CHUTES_API_KEY non définie ou vide")
            logger.error("   Le workflow GitHub Actions doit définir cette variable d'environnement")
            raise ValueError("CHUTES_API_KEY manquante - impossible de continuer")
        
        headers = {
            'Authorization': f'Bearer {self.chutes_api_key}',
            'Content-Type': 'application/json'
        }
        
        # Format officiel Chutes AI chat/completions
        payload = {
            'model': self.generation_config['chutes_model'],
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'stream': False,  # Mode non-streaming pour simplifier
            'max_tokens': max_tokens,
            'temperature': temperature
        }
        
        for attempt in range(self.generation_config['max_retries']):
            try:
                logger.info(f"Appel Chutes AI (tentative {attempt + 1}/{self.generation_config['max_retries']})")
                logger.info(f"Modèle: {self.generation_config['chutes_model']}")
                logger.info(f"Clé API: {self.chutes_api_key[:10]}...")
                
                response = requests.post(
                    self.generation_config['chutes_api_url'],
                    headers=headers,
                    json=payload,
                    timeout=self.generation_config['api_timeout']  # 3 minutes pour DeepSeek-R1
                )
                
                logger.info(f"Status Code API: {response.status_code}")
                
                # VALIDATION CRITIQUE: Vérifier le status code
                if response.status_code == 401:
                    logger.error("❌ ERREUR 401: Clé API invalide ou expirée")
                    logger.error("   Vérifiez la variable CHUTES_API_KEY dans GitHub Secrets")
                    raise ValueError("Authentification API échouée")
                elif response.status_code == 429:
                    logger.error("❌ ERREUR 429: Limite de taux API atteinte")
                    logger.info("   Attente plus longue avant retry...")
                    time.sleep(60)  # Attendre 1 minute pour les limites de taux
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                # VALIDATION CRITIQUE: Vérifier le format de réponse
                if 'choices' not in result:
                    logger.error(f"❌ Format de réponse API invalide: {result}")
                    continue
                    
                if len(result['choices']) == 0:
                    logger.error("❌ Aucun choix dans la réponse API")
                    continue
                
                raw_text = result['choices'][0]['message']['content'].strip()
                
                # VALIDATION CRITIQUE: Vérifier que le contenu n'est pas vide
                if not raw_text or len(raw_text) < 50:
                    logger.error(f"❌ Contenu généré trop court ou vide: {len(raw_text) if raw_text else 0} caractères")
                    continue
                
                # Extraire le contenu final du modèle DeepSeek-R1
                generated_text = self._extract_final_content_from_deepseek(raw_text)
                
                # VALIDATION FINALE: Vérifier que l'extraction a réussi
                if not generated_text or len(generated_text) < 100:
                    logger.error(f"❌ Extraction DeepSeek échouée: {len(generated_text) if generated_text else 0} caractères")
                    logger.debug(f"Contenu brut: {raw_text[:200]}...")
                    continue
                
                # VALIDATION HTML: Vérifier la présence de balises HTML
                if not ('<h1>' in generated_text or '<h2>' in generated_text or '<p>' in generated_text):
                    logger.error("❌ Contenu généré ne contient pas de HTML valide")
                    logger.debug(f"Contenu: {generated_text[:200]}...")
                    continue
                
                logger.info(f"✅ Génération réussie: {len(generated_text)} caractères (extrait de {len(raw_text)} caractères bruts)")
                return generated_text
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Erreur API (tentative {attempt + 1}): {e}")
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"   Réponse HTTP: {e.response.text}")
                if attempt < self.generation_config['max_retries'] - 1:
                    logger.info(f"   Attente de {self.generation_config['retry_delay']}s avant retry...")
                    time.sleep(self.generation_config['retry_delay'])
            except Exception as e:
                logger.error(f"❌ Erreur inattendue: {e}")
                logger.debug(f"Détails de l'erreur: {str(e)}")
                break
        
        logger.error("❌ ÉCHEC CRITIQUE: Impossible de générer du contenu après tous les retries")
        logger.error("   Cela empêchera la création d'articles vides")
        return None
    
    def pass1_creative_generation(self, context: str) -> Optional[Dict]:
        """
        Pass 1: Génération créative initiale.
        
        Args:
            context: Contexte des articles précédents
            
        Returns:
            Dictionnaire avec le contenu généré
        """
        logger.info("=== PASS 1: GÉNÉRATION CRÉATIVE ===")
        
        prompt = self.prompts['creative_generation'].format(
            context=context,
            target_words=self.generation_config['target_word_count']
        )
        
        generated_content = self.call_chutes_api(
            prompt, 
            max_tokens=self.generation_config['max_tokens_per_call'],  # Limite pour éviter les timeouts
            temperature=0.6  # Température plus basse pour DeepSeek-R1
        )
        
        if not generated_content:
            return None
        
        # Nettoyer et structurer le contenu
        cleaned_content = self._clean_generated_content(generated_content)
        
        # Extraire les métadonnées
        metadata = self._extract_metadata_from_content(cleaned_content)
        
        return {
            'content': cleaned_content,
            'metadata': metadata,
            'word_count': len(cleaned_content.split()),
            'generation_timestamp': datetime.now().isoformat()
        }
    
    def pass2_seo_audit(self, article_data: Dict) -> Dict:
        """
        Pass 2: Audit SEO automatique.
        
        Args:
            article_data: Données de l'article du Pass 1
            
        Returns:
            Résultats de l'audit SEO
        """
        logger.info("=== PASS 2: AUDIT SEO ===")
        
        # Créer un HTML temporaire pour l'audit
        temp_html = self.article_template.render(
            title=article_data['metadata'].get('title', 'Article'),
            meta_description=article_data['metadata'].get('description', ''),
            content=article_data['content']
        )
        
        # Effectuer l'audit SEO
        audit_result = self.seo_validator.perform_full_audit(temp_html)
        
        logger.info(f"Score SEO: {audit_result['global_score']}/100")
        logger.info(f"Statut: {audit_result['status']}")
        
        if audit_result['major_issues']:
            logger.warning(f"Problèmes majeurs détectés: {len(audit_result['major_issues'])}")
        
        return audit_result
    
    def pass3_auto_improvement(self, article_data: Dict, seo_audit: Dict) -> Optional[Dict]:
        """
        Pass 3: Auto-amélioration basée sur l'audit SEO.
        
        Args:
            article_data: Données de l'article
            seo_audit: Résultats de l'audit SEO
            
        Returns:
            Article amélioré ou None si échec
        """
        logger.info("=== PASS 3: AUTO-AMÉLIORATION ===")
        
        # Vérifier si des améliorations sont nécessaires
        if seo_audit['global_score'] >= self.generation_config['seo_score_threshold']:
            logger.info("Score SEO suffisant, pas d'amélioration nécessaire")
            return article_data
        
        # Construire la liste des problèmes à corriger
        issues_list = []
        issues_list.extend(seo_audit.get('major_issues', []))
        issues_list.extend(seo_audit.get('all_warnings', [])[:5])  # Top 5 warnings
        
        if not issues_list:
            logger.info("Aucun problème spécifique détecté")
            return article_data
        
        # Préparer le prompt d'amélioration
        issues_text = '\n'.join(f"- {issue}" for issue in issues_list)
        
        for attempt in range(self.generation_config['max_improvement_attempts']):
            logger.info(f"Tentative d'amélioration {attempt + 1}/{self.generation_config['max_improvement_attempts']}")
            
            prompt = self.prompts['seo_improvement'].format(
                article_content=article_data['content'],
                seo_issues=issues_text
            )
            
            improved_content = self.call_chutes_api(
                prompt,
                max_tokens=3500,
                temperature=0.5  # Moins créatif, plus focalisé
            )
            
            if improved_content:
                # Nettoyer le contenu amélioré
                cleaned_improved = self._clean_generated_content(improved_content)
                
                # Vérifier l'amélioration
                improved_metadata = self._extract_metadata_from_content(cleaned_improved)
                
                # Test rapide du nouveau score
                temp_html = self.article_template.render(
                    title=improved_metadata.get('title', article_data['metadata']['title']),
                    meta_description=improved_metadata.get('description', ''),
                    content=cleaned_improved
                )
                
                quick_audit = self.seo_validator.perform_full_audit(temp_html)
                
                if quick_audit['global_score'] > seo_audit['global_score']:
                    logger.info(f"Amélioration réussie: {seo_audit['global_score']} → {quick_audit['global_score']}")
                    return {
                        'content': cleaned_improved,
                        'metadata': improved_metadata,
                        'word_count': len(cleaned_improved.split()),
                        'improvement_score': quick_audit['global_score'] - seo_audit['global_score']
                    }
                else:
                    logger.warning(f"Pas d'amélioration significative (tentative {attempt + 1})")
        
        logger.warning("Échec de l'auto-amélioration, utilisation de la version originale")
        return article_data
    
    def pass4_seminary_integration(self, article_data: Dict) -> Dict:
        """
        Pass 4: Finalisation et intégration Seminary.
        
        Args:
            article_data: Données de l'article amélioré
            
        Returns:
            Article final avec intégrations Seminary
        """
        logger.info("=== PASS 4: INTÉGRATION SEMINARY ===")
        
        # Générer le HTML complet avec toutes les variables du template
        template_vars = {
            'article_title': article_data['metadata'].get('title', 'Article Seminary'),
            'meta_description': article_data['metadata'].get('description', ''),
            'article_content': article_data['content'],
            'publish_date': datetime.now().strftime('%d/%m/%Y'),
            'reading_time': max(1, article_data.get('word_count', 400) // 200),  # Estimation 200 mots/min
            'filename': self.generate_filename(article_data['metadata']),
            'header_html': '',  # Templates séparés dans le futur
            'footer_html': '',
            'article_subtitle': ''
        }
        
        final_html = self.article_template.render(**template_vars)
        
        # Intégrer les liens Seminary avec protection anti-corruption
        try:
            seminary_result = self.seminary_integrator.process_article(
                final_html, 
                article_data['metadata'].get('title', '')
            )
            
            # Vérifier que l'intégration Seminary n'a pas corrompu le HTML
            modified_html = seminary_result['modified_html']
            if '<html>' in modified_html and len(modified_html) > len(final_html) * 0.8:
                final_html = modified_html
                logger.info(f"Liens Seminary ajoutés: {seminary_result['links_added']}")
            else:
                logger.warning("Intégration Seminary a corrompu le HTML, conservation de l'original")
                seminary_result = {
                    'modified_html': final_html,
                    'links_added': 0,
                    'integration_plan': {'confidence_score': 0},
                    'analysis': {}
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de l'intégration Seminary: {e}")
            seminary_result = {
                'modified_html': final_html,
                'links_added': 0,
                'integration_plan': {'confidence_score': 0},
                'analysis': {}
            }
        
        # Intégrer images et illustrations CSS/SVG
        try:
            visual_integration = self._integrate_visual_elements(final_html, article_data)
            
            # Vérifier que l'intégration visuelle n'a pas corrompu le HTML
            integrated_html = visual_integration['html']
            if '<html>' in integrated_html and len(integrated_html) > len(final_html) * 0.8:
                final_html = integrated_html
                logger.info(f"Éléments visuels intégrés: {visual_integration['summary']}")
            else:
                logger.warning("Intégration visuelle a corrompu le HTML, conservation de l'original")
                visual_integration = {'summary': '0 éléments visuels ajoutés', 'elements_added': []}
                
        except Exception as e:
            logger.error(f"Erreur lors de l'intégration visuelle: {e}")
            visual_integration = {'summary': '0 éléments visuels ajoutés', 'elements_added': []}
        
        return {
            'final_html': final_html,
            'article_data': article_data,
            'seminary_integration': seminary_result,
            'generation_complete': True
        }
    
    def _clean_generated_content(self, content: str) -> str:
        """Nettoie le contenu généré par l'IA."""
        # Supprimer les préfixes indésirables
        content = re.sub(r'^(Article|Voici|Voilà):\s*', '', content, flags=re.IGNORECASE)
        
        # Nettoyer les balises HTML malformées
        content = re.sub(r'<([^>]+)>', lambda m: f'<{m.group(1).strip()}>', content)
        
        # Supprimer les doublons de balises
        content = re.sub(r'(<h[1-6][^>]*>)\s*\1', r'\1', content)
        
        # Assurer les balises fermantes
        if '<h1>' in content and '</h1>' not in content:
            content = content.replace('<h1>', '<h1>').replace('\n', '</h1>\n', 1)
        
        return content.strip()
    
    def _extract_metadata_from_content(self, content: str) -> Dict:
        """Extrait les métadonnées du contenu généré."""
        metadata = {}
        
        # Extraire le titre (H1)
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        if h1_match:
            metadata['title'] = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        
        # Générer une meta description basée sur le premier paragraphe
        p_match = re.search(r'<p[^>]*>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
        if p_match:
            first_p = re.sub(r'<[^>]+>', '', p_match.group(1)).strip()
            # Limiter à 160 caractères
            if len(first_p) > 160:
                metadata['description'] = first_p[:157] + '...'
            else:
                metadata['description'] = first_p
        
        return metadata
    
    def _integrate_visual_elements(self, html: str, article_data: Dict) -> Dict:
        """Intègre images Unsplash et illustrations CSS/SVG dans l'article."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        visual_elements_added = []
        
        # 1. Ajouter une image Unsplash si disponible
        if self.unsplash_access_key:
            try:
                # Afficher le statut de configuration
                config_status = self.image_handler.get_unsplash_config_status()
                logger.info(f"Configuration Unsplash: {config_status['demo_mode'] and 'Démo' or 'Production'} - {config_status['requests_remaining']} requêtes restantes")
                
                image_suggestions = self.image_handler.suggest_images_for_article(
                    article_data['content'],
                    article_data['metadata'].get('title', '')
                )
                
                if image_suggestions:
                    best_image = image_suggestions[0]
                    image_path = self.image_handler.download_image(best_image)
                    
                    if image_path:
                        # Créer la balise image
                        img_tag = soup.new_tag(
                            'img',
                            src=f"./images/{Path(image_path).name}",
                            alt=best_image.get('suggested_alt_text', 'Séminaire d\'entreprise Seminary'),
                            title=best_image.get('suggested_title', 'Seminary'),
                            style="width: 100%; max-width: 800px; height: auto; margin: 20px 0; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
                        )
                        
                        # Insérer après le premier paragraphe
                        content_div = soup.find('div', class_='article-content')
                        if content_div:
                            first_p = content_div.find('p')
                            if first_p:
                                first_p.insert_after(img_tag)
                                visual_elements_added.append(f"Image Unsplash: {best_image.get('description', 'N/A')[:50]}...")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'ajout d'image Unsplash: {e}")
        
        # 2. Ajouter des illustrations CSS/SVG automatiquement
        try:
            content_text = article_data['content']
            title = article_data['metadata'].get('title', '')
            
            # Suggérer des illustrations appropriées
            illustration_suggestions = self.image_handler.suggest_illustrations_for_article(content_text, title)
            
            content_div = soup.find('div', class_='article-content')
            if content_div and illustration_suggestions:
                
                # Ajouter 1-2 illustrations selon la longueur du contenu
                word_count = article_data.get('word_count', 0)
                max_illustrations = 2 if word_count > 500 else 1
                
                for i, suggestion in enumerate(illustration_suggestions[:max_illustrations]):
                    try:
                        # Extraire le type d'illustration sans modifier le dictionnaire original
                        illustration_type = suggestion.get('illustration_type', 'icon')
                        suggestion_copy = suggestion.copy()
                        suggestion_copy.pop('illustration_type', None)  # Enlever le type du copy
                        
                        # Générer l'illustration CSS/SVG
                        illustration_html = self.image_handler.generate_css_illustration(
                            illustration_type,
                            'professional',
                            **suggestion_copy
                        )
                        
                        # Créer un conteneur pour l'illustration avec HTML correctement inséré
                        illustration_div = soup.new_tag('div', class_='visual-illustration')
                        
                        # CORRECTION CRITIQUE: Utiliser BeautifulSoup pour parser le HTML
                        illustration_soup = BeautifulSoup(illustration_html, 'html.parser')
                        for element in illustration_soup:
                            if element.name:  # Ignorer les éléments texte
                                illustration_div.append(element)
                        
                        # Insérer à des positions stratégiques
                        paragraphs = content_div.find_all('p')
                        if len(paragraphs) > 2:
                            # Insérer après le paragraphe au milieu
                            middle_p = paragraphs[len(paragraphs) // 2]
                            middle_p.insert_after(illustration_div)
                            visual_elements_added.append(f"Illustration {illustration_type}: {suggestion.get('title', 'Sans titre')}")
                        
                    except Exception as e:
                        logger.error(f"Erreur lors de l'ajout d'illustration {illustration_type}: {e}")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout d'illustrations CSS: {e}")
        
        # 3. Optimiser la structure visuelle
        try:
            # Ajouter des classes CSS pour le responsive
            for img in soup.find_all('img'):
                current_style = img.get('style', '')
                if 'responsive' not in current_style:
                    img['style'] = current_style + ' max-width: 100%; height: auto;'
            
            # Ajouter des espacements appropriés
            for illustration in soup.find_all('div', class_='visual-illustration'):
                illustration['style'] = 'margin: 2rem 0;'
                
        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation visuelle: {e}")
        
        return {
            'html': str(soup),
            'elements_added': visual_elements_added,
            'summary': f"{len(visual_elements_added)} éléments visuels ajoutés"
        }
    
    def _inject_featured_image(self, html: str, image_path: str, image_info: Dict) -> str:
        """Injecte une image mise en avant dans l'article (méthode legacy)."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Créer la balise image
        img_tag = soup.new_tag(
            'img',
            src=f"./images/{Path(image_path).name}",
            alt=image_info.get('suggested_alt_text', 'Séminaire d\'entreprise'),
            title=image_info.get('suggested_title', 'Seminary'),
            style="width: 100%; max-width: 800px; height: auto; margin: 20px 0;"
        )
        
        # Trouver le premier paragraphe et insérer l'image après
        content_div = soup.find('div', class_='article-content')
        if content_div:
            first_p = content_div.find('p')
            if first_p:
                first_p.insert_after(img_tag)
        
        return str(soup)
    
    def generate_filename(self, metadata: Dict) -> str:
        """Génère un nom de fichier pour l'article."""
        title = metadata.get('title', 'article')
        
        # Nettoyer le titre pour le nom de fichier
        clean_title = re.sub(r'[^\w\s-]', '', title.lower())
        clean_title = re.sub(r'\s+', '-', clean_title.strip())[:50]
        
        # Ajouter la date
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        return f"{date_str}-{clean_title}.html"
    
    def save_article(self, final_result: Dict, filename: Optional[str] = None) -> str:
        """Sauvegarde l'article généré."""
        if not filename:
            filename = self.generate_filename(final_result['article_data']['metadata'])
        
        # Assurer que le répertoire articles existe
        articles_dir = Path('articles')
        articles_dir.mkdir(exist_ok=True)
        
        file_path = articles_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_result['final_html'])
            
            logger.info(f"Article sauvegardé: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            raise
    
    def generate_full_article(self) -> Optional[str]:
        """
        Génère un article complet via le pipeline 4-pass.
        
        Returns:
            Chemin du fichier généré ou None si échec
        """
        start_time = time.time()
        logger.info("🚀 DÉBUT DE GÉNÉRATION D'ARTICLE - PIPELINE 4-PASS")
        
        try:
            # VALIDATION PRÉALABLE: Vérifier la clé API
            if not self.chutes_api_key or self.chutes_api_key.strip() == "":
                logger.error("❌ ARRÊT IMMÉDIAT: CHUTES_API_KEY non définie")
                logger.error("   Impossible de continuer sans clé API valide")
                raise ValueError("CHUTES_API_KEY manquante")
            
            # Mettre à jour le contexte
            context = self.context_manager.get_context_for_ai()
            
            # Pass 1: Génération créative
            logger.info("=== PASS 1: GÉNÉRATION CRÉATIVE ===")
            article_data = self.pass1_creative_generation(context)
            if not article_data:
                logger.error("❌ ÉCHEC CRITIQUE: Pass 1 - Génération créative")
                logger.error("   Aucun article ne sera créé pour éviter les fichiers vides")
                return None
            
            # VALIDATION PASS 1: Vérifier la qualité du contenu généré
            content = article_data.get('content', '')
            word_count = article_data.get('word_count', 0)
            
            if not content or len(content.strip()) < 200:
                logger.error(f"❌ ÉCHEC CRITIQUE: Contenu Pass 1 trop court ({len(content)} caractères)")
                logger.error("   Aucun article ne sera créé pour éviter les fichiers vides")
                return None
            
            if word_count < 100:
                logger.error(f"❌ ÉCHEC CRITIQUE: Nombre de mots insuffisant ({word_count} mots)")
                logger.error("   Tentative avec article de fallback...")
                
                try:
                    from .fallback_article_generator import create_fallback_article
                    fallback_path = create_fallback_article(self.generation_config['target_word_count'])
                    logger.info(f"✅ Article de fallback créé: {fallback_path}")
                    return fallback_path
                except Exception as e:
                    logger.error(f"❌ Échec du fallback: {e}")
                    return None
            
            # Vérifier la présence de métadonnées essentielles
            metadata = article_data.get('metadata', {})
            if not metadata.get('title') or len(metadata.get('title', '').strip()) < 10:
                logger.error("❌ ÉCHEC CRITIQUE: Titre manquant ou trop court")
                logger.error("   Aucun article ne sera créé pour éviter les fichiers vides")
                return None
            
            logger.info(f"✅ Pass 1 validé: {word_count} mots, titre: '{metadata.get('title', '')[:50]}...'")
            
            # Pass 2: Audit SEO
            logger.info("=== PASS 2: AUDIT SEO ===")
            seo_audit = self.pass2_seo_audit(article_data)
            
            # Pass 3: Auto-amélioration
            logger.info("=== PASS 3: AUTO-AMÉLIORATION ===")
            improved_article = self.pass3_auto_improvement(article_data, seo_audit)
            if not improved_article:
                logger.error("❌ ÉCHEC CRITIQUE: Pass 3 - Auto-amélioration")
                logger.error("   Utilisation de l'article original du Pass 1")
                improved_article = article_data  # Fallback sur l'article original
            
            # VALIDATION FINALE: Vérifier l'article final
            final_content = improved_article.get('content', '')
            final_word_count = improved_article.get('word_count', 0)
            
            if not final_content or len(final_content.strip()) < 250:  # Seuil abaissé de 300 à 250 caractères
                logger.error(f"❌ ÉCHEC CRITIQUE: Contenu final trop court ({len(final_content)} caractères)")
                logger.error("   Aucun article ne sera créé pour éviter les fichiers vides")
                return None
            
            if final_word_count < 120:  # Seuil abaissé de 150 à 120 mots
                logger.error(f"❌ ÉCHEC CRITIQUE: Article final trop court ({final_word_count} mots)")
                logger.error("   Tentative avec article de fallback...")
                
                try:
                    from .fallback_article_generator import create_fallback_article
                    fallback_path = create_fallback_article(self.generation_config['target_word_count'])
                    logger.info(f"✅ Article de fallback créé: {fallback_path}")
                    return fallback_path
                except Exception as e:
                    logger.error(f"❌ Échec du fallback: {e}")
                    return None
            
            logger.info(f"✅ Article final validé: {final_word_count} mots")
            
            # Pass 4: Intégration Seminary
            logger.info("=== PASS 4: INTÉGRATION SEMINARY ===")
            final_result = self.pass4_seminary_integration(improved_article)
            
            # VALIDATION HTML FINALE: Vérifier le HTML complet
            final_html = final_result.get('final_html', '')
            if not final_html or len(final_html.strip()) < 500:
                logger.error(f"❌ ÉCHEC CRITIQUE: HTML final trop court ({len(final_html)} caractères)")
                logger.error("   Aucun article ne sera créé pour éviter les fichiers vides")
                return None
            
            # Vérifier la présence de balises HTML essentielles
            required_tags = ['<html>', '<head>', '<title>', '<body>', '<h1>']
            missing_tags = [tag for tag in required_tags if tag not in final_html]
            if missing_tags:
                logger.error(f"❌ ÉCHEC CRITIQUE: Balises HTML manquantes: {missing_tags}")
                logger.error("   Aucun article ne sera créé pour éviter les fichiers vides")
                return None
            
            logger.info("✅ HTML final validé - Structure complète détectée")
            
            # Sauvegarder l'article
            file_path = self.save_article(final_result)
            
            # VALIDATION POST-SAUVEGARDE: Vérifier que le fichier n'est pas vide
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size < 1000:  # Moins de 1KB = probablement vide
                    logger.error(f"❌ ÉCHEC CRITIQUE: Fichier sauvegardé trop petit ({file_size} bytes)")
                    logger.error("   Suppression du fichier vide")
                    os.remove(file_path)
                    return None
                logger.info(f"✅ Fichier validé: {file_size} bytes")
            
            # Mettre à jour le contexte avec le nouvel article
            self.context_manager.update_context(self.chutes_api_key)
            
            # Statistiques finales
            duration = time.time() - start_time
            
            logger.info(f"✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS")
            logger.info(f"📄 Fichier: {file_path}")
            logger.info(f"📊 Mots: {final_word_count}")
            logger.info(f"⏱️  Durée: {duration:.1f}s")
            logger.info(f"🔗 Liens Seminary: {final_result['seminary_integration']['links_added']}")
            
            return file_path
            
        except Exception as e:
            logger.error(f"❌ ERREUR CRITIQUE DANS LE PIPELINE: {e}")
            logger.error("   Tentative de création d'un article de fallback...")
            
            try:
                # Importer le générateur de fallback
                from .fallback_article_generator import create_fallback_article
                
                # Créer un article de fallback pour éviter l'échec complet
                fallback_path = create_fallback_article(self.generation_config['target_word_count'])
                logger.info(f"✅ Article de fallback créé avec succès: {fallback_path}")
                
                # Mettre à jour le contexte avec l'article de fallback
                self.context_manager.update_context(self.chutes_api_key)
                
                return fallback_path
                
            except Exception as fallback_error:
                logger.error(f"❌ ÉCHEC TOTAL: Impossible de créer même un article de fallback: {fallback_error}")
                logger.error("   Aucun article ne sera créé")
                return None


def main():
    """Point d'entrée principal pour l'exécution standalone."""
    parser = argparse.ArgumentParser(description="Article Generator - Seminary Blog Pipeline")
    parser.add_argument('--chutes-api-key', required=True, help='Clé API Chutes AI')
    parser.add_argument('--unsplash-access-key', help='Clé d\'accès Unsplash API (optionnel)')
    parser.add_argument('--unsplash-secret-key', help='Clé secrète Unsplash API (pour production, optionnel)')
    parser.add_argument('--update-context', action='store_true', help='Mettre à jour le contexte uniquement')
    parser.add_argument('--dry-run', action='store_true', help='Test sans génération réelle')
    
    args = parser.parse_args()
    
    if args.update_context:
        # Mise à jour du contexte uniquement
        context_manager = ContextManager()
        context_manager.update_context(args.chutes_api_key)
        print("✅ Contexte mis à jour")
        return
    
    if args.dry_run:
        print("🧪 MODE TEST - Pas de génération réelle")
        # Test de connexion API
        generator = ArticleGenerator(args.chutes_api_key, args.unsplash_access_key, args.unsplash_secret_key)
        test_response = generator.call_chutes_api("Test de connexion", max_tokens=10)
        if test_response:
            print("✅ Connexion API réussie")
        else:
            print("❌ Échec de connexion API")
        return
    
    # Génération normale
    generator = ArticleGenerator(args.chutes_api_key, args.unsplash_access_key, args.unsplash_secret_key)
    
    result_path = generator.generate_full_article()
    
    if result_path:
        print(f"✅ Article généré avec succès: {result_path}")
    else:
        print("❌ Échec de génération d'article")
        exit(1)


if __name__ == "__main__":
    main() 