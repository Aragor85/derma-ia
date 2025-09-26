import pickle
import numpy as np

# Charger les modèles (à remplacer par Azure Blob Storage input binding)
with open("data/surprise_svd_model.pkl", "rb") as f:
    surprise_model = pickle.load(f)

# Exemple embeddings articles
article_embeddings = {
    1: np.random.rand(50).tolist(),
    2: np.random.rand(50).tolist(),
    3: np.random.rand(50).tolist(),
    4: np.random.rand(50).tolist(),
    5: np.random.rand(50).tolist(),
    6: np.random.rand(50).tolist()
}

def recommend_surprise(user_id, top_n=5):
    all_items = list(article_embeddings.keys())
    preds = [(iid, surprise_model.predict(user_id, iid).est) for iid in all_items]
    preds_sorted = sorted(preds, key=lambda x: x[1], reverse=True)[:top_n]
    return [{"article_id": aid, "score": round(score, 3)} for aid, score in preds_sorted]

def recommend_content_based(user_id, top_n=5):
    # Profil utilisateur simulé
    user_vector = np.mean(list(article_embeddings.values()), axis=0)
    sims = []
    for aid, emb in article_embeddings.items():
        sim = np.dot(user_vector, emb) / (np.linalg.norm(user_vector) * np.linalg.norm(emb))
        sims.append((aid, sim))
    sims_sorted = sorted(sims, key=lambda x: x[1], reverse=True)[:top_n]
    return [{"article_id": aid, "similarity": round(sim, 3)} for aid, sim in sims_sorted]
