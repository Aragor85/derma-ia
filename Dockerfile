FROM python:3.10-slim

WORKDIR /app

# Installer dépendances système nécessaires pour la plupart des packages Python
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copier uniquement requirements.txt pour profiter du cache Docker
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Port exposé
ENV PORT=8080
EXPOSE 8080

# Lancer le script
CMD ["bash", "start.sh"]
