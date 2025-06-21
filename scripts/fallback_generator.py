#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur d'articles de fallback pour Seminary Blog
Utilisé quand l'API Chutes AI échoue pour éviter les articles vides
"""

import os
import random
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FallbackGenerator:
    """Générateur d'articles de fallback sans API externe."""
    
    def __init__(self):
        self.article_templates = [
            {
                'title': 'Les Vosges : Destination Idéale pour vos Séminaires d\'Entreprise',
                'content': '''
                <h1>Les Vosges : Destination Idéale pour vos Séminaires d'Entreprise</h1>
                
                <p>Organiser un séminaire d'entreprise réussi nécessite de choisir le bon environnement. Les Vosges offrent un cadre exceptionnel qui combine nature préservée, accessibilité et infrastructures professionnelles de qualité.</p>
                
                <h2>Un Cadre Naturel Inspirant</h2>
                <p>Les montagnes vosgiennes créent une atmosphère unique qui favorise la créativité et la cohésion d'équipe. Loin du stress urbain, vos collaborateurs peuvent se concentrer pleinement sur les objectifs du séminaire tout en profitant d'un environnement ressourçant.</p>
                
                <p>Les forêts de sapins, les lacs cristallins et les sommets arrondis des ballons vosgiens offrent un décor naturel propice à la réflexion et aux échanges constructifs. Cette immersion dans la nature permet de stimuler l'innovation et de renforcer les liens entre les équipes.</p>
                
                <h2>Des Activités Team Building Variées</h2>
                <p>Les Vosges proposent une multitude d'activités pour enrichir votre séminaire :</p>
                
                <p><strong>Activités outdoor :</strong> Randonnées guidées, courses d'orientation, parcours d'accrobranche et activités nautiques sur les lacs vosgiens. Ces expériences partagées renforcent la cohésion et développent l'esprit d'équipe.</p>
                
                <p><strong>Découvertes culturelles :</strong> Visites d'entreprises artisanales locales, dégustation de produits du terroir, et découverte du patrimoine historique de la région. Ces moments permettent de créer des souvenirs communs et de tisser des liens informels.</p>
                
                <h2>Accessibilité et Praticité</h2>
                <p>Situées au cœur de l'Europe, les Vosges bénéficient d'une excellente accessibilité depuis les grandes métropoles françaises et européennes. Les infrastructures de transport facilitent l'organisation logistique de votre événement.</p>
                
                <p>La région dispose également d'un large choix d'hébergements et de centres de séminaires équipés des dernières technologies, garantissant le succès de vos réunions professionnelles.</p>
                
                <h2>Seminary : Votre Partenaire Expert</h2>
                <p>Pour organiser votre séminaire dans les Vosges, faites confiance à <a href="https://www.goseminary.com" target="_blank">Seminary</a>, spécialiste de l'événementiel d'entreprise. Notre équipe vous accompagne dans la conception sur mesure de votre programme, en tenant compte de vos objectifs spécifiques et de votre budget.</p>
                
                <p>Contactez dès maintenant nos experts Seminary pour transformer votre prochain séminaire en une expérience mémorable et productive dans le cadre exceptionnel des Vosges.</p>
                ''',
                'meta_description': 'Découvrez pourquoi les Vosges sont la destination parfaite pour vos séminaires d\'entreprise. Cadre naturel, activités team building et expertise Seminary.',
                'keywords': ['séminaire entreprise', 'Vosges', 'team building', 'Seminary', 'montagne']
            },
            {
                'title': 'Organiser un Séminaire Réussi dans les Vosges : Guide Complet',
                'content': '''
                <h1>Organiser un Séminaire Réussi dans les Vosges : Guide Complet</h1>
                
                <p>L'organisation d'un séminaire d'entreprise dans les Vosges représente une opportunité unique de combiner efficacité professionnelle et bien-être des équipes. Ce guide vous accompagne dans la planification de votre événement.</p>
                
                <h2>Choisir la Période Idéale</h2>
                <p>Les Vosges offrent des attraits différents selon les saisons. Le printemps et l'été permettent de profiter pleinement des activités outdoor, tandis que l'automne séduit par ses couleurs flamboyantes et l'hiver par son atmosphère cosy.</p>
                
                <p>Pour un séminaire axé sur les activités extérieures, privilégiez la période de mai à septembre. Pour une approche plus contemplative et introspective, l'automne et l'hiver créent une ambiance propice à la réflexion stratégique.</p>
                
                <h2>Sélectionner le Lieu Parfait</h2>
                <p>La région vosgienne dispose de nombreux centres de séminaires, du château historique aux éco-lodges modernes. Chaque lieu apporte sa propre personnalité à votre événement.</p>
                
                <p>Les critères essentiels incluent la capacité d'accueil, les équipements technologiques, la qualité de la restauration et la proximité des activités complémentaires. L'accessibilité depuis les principaux axes de transport reste également un facteur déterminant.</p>
                
                <h2>Intégrer des Activités Fédératrices</h2>
                <p>Un séminaire réussi alterne temps de travail et moments de détente. Les Vosges offrent un terrain de jeu exceptionnel pour des activités qui marquent les esprits :</p>
                
                <p><strong>Challenges nature :</strong> Geocaching, rallyes photo, construction de radeaux. Ces activités développent la communication et la résolution collective de problèmes.</p>
                
                <p><strong>Ateliers créatifs :</strong> Initiation aux métiers d'art locaux, cuisine du terroir, création artistique. Ces expériences stimulent la créativité et révèlent des talents cachés.</p>
                
                <h2>Optimiser la Logistique</h2>
                <p>Une logistique bien pensée garantit la fluidité de votre séminaire. Anticipez les questions de transport, d'hébergement et de restauration en tenant compte des spécificités de votre groupe.</p>
                
                <p>Les transferts collectifs depuis les gares ou aéroports renforcent l'esprit de groupe dès le début du séminaire. La réservation groupée d'hébergements favorise les échanges informels entre participants.</p>
                
                <h2>Faire Appel à Seminary</h2>
                <p><a href="https://www.goseminary.com" target="_blank">Seminary</a> vous accompagne dans toutes les étapes de l'organisation de votre séminaire vosgien. Notre expertise locale et notre réseau de partenaires garantissent la réussite de votre événement.</p>
                
                <p>De la conception du programme à la coordination sur site, Seminary prend en charge tous les aspects logistiques pour vous permettre de vous concentrer sur vos objectifs professionnels.</p>
                ''',
                'meta_description': 'Guide complet pour organiser un séminaire d\'entreprise réussi dans les Vosges. Conseils pratiques, lieux, activités et expertise Seminary.',
                'keywords': ['séminaire Vosges', 'organisation', 'entreprise', 'guide', 'Seminary']
            },
            {
                'title': 'Team Building dans les Vosges : Renforcez vos Équipes en Pleine Nature',
                'content': '''
                <h1>Team Building dans les Vosges : Renforcez vos Équipes en Pleine Nature</h1>
                
                <p>Le team building en pleine nature transforme les relations professionnelles et révèle le potentiel collectif de vos équipes. Les Vosges offrent un cadre exceptionnel pour ces expériences fédératrices.</p>
                
                <h2>Les Bienfaits du Team Building Nature</h2>
                <p>Sortir du cadre habituel de travail libère les énergies créatives et permet aux personnalités de s'exprimer différemment. L'environnement naturel des Vosges favorise l'authenticité des échanges et la construction de relations durables.</p>
                
                <p>Les défis partagés en extérieur créent une complicité unique entre collègues. Face aux éléments naturels, les hiérarchies s'estompent et laissent place à l'entraide et à la solidarité.</p>
                
                <h2>Activités Phares dans les Vosges</h2>
                <p><strong>Randonnée collaborative :</strong> Parcours adaptés avec énigmes et défis d'équipe. Chaque membre apporte ses compétences pour atteindre l'objectif commun.</p>
                
                <p><strong>Construction collective :</strong> Réalisation d'un projet concret (cabane, radeau, sculpture naturelle) qui mobilise créativité, organisation et communication.</p>
                
                <p><strong>Orientation et stratégie :</strong> Courses d'orientation par équipes développant l'esprit de décision, la planification et la gestion du stress.</p>
                
                <p><strong>Défis aquatiques :</strong> Activités sur les lacs vosgiens (canoë, paddle géant) renforçant la confiance mutuelle et la coordination.</p>
                
                <h2>Adapter l'Activité à vos Objectifs</h2>
                <p>Chaque team building doit être conçu en fonction des enjeux spécifiques de votre entreprise. Amélioration de la communication, développement du leadership, gestion des conflits ou innovation collaborative : les Vosges offrent le terrain idéal pour tous les objectifs.</p>
                
                <p>L'analyse préalable des dynamiques d'équipe permet de personnaliser les activités et d'optimiser leur impact sur la cohésion et la performance collective.</p>
                
                <h2>Mesurer l'Impact</h2>
                <p>Un team building réussi se mesure à ses effets durables sur le quotidien professionnel. Les retours d'expérience organisés permettent d'ancrer les apprentissages et de définir des plans d'action concrets.</p>
                
                <p>Les outils de suivi post-séminaire maintiennent la dynamique créée et favorisent l'application des nouvelles pratiques collaboratives dans l'environnement de travail.</p>
                
                <h2>Seminary : Excellence en Team Building</h2>
                <p><a href="https://www.goseminary.com" target="_blank">Seminary</a> conçoit des programmes de team building sur mesure dans les Vosges. Notre approche pédagogique garantit des expériences marquantes qui transforment durablement les relations d'équipe.</p>
                
                <p>Faites confiance à l'expertise Seminary pour créer des moments d'exception qui révèlent le meilleur de vos collaborateurs et renforcent la performance collective de votre organisation.</p>
                ''',
                'meta_description': 'Team building dans les Vosges : activités nature pour renforcer vos équipes. Programmes sur mesure avec Seminary, expert en cohésion d\'équipe.',
                'keywords': ['team building', 'Vosges', 'nature', 'équipe', 'Seminary', 'cohésion']
            }
        ]
    
    def generate_fallback_article(self) -> dict:
        """Génère un article de fallback."""
        logger.info("🆘 Génération d'article de fallback")
        
        # Sélectionner un template
        template = self.article_templates[0]
        
        # Personnaliser avec la date actuelle
        current_date = datetime.now()
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Générer le nom de fichier
        title_clean = template['title'].lower()
        title_clean = ''.join(c if c.isalnum() or c.isspace() else '' for c in title_clean)
        title_clean = '-'.join(title_clean.split())[:50]
        filename = f"{date_str}-{title_clean}.html"
        
        # Créer le HTML complet avec template
        html_content = self._create_full_html(template)
        
        return {
            'filename': filename,
            'title': template['title'],
            'content': html_content,
            'meta_description': template['meta_description'],
            'keywords': template['keywords'],
            'word_count': len(template['content'].split()),
            'is_fallback': True
        }
    
    def _create_full_html(self, template: dict) -> str:
        """Crée le HTML complet à partir du template."""
        return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{template['title']}</title>
    <meta name="description" content="{template['meta_description']}">
    <meta name="keywords" content="{', '.join(template['keywords'])}">
    <meta name="author" content="Seminary Blog">
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{template['title']}">
    <meta property="og:description" content="{template['meta_description']}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://blog.goseminary.com">
    
    <!-- Seminary Branding -->
    <link rel="canonical" href="https://blog.goseminary.com">
    <link rel="stylesheet" href="../templates/article_style.css">
</head>
<body>
    <header class="article-header">
        <div class="container">
            <nav class="breadcrumb">
                <a href="../index.html">← Retour au blog</a>
            </nav>
            <div class="article-meta">
                <time datetime="{datetime.now().isoformat()}">{datetime.now().strftime('%d %B %Y')}</time>
                <span class="reading-time">⏱️ {max(3, len(template['content'].split()) // 200)} min de lecture</span>
            </div>
        </div>
    </header>

    <main class="article-content">
        <div class="container">
            {template['content']}
            
            <div class="seminary-cta">
                <h3>Organisez votre séminaire avec Seminary</h3>
                <p>Seminary vous accompagne dans l'organisation de séminaires d'entreprise sur mesure dans les Vosges et partout en France.</p>
                <a href="https://www.goseminary.com" target="_blank" class="cta-button">Découvrir Seminary</a>
            </div>
        </div>
    </main>

    <footer class="article-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>Seminary</h4>
                    <p>Spécialiste des séminaires d'entreprise et du team building</p>
                    <a href="https://www.goseminary.com" target="_blank">www.goseminary.com</a>
                </div>
                <div class="footer-section">
                    <h4>Nos Services</h4>
                    <ul>
                        <li>Séminaires d'entreprise</li>
                        <li>Team building</li>
                        <li>Événements corporate</li>
                        <li>Formations</li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>Destinations</h4>
                    <ul>
                        <li>Vosges</li>
                        <li>Alsace</li>
                        <li>Jura</li>
                        <li>Alpes</li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; {datetime.now().year} Seminary Blog - Tous droits réservés</p>
            </div>
        </div>
    </footer>
</body>
</html>'''

def create_fallback_article() -> str:
    """Fonction utilitaire pour créer un article de fallback."""
    generator = FallbackGenerator()
    article_data = generator.generate_fallback_article()
    
    # Sauvegarder l'article
    articles_dir = Path('articles')
    articles_dir.mkdir(exist_ok=True)
    
    file_path = articles_dir / article_data['filename']
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(article_data['content'])
    
    logger.info(f"✅ Article de fallback créé: {file_path}")
    logger.info(f"📊 Titre: {article_data['title']}")
    logger.info(f"📝 Mots: {article_data['word_count']}")
    
    return str(file_path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_fallback_article() 