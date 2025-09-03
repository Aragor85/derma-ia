# ------------------------------
# Stage unique : base légère Python 3.10
# ------------------------------
FROM python:3.10-slim

# Variables d'environnement pour pip et threads CPU
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OMP_NUM_THREADS=1 \
    TF_NUM_INTRAOP_THREADS=1 \
    TF_NUM_INTEROP_THREADS=1 \
    TORCH_NUM_THREADS=1

# Installer dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-openbsd \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de l'application
WORKDIR /app

# Copier requirements et installer les packages
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier tout le code et les modèles
COPY . .

# Exposer les ports FastAPI et Streamlit
EXPOSE 8000 8501

# Copier start.sh et le rendre exécutable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Commande par défaut
CMD ["/start.sh"]
