from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

# ---- Setup ----
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Load & preprocess ----
df = pd.read_csv("movies_fin.csv")
text_col = "overview"
categorical_cols = ["genres", "production_companies", "production_countries"]  # adjust if needed
numeric_cols = ["rating",'runtime',]

model_embed = SentenceTransformer("all-MiniLM-L6-v2")
text_emb = model_embed.encode(df[text_col].fillna(""), show_progress_bar=True)

enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
cat_enc = enc.fit_transform(df[categorical_cols].fillna("unknown"))

scaler = StandardScaler()
num_scaled = scaler.fit_transform(df[numeric_cols].fillna(0))

X = np.hstack([text_emb, cat_enc, num_scaled])
titles = df["title"]

# ---- LinUCB Model ----
class LinUCB:
    def __init__(self, n_features, alpha=1.0):
        self.alpha = alpha
        self.A = np.eye(n_features)
        self.b = np.zeros((n_features, 1))
        
    def predict(self, x):
        A_inv = np.linalg.inv(self.A)
        theta = A_inv @ self.b
        mean = float(theta.T @ x)
        uncertainty = self.alpha * np.sqrt(x.T @ A_inv @ x)
        return mean + uncertainty
    
    def update(self, x, reward):
        self.A += x @ x.T
        self.b += reward * x

bandit = LinUCB(n_features=X.shape[1], alpha=0.7)
seen = set()

# ---- API Models ----
class Feedback(BaseModel):
    movie_id: int
    reward: int

# ---- API Routes ----
@app.get("/next")

def get_next():
    if len(seen) >= len(X):
        return {"message": "All movies seen"}

    scores = []
    for i in range(len(X)):
        if i in seen:
            scores.append(-np.inf)
        else:
            x = X[i].reshape(-1, 1)
            try:
                score = bandit.predict(x)
            except Exception as e:
                print("⚠️ Prediction error:", e)
                score = -np.inf
            scores.append(score)

    best_idx = int(np.argmax(scores))
    seen.add(best_idx)

    title = str(titles.iloc[best_idx])
    overview = str(df[text_col].iloc[best_idx])[:400]

    print(f"🎬 Recommended: {title}")  # shows in backend log

    return {
        "id": best_idx,
        "title": title,
        "description": overview,
    }

@app.post("/feedback")
def send_feedback(fb: Feedback):
    x = X[fb.movie_id].reshape(-1, 1)
    bandit.update(x, fb.reward)
    print(f"✅ Feedback received for {titles.iloc[fb.movie_id]} — reward {fb.reward}")
    return {"status": "updated", "movie_id": fb.movie_id, "reward": fb.reward}
