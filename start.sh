#!/bin/bash
set -e

# --- Créer dossier modèles ---
mkdir -p /app/models

# --- Télécharger les modèles depuis Azure Blob si absent ---
declare -A MODELS
MODELS=(
    ["unet_model.h5"]="https://dermatologieiastorage.blob.core.windows.net/dermatologiemodels/unet_model.h5"
    ["cnn_model.h5"]="https://dermatologieiastorage.blob.core.windows.net/dermatologiemodels/cnn_model.h5"
    ["yolov8_model.pt"]="https://dermatologieiastorage.blob.core.windows.net/dermatologiemodels/yolov8_model.pt"
)

for name in "${!MODELS[@]}"; do
    path="/app/models/$name"
    url="${MODELS[$name]}"
    if [ ! -f "$path" ]; then
        echo "📥 Téléchargement $name..."
        curl -L -o "$path" "$url"
        echo "✅ $name téléchargé."
    else
        echo "✅ $name déjà présent."
    fi
done

# --- Lancer FastAPI ---
uvicorn app_fastapi:app --host 0.0.0.0 --port 8000 &

# --- Lancer Streamlit ---
streamlit run app_streamlit.py --server.port=${PORT:-8080} --server.address=0.0.0.0
