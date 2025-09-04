#!/bin/bash
set -e

# ------------------------------
# Ports
# ------------------------------
FASTAPI_PORT=8000
STREAMLIT_PORT=8501

# ------------------------------
# Répertoire de travail Python
# ------------------------------
export PYTHONPATH=/app

# ------------------------------
# Vérifier que les secrets sont définis
# ------------------------------
if [ -z "$AZURE_STORAGE_CONNECTION_STRING" ]; then
  echo "❌ AZURE_STORAGE_CONNECTION_STRING n'est pas défini !"
  exit 1
fi

if [ -z "$MISTRAL_API_KEY" ]; then
  echo "⚠️ MISTRAL_API_KEY n'est pas défini. LLM désactivé."
fi

# ------------------------------
# Démarrage FastAPI
# ------------------------------
echo "🚀 Démarrage FastAPI sur le port $FASTAPI_PORT..."
uvicorn app.app_fastapi:app \
    --host 0.0.0.0 \
    --port $FASTAPI_PORT \
    --log-level info &

# ------------------------------
# Démarrage Streamlit
# ------------------------------
echo "🚀 Démarrage Streamlit sur le port $STREAMLIT_PORT..."
streamlit run app/app_streamlit.py \
    --server.port=$STREAMLIT_PORT \
    --server.address=0.0.0.0 \
    --logger.level=info
