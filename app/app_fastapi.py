# app_fastapi.py
import os
from io import BytesIO
import base64
import logging
import traceback
import numpy as np
from PIL import Image, ImageDraw
import requests

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

import tensorflow as tf
from ultralytics import YOLO
from app import utils
from app import config


# ----------------- APP & LOG -----------------
app = FastAPI(title="Derma IA - FastAPI")
logging.basicConfig(level=logging.INFO)

# ----------------- CONFIG -----------------
MISTRAL_API_KEY = config.MISTRAL_API_KEY
MISTRAL_CHAT_URL = "https://api.mistral.ai/v1/chat/completions"
HEADERS_MISTRAL = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

# Labels ISIC
LABELS = ["MEL","NV","BCC","AKIEC","BKL","DF","VASC"]
TYPE2FULL = {
    "MEL": "Mélanome",
    "NV": "Nævus bénin",
    "BCC": "Carcinome basocellulaire",
    "AKIEC": "Kératose actinique / CE",
    "BKL": "Lésion kératosique bénigne",
    "DF": "Dermatofibrome",
    "VASC": "Lésion vasculaire",
}

# ----------------- LOAD MODELS -----------------
UNET_PATH = utils.download_blob_model("unet", "models/unet_model.h5")
CNN_PATH  = utils.download_blob_model("cnn", "models/cnn_model.h5")
YOLO_PATH = utils.download_blob_model("yolo", "models/yolov8_model.pt")

def safe_load_unet(path):
    try:
        return tf.keras.models.load_model(path, compile=False)
    except Exception as e:
        logging.error(f"Impossible de charger U-Net: {e}")
        return None

def safe_load_cnn(path):
    try:
        return tf.keras.models.load_model(path, compile=False)
    except Exception as e:
        logging.error(f"Impossible de charger CNN: {e}")
        return None

def safe_load_yolo(path):
    try:
        return YOLO(path)
    except Exception as e:
        logging.error(f"Impossible de charger YOLO: {e}")
        return None

model_unet = safe_load_unet(UNET_PATH)
model_cnn = safe_load_cnn(CNN_PATH)
model_yolo = safe_load_yolo(YOLO_PATH)

# ----------------- UTILS -----------------
def image_to_base64_pil(img_pil: Image.Image) -> str:
    buf = BytesIO()
    img_pil.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def call_mistral_chat(system_prompt: str, user_prompt: str, max_tokens: int = 1200, temperature: float = 0.2) -> str:
    if not MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY manquante ou invalide.")
    payload = {
        "model": "mistral-small",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    resp = requests.post(MISTRAL_CHAT_URL, headers=HEADERS_MISTRAL, json=payload, timeout=45)
    try:
        resp.raise_for_status()
    except Exception as e:
        return f"(Erreur API Mistral: {e}; status={resp.status_code}; body={resp.text})"
    data = resp.json()
    if "choices" in data and data["choices"]:
        return data["choices"][0].get("message", {}).get("content", "").strip()
    if "output" in data and data["output"]:
        return data["output"][0].get("content", "").strip()
    return "(Réponse Mistral vide)"

# ----------------- ENDPOINT: U-Net + CNN -----------------
@app.post("/predict_unet_cnn")
async def predict_unet_cnn(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(BytesIO(contents)).convert("RGB")
        img_resized = img.resize((256, 256))

        if model_unet is None or model_cnn is None:
            return JSONResponse(status_code=500, content={"error": "Modèles U-Net/CNN non chargés."})

        x = np.expand_dims(np.array(img_resized, dtype=np.float32)/255.0, axis=0)
        pred = model_unet.predict(x)
        mask = (pred[0, :, :, 0] > 0.5).astype(np.uint8)

        mask_img = Image.fromarray((mask*255).astype(np.uint8)).convert("L")
        red_mask = Image.new("RGBA", img_resized.size, color=(255, 0, 0, 100))
        overlay = img_resized.convert("RGBA")
        overlay.paste(red_mask, (0, 0), mask_img)

        arr = np.array(img_resized)
        arr_masked = arr * np.expand_dims(mask, axis=-1)
        arr_masked = arr_masked.astype(np.uint8)

        probs = model_cnn.predict(np.expand_dims(arr_masked/255.0, 0), verbose=0)[0]
        idx = int(np.argmax(probs))
        conf = float(probs[idx])
        short_label = LABELS[idx]
        full_label = TYPE2FULL.get(short_label, short_label)

        report_lines = [
            "🩺 ===== COMPTE RENDU AUTOMATIQUE (U-Net + CNN) =====",
            f"🏷️ Type probable : {full_label} [{short_label}]",
            f"📊 Confiance : {conf*100:.1f}%",
            "⚠️ Recommandation : évaluation dermatologique clinique conseillée.",
            "------------------------------------",
            "📈 Distribution complète :"
        ]
        for i, lbl in enumerate(LABELS):
            report_lines.append(f"• {lbl} ({TYPE2FULL.get(lbl,lbl)}): {probs[i]*100:.2f}%")
        report_text = "\n".join(report_lines)

        seg_b64 = image_to_base64_pil(overlay)
        return {
            "segmentation": seg_b64,
            "rapport": report_text,
            "label": short_label,
            "confidence": conf,
            "probs": [float(p) for p in probs]
        }
    except Exception as e:
        logging.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})

# ----------------- ENDPOINT: YOLO + LLM -----------------
@app.post("/predict_yolo")
async def predict_yolo(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(BytesIO(contents)).convert("RGB")
        draw = ImageDraw.Draw(img)

        if model_yolo is None:
            return JSONResponse(status_code=500, content={"error": "YOLO non chargé."})

        results = model_yolo.predict(np.array(img))
        detections = []
        yolo_labels = []

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = model_yolo.names.get(cls_id, str(cls_id))
                detections.append({"class_id": cls_id, "label": label, "confidence": conf,
                                   "xyxy": [float(x1), float(y1), float(x2), float(y2)]})
                yolo_labels.append(label)

                cx, cy = int((x1+x2)/2), int((y1+y2)/2)
                radius = int(min((x2-x1),(y2-y1))/2)
                draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], outline="red", width=3)
                draw.text((cx, cy-radius-10), f"{label}:{conf:.2f}", fill="red")

        det_b64 = image_to_base64_pil(img)

        system_prompt = "Tu es un dermatologue. Interprète uniquement les résultats YOLOv8 ci-dessous et rédige un compte rendu concis en français."
        details = "\n".join([f"- {d['label']} confiance {d['confidence']*100:.1f}%" for d in detections]) or "Aucune lésion détectée."
        rapport_yolo = call_mistral_chat(system_prompt, f"Résultats YOLOv8:\n{details}\nNe dépasse pas 1000 tokens.", max_tokens=1200)

        return {"detection": det_b64, "detections": detections, "rapport_yolo": rapport_yolo}

    except Exception as e:
        logging.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})

# ----------------- ENDPOINT: Comparatif -----------------
@app.post("/compare_models")
async def compare_models(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(BytesIO(contents)).convert("RGB")

        if model_unet is None or model_cnn is None or model_yolo is None:
            return JSONResponse(status_code=500, content={"error": "Modèles non chargés."})

        img_resized = img.resize((256, 256))
        x = np.expand_dims(np.array(img_resized, dtype=np.float32)/255.0, axis=0)
        pred = model_unet.predict(x)
        mask = (pred[0, :, :, 0] > 0.5).astype(np.uint8)
        arr = np.array(img_resized)
        arr_masked = arr * np.expand_dims(mask, axis=-1)
        probs = model_cnn.predict(np.expand_dims(arr_masked/255.0, 0), verbose=0)[0]
        idx = int(np.argmax(probs))
        cnn_label = LABELS[idx]
        cnn_conf = float(probs[idx])

        results = model_yolo.predict(np.array(img))
        yolo_labels = [model_yolo.names[int(box.cls[0])] for r in results for box in r.boxes]
        yolo_dets = yolo_labels or ["Aucune lésion détectée"]

        system_prompt = (
            "Tu es un dermatologue. Compare les résultats CNN+U-Net et YOLOv8.\n"
            "- Fournis un tableau comparatif clair.\n"
            "- Conclus par des recommandations prudentes."
        )

        dist_str = "\n".join([f"• {lbl}: {probs[i]*100:.2f}%" for i, lbl in enumerate(LABELS)])
        yolo_str = ", ".join(yolo_labels) if yolo_labels else "Aucune lésion détectée"

        user_prompt = f"Résultats CNN+U-Net : {cnn_label} ({cnn_conf*100:.1f}%)\nDistribution :\n{dist_str}\nRésultats YOLOv8 : {yolo_str}\nRédige en français, clair et concis."

        rapport_comparatif = call_mistral_chat(system_prompt, user_prompt, max_tokens=1500, temperature=0.2)

        return {"cnn_label": cnn_label, "cnn_confidence": cnn_conf, "cnn_probs": [float(p) for p in probs],
                "yolo_labels": yolo_dets, "rapport_comparatif": rapport_comparatif}

    except Exception as e:
        logging.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})
