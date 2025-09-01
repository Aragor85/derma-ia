import os
import numpy as np
from PIL import Image
from sklearn.metrics import precision_score, recall_score
from azure.storage.blob import BlobServiceClient
import io
import logging
import config

logging.basicConfig(level=logging.INFO)

def download_blob_model(model_name, local_path):
    """Télécharge le modèle depuis Azure Blob Storage si absent localement."""
    if os.path.exists(local_path):
        logging.info(f"✅ Modèle {model_name} déjà présent.")
        return local_path

    blob_service_client = BlobServiceClient.from_connection_string(config.AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=config.BLOB_CONTAINER_NAME,
                                                      blob=config.BLOB_MODELS[model_name])

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "wb") as f:
        f.write(blob_client.download_blob().readall())
    logging.info(f"✅ Modèle {model_name} téléchargé depuis Blob.")
    return local_path

def preprocess_image(image, target_size=(256,256)):
    image = image.resize(target_size)
    arr = np.array(image) / 255.0
    if len(arr.shape) == 2:
        arr = np.expand_dims(arr, -1)
    return np.expand_dims(arr, 0)

def calculate_metrics(y_true, y_pred):
    precision = precision_score(y_true.flatten(), y_pred.flatten(), zero_division=0)
    recall = recall_score(y_true.flatten(), y_pred.flatten(), zero_division=0)
    dice = (2 * precision * recall) / (precision + recall + 1e-7)
    total_loss = np.mean((y_true - y_pred)**2)
    return total_loss, dice, precision, recall

def convert_image_to_bytes(img_array):
    img = Image.fromarray((img_array*255).astype(np.uint8))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
