# Image de base Python 3.10 légère
FROM python:3.10-alpine

# Installer dépendances système nécessaires
RUN apk add --no-cache \
    build-base \
    bash \
    curl \
    nginx \
    netcat-openbsd \
    libstdc++ \
    mesa-gl \
    glib \
    libxext \
    libxrender \
    libsm \
    git \
    && rm -rf /var/cache/apk/*

# Créer un répertoire pour l'application
WORKDIR /app

# Copier requirements.txt si tu en as un
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer le port pour FastAPI et/ou Streamlit
EXPOSE 8000
EXPOSE 8501

# Commande par défaut (ici FastAPI avec uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
