# Seminary Blog - Système de Blog Automatisé SEO-First

## 🎯 Vue d'ensemble

Seminary Blog est un système de génération automatique d'articles de blog optimisés pour le SEO, spécialement conçu pour promouvoir les séminaires d'entreprise dans les Vosges. Le système utilise un pipeline d'IA sophistiqué en 4 passes pour créer du contenu de haute qualité de manière autonome.

### 🏔️ À propos de Seminary

Seminary est la plateforme de référence pour l'organisation de séminaires d'entreprise dans les Vosges. Ce blog automatisé génère du contenu pertinent pour attirer et informer les entreprises sur les avantages des séminaires en pleine nature.

**Domaine:** [blog.goseminary.com](https://blog.goseminary.com)  
**Fréquence:** Nouvel article toutes les 48 heures  
**Mots-clés cibles:** séminaires, Vosges, entreprise, team building, formation professionnelle

## 🚀 Architecture Technique

### Pipeline 4-Pass IA

Le système utilise un pipeline sophistiqué en 4 passes pour garantir la qualité et l'optimisation SEO :

#### 🎨 Pass 1 - Génération Créative
- **Objectif:** Génération d'articles originaux de 800-2000 mots
- **IA:** Chutes AI avec prompts contextuels
- **Contenu:** Statistiques, bénéfices, guides pratiques sur les séminaires
- **Contraintes:** Éviter la répétition grâce au système de contexte

#### 🔍 Pass 2 - Audit SEO Automatique
- **Validation:** Structure HTML, balises meta, densité de mots-clés
- **Métriques:** Score SEO global, recommandations détaillées
- **Critères:** Titre (30-60 chars), meta description (120-160 chars), H1-H6
- **Seuil:** Score minimum de 75/100 requis

#### ⚡ Pass 3 - Auto-Amélioration
- **Correction:** Optimisation ciblée sans régénération complète
- **Enrichissement:** Ajout de contenu pour atteindre le nombre de mots cible
- **Itération:** Maximum 3 tentatives d'amélioration par article
- **Préservation:** Maintien de la créativité originale

#### 🏢 Pass 4 - Intégration Seminary
- **Templates:** Application des templates Seminary avec branding
- **Images:** Insertion d'images via Unsplash avec alt-text optimisé
- **Liens:** Intégration automatique de liens vers goseminary.com
- **Finalisation:** Article prêt pour publication

### 🧠 Système de Contexte Intelligent

Le système maintient une mémoire contextuelle pour éviter la répétition :

- **Fenêtre:** 3 derniers articles résumés (100 mots chacun)
- **Rotation:** Suppression automatique des anciens résumés
- **Stockage:** `data/context_window.json`
- **Mise à jour:** Automatique après chaque génération

### 🖼️ Gestion d'Images Avancée

- **Source principale:** API Unsplash avec mots-clés pertinents
- **Fallback:** Images Picsum en cas d'échec Unsplash
- **Optimisation:** Redimensionnement automatique (1200x800)
- **SEO:** Génération automatique d'alt-text et titres
- **Cache:** Système de cache pour éviter les recherches répétitives

## 📁 Structure du Projet

```
seminary_blog/
├── 📄 README.md                 # Documentation complète
├── 📄 requirements.txt          # Dépendances Python
├── 📄 CNAME                     # Configuration domaine GitHub Pages
├── 🗂️ scripts/                  # Scripts Python principaux
│   ├── 🤖 article_generator.py   # Pipeline 4-pass principal
│   ├── 🧠 context_manager.py     # Gestion contexte 3 articles
│   ├── 🔍 seo_validator.py       # Validation SEO multi-couches
│   ├── 🖼️ image_handler.py       # Gestion images Unsplash
│   └── 🏢 seminary_integrator.py # Intégration liens Seminary
├── 🗂️ templates/                # Templates HTML
│   ├── 📄 header.html            # En-tête Seminary
│   ├── 📄 footer.html            # Pied de page Seminary
│   └── 📄 article_template.html  # Template article principal
├── 🗂️ data/                     # Données et cache
│   ├── 📄 context_window.json    # Contexte 3 derniers articles
│   └── 🗂️ image_cache/           # Cache recherches Unsplash
├── 🗂️ articles/                 # Articles générés
│   └── 📄 YYYY-MM-DD-titre.html  # Format de nommage
├── 🗂️ images/                   # Images téléchargées
├── 🗂️ .github/workflows/        # Automatisation GitHub
│   └── 📄 auto-publish.yml       # Workflow génération 48h
└── 🗂️ docs/                     # Documentation GitHub Pages
```

## ⚙️ Installation et Configuration

### 1. Prérequis

- Python 3.11+
- Compte GitHub avec Actions activées
- Clé API Chutes AI (obligatoire)
- Clé API Unsplash (optionnelle)

### 2. Clonage et Installation

```bash
# Cloner le repository
git clone https://github.com/TimHub88/seminary_blog.git
cd seminary_blog

# Installer les dépendances
pip install -r requirements.txt

# Créer les répertoires nécessaires
mkdir -p articles data/image_cache images
```

### 3. Configuration des Secrets GitHub

Aller dans **Settings > Secrets and variables > Actions** et ajouter :

| Secret | Description | Obligatoire |
|--------|-------------|-------------|
| `CHUTES_API_KEY` | Clé API Chutes AI pour génération | ✅ Oui |
| `UNSPLASH_ACCESS_KEY` | Clé API Unsplash pour images | ❌ Non |

### 4. Configuration du Domaine

Le fichier `CNAME` est déjà configuré pour `blog.goseminary.com`. 

Pour un autre domaine :
```bash
echo "votre-domaine.com" > CNAME
```

## 🔧 Utilisation

### Génération Automatique (Recommandée)

Le système génère automatiquement un article toutes les 48 heures via GitHub Actions :

- **Planification:** Cron `0 8 */2 * *` (8h00 UTC tous les 2 jours)
- **Déclenchement manuel:** Onglet Actions > "Seminary Blog Auto-Publisher" > Run workflow
- **Vérifications:** Évite la génération si article récent (< 40h)

### Génération Manuelle

#### Génération Complète
```bash
python scripts/article_generator.py \
  --chutes-api-key "votre-cle-chutes-ai" \
  --unsplash-api-key "votre-cle-unsplash"
```

#### Gestion du Contexte
```bash
# Afficher le contexte actuel
python scripts/context_manager.py --show-context

# Reconstruire le contexte
python scripts/context_manager.py --rebuild --api-key "votre-cle-chutes-ai"
```

#### Validation SEO
```bash
# Audit SEO détaillé
python scripts/seo_validator.py articles/2024-01-15-exemple.html --detailed

# Audit de tous les articles
python scripts/seo_validator.py articles/ --batch
```

#### Gestion des Images
```bash
# Rechercher des images
python scripts/image_handler.py --search "séminaire montagne" --count 5

# Nettoyer les anciennes images
python scripts/image_handler.py --cleanup --days 30
```

## 📊 Monitoring et Métriques

### Logs GitHub Actions

Chaque génération produit des logs détaillés :
- ✅ Succès/échec de génération
- 📊 Score SEO de l'article
- 🖼️ Images téléchargées
- 🔗 Liens Seminary intégrés

### Métriques SEO

Le système valide automatiquement :
- **Structure HTML:** Balises sémantiques, hiérarchie
- **Métadonnées:** Title, description, Open Graph
- **Contenu:** Nombre de mots, densité mots-clés
- **Images:** Alt-text, optimisation
- **Liens:** Liens internes Seminary

### Fichiers de Suivi

- `data/context_window.json` : Contexte des 3 derniers articles
- `data/image_cache/` : Cache des recherches Unsplash
- `generation.log` : Logs de la dernière génération

## 🛠️ Maintenance

### Nettoyage Périodique

```bash
# Nettoyer les anciennes images (30 jours)
python scripts/image_handler.py --cleanup --days 30

# Vérifier l'intégrité du contexte
python scripts/context_manager.py --validate
```

### Mise à Jour des Dépendances

```bash
pip install --upgrade -r requirements.txt
```

### Sauvegarde

Sauvegarder régulièrement :
- `data/context_window.json`
- `data/image_cache/`
- Dossier `articles/`

## 🔍 Dépannage

### Erreurs Communes

#### ❌ "CHUTES_API_KEY manquante"
**Solution:** Vérifier que la clé API est configurée dans les secrets GitHub

#### ❌ "Échec de génération d'article"
**Causes possibles:**
- Quota API Chutes AI dépassé
- Problème de connectivité
- Prompt trop long

**Solution:** Vérifier les logs GitHub Actions pour le détail de l'erreur

#### ❌ "Score SEO insuffisant"
**Solution:** Le système réessaie automatiquement 3 fois. Si l'échec persiste, vérifier les règles SEO dans `seo_validator.py`

#### ❌ "Images non trouvées"
**Solution:** Le système utilise automatiquement des images de fallback. Vérifier la clé Unsplash si nécessaire.

#### ❌ "Validation HTML: balises manquantes (ancienne version)"
Depuis la version 1.1, la validation utilise une analyse DOM robuste. Si ce message apparaît encore :
- Vérifier que le contenu généré comporte au moins une balise `<h1>`.
- Exécuter `python -m pytest tests/test_html_validation.py` pour diagnostiquer.

### Debugging Avancé

#### Mode Debug GitHub Actions
```yaml
# Activer lors du déclenchement manuel
debug_mode: true
```

#### Logs Détaillés
```bash
export LOG_LEVEL=DEBUG
python scripts/article_generator.py --chutes-api-key "..." --debug
```

#### Test des Modules
```bash
# Test du gestionnaire de contexte
python -m pytest tests/test_context_manager.py

# Test du validateur SEO
python -m pytest tests/test_seo_validator.py
```

## 🚀 Déploiement

### GitHub Pages

Le déploiement est automatique via GitHub Pages :

1. **Push** des articles vers `main`
2. **GitHub Pages** sert automatiquement le contenu
3. **Domaine** `blog.goseminary.com` pointe vers le site
4. **SSL** automatique via GitHub

### Domaine Personnalisé

Pour configurer un domaine personnalisé :

1. Modifier `CNAME` avec votre domaine
2. Configurer les DNS chez votre registrar :
   ```
   Type: CNAME
   Name: blog (ou @)
   Value: username.github.io
   ```
3. Activer HTTPS dans Settings > Pages

## 🔒 Sécurité

### Gestion des Secrets

- ✅ Clés API stockées dans GitHub Secrets
- ✅ Pas de clés en dur dans le code
- ✅ Accès limité aux repositories privés

### Validation du Contenu

- ✅ Validation HTML avant publication
- ✅ Filtrage de contenu inapproprié
- ✅ Vérification des liens externes

## 📈 Performance

### Optimisations

- **Cache Unsplash:** Évite les recherches répétitives
- **Images optimisées:** Redimensionnement automatique
- **Génération incrémentale:** Évite la régénération inutile
- **Retry automatique:** Gestion robuste des erreurs API

### Métriques Typiques

- **Temps de génération:** 2-5 minutes par article
- **Taille des articles:** 800-2000 mots (5-15 KB HTML)
- **Score SEO moyen:** 85-95/100
- **Images par article:** 1-3 images optimisées

## 🤝 Contribution

### Développement Local

```bash
# Cloner le repository
git clone https://github.com/TimHub88/seminary_blog.git

# Créer une branche de développement
git checkout -b feature/nouvelle-fonctionnalite

# Développer et tester
python scripts/article_generator.py --test

# Commit et push
git add .
git commit -m "Nouvelle fonctionnalité: ..."
git push origin feature/nouvelle-fonctionnalite
```

### Tests

```bash
# Exécuter tous les tests
python -m pytest tests/

# Tests spécifiques
python -m pytest tests/test_seo_validator.py -v
```

## 📞 Support

### Contacts

- **Développeur:** TimHub88
- **Repository:** https://github.com/TimHub88/seminary_blog
- **Issues:** https://github.com/TimHub88/seminary_blog/issues

### Documentation

- **API Chutes AI:** [Documentation officielle]
- **API Unsplash:** https://unsplash.com/developers
- **GitHub Actions:** https://docs.github.com/en/actions

## 📝 Changelog

### Version 1.0.0 (Actuelle)
- ✅ Pipeline 4-pass complet
- ✅ Système de contexte intelligent
- ✅ Intégration Seminary automatique
- ✅ Workflow GitHub Actions
- ✅ Gestion d'images Unsplash
- ✅ Validation SEO multi-couches

### Roadmap Futur
- 🔮 Intégration Google Analytics
- 🔮 A/B testing des titres
- 🔮 Génération de newsletters
- 🔮 Optimisation pour Core Web Vitals

---

**Seminary Blog** - Générer automatiquement du contenu de qualité pour les séminaires d'entreprise dans les Vosges 🏔️✨