# CreditRisk

Modélisation prédictive du risque de crédit pour l'inclusion financière.

## Objectif

Ce projet vise à développer un système intelligent capable d’évaluer automatiquement la solvabilité d’un demandeur de crédit, afin de soutenir l’inclusion financière des petites entreprises et agriculteurs dans la région.

## Fonctionnalités

- Analyse exploratoire des données (EDA)
- Préparation et nettoyage des données
- Modélisation prédictive (RandomForest, XGBoost, Logistic Regression, Stacking)
- API REST pour la prédiction et l'explication des décisions
- Visualisations et rapports automatisés (HTML, PDF, slides)

## Structure du projet

## Demo presets

To generate realistic demo presets from `Data/nouvelle_donnee_predite_filtre.csv`:

```bash
# quick check without writing files
python Data/generate_presets.py --dry-run

# write 10 presets into web/public/presets.json (auto-picked by the SPA)
python Data/generate_presets.py --out web/public/presets.json

# or use the helper shell script
bash Data/presets.sh

# customize counts
python Data/generate_presets.py --n-high 4 --n-mid 3 --n-low 3 --out web/public/presets.json
```

The web UI loads `public/presets.json` when present and falls back to built-in samples otherwise.
.
├── API/                  # Code de l'API FastAPI, modèles ML, preprocessing, logs
├── Data/                 # Jeux de données (train, test, economic indicators, etc.)
├── Models/               # Modèles sauvegardés
├── Notebook/             # Notebooks d'analyse, modélisation, interprétation
├── Src/                  # (optionnel) Code source additionnel
├── logs/                 # Logs d'exécution
├── LICENSE               # License du projet
├── docker-compose.yml    # Déploiement Docker
├── promtail-config.yaml  # Config pour la collecte de logs
├── requirements.txt      # Dépendances Python

1. **Installation**

   ```sh
   git clone https://github.com/<ton-user>/CreditRisk_WestAfrica.git
   cd CreditRisk_WestAfrica
   ```

2. **Créer un environnement virtuel :**

   ```sh
   python3 -m venv creditriskwestafricavenv
   source creditriskwestafricavenv/bin/activate
   ```

3. **Installer les dépendances :**

   ```sh
   pip install -r requirements.txt
   ```

4. **Configurer l'environnement :**
   - Copier `.env.example` en `.env` et adapter les variables si besoin.

## Utilisation

### 1. Analyse et Modélisation

- Ouvre et exécute le notebook principal :

  ```
  Notebook/book.ipynb
  ```

- Les rapports sont générés automatiquement dans `Docs/Rapport/`.

### 2. API de prédiction

# CreditRisk West Africa

Modélisation prédictive du risque de crédit pour l'inclusion financière en Afrique de l'Ouest.

Ce dépôt contient :

- une API FastAPI pour obtenir des prédictions et explications (SHAP),
- les pipelines et modèles entraînés (RandomForest, XGBoost, LogisticRegression, Stacking),
- les éléments de préprocessing (scaler, encoders, liste de features),
- une application web (Next.js) consommant l'API pour démo.

## Contenu important

- `API/` : code de l'API, preprocessing, modèles, routes et gestion des clés API.
- `Data/` : jeux de données et scripts utilitaires (ex : génération de presets).
- `Notebook/` : notebooks d'analyse et de reporting.
- `Docs/` : rapports et livrables exportés.
- `web/` : interface SPA (Next.js) pour démo.
- `requirements.txt` : dépendances Python.

## Quickstart (local)

1. Cloner le repo

```bash
git clone https://github.com/kjd-dktech/CreditRisk_WestAfrica.git
cd CreditRisk_WestAfrica
```

2. Créer un environnement Python et installer les dépendances

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Variables d'environnement importantes

- `MASTER_SECRET` : secret administrateur utilisé pour générer/administrer les API keys (header `X-ADMIN-SECRET`).
- (optionnel) `NEXT_PUBLIC_API_BASE` pour la configuration côté `web`.

Copier `.env.example` → `.env` si fourni, sinon exportez `MASTER_SECRET` avant d'utiliser les routes d'administration.

4. Lancer l'API en développement

```bash
cd API
uvicorn main:app --reload
```

La doc interactive est disponible par défaut sur `http://localhost:8000/docs`.

## Endpoints principaux (API)

- `GET /` : info et endpoints disponibles
- `GET /health` : état de santé (indique si modèle/explainer chargés)
- `GET /metadata` : metadata utiles (ex : valeurs de loan_type)
- `POST /predict` : prédiction (corps JSON — voir `API/main.py` pour le schéma)
- `POST /proba` : probabilité seule
- `POST /explain` : explication SHAP (si `explainer.pkl` chargé)

Routes d'administration / gestion des clés API (API/routes & API/security) :

- `POST /get-api-key` (ou `POST /create-key` dans `routes`) — nécessite header admin (`X-ADMIN-SECRET` / `MASTER_SECRET`)
- `POST /disable-key` — désactiver une clé
- Tableau d'administration HTML sur `/admin` (route protégée admin)

Notes :

- Les mécanismes d'authentification utilisent : header `X-API-Key` pour les requêtes clients (limitation quotidienne) et `X-ADMIN-SECRET` pour actions admin.
- Le code d'exemple actuel pour l'API publique (`API/main.py`) ne force pas l'utilisation de `verify_api_key` sur `/predict` — si vous souhaitez protéger `/predict`, il faut ajouter la dépendance `Depends(verify_api_key)` sur les endpoints correspondants.

## Fichiers et artefacts ML

- Modèles sauvegardés : `API/ml_models/` (pkl) — ex : `stacking_model.pkl`, `RandomForest_pipeline.pkl`, `XGBoost_pipeline.pkl`, `LogisticRegression_pipeline.pkl`.
- Explainer SHAP : `API/shap_explainer/explainer.pkl` (optionnel mais utilisé par `/explain`).
- Préprocessing / artefacts : `API/processing_elements/` — `scaler.pkl`, `Hot_encoder.pkl`, `feature_list.pkl`, `loan_type_dtype*.pkl`.

## Préprocessing attendu

L'entrée attendue par l'API (voir `LoanProfile` dans `API/main.py`):

```json
{
   "Total_Amount": 1000.0,
   "Total_Amount_to_Repay": 1200.0,
   "Amount_Funded_By_Lender": 1000.0,
   "duration": 90,
   "Lender_portion_to_be_repaid": 1200.0,
   "loan_type": "Type_7"  // correspondance gérée via les dtype / mapping
}
```

Le preprocessing effectue : typage de `loan_type` (cat), création de `repayment_ratio`, encodage (`loan_type_encoded`), sélection des features selon `feature_list.pkl`, remplissage des NaN par 0 et standardisation.

## Docker / Déploiement

- Docker Compose (dev) : `docker-compose.yml` contient services `api` et `web` (API exposée sur `8000` localement).
- Render : le fichier `.render.yml` montre un démarrage avec `uvicorn API/main.py:app` (port `10000` dans ce fichier). Assurez-vous que la config de déploiement et le docker-compose utilisent les mêmes ports/commandes.

## Web UI

- `web/` contient l'application Next.js qui consomme l'API. Configurez la base API via `NEXT_PUBLIC_API_BASE` ou `web/src/lib/config.ts`.

## Génération de presets (demo)

Exemples pour générer des données de démonstration depuis `Data/nouvelle_donnee_predite_filtre.csv` :

```bash
# vérification sans écrire
python Data/generate_presets.py --dry-run

# écrire 10 presets dans web/public/presets.json
python Data/generate_presets.py --out web/public/presets.json

# ou utiliser le script helper
bash Data/presets.sh
```

## Crédits

- Auteur principal : Kodjo Jean DEGBEVI - *Kodjojeandegbevi@gmail.com* - DKTech Innovations

## Licence

Voir `LICENSE`.

---
Fin du README — modifié automatiquement pour clarifier installation, architecture et points à vérifier.
