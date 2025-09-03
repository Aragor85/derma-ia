#!/bin/bash
set -e

# Ports
FASTAPI_PORT=8000
STREAMLIT_PORT=8501

# Chemin du code
export PYTHONPATH=/app

echo "🚀 Démarrage FastAPI..."
uvicorn app.app_fastapi:app \
    --host 0.0.0.0 \
    --port $FASTAPI_PORT \
    --log-level info &

echo "🚀 Démarrage Streamlit..."
streamlit run app/app_streamlit.py \
    --server.port=$STREAMLIT_PORT \
    --server.address=0.0.0.0 \
    --logger.level=info
