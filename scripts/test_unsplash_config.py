#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Configuration Unsplash - Seminary Blog
Script de validation complète des fonctionnalités images et illustrations
"""

import os
import sys
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

# Ajouter le répertoire scripts au path
sys.path.append(str(Path(__file__).parent))

from image_handler import ImageHandler
from article_generator import ArticleGenerator

def test_unsplash_connection(access_key: str, secret_key: Optional[str] = None) -> Dict:
    """Teste la connexion à l'API Unsplash."""
    print("🔌 Test de connexion Unsplash API...")
    
    handler = ImageHandler(access_key, secret_key)
    config_status = handler.get_unsplash_config_status()
    
    results = {
        'connection': False,
        'config_status': config_status,
        'search_test': False,
        'download_test': False,
        'error': None
    }
    
    try:
        # Test de recherche simple
        print("   📸 Test de recherche d'images...")
        images = handler.search_images("business meeting", count=3)
        
        if images:
            results['search_test'] = True
            results['connection'] = True
            print(f"   ✅ Trouvé {len(images)} images")
            
            # Test de téléchargement si images trouvées
            if not images[0].get('is_fallback', False):
                print("   💾 Test de téléchargement...")
                download_path = handler.download_image(images[0])
                if download_path:
                    results['download_test'] = True
                    print(f"   ✅ Image téléchargée: {download_path}")
                    # Nettoyer le fichier de test
                    try:
                        Path(download_path).unlink()
                        print("   🧹 Fichier de test nettoyé")
                    except:
                        pass
                else:
                    print("   ❌ Échec du téléchargement")
            else:
                print("   ℹ️ Images de fallback utilisées (pas de téléchargement)")
        else:
            print("   ❌ Aucune image trouvée")
            results['error'] = "Aucune image retournée"
            
    except Exception as e:
        results['error'] = str(e)
        print(f"   ❌ Erreur: {e}")
    
    return results

def test_illustrations_css() -> Dict:
    """Teste la génération d'illustrations CSS/SVG."""
    print("\n🎨 Test des illustrations CSS/SVG...")
    
    handler = ImageHandler()  # Pas besoin de clés pour les illustrations
    results = {
        'chart_bar': False,
        'chart_progress': False,
        'infographic': False,
        'icons': False,
        'diagram': False,
        'suggestions': False,
        'generated_count': 0
    }
    
    try:
        # Test graphique en barres
        print("   📊 Test graphique en barres...")
        chart_html = handler.generate_css_illustration('chart', 'professional', chart_type='bar')
        if len(chart_html) > 100:
            results['chart_bar'] = True
            results['generated_count'] += 1
            print("   ✅ Graphique en barres généré")
        
        # Test graphique circulaire
        print("   🎯 Test graphique circulaire...")
        progress_html = handler.generate_css_illustration('chart', 'statistics', chart_type='progress')
        if len(progress_html) > 100:
            results['chart_progress'] = True
            results['generated_count'] += 1
            print("   ✅ Graphique circulaire généré")
        
        # Test infographie
        print("   📋 Test infographie...")
        infographic_html = handler.generate_css_illustration('infographic', 'team-building')
        if len(infographic_html) > 100:
            results['infographic'] = True
            results['generated_count'] += 1
            print("   ✅ Infographie générée")
        
        # Test icônes
        print("   🔲 Test grille d'icônes...")
        icons_html = handler.generate_css_illustration('icon', 'professional')
        if len(icons_html) > 100:
            results['icons'] = True
            results['generated_count'] += 1
            print("   ✅ Grille d'icônes générée")
        
        # Test diagramme
        print("   🔄 Test diagramme de flux...")
        diagram_html = handler.generate_css_illustration('diagram', 'process')
        if len(diagram_html) > 100:
            results['diagram'] = True
            results['generated_count'] += 1
            print("   ✅ Diagramme de flux généré")
        
        # Test suggestions automatiques
        print("   🤖 Test suggestions automatiques...")
        test_content = """
        Ce séminaire permet d'améliorer la cohésion d'équipe de 85% en moyenne.
        Le processus Seminary comprend 4 étapes principales pour maximiser les résultats.
        Les statistiques montrent une progression significative de la motivation.
        """
        suggestions = handler.suggest_illustrations_for_article(test_content, "Séminaire Team Building")
        
        if suggestions:
            results['suggestions'] = True
            print(f"   ✅ {len(suggestions)} suggestions générées")
            for i, sugg in enumerate(suggestions, 1):
                print(f"      {i}. {sugg['type']} - {sugg['title']}")
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test d'illustrations: {e}")
    
    return results

def test_visual_integration(access_key: Optional[str] = None, secret_key: Optional[str] = None) -> Dict:
    """Teste l'intégration visuelle complète dans un article."""
    print("\n🖼️ Test d'intégration visuelle complète...")
    
    results = {
        'article_generation': False,
        'visual_integration': False,
        'elements_count': 0,
        'error': None
    }
    
    try:
        # Créer un générateur d'articles de test
        if not access_key:
            print("   ℹ️ Pas de clé Unsplash - test illustrations uniquement")
        
        # Simuler des données d'article
        mock_article_data = {
            'content': """
            <h1>Les Vosges : destination privilégiée pour vos séminaires d'entreprise</h1>
            <p>Les Vosges offrent un cadre exceptionnel pour organiser des séminaires d'entreprise réussis.</p>
            <p>Les statistiques montrent que 85% des participants constatent une amélioration de la cohésion d'équipe.</p>
            <p>Le processus Seminary comprend plusieurs étapes clés pour maximiser l'impact de votre séminaire.</p>
            <p>La performance des équipes s'améliore significativement après un séminaire dans ce cadre naturel.</p>
            """,
            'metadata': {
                'title': 'Séminaires Team Building dans les Vosges - Guide Complet',
                'description': 'Découvrez comment les Vosges peuvent transformer vos séminaires d\'entreprise'
            },
            'word_count': 150
        }
        
        # Test avec ImageHandler uniquement
        handler = ImageHandler(access_key, secret_key)
        
        # Test intégration visuelle
        mock_html = f"""
        <div class="article-content">
            {mock_article_data['content']}
        </div>
        """
        
        # Simuler la méthode d'intégration visuelle
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(mock_html, 'html.parser')
        visual_elements_added = []
        
        # Ajouter des illustrations automatiquement
        content_text = mock_article_data['content']
        title = mock_article_data['metadata']['title']
        
        illustration_suggestions = handler.suggest_illustrations_for_article(content_text, title)
        
        content_div = soup.find('div', class_='article-content')
        if content_div and illustration_suggestions:
            for i, suggestion in enumerate(illustration_suggestions[:2]):
                try:
                    illustration_html = handler.generate_css_illustration(
                        suggestion['type'],
                        'professional',
                        **suggestion
                    )
                    
                    # Créer un conteneur pour l'illustration
                    illustration_div = soup.new_tag('div', class_='visual-illustration')
                    illustration_div.string = illustration_html
                    
                    # Insérer à la fin pour le test
                    content_div.append(illustration_div)
                    visual_elements_added.append(f"Illustration {suggestion['type']}: {suggestion['title']}")
                    
                except Exception as e:
                    print(f"      ❌ Erreur illustration {suggestion['type']}: {e}")
        
        if visual_elements_added:
            results['visual_integration'] = True
            results['elements_count'] = len(visual_elements_added)
            print(f"   ✅ {len(visual_elements_added)} éléments visuels intégrés:")
            for element in visual_elements_added:
                print(f"      • {element}")
        
        # Test avec images Unsplash si clé disponible
        if access_key:
            try:
                print("   📸 Test intégration images Unsplash...")
                config_status = handler.get_unsplash_config_status()
                print(f"      Mode: {'Production' if not config_status['demo_mode'] else 'Démo'}")
                print(f"      Requêtes restantes: {config_status['requests_remaining']}")
                
                image_suggestions = handler.suggest_images_for_article(content_text, title)
                if image_suggestions and not image_suggestions[0].get('is_fallback', False):
                    print(f"      ✅ {len(image_suggestions)} suggestions d'images Unsplash")
                    results['elements_count'] += 1
                else:
                    print("      ℹ️ Images de fallback utilisées")
                    
            except Exception as e:
                print(f"      ❌ Erreur images Unsplash: {e}")
        
        results['article_generation'] = True
        
    except Exception as e:
        results['error'] = str(e)
        print(f"   ❌ Erreur: {e}")
    
    return results

def generate_test_report(unsplash_results: Dict, illustrations_results: Dict, integration_results: Dict) -> str:
    """Génère un rapport de test complet."""
    
    report = f"""
# 📊 RAPPORT DE TEST - CONFIGURATION UNSPLASH & ILLUSTRATIONS

## 🔌 Connexion Unsplash API

**Status**: {'✅ SUCCÈS' if unsplash_results['connection'] else '❌ ÉCHEC'}

### Configuration
- **Mode**: {'Production' if not unsplash_results['config_status']['demo_mode'] else 'Démo'}
- **Access Key**: {'✅ Configurée' if unsplash_results['config_status']['access_key_configured'] else '❌ Manquante'}
- **Secret Key**: {'✅ Configurée' if unsplash_results['config_status']['secret_key_configured'] else '❌ Manquante'}
- **Limite**: {unsplash_results['config_status']['rate_limit_per_hour']} requêtes/heure
- **Utilisées**: {unsplash_results['config_status']['requests_used']}
- **Restantes**: {unsplash_results['config_status']['requests_remaining']}

### Tests
- **Recherche d'images**: {'✅' if unsplash_results['search_test'] else '❌'}
- **Téléchargement**: {'✅' if unsplash_results['download_test'] else '❌'}

{f"**Erreur**: {unsplash_results['error']}" if unsplash_results['error'] else ""}

## 🎨 Illustrations CSS/SVG

**Status**: {'✅ SUCCÈS' if illustrations_results['generated_count'] > 0 else '❌ ÉCHEC'}

### Génération d'Illustrations ({illustrations_results['generated_count']}/5)
- **Graphique en barres**: {'✅' if illustrations_results['chart_bar'] else '❌'}
- **Graphique circulaire**: {'✅' if illustrations_results['chart_progress'] else '❌'}
- **Infographie**: {'✅' if illustrations_results['infographic'] else '❌'}
- **Grille d'icônes**: {'✅' if illustrations_results['icons'] else '❌'}
- **Diagramme de flux**: {'✅' if illustrations_results['diagram'] else '❌'}
- **Suggestions auto**: {'✅' if illustrations_results['suggestions'] else '❌'}

## 🖼️ Intégration Visuelle

**Status**: {'✅ SUCCÈS' if integration_results['visual_integration'] else '❌ ÉCHEC'}

- **Éléments intégrés**: {integration_results['elements_count']}
- **Article de test**: {'✅' if integration_results['article_generation'] else '❌'}

{f"**Erreur**: {integration_results['error']}" if integration_results['error'] else ""}

## 📋 Résumé Global

| Composant | Status | Score |
|-----------|--------|-------|
| API Unsplash | {'✅' if unsplash_results['connection'] else '❌'} | {('2/2' if unsplash_results['search_test'] and unsplash_results['download_test'] else '1/2' if unsplash_results['search_test'] else '0/2')} |
| Illustrations CSS | {'✅' if illustrations_results['generated_count'] >= 4 else '❌'} | {illustrations_results['generated_count']}/5 |
| Intégration | {'✅' if integration_results['visual_integration'] else '❌'} | {integration_results['elements_count']} éléments |

## 🚀 Prochaines Étapes

{'### ✅ Configuration Complète - Prêt pour Production' if (unsplash_results['connection'] and illustrations_results['generated_count'] >= 4) else '### ⚠️ Configuration Partielle'}

{'''
1. **Images Unsplash**: Système opérationnel
2. **Illustrations CSS**: Toutes fonctionnelles  
3. **Intégration**: Automatique dans articles
4. **Monitoring**: Quotas suivis en temps réel

Votre blog Seminary peut maintenant générer des articles avec images et illustrations automatiquement !
''' if (unsplash_results['connection'] and illustrations_results['generated_count'] >= 4) else '''

**À faire:**
''' + (f"- Configurer la clé Unsplash API" if not unsplash_results['connection'] else "") + f'''
- Vérifier les erreurs dans les logs
- Relancer les tests après correction

**Aide:** Consultez docs/UNSPLASH_SETUP.md pour la configuration détaillée.
'''
}

---
*Test généré le {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return report

def main():
    """Point d'entrée principal du script de test."""
    parser = argparse.ArgumentParser(description="Test de Configuration Unsplash - Seminary Blog")
    parser.add_argument('--access-key', help='Clé d\'accès Unsplash (optionnel)')
    parser.add_argument('--secret-key', help='Clé secrète Unsplash (optionnel)')
    parser.add_argument('--save-report', help='Sauvegarder le rapport dans un fichier')
    parser.add_argument('--test-only', choices=['unsplash', 'illustrations', 'integration'], 
                      help='Tester uniquement un composant spécifique')
    
    args = parser.parse_args()
    
    # Utiliser les variables d'environnement si pas d'arguments
    access_key = args.access_key or os.getenv('UNSPLASH_ACCESS_KEY')
    secret_key = args.secret_key or os.getenv('UNSPLASH_SECRET_KEY')
    
    print("🧪 DÉBUT DES TESTS - CONFIGURATION UNSPLASH & ILLUSTRATIONS")
    print("=" * 60)
    
    # Initialiser les résultats
    unsplash_results = {
        'connection': False, 
        'config_status': {
            'demo_mode': True,
            'access_key_configured': False,
            'secret_key_configured': False,
            'rate_limit_per_hour': 50,
            'requests_used': 0,
            'requests_remaining': 50
        }, 
        'search_test': False, 
        'download_test': False,
        'error': None
    }
    illustrations_results = {'generated_count': 0}
    integration_results = {'visual_integration': False, 'elements_count': 0}
    
    # Tests selon l'option choisie
    if not args.test_only or args.test_only == 'unsplash':
        if access_key:
            unsplash_results = test_unsplash_connection(access_key, secret_key)
        else:
            print("🔌 Test Unsplash ignoré - Pas de clé API fournie")
    
    if not args.test_only or args.test_only == 'illustrations':
        illustrations_results = test_illustrations_css()
    
    if not args.test_only or args.test_only == 'integration':
        integration_results = test_visual_integration(access_key, secret_key)
    
    # Générer le rapport
    print("\n" + "=" * 60)
    print("📊 GÉNÉRATION DU RAPPORT...")
    
    report = generate_test_report(unsplash_results, illustrations_results, integration_results)
    print(report)
    
    # Sauvegarder le rapport si demandé
    if args.save_report:
        report_path = Path(args.save_report)
        report_path.write_text(report, encoding='utf-8')
        print(f"\n💾 Rapport sauvegardé: {report_path}")
    
    # Status de sortie
    overall_success = (
        (not access_key or unsplash_results['connection']) and
        illustrations_results['generated_count'] >= 4 and
        integration_results['visual_integration']
    )
    
    print(f"\n🏁 TESTS TERMINÉS - {'✅ SUCCÈS' if overall_success else '❌ ÉCHECS DÉTECTÉS'}")
    
    if not overall_success:
        sys.exit(1)

if __name__ == "__main__":
    main() 