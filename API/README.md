# API — FastAPI pour le scoring

[![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/) [![license](https://img.shields.io/github/license/kjd-dktech/CreditRiskScoring?color=blue)](../LICENSE)

Ce dossier contient l'API FastAPI qui sert les prédictions et (optionnellement) les explications SHAP.

## Lancer localement

1. Depuis la racine du repo, créer l'environnement et installer les dépendances :

  ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
  ```

2. Démarrer l'API :

  ```bash
    cd API
    uvicorn main:app --reload
  ```

  Swagger UI : `http://127.0.0.1:8000/docs`.

## Endpoints principaux

- `GET /` — accueil
- `GET /health` — état de santé (modèle/explainer chargés)
- `GET /metadata` — métadonnées (ex : catégories attendues pour `loan_type`)
- `POST /predict` — prédiction (voir schéma ci‑dessous)
- `POST /proba` — renvoie la probabilité de défaut
- `POST /explain` — contributions SHAP (si explainer disponible)

Exemple d'entrée (cf. `LoanProfile` dans `API/main.py`):

```json
  {
    "Total_Amount": 1000.0,
    "Total_Amount_to_Repay": 1200.0,
    "duration": 90,
    "Lender_portion_to_be_repaid": 1200.0,
    "New_versus_Repeat": "Repeat Loan",
    "loan_type": "Type_7"
  }
```

Exemple curl pour `/predict` :

```bash
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"Total_Amount":1000,"Total_Amount_to_Repay":1200,"Amount_Funded_By_Lender":1000,"duration":90,"Lender_portion_to_be_repaid":1200,"loan_type":"Type_7"}'
```

## Artefacts requis

- `API/ml_models/` : modèles et pipelines picklés (.pkl)
- `API/shap_explainer/` : (optionnel) `explainer.pkl` pour `/explain`
- `API/processing_elements/` : scalers/encoders/lists (ex : `feature_list.pkl`)

Si le modèle principal est absent l'API retourne 503 (vérifier les logs au démarrage pour confirmer le chargement des artefacts).

## Sécurité

- Les routes peuvent être protégées par une vérification d'API key (header `X-API-Key`) et les actions d'administration par `X-ADMIN-SECRET` / variable `MASTER_SECRET`.
- Le code contient des helpers pour la gestion des clés (voir `API/routes` et `API/security`) — activer les dépendances FastAPI `Depends(verify_api_key)` sur les routes à protéger.

## Déploiement

- Préparer une image Docker légère et exécuter l'ASGI server (uvicorn/gunicorn).
- Gérer les secrets via des variables d'environnement ou un secret manager.

## Support

Auteur : Kodjo Jean DEGBEVI — kodjojeandegbevi@gmail.com — DKTech Innovations
