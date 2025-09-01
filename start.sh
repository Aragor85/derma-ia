#!/bin/bash
set -e

# --- Vérifier API Key ---
if [ -z "$MISTRAL_API_KEY" ]; then
  echo "❌ ERREUR : La variable d'environnement MISTRAL_API_KEY n'est pas définie."
  exit 1
fi
echo "✅ MISTRAL_API_KEY détectée."

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

# --- Ports ---
FASTAPI_PORT=${FASTAPI_PORT:-8000}
STREAMLIT_PORT=${PORT:-8080}

# --- Lancer FastAPI ---
echo "🚀 Démarrage FastAPI sur port $FASTAPI_PORT..."
uvicorn app.app_fastapi:app --host 0.0.0.0 --port $FASTAPI_PORT &

# --- Lancer Streamlit ---
echo "🚀 Démarrage Streamlit sur port $STREAMLIT_PORT..."
streamlit run app/app_streamlit.py --server.port=$STREAMLIT_PORT --server.address=0.0.0.0
