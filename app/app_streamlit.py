import streamlit as st
from PIL import Image
import requests
import base64
from io import BytesIO

st.set_page_config(page_title="Derma IA", layout="wide")

st.title("🩺 Derma IA - Diagnostic Dermatologique")

uploaded_file = st.file_uploader(
    "Choisissez une image de lésion cutanée", 
    type=["jpg", "png", "jpeg"]
)

# --- URLs fixes des API ---
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

    # Créer deux colonnes pour afficher CNN et YOLO côte à côte
    col1, col2 = st.columns(2)

    # --- CNN + U-Net ---
    with col1:
        with st.spinner("Analyse U-Net + CNN..."):
            try:
                resp_cnn = post_file(endpoint_unet_cnn, file_name, file_bytes, file_type)
                if "error" not in resp_cnn:
                    st.subheader("Segmentation + Classification (U-Net + CNN)")
                    display_image_b64(resp_cnn["segmentation"])
                    st.text(resp_cnn["rapport"])
                else:
                    st.error(resp_cnn["error"])
            except Exception as e:
                st.error(f"Erreur U-Net + CNN : {e}")

    # --- YOLO ---
    with col2:
        with st.spinner("Analyse YOLOv8..."):
            try:
                resp_yolo = post_file(endpoint_yolo, file_name, file_bytes, file_type)
                if "error" not in resp_yolo:
                    st.subheader("Détection YOLOv8")
                    display_image_b64(resp_yolo["detection"])
                    st.text(resp_yolo["rapport_yolo"])
                else:
                    st.error(resp_yolo["error"])
            except Exception as e:
                st.error(f"Erreur YOLO : {e}")

    # --- Comparatif en bas ---
    st.markdown("---")
    with st.spinner("Comparatif CNN/U-Net vs YOLO..."):
        try:
            resp_comp = post_file(endpoint_compare, file_name, file_bytes, file_type)
            if "error" not in resp_comp:
                st.subheader("📊 Comparatif des modèles")
                st.text(resp_comp["rapport_comparatif"])
            else:
                st.error(resp_comp["error"])
        except Exception as e:
            st.error(f"Erreur Comparatif : {e}")

# --- Disclaimer ---
st.markdown(
    "<hr><p style='color:red; font-weight:bold;'>⚠️ Ce site est un test et ne fournit pas de diagnostic médical. "
    "Toute interprétation doit être validée par un professionnel de santé.</p>",
    unsafe_allow_html=True
)
