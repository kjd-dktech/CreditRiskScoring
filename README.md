# CreditRiskScoring — scoring de risque de crédit

Modélisation prédictive du risque de crédit pour l'inclusion financière.

[![license](https://img.shields.io/github/license/kjd-dktech/CreditRiskScoring?color=blue)](LICENSE) [![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/) [![issues](https://img.shields.io/github/issues/kjd-dktech/CreditRiskScoring)](https://github.com/kjd-dktech/CreditRiskScoring/issues)

Projet de scoring de risque de crédit (préprocessing, modèles, API et interface web). Ce README donne l'essentiel pour exécuter et explorer le dépôt. Remplacez `kjd-dktech/CreditRiskScoring` par le chemin de votre dépôt GitHub pour activer les badges.

## Raccourci (si vous voulez tester rapidement)

1. Cloner le dépôt

   ```bash
      git clone https://github.com/kjd-dktech/CreditRiskScoring.git
      cd CreditRiskScoring
   ```

2. Créer un environnement Python et installer les dépendances

   ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      pip install -r requirements.txt
   ```

3. Lancer l'API en mode développement

   ```bash
      cd API
      uvicorn main:app --reload
   ```

   La documentation interactive Swagger sera disponible sur `http://127.0.0.1:8000/docs`.

4. (Facultatif) Démarrer le front-end (si vous avez Node.js)

   ```bash
      cd web
      npm install
      npm run dev
   ```

L'interface web par défaut sera sur `http://localhost:3000` et communiquera avec l'API (configurable via `NEXT_PUBLIC_API_BASE`).

## Arborescence principale (sélection)

- `API/` : API FastAPI (endpoints, preprocessing, modèles sauvegardés)
- `Data/` : jeux de données et scripts utilitaires (ex : génération de presets)
- `Notebook/` : notebooks d'exploration et rapports
- `web/` : application Next.js (demo UI)
- `Docs/` : rapports et exports

## Artefacts ML

- Modèles et pipelines : `API/ml_models/`
- Explainer SHAP : `API/shap_explainer/`
- Préprocessing / encoders / lists : `API/processing_elements/`

## Presets de démonstration

Un utilitaire génère des presets JSON utilisés par le front :

```bash
# dry-run
python Data/generate_presets.py --dry-run

# écrire des presets dans web/public/presets.json
python Data/generate_presets.py --out web/public/presets.json

# helper
bash Data/presets.sh
```

## Points d'attention / recommandations

- Vérifier que `API/ml_models/` contient bien les artefacts requis (pkl). L'API retourne 503 si le modèle principal est absent.
- Configurez `MASTER_SECRET` si vous utilisez les routes d'administration (header `X-ADMIN-SECRET`).
- Pour la production : sécurisez les endpoints (API keys, rate limiting), utilisez une image Python optimisée et un process manager ASGI.

## Contribution & contact

Auteur : Kodjo Jean DEGBEVI — kodjojeandegbevi@gmail.com — DKTech Innovations

Voir `LICENSE` pour les conditions d'utilisation.
