from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pickle
import os
import pandas as pd
import json
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

# Create feature name mapping
feature_names = []
current_idx = 0

# Numeric features first
feature_names.append("Rating")
feature_names.append("Runtime")
current_idx = 2

# Categorical features (one-hot encoded)
encoder = data.get("encoder")
if encoder:
    # Get category names from the encoder
    for cat_idx, category in enumerate(["genres", "production_companies", "production_countries"]):
        if hasattr(encoder, 'categories_'):
            for value in encoder.categories_[cat_idx]:
                feature_names.append(f"{category.replace('_', ' ').title()}: {value}")
        current_idx += 1

# Remaining features are text embeddings (overview TF-IDF)
while len(feature_names) < X.shape[1]:
    feature_names.append(f"Overview Keyword {len(feature_names) - current_idx + 1}")

print(f"Created {len(feature_names)} feature names")

# Load poster paths from CSV
print("Loading poster paths from CSV...")
df = pd.read_csv("movies_fin.csv")
poster_paths = df["poster_path"].values
print(f"Loaded {len(poster_paths)} poster paths")

# Create feature name mapping
print("Creating feature name mapping...")
feature_names = []
current_idx = 0

# Numeric features (from scaler)
scaler = data.get("scaler")
if scaler and hasattr(scaler, 'feature_names_in_'):
    numeric_features = list(scaler.feature_names_in_)
    for feat in numeric_features:
        feature_names.append(feat.capitalize())
    current_idx = len(numeric_features)
    print(f"Added {len(numeric_features)} numeric features")

# Categorical features (from encoder)
encoder = data.get("encoder")
if encoder and hasattr(encoder, 'get_feature_names_out'):
    cat_features = encoder.get_feature_names_out()
    for feat in cat_features:
        # Clean up: "genres_Action" -> "Genre: Action"
        if '_' in str(feat):
            category, value = str(feat).split('_', 1)
            category = category.replace('_', ' ').title()
            feature_names.append(f"{category}: {value}")
        else:
            feature_names.append(str(feat))
    print(f"Added {len(cat_features)} categorical features")
    current_idx += len(cat_features)

# Remaining features are text embeddings (overview TF-IDF)
remaining = X.shape[1] - current_idx
text_feature_start = current_idx

# Try to load TF-IDF vocabulary if available
tfidf_vocab = {}
vocab_file = "tfidf_vocabulary.json"
if os.path.exists(vocab_file):
    print(f"Loading TF-IDF vocabulary from {vocab_file}...")
    with open(vocab_file, "r") as f:
        tfidf_vocab = json.load(f)
    print(f"Loaded {len(tfidf_vocab)} TF-IDF keywords")

for i in range(remaining):
    # Use actual keyword if available, otherwise generic label
    keyword = tfidf_vocab.get(str(i), f"Embedding {i+1}")
    feature_names.append(f"Keyword: {keyword}")

print(f"Created {len(feature_names)} feature names")


# ---- LinUCB Model ----
class LinUCB:
    def __init__(self, n_features, alpha=1.0):
        self.alpha = alpha
        self.n_features = n_features
        self.X_history = []
        self.y_history = []
        
    def predict(self, x):
        if not self.X_history:
            return 0.0
        
        X_mat = np.array(self.X_history)  # (n_samples, n_features)
        y_vec = np.array(self.y_history)  # (n_samples,)
        A = X_mat.T @ X_mat + np.eye(self.n_features)
        A_inv = np.linalg.inv(A)
        theta = A_inv @ (X_mat.T @ y_vec)  # theta is (n_features,)
        
        x_flat = x.flatten()  # (n_features,)
        mean = theta.T @ x_flat
        uncertainty = self.alpha * np.sqrt(x_flat.T @ A_inv @ x_flat)
        return mean + uncertainty
    
    def update(self, x, reward):
        self.X_history.append(x.flatten())
        self.y_history.append(reward)

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

        # Precompute theta and A_inv once for all predictions
        if bandit.X_history:
            X_mat = np.array(bandit.X_history)  # (n_samples, n_features)
            y_vec = np.array(bandit.y_history)  # (n_samples,)
            A = X_mat.T @ X_mat + np.eye(bandit.n_features)
            A_inv = np.linalg.inv(A)
            theta = A_inv @ (X_mat.T @ y_vec)  # theta is (n_features,)
        else:
            theta = np.zeros(bandit.n_features)
            A_inv = np.eye(bandit.n_features)

        print(f"Computing scores for {len(X)} movies...")  # DEBUG
        scores = np.zeros(len(X))  # Pre-allocate array for speed
        for i in range(len(X)):
            if i % 100 == 0:  # Print progress every 100 movies
                print(f"  Progress: {i}/{len(X)} movies processed...")
            if i in seen:
                scores[i] = -np.inf
            else:
                x = X[i].reshape(-1, 1)  # (n_features, 1)
                x_flat = x.flatten()  # (n_features,)
                mean = theta.T @ x_flat
                uncertainty = bandit.alpha * np.sqrt(x_flat.T @ A_inv @ x_flat)
                score = mean + uncertainty
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

@app.get("/analytics")
def get_analytics():
    """Return current state of the bandit algorithm for visualization"""
    try:
        # Calculate current theta (learned weights)
        if bandit.X_history:
            X_mat = np.array(bandit.X_history)
            y_vec = np.array(bandit.y_history)
            A = X_mat.T @ X_mat + np.eye(bandit.n_features)
            A_inv = np.linalg.inv(A)
            theta = A_inv @ (X_mat.T @ y_vec)
            
            # Get top features by absolute weight
            top_indices = np.argsort(np.abs(theta))[-10:][::-1]
            top_weights = [
                {
                    "feature_index": int(idx), 
                    "feature_name": feature_names[idx] if idx < len(feature_names) else f"Feature {idx}",
                    "weight": float(theta[idx])
                }
                for idx in top_indices
            ]
            
            # Calculate confidence (inverse of average uncertainty)
            avg_uncertainty = np.mean(np.diag(A_inv))
            confidence = 1.0 / (1.0 + avg_uncertainty)  # Scale between 0-1
        else:
            top_weights = []
            confidence = 0.0
        
        # Calculate stats
        total_interactions = len(bandit.y_history)
        avg_reward = float(np.mean(bandit.y_history)) if bandit.y_history else 0.0
        
        return {
            "top_weights": top_weights,
            "confidence": confidence,
            "stats": {
                "total_interactions": total_interactions,
                "average_reward": avg_reward,
                "movies_rated": total_interactions,
                "movies_remaining": len(X) - len(seen)
            }
        }
    except Exception as e:
        print(f"Error in analytics: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/features/{feature_index}")
def get_feature(feature_index: int):
    """Get information about a specific feature"""
    try:
        if feature_index < 0 or feature_index >= len(feature_names):
            return {"error": f"Feature index {feature_index} out of range (0-{len(feature_names)-1})"}
        
        feature_name = feature_names[feature_index]
        
        # Get current weight if model has been trained
        current_weight = None
        if bandit.X_history:
            X_mat = np.array(bandit.X_history)
            y_vec = np.array(bandit.y_history)
            A = X_mat.T @ X_mat + np.eye(bandit.n_features)
            A_inv = np.linalg.inv(A)
            theta = A_inv @ (X_mat.T @ y_vec)
            current_weight = float(theta[feature_index])
        
        return {
            "feature_index": feature_index,
            "feature_name": feature_name,
            "current_weight": current_weight,
            "is_numeric": feature_index < 2,
            "is_categorical": 2 <= feature_index < 1455,
            "is_text_embedding": feature_index >= 1455
        }
    except Exception as e:
        print(f"Error getting feature: {e}")
        return {"error": str(e)}

@app.get("/features")
def search_features(q: str = "", limit: int = 20):
    """Search features by name"""
    try:
        if not q:
            # Return first N features
            results = [
                {"index": i, "name": feature_names[i]}
                for i in range(min(limit, len(feature_names)))
            ]
        else:
            # Search for matching features
            q_lower = q.lower()
            results = [
                {"index": i, "name": name}
                for i, name in enumerate(feature_names)
                if q_lower in name.lower()
            ][:limit]
        
        return {
            "total_features": len(feature_names),
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        print(f"Error searching features: {e}")
        return {"error": str(e)}

@app.post("/feedback")
def send_feedback(fb: Feedback):
    """Update bandit with user feedback and return what changed"""
    try:
        # Calculate theta BEFORE update
        if bandit.X_history:
            X_mat = np.array(bandit.X_history)
            y_vec = np.array(bandit.y_history)
            A = X_mat.T @ X_mat + np.eye(bandit.n_features)
            A_inv = np.linalg.inv(A)
            theta_before = A_inv @ (X_mat.T @ y_vec)
        else:
            theta_before = np.zeros(bandit.n_features)
        
        # Update the bandit
        x = X[fb.movie_id].reshape(-1, 1)
        bandit.update(x, fb.reward)
        
        # Calculate theta AFTER update
        X_mat = np.array(bandit.X_history)
        y_vec = np.array(bandit.y_history)
        A = X_mat.T @ X_mat + np.eye(bandit.n_features)
        A_inv = np.linalg.inv(A)
        theta_after = A_inv @ (X_mat.T @ y_vec)
        
        # Find top changes
        deltas = theta_after - theta_before
        top_change_indices = np.argsort(np.abs(deltas))[-5:][::-1]
        
        changes = [
            {
                "feature_index": int(idx),
                "feature_name": feature_names[idx] if idx < len(feature_names) else f"Feature {idx}",
                "before": float(theta_before[idx]),
                "after": float(theta_after[idx]),
                "change": float(deltas[idx])
            }
            for idx in top_change_indices
        ]
        
        print(f"Feedback received for {titles[fb.movie_id]} - reward {fb.reward}")
        
        return {
            "status": "updated",
            "movie_id": fb.movie_id,
            "reward": fb.reward,
            "changes": changes
        }
    except Exception as e:
        print(f"Error in feedback: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}