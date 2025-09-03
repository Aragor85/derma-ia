# Base légère Python 3.10
FROM python:3.10-slim

# Variables d'environnement pour pip et pour limiter CPU threads
# Ajouter PATH pour que uvicorn et streamlit soient trouvés
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OMP_NUM_THREADS=1 \
    TF_NUM_INTRAOP_THREADS=1 \
    TF_NUM_INTEROP_THREADS=1 \
    TORCH_NUM_THREADS=1 \
    PATH="/usr/local/bin:$PATH"

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

# Copier requirements.txt et installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code et les modèles
COPY . .

# Exposer les ports FastAPI et Streamlit
EXPOSE 8000 8501

# Copier start.sh et rendre exécutable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Commande par défaut
CMD ["/start.sh"]
