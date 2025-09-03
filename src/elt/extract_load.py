import requests
import os
from dotenv import load_dotenv 
import pandas as pd
from model.movie_model import Movie
from model.credits_model import Credits
from model.genres_model import Genres
from model.keywords_model import Keywords
from tqdm import tqdm
import argparse
import logging
import pickle

logging.basicConfig(level=logging.INFO)

# Base URL for TMDB API
base_url = "https://api.themoviedb.org/3/movie/"

# Authentication
# Load API key from .env file
load_dotenv()
API = os.getenv("TMDB_API")
headers = {
  "accept": "application/json",
  "Authorization": f"Bearer {API}"
}



def fetch_popular_movies(base_url, headers, page=1):
  """Fetch popular movies from TMDB API and return list of Movie objects."""
  url = f"{base_url}popular?language=en-US&page={page}"
  try:
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
      raise Exception(f"Error {response.status_code}: {response.text}")
    data = response.json()
    movies = [Movie.from_api(m) for m in data.get('results', [])]
    return movies
  
  except requests.RequestException as e:
    logging.error(f"Failed to fetch popular movies for page {page}: {e}")
    return []



def fetch_credits(base_url, headers, movie_id):
  """Fetch corresponding credits info from TMDB API and return list of Credits objects.""" 
  url = f"{base_url}{movie_id}/credits?language=en-US"
  try:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      raise Exception(f"Error {response.status_code}: {response.text}")
    data = response.json()
    credits = Credits.from_api(data)
    return credits
  except requests.RequestException as e:
    logging.error(f"Error fetching credits for movie {movie_id}: {e}")
    return Credits(cast=[], crew=[])


def fetch_genres(base_url, headers, movie_id):
  """Fetch corresponding genres info from TMDB API and return list of Genres objects.""" 
  url = f"{base_url}{movie_id}"
  try:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      raise Exception(f"Error {response.status_code}: {response.text}")
    data = response.json()
    genres = Genres.from_api(data)
    return genres.genres
  except requests.RequestException as e:
    logging.error(f"Error fetching genres for movie {movie_id}: {e}")
    return Genres(genres=[])



def fetch_keywords(base_url, headers, movie_id):
  """Fetch corresponding keywords info from TMDB API and return list of Keywords objects.""" 
  url = f"{base_url}{movie_id}/keywords"
  try:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      raise Exception(f"Error {response.status_code}: {response.text}")
    data = response.json()
    keywords = Keywords.from_api(data)
    return keywords.keywords
  except requests.RequestException as e:
    logging.error(f"Error fetching keywords for movie {movie_id}: {e}")
    return Keywords(keywords=[])


def parse_args():
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser(description="Fetch and save movie data in batches.")
  parser.add_argument('--num_page', type=int, default = 25)
  parser.add_argument('--file_path', type=str, default = './data/fetched_sample_data.csv')
  parser.add_argument('--batch_size', type=int, default = 100)

  return parser.parse_args()
  


if __name__=='__main__':

  # Parse command-line arguments
  args = parse_args()

  file_path = args.file_path
  num_page = args.num_page
  batch_size = args.batch_size

  batch_rows = []


  # Fetch movies in batches
  for page in tqdm(range(1, num_page+1), desc="Fetching Pages"):

    movies = fetch_popular_movies(base_url, headers, page=page)
 
    for m in tqdm(movies, desc=f"Processing page {page}", leave=False):
      credits = fetch_credits(base_url, headers, m.id)
      genres = fetch_genres(base_url, headers, m.id)
      keywords = fetch_keywords(base_url, headers, m.id)
        
      row = {
              "movie_id": m.id,
              "title": m.title, 
              "overview": m.overview, 
              "genres": genres,
              "keywords": keywords,
              "cast": credits.cast,
              "crew": credits.crew         
          }
      batch_rows.append(row)
    
    # Batch Write 
    if len(batch_rows) % batch_size == 0 or page == num_page:

      # Convert batch to DataFrame
      df_batch = pd.DataFrame(batch_rows)
      
      # Append to CSV if file path exists else create it
      try:
        if os.path.exists(file_path):
          df_batch.to_csv(file_path, mode='a', header=False, index=False)
        
        else:
          df_batch.to_csv(file_path, mode='w', header=True, index=False)
      except Exception as e:
        logging.error(f"Failed to write batch to CSV: {e}")  
      
      # Clear buffer
      batch_rows = []
  
  logging.info("Successfully Movie Fetched Data")


