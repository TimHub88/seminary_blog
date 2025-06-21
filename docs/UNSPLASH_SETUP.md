# Guide de Configuration Unsplash API

## 📋 Vue d'ensemble

Ce guide vous aide à configurer l'API Unsplash pour votre blog Seminary, en suivant la [documentation officielle Unsplash](https://unsplash.com/documentation).

## 🔑 Types de Clés API

### Access Key (Obligatoire)
- **Usage**: Mode démo et production
- **Limite démo**: 50 requêtes/heure
- **Format**: `Client-ID your_access_key`

### Secret Key (Optionnel - Production)
- **Usage**: Mode production uniquement
- **Limite production**: 5000 requêtes/heure
- **Nécessite**: Approbation d'Unsplash

## 🚀 Configuration Étape par Étape

### 1. Créer un Compte Développeur

1. Allez sur [Unsplash Developers](https://unsplash.com/developers)
2. Cliquez sur "Register as a developer"
3. Acceptez les termes d'utilisation

### 2. Créer une Application

1. Connectez-vous à votre [dashboard](https://unsplash.com/oauth/applications)
2. Cliquez sur "New Application"
3. Remplissez les informations :
   - **Application name**: "Seminary Blog"
   - **Description**: "Blog système automatisé pour Seminary - séminaires d'entreprise dans les Vosges"
   - **Website**: "https://blog.goseminary.com"
   - **Accept terms**: ✅

### 3. Récupérer les Clés

Après création, vous obtenez :
- **Access Key**: Utilisable immédiatement (mode démo)
- **Secret Key**: Pour la production (après approbation)

## ⚙️ Configuration Seminary Blog

### Variables d'Environnement

Ajoutez dans GitHub Secrets :

```
UNSPLASH_ACCESS_KEY=your_access_key_here
UNSPLASH_SECRET_KEY=your_secret_key_here  # Optionnel
```

### Mode Démo vs Production

| Mode | Access Key | Secret Key | Limite | Status |
|------|------------|------------|--------|--------|
| **Démo** | ✅ | ❌ | 50 req/h | Immédiat |
| **Production** | ✅ | ✅ | 5000 req/h | Après approbation |

## 📈 Passer en Production

### Critères d'Approbation

1. **Application fonctionnelle** avec images Unsplash
2. **Attribution correcte** (nom photographe + lien Unsplash)
3. **Usage respectueux** des guidelines
4. **Trafic réel** sur votre application

### Processus d'Approbation

1. Dans votre dashboard Unsplash, cliquez "Apply for Production"
2. Remplissez le formulaire :
   - URL de l'application : `https://blog.goseminary.com`
   - Description de l'usage
   - Capture d'écran de l'attribution
3. Attendez la réponse (généralement quelques jours)

## 🔧 Test de Configuration

### Test Local

```bash
cd seminary_blog
python scripts/image_handler.py --access-key "your_key" --test-illustrations
```

### Test Complet

```bash
python scripts/article_generator.py \
  --chutes-api-key "your_chutes_key" \
  --unsplash-access-key "your_unsplash_key" \
  --dry-run
```

## 📊 Surveillance des Quotas

Le système Seminary affiche automatiquement :
- Mode actuel (démo/production)
- Requêtes utilisées/restantes
- Status des limites

Logs exemple :
```
Configuration Unsplash: Démo - 45 requêtes restantes
Trouvé 5 images Unsplash pour 'mountain meeting' (requêtes: 5/50)
```

## ⚡ Fonctionnalités Seminary

### Images Automatiques
- Recherche intelligente basée sur le contenu
- Alt-text SEO optimisé
- Attribution automatique
- Cache pour éviter les requêtes répétitives

### Illustrations CSS/SVG
- Graphiques en barres animés
- Cercles de progression
- Infographies processus
- Diagrammes de flux
- Grilles d'icônes thématiques

### Intégration Intelligente
- 1-2 illustrations par article selon la longueur
- Positionnement stratégique dans le contenu
- Styles responsive intégrés
- Animations CSS Seminary

## 🛡️ Bonnes Pratiques

### Attribution Requise
- Nom du photographe
- Lien vers leur profil Unsplash
- UTM tracking avec `utm_source=seminary_blog`

### Respect des Limites
- Cache local des recherches (1h)
- Fallback vers images Picsum si quota atteint
- Monitoring automatique des requêtes

### SEO Optimisé
- Alt-text descriptif et keyword-rich
- Lazy loading des images
- Formats optimisés (WebP/JPEG)
- Compression automatique

## 🆘 Résolution de Problèmes

### ❌ "Clé API Unsplash manquante"
```bash
# Vérifiez la variable d'environnement
echo $UNSPLASH_ACCESS_KEY

# Testez la clé manuellement
curl -H "Authorization: Client-ID your_key" \
  "https://api.unsplash.com/photos/random"
```

### ❌ "Limite de requêtes atteinte"
- **Solution immédiate**: Attendez 1h pour reset
- **Solution permanente**: Demandez l'approbation production

### ❌ "Images de fallback utilisées"
- Vérifiez votre clé API
- Contrôlez votre quota restant
- Vérifiez votre connexion internet

## 📚 Ressources

- [Documentation Unsplash API](https://unsplash.com/documentation)
- [Guidelines Unsplash](https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines)
- [Seminary Blog Repository](https://github.com/your-username/seminary_blog)

---

💡 **Astuce**: Commencez en mode démo pour tester, puis demandez la production une fois le système stable et fonctionnel. 