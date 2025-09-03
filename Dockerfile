FROM python:3.10-slim

WORKDIR /app

# Dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Installer dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier app + scripts
COPY . .

# Copier la config NGINX
COPY nginx.conf /etc/nginx/nginx.conf

# Exposer uniquement le port NGINX
EXPOSE 8080

# Lancer le script
CMD ["bash", "start.sh"]
