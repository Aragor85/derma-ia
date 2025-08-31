import os

# Clé API Mistral
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "hrupvGAkYlrC9AsZTFChVFpbl2drY009")

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING",
    "DefaultEndpointsProtocol=...;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"
)
BLOB_CONTAINER_NAME = "dermatologiemodels"

# Noms des blobs pour les modèles
BLOB_MODELS = {
    "unet": "unet_model.h5",
    "cnn": "cnn_model.h5",
    "yolo": "yolov8_model.pt"
}
