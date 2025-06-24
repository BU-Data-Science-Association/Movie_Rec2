import requests
import csv
import time
import random
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
print(f"Loaded API_KEY: {API_KEY}")
NUM_MOVIES = 1000
MOVIES_PER_PAGE = 20
NUM_PAGES = NUM_MOVIES // MOVIES_PER_PAGE
CSV_FILE = "movies.csv"

def fetch_discover_movies(page):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": page
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["results"]
def contains_nudity_keywords(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords"
    params = {
        "api_key": API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    keywords = response.json().get("keywords", [])
    lower_keywords = [k["name"].lower() for k in keywords]
    return any(k in lower_keywords for k in ["nudity", "sexual content", "sex", "erotic", "explicit"])

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

movie_dict = {}

for page in range(1, NUM_PAGES + 1):
    print(f"Fetching movie list from page {page}...")
    try:
        movies = fetch_discover_movies(page)
        for m in movies:
            movie_id = m["id"]
            if movie_id not in movie_dict:
                try:
                    if contains_nudity_keywords(movie_id):
                        print(f"Skipping {movie_id} due to nudity-related keywords.")
                        continue

                    details = fetch_movie_details(movie_id)
                    movie_dict[movie_id] = [
                        details["id"],
                        details["title"],
                        details.get("overview", "").replace("\n", " ").replace("\r", " "),
                        details.get("poster_path", "") or ""
                    ]
                    time.sleep(0.2)
                except Exception as e:
                    print(f"Error fetching details for movie ID {movie_id}: {e}")
        time.sleep(0.25)
    except Exception as e:
        print(f"Error on page {page}: {e}")
        break


# Shuffle results
movie_list = list(movie_dict.values())
random.shuffle(movie_list)

print(f"Fetched {len(movie_list)} unique detailed movies. Saving to CSV...")

with open(CSV_FILE, "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["id", "title", "overview", "poster_path"])
    writer.writerows(movie_list)

print("CSV saved successfully.")
