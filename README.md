# 🐦 Twitter Sentiment Analysis - Interface Streamlit

Interface web interactive pour l'analyse de sentiment de tweets en temps réel, utilisant un modèle BERTweet optimisé (ONNX).

## 🎯 Fonctionnalités

- 📝 **Saisie de tweets** - Interface intuitive pour analyser des tweets
- 🔍 **Analyse en temps réel** - Prédictions instantanées via API REST
- 📊 **Visualisation** - Graphiques de probabilités et métriques
- ✅ **Validation** - Feedback utilisateur sur les prédictions
- 📈 **Statistiques** - Suivi de la précision en temps réel
- ☁️ **CloudWatch** - Logging optionnel vers AWS CloudWatch
- 🚨 **Alertes SNS** - Notifications automatiques en cas de mauvaises prédictions

## 🚀 Déploiement sur Streamlit Cloud

### Prérequis

1. Un compte [Streamlit Cloud](https://streamlit.io/cloud) (gratuit)
2. Ce repository GitHub
3. Une API déployée sur AWS EC2 (voir instructions ci-dessous)

### Étapes de Déploiement

#### 1. Connecter le Repository à Streamlit Cloud

1. Allez sur [share.streamlit.io](https://share.streamlit.io/)
2. Cliquez sur **"New app"**
3. Connectez votre compte GitHub si nécessaire
4. Sélectionnez :
   - **Repository** : `GuillaumeC96/Streamlit-BerTweet`
   - **Branch** : `main`
   - **Main file path** : `app.py`
5. Cliquez sur **"Advanced settings"**

#### 2. Configurer les Secrets

Dans les **Advanced settings**, ajoutez vos secrets dans la section **Secrets** :

```toml
# URL de votre API AWS EC2
API_URL = "http://56.228.68.157:8000"

# Configuration AWS (optionnel)
AWS_REGION = "eu-north-1"
AWS_ACCESS_KEY_ID = "votre_access_key"
AWS_SECRET_ACCESS_KEY = "votre_secret_access_key"
SNS_TOPIC_ARN = "arn:aws:sns:eu-north-1:401399516096:twitter-sentiment-alerts"
```

**⚠️ IMPORTANT** :
- Remplacez `56.228.68.157` par l'IP actuelle de votre instance EC2
- Pour une IP fixe, utilisez une **Elastic IP** sur AWS
- Les credentials AWS sont optionnels (seulement pour CloudWatch/SNS)

#### 3. Déployer

1. Cliquez sur **"Deploy!"**
2. Attendez ~2-3 minutes que l'application démarre
3. Votre app sera disponible à : `https://votre-app-name.streamlit.app`

## 🔧 Installation Locale

### Prérequis

```bash
python 3.8+
pip
```

### Installation

```bash
# Cloner le repository
git clone https://github.com/GuillaumeC96/Streamlit-BerTweet.git
cd Streamlit-BerTweet

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier de secrets d'exemple
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Éditer secrets.toml avec votre URL d'API
nano .streamlit/secrets.toml
```

### Lancement

```bash
# Définir l'URL de l'API (alternative aux secrets)
export API_URL="http://56.228.68.157:8000"

# Lancer Streamlit
streamlit run app.py
```

L'interface sera accessible à : http://localhost:8501

## 🌐 Architecture

```
┌─────────────────────────────────────────────────────────┐
│              STREAMLIT CLOUD / LOCAL                     │
│                   (Port 8501)                            │
│  • Interface utilisateur                                 │
│  • Validation des prédictions                           │
│  • Statistiques en temps réel                           │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS/HTTP
                       ▼
┌─────────────────────────────────────────────────────────┐
│              API FASTAPI (AWS EC2)                       │
│              (IP: 56.228.68.157:8000)                   │
│  • Modèle BERTweet ONNX (515 MB)                       │
│  • Inférence CPU (~165ms)                               │
│  • Endpoints REST                                       │
└──────────────────────┬──────────────────────────────────┘
                       │ (Optionnel)
                       ▼
┌─────────────────────────────────────────────────────────┐
│              AWS CloudWatch + SNS                        │
│  • Logs des prédictions incorrectes                     │
│  • Métriques de performance                             │
│  • Alertes automatiques                                 │
└─────────────────────────────────────────────────────────┘
```

## 📊 Modèle

- **Architecture** : BERTweet (BERT pour Twitter)
- **Format** : ONNX (optimisé pour inférence)
- **Taille** : 515 MB
- **F1 Score** : 0.813
- **Seuil optimal** : 0.35
- **Performance** : ~165ms par prédiction (CPU)

## 🔑 Configuration

### Variables d'Environnement

| Variable | Description | Requis | Défaut |
|----------|-------------|--------|--------|
| `API_URL` | URL de l'API FastAPI | ✅ Oui | `http://localhost:8000` |
| `AWS_REGION` | Région AWS | ❌ Non | `eu-west-1` |
| `AWS_ACCESS_KEY_ID` | Access Key AWS | ❌ Non | - |
| `AWS_SECRET_ACCESS_KEY` | Secret Key AWS | ❌ Non | - |
| `SNS_TOPIC_ARN` | ARN du topic SNS | ❌ Non | - |

### Secrets Streamlit Cloud

Sur Streamlit Cloud, ajoutez ces valeurs dans **Settings → Secrets** :

```toml
API_URL = "http://56.228.68.157:8000"
```

## 🧪 Tests

### Test de Connexion API

Dans l'interface :
1. Cliquez sur **"Tester la connexion API"** dans la sidebar
2. Vérifiez que le statut est ✅

### Test de Prédiction

Exemples de tweets :
- **Positif** : "This is absolutely amazing! I love it so much!"
- **Négatif** : "This is terrible! Worst experience ever!"
- **Neutre** : "It's okay I guess, nothing special"

## 📖 API Backend

L'API backend doit être déployée séparément sur AWS EC2.

### Endpoints de l'API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Health check |
| `/predict` | POST | Prédiction d'un tweet |
| `/predict_batch` | POST | Prédictions en batch |
| `/model_info` | GET | Informations sur le modèle |
| `/docs` | GET | Documentation Swagger |

### Documentation Swagger

Disponible à : http://56.228.68.157:8000/docs

## 🔐 Sécurité

- ✅ Ne commitez **JAMAIS** le fichier `.streamlit/secrets.toml`
- ✅ Utilisez des variables d'environnement pour les credentials
- ✅ Sur Streamlit Cloud, configurez les secrets via l'interface web
- ⚠️ L'API est actuellement accessible publiquement (0.0.0.0/0)
- 💡 Recommandé : Utiliser une Elastic IP sur AWS

## 📈 Performance

- **Temps d'inférence** : ~165ms (CPU)
- **Latence réseau** : Variable selon votre connexion
- **Temps total** : ~200-300ms par prédiction

## 🆘 Troubleshooting

### "Connection error" dans l'interface

**Cause** : L'API n'est pas accessible

**Solution** :
1. Vérifiez que l'API est en ligne : `curl http://56.228.68.157:8000/health`
2. Vérifiez que le port 8000 est ouvert dans le Security Group AWS
3. Vérifiez l'URL dans les secrets Streamlit

### L'IP de l'API a changé

**Cause** : L'instance EC2 a été redémarrée sans Elastic IP

**Solution** :
1. Récupérez la nouvelle IP via la console AWS
2. Mettez à jour les secrets Streamlit Cloud
3. Redéployez l'application
4. **Recommandation** : Allouez une Elastic IP (gratuit si attachée)

### "ModuleNotFoundError"

**Cause** : Dépendances manquantes

**Solution** :
```bash
pip install -r requirements.txt
```

## 🎯 Roadmap

- [ ] Authentification utilisateur
- [ ] Historique des prédictions
- [ ] Export CSV des résultats
- [ ] Support multi-langues
- [ ] Mode batch avec upload de fichier
- [ ] Dashboard admin avec métriques avancées

## 📝 Licence

MIT License

## 👤 Auteur

Guillaume C. - [GitHub](https://github.com/GuillaumeC96)

## 🙏 Remerciements

- Modèle BERTweet par VinAI Research
- FastAPI par Sebastián Ramírez
- Streamlit par Snowflake

---

**🚀 Votre application est prête à être déployée sur Streamlit Cloud !**

Pour toute question, ouvrez une issue sur GitHub.
