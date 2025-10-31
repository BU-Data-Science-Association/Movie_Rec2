# =====================================
# INTERACTIVE LINUCB MOVIE RECOMMENDER
# =====================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sentence_transformers import SentenceTransformer

# ---- Load and preprocess ----
df = pd.read_csv("movies_fin.csv")

text_col = "overview"
categorical_cols = ["genres", "production_companies", "production_countries"]  # adjust if needed
numeric_cols = ["rating",'runtime',]

# Sentence embeddings
embedder = SentenceTransformer("all-MiniLM-L6-v2")
text_emb = embedder.encode(df[text_col].fillna(""), show_progress_bar=True)

# One-hot encode categoricals
enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
cat_enc = enc.fit_transform(df[categorical_cols].fillna("unknown"))

# Scale numerics
scaler = StandardScaler()
num_scaled = scaler.fit_transform(df[numeric_cols].fillna(0))

# Final contextual vectors
X = np.hstack([text_emb, cat_enc, num_scaled])
movie_titles = df["title"] if "title" in df.columns else df.index
print("Final feature matrix shape:", X.shape)

# ---- LinUCB implementation ----
class LinUCB:
    def __init__(self, n_features, alpha=1.0):
        self.alpha = alpha
        self.A = np.eye(n_features)
        self.b = np.zeros((n_features, 1))
        
    def predict(self, x):
        A_inv = np.linalg.inv(self.A)
        theta = A_inv @ self.b
        mean = float((theta.T @ x).item())
        uncertainty = self.alpha * np.sqrt(x.T @ A_inv @ x)
        return mean + uncertainty
    
    def update(self, x, reward):
        self.A += x @ x.T
        self.b += reward * x

# ---- Interactive loop ----
bandit = LinUCB(n_features=X.shape[1], alpha=0.6)
seen = set()

print("\n🎥 Interactive LinUCB Recommender Ready!")
print("Type 'quit' to stop.\n")

while True:
    # Pick top un-seen movie by UCB
    scores = []
    for i in range(len(X)):
        if i in seen:  # skip already rated
            scores.append(-np.inf)
        else:
            x = X[i].reshape(-1, 1)
            scores.append(bandit.predict(x))
    
    best_idx = int(np.argmax(scores))
    seen.add(best_idx)

    # Show recommendation
    title = movie_titles.iloc[best_idx] if isinstance(movie_titles, pd.Series) else best_idx
    print(f"🎬 Recommended Movie: {title}")
    print(f"Description: {df[text_col].iloc[best_idx][:200]}...")
    
    # User feedback
    feedback = input("Did you like this movie? (1 = 👍, 0 = 👎, or 'quit'): ").strip()
    if feedback.lower() == "quit":
        break

    if feedback in ["0", "1"]:
        reward = int(feedback)
        x = X[best_idx].reshape(-1, 1)
        bandit.update(x, reward)
        print(f"✅ Updated model with reward={reward}\n")
    else:
        print("⚠️ Invalid input. Please type 1, 0, or quit.\n")

print("\nSession ended. Model trained on", len(seen), "movies.")
