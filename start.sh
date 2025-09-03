#!/bin/bash
set -e

# --- Variables ---
MODEL_DIR=/app/models
FASTAPI_PORT=8000
STREAMLIT_PORT=8501   # interne (NGINX fera le proxy)
NGINX_PORT=8080

export PYTHONPATH=/app
mkdir -p "$MODEL_DIR"

# --- Téléchargement modèles ---
declare -A MODELS=(
    ["unet_model.h5"]="https://dermatologieiastorage.blob.core.windows.net/dermatologiemodels/unet_model.h5"
    ["cnn_model.h5"]="https://dermatologieiastorage.blob.core.windows.net/dermatologiemodels/cnn_model.h5"
    ["yolov8_model.pt"]="https://dermatologieiastorage.blob.core.windows.net/dermatologiemodels/yolov8_model.pt"
)

for name in "${!MODELS[@]}"; do
    path="$MODEL_DIR/$name"
    url="${MODELS[$name]}"
    if [ ! -f "$path" ]; then
        echo "📥 Téléchargement $name..."
        curl -L -o "$path" "$url"
        echo "✅ $name téléchargé."
    fi
done

# --- Lancer FastAPI ---
uvicorn app.app_fastapi:app --host 0.0.0.0 --port $FASTAPI_PORT --log-level info &

# --- Lancer Streamlit ---
streamlit run app/app_streamlit.py \
    --server.port=$STREAMLIT_PORT \
    --server.address=0.0.0.0 \
    --logger.level=info &

# --- Lancer NGINX ---
echo "🚀 Démarrage NGINX sur le port $NGINX_PORT..."
exec nginx -g "daemon off;"
