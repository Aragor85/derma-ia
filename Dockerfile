# --- Base image Python 3.10 slim ---
FROM python:3.10-slim

# --- Répertoire de travail ---
WORKDIR /app

# --- Installer dépendances système nécessaires ---
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    git \
    && rm -rf /var/lib/apt/lists/*

# --- Copier tout le code et les scripts ---
COPY . .

# --- Installer les dépendances Python ---
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# --- Port exposé pour Azure App Service ---
ENV PORT=8080
EXPOSE 8080

# --- Lancer le script de démarrage ---
CMD ["bash", "start.sh"]
