# API — Credit‑Risk‑Scoring

Ce dossier contient l'API FastAPI qui fournit les prédictions et les explications (SHAP) pour des profils de prêt.

## Résumé rapide

- Entrée principale : `API/main.py` (FastAPI).
- Endpoints exposés : `/`, `/health`, `/metadata`, `/predict`, `/proba`, `/explain`.
- Modèles et artefacts : `API/ml_models/`, `API/shap_explainer/`, `API/processing_elements/`.

## Installation locale

Depuis la racine du projet :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd API
uvicorn main:app --reload
```

L'API sera disponible par défaut sur `http://127.0.0.1:8000` et la documentation interactive Swagger à `http://127.0.0.1:8000/docs`.

## Endpoints (détails)

- `GET /` — message d'accueil et liste rapide d'endpoints.
- `GET /health` — retourne l'état de santé et indique si le modèle / explainer ont été chargés.
- `GET /metadata` — fournit des valeurs de référence (ex. catégories attendues pour `loan_type`).
- `POST /predict` — effectue la prédiction pour un profil de prêt (retourne probabilité, prédiction binaire, niveau de risque et confiance).
- `POST /proba` — renvoie uniquement la probabilité de défaut.
- `POST /explain` — renvoie les contributions SHAP si `explainer.pkl` est présent, sinon une réponse dégradée est retournée.

### Schéma d'entrée (exemple)

Corps JSON attendu (défini par `LoanProfile` dans `API/main.py`) :

```json
{
  "Total_Amount": 1000.0,
  "Total_Amount_to_Repay": 1200.0,
  "Amount_Funded_By_Lender": 1000.0,
  "duration": 90,
  "Lender_portion_to_be_repaid": 1200.0,
  "loan_type": "Type_7"
}
```

### Exemple curl pour `/predict`

```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"Total_Amount":1000,"Total_Amount_to_Repay":1200,"Amount_Funded_By_Lender":1000,"duration":90,"Lender_portion_to_be_repaid":1200,"loan_type":"Type_7"}'
```

## Comportement et sécurité

- Le code actuel charge les artefacts depuis `API/ml_models/` et `API/shap_explainer/` si présents ; il retourne une erreur 503 si le modèle principal n'est pas chargé.
- À l'état actuel du code, les endpoints ne sont pas nécessairement protégés par une vérification automatique de clé API. Si vous voulez activer une protection (par exemple header `X-API-Key`), il faudra ajouter la dépendance FastAPI `Depends(verify_api_key)` sur les routes concernées et implémenter la gestion des clés/API.

## Emplacements des artefacts ML

- Modèles picklés : `API/ml_models/` (ex. `stacking_model.pkl`).
- Explainer (SHAP) : `API/shap_explainer/explainer.pkl` (optionnel).
- Préprocessing : `API/processing_elements/` (`scaler.pkl`, `Hot_encoder.pkl`, `feature_list.pkl`, `loan_type_dtype*.pkl`).

## Journalisation

Les logs, si configurés, peuvent être écrits dans `API/logs/` ou fournis par la configuration de log du projet. Le code utilise des impressions et peut s'appuyer sur des bibliothèques (ex. `loguru`) selon les modules présents.

## Déploiement

Le dépôt peut être packagé pour Docker / Docker Compose ou déployé sur une plateforme cloud. Pour un déploiement production :

- utilisez une image Python optimisée et un process manager ASGI (uvicorn/gunicorn) ;
- sécurisez l'accès aux endpoints (authentification, rate limiting) ;
- gérez les secrets via votre plateforme (Vault, variables d'environnement, service provider secrets).

## Support & contact

Auteur : Kodjo Jean DEGBEVI

Si une information manque ou si vous souhaitez que je documente un élément plus en détail (ex. schéma complet des features après preprocessing, gestion des API keys), dites-le et j'actualiserai ce README.
