# app_streamlit.py
import streamlit as st
from PIL import Image
import requests
import base64
from io import BytesIO

st.set_page_config(page_title="Derma IA", layout="wide")

st.title("🩺 Derma IA - Diagnostic Dermatologique")

uploaded_file = st.file_uploader("Choisissez une image de lésion cutanée", type=["jpg", "png", "jpeg"])

# --- URLs fixes des API (non affichées à l'utilisateur) ---
endpoint_unet_cnn = "http://localhost:8000/predict_unet_cnn"
endpoint_yolo = "http://localhost:8000/predict_yolo"
endpoint_compare = "http://localhost:8000/compare_models"

def display_image_b64(b64_str):
    """Affiche une image encodée en base64 dans Streamlit"""
    img = Image.open(BytesIO(base64.b64decode(b64_str)))
    st.image(img, use_column_width=True)

def post_file(url, name, bytes_content, content_type):
    """Envoie le fichier au format multipart/form-data et retourne la réponse JSON"""
    files = {"file": (name, bytes_content, content_type)}
    resp = requests.post(url, files=files)
    return resp.json()

if uploaded_file:
    st.info("📤 Téléversement et analyse de l'image...")

    # Lire le contenu du fichier une seule fois
    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name
    file_type = uploaded_file.type

    endpoints = [
        ("Segmentation + Classification (U-Net + CNN)", endpoint_unet_cnn, "segmentation", "rapport"),
        ("Détection YOLOv8", endpoint_yolo, "detection", "rapport_yolo"),
        ("Comparatif des modèles", endpoint_compare, None, "rapport_comparatif")
    ]

    for title, url, img_key, report_key in endpoints:
        with st.spinner(f"Analyse {title}..."):
            try:
                resp = post_file(url, file_name, file_bytes, file_type)
                if "error" not in resp:
                    st.subheader(title)
                    if img_key:
                        display_image_b64(resp[img_key])
                    st.text(resp[report_key])
                else:
                    st.error(resp["error"])
            except Exception as e:
                st.error(f"Erreur {title} : {e}")

# --- Disclaimer ---
st.markdown(
    "<hr><p style='color:red; font-weight:bold;'>⚠️ Ce site est un test et ne fournit pas de diagnostic médical. "
    "Toute interprétation doit être validée par un professionnel de santé.</p>",
    unsafe_allow_html=True
)
