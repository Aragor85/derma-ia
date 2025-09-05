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

    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name
    file_type = uploaded_file.type

    # --- Récupérer les réponses séparément ---
    try:
        resp_cnn = post_file(endpoint_unet_cnn, file_name, file_bytes, file_type)
        resp_yolo = post_file(endpoint_yolo, file_name, file_bytes, file_type)
        resp_cmp = post_file(endpoint_compare, file_name, file_bytes, file_type)
    except Exception as e:
        st.error(f"Erreur lors de l'appel API : {e}")
        resp_cnn, resp_yolo, resp_cmp = None, None, None

    # --- Disposition forcée en 2 colonnes HTML (fixé même sur mobile) ---
    if resp_cnn and resp_yolo:
        cnn_img_html = ""
        yolo_img_html = ""

        if "segmentation" in resp_cnn:
            img_cnn = base64.b64decode(resp_cnn["segmentation"])
            cnn_img_html = f"<img src='data:image/png;base64,{resp_cnn['segmentation']}' style='max-width:100%; border-radius:10px;'>"

        if "detection" in resp_yolo:
            yolo_img_html = f"<img src='data:image/png;base64,{resp_yolo['detection']}' style='max-width:100%; border-radius:10px;'>"

        st.markdown(f"""
        <div style="display:flex; flex-direction:row; gap:20px; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;">
            
            <div style="flex:1; min-width:300px; background:#f9f9f9; padding:15px; border-radius:12px;">
                <h3>🧠 Segmentation + Classification (U-Net + CNN)</h3>
                {cnn_img_html}
                <pre style="white-space:pre-wrap; font-size:14px;">{resp_cnn.get('rapport','')}</pre>
            </div>

            <div style="flex:1; min-width:300px; background:#f9f9f9; padding:15px; border-radius:12px;">
                <h3>🎯 Détection YOLOv8</h3>
                {yolo_img_html}
                <pre style="white-space:pre-wrap; font-size:14px;">{resp_yolo.get('rapport_yolo','')}</pre>
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --- Comparatif en bas ---
    if resp_cmp:
        st.subheader("📊 Comparatif des modèles")
        st.markdown(f"""
        <pre style="white-space:pre-wrap; font-size:14px;">{resp_cmp.get('rapport_comparatif','')}</pre>
        """, unsafe_allow_html=True)

# --- Disclaimer ---
st.markdown(
    "<hr><p style='color:red; font-weight:bold;'>⚠️ Ce site est un test et ne fournit pas de diagnostic médical. "
    "Toute interprétation doit être validée par un professionnel de santé.</p>",
    unsafe_allow_html=True
)
