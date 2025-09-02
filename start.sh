#!/bin/bash
set -e

# --- Variables ---
MODEL_DIR=/app/models
FASTAPI_PORT=8000
STREAMLIT_PORT=${PORT:-8080}

# Ajouter /app au PYTHONPATH pour que utils soit trouvé
export PYTHONPATH=/app

# Créer le dossier modèles
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

# --- Lancer FastAPI en arrière-plan ---
echo "🚀 Démarrage FastAPI sur le port $FASTAPI_PORT..."
uvicorn app.app_fastapi:app --host 0.0.0.0 --port $FASTAPI_PORT --log-level info &

# --- Vérifier que FastAPI est prêt via HTTP ---
echo "⏳ Vérification que FastAPI est démarré..."
for i in {1..10}; do
    if curl -s http://localhost:$FASTAPI_PORT/docs >/dev/null 2>&1; then
        echo "✅ FastAPI est prêt."
        break
    fi
    sleep 1
done

# --- Lancer Streamlit au premier plan ---
echo "🚀 Démarrage Streamlit sur le port $STREAMLIT_PORT..."
exec streamlit run app/app_streamlit.py \
    --server.port=$STREAMLIT_PORT \
    --server.address=0.0.0.0 \
    --logger.level=info
