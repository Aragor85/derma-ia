import streamlit as st
import requests
import pandas as pd

st.title("🧠 Mind Reading Recommender (Azure)")

# URL publique de ton Azure Function App
API_URL = "https://mind-reading-func.azurewebsites.net/api/recommend"

user_id = st.text_input("Entrez votre user_id :")

if st.button("Recommander"):
    try:
        resp = requests.post(API_URL, json={"user_id": user_id})
        if resp.status_code == 200:
            data = resp.json()
            st.success("✅ Recommandations reçues depuis Azure !")

            # === Content-Based ===
            st.subheader("📚 Recommandations Content-Based")
            df_content = pd.DataFrame(data["content_based"])
            df_content = df_content.reset_index().rename(columns={"index": "Column1"})
            st.dataframe(df_content[["Column1", "article_id", "similarity"]])

            # === Surprise (Collaborative) ===
            st.subheader("🤝 Recommandations Collaborative (Surprise)")
            df_surprise = pd.DataFrame(data["surprise"])
            df_surprise = df_surprise.reset_index().rename(columns={"index": "Column1"})
            st.dataframe(df_surprise[["Column1", "article_id", "pred_score"]])

        else:
            st.error(f"Erreur {resp.status_code}: {resp.text}")

    except Exception as e:
        st.error(f"❌ Impossible de contacter l’API Azure : {e}")
