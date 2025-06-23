#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seminary Blog - Générateur de Fallback Robuste
Génère des articles Seminary valides même en cas d'échec de l'API principale.
"""

import os
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FallbackArticleGenerator:
    """Générateur d'articles de fallback pour Seminary Blog."""
    
    def __init__(self):
        """Initialise le générateur de fallback."""
        self.base_path = Path(__file__).parent.parent
        self.templates_dir = self.base_path / 'templates'
        
        # Banques de contenu Seminary
        self.seminary_content = {
            'titres': [
                "Les Vosges : La Destination Idéale pour Vos Séminaires d'Entreprise",
                "Séminaires d'Entreprise dans les Vosges : L'Excellence Naturelle",
                "Team Building et Séminaires : Pourquoi Choisir les Vosges",
                "Les Vosges : Cadre Exceptionnel pour Vos Événements Corporate",
                "Séminaires Innovants dans les Vosges : L'Atout Seminary",
                "Formation et Cohésion d'Équipe : L'Expérience Vosges Seminary",
                "Les Vosges : Votre Partenaire Idéal pour des Séminaires Réussis",
                "Séminaires d'Exception dans les Vosges : La Garantie Seminary"
            ],
            
            'introductions': [
                "Dans un monde professionnel en constante évolution, l'organisation de séminaires d'entreprise efficaces est devenue un enjeu majeur pour les entreprises. Les Vosges, avec leur cadre naturel exceptionnel et leur accessibilité, offrent un environnement idéal pour ces événements cruciaux.",
                "Organiser un séminaire d'entreprise réussi nécessite de choisir le bon environnement. Les Vosges se distinguent comme une destination privilégiée, combinant nature préservée, infrastructures modernes et expertise Seminary pour garantir le succès de vos événements.",
                "Les séminaires d'entreprise dans les Vosges connaissent un succès grandissant. Cette région offre un cadre unique, mêlant détente naturelle et productivité professionnelle, particulièrement adapté aux besoins des entreprises modernes.",
                "Choisir les Vosges pour votre prochain séminaire d'entreprise, c'est opter pour l'excellence. Cette région montagnarde propose un environnement stimulant qui favorise la créativité, la cohésion d'équipe et l'efficacité des formations."
            ],
            
            'avantages_vosges': [
                "**Cadre naturel exceptionnel** : Les montagnes vosgiennes offrent un environnement apaisant qui favorise la concentration et la créativité de vos équipes.",
                "**Accessibilité optimale** : Situées au cœur de l'Europe, les Vosges sont facilement accessibles depuis la France, l'Allemagne et la Suisse.",
                "**Infrastructures modernes** : La région dispose d'équipements de pointe pour accueillir vos séminaires dans les meilleures conditions.",
                "**Air pur et détente** : L'environnement montagnard contribue au bien-être des participants et à l'efficacité des sessions de travail.",
                "**Diversité des activités** : Des activités team building variées sont disponibles pour renforcer la cohésion d'équipe.",
                "**Expertise Seminary** : Bénéficiez de l'accompagnement d'experts pour une organisation parfaite de votre événement."
            ],
            
            'activites_team_building': [
                "**Randonnées en équipe** : Explorez les sentiers vosgiens pour renforcer l'esprit d'équipe dans un cadre naturel inspirant.",
                "**Ateliers artisanaux** : Découvrez les traditions locales à travers des activités créatives favorisant la collaboration.",
                "**Challenges outdoor** : Participez à des défis en pleine nature qui développent l'esprit d'équipe et la communication.",
                "**Séances de méditation en forêt** : Profitez du calme de la nature pour des activités de développement personnel.",
                "**Activités sportives** : VTT, escalade ou sports d'hiver selon la saison pour dynamiser vos équipes.",
                "**Ateliers culinaires** : Découvrez la gastronomie vosgienne en équipe pour créer des liens authentiques."
            ],
            
            'conseils_organisation': [
                "**Planification anticipée** : Réservez vos dates plusieurs mois à l'avance pour garantir la disponibilité des meilleurs sites.",
                "**Définition d'objectifs clairs** : Établissez des objectifs précis pour votre séminaire afin d'optimiser son efficacité.",
                "**Choix du lieu adapté** : Sélectionnez un site correspondant à la taille de votre groupe et à vos besoins techniques.",
                "**Programme équilibré** : Alternez sessions de travail et moments de détente pour maintenir l'engagement des participants.",
                "**Logistique optimisée** : Prévoyez transport, hébergement et restauration en fonction des spécificités de votre groupe.",
                "**Accompagnement professionnel** : Faites appel à Seminary pour bénéficier d'une expertise reconnue dans l'organisation d'événements."
            ],
            
            'seminary_services': [
                "Seminary vous accompagne dans l'organisation complète de vos séminaires d'entreprise dans les Vosges. Notre expertise reconnue garantit le succès de vos événements professionnels.",
                "Avec Seminary, bénéficiez d'un service sur-mesure adapté à vos besoins spécifiques. De la conception à la réalisation, nous gérons tous les aspects de votre séminaire.",
                "L'équipe Seminary met son savoir-faire à votre disposition pour créer des séminaires mémorables et efficaces. Nous connaissons parfaitement la région vosgienne et ses atouts.",
                "Choisir Seminary, c'est s'assurer d'un accompagnement professionnel de A à Z. Notre réseau de partenaires locaux garantit la qualité de chaque prestation.",
                "Seminary propose des solutions innovantes pour vos séminaires d'entreprise. Notre approche personnalisée s'adapte à votre culture d'entreprise et vos objectifs."
            ],
            
            'conclusions': [
                "Les Vosges représentent le choix idéal pour organiser des séminaires d'entreprise mémorables et efficaces. Avec l'expertise Seminary, transformez votre prochain événement professionnel en véritable succès.",
                "Optez pour les Vosges et Seminary pour votre prochain séminaire d'entreprise. Cette combinaison gagnante vous garantit un événement exceptionnel qui marquera durablement vos équipes.",
                "En choisissant les Vosges avec Seminary, vous investissez dans la réussite de vos équipes. Contactez-nous dès aujourd'hui pour organiser votre séminaire d'exception.",
                "Les Vosges et Seminary : le duo parfait pour des séminaires d'entreprise réussis. Donnez une nouvelle dimension à vos événements professionnels dans ce cadre d'exception."
            ]
        }
    
    def generate_fallback_article(self, target_word_count: int = 400) -> Dict:
        """
        Génère un article de fallback complet et valide.
        
        Args:
            target_word_count: Nombre de mots ciblé
            
        Returns:
            Article généré avec métadonnées
        """
        logger.info(f"Génération d'un article de fallback ({target_word_count} mots ciblés)")
        
        # Sélection aléatoire du contenu
        titre = random.choice(self.seminary_content['titres'])
        introduction = random.choice(self.seminary_content['introductions'])
        conclusion = random.choice(self.seminary_content['conclusions'])
        
        # Construction de l'article avec sections variées
        article_html = f"<h1>{titre}</h1>\n\n"
        article_html += f"<p>{introduction}</p>\n\n"
        
        # Section avantages des Vosges
        article_html += "<h2>Les Atouts Uniques des Vosges pour vos Séminaires</h2>\n"
        avantages = random.sample(self.seminary_content['avantages_vosges'], 4)
        for avantage in avantages:
            article_html += f"<p>{avantage}</p>\n"
        article_html += "\n"
        
        # Section activités team building
        article_html += "<h2>Activités Team Building Incontournables</h2>\n"
        activites = random.sample(self.seminary_content['activites_team_building'], 3)
        for activite in activites:
            article_html += f"<p>{activite}</p>\n"
        article_html += "\n"
        
        # Section conseils d'organisation
        article_html += "<h2>Conseils pour Organiser votre Séminaire</h2>\n"
        conseils = random.sample(self.seminary_content['conseils_organisation'], 4)
        for conseil in conseils:
            article_html += f"<p>{conseil}</p>\n"
        article_html += "\n"
        
        # Section Seminary
        article_html += "<h2>Pourquoi Choisir Seminary pour votre Événement</h2>\n"
        services = random.sample(self.seminary_content['seminary_services'], 2)
        for service in services:
            article_html += f"<p>{service}</p>\n"
        article_html += "\n"
        
        # Conclusion
        article_html += "<h2>Conclusion</h2>\n"
        article_html += f"<p>{conclusion}</p>\n"
        
        # Vérifier et ajuster la longueur si nécessaire
        current_word_count = len(article_html.split())
        if current_word_count < target_word_count:
            article_html = self._extend_article(article_html, target_word_count)
        
        # Génération des métadonnées
        metadata = {
            'title': titre,
            'description': introduction[:160] + "..." if len(introduction) > 160 else introduction,
            'keywords': 'séminaire d\'entreprise, Vosges, team building, Seminary, formation, événement corporate',
            'word_count': len(article_html.split()),
            'generation_type': 'fallback',
            'generation_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Article de fallback généré: {metadata['word_count']} mots")
        
        return {
            'content': article_html,
            'metadata': metadata,
            'word_count': metadata['word_count'],
            'generation_timestamp': metadata['generation_timestamp']
        }
    
    def _extend_article(self, article_html: str, target_word_count: int) -> str:
        """Étend l'article pour atteindre le nombre de mots ciblé."""
        
        current_word_count = len(article_html.split())
        words_needed = target_word_count - current_word_count
        
        if words_needed <= 0:
            return article_html
        
        # Extensions possibles
        extensions = [
            "<p>Les Vosges offrent également un patrimoine culturel riche qui peut enrichir l'expérience de vos collaborateurs. Entre visites de musées locaux, découverte de l'artisanat traditionnel et exploration des sites historiques, les possibilités sont nombreuses pour créer des moments de team building authentiques.</p>",
            
            "<p>La gastronomie vosgienne constitue un atout supplémentaire pour vos séminaires. Les spécialités locales comme la munster, les confitures artisanales ou encore les plats traditionnels de montagne créent une ambiance conviviale propice aux échanges entre collaborateurs.</p>",
            
            "<p>L'hébergement dans les Vosges s'adapte parfaitement aux besoins des entreprises. Des hôtels de charme aux gîtes de groupe, en passant par les centres de séminaires spécialisés, vous trouverez la solution d'hébergement idéale pour votre événement.</p>",
            
            "<p>Les Vosges bénéficient d'un climat favorable qui permet l'organisation de séminaires tout au long de l'année. Chaque saison offre ses propres avantages : activités de montagne en hiver, randonnées printanières, événements outdoor en été, et couleurs automnales spectaculaires.</p>",
            
            "<p>La situation géographique des Vosges facilite l'organisation de séminaires internationaux. Proche de l'Allemagne et de la Suisse, cette région permet d'accueillir facilement des équipes européennes pour des événements multiculturels enrichissants.</p>"
        ]
        
        # Ajouter des extensions jusqu'à atteindre l'objectif
        extended_article = article_html
        available_extensions = extensions.copy()
        
        while len(extended_article.split()) < target_word_count and available_extensions:
            extension = random.choice(available_extensions)
            available_extensions.remove(extension)
            
            # Insérer l'extension avant la conclusion
            if "<h2>Conclusion</h2>" in extended_article:
                extended_article = extended_article.replace("<h2>Conclusion</h2>", f"{extension}\n\n<h2>Conclusion</h2>")
            else:
                extended_article += f"\n{extension}\n"
        
        return extended_article


def create_fallback_article(target_word_count: int = 400) -> str:
    """
    Fonction utilitaire pour créer un article de fallback.
    
    Args:
        target_word_count: Nombre de mots ciblé
        
    Returns:
        Chemin du fichier article créé
    """
    try:
        generator = FallbackArticleGenerator()
        article_data = generator.generate_fallback_article(target_word_count)
        
        # Générer le nom de fichier
        date_str = datetime.now().strftime('%Y-%m-%d')
        safe_title = "".join(c for c in article_data['metadata']['title'][:50] if c.isalnum() or c in (' ', '-')).rstrip()
        safe_title = safe_title.replace(' ', '-').lower()
        filename = f"{date_str}-{safe_title}.html"
        
        # Charger le template d'article
        template_path = Path(__file__).parent.parent / 'templates' / 'article_template.html'
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Variables pour le template
            template_vars = {
                'article_title': article_data['metadata']['title'],
                'meta_description': article_data['metadata']['description'],
                'article_content': article_data['content'],
                'publish_date': datetime.now().strftime('%d/%m/%Y'),
                'reading_time': max(1, article_data['word_count'] // 200),
                'filename': filename
            }
            
            # Remplacer les variables dans le template
            final_html = template_content
            for var_name, var_value in template_vars.items():
                final_html = final_html.replace(f'{{{{ {var_name} }}}}', str(var_value))
        else:
            # Template de fallback simple
            final_html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_data['metadata']['title']}</title>
    <meta name="description" content="{article_data['metadata']['description']}">
</head>
<body>
    <article>
        {article_data['content']}
    </article>
</body>
</html>'''
        
        # Sauvegarder l'article
        articles_dir = Path(__file__).parent.parent / 'articles'
        articles_dir.mkdir(exist_ok=True)
        
        file_path = articles_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        
        logger.info(f"✅ Article de fallback créé: {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de l'article de fallback: {e}")
        raise


if __name__ == "__main__":
    # Test du générateur de fallback
    article_path = create_fallback_article(500)
    print(f"Article de fallback créé: {article_path}") 