from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pickle
import os
import pandas as pd
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
print(f"Loaded {len(titles)} movies with {X.shape[1]} features")

# Load poster paths from CSV
print("Loading poster paths from CSV...")
df = pd.read_csv("movies_fin.csv")
poster_paths = df["poster_path"].values
print(f"Loaded {len(poster_paths)} poster paths")


# ---- LinUCB Model ----
class LinUCB:
    def __init__(self, n_features, alpha=1.0):
        self.alpha = alpha
        self.n_features = n_features
        self.X_history = []
        self.y_history = []
        self._theta = None
        self._A_inv = None
        self._needs_update = True
        
    def _compute_params(self):
        """Compute and cache theta and A_inv"""
        if not self._needs_update:
            return
            
        if not self.X_history:
            self._theta = np.zeros(self.n_features)
            self._A_inv = np.eye(self.n_features)
        else:
            X_mat = np.array(self.X_history)  # (n_samples, n_features)
            y_vec = np.array(self.y_history)  # (n_samples,)
            A = X_mat.T @ X_mat + np.eye(self.n_features)
            self._A_inv = np.linalg.inv(A)
            self._theta = self._A_inv @ (X_mat.T @ y_vec)  # theta is (n_features,)
        
        self._needs_update = False
        
    def predict(self, x):
        """Predict UCB score for a single feature vector"""
        self._compute_params()
        
        x_flat = x.flatten()  # (n_features,)
        mean = self._theta.T @ x_flat
        uncertainty = self.alpha * np.sqrt(x_flat.T @ self._A_inv @ x_flat)
        return mean + uncertainty
    
    def update(self, x, reward):
        self.X_history.append(x.flatten())
        self.y_history.append(reward)
        self._needs_update = True

bandit = LinUCB(n_features=X.shape[1], alpha=2)
seen = set()

# ---- API Models ----
class Feedback(BaseModel):
    movie_id: int
    reward: int

# ---- API Routes ----
@app.get("/next")
def get_next():
    print("/next endpoint called")  # DEBUG
    try:
        if len(seen) >= len(X):
            return {"message": "All movies seen"}

        print(f"Computing scores for {len(X)} movies using bandit.predict...")  # DEBUG
        scores = np.zeros(len(X))  # Pre-allocate array for speed
        for i in range(len(X)):
            if i % 100 == 0:  # Print progress every 100 movies
                print(f"  Progress: {i}/{len(X)} movies processed...")
            if i in seen:
                scores[i] = -np.inf
            else:
                x = X[i].reshape(-1, 1)  # (n_features, 1)
                score = bandit.predict(x)
                scores[i] = float(score)

        print(f"All {len(X)} scores computed, finding best...")  # DEBUG
        best_idx = int(np.argmax(scores))
        seen.add(best_idx)

        title = str(titles[best_idx])
        overview_raw = overviews[best_idx]
        if isinstance(overview_raw, str) and not pd.isna(overview_raw):
            overview = overview_raw[:400] if len(overview_raw) > 400 else overview_raw
        else:
            overview = ""
        poster_path_raw = poster_paths[best_idx] if best_idx < len(poster_paths) else None
        poster_path = str(poster_path_raw) if poster_path_raw is not None and not pd.isna(poster_path_raw) else None

        print(f"Recommended: {title}")  # shows in backend log

        return {
            "id": best_idx,
            "title": title,
            "description": overview,
            "poster_path": poster_path,
        }
    except Exception as e:
        print(f"Error in get_next: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "message": "Error getting next movie"}

@app.post("/feedback")
def send_feedback(fb: Feedback):
    x = X[fb.movie_id].reshape(-1, 1)
    bandit.update(x, fb.reward)
    print(f"Feedback received for {titles[fb.movie_id]} - reward {fb.reward}")
    return {"status": "updated", "movie_id": fb.movie_id, "reward": fb.reward}