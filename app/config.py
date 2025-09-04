# config.py

import os

# 🔑 Clé de connexion Azure Blob Storage (à récupérer dans ton compte de stockage)
AZURE_STORAGE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING",
    "DefaultEndpointsProtocol=https;AccountName=dermatologieiastorage;AccountKey=TON_CLE_AZURE;EndpointSuffix=core.windows.net"
)

# 📦 Nom du container où sont stockés tes modèles
BLOB_CONTAINER_NAME = "dermatologiemodels"

# 📂 Noms simples des blobs (⚠️ PAS d’URL complète ici !)
BLOB_MODELS = {
    "unet": "unet_model.h5",
    "cnn": "cnn_model.h5",
    "yolo": "yolov8_model.pt",
}

# 🔑 Clé API Mistral (optionnelle pour tes LLM)
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
