# API — Backend FastAPI

Une API robuste pour l'évaluation du risque de crédit avec explicabilité (SHAP).

## Fonctionnalités

- **Prédiction** : Probabilité de défaut, classe (0/1), niveau de risque.
- **Explicabilité** : Contributions locales des features (valeurs SHAP).
- **Sécurité** : Gestion de clé API et limitation de débit (Rate Limiting).

## Utilisation Locale

### Avec Docker (Recommandé)
Accessible sur `http://localhost:7860`.

### Sans Docker (Python)
Accessible sur `http://localhost:8000`.

```bash
cd API
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

## Endpoints Clés

- `POST /predict`: Scoring complet (proba, risque, confiance).
- `POST /explain`: Contributions SHAP.
- `GET /metadata`: Informations sur les catégories et types attendus.

## Configuration

Les variables d'environnement suivantes sont supportées (voir `.env`):
- `API_KEY`: Clé pour protéger les endpoints (défaut: publique si vide).
- `ALLOWED_ORIGINS`: CORS (défaut: `*`).
- `RATE_LIMIT_PER_MIN`: Requêtes max/min par client.
