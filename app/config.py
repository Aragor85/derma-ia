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
