#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seminary Integrator - Intégration automatique des liens Seminary
Seminary Blog System - Système de Blog Automatisé SEO-First

Ce module injecte automatiquement des liens pertinents vers les pages
Seminary dans les articles, en fonction du contexte et des mots-clés.
"""

import re
import logging
import random
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup, Tag

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeminaryIntegrator:
    """Intégrateur de liens Seminary pour les articles de blog."""
    
    def __init__(self):
        """Initialise l'intégrateur avec les liens et règles Seminary."""
        
        # Pages Seminary principales avec contextes d'usage
        self.seminary_pages = {
            'statistiques': {
                'url': 'https://goseminary.com/statistics',
                'title': 'Statistiques des séminaires Seminary',
                'description': 'Données et métriques sur les séminaires organisés',
                'keywords': ['statistiques', 'données', 'métriques', 'résultats', 'chiffres', 'analyse'],
                'contexts': ['performance', 'efficacité', 'résultats', 'évaluation', 'impact']
            },
            'reservations': {
                'url': 'https://goseminary.com/reservations',
                'title': 'Réserver votre séminaire Seminary',
                'description': 'Système de réservation en ligne pour vos événements',
                'keywords': ['réservation', 'réserver', 'booking', 'planifier', 'organiser', 'dates'],
                'contexts': ['planification', 'organisation', 'réservation', 'agenda', 'disponibilités']
            },
            'prestataires': {
                'url': 'https://goseminary.com/providers',
                'title': 'Prestataires partenaires Seminary',
                'description': 'Réseau de prestataires qualifiés pour vos séminaires',
                'keywords': ['prestataires', 'partenaires', 'fournisseurs', 'services', 'équipe', 'experts'],
                'contexts': ['partenariat', 'collaboration', 'expertise', 'services', 'qualité']
            },
            'actualites': {
                'url': 'https://goseminary.com/news',
                'title': 'Actualités Seminary',
                'description': 'Dernières nouvelles et mises à jour Seminary',
                'keywords': ['actualités', 'nouvelles', 'news', 'informations', 'mise à jour'],
                'contexts': ['nouveautés', 'évolutions', 'annonces', 'développements']
            },
            'accueil': {
                'url': 'https://goseminary.com/',
                'title': 'Seminary - Organisateur de séminaires dans les Vosges',
                'description': 'Plateforme complète pour organiser vos séminaires d\'entreprise',
                'keywords': ['seminary', 'séminaires', 'vosges', 'entreprise', 'organisation'],
                'contexts': ['présentation', 'découverte', 'services', 'offre globale']
            }
        }
        
        # Templates de liens contextuels
        self.link_templates = {
            'call_to_action': [
                "Découvrez nos {service} sur Seminary",
                "En savoir plus sur {service}",
                "Consultez {service} Seminary",
                "Accédez à {service}"
            ],
            'contextual': [
                "comme le montrent nos {service}",
                "selon nos {service}",
                "grâce à nos {service}",
                "via notre système de {service}"
            ],
            'natural': [
                "nos {service}",
                "le système {service} de Seminary",
                "notre plateforme {service}",
                "les {service} Seminary"
            ]
        }
        
        # Règles d'intégration
        self.integration_rules = {
            'max_links_per_article': 4,
            'min_words_between_links': 150,
            'preferred_positions': ['middle', 'end'],  # début, milieu, fin
            'avoid_link_clustering': True,
            'natural_integration_priority': True
        }
    
    def analyze_article_content(self, content: str, title: str) -> Dict:
        """
        Analyse le contenu de l'article pour identifier les opportunités d'intégration.
        
        Args:
            content: Contenu textuel de l'article
            title: Titre de l'article
            
        Returns:
            Analyse avec mots-clés et contextes identifiés
        """
        full_text = f"{title} {content}".lower()
        
        # Identifier les mots-clés Seminary présents
        found_keywords = {}
        for page_key, page_info in self.seminary_pages.items():
            matches = []
            for keyword in page_info['keywords']:
                if keyword in full_text:
                    # Compter les occurrences et positions
                    positions = [m.start() for m in re.finditer(re.escape(keyword), full_text)]
                    matches.extend([(keyword, pos) for pos in positions])
            
            if matches:
                found_keywords[page_key] = {
                    'matches': matches,
                    'score': len(matches),
                    'relevance': self._calculate_relevance_score(matches, page_info, full_text)
                }
        
        # Analyser les contextes
        context_analysis = self._analyze_contexts(full_text)
        
        # Identifier les emplacements potentiels pour les liens
        potential_positions = self._find_link_positions(content)
        
        return {
            'found_keywords': found_keywords,
            'context_analysis': context_analysis,
            'potential_positions': potential_positions,
            'word_count': len(content.split()),
            'complexity_score': self._calculate_content_complexity(content)
        }
    
    def _calculate_relevance_score(self, matches: List[Tuple], page_info: Dict, text: str) -> float:
        """Calcule un score de pertinence pour une page Seminary."""
        score = len(matches) * 1.0  # Score de base
        
        # Bonus pour les contextes trouvés
        for context in page_info['contexts']:
            if context in text:
                score += 0.5
        
        # Bonus pour la diversité des mots-clés
        unique_keywords = set([match[0] for match in matches])
        if len(unique_keywords) > 1:
            score += 1.0
        
        return score
    
    def _analyze_contexts(self, text: str) -> Dict:
        """Analyse les contextes dans le texte."""
        contexts = {
            'organizational': 0,
            'performance': 0,
            'planning': 0,
            'collaboration': 0,
            'innovation': 0
        }
        
        context_keywords = {
            'organizational': ['organisation', 'organiser', 'structure', 'gestion', 'management'],
            'performance': ['performance', 'résultats', 'efficacité', 'productivité', 'amélioration'],
            'planning': ['planification', 'planning', 'agenda', 'programmation', 'calendrier'],
            'collaboration': ['collaboration', 'équipe', 'teamwork', 'partenariat', 'ensemble'],
            'innovation': ['innovation', 'nouveauté', 'créativité', 'développement', 'évolution']
        }
        
        for context, keywords in context_keywords.items():
            for keyword in keywords:
                contexts[context] += text.count(keyword)
        
        return contexts
    
    def _find_link_positions(self, content: str) -> List[Dict]:
        """Identifie les positions potentielles pour insérer des liens."""
        sentences = re.split(r'[.!?]+', content)
        positions = []
        
        current_pos = 0
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Position dans le texte
            position_type = 'beginning' if i < len(sentences) * 0.3 else \
                           'middle' if i < len(sentences) * 0.7 else 'end'
            
            # Analyser le contenu de la phrase
            sentence_lower = sentence.lower()
            link_opportunities = []
            
            for page_key, page_info in self.seminary_pages.items():
                keyword_matches = sum(1 for kw in page_info['keywords'] if kw in sentence_lower)
                if keyword_matches > 0:
                    link_opportunities.append({
                        'page': page_key,
                        'keywords_count': keyword_matches,
                        'sentence': sentence[:100] + '...' if len(sentence) > 100 else sentence
                    })
            
            if link_opportunities:
                positions.append({
                    'sentence_index': i,
                    'position_type': position_type,
                    'character_position': current_pos,
                    'opportunities': link_opportunities,
                    'sentence_length': len(sentence.split())
                })
            
            current_pos += len(sentence) + 1
        
        return positions
    
    def _calculate_content_complexity(self, content: str) -> float:
        """Calcule un score de complexité du contenu."""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = len(words) / len([s for s in sentences if s.strip()]) if sentences else 0
        
        complexity = (avg_word_length * 0.3) + (avg_sentence_length * 0.7)
        return min(complexity / 20, 1.0)  # Normaliser entre 0 et 1
    
    def generate_integration_plan(self, analysis: Dict) -> Dict:
        """
        Génère un plan d'intégration des liens Seminary.
        
        Args:
            analysis: Résultat de analyze_article_content
            
        Returns:
            Plan détaillé pour l'intégration des liens
        """
        plan = {
            'recommended_links': [],
            'integration_strategy': 'natural',
            'total_links': 0,
            'confidence_score': 0.0
        }
        
        # Trier les pages par pertinence
        sorted_pages = sorted(
            analysis['found_keywords'].items(),
            key=lambda x: x[1]['relevance'],
            reverse=True
        )
        
        # Sélectionner les liens à intégrer
        selected_positions = []
        for page_key, page_data in sorted_pages[:self.integration_rules['max_links_per_article']]:
            # Trouver la meilleure position pour ce lien
            best_position = self._find_best_position_for_page(
                page_key, analysis['potential_positions'], selected_positions
            )
            
            if best_position:
                link_info = self._create_link_info(page_key, best_position, page_data)
                plan['recommended_links'].append(link_info)
                selected_positions.append(best_position['character_position'])
        
        plan['total_links'] = len(plan['recommended_links'])
        plan['confidence_score'] = self._calculate_plan_confidence(plan, analysis)
        
        return plan
    
    def _find_best_position_for_page(self, page_key: str, positions: List[Dict], 
                                   used_positions: List[int]) -> Optional[Dict]:
        """Trouve la meilleure position pour un lien vers une page Seminary."""
        page_info = self.seminary_pages[page_key]
        
        # Filtrer les positions qui correspondent à cette page
        relevant_positions = []
        for pos in positions:
            for opp in pos['opportunities']:
                if opp['page'] == page_key:
                    # Vérifier la distance avec les liens existants
                    min_distance = float('inf')
                    for used_pos in used_positions:
                        distance = abs(pos['character_position'] - used_pos)
                        min_distance = min(min_distance, distance)
                    
                    if min_distance > self.integration_rules['min_words_between_links']:
                        relevant_positions.append({
                            **pos,
                            'distance_score': min_distance,
                            'keyword_score': opp['keywords_count']
                        })
        
        if not relevant_positions:
            return None
        
        # Trier par score combiné
        relevant_positions.sort(
            key=lambda x: (x['keyword_score'] * 2 + x['distance_score'] / 100),
            reverse=True
        )
        
        return relevant_positions[0]
    
    def _create_link_info(self, page_key: str, position: Dict, page_data: Dict) -> Dict:
        """Crée les informations détaillées pour un lien."""
        page_info = self.seminary_pages[page_key]
        
        # Choisir le type de lien basé sur la position
        link_type = 'natural' if position['position_type'] == 'middle' else \
                   'contextual' if position['position_type'] == 'beginning' else \
                   'call_to_action'
        
        # Générer le texte du lien
        link_text = self._generate_link_text(page_key, link_type, page_data)
        
        return {
            'page_key': page_key,
            'url': page_info['url'],
            'link_text': link_text,
            'title': page_info['title'],
            'position': position,
            'link_type': link_type,
            'confidence': page_data['relevance'] / 5.0  # Normaliser
        }
    
    def _generate_link_text(self, page_key: str, link_type: str, page_data: Dict) -> str:
        """Génère un texte de lien naturel et optimisé."""
        page_info = self.seminary_pages[page_key]
        
        # Sélectionner un template approprié
        templates = self.link_templates.get(link_type, self.link_templates['natural'])
        template = random.choice(templates)
        
        # Adapter le service selon la page
        service_names = {
            'statistiques': 'statistiques détaillées',
            'reservations': 'système de réservation',
            'prestataires': 'réseau de prestataires',
            'actualites': 'dernières actualités',
            'accueil': 'plateforme Seminary'
        }
        
        service_name = service_names.get(page_key, page_info['title'])
        
        # Générer le texte final
        if '{service}' in template:
            link_text = template.format(service=service_name)
        else:
            link_text = template
        
        return link_text
    
    def _calculate_plan_confidence(self, plan: Dict, analysis: Dict) -> float:
        """Calcule un score de confiance pour le plan d'intégration."""
        if not plan['recommended_links']:
            return 0.0
        
        # Score basé sur la pertinence moyenne des liens
        avg_confidence = sum(link['confidence'] for link in plan['recommended_links']) / len(plan['recommended_links'])
        
        # Bonus pour la diversité des pages liées
        unique_pages = set(link['page_key'] for link in plan['recommended_links'])
        diversity_bonus = len(unique_pages) / len(plan['recommended_links'])
        
        # Malus si trop de liens ou trop peu
        optimal_links = min(3, max(1, analysis['word_count'] // 300))
        link_count_score = 1.0 - abs(len(plan['recommended_links']) - optimal_links) * 0.2
        
        confidence = (avg_confidence * 0.6) + (diversity_bonus * 0.2) + (link_count_score * 0.2)
        return min(confidence, 1.0)
    
    def integrate_links_into_html(self, html_content: str, integration_plan: Dict) -> str:
        """
        Intègre les liens Seminary dans le contenu HTML.
        
        Args:
            html_content: Contenu HTML de l'article
            integration_plan: Plan d'intégration généré
            
        Returns:
            HTML modifié avec les liens intégrés
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Trouver le contenu principal de l'article
            content_div = soup.find('div', class_='article-content')
            if not content_div:
                logger.warning("Div article-content non trouvée, utilisation du body")
                content_div = soup.find('body')
            
            if not content_div:
                logger.error("Impossible de localiser le contenu à modifier")
                return html_content
            
            # Extraire le texte pour repérage des positions
            text_content = content_div.get_text()
            
            # Intégrer chaque lien
            links_added = 0
            for link_info in integration_plan['recommended_links']:
                if self._integrate_single_link(content_div, link_info, text_content):
                    links_added += 1
            
            logger.info(f"Liens Seminary intégrés: {links_added}/{len(integration_plan['recommended_links'])}")
            return str(soup)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'intégration des liens: {e}")
            return html_content
    
    def _integrate_single_link(self, content_div: Tag, link_info: Dict, text_content: str) -> bool:
        """Intègre un seul lien dans la section de contenu."""
        try:
            # Accès sécurisé aux données de position
            position_data = link_info.get('position', {})
            
            # Essayer différentes clés possibles pour obtenir la phrase cible
            target_sentence = None
            if isinstance(position_data, dict):
                # Essayer les clés possibles
                if 'sentence' in position_data:
                    target_sentence = position_data['sentence']
                elif 'opportunities' in position_data and position_data['opportunities']:
                    target_sentence = position_data['opportunities'][0].get('sentence', '')
                elif 'text' in position_data:
                    target_sentence = position_data['text']
            
            if not target_sentence:
                # Fallback: utiliser le mot-clé cible pour trouver une phrase
                target_keyword = link_info.get('target_keyword', '')
                if target_keyword:
                    # Chercher une phrase contenant le mot-clé
                    for p_tag in content_div.find_all('p'):
                        if target_keyword.lower() in p_tag.get_text().lower():
                            target_sentence = p_tag.get_text()[:100]  # Premiers 100 caractères
                            break
            
            if not target_sentence:
                logger.warning(f"Impossible de trouver une phrase cible pour le lien: {link_info.get('page_key', 'unknown')}")
                return False
            
            # Chercher le paragraphe correspondant
            paragraphs = content_div.find_all('p')
            for p_tag in paragraphs:
                p_text = p_tag.get_text()
                if target_sentence[:50] in p_text:  # Match partiel pour robustesse
                    # Créer le lien
                    link_tag = content_div.new_tag(
                        'a',
                        href=link_info.get('url', '#'),
                        title=link_info.get('title', ''),
                        target='_blank',
                        rel='noopener',
                        **{'class': 'seminary-link'}
                    )
                    link_tag.string = link_info.get('link_text', link_info.get('target_keyword', 'Seminary'))
                    
                    # Remplacer le terme
                    if self._replace_term_with_link(p_tag, link_info, link_tag):
                        logger.info(f"Lien intégré pour: {link_info.get('page_key', 'unknown')}")
                        return True
                    break
            
            logger.warning(f"Impossible de trouver une position pour le lien: {link_info.get('page_key', 'unknown')}")
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de l'intégration d'un lien: {e}")
            return False

    def _replace_term_with_link(self, p_tag: Tag, link_info: Dict, link_tag: Tag) -> bool:
        """Remplace un terme par un lien dans un paragraphe."""
        
        best_term_to_replace = link_info.get('target_keyword')
        if not best_term_to_replace:
            logger.warning("Aucun mot-clé cible pour le remplacement.")
            return False

        original_text = p_tag.get_text()
        pattern = re.compile(r'\b' + re.escape(best_term_to_replace) + r'\b', re.IGNORECASE)
        match = pattern.search(original_text)
        
        if match:
            start, end = match.span()
            before_text = original_text[:start]
            after_text = original_text[end:]
            
            p_tag.clear()
            p_tag.append(before_text)
            p_tag.append(link_tag)
            p_tag.append(after_text)
            return True
        
        return False
    
    def process_article(self, html_content: str, article_title: str = "") -> Dict:
        """
        Traite un article complet pour l'intégration Seminary.
        
        Args:
            html_content: Contenu HTML de l'article
            article_title: Titre de l'article (optionnel)
            
        Returns:
            Résultat du traitement avec HTML modifié et statistiques
        """
        # Extraire le contenu textuel pour analyse
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.get_text()
        
        if not article_title:
            title_tag = soup.find('h1')
            article_title = title_tag.get_text() if title_tag else ""
        
        # Analyser le contenu
        analysis = self.analyze_article_content(text_content, article_title)
        
        # Générer le plan d'intégration
        integration_plan = self.generate_integration_plan(analysis)
        
        # Intégrer les liens si le plan est viable
        if integration_plan['confidence_score'] > 0.3:  # Seuil de confiance minimum
            modified_html = self.integrate_links_into_html(html_content, integration_plan)
        else:
            modified_html = html_content
            logger.info("Plan d'intégration rejeté (confiance trop faible)")
        
        return {
            'modified_html': modified_html,
            'analysis': analysis,
            'integration_plan': integration_plan,
            'links_added': len(integration_plan['recommended_links']) if integration_plan['confidence_score'] > 0.3 else 0,
            'confidence_score': integration_plan['confidence_score']
        }


def main():
    """Point d'entrée pour les tests CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seminary Integrator - Seminary Blog")
    parser.add_argument('file', help='Fichier HTML à traiter')
    parser.add_argument('--analyze-only', action='store_true', help='Analyser sans modifier')
    parser.add_argument('--output', help='Fichier de sortie (défaut: remplace l\'original)')
    
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        integrator = SeminaryIntegrator()
        result = integrator.process_article(html_content)
        
        print(f"=== INTÉGRATION SEMINARY - {args.file} ===")
        print(f"Score de confiance: {result['confidence_score']:.2f}")
        print(f"Liens ajoutés: {result['links_added']}")
        
        if result['integration_plan']['recommended_links']:
            print("\n📎 LIENS RECOMMANDÉS:")
            for link in result['integration_plan']['recommended_links']:
                print(f"  - {link['link_text']} → {link['page_key']}")
        
        if not args.analyze_only and result['links_added'] > 0:
            output_file = args.output or args.file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['modified_html'])
            print(f"\n✅ Fichier modifié sauvegardé: {output_file}")
        
    except FileNotFoundError:
        print(f"Fichier non trouvé: {args.file}")
    except Exception as e:
        print(f"Erreur: {e}")


if __name__ == "__main__":
    main() 