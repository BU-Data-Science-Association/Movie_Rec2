#makes http requests to the Movie database api
import requests
#lets you write to a csv file
import csv
#use to pause between api calls so you dont break the rule
import time
#used to randomize the movie when calling the api
import random
#loads environment database where the api key is located
from dotenv import load_dotenv
#lets you access the .env
import os

#load key value pairs in .env to here
load_dotenv()
#reads the api key so the value attached to the api key variable in the .env
API_KEY = os.getenv("TMDB_API_KEY")

#configure the constants
#we want 1000 movies, at 20 per page so there shoudl be 50 pages that correspond to the api call
NUM_MOVIES = 1000
MOVIES_PER_PAGE = 20
NUM_PAGES = NUM_MOVIES // MOVIES_PER_PAGE
#the csv file that is created will be named movies.csv
CSV_FILE = "movies.csv"

#Fetch list of movies in the discover section of TMDB movie database
#gonna take a page as a input from this url and API key as parameters 
def fetch_discover_movies(page):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": page
    }s
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["results"]

#checks for nudity or any other Awkward situations so we dont have that in the presentation
#takes movie Id as input and then finds the keywords associated with that id
def contains_nudity_keywords(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords"
    params = {
        "api_key": API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    keywords = response.json().get("keywords", [])
    lower_keywords = [k["name"].lower() for k in keywords]
    #returns true if it fits any of the categories in the list
    return any(k in lower_keywords for k in ["nudity", "sexual content", "sex", "erotic", "explicit"])

#Gets the information for a movie using its id
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

#data storage container we are using Dictionary to get rid of any duplicates using jeys and values with the keys being the IDs
movie_dict = {}

for page in range(1, NUM_PAGES + 1):
    print(f"Fetching movie list from page {page}...")
    try:
        movies = fetch_discover_movies(page)
        for m in movies:
            movie_id = m["id"]
            #checks for duplicates 
            if movie_id not in movie_dict:
                try:
                    #skip movies that are flagged true for nudity from function above
                    if contains_nudity_keywords(movie_id):
                        print(f"Skipping {movie_id} due to nudity-related keywords.")
                        continue
                    #Fetch details from function above and store it in the movie dictionary using ID as key and the details as the values
                    details = fetch_movie_details(movie_id)
                    movie_dict[movie_id] = [
                        details["id"],
                        details["title"],
                        details.get("overview", "").replace("\n", " ").replace("\r", " "),
                        details.get("poster_path", "") or ""
                    ]
                    #giving the API a rest 
                    time.sleep(0.2)
                
                #excecption section here is for error handing and logs them without crashing
                except Exception as e:
                    print(f"Error fetching details for movie ID {movie_id}: {e}")
        time.sleep(0.25)
    except Exception as e:
        print(f"Error on page {page}: {e}")
        break


# Shuffle results
#convert the dictionary to a list of rows and randomize the order of those rows
movie_list = list(movie_dict.values())
random.shuffle(movie_list)

#write it to the CSV
print(f"Fetched {len(movie_list)} unique detailed movies. Saving to CSV...")

with open(CSV_FILE, "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["id", "title", "overview", "poster_path"])
    writer.writerows(movie_list)

print("CSV saved successfully.")
