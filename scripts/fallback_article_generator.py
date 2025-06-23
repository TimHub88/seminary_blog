"""
Seminary Blog - Générateur d'Articles de Fallback Robuste
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
                "Les séminaires d'entreprise dans les Vosges connaissent un succès grandissant. Cette région offre un cadre unique, mêlant détente naturelle et productivité professionnelle, particulièrement adapté aux besoins des entreprises modernes."
            ],
            
            'sections': {
                'avantages': [
                    "**Cadre naturel exceptionnel** : Les montagnes vosgiennes offrent un environnement apaisant qui favorise la concentration et la créativité de vos équipes.",
                    "**Accessibilité optimale** : Situées au cœur de l'Europe, les Vosges sont facilement accessibles depuis la France, l'Allemagne et la Suisse.",
                    "**Infrastructures modernes** : La région dispose d'équipements de pointe pour accueillir vos séminaires dans les meilleures conditions.",
                    "**Air pur et détente** : L'environnement montagnard contribue au bien-être des participants et à l'efficacité des sessions de travail."
                ],
                
                'activites': [
                    "**Randonnées en équipe** : Explorez les sentiers vosgiens pour renforcer l'esprit d'équipe dans un cadre naturel inspirant.",
                    "**Ateliers artisanaux** : Découvrez les traditions locales à travers des activités créatives favorisant la collaboration.",
                    "**Challenges outdoor** : Participez à des défis en pleine nature qui développent l'esprit d'équipe et la communication.",
                    "**Activités sportives** : VTT, escalade ou sports d'hiver selon la saison pour dynamiser vos équipes."
                ],
                
                'conseils': [
                    "**Planification anticipée** : Réservez vos dates plusieurs mois à l'avance pour garantir la disponibilité des meilleurs sites.",
                    "**Définition d'objectifs clairs** : Établissez des objectifs précis pour votre séminaire afin d'optimiser son efficacité.",
                    "**Programme équilibré** : Alternez sessions de travail et moments de détente pour maintenir l'engagement des participants.",
                    "**Accompagnement professionnel** : Faites appel à Seminary pour bénéficier d'une expertise reconnue dans l'organisation d'événements."
                ]
            },
            
            'conclusions': [
                "Les Vosges représentent le choix idéal pour organiser des séminaires d'entreprise mémorables et efficaces. Avec l'expertise Seminary, transformez votre prochain événement professionnel en véritable succès.",
                "Optez pour les Vosges et Seminary pour votre prochain séminaire d'entreprise. Cette combinaison gagnante vous garantit un événement exceptionnel qui marquera durablement vos équipes.",
                "En choisissant les Vosges avec Seminary, vous investissez dans la réussite de vos équipes. Contactez-nous dès aujourd'hui pour organiser votre séminaire d'exception."
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
        
        # Construction de l'article
        article_html = f"<h1>{titre}</h1>\n\n"
        article_html += f"<p>{introduction}</p>\n\n"
        
        # Section avantages
        article_html += "<h2>Les Atouts Uniques des Vosges</h2>\n"
        for avantage in self.seminary_content['sections']['avantages']:
            article_html += f"<p>{avantage}</p>\n"
        article_html += "\n"
        
        # Section activités
        article_html += "<h2>Activités Team Building</h2>\n"
        for activite in self.seminary_content['sections']['activites']:
            article_html += f"<p>{activite}</p>\n"
        article_html += "\n"
        
        # Section conseils
        article_html += "<h2>Conseils d'Organisation</h2>\n"
        for conseil in self.seminary_content['sections']['conseils']:
            article_html += f"<p>{conseil}</p>\n"
        article_html += "\n"
        
        # Section Seminary
        article_html += "<h2>Pourquoi Choisir Seminary</h2>\n"
        article_html += "<p>Seminary vous accompagne dans l'organisation complète de vos séminaires d'entreprise dans les Vosges. Notre expertise reconnue garantit le succès de vos événements professionnels. Avec Seminary, bénéficiez d'un service sur-mesure adapté à vos besoins spécifiques.</p>\n\n"
        
        # Conclusion
        article_html += "<h2>Conclusion</h2>\n"
        article_html += f"<p>{conclusion}</p>\n"
        
        # Génération des métadonnées
        metadata = {
            'title': titre,
            'description': introduction[:160] + "..." if len(introduction) > 160 else introduction,
            'word_count': len(article_html.split()),
            'generation_type': 'fallback'
        }
        
        logger.info(f"✅ Article de fallback généré: {metadata['word_count']} mots")
        
        return {
            'content': article_html,
            'metadata': metadata,
            'word_count': metadata['word_count'],
            'generation_timestamp': datetime.now().isoformat()
        }


def create_fallback_article(target_word_count: int = 400) -> str:
    """
    Fonction utilitaire pour créer un article de fallback.
    
    Returns:
        Chemin du fichier article créé
    """
    try:
        generator = FallbackArticleGenerator()
        article_data = generator.generate_fallback_article(target_word_count)
        
        # Générer le nom de fichier
        date_str = datetime.now().strftime('%Y-%m-%d')
        safe_title = "seminary-vosges-seminaire-entreprise-fallback"
        filename = f"{date_str}-{safe_title}.html"
        
        # Template simple pour fallback
        final_html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_data['metadata']['title']}</title>
    <meta name="description" content="{article_data['metadata']['description']}">
    <meta name="keywords" content="séminaire entreprise, Vosges, team building, Seminary">
</head>
<body>
    <article class="article-content">
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
    article_path = create_fallback_article(400)
    print(f"Article de fallback créé: {article_path}") 