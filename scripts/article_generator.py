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

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArticleGenerator:
    """Générateur d'articles complet avec pipeline 4-pass."""
    
    def __init__(self, chutes_api_key: str, unsplash_api_key: Optional[str] = None):
        """
        Initialise le générateur d'articles.
        
        Args:
            chutes_api_key: Clé API Chutes AI
            unsplash_api_key: Clé API Unsplash (optionnel)
        """
        self.chutes_api_key = chutes_api_key
        self.unsplash_api_key = unsplash_api_key
        
        # Initialiser les modules
        self.context_manager = ContextManager()
        self.seo_validator = SEOValidator()
        self.image_handler = ImageHandler(unsplash_api_key)
        self.seminary_integrator = SeminaryIntegrator()
        
        # Configuration de génération - Optimisée pour DeepSeek-R1
        self.generation_config = {
            'max_retries': 3,  # Moins de retries car ils sont longs
            'retry_delay': 20,  # Délai réduit
            'chutes_api_url': 'https://llm.chutes.ai/v1/chat/completions',  # URL officielle Chutes AI
            'chutes_model': 'deepseek-ai/DeepSeek-R1-0528',  # Modèle officiel Chutes AI
            'min_article_words': 600,  # Objectifs plus réalistes
            'max_article_words': 1500,
            'target_word_count': 900,  # Plus court pour éviter les timeouts
            'seo_score_threshold': 70,  # Seuil plus permissif
            'max_improvement_attempts': 2,  # Moins d'améliorations
            'api_timeout': 180,  # 3 minutes pour DeepSeek-R1
            'max_tokens_per_call': 1500  # Limite pour éviter les timeouts
        }
        
        # Templates de prompts
        self.prompts = {
            'creative_generation': '''
            Écris DIRECTEMENT un article de blog de {target_words} mots sur les séminaires d'entreprise dans les Vosges.

            IMPORTANT: Ne montre pas ton processus de réflexion, donne directement l'article final.

            STRUCTURE:
            <h1>Titre principal</h1>
            <p>Introduction engageante</p>
            <h2>Section 1</h2>
            <p>Contenu...</p>
            <h2>Section 2</h2>
            <p>Contenu...</p>
            <h2>Conclusion</h2>
            <p>Appel à l'action</p>

            MOTS-CLÉS: séminaire d'entreprise, Vosges, team building, formation, nature, montagne

            CONTEXTE EXISTANT: {context}
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
        Le modèle DeepSeek-R1 commence souvent par <think>...</think> puis donne la vraie réponse.
        """
        import re
        
        # Cas 1: Contenu avec balises <think>
        if '<think>' in raw_content:
            # Chercher ce qui vient après </think>
            think_pattern = r'<think>.*?</think>\s*(.*)'
            match = re.search(think_pattern, raw_content, re.DOTALL)
            if match:
                final_content = match.group(1).strip()
                if final_content and len(final_content) > 100:  # Assurer un contenu substantiel
                    return final_content
        
        # Cas 2: Contenu qui commence directement par du reasoning
        lines = raw_content.split('\n')
        final_lines = []
        reasoning_ended = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Détecter la fin du reasoning (phrases méta sur le processus)
            if any(phrase in line.lower() for phrase in [
                'je vais', 'il faut', 'l\'utilisateur', 'je me concentre', 
                'il faudra', 'j\'éviterai', 'hmm', 'probablement', 
                'semble avoir besoin', 'visiblement', 'la chute sur'
            ]):
                continue
                
            # Si c'est une phrase normale (pas du meta-reasoning)
            if (line.startswith('#') or  # Titre
                line.startswith('<') or   # HTML
                len(line.split()) > 5):   # Phrase substantielle
                reasoning_ended = True
                
            if reasoning_ended and line:
                final_lines.append(line)
        
        if final_lines and len('\n'.join(final_lines)) > 200:
            return '\n'.join(final_lines)
        
        # Cas 3: Fallback - prendre tout le contenu s'il semble valide
        if len(raw_content) > 300 and not raw_content.lower().startswith('hmm'):
            return raw_content
            
        # Cas 4: Contenu trop court ou invalide
        logger.warning("Contenu généré insuffisant ou invalide")
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
                
                response = requests.post(
                    self.generation_config['chutes_api_url'],
                    headers=headers,
                    json=payload,
                    timeout=self.generation_config['api_timeout']  # 3 minutes pour DeepSeek-R1
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Format de réponse OpenAI-compatible
                if 'choices' in result and len(result['choices']) > 0:
                    raw_text = result['choices'][0]['message']['content'].strip()
                    
                    if raw_text:
                        # Extraire le contenu final du modèle DeepSeek-R1
                        generated_text = self._extract_final_content_from_deepseek(raw_text)
                        logger.info(f"Génération réussie: {len(generated_text)} caractères (extrait de {len(raw_text)} caractères bruts)")
                        return generated_text
                    else:
                        logger.warning("Texte généré vide")
                else:
                    logger.warning("Format de réponse inattendu")
                    logger.debug(f"Réponse reçue: {result}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur API (tentative {attempt + 1}): {e}")
                if attempt < self.generation_config['max_retries'] - 1:
                    logger.info(f"Attente de {self.generation_config['retry_delay']}s avant retry...")
                    time.sleep(self.generation_config['retry_delay'])
            except Exception as e:
                logger.error(f"Erreur inattendue: {e}")
                logger.debug(f"Détails de l'erreur: {str(e)}")
                break
        
        logger.error("Échec de génération après tous les retries")
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
        
        # Générer le HTML complet
        final_html = self.article_template.render(
            title=article_data['metadata'].get('title', 'Article Seminary'),
            meta_description=article_data['metadata'].get('description', ''),
            content=article_data['content'],
            date=datetime.now().strftime('%Y-%m-%d'),
            author='Seminary Blog Bot'
        )
        
        # Intégrer les liens Seminary
        seminary_result = self.seminary_integrator.process_article(
            final_html, 
            article_data['metadata'].get('title', '')
        )
        
        final_html = seminary_result['modified_html']
        
        logger.info(f"Liens Seminary ajoutés: {seminary_result['links_added']}")
        
        # Ajouter une image si disponible
        if self.unsplash_api_key:
            try:
                image_suggestions = self.image_handler.suggest_images_for_article(
                    article_data['content'],
                    article_data['metadata'].get('title', '')
                )
                
                if image_suggestions:
                    best_image = image_suggestions[0]
                    image_path = self.image_handler.download_image(best_image)
                    
                    if image_path:
                        # Injecter l'image dans le HTML
                        final_html = self._inject_featured_image(final_html, image_path, best_image)
                        logger.info(f"Image ajoutée: {image_path}")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'ajout d'image: {e}")
        
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
    
    def _inject_featured_image(self, html: str, image_path: str, image_info: Dict) -> str:
        """Injecte une image mise en avant dans l'article."""
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
            # Mettre à jour le contexte
            context = self.context_manager.get_context_for_ai()
            
            # Pass 1: Génération créative
            article_data = self.pass1_creative_generation(context)
            if not article_data:
                logger.error("Échec du Pass 1 - Génération créative")
                return None
            
            # Pass 2: Audit SEO
            seo_audit = self.pass2_seo_audit(article_data)
            
            # Pass 3: Auto-amélioration
            improved_article = self.pass3_auto_improvement(article_data, seo_audit)
            if not improved_article:
                logger.error("Échec du Pass 3 - Auto-amélioration")
                return None
            
            # Pass 4: Intégration Seminary
            final_result = self.pass4_seminary_integration(improved_article)
            
            # Sauvegarder l'article
            file_path = self.save_article(final_result)
            
            # Mettre à jour le contexte avec le nouvel article
            self.context_manager.update_context(self.chutes_api_key)
            
            # Statistiques finales
            duration = time.time() - start_time
            word_count = improved_article['word_count']
            
            logger.info(f"✅ GÉNÉRATION TERMINÉE")
            logger.info(f"📄 Fichier: {file_path}")
            logger.info(f"📊 Mots: {word_count}")
            logger.info(f"⏱️  Durée: {duration:.1f}s")
            logger.info(f"🔗 Liens Seminary: {final_result['seminary_integration']['links_added']}")
            
            return file_path
            
        except Exception as e:
            logger.error(f"Erreur critique dans le pipeline: {e}")
            return None


def main():
    """Point d'entrée principal pour l'exécution standalone."""
    parser = argparse.ArgumentParser(description="Article Generator - Seminary Blog Pipeline")
    parser.add_argument('--chutes-api-key', required=True, help='Clé API Chutes AI')
    parser.add_argument('--unsplash-api-key', help='Clé API Unsplash (optionnel)')
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
        generator = ArticleGenerator(args.chutes_api_key, args.unsplash_api_key)
        test_response = generator.call_chutes_api("Test de connexion", max_tokens=10)
        if test_response:
            print("✅ Connexion API réussie")
        else:
            print("❌ Échec de connexion API")
        return
    
    # Génération normale
    generator = ArticleGenerator(args.chutes_api_key, args.unsplash_api_key)
    
    result_path = generator.generate_full_article()
    
    if result_path:
        print(f"✅ Article généré avec succès: {result_path}")
    else:
        print("❌ Échec de génération d'article")
        exit(1)


if __name__ == "__main__":
    main() 