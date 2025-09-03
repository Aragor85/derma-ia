# Image de base légère Debian/Ubuntu
FROM python:3.10-slim

# Variables d'environnement pour pip
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    netcat \
    nginx \
    git \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de l'application
WORKDIR /app

# Copier requirements.txt et installer dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer les ports pour FastAPI et Streamlit
EXPOSE 8000 8501

# Commande par défaut pour lancer FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
