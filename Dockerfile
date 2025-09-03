FROM python:3.10-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    netcat-openbsd \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Installer TensorFlow
RUN pip install --upgrade pip && pip install tensorflow==2.16.1

# Copier les fichiers de l'application
WORKDIR /app
COPY . .

# Exposer les ports nécessaires
EXPOSE 8000 8501

# Commande de démarrage
CMD ["bash", "start.sh"]
