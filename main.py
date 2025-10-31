from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pickle
import os
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

# ---- Load precomputed embeddings ----
EMBEDDINGS_FILE = "movie_embeddings.pkl"

if not os.path.exists(EMBEDDINGS_FILE):
    raise FileNotFoundError(
        f"{EMBEDDINGS_FILE} not found! Run precompute_embeddings.py first."
    )

print(f"Loading precomputed embeddings from {EMBEDDINGS_FILE}...")
with open(EMBEDDINGS_FILE, "rb") as f:
    data = pickle.load(f)

X = data["X"]
titles = data["titles"]
overviews = data["overviews"]
print(f"✅ Loaded {len(titles)} movies with {X.shape[1]} features")


# ---- LinUCB Model ----
class LinUCB:
    def __init__(self, n_features, alpha=1.0):
        self.alpha = alpha
        self.A = np.eye(n_features)
        self.b = np.zeros((n_features, 1))
        self.A_inv = np.eye(n_features)  # Cache the inverse
        
    def predict(self, x):
        theta = self.A_inv @ self.b
        mean = float(theta.T @ x)
        uncertainty = float(self.alpha * np.sqrt(x.T @ self.A_inv @ x))
        return mean + uncertainty
    
    def update(self, x, reward):
        self.A += x @ x.T
        self.b += reward * x
        self.A_inv = np.linalg.inv(self.A)  # Only invert when A changes

bandit = LinUCB(n_features=X.shape[1], alpha=0.7)
seen = set()

# ---- API Models ----
class Feedback(BaseModel):
    movie_id: int
    reward: int

# ---- API Routes ----
@app.get("/next")
def get_next():
    print("🔵 /next endpoint called")  # DEBUG
    try:
        if len(seen) >= len(X):
            return {"message": "All movies seen"}

        print(f"📊 Computing scores for {len(X)} movies...")  # DEBUG
        scores = np.zeros(len(X))  # Pre-allocate array for speed
        
        for i in range(len(X)):
            if i % 100 == 0:  # Print progress every 100 movies
                print(f"  Progress: {i}/{len(X)} movies processed...")
            
            if i in seen:
                scores[i] = -np.inf
            else:
                x = X[i].reshape(-1, 1)
                try:
                    score = bandit.predict(x)
                    scores[i] = float(score)
                except Exception as e:
                    print(f"⚠️ Prediction error for movie {i}:", e)
                    scores[i] = 0.0

        print(f"✅ All {len(X)} scores computed, finding best...")  # DEBUG
        best_idx = int(np.argmax(scores))
        seen.add(best_idx)

        title = str(titles[best_idx])
        overview = str(overviews[best_idx])[:400] if len(overviews[best_idx]) > 400 else str(overviews[best_idx])

        print(f"🎬 Recommended: {title}")  # shows in backend log

        return {
            "id": best_idx,
            "title": title,
            "description": overview,
        }
    except Exception as e:
        print(f"❌ Error in get_next: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "message": "Error getting next movie"}

@app.post("/feedback")
def send_feedback(fb: Feedback):
    x = X[fb.movie_id].reshape(-1, 1)
    bandit.update(x, fb.reward)
    print(f"✅ Feedback received for {titles[fb.movie_id]} — reward {fb.reward}")
    return {"status": "updated", "movie_id": fb.movie_id, "reward": fb.reward}