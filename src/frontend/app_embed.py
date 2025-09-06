import streamlit as st
import pandas as pd
import requests
import os
import sys
import logging
import faiss 
from sentence_transformers import SentenceTransformer
import numpy as np
# import time

logging.basicConfig(level=logging.INFO)

@st.cache_data
def load_movie_data():
   """Load movie metadata from CSV file."""
   movie_path = './data/movies.csv'
   return pd.read_csv(movie_path)

@st.cache_data
def normalize(embeddings):
  """Function to normlize vector embeddings"""
  return(embeddings/np.linalg.norm(embeddings, axis=1, keepdims=True))
   

@st.cache_resource
def load_faiss_index():
   """Load FAISS index from file."""
   index_path = './vector_db/faiss_index.index'
   return faiss.read_index(index_path)

@st.cache_resource
def load_sentence_transformer():
   """Load SentenceTransformer model."""
   return SentenceTransformer('all-MiniLM-L6-v2')
  

# Load model, index, and metadata
model = load_sentence_transformer()
movies = load_movie_data()
index = load_faiss_index()

   
base_url = "https://api.themoviedb.org/3/movie/"
img_base_url = "http://image.tmdb.org/t/p/w500"


def fetch_poster(movie_id):
  # Fetch Movie Details 
  url = base_url + "{}?language=en-US".format(movie_id)

  # Get API key from Streamlit secrets
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

 

def recommend(movie_id, k=6):

  recc_movies = []
  recc_poster = []

  # Get the query vector
  query = movies[movies['movie_id'] == movie_id]['tags'].values
  query_embedding = model.encode(query)
  qembed_norm = normalize(query_embedding)

  # Search Vector DB
  similarity, idx  = index.search(qembed_norm, k)
  recc_ids = [i for i in idx[0] if i != movie_id]

  for i in recc_ids:
    # Get recommended movie
    recc_movies.append(movies[movies['movie_id']==i]['title'].values[0])

    # Fetch movie poster
    recc_poster.append(fetch_poster(i))

  return recc_movies, recc_poster



st.title('Movie Recommender System')

selected_movie_name = st.selectbox('Search Movie', movies['title'].values)

# start_time = time.time()
if st.button('Recommend'):
  selected_movie_id = movies[movies['title'] == selected_movie_name]['movie_id'].values
  recc_movies, recc_poster = recommend(selected_movie_id[0])

  # end_time = time.time()
  # st.info(f"Recommendation took {end_time - start_time:.2f} seconds")

  cols = st.columns(5, vertical_alignment = "bottom")

  for i, col in enumerate(cols):
      with col:
          st.markdown(f"<h6 style='text-align: center;'>{recc_movies[i]}</h6>", unsafe_allow_html=True)
          st.image(recc_poster[i], use_container_width=True)

