from models import Movie


def normalize_movie_data(tmdb_data, trailer_data, poster_url):
    if trailer_data is None:
        trailer_title = ""
        trailer_url = ""
        trailer_video_id = ""
    else:
        trailer_title = trailer_data.get("title", "")
        trailer_url = trailer_data.get("url", "")
        trailer_video_id = trailer_data.get("video_id", "")

    genres = tmdb_data.get("genres", [])
    genre_names = ", ".join(genre.get("name", "") for genre in genres)

    cast_list = tmdb_data.get("credits", {}).get("cast", [])
    actors = ", ".join(actor.get("name", "") for actor in cast_list[:5])

    release_date = tmdb_data.get("release_date") or tmdb_data.get("first_air_date") or ""
    year = release_date[:4] if release_date else ""

    runtime_value = tmdb_data.get("runtime")
    if runtime_value:
        runtime = f"{runtime_value} min"
    else:
        episode_runtime = tmdb_data.get("episode_run_time", [])
        runtime = f"{episode_runtime[0]} min" if episode_runtime else ""

    title = tmdb_data.get("title") or tmdb_data.get("name", "")
    content_type = "serie" if tmdb_data.get("name") else "film"

    return Movie(
        title=title,
        year=year,
        imdb_id=str(tmdb_data.get("id", "")),
        content_type=content_type,
        genre=genre_names,
        plot=tmdb_data.get("overview", ""),
        rating=str(tmdb_data.get("vote_average", "")),
        runtime=runtime,
        actors=actors,
        poster=poster_url,
        source="TMDb",
        trailer_title=trailer_title,
        trailer_url=trailer_url,
        trailer_video_id=trailer_video_id
    )