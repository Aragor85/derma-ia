# config.py

import os

# ------------------------------
# 🔑 Clé de connexion Azure Blob Storage
# ------------------------------
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if not AZURE_STORAGE_CONNECTION_STRING:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING n'est pas défini !")

# ------------------------------
# 📦 Nom du container où sont stockés les modèles
# ------------------------------
BLOB_CONTAINER_NAME = "dermatologiemodels"

# ------------------------------
# 📂 Noms simples des blobs (⚠️ PAS d’URL complète ici !)
# ------------------------------
BLOB_MODELS = {
    "unet": "unet_model.h5",
    "cnn": "cnn_model.h5",
    "yolo": "yolov8_model.pt",
}

# ------------------------------
# 🔑 Clé API Mistral (optionnelle pour LLM)
# ------------------------------
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# ------------------------------
# 📌 Paramètres optionnels supplémentaires (exemple)
# ------------------------------
# Taille d’image pour U-Net/CNN
#IMG_SIZE = (256, 256)

# Confiance minimale pour YOLO (si utilisé dans le filtrage)
YOLO_CONF_THRESHOLD = 0.3
