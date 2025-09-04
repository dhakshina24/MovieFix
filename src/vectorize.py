from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss
import os
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


def normalize(embeddings):
  """Function to normlize vector embeddings"""
  return(embeddings/np.linalg.norm(embeddings, axis=1, keepdims=True))


def create_index(df, embeddings, index_path):
  """Store Embeddings in Vector DB"""
  
  # Vector Normalization
  norm_embeddings = normalize(embeddings)

  # IDs for FAISS
  ids = df["movie_id"].values.astype('int64')

  # Check if index exists 
  if os.path.exists(index_path):
    logging.info("Loading existing FAISS index")
    index = faiss.read_index(index_path)
  else:
    logging.info("Creating new FAISS index")
    index = faiss.IndexIDMap(faiss.IndexFlatIP(norm_embeddings.shape[1]))
  
  # Add embeddings with IDs
  index.add_with_ids(norm_embeddings, ids)
  logging.info("Number of vectors: %d", index.ntotal)

  # Save index
  faiss.write_index(index, index_path)
  logging.info("Index saved at %s", index_path)

  return index

def parse_args():
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser(description="Vectorize movie data")
  parser.add_argument('--src_path', type=str, default='./data/sample_movies.csv')
  parser.add_argument('--index_path', type=str, default='./vector_db/sample_index.index')
  return parser.parse_args()

if __name__ == '__main__':

  # Parse command-line arguments
  args = parse_args()
  
  # Filepath
  movie_path = args.src_path

  # Path to Index
  index_path = args.index_path

  # Load Transformed Dataframe
  df = pd.read_csv(movie_path)

  # Load a pretrained Sentence Transformer model
  model = SentenceTransformer("all-MiniLM-L6-v2")

  # Get embeddings for tags
  embeddings = model.encode(df["tags"].tolist(), show_progress_bar=True)
  logging.info("Embeddings Generated for Tags: %s", embeddings.shape)

  # Store Embeddings in Vector DB
  index = create_index(df, embeddings, index_path)
  logging.info("Embeddings successfully added to vector DB")




