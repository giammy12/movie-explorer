from urllib.parse import urlencode


PROVIDER_BASE_URL = "https://vixsrc.to"


PLAYER_PARAMS = {
    "lang": "it",
    "autoplay": "false",
    "primaryColor": "B20710",
    "secondaryColor": "170000"
}


def build_movie_video_url(tmdb_id, start_at=0):
    params = PLAYER_PARAMS.copy()

    try:
        start_at = int(start_at)
    except Exception:
        start_at = 0

    if start_at > 0:
        params["startAt"] = start_at

    query_string = urlencode(params)

    return f"{PROVIDER_BASE_URL}/movie/{tmdb_id}?{query_string}"


def build_tv_video_url(tmdb_id, season, episode, start_at=0):
    params = PLAYER_PARAMS.copy()

    try:
        start_at = int(start_at)
    except Exception:
        start_at = 0

    if start_at > 0:
        params["startAt"] = start_at

    query_string = urlencode(params)

    return f"{PROVIDER_BASE_URL}/tv/{tmdb_id}/{season}/{episode}?{query_string}"


def get_provider_origin():
    return PROVIDER_BASE_URL