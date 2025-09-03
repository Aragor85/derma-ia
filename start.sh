#!/bin/bash
set -e

# Définir les ports
FASTAPI_PORT=8000
STREAMLIT_PORT=8501

# Définir le PYTHONPATH pour que les imports fonctionnent
export PYTHONPATH=/app

echo "🚀 Démarrage FastAPI..."
# Lancer FastAPI en arrière-plan
uvicorn app.app_fastapi:app --host 0.0.0.0 --port $FASTAPI_PORT --log-level info &

echo "🚀 Démarrage Streamlit..."
# Lancer Streamlit au premier plan
streamlit run app/app_streamlit.py \
    --server.port=$STREAMLIT_PORT \
    --server.address=0.0.0.0 \
    --logger.level=info
