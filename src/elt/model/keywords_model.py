class Keywords:
  """
    Represents the keywords associated with a movie.

    Attributes:
        id (int): The unique ID of the movie.
        keywords (List[str]): A list of keywords for the movie.

    Methods:
        from_api(cls, data: dict) -> Keywords:
            Parses movie details JSON from the TMDB API into a Keywords instance.
  """
  def __init__(self, id, keywords):
    self.id = id
    self.keywords = keywords
  
  @classmethod
  def from_api(cls, data: dict):
    """Creates a Keywords instance from TMDB API JSON data."""
    return cls(
      id = data.get("id"),
      keywords = [i.get("name") for i in data.get("keywords")]
    )