FROM python:3.10-slim

# Dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur pour éviter les problèmes de permissions
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copie des dépendances
COPY --chown=user requirements.txt $HOME/app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r $HOME/app/requirements.txt

# Copie des fichiers applicatifs
COPY --chown=user API $HOME/app/API
COPY --chown=user Data $HOME/app/Data

# Configuration des variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/home/user/app:/home/user/app/API"
# Hugging Face impose le port 7860
ENV PORT=7860

EXPOSE 7860

# Lancement avec le port 7860
CMD ["uvicorn", "API.main:app", "--host", "0.0.0.0", "--port", "7860"]