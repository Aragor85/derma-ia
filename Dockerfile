# Base légère avec Python 3.10
FROM python:3.10-alpine  

# Installer dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    netcat-openbsd \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier seulement requirements et installer
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Copier le fichier NGINX
COPY nginx.conf /etc/nginx/nginx.conf

# Exposer le port Azure
EXPOSE 8080

# Lancer le script de démarrage
CMD ["bash", "start.sh"]
