# Web — interface Next.js

[![Vercel](https://img.shields.io/badge/deploy-ready-lightgrey)](https://vercel.com/) [![license](https://img.shields.io/github/license/kjd-dktech/CreditRiskScoring?color=blue)](../LICENSE)

Application SPA (Next.js + Tailwind) utilisée comme interface de démonstration pour l'API de scoring.

## Résumé

- Framework : Next.js (App Router), TypeScript
- Style : Tailwind CSS
- Emplacement de configuration API : `web/src/lib/config.ts` (utilise `process.env.NEXT_PUBLIC_API_BASE`)

## Démarrage en développement

Depuis le dossier `web/` :

```bash
    cd web
    npm install
    npm run dev
```

L'application démarre par défaut sur `http://localhost:3000`.

## Configuration

Le front utilise `web/src/lib/config.ts` :

```ts
    export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
```

Pour pointer vers une API distante en dev :

```bash
    export NEXT_PUBLIC_API_BASE=https://mon-api.example.com
    npm run dev
```

## Scripts utiles (depuis `web/`)

- `npm run dev` — démarre le serveur de développement (port 3000)
- `npm run build` — build de production
- `npm run start` — démarre le build en production
- `npm run lint` — lance ESLint

## Bonnes pratiques et recommandations

- Utiliser une variable d'environnement `NEXT_PUBLIC_API_BASE` pour configurer l'URL de l'API.
- Pour la production, déployer sur une plateforme adaptée (Vercel, Netlify, Docker + CDN) et protéger toute clé côté serveur.
- Vérifier la compatibilité Node.js/Next.js (préférer une version LTS récente).

## Déploiement

<!-- - Vercel : configuration simple si vous utilisez le repo GitHub (paramètres d'environnement `NEXT_PUBLIC_API_BASE`).
- Docker : builder l'image et servir le build statique derrière un reverse proxy.-->

## Structure

- `web/src/app` — pages / layout (App Router)
- `web/src/components` — composants UI
- `web/src/lib/config.ts` — configuration de base (API)
- `web/public/presets.json` — (optionnel) presets de démonstration générés depuis `Data/generate_presets.py`

## Note

La documentation de l'API se trouve dans `API/README.md` (endpoints `/predict`, `/explain`, etc.). Le front attend le format JSON compatible avec l'API décrite.

## Auteur

**Kodjo Jean DEGBEVI** - *kodjojeandegbevi@gmail.com* - DKTech Innovations
