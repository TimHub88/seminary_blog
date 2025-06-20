#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO Validator - Validation SEO automatique
Seminary Blog System - Système de Blog Automatisé SEO-First

Ce module analyse et valide la conformité SEO des articles générés,
détecte les problèmes majeurs et propose des corrections automatiques.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse
import math

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SEOValidator:
    """Validateur SEO pour les articles Seminary Blog."""
    
    def __init__(self):
        """Initialise le validateur SEO avec les règles de validation."""
        self.seminary_domain = "blog.goseminary.com"
        self.seminary_main_domain = "goseminary.com"
        
        # Règles SEO
        self.rules = {
            'title_min_chars': 30,
            'title_max_chars': 60,
            'meta_desc_min_chars': 120,
            'meta_desc_max_chars': 160,
            'h1_count': 1,
            'content_min_words': 300,
            'content_max_words': 2000,
            'keyword_density_min': 0.5,  # %
            'keyword_density_max': 3.0,  # %
            'internal_links_min': 1,
            'internal_links_max': 8,
            'images_alt_required': True
        }
        
        # Mots-clés prioritaires pour Seminary
        self.target_keywords = [
            'séminaire', 'séminaires', 'vosges', 'entreprise', 'équipe',
            'team building', 'formation', 'événement', 'professionnel',
            'montagne', 'nature', 'retreat', 'offsite'
        ]
    
    def validate_html_structure(self, html_content: str) -> Dict:
        """
        Valide la structure HTML de base de l'article.
        
        Args:
            html_content: Contenu HTML de l'article
            
        Returns:
            Dictionnaire avec les résultats de validation
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            issues = []
            warnings = []
            
            # Vérifier la structure HTML basique
            if not soup.find('html'):
                issues.append("Balise <html> manquante")
            
            if not soup.find('head'):
                issues.append("Balise <head> manquante")
            
            if not soup.find('body'):
                issues.append("Balise <body> manquante")
                
            # Vérifier l'attribut lang
            html_tag = soup.find('html')
            if html_tag and not html_tag.get('lang'):
                warnings.append("Attribut lang manquant sur la balise <html>")
            
            # Vérifier le charset
            charset_meta = soup.find('meta', attrs={'charset': True})
            if not charset_meta:
                issues.append("Déclaration charset manquante")
            
            # Vérifier viewport
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            if not viewport_meta:
                warnings.append("Meta viewport manquante (responsive design)")
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'warnings': warnings,
                'score': max(0, 100 - len(issues) * 20 - len(warnings) * 5)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation HTML: {e}")
            return {
                'valid': False,
                'issues': [f"Erreur de parsing HTML: {str(e)}"],
                'warnings': [],
                'score': 0
            }
    
    def validate_title_tag(self, soup: BeautifulSoup) -> Dict:
        """Valide la balise title."""
        title_tag = soup.find('title')
        
        if not title_tag:
            return {
                'valid': False,
                'issues': ["Balise <title> manquante"],
                'warnings': [],
                'title': '',
                'length': 0,
                'score': 0
            }
        
        title_text = title_tag.get_text().strip()
        title_length = len(title_text)
        
        issues = []
        warnings = []
        
        # Vérifier la longueur
        if title_length < self.rules['title_min_chars']:
            issues.append(f"Titre trop court ({title_length} chars, minimum {self.rules['title_min_chars']})")
        elif title_length > self.rules['title_max_chars']:
            warnings.append(f"Titre long ({title_length} chars, optimal < {self.rules['title_max_chars']})")
        
        # Vérifier la présence de mots-clés
        title_lower = title_text.lower()
        keywords_found = [kw for kw in self.target_keywords if kw in title_lower]
        
        if not keywords_found:
            warnings.append("Aucun mot-clé cible trouvé dans le titre")
        
        # Vérifier les caractères spéciaux problématiques
        if '|' in title_text or ' - ' in title_text:
            warnings.append("Éviter les séparateurs '|' ou ' - ' dans le titre")
        
        score = 100
        score -= len(issues) * 30
        score -= len(warnings) * 10
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'title': title_text,
            'length': title_length,
            'keywords_found': keywords_found,
            'score': max(0, score)
        }
    
    def validate_meta_description(self, soup: BeautifulSoup) -> Dict:
        """Valide la meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        
        if not meta_desc:
            return {
                'valid': False,
                'issues': ["Meta description manquante"],
                'warnings': [],
                'description': '',
                'length': 0,
                'score': 0
            }
        
        desc_text = meta_desc.get('content', '').strip()
        desc_length = len(desc_text)
        
        issues = []
        warnings = []
        
        # Vérifier la longueur
        if desc_length < self.rules['meta_desc_min_chars']:
            issues.append(f"Meta description trop courte ({desc_length} chars, minimum {self.rules['meta_desc_min_chars']})")
        elif desc_length > self.rules['meta_desc_max_chars']:
            warnings.append(f"Meta description longue ({desc_length} chars, optimal < {self.rules['meta_desc_max_chars']})")
        
        # Vérifier la présence de mots-clés
        desc_lower = desc_text.lower()
        keywords_found = [kw for kw in self.target_keywords if kw in desc_lower]
        
        if not keywords_found:
            warnings.append("Aucun mot-clé cible trouvé dans la meta description")
        
        score = 100
        score -= len(issues) * 30
        score -= len(warnings) * 10
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'description': desc_text,
            'length': desc_length,
            'keywords_found': keywords_found,
            'score': max(0, score)
        }
    
    def validate_heading_structure(self, soup: BeautifulSoup) -> Dict:
        """Valide la structure des titres (H1-H6)."""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        issues = []
        warnings = []
        
        # Compter les H1
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0:
            issues.append("Aucun H1 trouvé")
        elif len(h1_tags) > 1:
            issues.append(f"Plusieurs H1 trouvés ({len(h1_tags)}), un seul recommandé")
        
        # Vérifier la hiérarchie
        heading_levels = []
        for heading in headings:
            level = int(heading.name[1])
            heading_levels.append(level)
        
        # Analyser la progression des niveaux
        if heading_levels:
            current_level = 1 if h1_tags else 2
            for i, level in enumerate(heading_levels):
                if level > current_level + 1:
                    warnings.append(f"Saut de niveau détecté: {heading_levels[i-1] if i > 0 else 'début'} → H{level}")
                current_level = level
        
        # Vérifier le contenu des headings
        empty_headings = [h for h in headings if not h.get_text().strip()]
        if empty_headings:
            issues.append(f"{len(empty_headings)} titre(s) vide(s)")
        
        score = 100
        score -= len(issues) * 25
        score -= len(warnings) * 5
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'h1_count': len(h1_tags),
            'total_headings': len(headings),
            'heading_structure': heading_levels,
            'score': max(0, score)
        }
    
    def validate_content_quality(self, soup: BeautifulSoup) -> Dict:
        """Valide la qualité du contenu."""
        # Extraire le contenu principal
        content_div = soup.find('div', class_='article-content')
        if content_div:
            content_text = content_div.get_text(separator=' ', strip=True)
        else:
            # Fallback: tout le contenu du body moins header/footer
            body = soup.find('body')
            if body:
                # Supprimer header et footer pour ne garder que le contenu
                for element in body.find_all(['header', 'footer', 'nav']):
                    element.decompose()
                content_text = body.get_text(separator=' ', strip=True)
            else:
                content_text = soup.get_text(separator=' ', strip=True)
        
        # Nettoyer le texte
        content_text = re.sub(r'\s+', ' ', content_text).strip()
        word_count = len(content_text.split())
        
        issues = []
        warnings = []
        
        # Vérifier la longueur du contenu
        if word_count < self.rules['content_min_words']:
            issues.append(f"Contenu trop court ({word_count} mots, minimum {self.rules['content_min_words']})")
        elif word_count > self.rules['content_max_words']:
            warnings.append(f"Contenu très long ({word_count} mots, optimal < {self.rules['content_max_words']})")
        
        # Analyser la densité des mots-clés
        content_lower = content_text.lower()
        keyword_analysis = {}
        
        for keyword in self.target_keywords:
            count = content_lower.count(keyword.lower())
            density = (count / word_count) * 100 if word_count > 0 else 0
            keyword_analysis[keyword] = {
                'count': count,
                'density': density
            }
        
        # Vérifier la densité globale des mots-clés principaux
        main_keywords = ['séminaire', 'vosges', 'entreprise']
        total_keyword_density = sum(
            keyword_analysis.get(kw, {}).get('density', 0) 
            for kw in main_keywords
        )
        
        if total_keyword_density < self.rules['keyword_density_min']:
            warnings.append(f"Densité de mots-clés faible ({total_keyword_density:.1f}%)")
        elif total_keyword_density > self.rules['keyword_density_max']:
            warnings.append(f"Densité de mots-clés élevée ({total_keyword_density:.1f}%)")
        
        # Vérifier la lisibilité basique
        sentences = re.split(r'[.!?]+', content_text)
        avg_sentence_length = word_count / len([s for s in sentences if s.strip()]) if sentences else 0
        
        if avg_sentence_length > 25:
            warnings.append(f"Phrases longues en moyenne ({avg_sentence_length:.1f} mots/phrase)")
        
        score = 100
        score -= len(issues) * 20
        score -= len(warnings) * 5
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'word_count': word_count,
            'keyword_analysis': keyword_analysis,
            'total_keyword_density': total_keyword_density,
            'avg_sentence_length': avg_sentence_length,
            'score': max(0, score)
        }
    
    def validate_internal_links(self, soup: BeautifulSoup) -> Dict:
        """Valide les liens internes."""
        all_links = soup.find_all('a', href=True)
        
        internal_links = []
        external_links = []
        seminary_links = []
        
        for link in all_links:
            href = link.get('href', '')
            
            # Identifier le type de lien
            if href.startswith('http'):
                domain = urlparse(href).netloc
                if self.seminary_domain in domain or self.seminary_main_domain in domain:
                    seminary_links.append(link)
                else:
                    external_links.append(link)
            elif href.startswith('/') or href.startswith('./') or href.startswith('../'):
                internal_links.append(link)
            elif href.startswith('#'):
                # Liens d'ancrage - ignorés pour cette validation
                pass
        
        issues = []
        warnings = []
        
        # Vérifier le nombre de liens Seminary
        if len(seminary_links) < self.rules['internal_links_min']:
            warnings.append(f"Peu de liens vers Seminary ({len(seminary_links)}, recommandé ≥ {self.rules['internal_links_min']})")
        elif len(seminary_links) > self.rules['internal_links_max']:
            warnings.append(f"Beaucoup de liens Seminary ({len(seminary_links)}, optimal ≤ {self.rules['internal_links_max']})")
        
        # Vérifier les textes d'ancre
        poor_anchor_texts = []
        for link in seminary_links + internal_links:
            anchor_text = link.get_text().strip().lower()
            if anchor_text in ['cliquez ici', 'ici', 'lire plus', 'voir plus', 'click here']:
                poor_anchor_texts.append(anchor_text)
        
        if poor_anchor_texts:
            warnings.append(f"Textes d'ancre peu descriptifs: {', '.join(set(poor_anchor_texts))}")
        
        # Vérifier les liens externes sans nofollow
        external_without_nofollow = []
        for link in external_links:
            rel = link.get('rel', [])
            if isinstance(rel, str):
                rel = [rel]
            if 'nofollow' not in rel:
                external_without_nofollow.append(link.get('href'))
        
        if len(external_without_nofollow) > 3:
            warnings.append(f"{len(external_without_nofollow)} liens externes sans nofollow")
        
        score = 100
        score -= len(issues) * 20
        score -= len(warnings) * 5
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'seminary_links_count': len(seminary_links),
            'internal_links_count': len(internal_links),
            'external_links_count': len(external_links),
            'poor_anchor_texts': poor_anchor_texts,
            'score': max(0, score)
        }
    
    def validate_images(self, soup: BeautifulSoup) -> Dict:
        """Valide les images et leurs attributs SEO."""
        images = soup.find_all('img')
        
        issues = []
        warnings = []
        
        images_without_alt = []
        images_without_title = []
        large_images = []
        
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            title = img.get('title', '')
            
            # Vérifier l'attribut alt
            if not alt:
                images_without_alt.append(src)
            elif len(alt) > 125:
                warnings.append(f"Attribut alt très long pour {src}")
            
            # Vérifier l'attribut title (optionnel mais recommandé)
            if not title:
                images_without_title.append(src)
        
        if images_without_alt and self.rules['images_alt_required']:
            issues.append(f"{len(images_without_alt)} image(s) sans attribut alt")
        
        if len(images_without_title) > 0:
            warnings.append(f"{len(images_without_title)} image(s) sans attribut title")
        
        score = 100
        score -= len(issues) * 25
        score -= len(warnings) * 5
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_images': len(images),
            'images_without_alt': len(images_without_alt),
            'images_without_title': len(images_without_title),
            'score': max(0, score)
        }
    
    def validate_technical_seo(self, soup: BeautifulSoup) -> Dict:
        """Valide les aspects techniques SEO."""
        issues = []
        warnings = []
        
        # Vérifier la balise canonical
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            warnings.append("Balise canonical manquante")
        else:
            canonical_url = canonical.get('href', '')
            if not canonical_url.startswith('https://'):
                warnings.append("URL canonical non HTTPS")
        
        # Vérifier les meta robots
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        if not robots_meta:
            warnings.append("Meta robots manquante")
        else:
            robots_content = robots_meta.get('content', '').lower()
            if 'noindex' in robots_content:
                issues.append("Page configurée en noindex")
            if 'nofollow' in robots_content:
                warnings.append("Page configurée en nofollow")
        
        # Vérifier les Open Graph tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        og_description = soup.find('meta', attrs={'property': 'og:description'})
        og_type = soup.find('meta', attrs={'property': 'og:type'})
        
        if not og_title:
            warnings.append("Open Graph title manquant")
        if not og_description:
            warnings.append("Open Graph description manquante")
        if not og_type:
            warnings.append("Open Graph type manquant")
        
        # Vérifier les Twitter Cards
        twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
        if not twitter_card:
            warnings.append("Twitter Card manquante")
        
        # Vérifier la structure JSON-LD (optionnel)
        json_ld = soup.find('script', attrs={'type': 'application/ld+json'})
        if not json_ld:
            warnings.append("Données structurées JSON-LD manquantes")
        
        score = 100
        score -= len(issues) * 20
        score -= len(warnings) * 3
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'has_canonical': canonical is not None,
            'has_og_tags': all([og_title, og_description, og_type]),
            'has_twitter_card': twitter_card is not None,
            'has_json_ld': json_ld is not None,
            'score': max(0, score)
        }
    
    def perform_full_audit(self, html_content: str) -> Dict:
        """
        Effectue un audit SEO complet de l'article.
        
        Args:
            html_content: Contenu HTML de l'article
            
        Returns:
            Rapport d'audit complet avec score global
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Exécuter toutes les validations
            results = {
                'html_structure': self.validate_html_structure(html_content),
                'title': self.validate_title_tag(soup),
                'meta_description': self.validate_meta_description(soup),
                'headings': self.validate_heading_structure(soup),
                'content': self.validate_content_quality(soup),
                'links': self.validate_internal_links(soup),
                'images': self.validate_images(soup),
                'technical': self.validate_technical_seo(soup)
            }
            
            # Calculer le score global
            total_score = 0
            total_weight = 0
            
            weights = {
                'html_structure': 1.0,
                'title': 2.0,
                'meta_description': 1.5,
                'headings': 1.5,
                'content': 2.5,
                'links': 1.0,
                'images': 0.5,
                'technical': 1.0
            }
            
            for category, weight in weights.items():
                if category in results:
                    score = results[category].get('score', 0)
                    total_score += score * weight
                    total_weight += weight
            
            global_score = round(total_score / total_weight if total_weight > 0 else 0, 1)
            
            # Identifier les problèmes majeurs
            major_issues = []
            all_warnings = []
            
            for category, result in results.items():
                if not result.get('valid', True):
                    major_issues.extend(result.get('issues', []))
                all_warnings.extend(result.get('warnings', []))
            
            # Déterminer le statut global
            status = 'excellent' if global_score >= 90 else \
                    'good' if global_score >= 75 else \
                    'needs_improvement' if global_score >= 60 else \
                    'poor'
            
            return {
                'global_score': global_score,
                'status': status,
                'has_major_issues': len(major_issues) > 0,
                'major_issues': major_issues,
                'all_warnings': all_warnings,
                'detailed_results': results,
                'recommendations': self._generate_recommendations(results)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'audit SEO: {e}")
            return {
                'global_score': 0,
                'status': 'error',
                'has_major_issues': True,
                'major_issues': [f"Erreur d'audit: {str(e)}"],
                'all_warnings': [],
                'detailed_results': {},
                'recommendations': []
            }
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Génère des recommandations basées sur les résultats d'audit."""
        recommendations = []
        
        # Recommandations pour le titre
        title_result = results.get('title', {})
        if title_result.get('length', 0) < 30:
            recommendations.append("Allonger le titre (30-60 caractères optimal)")
        
        # Recommandations pour le contenu
        content_result = results.get('content', {})
        if content_result.get('word_count', 0) < 500:
            recommendations.append("Enrichir le contenu (minimum 500 mots recommandé)")
        
        # Recommandations pour les liens
        links_result = results.get('links', {})
        if links_result.get('seminary_links_count', 0) < 2:
            recommendations.append("Ajouter plus de liens vers les pages Seminary")
        
        # Recommandations techniques
        technical_result = results.get('technical', {})
        if not technical_result.get('has_og_tags', False):
            recommendations.append("Ajouter les balises Open Graph complètes")
        
        return recommendations[:5]  # Limiter à 5 recommandations principales


def main():
    """Point d'entrée pour les tests CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SEO Validator - Seminary Blog")
    parser.add_argument('file', help='Fichier HTML à analyser')
    parser.add_argument('--detailed', action='store_true', help='Affichage détaillé')
    
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        validator = SEOValidator()
        audit_result = validator.perform_full_audit(html_content)
        
        print(f"=== AUDIT SEO - {args.file} ===")
        print(f"Score global: {audit_result['global_score']}/100")
        print(f"Statut: {audit_result['status']}")
        
        if audit_result['major_issues']:
            print("\n❌ PROBLÈMES MAJEURS:")
            for issue in audit_result['major_issues']:
                print(f"  - {issue}")
        
        if audit_result['all_warnings']:
            print(f"\n⚠️  AVERTISSEMENTS ({len(audit_result['all_warnings'])}):")
            for warning in audit_result['all_warnings'][:5]:  # Afficher les 5 premiers
                print(f"  - {warning}")
        
        if audit_result['recommendations']:
            print("\n💡 RECOMMANDATIONS:")
            for rec in audit_result['recommendations']:
                print(f"  - {rec}")
        
        if args.detailed:
            print("\n=== DÉTAILS PAR CATÉGORIE ===")
            for category, result in audit_result['detailed_results'].items():
                print(f"\n{category.upper()}: {result.get('score', 0)}/100")
                if result.get('issues'):
                    for issue in result['issues']:
                        print(f"  ❌ {issue}")
                if result.get('warnings'):
                    for warning in result['warnings']:
                        print(f"  ⚠️  {warning}")
        
    except FileNotFoundError:
        print(f"Fichier non trouvé: {args.file}")
    except Exception as e:
        print(f"Erreur: {e}")


if __name__ == "__main__":
    main() 