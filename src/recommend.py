import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from vectorize import normalize
import argparse
import logging

logging.basicConfig(level=logging.INFO)

# Store Results
results = []



def parse_args():
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser(description="Recommend Movies")
  parser.add_argument('--src_path', type=str, default='./data/movies.csv')
  parser.add_argument('--index_path', type=str, default='./vector_db/faiss_index.index')
  parser.add_argument('--k', type=int, default=6)
  return parser.parse_args()



def get_recommendations(movie_path, index_path, movie_id, k):
  """Returns top-k recommended movies given a movie_id"""

  # Load model, index, and metadata
  model = SentenceTransformer("all-MiniLM-L6-v2")
  df_movies = pd.read_csv(movie_path)
  index = faiss.read_index(index_path)

  # Get the query vector
  query = df_movies[df_movies['movie_id'] == movie_id]['tags'].values
  query_embedding = model.encode(query)
  qembed_norm = normalize(query_embedding)

  # Search Vector DB
  similarity, idx  = index.search(qembed_norm, k)
  recc_ids = [i for i in idx[0] if i != movie_id]
  query_title = df_movies[df_movies['movie_id']==movie_id]['title'].values[0]
  logging.info(f"Recommendations for {query_title}:")

  
  for idx, rec_id in enumerate(recc_ids):
      rec_title = df_movies[df_movies['movie_id']==rec_id]['title'].values[0]
      sim_score = similarity[0, idx]  # assuming similarity shape is (1, k)
      logging.info(f"Movie {idx+1}: {rec_title} with a similarity score of {sim_score:.4f}")
      results.append({"Rank": idx+1, "Title": rec_title, "Similarity": sim_score})

  return recc_ids





if __name__ == '__main__':
  logging.info("Starting movie recommendation...")

  # Command-line arguments
  args = parse_args()
  
  # Filepath
  movie_path = args.src_path
  
  # Path to Index
  index_path = args.index_path

  # Number of recommendations
  k = args.k

  # Superman
  get_recommendations(movie_path, index_path, 1061474, k)

  # Harry Potter
  get_recommendations(movie_path, index_path, 674, k)

  # Kpop Demon Hunters
  get_recommendations(movie_path, index_path, 803796, k)

  df_recc = pd.DataFrame(results)
  df_recc.to_csv("recommendations.csv", index=False)




