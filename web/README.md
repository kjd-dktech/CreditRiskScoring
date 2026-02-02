# Web — Interface Next.js

Interface utilisateur moderne pour visualiser les scores de crédit et leur explication.

## Stack Technique

- **Framework** : Next.js 13+ (App Router)
- **Styling** : Tailwind CSS
- **État** : React Hooks

## Configuration

L'URL de l'API Backend est définie via la variable `NEXT_PUBLIC_API_BASE`.

- **Avec Docker** : Géré automatiquement (`http://localhost:7860` mappé).
- **En Local** : Par défaut sur `http://localhost:8000`.

## Scripts

```bash
cd web
npm install

# Développement (localhost:3000)
npm run dev

# Construction Production
npm run build
npm start
```
