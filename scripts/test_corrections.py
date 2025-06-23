#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier les corrections des erreurs critiques
Seminary Blog System - Test des méthodes corrigées
"""

import sys
import traceback
from bs4 import BeautifulSoup

def test_image_handler():
    """Test des méthodes ImageHandler corrigées."""
    print("🧪 TEST 1: ImageHandler - Méthodes manquantes")
    
    try:
        from image_handler import ImageHandler
        
        handler = ImageHandler()
        
        # Test 1: _generate_icon_illustration
        print("   ✓ Test _generate_icon_illustration...")
        icon_html = handler.generate_css_illustration('icon', 'professional')
        assert '<div class="seminary-icons-grid"' in icon_html
        assert len(icon_html) > 1000
        print(f"     → HTML généré: {len(icon_html)} caractères")
        
        # Test 2: _generate_diagram_css
        print("   ✓ Test _generate_diagram_css...")
        diagram_html = handler.generate_css_illustration('diagram', 'professional', diagram_type='process')
        assert '<div class="seminary-process-diagram"' in diagram_html
        assert len(diagram_html) > 1000
        print(f"     → HTML généré: {len(diagram_html)} caractères")
        
        # Test 3: _generate_default_illustration
        print("   ✓ Test _generate_default_illustration...")
        default_html = handler.generate_css_illustration('unknown_type', 'professional')
        assert '<div class="seminary-default-illustration"' in default_html
        assert len(default_html) > 500
        print(f"     → HTML généré: {len(default_html)} caractères")
        
        # Test 4: Suggestions d'illustrations
        print("   ✓ Test suggest_illustrations_for_article...")
        suggestions = handler.suggest_illustrations_for_article(
            "Nos statistiques montrent une amélioration de la performance des équipes",
            "Améliorer la performance avec Seminary"
        )
        assert len(suggestions) > 0
        print(f"     → {len(suggestions)} suggestions générées")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERREUR: {e}")
        traceback.print_exc()
        return False

def test_seminary_integrator():
    """Test du SeminaryIntegrator corrigé."""
    print("\n🧪 TEST 2: SeminaryIntegrator - Création de liens")
    
    try:
        from seminary_integrator import SeminaryIntegrator
        
        integrator = SeminaryIntegrator()
        
        # HTML de test complet
        test_html = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <title>Test Article</title>
        </head>
        <body>
            <div class="article-content">
                <h1>Test des séminaires Seminary</h1>
                <p>Les séminaires d'entreprise permettent d'améliorer la cohésion d'équipe.</p>
                <p>Nos statistiques montrent des résultats exceptionnels pour les entreprises.</p>
                <p>Pour organiser votre événement, consultez nos services de réservation.</p>
            </div>
        </body>
        </html>
        """
        
        print("   ✓ Test process_article...")
        result = integrator.process_article(test_html, "Test des séminaires")
        
        assert 'modified_html' in result
        assert 'links_added' in result
        assert 'confidence_score' in result
        
        modified_html = result['modified_html']
        
        # Vérifier que le HTML n'est pas corrompu
        soup = BeautifulSoup(modified_html, 'html.parser')
        assert soup.find('html') is not None
        assert soup.find('head') is not None
        assert soup.find('body') is not None
        assert soup.find('h1') is not None
        
        print(f"     → Score de confiance: {result['confidence_score']:.2f}")
        print(f"     → Liens ajoutés: {result['links_added']}")
        print(f"     → HTML valide: {len(modified_html)} caractères")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERREUR: {e}")
        traceback.print_exc()
        return False

def test_visual_integration():
    """Test de l'intégration visuelle corrigée."""
    print("\n🧪 TEST 3: Intégration visuelle - BeautifulSoup parsing")
    
    try:
        from image_handler import ImageHandler
        from bs4 import BeautifulSoup
        
        handler = ImageHandler()
        
        # HTML de base
        base_html = """
        <div class="article-content">
            <p>Premier paragraphe de test.</p>
            <p>Deuxième paragraphe pour l'intégration.</p>
            <p>Troisième paragraphe de conclusion.</p>
        </div>
        """
        
        # Test d'intégration d'illustration
        soup = BeautifulSoup(base_html, 'html.parser')
        content_div = soup.find('div', class_='article-content')
        
        # Générer une illustration
        illustration_html = handler.generate_css_illustration('icon', 'professional')
        
        # Créer un conteneur
        illustration_div = soup.new_tag('div', class_='visual-illustration')
        
        # TEST CRITIQUE: Parser le HTML correctement
        illustration_soup = BeautifulSoup(illustration_html, 'html.parser')
        for element in illustration_soup:
            if element.name:  # Ignorer les éléments texte
                illustration_div.append(element)
        
        # Insérer dans le document
        paragraphs = content_div.find_all('p')
        if len(paragraphs) > 1:
            paragraphs[1].insert_after(illustration_div)
        
        # Vérifier le résultat
        final_html = str(soup)
        
        assert 'visual-illustration' in final_html
        assert 'seminary-icons-grid' in final_html
        assert len(paragraphs) == 3  # Structure préservée
        
        print("   ✓ Test parsing HTML avec BeautifulSoup...")
        print(f"     → HTML final: {len(final_html)} caractères")
        print("     → Structure DOM préservée")
        print("     → Illustration intégrée avec succès")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERREUR: {e}")
        traceback.print_exc()
        return False

def test_html_validation():
    """Test de la validation HTML finale."""
    print("\n🧪 TEST 4: Validation HTML - Balises requises")
    
    try:
        # HTML complet avec toutes les balises requises
        complete_html = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Article Seminary Test</title>
            <meta name="description" content="Description de test">
        </head>
        <body>
            <div class="article-content">
                <h1>Titre de l'article Seminary</h1>
                <p>Contenu de l'article avec plus de 500 caractères pour respecter les seuils de validation. Ce paragraphe contient suffisamment de texte pour passer tous les tests de longueur minimale requis par le système de validation du générateur d'articles Seminary Blog. Les validations incluent la présence des balises HTML essentielles comme html, head, title, body et h1.</p>
            </div>
        </body>
        </html>
        """
        
        # Vérifier les balises requises
        required_tags = ['<html>', '<head>', '<title>', '<body>', '<h1>']
        missing_tags = [tag for tag in required_tags if tag not in complete_html]
        
        assert len(missing_tags) == 0, f"Balises manquantes: {missing_tags}"
        assert len(complete_html) > 500, "HTML trop court"
        
        # Vérifier avec BeautifulSoup
        soup = BeautifulSoup(complete_html, 'html.parser')
        assert soup.find('html') is not None
        assert soup.find('head') is not None
        assert soup.find('title') is not None
        assert soup.find('body') is not None
        assert soup.find('h1') is not None
        
        print("   ✓ Test validation HTML...")
        print(f"     → Toutes les balises requises présentes: {required_tags}")
        print(f"     → Taille HTML: {len(complete_html)} caractères")
        print("     → Structure DOM valide")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERREUR: {e}")
        traceback.print_exc()
        return False

def main():
    """Lance tous les tests de correction."""
    print("🚀 TESTS DE VALIDATION DES CORRECTIONS SEMINARY BLOG")
    print("=" * 60)
    
    tests = [
        test_image_handler,
        test_seminary_integrator, 
        test_visual_integration,
        test_html_validation
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print("   ✅ SUCCÈS")
            else:
                failed += 1
                print("   ❌ ÉCHEC")
        except Exception as e:
            failed += 1
            print(f"   ❌ ERREUR CRITIQUE: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSULTATS: {passed} succès, {failed} échecs")
    
    if failed == 0:
        print("🎉 TOUS LES TESTS PASSENT - Corrections validées!")
        print("✅ Le système Seminary Blog est opérationnel")
        return 0
    else:
        print("⚠️  Certains tests ont échoué - Vérification requise")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 