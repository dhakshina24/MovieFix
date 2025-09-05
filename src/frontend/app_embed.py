import streamlit as st
import pickle
import pandas as pd
from dotenv import load_dotenv
import requests
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from recommend import get_recommendations

base_url = "https://api.themoviedb.org/3/movie/"
img_base_url = "http://image.tmdb.org/t/p/w500"

# Load Movie DataFrame and paths
movie_path = './data/movies.csv'
index_path = './vector_db/faiss_index.index'
movies = pd.read_csv(movie_path)


def fetch_poster(movie_id):
  # Fetch Movie Details 
  url = base_url + "{}?language=en-US".format(movie_id)

  # Auth
  # Load .env file
  # load_dotenv()

  # Get API Key
  # API = os.getenv("TMDB_API")
  API = st.secrets["TMDB_API"]["header"]

  headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API}"
    }
  
  # Hit API
  response = requests.get(url, headers=headers)

  # Validate API response 
  if (response.status_code == 200):
     data = response.json()
     return img_base_url + data['poster_path']
  else:
     logging.error(f"Error: {response.status_code}, {response.text}")

 

def recommend(movie_id):

  recc_movies = []
  recc_poster = []
  print("Movie ID",movie_id)
  recc_ids = get_recommendations(movie_path, index_path, movie_id, k=6)
  for i in recc_ids:
    # Get recommended movie
    recc_movies.append(movies[movies['movie_id']==i]['title'].values[0])

    # Fetch movie poster
    recc_poster.append(fetch_poster(i))

    print(recc_movies)
  return recc_movies, recc_poster



st.title('Movie Recommender System')

selected_movie_name = st.selectbox('Search Movie', movies['title'].values)

if st.button('Recommend'):
  selected_movie_id = movies[movies['title'] == selected_movie_name]['movie_id'].values
  recc_movies, recc_poster = recommend(selected_movie_id[0])

  
  cols = st.columns(5, vertical_alignment = "bottom")

  for i, col in enumerate(cols):
      with col:
          st.markdown(f"<h6 style='text-align: center;'>{recc_movies[i]}</h6>", unsafe_allow_html=True)
          st.image(recc_poster[i], use_container_width=True)

