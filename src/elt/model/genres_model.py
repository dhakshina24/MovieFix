class Genres:
  """
    Represents the genres associated with a movie.

    Attributes:
        id (int): The unique ID of the movie.
        genres (List[str]): A list of genre names for the movie.

    Methods:
        from_api(cls, data: dict) -> Genres:
            Parses movie details JSON from the TMDB API into a Genres instance.
  """
  def __init__(self, id, genres):
    self.genres = genres
    self.id = id
  
  @classmethod
  def from_api(cls, data: dict):
    """Creates a Genres instance from TMDB API JSON data."""
    return cls(
      genres = [i.get("name") for i in data.get("genres")],
      id = data.get("id"),
    )