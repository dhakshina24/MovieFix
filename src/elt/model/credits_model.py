class Credits:
  """
    Represents the cast and crew information for a movie.

    Attributes:
        id (int): The unique ID of the movie.
        cast (List[str]): A list of the top 3 cast member names.
        crew (List[str]): A list of crew members filtered by a specific job (Director).

    Methods:
        from_api(cls, data: dict) -> Credits:
            Parses movie credits JSON from the TMDB API into a Credits instance.
  """

  def __init__(self, id, cast, crew):
    self.id = id
    self.cast = cast
    self.crew = crew

  
  @classmethod
  def from_api(cls, data: dict):
    """Creates a Credits instance from TMDB API JSON data."""
    return cls(
      id = data.get("id", 0),
      cast = [i.get('name') for i in data.get("cast", [])][:3],
      crew = [i.get('name') for i in data.get("crew", []) if i.get('job') == "Director"]
    )