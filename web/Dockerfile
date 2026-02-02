FROM node:18-alpine AS base

# 1. Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# 2. Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1

ARG NEXT_PUBLIC_API_BASE
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE

RUN npm run build

# 3. Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# 1. On crée le groupe s'il n'existe pas
# 2. On vérifie si l'UID 1000 est déjà pris. 
#    Si oui, on renomme l'utilisateur existant en 'user'.
#    Si non, on crée l'utilisateur 'user' avec l'UID 1000.
RUN addgroup -S -g 1001 nodejs || true && \
    if [ $(getent passwd 1000 | cut -d: -f1) ]; then \
    old_user=$(getent passwd 1000 | cut -d: -f1); \
    if [ "$old_user" != "user" ]; then \
    sed -i "s/$old_user/user/g" /etc/passwd; \
    fi; \
    else \
    adduser -S -u 1000 user -G nodejs; \
    fi

COPY --from=builder /app/public ./public

# On donne les droits à l'utilisateur 'user' (qui possède maintenant l'UID 1000)
RUN mkdir .next && chown -R user:nodejs .next

COPY --from=builder --chown=user:nodejs /app/.next/standalone ./
COPY --from=builder --chown=user:nodejs /app/.next/static ./.next/static

USER user
# --------------------------------------------------

EXPOSE 7860
ENV PORT 7860
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]