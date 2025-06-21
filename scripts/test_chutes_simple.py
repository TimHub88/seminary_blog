#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple de l'API Chutes AI pour diagnostiquer les articles vides
"""

import os
import json
import requests
import time
from datetime import datetime

def test_chutes_api():
    """Test simple de l'API Chutes AI"""
    
    # Récupérer la clé API depuis les variables d'environnement
    api_key = os.getenv('CHUTES_API_KEY')
    if not api_key:
        print("❌ CHUTES_API_KEY non définie")
        return False
    
    print(f"🔑 Clé API: {api_key[:10]}...")
    
    # Configuration API
    url = 'https://llm.chutes.ai/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Prompt simple et direct
    payload = {
        'model': 'deepseek-ai/DeepSeek-R1-0528',
        'messages': [
            {
                'role': 'user',
                'content': '''Écris un article HTML simple de 300 mots sur les séminaires d'entreprise dans les Vosges.

STRUCTURE REQUISE:
<h1>Titre principal</h1>
<p>Introduction</p>
<h2>Section 1</h2>
<p>Contenu...</p>
<h2>Conclusion</h2>
<p>Appel à l'action</p>

IMPORTANT: Réponds DIRECTEMENT avec le HTML, sans explications.'''
            }
        ],
        'stream': False,
        'max_tokens': 800,
        'temperature': 0.7
    }
    
    print("🚀 Test de l'API Chutes AI...")
    print(f"📡 URL: {url}")
    print(f"🤖 Modèle: {payload['model']}")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=120  # 2 minutes
        )
        
        duration = time.time() - start_time
        print(f"⏱️  Durée: {duration:.1f}s")
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"📄 Réponse: {response.text}")
            return False
        
        result = response.json()
        print(f"✅ Réponse JSON reçue")
        
        # Analyser la réponse
        if 'choices' not in result:
            print(f"❌ Format de réponse invalide: {result}")
            return False
        
        if len(result['choices']) == 0:
            print(f"❌ Aucun choix dans la réponse: {result}")
            return False
        
        content = result['choices'][0]['message']['content']
        print(f"📝 Contenu généré: {len(content)} caractères")
        
        if len(content) < 100:
            print(f"⚠️  Contenu trop court: {content}")
            return False
        
        # Afficher un extrait
        print("📄 Extrait du contenu généré:")
        print("-" * 50)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 50)
        
        # Vérifier si c'est du HTML valide
        if '<h1>' in content and '<p>' in content:
            print("✅ HTML détecté dans la réponse")
        else:
            print("⚠️  Pas de HTML détecté - contenu brut")
        
        # Sauvegarder pour inspection
        with open('test_chutes_output.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("💾 Contenu sauvegardé dans test_chutes_output.html")
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - L'API Chutes AI a pris trop de temps")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_environment():
    """Test de l'environnement"""
    print("🔍 Test de l'environnement:")
    
    # Variables d'environnement
    env_vars = ['CHUTES_API_KEY', 'UNSPLASH_ACCESS_KEY']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:10]}...")
        else:
            print(f"❌ {var}: Non définie")
    
    # Fichiers critiques
    critical_files = [
        'templates/article_template.html',
        'scripts/article_generator.py',
        'requirements.txt'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}: Existe")
        else:
            print(f"❌ {file_path}: Manquant")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DIAGNOSTIC - API CHUTES AI")
    print("=" * 60)
    
    # Test de l'environnement
    test_environment()
    print()
    
    # Test de l'API
    success = test_chutes_api()
    
    print()
    print("=" * 60)
    if success:
        print("✅ TEST RÉUSSI - L'API Chutes AI fonctionne")
    else:
        print("❌ TEST ÉCHOUÉ - Problème avec l'API Chutes AI")
    print("=" * 60) 