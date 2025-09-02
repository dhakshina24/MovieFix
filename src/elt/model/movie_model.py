class Movie:
  """
    Represents the details associated with a movie.

    Attributes:
        id (int): The unique ID of the movie.
        title (str): Title of the movie.
        overview (str): Summary of the movie.

    Methods:
        from_api(cls, data: dict) -> Movie:
            Parses movie details JSON from the TMDB API into a Movie instance.
  """
  def __init__(self, id, title, overview):
    self.id = id
    self.title = title
    self.overview = overview

  
  @classmethod
  def from_api(cls, data: dict):
    """Creates a Movie instance from TMDB API JSON data."""
    return cls(
      id = data.get("id"),
      title = data.get("title"),
      overview = data.get("overview").split()
    )