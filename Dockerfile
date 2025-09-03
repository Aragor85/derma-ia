# Base Python légère
FROM python:3.10-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OMP_NUM_THREADS=1 \
    TF_NUM_INTRAOP_THREADS=1 \
    TF_NUM_INTEROP_THREADS=1 \
    TORCH_NUM_THREADS=1

# Installer dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de l’application
WORKDIR /app

# Copier requirements.txt et installer dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Copier seulement le code (pas les datasets / modèles)
COPY app ./app
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Exposer les ports
EXPOSE 8000 8501

# Commande par défaut
CMD ["/start.sh"]
