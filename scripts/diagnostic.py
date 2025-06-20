#!/usr/bin/env python3
"""
Script de diagnostic pour Seminary Blog
Aide à identifier les problèmes de configuration et de dépendances
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def check_environment():
    """Vérifie l'environnement et les variables."""
    print("🔍 DIAGNOSTIC SEMINARY BLOG")
    print("=" * 50)
    
    # Vérifier Python
    print(f"🐍 Python: {sys.version}")
    
    # Vérifier les variables d'environnement
    print("\n📋 Variables d'environnement:")
    env_vars = ['CHUTES_API_KEY', 'UNSPLASH_ACCESS_KEY', 'LOG_LEVEL']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Masquer les clés API pour la sécurité
            if 'API' in var or 'KEY' in var:
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Non définie")
    
    # Vérifier les dépendances
    print("\n📦 Dépendances:")
    dependencies = [
        ('openai', 'OpenAI'),
        ('requests', 'Requests'),
        ('beautifulsoup4', 'BeautifulSoup'),
        ('chardet', 'Chardet'),
        ('Pillow', 'PIL'),
        ('lxml', 'LXML')
    ]
    
    for package, display_name in dependencies:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {display_name}")
        except ImportError:
            print(f"  ❌ {display_name}")
    
    # Vérifier la structure des fichiers
    print("\n📁 Structure des fichiers:")
    required_files = [
        'scripts/article_generator.py',
        'scripts/context_manager.py',
        'scripts/seo_validator.py',
        'scripts/image_handler.py',
        'scripts/seminary_integrator.py',
        'scripts/update_index.py',
        'templates/header.html',
        'templates/footer.html',
        'templates/article_template.html',
        'requirements.txt',
        'index.html'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"  ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"  ❌ {file_path}")
    
    # Vérifier les répertoires
    print("\n📂 Répertoires:")
    required_dirs = ['scripts', 'templates', 'data', 'articles', 'images']
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            items = len(list(Path(dir_path).iterdir()))
            print(f"  ✅ {dir_path}/ ({items} éléments)")
        else:
            print(f"  ❌ {dir_path}/")
    
    # Vérifier le contexte
    print("\n🧠 Contexte:")
    context_file = Path('data/context_window.json')
    if context_file.exists():
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                context = json.load(f)
            
            articles_count = len(context.get('last_articles', []))
            last_updated = context.get('last_updated', 'Jamais')
            print(f"  ✅ Contexte chargé: {articles_count} articles")
            print(f"  📅 Dernière MAJ: {last_updated}")
        except Exception as e:
            print(f"  ⚠️ Erreur lecture contexte: {e}")
    else:
        print("  ℹ️ Fichier contexte inexistant (sera créé)")
    
    # Vérifier les articles existants
    print("\n📰 Articles existants:")
    articles_dir = Path('articles')
    if articles_dir.exists():
        articles = list(articles_dir.glob('*.html'))
        print(f"  📄 {len(articles)} articles trouvés")
        
        if articles:
            # Afficher les 3 plus récents
            articles_sorted = sorted(articles, key=lambda x: x.stat().st_mtime, reverse=True)
            for i, article in enumerate(articles_sorted[:3]):
                size = article.stat().st_size
                mtime = datetime.fromtimestamp(article.stat().st_mtime)
                print(f"    {i+1}. {article.name} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
    else:
        print("  ℹ️ Dossier articles inexistant")

def test_api_connection():
    """Test basique de connexion API (sans vraie clé)."""
    print("\n🌐 Test API:")
    
    chutes_key = os.getenv('CHUTES_API_KEY')
    if not chutes_key:
        print("  ⚠️ CHUTES_API_KEY manquante - impossible de tester")
        return
    
    print("  ℹ️ Clé API trouvée - test de format...")
    
    # Vérifier le format de la clé (sans appel réel)
    if len(chutes_key) < 10:
        print("  ⚠️ Clé API suspicieusement courte")
    elif chutes_key.startswith('sk-') or chutes_key.startswith('api-'):
        print("  ✅ Format de clé API valide")
    else:
        print("  ⚠️ Format de clé API inhabituel")

def generate_report():
    """Génère un rapport de diagnostic."""
    print("\n📊 RÉSUMÉ:")
    print("=" * 50)
    
    # Compter les problèmes
    issues = []
    
    # Vérifier les variables critiques
    if not os.getenv('CHUTES_API_KEY'):
        issues.append("CHUTES_API_KEY manquante")
    
    # Vérifier les fichiers critiques
    critical_files = [
        'scripts/article_generator.py',
        'scripts/context_manager.py',
        'templates/article_template.html'
    ]
    
    for file_path in critical_files:
        if not Path(file_path).exists():
            issues.append(f"Fichier manquant: {file_path}")
    
    # Afficher le résumé
    if issues:
        print(f"❌ {len(issues)} problème(s) détecté(s):")
        for issue in issues:
            print(f"  • {issue}")
        print("\n🔧 Actions recommandées:")
        print("  1. Configurer CHUTES_API_KEY dans GitHub Secrets")
        print("  2. Vérifier que tous les fichiers sont présents")
        print("  3. Installer toutes les dépendances (pip install -r requirements.txt)")
    else:
        print("✅ Aucun problème critique détecté")
        print("🚀 Le système devrait fonctionner correctement")
    
    print(f"\n⏰ Diagnostic effectué le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Point d'entrée principal."""
    check_environment()
    test_api_connection()
    generate_report()

if __name__ == "__main__":
    main() 