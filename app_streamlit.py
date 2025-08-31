# app_streamlit.py
import streamlit as st
from PIL import Image
import requests
import base64
from io import BytesIO

st.set_page_config(page_title="Derma IA", layout="wide")

st.title("🩺 Derma IA - Diagnostic Dermatologique")

uploaded_file = st.file_uploader("Choisissez une image de lésion cutanée", type=["jpg","png","jpeg"])

endpoint_unet_cnn = st.text_input("API U-Net + CNN URL", value="http://localhost:8000/predict_unet_cnn")
endpoint_yolo = st.text_input("API YOLO URL", value="http://localhost:8000/predict_yolo")
endpoint_compare = st.text_input("API Comparatif URL", value="http://localhost:8000/compare_models")

def display_image_b64(b64_str):
    img = Image.open(BytesIO(base64.b64decode(b64_str)))
    st.image(img, use_column_width=True)

if uploaded_file:
    st.info("📤 Téléversement et analyse de l'image...")
    files = {"file": uploaded_file}

    with st.spinner("Analyse U-Net + CNN..."):
        resp = requests.post(endpoint_unet_cnn, files=files).json()
        if "error" not in resp:
            st.subheader("Segmentation + Classification (U-Net + CNN)")
            display_image_b64(resp["segmentation"])
            st.text(resp["rapport"])
        else:
            st.error(resp["error"])

    with st.spinner("Analyse YOLO + LLM..."):
        resp_yolo = requests.post(endpoint_yolo, files=files).json()
        if "error" not in resp_yolo:
            st.subheader("Détection YOLOv8")
            display_image_b64(resp_yolo["detection"])
            st.text(resp_yolo["rapport_yolo"])
        else:
            st.error(resp_yolo["error"])

    with st.spinner("Comparatif CNN/U-Net vs YOLO..."):
        resp_comp = requests.post(endpoint_compare, files=files).json()
        if "error" not in resp_comp:
            st.subheader("Comparatif des modèles")
            st.text(resp_comp["rapport_comparatif"])
        else:
            st.error(resp_comp["error"])
