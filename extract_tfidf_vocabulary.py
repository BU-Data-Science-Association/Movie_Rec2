"""
Extract TF-IDF vocabulary by recreating the vectorizer on the overview text.
This will give us the actual keywords that map to the text embedding features.
"""
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import json

# Load the data
print("Loading embeddings and movie data...")
with open("movie_embeddings.pkl", "rb") as f:
    data = pickle.load(f)

df = pd.read_csv("movies_fin.csv")

# Get the overviews in the same order
overviews = data["overviews"]
print(f"Loaded {len(overviews)} movie overviews")

# Clean overviews - replace NaN with empty string
clean_overviews = []
for overview in overviews:
    if isinstance(overview, str):
        clean_overviews.append(overview)
    else:
        clean_overviews.append("")
print(f"Cleaned {len(clean_overviews)} overviews")

# Count non-text features
encoder = data.get("encoder")
num_categorical = len(encoder.get_feature_names_out()) if encoder else 0
num_numeric = 2  # rating, runtime
num_non_text = num_numeric + num_categorical

total_features = data["X"].shape[1]
num_text_features = total_features - num_non_text

print(f"Total features: {total_features}")
print(f"Numeric features: {num_numeric}")
print(f"Categorical features: {num_categorical}")
print(f"Text features (TF-IDF): {num_text_features}")

# Recreate TF-IDF vectorizer with the same number of features
print("\nRecreating TF-IDF vectorizer...")
vectorizer = TfidfVectorizer(
    max_features=num_text_features,
    stop_words='english',
    ngram_range=(1, 2),  # unigrams and bigrams
    min_df=2
)

# Fit on the overviews
try:
    vectorizer.fit(clean_overviews)
    
    # Get the vocabulary
    vocab = vectorizer.vocabulary_
    print(f"Vocabulary size: {len(vocab)}")
    
    # Create reverse mapping (index -> word)
    reverse_vocab = {int(idx): word for word, idx in vocab.items()}
    
    # Save the vocabulary
    vocab_file = "tfidf_vocabulary.json"
    with open(vocab_file, "w") as f:
        json.dump(reverse_vocab, f, indent=2)
    
    print(f"\nVocabulary saved to {vocab_file}")
    
    # Show some examples
    print("\nSample keywords:")
    for i in range(min(20, len(reverse_vocab))):
        print(f"  Index {i}: {reverse_vocab.get(i, 'N/A')}")
    
    print(f"\nKeyword at index 350 (Feature 1804): {reverse_vocab.get(349, 'N/A')}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
