# Stage unique : base TensorFlow mini
FROM tensorflow/tensorflow:2.16.1-mini

# Variables d'environnement pour Docker et pip
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer dépendances système nécessaires pour OpenCV / Streamlit
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

# Créer le répertoire de l'application
WORKDIR /app

# Copier requirements.txt et installer les dépendances Python restantes
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer les ports pour FastAPI et Streamlit
EXPOSE 8000 8501

# Copier le script de démarrage et le rendre exécutable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Commande par défaut : lancer FastAPI et Streamlit via start.sh
CMD ["/start.sh"]
