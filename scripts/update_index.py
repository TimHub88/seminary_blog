#!/usr/bin/env python3
"""
Script pour mettre à jour index.html avec la liste des articles
Utilisé par le workflow GitHub Actions
"""

import os
import re
from datetime import datetime
from pathlib import Path
import chardet

def detect_encoding(file_path):
    """Détecte l'encodage d'un fichier"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding'] or 'utf-8'
    except:
        return 'utf-8'

def update_index_html():
    """Met à jour index.html avec la liste des articles disponibles"""
    
    # Lister tous les articles
    articles_dir = Path('articles')
    articles = []
    
    if not articles_dir.exists():
        print("⚠️ Dossier articles/ inexistant")
        articles_dir.mkdir(exist_ok=True)
    
    for html_file in articles_dir.glob('*.html'):
        match = re.match(r'^(\d{4}-\d{2}-\d{2})-(.+)\.html$', html_file.name)
        if match:
            date_str, title_slug = match.groups()
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                
                # Lire le contenu pour extraire titre et description
                encoding = detect_encoding(html_file)
                with open(html_file, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # Extraire le titre
                title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE)
                title = title_match.group(1) if title_match else title_slug.replace('-', ' ').title()
                
                # Extraire la description
                desc_match = re.search(r'<meta name="description" content="(.*?)"', content)
                description = desc_match.group(1) if desc_match else 'Article sur les séminaires dans les Vosges'
                
                articles.append({
                    'filename': html_file.name,
                    'date': date_obj,
                    'date_str': date_str,
                    'title': title,
                    'description': description[:150] + '...' if len(description) > 150 else description
                })
                
            except Exception as e:
                print(f'⚠️ Erreur lecture {html_file}: {e}')
    
    # Trier par date décroissante
    articles.sort(key=lambda x: x['date'], reverse=True)
    
    # Générer le HTML de la liste des articles
    articles_html = ""
    if articles:
        for article in articles[:10]:  # Derniers 10 articles
            articles_html += f'''
                <div class="blog-card p-4">
                    <h3><a href="articles/{article['filename']}" class="text-decoration-none">{article['title']}</a></h3>
                    <p class="text-muted mb-2">
                        <i class="fas fa-calendar me-2"></i>
                        {article['date_str']}
                    </p>
                    <p class="mb-0">{article['description']}</p>
                </div>'''
    else:
        articles_html = '''
                <div class="text-center py-5">
                    <i class="fas fa-edit fa-4x text-primary mb-3"></i>
                    <h3>Articles en préparation</h3>
                    <p class="lead">Notre système d'IA génère automatiquement du contenu de qualité toutes les 48 heures.</p>
                    <p>Le premier article sera bientôt disponible !</p>
                </div>'''
    
    # Lire le template index.html actuel et le mettre à jour
    index_path = Path('index.html')
    if index_path.exists():
        try:
            encoding = detect_encoding(index_path)
            with open(index_path, 'r', encoding=encoding) as f:
                current_content = f.read()
        except Exception as e:
            print(f"⚠️ Erreur lecture index.html: {e}")
            print("📝 Création d'un nouveau index.html")
            current_content = None
        
        if current_content:
            # Chercher et remplacer la section des articles
            # Pattern pour identifier la zone à remplacer
            pattern = r'(<div class="col-lg-8">.*?)(<!-- Articles dynamiques -->.*?<!-- Fin articles dynamiques -->)(.*?</div>)'
            
            # Si le pattern n'existe pas, on ajoute les marqueurs
            if '<!-- Articles dynamiques -->' not in current_content:
                # Remplacer la section existante par défaut
                replacement_pattern = r'(<div class="text-center py-5">.*?</div>\s*</div>\s*</div>)'
                articles_section = f'''
                <!-- Articles dynamiques -->
                {articles_html}
                <!-- Fin articles dynamiques -->
                '''
                current_content = re.sub(replacement_pattern, articles_section, current_content, flags=re.DOTALL)
            else:
                # Remplacer le contenu entre les marqueurs
                replacement = f'\\1<!-- Articles dynamiques -->{articles_html}<!-- Fin articles dynamiques -->\\3'
                current_content = re.sub(pattern, replacement, current_content, flags=re.DOTALL)
            
            # Sauvegarder
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(current_content)
        else:
            # Créer un index.html minimal si erreur
            print("📝 Création d'un index.html minimal")
            minimal_html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seminary Blog - Séminaires d'entreprise dans les Vosges</title>
    <meta name="description" content="Blog dédié aux séminaires d'entreprise dans les Vosges.">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div id="header-container"></div>
    
    <div class="container my-5">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center mb-4">Seminary Blog</h1>
                <!-- Articles dynamiques -->
                {articles_html}
                <!-- Fin articles dynamiques -->
            </div>
        </div>
    </div>
    
    <div id="footer-container"></div>
    
    <script>
        fetch('./templates/header.html').then(r => r.text()).then(h => document.getElementById('header-container').innerHTML = h);
        fetch('./templates/footer.html').then(r => r.text()).then(h => document.getElementById('footer-container').innerHTML = h);
    </script>
</body>
</html>'''
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(minimal_html)
    
    print(f'✅ Index.html mis à jour avec {len(articles)} article(s)')
    return len(articles)

if __name__ == '__main__':
    update_index_html() 