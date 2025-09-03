import pandas as pd
import ast
import re
import os
import argparse
import logging
from tqdm import tqdm 

logging.basicConfig(level=logging.INFO)

def convert_to_list(df, column_names=None):
  """Converts strings of lists of strings into list of strings"""
  if column_names is None:
     column_names = []

  for col in column_names:
    df[col] = df[col].apply(lambda x: ast.literal_eval(x))
  return df


def replace_space(df,column_names=None):
  """Removes spaces in each feature"""
  if column_names is None:
     column_names = []

  for name in column_names:
     df[name] = df[name].apply(lambda x: [i.replace(" ", "") for i in x])
  return df

def clean_text(text):
    """Function to remove special characters and spaces"""
    if isinstance(text, list):
        # Clean each string in the list
        return [re.sub(r'[^A-Za-z0-9]', '', i) for i in text]
    elif isinstance(text, str):
        # Clean a string
        return re.sub(r'[^A-Za-z0-9\s]', '', text)
    return text

def clean_strings(df, column_names=None):
  """Applies Function to remove special characters and spaces to all columns"""
  if column_names is None:
     column_names = []

  for name in column_names:
     df[name] = df[name].apply(clean_text)
  return df

def create_tags(df):
  """Function to create tags"""
  df['tags'] = df['overview'] + df['genres'] + df['keywords'] + df['cast'] + df['crew']
  
  # Join to form one string
  df['tags'] = df['tags'].apply(lambda x: " ".join(x))

  # Convert to lowercase
  df['tags'] = df['tags'].apply(lambda x: x.lower())
  return df



def parse_args():
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser(description="Preprocess Features")
  parser.add_argument('--src_path', type=str, default = './data/sample_fetched_movies.csv')
  parser.add_argument('--dest_path', type=str, default = './data/sample_movies.csv')
  parser.add_argument('--batch_size', type=int, default = 20)
  parser.add_argument('--column_names', nargs='+', type=str, default=['overview', 'genres', 'keywords', 'cast', 'crew'])

  return parser.parse_args()




if __name__ == '__main__':

  # Parse command-line arguments
  args = parse_args()
  
  # Path to Dataframe
  file_path = args.src_path

  # Path to save pre-processed data
  dest_path = args.dest_path

  # Batch size for processing
  batch_size = args.batch_size

  # Column names for processing 
  column_names = args.column_names

  # Dataframe operations (.pipe() used to chain operations on df)
  try:
    # subtract 1 for header
    total_rows = sum(1 for _ in open(file_path, encoding='utf-8')) - 1 

    # Calculate number of batches (Rounded up number)
    num_batches = (total_rows + batch_size - 1) // batch_size
    
    for chunk in tqdm(pd.read_csv(file_path, chunksize=batch_size), total=num_batches):
      df = (
            chunk
            .pipe(convert_to_list, column_names=column_names)
            .pipe(replace_space, column_names=column_names)
            .pipe(clean_strings, column_names=column_names)
            .pipe(create_tags)
          )

      # Create new data frame 
      movies = df[['movie_id', 'title', 'tags']]

      if os.path.exists(dest_path):
          movies.to_csv(dest_path, mode='a', header=False, index=False)
      else:
          movies.to_csv(dest_path, mode='w', header=True, index=False)
    
    logging.info("Successfully Transformed Data")
  except Exception as e:
     logging.error(f"Error during batch processing: {e}")
  