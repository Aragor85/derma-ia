#!/bin/bash
set -e

# --- Variables ---
MODEL_DIR=/app/models
FASTAPI_PORT=8000                # Port interne FastAPI
STREAMLIT_PORT=${PORT:-8080}    # Port exposé par Azure

# --- Création du dossier modèles ---
mkdir -p "$MODEL_DIR"

# --- Téléchargement modèles si manquants ---
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
    else
        echo "✅ $name déjà présent."
    fi
done

# --- Lancer FastAPI en arrière-plan avec logs vers stdout/stderr ---
echo "🚀 Démarrage FastAPI sur le port $FASTAPI_PORT..."
uvicorn app.app_fastapi:app --host 0.0.0.0 --port $FASTAPI_PORT --log-level info &

# --- Attendre que FastAPI soit prêt (10 secondes max) ---
echo "⏳ Vérification que FastAPI est démarré..."
for i in {1..10}; do
    if nc -z localhost $FASTAPI_PORT; then
        echo "✅ FastAPI est prêt."
        break
    fi
    sleep 1
done

# --- Lancer Streamlit au premier plan pour Azure ---
echo "🚀 Démarrage Streamlit sur le port $STREAMLIT_PORT..."
exec streamlit run app/app_streamlit.py \
    --server.port=$STREAMLIT_PORT \
    --server.address=0.0.0.0 \
    --logger.level=info
