from dataclasses import dataclass

@dataclass
class Movie:
    title: str
    year: str
    imdb_id: str
    content_type: str
    genre: str
    plot: str
    rating: str
    runtime:str
    actors: str
    poster: str
    source: str

    trailer_title: str
    trailer_url: str
    trailer_video_id: str