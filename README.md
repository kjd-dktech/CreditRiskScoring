# CreditRiskScoring

Modélisation prédictive du risque de crédit pour l'inclusion financière.

[![license](https://img.shields.io/github/license/kjd-dktech/CreditRiskScoring?color=blue)](LICENSE) [![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

Projet complet comprenant :
- **API** : FastAPI, scikit-learn, SHAP (Backend)
- **Web** : Next.js, Tailwind CSS (Frontend)
- **Data** : Pipelines de preprocessing et modèles

## Démarrage rapide (Docker)

Méthode recommandée pour tester l'ensemble du projet.

```bash
docker compose up
```

- **Web** : [http://localhost:3000](http://localhost:3000)
- **Documentation API** : [http://localhost:7860/docs](http://localhost:7860/docs)

## Installation Manuelle (Développement)

Si vous n'utilisez pas Docker, vous devez lancer l'API et le Web séparément.

### 1. API

```bash
cd API
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
# Access: http://localhost:8000
```

### 2. Web

```bash
cd web
npm install
npm run dev
# Access: http://localhost:3000
```

## Structure

- `API/` : Backend FastAPI (preprocessing, modèles, endpoints).
- `web/` : Frontend Next.js.
- `Data/` : Jeux de données et scripts (génération de presets).
- `Notebook/` : Analyses exploratoires et rapports.
- `Docs/` : Documentation projet.

## Auteur

**Kodjo Jean DEGBEVI** — DKTech Innovations

