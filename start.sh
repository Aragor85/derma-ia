#!/bin/bash
set -e

MODEL_DIR=/app/models
FASTAPI_PORT=8000
STREAMLIT_PORT=8501  # Streamlit interne, NGINX exposera le 8080

export PYTHONPATH=/app

# Lancer NGINX
echo "🚀 Démarrage NGINX..."
nginx -g 'daemon off;' &

# Lancer FastAPI
echo "🚀 Démarrage FastAPI..."
uvicorn app.app_fastapi:app --host 0.0.0.0 --port $FASTAPI_PORT --log-level info &

# Lancer Streamlit
echo "🚀 Démarrage Streamlit..."
streamlit run app/app_streamlit.py \
    --server.port=$STREAMLIT_PORT \
    --server.address=0.0.0.0 \
    --logger.level=info
